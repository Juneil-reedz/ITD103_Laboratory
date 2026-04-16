// =============================================================
// Lab 6 – Part B: Sharding Configuration & Testing
// Connect via mongos: mongosh --port 27023
// =============================================================

// -------------------------------------------------------------
// STEP 1: Add shards to the cluster
// -------------------------------------------------------------
sh.addShard("localhost:27020")
sh.addShard("localhost:27021")

// Verify shards were added
sh.status()

// -------------------------------------------------------------
// STEP 2: Enable sharding on a database
// -------------------------------------------------------------
sh.enableSharding("sharded_db")

// -------------------------------------------------------------
// STEP 3: Create a shard key and shard the collection
// Shard key choice matters — it determines data distribution
//   Range sharding: { customer_id: 1 }  — sequential, good for range queries
//   Hash sharding:  { customer_id: "hashed" } — even distribution
// -------------------------------------------------------------

// Option A: Range-based shard key
sh.shardCollection("sharded_db.orders", { customer_id: 1 })

// Option B: Hash-based shard key (better distribution for random inserts)
// sh.shardCollection("sharded_db.orders", { customer_id: "hashed" })

// -------------------------------------------------------------
// STEP 4: Insert test data and verify distribution
// -------------------------------------------------------------
use sharded_db

for (let i = 0; i < 10000; i++) {
  db.orders.insertOne({
    customer_id: `CUST${Math.floor(Math.random() * 1000).toString().padStart(4, "0")}`,
    order_date: new Date(),
    amount: Math.round(Math.random() * 1000 * 100) / 100,
    items: Array.from(
      { length: Math.floor(Math.random() * 5) + 1 },
      () => `item${Math.floor(Math.random() * 100)}`
    ),
    region: ["North", "South", "East", "West"][Math.floor(Math.random() * 4)]
  })
}

// Check how data is distributed across shards
db.orders.getShardDistribution()

// -------------------------------------------------------------
// STEP 5: Verify routing — explain shows which shard(s) are hit
// -------------------------------------------------------------

// Targeted query (hits one shard — uses shard key)
db.orders.find({ customer_id: "CUST0500" }).explain("executionStats")

// Scatter-gather query (hits all shards — no shard key in filter)
db.orders.find({ amount: { $gt: 800 } }).explain("executionStats")

// -------------------------------------------------------------
// STEP 6: Chunk management
// -------------------------------------------------------------
sh.status()           // shows chunk distribution per shard

// Move a chunk manually (advanced — usually done automatically by balancer)
// sh.moveChunk("sharded_db.orders", { customer_id: "CUST0500" }, "shard2")
