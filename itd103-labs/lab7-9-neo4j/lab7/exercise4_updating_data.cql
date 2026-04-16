// =============================================================
// Lab 7 – Exercise 4: Updating & Deleting Data
// Run AFTER exercises 1–3
// =============================================================

// -------------------------------------------------------------
// 1. Update specific properties on Alice
// -------------------------------------------------------------
MATCH (p:Person {name: 'Alice'})
SET p.age = 31,
    p.skills = ['MongoDB', 'Neo4j', 'Cypher']
RETURN p.name, p.age, p.skills;

// -------------------------------------------------------------
// 2. Add a new property to ALL Person nodes
// -------------------------------------------------------------
MATCH (p:Person)
SET p.updated_at = timestamp()
RETURN p.name, p.updated_at;

// -------------------------------------------------------------
// 3. Remove a property from Bob (REMOVE vs SET to null)
// -------------------------------------------------------------
MATCH (p:Person {name: 'Bob'})
REMOVE p.age
RETURN p;

// Verify Bob no longer has age
MATCH (p:Person {name: 'Bob'})
RETURN p.name, p.age;  // Should return null

// -------------------------------------------------------------
// 4. Update a relationship property
// -------------------------------------------------------------
MATCH (a:Person {name: 'Alice'})-[r:KNOWS]->(b:Person {name: 'Bob'})
SET r.since = 2019,
    r.closeness = 'Close Friend'
RETURN a.name, r, b.name;

// -------------------------------------------------------------
// 5. Add a label to an existing node (multi-label)
// -------------------------------------------------------------
MATCH (p:Person {name: 'Alice'})
SET p:Admin
RETURN labels(p) AS Labels;

// Remove the extra label
MATCH (p:Person {name: 'Alice'})
REMOVE p:Admin
RETURN labels(p) AS Labels;

// -------------------------------------------------------------
// 6. Delete Charlie and all his relationships safely
//    DETACH DELETE removes relationships before deleting the node
// -------------------------------------------------------------
MATCH (p:Person {name: 'Charlie'})
DETACH DELETE p;

// Original approach (manual relationship delete first):
// MATCH (p:Person {name: 'Charlie'})-[r]-()
// DELETE r, p

// Verify Charlie is gone
MATCH (p:Person)
RETURN p.name, p.city;

// -------------------------------------------------------------
// 7. MERGE — create node only if it doesn't already exist
//    Useful for upserts
// -------------------------------------------------------------
MERGE (diana:Person {name: 'Diana'})
ON CREATE SET diana.age = 28, diana.city = 'Manila', diana.created_at = timestamp()
ON MATCH  SET diana.updated_at = timestamp()
RETURN diana;

// -------------------------------------------------------------
// 8. MERGE relationship — create only if it doesn't exist
// -------------------------------------------------------------
MATCH (alice:Person {name: 'Alice'})
MATCH (diana:Person {name: 'Diana'})
MERGE (alice)-[r:KNOWS]->(diana)
ON CREATE SET r.since = 2024
RETURN alice.name, r, diana.name;

// -------------------------------------------------------------
// 9. Final state: all nodes and relationships
// -------------------------------------------------------------
MATCH (n1)-[r]->(n2)
RETURN n1.name AS From, type(r) AS Rel, n2.name AS To
ORDER BY type(r);

MATCH (n)
RETURN labels(n)[0] AS Label, count(*) AS Total;
