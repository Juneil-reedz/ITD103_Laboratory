// =============================================================
// Lab 7 – Exercise 3: Basic Queries
// Run AFTER exercises 1 and 2
// =============================================================

// -------------------------------------------------------------
// 1. Find all people
// -------------------------------------------------------------
MATCH (p:Person)
RETURN p;

// With specific properties only
MATCH (p:Person)
RETURN p.name AS Name, p.age AS Age, p.city AS City
ORDER BY p.age;

// -------------------------------------------------------------
// 2. Find people in a specific city
// -------------------------------------------------------------
MATCH (p:Person {city: 'Manila'})
RETURN p.name, p.age;

// Using WHERE clause (equivalent, more flexible)
MATCH (p:Person)
WHERE p.city = 'Manila'
RETURN p.name, p.age;

// -------------------------------------------------------------
// 3. Find all KNOWS relationships
// -------------------------------------------------------------
MATCH (p1:Person)-[r:KNOWS]->(p2:Person)
RETURN p1.name AS Person1,
       r.since  AS KnownSince,
       p2.name  AS Person2;

// -------------------------------------------------------------
// 4. Find people who like the Database technology
// -------------------------------------------------------------
MATCH (p:Person)-[:LIKES]->(t:Technology {name: 'Database'})
RETURN p.name AS Person, p.city AS City;

// With relationship properties
MATCH (p:Person)-[l:LIKES]->(t:Technology {name: 'Database'})
RETURN p.name AS Person, l.score AS LikeScore, l.interest AS InterestType
ORDER BY l.score DESC;

// -------------------------------------------------------------
// 5. Count nodes by label
// -------------------------------------------------------------
MATCH (n)
RETURN labels(n)[0] AS Label, count(*) AS Count
ORDER BY Count DESC;

// -------------------------------------------------------------
// 6. BONUS: Find all technologies and who likes them
// -------------------------------------------------------------
MATCH (p:Person)-[l:LIKES]->(t:Technology)
RETURN t.name AS Technology,
       collect(p.name) AS Fans,
       count(p) AS FanCount
ORDER BY FanCount DESC;

// -------------------------------------------------------------
// 7. BONUS: Find people with a WORKS_AT relationship
// -------------------------------------------------------------
MATCH (p:Person)-[w:WORKS_AT]->(c:Company)
RETURN p.name AS Employee,
       w.role  AS Role,
       c.name  AS Company,
       w.since AS Since;

// -------------------------------------------------------------
// 8. BONUS: Find who works with whom and on what project
// -------------------------------------------------------------
MATCH (p1:Person)-[r:WORKS_WITH]->(p2:Person)
RETURN p1.name AS Person1,
       p2.name AS Person2,
       r.project AS Project;
