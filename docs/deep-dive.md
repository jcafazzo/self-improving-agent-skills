# Deep dive: "How To Build Self-Improving AI Agents with Claude (Stanford's Method)"

- Video: https://www.youtube.com/watch?v=UUg5oij7ptw
- Channel: Austin Marchese. Published 21 November 2026. Length 16:44.
- Read on 24 November 2026 from the auto-generated English captions and from the prompts shown on screen.

This document has two parts. Part 1 reports what the video says, in paraphrase, with timestamps. Part 2 is commentary by the author of this repository and is not from the video. The skills in this repository follow Part 1; where they add something from Part 2, the skill says so.

Timestamps are when the point is spoken. The chapter markers in the video description run earlier than the speech for some chapters (for example, the "Step 2" chapter starts during the sponsor segment), so they are not used here.

---

## Part 1. What the video says

### 1.1 Terms (0:19 to 1:25)

- An agent is a system with a goal that acts on an environment, collects feedback and corrects its steps. In practical terms: a model, tools and context used to get a job done. (0:27 to 0:50)
- A main agent can create sub-agents with different tools and permissions. (1:04)
- A skill is a recipe handed to an agent. Skills can call agents and agents can use skills; the skill is the guide and the agent follows it. (1:08 to 1:25)

### 1.2 Two routes to self-improvement (1:30 to 2:00)

1. Retrain the model (fine-tuning, changing weights). The video sets this aside as out of scope for its audience.
2. Change what the model reads. This is the route the video takes. It names three things that can be improved: the agent's tools, its context, and its skills. (1:50)

### 1.3 Step 1: the generator (2:00 to 3:30)

- The generator is the agent that does the job. The name is attributed to the Stanford course. (2:06)
- It should have a specific, well-defined job description. (2:13)
- The worked example is a clone of the user: an agent that answers questions the way the user would. (2:22)
- Why that example: the best self-improving systems have a concrete, checkable way to judge an output. A course excerpt makes the point that math and engineering are easy domains because outputs can be verified, and that this approach works better where verification exists. (2:34 to 3:06)
- For a personal clone, the user is the source of truth. (3:11)
- On-screen prompt (3:20), paraphrased: build an agent that answers as I do; interview me first, one question at a time, about how I think, what I say yes and no to, and how I talk; write the agent file as a job description with a reason behind every rule; if my answers do not cover a question, the agent says so instead of guessing; it cannot send messages.
- An agent that produces work cannot tell you whether the work is good. That is the next step, described as the one most people skip. (3:27)

(3:41 to 5:22 is a sponsor segment and is not covered.)

### 1.4 Step 2: the verifier (5:22 to 8:16)

- The agent that did the work should not check it: "the student can't mark their own exam". (5:26)
- A course excerpt says models critiquing themselves is harder and a set of other models critiquing often works better, because models can be overconfident. (5:36)
- A study is cited: an agent ran 54 self-improvement cycles and reported improvement all 54 times, while 56% of the changes were flat or worse. No source is named. (5:48)
- So a second agent is needed whose only job is to review output. It has two parts. (6:05)

**Part A, the answer key (6:15 to 7:45)**

- A mapping from specific inputs to the output you want. For code this is a pass/fail test. For knowledge work it is a table: example input on the left, the answer the user would actually give on the right. (6:18 to 6:42)
- The model drafts the table and the user edits it directly. In the example, the 20 most common questions from the user's team chat, with the user's real answers, are pulled in and then reviewed by hand. (7:04 to 7:22)
- The file is an evaluation data set, named `answer-key.md` in the video. (7:24)
- It is a living document. Every time the agent gets something wrong, that becomes a new row. It is the source of truth for grading every future change. (7:32 to 7:45)

**Part B, the verifier agent (7:48 to 8:16)**

- Its goal is to answer "is this right or wrong". It never edits anything: not the answer key, not the agent. (7:54)
- It explains why it thinks an answer is wrong, because the reason is the context needed to fix it. (8:07)
- On-screen prompt (8:09), paraphrased: ask the agent every question in `answer-key.md` and compare each answer to mine; right or wrong, with a reason for each; report "X of 20 matched" with every miss next to my real answer; never edit anything.

