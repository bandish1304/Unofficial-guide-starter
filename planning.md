# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

**Domain:** Computer Science professor and course reviews at Cal State Fullerton (CSUF).

My system covers what CSUF CS students actually say about professors and classes: who explains things well, which exams are fair, how heavy the workload is, and which sections to take or skip. The official course catalog only gives you the course description and prerequisites, so none of that is in there. Right now this info is scattered across Rate My Professors, the r/csuf subreddit, and whatever your friends happen to know, so there's no single place to check before you register for a class.

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

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about exam format and difficulty in Professor Panangadan's CPSC 481? | Students say the exams are basically like the homework, so the class feels manageable. He's known for clear lectures and for extending deadlines if you ask. |
| 2 | What is the difference in student opinion of Alireza Abdoli between CPSC 449 and CPSC 481? | CPSC 449 reviews are very negative (rarely teaches, relies on a sub, doesn't answer emails); CPSC 481 reviews are positive (chill, good up-to-date industry advice, low-stress exams). |
| 3 | How are exams structured in Kenneth Kung's classes? | Exams are open-note / open-book and make you think; in CPSC 353 he uses a two-stage take-home test format. Students still warn you must understand the concepts to score well. |
| 4 | What should students expect from the group project and participation grading in Kanika Sood's CPSC 483? | A significant group project (can be taken toward a publishable research paper) plus graded/forced participation; paper exams that are manageable if you study. Reviews are mixed on email responsiveness. |
| 5 | Which CPSC professors do students recommend avoiding, and why? | Students name McCarthy (talks about interviews instead of teaching), Holliday (CPSC 240 assembly — "just said Google it"), Stephen/Eric May, and Yun Tian (hard to follow). NOTE: this source mixes r/csuf with r/UCalgary, so attribution should be treated cautiously. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
