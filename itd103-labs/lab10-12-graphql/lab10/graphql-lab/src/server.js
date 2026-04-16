// src/server.js
const express      = require('express');
const { graphqlHTTP } = require('express-graphql');
const connectDB    = require('./config/database');
const typeDefs     = require('./schema/typeDefs');
const resolvers    = require('./schema/resolvers');

const app = express();

// Connect to MongoDB
connectDB();

// GraphQL endpoint
app.use('/graphql', graphqlHTTP({
  schema:    typeDefs,
  rootValue: resolvers,
  graphiql:  true   // enables GraphiQL browser UI at /graphql
}));

// Health check
app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`GraphQL server running at http://localhost:${PORT}/graphql`);
  console.log(`GraphiQL interface available at http://localhost:${PORT}/graphql`);
});
