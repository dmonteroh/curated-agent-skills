# Terraform Best Practices: DRY and Naming

## DRY Principles

**Use modules for reusability**
```hcl
# Bad - repeated code
resource "aws_vpc" "app1" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "app1-vpc", Environment = "prod" }
}

resource "aws_vpc" "app2" {
  cidr_block = "10.1.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "app2-vpc", Environment = "prod" }
}

# Good - use module
module "vpc_app1" {
  source = "./modules/vpc"

  name        = "app1"
  cidr_block  = "10.0.0.0/16"
  environment = "prod"
}

module "vpc_app2" {
  source = "./modules/vpc"

  name        = "app2"
  cidr_block  = "10.1.0.0/16"
  environment = "prod"
}
```

**Use locals for repeated values**
```hcl
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = var.project_name
    CostCenter  = var.cost_center
  }

  name_prefix = "${var.project_name}-${var.environment}"
  vpc_cidr    = var.environment == "production" ? "10.0.0.0/16" : "10.1.0.0/16"
}

resource "aws_vpc" "main" {
  cidr_block = local.vpc_cidr
  tags       = merge(local.common_tags, { Name = "${local.name_prefix}-vpc" })
}
```

**Use data sources instead of hardcoding**
```hcl
# Bad - hardcoded AMI
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
}

# Good - dynamic AMI lookup
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t3.micro"
}
```

**Use `for_each` for multiple similar resources**
```hcl
variable "private_subnets" {
  type = map(object({
    cidr_block = string
    az         = string
  }))
  default = {
    subnet1 = { cidr_block = "10.0.1.0/24", az = "us-east-1a" }
    subnet2 = { cidr_block = "10.0.2.0/24", az = "us-east-1b" }
  }
}

resource "aws_subnet" "private" {
  for_each = var.private_subnets

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value.cidr_block
  availability_zone = each.value.az

  tags = {
    Name = "${var.name}-private-${each.key}"
  }
}
```

## Naming Conventions

**Resource naming**
```hcl
resource "aws_vpc" "main" {}
resource "aws_subnet" "private" {}
resource "aws_security_group" "web" {}
resource "aws_instance" "app" {}

# Avoid generic names outside modules
resource "aws_vpc" "vpc" {}        # Bad
resource "aws_subnet" "subnet" {}  # Bad
```

**AWS resource name tags**
```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

resource "aws_vpc" "main" {
  cidr_block = var.cidr_block

  tags = {
    Name = "${local.name_prefix}-vpc"
  }
}

resource "aws_security_group" "web" {
  name   = "${local.name_prefix}-web-sg"
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name_prefix}-web-sg"
  }
}
```

**Variable naming**
```hcl
variable "instance_type" {}      # Good
variable "instanceType" {}       # Bad
variable "InstanceType" {}       # Bad

variable "vpc_cidr_block" {}     # Good
variable "cidr" {}               # Too vague

variable "enable_nat_gateway" {} # Good
variable "nat_gateway" {}        # Ambiguous

variable "availability_zones" {} # Good
variable "private_subnets" {}    # Good
```

**File naming**
```
main.tf           # Primary resource definitions
variables.tf      # Input variables
outputs.tf        # Output values
versions.tf       # Terraform and provider versions
backend.tf        # Backend configuration (optional)
locals.tf         # Local values (optional)
data.tf           # Data sources (optional)

# Resource-specific files for complex modules
vpc.tf
subnets.tf
security_groups.tf
route_tables.tf
```
