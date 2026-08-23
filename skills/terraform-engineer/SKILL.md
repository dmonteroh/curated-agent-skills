---
name: terraform-engineer
description: "Use when implementing infrastructure as code with Terraform across AWS, Azure, GCP, or OCI. Invoke for module development, state management, provider configuration, multi-environment workflows, infrastructure testing."
metadata:
  category: devops
---
# Terraform Engineer

## Use this skill when

- Building or updating Terraform modules and root configurations
- Setting up remote state, locking, and workspace strategies
- Configuring AWS, Azure, GCP, or OCI providers safely
- Refactoring existing IaC for reuse, security, or compliance
- Adding infrastructure testing or policy checks

## Do not use this skill when

- The task is not Terraform-based infrastructure as code
- The request is purely high-level cloud architecture with no IaC changes
- The repo uses a different IaC tool (e.g., Pulumi, CloudFormation) exclusively

## Required inputs

- Target cloud(s) and provider versions
- Environment list (dev/stage/prod) and naming conventions
- State backend requirements (location, encryption, locking)
- Security/compliance expectations (tagging, IAM, encryption)
- Module boundaries and expected inputs/outputs
- Verification expectations (plan-only, tests, policy checks)

## Workflow

1. Confirm scope and constraints.
   - Output: summarized assumptions and missing inputs.
   - Decision: if required inputs are missing, ask before coding.
2. Map module and root structure.
   - Output: module boundaries, inputs/outputs, and file layout.
   - Decision: if refactoring, document compatibility risks and migration steps.
3. Implement providers and versions.
   - Output: provider blocks, version constraints, and required providers.
   - Decision: if multiple clouds, separate providers with explicit aliases.
4. Configure state and environments.
   - Output: backend configuration, locking/encryption settings, workspace strategy.
   - Decision: if production, require remote state and locking; otherwise explain exceptions.
5. Build resources and module logic.
   - Output: Terraform code with variables, outputs, and validation blocks.
6. Add security and cost controls.
   - Output: tagging strategy, IAM least privilege notes, encryption settings.
7. Verify behavior.
   - Output: `terraform validate` exits 0; `terraform plan` shows no unexpected destroy/replace actions against the stated intent; any required policy or test commands (tflint, terraform test, terratest, OPA) pass, named explicitly, with failing output treated as a blocking failure, not a note.

## Examples

**Example request**
"Create a Terraform module for an AWS S3 bucket with versioning, encryption, and tags. Provide module inputs and a root usage example."

**Example response outline**
- Module files: `main.tf`, `variables.tf`, `outputs.tf`
- Variables: `bucket_name`, `tags`, `enable_versioning`
- State: backend configuration note for S3 + DynamoDB
- Usage: root module example with provider pinning

## Output contract

When this skill runs, report using these headings in order:

- Summary: what was built/changed and why
- Assumptions: defaults or constraints applied
- Files changed: Terraform files touched
- Deliverables: module structure, backend config, provider config, usage example
- Validation: commands run or suggested (plan, validate, tests)
- Follow-ups: missing inputs or recommended next steps

## References

Use `references/README.md` to load detailed guidance by topic.

## Constraints

### MUST DO
- Use semantic versioning for modules
- Enable remote state with locking
- Validate inputs with validation blocks
- Use consistent naming conventions
- Tag all resources for cost tracking
- Document module interfaces
- Pin provider versions
- Run terraform fmt and validate

### MUST NOT DO
- Store secrets in plain text
- Use local state for production
- Skip state locking
- Hardcode environment-specific values
- Mix provider versions without constraints
- Create circular module dependencies
- Commit .terraform directories
- Run `terraform apply`, `destroy`, or other state-mutating commands without explicit operator approval
