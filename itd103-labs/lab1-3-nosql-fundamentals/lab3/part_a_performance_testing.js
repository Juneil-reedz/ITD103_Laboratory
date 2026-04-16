// =============================================================
// Lab 3 – Part A: Performance Testing (No Indexes)
// Run inside mongosh
// =============================================================

use performance_lab

// =============================================================
// STEP 1: Generate 100,000 test documents
// =============================================================

function generateProducts(count) {
  const products = []
  for (let i = 0; i < count; i++) {
    products.push({
      product_id: i,
      name: `Product ${i}`,
      category: `Category ${Math.floor(Math.random() * 10)}`,
      price: Math.round(Math.random() * 1000 * 100) / 100,
      stock: Math.floor(Math.random() * 1000),
      tags: Array.from(
        { length: 5 },
        () => `tag${Math.floor(Math.random() * 50)}`
      ),
      created_at: new Date()
    })
  }
  return products
}

// Drop existing collection to start fresh
db.products.drop()

// Insert in batches of 10,000 to avoid memory issues
print("Inserting 100,000 documents...")
for (let batch = 0; batch < 10; batch++) {
  db.products.insertMany(generateProducts(10000))
  print(`Batch ${batch + 1}/10 inserted`)
}

print("Total documents:", db.products.countDocuments())

// =============================================================
// STEP 2: Baseline queries WITHOUT indexes
// Check: executionStats.totalDocsExamined and executionTimeMillis
// =============================================================

print("\n--- QUERY 1: Filter by category (no index) ---")
db.products.find({ category: "Category 5" }).explain("executionStats")

print("\n--- QUERY 2: Range query on price (no index) ---")
db.products.find({ price: { $gt: 500 } }).explain("executionStats")

print("\n--- QUERY 3: Array field search on tags (no index) ---")
db.products.find({ tags: "tag25" }).explain("executionStats")

print("\n--- QUERY 4: Compound filter (no index) ---")
db.products.find({
  category: "Category 3",
  price: { $lt: 300 }
}).explain("executionStats")

// =============================================================
// STEP 3: Record baseline results
// Key metrics to note from executionStats:
//   - executionTimeMillisEstimate
//   - totalDocsExamined   (should equal ~100,000 — full scan)
//   - totalKeysExamined   (should be 0 — no index used)
//   - stage              (should be "COLLSCAN")
// =============================================================
