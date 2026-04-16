#!/usr/bin/env bash
# =============================================================
# Lab 4 – Part A: Import Dataset
# Run from the itd103-labs/ root directory
# =============================================================

# Import restaurants dataset into the 'food' database
mongoimport \
  --db food \
  --collection restaurants \
  --file datasets/restaurants.json \
  --jsonArray

echo "Import complete. Verifying..."

# Quick count check
mongosh --quiet --eval "
  use food
  print('Documents imported:', db.restaurants.countDocuments())
"
