# Labs 16-18 – Distributed Query Processing

## Overview

This section covers distributed MongoDB clusters, consistency models,
ACID transactions, sharding strategies, and distributed aggregation pipelines.

## Lab Summary

| Lab | Topic | Key Tools |
|-----|-------|-----------|
| [Lab 16](lab16/) | Distributed Query Processing | MongoDB Replica Set, pymongo, index benchmarking |
| [Lab 17](lab17/) | Consistency Models & Transactions | CAP theorem, write/read concerns, ACID sessions |
| [Lab 18](lab18/) | Distributed Database Systems | Sharding simulation, aggregation pipelines, map-reduce |

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start MongoDB

**Standalone** (sufficient for Lab 16 Ex.3, Lab 17, and Lab 18):
```bash
mongod --dbpath ./data/standalone
```

**Replica set** (required for Lab 16 Ex.1 & Ex.2, and full Lab 17 demos):
```bash
# Create data dirs
mkdir -p ./data/rs1 ./data/rs2 ./data/rs3

# Terminal 1 / 2 / 3 (one per node)
mongod --replSet rs0 --port 27017 --dbpath ./data/rs1 --bind_ip localhost
mongod --replSet rs0 --port 27018 --dbpath ./data/rs2 --bind_ip localhost
mongod --replSet rs0 --port 27019 --dbpath ./data/rs3 --bind_ip localhost

# Initiate
mongosh --port 27017 --eval '
  rs.initiate({_id:"rs0",members:[
    {_id:0,host:"localhost:27017"},
    {_id:1,host:"localhost:27018"},
    {_id:2,host:"localhost:27019"}]})'
```

Or use the helper script:
```bash
bash lab16/lab16_mongodb_cluster.sh --start-all
```

### 3. Run labs in order

```bash
# Lab 16
cd lab16
python lab16_replication_test.py      # needs replica set
python lab16_query_optimization.py   # standalone OK

# Lab 17
cd ../lab17
python lab17_consistency_models.py
python lab17_transactions.py

# Lab 18
cd ../lab18
python lab18_sharding_simulation.py
python lab18_distributed_aggregation.py
```

## Generated Files

| File | Created by | Description |
|------|-----------|-------------|
| `lab16/query_performance_comparison.png` | Lab 16 Ex.3 | Index vs no-index timing bar chart |
| `lab18/sharding_comparison.png` | Lab 18 Ex.1 | Doc distribution for each shard strategy |
| `lab18/aggregation_dashboard.png` | Lab 18 Ex.2 | Revenue by region, category, and month |

## Key Concepts

### Replica Set
A group of mongod instances that maintain the same dataset.
One is elected **primary**; the rest are **secondaries** that replicate
the primary's oplog. If the primary fails, the secondaries hold an election.

### Consistency Spectrum
```
Strong ←────────────────────────────────────→ Eventual
  w=majority       w=1          w=0
  primary read     primary      nearest read
  (slow, safe)                  (fast, may be stale)
```

### Sharding
Horizontal partitioning — data is split across independent shards
so reads and writes scale linearly with the number of shards.

| Strategy | Targeted queries | Balanced writes |
|----------|-----------------|-----------------|
| Range    | Yes (range)     | Only if key is uniform |
| Hash     | Point only      | Yes |
| Zone     | Yes (by tag)    | Depends on zone sizes |

### ACID Transactions
MongoDB 4.x+ supports multi-document, multi-collection transactions
on replica sets. `session.with_transaction()` automatically retries
on transient errors and rolls back on application errors.
