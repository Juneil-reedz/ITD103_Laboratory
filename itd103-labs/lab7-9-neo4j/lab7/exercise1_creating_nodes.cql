// =============================================================
// Lab 7 – Exercise 1: Creating Nodes
// Paste into Neo4j Browser or run via cypher-shell
// =============================================================

// -------------------------------------------------------------
// STEP 0: Clear the database (start fresh)
// WARNING: This deletes all nodes and relationships
// -------------------------------------------------------------
MATCH (n) DETACH DELETE n;

// -------------------------------------------------------------
// 1. Create individual Person nodes
// -------------------------------------------------------------
CREATE (alice:Person {name: 'Alice', age: 30, city: 'Manila'});
CREATE (bob:Person {name: 'Bob', age: 25, city: 'Cebu'});
CREATE (charlie:Person {name: 'Charlie', age: 35, city: 'Davao'});

// -------------------------------------------------------------
// 2. Create multiple Technology nodes in one statement
// -------------------------------------------------------------
CREATE
  (database:Technology {name: 'Database',  type: 'Backend'}),
  (frontend:Technology {name: 'Frontend',  type: 'Development'}),
  (ai:Technology       {name: 'AI',        type: 'Emerging'});

// -------------------------------------------------------------
// 3. Create Company nodes
// -------------------------------------------------------------
CREATE
  (companyA:Company {name: 'TechCorp',    industry: 'IT',      location: 'Manila'}),
  (companyB:Company {name: 'InnovateLab', industry: 'Research', location: 'Cebu'});

// -------------------------------------------------------------
// 4. Verify: count nodes by label
// -------------------------------------------------------------
MATCH (n)
RETURN labels(n)[0] AS Label, count(*) AS Count
ORDER BY Count DESC;
