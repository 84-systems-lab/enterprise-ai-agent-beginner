"""Agent boundaries with scripted model responses, no network or cloud credentials."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "app/shared"), str(ROOT)]
from askanydoc_rag.tool_agent import AgentError, run_agent, validate_options
from tools.agent_app_demo import fixture_agent


def fact(source="pdf", text="Report within seven days."):
    return {"chunk_text": text, "source_type": source, "source_name": "Policy",
            "source_uri": "s3://fictional-book/uploads/policy.pdf", "object_key": "uploads/policy.pdf",
            "location": {"page_number": 1}, "similarity": 0.8}


def result(items=None, **values):
    return {"evidence": [fact()] if items is None else items, "truncated": False, **values}


def call(name="read_aws", args=None, identifier="one"):
    return {"toolUse": {"toolUseId": identifier, "name": name,
                        "input": {"query": "chair"} if args is None else args}}


def response(blocks, stop="tool_use"):
    return {"stopReason": stop, "output": {"message": {"role": "assistant", "content": blocks}},
            "usage": {"inputTokens": 3, "outputTokens": 2}}


def final(refs=None, text="Supported policy."):
    return response([{"text": json.dumps({"answer": text, "citations": [1] if refs is None else refs})}], "end_turn")


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.fetch = Mock(return_value=result())
        self.adapter = SimpleNamespace(description="Read company policy.", fetch=self.fetch,
                                       max_items=30, source_types=("pdf",))
        self.model = Mock()

    def run_loop(self, responses, **values):
        self.model.converse.side_effect = responses
        return run_agent(self.model, "fixture", "chair", {"aws": self.adapter}, ["aws"], **values)

    def test_success_builds_citations_from_provenance_and_counts_usage(self):
        self.fetch.return_value = result(input_tokens=5, output_tokens=1)
        output = self.run_loop([response([call()]), final()])
        self.assertEqual(output["citations"][0]["source_uri"], fact()["source_uri"])
        self.assertEqual(output["input_tokens"], 11)
        self.assertEqual(output["output_tokens"], 5)
        self.assertEqual(output["source_outcomes"], {"aws": "found"})
        self.assertEqual(output["agent_trace"][0]["outcome"], "found")
        self.assertNotIn("chair", json.dumps(output["agent_trace"]))

    def test_unknown_or_write_tool_never_executes(self):
        output = self.run_loop([response([call("write_refund")]), final([])])
        self.fetch.assert_not_called()
        self.assertEqual(output["agent_trace"][0]["outcome"], "rejected")
        self.assertEqual(output["source_outcomes"]["aws"], "not_checked")

    def test_unselected_connector_cannot_be_called(self):
        output = self.run_loop([response([call("read_sharepoint")]), final([])])
        self.fetch.assert_not_called()
        self.assertEqual(output["agent_trace"][0]["tool"], "rejected_tool")

    def test_invalid_arguments_do_not_reach_reader(self):
        for args in ({"query": "chair", "url": "https://example.com"}, {"query": " "}, [], {"query": 1}):
            with self.subTest(args=args):
                self.run_loop([response([call(args=args)]), final([])])
                self.fetch.assert_not_called()

    def test_batch_budget_is_checked_before_any_read(self):
        with self.assertRaisesRegex(AgentError, "agent_tool_budget_exhausted"):
            self.run_loop([response([call(identifier="one"), call(identifier="two")])], max_tool_calls=1)
        self.fetch.assert_not_called()

    def test_duplicate_call_ids_do_not_execute(self):
        with self.assertRaisesRegex(AgentError, "invalid_tool_call_id"):
            self.run_loop([response([call(), call()])])
        self.fetch.assert_not_called()

    def test_turn_budget_stops_loop(self):
        with self.assertRaisesRegex(AgentError, "agent_turn_budget_exhausted"):
            self.run_loop([response([call()])], max_turns=1)
        self.assertEqual(self.fetch.call_count, 1)

    def test_unknown_citation_is_rejected(self):
        for refs in ([2], [True], [0], [1, 1], ["1"]):
            with self.subTest(refs=refs), self.assertRaises(AgentError):
                self.run_loop([response([call()]), final(refs)])

    def test_no_tool_answer_cannot_be_company_advice(self):
        output = self.run_loop([final([], "The refund was approved.")])
        self.assertNotIn("refund was approved", output["answer"])
        self.assertFalse(output["grounded"])

    def test_error_details_are_not_in_tool_result_or_trace(self):
        self.fetch.side_effect = TimeoutError("SECRET_PRIVATE_VALUE")
        output = self.run_loop([response([call()]), final([])])
        self.assertEqual(output["source_outcomes"]["aws"], "unavailable")
        self.assertNotIn("SECRET_PRIVATE_VALUE", json.dumps(output))
        self.assertNotIn("SECRET_PRIVATE_VALUE", repr(self.model.converse.call_args))

    def test_no_match_is_distinct_from_unavailable(self):
        self.fetch.return_value = result([])
        output = self.run_loop([response([call()]), final([])])
        self.assertEqual(output["source_outcomes"]["aws"], "no_match")

    def test_wrong_source_evidence_never_enters_model_context(self):
        self.fetch.return_value = result([fact("salesforce_case", "PRIVATE_WRONG_SOURCE")])
        output = self.run_loop([response([call()]), final([])])
        self.assertEqual(output["source_outcomes"]["aws"], "unavailable")
        self.assertNotIn("PRIVATE_WRONG_SOURCE", repr(self.model.converse.call_args))

    def test_truncation_is_visible(self):
        self.fetch.return_value = result([fact(text="x" * 4500)])
        output = self.run_loop([response([call()]), final()])
        self.assertEqual(output["source_outcomes"]["aws"], "truncated")
        messages = self.model.converse.call_args.kwargs["messages"]
        self.assertEqual(len(messages[-1]["content"][0]["toolResult"]["content"][0]["json"]["evidence"][0]["text"]), 4000)

    def test_unavailable_source_is_recorded_without_tool_exposure(self):
        output = run_agent(self.model, "fixture", "chair", {}, ["sharepoint"])
        self.model.converse.assert_not_called()
        self.assertEqual(output["source_outcomes"], {"sharepoint": "unavailable"})

    def test_malformed_and_incomplete_final_are_rejected(self):
        for value in (response([{"text": "not JSON"}], "end_turn"),
                      response([{"text": "{}"}], "max_tokens"),
                      response([{"text": "[]"}], "end_turn")):
            with self.subTest(value=value), self.assertRaises(AgentError):
                self.run_loop([value])

    def test_invalid_request_options(self):
        for mode, sources in (([], []), ("write", ["aws"]), ("agent", []), ("agent", ["aws", "aws"]),
                              ("agent", ["url"]), ("agent", [None]), ("assistant", ["aws"])):
            with self.subTest(mode=mode, sources=sources), self.assertRaises(ValueError):
                validate_options(mode, sources)

    def test_scripted_application_loop_combines_sources(self):
        output = fixture_agent("damaged chair policy triage case status", ["aws", "sharepoint", "salesforce"])
        self.assertEqual(output["source_outcomes"], dict.fromkeys(("aws", "sharepoint", "salesforce"), "found"))
        self.assertEqual(len(output["agent_trace"]), 3)

    def test_fixture_authorisation_happens_before_agent(self):
        for user in ("alex", "sam"):
            output = fixture_agent("approval exception", ["sharepoint"], user)
            self.assertEqual(bool(output["citations"]), user == "sam")
            if user == "alex":
                self.assertNotIn("750", json.dumps(output))

    def test_missing_source_preserves_other_evidence(self):
        output = fixture_agent("chair", ["aws", "sharepoint"], unavailable=["sharepoint"])
        self.assertEqual(output["source_outcomes"], {"aws": "found", "sharepoint": "unavailable"})
        self.assertTrue(output["citations"])


if __name__ == "__main__":
    unittest.main()
