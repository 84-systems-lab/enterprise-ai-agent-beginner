import hashlib
import os
import unittest
from unittest.mock import patch, Mock
from tools.manage_document import database_arguments, source_identity, verify_cluster_secret

class DocumentToolTests(unittest.TestCase):
    def test_rds_generated_secret_is_bound_to_exact_cluster(self):
        env = {'VECTOR_DATABASE_ARN': 'arn:aws:rds:ap-southeast-2:111111111111:cluster:eos-book-demo',
               'VECTOR_DATABASE_SECRET_ARN': 'arn:aws:secretsmanager:ap-southeast-2:111111111111:secret:rds!cluster-fixture',
               'VECTOR_DATABASE_NAME': 'askanydoc'}
        with patch.dict(os.environ, env):
            options = database_arguments('111111111111')
        rds = Mock()
        rds.describe_db_clusters.return_value = {'DBClusters': [{'DBClusterArn': options['resourceArn'],
            'MasterUserSecret': {'SecretArn': options['secretArn']}, 'DatabaseName': 'askanydoc'}]}
        verify_cluster_secret(rds, options)
        rds.describe_db_clusters.assert_called_once_with(DBClusterIdentifier='eos-book-demo')

    def test_same_account_unrelated_secret_is_rejected(self):
        options = {'resourceArn': 'arn:aws:rds:ap-southeast-2:111111111111:cluster:eos-book-demo',
                   'secretArn': 'arn:aws:secretsmanager:ap-southeast-2:111111111111:secret:other', 'database': 'askanydoc'}
        rds = Mock()
        rds.describe_db_clusters.return_value = {'DBClusters': [{'DBClusterArn': options['resourceArn'],
            'MasterUserSecret': {'SecretArn': 'different'}, 'DatabaseName': 'askanydoc'}]}
        with self.assertRaises(ValueError):
            verify_cluster_secret(rds, options)

    def test_source_identity_matches_ingestion_uri_hash(self):
        uri = 's3://eos-book-fixture-documents/uploads/policy.pdf'
        bucket, identity = source_identity(uri)
        self.assertEqual(bucket, 'eos-book-fixture-documents')
        self.assertEqual(identity, hashlib.sha256(uri.encode()).hexdigest())

    def test_unrelated_or_broad_target_is_rejected(self):
        for uri in ['s3://production/uploads/policy.pdf', 's3://eos-book-demo/',
                    'https://example.com/policy.pdf', 's3://eos-book-demo/uploads/p.pdf?version=old']:
            with self.subTest(uri=uri), self.assertRaises(ValueError):
                source_identity(uri)

    def test_cross_account_cluster_is_rejected(self):
        env = {'VECTOR_DATABASE_ARN': 'arn:aws:rds:ap-southeast-2:111111111111:cluster:eos-book-demo',
               'VECTOR_DATABASE_SECRET_ARN': 'arn:aws:secretsmanager:ap-southeast-2:222222222222:secret:eos-book-demo',
               'VECTOR_DATABASE_NAME': 'askanydoc'}
        with patch.dict(os.environ, env), self.assertRaises(ValueError):
            database_arguments('222222222222')
