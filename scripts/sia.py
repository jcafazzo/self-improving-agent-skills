#!/usr/bin/env python3
"""sia.py: file manager for a self-improving agent (generator, verifier, coach).

Creates and checks the files, records verifier scores, compares the live agent
with a candidate, and carries out promote or reject decisions. It never calls a
model and never uses the network. Python 3.8+, standard library only.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

COLUMNS = ["id", "input", "expected", "must", "set", "added", "source"]
REQUIRED = COLUMNS[:-1]  # every column except source
SETS = ("train", "holdout")
LOG_COLUMNS = ["date", "version", "live score", "candidate score", "change", "decision", "decided-by"]
DECISIONS = ("created", "edited", "promoted", "rejected")
FILES = ["agent.md", "answer-key.md", "verifier.md", "coach.md", "config.json",
         "PERMISSIONS.md", "versions/LOG.md", "versions/v001.md"]
TEMPLATES = ["agent.md", "answer-key.md", "verifier.md", "coach.md", "PERMISSIONS.md", "LOG.md"]
HERE = Path(__file__).resolve().parent
TEMPLATE_DIRS = [HERE / "templates", HERE.parent / "templates"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RUN_RE = re.compile(r"^(\d{3,})-(live|candidate)\.json$")
HASHED = (("answer_key_sha256", "answer-key.md"), ("verifier_sha256", "verifier.md"))
LEVELS = {1: "human proposes, human approves", 2: "system proposes, human approves",
          3: "system proposes, system approves"}

class Refused(Exception):
    """A guard stopped the command. The message says why."""

def today():
    return os.environ.get("SIA_DATE") or date.today().isoformat()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return Path(path).read_text(encoding="utf-8")

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

# Markdown tables ------------------------------------------------------------

def split_row(line):
    cells = re.split(r"(?<!\\)\|", line.strip())
    cells = cells[1:] if cells[:1] == [""] else cells
    cells = cells[:-1] if cells[-1:] == [""] else cells
    return [c.strip().replace("\\|", "|") for c in cells]

def esc(text):
    return text.replace("\r", "").replace("|", "\\|").replace("\n", "<br>").strip()

def find_table(lines, columns):
    """First table with these columns outside HTML comments.
    Returns (header_index, end_index, separator_ok, [(line_number, cells)])."""
    in_comment, header, sep_ok, rows = False, None, False, []
    for i, line in enumerate(lines):
        s = line.strip()
        if in_comment or s.startswith("<!--"):
            in_comment = "-->" not in s
        elif header is None:
            if s.startswith("|") and [c.lower() for c in split_row(s)] == columns:
                header = i
        elif i == header + 1 and re.match(r"^\|(\s*:?-+:?\s*\|)+$", s):
            sep_ok = True
        elif s.startswith("|"):
            rows.append((i + 1, split_row(s)))
        else:
            return header, i, sep_ok, rows
    return header, len(lines), sep_ok, rows

def append_row(path, columns, cells):
    lines = read(path).splitlines()
    header, end, _, _ = find_table(lines, columns)
    if header is None:
        raise Refused("%s: no table with columns %s" % (path, " | ".join(columns)))
    lines.insert(end, "| " + " | ".join(esc(c) for c in cells) + " |")
    write(path, "\n".join(lines) + "\n")

def load_key(d):
    """Return (cases, findings) for answer-key.md."""
    header, _, sep_ok, raw = find_table(read(d / "answer-key.md").splitlines(), COLUMNS)
    if header is None:
        return [], [("ERROR", "answer-key.md: no table with columns " + " | ".join(COLUMNS))]
    out = [] if sep_ok else [("ERROR", "answer-key.md: header row is not followed by a |---| separator")]
    cases, seen = [], set()
    for lineno, cells in raw:
        where = "answer-key.md line %d: " % lineno
        if len(cells) != len(COLUMNS):
            out.append(("ERROR", where + "%d cells, expected %d" % (len(cells), len(COLUMNS))))
            continue
        row = dict(zip(COLUMNS, cells))
        checks = [("ERROR", "column '%s' is empty" % c, not row[c]) for c in REQUIRED] + [
            ("WARN", "column 'source' is empty", not row["source"]),
            ("ERROR", "duplicate id %s" % row["id"], row["id"] in seen),
            ("ERROR", "set '%s' is not train or holdout" % row["set"], row["set"] and row["set"] not in SETS),
            ("ERROR", "added '%s' is not YYYY-MM-DD" % row["added"], row["added"] and not DATE_RE.match(row["added"]))]
        out += [(lv, where + msg) for lv, msg, failed in checks if failed]
        seen.add(row["id"])
        cases.append(row)
    return cases, out

def key_or_refuse(d):
    cases, found = load_key(d)
    if any(lv == "ERROR" for lv, _ in found):
        raise Refused("answer-key.md has errors; run validate first")
    return cases

# Folder helpers ---------------------------------------------------------------

def agent_dir(a):
    base = Path(a.dir) / "self-improve"
    if a.agent:
        if not (base / a.agent).is_dir():
            raise Refused("no agent folder at %s" % (base / a.agent))
        return base / a.agent
    found = sorted(p for p in base.glob("*") if (p / "config.json").exists())
    if len(found) != 1:
        raise Refused("found %d agent folders under %s; name the agent" % (len(found), base))
    return found[0]

def runs(d, target=None):
    found = [(int(m.group(1)), p) for p in (d / "runs").glob("*.json")
             for m in [RUN_RE.match(p.name)] if m and target in (None, m.group(2))]
    return [p for _, p in sorted(found)]

def latest_run(d, target):
    r = runs(d, target)
    return json.loads(read(r[-1])) if r else None

def versions(d, prefix="v"):
    """Highest NNN among versions/<prefix>NNN.md (live versions by default)."""
    names = [re.match(r"^%s(\d{3,})\.md$" % prefix, p.name) for p in (d / "versions").iterdir()]
    return max([int(m.group(1)) for m in names if m], default=0)

def vfile(d, v):
    return d / "versions" / ("v%03d.md" % v)

def totals(results):
    t = {k: {"passed": 0, "total": 0} for k in ("train", "holdout", "all")}
    for r in results:
        for k in (r["set"], "all"):
            t[k]["total"] += 1
            t[k]["passed"] += 1 if r["pass"] else 0
    return t

def fmt(t):
    return "%d/%d (train %d/%d, holdout %d/%d)" % (
        t["all"]["passed"], t["all"]["total"], t["train"]["passed"], t["train"]["total"],
        t["holdout"]["passed"], t["holdout"]["total"])

def change_line(d):
    p = d / "candidate-change.txt"
    text = read(p).strip() if p.exists() else ""
    return text.splitlines()[0].strip() if text else ""

def retire_candidate(d, dest):
    os.replace(d / "candidate.md", dest)
    if (d / "candidate-change.txt").exists():
        os.remove(d / "candidate-change.txt")

def log(d, *cells):
    append_row(d / "versions" / "LOG.md", LOG_COLUMNS, [today()] + list(cells))

# Commands -------------------------------------------------------------------

def cmd_init(a):
    if not re.match(r"^[a-z0-9][a-z0-9-]*$", a.agent):
        raise Refused("agent name must be lowercase letters, digits and hyphens")
    if a.level not in LEVELS:
        raise Refused("--level must be 1, 2 or 3")
    tdir = next((t for t in TEMPLATE_DIRS if (t / "agent.md").exists()), None)
    if tdir is None:
        raise Refused("templates/ not found next to sia.py or in its parent folder")
    d = Path(a.dir) / "self-improve" / a.agent
    clash = [f for f in FILES + ["runs"] if (d / f).exists()]
    if clash:
        raise Refused("will not overwrite existing files in %s: %s" % (d, ", ".join(clash)))
    (d / "versions").mkdir(parents=True, exist_ok=True)
    (d / "runs").mkdir()
    for name in TEMPLATES:
        text = read(tdir / name).replace("{{agent}}", a.agent).replace("{{date}}", today())
        write(d / ("versions/LOG.md" if name == "LOG.md" else name), text)
    shutil.copyfile(d / "agent.md", vfile(d, 1))
    config = {"agent": a.agent, "level": a.level, "max_iterations": 10, "min_cases": 5,
              "promotion_rule": "higher total and no regressions"}
    write(d / "config.json", json.dumps(config, indent=2) + "\n")
    write(d / "runs" / ".gitkeep", "")
    print("created %s with: %s, runs/" % (d, ", ".join(FILES)))
    print("next: fill in agent.md and answer-key.md, then run: sia.py validate %s" % a.agent)
    return 0

def check_config(d):
    try:
        cfg = json.loads(read(d / "config.json"))
    except ValueError as e:
        return {}, [("ERROR", "config.json does not parse: %s" % e)]
    whole = lambda k: isinstance(cfg.get(k), int) and not isinstance(cfg[k], bool) and cfg[k] >= 1
    bad = (["agent is %r but the folder is %r" % (cfg.get("agent"), d.name)] if cfg.get("agent") != d.name else []) \
        + (["level must be 1, 2 or 3"] if cfg.get("level") not in LEVELS else []) \
        + ["%s must be a whole number of at least 1" % k for k in ("max_iterations", "min_cases") if not whole(k)]
    if bad:
        return {}, [("ERROR", "config.json: " + b) for b in bad]
    return cfg, [("OK", "config.json: level %d (%s)" % (cfg["level"], LEVELS[cfg["level"]]))]

def check_log(d):
    header, _, sep_ok, rows = find_table(read(d / "versions" / "LOG.md").splitlines(), LOG_COLUMNS)
    if header is None or not sep_ok:
        return [("ERROR", "versions/LOG.md: table header or separator not found")]
    out = []
    for lineno, cells in rows:
        where = "versions/LOG.md line %d: " % lineno
        if len(cells) != len(LOG_COLUMNS):
            out.append(("ERROR", where + "%d cells, expected %d" % (len(cells), len(LOG_COLUMNS))))
            continue
        row = dict(zip(LOG_COLUMNS, cells))
        checks = [("bad date %r" % row["date"], not DATE_RE.match(row["date"])),
                  ("decision must start with " + "/".join(DECISIONS), not row["decision"].startswith(DECISIONS)),
                  ("decided-by must be human or auto", row["decided-by"] not in ("human", "auto")),
                  ("versions/%s.md does not exist" % row["version"],
                   not (d / "versions" / (row["version"] + ".md")).exists())]
        out += [("ERROR", where + msg) for msg, failed in checks if failed]
    return out + [("OK", "versions/LOG.md: %d entries" % len(rows))]

def check_runs(d, ids):
    out = []
    for p in runs(d):
        try:
            run = json.loads(read(p))
            bad = [r["id"] for r in run["results"] if r["id"] not in ids]
            if bad:
                out.append(("ERROR", "runs/%s: ids not in answer key: %s" % (p.name, ", ".join(bad))))
            elif run["totals"] != totals(run["results"]) or run["target"] not in ("live", "candidate"):
                out.append(("ERROR", "runs/%s: totals or target do not match the results" % p.name))
        except (ValueError, KeyError, TypeError) as e:
            out.append(("ERROR", "runs/%s: not a valid run file (%s)" % (p.name, e)))
    if runs(d):
        out.append(("OK", "runs/: %d run files" % len(runs(d))))
    for target in ("live", "candidate"):
        try:
            run = latest_run(d, target)
        except ValueError:
            continue
        out += [("WARN", "tamper check: %s changed since run %03d (%s) was recorded" % (f, run["run"], target))
                for key, f in HASHED if run and run.get(key) != sha(d / f)]
    return out

def check_agent(d):
    missing = [f for f in FILES if not (d / f).exists()] + ([] if (d / "runs").is_dir() else ["runs/"])
    if missing:
        return [("ERROR", "missing: " + ", ".join(missing))]
    out = [("OK", "all %d files and runs/ present" % len(FILES))]
    cfg, found = check_config(d)
    cases, key_found = load_key(d)
    out += found + key_found
    n_hold, min_cases = sum(1 for c in cases if c["set"] == "holdout"), cfg.get("min_cases", 5)
    if len(cases) < min_cases:
        out.append(("WARN", "answer key not yet filled in: %d cases, minimum is %d" % (len(cases), min_cases)))
    else:
        out.append(("OK", "answer key: %d cases (%d train, %d holdout)" % (len(cases), len(cases) - n_hold, n_hold)))
    if cases and not n_hold:
        out.append(("WARN", "answer key has no holdout rows; gains cannot be checked for overfitting"))
    holes = re.sub(r"<!--.*?-->", "", read(d / "agent.md"), flags=re.S).count("[[")
    if holes:
        out.append(("WARN", "agent.md: %d [[...]] placeholders not yet filled in" % holes))
    out += check_log(d)
    v = versions(d)
    if sha(d / "agent.md") != sha(vfile(d, v)):
        out.append(("WARN", "agent.md differs from versions/v%03d.md; record the edit with sia.py snapshot" % v))
    out += check_runs(d, {c["id"] for c in cases})
    if (d / "candidate.md").exists():
        if sha(d / "candidate.md") == sha(d / "agent.md"):
            out.append(("ERROR", "candidate.md is identical to agent.md"))
        elif change_line(d):
            out.append(("OK", "candidate.md pending: " + change_line(d)))
        else:
            out.append(("WARN", "candidate.md pending but candidate-change.txt is missing or empty"))
    elif (d / "candidate-change.txt").exists():
        out.append(("WARN", "candidate-change.txt exists but candidate.md does not"))
    return out

def cmd_validate(a):
    base = Path(a.dir) / "self-improve"
    dirs = [base / a.agent] if a.agent else sorted(p for p in base.glob("*") if p.is_dir())
    if not dirs or not all(p.is_dir() for p in dirs):
        print("ERROR  no agent folder found under %s" % base)
        return 1
    errors = 0
    for d in dirs:
        found = check_agent(d)
        print("[%s]" % d)
        print("\n".join("%-6s %s" % f for f in found))
        n_err = sum(1 for lv, _ in found if lv == "ERROR")
        print("%s: %d errors, %d warnings" % (d.name, n_err, sum(1 for lv, _ in found if lv == "WARN")))
        errors += n_err
    return 1 if errors else 0

def cmd_add_case(a):
    d = agent_dir(a)
    if not (a.input.strip() and a.expected.strip() and a.must.strip()):
        raise Refused("--input, --expected and --must must not be empty")
    nums = [int(m.group(1)) for c in key_or_refuse(d) for m in [re.match(r"^c(\d+)$", c["id"])] if m]
    cid = "c%03d" % (max(nums, default=0) + 1)
    append_row(d / "answer-key.md", COLUMNS, [cid, a.input, a.expected, a.must, a.set, today(), a.source])
    print("added %s (%s) to answer-key.md" % (cid, a.set))
    return 0

def parse_results(text):
    """Verifier output: a JSON list (or {"results": [...]}) or `id,pass|fail,reason` lines."""
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    if data is not None:
        items = data["results"] if isinstance(data, dict) else data
        return [{"id": str(r["id"]), "pass": r["pass"] is True, "reason": str(r.get("reason", "")).strip(),
                 "answer": str(r.get("answer", ""))} for r in items]
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip() and not line.lstrip().startswith("#"):
            parts = [p.strip() for p in line.split(",", 2)] + ["", ""]
            if parts[1].lower() not in ("pass", "fail"):
                raise Refused("input line %d: expected `id,pass|fail,reason`" % n)
            out.append({"id": parts[0], "pass": parts[1].lower() == "pass", "reason": parts[2], "answer": ""})
    return out

def coach_brief(run, case):
    """Markdown for the coach: train rows only, so holdout rows never reach it."""
    t = run["totals"]["train"]
    lines = ["# Coach brief: run %03d (%s)" % (run["run"], run["file"]), "",
             "Written by sia.py record. Train rows only; holdout rows are withheld from the coach.", "",
             "Train score: %d of %d matched." % (t["passed"], t["total"]), "", "## Misses", ""]
    for r in (r for r in run["results"] if r["set"] == "train" and not r["pass"]):
        c = case[r["id"]]
        lines += ["### " + r["id"], "- Input: " + c["input"], "- Expected: " + c["expected"],
                  "- Must include: " + c["must"], "- Agent's answer: " + (r["answer"] or "(not recorded)"),
                  "- Verifier's reason: " + r["reason"], ""]
    return lines + ["## Passes", ""] + ["- %s: %s" % (r["id"], r["reason"]) for r in run["results"]
                                       if r["set"] == "train" and r["pass"]]

def cmd_record(a):
    d = agent_dir(a)
    scored = d / ("agent.md" if a.target == "live" else "candidate.md")
    if not scored.exists():
        raise Refused("%s does not exist" % scored.name)
    cases = key_or_refuse(d)
    results = parse_results(sys.stdin.read() if a.input in (None, "-") else read(a.input))
    by_id, key_ids = {}, [c["id"] for c in cases]
    for r in results:
        if r["id"] in by_id:
            raise Refused("case %s appears twice in the input" % r["id"])
        if not r["reason"]:
            raise Refused("case %s has no reason; every row needs one, pass or fail" % r["id"])
        by_id[r["id"]] = r
    unknown, missing = [i for i in by_id if i not in key_ids], [i for i in key_ids if i not in by_id]
    if unknown or missing:
        raise Refused("input must cover every case once; unknown: %s; missing: %s"
                      % (", ".join(unknown) or "none", ", ".join(missing) or "none"))
    case = {c["id"]: c for c in cases}
    ordered = [dict(by_id[i], set=case[i]["set"]) for i in key_ids]
    n = max([int(RUN_RE.match(p.name).group(1)) for p in runs(d)], default=0) + 1
    run = {"schema": 1, "agent": d.name, "run": n, "target": a.target, "file": scored.name,
           "file_sha256": sha(scored), "live_version": "v%03d" % versions(d), "recorded": today(),
           "answer_key_sha256": sha(d / "answer-key.md"), "verifier_sha256": sha(d / "verifier.md"),
           "results": ordered, "totals": totals(ordered)}
    write(d / "runs" / ("%03d-%s.json" % (n, a.target)), json.dumps(run, indent=2) + "\n")
    write(d / "runs" / ("%03d-%s-coach.md" % (n, a.target)), "\n".join(coach_brief(run, case)) + "\n")
    print("recorded runs/%03d-%s.json: %s" % (n, a.target, fmt(run["totals"])))
    for r in (r for r in ordered if not r["pass"]):
        print("  miss %s [%s]: %s" % (r["id"], r["set"], r["reason"]))
    return 0

def comparison(d):
    """Latest live run vs latest candidate run, with every guard applied."""
    L, C = latest_run(d, "live"), latest_run(d, "candidate")
    if not L or not C:
        raise Refused("need a live run and a candidate run in runs/ (use sia.py record)")
    pair = "runs %03d and %03d" % (L["run"], C["run"])
    for key, f in HASHED:
        if L[key] != C[key]:
            raise Refused("%s differs between %s; score both against the same file" % (f, pair))
        if L[key] != sha(d / f):
            raise Refused("tamper check: %s changed since %s were recorded; re-run the verifier" % (f, pair))
    if L["file_sha256"] != sha(d / "agent.md"):
        raise Refused("agent.md changed since run %03d; score the live agent again" % L["run"])
    if not (d / "candidate.md").exists() or C["file_sha256"] != sha(d / "candidate.md"):
        raise Refused("candidate.md is missing or changed since run %03d; score the candidate again" % C["run"])
    lr, cr = {r["id"]: r for r in L["results"]}, {r["id"]: r for r in C["results"]}
    regressions = [i for i in lr if lr[i]["pass"] and not cr[i]["pass"]]
    fixes = [i for i in lr if not lr[i]["pass"] and cr[i]["pass"]]
    higher = C["totals"]["all"]["passed"] > L["totals"]["all"]["passed"]
    return {"L": L, "C": C, "cr": cr, "regressions": regressions, "fixes": fixes,
            "higher": higher, "qualifies": higher and not regressions}

def cmd_compare(a):
    d = agent_dir(a)
    c = comparison(d)
    print("live      run %03d  %s" % (c["L"]["run"], fmt(c["L"]["totals"])))
    print("candidate run %03d  %s" % (c["C"]["run"], fmt(c["C"]["totals"])))
    print("change:   %s" % (change_line(d) or "(no candidate-change.txt)"))
    for label, ids in (("fixed", c["fixes"]), ("regression", c["regressions"])):
        for i in ids:
            print("  %-10s %s [%s]: %s" % (label, i, c["cr"][i]["set"], c["cr"][i]["reason"]))
    why = ([] if c["higher"] else ["total is not higher"]) + (
        ["%d regression(s)" % len(c["regressions"])] if c["regressions"] else [])
    print("fixes: %d, regressions: %d" % (len(c["fixes"]), len(c["regressions"])))
    print("qualifies (higher total and no regressions): " + ("yes" if c["qualifies"] else "no; " + ", ".join(why)))
    return 0

def cmd_promote(a):
    d = agent_dir(a)
    cand, live = d / "candidate.md", d / "agent.md"
    if not cand.exists():
        raise Refused("no candidate.md to promote")
    if sha(cand) == sha(live):
        raise Refused("candidate.md is identical to agent.md")
    change = (a.change or change_line(d)).strip()
    if not change:
        raise Refused("give --change \"one line\" or write candidate-change.txt")
    c = comparison(d)
    level = json.loads(read(d / "config.json")).get("level")
    if a.by == "auto" and level != 3:
        raise Refused("promote --by auto needs level 3 in config.json; this agent is level %s" % level)
    if a.by == "auto" and not c["qualifies"]:
        raise Refused("candidate does not qualify (higher total and no regressions); not promoting")
    if not c["qualifies"]:
        print("note: candidate does not qualify; promoting on the human's decision")
    v = versions(d)
    if sha(live) != sha(vfile(d, v)):  # an unrecorded hand edit: archive it first
        v += 1
        shutil.copyfile(live, vfile(d, v))
        log(d, "v%03d" % v, "-", "-", "unrecorded edit to agent.md, archived before promotion", "edited", "human")
    shutil.copyfile(cand, vfile(d, v + 1))
    retire_candidate(d, live)
    log(d, "v%03d" % (v + 1), fmt(c["L"]["totals"]), fmt(c["C"]["totals"]), change, "promoted", a.by)
    print("promoted candidate.md to agent.md as v%03d (decided by %s)" % (v + 1, a.by))
    print("logged: live %s -> candidate %s" % (fmt(c["L"]["totals"]), fmt(c["C"]["totals"])))
    return 0

def cmd_reject(a):
    d = agent_dir(a)
    if not (d / "candidate.md").exists():
        raise Refused("no candidate.md to reject")
    if not a.reason.strip():
        raise Refused("give --reason \"one line\"")
    scores = []  # log only scores that describe the current files
    for target, f in (("live", "agent.md"), ("candidate", "candidate.md")):
        run = latest_run(d, target) or {}
        scores.append(fmt(run["totals"]) if run.get("file_sha256") == sha(d / f) else "-")
    name, change = "rejected-%03d" % (versions(d, "rejected-") + 1), change_line(d) or "(no change statement)"
    retire_candidate(d, d / "versions" / (name + ".md"))
    log(d, name, scores[0], scores[1], change, "rejected: " + a.reason.strip(), a.by)
    print("rejected candidate; moved to versions/%s.md and logged the reason" % name)
    return 0

def cmd_snapshot(a):
    d = agent_dir(a)
    v = versions(d)
    if sha(d / "agent.md") == sha(vfile(d, v)):
        print("agent.md matches versions/v%03d.md; nothing to record" % v)
        return 0
    if not a.change.strip():
        raise Refused("give --change \"one line\"")
    shutil.copyfile(d / "agent.md", vfile(d, v + 1))
    log(d, "v%03d" % (v + 1), "-", "-", a.change.strip(), "edited", "human")
    print("recorded the edited agent.md as versions/v%03d.md" % (v + 1))
    return 0

def cmd_status(a):
    d = agent_dir(a)
    cfg, cases, v = json.loads(read(d / "config.json")), load_key(d)[0], versions(d)
    n_hold = sum(1 for c in cases if c["set"] == "holdout")
    edited = "" if sha(d / "agent.md") == sha(vfile(d, v)) else " (agent.md edited since; run snapshot)"
    print("agent:              %s" % d.name)
    print("level:              %s (%s), max_iterations %s" % (cfg.get("level"), LEVELS.get(cfg.get("level"), "?"),
                                                        cfg.get("max_iterations")))
    print("live version:       v%03d%s" % (v, edited))
    print("answer key:         %d cases (%d train, %d holdout), minimum %s"
          % (len(cases), len(cases) - n_hold, n_hold, cfg.get("min_cases")))
    for target in ("live", "candidate"):
        run = latest_run(d, target)
        print("%-20s%s" % ("last %s run:" % target, "run %03d, %s" % (run["run"], fmt(run["totals"])) if run else "none"))
    pending = (d / "candidate.md").exists()
    print("candidate:          %s" % (("pending: " + (change_line(d) or "(no change statement)")) if pending else "none"))
    rows = find_table(read(d / "versions" / "LOG.md").splitlines(), LOG_COLUMNS)[3]
    print("last log entry:     %s" % (" | ".join(rows[-1][1]) if rows else "none"))
    return 0

def main(argv=None):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", default=".", help="project folder that holds self-improve/ (default: .)")
    parser = argparse.ArgumentParser(prog="sia.py", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    optional_agent = ("agent", dict(nargs="?", help="agent name (optional when there is only one)"))
    spec = [
        ("init", cmd_init, "create self-improve/<agent>/ from templates",
         [("agent", {}), ("--level", dict(type=int, default=2, choices=(1, 2, 3)))]),
        ("validate", cmd_validate, "check the files for completeness and well-formedness", []),
        ("add-case", cmd_add_case, "append a row to answer-key.md",
         [("--input", dict(required=True)), ("--expected", dict(required=True)),
          ("--must", dict(required=True, help="facts that must be present, separated by ;")),
          ("--set", dict(default="train", choices=SETS)), ("--source", dict(default=""))]),
        ("record", cmd_record, "record a verifier run from JSON or id,pass,reason lines",
         [("--target", dict(required=True, choices=("live", "candidate"))),
          ("--input", dict(help="file with the verifier's results (default: stdin)"))]),
        ("compare", cmd_compare, "compare the latest live and candidate runs", []),
        ("promote", cmd_promote, "make candidate.md the live agent",
         [("--by", dict(required=True, choices=("human", "auto"))),
          ("--change", dict(default="", help="one line (default: candidate-change.txt)"))]),
        ("reject", cmd_reject, "archive candidate.md as rejected, with a reason",
         [("--reason", dict(required=True)), ("--by", dict(default="human", choices=("human", "auto")))]),
        ("snapshot", cmd_snapshot, "record a hand edit of agent.md (level 1) as a new version",
         [("--change", dict(required=True))]),
        ("status", cmd_status, "one-screen summary", []),
    ]
    for name, fn, help_text, args in spec:
        s = sub.add_parser(name, parents=[common], help=help_text, description=help_text)
        for flag, kw in (args if name == "init" else [optional_agent] + args):
            s.add_argument(flag, **kw)
        s.set_defaults(fn=fn)
    a = parser.parse_args(argv)
    try:
        return a.fn(a)
    except Refused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
