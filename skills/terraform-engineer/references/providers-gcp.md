# Terraform GCP Provider Configuration

## Basic Configuration

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone

  default_labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}
```

## Multiple GCP Projects

```hcl
provider "google" {
  alias   = "production"
  project = var.prod_project_id
  region  = "us-central1"
}

provider "google" {
  alias   = "development"
  project = var.dev_project_id
  region  = "us-central1"
}

resource "google_compute_network" "prod" {
  provider = google.production
  name     = "prod-vpc"
}
```

## GCP Authentication Methods

```hcl
# Method 1: Service Account Key (not recommended for production)
provider "google" {
  credentials = file("service-account-key.json")
  project     = var.project_id
  region      = var.region
}

# Method 2: Application Default Credentials (recommended)
provider "google" {
  # Uses GOOGLE_APPLICATION_CREDENTIALS env var
  project = var.project_id
  region  = var.region
}

# Method 3: Impersonate Service Account
provider "google" {
  project = var.project_id
  region  = var.region

  impersonate_service_account = "terraform@project-id.iam.gserviceaccount.com"
  scopes = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email"
  ]
}

# Method 4: Workload Identity (for GKE)
provider "google" {
  project = var.project_id
  region  = var.region
  # Automatically uses workload identity
}
```

## GCP Beta Resources

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

resource "google_compute_security_policy" "policy" {
  provider = google-beta
  name     = "my-policy"
}
```
