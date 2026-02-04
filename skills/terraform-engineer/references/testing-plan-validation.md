# Terraform Testing: Plan and Validation

## Basic Plan Workflow

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform show -json tfplan | jq .
terraform apply tfplan
```

## Plan with Variable Files

```bash
terraform plan -var-file="production.tfvars"
terraform plan -var="instance_count=5"
terraform plan \
  -var-file="common.tfvars" \
  -var-file="production.tfvars"
```

## Plan Analysis

```bash
terraform plan -target=aws_vpc.main
terraform plan -refresh-only
terraform plan -destroy
terraform plan -out=tfplan 2>&1 | tee plan-output.txt
```
