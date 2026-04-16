// =============================================================
// Lab 8 – Exercise 1: Basic Path Finding
// Run AFTER part_a_load_dataset.cql
// =============================================================

// -------------------------------------------------------------
// 1. Find ANY path between Alice and Frank (all paths)
//    * = any number of hops; - = undirected
// -------------------------------------------------------------
MATCH path = (alice:Person {name: 'Alice'})-[:FRIENDS_WITH*]-(frank:Person {name: 'Frank'})
RETURN path
LIMIT 5;

// With hop count
MATCH path = (alice:Person {name: 'Alice'})-[:FRIENDS_WITH*]-(frank:Person {name: 'Frank'})
RETURN path, length(path) AS Hops
ORDER BY Hops
LIMIT 5;

// -------------------------------------------------------------
// 2. Shortest path between Alice and Frank
//    shortestPath() returns the single path with fewest hops
// -------------------------------------------------------------
MATCH path = shortestPath(
  (alice:Person {name: 'Alice'})-[:FRIENDS_WITH*]-(frank:Person {name: 'Frank'})
)
RETURN path,
       length(path) AS Degrees,
       [node IN nodes(path) | node.name] AS PathNodes;

// -------------------------------------------------------------
// 3. All paths up to 3 degrees from Alice
// -------------------------------------------------------------
MATCH path = (alice:Person {name: 'Alice'})-[:FRIENDS_WITH*1..3]-(other:Person)
WHERE other.name <> 'Alice'
RETURN DISTINCT other.name AS ReachablePerson,
       min(length(path))   AS ClosestDistance
ORDER BY ClosestDistance;

// -------------------------------------------------------------
// 4. BONUS: All shortest paths between two nodes
//    allShortestPaths() finds every shortest-hop path
// -------------------------------------------------------------
MATCH path = allShortestPaths(
  (alice:Person {name: 'Alice'})-[:FRIENDS_WITH*]-(frank:Person {name: 'Frank'})
)
RETURN path,
       [node IN nodes(path) | node.name] AS PathNodes,
       length(path) AS Hops;

// -------------------------------------------------------------
// 5. BONUS: Check if two nodes are connected (EXISTS)
// -------------------------------------------------------------
MATCH (alice:Person {name: 'Alice'}), (frank:Person {name: 'Frank'})
RETURN EXISTS {
  MATCH (alice)-[:FRIENDS_WITH*]-(frank)
} AS AreConnected;
