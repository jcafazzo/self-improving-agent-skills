# Toy cycle transcript

This is a record of one full level 2 improvement cycle, plus part of a second cycle, run by hand on a toy agent. Every command below was run from `examples/toy-cycle/`, and the output under each command is the real output, copied from a log written while the commands ran. `[exit N]` is the command's exit status.

## Read this first

**One model played every role.** The generator, the verifier and the coach were all played by the same model, in the same session that wrote this repository. That model also knew which cases the first version of the agent was meant to miss. So this transcript shows the file mechanics and the guards in `sia.py`: scaffolding, recording, the coach brief withholding holdout rows, comparison, the regression rule, the tamper check, promotion and rejection. It does not show independent grading, and it is not evidence that the method improves agents. For that, run each role in its own context as the skills describe, on your own cases.

Other things to know:

- The task is fictional. Fernhill Paper Co., its staff, links and channels are made up.
- The first version of the agent (`versions/v002.md`) was written to leave out the discount policy and the custom-order refund rule, so that it would miss two cases (c003 and c005).
- The generator's answers and the verifier's grades are in `grades/*.json`. The generator answers were written from the agent file being scored and nothing else; the grades were made against each row's `must` column.
- Run 003 rescored the live agent at the start of cycle 2. `agent.md` at that point was byte-identical to the candidate scored in run 002, so the same answers and grades were reused (`grades/run3-live.json` is a copy of `grades/run2-candidate.json`).
- The second cycle's candidate was deliberately flawed: its rewrite of the refunds line drops the 30-day standard window. That was done to show the regression check and a rejection.
- An earlier attempt at this walk-through was thrown away: a file write failed and the following commands ran against the unfilled template. The folder was deleted and everything below was run again from `init`.
- The tamper demonstration backs up the answer key to `/tmp` and restores it afterwards; the backup was deleted.

## Setup

Scaffold the agent folder.

```
$ python3 ../../scripts/sia.py init helpdesk
created self-improve/helpdesk with: agent.md, answer-key.md, verifier.md, coach.md, config.json, PERMISSIONS.md, versions/LOG.md, versions/v001.md, runs/
next: fill in agent.md and answer-key.md, then run: sia.py validate helpdesk
[exit 0]
```

`agent.md` was then written by hand (it is preserved as `self-improve/helpdesk/versions/v002.md`). `validate` notices the live file no longer matches `v001`, and `snapshot` records it.

```
$ python3 ../../scripts/sia.py validate helpdesk
[self-improve/helpdesk]
OK     all 8 files and runs/ present
OK     config.json: level 2 (system proposes, human approves)
WARN   answer key not yet filled in: 0 cases, minimum is 5
OK     versions/LOG.md: 1 entries
WARN   agent.md differs from versions/v001.md; record the edit with sia.py snapshot
helpdesk: 0 errors, 2 warnings
[exit 0]

$ python3 ../../scripts/sia.py snapshot helpdesk --change 'first written version of the helpdesk generator'
recorded the edited agent.md as versions/v002.md
[exit 0]
```

Eight cases are added to the answer key: six train, two holdout. In real use the human would draft these from past conversations and review every row.

