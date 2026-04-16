// =============================================================
// Lab 9 – Exercise 1: Collaborative Filtering
// Run AFTER part_a_product_graph.cql
// =============================================================

// -------------------------------------------------------------
// 1. "Customers who bought this also bought"
//    Weighted by customer segment (Premium = 2x weight)
// -------------------------------------------------------------
MATCH (target:Product {name: 'Laptop'})<-[:PURCHASED]-(customer:Customer)-[:PURCHASED]->(other:Product)
WHERE target <> other
RETURN other.name        AS RecommendedProduct,
       other.category    AS Category,
       other.price       AS Price,
       count(customer)   AS CustomerCount,
       sum(
         CASE
           WHEN customer.segment = 'Premium' THEN 2
           ELSE 1
         END
       ) AS WeightedScore
ORDER BY WeightedScore DESC;

// -------------------------------------------------------------
// 2. Find similar customers to Alice
//    Based on shared purchases → suggest what they bought but Alice hasn't
// -------------------------------------------------------------
MATCH (me:Customer {name: 'Alice'})-[:PURCHASED]->(myProduct:Product)
MATCH (other:Customer)-[:PURCHASED]->(myProduct)
WHERE me <> other
WITH other, count(myProduct) AS CommonProducts

MATCH (other)-[:PURCHASED]->(theirProduct:Product)
WHERE NOT EXISTS {
  MATCH (me:Customer {name: 'Alice'})-[:PURCHASED]->(theirProduct)
}
RETURN other.name                           AS SimilarCustomer,
       other.segment                        AS Segment,
       collect(theirProduct.name)           AS RecommendedProducts,
       CommonProducts                       AS SimilarityScore
ORDER BY SimilarityScore DESC;

// -------------------------------------------------------------
// 3. BONUS: Popularity-weighted recommendations (all customers)
//    Most-purchased products not yet bought by a given customer
// -------------------------------------------------------------
MATCH (me:Customer {name: 'Bob'})
MATCH (:Customer)-[:PURCHASED]->(p:Product)
WHERE NOT EXISTS {
  MATCH (me)-[:PURCHASED]->(p)
}
RETURN p.name          AS RecommendedProduct,
       p.category      AS Category,
       p.price         AS Price,
       count(*)        AS GlobalPurchaseCount
ORDER BY GlobalPurchaseCount DESC;
