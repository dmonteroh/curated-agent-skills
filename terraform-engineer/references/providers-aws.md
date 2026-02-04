# Terraform AWS Provider Configuration

## Basic Configuration

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = var.project_name
    }
  }
}
```

## Multiple AWS Accounts/Regions

```hcl
provider "aws" {
  alias  = "primary"
  region = "us-east-1"

  assume_role {
    role_arn     = "arn:aws:iam::123456789012:role/TerraformRole"
    session_name = "terraform-session"
  }
}

provider "aws" {
  alias  = "secondary"
  region = "us-west-2"

  assume_role {
    role_arn = "arn:aws:iam::987654321098:role/TerraformRole"
  }
}

resource "aws_vpc" "primary" {
  provider   = aws.primary
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "secondary" {
  provider   = aws.secondary
  cidr_block = "10.1.0.0/16"
}
```

## AWS Authentication Methods

```hcl
# Method 1: Environment variables (recommended for CI/CD)
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN

# Method 2: Shared credentials file
provider "aws" {
  region                   = "us-east-1"
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "production"
}

# Method 3: IAM role (recommended for EC2/ECS)
provider "aws" {
  region = "us-east-1"
  # Automatically uses instance profile
}

# Method 4: Assume role
provider "aws" {
  region = "us-east-1"

  assume_role {
    role_arn     = var.terraform_role_arn
    session_name = "terraform-${var.environment}"
    external_id  = var.external_id
  }
}
```

## AWS Provider Features

```hcl
provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Environment = "production"
      ManagedBy   = "Terraform"
      CostCenter  = "engineering"
    }
  }

  ignore_tags {
    keys = ["aws:autoscaling:groupName"]
  }

  endpoints {
    s3  = "http://localhost:4566"
    ec2 = "http://localhost:4566"
  }

  max_retries = 3
  http_proxy  = "http://proxy.example.com:8080"
}
```
