variable "project_name" {
  type        = string
  description = "Unique book-only resource prefix; never use the reference prefix."
  validation {
    condition     = can(regex("^eos-book-[a-z0-9-]{3,24}$", var.project_name))
    error_message = "Choose eos-book- followed by a unique lowercase suffix."
  }
}
variable "expected_account_id" {
  type = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.expected_account_id))
    error_message = "Supply the intended AWS account ID."
  }
}
variable "aws_region" { type = string }
variable "answer_model_id" { type = string }
variable "aurora_engine_version" { type = string }
variable "answer_model_resource_arns" {
  type        = list(string)
  description = "Verified inference profile and foundation model ARNs, including Titan."
  validation {
    condition     = length(var.answer_model_resource_arns) > 0
    error_message = "Supply the exact permitted Bedrock resources."
  }
}
variable "ingestion_image_uri" {
  type        = string
  description = "Image URI in the book ECR repository, pinned to its pushed digest."
  validation {
    condition     = can(regex("@sha256:[a-f0-9]{64}$", var.ingestion_image_uri))
    error_message = "Supply a verified immutable image digest."
  }
}
