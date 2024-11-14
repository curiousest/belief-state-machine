# main.tf

provider "aws" {
  region = var.aws_region
}

terraform {
  backend "s3" {
    bucket         = "bsm-terraform-state-bucket"
    key            = "terraform.tfstate"
    region         = var.aws_region
    dynamodb_table = "bsm-terraform-lock-table"
    encrypt        = true
  }
}
