---
name: scaffold-self-improving-agent
description: Use when setting up a new self-improving agent in a project, or when checking that an existing self-improve/<agent>/ folder is complete and well-formed before running an improvement cycle.
---

# Scaffold a self-improving agent

## Purpose

Create the files a self-improving agent needs (generator, answer key, verifier, coach, versions, runs) and check them. The design has three separate roles reading and writing separate files; getting the layout right first is what makes the later separation possible.

## Inputs

- A short agent name: lowercase letters, digits and hyphens (for example `helpdesk`).
- The project folder that should hold `self-improve/`.
- Optionally the autonomy level (1, 2 or 3). Default is 2. If the user has not chosen, use the `choose-autonomy-level` skill afterwards.
- `sia.py` and its `templates/` folder from this repository. `sia.py` looks for `templates/` beside itself or in its parent folder.

## Steps

1. Run, from the project folder:

   ```
   python3 path/to/scripts/sia.py init <agent-name> [--level N]
   ```

   It refuses to overwrite existing files. If it refuses, do not delete anything; ask the user whether the existing folder should be used instead.

2. Run:

   ```
   python3 path/to/scripts/sia.py validate <agent-name>
   ```

   On a fresh scaffold expect two warnings and no errors: the answer key has no rows yet, and `agent.md` still has `[[...]]` placeholders. Exit status 0 means no errors.

3. Tell the user what each file is for (table below) and what comes next: `build-generator` for `agent.md`, then `build-answer-key`.

4. After any later hand edit, run `validate` again. Treat every ERROR as something to fix before running a cycle. Read every WARN aloud to the user; some (such as a tamper warning) mean recent runs can no longer be compared.

## What the files are for

| File | Purpose | Written by |
|---|---|---|
| `agent.md` | The live generator: a job description with a reason behind every rule | Promotion step only, once the cycle runs |
| `answer-key.md` | Table of inputs and the answers the human would give | The human |
| `verifier.md` | Instructions for the read-only grader | The human |
| `coach.md` | Instructions for the one-change coach | The human |
| `config.json` | Level, iteration cap, minimum cases | The human |
| `PERMISSIONS.md` | Who may read and write what, and how to enforce it | The human |
| `versions/` | Every live version, rejected candidates, `LOG.md` | `sia.py` |
| `runs/` | One JSON score file per verifier run, plus a train-only coach brief | `sia.py record` |
| `candidate.md`, `candidate-change.txt` | The coach's proposal and its one-line summary (appear later) | The coach |

## If the harness cannot run scripts

Create the same files by hand with your file write tools:

1. Copy each file in `templates/` into `self-improve/<agent-name>/`, putting `LOG.md` under `versions/`. Replace `{{agent}}` with the agent name and `{{date}}` with today's date (YYYY-MM-DD).
2. Copy `agent.md` to `versions/v001.md`.
3. Create `config.json`:

   ```json
   {"agent": "<agent-name>", "level": 2, "max_iterations": 10, "min_cases": 5,
    "promotion_rule": "higher total and no regressions"}
   ```

4. Create an empty `runs/` folder.
5. Check by eye what `validate` would check: every file present; the answer-key table has the header `id | input | expected | must | set | added | source`; `config.json` parses. Tell the user that without the script there is no automatic tamper check, so the answer key and verifier should be kept under version control and diffed before each promotion.

## Output

A `self-improve/<agent-name>/` folder and the `validate` output, reported to the user verbatim.

## Rules

- Never overwrite an existing agent folder. Reason: it may hold the only copy of an answer key the user built by hand.
- Do not fill in `agent.md` or the answer key during scaffolding. Reason: both need the user's input; drafting them unasked produces content the user has not reviewed.

## Source

Deep dive Part 1, sections 1.3 to 1.5 and 1.8 (the generator, `answer-key.md`, verifier, coach, candidate file and versions folder; video 2:00 to 11:10). Additions not from the video: `config.json`, `runs/` with hashes, `versions/LOG.md`, the `must` and `set` columns, and the validator itself (deep dive Part 2, gaps 1 to 6).
