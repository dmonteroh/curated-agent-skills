# Release Orchestration and Migrations

## Coordinated Release Script

Requirements: `gh`, `git`, `kubectl`, and access to service repositories.

```bash
#!/bin/bash
# release.sh - Multi-service coordinated release

VERSION=$1
SERVICES=(auth api worker frontend)

echo "Release: $VERSION"

# Create release branches
for svc in "${SERVICES[@]}"; do
    gh api repos/org/$svc/git/refs -f ref=refs/heads/release/$VERSION -f sha=$(git rev-parse main)
done

# Trigger builds
for svc in "${SERVICES[@]}"; do
    gh workflow run ci.yml --repo org/$svc --ref release/$VERSION
done

# Wait for completion
for svc in "${SERVICES[@]}"; do
    gh run watch --repo org/$svc $(gh run list --repo org/$svc -L1 -q '.[0].databaseId')
done

# Deploy to staging
kubectl apply -f staging/release-$VERSION.yaml

# Smoke tests
./scripts/smoke-test.sh staging

echo "Release $VERSION ready for production"
```

Usage: `./release.sh 2.5.0`

Verification: confirm all builds complete and staging health checks pass.

## Release Coordinator Job

```yaml
# release-coordinator.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: release-v2.5.0
spec:
  template:
    spec:
      containers:
        - name: coordinator
          image: release-bot:latest
          env:
            - name: RELEASE_VERSION
              value: "2.5.0"
          command:
            - /bin/sh
            - -c
            - |
              for svc in auth api worker frontend; do
                echo "Deploying $svc..."
                kubectl set image deploy/$svc \
                  $svc=registry.io/$svc:$RELEASE_VERSION

                kubectl rollout status deploy/$svc --timeout=5m

                kubectl run test-$svc --rm -i --restart=Never \
                  --image=curlimages/curl -- \
                  curl -f http://$svc/health

                echo "$svc deployed successfully"
              done
```

Verification: ensure each deployment reports healthy before moving to the next.

## Zero-Downtime Database Migrations

```python
# migrations/release_v2_5.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users',
      sa.Column('email_verified', sa.Boolean(), nullable=True))

    connection = op.get_bind()
    connection.execute("""
      UPDATE users SET email_verified = true
      WHERE email IS NOT NULL
      LIMIT 1000
    """)

def downgrade():
    op.drop_column('users', 'email_verified')
```

Verification: confirm migrations are backward compatible and production load is stable.

## Dependency Management

```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "matchDepTypes": ["devDependencies"],
      "automerge": true
    }
  ],
  "schedule": ["before 6am on Monday"],
  "prConcurrentLimit": 5
}
```

Verification: review dependency PR cadence and confirm automerge policies apply.
