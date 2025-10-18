import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# --- ENVIRONMENT SETUP ---
# This ensures the script can find the GOOGLE_API_KEY when run directly.
load_dotenv()

# --- LLM INITIALIZATION ---
# Initialize the LLM once to be reused by both functions for efficiency.
# Using the stable "gemini-2.5-flash" model for compatibility.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# --- CLASSIFIER FUNCTION ---
def classify_email(email_body: str) -> str:
    """
    Uses an LLM to classify an email's text into a specific category.
    Returns a single category string: 'Hot Lead', 'General Question', or 'Spam'.
    """
    classifier_prompt_template = """
    **Persona:** You are an expert sales assistant responsible for triaging an inbox.
    **Task:** Classify the following email into one of three categories: `Hot Lead`, `General Question`, or `Spam`.
    **Criteria:**
    - A `Hot Lead` shows clear buying intent, mentions a company, a specific business problem, or directly asks for a meeting.
    - A `General Question` is a simple request for information without clear buying intent.
    - `Spam` is an unsolicited marketing email or an irrelevant message.
    **Output Format:** You MUST only return the category name and nothing else.
    ---
    **Email to Classify:**
    {email_text}
    """
    prompt = PromptTemplate.from_template(classifier_prompt_template)
    classifier_chain = prompt | llm
    response = classifier_chain.invoke({"email_text": email_body})
    return response.content.strip()

# --- EXTRACTOR FUNCTION ---
def extract_lead_details(email_body: str) -> str:
    """
    Uses an LLM to extract key details from a hot lead's email.
    Returns a clean, minified JSON string with 'name', 'company', and 'need'.
    """
    extractor_prompt_template = """
    **Persona:** You are a highly accurate data extraction expert that always responds in JSON.
    **Task:** Read the following email from a potential lead and extract the specified information.
    **Output Format:** You MUST return the information as a single, minified JSON object with the following keys: `name`, `company`, and `need`.
    **Rules:**
    - If a specific piece of information (like the company name) is not mentioned, use the JSON value `null`.
    - The "need" should be a concise, one-sentence summary of the user's primary request.
    ---
    **Email to Extract From:**
    {email_text}
    """
    prompt = PromptTemplate.from_template(extractor_prompt_template)
    extractor_chain = prompt | llm
    response = extractor_chain.invoke({"email_text": email_body})
    return response.content.strip()

# --- Test Block ---
# This allows you to test this file's functions independently.
if __name__ == '__main__':
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found in .env file.")
    else:
        test_email = "Hi there, I saw your portfolio. My name is Sameer from a company called Tech Innovators. We are looking for a way to automate our lead qualification process. Can we schedule a brief call?"
        
        print("--- Testing Classifier ---")
        category = classify_email(test_email)
        print(f"Category: '{category}'")

        print("\n--- Testing Extractor ---")
        if category == "Hot Lead":
            details_json = extract_lead_details(test_email)
            try:
                details_dict = json.loads(details_json)
                print(f"Extracted Details: {details_dict}")
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from LLM response: {details_json}")
        else:
            print("Not a hot lead, skipping extraction.")

