# CI/CD Chaos Automation (GitHub Actions)

Provides a GitHub Actions workflow template for scheduled chaos runs.

## Prerequisites

- A staging cluster and kubeconfig access stored as CI secrets.
- Chaos manifests stored locally in the repository (avoid remote downloads).
- Optional: Slack webhook configured if notifications are required.

## Usage

1. Store chaos manifests under a repo path such as `.github/chaos/`.
2. Add the workflow to `.github/workflows/chaos-tests.yml`.
3. Define secrets for cloud credentials and any notification hooks.
4. Run manually via `workflow_dispatch` or allow the schedule to trigger.

## Verification

- Confirm the workflow completes and the chaos engine reaches `Complete`.
- Validate steady-state metrics stay within guardrails.
- Ensure cleanup steps delete chaos resources.

## Workflow Example

```yaml
name: Chaos Engineering Tests

on:
  schedule:
    - cron: '0 10 * * 1-5'
  workflow_dispatch:

jobs:
  chaos-tests:
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name staging-cluster --region us-east-1

      - name: Install Litmus
        run: |
          kubectl apply -f .github/chaos/litmus-operator.yaml
          kubectl wait --for=condition=Ready pods -l app.kubernetes.io/component=operator --timeout=300s

      - name: Run pod-delete chaos experiment
        run: |
          kubectl apply -f .github/chaos/pod-delete-experiment.yaml
          kubectl wait --for=condition=Complete chaosengine/pod-delete-chaos --timeout=600s

      - name: Verify system recovery
        run: |
          kubectl wait --for=condition=Ready pods -l app=myapp --timeout=300s

          ERROR_RATE=$(curl -s "http://prometheus/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])" | jq -r '.data.result[0].value[1]')

          if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
            echo "Error rate too high: $ERROR_RATE"
            exit 1
          fi

      - name: Cleanup chaos resources
        if: always()
        run: |
          kubectl delete chaosengine --all
          kubectl delete chaosexperiments --all

      - name: Report results to Slack
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Chaos test failed in staging",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "Chaos engineering test failed. System did not recover properly."
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```
