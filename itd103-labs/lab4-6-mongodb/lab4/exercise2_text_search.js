// =============================================================
// Lab 4 – Exercise 2: Text Search
// Run inside mongosh
// =============================================================

use food

// -------------------------------------------------------------
// 1. Create a text index on name and address.street
//    Only one text index is allowed per collection
// -------------------------------------------------------------
print("--- Creating text index ---")
db.restaurants.createIndex(
  { name: "text", "address.street": "text" },
  { name: "restaurant_text_index" }
)

// Verify index was created
db.restaurants.getIndexes()

// -------------------------------------------------------------
// 2. Text search: find documents matching "bakery shop"
//    - Returns docs where name or street contains "bakery" OR "shop"
//    - Ranked by textScore (relevance)
// -------------------------------------------------------------
print("\n--- 2. Text search: 'bakery shop' ---")
db.restaurants.find(
  { $text: { $search: "bakery shop" } },
  { score: { $meta: "textScore" }, name: 1, _id: 0 }
).sort({ score: { $meta: "textScore" } })

// Exact phrase search using quoted string
print("\n--- 2b. Exact phrase: 'Bake Shop' ---")
db.restaurants.find(
  { $text: { $search: "\"Bake Shop\"" } },
  { score: { $meta: "textScore" }, name: 1, _id: 0 }
)

// Exclude a term: "bakery" but NOT "coffee"
print("\n--- 2c. Text search: bakery but NOT coffee ---")
db.restaurants.find(
  { $text: { $search: "bakery -coffee" } },
  { score: { $meta: "textScore" }, name: 1, _id: 0 }
)

// -------------------------------------------------------------
// 3. Case-insensitive regex search on name
//    Regex does NOT use text index — use for pattern matching only
// -------------------------------------------------------------
print("\n--- 3. Regex search: /pizza/i ---")
db.restaurants.find(
  { name: { $regex: /pizza/i } },
  { name: 1, cuisine: 1, _id: 0 }
)

// Starts-with pattern (more efficient — anchored to start)
print("\n--- 3b. Regex: starts with 'Dragon' ---")
db.restaurants.find(
  { name: { $regex: /^Dragon/i } },
  { name: 1, _id: 0 }
)

// Contains pattern on street
print("\n--- 3c. Regex on address.street: contains 'Ave' ---")
db.restaurants.find(
  { "address.street": { $regex: /Ave/i } },
  { name: 1, "address.street": 1, _id: 0 }
)
