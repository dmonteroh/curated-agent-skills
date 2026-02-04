---
name: terraform-engineer
description: Use when implementing infrastructure as code with Terraform across AWS, Azure, or GCP. Invoke for module development, state management, provider configuration, multi-environment workflows, infrastructure testing.
category: devops
triggers:
  - Terraform
  - infrastructure as code
  - IaC
  - terraform module
  - terraform state
  - AWS provider
  - Azure provider
  - GCP provider
  - terraform plan
  - terraform apply
role: specialist
scope: implementation
output-format: code
---

# Terraform Engineer

Deliver production-grade Terraform infrastructure code with modular design, secure state management, and multi-environment workflows.

## Use this skill when

- Building or updating Terraform modules and root configurations
- Setting up remote state, locking, and workspace strategies
- Configuring AWS, Azure, or GCP providers safely
- Refactoring existing IaC for reuse, security, or compliance
- Adding infrastructure testing or policy checks

## Do not use this skill when

- The task is not Terraform-based infrastructure as code
- The request is purely high-level cloud architecture with no IaC changes
- The repo uses a different IaC tool (e.g., Pulumi, CloudFormation) exclusively

## Trigger phrases

- "Terraform module" or "module interface"
- "remote state" or "state locking"
- "terraform plan" or "terraform apply"
- "AWS provider" or "AzureRM provider"
- "GCP provider" or "Google provider"

## Trigger test

- "Build a Terraform module for an S3 bucket with logging and tags."
- "Refactor this Terraform root module to use remote state and workspaces."

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
   - Output: planned commands or tests run with expected results.

## Common pitfalls to avoid

- Using local state for production environments
- Skipping input validation and relying on provider errors
- Hardcoding environment-specific values in modules
- Omitting provider version constraints or required providers
- Mixing aliases/providers without explicit mapping

## Examples

**Example request**
"Create a Terraform module for an AWS S3 bucket with versioning, encryption, and tags. Provide module inputs and a root usage example."

**Example response outline**
- Module files: `main.tf`, `variables.tf`, `outputs.tf`
- Variables: `bucket_name`, `tags`, `enable_versioning`
- State: backend configuration note for S3 + DynamoDB
- Usage: root module example with provider pinning

## Output contract

When this skill runs, report in this format:

- Summary: what was built/changed and why
- Assumptions: any defaults or constraints applied
- Files changed: list of Terraform files touched
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
- Skip input validation
- Commit .terraform directories

## Output Templates

When implementing Terraform solutions, provide:
1. Module structure (main.tf, variables.tf, outputs.tf)
2. Backend configuration for state
3. Provider configuration with versions
4. Example usage with tfvars
5. Brief explanation of design decisions

## Knowledge Reference

Terraform 1.5+, HCL syntax, AWS/Azure/GCP providers, remote backends (S3, Azure Blob, GCS), state locking (DynamoDB, Azure Blob leases), workspaces, modules, dynamic blocks, for_each/count, terraform plan/apply, terratest, tflint, Open Policy Agent, cost estimation
