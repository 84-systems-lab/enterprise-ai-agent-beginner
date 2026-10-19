from learning.evidence import read_policy

TOOLS = {"read_policy": read_policy}


def execute_tool(name, arguments):
    if name not in TOOLS:
        raise ValueError("Tool is not allowed.")
    if not isinstance(arguments, dict) or set(arguments) != {"query"}:
        raise ValueError("Supply only a query argument.")
    query = arguments["query"]
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 200:
        raise ValueError("Query must contain 1 to 200 characters.")
    return TOOLS[name](query)


if __name__ == "__main__":
    import json
    proposal = {"name": "read_policy", "arguments": {"query": "damaged"}}
    print(json.dumps(execute_tool(proposal["name"], proposal["arguments"]), indent=2))
