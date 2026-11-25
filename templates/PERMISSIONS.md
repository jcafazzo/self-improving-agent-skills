# Permissions: {{agent}}

The video's design depends on three separate agents with separate permissions, "enforced by the harness and not only by instruction" (10:16 to 10:36). This file says who may read and write what, and how to enforce it.

## Matrix

R = read, W = write, - = no access. "sia.py" means the change is made only by running the script.

| Path | Generator | Verifier | Coach | Promotion step | Human |
|---|---|---|---|---|---|
| `agent.md` | R (when live is scored) | - | R | W (sia.py promote) | R; W at level 1, then sia.py snapshot |
| `candidate.md` | R (when candidate is scored) | - | W | moves it (promote, reject) | R |
| `candidate-change.txt` | - | - | W | removes it | R |
| `answer-key.md` | - | R | - | R (hash) | W |
| `verifier.md` | - | R | - | R (hash) | W |
| `coach.md` | - | - | R | - | W |
| `config.json` | - | - | - | R | W |
| `versions/` (incl. `LOG.md`) | - | - | R | W (append only) | R |
| `runs/NNN-*.json` | - | adds via sia.py record | - | R | R |
| `runs/NNN-*-coach.md` | - | adds via sia.py record | R | - | R |
| `PERMISSIONS.md` | - | - | - | - | W |

Notes:

- The generator sees only the instructions being scored and the case `input`. It never sees `answer-key.md`.
- The verifier grades the answers it is given. It does not need to see the agent's instructions, and should not, so that it grades the output and not the intent.
- The coach reads the coach brief, which holds train rows only. It never reads `answer-key.md` or the run JSON files, because those contain holdout rows. (Holdout rows are an addition, not from the video.)
- The promotion step is `sia.py promote` or `sia.py reject`, run by the human at level 2, or by the loop at level 3 (`promote --by auto` is refused unless `config.json` says level 3 and the candidate qualifies).

## Enforcement

Use the strongest mechanism your harness has, in this order:

1. **Harness permissions.** Give each role its own agent definition with its own tool list or write scope. The verifier gets read-only tools. The coach gets read tools and a write tool limited, if the harness allows, to `candidate.md` and `candidate-change.txt`. See `adapters/` in the skills repository for specifics.
2. **Separate contexts.** If the harness has no per-agent permissions but has sub-agents or separate sessions, run each role in its own one, loaded with only the role file and the files it may read.
3. **Instruction only.** If neither exists, run each role in a fresh conversation with only its role file and permitted files pasted in.

Whatever the harness offers, `sia.py` adds a check that does not depend on it: every run records the SHA-256 of `answer-key.md` and `verifier.md`, and `compare` and `promote` refuse if either changed between the live run, the candidate run and now. (Hash check is an addition, not from the video.) It detects tampering; it does not prevent it, and it does not protect `coach.md` or `config.json`. Review those with ordinary version control.
