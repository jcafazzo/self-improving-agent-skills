# self-improving-agent-skills

A small set of skills, written as plain Markdown, for building an AI agent that improves through a feedback loop: one agent does the job, a second grades it against an answer key, and a third proposes one change at a time for a human (or, in strictly verifiable cases, the loop) to accept or reject. A single-file Python script, `sia.py`, creates and checks the files and enforces the rules that can be enforced by a script. Nothing here calls a model; the skills are run by whatever agent harness you already use.

## Credit

The method follows the video "How To Build Self-Improving AI Agents with Claude (Stanford's Method)" by Austin Marchese: https://www.youtube.com/watch?v=UUg5oij7ptw

This is an independent implementation. It is not affiliated with or endorsed by the video's creator or by Stanford University. The video attributes some terms and arguments to a Stanford course but does not name the course; a web search suggests it may be CS329A, "Self-Improving AI Agents", but that is not confirmed by the video and the course was not reviewed for this repository. See `docs/deep-dive.md`, which separates what the video says (Part 1, with timestamps) from this repository's own commentary and additions (Part 2).

## The method in brief

Four pieces:

| Piece | What it is | File |
|---|---|---|
| Generator | The agent that does the job, written as a job description with a reason behind every rule | `agent.md` |
| Verifier | A read-only grader that asks every case in the answer key and says right or wrong, with a reason | `verifier.md`, `answer-key.md` |
| Coach | Reads the verifier's misses and writes a candidate: the live agent with exactly one change | `coach.md`, `candidate.md` |
| Level | How much the system may decide on its own | `config.json` |

Three levels:

| Level | Who proposes | Who approves | Use when |
|---|---|---|---|
| 1 | You | You | From day one: you notice a mistake and ask for the rule to be written |
| 2 | The system | You | The recommended default |
| 3 | The system | The system | Only with fully verifiable pass/fail cases, capped at 10 iterations by default |

## Repository layout

```
skills/                     nine skills, one job each (SKILL.md with name and description)
  scaffold-self-improving-agent/  build-generator/  build-answer-key/
  verify-agent/  coach-candidate/  run-improvement-cycle/
  promote-or-reject/  quick-fix-from-conversation/  choose-autonomy-level/
scripts/sia.py              file manager and validator (Python 3.8+, standard library only)
templates/                  the files sia.py init copies into a project
adapters/                   notes for Claude Code, Codex, Cursor, Gemini CLI and plain chat
examples/fresh-scaffold.txt init and validate in an empty temporary folder, real output
examples/toy-cycle/         a full level 2 cycle on a toy agent, with TRANSCRIPT.md
tests/test_sia.py           unit tests for sia.py
docs/deep-dive.md           what the video says, and what this repository adds
```

## What a scaffolded agent looks like

```
self-improve/<agent>/
  agent.md                the live generator
  answer-key.md           | id | input | expected | must | set | added | source |
  verifier.md             verifier role instructions
  coach.md                coach role instructions
  config.json             {"agent", "level", "max_iterations", "min_cases", ...}
  PERMISSIONS.md          who may read and write what, and how to enforce it
  candidate.md            the coach's proposal (only while one is pending)
  candidate-change.txt    its one-line summary
  versions/LOG.md         append-only decision log
  versions/v001.md ...    every version that has been live
  versions/rejected-NNN.md  rejected candidates
  runs/NNN-live.json      one score file per verifier run, with hashes
  runs/NNN-live-coach.md  the train-only brief the coach reads
```

## Quick start

```
python3 scripts/sia.py init helpdesk --dir /path/to/project
python3 scripts/sia.py validate helpdesk --dir /path/to/project
```

Real output on an empty folder (from `examples/fresh-scaffold.txt`):

```
$ python3 path/to/scripts/sia.py validate
[self-improve/support-bot]
OK     all 8 files and runs/ present
OK     config.json: level 2 (system proposes, human approves)
WARN   answer key not yet filled in: 0 cases, minimum is 5
WARN   agent.md: 9 [[...]] placeholders not yet filled in
OK     versions/LOG.md: 1 entries
support-bot: 0 errors, 2 warnings
[exit 0]
```

Then use the skills in order: `choose-autonomy-level`, `build-generator`, `build-answer-key`, and `run-improvement-cycle`.

Other subcommands: `add-case`, `record`, `compare`, `promote`, `reject`, `snapshot` (records a hand edit of `agent.md` as a new version, for level 1 fixes) and `status`. Run `python3 scripts/sia.py <command> -h` for arguments.

## Install per harness

Copy the folders in `skills/` to wherever your harness loads skills or instructions from, and copy `scripts/sia.py` with `templates/` beside it. Harness-specific notes, including how to give the three roles separate contexts and restricted permissions:

- [Claude Code](adapters/claude-code.md)
- [Codex CLI](adapters/codex.md)
- [Cursor](adapters/cursor.md)
- [Gemini CLI](adapters/gemini-cli.md)
- [Any chat model](adapters/generic-system-prompt.md)

## A cycle, with real output

