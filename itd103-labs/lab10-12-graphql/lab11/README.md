# Lab 11: Advanced GraphQL Features

## Objectives
- Solve N+1 with DataLoader
- Add JWT authentication and role-based authorization
- Implement real-time subscriptions

## Files
```
src/
├── models/
│   ├── Author.js               ← Author Mongoose model
│   ├── Book.js                 ← Book model (references Author by ObjectId)
│   └── User.js                 ← User model with bcrypt password hashing
├── dataloaders/
│   └── authorLoader.js         ← DataLoader: batch author lookups
├── utils/
│   └── auth.js                 ← JWT generate / verify / authorize
├── pubsub.js                   ← PubSub instance + event name constants
├── schema/
│   ├── typeDefs.js             ← Updated schema with User, AuthPayload, Subscription
│   └── resolvers.js            ← Full resolvers with auth guards + pubsub publish
└── server.js                   ← Apollo Server with context + subscription handlers
package.json
```

## Quick Start
```bash
cd lab11
npm install
node src/server.js
```
API: `http://localhost:4010/graphql`

---

## Working Queries (Run in Order)

Open `http://localhost:4010/graphql`

### Step 1 — Register a user
```graphql
mutation {
  register(input: {
    username: "alice"
    email: "alice@email.com"
    password: "secret123"
  }) {
    token
    user {
      id
      username
      role
    }
  }
}
```
Copy the `token` from the response.

### Step 2 — Add Authorization header
In GraphiQL click **Headers** (bottom panel) and add:
```json
{
  "Authorization": "Bearer PASTE_TOKEN_HERE"
}
```

### Step 3 — Add an author (requires token)
```graphql
mutation {
  addAuthor(input: {
    name: "Robert C. Martin"
    bio: "Software engineer and author"
    birthYear: 1952
    nationality: "American"
  }) {
    id
    name
  }
}
```
Copy the author `id`.

### Step 4 — Add a book (requires token)
Replace `AUTHOR_ID` with the id from Step 3:
```graphql
mutation {
  addBook(input: {
    title: "Clean Code"
    authorId: "AUTHOR_ID"
    genre: "Technology"
    publishedYear: 2008
    price: 35.99
  }) {
    id
    title
    author {
      name
    }
  }
}
```

### Step 5 — Query books with nested author (DataLoader in action)
```graphql
query {
  books {
    id
    title
    genre
    price
    author {
      name
      nationality
    }
  }
}
```

### Step 6 — Login
```graphql
mutation {
  login(input: {
    email: "alice@email.com"
    password: "secret123"
  }) {
    token
    user {
      id
      username
      role
    }
  }
}
```

### Step 7 — Get current user (requires token)
```graphql
query {
  me {
    id
    username
    email
    role
  }
}
```

### Step 8 — Toggle stock (requires token)
```graphql
mutation {
  toggleStock(id: "BOOK_ID") {
    id
    title
    inStock
  }
}
```

### Step 9 — Delete book (admin only)
Only works if your user has `role: "admin"`. Update role first via MongoDB or use `updateRole` mutation with an existing admin account.
```graphql
mutation {
  deleteBook(id: "BOOK_ID") {
    id
    title
  }
}
```

---

## Auth Flow
1. `register` mutation → returns JWT token
2. Copy token → add header: `Authorization: Bearer <token>`
3. All write mutations now require this header
4. `users` query + `deleteBook` + `updateRole` require `admin` role

## DataLoader — N+1 Fix
Without DataLoader:
- 10 books → 10 separate `Author.findById()` calls

With DataLoader:
- 10 books → 1 batched `Author.find({ _id: { $in: [...] } })` call

## Deliverables
- [ ] Advanced GraphQL server with all features
- [ ] DataLoader implementation
- [ ] Authentication system
- [ ] Subscription test results