### 1.5 Step 3: the coach (8:16 to 11:10)

- Why the verifier should not fix the generator (8:26 to 8:55):
  1. The score stops meaning anything if the grader also writes the fixes. The verifier is trustworthy because it is read-only and has no stake in the result.
  2. An agent that can see the test and write the fix learns to pass the test rather than do the job.
- Why the generator should not fix itself: it would be editing itself while trying to fix itself, a moving target. (8:59)
- The coach reads what the verifier found and writes a draft of the agent file, a candidate, next to the live one. The live file is never touched. (9:11 to 9:28)
- The candidate is a copy of the live agent with one thing changed, so the changed variable is isolated and the original stays constant as the control. (9:30 to 9:47)
- Rules (9:55 to 10:16):
  1. One change per draft. With eight changes you cannot tell which one mattered.
  2. The coach never touches the answer key or the verifier. If it could, the easiest way to pass would be to change the test.
  3. It keeps a versions folder, a history of past agents, so it can learn over time.
- On-screen prompt (9:52), paraphrased: the coach reads the verifier's misses and writes one change into a candidate file next to the live agent; it saves old versions and rejected candidates with a one-line reason in a versions folder; its permissions are set so it cannot edit the live agent, the answer key or the verifier.
- Three separate agents allow separate permissions, enforced by the harness and not only by instruction. (10:16 to 10:36)
- Compare the candidate with the original by testing on the cases the generator got wrong and on all the other historical cases. (10:58 to 11:08)

### 1.6 Step 4: pick a level (11:57 to 15:12)

| Level | Who proposes | Who approves | Video's guidance |
|---|---|---|---|
| 1 | You | You | Works from day one and for many uses. (12:24) |
| 2 | The system | You | The recommended default. (12:50) |
| 3 | The system | The system | Only with fully verifiable pass/fail cases. (13:36, 14:37) |

- Level 1: you notice a problem, tell the model, and it writes the rule. The one-line instruction given: based on this conversation, update the skill or agent I used so this does not happen again. (12:24 to 12:44)
- Level 2: generator, verifier and coach run on their own against past outputs, suggest an improvement and leave the decision to you. (12:50 to 13:05)
- On-screen prompt (13:08), paraphrased: a skill that runs the full loop. (1) The verifier scores the live agent. (2) The coach writes one candidate. (3) The verifier scores the candidate on the full answer key. Then show both scores, the change, and one choice: promote or reject. It never promotes on its own.
- A lighter level 2 is also mentioned: a tool that suggests improvements during a conversation for the user to approve or deny. This is the creator's own product and is not described in detail. (13:14 to 13:33)
- Level 3: loop generator, verifier and coach until every case in the answer key passes, or stop at 10 iterations. The cap is there to bound cost and prevent an endless loop. (13:36 to 14:02)
- On-screen prompt (13:52), paraphrased: run the improvement skill in a loop, promoting the candidate automatically if it scores higher; continue until every answer matches or 10 iterations; save each promoted version to the versions folder; show the score from every round.
- Caution, quoting a speaker from Weights & Biases: automatic mode does not remove the need to think about how you want improvements made. (14:02 to 14:14)
- Failure mode of level 3 on non-technical work: you stop understanding how your agent works and outcomes become unpredictable, because it changes without you. (14:18 to 14:31)
- Choosing: with a strictly verifiable pass/fail test, level 3 can work, mainly for technical work. If you cannot find an exact measurable criterion for the verifier, stay at level 2, where your judgement is the final sign-off. Use level 1 whenever you notice something. (14:31 to 15:12)

### 1.7 Summary and mental model (15:12 to 16:10)

- Four pieces: a generator with a clear job description and a reason behind every rule; an independent read-only verifier that checks against an answer key; a coach that proposes improvements in a separate candidate file; and a chosen level of autonomy. (15:20 to 15:52)
- Self-improving does not mean an agent rewriting itself until it is smarter. It means a feedback loop in which the intelligence is in the design of the system, including which decisions the model makes and which you make. (15:57 to 16:10)

