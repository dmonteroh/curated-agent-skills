# Terraform Testing: Terratest

## Requirements

- Go toolchain available in the environment
- Terratest and testing libraries declared in `go.mod`

## Test Structure

```
tests/
├── go.mod
├── go.sum
└── vpc_test.go
```

## go.mod

```go
module github.com/example/terraform-modules/tests

go 1.21

require (
    github.com/gruntwork-io/terratest v0.45.0
    github.com/stretchr/testify v1.8.4
)
```

## Basic Terratest

```go
package test

import (
    "testing"

    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCCreation(t *testing.T) {
    t.Parallel()

    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/complete",
        Vars: map[string]interface{}{
            "name":       "test-vpc",
            "cidr_block": "10.0.0.0/16",
        },
        EnvVars: map[string]string{
            "AWS_DEFAULT_REGION": "us-east-1",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)

    vpcCIDR := terraform.Output(t, terraformOptions, "vpc_cidr_block")
    assert.Equal(t, "10.0.0.0/16", vpcCIDR)
}
```

## Advanced Terratest with AWS SDK

```go
package test

import (
    "testing"

    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/service/ec2"
    "github.com/gruntwork-io/terratest/modules/terraform"
    aws_helper "github.com/gruntwork-io/terratest/modules/aws"
    "github.com/stretchr/testify/assert"
)

func TestVPCConfiguration(t *testing.T) {
    t.Parallel()

    awsRegion := "us-east-1"

    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/complete",
        Vars: map[string]interface{}{
            "name":       "test-vpc",
            "cidr_block": "10.0.0.0/16",
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    vpc := aws_helper.GetVpcById(t, vpcID, awsRegion)

    assert.Equal(t, "10.0.0.0/16", *vpc.CidrBlock)
    assert.True(t, *vpc.EnableDnsSupport)
    assert.True(t, *vpc.EnableDnsHostnames)

    tags := convertEC2TagsToMap(vpc.Tags)
    assert.Equal(t, "test-vpc", tags["Name"])
}

func convertEC2TagsToMap(tags []*ec2.Tag) map[string]string {
    result := make(map[string]string)
    for _, tag := range tags {
        result[*tag.Key] = *tag.Value
    }
    return result
}
```

## Run Terratest

```bash
cd tests
go test -v -timeout 30m
```
