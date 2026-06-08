# The Unofficial Guide — Project 1

A small RAG system that answers questions about Computer Science professors and courses at Cal State Fullerton, using what students actually wrote in reviews instead of the official catalog. You type a question, it pulls the most relevant reviews out of a vector store, and a language model writes an answer that's only allowed to use those reviews — and it lists which ones it used.

## Running it

From the project folder, using the virtual environment:


..\.venv\Scripts\python.exe ingest.py     # build chunks.json from documents/
..\.venv\Scripts\python.exe embed.py       # embed the chunks into ChromaDB
..\.venv\Scripts\python.exe app.py         # launch the Gradio web UI


Then open http://localhost:7860. You'll need a free Groq API key in a .env file (GROQ_API_KEY=...); see .env.example.

---

## Domain

This system covers Computer Science professor and course reviews at Cal State Fullerton (CSUF) — what CSUF CS students actually say about professors and classes: who explains things well, which exams are fair, how heavy the workload is, and which sections to take or skip. The official course catalog only gives you the course description and prerequisites, so none of that is in there. Right now this info is scattered across Rate My Professors, the r/csuf subreddit, and whatever your friends happen to know, so there's no single place to check before you register.

---

## Document Sources

I collected 10 documents — 6 from Rate My Professors (one file per professor) and 4 from Reddit. Together they cover several different professors, a mix of undergrad and grad courses, and two pretty different kinds of text (short star-rated reviews vs. longer back-and-forth threads).

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Anand Panangadan — CPSC 481 / 375, well liked, exams like the homework | Rate My Professors | documents/rmp_panangadan_anand.txt · https://www.ratemyprofessors.com/professor/2078580 |
| 2 | Alireza Abdoli — mixed; disliked in CPSC 449, liked in CPSC 481 | Rate My Professors | documents/rmp_abdoli_alireza.txt · https://www.ratemyprofessors.com/professor/2803384 |
| 3 | Son Nguyen — CPSC 471/546/544/362, lots of group projects | Rate My Professors | documents/rmp_nguyen_son.txt · https://www.ratemyprofessors.com/professor/1966157 |
| 4 | Kenneth Kung — CPSC 353/440/589, open-note exams | Rate My Professors | documents/rmp_kung_kenneth.txt · https://www.ratemyprofessors.com/professor/215430 |
| 5 | Kanika Sood — CPSC 483 (ML)/315, participation + research project | Rate My Professors | documents/rmp_sood_kanika.txt · https://www.ratemyprofessors.com/professor/2552839 |
| 6 | Christopher Ryu — CPSC 254/483/485/491/585 | Rate My Professors | documents/rmp_ryu_christopher.txt · https://www.ratemyprofessors.com/professor/2382378 |
| 7 | Trying to contact Prof Ning Chen (CPSC 477) — short thread | Reddit (r/csuf) | documents/reddit_ning_chen_contact.txt · https://www.reddit.com/r/csuf/comments/1dupxrm/cs_prof_ning_chen/ |
| 8 | Dr. Mira Kim — CPSC 481/362, plus a CPSC 455 comparison | Reddit (r/csuf) | documents/reddit_mira_kim.txt · https://www.reddit.com/r/csuf/search/?q=Mira+Kim |
| 9 | CPSC 375 with Panangadan — uses R and Spark, two projects | Reddit (r/csuf) | documents/reddit_cpsc375_panangadan.txt · https://www.reddit.com/r/csuf/comments/br50p6/ |
| 10 | "CPSC professors to avoid at CSUF" list (mixed sources — see note) | Reddit Answers (AI summary) | documents/reddit_profs_to_avoid.txt · https://www.reddit.com/answers/597a2e2c-c48b-4cb5-a994-69fd265f68bf/ |

---

## Chunking Strategy

**Chunk size:** For the Rate My Professors files, one chunk is one review (I split on the --- Review N --- markers in the files). For the Reddit files, one chunk is the whole file — a captured thread (or a couple of short related threads about the same professor that I grabbed together).

**Overlap:** 0.

