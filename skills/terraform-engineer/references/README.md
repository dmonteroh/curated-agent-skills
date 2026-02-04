# Terraform Engineer References

## Best Practices

- `best-practices-dry-naming.md`: DRY patterns, naming conventions, file layout.
- `best-practices-security.md`: Secrets, encryption, IAM, and network security.
- `best-practices-tagging.md`: Tagging strategy and provider defaults.
- `best-practices-cost-optimization.md`: Sizing, lifecycle, and scheduling.
- `best-practices-organization.md`: Directory structure and module hygiene.
- `best-practices-checklist.md`: Implementation checklist.

## Modules

- `module-structure-basics.md`: Module structure, inputs/outputs, and versions.
- `module-composition-advanced.md`: Composition, dynamic blocks, conditionals.
- `module-versioning-testing.md`: Module versioning and test examples.

## Providers

- `providers-aws.md`: AWS provider configuration, auth, and aliases.
- `providers-azure.md`: Azure provider configuration and auth.
- `providers-gcp.md`: GCP provider configuration and auth.
- `providers-kubernetes-helm.md`: Kubernetes and Helm providers.
- `providers-versioning-best-practices.md`: Provider version constraints and guidance.

## State Management

- `state-backends-aws.md`: S3 backend config and DynamoDB locking.
- `state-backends-azure-gcp.md`: Azure Blob and GCS backends.
- `state-workspaces-operations.md`: Workspaces, backend configs, state ops.
- `state-locking-security-organization.md`: Locking, security, and organization.

## Testing

- `testing-plan-validation.md`: Plan, validate, and plan analysis.
- `testing-terraform-test.md`: `terraform test` examples.
- `testing-terratest.md`: Terratest setup and usage.
- `testing-policy-as-code.md`: OPA and Conftest policy checks.
- `testing-tflint.md`: TFLint configuration and usage.
- `testing-pre-commit-ci.md`: Pre-commit hooks and CI pipeline example.
