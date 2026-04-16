// src/dataloaders/authorLoader.js
// DataLoader batches multiple individual author lookups into one DB query,
// solving the N+1 problem: instead of 1 query per book, it fires 1 query total.

const DataLoader = require('dataloader');
const Author     = require('../models/Author');

const createAuthorLoader = () =>
  new DataLoader(async (authorIds) => {
    try {
      const authors = await Author.find({ _id: { $in: authorIds } });

      // Map authors by string ID for O(1) lookup
      const authorMap = {};
      authors.forEach(author => {
        authorMap[author._id.toString()] = author;
      });

      // Return authors in the SAME ORDER as the requested IDs
      // DataLoader requires this order to be preserved
      return authorIds.map(id => authorMap[id.toString()] || null);
    } catch (error) {
      throw new Error('Error loading authors: ' + error.message);
    }
  });

module.exports = createAuthorLoader;
