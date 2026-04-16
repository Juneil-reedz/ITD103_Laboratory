// src/models/Author.js
const mongoose = require('mongoose');

const authorSchema = new mongoose.Schema({
  name:        { type: String, required: true, unique: true },
  bio:         { type: String },
  birthYear:   { type: Number },
  nationality: { type: String }
});

module.exports = mongoose.model('Author', authorSchema);
