// books-service/src/server.js
// Federated service — owns Book type and MongoDB data source
const { ApolloServer, gql } = require('apollo-server');
const { buildFederatedSchema } = require('@apollo/federation');
const mongoose = require('mongoose');

// ─── Book Model ────────────────────────────────────────────
const bookSchema = new mongoose.Schema({
  title:           { type: String, required: true },
  author:          { type: String, required: true },
  genre:           { type: String, required: true },
  publishedYear:   { type: Number },
  isbn:            { type: String, required: true, unique: true },
  totalCopies:     { type: Number, required: true },
  availableCopies: { type: Number, required: true }
});

const Book = mongoose.model('Book', bookSchema);

// ─── Type Definitions ──────────────────────────────────────
const typeDefs = gql`
  type Book @key(fields: "id") {
    id: ID!
    title: String!
    author: String!
    genre: String!
    publishedYear: Int
    isbn: String!
    availableCopies: Int!
  }

  extend type Query {
    books: [Book!]!
    book(id: ID!): Book
    searchBooks(query: String!): [Book!]!
  }

  extend type Mutation {
    addBook(
      title: String!
      author: String!
      genre: String!
      publishedYear: Int
      isbn: String!
      totalCopies: Int!
    ): Book!
    updateCopies(id: ID!, delta: Int!): Book!
  }
`;

// ─── Resolvers ─────────────────────────────────────────────
const resolvers = {
  Book: {
    // Federation: resolve this entity by its @key field
    __resolveReference: async ({ id }) => {
      return await Book.findById(id);
    }
  },

  Query: {
    books:       async ()          => await Book.find(),
    book:        async (_, { id }) => await Book.findById(id),
    searchBooks: async (_, { query }) =>
      await Book.find({
        $or: [
          { title:  { $regex: query, $options: 'i' } },
          { author: { $regex: query, $options: 'i' } },
          { genre:  { $regex: query, $options: 'i' } }
        ]
      })
  },

  Mutation: {
    addBook: async (_, args) => {
      const book = new Book({ ...args, availableCopies: args.totalCopies });
      return await book.save();
    },

    updateCopies: async (_, { id, delta }) => {
      const book = await Book.findById(id);
      if (!book) throw new Error('Book not found');
      book.availableCopies = Math.max(0, book.availableCopies + delta);
      return await book.save();
    }
  }
};

// ─── Server Bootstrap ──────────────────────────────────────
async function start() {
  await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/library_books');
  console.log('Books service: connected to MongoDB');

  const server = new ApolloServer({
    schema: buildFederatedSchema([{ typeDefs, resolvers }])
  });

  const { url } = await server.listen(4001);
  console.log(`Books service ready at ${url}`);
}

start().catch(console.error);
