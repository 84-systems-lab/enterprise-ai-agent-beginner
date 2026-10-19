"""Run the application agent loop with fictional sources and a scripted model."""
from pathlib import Path
from dataclasses import dataclass
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "app/shared"), str(ROOT)]
from askanydoc_rag.tool_agent import run_agent
from lab.core import retrieve


@dataclass(frozen=True)
class FixtureAdapter:
    source_id: str
    user: str = "alex"
    failure: bool = False
    description: str = "Read fictional company evidence for the selected source."
    source_types: tuple = ("pdf", "sharepoint", "salesforce_case")
    max_items: int = 30

    def fetch(self, query, fallback):
        if self.failure:
            raise TimeoutError("Controlled fixture failure")
        records, _ = retrieve(query, [self.source_id], self.user)
        types = {"aws": "pdf", "sharepoint": "sharepoint", "salesforce": "salesforce_case"}
        return {"evidence": [{"chunk_text": e.text, "source_name": e.title,
            "source_type": types[e.source], "source_uri": e.uri, "object_key": "",
            "location": {"fixture_location": e.location}, "similarity": None} for e in records],
            "truncated": False}


class ScriptedAgentModel:
    """No inference: requests one selected tool per turn, then quotes its evidence."""
    def __init__(self, sources, query, repeat=False):
        self.sources = [*sources, *([sources[0]] if repeat else [])]
        self.query, self.turn, self.offered = query, 0, []

    def converse(self, **request):
        if self.turn:
            for block in request["messages"][-1]["content"]:
                result = block.get("toolResult", {})
                self.offered.extend(result.get("content", [{}])[0].get("json", {}).get("evidence", []))
        if self.turn < len(self.sources):
            source = self.sources[self.turn]
            blocks = [{"toolUse": {"toolUseId": "fixture-" + str(self.turn + 1),
                       "name": "read_" + source, "input": {"query": self.query}}}]
            stop = "tool_use"
        else:
            blocks = [{"text": json.dumps({"answer": "\n\n".join(e["text"] for e in self.offered)
                or "No accessible fixture evidence.", "citations": [e["evidence_number"] for e in self.offered]})}]
            stop = "end_turn"
        self.turn += 1
        return {"stopReason": stop, "output": {"message": {"role": "assistant", "content": blocks}}}


def fixture_agent(question, sources, user="alex", unavailable=(), repeat=False, tool_budget=4):
    adapters = {s: FixtureAdapter(s, user, s in unavailable) for s in sources}
    return run_agent(ScriptedAgentModel(sources, question, repeat), "scripted-fixture", question,
                     adapters, list(sources), max_tool_calls=tool_budget)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", default="damaged chair policy triage case status")
    parser.add_argument("--sources", nargs="+", choices=["aws", "sharepoint", "salesforce"], default=["aws"])
    parser.add_argument("--user", choices=["alex", "sam"], default="alex")
    parser.add_argument("--unavailable", nargs="*", choices=["aws", "sharepoint", "salesforce"], default=[])
    parser.add_argument("--repeat", action="store_true")
    parser.add_argument("--tool-budget", type=int, default=4)
    args = parser.parse_args()
    try:
        result = fixture_agent(args.question, args.sources, args.user, args.unavailable,
                               args.repeat, args.tool_budget)
    except ValueError as error:
        print("Agent stopped: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps({"mode": "scripted_model_offline", **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
