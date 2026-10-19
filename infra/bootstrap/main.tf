terraform {
  required_version = ">=1.5, <2.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "5.100.0" }
  }
}
variable "project_name" {
  type = string
  validation {
    condition     = can(regex("^eos-book-[a-z0-9-]{3,24}$", var.project_name))
    error_message = "Use a unique eos-book prefix."
  }
}
variable "expected_account_id" { type = string }
variable "aws_region" { type = string }
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.expected_account_id]
}
resource "aws_ecr_repository" "ingestion_lambda_images" {
  name                 = "${var.project_name}-ingestion-lambda-images-dev"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
  tags = { project = var.project_name, purpose = "book-ingestion" }
}
output "repository_url" { value = aws_ecr_repository.ingestion_lambda_images.repository_url }
