---
name: quick-fix-from-conversation
description: Use when the user notices that an agent or skill got something wrong in the current conversation and asks for it to be updated so it does not happen again (level 1 self-improvement).
---

# Quick fix from the conversation (level 1)

## Purpose

Level 1: the user notices a problem and approves the fix. The instruction from the video is, in effect: based on this conversation, update the skill or agent I used so this does not happen again. This skill does that, and first records the case in the answer key so the fix is still checked by later grading.

## Inputs

- The current conversation, containing the mistake and, ideally, the right answer.
- The agent or skill file that was used. If it is a self-improving agent, that is `self-improve/<agent>/agent.md`.

## Steps

1. Identify the mistake. State it back to the user in one or two sentences: what was asked, what the agent said, what it should have said. Ask the user to confirm or correct this.
2. **Add the case to the answer key first** (addition, not from the video). If the agent has a `self-improve/<agent>/` folder:

   ```
   python3 path/to/scripts/sia.py add-case <agent> --input "..." --expected "..." \
       --must "..." --set train --source "conversation, <date>"
   ```

   Use the user's confirmed answer for `expected`. Ask the user what must be present for `must`. Without the script, add the row by hand. If there is no answer key yet, skip this step and suggest `build-answer-key` afterwards.
   Reason: a fix that is not in the key can be undone by a later change without anyone noticing.
3. Make the smallest change to the agent or skill file that would have prevented the mistake: one rule, with its reason, or one missing fact. Use your file write tools. Keep the file's existing structure.
4. Show the user the change as a before/after of the affected section, and ask for approval. Apply corrections.
5. If the agent has a `self-improve/` folder, record the hand edit:

   ```
   python3 path/to/scripts/sia.py snapshot <agent> --change "one line"
   ```

   This copies the edited `agent.md` to the next `versions/vNNN.md` and logs it with decision `edited`. Without the script, do the same by hand.
6. Run `python3 path/to/scripts/sia.py validate <agent>`. Tell the user that runs recorded before the new row no longer match the answer key, so the next improvement cycle will start by scoring the live agent again.

## Output

One new answer-key row (where a key exists), one change to the agent file, and a recorded version.

## Rules

- Change one thing. If the conversation shows several problems, fix the one the user asked about and list the others.
  Reason: several changes at once make it impossible to tell which one helped or hurt.
- Give the new rule its reason. Reason: so it can be applied to cases it did not foresee, and changed sensibly later.
- Do not edit `answer-key.md` beyond adding the new row, and do not edit `verifier.md` or `coach.md`.
- Do not use this skill to apply a coach's candidate. Candidates go through `promote-or-reject`.
- If `candidate.md` is pending, tell the user that editing `agent.md` now will make the pending comparison invalid, and ask whether to resolve the candidate first.

## Source

Deep dive Part 1, section 1.6 (video 12:24 to 12:44): level 1, you notice, tell the model, and it writes the rule; the one-line instruction. Section 1.4 (7:32 to 7:45): every miss becomes a new row. Adding the row before the rule is this repository's addition (Part 2, gap 7), as are `snapshot` and the version log (gap 6).
