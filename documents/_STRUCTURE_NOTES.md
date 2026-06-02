# Notes on how my documents are structured

I skimmed all 10 documents before doing anything else. They fall into two pretty
different shapes, and that's going to matter a lot when I chunk them in Milestone 2.

## Rate My Professors files (docs 1–6)
These are a bunch of short reviews stacked on top of each other. Each review is only
about 2–5 sentences, with a little header on top (course, quality, difficulty, grade,
tags). The useful info is usually packed into one or two sentences, like "exams are just
like the homework."

One thing I noticed: the same professor can get totally different reviews depending on
the course. Abdoli gets trashed for CPSC 449 but praised for CPSC 481, and Ryu is an easy
A in CPSC 254 but rough in his ML/AI classes. So the course code really needs to stay
attached to each review, otherwise the system might mix up opinions about different classes.

## Reddit files (docs 7–10)
These are conversations, not reviews. There's a question and then people reply to it and
to each other. The actual answer is usually spread out over several comments instead of
sitting in one place. For example, in the CPSC 375 thread one person says it's R-based,
someone else says installing Spark is the annoying part, and a third lists the topics. You
need all of it to really answer "is this class hard."

(Doc 7 is barely anything — just a question with no replies. Doc 10 isn't even real posts,
it's an AI summary that pulls from r/csuf AND r/UCalgary, so I'm not fully trusting it.)

## What this means for chunking (Milestone 2)
- RMP files: it makes sense to chunk one review at a time. They're short, so small chunks.
- Reddit files: chunking one comment at a time risks cutting an answer off from its
  question, so I might keep a question + its replies together, or use bigger chunks here.
- Either way I have to keep the professor name and course code with each chunk.

The tricky part is the two file types kind of want different chunk sizes. I'll figure out
whether to split on my own "--- Review ---" / "--- Comment ---" markers, or just pick one
fixed size and live with it. Decide this in the Chunking Strategy section.
