# Gemini CLI

## Install the skills

Gemini CLI reads context from `GEMINI.md` files (in the project, and a personal one under `~/.gemini/`). It also supports custom commands defined in files under `.gemini/commands/`; check the current Gemini CLI documentation for their format. Some recent versions may also support skills or extensions directly; check the documentation for your version.

A route that does not depend on those features:

```
mkdir -p /path/to/project/docs/self-improve-skills
cp -R skills/* /path/to/project/docs/self-improve-skills/
```

and add to `/path/to/project/GEMINI.md`:

```markdown
## Self-improving agents

Procedures for improving agents under self-improve/ are in docs/self-improve-skills/<name>/SKILL.md.
When asked to scaffold, verify, coach, run an improvement cycle, promote or reject, or make a
quick fix to one of these agents, read the matching SKILL.md first and follow it.
The file manager is tools/sia/sia.py (run with python3).
```

Copy `scripts/sia.py` and `templates/` together, for example to `/path/to/project/tools/sia/`.

## Separate contexts and permissions for the three roles

Gemini CLI can run a one-off, non-interactive prompt (`gemini -p "<prompt>"` in the versions the authors have seen), which gives each role a fresh context. It also has sandboxing and approval settings that control what tools may do. Check `gemini --help` and the current documentation for the exact flags in your version.

- **Generator:** one non-interactive run per case, told to read only `agent.md` (or `candidate.md`) and answer the given input.
- **Verifier:** one non-interactive run given `verifier.md`, `answer-key.md` and the collected answers, told to print JSON grades and not to write files. Where your version can deny file-writing tools for a run, deny them.
- **Coach:** one run told to follow `coach.md` and write only `candidate.md` and `candidate-change.txt`.
- **Runner:** your interactive session, which runs `sia.py`.

The authors do not know of a per-file write restriction in Gemini CLI, so the coach's two-file limit is enforced by instruction, and `sia.py`'s hash check detects (but does not prevent) a changed answer key or verifier. Keep `self-improve/` under version control and review each coach diff.

## Run the cycle

In an interactive session: "Follow docs/self-improve-skills/run-improvement-cycle/SKILL.md for the helpdesk agent, using a separate non-interactive run for the generator, verifier and coach." It ends with a single promote-or-reject question.
