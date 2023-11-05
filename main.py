from MailInterface import getMessages
from DBInterface import collection


filtered = getMessages(['TRASH', 'UNREAD'])

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


print(f"Adding messages to DB...")
ids = [msg['id'] for msg in filtered]
bodies = []
for msg in filtered:
    if type(msg['body-truncated']) == str:
        bodies.append(msg['body-truncated'])
    elif len(msg['body']) > 0:
        bodies.append(msg['body'])
    elif len(msg['snippet']) > 0:
        bodies.append(msg['snippet'])
    else:
        bodies.append('NO BODY OR SNIPPET FOUND')

result = collection.add(
    ids=ids,
    metadatas=filtered,
    documents=bodies
)
print(f"Added with result: {result}")
