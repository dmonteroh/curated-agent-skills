# Game Day Planning Template

Provides a planning template for game day logistics and objectives.

## Usage

1. Populate the metadata (date, time, environment).
2. Define objectives, participants, and scenarios.
3. Review rollback triggers with on-call owners.

## Verification

- Confirm participants are available for the scheduled window.
- Validate rollback commands are tested in the target environment.

```yaml
game_day:
  name: "Database Failover Drill"
  date: "YYYY-MM-DD"
  time: "HH:MM-HH:MM TZ"
  environment: "staging"

  objectives:
    - "Verify RDS failover to standby in under 2 minutes"
    - "Validate application auto-reconnect logic"
    - "Test monitoring and alerting effectiveness"
    - "Practice incident response procedures"

  participants:
    facilitator: "chaos-engineer@company.com"
    observers:
      - "sre-team@company.com"
      - "dev-team@company.com"
    responders:
      - "on-call-engineer@company.com"
      - "database-admin@company.com"
    stakeholders:
      - "engineering-manager@company.com"

  scenarios:
    - name: "Primary database instance failure"
      duration_minutes: 30
      steps:
        - action: "Force RDS instance reboot with failover"
          expected: "Failover to standby in <2 min"
          success_criteria:
            - "Downtime < 2 minutes"
            - "No data loss"
            - "Alerts fired correctly"

    - name: "Network partition to database"
      duration_minutes: 20
      steps:
        - action: "Block network traffic to RDS security group"
          expected: "Application switches to read replica"
          success_criteria:
            - "Read-only mode activated"
            - "User-facing error messages clear"

  communication_plan:
    announcement_channel: "#game-day-announcements"
    war_room: "Video call link"
    status_updates_every: "5 minutes"
    escalation_contacts:
      - name: "VP Engineering"
        phone: "+1-555-0100"
        threshold: "downtime > 5 minutes"

  rollback_plan:
    automatic_rollback_triggers:
      - "production traffic affected"
      - "customer complaints received"
      - "error_rate > 10%"
    manual_rollback_command: "aws rds reboot-db-instance --db-instance-identifier primary --force-failover"
    rollback_time_limit_seconds: 60

  success_metrics:
    - metric: "RTO (Recovery Time Objective)"
      target: "< 2 minutes"
      measurement: "time between failure and full recovery"
    - metric: "Alert accuracy"
      target: "100%"
      measurement: "all expected alerts fired"
    - metric: "Team response time"
      target: "< 5 minutes"
      measurement: "time to acknowledge incident"

  post_mortem:
    scheduled_for: "YYYY-MM-DD HH:MM TZ"
    template: "game-day-retro.md"
    required_attendees: "all participants"
```
