import chromadb

client = chromadb.PersistentClient(path='db')

for collection in client.list_collections():
    print(f"{collection.name} : {collection.count()} docs")
    confirm = input(f"Delete collection {collection.name}? (y/N): ").strip()[0].lower()
    if confirm == 'y':
        client.delete_collection(collection.name)

print(f"\nCollections after: {client.list_collections()}")