```
$ python3 ../../scripts/sia.py add-case helpdesk --input 'Where do I find the checkout link to send a customer?' --expected 'Send the live link, shop.fernhill.example/checkout. It is on the Notion page Sales > Links. Never send the staging link.' --must 'shop.fernhill.example/checkout; Notion page Sales > Links; not the staging link' --set train --source 'fictional example'
added c001 (train) to answer-key.md
[exit 0]

$ python3 ../../scripts/sia.py add-case helpdesk --input "What's our refund window?" --expected '30 days from delivery for standard items.' --must '30 days; from delivery' --set train --source 'fictional example'
added c002 (train) to answer-key.md
[exit 0]

$ python3 ../../scripts/sia.py add-case helpdesk --input 'Who approves discounts?' --expected 'Any sales rep can apply up to 10%. Anything above 10% needs approval from Dana (Head of Sales) in #discounts. Nothing above 25%.' --must 'up to 10% without approval; above 10% needs Dana; ask in #discounts; 25% maximum' --set train --source 'fictional example'
added c003 (train) to answer-key.md
[exit 0]

$ python3 ../../scripts/sia.py add-case helpdesk --input 'Someone emailed asking about wholesale pricing. What do I do?' --expected 'Forward it to wholesale@fernhill.example and do not quote prices yourself.' --must 'forward to wholesale@fernhill.example; do not quote prices' --set train --source 'fictional example'
added c004 (train) to answer-key.md
[exit 0]

$ python3 ../../scripts/sia.py add-case helpdesk --input 'A customer wants to return a custom-printed wedding notebook. Can we refund it?' --expected 'No. Custom-printed orders are not refundable. If it was misprinted, we reprint or refund it if they report it within 14 days of delivery.' --must 'custom-printed orders not refundable; misprint exception; 14 days from delivery' --set train --source 'fictional example'
added c005 (train) to answer-key.md
[exit 0]

$ python3 ../../scripts/sia.py add-case helpdesk --input 'What time do orders need to be in to ship the same day?' --expected 'Before 2pm UK time, Monday to Friday. Later orders ship the next business day.' --must '2pm; weekdays only; later orders ship next business day' --set train --source 'fictional example'
added c006 (train) to answer-key.md
[exit 0]

$ python3 ../../scripts/sia.py add-case helpdesk --input 'A customer ordered at 4pm on Friday. When will it ship?' --expected 'On Monday, the next business day, because it missed the 2pm cutoff.' --must 'Monday / next business day; missed the 2pm cutoff' --set holdout --source 'fictional example'
added c007 (holdout) to answer-key.md
[exit 0]

$ python3 ../../scripts/sia.py add-case helpdesk --input "I'm locked out of the admin panel. Should I message Sam directly?" --expected 'No. Open a ticket in #it-help; Sam handles admin panel access from there.' --must 'open a ticket in #it-help; not a direct message' --set holdout --source 'fictional example'
added c008 (holdout) to answer-key.md
[exit 0]

$ python3 ../../scripts/sia.py validate helpdesk
[self-improve/helpdesk]
OK     all 8 files and runs/ present
OK     config.json: level 2 (system proposes, human approves)
OK     answer key: 8 cases (6 train, 2 holdout)
OK     versions/LOG.md: 2 entries
helpdesk: 0 errors, 0 warnings
[exit 0]

$ python3 ../../scripts/sia.py status helpdesk
agent:              helpdesk
level:              2 (system proposes, human approves), max_iterations 10
live version:       v002
answer key:         8 cases (6 train, 2 holdout), minimum 5
last live run:      none
last candidate run: none
candidate:          none
last log entry:     2026-11-24 | v002 | - | - | first written version of the helpdesk generator | edited | human
[exit 0]
```

## Cycle 1

### 1. Verifier scores the live agent

The generator answers each `input` from `agent.md`; the verifier grades each answer against `must` and gives a reason for every row (`grades/run1-live.json`). `record` stores the run with hashes and writes the coach brief.

```
$ python3 ../../scripts/sia.py record helpdesk --target live --input grades/run1-live.json
recorded runs/001-live.json: 6/8 (train 4/6, holdout 2/2)
  miss c003 [train]: Honestly says it is not covered, but the key has an answer: missing the 10% threshold, Dana's approval above 10%, the #discounts channel and the 25% cap.
  miss c005 [train]: Does not say custom-printed orders are not refundable, and has no misprint exception or 14-day limit.
[exit 0]
```

The coach brief contains train rows only. Neither holdout case (c007, c008) appears in it.

