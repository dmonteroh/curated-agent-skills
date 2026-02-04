# Terraform Module Versioning and Testing

## Module Versioning

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"  # >= 19.0, < 20.0
}

module "custom" {
  source = "git::https://github.com/org/terraform-modules.git//vpc?ref=v1.2.3"
}
```

## Module Testing Example

```hcl
# examples/complete/main.tf
module "vpc_test" {
  source = "../.."

  name       = "test-vpc"
  cidr_block = "10.100.0.0/16"

  private_subnets = {
    app = { cidr_block = "10.100.1.0/24", az = "us-east-1a" }
  }

  tags = {
    Environment = "test"
    ManagedBy   = "terraform"
  }
}

output "vpc_id" {
  value = module.vpc_test.vpc_id
}
```

## Module Best Practices

- Keep modules focused and single-purpose
- Use `for_each` over `count` for resources
- Validate all inputs with validation blocks
- Document all variables and outputs
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Provide complete examples
- Test modules before publishing
- Use consistent naming conventions
- Tag all taggable resources
- Avoid hardcoded values
