# Claude Code

## Install the skills

Claude Code reads skills from `~/.claude/skills/<name>/SKILL.md` (all projects) or `.claude/skills/<name>/SKILL.md` (one project). From a clone of this repository:

```
mkdir -p ~/.claude/skills
cp -R skills/* ~/.claude/skills/
```

or, for one project:

```
mkdir -p /path/to/project/.claude/skills
cp -R skills/* /path/to/project/.claude/skills/
```

Copy `scripts/sia.py` and `templates/` somewhere stable, keeping `templates/` beside `sia.py` or in its parent folder, for example `/path/to/project/tools/sia/sia.py` and `/path/to/project/tools/sia/templates/`. The skills write `path/to/sia.py`; tell Claude where you put it, or note it in the project's `CLAUDE.md`.

## Separate contexts and permissions for the three roles

Claude Code sub-agents are Markdown files in `.claude/agents/` (project) or `~/.claude/agents/` (user), with YAML frontmatter that includes a `tools:` list. A sub-agent runs in its own context and can use only the tools listed. This is how to give the verifier and coach their own permissions.

Example `.claude/agents/helpdesk-verifier.md`:

```markdown
---
name: helpdesk-verifier
description: Grades helpdesk answers against self-improve/helpdesk/answer-key.md. Read-only.
tools: Read, Grep, Glob
---
Follow self-improve/helpdesk/verifier.md. You will be given the agent's answer to each case.
Return your grades as a JSON list of {"id", "pass", "reason", "answer"}. Do not write files.
```

Example `.claude/agents/helpdesk-coach.md`:

```markdown
---
name: helpdesk-coach
description: Writes one-change candidates for self-improve/helpdesk/agent.md.
tools: Read, Write, Edit, Glob
---
Follow self-improve/helpdesk/coach.md. Read only the newest runs/NNN-live-coach.md, agent.md and versions/.
Write only candidate.md and candidate-change.txt.
```

Example `.claude/agents/helpdesk-generator.md`, used to collect answers:

```markdown
---
name: helpdesk-generator
description: Answers one question using self-improve/helpdesk/agent.md (or candidate.md when told).
tools: Read
---
Read the instructions file you are told to use and answer the question you are given. Do not read any other file in self-improve/.
```

Limits to know about:

- A `tools:` list restricts which tools a sub-agent has, not which paths it may write. The coach above can still write any file with `Write`. The instruction says otherwise, and `sia.py` will detect a changed answer key or verifier by hash, but it does not prevent the write. For path-level rules, Claude Code's settings support permission rules for tools such as `Edit` and `Read` with path patterns; check the current Claude Code permissions documentation for the exact syntax before relying on it. Rules that cover `Edit` do not cover shell commands, so leave `Bash` out of the coach's and verifier's tool lists.
- The verifier above has no shell access, so it cannot run `sia.py record`. That is intended: the main session (the runner) records the grades the verifier returns.
- Check the current documentation on whether sub-agents can start other sub-agents. The skills assume they cannot, which is why the main session collects the generator's answers and passes them to the verifier.

## Run the cycle

In the main session, ask Claude to use the `run-improvement-cycle` skill for the agent, for example: "Run the improvement cycle for the helpdesk agent." The skill tells the main session to use the generator sub-agent for answers, the verifier sub-agent for grades, and the coach sub-agent for the candidate, and to run `sia.py` itself. It ends with a single promote-or-reject question.

For a level 1 fix, ask Claude to use `quick-fix-from-conversation` in the conversation where the mistake happened.
