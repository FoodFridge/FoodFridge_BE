variable "environment" {
  description = "The environment for the deployment"
  default     = "prod"
  type        = string
}

variable "lambda_zip_file" {
  description = "The filename of the lambda zip file in the S3 bucket"
  type        = string
}
