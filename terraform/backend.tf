terraform {
  backend "s3" {
    bucket         = "bmin5100-terraform-state"
    key            = "ananya.rajagopalan@pennmedicine.upenn.edu-EndoPheno/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}