### 1.8 Artifacts named in the video

| Artifact | Purpose | Who may write it |
|---|---|---|
| Agent file (the generator) | The live instructions | Only a promotion step |
| `answer-key.md` | Input and expected-answer table | The human; new rows on each miss |
| Verifier agent | Grades, explains misses | The human |
| Coach agent | Writes one-change candidates | The human |
| Candidate file | Draft next to the live agent | The coach |
| Versions folder | Old versions, rejected candidates, one-line reasons | Coach / promotion step |
| Improvement loop skill | Runs score, coach, re-score, decision | The human |

### 1.9 Failure modes named in the video

1. Self-grading and overconfidence (5:26 to 5:58).
2. Score loses meaning when grader and fixer are the same (8:34).
3. Gaming the test (8:44).
4. Editing the test to pass it (10:04).
5. Moving target when the generator edits itself (8:59).
6. Many changes at once, so the effect cannot be attributed (9:57).
7. Unbounded loops that cost time and money (13:56).
8. Losing understanding of your own agent under full automation (14:18).
9. Attempting level 3 without a measurable criterion (14:52).

### 1.10 Links in the description

The description links the creator's own videos, newsletter and product, and a sponsor. It does not link the Stanford course, a repository, or the study behind the 54-cycle figure.

---

## Part 2. Commentary (not from the video)

**What could not be confirmed.**

- The course is not named in the video. A web search suggests it is Stanford CS329A, "Self-Improving AI Agents" (https://cs329a.stanford.edu/), whose syllabus covers verifiers and test-time compute. The video does not confirm this, and the course lectures were not reviewed for this document.
- "Generator", "verifier" and the verifiability argument are presented as from the course, with excerpts. The "coach" role, the three levels and the file layout appear to be the creator's packaging; the video does not attribute them to the course.
- The 54-cycle, 56% figure has no source in the video. A search found a secondary write-up repeating the numbers and cautioning that they describe one testbed. The primary paper was not found. Treat it as an illustration.
- The captions are auto-generated. Names and some words may be wrong.

**Gaps the video leaves, and how this repository fills them.**

1. *Overfitting to the answer key.* A level 3 loop that runs until every row passes will tend to write the rows into the agent. The video does not mention a held-out set. The scaffold here supports marking rows as `holdout`; the coach works from a brief that leaves them out, and every run reports train and holdout scores separately.
2. *What "scores better" means.* The video says promote if the candidate scores higher. This repository adds a regression rule: a candidate that newly fails a case the live agent passed is reported as a regression, and at level 3 it is not promoted even if the total is higher.
3. *Grading rubric for prose.* "Matches what I would say" needs a definition. The answer-key template has a per-row `must` column for the facts or decisions that have to be present, so the verifier grades on substance and not on wording.
4. *Verifier noise.* A model-based verifier can grade the same answer differently on two runs. The verifier skill asks for a reason on every row, pass or fail, and the loop compares row by row, not only totals.
5. *Tamper evidence.* The video relies on harness permissions to stop the coach editing the key or verifier. Not every harness has permissions, so the script records a hash of the answer key and verifier at the start of a cycle and refuses to promote if either changed.
6. *Record of decisions.* The versions folder is described loosely. Here it has an append-only log with the date, both scores, the one-line change, the decision and who made it.
7. *Level 1 feeds the key.* The video says each miss becomes a row, and separately that level 1 is "tell it to fix the rule". Here the level 1 skill does both: it adds the row first, then the rule, so quick fixes are still covered by later grading.

**Where the method fits and where it does not.** It fits tasks with a stable notion of a right answer and a modest number of representative cases: support answers, triage, formatting, routing, code with tests. It fits poorly where quality is taste with no stated criteria, or where cases are too few to tell a real gain from noise. With 20 rows, one row is five points; a one-row gain should not be read as more than that.
