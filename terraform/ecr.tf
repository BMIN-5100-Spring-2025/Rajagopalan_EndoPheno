resource "aws_ecr_repository" "rajagopalan-endopheno_ecr_repository" {
  name                 = "rajagopalan-endopheno"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}