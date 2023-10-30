import os.path
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import json
import base64
from datetime import datetime

# Add the scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Path to your credentials.json file
credential_path = 'credentials.json'
token_path = 'token.json'

# Check if the token.json file exists
if os.path.exists(token_path):
    credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
else:
    # If no token exists, use the credentials.json to authenticate and get a new token
    flow = InstalledAppFlow.from_client_secrets_file(credential_path, SCOPES)
    credentials = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open(token_path, 'w') as token:
        token.write(credentials.to_json())

service = build('gmail', 'v1', credentials=credentials)

results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
messages = results.get('messages', [])
print(f"Found {len(messages)} total unread messages in inbox")


for message in messages:
    msg_id = message['id']
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    received_date = datetime.fromtimestamp(int(msg['internalDate']) / 1000)

    print('=' * 80)
    print(json.dumps(msg, indent=2))

    try:
        if 'data' in msg['payload']['body']:
            msg_body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
        elif 'data' in msg['payload']['parts'][0]['body']:
            msg_body = base64.urlsafe_b64decode(msg['payload']['parts'][0]['body']['data']).decode('utf-8')
        else:
            msg_body = "No message body found."

        print(f"Message ID: {msg_id}\nMessage Date: {received_date.strftime('%Y-%m-%d %H:%M:%S')}\nMessage Body:\n{msg_body}\n")
    except Exception as e:
        print(f"Error processing message with ID {msg_id}: {e}")

    break
