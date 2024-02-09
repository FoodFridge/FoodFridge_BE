terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# S3 Bucket for Lambda Function Code
resource "aws_s3_bucket" "lambda_code_bucket" {
  bucket_prefix = "foodfridge-" # Terraform will auto-generate a unique suffix
}
