# Terraform OCI Provider and Module Components

Oracle Cloud Infrastructure coverage, in the same shape as the AWS/Azure/GCP provider references: how the provider is pinned and scoped, then what a complete module for each common OCI service contains.

Provenance: the module component checklists and module conventions are carried from a third-party Terraform module-library skill drop. The provider block below is *(authored)* scaffolding to match the shape of the sibling provider references, not source material.

## Provider Configuration

```hcl
terraform {
  required_providers {
    oci = {
      source = "oracle/oci"
      # Pin with a pessimistic constraint on the major version the project is on.
      # Read the current version from the registry; do not copy a pin out of a document.
      version = "~> <major>.0"
    }
  }
}

provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  region       = var.region
}
```

- Pin the OCI provider with a pessimistic (`~>`) constraint, as `references/providers-versioning-best-practices.md` requires of every provider. The version above is deliberately a placeholder: the source this checklist came from pinned a specific minor version as if it were current fact, and OCI ships provider releases frequently enough that any pin written into a reference is stale on arrival.
- Model compartments explicitly. A compartment OCID is a module input in the same class as a subnet ID or a resource group name — never derived inside the module, never defaulted to the tenancy root.
- Expose OCIDs (compartment, VCN, subnet, NSG) as module outputs. Composition in OCI is OCID passing, and a module that hides its OCIDs cannot be composed with the next one.
- For multiple tenancies or regions, use provider aliases with explicit mapping, exactly as in `references/providers-aws.md`.

## VCN Module

- VCN with public and private subnets
- Dynamic Routing Gateway (DRG) attachment for hybrid or cross-VCN connectivity
- Internet Gateway, NAT Gateway, and Service Gateway
- Route tables plus security lists and/or network security groups (NSGs)
- VCN Flow Logs

## OKE Module

- Cluster and node pools as separately versioned inputs, so a node-pool change does not force a cluster replacement
- IAM policies and dynamic groups for node and workload identity
- VCN-native pod networking
- Cluster autoscaling and observability hooks
- OCIR (container registry) integration

## Autonomous Database Module

- Database provisioning with workload type as an input
- Network access controls and private endpoints
- Wallet and secret handling — the wallet is a credential, so route it to a secret store; never emit it as a plaintext output or commit it to the repo
- Backup and maintenance preferences
- Tagging for cost tracking

## Object Storage Module

- Buckets with lifecycle rules
- Versioning and retention
- Customer-managed encryption keys
- Replication policies
- Event rules and service connectors

## Load Balancer Module

- Public or private placement as an input
- Backend sets and listeners
- TLS certificates
- Health checks
- Logging and metrics integration

## OCI Module Conventions

- Prefer NSGs over broad security list rules where practical. NSGs attach to resources and security lists attach to subnets; mixing both makes effective access hard to reason about and hard to review.
- Tag every resource with owner, environment, and cost center — the tagging contract in `references/best-practices-tagging.md`, applied through OCI defined and freeform tags.
- Use dynamic groups with least-privilege IAM policies for workload access, rather than static credentials handed to the workload.
- Keep network, identity, and data modules loosely coupled, composed through OCID inputs and outputs rather than shared state or hardcoded references.
- Enable logging, metrics, and backup settings by default. Disabling them should require an explicit input, not merely the absence of one.
