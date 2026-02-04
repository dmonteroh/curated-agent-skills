# Terraform Testing: Policy as Code

## Open Policy Agent (OPA)

```rego
package terraform.analysis

import input as tfplan

deny[msg] {
    r := tfplan.resource_changes[_]
    r.change.actions[_] == "create"
    not r.change.after.tags.Environment
    msg := sprintf("Resource %s is missing Environment tag", [r.address])
}

deny[msg] {
    r := tfplan.resource_changes[_]
    r.type == "aws_s3_bucket"
    r.change.actions[_] == "create"
    not r.change.after.server_side_encryption_configuration
    msg := sprintf("S3 bucket %s must have encryption enabled", [r.address])
}

deny[msg] {
    r := tfplan.resource_changes[_]
    r.type == "aws_vpc"
    r.change.actions[_] == "create"
    vpc_id := r.change.after.id
    not has_flow_log(vpc_id)
    msg := sprintf("VPC %s must have flow logs enabled", [r.address])
}

has_flow_log(vpc_id) {
    r := tfplan.resource_changes[_]
    r.type == "aws_flow_log"
    r.change.after.vpc_id == vpc_id
}
```

## Run OPA Policy

```bash
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json
opa eval -i tfplan.json -d policy.rego "data.terraform.analysis.deny"
```

## Conftest

```bash
conftest test tfplan.json
conftest test tfplan.json --namespace terraform.analysis
```

## Requirements

- `opa` and `conftest` available in the environment
