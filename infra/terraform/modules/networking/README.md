# Networking Module

Provisions the core AWS networking foundation for the AUS Fin Agent platform in `ap-southeast-2`. Designed for ECS Fargate workloads spread across two availability zones.

---

## Resources created

| Resource | Count | Description |
|----------|-------|-------------|
| `aws_vpc` | 1 | VPC with DNS hostnames and DNS resolution enabled |
| `aws_internet_gateway` | 1 | Internet gateway attached to the VPC |
| `aws_subnet` (public) | 2 | Public subnets in AZs `a` and `b` — hosts the ALB and NAT Gateway |
| `aws_subnet` (private) | 2 | Private subnets in AZs `a` and `b` — hosts ECS tasks and RDS |
| `aws_eip` | 1 | Elastic IP for the NAT Gateway |
| `aws_nat_gateway` | 1 | NAT Gateway in the first public subnet for private egress |
| `aws_route_table` (public) | 1 | Routes `0.0.0.0/0` to the internet gateway |
| `aws_route_table` (private) | 1 | Routes `0.0.0.0/0` through the NAT Gateway |
| `aws_security_group` (alb) | 1 | Allows inbound HTTP (80) and HTTPS (443) from the internet |
| `aws_security_group` (ecs_api) | 1 | Allows inbound port 8000 from the ALB SG only |
| `aws_security_group` (ecs_web) | 1 | Allows inbound port 80 from the ALB SG only |
| `aws_security_group` (ecs_worker) | 1 | Egress-only — no inbound from ALB |
| `aws_security_group` (rds) | 1 | Allows inbound PostgreSQL (5432) from the API and worker SGs |

---

## Variables

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project` | `string` | — | Project name prefix applied to all resource names |
| `environment` | `string` | — | Environment label (`dev` or `prod`) |
| `aws_region` | `string` | `ap-southeast-2` | AWS region |
| `vpc_cidr` | `string` | `10.0.0.0/16` | CIDR block for the VPC |
| `tags` | `map(string)` | `{}` | Common tags merged onto every resource |

---

## Outputs

| Name | Description |
|------|-------------|
| `vpc_id` | ID of the created VPC |
| `public_subnet_ids` | List of public subnet IDs |
| `private_subnet_ids` | List of private subnet IDs |
| `alb_sg_id` | Security group ID for the ALB |
| `ecs_api_sg_id` | Security group ID for the API ECS task |
| `ecs_web_sg_id` | Security group ID for the Web ECS task |
| `ecs_worker_sg_id` | Security group ID for the Worker ECS task |
| `rds_sg_id` | Security group ID for RDS |

---

## Usage

Call this module from an environment root module:

```hcl
module "networking" {
  source      = "../../modules/networking"
  project     = "aus-fin-agent"
  environment = "dev"
  aws_region  = "ap-southeast-2"
  vpc_cidr    = "10.0.0.0/16"
  tags = {
    Project     = "aus-fin-agent"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}
```

---

## Deploying

This module is consumed by the root stack in `infra/terraform`. Deploy it through the root stack, not directly from this module folder.

### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.6
- AWS CLI configured with credentials that have sufficient IAM permissions
- An S3 bucket and DynamoDB table for remote state (update the `backend` block in the root module before first use)

### First-time setup

```bash
# Authenticate to AWS
aws sso login --profile aus-fin-agent-dev   # or export AWS_PROFILE / AWS_ACCESS_KEY_ID etc.

# Move into the root terraform stack
cd infra/terraform
```

### Deploy to dev

```bash
terraform init
terraform plan \
  -var-file=environments/dev/terraform.tfvars \
  -var="api_secret_key=$API_SECRET_KEY" \
  -var="db_password=$DB_PASSWORD" \
  -out=dev.tfplan
terraform apply dev.tfplan
```

### Deploy to prod

```bash
terraform init
terraform plan \
  -var-file=environments/prod/terraform.tfvars \
  -var="api_secret_key=$API_SECRET_KEY" \
  -var="db_password=$DB_PASSWORD" \
  -out=prod.tfplan
# Review the plan carefully before applying to production
terraform apply prod.tfplan
```

### Destroy an environment

> **Warning:** this will delete all networking resources including subnets and security groups. ECS services and RDS must be destroyed first to avoid dependency errors.

```bash
terraform destroy -var="environment=dev"
```

Or with the current structure:

```bash
terraform destroy \
  -var-file=environments/dev/terraform.tfvars \
  -var="api_secret_key=$API_SECRET_KEY" \
  -var="db_password=$DB_PASSWORD"
```

### Useful commands

```bash
# Show current state
terraform show

# List all managed resources
terraform state list

# Refresh state without applying changes
terraform refresh -var-file=environments/dev/terraform.tfvars

# Format all Terraform files
terraform fmt -recursive
```
