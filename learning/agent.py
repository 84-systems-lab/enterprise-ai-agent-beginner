from learning.evidence import compose_from_evidence
from learning.tool import execute_tool


def scripted_choice(question, observation):
    """Teaching stand-in for a model; it follows a written rule."""
    if observation is None:
        return {"kind": "tool", "name": "read_policy",
                "arguments": {"query": question}}
    return {"kind": "finish"}


def run_agent(question, choose=scripted_choice, max_reads=1):
    observation = None
    reads = 0
    activity = []
    for turn in range(3):
        proposal = choose(question, observation)
        if proposal["kind"] == "finish":
            result = compose_from_evidence(observation or [])
            result["activity"] = activity
            result["mode"] = "scripted_teaching_loop"
            return result
        if proposal["kind"] != "tool":
            raise ValueError("Unknown proposal kind.")
        if reads >= max_reads:
            raise ValueError("Read limit reached.")
        observation = execute_tool(proposal["name"], proposal["arguments"])
        reads += 1
        activity.append({"turn": turn + 1, "tool": proposal["name"],
                         "items": len(observation)})
    raise ValueError("Turn limit reached.")


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", default="damaged")
    args = parser.parse_args()
    print(json.dumps(run_agent(args.query), indent=2))
