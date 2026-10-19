"""Wire the shared agent loop to the application's authorised source adapters."""
from askanydoc_rag.aws import aws_client
from askanydoc_rag.tool_agent import run_agent
from shared_source_controller import registered_sources
import os


def answer_with_agent(question, auth_context, sources):
    if not auth_context or not all(auth_context.get(k) for k in ("tenant_id", "user_id", "access_token")):
        raise ValueError("The agent requires a validated organisation identity.")
    # Browser choices narrow this catalogue; they cannot enable a connector or supply credentials.
    catalogue = registered_sources(auth_context)
    return run_agent(aws_client("bedrock-runtime"), os.environ["ANSWER_MODEL_ID"],
                     question, catalogue, list(sources))
