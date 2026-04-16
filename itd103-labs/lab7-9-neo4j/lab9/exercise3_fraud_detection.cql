// =============================================================
// Lab 9 – Exercise 3: Fraud Detection Patterns
// Run AFTER part_a_product_graph.cql
// Creates a separate fraud scenario graph
// =============================================================

// -------------------------------------------------------------
// STEP 1: Create suspicious pattern graph
// Add fraud suspects alongside existing data
// -------------------------------------------------------------
CREATE
  (cust1:Customer {id: 201, name: 'User1', signup_date: '2024-01-01', segment: 'Regular'}),
  (cust2:Customer {id: 202, name: 'User2', signup_date: '2024-01-02', segment: 'Regular'}),
  (cust3:Customer {id: 203, name: 'User3', signup_date: '2024-01-03', segment: 'Regular'}),

  // Shared identifiers (suspicious links)
  (cust1)-[:SHARES_IP      {timestamp: '2024-01-15', ip: '192.168.1.100'}]->(cust2),
  (cust1)-[:SHARES_PHONE   {timestamp: '2024-01-16', phone: '+63-917-000-0001'}]->(cust3),
  (cust2)-[:SHARES_ADDRESS {address: '123 Fraud St, Manila'}]->(cust3),

  // High-frequency rapid purchases by cust1
  (fraudProd1:Product {id: 901, name: 'Gift Card 1000', category: 'Gift Cards', price: 999.99}),
  (fraudProd2:Product {id: 902, name: 'Gift Card 500',  category: 'Gift Cards', price: 499.99}),

  (cust1)-[:PURCHASED {amount: 999.99, timestamp: '2024-01-15T10:00:00', order_id: 'ORD901'}]->(fraudProd1),
  (cust1)-[:PURCHASED {amount: 499.99, timestamp: '2024-01-15T10:03:00', order_id: 'ORD902'}]->(fraudProd2),
  (cust1)-[:PURCHASED {amount: 999.99, timestamp: '2024-01-15T10:06:00', order_id: 'ORD903'}]->(fraudProd1),

  (cust2)-[:PURCHASED {amount: 499.99, timestamp: '2024-01-15T10:02:00', order_id: 'ORD904'}]->(fraudProd2);

// -------------------------------------------------------------
// STEP 2: Detect shared-attribute fraud rings
//    Flag customer pairs that share 2+ identifying attributes
// -------------------------------------------------------------
MATCH (c1:Customer)-[r:SHARES_IP|SHARES_PHONE|SHARES_ADDRESS]-(c2:Customer)
WHERE id(c1) < id(c2)
WITH c1, c2, count(r) AS SharedAttributes, collect(type(r)) AS SharedTypes
WHERE SharedAttributes >= 2
RETURN c1.name        AS Customer1,
       c2.name        AS Customer2,
       SharedAttributes,
       SharedTypes    AS SuspiciousLinks,
       'Possible Identity Ring' AS Alert
ORDER BY SharedAttributes DESC;

// -------------------------------------------------------------
// STEP 3: Detect velocity fraud — rapid purchases (same customer)
//    Flag customers with 3+ purchases in the same day
// -------------------------------------------------------------
MATCH (c:Customer)-[p:PURCHASED]->(prod:Product)
WITH c,
     count(p)         AS TotalPurchases,
     sum(p.amount)    AS TotalAmount,
     collect(p.timestamp) AS PurchaseTimes
WHERE TotalPurchases >= 3
RETURN c.name         AS FlaggedCustomer,
       TotalPurchases AS PurchaseCount,
       TotalAmount    AS TotalSpent,
       PurchaseTimes  AS Timestamps,
       'High Velocity Purchases' AS Alert
ORDER BY TotalPurchases DESC;

// -------------------------------------------------------------
// STEP 4: Combine — customers in a ring AND high-velocity buying
// -------------------------------------------------------------
MATCH (c1:Customer)-[:SHARES_IP|SHARES_PHONE|SHARES_ADDRESS]-(c2:Customer)
WITH c1, c2, count(*) AS SharedAttributes
WHERE SharedAttributes >= 2
MATCH (c1)-[p:PURCHASED]->()
WITH c1, c2, SharedAttributes, count(p) AS c1Purchases
MATCH (c2)-[p2:PURCHASED]->()
WITH c1, c2, SharedAttributes,
     c1Purchases,
     count(p2) AS c2Purchases
WHERE c1Purchases >= 3 OR c2Purchases >= 3
RETURN c1.name        AS Customer1,
       c2.name        AS Customer2,
       SharedAttributes AS SuspiciousLinks,
       c1Purchases    AS C1PurchaseCount,
       c2Purchases    AS C2PurchaseCount,
       c1Purchases + c2Purchases AS TotalRapidPurchases,
       'Possible Fraud Ring' AS Alert;

// -------------------------------------------------------------
// STEP 5: BONUS — flag accounts created within 3 days of each other
//    and sharing attributes (common synthetic identity pattern)
// -------------------------------------------------------------
MATCH (c1:Customer)-[:SHARES_IP|SHARES_PHONE|SHARES_ADDRESS]-(c2:Customer)
WHERE id(c1) < id(c2)
WITH c1, c2,
     duration.between(
       date(c1.signup_date),
       date(c2.signup_date)
     ).days AS DaysBetweenSignups,
     count(*) AS SharedAttributes
WHERE abs(DaysBetweenSignups) <= 3
  AND SharedAttributes >= 1
RETURN c1.name           AS Account1,
       c2.name           AS Account2,
       DaysBetweenSignups AS SignupGapDays,
       SharedAttributes   AS SharedAttributes,
       'Synthetic Identity Risk' AS Alert;
