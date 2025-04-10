resource "aws_ecr_repository" "rajagopalan-endopheno" {
  name                 = "rajagopalan-endopheno"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}