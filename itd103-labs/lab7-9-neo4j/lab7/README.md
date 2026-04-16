# Lab 7: Neo4j Fundamentals & Cypher Basics

## Objectives
- Install and configure Neo4j
- Master Cypher query language basics
- Create nodes and relationships

## Files
| File | Description |
|------|-------------|
| `part_a_setup.md` | Neo4j installation guide (Desktop + Docker) |
| `exercise1_creating_nodes.cql` | CREATE nodes with labels and properties |
| `exercise2_creating_relationships.cql` | MATCH + CREATE relationships with properties |
| `exercise3_basic_queries.cql` | MATCH, WHERE, RETURN, ORDER BY |
| `exercise4_updating_data.cql` | SET, REMOVE, DETACH DELETE, MERGE |

## Run Order
1. Start Neo4j (see `part_a_setup.md`)
2. Open Neo4j Browser: `http://localhost:7474`
3. Run exercises in order: `exercise1` → `exercise2` → `exercise3` → `exercise4`

## Via cypher-shell
```bash
cypher-shell -u neo4j -p password -f exercise1_creating_nodes.cql
cypher-shell -u neo4j -p password -f exercise2_creating_relationships.cql
cypher-shell -u neo4j -p password -f exercise3_basic_queries.cql
cypher-shell -u neo4j -p password -f exercise4_updating_data.cql
```

## Key Cypher Syntax Reference
| Operation | Syntax |
|-----------|--------|
| Create node | `CREATE (n:Label {prop: value})` |
| Create relationship | `CREATE (a)-[:REL_TYPE {prop: val}]->(b)` |
| Match + filter | `MATCH (n:Label) WHERE n.prop = val RETURN n` |
| Update property | `SET n.prop = newValue` |
| Remove property | `REMOVE n.prop` |
| Safe delete | `DETACH DELETE n` |
| Upsert | `MERGE (n:Label {prop: val}) ON CREATE SET ... ON MATCH SET ...` |

## Deliverables
- [ ] Neo4j connection screenshot
- [ ] Cypher queries file (.cql)
- [ ] Graph visualization screenshot