**Why these choices fit my documents:** My documents aren't long flowing articles, they're a bunch of separate little reviews and threads. Each RMP review is already a complete, standalone opinion from one person, and each Reddit thread is one conversation, so cutting at those natural boundaries gives me chunks that already make sense on their own. That's also why I went with no overlap — overlap exists to avoid slicing a paragraph in half when you split by length, but I'm not splitting by length, I'm splitting at the end of each review or thread. If I added overlap I'd just be copying one person's review into the next person's, which would make near-duplicate chunks and muddy retrieval.

One important preprocessing step: the review text itself never repeats the professor's name (RMP only shows it once at the top of the page), so when I chunk I prepend the professor/topic to every chunk (Professor: Kenneth Kung ...). Without that, a chunk about "his exams" has no idea whose exams it is, and retrieval for "Kung's exams" would fall apart. I also do light cleaning before chunking — Unicode normalize, turn smart quotes/dashes into plain ASCII, fix weird spaces — but nothing that touches the review/thread boundaries. I store the source filename, professor/course, URL, and the chunk's position in the file as metadata.

**Final chunk count:** 55 total — 51 RMP review chunks and 4 Reddit thread chunks. Chunks run from about 216 to 2,835 characters (average ~579).

---

## Sample Chunks

Here are 5 actual chunks straight out of chunks.json, so you can see what the splitter produces. Notice the `Professor: ...` / `Reddit thread: ...` header line on every one — that's the prepended name I talked about above, and it's part of the text that gets embedded.

**Sample 1 — source: `rmp_panangadan_anand.txt` (chunk 1 of 7, CPSC 481)**
```
Professor: Anand Panangadan (Computer Science, CSUF)
Course: CPSC 481 | Date: May 23, 2026
Quality: 5.0 | Difficulty: 3.0 | Grade: A | Would Take Again: Yes | Attendance: Mandatory
Tags: Amazing lectures, Caring, Lecture heavy
He really teaches great. On top of that he also extends HW/projects deadline on request. Very good guy and amazing lectures.
```

**Sample 2 — source: `rmp_abdoli_alireza.txt` (chunk 1 of 7, CPSC 449)**
```
Professor: Alireza Abdoli (Computer Science, CSUF)
Course: CPSC 449 | Date: Jan 16, 2026
Quality: 1.0 | Difficulty: 1.0 | Grade: A | Attendance: Not Mandatory
Tags: Helpful
The lectures consisted of him talking about certificates and assigning them as homework. This was a 3 hr Sat class, but he would leave less than an hour in and have his colleague "teach" the rest of the time. He does not reply to emails or messages. There were incorrect exam answers that were never fixed or regraded. The course was a waste of time.
```

**Sample 3 — source: `rmp_kung_kenneth.txt` (chunk 1 of 10, CPSC 353)**
```
Professor: Kenneth Kung (Computer Science, CSUF)
Course: CPSC 353 | Date: Nov 10, 2021
Quality: 5.0 | Difficulty: 2.0 | Grade: A- | Would Take Again: Yes | Attendance: Mandatory | Online Class: Yes
Tags: Gives good feedback, Inspirational, Amazing lectures, Helpful
Easy Professor, Easy A similar to Heckathorn. Take-home tests which get you thinking, 2 stages: stage 1 you take your test, 2 days to take it; stage 2 work with people to change your answers, possible extra credit if you improve your answers. Very easy A and fun to learn from the professor. Quiz canvases are super easy. Be nice to the professor.
```

**Sample 4 — source: `rmp_nguyen_son.txt` (chunk 1 of 7, CPSC 471)**
```
Professor: Son Nguyen (Computer Science, CSUF)
Course: CPSC 471 | Date: Mar 25, 2026
Quality: 1.0 | Difficulty: 5.0 | Grade: B- | Attendance: Mandatory
Tags: Tough grader, Get ready to read, Group projects, Helpful
Take this professor if you want a class that bases all of its quizzes and exams based solely off of trivia found in the slides and a group project which is worth a huge portion of your grade and yet has almost nothing to do with the subject. He also complained about how everyone got low grades on exams/homework, but did not care to adjust them.
```

