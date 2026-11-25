---
name: choose-autonomy-level
description: Use when deciding how much a self-improving agent may change itself (level 1, 2 or 3), before the first improvement cycle or when the user wants to change the level, and when writing that choice to config.json.
---

# Choose an autonomy level

## Purpose

Help the user pick who proposes improvements and who approves them, using the video's criteria, and record the choice in `self-improve/<agent>/config.json`.

## The levels

| Level | Who proposes | Who approves | When it fits |
|---|---|---|---|
| 1 | The user | The user | From day one, for many uses. The user notices a problem and asks for the rule to be written (`quick-fix-from-conversation`). |
| 2 | The system | The user | The recommended default. Generator, verifier and coach run on past cases and suggest one change; the user promotes or rejects (`run-improvement-cycle`). |
| 3 | The system | The system | Only with fully verifiable pass/fail cases, mainly technical work. The loop promotes automatically, with an iteration cap. |

Levels are not exclusive. Level 1 fixes can be made at any time, whatever the configured level.

## Inputs

- The agent's job (from `agent.md`) and its answer key, if one exists.
- The user, available to answer.

## Steps

Ask one question at a time.

1. "Can every case in the answer key be judged pass or fail exactly, without judgement? For example, by a test that runs, or a fact that is either present or not." Look at the answer key with the user. If several rows need taste or judgement to grade, the answer is no.
2. "Does it matter to you to understand every change the agent makes to itself?" For personal or non-technical agents (tone, judgement calls, voice) the answer is usually yes.
3. "Do you have enough cases for a one-row difference to mean something?" With few rows, one row is a large share of the score and can be noise. (This criterion is an addition, not from the video.)
4. Recommend:
   - **Level 3** only if question 1 is clearly yes, question 2 is no, and the key has enough rows, including holdout rows.
   - **Level 2** if question 1 is no or uncertain, or question 2 is yes. If you cannot find an exact, measurable criterion for the verifier, stay at level 2.
   - **Level 1 only** if there is no answer key yet, or the user does not want cycles run at all. Recommend building a key so that level 2 becomes possible.
5. Before recording level 3, repeat the cautions: automatic mode does not remove the need to think about how improvements should be made, and on non-technical work you can stop understanding how your agent works because it changes without you.
6. Write the choice into `config.json` with your file write tools, changing only `level`, and `max_iterations` if the user wants a cap other than 10:

   ```json
   {"agent": "<agent>", "level": 2, "max_iterations": 10, "min_cases": 5,
    "promotion_rule": "higher total and no regressions"}
   ```

7. Run `python3 path/to/scripts/sia.py validate <agent>` and report the `config.json` line.

## Output

A recommended level with the reason, and `config.json` updated after the user agrees.

## Rules

- The user decides the level. Do not raise it without their explicit agreement.
- Never raise the level to get past a refusal from `sia.py promote --by auto`.
  Reason: that refusal is the check that keeps level 2 a human decision.
- Write down, in your reply, which answers led to the recommendation, so the user can revisit it later.

## Source

Deep dive Part 1, section 1.6 (video 11:57 to 15:12): the three levels and who proposes and approves; level 1 from day one; level 2 as the recommended default; level 3 only with fully verifiable pass/fail cases, the 10-iteration cap, the Weights & Biases caution, the failure mode of losing understanding on non-technical work, and the rule to stay at level 2 without a measurable criterion. The case-count question is an addition, not from the video (Part 2, "Where the method fits").
