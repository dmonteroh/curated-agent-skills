# Operator Panel Sets by System

Generic templates (`assets/api-dashboard.json`, `assets/infrastructure-dashboard.json`, `assets/database-dashboard.json`) cover request rate, error rate, latency, CPU, and memory - the signals every system has. They do not cover the signal that is specific to *this* system and is usually the one an experienced operator checks first. A Kafka operator looks at under-replicated partitions before CPU; an Elasticsearch operator looks at cluster colour and shard allocation before search latency.

Use this file at workflow step 3 (panel specs) when the dashboard target is one of the systems below: start from its panel set, then apply the normal gates. Each panel still has to answer one question the audience would act on - a panel inherited from this list that nobody on the target team acts on is a vanity panel and gets cut like any other.

Metric names below are indicative. Kafka and Elasticsearch signals reach Prometheus through an exporter (JMX exporter, kafka_exporter, elasticsearch_exporter, or a vendor agent) and each exposes its own names, so confirm the series against the live data source before writing queries. The panel and the question it answers are the durable part; the series name is not.

## Kafka

| Panel | Question it answers | Viz | Notes |
| --- | --- | --- | --- |
| Broker count vs expected | Is the cluster whole? | Stat | Compare live brokers against the configured cluster size. The absolute number means nothing on its own - the gap does. |
| Under-replicated partitions | Is durability at risk right now? | Stat + time series | The one panel where the threshold is not tuned: healthy is zero. Sustained non-zero means a replica cannot keep up or a broker is gone, and the cluster is one more failure from data loss. |
| Messages and bytes in / out | Is the workload what we think it is? | Time series | Split in from out. A produce rate that holds while consume rate drops is the leading edge of a lag problem, visible here before it shows up as lag. |
| Consumer lag by group | Are consumers keeping up? | Time series + table | Break out by consumer group and topic. Lag trending up with steady produce rate is a consumer problem; lag rising with a produce spike may be normal catch-up. This is the panel application teams act on; the rest are for the platform owner. |
| Disk and network pressure per broker | What runs out first? | Time series | Broker disk fills silently and takes the cluster down hard. Pair free-disk with retention settings, since retention is the lever that actually moves it. |

## Elasticsearch

| Panel | Question it answers | Viz | Notes |
| --- | --- | --- | --- |
| Cluster health status | Is data available, and is redundancy intact? | Stat with value mapping | Map the colour to its meaning rather than showing it raw: yellow means replicas are unassigned (data is served, redundancy is lost), red means primaries are unassigned (data is unavailable). Yellow and red are different pages, not different shades. |
| Shard allocation | Why is it not green, and is it recovering? | Time series | Track unassigned, initializing, and relocating shards separately. A falling unassigned count with active relocation is a recovery in progress and needs no intervention; a flat unassigned count is stuck and does. |
| Search latency | Are queries getting slower? | Time series | Separate query phase from fetch phase - they fail for different reasons. Exporters expose cumulative time and count counters, so the rate ratio is an average over the window: label it as one, and prefer percentiles where the source supports them (`references/dashboard-design.md`). |
| Indexing rate and rejections | Is write load being absorbed or shed? | Time series | Indexing rate alone looks healthy right up to saturation. Show bulk-queue rejections beside it - rejections are the point where ingest starts losing data. |
| JVM heap and GC | Is the node about to stall? | Time series | Raw heap usage sawtoothing to a high peak is normal. The signal is heap *after* old-generation GC staying high, plus GC pause time and frequency climbing. A heap-percentage panel without a GC panel next to it reads as an emergency during ordinary operation. |

## Deriving a set for a system not listed here

Three questions produce the system-specific section for anything else - a database, a queue, an object store, a cache:

1. What does its operator get paged for that is not latency, errors, or saturation? That failure mode is the system-specific panel, and it usually has a metric with a fixed healthy value (zero, or a count matching a configured size) rather than a tuned threshold.
2. What silently degrades durability or correctness without degrading the request path? Replication lag, unassigned replicas, split-brain, and quorum loss all keep serving traffic while the safety margin is already gone, so they never surface in a RED view.
3. What resource does this system exhaust first, and what is the lever that relieves it? Show the resource and the lever together - free disk beside retention, connections beside pool size - so the panel implies the action instead of only the alarm.

Thresholds are deliberately absent from the tables above: they belong to the specific cluster's capacity and traffic, not to the technology. Set them from the target's own observed range, with the one exception noted for under-replicated partitions, where any sustained non-zero value is the fault condition.
