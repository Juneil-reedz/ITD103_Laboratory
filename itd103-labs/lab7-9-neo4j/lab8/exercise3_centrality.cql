// =============================================================
// Lab 8 – Exercise 3: Centrality Algorithms
// Run AFTER part_a_load_dataset.cql
// =============================================================

// -------------------------------------------------------------
// 1. Degree Centrality — how many direct connections each node has
//    High degree = highly connected "hub"
// -------------------------------------------------------------
MATCH (p:Person)
RETURN p.name                                   AS Person,
       size((p)-[:FRIENDS_WITH]-())             AS TotalDegree,
       size((p)-[:FRIENDS_WITH]->())            AS OutDegree,
       size((p)<-[:FRIENDS_WITH]-())            AS InDegree
ORDER BY TotalDegree DESC;

// -------------------------------------------------------------
// 2. Closeness Centrality (manual approximation)
//    Measures average shortest path distance to all other nodes
//    Lower avg distance = more "central" in the network
// -------------------------------------------------------------
MATCH (p:Person), (other:Person)
WHERE p <> other
MATCH path = shortestPath((p)-[:FRIENDS_WITH*]-(other))
WITH p, avg(length(path)) AS AvgDistance
RETURN p.name        AS Person,
       round(AvgDistance * 100) / 100  AS AvgShortestPath,
       round((1.0 / AvgDistance) * 100) / 100 AS ClosenessScore
ORDER BY ClosenessScore DESC;

// -------------------------------------------------------------
// 3. Betweenness Centrality (simplified Cypher approximation)
//    Counts how often a node appears on shortest paths between others
//    High betweenness = "bridge" or "broker" in the network
// -------------------------------------------------------------
MATCH (source:Person), (target:Person)
WHERE id(source) < id(target)
MATCH path = allShortestPaths((source)-[:FRIENDS_WITH*]-(target))
WITH nodes(path) AS pathNodes
UNWIND pathNodes AS intermediary
MATCH (intermediary:Person)
WHERE NOT intermediary IN [pathNodes[0], pathNodes[-1]]
RETURN intermediary.name AS Person,
       count(*) AS BetweennessApprox
ORDER BY BetweennessApprox DESC;

// -------------------------------------------------------------
// 4. BONUS: Eigenvector-style influence
//    People with highly-connected friends score higher
// -------------------------------------------------------------
MATCH (p:Person)-[:FRIENDS_WITH]-(friend:Person)
WITH p, friend, size((friend)-[:FRIENDS_WITH]-()) AS friendDegree
RETURN p.name                   AS Person,
       count(friend)             AS DirectFriends,
       sum(friendDegree)         AS SumFriendDegrees,
       round(toFloat(sum(friendDegree)) / count(friend) * 100) / 100 AS AvgFriendInfluence
ORDER BY AvgFriendInfluence DESC;
