# Lab 7 – Part A: Neo4j Setup

## Option 1: Neo4j Desktop Application

1. Download Neo4j Desktop from [neo4j.com/download](https://neo4j.com/download/)
2. Install and open the application
3. Click **New Project** → give it a name (e.g., `ITD103`)
4. Click **Add** → **Local DBMS**
5. Set name: `lab7-dbms`, password: `password`, version: latest
6. Click **Create**, then **Start**
7. Click **Open** → opens Neo4j Browser at `http://localhost:7474`
8. Login: username `neo4j`, password `password`

---

## Option 2: Docker

```bash
docker run \
  --name neo4j-lab \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -v neo4j_data:/data \
  neo4j:5.15
```

Then open: `http://localhost:7474`

---

## Verify Connection

Once in Neo4j Browser, run:

```cypher
RETURN "Connected to Neo4j!" AS message
```

Expected output:
```
╒══════════════════════════╕
│message                   │
╞══════════════════════════╡
│"Connected to Neo4j!"     │
└──────────────────────────┘
```

---

## Connection Details

| Setting  | Value          |
|----------|----------------|
| URL      | bolt://localhost:7687 |
| Browser  | http://localhost:7474 |
| Username | neo4j          |
| Password | password    |

---

## Running .cql Files

In Neo4j Browser, paste the contents of each `.cql` file directly into the query editor.

Or via terminal using cypher-shell:
```bash
cypher-shell -u neo4j -p password -f exercise1_creating_nodes.cql
```
