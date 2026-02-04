# Terraform Best Practices: Cost Optimization

## Cost-Aware Resource Sizing

```hcl
variable "environment" {
  type = string
}

locals {
  instance_type = {
    production  = "t3.large"
    staging     = "t3.medium"
    development = "t3.micro"
  }

  rds_instance_class = {
    production  = "db.r5.xlarge"
    staging     = "db.t3.medium"
    development = "db.t3.micro"
  }

  enable_multi_az = var.environment == "production" ? true : false
}

resource "aws_instance" "app" {
  instance_type = local.instance_type[var.environment]
}

resource "aws_db_instance" "main" {
  instance_class = local.rds_instance_class[var.environment]
  multi_az       = local.enable_multi_az
}
```

## Lifecycle Management

```hcl
resource "aws_instance" "app" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = var.environment == "production"
    ignore_changes        = [ami, user_data]
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
```

## Resource Scheduling

```hcl
resource "aws_autoscaling_schedule" "scale_down_evening" {
  scheduled_action_name  = "scale-down-evening"
  min_size               = 1
  max_size               = 1
  desired_capacity       = 1
  recurrence             = "0 20 * * MON-FRI"
  autoscaling_group_name = aws_autoscaling_group.app.name
}

resource "aws_autoscaling_schedule" "scale_up_morning" {
  scheduled_action_name  = "scale-up-morning"
  min_size               = 3
  max_size               = 10
  desired_capacity       = 3
  recurrence             = "0 7 * * MON-FRI"
  autoscaling_group_name = aws_autoscaling_group.app.name
}
```
