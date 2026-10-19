import json
import unittest
from lab.core import answer, retrieve
from lab.basic_agent import run_agent

class FakeModel:
    def __init__(self, unknown=False, wrong_tool=False):
        self.calls, self.unknown, self.wrong_tool = 0, unknown, wrong_tool
    def converse(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            content = [{'toolUse': {'toolUseId': 'call-1',
                'name': 'write_record' if self.wrong_tool else 'search_documents',
                'input': {'question': 'damaged chair policy'}}}]
        else:
            result = kwargs['messages'][-1]['content'][0]['toolResult']
            refs = ['unknown'] if self.unknown else (['policy-returns'] if result['status']=='success' else [])
            content = [{'text': json.dumps({'answer': 'Fixture answer', 'citations': refs})}]
        return {'output': {'message': {'role': 'assistant', 'content': content}}}

class LabTests(unittest.TestCase):
    def test_policy_is_grounded(self):
        result = answer('damaged chair')
        self.assertEqual(result['citations'][0]['id'], 'policy-returns')
        self.assertIn('7 calendar days', result['answer'])
    def test_restricted_context_is_filtered_before_answer(self):
        for user in ['alex', 'sam']:
            result = answer('approval exception', ['sharepoint'], user)
            self.assertEqual(bool(result['citations']), user == 'sam')
            if user == 'alex':
                self.assertNotIn('750', json.dumps(result))
    def test_no_match_does_not_invent(self):
        self.assertEqual(answer('moon mining')['citations'], [])
    def test_failure_is_distinct_from_no_match(self):
        self.assertEqual(answer('chair', ['sharepoint'], unavailable=['sharepoint'])['coverage'],
                         {'sharepoint': 'unavailable'})
    def test_partial_coverage_remains_visible(self):
        r = answer('chair', ['aws', 'sharepoint'], unavailable=['sharepoint'])
        self.assertEqual(r['coverage'], {'aws': 'found', 'sharepoint': 'unavailable'})
    def test_bad_request(self):
        for question in ['', 'x' * 2001]:
            with self.assertRaises(ValueError): answer(question)
    def test_unknown_source(self):
        with self.assertRaises(ValueError): answer('chair', ['write'])
    def test_invalid_fixture_user(self):
        with self.assertRaises(ValueError): answer('chair', user='admin')
    def test_agent_tool_success(self):
        result = run_agent(FakeModel(), 'fixture', 'chair',
            lambda q: [{'id':'policy-returns', 'text':'fictional policy'}])
        self.assertEqual(result['citations'], ['policy-returns'])
        self.assertTrue(result['trace'][0]['ok'])
    def test_agent_tool_failure(self):
        def fail(_): raise TimeoutError()
        result = run_agent(FakeModel(), 'fixture', 'chair', fail)
        self.assertEqual(result['citations'], [])
        self.assertFalse(result['trace'][0]['ok'])
    def test_agent_rejects_unknown_citation(self):
        with self.assertRaises(ValueError):
            run_agent(FakeModel(unknown=True), 'fixture', 'chair', lambda q: [])
    def test_agent_does_not_execute_unknown_tool(self):
        def fail(_): raise AssertionError('Must not call adapter')
        result = run_agent(FakeModel(wrong_tool=True), 'fixture', 'chair', fail)
        self.assertFalse(result['trace'][0]['ok'])

if __name__ == '__main__': unittest.main()
