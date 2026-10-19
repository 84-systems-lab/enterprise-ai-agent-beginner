"""Observe the real tool loop with a scripted model and safe fixture retrieval."""
from pathlib import Path
from dataclasses import asdict
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.basic_agent import run_agent
from lab.core import retrieve

class ScriptedModel:
    """A deterministic teaching client; it performs no model inference."""
    def __init__(self, repeat=False):
        self.turn = 0
        self.repeat = repeat

    def converse(self, **request):
        self.turn += 1
        if self.turn == 1 or (self.repeat and self.turn == 2):
            content = [{'toolUse': {'toolUseId': f'demo-{self.turn}',
                'name': 'search_documents', 'input': {'question': 'damaged chair policy'}}}]
        else:
            result = request['messages'][-1]['content'][0]['toolResult']
            if result['status'] == 'success':
                items = result['content'][0]['json']['evidence']
                answer = ' '.join(item['text'] for item in items)
                refs = [item['id'] for item in items]
            else:
                answer, refs = 'The document tool is unavailable; the policy was not checked.', []
            content = [{'text': json.dumps({'answer': answer, 'citations': refs})}]
        return {'output': {'message': {'role': 'assistant', 'content': content}}}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--failure', action='store_true')
    parser.add_argument('--repeat', action='store_true')
    parser.add_argument('--tool-budget', type=int, default=2)
    args = parser.parse_args()
    def read(question):
        if args.failure:
            raise TimeoutError('Controlled fixture failure')
        records, _coverage = retrieve(question, ['aws'], 'alex')
        return [asdict(item) for item in records]
    try:
        result = run_agent(ScriptedModel(args.repeat), 'scripted-fixture',
            'What does the damaged-chair policy require?', read,
            max_tool_calls=args.tool_budget)
    except ValueError as error:
        print(f'Agent stopped: {error}', file=sys.stderr)
        return 2
    print(json.dumps({'mode': 'scripted_model_offline', **result}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
