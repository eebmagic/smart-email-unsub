import os.path
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import json

from filters import filterMeta

### AUTHENTICATION ###
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

### GET MESSAGES IN TRASH ###
# TODO: Maybe add pagination here to try to get more than 100 resulting messages
results = service.users().messages().list(userId='me', labelIds=['TRASH', 'UNREAD']).execute()
messageIds = results.get('messages', [])
print(f"Found {len(messageIds)} total unread messages in inbox")

print(f"Getting message bodies...")
messages = [service.users().messages().get(userId='me', id=msg['id']).execute() for msg in messageIds]

print(f"Filtering message bodies...")
filtered = filterMeta(messages)
print(json.dumps(filtered, indent=2))

# TODO: Use this regex to filter for receipt values:
'''
grep -E '\$\d{1,3}(,?\d{3})*(\.\d{2})?' message_samples.json
'''

# TODO: Handoff to vector db processing
'''
- Check that messages are not already in the db (by message id)
- Get embeddings from new messages (through OpenAI embeddings)
    - For truncated bodies AND snippets
- Add new messages to the db with embeddings
'''
