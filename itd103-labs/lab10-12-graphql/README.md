# Labs 10–12: GraphQL

## Overview
| Lab | Topic | Key Skills |
|-----|-------|-----------|
| [Lab 10](./lab10/) | GraphQL Fundamentals | Schema design, queries, mutations |
| [Lab 11](./lab11/) | Advanced GraphQL | DataLoader, JWT auth, subscriptions |
| [Lab 12](./lab12/) | Multiple Data Sources | Apollo Federation, microservices, gateway |

## Prerequisites
- Node.js 18+
- MongoDB running on port 27017
- Neo4j running on port 7687 (for Lab 12)

## Directory Structure
```
lab10-12-graphql/
├── lab10/
│   ├── README.md
│   ├── graphql-lab/          ← Express + express-graphql server
│   └── test_queries.graphql
├── lab11/
│   ├── README.md
│   ├── src/                  ← Apollo Server with auth + DataLoader
│   └── package.json
├── lab12/
│   ├── README.md
│   ├── library-system/       ← 3 federated microservices + gateway
│   └── test_queries.graphql
└── README.md
```
