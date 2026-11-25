"""Tests for scripts/sia.py. Run from the repository root: python3 -m unittest discover tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIA = Path(__file__).resolve().parent.parent / "scripts" / "sia.py"


class SiaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.d = self.root / "self-improve" / "bot"

    def tearDown(self):
        self.tmp.cleanup()

    def sia(self, *args, stdin=None):
        env = dict(os.environ, SIA_DATE="2026-11-24")
        return subprocess.run([sys.executable, str(SIA)] + list(args) + ["--dir", str(self.root)],
                              input=stdin, capture_output=True, text=True, env=env)

    def ok(self, *args, stdin=None):
        r = self.sia(*args, stdin=stdin)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def refused(self, *args, stdin=None):
        r = self.sia(*args, stdin=stdin)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("refused:", r.stderr)
        return r.stderr

    def scaffold(self, level=2, cases=(("train", "Q1"), ("train", "Q2"), ("holdout", "Q3"))):
        self.ok("init", "bot", "--level", str(level))
        for s, q in cases:
            self.ok("add-case", "--input", q, "--expected", "A " + q, "--must", "fact " + q, "--set", s,
                    "--source", "test")

    def record(self, target, verdicts):
        lines = "\n".join("c%03d,%s,reason %d" % (i + 1, v, i) for i, v in enumerate(verdicts))
        return self.ok("record", "--target", target, stdin=lines)

    def candidate(self, text="# changed\n"):
        (self.d / "candidate.md").write_text((self.d / "agent.md").read_text() + text)
        (self.d / "candidate-change.txt").write_text("add one rule\n")

    def log_rows(self):
        return [l for l in (self.d / "versions" / "LOG.md").read_text().splitlines() if l.startswith("| 2026")]

    # init and validate

    def test_init_creates_layout_and_refuses_overwrite(self):
        self.ok("init", "bot")
        for f in ["agent.md", "answer-key.md", "verifier.md", "coach.md", "config.json", "PERMISSIONS.md",
                  "versions/LOG.md", "versions/v001.md"]:
            self.assertTrue((self.d / f).exists(), f)
        self.assertTrue((self.d / "runs").is_dir())
        self.assertEqual(json.loads((self.d / "config.json").read_text())["level"], 2)
        self.assertIn("will not overwrite", self.refused("init", "bot"))

    def test_validate_fresh_scaffold_passes_with_warnings(self):
        self.ok("init", "bot")
        out = self.ok("validate")
        self.assertIn("WARN   answer key not yet filled in: 0 cases", out)
        self.assertIn("0 errors", out)

    def test_validate_fails_on_bad_rows(self):
        self.scaffold()
        key = self.d / "answer-key.md"
        key.write_text(key.read_text() + "| c001 | dup | x | y | maybe | 2026-11-24 | s |\n")
        r = self.sia("validate")
        self.assertEqual(r.returncode, 1)
        self.assertIn("duplicate id c001", r.stdout)
        self.assertIn("set 'maybe' is not train or holdout", r.stdout)

    def test_validate_flags_identical_candidate_and_bad_config(self):
        self.scaffold()
        (self.d / "candidate.md").write_text((self.d / "agent.md").read_text())
        cfg = self.d / "config.json"
        cfg.write_text(json.dumps(dict(json.loads(cfg.read_text()), level=7)))
        out = self.sia("validate").stdout
        self.assertIn("candidate.md is identical to agent.md", out)
        self.assertIn("level must be 1, 2 or 3", out)

    # add-case and record

    def test_add_case_auto_ids_and_escapes_pipes(self):
        self.scaffold(cases=())
        self.ok("add-case", "--input", "a | b?", "--expected", "line1\nline2", "--must", "x; y")
        self.ok("add-case", "--input", "second", "--expected", "e", "--must", "m", "--set", "holdout")
        text = (self.d / "answer-key.md").read_text()
        self.assertIn("| c001 | a \\| b? | line1<br>line2 | x; y | train | 2026-11-24 |  |", text)
        self.assertIn("| c002 | second |", text)
        self.assertIn("2 cases (1 train, 1 holdout)", self.ok("status"))

    def test_record_computes_totals_hashes_and_coach_brief(self):
        self.scaffold()
        self.record("live", ["pass", "fail", "fail"])
        run = json.loads((self.d / "runs" / "001-live.json").read_text())
        self.assertEqual(run["totals"]["all"], {"passed": 1, "total": 3})
        self.assertEqual(run["totals"]["holdout"], {"passed": 0, "total": 1})
        self.assertEqual(len(run["answer_key_sha256"]), 64)
        brief = (self.d / "runs" / "001-live-coach.md").read_text()
        self.assertIn("### c002", brief)
        self.assertNotIn("c003", brief)  # holdout rows never reach the coach

    def test_record_refuses_incomplete_or_unknown_cases(self):
        self.scaffold()
        self.assertIn("missing: c003", self.refused("record", "--target", "live", stdin="c001,pass,r\nc002,pass,r"))
        self.assertIn("unknown: c999", self.refused(
            "record", "--target", "live", stdin="c001,pass,r\nc002,pass,r\nc003,pass,r\nc999,pass,r"))
        data = json.dumps([{"id": "c001", "pass": True, "reason": ""}])
        self.assertIn("no reason", self.refused("record", "--target", "live", stdin=data))

    # compare

    def test_compare_detects_regressions_and_fixes(self):
        self.scaffold()
        self.record("live", ["pass", "fail", "pass"])
        self.candidate()
        self.record("candidate", ["fail", "pass", "pass"])
        out = self.ok("compare")
        self.assertIn("fixed      c002", out)
        self.assertIn("regression c001", out)
        self.assertIn("qualifies (higher total and no regressions): no", out)

    def test_compare_qualifies_when_higher_and_no_regressions(self):
        self.scaffold()
        self.record("live", ["pass", "fail", "fail"])
        self.candidate()
        self.record("candidate", ["pass", "pass", "fail"])
        self.assertIn("qualifies (higher total and no regressions): yes", self.ok("compare"))

    def test_compare_refuses_after_answer_key_edit(self):
        self.scaffold()
        self.record("live", ["pass", "fail", "pass"])
        self.candidate()
        self.record("candidate", ["pass", "pass", "pass"])
        key = self.d / "answer-key.md"
        key.write_text(key.read_text().replace("A Q2", "A different answer"))
        self.assertIn("tamper check: answer-key.md changed", self.refused("compare"))
        self.assertIn("tamper check", self.refused("promote", "--by", "human"))
        self.assertIn("tamper check", self.ok("validate"))

    # promote and reject

    def test_promote_guards(self):
        self.scaffold()
        self.assertIn("no candidate.md", self.refused("promote", "--by", "human"))
        self.record("live", ["pass", "fail", "pass"])
        self.candidate()
        self.assertIn("need a live run and a candidate run", self.refused("promote", "--by", "human"))
        self.record("candidate", ["pass", "pass", "pass"])
        self.assertIn("needs level 3", self.refused("promote", "--by", "auto"))
        (self.d / "candidate.md").write_text("edited after scoring\n")
        self.assertIn("score the candidate again", self.refused("promote", "--by", "human"))

    def test_promote_by_human_archives_and_logs(self):
        self.scaffold()
        self.record("live", ["pass", "fail", "pass"])
        self.candidate()
        cand_text = (self.d / "candidate.md").read_text()
        self.record("candidate", ["pass", "pass", "pass"])
        self.ok("promote", "--by", "human")
        self.assertEqual((self.d / "agent.md").read_text(), cand_text)
        self.assertEqual((self.d / "versions" / "v002.md").read_text(), cand_text)
        self.assertFalse((self.d / "candidate.md").exists())
        self.assertIn("| v002 | 2/3 (train 1/2, holdout 1/1) | 3/3 (train 2/2, holdout 1/1) | add one rule "
                      "| promoted | human |", self.log_rows()[-1])
        self.assertIn("0 errors", self.ok("validate"))

    def test_promote_by_auto_at_level_3_requires_qualifying(self):
        self.scaffold(level=3)
        self.record("live", ["pass", "fail", "pass"])
        self.candidate()
        self.record("candidate", ["fail", "pass", "pass"])  # same total, one regression
        self.assertIn("does not qualify", self.refused("promote", "--by", "auto"))
        self.record("candidate", ["pass", "pass", "pass"])
        self.ok("promote", "--by", "auto")
        self.assertIn("| promoted | auto |", self.log_rows()[-1])

    def test_reject_moves_candidate_and_logs_reason(self):
        self.scaffold()
        self.record("live", ["pass", "fail", "pass"])
        self.candidate()
        self.record("candidate", ["fail", "pass", "pass"])
        self.ok("reject", "--reason", "regressed c001")
        self.assertTrue((self.d / "versions" / "rejected-001.md").exists())
        self.assertFalse((self.d / "candidate.md").exists())
        self.assertIn("| rejected-001 |", self.log_rows()[-1])
        self.assertIn("rejected: regressed c001 | human |", self.log_rows()[-1])
        self.assertIn("no candidate.md", self.refused("reject", "--reason", "again"))
        self.assertIn("0 errors", self.ok("validate"))

    def test_snapshot_records_hand_edit(self):
        self.scaffold()
        (self.d / "agent.md").write_text("# hand edited\n")
        self.assertIn("record the edit with sia.py snapshot", self.ok("validate"))
        self.ok("snapshot", "--change", "level 1 fix")
        self.assertTrue((self.d / "versions" / "v002.md").exists())
        self.assertIn("| v002 | - | - | level 1 fix | edited | human |", self.log_rows()[-1])
        self.assertIn("nothing to record", self.ok("snapshot", "--change", "x"))


if __name__ == "__main__":
    unittest.main()
