"""Contract changes must neither drop restrictions nor accept ambiguous inputs."""
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from salesforce.tool_contract import checked_call, soql_argument_name

def listing(properties, required):
    return SimpleNamespace(tools=[SimpleNamespace(name='soqlQuery', inputSchema={
        'properties': properties, 'required': required})])

class ToolContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_published_query_name(self):
        session = SimpleNamespace(call_tool=AsyncMock(return_value='result'))
        call = checked_call(session, listing({'query': {'type': 'string'}}, ['query']))
        self.assertEqual(await call('soqlQuery', {'q': 'SELECT Id FROM Case LIMIT 1'}), 'result')
        session.call_tool.assert_awaited_once_with('soqlQuery', {'query': 'SELECT Id FROM Case LIMIT 1'})

    async def test_q_name(self):
        session = SimpleNamespace(call_tool=AsyncMock())
        call = checked_call(session, listing({'q': {'type': 'string'}}, ['q']))
        await call('soqlQuery', {'q': 'SELECT Id FROM Case LIMIT 1'})
        session.call_tool.assert_awaited_once_with('soqlQuery', {'q': 'SELECT Id FROM Case LIMIT 1'})

    def test_changed_required_parameter_fails_closed(self):
        with self.assertRaises(ValueError):
            soql_argument_name(listing({'query': {'type': 'string'}}, ['query', 'write']))

    def test_ambiguous_schema_fails_closed(self):
        with self.assertRaises(ValueError):
            soql_argument_name(listing({'q': {'type': 'string'}, 'query': {'type': 'string'}}, ['q', 'query']))

    async def test_arbitrary_tool_not_forwarded(self):
        session = SimpleNamespace(call_tool=AsyncMock())
        call = checked_call(session, listing({'q': {'type': 'string'}}, ['q']))
        with self.assertRaises(ValueError):
            await call('deleteRecord', {'q': 'x'})
        session.call_tool.assert_not_awaited()
