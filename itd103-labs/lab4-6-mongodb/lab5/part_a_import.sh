#!/usr/bin/env bash
# =============================================================
# Lab 5 – Part A: Import Sales & Customers Datasets
# Run from the itd103-labs/ root directory
# =============================================================

# Import sales transactions
mongoimport \
  --db sales \
  --collection transactions \
  --file datasets/sales.json \
  --jsonArray

# Import customers (needed for $lookup in Exercise 2)
mongoimport \
  --db sales \
  --collection customers \
  --file datasets/customers.json \
  --jsonArray

echo "Import complete. Verifying..."

mongosh --quiet --eval "
  use sales
  print('Transactions:', db.transactions.countDocuments())
  print('Customers:',    db.customers.countDocuments())
"
