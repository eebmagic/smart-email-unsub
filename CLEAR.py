import chromadb
client = chromadb.PersistentClient('db')
print(f"Before: {client.list_collections()}")
for col in client.list_collections():
    print(f"Removing: {col.name}")
    client.delete_collection(col.name)
print(f"After: {client.list_collections()}")
