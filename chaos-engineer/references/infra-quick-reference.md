# Infrastructure Chaos Quick Reference

| Failure Type | Tool | Command/Method |
|--------------|------|----------------|
| Network latency | toxiproxy | `add_latency(proxy, ms)` |
| Packet loss | toxiproxy/pumba | `loss --percent 20` |
| AZ failure | AWS API | `simulate_az_failure(az, asg)` |
| CPU stress | stress-ng | `--cpu N --cpu-load 80` |
| Memory exhaustion | stress-ng | `--vm 1 --vm-bytes XG` |
| Container kill | pumba | `kill --signal SIGKILL` |
| DNS failure | /etc/hosts | Block domain resolution |
| Cert expiry | cryptography | Generate expired cert |
