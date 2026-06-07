"""
debug_retrieval.py — Milestone 4, Step 6: Retrieval debugging checklist
The Unofficial Guide (CSUF CS professor/course reviews)

Runs the five diagnostics from the milestone step, even though step 5 looked
healthy — the point is to PROVE there's no hidden problem, not assume:

  1. Print a retrieved chunk IN FULL  -> real relevant content, or just shared words?
  2. Distance scores                  -> anything above ~0.6-0.7 = weak match
  3. Chunk content                    -> fragments / HTML leftovers = bad cleaning/chunking
  4. Metadata                         -> right source filename stored on every chunk?
  5. Chunk size                       -> are any chunks too short to carry semantic signal?

Run with the venv's Python:
    .venv\\Scripts\\python.exe debug_retrieval.py
"""

import os
import re
import json

from embed import retrieve, get_collection

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
HIGH_DISTANCE = 0.6   # threshold the milestone flags as a weak match
SHORT_CHUNK = 200     # chars below which a chunk may lack semantic signal
HTML_TAG = re.compile(r"<[a-zA-Z/][^>]*>")


def check_1_print_full_chunk():
    print("\n" + "#" * 84)
    print("# CHECK 1 — print a retrieved chunk IN FULL (relevant, or just shared words?)")
    print("#" * 84)
    q = "What do students say about exam format and difficulty in Professor Panangadan's CPSC 481?"
    top = retrieve(q, k=1)[0]
    print(f"query   : {q}")
    print(f"distance: {top['distance']:.3f}")
    print(f"source  : {top['metadata']['source_file']} "
          f"(chunk {top['metadata']['chunk_index']} of {top['metadata']['chunk_count']})")
    print("FULL CHUNK TEXT:")
    print("-" * 84)
    print(top["text"])
    print("-" * 84)


def check_2_distances():
    print("\n" + "#" * 84)
    print(f"# CHECK 2 — distance scores (flag anything >= {HIGH_DISTANCE})")
    print("#" * 84)
    queries = [
        "What do students say about exam format and difficulty in Professor Panangadan's CPSC 481?",
        "What is the difference in student opinion of Alireza Abdoli between CPSC 449 and CPSC 481?",
        "How are exams structured in Kenneth Kung's classes?",
        "What should students expect from the group project and participation grading in Kanika Sood's CPSC 483?",
        "Which CPSC professors do students recommend avoiding, and why?",
    ]
    worst_top1 = 0.0
    flagged = 0
    for q in queries:
        hits = retrieve(q, k=5)
        top1 = hits[0]["distance"]
        worst_top1 = max(worst_top1, top1)
        all_d = [round(h["distance"], 3) for h in hits]
        flagged += sum(1 for d in all_d if d >= HIGH_DISTANCE)
        print(f"  top1={top1:.3f}  top5={all_d}  | {q[:46]}...")
    print(f"\n  worst top-1 distance across all queries: {worst_top1:.3f} "
          f"({'OK — well under 0.6' if worst_top1 < HIGH_DISTANCE else 'WEAK'})")
    print(f"  total hits >= {HIGH_DISTANCE} (weak matches): {flagged}")


def check_3_and_5_content_and_size():
    print("\n" + "#" * 84)
    print("# CHECK 3 & 5 — chunk content (HTML/fragments?) and chunk size")
    print("#" * 84)
    chunks = json.load(open(os.path.join(os.path.dirname(__file__), "chunks.json"),
                             encoding="utf-8"))
    html_hits = [c["id"] for c in chunks if HTML_TAG.search(c["text"])]
    lengths = [len(c["text"]) for c in chunks]
    short = [(c["id"], len(c["text"])) for c in chunks if len(c["text"]) < SHORT_CHUNK]
    print(f"  chunks with HTML tags: {len(html_hits)} {html_hits if html_hits else ''}")
    print(f"  chunk length (chars): min={min(lengths)} max={max(lengths)} "
          f"avg={sum(lengths)//len(lengths)}")
    print(f"  chunks shorter than {SHORT_CHUNK} chars: {len(short)} {short if short else ''}")


def check_4_metadata():
    print("\n" + "#" * 84)
    print("# CHECK 4 — metadata: correct source filename stored on every chunk?")
    print("#" * 84)
    col = get_collection()
    md = col.get(include=["metadatas"])["metadatas"]
    real_files = set(os.listdir(DOCS_DIR))
    missing_file = [m["source_file"] for m in md if m["source_file"] not in real_files]
    prefix_ok = all(
        (m["doc_type"] == "rmp" and m["source_file"].startswith("rmp_")) or
        (m["doc_type"] == "reddit" and m["source_file"].startswith("reddit_")) or
        (m["doc_type"] not in ("rmp", "reddit"))
        for m in md
    )
    print(f"  chunks whose source_file is NOT a real file in documents/: {len(missing_file)}")
    print(f"  doc_type matches filename prefix on every chunk: {prefix_ok}")
    print(f"  distinct source files represented: {len(set(m['source_file'] for m in md))}")


if __name__ == "__main__":
    check_1_print_full_chunk()
    check_2_distances()
    check_3_and_5_content_and_size()
    check_4_metadata()
