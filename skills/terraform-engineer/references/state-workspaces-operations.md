# Terraform State Workspaces and Operations

## Workspaces

```bash
terraform workspace list
terraform workspace new staging
terraform workspace select production
terraform workspace show
terraform workspace delete dev
```

```hcl
locals {
  environment = terraform.workspace

  vpc_cidr = {
    production = "10.0.0.0/16"
    staging    = "10.1.0.0/16"
    dev        = "10.2.0.0/16"
  }

  instance_count = {
    production = 5
    staging    = 2
    dev        = 1
  }
}

resource "aws_vpc" "main" {
  cidr_block = local.vpc_cidr[local.environment]

  tags = {
    Name        = "${local.environment}-vpc"
    Environment = local.environment
  }
}

resource "aws_instance" "app" {
  count = local.instance_count[local.environment]

  ami           = var.ami_id
  instance_type = "t3.micro"

  tags = {
    Name        = "${local.environment}-app-${count.index + 1}"
    Environment = local.environment
  }
}
```

## Partial Backend Configuration

```hcl
terraform {
  backend "s3" {}
}
```

```hcl
# config/backend-prod.hcl
bucket         = "terraform-state-prod"
key            = "vpc/terraform.tfstate"
region         = "us-east-1"
encrypt        = true
dynamodb_table = "terraform-lock-prod"
```

```bash
terraform init -backend-config=config/backend-prod.hcl
```

## State Operations

```bash
terraform import aws_vpc.main vpc-12345678
terraform import module.network.aws_vpc.main vpc-12345678

terraform state list
terraform state show aws_vpc.main
terraform state mv aws_instance.old aws_instance.new
terraform state rm aws_instance.example
terraform state pull > terraform.tfstate.backup
terraform state push terraform.tfstate
```

## State Migration

```bash
terraform init -migrate-state
terraform init -reconfigure
terraform init -backend-config=new-backend.hcl -migrate-state
```
