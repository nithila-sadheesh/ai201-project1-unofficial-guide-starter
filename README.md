# The Unofficial Guide — Project 1

---

## Domain

This system makes student-generated survival advice for UC Berkeley searchable and accessible in one place. Rather than covering official information like course descriptions or degree requirements, it consolidates lifestyle, safety, academic, and mental health tips that reflect the lived experience of students — advice that is specific to Berkeley's culture and environment. This knowledge is hard to find through official channels because it captures personal, hard-won experiences scattered across Reddit threads, student blogs, campus newspaper articles, and online forums. This project aggregates and indexes those sources so students can ask natural questions and get grounded, cited answers.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Her Campus UC Berkeley | Article | https://www.hercampus.com/school/uc-berkeley/uc-berkeley-college-survival-guide/ |
| 2 | The Daily Californian — Survival Guide | Article | https://www.dailycal.org/archives/uc-berkeley-survival-guide-for-newer-students/article_5664df0b-aa7e-5076-8a5a-17be645aa5a9.html |
| 3 | Plexuss — UC Berkeley College Survival Guide | Article | https://plexuss.com/n/uc-berkeley-college-survival-guide |
| 4 | The Daily Californian — Stay Motivated | Article | https://www.dailycal.org/archives/stay-motivated-a-uc-berkeley-survival-guide/article_f2a640cd-ea05-5e97-859d-e470df9401ae.html |
| 5 | r/berkeley — What should every new Cal student know? | Reddit | https://www.reddit.com/r/berkeley/comments/1dqccmk/what_should_every_new_cal_student_know_about/ |
| 6 | r/berkeley — Mental health resource guide | Reddit | https://www.reddit.com/r/berkeley/comments/16hgeb0/mental_health_resource_guide_and_a/ |
| 7 | r/berkeley — What is essential to have/know in Berkeley | Reddit | https://www.reddit.com/r/berkeley/comments/15njiw6/what_is_essential_to_haveknow_when_living_in/ |
| 8 | r/berkeley — How to survive Berkeley EECS | Reddit | https://www.reddit.com/r/berkeley/comments/25kp1d/how_to_survive_berkeley_eecs/ |
| 9 | r/berkeley — Guide to maximizing your finals score | Reddit | https://www.reddit.com/r/berkeley/comments/13c6atg/guide_to_maximizing_your_score_on_your_finals_if/ |
| 10 | r/berkeley — How to Succeed at Berkeley | Reddit | https://www.reddit.com/r/berkeley/comments/pfa2j3/how_to_succeed_at_berkeley/ |

---

## Chunking Strategy

**Chunk size:**
Approximately 450 tokens (346 words) per chunk for articles. One comment per chunk for Reddit threads, with the thread title prepended to each comment for context.

**Overlap:**
75 tokens (58 words) for articles; 0 for Reddit.

**Why these choices fit your documents:**
Articles are continuous prose where ideas often span paragraph boundaries, so overlapping adjacent chunks prevents a relevant sentence from being split across two chunks and missed by retrieval. Reddit comments are self-contained units of advice — each one makes a single point — so the comment boundary is the natural chunk boundary and overlap would duplicate content without adding value. The thread title is prepended to each Reddit chunk because comments are too short to stand alone without knowing the thread topic (e.g., a comment saying "take two technical classes" only makes sense in the context of the EECS survival thread).

**Final chunk count:**
146 chunks total across all 10 sources.

**Sample Chunks**

**Chunk 1** — `dailycal_motivated` (Article)
> Recreational Sports Facility on campus. They offer everything from abs and back to kickboxing to Zumba and yoga. 3. Routine — Having a routine might sound like a drag, but it can greatly improve your habits and increase your productivity. Try finding a routine that suits you. 4. Sleep — Getting an adequate amount of sleep at night can actually help you become more productive throughout the day. It is usually recommended to get seven to eight hours of sleep at night. Don't be afraid to take naps on campus — some great places include Doe Library, Main Stacks, Memorial Glade and North Field. 5. Save partying for after midterms/papers — just because you miss an awesome party tonight doesn't mean there won't be more later on.

**Chunk 2** — `reddit_eecs` (Reddit)
> How to survive Berkeley EECS?
>
> Your first semester you should only take 2 technical classes and just enough other courses to have a full load (which for EECS is 12 units). You need to calibrate yourself for how tough Berkeley is. It's a horrible idea to start off at Cal by digging yourself into a hole by getting a bad GPA, so be cautious at first. Either way, take the time you save by not taking a 4th class and work on building a support network and a set of friends, both in and out of your intended major.

**Chunk 3** — `reddit_new_student` (Reddit)
> What should every new Cal student know about before they come to campus this Fall?
>
> I wish I had been more serious earlier about taking random DeCal classes, joining non-academic student clubs, going to more events, and attending academic talks. It's easy to get overwhelmed by being on your own and taking college classes, but there's a lot of really fun stuff to try out.

