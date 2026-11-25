# Answer key: {{agent}}

<!--
The evaluation data set: example inputs on the left, the answer the human would actually
give on the right. It is the source of truth for grading every change to the agent.

Columns
- id: unique, for example c001. sia.py add-case assigns it.
- input: the question or task exactly as the agent would receive it.
- expected: the answer the human would give.
- must: the facts or decisions that must be present for a pass, separated by semicolons.
  The verifier grades on these, not on wording. (Addition, not from the video.)
- set: train or holdout. The coach never sees holdout rows, so a gain on them is evidence
  that a change generalises. (Addition, not from the video.)
- added: the date the row was added, YYYY-MM-DD.
- source: where the case came from, for example a chat thread, a ticket, or "miss in run 004".

Rules
- A model may draft rows. The human reviews and edits every row before it counts.
- Every time the agent gets something wrong, add a row for it.
- Only the human edits this file. The verifier and the coach never do. sia.py records a
  hash of this file with every run and refuses to compare or promote if it changed between runs.
- Write a literal pipe character as \| and a line break inside a cell as <br>.

Example row (inside this comment, so it is not parsed):
| c001 | What is our refund window? | 30 days from delivery for standard items; custom orders are not refundable. | 30 days; from delivery; custom orders not refundable | train | 2026-01-15 | team chat, March |
-->

| id | input | expected | must | set | added | source |
|---|---|---|---|---|---|---|
