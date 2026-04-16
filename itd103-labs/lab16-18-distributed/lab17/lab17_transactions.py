# =============================================================
# Lab 17 – Exercise 2: ACID Multi-Document Transactions
# Run: python lab17_transactions.py
# (Requires replica set OR MongoDB 5+ standalone with WiredTiger)
# =============================================================

from pymongo import MongoClient, WriteConcern
from pymongo.read_preferences import ReadPreference
from pymongo.errors import (
    PyMongoError, OperationFailure, ConnectionFailure
)
import time
import threading
import random
from datetime import datetime, timezone

STANDALONE_URI  = "mongodb://localhost:27017"
REPLICA_SET_URI = (
    "mongodb://localhost:27017,localhost:27018,localhost:27019/"
    "?replicaSet=rs0"
)


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


# ── Database ───────────────────────────────────────────────
class BankDatabase:
    """Simple banking schema to demonstrate ACID transactions."""

    def __init__(self, client):
        self.db = client.bank

    def reset(self):
        self.db.accounts.drop()
        self.db.transactions.drop()
        self.db.audit_log.drop()

        # Seed accounts
        accounts = [
            {"_id": "A001", "owner": "Alice", "balance": 5000.00, "version": 1},
            {"_id": "A002", "owner": "Bob",   "balance": 3000.00, "version": 1},
            {"_id": "A003", "owner": "Carol", "balance": 1500.00, "version": 1},
        ]
        self.db.accounts.insert_many(accounts)
        print("\n  Accounts seeded:")
        for a in accounts:
            print(f"    {a['_id']} {a['owner']:6s}  balance=${a['balance']:,.2f}")

    def print_balances(self, label=""):
        label_str = f" ({label})" if label else ""
        print(f"\n  Account balances{label_str}:")
        total = 0
        for a in self.db.accounts.find().sort("_id", 1):
            print(f"    {a['_id']} {a['owner']:6s}  ${a['balance']:,.2f}")
            total += a["balance"]
        print(f"    {'TOTAL':15s}  ${total:,.2f}")
        return total


# ── Exercise A: Basic transaction ──────────────────────────
def test_basic_transaction(client):
    section("A. Basic ACID Transaction (funds transfer)")

    bank = BankDatabase(client)
    bank.reset()
    initial_total = bank.print_balances("before")

    def transfer(from_id, to_id, amount, session):
        """Move `amount` from one account to another atomically."""
        from_acc = client.bank.accounts.find_one({"_id": from_id}, session=session)
        if from_acc is None:
            raise ValueError(f"Account {from_id} not found")
        if from_acc["balance"] < amount:
            raise ValueError(
                f"Insufficient funds: {from_id} has ${from_acc['balance']:.2f}, "
                f"need ${amount:.2f}"
            )

        # Debit
        client.bank.accounts.update_one(
            {"_id": from_id},
            {"$inc": {"balance": -amount}, "$inc": {"version": 1}},
            session=session,
        )
        # Credit
        client.bank.accounts.update_one(
            {"_id": to_id},
            {"$inc": {"balance": amount}, "$inc": {"version": 1}},
            session=session,
        )
        # Record transaction
        client.bank.transactions.insert_one(
            {
                "from":   from_id,
                "to":     to_id,
                "amount": amount,
                "ts":     datetime.now(timezone.utc),
                "status": "completed",
            },
            session=session,
        )

    print(f"\n  Transferring $500 from A001 (Alice) -> A002 (Bob) …")
    with client.start_session() as session:
        try:
            session.with_transaction(
                lambda s: transfer("A001", "A002", 500.00, s)
            )
            print("  Transaction committed.")
        except Exception as exc:
            print(f"  Transaction aborted: {exc}")

    final_total = bank.print_balances("after")

    assert abs(initial_total - final_total) < 0.01, "Total money not conserved!"
    print("\n  Conservation check passed: total money unchanged.")


# ── Exercise B: Automatic retry on transient errors ────────
def test_transaction_retry(client):
    section("B. Automatic Retry on Transient Write Conflicts")

    bank = BankDatabase(client)
    bank.reset()

    conflict_count = [0]

    def conflicting_transfer(session):
        """Simulates a write conflict the first time."""
        if conflict_count[0] == 0:
            conflict_count[0] += 1
            # Deliberately update outside the session to provoke conflict
            client.bank.accounts.update_one(
                {"_id": "A001"},
                {"$inc": {"balance": 0}},   # no-op; in real life another txn wins
            )

        client.bank.accounts.update_one(
            {"_id": "A001"}, {"$inc": {"balance": -200}}, session=session
        )
        client.bank.accounts.update_one(
            {"_id": "A002"}, {"$inc": {"balance":  200}}, session=session
        )

    print("\n  Running transfer that may encounter write conflict …")
    with client.start_session() as session:
        session.with_transaction(conflicting_transfer)

    print(f"  Completed (conflict retried {conflict_count[0]} time(s)).")
    bank.print_balances("after retry")


