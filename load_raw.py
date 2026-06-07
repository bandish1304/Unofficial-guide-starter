"""
load_raw.py — Step 1: Load all documents and save the RAW text to a consistent format.

This is the FIRST stage of the pipeline (planning.md Architecture, stage 1).
Its only job is to get every source document into one consistent file, EXACTLY as
it sits on disk, before any cleaning or chunking happens.

Why a separate "raw" stage?
  - My sources are local .txt files (10 of them: 6 Rate My Professors + 4 Reddit),
    captured by hand from the URLs listed in planning.md. Since they're already on
    disk, "loading" means reading them from disk — I'm not scraping live URLs.
  - Saving the raw text untouched gives me a single, reproducible snapshot. If a
    cleaning rule later turns out to be too aggressive, I can re-run from this raw
    file instead of re-collecting the documents.
  - clean_text() / chunking live in ingest.py and read FROM this raw output, so the
    "load" step and the "clean" step stay cleanly separated.

Output: raw_documents.json — a list of records, one per source file:
    {
      "filename":    "rmp_kung_kenneth.txt",
      "source_type": "rmp" | "reddit" | "unknown",
      "path":        "<absolute path>",
      "char_count":  4710,
      "raw_text":    "<file contents, completely unmodified>"
    }
"""

import os
import json

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "raw_documents.json")


def classify(filename):
    """Decide the source type from the filename prefix (matches planning.md)."""
    if filename.startswith("rmp_"):
        return "rmp"
    if filename.startswith("reddit_"):
        return "reddit"
    return "unknown"


def load_raw_documents(docs_dir):
    """Read every .txt file in documents/ into a list of raw records.

    The text is stored VERBATIM — no normalizing, no stripping, no chunking.
    Cleaning is a separate, later stage (clean_text in ingest.py).
    """
    documents = []
    for filename in sorted(os.listdir(docs_dir)):
        # Only the actual source documents; skip .gitkeep and the _*.md notes.
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(docs_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()  # exactly as on disk — do NOT touch it here

        documents.append({
            "filename": filename,
            "source_type": classify(filename),
            "path": os.path.abspath(path),
            "char_count": len(raw_text),
            "raw_text": raw_text,
        })
    return documents


def main():
    documents = load_raw_documents(DOCS_DIR)

    print("=" * 70)
    print("RAW DOCUMENT LOAD")
    print("=" * 70)
    for doc in documents:
        print(f"  {doc['filename']:<35} type={doc['source_type']:<7} "
              f"chars={doc['char_count']}")

    rmp = sum(1 for d in documents if d["source_type"] == "rmp")
    reddit = sum(1 for d in documents if d["source_type"] == "reddit")
    print(f"\n  Loaded {len(documents)} documents  "
          f"({rmp} RMP + {reddit} Reddit)")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    print(f"  Saved raw text -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
