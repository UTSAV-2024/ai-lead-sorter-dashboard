import streamlit as st
import pandas as pd
import os
import re

from agent_backend import run_agent_workflow

# --- Page Configuration & Helper Function ---
st.set_page_config(page_title="AI Lead Qualification Assistant", page_icon="🤖", layout="centered")

def extract_spreadsheet_id(url: str) -> str:
    """Extracts the spreadsheet ID from a Google Sheets URL."""
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else None

# --- UI Layout ---
st.title("🤖 AI Lead Qualification Assistant")
st.markdown("This AI agent securely processes your unread emails to identify and save hot leads directly to your Google Sheet.")

# --- User Inputs ---
email_input = st.text_input("Enter your Google Email Address", placeholder="your.email@gmail.com")
sheet_url_input = st.text_input("Enter your Google Sheet URL", placeholder="https://docs.google.com/spreadsheets/d/...")

st.info("First-Time Use: A browser tab will open for you to grant permission. Please select the same Google Account you entered above.", icon="ℹ️")

# --- Main Action Button ---
if st.button("▶️ Scan Inbox & Process Leads", type="primary", use_container_width=True):
    if not email_input or not sheet_url_input:
        st.warning("Please enter both your email and Google Sheet URL.", icon="⚠️")
    else:
        spreadsheet_id = extract_spreadsheet_id(sheet_url_input)
        if not spreadsheet_id:
            st.error("Invalid Google Sheet URL. Please paste the full URL.", icon="🚨")
        elif not os.path.exists("credentials.json"):
            st.error("`credentials.json` not found. Please follow setup instructions.", icon="🚨")
        else:
            with st.spinner(f"🤖 Agent connecting to '{email_input}'... Please check for an authentication pop-up in your browser."):
                try:
                    # Pass all necessary info to the backend
                    agent_result = run_agent_workflow(
                        email_address=email_input,
                        spreadsheet_id=spreadsheet_id
                    )

                    summary = agent_result.get("summary", "No summary provided.")
                    leads = agent_result.get("leads", [])

                    st.success("🎉 Workflow Complete!")
                    st.write(f"**Agent's Summary:** {summary}")

                    st.session_state['processed_leads'] = leads
                    st.session_state['has_run'] = True

                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}", icon="🚨")

# --- Results Display ---
if 'has_run' in st.session_state:
    st.write("---")
    st.subheader("Processed Leads")
    if 'processed_leads' in st.session_state and st.session_state['processed_leads']:
        leads_df = pd.DataFrame(st.session_state['processed_leads'])
        st.dataframe(leads_df, use_container_width=True, hide_index=True)
        st.balloons()
    else:
         st.write("No new hot leads were found during the last scan.")

