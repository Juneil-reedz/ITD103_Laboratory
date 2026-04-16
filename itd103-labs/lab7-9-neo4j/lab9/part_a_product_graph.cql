// =============================================================
// Lab 9 – Part A: Build E-Commerce Product Graph
// Paste into Neo4j Browser or run via cypher-shell
// =============================================================

// Clear previous data
MATCH (n) DETACH DELETE n;

// -------------------------------------------------------------
// Create the full e-commerce graph in one statement
// -------------------------------------------------------------
CREATE
  // Products
  (p1:Product {id: 1, name: 'Laptop',            category: 'Electronics', price: 999.99}),
  (p2:Product {id: 2, name: 'Smartphone',         category: 'Electronics', price: 699.99}),
  (p3:Product {id: 3, name: 'Headphones',         category: 'Electronics', price: 199.99}),
  (p4:Product {id: 4, name: 'Book: MongoDB Guide', category: 'Books',       price: 49.99}),
  (p5:Product {id: 5, name: 'Book: Neo4j Guide',   category: 'Books',       price: 59.99}),
  (p6:Product {id: 6, name: 'T-Shirt',             category: 'Clothing',    price: 29.99}),

  // Customers
  (c1:Customer {id: 101, name: 'Alice',   segment: 'Premium'}),
  (c2:Customer {id: 102, name: 'Bob',     segment: 'Regular'}),
  (c3:Customer {id: 103, name: 'Charlie', segment: 'Premium'}),

  // Frequently bought together
  (p1)-[:BOUGHT_WITH {frequency: 150}]->(p3),
  (p1)-[:BOUGHT_WITH {frequency: 75}]->(p4),
  (p2)-[:BOUGHT_WITH {frequency: 200}]->(p3),
  (p4)-[:BOUGHT_WITH {frequency: 50}]->(p5),

  // Customer purchases
  (c1)-[:PURCHASED {date: '2024-01-15', quantity: 1}]->(p1),
  (c1)-[:PURCHASED {date: '2024-01-15', quantity: 1}]->(p3),
  (c1)-[:PURCHASED {date: '2024-02-20', quantity: 1}]->(p4),
  (c2)-[:PURCHASED {date: '2024-01-20', quantity: 1}]->(p2),
  (c2)-[:PURCHASED {date: '2024-01-20', quantity: 1}]->(p3),
  (c3)-[:PURCHASED {date: '2024-03-01', quantity: 2}]->(p5),

  // Views (browsed but not yet bought)
  (c3)-[:VIEWED {timestamp: '2024-03-05'}]->(p4),
  (c2)-[:VIEWED {timestamp: '2024-03-10'}]->(p1),
  (c1)-[:VIEWED {timestamp: '2024-03-12'}]->(p2);

// Verify
MATCH (n)
RETURN labels(n)[0] AS Label, count(*) AS Count;

MATCH ()-[r]->()
RETURN type(r) AS RelType, count(*) AS Count;
