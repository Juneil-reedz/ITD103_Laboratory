# Lab 18 – Distributed Database Systems

## Overview
Simulate horizontal scaling strategies (range, hash, and zone sharding)
and build optimised distributed aggregation pipelines including
map-reduce patterns and time-series analysis.

## Exercises

| Exercise | File | Description |
|----------|------|-------------|
| 1 | `lab18_sharding_simulation.py` | Range / hash / zone sharding strategies |
| 2 | `lab18_distributed_aggregation.py` | Revenue, category, trend & map-reduce aggregations |

## Prerequisites

```bash
pip install -r ../requirements.txt
```

Both scripts connect to a **standalone** mongod on port 27017.

## Run Order

```bash
python lab18_sharding_simulation.py
python lab18_distributed_aggregation.py
```

## Expected Output

### Exercise 1 – Sharding Simulation
```
=== A. Range Sharding (by customer_id) ===
  Shard distribution (range sharding):
    Shard 0:   3000 docs  ██████
    Shard 1:   3000 docs  ██████
    Shard 2:   3000 docs  ██████
    Total :    9000 docs
    Imbalance: 0.0%  (0% = perfectly balanced)

  Range query: customer_id 3 000 – 5 999 (should hit Shard 1 only)
    Found 5 docs in 0.5 ms (targeted shard)

=== B. Hash Sharding (uniform distribution) ===
  Shard distribution (hash sharding):
    Shard 0:   2998 docs  ██████
    Shard 1:   3004 docs  ██████
    Shard 2:   2998 docs  ██████
    Imbalance: 0.2%

  Range query customer_id 1 000 – 2 000 requires broadcast across ALL shards:
    Total found: 1001 in 12.3 ms (scatter-gather)

=== C. Zone Sharding (by geographic region) ===
  Zone map: {'North': 0, 'South': 1, 'East': 2, 'West': 2}
  Shard distribution (zone sharding):
    Shard 0:   2250 docs  ████
    Shard 1:   2250 docs  ████
    Shard 2:   4500 docs  █████████
    Imbalance: 33.3%
```

### Exercise 2 – Aggregation
```
=== A. Revenue by Region ===
  Region       Revenue         Orders  Avg Order
  North      $3,412,580.50     3125   $1,092.03
  South      $3,398,220.75     3150   $1,078.80
  ...

=== D. Map-Reduce Pattern ===
  Map-reduce completed in 85.2 ms
  Results written to 'region_summary' collection:
    North       revenue=$3,412,580.50  orders=3125
    ...
```

## Generated Files

| File | Description |
|------|-------------|
| `sharding_comparison.png` | Doc distribution per shard for each strategy |
| `aggregation_dashboard.png` | Revenue by region, category, and monthly trend |

## Key Concepts

### Sharding Strategies

| Strategy | Shard key | Targeted reads | Write distribution | Best for |
|----------|-----------|---------------|--------------------|----------|
| Range | Numeric/date range | Yes (range queries) | Uneven if hotspot | Sequential IDs, time-series |
| Hash | MD5(key) | Point lookups only | Uniform | Random access patterns |
| Zone | Tag/region | Yes (zone queries) | Uneven by design | Geographic data locality |

### Aggregation Pipeline Stages

| Stage | Purpose |
|-------|---------|
| `$match` | Filter documents early (uses indexes) |
| `$group` | Reduce documents to aggregated values |
| `$lookup` | Distributed join between collections |
| `$unwind` | Flatten array fields from `$lookup` |
| `$sort` | Order results (can use index if early in pipeline) |
| `$merge` | Write aggregation output to a collection (map-reduce pattern) |

### Horizontal Scaling Patterns

```
Write path (sharded cluster):
  Application → mongos router
                     ├→ Shard A (owns key range 0–N)
                     ├→ Shard B (owns key range N–2N)
                     └→ Shard C (owns key range 2N–3N)

Read path (targeted):
  Query with shard key → mongos routes to exactly ONE shard

Read path (scatter-gather):
  Query without shard key → mongos broadcasts to ALL shards,
  merges and returns results
```

### Aggregation Optimisation Rules
1. Place `$match` as early as possible to reduce working set.
2. Use covering indexes: all fields referenced in `$match` and `$group` in one index.
3. Avoid `$lookup` on large collections — pre-join or embed when access patterns allow.
4. Use `$merge` to materialise expensive aggregations into summary collections.
5. For time-series, partition by `$year`/`$month` to limit scanned documents.