```
$ cat self-improve/helpdesk/runs/001-live-coach.md
# Coach brief: run 001 (agent.md)

Written by sia.py record. Train rows only; holdout rows are withheld from the coach.

Train score: 4 of 6 matched.

## Misses

### c003
- Input: Who approves discounts?
- Expected: Any sales rep can apply up to 10%. Anything above 10% needs approval from Dana (Head of Sales) in #discounts. Nothing above 25%.
- Must include: up to 10% without approval; above 10% needs Dana; ask in #discounts; 25% maximum
- Agent's answer: My instructions do not cover who approves discounts. Your sales lead is the most likely person to know. I cannot apply discounts myself.
- Verifier's reason: Honestly says it is not covered, but the key has an answer: missing the 10% threshold, Dana's approval above 10%, the #discounts channel and the 25% cap.

### c005
- Input: A customer wants to return a custom-printed wedding notebook. Can we refund it?
- Expected: No. Custom-printed orders are not refundable. If it was misprinted, we reprint or refund it if they report it within 14 days of delivery.
- Must include: custom-printed orders not refundable; misprint exception; 14 days from delivery
- Agent's answer: Standard items can be refunded within 30 days of delivery, but my instructions do not say whether custom-printed items count as standard. Check with whoever handles refunds before promising anything.
- Verifier's reason: Does not say custom-printed orders are not refundable, and has no misprint exception or 14-day limit.

## Passes

- c001: Gives the live link, the Notion page Sales > Links, and says not to use the staging link.
- c002: States 30 days, counted from delivery.
- c004: Forwards to wholesale@fernhill.example and says not to quote prices.
- c006: States 2pm, weekdays only, and next business day for later orders.
[exit 0]
```

### 2. Coach writes one candidate

The coach picks one cause (the missing discount policy, behind c003) and writes `candidate.md` and `candidate-change.txt`. The live file is not touched. The diff is one added line.

```
$ diff self-improve/helpdesk/agent.md self-improve/helpdesk/candidate.md
26a27
> - Discounts: any sales rep can apply a discount of up to 10%. Anything above 10% needs approval from Dana (Head of Sales), requested in #discounts. No discount may exceed 25%.
[exit 1]
```

Trying to promote before the candidate has been scored is refused.

```
$ python3 ../../scripts/sia.py promote helpdesk --by human
refused: need a live run and a candidate run in runs/ (use sia.py record)
[exit 1]
```

### 3. Verifier scores the candidate on the full answer key

```
$ python3 ../../scripts/sia.py record helpdesk --target candidate --input grades/run2-candidate.json
recorded runs/002-candidate.json: 7/8 (train 5/6, holdout 2/2)
  miss c005 [train]: Still does not say custom-printed orders are not refundable; no misprint exception or 14-day limit.
[exit 0]
```

### 4. Compare, then one decision

```
$ python3 ../../scripts/sia.py compare helpdesk
live      run 001  6/8 (train 4/6, holdout 2/2)
candidate run 002  7/8 (train 5/6, holdout 2/2)
change:   Add the discount policy (up to 10% without approval, Dana approves above 10% via #discounts, 25% cap) to What the agent knows; addresses c003.
  fixed      c003 [train]: Has all four items: 10% without approval, Dana above 10%, #discounts, 25% cap.
fixes: 1, regressions: 0
qualifies (higher total and no regressions): yes
[exit 0]
```

At level 2 the system may not promote on its own, even when the candidate qualifies.

```
$ python3 ../../scripts/sia.py promote helpdesk --by auto
refused: promote --by auto needs level 3 in config.json; this agent is level 2
[exit 1]
```

The human promotes.

```
$ python3 ../../scripts/sia.py promote helpdesk --by human
promoted candidate.md to agent.md as v003 (decided by human)
logged: live 6/8 (train 4/6, holdout 2/2) -> candidate 7/8 (train 5/6, holdout 2/2)
[exit 0]

$ tail -4 self-improve/helpdesk/versions/LOG.md
|---|---|---|---|---|---|---|
| 2026-11-24 | v001 | - | - | initial scaffold from template | created | human |
| 2026-11-24 | v002 | - | - | first written version of the helpdesk generator | edited | human |
| 2026-11-24 | v003 | 6/8 (train 4/6, holdout 2/2) | 7/8 (train 5/6, holdout 2/2) | Add the discount policy (up to 10% without approval, Dana approves above 10% via #discounts, 25% cap) to What the agent knows; addresses c003. | promoted | human |
[exit 0]
```

