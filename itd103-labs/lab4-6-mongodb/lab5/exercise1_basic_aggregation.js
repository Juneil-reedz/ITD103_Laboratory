// =============================================================
// Lab 5 – Exercise 1: Basic Aggregation
// Run inside mongosh
// =============================================================

use sales

// -------------------------------------------------------------
// 1. Total sales per category (sorted highest first)
// -------------------------------------------------------------
print("--- 1. Total sales per category ---")
db.transactions.aggregate([
  {
    $group: {
      _id: "$category",
      totalSales: { $sum: "$amount" },
      transactionCount: { $sum: 1 }
    }
  },
  { $sort: { totalSales: -1 } }
])

// -------------------------------------------------------------
// 2. Average transaction amount per month
// -------------------------------------------------------------
print("\n--- 2. Average transaction amount per month ---")
db.transactions.aggregate([
  {
    $group: {
      _id: {
        year:  { $year:  "$date" },
        month: { $month: "$date" }
      },
      avgAmount: { $avg: "$amount" },
      count: { $sum: 1 }
    }
  },
  { $sort: { "_id.year": 1, "_id.month": 1 } }
])

// -------------------------------------------------------------
// 3. BONUS: Sales by region
// -------------------------------------------------------------
print("\n--- 3. Total sales by region ---")
db.transactions.aggregate([
  {
    $group: {
      _id: "$region",
      totalSales: { $sum: "$amount" },
      avgSale: { $avg: "$amount" },
      count: { $sum: 1 }
    }
  },
  { $sort: { totalSales: -1 } }
])

// -------------------------------------------------------------
// 4. BONUS: Top 5 best-selling products
// -------------------------------------------------------------
print("\n--- 4. Top 5 best-selling products by revenue ---")
db.transactions.aggregate([
  {
    $group: {
      _id: "$product",
      revenue: { $sum: "$amount" },
      unitsSold: { $sum: 1 }
    }
  },
  { $sort: { revenue: -1 } },
  { $limit: 5 },
  {
    $project: {
      product: "$_id",
      revenue: { $round: ["$revenue", 2] },
      unitsSold: 1,
      _id: 0
    }
  }
])

// -------------------------------------------------------------
// 5. BONUS: $bucket — group transactions into price ranges
// -------------------------------------------------------------
print("\n--- 5. Transactions bucketed by amount ---")
db.transactions.aggregate([
  {
    $bucket: {
      groupBy: "$amount",
      boundaries: [0, 50, 100, 200, 500, 1500],
      default: "Other",
      output: {
        count: { $sum: 1 },
        totalRevenue: { $sum: "$amount" }
      }
    }
  }
])
