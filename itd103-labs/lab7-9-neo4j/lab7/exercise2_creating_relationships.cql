// =============================================================
// Lab 7 – Exercise 2: Creating Relationships
// Run AFTER exercise1_creating_nodes.cql
// =============================================================

// -------------------------------------------------------------
// 1. Create KNOWS relationship between Alice and Bob
// -------------------------------------------------------------
MATCH (a:Person {name: 'Alice'})
MATCH (b:Person {name: 'Bob'})
CREATE (a)-[:KNOWS {since: 2020, how: 'University'}]->(b);

// -------------------------------------------------------------
// 2. Create WORKS_WITH relationship between Alice and Charlie
// -------------------------------------------------------------
MATCH (alice:Person   {name: 'Alice'})
MATCH (charlie:Person {name: 'Charlie'})
CREATE (alice)-[:WORKS_WITH {project: 'Database Migration', since: 2022}]->(charlie);

// -------------------------------------------------------------
// 3. LIKES relationships — persons who like technologies
//    $all array match not available in Cypher; use WHERE IN
// -------------------------------------------------------------
MATCH (p:Person),      (t:Technology)
WHERE p.name IN ['Alice', 'Bob']
  AND t.name IN ['Database', 'AI']
CREATE (p)-[:LIKES {score: 8.5, interest: 'Professional'}]->(t);

// Charlie likes Frontend
MATCH (charlie:Person    {name: 'Charlie'})
MATCH (frontend:Technology {name: 'Frontend'})
CREATE (charlie)-[:LIKES {score: 7.0, interest: 'Hobby'}]->(frontend);

// -------------------------------------------------------------
// 4. WORKS_AT relationships — persons to companies
// -------------------------------------------------------------
MATCH (alice:Person  {name: 'Alice'})
MATCH (comp:Company  {name: 'TechCorp'})
CREATE (alice)-[:WORKS_AT {role: 'Senior DBA', since: 2021}]->(comp);

MATCH (bob:Person   {name: 'Bob'})
MATCH (comp:Company {name: 'InnovateLab'})
CREATE (bob)-[:WORKS_AT {role: 'Junior Developer', since: 2023}]->(comp);

// -------------------------------------------------------------
// 5. Verify: return all relationships
// -------------------------------------------------------------
MATCH (n1)-[r]->(n2)
RETURN n1.name AS From,
       type(r)  AS Relationship,
       n2.name  AS To
ORDER BY Relationship;
