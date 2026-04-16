// src/schema/resolvers.js
const Book = require('../models/Book');

const resolvers = {
  // ─── Query Resolvers ───────────────────────────────────────
  books: async () => {
    try {
      return await Book.find();
    } catch (error) {
      throw new Error('Error fetching books: ' + error.message);
    }
  },

  book: async ({ id }) => {
    try {
      const book = await Book.findById(id);
      if (!book) throw new Error('Book not found');
      return book;
    } catch (error) {
      throw new Error('Error fetching book: ' + error.message);
    }
  },

  booksByGenre: async ({ genre }) => {
    try {
      return await Book.find({ genre });
    } catch (error) {
      throw new Error('Error fetching books by genre: ' + error.message);
    }
  },

  booksByAuthor: async ({ author }) => {
    try {
      return await Book.find({ author });
    } catch (error) {
      throw new Error('Error fetching books by author: ' + error.message);
    }
  },

  authors: async () => {
    try {
      const books = await Book.find();
      const authorsMap = {};

      books.forEach(book => {
        if (!authorsMap[book.author]) {
          authorsMap[book.author] = {
            id: book.author.toLowerCase().replace(/\s+/g, '-'),
            name: book.author,
            books: []
          };
        }
        authorsMap[book.author].books.push(book);
      });

      return Object.values(authorsMap);
    } catch (error) {
      throw new Error('Error fetching authors: ' + error.message);
    }
  },

  author: async ({ name }) => {
    try {
      const books = await Book.find({ author: name });
      if (!books.length) throw new Error('Author not found');
      return {
        id: name.toLowerCase().replace(/\s+/g, '-'),
        name,
        books
      };
    } catch (error) {
      throw new Error('Error fetching author: ' + error.message);
    }
  },

  // ─── Mutation Resolvers ────────────────────────────────────
  addBook: async ({ input }) => {
    try {
      const book = new Book(input);
      return await book.save();
    } catch (error) {
      throw new Error('Error adding book: ' + error.message);
    }
  },

  updateBook: async ({ id, input }) => {
    try {
      const book = await Book.findByIdAndUpdate(
        id,
        { $set: input },
        { new: true, runValidators: true }
      );
      if (!book) throw new Error('Book not found');
      return book;
    } catch (error) {
      throw new Error('Error updating book: ' + error.message);
    }
  },

  deleteBook: async ({ id }) => {
    try {
      const book = await Book.findByIdAndDelete(id);
      if (!book) throw new Error('Book not found');
      return book;
    } catch (error) {
      throw new Error('Error deleting book: ' + error.message);
    }
  },

  toggleStock: async ({ id }) => {
    try {
      const book = await Book.findById(id);
      if (!book) throw new Error('Book not found');
      book.inStock = !book.inStock;
      return await book.save();
    } catch (error) {
      throw new Error('Error toggling stock: ' + error.message);
    }
  },

  addBooks: async ({ books }) => {
    try {
      return await Book.insertMany(books);
    } catch (error) {
      throw new Error('Error adding books: ' + error.message);
    }
  }
};

module.exports = resolvers;
