import os.path
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from tqdm import tqdm

from filters import filterMeta
from DBInterface import trashCollection

### AUTHENTICATION ###
# Add the scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Path to your credentials.json file
credential_path = 'credentials.json'
token_path = 'token.json'

# Check if the token.json file exists
def getCredentials():
    if os.path.exists(token_path):
        credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
        try:
            service = build('gmail', 'v1', credentials=credentials)
            _ = service.users().messages().list(userId='me').execute()
            return credentials
        except RefreshError:
            # If the token has expired, use the refresh_token to get a new one
            os.remove(token_path)
            return getCredentials()
    else:
        # If no token exists, use the credentials.json to authenticate and get a new token
        flow = InstalledAppFlow.from_client_secrets_file(credential_path, SCOPES)
        credentials = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(credentials.to_json())

        return credentials

credentials = getCredentials()
service = build('gmail', 'v1', credentials=credentials)

def getMessages(labels):
    '''
    Gets messages from GMAIL basd on labels.
    Example: labels=['TRASH', 'UNREAD']
    or labels=['INBOX', 'UNREAD']
    '''
    assert type(labels) == list, "labels must be list"
    assert all([type(val) == str for val in labels]), "labels must be list of strings"

    results = service.users().messages().list(userId='me', labelIds=labels).execute()
    messageIds = results.get('messages', [])

    while 'nextPageToken' in results:
        pageToken = results['nextPageToken']
        results = service.users().messages().list(userId='me', labelIds=labels, pageToken=pageToken).execute()
        messageIds += results.get('messages', [])

    print(f"Found {len(messageIds)} total unread messages in {labels}")

    print(f"Getting message bodies...")
    gres = trashCollection.get(
        ids=[msg['id'] for msg in messageIds],
        include=['metadatas']
    )
    existingIds = set(gres['ids'])
    existing = gres['metadatas']
    print(f"Found {len(existingIds)} / {len(messageIds)} already existing messages in DB.")

    newMessages = []
    for msg in tqdm(messageIds):
        if msg['id'] not in existingIds:
            result = service.users().messages().get(userId='me', id=msg['id']).execute()
            newMessages.append(result)

    print(f"Filtering message bodies...")

    filtered = filterMeta(newMessages)
    filtered += existing

    return filtered