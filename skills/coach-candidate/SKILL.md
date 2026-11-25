---
name: coach-candidate
description: Use when a self-improving agent has a verifier report with misses and a candidate with exactly one change to the live agent file is needed, written next to the live file without touching it.
---

# Coach a candidate

## Purpose

Read what the verifier found and write `candidate.md`: a copy of the live `agent.md` with exactly one change, plus a one-line statement of the change. The live file stays as it is, as the control.

## Inputs

- The newest live coach brief, `self-improve/<agent>/runs/NNN-live-coach.md`. It holds the train misses with expected answers, the agent's answers and the verifier's reasons.
- `agent.md`
- `versions/`, including `LOG.md` and any `rejected-NNN.md`, to see what has already been tried.
- `coach.md` (the coach's role instructions).

## Separate context

Run the coach in its own context, separate from the generator and the verifier: a sub-agent or separate session if your harness has them, otherwise a fresh conversation, loaded with only the files listed above. Where the harness supports per-agent write permissions, allow writes to `candidate.md` and `candidate-change.txt` only.
Reason: the verifier must not fix (the score stops meaning anything and the fixer learns to pass the test), and the generator must not fix itself (it would be editing the thing it is trying to measure).

## Steps

1. Read the coach brief and `versions/LOG.md`. Note any change that was already tried and rejected, and why.
2. Group the misses by likely cause, using the verifier's reasons.
3. Choose one cause. Prefer the one behind the most misses. If tied, prefer the change least likely to disturb cases that pass now, and avoid repeating a rejected change.
4. Copy `agent.md` to `candidate.md` with your file write tools. Make one change: add, remove or rewrite one rule, or add one missing piece of knowledge. Give a new rule its reason, in the file's existing style.
5. Before saving, reread the changed section and check that nothing the live file said has been lost unintentionally. A rewrite that drops an existing fact is a common cause of regressions.
6. Write `candidate-change.txt`: one line saying what changed and which miss it addresses.
7. Run `python3 path/to/scripts/sia.py validate <agent>` if the harness can run it; it checks that the candidate differs from the live file. Then stop.

## Output

`candidate.md` and `candidate-change.txt`. Nothing else is written.

## Rules

- One change per candidate. If the change needs "and" to describe, it is two; pick one.
  Reason: with several changes at once you cannot tell which one mattered.
- Never edit `agent.md`, `answer-key.md`, `verifier.md`, `coach.md` or `config.json`.
  Reason: if the coach could change the test, the easiest way to pass would be to change the test; if it could change the live agent, there would be no control.
- Never read `answer-key.md` or the run JSON files; they contain holdout rows. Work from the coach brief, which has train rows only. (Holdout rows are an addition, not from the video.)
- State knowledge and rules in general form. Do not paste a test question and its answer into the agent as a special case.
  Reason: an agent that memorises the test passes it without doing the job.
- Do not score the candidate or decide whether it is promoted.

## Source

Deep dive Part 1, section 1.5 (video 8:16 to 11:10): why neither the verifier nor the generator should fix; the candidate next to the live file; one change so the variable is isolated; never touching the answer key or verifier; keeping versions and rejected candidates with a one-line reason; separate permissions enforced by the harness. Additions not from the video: the train-only coach brief and the holdout restriction (Part 2, gap 1), and `candidate-change.txt` as a fixed place for the one-line statement.
