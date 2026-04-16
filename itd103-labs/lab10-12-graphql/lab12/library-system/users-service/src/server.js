// users-service/src/server.js
// Federated service — owns User type and Neo4j data source
const { ApolloServer, gql } = require('apollo-server');
const { buildFederatedSchema } = require('@apollo/federation');
const neo4j = require('neo4j-driver');

// ─── Type Definitions ──────────────────────────────────────
const typeDefs = gql`
  type User @key(fields: "id") {
    id: ID!
    name: String!
    email: String!
    membershipType: String!
    joinedDate: String!
    borrowedBooks: [Book]
    friends: [User]
  }

  # Reference to Book from books-service (no fields — resolved there)
  extend type Book @key(fields: "id") {
    id: ID! @external
  }

  extend type Query {
    users: [User!]!
    user(id: ID!): User
    recommendedBooks(userId: ID!): [Book!]!
  }

  extend type Mutation {
    registerUser(name: String!, email: String!, membershipType: String!): User!
    addFriend(userId: ID!, friendId: ID!): User!
  }
`;

// ─── Helpers ───────────────────────────────────────────────
const toUser = (record, key = 'u') => record.get(key).properties;

// ─── Resolvers ─────────────────────────────────────────────
const resolvers = {
  User: {
    __resolveReference: async ({ id }, { driver }) => {
      const session = driver.session();
      try {
        const result = await session.run(
          'MATCH (u:User {id: $id}) RETURN u', { id }
        );
        return result.records[0] ? toUser(result.records[0]) : null;
      } finally {
        await session.close();
      }
    },

    borrowedBooks: async (parent, _, { driver }) => {
      const session = driver.session();
      try {
        const result = await session.run(
          'MATCH (u:User {id: $userId})-[:BORROWED]->(b:Book) RETURN b',
          { userId: parent.id }
        );
        // Return stub objects — federation will resolve full Book via books-service
        return result.records.map(r => ({ __typename: 'Book', id: r.get('b').properties.id }));
      } finally {
        await session.close();
      }
    },

    friends: async (parent, _, { driver }) => {
      const session = driver.session();
      try {
        const result = await session.run(
          'MATCH (u:User {id: $userId})-[:FRIENDS_WITH]->(f:User) RETURN f',
          { userId: parent.id }
        );
        return result.records.map(r => r.get('f').properties);
      } finally {
        await session.close();
      }
    }
  },

  Query: {
    users: async (_, __, { driver }) => {
      const session = driver.session();
      try {
        const result = await session.run('MATCH (u:User) RETURN u');
        return result.records.map(r => toUser(r));
      } finally {
        await session.close();
      }
    },

    user: async (_, { id }, { driver }) => {
      const session = driver.session();
      try {
        const result = await session.run(
          'MATCH (u:User {id: $id}) RETURN u', { id }
        );
        return result.records[0] ? toUser(result.records[0]) : null;
      } finally {
        await session.close();
      }
    },

    // Friends-based book recommendation using graph traversal
    recommendedBooks: async (_, { userId }, { driver }) => {
      const session = driver.session();
      try {
        const result = await session.run(`
          MATCH (u:User {id: $userId})-[:FRIENDS_WITH]->(friend:User)
          MATCH (friend)-[:BORROWED]->(b:Book)
          WHERE NOT (u)-[:BORROWED]->(b)
          RETURN b.id AS bookId, count(friend) AS friendCount
          ORDER BY friendCount DESC
          LIMIT 10
        `, { userId });
        return result.records.map(r => ({
          __typename: 'Book',
          id: r.get('bookId')
        }));
      } finally {
        await session.close();
      }
    }
  },

  Mutation: {
    registerUser: async (_, { name, email, membershipType }, { driver }) => {
      const session = driver.session();
      try {
        const id = `user-${Date.now()}`;
        const result = await session.run(`
          CREATE (u:User {
            id: $id, name: $name, email: $email,
            membershipType: $membershipType,
            joinedDate: $joinedDate
          }) RETURN u
        `, { id, name, email, membershipType, joinedDate: new Date().toISOString() });
        return toUser(result.records[0]);
      } finally {
        await session.close();
      }
    },

    addFriend: async (_, { userId, friendId }, { driver }) => {
      const session = driver.session();
      try {
        await session.run(`
          MATCH (u:User {id: $userId}), (f:User {id: $friendId})
          MERGE (u)-[:FRIENDS_WITH]->(f)
        `, { userId, friendId });
        const result = await session.run(
          'MATCH (u:User {id: $userId}) RETURN u', { userId }
        );
        return toUser(result.records[0]);
      } finally {
        await session.close();
      }
    }
  }
};

// ─── Server Bootstrap ──────────────────────────────────────
const driver = neo4j.driver(
  process.env.NEO4J_URI || 'bolt://localhost:7687',
  neo4j.auth.basic(
    process.env.NEO4J_USER     || 'neo4j',
    process.env.NEO4J_PASSWORD || 'password'
  )
);

async function start() {
  const server = new ApolloServer({
    schema: buildFederatedSchema([{ typeDefs, resolvers }]),
    context: () => ({ driver })
  });

  const { url } = await server.listen(4002);
  console.log(`Users service ready at ${url}`);
}

start().catch(console.error);
