terraform {
  required_version = "1.7.3"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
  backend "s3" {
    bucket         = "jessiep-tf-state-bucket"
    key            = "infra/s3/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "jessiep-tf-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-east-1"
}

# S3 Bucket for Lambda Function Code
resource "aws_s3_bucket" "lambda_code_bucket" {
  bucket_prefix = "foodfridge-" # Terraform will auto-generate a unique suffix
}
