# Lab 17 – Consistency Models

## Overview
Explore the CAP theorem in practice, compare strong vs eventual consistency
through read/write concern combinations, and implement ACID multi-document
transactions in MongoDB.

## Exercises

| Exercise | File | Description |
|----------|------|-------------|
| 1 | `lab17_consistency_models.py` | CAP tradeoffs, causal sessions, stale-read demo |
| 2 | `lab17_transactions.py` | ACID transactions, rollback, retry, concurrency |

## Prerequisites

```bash
pip install -r ../requirements.txt
```

Exercises run on a **standalone** mongod for most demos.  
Replica set (rs0) unlocks the full stale-read and causal-session sections.

## Run Order

```bash
python lab17_consistency_models.py
python lab17_transactions.py
```

## Expected Output

### Exercise 1 – Consistency Models
```
=== A. CAP Theorem – CP vs AP Trade-offs ===
  CP write (w=majority, j=True)  :  8.72 ms
  AP write (w=0, unacknowledged) :  0.11 ms
  CP is ~79× slower but guarantees durability.

=== B. Strong vs Eventual Consistency ===
  Strong consistency   – read-your-own-write visible : 100%
  Eventual consistency – read-your-own-write visible : 80%

=== E. Consistency Model Summary ===
  Model                  WriteConcern            ReadPref                Read-YW   Stale?   Perf
  -------...
  Strong                 w=majority, j=True      PRIMARY                 Yes       No       Slowest
  Eventual               w=0                     nearest                 No        Yes      Fastest
```

### Exercise 2 – Transactions
```
=== A. Basic ACID Transaction (funds transfer) ===
  Transferring $500 from A001 (Alice) → A002 (Bob) …
  Transaction committed.
  Account balances (after):
    A001 Alice   $4500.00
    A002 Bob     $3500.00
    A003 Carol   $1500.00
    TOTAL          $9500.00
  Conservation check passed: total money unchanged.

=== C. Rollback on Error (insufficient funds) ===
  Attempting to transfer $5 000 from Carol (A003) → Alice …
  Transaction aborted: Insufficient funds: Carol has $1 500.00, need $5 000
  Account balances (after rollback): [unchanged]
```

## Key Concepts

### CAP Theorem
| Property | Guarantee |
|----------|-----------|
| Consistency | Every read receives the most recent write |
| Availability | Every request gets a non-error response |
| Partition tolerance | System continues despite network splits |

In MongoDB:
- **CP** → `w=majority, j=True` + `readPreference=primary`
- **AP** → `w=1` (or `w=0`) + `readPreference=secondaryPreferred`

### Write Concerns
| Level | Meaning |
|-------|---------|
| `w=0` | Fire and forget – no acknowledgement |
| `w=1` | Primary acknowledged (default) |
| `w=majority` | Quorum of voting members acknowledged |
| `j=True` | Journaled to disk before acknowledgement |

### Read Preferences
| Level | Routes reads to |
|-------|----------------|
| `primary` | Primary only (strong consistency) |
| `primaryPreferred` | Primary if available, else secondary |
| `secondaryPreferred` | Secondary if available (may be stale) |
| `nearest` | Lowest network latency member |

### ACID in MongoDB Transactions
| Property | How MongoDB achieves it |
|----------|------------------------|
| Atomicity | All ops in the session commit or all abort |
| Consistency | Schema validation + application logic |
| Isolation | Snapshot isolation within a transaction |
| Durability | `j=True` or `w=majority` write concern |
