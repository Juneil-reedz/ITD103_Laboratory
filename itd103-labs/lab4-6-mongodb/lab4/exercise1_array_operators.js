// =============================================================
// Lab 4 – Exercise 1: Array Operators
// Run inside mongosh
// =============================================================

use food

// -------------------------------------------------------------
// 1. Find restaurants that serve BOTH "Chinese" AND "Thai" cuisine
//    $all: every element in the array must be present
// -------------------------------------------------------------
print("--- 1. Restaurants with both Chinese and Thai cuisine ---")
db.restaurants.find(
  { cuisine: { $all: ["Chinese", "Thai"] } },
  { name: 1, cuisine: 1, _id: 0 }
)

// -------------------------------------------------------------
// 2. Find restaurants with EXACTLY 3 grades
//    $size: matches arrays of exact length
// -------------------------------------------------------------
print("\n--- 2. Restaurants with exactly 3 grades ---")
db.restaurants.find(
  { grades: { $size: 3 } },
  { name: 1, "grades": 1, _id: 0 }
)

// -------------------------------------------------------------
// 3. Find restaurants where ANY grade score is above 20
//    Dot-notation queries on array-of-objects match any element
// -------------------------------------------------------------
print("\n--- 3. Restaurants where any grade score > 20 ---")
db.restaurants.find(
  { "grades.score": { $gt: 20 } },
  { name: 1, "grades.score": 1, _id: 0 }
)

// Using $elemMatch to enforce multiple conditions on the SAME array element
print("\n--- 3b. Using $elemMatch: grade = B AND score > 20 ---")
db.restaurants.find(
  { grades: { $elemMatch: { grade: "B", score: { $gt: 20 } } } },
  { name: 1, grades: 1, _id: 0 }
)

// -------------------------------------------------------------
// 4. Update: Add "Bakery" cuisine to a restaurant using $addToSet
//    $addToSet: adds value only if it does not already exist
// -------------------------------------------------------------
print("\n--- 4. Add 'Bakery' cuisine to Morris Park Bake Shop ---")
db.restaurants.updateOne(
  { name: "Morris Park Bake Shop" },
  { $addToSet: { cuisine: "Bakery" } }
)

// Verify the update
db.restaurants.findOne(
  { name: "Morris Park Bake Shop" },
  { name: 1, cuisine: 1, _id: 0 }
)

// -------------------------------------------------------------
// BONUS: Additional array operators
// -------------------------------------------------------------

// $in: any of these cuisine values
print("\n--- BONUS: Restaurants with Italian OR Pizza cuisine ($in) ---")
db.restaurants.find(
  { cuisine: { $in: ["Italian", "Pizza"] } },
  { name: 1, cuisine: 1, _id: 0 }
)

// $nin: none of these values
print("\n--- BONUS: Restaurants NOT serving American food ($nin) ---")
db.restaurants.find(
  { cuisine: { $nin: ["American"] } },
  { name: 1, cuisine: 1, _id: 0 }
)

// $push: append a new grade to a restaurant
db.restaurants.updateOne(
  { name: "Pizza Palace" },
  {
    $push: {
      grades: {
        date: new Date(),
        grade: "A",
        score: 8
      }
    }
  }
)
print("\n--- BONUS: Pizza Palace after $push new grade ---")
db.restaurants.findOne({ name: "Pizza Palace" }, { name: 1, grades: 1, _id: 0 })

// $pull: remove grades with score > 25
db.restaurants.updateMany(
  {},
  { $pull: { grades: { score: { $gt: 25 } } } }
)
print("\n--- BONUS: After $pull grades with score > 25 ---")
db.restaurants.find(
  {},
  { name: 1, "grades.score": 1, _id: 0 }
)
