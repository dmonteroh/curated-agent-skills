# Platform Principles and Self-Service

## Platform Principles

- **Self-service first**: minimize manual work through automation
- **Golden paths**: pre-approved, opinionated templates
- **Developer experience**: measure and optimize productivity
- **Platform as product**: treat with a product mindset

## Self-Service with Crossplane

Requirements: Crossplane installed and configured with provider credentials.

```yaml
# Composition for self-service database
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: postgres-database
spec:
  compositeTypeRef:
    apiVersion: platform.example.com/v1alpha1
    kind: Database
  resources:
    - name: rds-instance
      base:
        apiVersion: rds.aws.crossplane.io/v1alpha1
        kind: DBInstance
        spec:
          forProvider:
            dbInstanceClass: db.t3.micro
            engine: postgres
            engineVersion: "15"
            masterUsername: admin
            allocatedStorage: 20
```

Verification: provision a test database and validate readiness and credentials.

## Terraform Self-Service Module

Requirements: Terraform modules available in the repository and a configured backend.

```hcl
# modules/service/main.tf
variable "service_name" {}
variable "environment" {}

module "k8s_service" {
  source   = "./k8s-deployment"
  name     = var.service_name
  env      = var.environment
}

module "database" {
  source = "./postgres"
  name   = "${var.service_name}-db"
}

module "monitoring" {
  source  = "./monitoring-stack"
  service = var.service_name
}

output "service_url" {
  value = module.k8s_service.url
}
```

Verification: run `terraform plan` and confirm module outputs align with desired state.
