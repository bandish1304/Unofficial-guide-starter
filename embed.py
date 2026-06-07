"""
embed.py — Milestone 4: Embedding + Vector Store + Retrieval
The Unofficial Guide (CSUF CS professor/course reviews)

Two jobs (per planning.md Architecture, stages 3-4):
  3. EMBEDDING + VECTOR STORE — turn each chunk into a vector and store it in ChromaDB
  4. RETRIEVAL                — embed a question and pull back the top-k closest chunks

Retrieval Approach (from planning.md):
  - Embedding model: all-MiniLM-L6-v2  (via sentence-transformers)
  - Vector store:    ChromaDB          (persisted to ./chroma_db so it survives restarts)
  - Top-k:           5

Why the chunk text already carries the professor name:
  ingest.py prepends "Professor: <name>" / "Reddit thread: <topic>" to every chunk.
  That means the professor identity is *inside the embedded text*, so a query like
  "How are Kung's exams?" can match Kung's reviews even though the review body itself
  never repeats his name. We also copy that into metadata for attribution.

Run it directly to (re)build the index and run a couple of evaluation questions:
    python embed.py
"""

import os
import json

import chromadb
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
CHUNKS_FILE = os.path.join(BASE_DIR, "chunks.json")     # output of ingest.py (Milestone 3)
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")        # where ChromaDB persists to disk

COLLECTION_NAME = "unofficial_guide"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5


# ---------------------------------------------------------------------------
# EMBEDDING MODEL (loaded once, then reused)
# ---------------------------------------------------------------------------
# SentenceTransformer downloads the model the first time (~90 MB) and caches it.
# We keep one instance at module level so we don't reload it on every query — the
# SAME model must embed both the chunks and the questions, or the vectors wouldn't
# live in the same space and the distances would be meaningless.
_model = None


def get_model():
    """Lazily load (and cache) the all-MiniLM-L6-v2 embedding model."""
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBED_MODEL_NAME} ...")
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def embed_texts(texts):
    """Embed a list of strings into a list of vectors (Python lists, ready for Chroma).

    normalize_embeddings=True scales every vector to length 1. Combined with the
    cosine distance space we set on the collection, this makes "how similar are
    these two pieces of text?" depend only on their direction, not their length.
    """
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()


# ---------------------------------------------------------------------------
# STAGE 3 — BUILD THE VECTOR STORE
# ---------------------------------------------------------------------------
def build_index(reset=True):
    """Load chunks.json, embed every chunk, and store them in a ChromaDB collection.

    reset=True wipes any existing collection first, so re-running gives a clean
    index instead of duplicating chunks (collection.add would error on repeat ids).
    """
    # 1. Load the chunks produced by the ingestion pipeline (Milestone 3).
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks from {os.path.basename(CHUNKS_FILE)}")

    # 2. Pull the three parallel lists ChromaDB wants. Index i lines up across all
    #    three: ids[i] <-> documents[i] <-> metadatas[i] <-> embeddings[i].
    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # 3. Embed all chunk texts in one batch.
    print("Embedding chunks ...")
    embeddings = embed_texts(documents)

    # 4. Open a *persistent* ChromaDB on disk (survives between runs).
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # 5. Start clean so re-runs don't pile up duplicate ids.
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection didn't exist yet — fine on a first run

    # 6. Create the collection. hnsw:space="cosine" tells Chroma to rank results by
    #    cosine distance, which is the right metric for sentence-transformer vectors.
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # 7. Store everything. We pass our OWN embeddings, so Chroma never has to embed
    #    anything itself — it just indexes the vectors and keeps the text + metadata.
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB collection "
          f"'{COLLECTION_NAME}' (persisted to {os.path.basename(CHROMA_DIR)}/)")
    return collection


# ---------------------------------------------------------------------------
# STAGE 4 — RETRIEVAL
# ---------------------------------------------------------------------------
def get_collection():
    """Open the already-built collection for querying."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION_NAME)


def retrieve(query, k=TOP_K):
    """Embed `query` and return the k closest chunks as a list of dicts.

    Each hit: {id, text, metadata, distance}.
    Lower distance = more similar (0.0 = identical direction under cosine).
    """
    collection = get_collection()

    # Embed the question with the SAME model used for the chunks.
    query_embedding = embed_texts([query])  # one-element list -> one vector

    # Ask Chroma for the k nearest chunks. Results come back as parallel lists
    # wrapped one level deep (one inner list per query); we sent one query, so
    # everything we want is at index [0].
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
    )

    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return hits


# ---------------------------------------------------------------------------
# SMOKE TEST — retrieval must return relevant chunks before Milestone 5
# ---------------------------------------------------------------------------
def _print_hits(query, hits):
    print("\n" + "=" * 78)
    print(f"QUERY: {query}")
    print("=" * 78)
    for rank, h in enumerate(hits, start=1):
        meta = h["metadata"]
        preview = h["text"].replace("\n", " ")[:160]
        print(f"\n[{rank}] distance={h['distance']:.4f}  "
              f"({meta['doc_type']}) {meta['professor_or_topic'][:60]}")
        print(f"    course={meta['course']}  file={meta['source_file']}")
        print(f"    {preview} ...")


def main():
    # Build the index from scratch.
    build_index(reset=True)

    # Two evaluation questions from planning.md. The right professor's reviews
    # should come back at the top — that's the bar for moving to Milestone 5.
    for q in [
        "What do students say about exam format and difficulty in Professor Panangadan's CPSC 481?",
        "How are exams structured in Kenneth Kung's classes?",
    ]:
        _print_hits(q, retrieve(q))


if __name__ == "__main__":
    main()
