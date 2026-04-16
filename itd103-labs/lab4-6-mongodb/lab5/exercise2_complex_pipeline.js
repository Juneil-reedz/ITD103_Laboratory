// =============================================================
// Lab 5 – Exercise 2: Complex Aggregation Pipeline
// Customer Lifetime Value (CLV) Analysis
// Run inside mongosh
// =============================================================

use sales

// -------------------------------------------------------------
// Full 7-stage CLV pipeline
// -------------------------------------------------------------
print("--- Customer Lifetime Value Analysis ---")
db.transactions.aggregate([

  // Stage 1: Filter transactions from 2024 onward
  {
    $match: {
      date: { $gte: new Date("2024-01-01") }
    }
  },

  // Stage 2: Join customer details from 'customers' collection
  {
    $lookup: {
      from: "customers",
      localField: "customer_id",
      foreignField: "_id",
      as: "customer"
    }
  },

  // Stage 3: Flatten the customer array (1:1 join result)
  { $unwind: "$customer" },

  // Stage 4: Group by customer — aggregate spend + dates
  {
    $group: {
      _id: "$customer._id",
      customerName:     { $first: "$customer.name" },
      city:             { $first: "$customer.city" },
      totalSpent:       { $sum: "$amount" },
      transactionCount: { $sum: 1 },
      firstPurchase:    { $min: "$date" },
      lastPurchase:     { $max: "$date" }
    }
  },

  // Stage 5: Compute derived metrics
  {
    $addFields: {
      avgTransaction: {
        $divide: ["$totalSpent", "$transactionCount"]
      },
      customerSinceDays: {
        $floor: {
          $divide: [
            { $subtract: [new Date(), "$firstPurchase"] },
            1000 * 60 * 60 * 24
          ]
        }
      },
      daysSinceLastPurchase: {
        $floor: {
          $divide: [
            { $subtract: [new Date(), "$lastPurchase"] },
            1000 * 60 * 60 * 24
          ]
        }
      }
    }
  },

  // Stage 6: Sort by total spend descending
  { $sort: { totalSpent: -1 } },

  // Stage 7: Format output
  {
    $project: {
      _id: 0,
      customerName: 1,
      city: 1,
      totalSpent:        { $round: ["$totalSpent", 2] },
      transactionCount: 1,
      avgTransaction:    { $round: ["$avgTransaction", 2] },
      customerSinceDays: 1,
      daysSinceLastPurchase: 1
    }
  }
])

// -------------------------------------------------------------
// BONUS: Category preference per customer
// Which category does each customer spend most on?
// -------------------------------------------------------------
print("\n--- BONUS: Top category per customer ---")
db.transactions.aggregate([
  {
    $group: {
      _id: { customer: "$customer_id", category: "$category" },
      spent: { $sum: "$amount" }
    }
  },
  { $sort: { "_id.customer": 1, spent: -1 } },
  {
    $group: {
      _id: "$_id.customer",
      topCategory: { $first: "$_id.category" },
      topCategorySpend: { $first: "$spent" }
    }
  },
  { $sort: { _id: 1 } }
])
