# Lab 3: NoSQL Performance Comparison

## Objectives
- Compare NoSQL database performance before and after indexing
- Implement indexing strategies
- Analyze query execution plans

## Files
| File | Description |
|------|-------------|
| `part_a_performance_testing.js` | Generate 100k documents, run baseline queries without indexes |
| `part_b_indexing.js` | Create indexes, re-test queries, collect stats |

## Quick Start

### Step 1 – Run baseline (no indexes)
```bash
mongosh --file part_a_performance_testing.js
```

### Step 2 – Apply indexes and compare
```bash
mongosh --file part_b_indexing.js
```

## Key Metrics to Record
From `explain("executionStats")` output, capture:

| Metric | Meaning |
|--------|---------|
| `stage` | `COLLSCAN` = full scan, `IXSCAN` = index used |
| `executionTimeMillisEstimate` | Query execution time |
| `totalDocsExamined` | Documents scanned (lower = better) |
| `totalKeysExamined` | Index keys scanned |

## Indexes Created
| Index | Type | Purpose |
|-------|------|---------|
| `{ category: 1 }` | Single-field | Filter by category |
| `{ category: 1, price: -1 }` | Compound | Category filter + price range/sort |
| `{ tags: 1 }` | Multikey | Array field lookups |
| `{ name: "text" }` | Text | Full-text keyword search |

## Deliverables
- [ ] Performance comparison table (COLLSCAN vs IXSCAN timings)
- [ ] Index analysis report
- [ ] Optimization recommendations
