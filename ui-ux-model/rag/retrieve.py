"""
Retrieval helper: given a query, returns the top-k most relevant design
principles from the Chroma store built by build_knowledge_base.py.
"""

import sys
from pathlib import Path
from functools import lru_cache

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402


@lru_cache(maxsize=1)
def _get_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(config.EMBEDDING_MODEL_ID)


@lru_cache(maxsize=1)
def _get_collection():
    import chromadb
    client = chromadb.PersistentClient(path=str(config.CHROMA_PERSIST_DIR))
    try:
        return client.get_collection("design_principles")
    except Exception as e:
        raise RuntimeError(
            "Knowledge base not built yet. Run rag/build_knowledge_base.py first."
        ) from e


def retrieve(query: str, top_k: int = None) -> list[str]:
    """Returns the top_k most relevant knowledge-base snippets for the query."""
    top_k = top_k or config.RAG_TOP_K
    embedder = _get_embedder()
    collection = _get_collection()

    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    documents = results.get("documents", [[]])[0]
    return documents


if __name__ == "__main__":
    # Quick manual test: python rag/retrieve.py "e-commerce marvel theme"
    q = " ".join(sys.argv[1:]) or "e-commerce store, marvel theme"
    for i, doc in enumerate(retrieve(q), start=1):
        print(f"{i}. {doc}")
