# S3 bucket infrastructure.

resource "aws_s3_bucket" "website" {
  bucket = "${var.project_name}-site-dev"

  tags = {
    project    = var.project_name
    managed-by = "terraform"
  }
}

# Configure the public bucket as a static website.
resource "aws_s3_bucket_website_configuration" "bucket_config" {
  bucket = aws_s3_bucket.website.id

  index_document {
    suffix = "index.html"
  }
}

# Block public access. CloudFront reads through signed Origin Access Control requests.
resource "aws_s3_bucket_public_access_block" "website_public_access" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Allow only this CloudFront distribution to read the frontend files.
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.website.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontRead"
        Effect    = "Allow"
        Principal = { Service = "cloudfront.amazonaws.com" }
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.website.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
          }
        }
      }
    ]
  })
}

# Upload the versioned React build through the private origin.


# Upload every built React asset with correct browser metadata.
resource "aws_s3_object" "frontend_files" {
  for_each = fileset("${path.module}/../frontend/dist", "**")

  bucket = aws_s3_bucket.website.id
  key    = each.value
  source = "${path.module}/../frontend/dist/${each.value}"
  etag   = filemd5("${path.module}/../frontend/dist/${each.value}")
  content_type = lookup({
    css  = "text/css"
    html = "text/html"
    js   = "application/javascript"
    png  = "image/png"
    svg  = "image/svg+xml"
  }, try(reverse(split(".", each.value))[0], ""), "application/octet-stream")
  cache_control = can(regex("^assets/", each.value)) ? "public,max-age=31536000,immutable" : "no-cache"
}

# Private bucket that stores original documents for RAG ingestion.
resource "aws_s3_bucket" "documents" {
  bucket = "${var.project_name}-documents-dev"

  tags = {
    project    = var.project_name
    managed-by = "terraform"
    purpose    = "rag-document-ingestion"
  }
}

# Encrypt uploaded documents at rest with S3-managed keys.
resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Retain older object versions when a document is replaced.
resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Prevent public access to company documents.
resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
