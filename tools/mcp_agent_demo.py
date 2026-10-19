"""Connect to a real local MCP server and optionally use it in the application agent."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import asyncio
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "app/shared"), str(ROOT)]
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from askanydoc_rag.tool_agent import run_agent
from tools.agent_app_demo import ScriptedAgentModel

TOOL = "search_company_policy"


async def read_policy(session, query):
    response = await session.call_tool(TOOL, {"query": query})
    if response.isError or not isinstance(response.structuredContent, dict):
        raise ValueError("The local MCP policy read was unavailable.")
    return response.structuredContent


async def demo(question, use_agent):
    # Only this supplied child process is launched. Questions never become shell commands.
    parameters = StdioServerParameters(command=sys.executable, args=[str(ROOT / "tools/local_mcp_server.py")])
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            catalogue = await session.list_tools()
            tools = {tool.name: tool for tool in catalogue.tools}
            tool = tools.get(TOOL)
            schema = tool.inputSchema if tool else {}
            if (set(tools) != {TOOL} or schema.get("type") != "object"
                    or schema.get("required") != ["query"]
                    or set(schema.get("properties", {})) != {"query"}
                    or schema["properties"]["query"].get("type") != "string"):
                raise ValueError("The local MCP catalogue differs from the approved contract.")
            if not use_agent:
                result = await read_policy(session, question)
                return {"mode": "real_local_mcp_read", "tool": TOOL, **result}
            loop = asyncio.get_running_loop()
            def fetch(query, fallback):
                future = asyncio.run_coroutine_threadsafe(read_policy(session, query), loop)
                try:
                    return future.result(timeout=15)
                except BaseException:
                    future.cancel()
                    raise
            adapter = SimpleNamespace(description="Read fictional company policy through the local MCP server.",
                                      source_types=("pdf",), max_items=30, fetch=fetch)
            # Keep the async MCP session on its event loop while the sync agent calls a read.
            result = await asyncio.to_thread(run_agent, ScriptedAgentModel(["aws"], question),
                "scripted-fixture", question, {"aws": adapter}, ["aws"])
            if result["source_outcomes"] != {"aws": "found"} or not result["citations"]:
                raise ValueError("The local MCP agent checkpoint did not retrieve cited policy evidence.")
            return {"mode": "scripted_model_real_local_mcp", "mcp_tool": TOOL, **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", default="damaged chair policy")
    parser.add_argument("--agent", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(demo(args.question, args.agent)), indent=2))


if __name__ == "__main__":
    main()