**Sample 5 — source: `reddit_mira_kim.txt` (chunk 1 of 1, the whole thread)** — this is a Reddit chunk, so it's the entire file as one chunk instead of one review. Shown trimmed; the real chunk is ~1,632 characters.
```
Reddit thread: Dr. Mira Kim (CPSC 481 Artificial Intelligence, CPSC 362)
--- Thread 1: "CPSC 481 - Dr. Mira Kim" (Flair: Professors) ---
Post: Hey guys, if you took Dr. Mira Kim for CPSC 481 before, can I ask you some questions? Also, is she a tough grader?
Comment (Salt-Ganache9713, 9mo ago): I took her class last semester, she's not a tough grader at all.
--- Thread 2: CPSC 481 (Artificial Intelligence) difficulty with Mira Kim ---
Comment (shadowwizard296, 2y ago): It's the best class I've ever taken ... weekly homework that you have infinite attempts on, some quizzes that are pretty easy, one group project, and a midterm and final that are not that hard, mostly multiple choice. She lets you have 2 pages of notes ...
--- Thread 3: Which class to drop - CPSC 455 (Web Security) vs CPSC 481 (AI, Mira Kim) ---
[…thread continues…]
```

You can see the difference the chunking strategy makes: samples 1–4 are each one self-contained RMP review (and could stand on their own), while sample 5 keeps a whole multi-thread Reddit conversation together as a single chunk.

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 from sentence-transformers (384-dimensional vectors). I picked it because it runs locally with no API key and no rate limits, it's fast, and for short English review text it's plenty accurate. I store the vectors in ChromaDB using cosine distance, and I normalize the embeddings so cosine similarity is comparing direction only.

**Production tradeoff reflection:** If this were a real product and cost didn't matter, I'd test a stronger model like OpenAI's text-embedding-3-large. What I'd really be paying for is better accuracy on domain-specific wording — it'd probably be better at realizing that "reads off slides" and "boring lectures" mean the same thing. I'd weigh that against latency (a bigger, API-hosted model is slower and adds a network call) and context length (only matters if I move to bigger chunks — MiniLM caps out at 256 tokens, which a couple of my longer Reddit threads actually exceed and get truncated). Multilingual support isn't a factor since all my sources are in English. At my scale MiniLM is good enough, so the small accuracy gain from a paid model probably wouldn't be worth the cost and delay.

---

## Retrieval Test Results

Before I built generation, I ran queries straight through `retrieve()` (top-k = 5) to make sure the right chunks were coming back. These are real outputs — the distance is cosine distance, so lower = closer (for this corpus, ~0.30–0.45 is a strong match, >0.55 is getting weak). I'm showing 3 queries below with their top chunks, and the excerpts are the start of each chunk.

**Query 1: "How are exams structured in Kenneth Kung classes?"**

| Rank | Distance | Source (chunk) | Excerpt |
|------|----------|----------------|---------|
| 1 | 0.346 | `rmp_kung_kenneth.txt` (4/10, CPSC 440) | Kenneth Kung … CPSC 440 … |
| 2 | 0.351 | `rmp_kung_kenneth.txt` (1/10, CPSC 353) | Kenneth Kung … take-home tests which get you thinking … |
| 3 | 0.359 | `rmp_kung_kenneth.txt` (3/10, CPSC 353) | Kenneth Kung … CPSC 353 … |
| 4 | 0.388 | `rmp_kung_kenneth.txt` (2/10, CPSC 353) | Kenneth Kung … CPSC 353 … |
| 5 | 0.392 | `rmp_kung_kenneth.txt` (9/10, CPSC 440) | Kenneth Kung … CPSC 440 … |

**Why these are relevant:** all 5 chunks are Kenneth Kung reviews and nothing else leaked in, which is exactly what I want for a question that names him. This is the prepend-the-name trick paying off — the review bodies barely say "exam," but because every chunk starts with `Professor: Kenneth Kung`, the query latches onto his reviews instead of drifting to other professors who talk about exams. The distances are all in the strong 0.34–0.39 band. The one thing to notice is that his graduate CPSC 589 reviews (which say there are *no* exams) did **not** come back — "no exams" is semantically far from "how are exams structured," and that gap is exactly the retrieval miss I dig into in the Failure Case Analysis.

**Query 2: "What is the difference in student opinion of Alireza Abdoli between CPSC 449 and CPSC 481?"**

