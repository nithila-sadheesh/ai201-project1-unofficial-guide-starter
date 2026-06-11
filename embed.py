import json
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHUNKS_FILE = "chunks.json"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "berkeley_guide"


def main():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Drop existing collection so re-runs don't hit duplicate ID errors
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Dropped existing collection (re-run detected)")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["id"])
        documents.append(chunk["text"])
        metadatas.append({
            "source_name": chunk["source_name"],
            "source_type": chunk["source_type"],
            "source_url": chunk["source_url"],
            "source_id": chunk["source_id"],
            # chunk position within its source document
            "chunk_index": int(chunk["id"].split("_")[-1]),
        })

    # Add in batches of 100 to stay within ChromaDB limits
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )
        print(f"  Stored chunks {i}–{min(i + batch_size, len(ids)) - 1}")

    print(f"\nDone. {collection.count()} chunks embedded and stored in {CHROMA_DIR}/")


if __name__ == "__main__":
    main()
