# Lab 10: GraphQL Fundamentals

## Objectives
- Understand GraphQL schema design
- Implement basic queries and mutations
- Set up a GraphQL server with MongoDB

## Files
```
graphql-lab/
├── src/
│   ├── config/database.js      ← MongoDB connection
│   ├── models/Book.js          ← Mongoose schema
│   ├── schema/typeDefs.js      ← GraphQL type definitions
│   ├── schema/resolvers.js     ← Query + Mutation resolvers
│   └── server.js               ← Express + express-graphql server
├── package.json
test_queries.graphql             ← All test queries for GraphiQL
```

## Quick Start
```bash
cd lab10/graphql-lab
npm install
npm run dev
```
Open GraphiQL: `http://localhost:4000/graphql`

## Run Order in GraphiQL

Open `http://localhost:4000/graphql` and run these in order:

### Step 1 — Seed sample books
```graphql
mutation {
  addBooks(books: [
    { title: "The Great Gatsby", author: "F. Scott Fitzgerald", genre: "Classic", publishedYear: 1925, price: 12.99 }
    { title: "Harry Potter", author: "J.K. Rowling", genre: "Fantasy", publishedYear: 1997, price: 15.99 }
    { title: "The Hobbit", author: "J.R.R. Tolkien", genre: "Fantasy", publishedYear: 1937, price: 13.99 }
    { title: "Clean Code", author: "Robert C. Martin", genre: "Technology", publishedYear: 2008, price: 35.99 }
  ]) {
    id
    title
    author
  }
}
```

### Step 2 — Query all books
```graphql
query {
  books {
    id
    title
    author
    genre
    price
    inStock
  }
}
```

### Step 3 — Filter by genre
```graphql
query {
  booksByGenre(genre: "Fantasy") {
    title
    author
    publishedYear
  }
}
```

### Step 4 — Query all authors with their books
```graphql
query {
  authors {
    name
    books {
      title
      genre
    }
  }
}
```

### Step 5 — Update a book (paste a real `id` from Step 2)
```graphql
mutation {
  updateBook(id: "PASTE_ID_HERE", input: { price: 9.99, inStock: false }) {
    title
    price
    inStock
  }
}
```

### Step 6 — Toggle stock status
```graphql
mutation {
  toggleStock(id: "PASTE_ID_HERE") {
    title
    inStock
  }
}
```

### Step 7 — Delete a book
```graphql
mutation {
  deleteBook(id: "PASTE_ID_HERE") {
    id
    title
  }
}
```

## Key Concepts
| Concept | Description |
|---------|-------------|
| Type | Defines shape of data (`Book`, `Author`) |
| Query | Read operations |
| Mutation | Write operations (add, update, delete) |
| Input type | Structured argument for mutations |
| Resolver | Function that fetches/modifies data |

## Deliverables
- [ ] Complete GraphQL server code
- [ ] GraphiQL test results (screenshots)
- [ ] API documentation
