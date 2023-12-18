from MailInterface import getMessages
from DBInterface import SafeInterface, trashCollection
from filters import getUsefulBodies

interface = SafeInterface(trashCollection, batchSize=100)

# Get unread trash and add to db
unreadTrash = getMessages(['TRASH', 'UNREAD'])

input("Press enter to continue and add to DB...")
print(f"Adding messages to DB...")
ids, bodies, usedUnreadTrash = getUsefulBodies(unreadTrash)

result = interface.add(
    ids=ids,
    metadatas=usedUnreadTrash,
    documents=bodies
)
print(f"Done adding unread trash to DB.")
print(f"Safe interface added with result: {result}")
