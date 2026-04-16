// src/pubsub.js
// PubSub enables real-time events between mutations and subscriptions.
// In production, replace with Redis-based PubSub for multi-instance support.

const { PubSub } = require('graphql-subscriptions');

const pubsub = new PubSub();

const EVENTS = {
  BOOK_ADDED:   'BOOK_ADDED',
  BOOK_UPDATED: 'BOOK_UPDATED'
};

module.exports = { pubsub, EVENTS };
