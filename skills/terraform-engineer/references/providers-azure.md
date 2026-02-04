# Terraform Azure Provider Configuration

## Basic Configuration

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = true
    }

    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }

    virtual_machine {
      delete_os_disk_on_deletion     = true
      graceful_shutdown              = false
      skip_shutdown_and_force_delete = false
    }
  }

  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}
```

## Multiple Azure Subscriptions

```hcl
provider "azurerm" {
  alias           = "production"
  subscription_id = var.prod_subscription_id
  tenant_id       = var.tenant_id

  features {}
}

provider "azurerm" {
  alias           = "development"
  subscription_id = var.dev_subscription_id
  tenant_id       = var.tenant_id

  features {}
}

resource "azurerm_resource_group" "prod" {
  provider = azurerm.production
  name     = "prod-rg"
  location = "East US"
}
```

## Azure Authentication Methods

```hcl
# Method 1: Service Principal with Client Secret
provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.client_id
  client_secret   = var.client_secret
}

# Method 2: Service Principal with Certificate
provider "azurerm" {
  features {}

  subscription_id             = var.subscription_id
  tenant_id                   = var.tenant_id
  client_id                   = var.client_id
  client_certificate_path     = var.client_certificate_path
  client_certificate_password = var.client_certificate_password
}

# Method 3: Managed Identity (for Azure VMs)
provider "azurerm" {
  features {}

  use_msi         = true
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}

# Method 4: Azure CLI (local development)
provider "azurerm" {
  features {}

  use_cli = true
}
```
