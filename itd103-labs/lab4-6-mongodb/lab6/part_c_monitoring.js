// =============================================================
// Lab 6 – Part C: Performance Monitoring
// Run inside mongosh (on primary or mongos)
// =============================================================

use sharded_db   // or any active database

// -------------------------------------------------------------
// 1. View currently running operations
//    Useful for identifying slow or hung queries
// -------------------------------------------------------------
print("--- 1. Current Operations ---")
db.currentOp()

// Filter: only show operations running longer than 1 second
db.currentOp({ "active": true, "secs_running": { $gt: 1 } })

// Kill a specific operation by opid (replace 12345 with actual opid)
// db.killOp(12345)

// -------------------------------------------------------------
// 2. Database and collection statistics
// -------------------------------------------------------------
print("\n--- 2. Database Stats ---")
db.stats()

print("\n--- 2b. Collection Stats ---")
db.orders.stats()

// Key fields to note:
//   count          — total documents
//   size           — data size in bytes
//   storageSize    — on-disk size
//   totalIndexSize — total size of all indexes
//   nindexes       — number of indexes

// -------------------------------------------------------------
// 3. Explain query — see execution plan and timing
// -------------------------------------------------------------
print("\n--- 3. Explain query execution ---")
db.orders.find({ customer_id: "CUST0500" }).explain("executionStats")

// Fields to review in output:
//   executionStats.executionTimeMillis   — total ms
//   executionStats.totalDocsExamined     — documents scanned
//   executionStats.totalKeysExamined     — index keys scanned
//   winningPlan.stage                    — IXSCAN vs COLLSCAN

// -------------------------------------------------------------
// 4. Index usage statistics
// -------------------------------------------------------------
print("\n--- 4. Index Usage Stats ---")
db.orders.aggregate([{ $indexStats: {} }])

// Fields: name, ops (times used), since (when stats were reset)

// -------------------------------------------------------------
// 5. Query profiler — log slow queries
// Profiling levels:
//   0 = off
//   1 = log queries slower than slowms threshold
//   2 = log ALL operations (use only for debugging — heavy overhead)
// -------------------------------------------------------------
print("\n--- 5. Enable Query Profiler (log queries > 100ms) ---")
db.setProfilingLevel(1, { slowms: 100 })

// Run a query to generate profiler data
db.orders.find({ amount: { $gt: 900 } }).toArray()

// Read profiler output (most recent 5 entries)
print("\n--- 5b. Recent slow query log entries ---")
db.system.profile.find().sort({ ts: -1 }).limit(5).pretty()

// Turn off profiler when done
db.setProfilingLevel(0)

// -------------------------------------------------------------
// 6. Server status — broad system-level metrics
// -------------------------------------------------------------
print("\n--- 6. Server Status (connections + memory) ---")
const status = db.serverStatus()

printjson({
  connections: status.connections,
  memory: status.mem,
  opcounters: status.opcounters,   // insert/query/update/delete counts
  uptime: status.uptime
})

// -------------------------------------------------------------
// 7. BONUS: Identify large collections / index bloat
// -------------------------------------------------------------
print("\n--- 7. All collections with stats ---")
db.getCollectionNames().forEach(name => {
  const s = db.getCollection(name).stats()
  print(`${name}: docs=${s.count}, dataSize=${s.size}B, indexSize=${s.totalIndexSize}B`)
})
