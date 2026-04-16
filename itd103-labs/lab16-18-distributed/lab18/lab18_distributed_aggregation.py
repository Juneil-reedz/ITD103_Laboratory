# =============================================================
# Lab 18 – Exercise 2: Distributed Aggregation Pipelines
# Demonstrates advanced aggregation, map-reduce patterns,
# and horizontal scaling strategies.
# Run: python lab18_distributed_aggregation.py
# =============================================================

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timezone, timedelta
import time
import random
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt

MONGO_URI = "mongodb://localhost:27017"


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


class DistributedAggregation:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        try:
            self.client.admin.command("ping")
        except Exception as exc:
            raise SystemExit(f"Cannot reach MongoDB: {exc}")

        self.db = self.client.distributed_agg
        self._setup()

    # ── Dataset ────────────────────────────────────────────
    def _setup(self):
        self.db.orders.drop()
        self.db.products.drop()
        self.db.customers.drop()

        base_date = datetime(2024, 1, 1)
        REGIONS   = ["North", "South", "East", "West", "Central"]
        CATS      = ["Electronics", "Clothing", "Food", "Books", "Sports"]
        STATUSES  = ["completed", "pending", "shipped", "cancelled"]

        random.seed(42)

        products = [
            {
                "_id":      i,
                "name":     f"Product_{i}",
                "category": CATS[i % len(CATS)],
                "price":    round(random.uniform(5, 500), 2),
                "cost":     round(random.uniform(2, 250), 2),
            }
            for i in range(500)
        ]
        self.db.products.insert_many(products)

        customers = [
            {
                "_id":    i,
                "name":   f"Customer_{i}",
                "region": REGIONS[i % len(REGIONS)],
                "tier":   ["Gold", "Silver", "Bronze"][i % 3],
            }
            for i in range(5_000)
        ]
        self.db.customers.insert_many(customers)

        orders = [
            {
                "_id":         i,
                "customer_id": i % 5_000,
                "product_id":  i % 500,
                "quantity":    random.randint(1, 20),
                "price":       round(random.uniform(5, 500), 2),
                "status":      STATUSES[i % 4],
                "order_date":  base_date + timedelta(days=i % 365),
                "region":      REGIONS[i % len(REGIONS)],
            }
            for i in range(50_000)
        ]
        self.db.orders.insert_many(orders)

        print("Dataset created:")
        print(f"  products  : {self.db.products.count_documents({})}")
        print(f"  customers : {self.db.customers.count_documents({})}")
        print(f"  orders    : {self.db.orders.count_documents({})}")

    # ── A: Revenue by region ───────────────────────────────
    def revenue_by_region(self):
        section("A. Revenue by Region (parallel partition pattern)")

        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {
                "_id":       "$region",
                "revenue":   {"$sum": {"$multiply": ["$price", "$quantity"]}},
                "orders":    {"$sum": 1},
                "avg_order": {"$avg": {"$multiply": ["$price", "$quantity"]}},
            }},
            {"$sort": {"revenue": DESCENDING}},
        ]

        start   = time.perf_counter()
        results = list(self.db.orders.aggregate(pipeline))
        elapsed = (time.perf_counter() - start) * 1000

        print(f"\n  Execution time: {elapsed:.1f} ms")
        print(f"\n  {'Region':<12} {'Revenue':>12} {'Orders':>8} {'Avg Order':>12}")
        print("  " + "-" * 46)
        for r in results:
            print(
                f"  {r['_id']:<12} "
                f"${r['revenue']:>11,.2f} "
                f"{r['orders']:>8,} "
                f"${r['avg_order']:>11,.2f}"
            )
        return results

    # ── B: Product category performance ────────────────────
    def category_performance(self):
        section("B. Product Category Performance ($lookup join)")

        pipeline = [
            {"$match": {"status": "completed"}},
            {"$lookup": {
                "from":         "products",
                "localField":   "product_id",
                "foreignField": "_id",
                "as":           "product",
            }},
            {"$unwind": "$product"},
            {"$group": {
                "_id":     "$product.category",
                "revenue": {"$sum": {"$multiply": ["$price", "$quantity"]}},
                "units":   {"$sum": "$quantity"},
                "orders":  {"$sum": 1},
            }},
            {"$sort": {"revenue": DESCENDING}},
        ]

        start   = time.perf_counter()
        results = list(self.db.orders.aggregate(pipeline))
        elapsed = (time.perf_counter() - start) * 1000

        print(f"\n  Execution time (with $lookup): {elapsed:.1f} ms")
        print(f"\n  {'Category':<14} {'Revenue':>12} {'Units':>8} {'Orders':>8}")
        print("  " + "-" * 46)
        for r in results:
            print(
                f"  {r['_id']:<14} "
                f"${r['revenue']:>11,.2f} "
                f"{r['units']:>8,} "
                f"{r['orders']:>8,}"
            )
        return results

    # ── C: Time-series monthly aggregation ─────────────────
    def monthly_trend(self):
        section("C. Monthly Revenue Trend (time-bucket aggregation)")

        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {
                "_id": {
                    "year":  {"$year":  "$order_date"},
                    "month": {"$month": "$order_date"},
                },
                "revenue": {"$sum": {"$multiply": ["$price", "$quantity"]}},
                "orders":  {"$sum": 1},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]

        results = list(self.db.orders.aggregate(pipeline))
        print(f"\n  {'Month':<12} {'Revenue':>12} {'Orders':>8}")
        print("  " + "-" * 34)
        for r in results[:12]:      # first 12 months
            m = f"{r['_id']['year']}-{r['_id']['month']:02d}"
            print(f"  {m:<12} ${r['revenue']:>11,.2f} {r['orders']:>8,}")

        return results

    # ── D: Map-reduce pattern (manual simulation) ──────────
    def map_reduce_pattern(self):
        section("D. Map-Reduce Pattern (emulated with $group + merge)")

        # Phase 1 – MAP: emit (region, revenue) per order
        # Phase 2 – REDUCE: sum revenue per region
        # Phase 3 – MERGE: write results to summary collection

        self.db.region_summary.drop()

        pipeline = [
            {"$match": {"status": "completed"}},
            # Map: project just the fields we need
            {"$project": {
                "region":  1,
                "revenue": {"$multiply": ["$price", "$quantity"]},
            }},
            # Reduce: group and sum
            {"$group": {
                "_id":     "$region",
                "revenue": {"$sum": "$revenue"},
                "count":   {"$sum": 1},
            }},
            # Merge output into a summary collection
            {"$merge": {
                "into":           "region_summary",
                "whenMatched":    "replace",
                "whenNotMatched": "insert",
            }},
        ]

        start = time.perf_counter()
        list(self.db.orders.aggregate(pipeline))   # runs the merge
        elapsed = (time.perf_counter() - start) * 1000

        results = list(self.db.region_summary.find().sort("revenue", DESCENDING))
        print(f"\n  Map-reduce completed in {elapsed:.1f} ms")
        print(f"  Results written to 'region_summary' collection:")
        for r in results:
            print(f"    {r['_id']:<12}  revenue=${r['revenue']:,.2f}  orders={r['count']}")

        return results

    # ── E: Aggregation with index optimization ─────────────
    def optimized_vs_unoptimized(self):
        section("E. Aggregation: Optimized vs Unoptimized")

        # Create a covering index
        idx_name = self.db.orders.create_index(
            [("status", ASCENDING), ("region", ASCENDING), ("price", ASCENDING), ("quantity", ASCENDING)]
        )

        pipeline = [
            {"$match": {"status": "completed", "region": "North"}},
            {"$group": {
                "_id":     "$region",
                "revenue": {"$sum": {"$multiply": ["$price", "$quantity"]}},
                "orders":  {"$sum": 1},
            }},
        ]

        # Without hint
        start      = time.perf_counter()
        list(self.db.orders.aggregate(pipeline))
        no_idx_ms  = (time.perf_counter() - start) * 1000

        # With hint (force our covering index)
        start      = time.perf_counter()
        list(self.db.orders.aggregate(pipeline, hint=idx_name))
        idx_ms     = (time.perf_counter() - start) * 1000

        self.db.orders.drop_index(idx_name)

        print(f"\n  Without index hint : {no_idx_ms:.1f} ms")
        print(f"  With covering index: {idx_ms:.1f} ms")
        improvement = (no_idx_ms - idx_ms) / no_idx_ms * 100 if no_idx_ms else 0
        print(f"  Improvement        : {improvement:.1f}%")

    # ── F: Summary dashboard chart ─────────────────────────
    def generate_dashboard(self, region_data, category_data, monthly_data):
        section("F. Aggregation Dashboard")

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        # Revenue by region
        regions  = [r["_id"] for r in region_data]
        rev_reg  = [r["revenue"] / 1_000 for r in region_data]   # in thousands
        axes[0].bar(regions, rev_reg, color="steelblue", alpha=0.8)
        axes[0].set_title("Revenue by Region ($K)")
        axes[0].set_ylabel("Revenue ($K)")
        axes[0].grid(axis="y", alpha=0.3)

        # Revenue by category
        cats     = [r["_id"] for r in category_data]
        rev_cat  = [r["revenue"] / 1_000 for r in category_data]
        axes[1].barh(cats, rev_cat, color="seagreen", alpha=0.8)
        axes[1].set_title("Revenue by Category ($K)")
        axes[1].set_xlabel("Revenue ($K)")
        axes[1].grid(axis="x", alpha=0.3)

        # Monthly trend
        months   = [f"{r['_id']['month']:02d}" for r in monthly_data[:12]]
        rev_mon  = [r["revenue"] / 1_000 for r in monthly_data[:12]]
        axes[2].plot(months, rev_mon, marker="o", color="darkorange", linewidth=2)
        axes[2].fill_between(months, rev_mon, alpha=0.2, color="darkorange")
        axes[2].set_title("Monthly Revenue Trend ($K)")
        axes[2].set_xlabel("Month")
        axes[2].set_ylabel("Revenue ($K)")
        axes[2].grid(alpha=0.3)

        plt.suptitle("Distributed Aggregation Dashboard", fontsize=14)
        plt.tight_layout()
        out = "aggregation_dashboard.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        print(f"\n  Dashboard saved -> {out}")
    

# ── Entry point ────────────────────────────────────────────
if __name__ == "__main__":
    agg = DistributedAggregation()

    region_data   = agg.revenue_by_region()
    category_data = agg.category_performance()
    monthly_data  = agg.monthly_trend()
    agg.map_reduce_pattern()
    agg.optimized_vs_unoptimized()
    agg.generate_dashboard(region_data, category_data, monthly_data)

    agg.client.close()
    print("\nDistributed aggregation exercises complete.")