**Chunk 4** — `reddit_safety` (Reddit)
> What is essential to have/know when living in Berkeley
>
> No need for heavy jackets — light layers, sweaters, lots of fleece (it's a Berkeley thing).

**Chunk 5** — `reddit_new_student` (Reddit)
> What should every new Cal student know about before they come to campus this Fall?
>
> Buy a laptop lock and use it. Keep your wits around you — there's a lot of random spillover violent crime in Berkeley. The one useful thing my thermo professor said: you have time for anything, but you don't have time for everything. Time management is key; sometimes you have to say no to a social event. Figure out what studying strategies work for you — study groups can easily become just hang-out sessions. Homework can be divided into two categories: stuff you just need to slog through, and stuff you need to figure out.

---

## Embedding Model

**Model used:**
`all-MiniLM-L6-v2` via `sentence-transformers`, stored in ChromaDB with cosine similarity (`hnsw:space: cosine`). Chunks are embedded at index time by `embed.py` and stored persistently in `chroma_db/`. At query time, `retrieve.py` embeds the query using the same model and returns the top-5 most similar chunks.

**Production tradeoff reflection:**
In a production deployment, I would weigh several factors. `all-MiniLM-L6-v2` caps at 256 tokens, which means longer article chunks are silently truncated — for a corpus with longer documents, a model with a higher token limit would be preferable. For a Q&A-focused task, `multi-qa-MiniLM-L6-cos-v1` is trained specifically on question–passage pairs and would likely improve retrieval accuracy on direct factual questions. Domain-specificity would matter less here since student advice is conversational rather than highly technical. Multilingual support — offered by `paraphrase-multilingual-MiniLM-L12-v2` — would allow non-English queries, but at the cost of accuracy on English-only inputs.

---

## Retrieval Test Results

**Query 1:** If studying EECS, how many technical classes is it recommended to take each semester?

```
[reddit_eecs | chunk 13 | distance: 0.3915]
How to survive Berkeley EECS?
I recommend not taking those four classes at once. Take two techs and one or two humanities
classes/decals (and take them as pass/no pass if struggling)...

[reddit_eecs | chunk 9 | distance: 0.4827]
How to survive Berkeley EECS?
Your first semester you should only take 2 technical classes and just enough other courses
to have a full load (which for EECS is 12 units)...

[reddit_eecs | chunk 0 | distance: 0.4886]
How to survive Berkeley EECS?
Which teachers should I pick for the following classes: Math 53, Physics 7a, CS 61A,
and English R1B? What should I do my first semester? How do I make a support network?
```

**Why the results are relevant:** The top two chunks are directly relevant — both come from the EECS survival thread and explicitly discuss limiting technical courses per semester, with chunk 9 stating the exact "2 technical classes" figure. The word "EECS" is rare across the corpus and appears almost exclusively in this one thread, so the embedding model has little competition and retrieves the right source confidently. Chunk 0 (the original question post) is a known noise issue: the OP's question gets embedded alongside the answers and surfaces even though it contains no useful advice. This is a general weakness of comment-level chunking on Reddit threads.

---

**Query 2:** What is Berkeleytime and by how many minutes do Berkeley classes actually start after their listed time?

```
[reddit_new_student | chunk 5 | distance: 0.2412]
What should every new Cal student know about before they come to campus this Fall?
There's something called Berkeleytime, meaning all classes and events start 10 minutes
late. So if you look on the course catalog and see a class from 3-4pm, it'll actually
be from 3:10pm-4pm (unless otherwise specified)...

[reddit_succeed | chunk 10 | distance: 0.4774]
How to Succeed at Berkeley
Really depends on the part you get off track on, but just work your butt off to get
back up to speed on assignments and attend extra office hours...

[reddit_safety | chunk 22 | distance: 0.5045]
What is essential to have/know when living in Berkeley
Would love to show you around campus if you are interested...
```

**Why the results are relevant:** The top result at distance 0.2412 is a near-perfect match — unusually low for this corpus — because "Berkeleytime" is a unique term that appears in exactly one chunk. There is no ambiguity and no competing chunks. The second and third results are distant (0.47 and 0.50) and off-target, but they don't affect the answer since the correct chunk ranked first by a wide margin and dominates generation.

---

**Query 3:** What specific locations near Berkeley campus should students avoid walking through late at night?

```
[reddit_safety | chunk 8 | distance: 0.3991]
What is essential to have/know when living in Berkeley
don't leave ANYTHING inside a car that is visible from outside. don't go near people's
park, and don't go through downtown (west of campus, down shattuck ave), particularly
the BART plaza, late at night...

[reddit_new_student | chunk 23 | distance: 0.4501]
What should every new Cal student know about before they come to campus this Fall?
Do not come to Cal if you're not ready to be aware/vigilant of your safety. Have street
smarts, don't stay out too late at night and try to walk with someone wherever you go...

[reddit_safety | chunk 11 | distance: 0.4612]
What is essential to have/know when living in Berkeley
If you're a woman (actually even if you're a man) have pepper spray — grip onto it when
walking alone at night. Always clutch onto your belongings and be aware of your
surroundings, as robberies and violent crime are common in Berkeley especially late at night.
```

---

## Grounded Generation

**System prompt grounding instruction:**
The system prompt instructs the model to answer using only information explicitly stated in the provided context, and to output a fixed fallback message — *"The sources I have don't directly answer that. Try rephrasing your question or asking something more specific."* — if the context does not contain a direct, specific answer. The prompt explicitly forbids using general knowledge to fill gaps, so if a chunk partially addresses the question but lacks the specific detail, the model is expected to surface the fallback rather than infer or hallucinate.

The full instruction given to the model is:

> You answer based solely on the context provided, which comes from Reddit threads, student blogs, and campus newspaper articles written by Berkeley students. Use ONLY information explicitly stated in the provided context. Do not use any general knowledge. If the context does not contain a direct, specific answer to the question, respond with exactly: "The sources I have don't directly answer that. Try rephrasing your question or asking something more specific." Do not guess, infer beyond what is stated, or fill gaps with outside knowledge.

**How source attribution is surfaced in the response:**
Each chunk is passed to the model with its source name as a label (e.g., `[reddit_eecs]`). The system prompt instructs the model to cite the source name in square brackets immediately after any claim it draws from that chunk. Since the model can only see the source names that were actually retrieved and passed in context, it cannot fabricate or cite sources that weren't returned.

---

## Example Responses

**Example 1 — in-scope query with citation:**

> **Query:** What is Berkeleytime and by how many minutes do Berkeley classes actually start after their listed time?
>
> **Response:** Berkeleytime refers to the practice where all classes and events start 10 minutes late. So, if a class is listed from 3–4pm, it will actually start at 3:10pm and end at 4:10pm, unless otherwise specified [reddit_new_student].

---

**Example 2 — in-scope query with citation:**

> **Query:** How early should students schedule a same-day CAPS counseling appointment to guarantee they are seen?
>
> **Response:** To guarantee a same-day CAPS counseling appointment, students should schedule it before 10 AM or the night before [reddit_mental_health].

---

**Example 3 — out-of-scope query showing refusal:**

> **Query:** What is the best pizza place in New York City?
>
> **Response:** The sources I have don't directly answer that. Try rephrasing your question or asking something more specific.

---

## Query Interface

The interface is built with Gradio and launched via `python app.py`. It opens in the browser at `http://127.0.0.1:7860`.

**Input:** A free-text question typed into the message box at the bottom of the chat window. Questions can be submitted by pressing Enter or clicking the "Ask →" button.

**Output:** The answer appears as a chat message in the scrollable conversation thread above the input box. Answers include inline source citations in square brackets (e.g., `[reddit_eecs]`). If the system cannot find a relevant answer in the corpus, it returns the fallback message instead of generating a response from general knowledge.

**Example buttons:** Five pre-written example questions appear below the chat window. Clicking any one of them immediately submits the question and displays the answer — no typing required.

**Sample interaction transcript:**

> **User:** How many technical classes should EECS students take each semester?
>
> **Guide:** EECS students should take no more than 2 technical classes per semester, especially in their first semester. This allows for a full course load of 12 units while leaving time to build a support network and adjust to Berkeley's pace. Taking more is described as a way to "dig yourself into a hole" early on [reddit_eecs].

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | If studying EECS, how many technical classes should I take each semester? | No more than 2 technical courses per semester, especially in the first year; stacking CS 61A, 61B, CS 70 simultaneously is strongly discouraged | Correctly cited the 2-course recommendation and warned against stacking multiple technical courses, citing reddit_eecs | Relevant | Accurate |
| 2 | What is Berkeleytime and how does it affect class start times? | "Berkeleytime" means all classes start 10 minutes after their listed time; a 3–4pm class actually runs 3:10–4pm | Correctly explained Berkeleytime and the 10-minute offset, citing reddit_new_student | Relevant | Accurate |
| 3 | How early should I schedule a same-day CAPS appointment to guarantee a slot? | Before 10 AM, or the night before, to guarantee a same-day appointment | Returned the correct 10 AM cutoff and the recommendation to schedule the night before, citing reddit_mental_health | Partially relevant — correct chunk retrieved at rank 3; ranked below two less-relevant chunks | Accurate |
| 4 | What specific locations near Berkeley campus should I avoid late at night? | People's Park and downtown along Shattuck Ave, particularly the BART plaza | Correctly named People's Park and the BART plaza / Shattuck area as locations to avoid, citing reddit_safety | Relevant | Accurate |
| 5 | When cramming for finals, what content should I review first? | Content taught after the most recent midterm, because it wasn't covered on any previous exam and is most likely overrepresented on the final | Correctly described the prioritization order (post-last-midterm → beginning of semester → middle), citing reddit_finals | Relevant | Accurate |

---

## Failure Case Analysis

**Question that failed:**
*If studying EECS, how many technical classes is it recommended to take each semester?* (Q1)

**What the system returned:**
The top 5 retrieved chunks include `reddit_eecs chunk 0` at rank 3 (distance 0.4886). This chunk contains the original poster's question — "Which teachers should I pick for the following classes: Math 53, Physics 7a, CS 61A, and English R1B? What should I do my first semester? How do I make a support network?" — with no useful advice whatsoever. It occupies a retrieval slot that could have been used for a more relevant answer chunk.

**Root cause (tied to a specific pipeline stage):**
The failure originates at the **ingestion stage**. In `fetch_reddit()`, the OP's post body (`selftext`) is included as a chunk if it exceeds 50 characters. For the EECS thread, the selftext is entirely a list of questions — not advice. However, because it mentions CS 61A, Math 53, and first semester, it shares enough vocabulary with EECS-related queries to score a mid-range cosine distance. The chunking pipeline has no mechanism to distinguish between an OP question prompt and a genuine answer, so it treats both identically.

**What you would change to fix it:**
Filter the OP's selftext before adding it as a chunk — for example, skip it if it ends with a question mark or contains more questions than statements. Alternatively, tag each chunk with a `chunk_type` field (`op_post` vs `comment`) and exclude `op_post` chunks from retrieval. This would eliminate the noise without discarding any real advice.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Having precise chunk sizes written in planning.md before writing any code made the implementation of `chunk.py` straightforward. Because the spec stated exactly 450 tokens (~346 words) with 75-token (~58-word) overlap for articles and one comment per chunk for Reddit, there was no guesswork when writing the sliding-window logic or the Reddit comment loop. The spec also made it easy to verify the output — I could check that article chunks were roughly the right word count and that Reddit chunks each had the thread title prepended.

**One way your implementation diverged from the spec, and why:**
The spec originally specified `k=3` for retrieval and defined evaluation questions that were too broad (e.g., "What free or discounted perks should students take advantage of?" and "What areas are unsafe at night?"). Both had to be changed after running the pipeline. `k` was increased to 5 because relevant chunks were being edged out of the top 3 by noisy chunks. The evaluation questions were revised to use vocabulary that more precisely matches the source text, because the original phrasings used formal/general language that the embedding model failed to align with the conversational Reddit content. The spec was updated to reflect both changes.

---

## AI Usage

**Instance 1 — Implementing chunk.py and embed.py**

- *What I gave the AI:* The Chunking Strategy section and Documents section of planning.md, along with the pipeline diagram, and asked it to implement `chunk.py` and `embed.py` matching the specified approach.
- *What it produced:* A `chunk.py` with a sliding-window `chunk_article()` function and a comment-based `chunk_reddit()` function that prepended the thread title; an `embed.py` that loaded chunks, initialized `all-MiniLM-L6-v2`, created a ChromaDB collection with cosine similarity, and stored chunks in batches of 100.
- *What I changed or overrode:* The Plexuss source was blocked by anti-scraping and required manually pasting the article content into the JSON file. The raw dailycal_survival content contained social-share button text ("Facebook Twitter WhatsApp...") that was appearing as a top retrieval result — this required both manually cleaning the document JSON and adding CSS selector-based stripping to `fetch_article()` in `ingest.py`.

**Instance 2 — Designing and revising the evaluation questions**

- *What I gave the AI:* All 10 source document JSON files and asked it to generate 5 specific, verifiable evaluation questions with expected answers, using Q1 (the EECS class-count question) as a reference for the level of specificity required.
- *What it produced:* 5 questions targeting specific facts in the corpus: Berkeleytime (10-minute offset), CAPS same-day appointment cutoff (10 AM), BearWalk + shuttle end time (3 a.m.), unsafe locations (People's Park, Shattuck/BART), and finals cramming prioritization (post-last-midterm content first).
- *What I changed or overrode:* After running retrieval, Q3 and Q4 were performing poorly. The root cause was traced to vocabulary mismatch and chunk dilution. Q4 (BearWalk/shuttle) was replaced entirely with a locations-based question because the BearWalk detail lived in a multi-topic article chunk that never surfaced for safety queries. Q3 was rephrased to use vocabulary closer to the source text ("schedule" instead of "submit", "guarantee" instead of "guaranteed a slot").