| Rank | Distance | Source (chunk) | Excerpt |
|------|----------|----------------|---------|
| 1 | 0.402 | `rmp_abdoli_alireza.txt` (1/7, CPSC 449) | Abdoli … "waste of time," doesn't reply to emails … |
| 2 | 0.421 | `rmp_abdoli_alireza.txt` (2/7, CPSC 449) | Abdoli … CPSC 449 … |
| 3 | 0.422 | `rmp_abdoli_alireza.txt` (4/7, CPSC 449) | Abdoli … CPSC 449 … |
| 4 | 0.438 | `rmp_abdoli_alireza.txt` (3/7, CPSC 449) | Abdoli … CPSC 449 … |
| 5 | 0.471 | `rmp_abdoli_alireza.txt` (5/7, CPSC 481) | Abdoli … CPSC 481 … "great professor," quality 5.0 … |

**Why these are relevant:** every chunk is Abdoli, and crucially the set covers *both* sides of the comparison — four CPSC 449 reviews (the negative ones) and one CPSC 481 review (the positive one) at rank 5. A comparison question is only answerable if both courses show up, and they did, so the generator has what it needs to contrast 449 vs 481. The 481 chunk sits at the highest distance (0.471) because there's only one of it in the corpus, but it still made the top-5, which is what matters.

**Query 3: "What do students say about Mira Kim CPSC 481 AI class?"**

| Rank | Distance | Source (chunk) | Excerpt |
|------|----------|----------------|---------|
| 1 | 0.391 | `reddit_mira_kim.txt` (1/1) | Dr. Mira Kim CPSC 481 AI thread … "not a tough grader" … |
| 2 | 0.428 | `rmp_sood_kanika.txt` (3/10, CPSC 483) | Kanika Sood … CPSC 483 … |
| 3–5 | 0.430–0.457 | `rmp_sood_kanika.txt` (various, CPSC 483/315) | Kanika Sood … |

Here the #1 hit is the correct Mira Kim Reddit thread (0.391), but ranks 2–5 drifted to Kanika Sood reviews. That makes sense — Sood teaches CPSC 483, which is the *machine learning* elective, so "AI class" pulls her in even though the question names Mira Kim. The top result is still right, and in the full pipeline the grounding prompt keeps the answer anchored to the relevant chunk, but it's a good example of how a question that mixes a name and a topic ("AI") can let topically-similar-but-wrong chunks into the lower ranks.

---

## Grounded Generation

**System prompt grounding instruction:** I don't just ask the model nicely to use the documents — the system prompt gives it hard rules. The key ones are: use *only* the information in the CONTEXT and ignore anything it "knows" from training; if the context doesn't answer the question, reply exactly "The student reviews I have don't cover that" instead of guessing; never invent professors, course numbers, grades, dates, or quotes; and if a review carries a provenance caveat, reflect it. I also run the model at a low temperature (0.2) so it stays close to the source text. I tested this by asking an out-of-corpus question (campus parking) — even though retrieval still returned five reviews, the model correctly refused instead of making something up.

**How the context is built:** the retrieved chunks get passed in as a numbered CONTEXT block ([1]–[5]), each labeled with its source file and professor/course, and the question is appended with a reminder to answer only from that context.

**How source attribution is surfaced in the response:** I don't trust the model to cite its sources — I build the source list in code. After generation, build_sources() reads the metadata of the exact chunks that were retrieved and produces the "Retrieved from" list (source file, position in the file, professor/course). The numbering lines up with the CONTEXT block. This means the attribution is always correct and complete even if the model says nothing about sources, and the system can never cite a document it didn't actually retrieve.

---

## Query Interface

The interface is a small Gradio web app (app.py), launched with `python app.py` and opened at http://localhost:7860.

**Input field:**
- **"Your question"** — a single text box where you type a natural-language question about a CSUF CS professor or course. You can either click the **Ask** button or just press Enter. There are also three clickable example questions under the box so you don't have to type one to try it.

