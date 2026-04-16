# =============================================================
# Lab 16 – Exercise 3: Distributed Query Optimization
# Run: python lab16_query_optimization.py
# (Works against a standalone mongod or a replica set on 27017)
# =============================================================

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
import time
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt

MONGO_URI = "mongodb://localhost:27017"


class QueryOptimizer:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        try:
            self.client.admin.command("ping")
        except Exception as exc:
            raise SystemExit(f"Cannot reach MongoDB: {exc}")

        self.db = self.client.query_optimization
        self._setup_test_data()

    # ── Test data ──────────────────────────────────────────
    def _setup_test_data(self):
        """Populate products, customers, and orders collections."""
        self.db.orders.drop()
        self.db.products.drop()
        self.db.customers.drop()

        base_date = datetime(2024, 1, 1)

        products = [
            {
                "_id": i,
                "name": f"Product_{i}",
                "category": f"Category_{i % 10}",
                "price": 10 + (i % 100),
                "stock": 1000 - (i % 500),
                "popularity": i % 1000,
            }
            for i in range(1_000)
        ]
        self.db.products.insert_many(products)

        customers = [
            {
                "_id": i,
                "name": f"Customer_{i}",
                "city": f"City_{i % 20}",
                "segment": ["Premium", "Standard", "Basic"][i % 3],
                "join_date": base_date + timedelta(days=i % 365),
            }
            for i in range(10_000)
        ]
        self.db.customers.insert_many(customers)

        STATUSES  = ["pending", "completed", "shipped", "cancelled"]
        PAYMENTS  = ["credit", "debit", "paypal", "cash"]
        orders = [
            {
                "_id": i,
                "customer_id": i % 10_000,
                "product_id": i % 1_000,
                "quantity": 1 + (i % 10),
                "price": 10 + (i % 100),
                "order_date": base_date + timedelta(days=i % 365),
                "status": STATUSES[i % 4],
                "payment_method": PAYMENTS[i % 4],
            }
            for i in range(100_000)
        ]
        self.db.orders.insert_many(orders)

        print("Test data created:")
        print(f"  products  : {self.db.products.count_documents({})}")
        print(f"  customers : {self.db.customers.count_documents({})}")
        print(f"  orders    : {self.db.orders.count_documents({})}")

    # ── Explain helpers ────────────────────────────────────
    def _explain_cmd(self, filter_doc=None, sort=None, hint=None):
        """
        Run the MongoDB 'explain' command with executionStats verbosity.
        pymongo 4.x removed the verbosity arg from Cursor.explain(), so we
        use db.command() directly.
        """
        find_spec = {"find": "orders", "filter": filter_doc or {}, "limit": 100}
        if sort:
            find_spec["sort"] = dict(sort)
        if hint:
            find_spec["hint"] = dict(hint)
        try:
            return self.db.command(
                "explain", find_spec, verbosity="executionStats"
            )
        except Exception:
            # Fallback: use Cursor.explain() which gives queryPlanner only
            cur = self.db.orders.find(filter_doc or {}).limit(100)
            if hint:
                cur = cur.hint(hint)
            if sort:
                cur = cur.sort(sort)
            return cur.explain()

    def _extract_stats(self, explain_doc):
        """Pull the fields we care about from an explain document."""
        es   = explain_doc.get("executionStats", {})
        plan = explain_doc.get("queryPlanner", {}).get("winningPlan", {})
        return {
            "exec_ms":       es.get("executionTimeMillis", 0),
            "docs_examined": es.get("totalDocsExamined", 0),
            "keys_examined": es.get("totalKeysExamined", 0),
            "stage":         plan.get("stage", "?"),
            "input_stage":   plan.get("inputStage", {}).get("stage", ""),
        }

    # ── Generic benchmark ──────────────────────────────────
    def _benchmark(self, label, cursor_factory,
                   filter_doc=None, sort=None, hint=None, iterations=5):
        """
        Run cursor_factory() `iterations` times, measure wall-clock time,
        then explain the query via db.command for executionStats.

        cursor_factory must return a fresh cursor each call.
        filter_doc / sort / hint are forwarded to _explain_cmd.
        """
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            list(cursor_factory())
            times.append((time.perf_counter() - start) * 1000)

        explain_doc = self._explain_cmd(filter_doc, sort, hint)
        ex_stats    = self._extract_stats(explain_doc)

        return {
            "query":   label,
            "avg_ms":  sum(times) / len(times),
            "min_ms":  min(times),
            "max_ms":  max(times),
            **ex_stats,
        }

    # ── Queries WITHOUT indexes ────────────────────────────
    def test_queries_without_index(self):
        """Baseline: COLLSCAN on every query."""
        print("\n=== Queries WITHOUT Indexes ===")
        self.db.orders.drop_indexes()           # ensure clean slate

        results = []
        RANGE_START = datetime(2024, 6, 1)
        RANGE_END   = datetime(2024, 12, 31)

        defs = [
            ("Q1 – simple filter",
             lambda: self.db.orders.find({"status": "completed"}).limit(100),
             {"status": "completed"}, None, None),

            ("Q2 – date range",
             lambda: self.db.orders.find(
                 {"order_date": {"$gte": RANGE_START, "$lte": RANGE_END}}
             ).limit(100),
             {"order_date": {"$gte": RANGE_START, "$lte": RANGE_END}}, None, None),

            ("Q3 – compound condition",
             lambda: self.db.orders.find(
                 {"status": "completed", "payment_method": "credit", "quantity": {"$gt": 5}}
             ).limit(100),
             {"status": "completed", "payment_method": "credit", "quantity": {"$gt": 5}}, None, None),

            ("Q4 – sort descending",
             lambda: self.db.orders.find().sort("order_date", DESCENDING).limit(100),
             {}, [("order_date", DESCENDING)], None),
        ]

        for label, factory, f_doc, sort, hint in defs:
            stats = self._benchmark(label, factory, f_doc, sort, hint)
            results.append(stats)
            print(f"\n  {stats['query']}")
            print(f"    Avg time      : {stats['avg_ms']:.1f} ms")
            print(f"    Docs examined : {stats['docs_examined']}")
            print(f"    Stage         : {stats['stage']}")

        return results

    # ── Index creation ─────────────────────────────────────
    def create_indexes(self):
        """Build the optimal index set for the five benchmark queries."""
        print("\n=== Creating Indexes ===")
        index_defs = [
            [("status", ASCENDING)],
            [("order_date", ASCENDING)],
            [("order_date", DESCENDING)],
            [("status", ASCENDING), ("payment_method", ASCENDING), ("quantity", ASCENDING)],
            [("customer_id", ASCENDING)],
            [("status", ASCENDING), ("order_date", DESCENDING)],
            [("product_id", ASCENDING), ("status", ASCENDING)],
        ]
        for idx in index_defs:
            name = self.db.orders.create_index(idx)
            print(f"  Created: {name}")

    # ── Queries WITH indexes ───────────────────────────────
    def test_queries_with_index(self):
        """Same queries – now MongoDB can use indexes."""
        print("\n=== Queries WITH Indexes ===")

        RANGE_START = datetime(2024, 6, 1)
        RANGE_END   = datetime(2024, 12, 31)

        H1 = [("status", ASCENDING)]
        H2 = [("order_date", ASCENDING)]
        H3 = [("status", ASCENDING), ("payment_method", ASCENDING), ("quantity", ASCENDING)]
        H4 = [("order_date", DESCENDING)]

        defs = [
            ("Q1 – simple filter (idx)",
             lambda: self.db.orders.find({"status": "completed"}).hint(H1).limit(100),
             {"status": "completed"}, None, H1),

            ("Q2 – date range (idx)",
             lambda: self.db.orders
                 .find({"order_date": {"$gte": RANGE_START, "$lte": RANGE_END}})
                 .hint(H2).limit(100),
             {"order_date": {"$gte": RANGE_START, "$lte": RANGE_END}}, None, H2),

            ("Q3 – compound condition (idx)",
             lambda: self.db.orders
                 .find({"status": "completed", "payment_method": "credit", "quantity": {"$gt": 5}})
                 .hint(H3).limit(100),
             {"status": "completed", "payment_method": "credit", "quantity": {"$gt": 5}}, None, H3),

            ("Q4 – sort descending (idx)",
             lambda: self.db.orders.find().sort("order_date", DESCENDING).hint(H4).limit(100),
             {}, [("order_date", DESCENDING)], H4),
        ]

        results = []
        for label, factory, f_doc, sort, hint in defs:
            stats = self._benchmark(label, factory, f_doc, sort, hint)
            results.append(stats)
            print(f"\n  {stats['query']}")
            print(f"    Avg time      : {stats['avg_ms']:.1f} ms")
            print(f"    Docs examined : {stats['docs_examined']}")
            print(f"    Stage         : {stats['stage']}")
            if stats["input_stage"]:
                print(f"    Input stage   : {stats['input_stage']}")

        return results

    # ── Performance comparison ─────────────────────────────
    def compare_performance(self, without_idx, with_idx):
        """Print a comparison table and save a chart."""
        print("\n=== Performance Comparison ===")

        rows = []
        for woi, wi in zip(without_idx, with_idx):
            improvement = (
                (woi["avg_ms"] - wi["avg_ms"]) / woi["avg_ms"] * 100
                if woi["avg_ms"] > 0 else 0
            )
            rows.append({
                "Query":              woi["query"].split("–")[0].strip(),
                "No-Index (ms)":      round(woi["avg_ms"], 1),
                "With-Index (ms)":    round(wi["avg_ms"], 1),
                "Improvement (%)":    round(improvement, 1),
                "Docs Reduction":     woi["docs_examined"] - wi["docs_examined"],
            })

        df = pd.DataFrame(rows)
        print(df.to_string(index=False))

        # ── Chart ──────────────────────────────────────────
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        labels    = [r["Query"] for r in rows]
        times_woi = [r["No-Index (ms)"] for r in rows]
        times_wi  = [r["With-Index (ms)"] for r in rows]

        x, w = list(range(len(labels))), 0.35
        tick_pos = [i + w / 2 for i in x]

        axes[0].bar(x, times_woi, w, label="No Index", color="tomato", alpha=0.8)
        axes[0].bar([i + w for i in x], times_wi, w, label="With Index", color="steelblue", alpha=0.8)
        axes[0].set_xticks(tick_pos)
        axes[0].set_xticklabels(labels, rotation=15, ha="right")
        axes[0].set_ylabel("Avg execution time (ms)")
        axes[0].set_title("Execution Time: No-Index vs Indexed")
        axes[0].legend()
        axes[0].grid(axis="y", alpha=0.3)

        improvements = [r["Improvement (%)"] for r in rows]
        colors = ["seagreen" if v > 0 else "tomato" for v in improvements]
        axes[1].bar(x, improvements, color=colors, alpha=0.8)
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(labels, rotation=15, ha="right")
        axes[1].axhline(0, color="black", linewidth=0.8)
        axes[1].set_ylabel("Improvement (%)")
        axes[1].set_title("Speed-up from Indexing")
        axes[1].grid(axis="y", alpha=0.3)

        plt.tight_layout()
        out = "query_performance_comparison.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        print(f"\nChart saved -> {out}")
    
        return rows

    # ── Index selectivity ──────────────────────────────────
    def test_index_selectivity(self):
        """
        Show that high-cardinality (selective) indexes are faster
        than low-cardinality ones for equality queries.
        """
        print("\n=== Index Selectivity Analysis ===")

        TOTAL_DOCS = self.db.orders.count_documents({})

        # (field, sample_value, cardinality_label)
        scenarios = [
            ("status",          "completed",  "~4 values (low)"),
            ("payment_method",  "credit",     "~4 values (low)"),
            ("quantity",        5,            "~10 values (medium)"),
            ("customer_id",     42,           "10 000 values (high)"),
            ("_id",             42,           "100 000 values (unique)"),
        ]

        rows = []
        for field, value, cardinality_note in scenarios:
            # _id always has a built-in index named '_id_' – skip create/drop
            is_id_field = (field == "_id")
            idx_name = None
            if not is_id_field:
                idx_name = self.db.orders.create_index([(field, ASCENDING)])
            hint_spec = [(field, ASCENDING)]
            factory  = lambda f=field, v=value, h=hint_spec: (
                self.db.orders.find({f: v}).hint(h).limit(100)
            )
            stats = self._benchmark(
                f"{field} ({cardinality_note})", factory,
                filter_doc={field: value}, hint=hint_spec, iterations=3,
            )
            rows.append({
                "Field":       field,
                "Cardinality": cardinality_note,
                "Avg (ms)":    round(stats["avg_ms"], 2),
                "Docs Exam.":  stats["docs_examined"],
                "Stage":       stats["stage"],
                "InputStage":  stats["input_stage"],
            })
            if idx_name:
                self.db.orders.drop_index(idx_name)

        df = pd.DataFrame(rows)
        print(df.to_string(index=False))

        print(
            "\nKey insight: High-cardinality indexes (customer_id, _id) examine far "
            "fewer documents than low-cardinality ones (status, payment_method)."
        )
        return rows


# ── Entry point ────────────────────────────────────────────
if __name__ == "__main__":
    opt = QueryOptimizer()

    no_idx  = opt.test_queries_without_index()
    opt.create_indexes()
    with_idx = opt.test_queries_with_index()
    opt.compare_performance(no_idx, with_idx)
    opt.test_index_selectivity()
