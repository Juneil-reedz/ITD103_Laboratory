# =============================================================
# Lab 16 – Exercise 2: Replication and Failover Testing
# Prerequisites: replica set rs0 running on ports 27017-27019
# Run: python lab16_replication_test.py
# =============================================================

from pymongo import MongoClient, WriteConcern
from pymongo.read_preferences import ReadPreference
from pymongo.errors import ConnectionFailure, OperationFailure
import time
import threading

REPLICA_SET_URI = (
    "mongodb://localhost:27017,localhost:27018,localhost:27019/"
    "?replicaSet=rs0"
)


class ReplicationTester:
    def __init__(self):
        self.client = MongoClient(
            REPLICA_SET_URI,
            serverSelectionTimeoutMS=5000,
        )
        # Verify connectivity before proceeding
        try:
            self.client.admin.command("ping")
            print("Connected to replica set rs0")
        except ConnectionFailure as exc:
            raise SystemExit(
                f"Cannot reach replica set: {exc}\n"
                "Make sure all three mongod instances are running and rs0 is initiated."
            )

        self.db         = self.client.test_replication
        self.collection = self.db.data

    # ── Helpers ────────────────────────────────────────────
    def _direct_client(self, host, port):
        """Open a direct connection to one replica-set member."""
        return MongoClient(
            host, port,
            directConnection=True,
            serverSelectionTimeoutMS=3000,
        )

    # ── Setup ──────────────────────────────────────────────
    def setup_data(self):
        """Insert 1 000 test documents and verify replication."""
        self.collection.drop()

        documents = [
            {"_id": i, "value": f"data_{i}", "timestamp": time.time()}
            for i in range(1000)
        ]
        result = self.collection.insert_many(
            documents,
            # w=majority ensures at least two members acknowledged the write
        )
        print(f"Inserted {len(result.inserted_ids)} documents")
        self._verify_replication()

    def _verify_replication(self):
        """Check document counts across all replica-set members."""
        primary     = self.client.primary
        secondaries = list(self.client.secondaries)

        print(f"\nPrimary    : {primary}")
        print(f"Secondaries: {secondaries}")

        all_members = ([primary] if primary else []) + secondaries
        for host, port in all_members:
            try:
                mc    = self._direct_client(host, port)
                count = mc.test_replication.data.count_documents({})
                print(f"  {host}:{port}  ->  {count} documents")
                mc.close()
            except Exception as exc:
                print(f"  {host}:{port}  ->  error: {exc}")

    # ── Read preferences ───────────────────────────────────
    def test_read_preferences(self):
        """Demonstrate primary / secondary-preferred / nearest reads."""
        print("\n=== Read Preferences ===")

        scenarios = [
            ("PRIMARY",            ReadPreference.PRIMARY),
            ("SECONDARY_PREFERRED", ReadPreference.SECONDARY_PREFERRED),
            ("NEAREST",            ReadPreference.NEAREST),
        ]

        for label, pref in scenarios:
            col   = self.db.get_collection("data", read_preference=pref)
            start = time.time()
            docs  = list(col.find().limit(3))
            elapsed = (time.time() - start) * 1000

            ids = [d["_id"] for d in docs]
            print(f"\n  {label:25s}  ids={ids}  ({elapsed:.1f} ms)")

    # ── Write concerns ─────────────────────────────────────
    def test_write_concern(self):
        """Insert documents using various write-concern configurations."""
        print("\n=== Write Concern ===")

        test_cases = [
            ("w=1 (default)",        WriteConcern(w=1)),
            ("w=majority",           WriteConcern(w="majority")),
            ("w=2",                  WriteConcern(w=2)),
            ("w=1, j=True",          WriteConcern(w=1, j=True)),
            ("w=majority, j=True",   WriteConcern(w="majority", j=True)),
        ]

        for label, wc in test_cases:
            col   = self.collection.with_options(write_concern=wc)
            start = time.time()
            try:
                result  = col.insert_one({"test": label, "timestamp": time.time()})
                elapsed = (time.time() - start) * 1000
                print(f"  {label:25s}  id={result.inserted_id}  ({elapsed:.1f} ms)")
            except OperationFailure as exc:
                print(f"  {label:25s}  FAILED: {exc.details.get('errmsg', exc)}")

    # ── Failover ───────────────────────────────────────────
    def test_failover(self):
        """Step down the primary and confirm a new one is elected."""
        print("\n=== Failover Test ===")

        old_primary = self.client.primary
        print(f"  Current primary: {old_primary}")

        print("  Stepping down primary for 30 s ...")
        try:
            self.client.admin.command("replSetStepDown", 30)
        except OperationFailure:
            # replSetStepDown raises a network-level error when the connection
            # is dropped — that is expected and harmless.
            pass

        print("  Waiting for election (10 s) ...")
        time.sleep(10)

        new_primary = self.client.primary
        print(f"  New primary: {new_primary}")

        # Verify writes still work after failover
        print("  Writing with w=majority after failover ...")
        start = time.time()
        try:
            wc_col  = self.collection.with_options(write_concern=WriteConcern(w="majority"))
            result  = wc_col.insert_one({"failover_test": True, "ts": time.time()})
            elapsed = (time.time() - start) * 1000
            print(f"  Write succeeded in {elapsed:.1f} ms  id={result.inserted_id}")
        except Exception as exc:
            print(f"  Write FAILED: {exc}")

        count = self.collection.count_documents({})
        print(f"  Total documents after failover: {count}")

    # ── Concurrent read/write ──────────────────────────────
    def test_concurrent_read_write(self):
        """Run writer and reader threads simultaneously."""
        print("\n=== Concurrent Read/Write Test ===")

        def writer(thread_id):
            for i in range(100):
                self.collection.insert_one({
                    "thread": thread_id,
                    "iteration": i,
                    "ts": time.time(),
                })
                time.sleep(0.01)

        def reader(thread_id, result_list):
            read_count = 0
            deadline   = time.time() + 5
            col = self.db.get_collection(
                "data", read_preference=ReadPreference.SECONDARY_PREFERRED
            )
            while time.time() < deadline:
                list(col.find({"thread": thread_id}).limit(10))
                read_count += 1
                time.sleep(0.01)
            result_list.append(read_count)

        writer_threads = [
            threading.Thread(target=writer, args=(i,)) for i in range(3)
        ]
        reader_results = []
        reader_threads = [
            threading.Thread(target=reader, args=(i, reader_results)) for i in range(2)
        ]

        for t in writer_threads + reader_threads:
            t.start()
        for t in writer_threads + reader_threads:
            t.join()

        final_count = self.collection.count_documents({})
        print(f"  Final document count   : {final_count}")
        print(f"  Total reads completed  : {sum(reader_results)}")

        # Documents per writer thread
        per_thread = {}
        for doc in self.collection.find({"thread": {"$exists": True}}):
            tid = doc["thread"]
            per_thread[tid] = per_thread.get(tid, 0) + 1
        print(f"  Docs per writer thread : {dict(sorted(per_thread.items()))}")


# ── Entry point ────────────────────────────────────────────
if __name__ == "__main__":
    tester = ReplicationTester()

    tester.setup_data()
    tester.test_read_preferences()
    tester.test_write_concern()
    tester.test_failover()
    tester.test_concurrent_read_write()
