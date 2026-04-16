// =============================================================
// Lab 8 – Exercise 2: Variable Length Paths
// Run AFTER part_a_load_dataset.cql
// =============================================================

// -------------------------------------------------------------
// 1. Friends of friends (2nd-degree connections)
//    Exclude people Alice is already directly connected to
// -------------------------------------------------------------
MATCH (me:Person {name: 'Alice'})-[:FRIENDS_WITH*2]-(fof:Person)
WHERE NOT (me)-[:FRIENDS_WITH]-(fof)
  AND me <> fof
RETURN DISTINCT fof.name AS SuggestedFriend,
                fof.age   AS Age;

// -------------------------------------------------------------
// 2. Mutual friends between Alice and Frank
// -------------------------------------------------------------
MATCH (a:Person {name: 'Alice'})-[:FRIENDS_WITH]-(mutual)-[:FRIENDS_WITH]-(b:Person {name: 'Frank'})
RETURN mutual.name AS MutualFriend;

// -------------------------------------------------------------
// 3. People who share common interests with Alice
// -------------------------------------------------------------
MATCH (p1:Person {name: 'Alice'})-[:INTERESTED_IN]->(i:Interest)<-[:INTERESTED_IN]-(p2:Person)
WHERE p1 <> p2
RETURN p2.name         AS Person,
       collect(i.name) AS CommonInterests,
       count(i)        AS SharedCount
ORDER BY SharedCount DESC;

// -------------------------------------------------------------
// 4. BONUS: Network reach — how many people can Alice reach
//    within N hops?
// -------------------------------------------------------------
MATCH (alice:Person {name: 'Alice'})
UNWIND [1,2,3] AS hops
CALL {
  WITH alice, hops
  MATCH (alice)-[:FRIENDS_WITH*1..hops]-(reached:Person)
  WHERE reached <> alice
  RETURN hops, count(DISTINCT reached) AS PeopleReached
}
RETURN hops AS MaxHops, PeopleReached
ORDER BY MaxHops;

// -------------------------------------------------------------
// 5. BONUS: Degree of separation for all pairs
// -------------------------------------------------------------
MATCH (a:Person), (b:Person)
WHERE id(a) < id(b)
MATCH path = shortestPath((a)-[:FRIENDS_WITH*]-(b))
RETURN a.name AS PersonA,
       b.name AS PersonB,
       length(path) AS DegreesOfSeparation
ORDER BY DegreesOfSeparation;
