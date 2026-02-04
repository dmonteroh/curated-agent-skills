# Release Artifact Management

## Container Registry Lifecycle

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 prod images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["prod-"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {"type": "expire"}
    },
    {
      "rulePriority": 2,
      "description": "Remove untagged after 7 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": {"type": "expire"}
    }
  ]
}
```

Verification: confirm older tags are pruned and production tags remain intact.

## Artifact Promotion Workflow

Requirements: `docker`, `git`, and `yq` installed. Ensure registry credentials are configured.

```yaml
# .github/workflows/promote.yml
name: Artifact Promotion

on:
  workflow_dispatch:
    inputs:
      image_tag:
        required: true
      target_env:
        type: choice
        options: [staging, production]

jobs:
  promote:
    runs-on: ubuntu-latest
    steps:
      - name: Re-tag for environment
        run: |
          docker pull $REGISTRY/$IMAGE:${{ inputs.image_tag }}
          docker tag $REGISTRY/$IMAGE:${{ inputs.image_tag }} \
            $REGISTRY/$IMAGE:${{ inputs.target_env }}-latest
          docker push $REGISTRY/$IMAGE:${{ inputs.target_env }}-latest

      - name: Sign artifact
        uses: sigstore/cosign-installer@v3
      - run: cosign sign $REGISTRY/$IMAGE:${{ inputs.target_env }}-latest

      - name: Update GitOps
        run: |
          cd gitops/apps/${{ inputs.target_env }}
          yq e '.image.tag = "${{ inputs.image_tag }}"' -i values.yaml
          git commit -am "Promote to ${{ inputs.target_env }}"
          git push
```

Verification: confirm the GitOps repository references the promoted tag.

## Advanced Artifact Scanning

Requirements: `trivy`, `syft`, `jq`, and `cosign` available in the runner.

```bash
#!/bin/bash
# artifact-scanner.sh - Scan before promotion

IMAGE=$1
SEVERITY=${2:-HIGH}

# Vulnerability scan
trivy image --severity $SEVERITY --exit-code 1 $IMAGE

# License compliance
syft $IMAGE -o json | \
  jq '.artifacts[].licenses[] | select(.value |
    contains("GPL") or contains("AGPL"))' && \
  echo "License violation detected" && exit 1

# SBOM generation
syft $IMAGE -o spdx-json > sbom-$(basename $IMAGE).spdx.json

# Sign artifact
cosign sign --key cosign.key $IMAGE

# Promote
docker tag $IMAGE $IMAGE-approved
docker push $IMAGE-approved

echo "Artifact $IMAGE approved and promoted"
```

Usage: `./artifact-scanner.sh registry.io/app:1.2.3 CRITICAL`

Verification: confirm the SBOM is created and the signed tag exists in the registry.
