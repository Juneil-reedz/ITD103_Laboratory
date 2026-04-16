// loans-service/src/server.js
// Federated service — owns Loan type (tracks who borrowed what and when)
const { ApolloServer, gql } = require('apollo-server');
const { buildFederatedSchema } = require('@apollo/federation');
const mongoose = require('mongoose');

// ─── Loan Model ────────────────────────────────────────────
const loanSchema = new mongoose.Schema({
  userId:     { type: String, required: true },
  bookId:     { type: String, required: true },
  borrowedAt: { type: Date,   default: Date.now },
  dueDate:    { type: Date,   required: true },
  returnedAt: { type: Date }
});

const Loan = mongoose.model('Loan', loanSchema);

// ─── Type Definitions ──────────────────────────────────────
const typeDefs = gql`
  type Loan @key(fields: "id") {
    id: ID!
    user: User!
    book: Book!
    borrowedAt: String!
    dueDate: String!
    returnedAt: String
    isOverdue: Boolean!
  }

  extend type User @key(fields: "id") {
    id: ID! @external
  }

  extend type Book @key(fields: "id") {
    id: ID! @external
  }

  extend type Query {
    loans: [Loan!]!
    loan(id: ID!): Loan
    loansByUser(userId: ID!): [Loan!]!
    overdueLoans: [Loan!]!
  }

  extend type Mutation {
    createLoan(userId: ID!, bookId: ID!, dueDays: Int): Loan!
    returnBook(loanId: ID!): Loan!
  }
`;

// ─── Resolvers ─────────────────────────────────────────────
const resolvers = {
  Loan: {
    __resolveReference: async ({ id }) => await Loan.findById(id),

    // Return stubs — federation resolves full objects via other services
    user: (parent) => ({ __typename: 'User', id: parent.userId }),
    book: (parent) => ({ __typename: 'Book', id: parent.bookId }),

    borrowedAt:  (parent) => parent.borrowedAt?.toISOString(),
    dueDate:     (parent) => parent.dueDate?.toISOString(),
    returnedAt:  (parent) => parent.returnedAt?.toISOString() || null,
    isOverdue:   (parent) => !parent.returnedAt && new Date() > parent.dueDate
  },

  Query: {
    loans:          async ()          => await Loan.find(),
    loan:           async (_, { id }) => await Loan.findById(id),
    loansByUser:    async (_, { userId }) => await Loan.find({ userId }),
    overdueLoans:   async () =>
      await Loan.find({ returnedAt: null, dueDate: { $lt: new Date() } })
  },

  Mutation: {
    createLoan: async (_, { userId, bookId, dueDays = 14 }) => {
      const dueDate = new Date();
      dueDate.setDate(dueDate.getDate() + dueDays);
      const loan = new Loan({ userId, bookId, dueDate });
      return await loan.save();
    },

    returnBook: async (_, { loanId }) => {
      const loan = await Loan.findById(loanId);
      if (!loan) throw new Error('Loan not found');
      if (loan.returnedAt) throw new Error('Book already returned');
      loan.returnedAt = new Date();
      return await loan.save();
    }
  }
};

// ─── Server Bootstrap ──────────────────────────────────────
async function start() {
  await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/library_loans');
  console.log('Loans service: connected to MongoDB');

  const server = new ApolloServer({
    schema: buildFederatedSchema([{ typeDefs, resolvers }])
  });

  const { url } = await server.listen(4003);
  console.log(`Loans service ready at ${url}`);
}

start().catch(console.error);
