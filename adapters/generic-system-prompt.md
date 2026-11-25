# Any chat model (no skills support, no file tools)

This route works with any chat interface that lets you start a new conversation and set or paste instructions. It gives the weakest separation, because nothing stops a role from being shown files it should not see except your own care, so be deliberate about what you paste into each conversation.

## Setup

Run `sia.py` on your own machine:

```
python3 scripts/sia.py init helpdesk
```

If you cannot run Python, create the files by hand from `templates/`, as described in `skills/scaffold-self-improving-agent/SKILL.md`.

## One conversation per role

Start a new conversation for each role. Paste the role's instructions as the system prompt (or as the first message if the interface has no system prompt), followed by only the files listed.

| Role | Instructions to paste | Files to paste | Never paste |
|---|---|---|---|
| Generator | the contents of `agent.md` (or `candidate.md`) | one case `input` at a time | `answer-key.md`, run files |
| Verifier | `verifier.md` | `answer-key.md` and the generator's answers | `agent.md`, `coach.md` |
| Coach | `coach.md` | newest `runs/NNN-live-coach.md`, `agent.md`, `versions/LOG.md` | `answer-key.md`, `runs/*.json` |

For the generator, a fresh conversation per case is best. If that is impractical, one conversation can answer the inputs one after another; note that in the report.

## The cycle

1. Collect the live agent's answers in generator conversations.
2. Paste them into a verifier conversation. Save the JSON grades it returns as `grades.json` and run `python3 scripts/sia.py record helpdesk --target live --input grades.json`.
3. Paste the new coach brief into a coach conversation. Save its `candidate.md` and its one-line change as `candidate-change.txt` in `self-improve/helpdesk/`.
4. Repeat steps 1 and 2 for the candidate with `--target candidate`.
5. Run `python3 scripts/sia.py compare helpdesk`, read the result, and decide: `python3 scripts/sia.py promote helpdesk --by human` or `python3 scripts/sia.py reject helpdesk --reason "..."`.

You are the runner and the promotion step. The full procedure, with the reasons behind each rule, is in `skills/run-improvement-cycle/SKILL.md`; it can be pasted into a conversation as a guide.

## What is and is not enforced

Only `sia.py` enforces anything here: it refuses to record incomplete grades, and refuses to compare or promote if the answer key or verifier changed between runs, or if a file changed after it was scored. Everything else (what each role sees and writes) depends on what you paste and save.
