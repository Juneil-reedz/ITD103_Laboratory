# Lab 8: Advanced Cypher Queries & Graph Algorithms

## Objectives
- Implement complex graph queries
- Use path operations
- Apply graph algorithms manually in Cypher

## Files
| File | Description |
|------|-------------|
| `part_a_load_dataset.cql` | Create 6-person social network with interests |
| `exercise1_path_finding.cql` | `shortestPath()`, `allShortestPaths()`, variable-length `*` |
| `exercise2_variable_length_paths.cql` | Friends of friends, mutual friends, interest overlap |
| `exercise3_centrality.cql` | Degree, closeness, betweenness centrality |
| `exercise4_community_detection.cql` | Triangles, clustering coefficient, connected components |
| `exercise5_recommendations.cql` | Friend + interest recommendations |

## Run Order
```bash
cypher-shell -u neo4j -p password -f part_a_load_dataset.cql
cypher-shell -u neo4j -p password -f exercise1_path_finding.cql
cypher-shell -u neo4j -p password -f exercise2_variable_length_paths.cql
cypher-shell -u neo4j -p password -f exercise3_centrality.cql
cypher-shell -u neo4j -p password -f exercise4_community_detection.cql
cypher-shell -u neo4j -p password -f exercise5_recommendations.cql
```

## Key Concepts
| Concept | Cypher Pattern |
|---------|---------------|
| Any-length path | `(a)-[:REL*]-(b)` |
| Bounded path | `(a)-[:REL*1..3]-(b)` |
| Shortest path | `shortestPath((a)-[:REL*]-(b))` |
| All shortest paths | `allShortestPaths((a)-[:REL*]-(b))` |
| Path length | `length(path)` |
| Nodes in path | `nodes(path)` |

## Deliverables
- [ ] Complete Cypher query file
- [ ] Algorithm results (centrality scores, triangles, communities)
- [ ] Graph visualization with algorithms applied
