---
name: run-improvement-cycle
description: Use when running the improvement loop for a self-improving agent (score the live agent, coach one candidate, score the candidate, compare) and putting a single promote-or-reject decision to the user; also covers the level 3 automatic variant.
---

# Run an improvement cycle

## Purpose

Run the full loop once: the verifier scores the live agent, the coach writes one candidate, the verifier scores the candidate on the full answer key, and the results are compared. Then show the user both scores, the change, and one decision: promote or reject. At level 2 this skill never promotes on its own.

## Inputs

- A complete agent folder: `validate` passes with no errors and the answer key has at least `min_cases` rows.
- `config.json` for the level and `max_iterations`.

## Steps (level 2, the default)

1. Run `python3 path/to/scripts/sia.py validate <agent>`. Stop on any ERROR. If there is a pending `candidate.md` from an earlier cycle, ask the user whether to resolve it first with `promote-or-reject`.
2. **Score the live agent.** Follow `verify-agent` with target `live`, in separate generator and verifier contexts. This records `runs/NNN-live.json` and a coach brief.
   Score the live agent fresh every cycle, even if it was scored before. Reason: model graders vary between runs, and comparing against a fresh live score in the same conditions is fairer than comparing against an old one.
3. If every case passed, stop and tell the user there is nothing to improve on the current key.
4. **Coach one candidate.** Follow `coach-candidate` in its own context. It writes `candidate.md` and `candidate-change.txt` from the train-only coach brief.
5. **Score the candidate on the full answer key**, train and holdout. Follow `verify-agent` with target `candidate`.
6. **Compare:**

   ```
   python3 path/to/scripts/sia.py compare <agent>
   ```

   It prints both scores (all, train, holdout), every fixed row and every regression (a row the live agent passed and the candidate fails), and whether the candidate qualifies: higher total and no regressions. It refuses if `answer-key.md` or `verifier.md` changed between or since the two runs, or if either agent file changed after it was scored. If it refuses, do not work around it: find out what changed and rescore.
7. **Put one decision to the user.** Show, in this order:
   - live score and candidate score, with train and holdout separately;
   - the one-line change;
   - fixed rows and regressions, each with the verifier's reason;
   - whether it qualifies under the rule, and that the rule is this repository's addition;
   - then ask: promote or reject?
8. Carry out the answer with `promote-or-reject`. Do not promote without an explicit answer.

## Level 3 variant (automatic)

Use only when `config.json` has `"level": 3`. Check with `choose-autonomy-level` if unsure.

1. Repeat steps 2 to 6 in rounds.
2. After each comparison: if the candidate qualifies, run `sia.py promote <agent> --by auto`; if not, run `sia.py reject <agent> --by auto --reason "<why, from compare>"`. `promote --by auto` is refused by the script unless the level is 3 and the candidate qualifies.
3. Stop when every case passes, or after `max_iterations` rounds (default 10), whichever comes first. Count rounds yourself; the script does not.
   Reason: the cap bounds cost and prevents an endless loop.
4. Show the score from every round: round number, live score, candidate score, change, decision. `versions/LOG.md` holds the same record.
5. At the end, show the user the final `agent.md` diff against the version the loop started from, and the holdout scores across rounds.

Cautions from the video, to repeat to the user before a level 3 run:

- Automatic mode does not remove the need to think about how you want improvements made.
- On non-technical work, the risk is that you stop understanding how your agent works, because it changes without you.
- Level 3 is for strictly verifiable pass/fail cases, mainly technical work. If the verifier has no exact, measurable criterion, stay at level 2.

Additional caution (not from the video): a loop that runs until every row passes tends to write the rows into the agent. Watch the holdout scores; if train scores rise while holdout scores stay flat or fall, stop and review by hand.

## Output

One recorded live run, one candidate run, a comparison, and either a decision by the user (level 2) or a per-round score table (level 3).

## Rules

- Never promote at level 2 without the user's explicit decision in this conversation.
- Never edit `answer-key.md` or `verifier.md` during a cycle. If the user wants to add a case mid-cycle, add it, then restart the cycle from step 2.
- Keep the roles in separate contexts as described in `verify-agent` and `coach-candidate`. If the harness cannot, say so in the report to the user.

## Source

Deep dive Part 1, sections 1.5 and 1.6 (video 10:58 to 15:12): compare on the missed cases and all historical cases; the level 2 on-screen prompt at 13:08 (score live, one candidate, score candidate on the full key, show both scores, the change and one choice, never promote on its own); level 3 at 13:36 to 14:02 and the prompt at 13:52 (auto-promote if higher, stop when all match or at 10 iterations, save versions, show every round's score); the cautions at 14:02 to 15:12. Additions not from the video: the regression rule and "qualifies" (Part 2, gap 2), holdout scores (gap 1), the hash refusal (gap 5), row-by-row comparison (gap 4).