## Cycle 2: regression, tamper check and rejection

The live agent (now v003) is scored again, and the coach targets the remaining miss, c005.

```
$ python3 ../../scripts/sia.py record helpdesk --target live --input grades/run3-live.json
recorded runs/003-live.json: 7/8 (train 5/6, holdout 2/2)
  miss c005 [train]: Still does not say custom-printed orders are not refundable; no misprint exception or 14-day limit.
[exit 0]
```

The coach's candidate rewrites the refunds line. The rewrite covers custom-printed orders but drops the 30-day window for standard items (deliberately, as noted above).

```
$ diff self-improve/helpdesk/agent.md self-improve/helpdesk/candidate.md
25c25
< - Refunds: standard items can be refunded within 30 days from delivery.
---
> - Refunds: custom-printed orders are not refundable. The one exception is a misprint reported within 14 days of delivery, which we reprint or refund.
[exit 1]

$ python3 ../../scripts/sia.py record helpdesk --target candidate --input grades/run4-candidate.json
recorded runs/004-candidate.json: 7/8 (train 5/6, holdout 2/2)
  miss c002 [train]: Does not give the 30-day window from delivery for standard items; only the custom-order rule is stated.
[exit 0]

$ python3 ../../scripts/sia.py compare helpdesk
live      run 003  7/8 (train 5/6, holdout 2/2)
candidate run 004  7/8 (train 5/6, holdout 2/2)
change:   Rewrite the refunds line to cover custom-printed orders (not refundable; misprints within 14 days of delivery reprinted or refunded); addresses c005.
  fixed      c005 [train]: States custom-printed orders are not refundable, the misprint exception, and the 14-day limit from delivery.
  regression c002 [train]: Does not give the 30-day window from delivery for standard items; only the custom-order rule is stated.
fixes: 1, regressions: 1
qualifies (higher total and no regressions): no; total is not higher, 1 regression(s)
[exit 0]
```

The candidate fixes c005 but regresses c002, so the total is unchanged and it does not qualify.

Next, a simulated tampering: someone edits the `must` cell of c002 in the answer key so that the candidate's answer would pass. `compare` and `promote` refuse, and `validate` reports the tamper warning.

```
$ cp self-improve/helpdesk/answer-key.md /tmp/answer-key.backup.md
[exit 0]

$ sed -i '' 's/| 30 days; from delivery |/| custom-printed orders not refundable |/' self-improve/helpdesk/answer-key.md && grep -n 'c002' self-improve/helpdesk/answer-key.md
32:| c002 | What's our refund window? | 30 days from delivery for standard items. | custom-printed orders not refundable | train | 2026-11-24 | fictional example |
[exit 0]

$ python3 ../../scripts/sia.py compare helpdesk
refused: tamper check: answer-key.md changed since runs 003 and 004 were recorded; re-run the verifier
[exit 1]

$ python3 ../../scripts/sia.py promote helpdesk --by human
refused: tamper check: answer-key.md changed since runs 003 and 004 were recorded; re-run the verifier
[exit 1]

$ python3 ../../scripts/sia.py validate helpdesk
[self-improve/helpdesk]
OK     all 8 files and runs/ present
OK     config.json: level 2 (system proposes, human approves)
OK     answer key: 8 cases (6 train, 2 holdout)
OK     versions/LOG.md: 3 entries
OK     runs/: 4 run files
WARN   tamper check: answer-key.md changed since run 003 (live) was recorded
WARN   tamper check: answer-key.md changed since run 004 (candidate) was recorded
OK     candidate.md pending: Rewrite the refunds line to cover custom-printed orders (not refundable; misprints within 14 days of delivery reprinted or refunded); addresses c005.
helpdesk: 0 errors, 2 warnings
[exit 0]
```

