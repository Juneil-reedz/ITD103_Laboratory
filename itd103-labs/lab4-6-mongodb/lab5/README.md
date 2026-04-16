# Lab 5: Aggregation Framework

## Objectives
- Master aggregation pipeline stages
- Implement complex data transformations
- Optimize aggregation performance

## Files
| File | Description |
|------|-------------|
| `part_a_import.sh` | Import `sales.json` and `customers.json` |
| `exercise1_basic_aggregation.js` | `$group`, `$sort`, `$bucket`, `$bucketAuto` |
| `exercise2_complex_pipeline.js` | `$match`, `$lookup`, `$unwind`, `$addFields`, `$project` |
| `exercise3_facets_buckets.js` | `$facet`, `$bucketAuto`, `$sortByCount`, `$setWindowFields` |

## Quick Start

```bash
# From itd103-labs/ root:
bash lab4-6-mongodb/lab5/part_a_import.sh

# Then in mongosh:
mongosh --file lab4-6-mongodb/lab5/exercise1_basic_aggregation.js
mongosh --file lab4-6-mongodb/lab5/exercise2_complex_pipeline.js
mongosh --file lab4-6-mongodb/lab5/exercise3_facets_buckets.js
```

## Aggregation Stage Reference
| Stage | Purpose |
|-------|---------|
| `$match` | Filter documents (use early to reduce pipeline input) |
| `$group` | Group by field, apply accumulators (`$sum`, `$avg`, `$min`, `$max`) |
| `$lookup` | Left outer join with another collection |
| `$unwind` | Deconstruct array into separate documents |
| `$addFields` | Add computed fields without removing existing ones |
| `$project` | Shape output — include, exclude, rename, compute |
| `$facet` | Run multiple independent pipelines in one pass |
| `$bucket` | Group into user-defined numeric ranges |
| `$setWindowFields` | Running totals, moving averages (MongoDB 5.0+) |

## Deliverables
- [ ] Complete aggregation pipelines
- [ ] Performance analysis
- [ ] Business insights report
