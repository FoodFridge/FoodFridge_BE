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
    key            = "infra/tf-backend/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "jessiep-tf-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "jessiep-tf-state-bucket" # Ensure this is globally unique

  tags = {
    Name        = "Terraform State Bucket"
    Environment = "Production"
  }
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls   = true
  ignore_public_acls  = true
  block_public_policy = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_locks" {
  name           = "jessiep-tf-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Lock Table"
    Environment = "Production"
  }
}
