// src/server.js  (Lab 11 — Apollo Server with auth + DataLoader + subscriptions)
const express             = require('express');
const { ApolloServer }    = require('apollo-server-express');
const { createServer }    = require('http');
const mongoose            = require('mongoose');
const typeDefs            = require('./schema/typeDefs');
const resolvers           = require('./schema/resolvers');
const createAuthorLoader  = require('./dataloaders/authorLoader');
const { authenticate }    = require('./utils/auth');

async function startServer() {
  const app = express();

  // Connect to MongoDB
  await mongoose.connect('mongodb://localhost:27017/graphql_lab11');
  console.log('Connected to MongoDB');

  const server = new ApolloServer({
    typeDefs,
    resolvers,

    // Context runs on every request — attach user + DataLoader instances
    context: ({ req }) => {
      let user = null;
      if (req?.headers?.authorization) {
        try {
          user = authenticate({ req });
        } catch {
          // Invalid token — treat as unauthenticated
        }
      }

      return {
        req,
        user,
        loaders: {
          // New DataLoader per request to prevent cross-request caching
          author: createAuthorLoader()
        }
      };
    }
  });

  await server.start();
  server.applyMiddleware({ app });

  const PORT = process.env.PORT || 4010;
  app.listen(PORT, () => {
    console.log(`GraphQL API: http://localhost:${PORT}${server.graphqlPath}`);
  });
}

startServer().catch(console.error);
