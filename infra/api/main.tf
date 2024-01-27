terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.34.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# IAM Role for Lambda Function
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda-foodfridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = ["lambda.amazonaws.com", "apigateway.amazonaws.com"]
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "foodfridge_api_lambda" {
  function_name = "api-lambda"
  handler       = "run.lambda_handler"
  runtime       = "python3.11"

  role = aws_iam_role.lambda_exec_role.arn

  s3_bucket = "foodfridge-20240127052946263200000001"
  s3_key    = "lambda.zip"
}

# ... (Other resources: aws_apigatewayv2_api, aws_apigatewayv2_integration, etc.)

resource "aws_apigatewayv2_api" "api" {
  name          = "foodfridge-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id             = aws_apigatewayv2_api.api.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.foodfridge_api_lambda.invoke_arn

  request_parameters = {
    "overwrite:path"                   = "$request.path"
  }
}

resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"

  target = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "prod"
  auto_deploy = true
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.foodfridge_api_lambda.function_name}"
  retention_in_days = 3
}

resource "aws_iam_policy" "lambda_logs_policy" {
  name        = "lambda-logs-policy"
  description = "IAM policy to allow Lambda to create log streams and put log events"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "${aws_cloudwatch_log_group.lambda_log_group.arn}:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs_attachment" {
  policy_arn = aws_iam_policy.lambda_logs_policy.arn
  role       = aws_iam_role.lambda_exec_role.name
}

resource "aws_lambda_permission" "allow_execution_from_apigateway" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.foodfridge_api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
