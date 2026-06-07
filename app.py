"""
app.py — Milestone 5: Generation + Interface
The Unofficial Guide (CSUF CS professor/course reviews)

Pipeline stages 4-5 (per planning.md Architecture):
  4. RETRIEVAL   — retrieve(question) from embed.py returns the top-k chunks + metadata
  5. GENERATION  — feed question + retrieved chunks to Groq (llama-3.3-70b-versatile)
                   with a STRICT grounding prompt, then show answer + source list

THE GROUNDING CONTRACT (the whole point of this milestone):
  - The LLM is told, in the SYSTEM prompt, to answer ONLY from the provided reviews
    and to say so when the reviews don't cover the question. This is enforced as a
    rule, not a polite suggestion (temperature is low and the rules are explicit).
  - SOURCE ATTRIBUTION IS NOT LEFT TO THE LLM. build_sources() constructs the source
    list in Python directly from the metadata of the exact chunks we retrieved, so
    every answer is attributed correctly even if the model says nothing about sources.

Run (Milestone 5 later step, after `pip install gradio`):
    .venv\\Scripts\\python.exe app.py
"""

import os

from dotenv import load_dotenv
from groq import Groq

from embed import retrieve, TOP_K

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
load_dotenv()  # reads GROQ_API_KEY from .env

GROQ_MODEL = "llama-3.3-70b-versatile"   # per planning.md
TEMPERATURE = 0.2                        # low -> stays close to the provided reviews
MAX_TOKENS = 700

_client = None


def get_client():
    """Lazily create the Groq client (fails clearly if the API key is missing)."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _client = Groq(api_key=api_key)
    return _client


# ---------------------------------------------------------------------------
# GROUNDING PROMPT
# ---------------------------------------------------------------------------
# This is the system prompt. It ENFORCES grounding: the model is restricted to the
# CONTEXT, ordered to refuse when the context is insufficient, and forbidden from
# inventing details. It is not a gentle "please try to use the context" hint.
SYSTEM_PROMPT = """You are "The Unofficial Guide," a question-answering assistant about \
Computer Science professors and courses at Cal State Fullerton (CSUF). You answer using \
ONLY the student reviews provided in the CONTEXT section of the user's message.

STRICT RULES — follow all of them:
1. Use ONLY information found in the CONTEXT. Do NOT use any outside or prior knowledge \
about these professors, courses, or CSUF. If you happen to "know" something that is not \
in the CONTEXT, do not use it.
2. If the CONTEXT does not contain enough information to answer the question, reply \
exactly: "The student reviews I have don't cover that." Do not guess or fill gaps.
3. Never invent professors, course numbers, grades, dates, ratings, or quotes. Every \
claim must be supported by the CONTEXT.
4. If a review carries a provenance or reliability caveat (for example, a note that it \
is an AI-generated summary or mixes sources from another school), reflect that caveat \
in your answer instead of stating it as established fact.
5. Be concise and specific. Summarize what students actually said; attribute to the \
professor/course when the question compares more than one.

You do NOT need to list sources yourself — the application attaches the source list \
automatically and exactly."""


def build_context(hits):
    """Turn retrieved chunks into a numbered CONTEXT block for the prompt.

    Numbering ([1], [2], ...) lines up with build_sources() so the answer and the
    attached source list refer to the same chunks in the same order.
    """
    blocks = []
    for i, h in enumerate(hits, start=1):
        m = h["metadata"]
        label = f"[{i}] (source: {m['source_file']}, {m['professor_or_topic']}, course {m['course']})"
        blocks.append(f"{label}\n{h['text']}")
    return "\n\n".join(blocks)


def generate_answer(question, hits):
    """Call Groq with the grounding prompt and the retrieved context. Returns text only.

    The source list is built separately and programmatically (see build_sources);
    nothing here depends on the model choosing to cite anything.
    """
    context = build_context(hits)
    user_message = (
        f"CONTEXT (student reviews — your only source of truth):\n\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        f"Answer using ONLY the context above. If it doesn't cover the question, say so."
    )

    client = get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content.strip()


def build_sources(hits):
    """Build the source list IN CODE from chunk metadata — not from the LLM.

    Returns a LIST of one-line strings (one per retrieved chunk) so the UI can show
    them as bullets. This guarantees attribution: every answer is backed by the exact
    chunks that were retrieved, named by their real source filename and position.
    """
    sources = []
    for i, h in enumerate(hits, start=1):
        m = h["metadata"]
        sources.append(
            f"[{i}] {m['source_file']} — chunk {m['chunk_index']} of {m['chunk_count']} "
            f"({m['professor_or_topic']}, course {m['course']})"
        )
    return sources


def ask(question):
    """End-to-end RAG turn. Returns {'answer': str, 'sources': [str, ...]}.

    This is the single function the interface (or a CLI/tests) calls:
      retrieve (stage 4) -> generate grounded answer (stage 5) -> code-built sources.
    """
    question = (question or "").strip()
    if not question:
        return {"answer": "Please type a question about a CSUF CS professor or course.",
                "sources": []}

    hits = retrieve(question, k=TOP_K)          # stage 4
    if not hits:
        return {"answer": "No reviews are indexed yet. Run `python embed.py` first.",
                "sources": []}

    answer = generate_answer(question, hits)    # stage 5 (grounded)
    sources = build_sources(hits)               # attribution, guaranteed in code
    return {"answer": answer, "sources": sources}


# ---------------------------------------------------------------------------
# GRADIO INTERFACE
# ---------------------------------------------------------------------------
def handle_query(question):
    """Adapt ask() to the UI: return (answer_text, sources_text) for the two boxes."""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


def build_ui():
    """Minimal Gradio UI: a question box, an Ask button, and Answer + Sources boxes."""
    import gradio as gr  # imported here so the rest of the module works without gradio

    with gr.Blocks(title="The Unofficial Guide — CSUF CS Reviews") as demo:
        gr.Markdown(
            "# The Unofficial Guide\n"
            "Ask what CSUF CS students actually say about professors and courses. "
            "Answers come **only** from the collected student reviews — the documents "
            "each answer is drawn from are listed under *Retrieved from*."
        )
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. How are exams structured in Kenneth Kung's classes?",
            lines=2,
        )
        btn = gr.Button("Ask", variant="primary")
        answer = gr.Textbox(label="Answer", lines=8)
        sources = gr.Textbox(label="Retrieved from", lines=5)

        # Both the button and pressing Enter run the same end-to-end query.
        btn.click(handle_query, inputs=inp, outputs=[answer, sources])
        inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

        gr.Examples(
            examples=[
                "What do students say about exam format and difficulty in Professor Panangadan's CPSC 481?",
                "How are exams structured in Kenneth Kung's classes?",
                "Which CPSC professors do students recommend avoiding, and why?",
            ],
            inputs=inp,
        )

    return demo


def main():
    build_ui().launch()


if __name__ == "__main__":
    main()
