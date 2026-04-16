# Labs 4–6: MongoDB

## Overview
| Lab | Topic | Key Skills |
|-----|-------|-----------|
| [Lab 4](./lab4/) | Advanced MQL Queries | Array operators, text search, geospatial |
| [Lab 5](./lab5/) | Aggregation Framework | Pipelines, $lookup, $facet, window functions |
| [Lab 6](./lab6/) | Performance & Optimization | Replication, sharding, monitoring |

## Datasets Used
| File | Used By | Description |
|------|---------|-------------|
| `datasets/restaurants.json` | Lab 4 | 10 NYC restaurants with grades and coordinates |
| `datasets/sales.json` | Lab 5 | 20 sales transactions across categories/regions |
| `datasets/customers.json` | Lab 5 | 6 customers (for `$lookup` join) |

## Directory Structure
```
lab4-6-mongodb/
├── lab4/
│   ├── README.md
│   ├── part_a_import.sh
│   ├── exercise1_array_operators.js
│   ├── exercise2_text_search.js
│   └── exercise3_geospatial.js
├── lab5/
│   ├── README.md
│   ├── part_a_import.sh
│   ├── exercise1_basic_aggregation.js
│   ├── exercise2_complex_pipeline.js
│   └── exercise3_facets_buckets.js
├── lab6/
│   ├── README.md
│   ├── part_a_replication.sh
│   ├── part_a_replication.js
│   ├── part_b_sharding.sh
│   ├── part_b_sharding.js
│   └── part_c_monitoring.js
└── README.md
```
