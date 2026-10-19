# Registry is deliberately bootstrapped in infra/bootstrap with separate state.
data "aws_ecr_repository" "ingestion_lambda_images" {
  name = "${var.project_name}-ingestion-lambda-images-dev"
}
