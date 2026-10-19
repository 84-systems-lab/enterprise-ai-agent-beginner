from learning.search import find_lines

POLICY = "resources/company/returns-policy.md"


def read_policy(query):
    matches = find_lines(query, POLICY)
    return [{"text": item["text"], "source": POLICY, "line": item["line"]}
            for item in matches]


def compose_from_evidence(items):
    if not items:
        return {"answer": "No matching evidence.", "citations": []}
    answer = "\n".join(item["text"] for item in items)
    citations = [{"source": item["source"], "line": item["line"]}
                 for item in items]
    return {"answer": answer, "citations": citations}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", default="damaged")
    args = parser.parse_args()
    result = compose_from_evidence(read_policy(args.query))
    print(json.dumps(result, indent=2))
