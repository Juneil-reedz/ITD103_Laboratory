// src/models/Book.js  (updated — author references Author collection)
const mongoose = require('mongoose');

const bookSchema = new mongoose.Schema({
  title:         { type: String, required: true },
  author:        { type: mongoose.Schema.Types.ObjectId, ref: 'Author', required: true },
  genre:         { type: String, required: true },
  publishedYear: { type: Number },
  price:         { type: Number, required: true },
  inStock:       { type: Boolean, default: true }
});

module.exports = mongoose.model('Book', bookSchema);
