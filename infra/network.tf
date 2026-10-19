# A book-owned network. Lambda uses the HTTPS Data API outside this VPC.
data "aws_availability_zones" "book" {
  state = "available"
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required", "opted-in"]
  }
}
resource "aws_vpc" "book" {
  cidr_block           = "10.74.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "${var.project_name}-database", project = var.project_name }
}
resource "aws_subnet" "database" {
  count                   = 2
  vpc_id                  = aws_vpc.book.id
  availability_zone       = data.aws_availability_zones.book.names[count.index]
  cidr_block              = cidrsubnet(aws_vpc.book.cidr_block, 8, count.index)
  map_public_ip_on_launch = false
  tags                    = { Name = "${var.project_name}-database-${count.index + 1}", project = var.project_name }
}
