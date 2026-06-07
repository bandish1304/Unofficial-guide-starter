# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

The domain I choose is Computer Science professor and course reviews at Cal State Fullerton (CSUF).

My system covers what CSUF CS students actually say about professors and classes: who explains things well, which exams are fair, how heavy the workload is, and which sections to take or skip. This is knowledgeable because the official course catalog only gives you the course description and prerequisites, so none of that is in there. Right now this info is scattered across Rate My Professors, the r/csuf subreddit, and whatever your friends happen to know, so there's no single place to check before you register for a class.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Anand Panangadan — CPSC 481 (AI) and CPSC 375; well liked, exams are like the homework | documents/rmp_panangadan_anand.txt · https://www.ratemyprofessors.com/professor/2078580 |
| 2 | Rate My Professors | Alireza Abdoli — mixed reviews; students dislike his CPSC 449 but like CPSC 481 | documents/rmp_abdoli_alireza.txt · https://www.ratemyprofessors.com/professor/2803384 |
| 3 | Rate My Professors | Son Nguyen — CPSC 471/546/544/362; lots of group projects, reads off slides | documents/rmp_nguyen_son.txt · https://www.ratemyprofessors.com/professor/1966157 |
| 4 | Rate My Professors | Kenneth Kung — CPSC 353/440/589; open-note exams, nice prof, 10 reviews from 2014–2021 | documents/rmp_kung_kenneth.txt · https://www.ratemyprofessors.com/professor/215430 |
| 5 | Rate My Professors | Kanika Sood — CPSC 483 (ML)/315; engaging, paper exams, graded participation, research project | documents/rmp_sood_kanika.txt · https://www.ratemyprofessors.com/professor/2552839 |
| 6 | Rate My Professors | Christopher Ryu — CPSC 254/483/485/491/585; easy in CPSC 254, hard in his ML/AI classes | documents/rmp_ryu_christopher.txt · https://www.ratemyprofessors.com/professor/2382378 |
| 7 | Reddit (r/csuf) | Trying to contact Prof Ning Chen (CPSC 477); short, just a question with no answers | documents/reddit_ning_chen_contact.txt · https://www.reddit.com/r/csuf/comments/1dupxrm/cs_prof_ning_chen/ |
| 8 | Reddit (r/csuf) | Dr. Mira Kim — CPSC 481 (AI)/362; grading, exam format, plus a CPSC 455 (Avery) comparison | documents/reddit_mira_kim.txt · https://www.reddit.com/r/csuf/search/?q=Mira+Kim |
| 9 | Reddit (r/csuf) | CPSC 375 with Panangadan; uses R and Apache Spark, two projects, elective credit advice | documents/reddit_cpsc375_panangadan.txt · https://www.reddit.com/r/csuf/comments/br50p6/ |
| 10 | Reddit Answers (AI summary) | "CPSC professors to avoid at CSUF" list (McCarthy, Holliday, May, Tian, Peiravi); mixed sources, see the note in the file | documents/reddit_profs_to_avoid.txt · https://www.reddit.com/answers/597a2e2c-c48b-4cb5-a994-69fd265f68bf/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
My chunk size will be for RMP files it will be 1 review per chunk and for Reddit files it will be 1 file per chunk (one whole captured Reddit page = one chunk). Most of my Reddit files are a single thread, but a couple (e.g. reddit_mira_kim.txt) bundle a few short related threads about the same professor that I captured together — I keep those as one chunk on purpose so the full conversation stays intact instead of being chopped into tiny one-line fragments.
**Overlap:**
Honestly, my overlap will be 0 because the ratings and reddit comments are really small post, that i dont have to do overlap

**Reasoning:**
I'm not splitting my documents by a set number of tokens, so I don't really need overlap. For the RMP files, one chunk is just one review, and for Reddit one chunk is one thread. Each of those is already a full, standalone piece of text. The whole point of overlap is to deal with cutting a paragraph off in the middle when you split by length, but that's not happening here since I'm cutting at the end of each review or thread anyway. If I added overlap I'd just be copying part of one review into the next one, which doesn't make sense because they're written by different people about different things. That would make my embeddings messier and could give me a bunch of almost-identical chunks when I do retrieval. So 0 overlap just makes more sense for the kind of data I have.



---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
I will be using sentence-transformers (all-MiniLM-L6-v2)

**Top-k:**
k = 5
**Production tradeoff reflection:**
 If this were a real product and cost didn't matter, I'd test a stronger embedding model like OpenAI's text-embedding-3-large. The main thing I'd be paying for is better accuracy on domain-specific wording it'd be better at telling that "reads off slides" and "boring lectures" mean the same thing. I'd weigh that against latency (bigger models are slower and need an API call) and context length (only matters if I move to larger chunks). Multilingual support isn't really a factor since all my sources are in English. At my current scale MiniLM is good enough, so the paid model's small accuracy gain probably wouldn't be worth the cost and added delay.


---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

