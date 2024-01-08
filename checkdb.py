import chromadb

client = chromadb.PersistentClient(path='db')

for collection in client.list_collections():
    print(f"{collection.name} : {collection.count()} docs")
