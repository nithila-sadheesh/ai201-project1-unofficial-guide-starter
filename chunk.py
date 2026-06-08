import json
import os
import glob

DOCUMENTS_DIR = "documents"
CHUNKS_FILE = "chunks.json"

# Word-based approximation: 1 word ≈ 1.3 tokens for English text
# 450 tokens ≈ 346 words; 75-token overlap ≈ 58 words
ARTICLE_CHUNK_WORDS = 346
ARTICLE_OVERLAP_WORDS = 58


def chunk_article(text, chunk_size=ARTICLE_CHUNK_WORDS, overlap=ARTICLE_OVERLAP_WORDS):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 0:
            chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def chunk_reddit(title, comments):
    # Each comment is its own chunk; thread title prepended for context
    chunks = []
    for comment in comments:
        if comment.strip():
            chunk = f"{title}\n\n{comment.strip()}"
            chunks.append(chunk)
    return chunks


def load_documents():
    docs = []
    for path in sorted(glob.glob(os.path.join(DOCUMENTS_DIR, "*.json"))):
        with open(path, "r", encoding="utf-8") as f:
            docs.append(json.load(f))
    return docs


def produce_chunks(documents):
    all_chunks = []
    for doc in documents:
        if doc["type"] == "article":
            texts = chunk_article(doc["content"])
            for i, text in enumerate(texts):
                all_chunks.append({
                    "id": f"{doc['name']}_{i}",
                    "source_id": doc["id"],
                    "source_name": doc["name"],
                    "source_type": "article",
                    "source_url": doc["url"],
                    "text": text,
                })
        elif doc["type"] == "reddit":
            texts = chunk_reddit(doc["title"], doc["comments"])
            for i, text in enumerate(texts):
                all_chunks.append({
                    "id": f"{doc['name']}_{i}",
                    "source_id": doc["id"],
                    "source_name": doc["name"],
                    "source_type": "reddit",
                    "source_url": doc["url"],
                    "text": text,
                })
    return all_chunks


def main():
    documents = load_documents()
    if not documents:
        print("No documents found in documents/. Run ingest.py first.")
        return

    print(f"Loaded {len(documents)} documents")

    chunks = produce_chunks(documents)
    print(f"Produced {len(chunks)} total chunks")

    article_chunks = [c for c in chunks if c["source_type"] == "article"]
    reddit_chunks = [c for c in chunks if c["source_type"] == "reddit"]
    print(f"  Article chunks: {len(article_chunks)}")
    print(f"  Reddit chunks:  {len(reddit_chunks)}")

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"\nSaved → {CHUNKS_FILE}")

    # Print a sample of each type so you can verify the output looks right
    print("\n--- Sample article chunk ---")
    if article_chunks:
        print(article_chunks[0]["text"][:500])

    print("\n--- Sample Reddit chunk ---")
    if reddit_chunks:
        print(reddit_chunks[0]["text"][:500])


if __name__ == "__main__":
    main()