**Output fields:**
- **"Answer"** — the grounded answer the model wrote from the retrieved reviews (or the refusal line if the reviews don't cover it).
- **"Retrieved from"** — the source list, built in code, showing exactly which chunks the answer was drawn from. Each line is `[n] source_file — chunk X of Y (professor/course)`, and the numbers `[1]`–`[5]` match the `[n]` citations inside the answer text.

**Sample interaction transcript** (one complete real query and response):

```
Your question:
    How are exams structured in Kenneth Kung classes?

[Ask]

Answer:
    In Kenneth Kung's CPSC 353 class, exams are open notes, according to
    reviews [3] and [4]. Review [4] also mentions that the exams make you
    think about the questions and topics presented. In his CPSC 440 class,
    review [5] states that all exams are open book, open notes, and most
    questions are directly from the book or homework assignments.

Retrieved from:
    • [1] rmp_kung_kenneth.txt — chunk 4 of 10 (Kenneth Kung, course CPSC 440)
    • [2] rmp_kung_kenneth.txt — chunk 1 of 10 (Kenneth Kung, course CPSC 353)
    • [3] rmp_kung_kenneth.txt — chunk 3 of 10 (Kenneth Kung, course CPSC 353)
    • [4] rmp_kung_kenneth.txt — chunk 2 of 10 (Kenneth Kung, course CPSC 353)
    • [5] rmp_kung_kenneth.txt — chunk 9 of 10 (Kenneth Kung, course CPSC 440)
```

---

## Example Responses

These are real outputs from the running system (Groq llama-3.3-70b-versatile, top-k = 5), copied verbatim including the "Retrieved from" list so you can see the source attribution in the actual output.

**Example 1 — "How are exams structured in Kenneth Kung classes?"**

> In Kenneth Kung's CPSC 353 class, exams are open notes, according to reviews [3] and [4]. Review [4] also mentions that the exams make you think about the questions and topics presented. In his CPSC 440 class, review [5] states that all exams are open book, open notes, and most questions are directly from the book or homework assignments.
>
> **Retrieved from:**
> - [1] rmp_kung_kenneth.txt — chunk 4 of 10 (Kenneth Kung, course CPSC 440)
> - [2] rmp_kung_kenneth.txt — chunk 1 of 10 (Kenneth Kung, course CPSC 353)
> - [3] rmp_kung_kenneth.txt — chunk 3 of 10 (Kenneth Kung, course CPSC 353)
> - [4] rmp_kung_kenneth.txt — chunk 2 of 10 (Kenneth Kung, course CPSC 353)
> - [5] rmp_kung_kenneth.txt — chunk 9 of 10 (Kenneth Kung, course CPSC 440)

The `[3]`, `[4]`, `[5]` in the answer point at the same-numbered chunks in the source list, so you can trace every claim back to a specific review.

**Example 2 — "What is the difference in student opinion of Alireza Abdoli between CPSC 449 and CPSC 481?"**

> In CPSC 449, students consistently reported negative experiences with Professor Alireza Abdoli, citing that he rarely teaches, doesn't reply to emails, and leaves classes early for a substitute to teach. The quality ratings for this course were mostly 1.0.
>
> In contrast, for CPSC 481, a student reported a very positive experience, giving a quality rating of 5.0, and stating that the professor gives good advice and helps students by allowing them to figure things out first. This student also mentioned that they would take the course again.
>
> Overall, the student opinion of Alireza Abdoli differs significantly between CPSC 449, where he received largely negative reviews, and CPSC 481, where he received a very positive review.
>
> **Retrieved from:**
> - [1] rmp_abdoli_alireza.txt — chunk 1 of 7 (Alireza Abdoli, course CPSC 449)
> - [2] rmp_abdoli_alireza.txt — chunk 2 of 7 (Alireza Abdoli, course CPSC 449)
> - [3] rmp_abdoli_alireza.txt — chunk 4 of 7 (Alireza Abdoli, course CPSC 449)
> - [4] rmp_abdoli_alireza.txt — chunk 3 of 7 (Alireza Abdoli, course CPSC 449)
> - [5] rmp_abdoli_alireza.txt — chunk 5 of 7 (Alireza Abdoli, course CPSC 481)

**Example 3 (out-of-scope) — "Where is the best parking on campus?"**

> The student reviews I have don't cover that.
>
> **Retrieved from:**
> - [1] rmp_panangadan_anand.txt — chunk 1 of 7 (Anand Panangadan, course CPSC 481)
> - [2] rmp_sood_kanika.txt — chunk 1 of 10 (Kanika Sood, course CPSC 483)
> - [3] rmp_abdoli_alireza.txt — chunk 3 of 7 (Alireza Abdoli, course CPSC 449)
> - [4] rmp_sood_kanika.txt — chunk 10 of 10 (Kanika Sood, course CPSC 315)
> - [5] rmp_nguyen_son.txt — chunk 5 of 7 (Son Nguyen, course CPSC 362)

This is the grounding working the way it's supposed to. Parking isn't in any review, so even though retrieval still hands back its 5 closest chunks (it always returns *something* — these are just random professor reviews), the model refuses with the exact required line instead of making up an answer from outside knowledge. The refusal is the proof that the "use ONLY the context" rule actually fires, not just decoration.

---

## Evaluation Report

I ran all 5 of my test questions through the actual system on 6/7/2026 (Groq llama-3.3-70b-versatile, top-k = 5). The table summarizes each one, and I pasted the full answers the system gave underneath so nothing is cherry-picked.

I ended up with 2 accurate and 3 partially accurate. I could have called the partial ones accurate since the answers aren't actually wrong, but each one leaves out something that was in my expected answer, so "partially accurate" felt more honest.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about exam format and difficulty in Professor Panangadan's CPSC 481? | Exams are basically like the homework, so the class feels manageable. Clear lectures, and he'll extend deadlines if you ask. | Exams are "JUST like the homework," final is similar but harder; difficulty rated 2–3, course is manageable. | Relevant — 4 of 5 chunks were Panangadan (one Nguyen review snuck in but the answer didn't use it) | Accurate. It answered the exam + difficulty question straight from his reviews. |
| 2 | What is the difference in student opinion of Alireza Abdoli between CPSC 449 and CPSC 481? | 449 is very negative (rarely teaches, leans on a sub, ignores emails); 481 is positive (chill, good industry advice, low-stress exams). | 449: rarely teaches, doesn't reply to emails, leaves early, "waste of time," quality around 1.0. 481: "great professor," good advice, straightforward, quality 5.0. | Relevant — all 5 chunks were Abdoli and they covered both courses | Accurate. It got the 449-bad / 481-good split that I was looking for. |
| 3 | How are exams structured in Kenneth Kung's classes? | Open-note / open-book and they make you think, and his graduate class (CPSC 589) has no exams. | CPSC 353: open notes, make you think. CPSC 440: open book/open notes, questions from the book or homework. Also called "clear and short." | Partially relevant — all Kung, but only his 353/440 reviews came back; the CPSC 589 grad reviews didn't | Partially accurate. The open-note part is right, but it missed that his grad class has no exams, because those chunks never got retrieved. |
| 4 | What should students expect from the group project and participation grading in Kanika Sood's CPSC 483? | A real group project (can turn into a publishable research paper) plus graded/forced participation. Paper exams that are fine if you study. Mixed on how fast she answers email. | Participation is graded and matters, there are group projects, a good partner makes it manageable, the project is "a lot," and the forced participation can feel unnecessary. | Relevant — 3 of 5 chunks were Sood (two Nguyen reviews leaked in but the answer didn't use them) | Partially accurate. It's grounded in her actual reviews and gets the participation grading right, but it left out the part about the project becoming a publishable paper, since that review wasn't retrieved. |
| 5 | Which CPSC professors do students recommend avoiding, and why? | McCarthy (talks about interviews instead of teaching), Holliday (CPSC 240 assembly — "just Google it"), Stephen/Eric May, Yun Tian (hard to follow). Caveat: the source mixes r/csuf with r/UCalgary, so I don't fully trust the attribution. | Lists McCarthy, Holliday ("Google it"), Stephen/Eric May, Yun Tian, and Mehdi Peiravi with reasons — but presents them all as CSUF professors with no caveat. | Partially relevant — the right "profs to avoid" file was the #1 result; the other 4 chunks were unrelated RMP reviews | Partially accurate. The names and reasons match the source, but it dropped the r/UCalgary warning and stated possibly cross-school info as if it's all about CSUF. |

