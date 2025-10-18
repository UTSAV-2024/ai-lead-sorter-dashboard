import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def get_credentials(email_address: str):
    """
    Gets valid user-specific credentials from storage or logs the user in.
    """
    creds = None
    token_path = f"{email_address}.token.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Add a check for the credentials.json file
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError(
                    "Error: credentials.json not found. Please follow setup instructions."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds

def add_row_to_sheet(input_string: str, email_address: str, spreadsheet_id: str) -> str:
    """
    Appends a new row to the specified Google Sheet, checking for headers first.
    Expected input format: "Company Name|From|Relevant/Not|Type of Lead"
    """
    try:
        parts = input_string.strip().split('|')
        if len(parts) != 4:
            return "Error: Input string for the sheet must contain four parts separated by '|'."
        
        creds = get_credentials(email_address)
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        # --- HEADER CHECKING LOGIC ---
        header_range = "Sheet1!A1:D1"
        current_headers = sheet.values().get(spreadsheetId=spreadsheet_id, range=header_range).execute()
        header_values = current_headers.get('values', [])
        
        required_headers = [["Company Name", "From", "Relevant", "Type of Lead"]]

        if not header_values or header_values[0] != required_headers[0]:
            # Prepend headers if they don't exist or don't match
            sheet.values().update(
                spreadsheetId=spreadsheet_id,
                range=header_range,
                valueInputOption="USER_ENTERED",
                body={"values": required_headers}
            ).execute()

        # --- DATA APPENDING LOGIC ---
        new_row_data = [parts] # Use the parsed parts directly

        sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range="Sheet1!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": new_row_data}
        ).execute()
        
        saved_data = {"company": parts[0], "from": parts[1], "relevant": parts[2], "type": parts[3]}
        return json.dumps(saved_data)

    except Exception as e:
        return f"An error occurred while writing to the sheet: {e}"

