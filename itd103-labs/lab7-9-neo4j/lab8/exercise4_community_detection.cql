// =============================================================
// Lab 8 – Exercise 4: Community Detection
// Run AFTER part_a_load_dataset.cql
// =============================================================

// -------------------------------------------------------------
// 1. Find connected components (how many people each node can reach)
// -------------------------------------------------------------
MATCH (p:Person)
MATCH (p)-[:FRIENDS_WITH*]-(other:Person)
RETURN p.name              AS Person,
       count(DISTINCT other) AS ReachableCount,
       collect(DISTINCT other.name) AS ReachableMembers
ORDER BY ReachableCount DESC;

// -------------------------------------------------------------
// 2. Find triangles — cliques of exactly 3 people
//    id(a) < id(b) < id(c) prevents duplicate triples
// -------------------------------------------------------------
MATCH (a:Person)-[:FRIENDS_WITH]-(b:Person),
      (b:Person)-[:FRIENDS_WITH]-(c:Person),
      (c:Person)-[:FRIENDS_WITH]-(a:Person)
WHERE id(a) < id(b) AND id(b) < id(c)
RETURN a.name AS Member1,
       b.name AS Member2,
       c.name AS Member3;

// -------------------------------------------------------------
// 3. Clustering coefficient for each node
//    = (actual triangles through node) / (possible triangles)
//    Closer to 1 = node's friends are also friends with each other
// -------------------------------------------------------------
MATCH (p:Person)-[:FRIENDS_WITH]-(neighbor:Person)
WITH p, collect(DISTINCT neighbor) AS neighbors
WITH p, neighbors, size(neighbors) AS degree
WHERE degree >= 2
MATCH (a:Person)-[:FRIENDS_WITH]-(b:Person)
WHERE a IN neighbors AND b IN neighbors AND id(a) < id(b)
WITH p, degree, count(*) AS existingEdges
RETURN p.name AS Person,
       degree AS Degree,
       existingEdges AS ActualEdges,
       (degree * (degree - 1) / 2) AS PossibleEdges,
       round(toFloat(existingEdges) / (degree * (degree - 1) / 2) * 100) / 100 AS ClusteringCoefficient
ORDER BY ClusteringCoefficient DESC;

// -------------------------------------------------------------
// 4. Interest-based community grouping
//    Group people by shared top interest
// -------------------------------------------------------------
MATCH (p:Person)-[r:INTERESTED_IN]->(i:Interest)
WHERE r.level = 'High'
RETURN i.name                 AS Community,
       collect(p.name)        AS Members,
       count(p)               AS Size
ORDER BY Size DESC;

// -------------------------------------------------------------
// 5. BONUS: Bridge nodes — people whose removal splits the graph
//    Nodes NOT part of any triangle but connecting components
// -------------------------------------------------------------
MATCH (p:Person)
WHERE NOT EXISTS {
  MATCH (p)-[:FRIENDS_WITH]-(a:Person)-[:FRIENDS_WITH]-(b:Person)-[:FRIENDS_WITH]-(p)
}
RETURN p.name AS BridgeCandidate,
       size((p)-[:FRIENDS_WITH]-()) AS Connections;
