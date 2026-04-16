// =============================================================
// Lab 9 – Exercise 2: Content-Based Filtering
// Run AFTER part_a_product_graph.cql
// =============================================================

// -------------------------------------------------------------
// 1. Find similar products in the same category (to Laptop)
//    Sorted by price similarity
// -------------------------------------------------------------
MATCH (target:Product {name: 'Laptop'})
MATCH (similar:Product {category: target.category})
WHERE target <> similar
RETURN similar.name                           AS SimilarProduct,
       similar.price                          AS Price,
       abs(target.price - similar.price)      AS PriceDifference
ORDER BY PriceDifference;

// -------------------------------------------------------------
// 2. Products Charlie viewed but has NOT purchased
// -------------------------------------------------------------
MATCH (c:Customer {name: 'Charlie'})-[:VIEWED]->(v:Product)
WHERE NOT EXISTS {
  MATCH (c)-[:PURCHASED]->(v)
}
RETURN v.name     AS ViewedNotPurchased,
       v.category AS Category,
       v.price    AS Price;

// -------------------------------------------------------------
// 3. Cross-sell recommendations for Alice
//    Based on BOUGHT_WITH edges from products she already owns
// -------------------------------------------------------------
MATCH (c:Customer {name: 'Alice'})-[:PURCHASED]->(p:Product)
MATCH (p)-[bw:BOUGHT_WITH]->(recommended:Product)
WHERE NOT EXISTS {
  MATCH (c)-[:PURCHASED]->(recommended)
}
RETURN recommended.name                AS CrossSell,
       recommended.category            AS Category,
       recommended.price               AS Price,
       collect(p.name)                 AS BecauseYouBought,
       sum(bw.frequency)               AS PopularityScore
ORDER BY PopularityScore DESC;

// -------------------------------------------------------------
// 4. BONUS: Customers who viewed but didn't buy (re-engagement targets)
// -------------------------------------------------------------
MATCH (c:Customer)-[:VIEWED]->(p:Product)
WHERE NOT EXISTS {
  MATCH (c)-[:PURCHASED]->(p)
}
RETURN c.name     AS Customer,
       c.segment  AS Segment,
       collect(p.name) AS ProductsToFollowUp,
       count(p)   AS ViewedNotBoughtCount
ORDER BY ViewedNotBoughtCount DESC;

// -------------------------------------------------------------
// 5. BONUS: Category affinity per customer
//    What category does each customer buy from most?
// -------------------------------------------------------------
MATCH (c:Customer)-[:PURCHASED]->(p:Product)
WITH c, p.category AS category, count(*) AS purchases
ORDER BY c.name, purchases DESC
WITH c, collect({category: category, count: purchases})[0] AS topCategory
RETURN c.name         AS Customer,
       c.segment      AS Segment,
       topCategory.category  AS FavoriteCategory,
       topCategory.count     AS PurchaseCount;
