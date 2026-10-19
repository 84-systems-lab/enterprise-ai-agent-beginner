# Aurora PostgreSQL storage for AskAnyDoc document chunks and Titan embeddings.
# Lambda reaches this private database through the RDS Data API, so the Lambda
# does not need a direct network connection into the VPC.


resource "aws_db_subnet_group" "vector_database" {
  name       = "${var.project_name}-vector-database-dev"
  subnet_ids = aws_subnet.database[*].id

  tags = {
    project    = var.project_name
    managed-by = "terraform"
    purpose    = "rag-vector-storage"
  }
}

resource "aws_security_group" "vector_database" {
  name        = "${var.project_name}-vector-database-dev"
  description = "Network boundary for the AskAnyDoc vector database"
  vpc_id      = aws_vpc.book.id

  tags = {
    project    = var.project_name
    managed-by = "terraform"
    purpose    = "rag-vector-storage"
  }
}

resource "aws_rds_cluster" "vector_database" {
  cluster_identifier          = "${var.project_name}-vector-database-dev"
  engine                      = "aurora-postgresql"
  engine_mode                 = "provisioned"
  engine_version              = var.aurora_engine_version
  database_name               = "askanydoc"
  master_username             = "askanydoc_admin"
  manage_master_user_password = true
  enable_http_endpoint        = true
  storage_encrypted           = true
  db_subnet_group_name        = aws_db_subnet_group.vector_database.name
  vpc_security_group_ids      = [aws_security_group.vector_database.id]
  backup_retention_period     = 1
  skip_final_snapshot         = false
  final_snapshot_identifier   = "${var.project_name}-final"
  deletion_protection         = true

  serverlessv2_scaling_configuration {
    min_capacity             = 0
    max_capacity             = 1
    seconds_until_auto_pause = 300
  }

  tags = {
    project    = var.project_name
    managed-by = "terraform"
    purpose    = "rag-vector-storage"
  }
}

resource "aws_rds_cluster_instance" "vector_database_writer" {
  identifier          = "${var.project_name}-vector-database-writer-dev"
  cluster_identifier  = aws_rds_cluster.vector_database.id
  instance_class      = "db.serverless"
  engine              = aws_rds_cluster.vector_database.engine
  engine_version      = aws_rds_cluster.vector_database.engine_version
  publicly_accessible = false

  tags = {
    project    = var.project_name
    managed-by = "terraform"
    purpose    = "rag-vector-storage"
  }
}
