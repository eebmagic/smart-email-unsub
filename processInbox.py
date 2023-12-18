from MailInterface import getMessages
from filters import getUsefulBodies
from DBInterface import inboxCacheCollection, SafeInterface

# Get unread inbox and add to db
unreadInbox = getMessages(['INBOX', 'UNREAD'])
print(f"Got {len(unreadInbox)} unread messages from inbox.")
ids, bodies, usedUnreadInbox = getUsefulBodies(unreadInbox)

# Cache the inbox messages in a collection
inboxInterface = SafeInterface(inboxCacheCollection, batchSize=100)

inboxInterface.add(
    ids=ids,
    metadatas=usedUnreadInbox,
    documents=bodies
)
