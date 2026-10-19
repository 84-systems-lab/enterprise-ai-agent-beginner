# Protected answer Lambda, explicit packages and scoped service permissions.
resource "aws_iam_role" "lambda_exec" {    # nick name here like- lambda-exec are just for terraform to reference that aws never sees
  name = "${var.project_name}-lambda-exec" # and this name is real name that ends up showing in AWS console

  # assume_role_policy = the TRUST policy: WHO may wear this policy
  # Principal.Service = the Lambda service itself; sts:AssumeRole = "put badge on"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow" # Principal is allowed to Action - assume role 
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    project    = var.project_name
    managed-by = "terraform"
  }
}

# aws-MANAGED policy: AWS pre-wrote it; you reference it by ARN.
# ---------------------------------------------------------------------

# above was about making a role and defining who can take this role,

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Creating bedrock invoke policy from kind of scratch.

resource "aws_iam_role_policy" "bedrock_invoke" {
  name = "${var.project_name}-bedrock-invoke"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "bedrock:InvokeModel"
      Resource = var.answer_model_resource_arns
    }]
  })
}



# Same pattern as bedrock_invoke - a custom policy, written by us, attached to the role.


resource "aws_iam_role_policy" "entra_secret_access" {
  name = "${var.project_name}-entra-secret-access"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "secretsmanager:GetSecretValue"
      Resource = aws_secretsmanager_secret.entra_api_credential.arn
    }]
  })
}

resource "aws_iam_role_policy" "answer_vector_database" {
  name = "${var.project_name}-answer-vector-database"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "rds-data:ExecuteStatement"
        Resource = aws_rds_cluster.vector_database.arn
      },
      {
        Effect   = "Allow"
        Action   = "secretsmanager:GetSecretValue"
        Resource = aws_rds_cluster.vector_database.master_user_secret[0].secret_arn
      }
    ]
  })
}



# Installs pinned runtime dependencies and copies only deployable Python modules into build/.


data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/build"
  output_path = "${path.module}/lambda.zip"
}


# then upload the zip file

resource "aws_lambda_function" "lambda_function" {
  function_name    = "${var.project_name}-api"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256 # redeploy when the ZIP content changes
  handler          = "answer_lambda_handler.handler"                  # module.function inside the deployment ZIP
  runtime          = "python3.13"                                     # so that terraform knows if to do ZIP
  timeout          = 60
  memory_size      = 512

  environment {
    variables = {
      ANSWER_MODEL_ID              = var.answer_model_id
      EMBEDDING_MODEL_ID           = "amazon.titan-embed-text-v2:0"
      MAX_HISTORY_CHARACTERS       = "12000"
      MAX_HISTORY_MESSAGES         = "12"
      MAX_RESPONSE_TOKENS          = "2048"
      MAX_TOOL_ROUNDS              = "2"
      MINIMUM_RETRIEVAL_SIMILARITY = "0.35"
      # SharePoint is an explicit, environment-specific gate. Safe defaults keep it
      # disabled until delegated identity and retrieval are configured.
      SHAREPOINT_ENABLED             = tostring(var.sharepoint_enabled)
      SHAREPOINT_PROVIDER            = var.sharepoint_provider
      SHAREPOINT_GENERAL_SITE_URL    = var.sharepoint_general_site_url
      SHAREPOINT_RESTRICTED_SITE_URL = var.sharepoint_restricted_site_url
      SHAREPOINT_MAX_RESULTS         = tostring(var.sharepoint_max_results)
      SHAREPOINT_TIMEOUT_SECONDS     = "8"
      SHAREPOINT_MAX_RETRIES         = "2"
      ENTRA_TENANT_ID                = var.entra_tenant_id
      ENTRA_API_CLIENT_ID            = var.entra_api_client_id
      ENTRA_CREDENTIAL_SECRET_ID     = aws_secretsmanager_secret.entra_api_credential.id
      RETRIEVAL_RESULT_LIMIT         = "5"
      VECTOR_DATABASE_ARN            = aws_rds_cluster.vector_database.arn
      VECTOR_DATABASE_NAME           = aws_rds_cluster.vector_database.database_name
      VECTOR_DATABASE_SECRET_ARN     = aws_rds_cluster.vector_database.master_user_secret[0].secret_arn
    }
  }

  tags = {
    project    = var.project_name
    managed-by = "terraform"
  }
}












