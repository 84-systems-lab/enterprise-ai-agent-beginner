"""Explicit, user-run cloud checks. Never run automatically during offline checks."""
from pathlib import Path
import argparse
import json
import os
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'app/api'),str(ROOT/'app/shared'),str(ROOT/'app'),str(ROOT)]
parser=argparse.ArgumentParser()
parser.add_argument('command',choices=['identity','embed','retrieve','answer','agent','schema','database'])
parser.add_argument('--question',default='What information is needed for a damaged chair?')
args=parser.parse_args()
import boto3
if args.command=='identity':
    identity=boto3.client('sts').get_caller_identity()
    print(json.dumps({'Account':identity['Account'],'Arn':identity['Arn']},indent=2))
elif args.command=='embed':
    from askanydoc_rag.embeddings import embed_text
    vector=embed_text(args.question)
    print(json.dumps({'dimensions':len(vector),'first_three':vector[:3]}))
elif args.command=='retrieve':
    from retrieval import retrieve_evidence
    print(json.dumps(retrieve_evidence(args.question),indent=2))
elif args.command=='answer':
    from assistant_orchestrator import run_assistant
    print(json.dumps(run_assistant(args.question, []), indent=2))
elif args.command in {'schema','database'}:
    client=boto3.client('rds-data')
    options={'resourceArn':os.environ['VECTOR_DATABASE_ARN'],
             'secretArn':os.environ['VECTOR_DATABASE_SECRET_ARN'],
             'database':os.environ['VECTOR_DATABASE_NAME']}
    from askanydoc_rag.data_api import call_with_database_resume_retry
    if args.command=='schema':
        # The supplied schema files use independent semicolon-delimited DDL.
        for path in sorted((ROOT/'infra/sql').glob('*.sql')):
            for statement in path.read_text().split(';'):
                if statement.strip():
                    call_with_database_resume_retry(client.execute_statement, sql=statement,**options)
            print(f'Executed {path.name}')
    else:
        statements = ["SELECT extversion FROM pg_extension WHERE extname='vector'",
                      "SELECT source_name, source_sha256, count(*) AS chunks FROM document_chunks GROUP BY source_name,source_sha256 ORDER BY source_name"]
        for statement in statements:
            result = call_with_database_resume_retry(client.execute_statement,
                sql=statement, formatRecordsAs='JSON', **options)
            print(result.get('formattedRecords', '[]'))
else:
    from resources.agent.agent_starter import build_agent
    print(json.dumps(build_agent(args.question), indent=2))
