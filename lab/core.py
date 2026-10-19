"""Small offline evidence contract that can be inspected without cloud access."""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Evidence:
    id: str
    source: str
    title: str
    text: str
    location: str
    uri: str

def fixture_records():
    return json.loads((ROOT / 'resources/company/evidence.json').read_text(encoding='utf-8'))

def retrieve(question, sources=('aws',), user='alex', unavailable=()):
    """Exact fixture routing only. No embedding or semantic-search claim."""
    if user not in {'alex', 'sam'}:
        raise ValueError('Unknown fixture user')
    if not question.strip() or len(question) > 2000:
        raise ValueError('Question must contain 1 to 2000 characters')
    if not sources or not set(sources) <= {'aws', 'sharepoint', 'salesforce'}:
        raise ValueError('Choose aws, sharepoint or salesforce')
    query = set(re.findall(r'[a-z]+', question.lower())) - {
        'the', 'a', 'an', 'what', 'is', 'are', 'for', 'of', 'to', 'policy', 'procedure'}
    evidence, coverage = [], {}
    for source in dict.fromkeys(sources):
        if source in unavailable:
            coverage[source] = 'unavailable'
            continue
        found = []
        for item in fixture_records():
            if item['source'] != source or user not in item['allowed_users']:
                continue  # authorisation before passage text enters the answer context
            if query.intersection(item['keywords']):
                found.append(Evidence(**{k: item[k] for k in Evidence.__dataclass_fields__}))
        coverage[source] = 'found' if found else 'no_accessible_match'
        evidence.extend(found)
    return evidence, coverage

def answer(question, sources=('aws',), user='alex', unavailable=()):
    evidence, coverage = retrieve(question, sources, user, unavailable)
    return {
        'mode': 'offline_fixture',
        'answer': '\n\n'.join(f'{e.text} [{i}]' for i, e in enumerate(evidence, 1))
                  if evidence else 'No accessible evidence supports an answer.',
        'citations': [dict(number=i, **asdict(e)) for i, e in enumerate(evidence, 1)],
        'coverage': coverage,
    }

def inspect_document(path):
    data = Path(path).read_bytes()
    return {'name': Path(path).name, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
            'text': data.decode('utf-8')}
