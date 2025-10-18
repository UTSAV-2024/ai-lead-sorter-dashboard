# AI Lead Qualification Dashboard

This is a full-stack web application that leverages a multi-tool AI agent to function as an autonomous sales assistant. It provides a user-friendly interface for securely processing unread emails, identifying and analyzing hot leads, and automatically saving them to a Google Sheet.



## Core Capabilities

-   **User-Friendly Frontend:** A clean, intuitive web dashboard built with Streamlit for easy interaction.
-   **Multi-User Authentication:** Securely connects to any user's Google Account using the industry-standard OAuth 2.0 protocol, creating separate, persistent sessions for each user.
-   **Intelligent Email Analysis:** The backend agent uses a fine-tuned LLM (Google Gemini) to:
    -   **Classify** emails into categories like "Hot Lead" or "Spam".
    -   **Extract** structured information (name, company, need) from unstructured email text.
-   **Automated Workflow Orchestration:** The agent autonomously executes a multi-step workflow: reading emails, classifying, extracting, and saving data without human intervention.
-   **Dynamic Header Management:** Automatically creates and formats the required headers in the target Google Sheet if they don't exist.

## Tech Stack

-   **Frontend:** Streamlit
-   **Backend & Orchestration:** Python, LangChain
-   **LLM:** Google Gemini Pro
-   **Tools & APIs:** Google Workspace (Gmail & Sheets) with OAuth 2.0, Playwright, SerpAPI

---

## 🚀 Setup & Installation Guide

### 1. Initial Project Setup

```bash
# Clone the repository to your local machine
git clone <your-repo-url-here>
cd ai-lead-sorter-app

# Create and activate a Python virtual environment
python -m venv venv
# On Windows:
.\\venv\\Scripts\\activate
# On Mac/Linux:
source venv/bin/activate

# Install all required dependencies
pip install -r requirements.txt