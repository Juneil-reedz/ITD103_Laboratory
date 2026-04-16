// =============================================================
// Lab 5 – Exercise 3: Facets & Buckets
// Multi-dimensional analysis in a single aggregation pass
// Run inside mongosh
// =============================================================

use sales

// -------------------------------------------------------------
// $facet: run multiple independent sub-pipelines simultaneously
// Each facet is a named key with its own pipeline array
// -------------------------------------------------------------
print("--- Multi-faceted Sales Analysis ---")
db.transactions.aggregate([
  {
    $facet: {

      // Facet 1: Total revenue by category
      "byCategory": [
        { $group: { _id: "$category", total: { $sum: "$amount" } } },
        { $sort: { total: -1 } }
      ],

      // Facet 2: Monthly sales trend
      "byMonth": [
        {
          $group: {
            _id: { $month: "$date" },
            total: { $sum: "$amount" },
            count: { $sum: 1 }
          }
        },
        { $sort: { _id: 1 } }
      ],

      // Facet 3: Top 10 customers by spending
      "topCustomers": [
        { $group: { _id: "$customer_id", total: { $sum: "$amount" } } },
        { $sort: { total: -1 } },
        { $limit: 10 }
      ],

      // Facet 4: Summary statistics across all transactions
      "summary": [
        {
          $group: {
            _id: null,
            totalSales:       { $sum: "$amount" },
            avgSale:          { $avg: "$amount" },
            minSale:          { $min: "$amount" },
            maxSale:          { $max: "$amount" },
            transactionCount: { $sum: 1 }
          }
        },
        {
          $project: {
            _id: 0,
            totalSales:       { $round: ["$totalSales", 2] },
            avgSale:          { $round: ["$avgSale", 2] },
            minSale: 1,
            maxSale: 1,
            transactionCount: 1
          }
        }
      ],

      // Facet 5: Sales by region
      "byRegion": [
        { $group: { _id: "$region", total: { $sum: "$amount" }, count: { $sum: 1 } } },
        { $sort: { total: -1 } }
      ]
    }
  }
])

// -------------------------------------------------------------
// $bucketAuto: automatically determine bucket boundaries
// Useful when you don't know the data distribution up front
// -------------------------------------------------------------
print("\n--- $bucketAuto: Auto-grouped price ranges (5 buckets) ---")
db.transactions.aggregate([
  {
    $bucketAuto: {
      groupBy: "$amount",
      buckets: 5,
      output: {
        count: { $sum: 1 },
        totalRevenue: { $sum: "$amount" },
        avgAmount:    { $avg: "$amount" }
      }
    }
  }
])

// -------------------------------------------------------------
// $sortByCount shorthand: group + sort by count in one stage
// -------------------------------------------------------------
print("\n--- $sortByCount: Most common categories ---")
db.transactions.aggregate([
  { $unwind: "$category" },
  { $sortByCount: "$category" }
])

// -------------------------------------------------------------
// BONUS: $setWindowFields — running total of sales over time
// Requires MongoDB 5.0+
// -------------------------------------------------------------
print("\n--- BONUS: Running total of sales (by date) ---")
db.transactions.aggregate([
  { $sort: { date: 1 } },
  {
    $setWindowFields: {
      sortBy: { date: 1 },
      output: {
        runningTotal: {
          $sum: "$amount",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  {
    $project: {
      _id: 0,
      date: 1,
      amount: 1,
      category: 1,
      runningTotal: { $round: ["$runningTotal", 2] }
    }
  }
])
