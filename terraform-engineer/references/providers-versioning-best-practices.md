# Terraform Provider Versioning and Best Practices

## Provider Version Constraints

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # >= 5.0.0, < 6.0.0
    }

    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0.0, < 4.0.0"
    }

    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }

    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}
```

## Best Practices

- Always pin provider versions with constraints
- Use provider aliases for multi-region/account setups
- Leverage default tags for consistent resource tagging
- Use environment variables for credentials in CI/CD
- Prefer IAM roles and managed identities
- Never hardcode credentials in code
- Use separate providers for different environments
- Document provider requirements in README
- Test provider upgrades in non-production first
- Use official providers from the HashiCorp registry
