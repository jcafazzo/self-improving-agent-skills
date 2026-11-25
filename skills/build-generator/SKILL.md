---
name: build-generator
description: Use when writing or rewriting the live agent file (agent.md) for a self-improving agent, by interviewing the user about the job one question at a time.
---

# Build the generator

## Purpose

Write `self-improve/<agent>/agent.md`: the agent that does the job. It must read as a specific job description, give the reason behind every rule, and tell the agent to say so instead of guessing when its instructions do not cover a question.

## Inputs

- A scaffolded agent folder (see `scaffold-self-improving-agent`).
- The user, available to answer questions.
- Any material the user points to: existing prompts, policies, past answers. Read only what they point to.

## Steps

1. Ask one question at a time. Wait for the answer before asking the next. Do not send a list of questions.
   Reason: one question at a time gets considered answers; a list gets skimmed.
2. Cover, in roughly this order:
   - What the agent's job is, for whom, and what is out of scope.
   - What it receives as input and what a good output looks like (length, form, tone).
   - The facts, policies or preferences it answers from.
   - What the user says yes to and no to, and why.
   - How the user talks, if the output is meant to sound like them.
   - What the agent must never do (for example send messages or commit to anything on the user's behalf).
3. For every rule the user gives, ask why if they have not said. Write the reason under the rule.
   Reason: a rule with its reason can be applied to cases the rule did not foresee, and gives the coach the context to change it sensibly later.
4. Write `agent.md` with your file write tools, using the template's sections: Job, Inputs, Output, What the agent knows, Rules, When the answer is not covered, Limits. Remove every `[[...]]` placeholder.
5. Keep the "When the answer is not covered" section: if the instructions do not answer a question, the agent says so and says what is missing.
6. Show the whole file to the user and ask for corrections. Apply them.
7. Run `python3 path/to/scripts/sia.py validate <agent>`. It will warn that `agent.md` differs from `versions/v001.md`. Record the written version:

   ```
   python3 path/to/scripts/sia.py snapshot <agent> --change "first written version"
   ```

   Without the script, copy `agent.md` to the next `versions/vNNN.md` and add a row to `versions/LOG.md` with decision `edited`.

## Output

A filled-in `agent.md`, recorded as a new version.

## Rules

- Do not invent facts the user has not given. Where something is missing, ask; if the user does not know, leave it out and let the "not covered" rule handle it.
  Reason: invented facts become confident wrong answers, and they are hard to spot later because they look like the user's.
- Keep facts in one place ("What the agent knows") and rules in another.
  Reason: the coach changes one thing at a time; that is easier when each thing lives in one place.
- Do not read or copy from `answer-key.md` while writing the agent. If the key already exists, write from the interview.
  Reason: an agent written from the test learns the test, not the job.
- Once an improvement cycle is running, do not use this skill to edit `agent.md` directly. Changes then go through the coach and promotion, or through `quick-fix-from-conversation` at level 1.

## Source

Deep dive Part 1, section 1.3 (video 2:00 to 3:30): a specific job description, the on-screen prompt at 3:20 (interview one question at a time, a reason behind every rule, say so instead of guessing, cannot send messages). The `snapshot` step and the version log are additions, not from the video (Part 2, gap 6).
