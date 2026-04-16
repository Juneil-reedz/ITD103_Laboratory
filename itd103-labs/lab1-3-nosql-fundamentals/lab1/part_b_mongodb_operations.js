// =============================================================
// Lab 1 – Part B: MongoDB Basic Operations
// Run these commands inside mongosh
// =============================================================

// -------------------------------------------------------------
// STEP 1: Start MongoDB (run in terminal, not mongosh)
// mongod --dbpath ./data --port 27017
//
// STEP 2: Connect (run in terminal)
// mongosh
// -------------------------------------------------------------

// -------------------------------------------------------------
// 1. Create / switch to database
// -------------------------------------------------------------
use lab1_database

// -------------------------------------------------------------
// 2. Create collection
// -------------------------------------------------------------
db.createCollection("users")

// -------------------------------------------------------------
// 3. Insert documents
// -------------------------------------------------------------
db.users.insertMany([
  {
    name: "Alice",
    age: 25,
    city: "Manila",
    interests: ["coding", "reading"]
  },
  {
    name: "Bob",
    age: 30,
    city: "Cebu",
    interests: ["gaming", "music"]
  },
  {
    name: "Charlie",
    age: 22,
    city: "Davao",
    interests: ["sports", "travel"]
  }
])

// -------------------------------------------------------------
// 4. Query all documents
// -------------------------------------------------------------
db.users.find()

// Pretty-print version
db.users.find().pretty()

// -------------------------------------------------------------
// 5. Query by city
// -------------------------------------------------------------
db.users.find({ city: "Manila" })

// -------------------------------------------------------------
// 6. Query by age (greater than 25)
// -------------------------------------------------------------
db.users.find({ age: { $gt: 25 } })

// -------------------------------------------------------------
// 7. Bonus queries
// -------------------------------------------------------------

// Count total documents
db.users.countDocuments()

// Find one document
db.users.findOne({ name: "Alice" })

// Project specific fields (name and city only, exclude _id)
db.users.find({}, { name: 1, city: 1, _id: 0 })

// Sort by age descending
db.users.find().sort({ age: -1 })

// Update a document
db.users.updateOne(
  { name: "Alice" },
  { $set: { city: "Quezon City" }, $push: { interests: "hiking" } }
)

// Verify update
db.users.findOne({ name: "Alice" })

// Delete a document
db.users.deleteOne({ name: "Charlie" })

// Verify deletion
db.users.countDocuments()
