"""Exercise agent request -> owned job -> worker -> shared loop -> answer result."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import answer_job_api_handler as jobs
import answer_job_worker as worker
import answer_lambda_handler as chat
import enterprise_agent
from tools.agent_app_demo import FixtureAdapter, ScriptedAgentModel


def event(body):
    return {"routeKey": "POST /jobs", "headers": {"authorization": "Bearer fixture-token"},
            "requestContext": {"authorizer": {"jwt": {"claims": {"oid": "alex", "tid": "fixture-tenant"}}}},
            "body": json.dumps(body)}


class AgentApplicationTests(unittest.TestCase):
    def test_owned_job_runs_agent_and_preserves_activity(self):
        dynamo, queue = Mock(), Mock()
        dynamo.update_item.return_value = {"Attributes": {"attempt_count": {"N": "1"}}}
        model = ScriptedAgentModel(["aws"], "chair")
        with patch.object(jobs, "dynamodb_client", dynamo), patch.object(jobs, "sqs_client", queue):
            created = jobs.handler(event({"question": "chair", "mode": "agent", "sources": ["aws"]}), None)
        self.assertEqual(created["statusCode"], 202)
        queued = json.loads(queue.send_message.call_args.kwargs["MessageBody"])
        self.assertEqual(queued["mode"], "agent")
        self.assertEqual(queued["sources"], ["aws"])
        with (patch.object(worker, "dynamodb_client", dynamo),
              patch.object(worker, "configure_langfuse", return_value=False),
              patch.object(enterprise_agent, "aws_client", return_value=model),
              patch.object(enterprise_agent, "registered_sources", return_value={"aws": FixtureAdapter("aws")}) as catalogue,
              patch.dict("os.environ", {"ANSWER_MODEL_ID": "fixture-model"})):
            worker.handler({"Records": [{"body": json.dumps(queued)}]}, SimpleNamespace(aws_request_id="fixture-request"))
        catalogue.assert_called_once_with({"user_id": "alex", "tenant_id": "fixture-tenant", "access_token": "fixture-token"})
        stored = json.loads(dynamo.update_item.call_args.kwargs["ExpressionAttributeValues"][":result"]["S"])
        self.assertEqual(stored["answer_mode"], "agent")
        self.assertEqual(stored["source_outcomes"], {"aws": "found"})
        self.assertTrue(stored["agent_trace"])
        self.assertTrue(stored["citations"])

    def test_invalid_mode_or_scope_never_queues(self):
        for body in ([1], {"question": "chair", "mode": "write"},
                     {"question": "chair", "mode": "agent", "sources": []},
                     {"question": "chair", "mode": "agent", "sources": ["aws", "aws"]}):
            with self.subTest(body=body), patch.object(jobs, "dynamodb_client") as dynamo, patch.object(jobs, "sqs_client") as queue:
                result = jobs.handler(event(body), None)
                self.assertEqual(result["statusCode"], 400)
                dynamo.put_item.assert_not_called()
                queue.send_message.assert_not_called()

    def test_direct_route_uses_agent_with_validated_identity(self):
        request = event({"question": "chair", "mode": "agent", "sources": ["aws"], "user_id": "someone-else"})
        output = {"answer": "Supported", "source_mode": "organisation_sources", "citations": [], "input_tokens": 0, "output_tokens": 0}
        with patch.object(chat, "configure_langfuse", return_value=False), patch.object(chat, "answer_with_agent", return_value=output) as agent:
            result = chat.handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(agent.call_args.args[1]["user_id"], "alex")
        self.assertEqual(agent.call_args.args[2], ("aws",))

    def test_agent_rejects_missing_validated_identity(self):
        request = {"body": json.dumps({"question": "chair", "mode": "agent", "sources": ["aws"]})}
        with patch.object(chat, "configure_langfuse", return_value=False), patch.object(chat, "answer_with_agent") as agent:
            result = chat.handler(request, None)
        self.assertEqual(result["statusCode"], 401)
        agent.assert_not_called()

    def test_worker_revalidates_queue_options_before_claim(self):
        queued = {"job_id": "fixture-job", "question": "chair", "mode": "agent", "sources": ["shell"],
                  "auth_context": {"user_id": "alex", "tenant_id": "fixture", "access_token": "fixture"}}
        with patch.object(worker, "_claim_job") as claim, self.assertRaises(ValueError):
            worker.handler({"Records": [{"body": json.dumps(queued)}]}, None)
        claim.assert_not_called()