1. What do students say about exam format and difficulty in Professor Panangadan's CPSC 481? 
Ans: Students say the exams are basically like the homework, so the class feels manageable. He's known for clear lectures and for extending deadlines if you ask. 
2. What is the difference in student opinion of Alireza Abdoli between CPSC 449 and CPSC 481? 
Ans: CPSC 449 reviews are very negative (rarely teaches, relies on a sub, doesn't answer emails); CPSC 481 reviews are positive (chill, good up-to-date industry advice, low-stress exams). 
3. How are exams structured in Kenneth Kung's classes? 
Ans: Exams are open-note / open-book and make you think; and for graduate class there are no exams for his class
4. What should students expect from the group project and participation grading in Kanika Sood's CPSC 483? Ans: A significant group project (can be taken toward a publishable research paper) plus graded/forced participation; paper exams that are manageable if you study. Reviews are mixed on email responsiveness. |
5. Which CPSC professors do students recommend avoiding, and why? 
Ans: Students name McCarthy (talks about interviews instead of teaching), Holliday (CPSC 240 assembly — "just said Google it"), Stephen/Eric May, and Yun Tian (hard to follow). NOTE: this source mixes r/csuf with r/UCalgary, so attribution should be treated cautiously. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. One of my Reddit sources (the "profs to avoid" list) actually mixes r/csuf with r/UCalgary, so the system might pull in opinions about professors who aren't even at CSUF and present them like they are, which would give students wrong info.

2. If a Reddit thread is long and talks about several professors at once, that one big chunk could blend their reviews together, so a question about one professor might come back with another professor's comments mixed in.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE UNOFFICIAL GUIDE — RAG PIPELINE                │
└─────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────┐
  │ 1. DOCUMENT INGESTION│   Read the .txt files in documents/
  │                      │   (6 RMP files + 4 Reddit files)
  │  Tool: Python (open) │
  └──────────┬───────────┘
             │  raw text
             ▼
  ┌──────────────────────┐
  │ 2. CHUNKING          │   RMP  → 1 review per chunk
  │                      │   Reddit → 1 file  per chunk
  │  Tool: Python script │   Overlap: 0
  └──────────┬───────────┘
             │  list of chunks
             ▼
  ┌──────────────────────┐
  │ 3. EMBEDDING +       │   Turn each chunk into a vector,
  │    VECTOR STORE      │   then save it in the database
  │                      │
  │  Embed: all-MiniLM-  │
  │    L6-v2 (sentence-  │
  │    transformers)     │
  │  Store: ChromaDB     │
  └──────────┬───────────┘
             │  ChromaDB collection (searchable)
             ▼
  ┌──────────────────────┐        ┌─────────────────────┐
  │ 4. RETRIEVAL         │ ◄──────│  User's question    │
  │                      │        │  ("How are Kung's   │
  │  Embed the question, │        │   exams?")          │
  │  query for top-k = 5 │        └─────────────────────┘
  │  closest chunks      │
  │  Tool: ChromaDB      │
  │    (.query)          │
  └──────────┬───────────┘
             │  top 5 relevant chunks
             ▼
  ┌──────────────────────┐
  │ 5. GENERATION        │   Feed question + retrieved chunks
  │                      │   to the LLM, get a written answer
  │  Tool: Groq API      │
  │   (llama-3.3-70b-    │
  │    versatile)        │
  └──────────┬───────────┘
             │
             ▼
      ┌───────────────┐
      │  Final answer │  → grounded in real student reviews
      └───────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I'll use Claude. I'll give it my Documents table and my Chunking Strategy section, and ask it to write a Python script that reads each .txt file in documents/ and splits it into chunks. 1 review per chunk for the RMP files and 1 thread per chunk for the Reddit files, with 0 overlap. I expect it to produce a chunk_text() function plus the loop that loads all 10 files. I'll verify it by printing the chunks and checking that each RMP chunk is exactly one review and each Reddit chunk is one thread, and that no review got cut in half.

**Milestone 4 — Embedding and retrieval:**
I'll use Claude. I'll give it my Retrieval Approach section (all-MiniLM-L6-v2, ChromaDB, top-k = 5) and the chunks from Milestone 3, and ask it to embed each chunk and store it in a ChromaDB collection, then write a function that takes a question, embeds it, and returns the top 5 closest chunks. I expect working build_index() and retrieve(query) functions. I'll verify it by running a couple of my evaluation questions and checking that the chunks it returns are actually about the right professor for example, asking about Kung's exams should pull back Kung's reviews, not someone else's.

**Milestone 5 — Generation and interface:**
I'll use the Groq API with the llama-3.3-70b-versatile model (and Claude to help me write the code). I'll give it my Architecture diagram and the retrieve() function from Milestone 4, and ask it to build the final step: take the user's question plus the retrieved chunks, send them to llama-3.3-70b-versatile through Groq with a prompt that says "only answer using these reviews," and print the answer. I also want a simple command-line loop so I can type questions. I expect a generate_answer() function and a small CLI. I'll verify it against all 5 questions in my Evaluation Plan, checking the answers match my expected answers and that it doesn't make up info that isn't in the chunks.
