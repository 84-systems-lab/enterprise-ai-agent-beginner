"""Preview or explicitly remove one retired document's indexed rows."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

def source_identity(uri: str) -> tuple[str, str]:
    parsed = urlsplit(uri)
    if (parsed.scheme != 's3' or not parsed.netloc.startswith('eos-book-')
            or not parsed.path.startswith('/uploads/') or parsed.path == '/uploads/'
            or parsed.query or parsed.fragment or '@' in parsed.netloc):
        raise ValueError('Supply one exact s3://eos-book-.../uploads/... source URI.')
    return parsed.netloc, hashlib.sha256(uri.encode('utf-8')).hexdigest()

def database_arguments(account: str) -> dict:
    cluster = os.environ['VECTOR_DATABASE_ARN']
    secret = os.environ['VECTOR_DATABASE_SECRET_ARN']
    cluster_fields = cluster.split(':', 5)
    for arn, service in [(cluster, 'rds'), (secret, 'secretsmanager')]:
        fields = arn.split(':', 5)
        if (len(fields) != 6 or fields[0] != 'arn' or fields[2] != service
                or fields[4] != account):
            raise ValueError('The selected database and secret must be in the active account.')
    secret_fields = secret.split(':', 5)
    if (not cluster_fields[5].startswith('cluster:eos-book-')
            or secret_fields[1:2] != cluster_fields[1:2]
            or secret_fields[3] != cluster_fields[3]
            or not secret_fields[5].startswith('secret:')):
        raise ValueError('Use the book cluster and its secret in the same partition and Region.')
    return {'resourceArn': cluster, 'secretArn': secret,
            'database': os.environ['VECTOR_DATABASE_NAME']}

def verify_cluster_secret(rds, options: dict) -> None:
    """Bind an RDS-generated secret to this exact cluster instead of its name."""
    identifier = options['resourceArn'].split(':', 5)[5].removeprefix('cluster:')
    clusters = rds.describe_db_clusters(DBClusterIdentifier=identifier).get('DBClusters', [])
    if (len(clusters) != 1 or clusters[0].get('DBClusterArn') != options['resourceArn']
            or clusters[0].get('MasterUserSecret', {}).get('SecretArn') != options['secretArn']
            or clusters[0].get('DatabaseName') != options['database']):
        raise ValueError('The selected secret/database must belong to the exact book cluster.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-uri', required=True)
    parser.add_argument('--confirm-remove', help='Repeat the exact source URI to execute removal.')
    args = parser.parse_args()
    bucket, document_id = source_identity(args.source_uri)
    if args.confirm_remove is not None and args.confirm_remove != args.source_uri:
        raise SystemExit('Removal confirmation must equal the source URI exactly.')
    import boto3
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app/shared"))
    from askanydoc_rag.data_api import call_with_database_resume_retry
    account = boto3.client('sts').get_caller_identity()['Account']
    options = database_arguments(account)
    verify_cluster_secret(boto3.client('rds'), options)
    boto3.client('s3').head_bucket(Bucket=bucket, ExpectedBucketOwner=account)
    client = boto3.client('rds-data')
    parameters = [{'name': 'document_id', 'value': {'stringValue': document_id}}]
    result = call_with_database_resume_retry(client.execute_statement, **options, parameters=parameters,
        sql='SELECT source_uri, count(*) AS chunks FROM document_chunks WHERE document_id=:document_id GROUP BY source_uri',
        formatRecordsAs='JSON')
    print(json.dumps({'source_uri': args.source_uri, 'matching_rows': json.loads(result.get('formattedRecords','[]'))}, indent=2))
    if args.confirm_remove:
        result = call_with_database_resume_retry(client.execute_statement, **options, parameters=parameters,
            sql='DELETE FROM document_chunks WHERE document_id=:document_id')
        print(json.dumps({'removed_rows': result.get('numberOfRecordsUpdated', 0)}))
    else:
        print('Preview only. Quiesce ingestion and retire the source before confirming index removal.')

if __name__ == '__main__':
    main()
