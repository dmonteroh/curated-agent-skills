# Chaos Monkey Configuration

Provides configuration and a minimal termination script for Chaos Monkey-style instance termination.

## Prerequisites

- Instance termination is allowed in the target environment.
- AWS credentials with permission to describe ASGs and terminate instances.
- If using Spinnaker, Chaos Monkey is enabled for the application.

## Usage

1. Apply the JSON configuration to the Chaos Monkey service or Spinnaker configuration store.
2. Use the script example only in isolated environments with a kill switch.
3. Log all terminations to an experiment report and halt if guardrails breach.

## Verification

- Confirm the configured schedule and target clusters are visible in the Chaos Monkey UI or API.
- Validate that terminated instances are replaced by ASG and steady-state signals recover.

## Spinnaker Configuration Example

```json
{
  "enabled": true,
  "schedule": {
    "enabled": true,
    "frequency": 1,
    "frequencyUnit": "DAYS",
    "start": "09:00",
    "end": "15:00",
    "timezone": "America/Los_Angeles"
  },
  "grouping": "cluster",
  "regionsAreIndependent": true,
  "exceptions": [
    {
      "type": "Opt-In",
      "account": "production",
      "stack": "*",
      "detail": "*"
    }
  ],
  "minTimeBetweenKillsInWorkDays": 2,
  "maxAppsPerDay": 5,
  "clusters": [
    {
      "app": "myapp",
      "stack": "production",
      "enabled": true,
      "regions": ["us-east-1", "us-west-2"],
      "meanTimeBetweenKillsInWorkDays": 2,
      "minTimeBetweenKillsInWorkDays": 1,
      "maxTerminationsPerDay": 1
    }
  ]
}
```

## Minimal Termination Script Example

```bash
#!/bin/bash

INSTANCE_COUNT=5
KILL_PERCENTAGE=20

INSTANCES=$(aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names my-asg \
  --query 'AutoScalingGroups[0].Instances[?LifecycleState==`InService`].InstanceId' \
  --output text)

TOTAL=$(echo "$INSTANCES" | wc -w)
TO_KILL=$(( TOTAL * KILL_PERCENTAGE / 100 ))

if [ $TO_KILL -eq 0 ]; then
  TO_KILL=1
fi

echo "$INSTANCES" | tr ' ' '\n' | shuf | head -n $TO_KILL | while read instance; do
  echo "Terminating instance: $instance"
  aws ec2 terminate-instances --instance-ids "$instance"
  sleep 30
done
```
