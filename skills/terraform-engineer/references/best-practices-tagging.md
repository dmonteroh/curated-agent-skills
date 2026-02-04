# Terraform Best Practices: Tagging

## Consistent Tagging Strategy

```hcl
locals {
  # Required tags for all resources
  required_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = var.project_name
    CostCenter  = var.cost_center
    Owner       = var.owner_email
  }

  # Optional tags
  optional_tags = {
    Repository = "github.com/org/repo"
    Terraform  = "true"
  }

  # Merge all tags
  common_tags = merge(local.required_tags, local.optional_tags, var.additional_tags)
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type

  tags = merge(local.common_tags, {
    Name   = "${var.name}-app"
    Role   = "application"
    Backup = "daily"
  })
}
```
