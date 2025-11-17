"""Quick test script to verify ChromaDB connection and data."""
import chromadb

client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('denso_market_intelligence')

print(f'Collection count: {collection.count()}')

results = collection.get(limit=5, include=['documents', 'metadatas'])
print(f'\nSample document IDs: {results["ids"][:3]}')
print(f'\nSample metadata:')
if results["metadatas"]:
    for key, value in results["metadatas"][0].items():
        print(f'  {key}: {value}')
print(f'\nSample document text: {results["documents"][0][:100]}...')
