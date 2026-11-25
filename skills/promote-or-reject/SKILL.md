---
name: promote-or-reject
description: Use when the user (or, at level 3, the automatic loop) has decided whether a self-improving agent's pending candidate.md becomes the live agent, to carry out that decision and record it in the version log.
---

# Promote or reject a candidate

## Purpose

Carry out a decision about `candidate.md`: make it the live agent, or set it aside with a reason. Either way the old file is kept in `versions/` and the decision is logged.

## Inputs

- A pending `self-improve/<agent>/candidate.md` and its `candidate-change.txt`.
- A recorded live run and candidate run that `sia.py compare` accepts.
- The decision and who made it: `human`, or `auto` at level 3 only.

## Steps

1. Confirm the decision. At level 2 it must come from the user, explicitly, in this conversation. Restate it: "Promote the candidate that <change>?" or "Reject it because <reason>?"
2. Run `python3 path/to/scripts/sia.py compare <agent>` once more and show the output, so the decision is made on current numbers.
3. **To promote:**

   ```
   python3 path/to/scripts/sia.py promote <agent> --by human --change "one line"
   ```

   `--change` defaults to `candidate-change.txt`. The script refuses if there is no candidate, the candidate is identical to the live file, there is no comparable pair of runs, any file changed since it was scored, or the answer key or verifier changed (tamper check). With `--by auto` it also refuses unless `config.json` says level 3 and the candidate qualifies (higher total and no regressions). At level 2 a human may promote a candidate that does not qualify; the script prints a note, and you should make sure the user has seen the regressions first.

   On success it copies the candidate to the next `versions/vNNN.md`, moves it to `agent.md`, removes `candidate-change.txt`, and appends a row to `versions/LOG.md` with both scores, the change, the decision and who made it.

4. **To reject:**

   ```
   python3 path/to/scripts/sia.py reject <agent> --reason "one line"
   ```

   It moves the candidate to `versions/rejected-NNN.md` and logs the change, the reason and the scores (scores are logged only if the runs still describe the current files). The live agent is unchanged.

5. Run `python3 path/to/scripts/sia.py validate <agent>` and `status`, and report the new live version and the log row to the user.

## Without the script

Do the same by hand with your file write tools, in this order: confirm the answer key and verifier have not changed since both runs (compare against version control); copy `candidate.md` to the next `versions/vNNN.md` (or to `versions/rejected-NNN.md` for a rejection); for a promotion, replace `agent.md` with it; delete `candidate.md` and `candidate-change.txt`; append one row to `versions/LOG.md` with the date, version, both scores, the change, `promoted` or `rejected: <reason>`, and `human` or `auto`. Never edit earlier log rows.

## Output

A new live version or a rejected-candidate file, and one new row in `versions/LOG.md`.

## Rules

- At level 2, never promote without the user's explicit decision. Do not treat silence, or approval of an earlier candidate, as approval of this one.
- Never use `--by auto` at level 1 or 2, and never change `config.json` to make it work. Changing the level is the user's decision, made with `choose-autonomy-level`.
- If the script refuses, report the refusal verbatim and stop. Do not edit files to get past it.
  Reason: each refusal guards one of the failure modes the design exists to prevent: an unscored change, a moved test, or an unreviewed automatic promotion.
- A rejection is not a failure. Rejected candidates and their reasons are kept so the coach does not try the same change again.

## Source

Deep dive Part 1, sections 1.5 and 1.6 (video 9:52 to 10:16, 13:08, 13:52): the versions folder with old versions and rejected candidates and a one-line reason; at level 2 one choice, promote or reject, never promoting on its own; at level 3 automatic promotion if the candidate scores higher, saving each promoted version. Additions not from the video: the append-only log with both scores and who decided (Part 2, gap 6), the regression rule for automatic promotion (gap 2), and the hash refusal (gap 5).
