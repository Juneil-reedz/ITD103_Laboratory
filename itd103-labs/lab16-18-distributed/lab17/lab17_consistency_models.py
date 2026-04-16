# =============================================================
# Lab 17 – Exercise 1: Consistency Models in Distributed Systems
# Run: python lab17_consistency_models.py
# (replica set on 27017-27019 recommended; falls back to standalone)
# =============================================================

from pymongo import MongoClient, WriteConcern
from pymongo.read_preferences import ReadPreference
from pymongo.errors import ConnectionFailure, OperationFailure
import time
import random
import threading
from datetime import datetime, timezone

STANDALONE_URI    = "mongodb://localhost:27017"
REPLICA_SET_URI   = (
    "mongodb://localhost:27017,localhost:27018,localhost:27019/"
    "?replicaSet=rs0"
)


# ── Helpers ────────────────────────────────────────────────
def make_client(uri=STANDALONE_URI):
    c = MongoClient(uri, serverSelectionTimeoutMS=3000)
    c.admin.command("ping")
    return c


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


# ── Part A: CAP Theorem demonstration ─────────────────────
def demonstrate_cap_tradeoffs():
    """
    Illustrate CP vs AP trade-offs using MongoDB write concern.

    CP  (Consistency + Partition-tolerance)
        w="majority"  ->  blocks until a quorum acknowledges the write.
        If the network partitions, the minority side refuses writes.

    AP  (Availability + Partition-tolerance)
        w=1           ->  returns as soon as the primary has written.
        Replicas may lag, so reads from secondaries may be stale.
    """
    section("A. CAP Theorem – CP vs AP Trade-offs")

    try:
        client = make_client(REPLICA_SET_URI)
        print("  Using replica set (full CAP demo available)")
    except Exception:
        client = make_client(STANDALONE_URI)
        print("  Replica set not found – using standalone for illustration")

    db = client.consistency_demo
    db.cap_demo.drop()

    # CP: majority write
    cp_col = db.cap_demo.with_options(write_concern=WriteConcern(w="majority", j=True))
    start  = time.perf_counter()
    cp_col.insert_one({"mode": "CP", "ts": datetime.now(timezone.utc)})
    cp_ms  = (time.perf_counter() - start) * 1000

    # AP: fire-and-forget (unacknowledged)
    ap_col = db.cap_demo.with_options(write_concern=WriteConcern(w=0))
    start  = time.perf_counter()
    ap_col.insert_one({"mode": "AP", "ts": datetime.now(timezone.utc)})
    ap_ms  = (time.perf_counter() - start) * 1000

    print(f"\n  CP write (w=majority, j=True)  : {cp_ms:.2f} ms")
    print(f"  AP write (w=0, unacknowledged) : {ap_ms:.2f} ms")
    print(f"\n  CP is ~{cp_ms/max(ap_ms,0.01):.0f}× slower but guarantees durability.")
    print("  AP is faster but may lose the write if the primary crashes immediately.")

    client.close()


# ── Part B: Strong vs Eventual Consistency ─────────────────
def simulate_consistency_levels():
    """
    Simulate strong and eventual consistency using read/write concerns.

    Strong consistency  -> w=majority + readPreference=primary
    Eventual consistency-> w=1       + readPreference=secondaryPreferred
    """
    section("B. Strong vs Eventual Consistency")

    try:
        client = make_client(REPLICA_SET_URI)
        rs_available = True
    except Exception:
        client = make_client(STANDALONE_URI)
        rs_available = False

    db = client.consistency_demo
    db.events.drop()

    results = {"strong": [], "eventual": []}

    def write_and_read(mode, write_concern, read_pref, iterations=20):
        wc_col = db.events.with_options(write_concern=write_concern)

        for i in range(iterations):
            payload = {"mode": mode, "seq": i, "ts": datetime.now(timezone.utc)}

            # Write
            wc_col.insert_one(payload)

            # Read-your-own-write check
            if rs_available and read_pref != ReadPreference.PRIMARY:
                col = db.get_collection("events", read_preference=read_pref)
            else:
                col = db.events

            doc = col.find_one({"mode": mode, "seq": i})
            visible = doc is not None
            results[mode].append(visible)
            time.sleep(0.01)

    strong_thread = threading.Thread(
        target=write_and_read,
        args=("strong", WriteConcern(w="majority"), ReadPreference.PRIMARY),
    )
    eventual_thread = threading.Thread(
        target=write_and_read,
        args=("eventual", WriteConcern(w=1), ReadPreference.SECONDARY_PREFERRED),
    )

    strong_thread.start();  eventual_thread.start()
    strong_thread.join();   eventual_thread.join()

    strong_vis  = sum(results["strong"])  / len(results["strong"])  * 100
    eventual_vis = sum(results["eventual"]) / len(results["eventual"]) * 100

    print(f"\n  Strong consistency  – read-your-own-write visible : {strong_vis:.0f}%")
    print(f"  Eventual consistency – read-your-own-write visible: {eventual_vis:.0f}%")
    print("\n  (Eventual consistency may miss a just-written doc on a lagging secondary.)")

    client.close()


