"""
test_retrieval.py — Milestone 4, Step 5: Test retrieval before generation
The Unofficial Guide (CSUF CS professor/course reviews)

Runs the evaluation-plan questions from planning.md through retrieve() and prints,
for each hit: the distance score, the source, and an excerpt of the chunk text —
so we can answer the only question that matters here: "are these actually relevant?"

Reading the distance scores (cosine; lower = closer):
  ~0.30-0.45  strong, on-topic match
  ~0.45-0.55  loosely related — usable but watch for drift
  >0.55       weak; likely off-topic for this corpus

Run it (use the venv's Python):
    .venv\\Scripts\\python.exe test_retrieval.py
"""

from embed import retrieve, TOP_K

# The 5 questions from planning.md (Evaluation Plan), each paired with the
# professor/source the right chunks SHOULD come from, so we can judge relevance.
EVAL = [
    ("What do students say about exam format and difficulty in Professor Panangadan's CPSC 481?",
     "Panangadan"),
    ("What is the difference in student opinion of Alireza Abdoli between CPSC 449 and CPSC 481?",
     "Abdoli"),
    ("How are exams structured in Kenneth Kung's classes?",
     "Kung"),
    ("What should students expect from the group project and participation grading in Kanika Sood's CPSC 483?",
     "Sood"),
    ("Which CPSC professors do students recommend avoiding, and why?",
     "avoid"),
]


def excerpt(text, n=220):
    """One-line excerpt of a chunk, with the header line kept for context."""
    return " ".join(text.split())[:n]


def run():
    for qi, (query, expect) in enumerate(EVAL, start=1):
        hits = retrieve(query, k=TOP_K)
        print("\n" + "=" * 84)
        print(f"Q{qi}: {query}")
        print(f"     (relevant chunks should be about: {expect})")
        print("=" * 84)

        for rank, h in enumerate(hits, start=1):
            m = h["metadata"]
            print(f"\n  [{rank}] distance: {h['distance']:.3f}")
            print(f"      source : {m['source']} — {m['source_file']} "
                  f"(chunk {m['chunk_index']} of {m['chunk_count']})")
            print(f"      about  : {m['professor_or_topic'][:55]} | course {m['course']}")
            print(f"      text   : {excerpt(h['text'])} ...")


if __name__ == "__main__":
    run()