So that's 2 accurate, 3 partially accurate, and nothing flat-out wrong.

### The full answers the system gave

**Q1 — Panangadan CPSC 481 exams**
> In Professor Panangadan's CPSC 481, students say that the exams are "JUST like the homework" (review [1]), and the final is "similar to homework assignments, but harder" (review [3]). This suggests that the exam format is closely related to the homework assignments, but may be more challenging. The difficulty of the course is rated as 2.0 (review [1]) and 3.0 (reviews [3] and [5]) by students, indicating that it is manageable.

**Q2 — Abdoli CPSC 449 vs 481**
> In CPSC 449, students consistently reported that Professor Alireza Abdoli rarely teaches, doesn't reply to emails, and leaves classes early, with some calling the course a "waste of time." In contrast, a student in CPSC 481 described him as a "great professor" who gives good advice, is straightforward, and helps students by allowing them to figure things out first. The quality rating for CPSC 481 was 5.0, whereas for CPSC 449, the quality ratings were mostly 1.0.

**Q3 — Kung exams**
> In Kenneth Kung's CPSC 353 class, exams are described as "open notes" and are designed to make students think about the questions and topics presented. In his CPSC 440 class, exams are "open book, open notes" and most questions are directly from the book or homework assignments. Additionally, in one review of CPSC 353, exams are mentioned as being "clear and short".

