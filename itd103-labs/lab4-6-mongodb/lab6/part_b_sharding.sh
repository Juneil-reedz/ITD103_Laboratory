#!/usr/bin/env bash
# =============================================================
# Lab 6 – Part B: Sharding Setup
# Run each block in a SEPARATE terminal window
# =============================================================

# Create data directories (run once)
mkdir -p ./data/shard1 ./data/shard2 ./data/config

# -------------------------------------------------------------
# Terminal 1 — Shard 1 (port 27020)
# -------------------------------------------------------------
mongod --port 27020 --dbpath ./data/shard1 --shardsvr --bind_ip localhost

# -------------------------------------------------------------
# Terminal 2 — Shard 2 (port 27021)
# -------------------------------------------------------------
mongod --port 27021 --dbpath ./data/shard2 --shardsvr --bind_ip localhost

# -------------------------------------------------------------
# Terminal 3 — Config Server (port 27022)
# Stores shard metadata and routing info
# -------------------------------------------------------------
mongod --port 27022 --dbpath ./data/config --configsvr --replSet configRS --bind_ip localhost

# Initialize config server replica set (run in mongosh --port 27022)
# rs.initiate({ _id: "configRS", configsvr: true, members: [{ _id: 0, host: "localhost:27022" }] })

# -------------------------------------------------------------
# Terminal 4 — Mongos Router (port 27023)
# Routes client queries to the correct shards
# -------------------------------------------------------------
mongos --port 27023 --configdb configRS/localhost:27022 --bind_ip localhost
