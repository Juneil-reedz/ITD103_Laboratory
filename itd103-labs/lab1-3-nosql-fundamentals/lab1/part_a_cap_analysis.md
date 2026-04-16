# Lab 1 – Part A: CAP Theorem Analysis

## What is CAP Theorem?

CAP Theorem states that a distributed system can only guarantee **two of three** properties simultaneously:

| Property        | Description                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| **C**onsistency | Every read receives the most recent write or an error                       |
| **A**vailability| Every request receives a response (not guaranteed to be the most recent)    |
| **P**artition Tolerance | System continues operating despite network partitions              |

> In real distributed systems, **Partition Tolerance is mandatory** (network failures happen).
> The real choice is: **CP** (Consistency + Partition) vs **AP** (Availability + Partition).

---

## Scenario Analysis

### 1. Online Banking Transaction System
- **Priority:** CP (Consistency + Partition Tolerance)
- **Reasoning:**
  - Money transfers must be accurate — showing a stale balance could cause double-spending or overdrafts.
  - It is acceptable to return an error if data cannot be confirmed consistent.
  - Availability is secondary to correctness.
- **Sacrifice:** Availability — the system may reject requests rather than serve stale data.

---

### 2. Social Media Feed
- **Priority:** AP (Availability + Partition Tolerance)
- **Reasoning:**
  - Users expect feeds to always load, even if some posts are slightly delayed.
  - Seeing a post 2 seconds late is acceptable; a blank feed is not.
  - Eventual consistency is sufficient.
- **Sacrifice:** Consistency — feed may be temporarily out of date.

---

### 3. IoT Sensor Data Collection
- **Priority:** AP (Availability + Partition Tolerance)
- **Reasoning:**
  - Sensors produce high-frequency data; the system must always accept writes.
  - Missing a sensor reading is worse than a brief inconsistency.
  - Data can be reconciled later.
- **Sacrifice:** Consistency — some reads may not reflect the absolute latest sensor value.

---

### 4. E-Commerce Shopping Cart
- **Priority:** AP (Availability + Partition Tolerance)
- **Reasoning:**
  - Cart updates must always succeed so users can continue shopping.
  - Temporary inconsistency (e.g., two devices show slightly different cart states) is tolerable.
  - Consistency is enforced at checkout/payment, not during browsing.
- **Sacrifice:** Consistency — cart state converges eventually.

---

## Database Selection

| Scenario                    | Recommended DB | CAP Type | Justification                                                                 |
|-----------------------------|----------------|----------|-------------------------------------------------------------------------------|
| Online Banking Transactions | **MongoDB**    | CP       | Strong consistency with transactions; supports ACID since v4.0                |
| Social Media Feed           | **Cassandra**  | AP       | Highly available, linearly scalable, tunable consistency for reads/writes     |
| IoT Sensor Data Collection  | **Cassandra**  | AP       | Optimized for high write throughput; handles wide-column time-series data     |
| E-Commerce Shopping Cart    | **Redis**      | AP       | In-memory speed for session/cart data; supports expiry and atomic operations  |

> **Neo4j** is best suited for **relationship-heavy** queries (e.g., recommendation engines, fraud detection graphs) — CP by nature, prioritizing consistency in graph traversals.

---

## CAP Trade-off Summary

```
         Consistency
              /\
             /  \
            / CP \   ← MongoDB, Neo4j
           /------\
          /   ???  \  ← No real system here (CA requires no partitions)
    AP   /----------\ CP
Cassandra              MongoDB
Redis
              P
         Partition Tolerance
```

- **CP systems** → choose correctness over uptime
- **AP systems** → choose uptime over perfect accuracy
- **CA systems** → theoretical only (not viable in distributed environments)
