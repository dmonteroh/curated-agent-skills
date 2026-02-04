# Terraform Module Composition and Advanced Patterns

## Module Composition

```hcl
module "networking" {
  source = "./modules/vpc"

  name       = "production"
  cidr_block = "10.0.0.0/16"

  private_subnets = {
    app1 = { cidr_block = "10.0.1.0/24", az = "us-east-1a" }
    app2 = { cidr_block = "10.0.2.0/24", az = "us-east-1b" }
  }

  tags = local.common_tags
}

module "security" {
  source = "./modules/security-groups"

  vpc_id = module.networking.vpc_id

  security_groups = {
    web = {
      ingress = [
        { from_port = 443, to_port = 443, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] }
      ]
    }
  }
}
```

## Dynamic Blocks

```hcl
resource "aws_security_group" "this" {
  name   = var.name
  vpc_id = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  dynamic "egress" {
    for_each = var.egress_rules
    content {
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr_blocks
      description = egress.value.description
    }
  }
}
```

## Conditional Resources

```hcl
resource "aws_nat_gateway" "this" {
  count = var.enable_nat_gateway ? 1 : 0

  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.name}-nat"
  }

  depends_on = [aws_internet_gateway.this]
}

resource "aws_route53_zone" "private" {
  for_each = var.create_private_zone ? { main = var.domain_name } : {}

  name = each.value

  vpc {
    vpc_id = aws_vpc.this.id
  }
}
```
