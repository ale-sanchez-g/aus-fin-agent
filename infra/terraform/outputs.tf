output "cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  description = "Public ALB DNS name for web and API traffic."
  value       = aws_lb.main.dns_name
}

output "api_service_name" {
  description = "ECS API service name."
  value       = aws_ecs_service.api.name
}

output "web_service_name" {
  description = "ECS Web service name."
  value       = aws_ecs_service.web.name
}

output "worker_service_name" {
  description = "ECS Worker service name."
  value       = aws_ecs_service.worker.name
}

output "ecr_repository_urls" {
  description = "ECR repositories keyed by service name."
  value = {
    for service, repo in aws_ecr_repository.services : service => repo.repository_url
  }
}

output "reports_bucket_name" {
  description = "S3 bucket for recommendation reports."
  value       = aws_s3_bucket.reports.bucket
}

output "db_endpoint" {
  description = "RDS endpoint hostname."
  value       = aws_db_instance.postgres.address
}

output "db_port" {
  description = "RDS endpoint port."
  value       = aws_db_instance.postgres.port
}

output "db_name" {
  description = "RDS database name."
  value       = aws_db_instance.postgres.db_name
}

output "db_username" {
  description = "RDS master username."
  value       = aws_db_instance.postgres.username
}

output "db_password" {
  description = "RDS master password in use."
  value       = local.resolved_db_password
  sensitive   = true
}

output "cognito_user_pool_id" {
  description = "Cognito user pool id for auth integration."
  value       = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  description = "Cognito app client id used by web/API."
  value       = aws_cognito_user_pool_client.web.id
}
