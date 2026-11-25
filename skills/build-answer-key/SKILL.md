---
name: build-answer-key
description: Use when creating or extending the answer key (answer-key.md) for a self-improving agent, from real past cases the user points to, or when the agent has just got something wrong and the case should be recorded.
---

# Build the answer key

## Purpose

Build `self-improve/<agent>/answer-key.md`: a table mapping specific inputs to the answer the user would actually give. It is the source of truth for grading every future change, so every row must be one the user has reviewed.

## Inputs

- Real cases: past conversations, chat exports, tickets or logs that the user points to. Read only those.
- The user, available to review rows.
- `config.json` for `min_cases` (default 5).

## Steps

1. Ask the user where the real cases are. Prefer the most common questions the agent will face over unusual ones. In the video's example, the 20 most common questions from a team chat were pulled with the user's real answers.
2. Draft rows from that material. For each row:
   - `input`: the question as the agent would receive it.
   - `expected`: the user's real answer, in their words where possible.
   - `must`: the facts or decisions that must be present for a pass, separated by semicolons. Keep it to what matters; wording does not belong here. (Addition, not from the video.)
   - `source`: where it came from.
3. Show the drafted rows to the user and have them review every row: correct `expected`, tighten `must`, delete rows that are not representative. A row counts only after the user has approved it.
   Reason: the model drafting the key is not the source of truth; the user is.
4. Mark some rows `holdout`: roughly one in four, at least two, chosen by the user, spread across topics. The rest are `train`. (Addition, not from the video.)
   Reason: the coach never sees holdout rows, so a gain that also shows on holdout rows is evidence the change generalises rather than fitting the visible cases.
5. Add each approved row:

   ```
   python3 path/to/scripts/sia.py add-case <agent> --input "..." --expected "..." \
       --must "fact one; fact two" --set train --source "team chat, March"
   ```

   It assigns the next id and today's date. Without the script, add the row to the table by hand with your file write tools, keeping ids unique and writing a literal pipe as `\|`.
6. Run `python3 path/to/scripts/sia.py validate <agent>`. Fix any ERROR. A warning about fewer than `min_cases` rows means the key is not yet big enough to compare versions.

## Keeping it alive

- Every time the agent gets something wrong in real use, add a row for that case, reviewed by the user.
- Adding or editing a row changes the file's hash. Any runs recorded before the change can no longer be compared, and the next cycle starts by scoring the live agent again. This is intended.

## Output

An answer key the user has reviewed row by row, with train and holdout rows, and a clean `validate`.

## Rules

- Only the user edits this file, directly or by approving rows you add for them. The verifier and the coach never edit it.
  Reason: if the test can be changed by the parts being tested, the easiest way to pass is to change the test.
- Do not write rows from the agent's own outputs. Use the user's real answers.
- Do not copy rows into `agent.md`.
- With a small key, a one-row difference is a large share of the total. Say so when reporting scores. With 20 rows, one row is five points.

## Source

Deep dive Part 1, section 1.4 Part A (video 6:15 to 7:45): the answer key as input-to-expected mapping, model drafts and user edits, the 20 most common questions, `answer-key.md` as the evaluation data set, a new row on every miss. Additions not from the video: the `must` column (Part 2, gap 3), holdout rows (gap 1), and the hash-based invalidation of earlier runs (gap 5).
