// src/utils/auth.js
const jwt = require('jsonwebtoken');

const JWT_SECRET  = process.env.JWT_SECRET || 'itd103-secret-key-change-in-production';
const JWT_EXPIRES = '24h';

// Generate a signed JWT for a given user
const generateToken = (user) => {
  return jwt.sign(
    { userId: user.id, role: user.role },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES }
  );
};

// Verify token from Authorization header and return decoded payload
const authenticate = (context) => {
  const authHeader = context.req.headers.authorization;
  if (!authHeader) {
    throw new Error('Authentication required — provide Authorization: Bearer <token>');
  }

  const token = authHeader.replace('Bearer ', '');
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    throw new Error('Invalid or expired token');
  }
};

// Throw if authenticated user does not have the required role
const authorize = (user, requiredRole) => {
  if (!user) throw new Error('Not authenticated');
  if (user.role !== requiredRole && user.role !== 'admin') {
    throw new Error(`Insufficient permissions. Required: ${requiredRole}`);
  }
};

module.exports = { generateToken, authenticate, authorize };
