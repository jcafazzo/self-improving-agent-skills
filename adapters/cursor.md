# Cursor

## Install the skills

Cursor reads project rules from `.cursor/rules/`. Rule files there use the `.mdc` extension with a small frontmatter block (fields such as `description`, `globs` and `alwaysApply`); check the current Cursor documentation for the exact format your version expects. Cursor does not use `SKILL.md` frontmatter, so either convert each skill to a rule or keep the skills as plain files and point to them from one rule.

The simple route is the second one:

```
mkdir -p /path/to/project/docs/self-improve-skills /path/to/project/.cursor/rules
cp -R skills/* /path/to/project/docs/self-improve-skills/
```

and create `/path/to/project/.cursor/rules/self-improve.mdc`:

```
---
description: Procedures for self-improving agents under self-improve/
alwaysApply: false
---
When asked to scaffold, verify, coach, run an improvement cycle, promote or reject, or make a
quick fix to an agent under self-improve/, read the matching
docs/self-improve-skills/<name>/SKILL.md first and follow it. The file manager is
tools/sia/sia.py (run with python3 in the terminal).
```

Copy `scripts/sia.py` and `templates/` together, for example to `/path/to/project/tools/sia/`.

## Separate contexts and permissions for the three roles

The repository's authors do not know of a Cursor setting that restricts an agent's writes to particular files. Use separate chats as separate contexts:

- **Generator:** a new chat, given only the contents of `agent.md` (or `candidate.md`) and one input at a time. Do not attach `answer-key.md`.
- **Verifier:** a new chat, given `verifier.md`, `answer-key.md` and the collected answers, asked to return JSON grades and not to edit files. Use a mode that does not edit files, if your version has one (check the documentation for the current chat and agent modes).
- **Coach:** a new chat, given the newest `runs/NNN-live-coach.md`, `agent.md` and `versions/`, asked to write only `candidate.md` and `candidate-change.txt`.
- **Runner:** you, running `sia.py` in the terminal.

Because writes are restricted only by instruction, review the diff after the coach's chat, and rely on `sia.py`'s hash check to refuse a comparison if `answer-key.md` or `verifier.md` changed.

## Run the cycle

Open a chat, attach `docs/self-improve-skills/run-improvement-cycle/SKILL.md`, and ask it to walk you through the cycle for your agent, telling you when to open each separate chat. It ends with a single promote-or-reject question, which you answer and then carry out with `sia.py promote` or `sia.py reject`.
