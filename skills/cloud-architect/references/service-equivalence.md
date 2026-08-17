# Cross-Provider Service Equivalence

A use-case-indexed map of managed services across providers. Use it in step 3 (platform pattern) and step 7 (data/state) when the provider is not yet fixed, when a design must stay portable, or when an option has to be compared across a named set of providers.

**Read every row as "solves the same problem", never as "behaves the same way."** Rows are equivalent by use case only. Consistency model, quota and limit shapes, regional availability, failover semantics, and pricing model diverge inside every row. Before treating two cells as interchangeable, verify the specific limits the design depends on against each provider's current documentation, and record any that do not match as a risk in the risk register.

Provenance: carried from a third-party multi-cloud skill drop and restated in this skill's terms. Service names change and services get renamed or retired, so treat this as a starting index for comparison, not a current catalog.

## Compute

| Use case | AWS | Azure | GCP | OCI |
| --- | --- | --- | --- | --- |
| IaaS VMs | EC2 | Virtual Machines | Compute Engine | Compute |
| Managed Kubernetes | EKS | AKS | GKE | OKE |
| Serverless functions | Lambda | Functions | Cloud Functions | Functions |
| Containers without cluster management | Fargate (ECS/EKS) | Container Apps / Container Instances | Cloud Run | Container Instances |

## Storage

| Use case | AWS | Azure | GCP | OCI |
| --- | --- | --- | --- | --- |
| Object storage | S3 | Blob Storage | Cloud Storage | Object Storage |
| Block storage | EBS | Managed Disks | Persistent Disk | Block Volumes |
| Shared file storage | EFS | Azure Files | Filestore | File Storage |
| Cold / archive tier | S3 Glacier tiers | Archive Storage | Archive Storage | Archive Storage |

## Database and cache

| Use case | AWS | Azure | GCP | OCI |
| --- | --- | --- | --- | --- |
| Managed relational (PostgreSQL/MySQL) | RDS | Azure Database for PostgreSQL/MySQL | Cloud SQL | MySQL HeatWave |
| Managed NoSQL (document / key-value) | DynamoDB | Cosmos DB | Firestore | NoSQL Database |
| Provider-native scale-out relational | Aurora | Azure SQL Database (Hyperscale) | Cloud Spanner | Autonomous Database |
| Managed cache | ElastiCache | Azure Cache for Redis | Memorystore | OCI Cache |

## Using the table without accruing lock-in debt

- Row-level equivalence does not make a design portable. Portability comes from the interface: containers over provider-specific runtimes, standard engines (PostgreSQL, MySQL, Redis, Kafka) over proprietary APIs, and an S3-compatible object API where storage must be able to move.
- The provider-native scale-out relational row is the least portable in the table — each entry has a distinct data model, consistency contract, and operational model. Picking one of these is a provider commitment; state it as such in the decision summary rather than filing it as a swappable choice.
- This table informs option comparison. It does not overturn `references/multi-cloud.md`, which still prefers one primary provider with others as edge or specialty unless a mandate says otherwise.
