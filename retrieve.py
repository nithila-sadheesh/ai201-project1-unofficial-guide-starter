import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "berkeley_guide"

# Initialize once at module level so generate.py can import retrieve() cheaply
_ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
_client = chromadb.PersistentClient(path=CHROMA_DIR)
_collection = _client.get_collection(name=COLLECTION_NAME, embedding_function=_ef)


def retrieve(query, k=5):
    """Return the k most similar chunks to query, with source metadata."""
    results = _collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "source_name": meta["source_name"],
            "source_type": meta["source_type"],
            "source_url": meta["source_url"],
            "chunk_index": meta["chunk_index"],
            "similarity": round(1 - distance, 4),  # cosine distance → similarity score
        })
    return chunks


if __name__ == "__main__":
    # Sanity check: run all 5 evaluation questions and inspect retrieved chunks
    TEST_QUERIES = [
        "If studying EECS, how many technical classes is it recommended to take each semester?",
        "What is Berkeleytime and by how many minutes do Berkeley classes actually start after their listed time?",
        "How early should students schedule a same-day CAPS counseling appointment to guarantee they are seen?",
        "What specific locations near Berkeley campus do students warn to avoid walking through late at night?",
        "When cramming for Berkeley finals, which part of the semester's content should students prioritize reviewing first, and why?",
    ]

    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 70)
        for chunk in retrieve(query):
            print(f"[{chunk['source_name']} | chunk {chunk['chunk_index']} | distance: {round(1 - chunk['similarity'], 4)}]")
            print(chunk["text"][:300])
            print()
