---
name: verify-agent
description: Use when scoring a self-improving agent's live file (agent.md) or a candidate (candidate.md) against its answer key, to produce a pass/fail report with a reason for every case and record it as a run.
---

# Verify an agent

## Purpose

Answer one question for every case in the answer key: is the agent's answer right or wrong, and why. The verifier is read-only and has no stake in the result; that is what makes the score mean something.

## Inputs

- `self-improve/<agent>/answer-key.md`
- `self-improve/<agent>/verifier.md` (the verifier's role instructions)
- The target: `live` (`agent.md`) or `candidate` (`candidate.md`).

## Separate contexts

Use three contexts, none of which is the one that wrote the agent file:

1. **Generator context**: loaded with the target file as its instructions and nothing else. It receives only the `input` of each case.
2. **Verifier context**: loaded with `verifier.md`, `answer-key.md` and the generator's answers. It does not need the agent file.
3. **Runner**: you, coordinating, and recording the result with `sia.py`.

Use a sub-agent or separate session for each if your harness has them, otherwise a fresh conversation for each, with only the listed files pasted in. If even that is not possible, say plainly in the report that grading was done in the same context as the work, and treat the score as weak evidence.
Reason: the student cannot mark their own exam. A model grading its own output tends to be overconfident.

## Steps

1. Confirm the target with the user if it is not obvious. Check the target file exists.
2. Collect answers. For every row, train and holdout alike, give the generator context the row's `input` only. Never show it `expected` or `must`. Keep each answer verbatim. Ideally each case gets a fresh generator context; if that is too costly, one generator context may answer all inputs in turn, and the report should say so.
3. Grade. In the verifier context, follow `verifier.md`: for each row, pass only if every `must` item is present and nothing contradicts `expected`. Write a reason for every row, pass or fail. For a fail, name what is missing or wrong.
4. Report to the user:
   - "X of N matched", with train and holdout counts given separately.
   - Every miss next to the expected answer.
5. Record the run. Save the verifier's grades as JSON (a list of `{"id", "pass", "reason", "answer"}`), then:

   ```
   python3 path/to/scripts/sia.py record <agent> --target live --input grades.json
   ```

   `record` refuses unless every case is covered exactly once and every row has a reason. It writes `runs/NNN-<target>.json` with the SHA-256 of `answer-key.md`, `verifier.md` and the scored file, and a train-only coach brief, `runs/NNN-<target>-coach.md`.

   Without the script, write the same JSON by hand: `schema`, `agent`, `run`, `target`, `file`, `file_sha256`, `live_version`, `recorded`, `answer_key_sha256`, `verifier_sha256`, `results` (each with `id`, `set`, `pass`, `reason`, `answer`) and `totals` (`train`, `holdout`, `all`, each `{"passed", "total"}`). Compute hashes with any SHA-256 tool. Write the coach brief by hand, with train rows only.

## Output

A recorded run in `runs/`, a coach brief, and the report shown to the user.

## Rules

- The verifier never edits anything: not the agent, not the candidate, not the answer key, not its own instructions. It returns grades; the runner records them.
  Reason: a grader that can change what it grades against, or the thing it grades, produces a score that means nothing.
- Never pass a row on the strength of style, length or effort. Grade the `must` items.
- If you cannot tell whether a `must` item is present, it is not present.
- Give a reason on passes too. Model graders can grade the same answer differently on two runs; reasons on every row let the comparison be checked row by row. (Addition, not from the video.)
- Do not suggest fixes in the report beyond naming what was missing. Fixing is the coach's job.

## Source

Deep dive Part 1, section 1.4 (video 5:22 to 8:16): the generator should not check its own work; the verifier only answers right or wrong, explains why, never edits anything; the on-screen prompt at 8:09 ("X of 20 matched", misses next to the real answer). Additions not from the video: grading on the `must` column (Part 2, gap 3), reasons on passes (gap 4), holdout rows scored separately (gap 1), hashes in the run file (gap 5).
