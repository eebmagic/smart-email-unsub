import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Path to your credentials.json file
credential_path = 'credentials.json'

# If modifying these SCOPES, delete the file token.json.
if os.path.exists('token.json'):
    os.remove('token.json')

flow = InstalledAppFlow.from_client_secrets_file(credential_path, SCOPES)
creds = flow.run_local_server(port=0)

service = build('gmail', 'v1', credentials=creds)

results = service.users().messages().list(userId='me').execute()
messages = results.get('messages', [])
print(results)
print(messages)