`examples/toy-cycle/` holds a complete agent folder after one promoted candidate and one rejected candidate, and `TRANSCRIPT.md` with every command and its output. The agent answers internal questions for a fictional shop; its first version was written to miss two of eight cases. One model played all three roles in one session, so the example demonstrates the file mechanics and guards, not independent grading.

The verifier scores the live agent:

```
$ python3 ../../scripts/sia.py record helpdesk --target live --input grades/run1-live.json
recorded runs/001-live.json: 6/8 (train 4/6, holdout 2/2)
  miss c003 [train]: Honestly says it is not covered, but the key has an answer: missing the 10% threshold, Dana's approval above 10%, the #discounts channel and the 25% cap.
  miss c005 [train]: Does not say custom-printed orders are not refundable, and has no misprint exception or 14-day limit.
```

The coach adds one line to a candidate; the verifier scores it on the full key; compare:

```
$ python3 ../../scripts/sia.py compare helpdesk
live      run 001  6/8 (train 4/6, holdout 2/2)
candidate run 002  7/8 (train 5/6, holdout 2/2)
change:   Add the discount policy (up to 10% without approval, Dana approves above 10% via #discounts, 25% cap) to What the agent knows; addresses c003.
  fixed      c003 [train]: Has all four items: 10% without approval, Dana above 10%, #discounts, 25% cap.
fixes: 1, regressions: 0
qualifies (higher total and no regressions): yes
```

At level 2 the loop may not promote on its own; the human does:

```
$ python3 ../../scripts/sia.py promote helpdesk --by auto
refused: promote --by auto needs level 3 in config.json; this agent is level 2
[exit 1]

$ python3 ../../scripts/sia.py promote helpdesk --by human
promoted candidate.md to agent.md as v003 (decided by human)
logged: live 6/8 (train 4/6, holdout 2/2) -> candidate 7/8 (train 5/6, holdout 2/2)
```

In a second cycle, a candidate that fixes one case but breaks another is caught, an edit to the answer key between runs is refused, and the candidate is rejected:

```
$ python3 ../../scripts/sia.py compare helpdesk
...
  fixed      c005 [train]: States custom-printed orders are not refundable, the misprint exception, and the 14-day limit from delivery.
  regression c002 [train]: Does not give the 30-day window from delivery for standard items; only the custom-order rule is stated.
fixes: 1, regressions: 1
qualifies (higher total and no regressions): no; total is not higher, 1 regression(s)

$ python3 ../../scripts/sia.py compare helpdesk
refused: tamper check: answer-key.md changed since runs 003 and 004 were recorded; re-run the verifier
[exit 1]

$ python3 ../../scripts/sia.py reject helpdesk --reason 'fixes c005 but regresses c002: the rewrite dropped the 30-day standard refund window'
rejected candidate; moved to versions/rejected-001.md and logged the reason
```

## From the video, and added here

From the video: the generator, verifier and coach as three separate agents with separate permissions; a job description with a reason behind every rule; saying so instead of guessing; the answer key as a living table that gains a row on every miss; a verifier that never edits anything and explains every miss; a coach that makes one change per candidate in a file next to the live one and never touches the answer key or verifier; a versions folder with rejected candidates and one-line reasons; the three levels, the level 2 "show both scores, the change and one choice" step, the level 3 loop with a 10-iteration cap, and the cautions about level 3.

Added here, and labelled as additions in each skill (see `docs/deep-dive.md`, Part 2):

- `holdout` rows that the coach never sees, scored separately.
- A regression rule: a candidate qualifies only with a higher total and no row that the live agent passed and the candidate fails. Automatic promotion requires it.
- A `must` column, so the verifier grades on required facts rather than wording, and a reason on every row, pass or fail.
- SHA-256 hashes of the answer key and verifier in every run, with `compare` and `promote` refusing if either changed.
- An append-only decision log with both scores, the change, the decision and who made it.
- Level 1 adds the case to the answer key before writing the rule.
- `config.json`, the validator, the train-only coach brief, and the `snapshot` command.

## Limitations

- `sia.py` manages files. It does not run models, so it cannot check that the roles really ran in separate contexts, that the generator never saw the answer key, or that the grades are honest. The skills say how to arrange that; the harness and the person running the cycle have to do it.
- The hash check detects a changed answer key or verifier; it does not prevent the change, and it does not cover `coach.md` or `config.json`. Use version control as well.
- Where a harness cannot restrict writes per file, the coach's two-file limit is an instruction, not a permission. The adapter notes say where this applies.
- A model-based verifier can grade the same answer differently on two runs. With a small answer key, a one-row difference may be noise. With 20 rows, one row is five points.
- The toy example was run by one model playing every role, and its first agent version was written to fail two cases. It demonstrates the mechanics only.
- The harness details in `adapters/` were written from the authors' understanding at the time of writing and were not all tested. Where a detail was uncertain, the note says to check the harness's documentation.

## Tests

```
python3 -m unittest discover tests
```

## Licence

MIT. See `LICENSE`.
