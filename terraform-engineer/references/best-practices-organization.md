# Terraform Best Practices: Code Organization

## Directory Structure

```
terraform/
├── environments/
│   ├── production/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── development/
├── modules/
│   ├── vpc/
│   ├── eks/
│   └── rds/
├── global/
│   ├── iam/
│   └── route53/
└── README.md
```

## Module Best Practices

```hcl
# Keep modules small and focused
# modules/vpc/main.tf - does one thing well

# Clear input/output contracts
# modules/vpc/variables.tf
variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  validation { ... }
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.this.id
}

# Version all modules
# modules/vpc/versions.tf
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```
