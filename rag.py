"""
rag.py
Builds a local vector store using ChromaDB.
Embeds document chunks and retrieves the most relevant ones
for a given query — this is the core RAG retrieval step.
"""
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Use a lightweight local embedding model (no API key needed)
EMBED_FN = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
COLLECTION_NAME = "business_cases"


def build_index(chunks: list[dict]) -> chromadb.Collection:
    """
    Takes document chunks and stores them in a local ChromaDB vector index.
    Re-creates the collection fresh each time (for simplicity).
    """
    client = chromadb.Client()  # in-memory, resets on restart

    # Delete if exists, then recreate
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=EMBED_FN
    )

    # Add chunks to the collection
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=[c["content"] for c in chunks],
        metadatas=[{"filename": c["filename"], "chunk_index": c["chunk_index"]} for c in chunks]
    )

    print(f"  Indexed {len(chunks)} chunks into ChromaDB")
    return collection


def retrieve(collection: chromadb.Collection, query: str, top_k: int = 4) -> list[dict]:
    """
    Embed the user query and return the top_k most relevant chunks.
    """
    results = collection.query(query_texts=[query], n_results=top_k)

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "content": results["documents"][0][i],
            "filename": results["metadatas"][0][i]["filename"],
            "distance": results["distances"][0][i] if results.get("distances") else None
        })
    return chunks


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a single context string for the LLM."""
    parts = []
    for c in chunks:
        parts.append(f"[Source: {c['filename']}]\n{c['content']}")
    return "\n\n---\n\n".join(parts)