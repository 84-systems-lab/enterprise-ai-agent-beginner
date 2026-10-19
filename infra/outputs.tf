# Terraform outputs.
# Displays the deployed endpoints and resource names used during verification.





output "https_website_url" {
  value = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "protected_api_url" {
  value = "${aws_apigatewayv2_api.protected_chat.api_endpoint}/chat"
}

output "answer_jobs_api_url" {
  value = "${aws_apigatewayv2_api.protected_chat.api_endpoint}/jobs"
}

output "document_bucket_name" {
  value = aws_s3_bucket.documents.bucket
}

output "ingestion_lambda_name" {
  value = aws_lambda_function.ingestion.function_name
}

output "ingestion_ecr_repository_url" {
  value = data.aws_ecr_repository.ingestion_lambda_images.repository_url
}

output "vector_database_cluster_arn" {
  value = aws_rds_cluster.vector_database.arn
}

output "vector_database_secret_arn" {
  value = aws_rds_cluster.vector_database.master_user_secret[0].secret_arn
}

output "vector_database_name" {
  value = aws_rds_cluster.vector_database.database_name
}

output "frontend_distribution_id" {
  value = aws_cloudfront_distribution.frontend.id
}

output "answer_lambda_name" {
  value = aws_lambda_function.lambda_function.function_name
}

output "answer_worker_lambda_name" {
  value = aws_lambda_function.answer_job_worker.function_name
}

output "entra_credential_secret_id" {
  value = aws_secretsmanager_secret.entra_api_credential.id
}

output "ingestion_failure_queue_url" {
  value = aws_sqs_queue.ingestion_failed_events.url
}