**Q4 — Sood CPSC 483 group project / participation**
> In Kanika Sood's CPSC 483, students should expect that participation matters and is graded. The course includes group projects, and having a good partner or two can make the project manageable. However, one review mentions that the project is "a lot," suggesting it may be challenging. Another review from a different date describes the lectures as helpful and the material as easy to understand, with participation, such as raising hands and asking/answering questions, being graded, which can feel unnecessary.

**Q5 — Professors to avoid**
> According to the student reviews, the following CPSC professors are recommended to be avoided:
> 1. McCarthy: Students say he spends more time talking about potential interviews than teaching code and should not be teaching at all.
> 2. Holliday (for Assembly / CPSC 240): He couldn't do assembly and would tell students to "Google it" when they asked for help.
> 3. Stephen May / Eric May (reports vary): Students describe them as "horrible" and say their classes become "ghost towns" towards the end of the semester.
> 4. Yun Tian: Students have difficulty understanding her due to her thick accent and find her teaching unclear.
> 5. Mehdi Peiravi: A commenter mentions that he doesn't teach and requires self-study.
>
> These professors are recommended to be avoided due to issues such as poor teaching, lack of engagement, unhelpfulness, and unclear instruction.

---

## Failure Case Analysis

**Question that failed:**

Q5 — "Which CPSC professors do students recommend avoiding, and why?"

**What the system returned:**

It gave a clean, confident list — McCarthy, Holliday, Stephen/Eric May, Yun Tian, and Mehdi Peiravi — with a reason for each, and presented all of them as CSUF CPSC professors. The list itself isn't the problem. The problem is that it stated everything as fact about CSUF and never once mentioned that the source isn't fully trustworthy.

**Root cause (tied to a specific pipeline stage):**

This is mostly a generation problem, and it goes back to a chunking decision I made earlier. My "profs to avoid" document is stored as one single chunk (my rule was one whole Reddit file = one chunk), and right at the top of that chunk there's a provenance note saying it's an AI-generated Reddit Answers summary that pulls from r/UCalgary on top of r/csuf — and University of Calgary also uses "CPSC" course codes, so some of those names might not even be CSUF professors. That warning text was sitting inside the exact chunk that got retrieved, so the model definitely saw it. I even have a rule in my system prompt (rule 4) that tells it to repeat provenance caveats. It dropped it anyway.

The reason it dropped it is that the caveat is one sentence buried at the top of a long chunk, and rule 4 is a soft instruction that loses out to the model's stronger pull to just directly answer the question I asked. So it grabbed the useful avoid-list and skipped the boring meta-warning. Lowering the temperature doesn't help here, because this isn't randomness — it's the model deciding what's worth including.

**What you would change to fix it:**

I'd stop relying on the model to remember the caveat and make it structural instead — the same way I already made source attribution programmatic instead of trusting the LLM to cite. When I ingest that file I'd add a metadata flag on the chunk (something like provenance_warning: true), and then in app.py, after generation, I'd check whether any retrieved chunk has that flag and automatically stick a warning line on top of the answer ("Heads up — one of these sources mixes r/csuf with r/UCalgary, so some of these names may not be CSUF professors"). That way the warning shows up no matter what the model decides to do. I'd also tighten rule 4 in the prompt, but I trust the programmatic version more.

**A second, different kind of failure (Q3):**

