from DBInterface import trashCollection, inboxCacheCollection, SafeInterface

THRESHOLD = 0.3
SENDER_MUST_MATCH = True

inboxResults = inboxCacheCollection.get(include=['documents', 'metadatas', 'embeddings'])

qres = trashCollection.query(
    query_embeddings=inboxResults['embeddings'],
    n_results=20
)
for i, msg in enumerate(inboxResults['metadatas']):
    sender = msg['From']
    subject = msg['Subject']
    snippet = msg['snippet']
    dollars = msg['dollar-amounts']

    dists = qres['distances'][i]
    metadata = qres['metadatas'][i]
    if SENDER_MUST_MATCH:
        validDists = [d for i, d in enumerate(dists) if d < THRESHOLD and metadata[i]['From'] == sender]
    else:
        validDists = [d for d in dists if d < THRESHOLD]
    numNeighbors = len(validDists)

    if min(dists) < THRESHOLD and numNeighbors >= 4:
        print(sender)
        print(dollars)
        print(snippet)
        print(f"NUMBER OF NEIGHBORS: {numNeighbors}")
        print(f"Average dist: {sum(validDists) / len(validDists)}")
        for j in range(min(len(qres['ids'][i]), 6)):
            dist = dists[j]
            if SENDER_MUST_MATCH:
                validNeighbor = dist < THRESHOLD and metadata[j]['From'] == sender
            else:
                validNeighbor = dist < THRESHOLD
            if validNeighbor:
                print('---')
                print('\t', dist)
                print('\t', metadata[j]['From'])
                print('\t', metadata[j]['Subject'])
                snippet = metadata[j]['snippet']
                if len(snippet) > 80:
                    snippet = snippet[:80].strip() + '...'
                print('\t', snippet)
        print('\n====================')