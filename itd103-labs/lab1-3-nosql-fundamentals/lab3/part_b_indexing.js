// =============================================================
// Lab 3 – Part B: Indexing & Optimization
// Run inside mongosh (after part_a_performance_testing.js)
// =============================================================

use performance_lab

// =============================================================
// STEP 1: Create Indexes
// =============================================================

// Single-field index on category
db.products.createIndex({ category: 1 })
print("Created: single-field index on category")

// Compound index on category + price (descending price for range queries)
db.products.createIndex({ category: 1, price: -1 })
print("Created: compound index on category + price")

// Multikey index on tags array
db.products.createIndex({ tags: 1 })
print("Created: multikey index on tags")

// Text index on name field for full-text search
db.products.createIndex({ name: "text" })
print("Created: text index on name")

// View all indexes
print("\n--- All Indexes ---")
db.products.getIndexes()

// =============================================================
// STEP 2: Re-test queries WITH indexes
// Compare: stage should change from COLLSCAN → IXSCAN
// =============================================================

print("\n--- QUERY 1: Filter by category (with index) ---")
db.products
  .find({ category: "Category 5" })
  .hint({ category: 1 })
  .explain("executionStats")

print("\n--- QUERY 2: Range query on price (with compound index) ---")
db.products
  .find({ price: { $gt: 500 } })
  .hint({ category: 1, price: -1 })
  .explain("executionStats")

print("\n--- QUERY 3: Array field search on tags (with multikey index) ---")
db.products
  .find({ tags: "tag25" })
  .hint({ tags: 1 })
  .explain("executionStats")

print("\n--- QUERY 4: Compound filter (uses compound index) ---")
db.products
  .find({ category: "Category 3", price: { $lt: 300 } })
  .hint({ category: 1, price: -1 })
  .explain("executionStats")

print("\n--- QUERY 5: Full-text search on name ---")
db.products
  .find({ $text: { $search: "Product" } })
  .explain("executionStats")

// =============================================================
// STEP 3: Index & Collection Statistics
// =============================================================

print("\n--- Collection Stats ---")
db.products.stats()

print("\n--- Index Sizes ---")
const stats = db.products.stats()
printjson(stats.indexSizes)

// =============================================================
// STEP 4: Query Optimization Example
// MongoDB query planner automatically picks the best index.
// Use hint() only when you need to force a specific index.
// =============================================================

// Optimized compound query (planner selects compound index automatically)
db.products.find({
  category: "Category 5",
  price: { $gt: 500 }
}).explain("executionStats")

// Check which index the planner chose (winningPlan.inputStage.indexName)

// =============================================================
// STEP 5: Performance Comparison Summary
// Fill in values observed from executionStats above
// =============================================================

/*
+------------------+------------------+----------------+------------------+------------------+
| Query            | Stage (before)   | Time ms (before)| Stage (after)   | Time ms (after)  |
+------------------+------------------+----------------+------------------+------------------+
| category filter  | COLLSCAN         | ???            | IXSCAN           | ???              |
| price > 500      | COLLSCAN         | ???            | IXSCAN           | ???              |
| tags = tag25     | COLLSCAN         | ???            | IXSCAN           | ???              |
| category+price   | COLLSCAN         | ???            | IXSCAN           | ???              |
+------------------+------------------+----------------+------------------+------------------+

Key Observations:
- COLLSCAN examines ALL ~100,000 documents
- IXSCAN examines only documents matching the index key
- Compound index covers both category filter + price sort in one pass
- Multikey index handles array field queries efficiently
- Text index enables keyword search without regex (which bypasses indexes)

Recommendations:
1. Always index fields used in frequent WHERE / find() conditions
2. Prefer compound indexes over multiple single-field indexes for multi-condition queries
3. Avoid over-indexing — each index slows down writes (INSERT/UPDATE/DELETE)
4. Monitor index usage with: db.products.aggregate([{ $indexStats: {} }])
5. Remove unused indexes: db.products.dropIndex("<index_name>")
*/

// =============================================================
// BONUS: Check index usage statistics
// =============================================================
db.products.aggregate([{ $indexStats: {} }])

// Remove a specific index (example)
// db.products.dropIndex("category_1")
