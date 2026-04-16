// src/schema/typeDefs.js
const { buildSchema } = require('graphql');

const typeDefs = buildSchema(`
  type Book {
    id: ID!
    title: String!
    author: String!
    genre: String!
    publishedYear: Int
    price: Float!
    inStock: Boolean!
  }

  type Author {
    id: ID!
    name: String!
    books: [Book!]!
  }

  input BookInput {
    title: String!
    author: String!
    genre: String!
    publishedYear: Int
    price: Float!
    inStock: Boolean
  }

  input BookUpdateInput {
    title: String
    author: String
    genre: String
    publishedYear: Int
    price: Float
    inStock: Boolean
  }

  type Query {
    books: [Book!]!
    book(id: ID!): Book
    booksByGenre(genre: String!): [Book!]!
    booksByAuthor(author: String!): [Book!]!
    authors: [Author!]!
    author(name: String!): Author
  }

  type Mutation {
    addBook(input: BookInput!): Book!
    updateBook(id: ID!, input: BookUpdateInput!): Book!
    deleteBook(id: ID!): Book!
    toggleStock(id: ID!): Book!
    addBooks(books: [BookInput!]!): [Book!]!
  }
`);

module.exports = typeDefs;
