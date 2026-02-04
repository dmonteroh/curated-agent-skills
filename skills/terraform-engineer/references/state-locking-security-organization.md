# Terraform State Locking, Security, and Organization

## State Locking

```bash
terraform force-unlock LOCK_ID
```

```hcl
# State locking happens automatically with supported backends
# DynamoDB for S3, automatic for Azure Blob and GCS

# Disable locking for specific operations (not recommended)
terraform apply -lock=false  # Avoid in production
```

## State File Security

```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform.arn
    }
    bucket_key_enabled = true
  }
}
```

```hcl
resource "aws_s3_bucket_policy" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "RequireEncryptedTransport"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}
```

## State File Organization

```
terraform-state-bucket/
├── production/
│   ├── vpc/terraform.tfstate
│   ├── eks/terraform.tfstate
│   └── rds/terraform.tfstate
├── staging/
│   ├── vpc/terraform.tfstate
│   └── eks/terraform.tfstate
└── dev/
    └── vpc/terraform.tfstate
```

## Best Practices

- Always use remote state for teams
- Enable state locking to prevent conflicts
- Encrypt state files at rest and in transit
- Enable versioning for state file history
- Use separate state files per environment
- Restrict access to state buckets
- Back up state files regularly
- Never commit state files to git
- Use workspaces for similar environments only
- Document state migration procedures
