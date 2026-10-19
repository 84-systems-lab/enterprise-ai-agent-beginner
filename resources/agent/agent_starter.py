"""Build an AWS knowledge agent from the companion's reusable parts.

Run from the companion root after the database/model checkpoints.
This explicit live command uses the operator's AWS credentials and incurs usage.
"""
from pathlib import Path
import argparse
import json
import os
import sys

ROOT = Path.cwd()
if not (ROOT / "app/shared/askanydoc_rag").is_dir():
    raise SystemExit("Run from the companion root containing app, tools and resources.")
sys.path[:0] = [str(ROOT / "app"), str(ROOT / "app/api"), str(ROOT / "app/shared")]
from askanydoc_rag.aws import aws_client
from askanydoc_rag.tool_agent import run_agent
from shared_source_controller import SourceAdapter
from retrieval import retrieve_evidence


def read_library(query, fallback):
    return {"evidence": retrieve_evidence(query), "truncated": False}


def build_agent(question):
    library = SourceAdapter("aws", "Read policies from the shared AWS document library.",
                            read_library, ("pdf", "txt", "docx", "md", "text", "document"))
    return run_agent(aws_client("bedrock-runtime"), os.environ["ANSWER_MODEL_ID"], question,
                     {"aws": library}, ["aws"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", default="What is needed to report a damaged chair?")
    args = parser.parse_args()
    print(json.dumps(build_agent(args.question), indent=2))


if __name__ == "__main__":
    main()
