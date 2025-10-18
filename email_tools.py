import os.path
import base64
from bs4 import BeautifulSoup
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
    """Gets valid user-specific credentials."""
    creds = None
    token_path = f"{email_address}.token.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds

def read_unread_emails(input_arg: str = "5", email_address: str = None) -> str:
    """Fetches and cleans unread emails for the specified user."""
    if not email_address:
        return "Error: Email address not provided to read_unread_emails function."
    try:
        max_results = int(input_arg)
    except (ValueError, TypeError):
        max_results = 5

    try:
        creds = get_credentials(email_address)
        service = build("gmail", "v1", credentials=creds)

        # ... (rest of the email reading logic is the same)
        results = service.users().messages().list(
            userId='me', labelIds=['UNREAD'], maxResults=max_results
        ).execute()
        messages = results.get('messages', [])

        if not messages:
            return "No unread messages found."

        email_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'No Sender')
            
            plain_text_body = "Email body not found."

            if 'parts' in payload:
                part = next((p for p in payload['parts'] if p.get('mimeType') == 'text/plain'), None)
                if part:
                    body_data = part.get('body', {}).get('data')
                    if body_data:
                        decoded_data = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        plain_text_body = ' '.join(decoded_data.split())
                else:
                    html_part = next((p for p in payload['parts'] if p.get('mimeType') == 'text/html'), None)
                    if html_part:
                        body_data = html_part.get('body', {}).get('data')
                        if body_data:
                            decoded_html = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                            soup = BeautifulSoup(decoded_html, 'html.parser')
                            plain_text_body = ' '.join(soup.get_text().split())
            else:
                 body_data = payload.get('body', {}).get('data')
                 if body_data:
                    decoded_data = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                    plain_text_body = ' '.join(decoded_data.split())
            
            email_data = {
                "id": message['id'],
                "sender": sender,
                "subject": subject,
                "body": plain_text_body[:2000]
            }
            email_list.append(email_data)
        
        return f"Found {len(email_list)} emails: {str(email_list)}"

    except Exception as e:
        return f"An unexpected error occurred: {e}"

