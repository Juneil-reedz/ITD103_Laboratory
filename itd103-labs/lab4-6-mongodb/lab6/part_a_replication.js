// =============================================================
// Lab 6 – Part A: Replica Set Configuration & Testing
// Connect to primary first: mongosh --port 27017
// =============================================================

// -------------------------------------------------------------
// STEP 1: Initiate the replica set
// -------------------------------------------------------------
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017" },                       // Primary
    { _id: 1, host: "localhost:27018" },                       // Secondary
    { _id: 2, host: "localhost:27019", arbiterOnly: true }     // Arbiter
  ]
})

// Wait a few seconds for election, then check status
rs.status()

// -------------------------------------------------------------
// STEP 2: Inspect replica set configuration
// -------------------------------------------------------------
rs.conf()

// Check which member is primary
rs.isMaster()   // or rs.hello() in MongoDB 5+

// -------------------------------------------------------------
// STEP 3: Test replication — write on primary, read on secondary
// -------------------------------------------------------------

// Write on primary (port 27017)
use replication_test
db.messages.insertOne({ msg: "Hello from primary", ts: new Date() })

// On secondary (open new mongosh --port 27018):
//   rs.secondaryOk()          -- allow reads on secondary
//   use replication_test
//   db.messages.find()        -- should see the document

// -------------------------------------------------------------
// STEP 4: Test failover
// -------------------------------------------------------------

// Simulate primary stepping down (triggers re-election)
rs.stepDown()       // primary gives up role

// Check who became new primary
rs.status()         // look for "stateStr": "PRIMARY"

// Re-connect to the new primary port if needed
// mongosh --port 27018   (or whichever port was elected)

// -------------------------------------------------------------
// STEP 5: Write concern — ensure replication before acknowledging
// -------------------------------------------------------------

use replication_test

// w: "majority" means write is confirmed on >50% of voting members
db.messages.insertOne(
  { msg: "Durable write", ts: new Date() },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
)

// Read concern — only return data acknowledged by majority
db.messages.find().readConcern("majority")
