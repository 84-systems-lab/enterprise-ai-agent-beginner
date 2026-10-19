"""Region selection and fixed-route forwarding must agree."""
import os
import unittest
from unittest.mock import patch

from askanydoc_rag import aws
import shared_source_controller as shared


class RegionTests(unittest.TestCase):
    def test_document_adapter_accepts_markdown_provenance(self):
        adapter = shared._document_adapter("aws", "search_aws_documents", {})
        passage = {"source_type": "md", "chunk_text": "Report damage within seven days.",
                   "source_name": "policy.md", "source_uri": "s3://eos-book-demo/uploads/policy.md",
                   "object_key": "uploads/policy.md", "location": {"heading_path": ["Returns"]}, "similarity": 0.8}
        result = shared._validated_evidence({"evidence": [passage], "truncated": False}, adapter)
        self.assertEqual(result[0]["location"], {"heading_path": ["Returns"]})

    def test_local_region_reaches_sdk(self):
        with patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-west-2"}, clear=True), patch.object(aws.boto3, "client") as client:
            aws.aws_client("s3")
            self.assertEqual(client.call_args.kwargs["region_name"], "us-west-2")

    def test_lambda_region_is_used(self):
        with patch.dict(os.environ, {"AWS_REGION": "eu-west-1", "AWS_DEFAULT_REGION": "us-west-2"}, clear=True):
            self.assertEqual(aws.deployment_region(), "eu-west-1")

    def test_example_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(aws.deployment_region(), "ap-southeast-2")

    def test_endpoint_must_match_region_and_exact_route(self):
        settings = {"AWS_DEFAULT_REGION": "us-west-2", "SALESFORCE_EVIDENCE_URL": "https://example.execute-api.us-west-2.amazonaws.com/salesforce/evidence"}
        with patch.dict(os.environ, settings, clear=True):
            self.assertEqual(shared._salesforce_adapter({"access_token": "fixture"}).source_id, "salesforce")
            for url in ["https://example.execute-api.ap-southeast-2.amazonaws.com/salesforce/evidence", "https://example.execute-api.us-west-2.amazonaws.com.attacker.invalid/salesforce/evidence", "https://example.execute-api.us-west-2.amazonaws.com/salesforce/evidence?forward=1"]:
                os.environ["SALESFORCE_EVIDENCE_URL"] = url
                with self.assertRaises(ValueError):
                    shared._salesforce_adapter({"access_token": "fixture"})
