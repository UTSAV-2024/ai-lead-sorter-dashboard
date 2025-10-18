from langchain.tools import Tool
from functools import partial
from langchain_community.utilities import SerpAPIWrapper
from playwright.sync_api import sync_playwright

from email_tools import read_unread_emails
from llm_tools import classify_email, extract_lead_details
from sheets_tool import add_row_to_sheet

def scrape_with_playwright(url: str) -> str:
    """Scrapes a URL using Playwright."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            content = page.locator('body').inner_text()
            browser.close()
            return content[:4000]
    except Exception as e:
        return f"Error scraping website: {e}"

def get_all_tools(email_address: str, spreadsheet_id: str) -> list:
    """
    Initializes and returns a list of all tools for the agent.
    """
    read_emails_for_user = partial(read_unread_emails, email_address=email_address)
    add_row_for_user_sheet = partial(add_row_to_sheet, email_address=email_address, spreadsheet_id=spreadsheet_id)
    search = SerpAPIWrapper()

    all_tools = [
        Tool.from_function(
            func=read_emails_for_user,
            name="ReadUnreadEmails",
            description="Use this tool first to read recent unread emails from the user's inbox."
        ),
        Tool.from_function(
            func=classify_email,
            name="ClassifyEmail",
            description="Use this tool to classify an email's text into 'Hot Lead', 'General Question', or 'Spam'."
        ),
        Tool.from_function(
            func=extract_lead_details,
            name="ExtractLeadDetails",
            description="Use this on a 'Hot Lead' email to extract the sender's name and company into a JSON format."
        ),
        Tool(
            name="SaveToSpreadsheet",
            func=add_row_for_user_sheet,
            description="""
            Use this as the mandatory final step to save a single lead's information to a Google Sheet.
            The input MUST be a single string with four parts separated by '|': Company Name, From (sender's email), Relevant (e.g., 'Yes' or 'No'), and Type of Lead (e.g., 'Hot Lead').
            This tool is the final action in the workflow.
            """
        )
    ]
    return all_tools

