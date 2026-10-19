"""A local read-only MCP server for fictional policy evidence; transport is stdio."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "app/shared"), str(ROOT)]
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from tools.agent_app_demo import FixtureAdapter

server = FastMCP("Fictional company policy")


class PolicyResult(BaseModel):
    evidence: list[dict]
    truncated: bool


@server.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False})
def search_company_policy(query: str) -> PolicyResult:
    """Read supplied fictional AWS-library policy fixtures. No arbitrary files or writes."""
    if not 0 < len(query.strip()) <= 2000:
        raise ValueError("Query must contain 1 to 2000 characters.")
    return PolicyResult(**FixtureAdapter("aws").fetch(query, ""))


if __name__ == "__main__":
    server.run(transport="stdio")
