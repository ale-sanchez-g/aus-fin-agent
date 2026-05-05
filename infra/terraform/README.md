# Terraform Infrastructure

This Terraform stack deploys all platform services required by aus-fin-agent in AWS.

## What gets deployed

The root stack in this folder provisions:

- Networking baseline from the reusable module in modules/networking:
  - VPC, IGW, NAT Gateway, 2 public + 2 private subnets, route tables
  - Security groups for ALB, ECS services, and RDS
- Compute and traffic:
  - ECS Fargate cluster
  - ECS services for api, web, and worker
  - Application Load Balancer with path routing:
    - /api and /api/* to the api service
    - all other paths to the web service
- Data and storage:
  - RDS PostgreSQL instance in private subnets
  - S3 bucket for generated reports
- Registry and logging:
  - ECR repositories for api, web, worker images
  - CloudWatch log groups for each service
- Auth and identity:
  - Cognito user pool
  - Cognito app client
- IAM runtime permissions:
  - ECS execution role
  - ECS task role with S3 report access, Bedrock invoke permissions, and Cognito read permissions

## Repository layout

- infra/terraform/main.tf: full infrastructure composition
- infra/terraform/variables.tf: configurable inputs
- infra/terraform/outputs.tf: key outputs for deployment wiring
- infra/terraform/providers.tf: provider and version constraints
- infra/terraform/environments/dev/terraform.tfvars: dev sizing and behavior
- infra/terraform/environments/dev/backend.hcl.example: dev backend template
- infra/terraform/environments/prod/terraform.tfvars: prod sizing and behavior
- infra/terraform/environments/prod/backend.hcl.example: prod backend template
- infra/terraform/modules/networking: shared networking module

## Prerequisites

- Terraform >= 1.6
- AWS credentials with permissions for VPC, ECS, ECR, ALB, IAM, RDS, S3, Cognito, and CloudWatch
- AWS CLI configured (optional but useful)

## Deploy steps

Run all commands from infra/terraform.

### 1) Initialize

```bash
terraform init
```

Optional remote state initialization:

```bash
cp environments/dev/backend.hcl.example environments/dev/backend.hcl
terraform init -backend-config=environments/dev/backend.hcl
```

### 2) Plan for dev

```bash
terraform plan \
  -var-file=environments/dev/terraform.tfvars \
  -var="api_secret_key=$API_SECRET_KEY" \
  -var="db_password=$DB_PASSWORD" \
  -out=dev.tfplan
```

### 3) Apply dev

```bash
terraform apply dev.tfplan
```

### 4) Plan for prod

```bash
terraform plan \
  -var-file=environments/prod/terraform.tfvars \
  -var="api_secret_key=$API_SECRET_KEY" \
  -var="db_password=$DB_PASSWORD" \
  -out=prod.tfplan
```

### 5) Apply prod

```bash
terraform apply prod.tfplan
```

## Deploying a specific image tag

By default, services use latest. To pin images built by CI/CD, pass tags at plan time:

```bash
terraform plan \
  -var-file=environments/dev/terraform.tfvars \
  -var="api_image_tag=<git-sha>" \
  -var="web_image_tag=<git-sha>" \
  -var="worker_image_tag=<git-sha>" \
  -var="api_secret_key=$API_SECRET_KEY" \
  -var="db_password=$DB_PASSWORD" \
  -out=dev.tfplan
```

## Post-deploy checks

After apply, validate critical outputs:

```bash
terraform output alb_dns_name
terraform output cluster_name
terraform output ecr_repository_urls
terraform output reports_bucket_name
terraform output db_endpoint
terraform output cognito_user_pool_id
```

Then check:

- Web UI: http://<alb-dns-name>/
- API health: http://<alb-dns-name>/api/v1/health

## Notes

- The API and worker containers already include the open-banking-mcp npm package and run it in-process when required.
- In prod, set cdr_mock_mode=false (already set in environments/prod/terraform.tfvars) and ensure outbound connectivity to CDR APIs.
- For safe production operation, keep enable_deletion_protection=true in prod.
