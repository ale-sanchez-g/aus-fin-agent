output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "alb_sg_id" {
  value = aws_security_group.alb.id
}

output "ecs_api_sg_id" {
  value = aws_security_group.ecs_api.id
}

output "ecs_web_sg_id" {
  value = aws_security_group.ecs_web.id
}


output "rds_sg_id" {
  value = aws_security_group.rds.id
}
