# Platform Templates and GitOps

## Backstage Service Template

```yaml
# templates/microservice/template.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: microservice-template
  title: Microservice Golden Path
spec:
  owner: platform-team
  type: service
  parameters:
    - title: Service Info
      properties:
        name:
          type: string
        owner:
          type: string
          ui:field: OwnerPicker
        language:
          type: string
          enum: [go, python, nodejs, java]
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
    - id: publish
      action: publish:github
      input:
        repoUrl: github.com?owner=org&repo=${{ parameters.name }}
    - id: register
      action: catalog:register
```

## Service Catalog Info

```yaml
# catalog-info.yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payment-service
  annotations:
    github.com/project-slug: org/payment-service
    pagerduty.com/integration-key: abc123
    grafana/dashboard-selector: service=payment
spec:
  type: service
  lifecycle: production
  owner: payments-team
  system: checkout
  dependsOn:
    - resource:default/payment-db
    - component:default/auth-service
  providesApis:
    - payment-api
```

## Golden Path Scaffolding Script

Requirements: `gh`, `git`, and access to the template repository.

```bash
#!/bin/bash
# create-service.sh - Golden path for new services

SERVICE=$1
LANG=$2

# Create from template
gh repo create "org/$SERVICE" --template "org/template-$LANG"
git clone "git@github.com:org/$SERVICE.git"
cd "$SERVICE"

# Setup CI/CD
cat > .github/workflows/ci.yml <<EOF
name: CI/CD
on: [push]
jobs:
  pipeline:
    uses: org/workflows/.github/workflows/standard.yml@v1
    with:
      service_name: $SERVICE
EOF

# Create infrastructure
cat > terraform/main.tf <<EOF
module "service" {
  source = "git::https://github.com/org/terraform//service"
  name   = "$SERVICE"
}
EOF

git add . && git commit -m "Golden path init" && git push

echo "Service created. Merge to main to deploy."
```

Usage: `./create-service.sh payments-service go`

Verification: confirm repo creation, CI workflow presence, and initial Terraform config.

## GitOps Repository Structure

```
gitops/
├── apps/
│   ├── production/
│   │   ├── payment-service/
│   │   └── auth-service/
│   └── staging/
│       └── payment-service/
├── infrastructure/
│   ├── clusters/
│   │   ├── prod-us-east/
│   │   └── prod-eu-west/
│   └── base/
│       ├── ingress/
│       └── monitoring/
└── platform/
    ├── backstage/
    ├── argocd/
    └── vault/
```

## ArgoCD Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payment-service
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops
    path: apps/production/payment-service
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    retry:
      limit: 5
      backoff:
        duration: 5s
        maxDuration: 3m
```

Verification: ensure the application reports `Synced` and `Healthy` in ArgoCD.
