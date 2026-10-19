"""Run deterministic offline fixtures and check source syntax without credentials."""
from pathlib import Path
import ast
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    from lab.core import retrieve
    for path in (ROOT/'app').rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path))
    rows=json.loads((ROOT/'resources/evaluation/questions.json').read_text())
    for row in rows:
        evidence,coverage=retrieve(row['question'],row['sources'],row['user'])
        assert [e.id for e in evidence]==row['expected_ids'],row['id']
        assert all(v==row['expected_coverage'] for v in coverage.values()),row['id']
    suite=unittest.TestLoader().discover(str(ROOT/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'fixture_evaluations':len(rows),'source_syntax':'passed',
                      'mode':'offline_contracts'}))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__': raise SystemExit(main())
