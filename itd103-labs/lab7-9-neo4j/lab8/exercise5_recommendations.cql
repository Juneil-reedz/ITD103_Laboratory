// =============================================================
// Lab 8 – Exercise 5: Recommendation Queries
// Run AFTER part_a_load_dataset.cql
// =============================================================

// -------------------------------------------------------------
// 1. Friend recommendation based on mutual friends (Alice)
// -------------------------------------------------------------
MATCH (me:Person {name: 'Alice'})-[:FRIENDS_WITH]-(friend)-[:FRIENDS_WITH]-(potential:Person)
WHERE NOT (me)-[:FRIENDS_WITH]-(potential)
  AND me <> potential
RETURN potential.name   AS RecommendedFriend,
       count(friend)     AS MutualFriends,
       collect(friend.name) AS SharedFriendNames
ORDER BY MutualFriends DESC;

// -------------------------------------------------------------
// 2. Interest-based person recommendation
//    Find people with common interests AND suggest their unique interests
// -------------------------------------------------------------
MATCH (me:Person {name: 'Alice'})-[:INTERESTED_IN]->(myInterest:Interest)
MATCH (other:Person)-[:INTERESTED_IN]->(myInterest)
WHERE me <> other
WITH other, count(myInterest) AS CommonInterests

MATCH (other)-[:INTERESTED_IN]->(theirInterest:Interest)
WHERE NOT EXISTS {
  MATCH (me:Person {name: 'Alice'})-[:INTERESTED_IN]->(theirInterest)
}
RETURN other.name                       AS Person,
       collect(DISTINCT theirInterest.name) AS SuggestedInterests,
       CommonInterests
ORDER BY CommonInterests DESC;

// -------------------------------------------------------------
// 3. BONUS: People Alice might know (2 hops, not yet connected)
//    Sorted by how many mutual friends they share
// -------------------------------------------------------------
MATCH (me:Person {name: 'Alice'})
MATCH (me)-[:FRIENDS_WITH*2]-(candidate:Person)
WHERE NOT (me)-[:FRIENDS_WITH]-(candidate)
  AND me <> candidate
WITH me, candidate,
     [(me)-[:FRIENDS_WITH]-(mutual)-[:FRIENDS_WITH]-(candidate) | mutual.name] AS mutuals
RETURN DISTINCT candidate.name     AS YouMayKnow,
                size(mutuals)      AS MutualCount,
                mutuals            AS MutualFriends
ORDER BY MutualCount DESC;

// -------------------------------------------------------------
// 4. BONUS: Recommend interests to Bob (not already following)
//    Based on what his friends are interested in
// -------------------------------------------------------------
MATCH (me:Person {name: 'Bob'})-[:FRIENDS_WITH]-(friend:Person)-[:INTERESTED_IN]->(i:Interest)
WHERE NOT EXISTS {
  MATCH (me)-[:INTERESTED_IN]->(i)
}
RETURN i.name             AS SuggestedInterest,
       count(friend)       AS FriendsWhoLikeIt,
       collect(friend.name) AS RecommendedBy
ORDER BY FriendsWhoLikeIt DESC;
