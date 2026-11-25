# Answer key: helpdesk

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
| c001 | Where do I find the checkout link to send a customer? | Send the live link, shop.fernhill.example/checkout. It is on the Notion page Sales > Links. Never send the staging link. | shop.fernhill.example/checkout; Notion page Sales > Links; not the staging link | train | 2026-11-24 | fictional example |
| c002 | What's our refund window? | 30 days from delivery for standard items. | 30 days; from delivery | train | 2026-11-24 | fictional example |
| c003 | Who approves discounts? | Any sales rep can apply up to 10%. Anything above 10% needs approval from Dana (Head of Sales) in #discounts. Nothing above 25%. | up to 10% without approval; above 10% needs Dana; ask in #discounts; 25% maximum | train | 2026-11-24 | fictional example |
| c004 | Someone emailed asking about wholesale pricing. What do I do? | Forward it to wholesale@fernhill.example and do not quote prices yourself. | forward to wholesale@fernhill.example; do not quote prices | train | 2026-11-24 | fictional example |
| c005 | A customer wants to return a custom-printed wedding notebook. Can we refund it? | No. Custom-printed orders are not refundable. If it was misprinted, we reprint or refund it if they report it within 14 days of delivery. | custom-printed orders not refundable; misprint exception; 14 days from delivery | train | 2026-11-24 | fictional example |
| c006 | What time do orders need to be in to ship the same day? | Before 2pm UK time, Monday to Friday. Later orders ship the next business day. | 2pm; weekdays only; later orders ship next business day | train | 2026-11-24 | fictional example |
| c007 | A customer ordered at 4pm on Friday. When will it ship? | On Monday, the next business day, because it missed the 2pm cutoff. | Monday / next business day; missed the 2pm cutoff | holdout | 2026-11-24 | fictional example |
| c008 | I'm locked out of the admin panel. Should I message Sam directly? | No. Open a ticket in #it-help; Sam handles admin panel access from there. | open a ticket in #it-help; not a direct message | holdout | 2026-11-24 | fictional example |
