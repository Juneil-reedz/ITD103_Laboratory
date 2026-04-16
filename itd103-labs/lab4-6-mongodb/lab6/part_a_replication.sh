#!/usr/bin/env bash
# =============================================================
# Lab 6 – Part A: Replica Set Setup
# Run each block in a SEPARATE terminal window
# =============================================================

# Create data directories first (run once)
mkdir -p ./data/rs1 ./data/rs2 ./data/rs3

# -------------------------------------------------------------
# Terminal 1 — Primary (port 27017)
# -------------------------------------------------------------
mongod --port 27017 --dbpath ./data/rs1 --replSet rs0 --bind_ip localhost

# -------------------------------------------------------------
# Terminal 2 — Secondary (port 27018)
# -------------------------------------------------------------
mongod --port 27018 --dbpath ./data/rs2 --replSet rs0 --bind_ip localhost

# -------------------------------------------------------------
# Terminal 3 — Arbiter (port 27019)
# An arbiter participates in elections but holds no data
# -------------------------------------------------------------
mongod --port 27019 --dbpath ./data/rs3 --replSet rs0 --bind_ip localhost
