# Terraform Testing: `terraform test`

## Test File Structure

```
tests/
├── unit/
│   ├── vpc_test.tftest.hcl
│   └── security_group_test.tftest.hcl
└── integration/
    └── complete_test.tftest.hcl
```

## Basic Test

```hcl
run "validate_vpc_cidr" {
  command = plan

  variables {
    cidr_block = "10.0.0.0/16"
    name       = "test-vpc"
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR block did not match expected value"
  }

  assert {
    condition     = aws_vpc.main.enable_dns_hostnames == true
    error_message = "DNS hostnames should be enabled"
  }
}

run "validate_tags" {
  command = plan

  variables {
    cidr_block = "10.0.0.0/16"
    name       = "test-vpc"
    tags = {
      Environment = "test"
    }
  }

  assert {
    condition     = aws_vpc.main.tags["Environment"] == "test"
    error_message = "Environment tag not set correctly"
  }
}
```

## Integration Test

```hcl
run "create_full_stack" {
  command = apply

  variables {
    cidr_block = "10.0.0.0/16"
    name       = "integration-test"

    private_subnets = {
      app = { cidr_block = "10.0.1.0/24", az = "us-east-1a" }
    }
  }

  assert {
    condition     = length(aws_subnet.private) == 1
    error_message = "Should create exactly one private subnet"
  }

  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC ID should not be empty"
  }
}
```

## Run Tests

```bash
terraform test
terraform test tests/vpc_test.tftest.hcl
terraform test -verbose
terraform test -no-cleanup
```
