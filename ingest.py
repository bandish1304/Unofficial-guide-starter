"""
ingest.py — Milestone 3: Document Ingestion + Chunking
The Unofficial Guide (CSUF CS professor/course reviews)

Two jobs (per planning.md Architecture, stages 1-2):
  1. INGESTION — read every .txt file in documents/ into memory
  2. CHUNKING  — split each document into chunks for the embedding model

Chunking Strategy (from planning.md):
  - RMP files (rmp_*.txt)    -> 1 review per chunk  (split on "--- Review N ---")
  - Reddit files (reddit_*)  -> 1 file   per chunk  (the whole captured page is one chunk;
                                some files bundle a few short related threads on purpose)
  - Overlap: 0  (each review / Reddit page is already a standalone unit)

Critical rule (from _STRUCTURE_NOTES.md):
  The professor name and course code MUST stay attached to every chunk, because
  the review text itself never repeats the professor's name. Without this,
  retrieval for "Kung's exams" can't tell whose exams a chunk is about.
"""

import os
import re
import json
import unicodedata

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "chunks.json")


# ---------------------------------------------------------------------------
# STAGE 1 — INGESTION (+ CLEANING)
# ---------------------------------------------------------------------------
# Light, conservative cleaning. The chunker depends on the "--- Review N ---" /
# "--- Thread N ---" markers and on blank lines between fields, so cleaning must
# NOT touch those. It only normalizes invisible/inconsistent characters that
# would otherwise make near-identical text embed differently.
SMART_QUOTES = {
    "‘": "'", "’": "'",   # ‘ ’  -> '
    "“": '"', "”": '"',   # “ ”  -> "
    "—": "-", "–": "-",   # — –  -> -   (also fixes the console "?" display)
    "…": "...",                # …    -> ...
}


def clean_text(raw_text):
    """Normalize a raw document before parsing/chunking.

    Steps (all order-preserving, none change line/block structure):
      1. Unicode NFKC normalize (collapses look-alike codepoints).
      2. Map smart quotes / dashes / ellipsis to plain ASCII.
      3. Normalize line endings (\\r\\n, \\r -> \\n).
      4. Replace non-breaking / odd spaces with a regular space.
      5. Strip trailing whitespace on each line.
      6. Collapse 3+ blank lines down to a single blank line.
    """
    text = unicodedata.normalize("NFKC", raw_text)

    for bad, good in SMART_QUOTES.items():
        text = text.replace(bad, good)

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace(" ", " ").replace("​", "")  # nbsp, zero-width

    # Strip trailing spaces/tabs per line (keeps the newlines themselves).
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Collapse runs of 3+ newlines (2+ blank lines) into one blank line.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_header(raw_text):
    """Pull the 3-line header (SOURCE / PROFESSOR-TOPIC / URL) off the top of a file.

    Returns (header_dict, body_text) where body_text is everything after the header.
    """
    lines = raw_text.splitlines()
    header = {"source": "", "topic": "", "url": ""}
    body_start = 0

    for i, line in enumerate(lines[:5]):  # header is in the first few lines
        upper = line.upper()
        if upper.startswith("SOURCE:"):
            header["source"] = line.split(":", 1)[1].strip()
            body_start = i + 1
        elif upper.startswith("PROFESSOR/TOPIC:"):
            header["topic"] = line.split(":", 1)[1].strip()
            body_start = i + 1
        elif upper.startswith("URL:"):
            header["url"] = line.split(":", 1)[1].strip()
            body_start = i + 1

    body = "\n".join(lines[body_start:]).strip()
    return header, body


