import chromadb
client = chromadb.PersistentClient('db')

print(client.list_collections())

for col in client.list_collections():
    print(col.name)
    results = col.get(include=['documents'])
    docs = results['documents']
    lens = [len(d) for d in docs]
    if lens:
        print('min max avg')
        print(min(lens), max(lens), sum(lens) / len(lens))
