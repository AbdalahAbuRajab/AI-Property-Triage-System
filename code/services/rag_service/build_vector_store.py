import chromadb
from sentence_transformers import SentenceTransformer
from listings_data import property_listings

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "property_listings"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)

try:
    client.delete_collection(name=COLLECTION_NAME)
except Exception:
    pass

collection = client.get_or_create_collection(name=COLLECTION_NAME)

for listing in property_listings:
    text = (
        f"Title: {listing['title']}. "
        f"Location: {listing['location']}. "
        f"Type: {listing['property_type']}. "
        f"Price: {listing['price']}. "
        f"Features: {', '.join(listing['features'])}."
    )

    embedding = model.encode(text).tolist()

    collection.add(
        ids=[str(listing["id"])],
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "id": listing["id"],
            "title": listing["title"],
            "location": listing["location"],
            "property_type": listing["property_type"],
            "price": listing["price"],
            "features": ", ".join(listing["features"])
        }]
    )

print(f"Added {len(property_listings)} listings to ChromaDB.")