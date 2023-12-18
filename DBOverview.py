import chromadb

client = chromadb.PersistentClient('db')
print(client.list_collections())

for col in client.list_collections():
    print(col.name, col.count())