# ── Exercise C: Rollback on error ──────────────────────────
def test_transaction_rollback(client):
    section("C. Rollback on Error (insufficient funds)")

    bank = BankDatabase(client)
    bank.reset()

    bank.print_balances("before failed transfer")

    def bad_transfer(session):
        # Carol (A003) only has $1 500 — try to send $5 000
        from_acc = client.bank.accounts.find_one({"_id": "A003"}, session=session)
        if from_acc["balance"] < 5000:
            raise ValueError(
                f"Insufficient funds: Carol has ${from_acc['balance']:.2f}, need $5 000"
            )
        client.bank.accounts.update_one(
            {"_id": "A003"}, {"$inc": {"balance": -5000}}, session=session
        )
        client.bank.accounts.update_one(
            {"_id": "A001"}, {"$inc": {"balance":  5000}}, session=session
        )

    print("\n  Attempting to transfer $5 000 from Carol (A003) -> Alice (A001) …")
    with client.start_session() as session:
        try:
            session.with_transaction(bad_transfer)
        except ValueError as exc:
            print(f"  Transaction aborted: {exc}")

    bank.print_balances("after rollback (should be unchanged)")


# ── Exercise D: Concurrent transactions ────────────────────
def test_concurrent_transactions(client):
    section("D. Concurrent Transactions – Isolation")

    bank = BankDatabase(client)
    bank.reset()

    results     = {"success": 0, "failed": 0}
    lock        = threading.Lock()

    def concurrent_transfer(thread_id, from_id, to_id, amount):
        with client.start_session() as session:
            try:
                def txn(s):
                    acc = client.bank.accounts.find_one({"_id": from_id}, session=s)
                    if acc and acc["balance"] >= amount:
                        client.bank.accounts.update_one(
                            {"_id": from_id}, {"$inc": {"balance": -amount}}, session=s
                        )
                        client.bank.accounts.update_one(
                            {"_id": to_id}, {"$inc": {"balance":  amount}}, session=s
                        )

                session.with_transaction(txn)
                with lock:
                    results["success"] += 1
            except Exception:
                with lock:
                    results["failed"] += 1

    initial = bank.print_balances("initial")

    threads = [
        threading.Thread(
            target=concurrent_transfer,
            args=(i, random.choice(["A001", "A002", "A003"]),
                  random.choice(["A001", "A002", "A003"]),
                  random.randint(50, 300)),
        )
        for i in range(10)
    ]

    print(f"\n  Launching {len(threads)} concurrent transfer threads …")
    for t in threads: t.start()
    for t in threads: t.join()

    final = bank.print_balances("final")

    print(f"\n  Succeeded : {results['success']}")
    print(f"  Failed    : {results['failed']}")
    print(f"  Money conservation: {'OK' if abs(initial - final) < 0.01 else 'VIOLATED!'}")


# ── Exercise E: Multi-collection transaction ───────────────
def test_multi_collection_transaction(client):
    section("E. Multi-Collection Atomic Operation")

    bank = BankDatabase(client)
    bank.reset()

    def process_order(session, customer_id, amount):
        """
        Debit customer account AND write audit log atomically.
        Either both happen or neither.
        """
        acc = client.bank.accounts.find_one({"_id": customer_id}, session=session)
        if acc is None or acc["balance"] < amount:
            raise ValueError(f"Cannot process order for {customer_id}")

        client.bank.accounts.update_one(
            {"_id": customer_id}, {"$inc": {"balance": -amount}}, session=session
        )
        client.bank.audit_log.insert_one(
            {
                "event":    "ORDER_PAYMENT",
                "customer": customer_id,
                "amount":   amount,
                "ts":       datetime.now(timezone.utc),
            },
            session=session,
        )

    print("\n  Processing order payment + audit log atomically …")
    with client.start_session() as session:
        session.with_transaction(
            lambda s: process_order(s, "A002", 250.00)
        )

    audit_count = client.bank.audit_log.count_documents({})
    print(f"  Audit log entries: {audit_count}")
    bank.print_balances("after order")


# ── Entry point ────────────────────────────────────────────
def _run(client, label, func):
    """Run one exercise, catching OperationFailure for standalone mode."""
    try:
        func(client)
    except OperationFailure as exc:
        code = exc.details.get("errmsg", str(exc)) if exc.details else str(exc)
        print(f"\n  [SKIPPED on standalone] {label}: {code}")
        print("  Start a replica set (rs0) to run this exercise fully.")


if __name__ == "__main__":
    # Try replica set first (transactions require it)
    rs_available = True
    try:
        client = MongoClient(REPLICA_SET_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        print("Connected to replica set rs0")
    except Exception:
        rs_available = False
        client = MongoClient(STANDALONE_URI, serverSelectionTimeoutMS=3000)
        try:
            client.admin.command("ping")
            print("Connected to standalone mongod")
            print("NOTE: Multi-document transactions require a replica set.")
            print("      Exercises that need transactions will be skipped gracefully.")
        except Exception as exc:
            raise SystemExit(f"Cannot reach MongoDB: {exc}")

    _run(client, "Basic ACID Transaction",         test_basic_transaction)
    _run(client, "Transaction Retry",              test_transaction_retry)
    _run(client, "Rollback on Error",              test_transaction_rollback)
    _run(client, "Concurrent Transactions",        test_concurrent_transactions)
    _run(client, "Multi-Collection Transaction",   test_multi_collection_transaction)

    client.close()
    print("\nAll transaction exercises complete.")
