# Labs 7–9: Neo4j Graph Database

## Overview
| Lab | Topic | Key Skills |
|-----|-------|-----------|
| [Lab 7](./lab7/) | Neo4j Fundamentals & Cypher Basics | Nodes, relationships, CRUD |
| [Lab 8](./lab8/) | Advanced Cypher & Graph Algorithms | Paths, centrality, community detection |
| [Lab 9](./lab9/) | Real-World Graph Application | Recommendations, fraud detection |

## Prerequisites
- Neo4j 5.x (Desktop or Docker)
- cypher-shell (bundled with Neo4j)
- Connection: `bolt://localhost:7687`, user: `neo4j`, pass: `password`

## Directory Structure
```
lab7-9-neo4j/
├── lab7/
│   ├── README.md
│   ├── part_a_setup.md
│   ├── exercise1_creating_nodes.cql
│   ├── exercise2_creating_relationships.cql
│   ├── exercise3_basic_queries.cql
│   └── exercise4_updating_data.cql
├── lab8/
│   ├── README.md
│   ├── part_a_load_dataset.cql
│   ├── exercise1_path_finding.cql
│   ├── exercise2_variable_length_paths.cql
│   ├── exercise3_centrality.cql
│   ├── exercise4_community_detection.cql
│   └── exercise5_recommendations.cql
├── lab9/
│   ├── README.md
│   ├── part_a_product_graph.cql
│   ├── exercise1_collaborative_filtering.cql
│   ├── exercise2_content_based_filtering.cql
│   └── exercise3_fraud_detection.cql
└── README.md
```

## Quick Docker Start
```bash
docker run --name neo4j-lab -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -v neo4j_data:/data neo4j:5.15
```
