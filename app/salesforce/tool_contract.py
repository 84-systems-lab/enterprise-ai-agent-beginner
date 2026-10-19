"""Reconcile the two documented SOQL argument names against a live MCP schema."""
from typing import Any

def soql_argument_name(listing: Any) -> str:
    tool = next((item for item in listing.tools if item.name == 'soqlQuery'), None)
    if tool is None:
        raise ValueError('The read server has no SOQL tool.')
    schema = tool.inputSchema
    properties = schema.get('properties', {})
    required = schema.get('required', [])
    candidates = [name for name in ('q', 'query')
                  if properties.get(name, {}).get('type') == 'string' and name in required]
    if len(candidates) != 1 or set(required) != {candidates[0]}:
        raise ValueError('The Salesforce SOQL tool schema is unsupported.')
    return candidates[0]

def checked_call(session: Any, listing: Any):
    argument = soql_argument_name(listing)
    async def call(name: str, arguments: dict):
        if name != 'soqlQuery' or set(arguments) != {'q'} or not isinstance(arguments['q'], str):
            raise ValueError('Only the compiled SOQL read is allowed.')
        return await session.call_tool(name, {argument: arguments['q']})
    return call
