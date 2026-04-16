// src/schema/typeDefs.js  (Lab 11 — updated with auth + subscriptions)
const { gql } = require('apollo-server-express');

const typeDefs = gql`
  type Book {
    id: ID!
    title: String!
    author: Author!
    genre: String!
    publishedYear: Int
    price: Float!
    inStock: Boolean!
  }

  type Author {
    id: ID!
    name: String!
    bio: String
    birthYear: Int
    nationality: String
    books: [Book!]!
  }

  type User {
    id: ID!
    username: String!
    email: String!
    role: String!
    createdAt: String!
  }

  type AuthPayload {
    token: String!
    user: User!
  }

  input BookInput {
    title: String!
    authorId: ID!
    genre: String!
    publishedYear: Int
    price: Float!
    inStock: Boolean
  }

  input BookUpdateInput {
    title: String
    genre: String
    publishedYear: Int
    price: Float
    inStock: Boolean
  }

  input AuthorInput {
    name: String!
    bio: String
    birthYear: Int
    nationality: String
  }

  input UserInput {
    username: String!
    email: String!
    password: String!
  }

  input LoginInput {
    email: String!
    password: String!
  }

  type Query {
    books: [Book!]!
    book(id: ID!): Book
    booksByGenre(genre: String!): [Book!]!
    authors: [Author!]!
    author(id: ID!): Author
    me: User
    users: [User!]!
  }

  type Mutation {
    addBook(input: BookInput!): Book!
    updateBook(id: ID!, input: BookUpdateInput!): Book!
    deleteBook(id: ID!): Book!
    toggleStock(id: ID!): Book!
    addAuthor(input: AuthorInput!): Author!
    register(input: UserInput!): AuthPayload!
    login(input: LoginInput!): AuthPayload!
    updateRole(userId: ID!, role: String!): User!
  }

  type Subscription {
    bookAdded: Book!
    bookUpdated: Book!
  }
`;

module.exports = typeDefs;
