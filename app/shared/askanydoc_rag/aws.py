"""Create regional AWS clients with one consistent retry policy."""

from __future__ import annotations

import os

import boto3
from botocore.config import Config


AWS_CLIENT_CONFIG = Config(retries={"mode": "standard", "max_attempts": 4})


def deployment_region() -> str:
    """Use the Lambda Region or local book setting, with Sydney as the example."""
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "ap-southeast-2"


def aws_client(service_name: str):
    """Return an AWS client configured for AskAnyDoc's deployment Region."""
    return boto3.client(
        service_name,
        region_name=deployment_region(),
        config=AWS_CLIENT_CONFIG,
    )