Q3 (Kung's exams) failed in a completely different way that's worth noting. My expected answer included that his graduate class (CPSC 589) has no exams, but the system never said that. This one is retrieval, not generation: the CPSC 589 reviews talk about there being *no* exams, which is actually semantically far from a question about "how exams are structured," so those chunks score low and fall outside my top-5. The same thing happened on Q4 — the review where a student talks about turning the project into a publishable paper didn't get retrieved either. Bumping k up a bit, or pulling all of a named professor's chunks when the question names them, would catch both of these.

---

## Spec Reflection

**One way the spec helped me during implementation:**

Writing the planning.md first really did help. By the time I started coding each stage I already knew exactly what I wanted, so I could hand that to the AI tool instead of figuring it out as I went. The Chunking Strategy and Retrieval Approach sections were the most useful. I had already decided on one review per chunk, one Reddit file per chunk, no overlap, all-MiniLM-L6-v2, ChromaDB, and top-k 5, so the code I got back actually matched what I had in mind and I could just check it against my own plan instead of rethinking the whole design. The architecture diagram helped too, because I could point the AI at one picture and it understood how retrieval was supposed to feed into generation.

**One way my implementation diverged from the spec, and why:**

In my planning.md I said I'd make a simple command-line loop for the interface, but I ended up using a Gradio web UI instead. Part of it was that the milestone recommended Gradio, but mostly it just makes a better demo. Someone can open a browser, click one of my example questions, and see the answer and the sources right away, and I don't have to explain how to use a terminal first. The actual logic stayed the same, since the ask() function works the same either way. It was really only the wrapper around it that changed. The other small thing I added that wasn't in my plan was the chunk position metadata (chunk_index and chunk_count), which I put in once I realized I'd want it for the source list.

---

## AI Usage

**Instance 1: Ingestion and chunking (Milestone 3)**

- *What I gave the AI:* My Documents table and Chunking Strategy section from planning.md, and I asked it to write a script that reads every .txt in documents/ and splits the RMP files into one chunk per review and the Reddit files into one chunk per file, with no overlap.
- *What it produced:* ingest.py, which has a loader, a clean_text() step, header parsing, and separate chunk_rmp() and chunk_reddit() functions, and writes everything out to chunks.json.
- *What I changed or directed:* The main thing I told it to do was prepend the professor's name to every chunk. I knew the review text never actually repeats the name, so without that a chunk about "his exams" would have no idea whose exams it was, and a search for Kung's exams would fall apart. I also told it to keep the cleaning gentle so it wouldn't break the --- Review N --- markers that the splitter relies on.

**Instance 2: Embedding and retrieval (Milestone 4)**

- *What I gave the AI:* My Retrieval Approach section and the architecture diagram, and I asked it to embed the chunks with all-MiniLM-L6-v2, store them in ChromaDB with their metadata, and write a retrieve() function that gives back the top 5 closest chunks.
- *What it produced:* embed.py with build_index() and retrieve(), saving the collection to disk so I don't have to re-embed every time.
- *What I changed or directed:* I had it add the chunk_index and chunk_count position metadata, since it wasn't tracking position at first and I wanted it for the source list later. I also had it set ChromaDB to cosine distance and normalize the embeddings. Then I tested retrieval on my eval questions before moving on, which is how I caught that searching "Sood" without the possessive was pulling back mostly Son Nguyen's reviews.

**Instance 3: Grounded generation and interface (Milestone 5)**

- *What I gave the AI:* My architecture diagram and the retrieve() function, and I asked it to connect generation through Groq's llama-3.3-70b-versatile with a prompt that only answers from the retrieved context, plus a Gradio interface.
- *What it produced:* app.py, with the grounding system prompt, an ask() function, and the Gradio UI that has an Answer box and a "Retrieved from" box.
- *What I changed or directed:* The thing I insisted on was that the source list be built in code from the chunk metadata instead of being written by the model, so it can't make up a citation. I also read through the system prompt myself to make sure the grounding was written as actual rules (only answer from the context, refuse if it isn't there) and not just polite suggestions, and I checked that the refusal really fires by asking it something my documents don't cover.

---

## Project Walkthrough

Video demo: https://www.loom.com/share/6ca2535ea0694bbf9e4b471da620e4ec
