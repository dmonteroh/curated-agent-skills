# AWS Zone Failure Simulation

Provides a helper for simulating AZ failures in AWS.

## Prerequisites

- AWS credentials with `ec2`, `autoscaling`, and `elbv2` permissions.
- Network access to AWS APIs.

## Usage

1. Identify the target ASG and availability zone.
2. Suspend AZ rebalance if required for the experiment.
3. Terminate instances or deregister targets for the duration.

## Verification

- Confirm ASG launches replacements in other zones.
- Validate load balancer target health stabilizes after rollback.

```python
import boto3
from datetime import datetime, timedelta

class AWSChaosSimulator:
    def __init__(self, region: str):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.asg = boto3.client('autoscaling', region_name=region)
        self.elb = boto3.client('elbv2', region_name=region)

    def simulate_az_failure(
        self,
        availability_zone: str,
        asg_name: str,
        duration_minutes: int = 10
    ):
        instances = self.ec2.describe_instances(Filters=[
            {'Name': 'tag:aws:autoscaling:groupName', 'Values': [asg_name]},
            {'Name': 'availability-zone', 'Values': [availability_zone]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ])

        instance_ids = [
            i['InstanceId']
            for r in instances['Reservations']
            for i in r['Instances']
        ]

        if not instance_ids:
            return {"status": "no_instances", "instances": []}

        self.asg.suspend_processes(
            AutoScalingGroupName=asg_name,
            ScalingProcesses=['AZRebalance']
        )

        self.ec2.terminate_instances(InstanceIds=instance_ids)

        return {
            "status": "simulated",
            "availability_zone": availability_zone,
            "terminated_instances": instance_ids,
            "recovery_time": datetime.now() + timedelta(minutes=duration_minutes)
        }

    def drain_az_from_load_balancer(
        self,
        target_group_arn: str,
        availability_zone: str
    ):
        health = self.elb.describe_target_health(
            TargetGroupArn=target_group_arn
        )

        targets_to_deregister = []
        for target in health['TargetHealthDescriptions']:
            instance = self.ec2.describe_instances(
                InstanceIds=[target['Target']['Id']]
            )
            if instance['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone'] == availability_zone:
                targets_to_deregister.append(target['Target'])

        if targets_to_deregister:
            self.elb.deregister_targets(
                TargetGroupArn=target_group_arn,
                Targets=targets_to_deregister
            )

        return {
            "deregistered_targets": len(targets_to_deregister),
            "availability_zone": availability_zone
        }
```
