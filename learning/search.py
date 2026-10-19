from pathlib import Path


def find_lines(query, policy_path):
    if not query.strip():
        raise ValueError("Enter a search word or phrase.")
    text = Path(policy_path).read_text(encoding="utf-8")
    matches = []
    for number, line in enumerate(text.splitlines(), start=1):
        if query.casefold() in line.casefold():
            matches.append({"line": number, "text": line})
    return matches


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    args = parser.parse_args()
    found = find_lines(args.query, "resources/company/returns-policy.md")
    if not found:
        print("No matching line. Try a word used in the policy.")
    for match in found:
        print("Line", match["line"], ":", match["text"])
