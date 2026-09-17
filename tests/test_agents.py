"""Offline tests: backend.ask is replaced with a canned answer, so a full run spends zero tokens
and needs no network. Run: python3 -m unittest -v"""
import json, os, pathlib, shutil, subprocess, sys, tempfile, unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import backend, memory


def load(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(pathlib.Path(path).stem, ROOT / path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


class Reader(unittest.TestCase):
    def test_ledger_is_a_set_and_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(ROOT / "reader/collect.py", tmp); (pathlib.Path(tmp) / "inbox").mkdir()
            (pathlib.Path(tmp) / "inbox/a.txt").write_text("one"); (pathlib.Path(tmp) / "inbox/b.txt").write_text("two")
            (pathlib.Path(tmp) / "ledger.txt").write_text("a\n")
            out = subprocess.run([sys.executable, "collect.py"], cwd=tmp, capture_output=True, text=True).stdout
            self.assertIn("1 already in ledger, 1 would be written", out)
            self.assertFalse((pathlib.Path(tmp) / "reading").exists())


class Writer(unittest.TestCase):
    def test_guard_rejects_the_sentence_that_cost_nine_weeks(self):
        w = load("writer/writer.py")
        ok, why = w.looks_like_report("I have saved the report to reports/2026/09/2026-09-15.md.")
        self.assertFalse(ok); self.assertIn("heading", why)
        ok, why = w.looks_like_report("# Saved\nDone.")
        self.assertFalse(ok); self.assertIn("confirmation", why)

    def test_writes_the_parts_it_has_when_the_model_fails(self):
        w = load("writer/writer.py")
        with mock.patch.object(w, "ask", side_effect=RuntimeError("cli down")):
            report = w.build(__import__("datetime").date(2026, 9, 16), {"terminal log": "x"}, ["reading notes"])
        self.assertIn("No analysis was generated", report)
        self.assertIn("missing: reading notes", report)
        self.assertIn("sources: terminal log", report)


class Decider(unittest.TestCase):
    def test_pick_outside_the_list_is_rejected_and_nothing_written(self):
        d = load("decider/decide.py")
        with mock.patch.object(d, "candidates", return_value=[{"id": "a", "title": "A", "url": "", "summary": ""}]), \
             mock.patch.object(d, "ask", return_value={"id": "zzz", "reason": "made up"}), \
             mock.patch.object(sys, "argv", ["decide.py", "--apply"]):
            with self.assertRaises(SystemExit) as cm:
                d.main()
            self.assertIn("not in the list", str(cm.exception))


class Backend(unittest.TestCase):
    def test_api_mode_fails_loud_instead_of_spending(self):
        with mock.patch.dict(os.environ, {"AGENT_BACKEND": "api"}):
            with self.assertRaises(RuntimeError):
                backend.ask("hello")

    def test_auto_picks_cli_when_binary_exists(self):
        with mock.patch.dict(os.environ, {"AGENT_BACKEND": "auto"}), mock.patch.object(os.path, "exists", return_value=True):
            self.assertEqual(backend.backend(), "cli")


class Memory(unittest.TestCase):
    def test_append_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "m.txt"
            memory.append(p, "one"); memory.append(p, "two")
            self.assertEqual(memory.load(p), ["one", "two"])


if __name__ == "__main__":
    unittest.main()
