# Lab 6: MongoDB Performance & Optimization

## Objectives
- Configure replica sets for high availability
- Implement sharding for horizontal scaling
- Monitor database performance

## Files
| File | Description |
|------|-------------|
| `part_a_replication.sh` | Start 3 mongod processes for replica set |
| `part_a_replication.js` | `rs.initiate()`, status checks, failover, write concern |
| `part_b_sharding.sh` | Start shards, config server, and mongos router |
| `part_b_sharding.js` | `sh.addShard()`, `sh.shardCollection()`, distribution check |
| `part_c_monitoring.js` | `currentOp`, `stats()`, `explain()`, query profiler |

## Setup Order

### Part A – Replication (4 terminals required)
```bash
# Terminals 1–3: run commands from part_a_replication.sh
# Then in mongosh --port 27017:
mongosh --port 27017 --file lab4-6-mongodb/lab6/part_a_replication.js
```

### Part B – Sharding (5 terminals required)
```bash
# Terminals 1–4: run commands from part_b_sharding.sh
# Then connect via mongos:
mongosh --port 27023 --file lab4-6-mongodb/lab6/part_b_sharding.js
```

### Part C – Monitoring
```bash
mongosh --port 27023 --file lab4-6-mongodb/lab6/part_c_monitoring.js
```

## Architecture Overview

```
Replication:
  [Primary :27017] ←→ [Secondary :27018] ←→ [Arbiter :27019]

Sharding:
  Client → [mongos :27023] → [Config :27022]
                          → [Shard1 :27020]
                          → [Shard2 :27021]
```

## Deliverables
- [ ] Replica set configuration and `rs.status()` output
- [ ] Sharding implementation and `getShardDistribution()` output
- [ ] Performance monitoring report
