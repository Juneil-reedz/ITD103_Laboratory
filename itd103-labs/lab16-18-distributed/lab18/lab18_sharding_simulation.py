# =============================================================
# Lab 18 – Exercise 1: Sharding Simulation
# Demonstrates range, hash, and zone sharding strategies
# using in-process Python simulation (no mongos required).
# Run: python lab18_sharding_simulation.py
# =============================================================

from pymongo import MongoClient, ASCENDING
from datetime import datetime, timezone, timedelta
import hashlib
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


# ── Shard helper ───────────────────────────────────────────
class ShardManager:
    """
    Simulates a sharded cluster using separate MongoDB collections
    as shard partitions. Each 'shard' is a collection prefixed by
    its name so everything lives on the same local instance.
    """

    def __init__(self, db, num_shards=3):
        self.db         = db
        self.num_shards = num_shards
        self.shards     = [db[f"shard_{i}"] for i in range(num_shards)]

    def reset(self):
        for s in self.shards:
            s.drop()

    def stats(self, label=""):
        print(f"\n  Shard distribution{f' ({label})' if label else ''}:")
        total = 0
        counts = []
        for i, s in enumerate(self.shards):
            c = s.count_documents({})
            counts.append(c)
            total += c
            bar = "#" * (c // 500) if c else ""
            print(f"    Shard {i}: {c:6d} docs  {bar}")
        print(f"    Total : {total:6d} docs")

        if total > 0:
            imbalance = (max(counts) - min(counts)) / (total / self.num_shards) * 100
            print(f"    Imbalance: {imbalance:.1f}%  (0% = perfectly balanced)")
        return counts


# ── Strategy A: Range sharding ─────────────────────────────
def demo_range_sharding(db):
    section("A. Range Sharding (by customer_id)")

    sm = ShardManager(db, num_shards=3)
    sm.reset()

    NUM_DOCS   = 9_000
    CHUNK_SIZE = NUM_DOCS // sm.num_shards  # 3 000 per shard

    print(f"\n  Inserting {NUM_DOCS} documents with range key = customer_id ...")

    for i in range(NUM_DOCS):
        shard_idx = i // CHUNK_SIZE
        if shard_idx >= sm.num_shards:
            shard_idx = sm.num_shards - 1           # last shard absorbs tail

        sm.shards[shard_idx].insert_one({
            "customer_id": i,
            "name":        f"Customer_{i}",
            "region":      ["North", "South", "East", "West"][i % 4],
            "balance":     round(random.uniform(100, 10_000), 2),
        })

    sm.stats("range sharding")

    # Targeted query: range queries hit exactly ONE shard
    print("\n  Range query: customer_id 3 000 – 5 999 (should hit Shard 1 only)")
    start = time.perf_counter()
    results = list(sm.shards[1].find(
        {"customer_id": {"$gte": 3_000, "$lt": 6_000}}
    ).limit(5))
    elapsed = (time.perf_counter() - start) * 1000
    print(f"    Found {len(results)} docs in {elapsed:.1f} ms (targeted shard)")
    print(f"    Sample ids: {[r['customer_id'] for r in results]}")

    print("\n  Cross-shard range query: customer_id 2 500 – 3 500 (spans Shard 0 & 1)")
    combined = (
        list(sm.shards[0].find({"customer_id": {"$gte": 2_500, "$lt": 3_000}}).limit(3))
        + list(sm.shards[1].find({"customer_id": {"$gte": 3_000, "$lte": 3_500}}).limit(3))
    )
    print(f"    Fetched from 2 shards: {[r['customer_id'] for r in combined]}")

    return sm


# ── Strategy B: Hash sharding ──────────────────────────────
def demo_hash_sharding(db):
    section("B. Hash Sharding (uniform distribution)")

    sm = ShardManager(db, num_shards=3)
    sm.reset()

    NUM_DOCS = 9_000

    def hash_shard(key_value, n_shards):
        h = int(hashlib.md5(str(key_value).encode()).hexdigest(), 16)
        return h % n_shards

    print(f"\n  Inserting {NUM_DOCS} documents using MD5 hash of customer_id ...")
    for i in range(NUM_DOCS):
        shard_idx = hash_shard(i, sm.num_shards)
        sm.shards[shard_idx].insert_one({
            "customer_id": i,
            "name":        f"Customer_{i}",
            "region":      ["North", "South", "East", "West"][i % 4],
            "balance":     round(random.uniform(100, 10_000), 2),
        })

    sm.stats("hash sharding")

    # Hash sharding requires broadcast for range queries
    print("\n  Range query customer_id 1 000 – 2 000 requires broadcast across ALL shards:")
    start   = time.perf_counter()
    total   = 0
    for shard in sm.shards:
        total += shard.count_documents({"customer_id": {"$gte": 1_000, "$lte": 2_000}})
    elapsed = (time.perf_counter() - start) * 1000
    print(f"    Total found: {total} in {elapsed:.1f} ms (scatter-gather)")

    # Point lookup is still targeted
    target_id = 42
    target_shard = hash_shard(target_id, sm.num_shards)
    doc = sm.shards[target_shard].find_one({"customer_id": target_id})
    print(f"\n  Point lookup customer_id={target_id} -> Shard {target_shard}")
    print(f"    Found: {doc['name'] if doc else 'NOT FOUND'}")

    return sm


# ── Strategy C: Zone (geo) sharding ───────────────────────
def demo_zone_sharding(db):
    section("C. Zone Sharding (by geographic region)")

    ZONES = {
        "North": 0,
        "South": 1,
        "East":  2,
        "West":  2,   # East and West share shard 2
    }
    sm = ShardManager(db, num_shards=3)
    sm.reset()

    NUM_DOCS = 9_000
    REGIONS  = list(ZONES.keys())

    print(f"\n  Zone map: {ZONES}")
    print(f"  Inserting {NUM_DOCS} documents ...")

    for i in range(NUM_DOCS):
        region    = REGIONS[i % len(REGIONS)]
        shard_idx = ZONES[region]
        sm.shards[shard_idx].insert_one({
            "customer_id": i,
            "region":      region,
            "balance":     round(random.uniform(100, 10_000), 2),
        })

    sm.stats("zone sharding")

    # Zone query targets a single shard
    print("\n  Query: all North customers (targeted to Shard 0)")
    start = time.perf_counter()
    count = sm.shards[0].count_documents({"region": "North"})
    elapsed = (time.perf_counter() - start) * 1000
    print(f"    Found {count} North docs in {elapsed:.1f} ms")

    return sm


# ── Strategy comparison chart ──────────────────────────────
def compare_strategies(range_sm, hash_sm, zone_sm):
    section("D. Strategy Comparison Chart")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = ["steelblue", "seagreen", "tomato"]

    for ax, sm, title in zip(
        axes,
        [range_sm, hash_sm, zone_sm],
        ["Range Sharding", "Hash Sharding", "Zone Sharding"],
    ):
        counts = [s.count_documents({}) for s in sm.shards]
        ax.bar([f"Shard {i}" for i in range(len(counts))], counts, color=colors, alpha=0.8)
        ax.set_title(title)
        ax.set_ylabel("Document count")
        ax.set_ylim(0, max(counts) * 1.2)
        ax.grid(axis="y", alpha=0.3)

        avg = sum(counts) / len(counts)
        ax.axhline(avg, color="black", linestyle="--", linewidth=1, label=f"avg={avg:.0f}")
        ax.legend(fontsize=9)

    plt.suptitle("Sharding Strategy: Document Distribution per Shard", fontsize=13)
    plt.tight_layout()
    out = "sharding_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\n  Chart saved -> {out}")


# ── Entry point ────────────────────────────────────────────
if __name__ == "__main__":
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as exc:
        raise SystemExit(f"Cannot reach MongoDB: {exc}")

    db = client.sharding_demo

    range_sm = demo_range_sharding(db)
    hash_sm  = demo_hash_sharding(db)
    zone_sm  = demo_zone_sharding(db)
    compare_strategies(range_sm, hash_sm, zone_sm)

    client.close()
    print("\nSharding simulation complete.")
