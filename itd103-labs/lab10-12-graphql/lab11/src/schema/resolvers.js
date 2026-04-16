// src/schema/resolvers.js  (Lab 11 — DataLoader + auth + subscriptions)
const Book    = require('../models/Book');
const Author  = require('../models/Author');
const User    = require('../models/User');
const { generateToken, authorize } = require('../utils/auth');
const { pubsub, EVENTS }           = require('../pubsub');

const resolvers = {
  // ─── Field-level (nested) resolvers ───────────────────────
  // These fire per-object and use DataLoader to batch DB calls
  Book: {
    author: async (parent, _, { loaders }) => {
      // DataLoader batches all author lookups from a single query result
      return await loaders.author.load(parent.author.toString());
    }
  },

  Author: {
    books: async (parent) => {
      return await Book.find({ author: parent._id });
    }
  },

  // ─── Query Resolvers ───────────────────────────────────────
  Query: {
    books: async () => await Book.find(),

    book: async (_, { id }) => {
      const book = await Book.findById(id);
      if (!book) throw new Error('Book not found');
      return book;
    },

    booksByGenre: async (_, { genre }) => await Book.find({ genre }),

    authors: async () => await Author.find(),

    author: async (_, { id }) => {
      const author = await Author.findById(id);
      if (!author) throw new Error('Author not found');
      return author;
    },

    me: async (_, __, { user }) => {
      if (!user) throw new Error('Not authenticated');
      return await User.findById(user.userId);
    },

    users: async (_, __, { user }) => {
      authorize(user, 'admin');   // only admins can list all users
      return await User.find();
    }
  },

  // ─── Mutation Resolvers ────────────────────────────────────
  Mutation: {
    addBook: async (_, { input }, { user }) => {
      if (!user) throw new Error('Authentication required');
      const book = new Book(input);
      const saved = await book.save();
      // Publish real-time event to subscribers
      pubsub.publish(EVENTS.BOOK_ADDED, { bookAdded: saved });
      return saved;
    },

    updateBook: async (_, { id, input }, { user }) => {
      if (!user) throw new Error('Authentication required');
      const book = await Book.findByIdAndUpdate(
        id, { $set: input }, { new: true, runValidators: true }
      );
      if (!book) throw new Error('Book not found');
      pubsub.publish(EVENTS.BOOK_UPDATED, { bookUpdated: book });
      return book;
    },

    deleteBook: async (_, { id }, { user }) => {
      authorize(user, 'admin');   // only admins can delete
      const book = await Book.findByIdAndDelete(id);
      if (!book) throw new Error('Book not found');
      return book;
    },

    toggleStock: async (_, { id }, { user }) => {
      if (!user) throw new Error('Authentication required');
      const book = await Book.findById(id);
      if (!book) throw new Error('Book not found');
      book.inStock = !book.inStock;
      return await book.save();
    },

    addAuthor: async (_, { input }, { user }) => {
      if (!user) throw new Error('Authentication required');
      const author = new Author(input);
      return await author.save();
    },

    register: async (_, { input }) => {
      const existing = await User.findOne({ email: input.email });
      if (existing) throw new Error('Email already registered');
      const user = new User(input);
      await user.save();
      const token = generateToken(user);
      return { token, user };
    },

    login: async (_, { input }) => {
      const user = await User.findOne({ email: input.email });
      if (!user) throw new Error('Invalid credentials');
      const valid = await user.comparePassword(input.password);
      if (!valid) throw new Error('Invalid credentials');
      const token = generateToken(user);
      return { token, user };
    },

    updateRole: async (_, { userId, role }, { user }) => {
      authorize(user, 'admin');
      const updated = await User.findByIdAndUpdate(
        userId, { role }, { new: true }
      );
      if (!updated) throw new Error('User not found');
      return updated;
    }
  },

  // ─── Subscription Resolvers ────────────────────────────────
  Subscription: {
    bookAdded: {
      subscribe: () => pubsub.asyncIterator([EVENTS.BOOK_ADDED])
    },
    bookUpdated: {
      subscribe: () => pubsub.asyncIterator([EVENTS.BOOK_UPDATED])
    }
  }
};

module.exports = resolvers;
