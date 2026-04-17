"""
Vishnu Gita - Database Builder
Loads all scripture data into ChromaDB vector database
"""

import os
import json
import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = os.path.join(os.path.dirname(__file__), "raw")
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "divine_db")


def load_all_data():
    all_records = []
    files = ["mahabharata.json", "bhagavad_gita.json"]
    for fname in files:
        fpath = os.path.join(DATA_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            all_records.extend(data)
            print(f"  Loaded {len(data)} records from {fname}")
        else:
            print(f"  Skipping {fname} - not found. Run download_data.py first.")
    return all_records


def build_database():
    print("=" * 60)
    print("  Vishnu Gita - Building Vector Database")
    print("=" * 60)

    records = load_all_data()
    if not records:
        print("\nNo data found! Run download_data.py first.")
        return

    print(f"\nTotal records to index: {len(records)}")
    print("Building ChromaDB... (first time takes 3-5 mins)")

    os.makedirs(DB_DIR, exist_ok=True)

    client = chromadb.PersistentClient(path=DB_DIR)

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Delete existing collection if rebuilding
    try:
        client.delete_collection("scriptures")
    except Exception:
        pass

    collection = client.create_collection(
        name="scriptures",
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )

    # Add in batches of 100
    batch_size = 100
    added = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        docs, metas, ids = [], [], []
        for j, rec in enumerate(batch):
            text = rec.get("text", "").strip()
            if not text or len(text) < 20:
                continue
            docs.append(text[:2000])  # Cap at 2000 chars per chunk
            metas.append({
                "source": rec.get("source", "Unknown"),
                "parva": rec.get("parva", ""),
                "section": rec.get("section", "")
            })
            ids.append(f"rec_{i + j}")

        if docs:
            collection.add(documents=docs, metadatas=metas, ids=ids)
            added += len(docs)

        if (i // batch_size) % 10 == 0:
            print(f"  Progress: {min(i + batch_size, len(records))}/{len(records)} records...")

    print(f"\n Database ready! {added} passages indexed.")
    print(f"  Location: {DB_DIR}")
    print("\n Now run: cd ../backend && python main.py")
    print("=" * 60)


if __name__ == "__main__":
    build_database()
