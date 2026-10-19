"""Run controlled checks of the small teaching programs, with no cloud calls."""
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from learning.decision import reporting_message
from learning.search import find_lines
from learning.evidence import read_policy, compose_from_evidence
from learning.tool import execute_tool
from learning.agent import run_agent


class Lessons(unittest.TestCase):
    def test_hello(self):
        result = subprocess.run([sys.executable, "learning/hello.py"], check=True,
                                text=True, capture_output=True)
        self.assertEqual(result.stdout.splitlines(), ["Everyday Office Supplies",
                         "What should I do about a damaged chair?"])

    def test_reporting_boundary(self):
        self.assertIn("Within", reporting_message(7))
        self.assertIn("Outside", reporting_message(8))
        self.assertEqual(reporting_message(-1), "Check the delivery date.")

    def test_facts(self):
        result = subprocess.run([sys.executable, "learning/facts.py"], check=True,
                                text=True, capture_output=True)
        self.assertIn("Report within 7 calendar days.", result.stdout)
        self.assertIn("Bring: photographs", result.stdout)

    def test_search_and_line(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "policy.md"
            path.write_text("Title\nReport DAMAGED items.\nKeep receipt.", encoding="utf-8")
            self.assertEqual(find_lines("damaged", path),
                             [{"line": 2, "text": "Report DAMAGED items."}])

    def test_empty_query(self):
        with self.assertRaisesRegex(ValueError, "search word"):
            find_lines("   ", "resources/company/returns-policy.md")

    def test_no_match(self):
        self.assertEqual(read_policy("lunar mining"), [])
        self.assertEqual(compose_from_evidence([])["citations"], [])

    def test_provenance(self):
        result = compose_from_evidence(read_policy("damaged"))
        source = Path("resources/company/returns-policy.md").read_text(encoding="utf-8").splitlines()
        self.assertTrue(result["citations"])
        for citation in result["citations"]:
            self.assertIn(source[citation["line"] - 1], result["answer"])

    def test_unknown_tool(self):
        with self.assertRaisesRegex(ValueError, "not allowed"):
            execute_tool("approve_refund", {"query": "damaged"})

    def test_arguments(self):
        for args in [{"query": "damaged", "path": "private.txt"}, {"query": 3}, {"query": ""}]:
            with self.assertRaises(ValueError):
                execute_tool("read_policy", args)

    def test_agent(self):
        result = run_agent("damaged")
        self.assertEqual(result["mode"], "scripted_teaching_loop")
        self.assertEqual(len(result["activity"]), 1)
        self.assertTrue(result["citations"])

    def test_budget(self):
        def repeat(question, observation):
            return {"kind": "tool", "name": "read_policy", "arguments": {"query": question}}
        with self.assertRaisesRegex(ValueError, "Read limit reached"):
            run_agent("damaged", choose=repeat)

    def test_finish_without_evidence(self):
        result = run_agent("damaged", choose=lambda q, o: {"kind": "finish"})
        self.assertEqual(result["answer"], "No matching evidence.")
        self.assertFalse(result["citations"])


if __name__ == "__main__":
    unittest.main()
