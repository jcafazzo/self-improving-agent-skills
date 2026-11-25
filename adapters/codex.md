# Codex CLI

## Install the skills

Codex reads project instructions from `AGENTS.md` (in the repository, and a personal one under `~/.codex/`). Recent Codex releases may also load skills from a skills folder; the location has changed between releases, so check the current Codex documentation for where skills go and whether your version supports them.

If your version supports skills, copy each folder in `skills/` to the documented skills location.

If it does not, or you prefer not to rely on it, keep the skills in the project and point to them from `AGENTS.md`:

```
mkdir -p /path/to/project/docs/self-improve-skills
cp -R skills/* /path/to/project/docs/self-improve-skills/
```

and add to `/path/to/project/AGENTS.md`:

```markdown
## Self-improving agents

Procedures for improving agents under self-improve/ are in docs/self-improve-skills/<name>/SKILL.md.
When asked to scaffold, verify, coach, run an improvement cycle, promote or reject, or make a
quick fix to one of these agents, read the matching SKILL.md first and follow it.
The file manager is tools/sia/sia.py (run with python3).
```

Copy `scripts/sia.py` and `templates/` together, for example to `/path/to/project/tools/sia/`.

## Separate contexts and permissions for the three roles

Codex can run a separate, non-interactive session with `codex exec "<prompt>"`, and has sandbox modes that control whether a session may write to the workspace (for example a read-only mode). Check `codex exec --help` and the current documentation for the exact flags in your version.

A workable arrangement:

- **Generator:** a separate `codex exec` session per case, told to read only `agent.md` (or `candidate.md`) and answer the given input, in a read-only sandbox.
- **Verifier:** a separate `codex exec` session in a read-only sandbox, given `verifier.md`, `answer-key.md` and the collected answers, returning grades as JSON on its output.
- **Coach:** a separate `codex exec` session that may write to the workspace, told to follow `coach.md` and write only `candidate.md` and `candidate-change.txt`.
- **Runner:** your interactive session, which runs `sia.py record`, `compare`, and, on your decision, `promote` or `reject`.

As far as this repository's authors know, the sandbox modes apply to the whole workspace, not to individual files, so the coach's restriction to two files is enforced by instruction. `sia.py` detects a changed answer key or verifier by hash and refuses to compare or promote, but it does not prevent the write. Keep `self-improve/` under version control and review the diff after each coach run.

## Run the cycle

In your interactive session: "Follow docs/self-improve-skills/run-improvement-cycle/SKILL.md for the helpdesk agent. Use separate codex exec sessions for the generator, verifier and coach as described in AGENTS.md." It ends with a single promote-or-reject question.
