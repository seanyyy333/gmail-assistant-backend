import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

def get_gmail_service():
    """Authenticates and returns a Gmail API service instance."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'token.json')
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'credentials.json')

    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None

        if not creds or not creds.valid:
            if os.path.exists(credentials_path):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"An error occurred during OAuth flow: {e}")
                    return None
            else:
                print("credentials.json not found. Please set up your OAuth credentials.")
                return None

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f"API error creating Gmail service: {error}")
        return None

def get_gmail_service_dependency():
    """FastAPI dependency to provide the Gmail API service."""
    service = get_gmail_service()
    if service is None:
        print("Gmail service not initialized.")
    return service
