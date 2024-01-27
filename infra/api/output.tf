data "aws_region" "current" {}

output "api_endpoint" {
  value = "${aws_apigatewayv2_api.api.api_endpoint}/${aws_apigatewayv2_stage.stage.name}/${replace(aws_apigatewayv2_route.route.route_key, "GET /", "")}"
}

output "cloudwatch_log_group_url" {
  value       = format("https://%s.console.aws.amazon.com/cloudwatch/home?region=%s#logsV2:log-groups/log-group/%s", data.aws_region.current.name, data.aws_region.current.name, replace(aws_cloudwatch_log_group.lambda_log_group.name, "/", "$252F"))
  description = "URL to AWS CloudWatch Log Group in the AWS Management Console"
}