The answer key is restored, the comparison is valid again, and the human rejects the candidate with a one-line reason.

```
$ cp /tmp/answer-key.backup.md self-improve/helpdesk/answer-key.md && python3 ../../scripts/sia.py compare helpdesk | tail -1
qualifies (higher total and no regressions): no; total is not higher, 1 regression(s)
[exit 0]

$ python3 ../../scripts/sia.py reject helpdesk --reason 'fixes c005 but regresses c002: the rewrite dropped the 30-day standard refund window'
rejected candidate; moved to versions/rejected-001.md and logged the reason
[exit 0]

$ python3 ../../scripts/sia.py validate helpdesk
[self-improve/helpdesk]
OK     all 8 files and runs/ present
OK     config.json: level 2 (system proposes, human approves)
OK     answer key: 8 cases (6 train, 2 holdout)
OK     versions/LOG.md: 4 entries
OK     runs/: 4 run files
helpdesk: 0 errors, 0 warnings
[exit 0]

$ python3 ../../scripts/sia.py status helpdesk
agent:              helpdesk
level:              2 (system proposes, human approves), max_iterations 10
live version:       v003
answer key:         8 cases (6 train, 2 holdout), minimum 5
last live run:      run 003, 7/8 (train 5/6, holdout 2/2)
last candidate run: run 004, 7/8 (train 5/6, holdout 2/2)
candidate:          none
last log entry:     2026-11-24 | rejected-001 | 7/8 (train 5/6, holdout 2/2) | 7/8 (train 5/6, holdout 2/2) | Rewrite the refunds line to cover custom-printed orders (not refundable; misprints within 14 days of delivery reprinted or refunded); addresses c005. | rejected: fixes c005 but regresses c002: the rewrite dropped the 30-day standard refund window | human
[exit 0]

$ cat self-improve/helpdesk/versions/LOG.md
# Version log: helpdesk

Append-only. One row per decision. Rows are written by `sia.py` (init, promote, reject, snapshot); do not edit or delete existing rows. Scores read "all (train, holdout)". (This log is an addition, not from the video, which describes the versions folder loosely.)

| date | version | live score | candidate score | change | decision | decided-by |
|---|---|---|---|---|---|---|
| 2026-11-24 | v001 | - | - | initial scaffold from template | created | human |
| 2026-11-24 | v002 | - | - | first written version of the helpdesk generator | edited | human |
| 2026-11-24 | v003 | 6/8 (train 4/6, holdout 2/2) | 7/8 (train 5/6, holdout 2/2) | Add the discount policy (up to 10% without approval, Dana approves above 10% via #discounts, 25% cap) to What the agent knows; addresses c003. | promoted | human |
| 2026-11-24 | rejected-001 | 7/8 (train 5/6, holdout 2/2) | 7/8 (train 5/6, holdout 2/2) | Rewrite the refunds line to cover custom-printed orders (not refundable; misprints within 14 days of delivery reprinted or refunded); addresses c005. | rejected: fixes c005 but regresses c002: the rewrite dropped the 30-day standard refund window | human |
[exit 0]

$ ls self-improve/helpdesk self-improve/helpdesk/versions self-improve/helpdesk/runs
self-improve/helpdesk:
PERMISSIONS.md
agent.md
answer-key.md
coach.md
config.json
runs
verifier.md
versions

self-improve/helpdesk/runs:
001-live-coach.md
001-live.json
002-candidate-coach.md
002-candidate.json
003-live-coach.md
003-live.json
004-candidate-coach.md
004-candidate.json

self-improve/helpdesk/versions:
LOG.md
rejected-001.md
v001.md
v002.md
v003.md
[exit 0]
```

c005 is still a miss in the live agent. The next cycle would try a candidate that adds the custom-order rule without removing the standard window.