# ── Part C: Read-your-writes and Monotonic reads ──────────
def demonstrate_session_consistency():
    """
    MongoDB 4.x causal sessions guarantee:
      - Read-your-writes
      - Monotonic reads
      - Monotonic writes
      - Writes follow reads
    """
    section("C. Causal Consistency via Sessions")

    rs_available = True
    try:
        client = make_client(REPLICA_SET_URI)
    except Exception:
        rs_available = False
        client = make_client(STANDALONE_URI)

    if not rs_available:
        print("  NOTE: Multi-document transactions require a replica set.")
        print("  Showing session-scoped reads on standalone (no transaction).\n")

    db = client.consistency_demo
    db.session_test.drop()

    # ── Without causal session ─────────────────────────────
    print("\n  Without causal session:")
    client.consistency_demo.session_test.insert_one({"v": 1})
    count_direct = db.session_test.count_documents({})
    print(f"    Inserted 1 doc, count from default read: {count_direct}")

    # ── With causal session ────────────────────────────────
    print("\n  With causal session (read-your-writes guaranteed):")
    with client.start_session() as session:
        try:
            session.start_transaction()
            db.session_test.insert_one({"v": 2}, session=session)
            session.commit_transaction()
            count_session = db.session_test.count_documents({}, session=session)
            print(f"    Inserted doc v=2, count inside session: {count_session}")
        except OperationFailure as exc:
            session.abort_transaction()
            msg = exc.details.get("errmsg", str(exc))
            print(f"    Transaction not available on standalone: {msg}")
            print("    (Start a replica set to see full causal consistency.)")
            # Still show session-level read without transaction
            db.session_test.insert_one({"v": 2})
            count_session = db.session_test.count_documents({})
            print(f"    Fallback direct insert: count = {count_session}")

    client.close()


# ── Part D: Stale-read simulation ──────────────────────────
def simulate_stale_reads():
    """
    Demonstrate replication lag by writing quickly and reading
    from a secondary-preferred cursor immediately after.
    """
    section("D. Stale-Read Simulation (Replication Lag)")

    try:
        client = make_client(REPLICA_SET_URI)
    except Exception:
        print("  Replica set required for stale-read demo. Skipping.")
        return

    db      = client.consistency_demo
    db.lag_test.drop()

    BATCH   = 500
    prim_col = db.lag_test.with_options(write_concern=WriteConcern(w=1))
    sec_col  = db.get_collection(
        "lag_test", read_preference=ReadPreference.SECONDARY_PREFERRED
    )

    print(f"\n  Writing {BATCH} docs with w=1 (fast, no majority wait) ...")
    docs = [{"i": i, "ts": datetime.now(timezone.utc)} for i in range(BATCH)]
    prim_col.insert_many(docs)

    # Immediately read from secondary
    sec_count   = db.lag_test.with_options(
        read_preference=ReadPreference.SECONDARY_PREFERRED
    ).count_documents({})
    prim_count  = db.lag_test.count_documents({})

    print(f"  Primary count   : {prim_count}")
    print(f"  Secondary count : {sec_count}  (may be lower due to replication lag)")

    lag_docs = prim_count - sec_count
    if lag_docs > 0:
        print(f"  -> {lag_docs} docs not yet replicated (stale window visible)")
    else:
        print("  -> Replication was fast enough; both counts agree.")

    client.close()


# ── Part E: Consistency comparison table ───────────────────
def print_consistency_summary():
    section("E. Consistency Model Summary")

    rows = [
        ("Strong",     "w=majority, j=True",  "PRIMARY",            "Yes", "No",  "Slowest"),
        ("Read-Committed", "w=majority",       "primaryPreferred",   "Yes", "No",  "Moderate"),
        ("Monotonic",  "w=1",                  "secondaryPreferred", "No",  "Yes", "Fast"),
        ("Eventual",   "w=0",                  "nearest",            "No",  "Yes", "Fastest"),
    ]

    hdr = f"  {'Model':<22} {'WriteConcern':<22} {'ReadPref':<22} {'Read-YW':<9} {'Stale?':<8} {'Perf'}"
    print(f"\n{hdr}")
    print("  " + "-" * 95)
    for r in rows:
        print(f"  {r[0]:<22} {r[1]:<22} {r[2]:<22} {r[3]:<9} {r[4]:<8} {r[5]}")

    print("""
  Legend:
    Read-YW  = Read-your-own-writes guarantee
    Stale?   = Secondary reads may return stale data
  """)


# ── Entry point ────────────────────────────────────────────
if __name__ == "__main__":
    demonstrate_cap_tradeoffs()
    simulate_consistency_levels()
    demonstrate_session_consistency()
    simulate_stale_reads()
    print_consistency_summary()
