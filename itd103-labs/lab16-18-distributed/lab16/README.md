# Lab 16 – Distributed Query Processing

## Overview
Set up a MongoDB Replica Set, test replication and failover behaviour,
and benchmark query performance with and without indexes.

## Exercises

| Exercise | File | Description |
|----------|------|-------------|
| 1 | `lab16_mongodb_cluster.sh` | Spin up a 3-node replica set (rs0) |
| 2 | `lab16_replication_test.py` | Read preferences, write concerns, failover |
| 3 | `lab16_query_optimization.py` | Index impact benchmarking & selectivity |

## Prerequisites

### 1. Install MongoDB (Community Edition)
Download from the MongoDB website and make sure `mongod` and `mongosh`
are on your PATH.

### 2. Install Python dependencies
```bash
pip install -r ../requirements.txt
```

## Setup: Start the Replica Set

### Option A – manual (three terminals)
```bash
# Terminal 1
mongod --replSet rs0 --port 27017 --dbpath ./data/rs1 --bind_ip localhost

# Terminal 2
mongod --replSet rs0 --port 27018 --dbpath ./data/rs2 --bind_ip localhost

# Terminal 3
mongod --replSet rs0 --port 27019 --dbpath ./data/rs3 --bind_ip localhost
```

Then in a fourth terminal:
```bash
mongosh --port 27017 --eval '
  rs.initiate({
    _id: "rs0",
    members: [
      { _id: 0, host: "localhost:27017" },
      { _id: 1, host: "localhost:27018" },
      { _id: 2, host: "localhost:27019" }
    ]
  })'
```

### Option B – automated script
```bash
bash lab16_mongodb_cluster.sh --start-all
```

Verify the set is up before running Python scripts:
```bash
mongosh --port 27017 --eval 'rs.status()' | grep stateStr
```
You should see one `PRIMARY` and two `SECONDARY` lines.

## Run Order

```bash
# Exercise 2 – replication & failover (needs replica set)
python lab16_replication_test.py

# Exercise 3 – query optimisation (works on standalone too)
python lab16_query_optimization.py
```

## Expected Output

### Exercise 2
```
Connected to replica set rs0
Inserted 1000 documents

Primary    : ('localhost', 27017)
Secondaries: [('localhost', 27018), ('localhost', 27019)]

=== Read Preferences ===
  PRIMARY                    ids=[0, 1, 2]  (1.2 ms)
  SECONDARY_PREFERRED        ids=[0, 1, 2]  (1.0 ms)
  NEAREST                    ids=[0, 1, 2]  (0.9 ms)

=== Write Concern ===
  w=1 (default)              id=ObjectId(...)  (0.4 ms)
  w=majority                 id=ObjectId(...)  (2.1 ms)
  ...
```

### Exercise 3
```
Test data created:
  products  : 1000
  customers : 10000
  orders    : 100000

=== Queries WITHOUT Indexes ===
  Q1 – simple filter
    Avg time      : 185.3 ms
    Docs examined : 100000
    Stage         : COLLSCAN
  ...

=== Queries WITH Indexes ===
  Q1 – simple filter (idx)
    Avg time      : 1.2 ms
    Docs examined : 25000
    Stage         : FETCH
    Input stage   : IXSCAN
  ...
```

## Generated Files

| File | Description |
|------|-------------|
| `query_performance_comparison.png` | Bar charts: time & improvement % |

## Key Concepts

| Concept | What it means |
|---------|--------------|
| Replica set | Group of mongod instances that maintain the same dataset |
| Primary | The member that receives all write operations |
| Secondary | Replicates the oplog from the primary; can serve reads |
| Read preference | Which member(s) to route read operations to |
| Write concern | How many members must acknowledge a write before it returns |
| COLLSCAN | Full collection scan – O(n) regardless of result size |
| IXSCAN | Index scan – O(log n + k) where k = matching documents |
| Index selectivity | Fraction of documents a given key value matches; lower = more selective |
