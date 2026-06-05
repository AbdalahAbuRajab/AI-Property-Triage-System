from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer

app = FastAPI(title="RAG Service")


class QueryInput(BaseModel):
    description: str


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "property_listings"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


@app.get("/")
def root():
    return {
        "message": "RAG Service Running with ChromaDB",
        "collection": COLLECTION_NAME
    }


@app.post("/query")
def query_similar_listings(data: QueryInput):
    query_embedding = model.encode(data.description).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    similar_listings = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        similar_listings.append({
            "document": document,
            "metadata": metadata,
            "similarity_distance": distance
        })

    insight = (
        "The RAG service used ChromaDB vector search to retrieve the most semantically "
        "similar property listings based on the submitted description."
    )

    return {
        "similar_listings": similar_listings,
        "insight": insight
    }