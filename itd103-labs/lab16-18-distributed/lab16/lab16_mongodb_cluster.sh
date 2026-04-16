#!/bin/bash
# =============================================================
# Lab 16 – Exercise 1: MongoDB Replica Set Setup
# Run each step in a separate terminal as noted below.
# =============================================================

# ── Step 1: Create data directories ───────────────────────
mkdir -p ./data/rs1 ./data/rs2 ./data/rs3
echo "Data directories created: ./data/rs1  ./data/rs2  ./data/rs3"

# ── Step 2: Start mongod instances (separate terminals) ────
# Open Terminal 1 and run:
#   mongod --replSet rs0 --port 27017 --dbpath ./data/rs1 --bind_ip localhost
#
# Open Terminal 2 and run:
#   mongod --replSet rs0 --port 27018 --dbpath ./data/rs2 --bind_ip localhost
#
# Open Terminal 3 and run:
#   mongod --replSet rs0 --port 27019 --dbpath ./data/rs3 --bind_ip localhost

# ── Step 3: Initiate the replica set ──────────────────────
# Connect to any member (e.g., port 27017):
#   mongosh --port 27017
#
# Then in the mongosh shell run:
#
#   rs.initiate({
#     _id: "rs0",
#     members: [
#       { _id: 0, host: "localhost:27017" },
#       { _id: 1, host: "localhost:27018" },
#       { _id: 2, host: "localhost:27019" }
#     ]
#   })
#
# Verify election is complete (PRIMARY must appear):
#   rs.status()

# ── Step 4 (optional): Automated startup wrapper ──────────
# If you want all three mongod processes in one terminal
# (foreground, Ctrl-C to stop all):

if [[ "$1" == "--start-all" ]]; then
    echo "Starting all three mongod instances..."

    mongod --replSet rs0 --port 27017 --dbpath ./data/rs1 \
           --bind_ip localhost --logpath ./data/rs1.log --fork
    mongod --replSet rs0 --port 27018 --dbpath ./data/rs2 \
           --bind_ip localhost --logpath ./data/rs2.log --fork
    mongod --replSet rs0 --port 27019 --dbpath ./data/rs3 \
           --bind_ip localhost --logpath ./data/rs3.log --fork

    echo "Waiting 3 s for processes to start..."
    sleep 3

    echo "Initiating replica set rs0..."
    mongosh --port 27017 --eval '
        rs.initiate({
            _id: "rs0",
            members: [
                { _id: 0, host: "localhost:27017" },
                { _id: 1, host: "localhost:27018" },
                { _id: 2, host: "localhost:27019" }
            ]
        });
    '

    echo "Waiting 5 s for election..."
    sleep 5

    mongosh --port 27017 --eval 'rs.status()' | grep -E "name|stateStr"

    echo ""
    echo "Replica set rs0 is up. Connect with:"
    echo "  mongosh 'mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0'"
fi