def load_documents(docs_dir):
    """Read every .txt file in documents/ into a list of dicts.

    Each doc: {filename, doc_type, source, topic, url, body}
    doc_type is decided by the filename prefix (rmp_ vs reddit_).
    """
    documents = []
    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith(".txt"):
            continue  # skip .gitkeep, _COLLECTION_GUIDE.md, etc.

        path = os.path.join(docs_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned_text = clean_text(raw_text)        # <-- cleaning stage
        header, body = parse_header(cleaned_text)

        if filename.startswith("rmp_"):
            doc_type = "rmp"
        elif filename.startswith("reddit_"):
            doc_type = "reddit"
        else:
            doc_type = "unknown"

        documents.append({
            "filename": filename,
            "doc_type": doc_type,
            "source": header["source"],
            "topic": header["topic"],
            "url": header["url"],
            "body": body,
        })
    return documents


# ---------------------------------------------------------------------------
# STAGE 2 — CHUNKING
# ---------------------------------------------------------------------------
REVIEW_MARKER = re.compile(r"^--- Review \d+ ---\s*$", re.MULTILINE)
COURSE_LINE = re.compile(r"Course:\s*([A-Z]{2,4}\s?\d{3})", re.IGNORECASE)


def chunk_rmp(doc):
    """RMP file -> one chunk per '--- Review N ---' block.

    Each chunk text is prefixed with the professor name so the professor stays
    attached to the review (the review body never names the professor itself).
    The course code is pulled into metadata for filtering/attribution.
    """
    chunks = []
    # Split the body on the review markers; drop the empty piece before Review 1.
    parts = [p.strip() for p in REVIEW_MARKER.split(doc["body"]) if p.strip()]

    for i, review_body in enumerate(parts, start=1):
        course_match = COURSE_LINE.search(review_body)
        course = course_match.group(1).upper().replace("  ", " ") if course_match else "Unknown"

        # Prepend professor identity so the embedding "knows" whose review this is.
        text = f"Professor: {doc['topic']}\n{review_body}"

        chunks.append({
            "id": f"{doc['filename'].replace('.txt', '')}_review_{i}",
            "text": text,
            "metadata": {
                "source": doc["source"],
                "professor_or_topic": doc["topic"],
                "course": course,
                "url": doc["url"],
                "doc_type": "rmp",
                "source_file": doc["filename"],
            },
        })
    return chunks


def chunk_reddit(doc):
    """Reddit file -> ONE chunk for the whole captured page (1 file = 1 chunk, overlap 0).

    Most files are a single thread; a few bundle several short related threads
    about the same professor, kept together on purpose so the full conversation
    stays intact. The topic (which names the professor/class) is prefixed so the
    chunk is self-describing during retrieval.
    """
    text = f"Reddit thread: {doc['topic']}\n{doc['body']}"
    return [{
        "id": f"{doc['filename'].replace('.txt', '')}_thread",
        "text": text,
        "metadata": {
            "source": doc["source"],
            "professor_or_topic": doc["topic"],
            "course": "Unknown",  # threads often span several courses
            "url": doc["url"],
            "doc_type": "reddit",
            "source_file": doc["filename"],
        },
    }]


def chunk_document(doc):
    """Dispatch to the right chunker based on doc_type."""
    if doc["doc_type"] == "rmp":
        return chunk_rmp(doc)
    elif doc["doc_type"] == "reddit":
        return chunk_reddit(doc)
    else:
        # Fallback: treat the whole file as one chunk so nothing is silently lost.
        return [{
            "id": f"{doc['filename'].replace('.txt', '')}_whole",
            "text": doc["body"],
            "metadata": {
                "source": doc["source"],
                "professor_or_topic": doc["topic"],
                "course": "Unknown",
                "url": doc["url"],
                "doc_type": "unknown",
                "source_file": doc["filename"],
            },
        }]


def build_chunks(documents):
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    return all_chunks


# ---------------------------------------------------------------------------
# STAGE 3 — INSPECTION (do NOT skip this — milestone 3 requires it)
# ---------------------------------------------------------------------------
def inspect(documents, chunks):
    print("=" * 70)
    print("INGESTION SUMMARY")
    print("=" * 70)
    for doc in documents:
        print(f"  {doc['filename']:<35} type={doc['doc_type']:<7} "
              f"body_chars={len(doc['body'])}")
    print(f"\n  Loaded {len(documents)} documents.\n")

    print("=" * 70)
    print("CHUNKING SUMMARY")
    print("=" * 70)
    rmp_chunks = [c for c in chunks if c["metadata"]["doc_type"] == "rmp"]
    reddit_chunks = [c for c in chunks if c["metadata"]["doc_type"] == "reddit"]
    print(f"  Total chunks:  {len(chunks)}")
    print(f"  RMP chunks:    {len(rmp_chunks)}  (one per review)")
    print(f"  Reddit chunks: {len(reddit_chunks)}  (one per thread)")

    lengths = [len(c["text"]) for c in chunks]
    print(f"  Chunk size (chars): min={min(lengths)}  "
          f"max={max(lengths)}  avg={sum(lengths)//len(lengths)}")

    print("\n" + "=" * 70)
    print("SAMPLE CHUNKS (eyeball these — is each one a clean, standalone unit?)")
    print("=" * 70)
    # Show one RMP review and one Reddit thread so we can verify nothing got cut.
    for sample in [rmp_chunks[0] if rmp_chunks else None,
                   reddit_chunks[0] if reddit_chunks else None]:
        if not sample:
            continue
        print(f"\n--- id: {sample['id']} ---")
        print(f"metadata: {sample['metadata']}")
        print("text:")
        print(sample["text"])
        print("-" * 70)


def main():
    documents = load_documents(DOCS_DIR)
    chunks = build_chunks(documents)
    inspect(documents, chunks)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(chunks)} chunks -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
