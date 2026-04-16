# Lab 12: GraphQL with Multiple Data Sources

## Objectives
- Integrate GraphQL with MongoDB (books, loans) and Neo4j (users/graph)
- Implement Apollo Federation across 3 microservices
- Create a unified API gateway

## Architecture
```
Client → Gateway (:4000)
              ├── books-service  (:4001)  ← MongoDB
              ├── users-service  (:4002)  ← Neo4j
              └── loans-service  (:4003)  ← MongoDB
```

## Files
```
library-system/
├── books-service/src/server.js   ← Book type, MongoDB CRUD
├── users-service/src/server.js   ← User type, Neo4j graph queries
├── loans-service/src/server.js   ← Loan type, borrow/return logic
├── gateway/src/server.js         ← Apollo Gateway, auth context
├── docker-compose.yml            ← Full stack with one command
└── (each service has package.json)
test_queries.graphql              ← Cross-service federated queries
```

## Quick Start (Docker — recommended)
```bash
cd lab12/library-system
docker-compose up
```
Gateway: `http://localhost:4000`

## Quick Start (Manual — 5 terminals)
```bash
# Terminal 1 — MongoDB
mongod --port 27017

# Terminal 2 — Neo4j
docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.15

# Terminal 3
cd books-service && npm install && npm start

# Terminal 4
cd users-service && npm install && npm start

# Terminal 5
cd loans-service && npm install && npm start

# Terminal 6
cd gateway && npm install && npm start
```

## Working Queries (Run in Order)

Open `http://localhost:4000/graphql` and run these in order:

### Step 1 — Add a book (books-service → MongoDB)
```graphql
mutation {
  addBook(
    title: "MongoDB: The Definitive Guide"
    author: "Shannon Bradshaw"
    genre: "Technology"
    isbn: "978-1491954461"
    totalCopies: 5
  ) {
    id
    title
  }
}
```

### Step 2 — Register a user (users-service → Neo4j)
```graphql
mutation {
  registerUser(
    name: "Alice Santos"
    email: "alice@library.com"
    membershipType: "Premium"
  ) {
    id
    name
    membershipType
    joinedDate
  }
}
```

### Step 3 — Create a loan (loans-service → MongoDB)
Replace `USER_ID` and `BOOK_ID` with the IDs from Steps 1 and 2:
```graphql
mutation {
  createLoan(
    userId: "USER_ID"
    bookId: "BOOK_ID"
    dueDays: 14
  ) {
    id
    dueDate
    isOverdue
  }
}
```

### Step 4 — Federated query across all 3 services
```graphql
query {
  loans {
    id
    borrowedAt
    dueDate
    isOverdue
    user {
      name
      email
    }
    book {
      title
      author
    }
  }
}
```

**Expected response** — data pulled from 3 separate databases in one query:
```json
{
  "data": {
    "loans": [
      {
        "id": "...",
        "borrowedAt": "2026-04-13T05:58:37.306Z",
        "dueDate": "2026-04-27T05:58:37.303Z",
        "isOverdue": false,
        "user": {
          "name": "Alice Santos",
          "email": "alice@library.com"
        },
        "book": {
          "title": "MongoDB: The Definitive Guide",
          "author": "Shannon Bradshaw"
        }
      }
    ]
  }
}
```

| Field | Source |
|-------|--------|
| `id`, `borrowedAt`, `dueDate`, `isOverdue` | loans-service (MongoDB) |
| `user.name`, `user.email` | users-service (Neo4j) |
| `book.title`, `book.author` | books-service (MongoDB) |

### Step 5 — Search books
```graphql
query {
  searchBooks(query: "MongoDB") {
    id
    title
    author
    availableCopies
  }
}
```

### Step 6 — Return a book (replace LOAN_ID)
```graphql
mutation {
  returnBook(loanId: "LOAN_ID") {
    id
    returnedAt
    isOverdue
    book {
      title
    }
  }
}
```

---

## Federation Key Points
| Concept | Description |
|---------|-------------|
| `@key(fields: "id")` | Marks entity as resolvable across services |
| `__resolveReference` | How a service resolves its own entity by key |
| `extend type` | Reference a type owned by another service |
| `@external` | Field owned by another service |

## Deliverables
- [ ] Complete federated GraphQL architecture
- [ ] Multiple service implementations
- [ ] Gateway configuration
- [ ] Performance optimization report
