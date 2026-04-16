// gateway/src/server.js
// Apollo Gateway — unified entry point that federates all three services
const { ApolloServer }  = require('apollo-server');
const { ApolloGateway, RemoteGraphQLDataSource } = require('@apollo/gateway');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'itd103-secret-key-change-in-production';

// ─── Custom Data Source ────────────────────────────────────
// Forwards the authenticated user's ID to downstream services via header
class AuthenticatedDataSource extends RemoteGraphQLDataSource {
  willSendRequest({ request, context }) {
    if (context.user) {
      request.http.headers.set('user-id',   context.user.userId);
      request.http.headers.set('user-role', context.user.role);
    }
  }

  // Optional: cache GET responses for read-heavy queries
  didReceiveResponse({ response }) {
    return response;
  }
}

// ─── Gateway Configuration ─────────────────────────────────
const gateway = new ApolloGateway({
  serviceList: [
    { name: 'books', url: process.env.BOOKS_SERVICE_URL || 'http://localhost:4001/graphql' },
    { name: 'users', url: process.env.USERS_SERVICE_URL || 'http://localhost:4002/graphql' },
    { name: 'loans', url: process.env.LOANS_SERVICE_URL || 'http://localhost:4003/graphql' }
  ],

  buildService: ({ url }) => new AuthenticatedDataSource({ url }),

  // Poll services every 10 seconds for schema changes
  pollIntervalInMs: 10000
});

// ─── Server Bootstrap ──────────────────────────────────────
async function start() {
  const server = new ApolloServer({
    gateway,
    subscriptions: false,   // Subscriptions not supported via gateway in v2

    context: ({ req }) => {
      let user = null;
      const authHeader = req.headers.authorization;
      if (authHeader) {
        const token = authHeader.replace('Bearer ', '');
        try {
          user = jwt.verify(token, JWT_SECRET);
        } catch {
          // Invalid token — proceed as unauthenticated
        }
      }
      return { user };
    }
  });

  const { url } = await server.listen(4000);
  console.log(`Gateway ready at ${url}`);
  console.log('Federated services:');
  console.log('  Books  → http://localhost:4001/graphql');
  console.log('  Users  → http://localhost:4002/graphql');
  console.log('  Loans  → http://localhost:4003/graphql');
}

start().catch(console.error);
