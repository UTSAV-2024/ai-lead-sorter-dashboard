import os
import json
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_json_chat_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import get_all_tools

load_dotenv()

def create_agent(email_address: str, spreadsheet_id: str):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    all_tools = get_all_tools(email_address=email_address, spreadsheet_id=spreadsheet_id)
    prompt = hub.pull("hwchase17/react-chat-json")
    agent = create_json_chat_agent(llm, all_tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,
        handle_parsing_errors=True
    )

def run_agent_workflow(email_address: str, spreadsheet_id: str):
    lead_sorter_agent = create_agent(email_address=email_address, spreadsheet_id=spreadsheet_id)
    
    # --- UPGRADED MASTER PROMPT ---
    master_prompt = """
    Your mission is to execute a full lead sorting workflow. You must think step-by-step.

    1.  **First, read the user's inbox:** Use the `ReadUnreadEmails` tool.
    2.  **Process each email one by one:** For each email you find, you must perform the following sub-tasks:
        a. **Classify:** Use the `ClassifyEmail` tool on the email's body to determine its category.
        b. **Check if it's a Hot Lead:** If and only if the category is 'Hot Lead', proceed to the next step. Otherwise, you can consider it 'Not Relevant' and move to the next email.
        c. **Extract Details:** Use the `ExtractLeadDetails` tool on the email's body. This will return a JSON string.
        d. **Assemble the Final Data:** You MUST now take information from MULTIPLE previous steps and assemble the data for the spreadsheet. The format is 'Company Name|From|Relevant|Type of Lead'.
           - 'Company Name' comes from the JSON from the Extract tool.
           - 'From' is the 'sender' you got from the ReadUnreadEmails tool for this email.
           - 'Relevant' should be 'Yes'.
           - 'Type of Lead' is 'Hot Lead'.
        e. **Save the Lead:** Use the `SaveToSpreadsheet` tool with the assembled pipe-separated string.
    3.  **Final Report:** After you have processed all emails, you MUST provide your final answer as a single, minified JSON object with two keys: "summary" and "leads". The "summary" should describe your work, and "leads" should be a list of all the JSON objects for the leads you successfully saved.
    """
    
    print(f"Starting agent workflow for {email_address}...")
    result = lead_sorter_agent.invoke({"input": master_prompt})
    
    try:
        # A more robust way to handle potential malformed JSON from the LLM
        output_str = result.get('output', '{}').strip()
        json_start = output_str.find('{')
        json_end = output_str.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = output_str[json_start:json_end]
            return json.loads(json_str)
        else:
             return {"summary": "Agent returned a non-JSON response.", "leads": []}
    except json.JSONDecodeError:
        return {"summary": "Agent returned an invalid JSON format.", "leads": []}

