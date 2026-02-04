# Terraform Testing: TFLint

## Configuration

```hcl
plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "aws" {
  enabled = true
  version = "0.27.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

rule "terraform_required_version" {
  enabled = true
}

rule "terraform_required_providers" {
  enabled = true
}

rule "aws_instance_invalid_type" {
  enabled = true
}

rule "aws_s3_bucket_encryption" {
  enabled = true
}
```

## Run TFLint

```bash
tflint
tflint --config=.tflint.hcl
tflint --recursive
tflint --format=json
```

## Requirements

- `tflint` and required ruleset plugins available in the environment
