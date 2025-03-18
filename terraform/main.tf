resource "aws_s3_bucket" "rajagopalan-endopheno" {
  bucket = "rajagopalan-endopheno"

  tags = {
    Owner = element(split("/", data.aws_caller_identity.current.arn), 1)
  }
}