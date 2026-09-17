"""
Embeds rag/knowledge_base/design_principles.jsonl into a local Chroma vector
store. Run this once (and again whenever you edit the knowledge base file).

This step is CPU-only and free — no GPU rental needed for RAG.

Usage:
    python rag/build_knowledge_base.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402


def load_knowledge_base() -> list[dict]:
    docs = []
    with open(config.KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def main():
    import chromadb
    from sentence_transformers import SentenceTransformer

    docs = load_knowledge_base()
    if not docs:
        print(f"No documents found in {config.KNOWLEDGE_BASE_FILE}", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded {len(docs)} knowledge base entries.")

    print(f"Loading embedding model: {config.EMBEDDING_MODEL_ID} ...")
    embedder = SentenceTransformer(config.EMBEDDING_MODEL_ID)

    texts = [d["text"] for d in docs]
    ids = [d["id"] for d in docs]
    metadatas = [{"topic": d["topic"]} for d in docs]

    print("Computing embeddings...")
    embeddings = embedder.encode(texts, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=str(config.CHROMA_PERSIST_DIR))
    # Reset the collection each run so re-running this script after editing
    # the knowledge base doesn't leave stale/duplicate entries behind.
    try:
        client.delete_collection("design_principles")
    except Exception:
        pass
    collection = client.create_collection("design_principles")

    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    print(f"Stored {len(docs)} embeddings in {config.CHROMA_PERSIST_DIR}")


if __name__ == "__main__":
    main()
