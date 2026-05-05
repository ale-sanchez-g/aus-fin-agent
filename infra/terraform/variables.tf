variable "project" {
  description = "Project name prefix used for resources."
  type        = string
  default     = "aus-fin-agent"
}

variable "environment" {
  description = "Deployment environment (for example: dev, prod)."
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy resources into."
  type        = string
  default     = "ap-southeast-2"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "api_image_tag" {
  description = "Container image tag to deploy for API."
  type        = string
  default     = "latest"
}

variable "web_image_tag" {
  description = "Container image tag to deploy for Web."
  type        = string
  default     = "latest"
}


variable "api_desired_count" {
  description = "Number of running API tasks."
  type        = number
  default     = 1
}

variable "web_desired_count" {
  description = "Number of running Web tasks."
  type        = number
  default     = 1
}


variable "api_task_cpu" {
  description = "CPU units for the API task definition."
  type        = number
  default     = 512
}

variable "api_task_memory" {
  description = "Memory (MiB) for the API task definition."
  type        = number
  default     = 1024
}

variable "web_task_cpu" {
  description = "CPU units for the Web task definition."
  type        = number
  default     = 256
}

variable "web_task_memory" {
  description = "Memory (MiB) for the Web task definition."
  type        = number
  default     = 512
}



variable "db_name" {
  description = "PostgreSQL database name."
  type        = string
  default     = "ausfinagent"
}

variable "db_username" {
  description = "PostgreSQL master username."
  type        = string
  default     = "ausfin"
}

variable "db_password" {
  description = "PostgreSQL master password. If empty, Terraform generates one."
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_engine_version" {
  description = "PostgreSQL engine version for RDS."
  type        = string
  default     = "16.13"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for PostgreSQL in GiB."
  type        = number
  default     = 20
}


variable "cdr_mock_mode" {
  description = "Whether API and Worker run against mock CDR data."
  type        = bool
  default     = true
}

variable "cdr_base_url" {
  description = "Base URL for live CDR API when mock mode is disabled."
  type        = string
  default     = "https://api.cdr.gov.au"
}

variable "bedrock_model_id" {
  description = "Bedrock model id used by API."
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "api_secret_key" {
  description = "Secret key used by API auth fallback mode."
  type        = string
  default     = "replace-me"
  sensitive   = true
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for stateful resources in production."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags applied to all resources."
  type        = map(string)
  default     = {}
}
