terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>5.92"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  required_version = ">=1.5, <2.0"
}

# Shared Terraform and AWS provider configuration.
# Service resources are grouped in the other clearly named .tf files.
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.expected_account_id]
}

# Read the active AWS account ID for account-scoped Lambda permissions.
data "aws_caller_identity" "current" {}
