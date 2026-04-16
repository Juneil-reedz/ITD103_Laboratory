# Lab 1: Understanding CAP Theorem

## Objectives
- Understand CAP Theorem trade-offs
- Compare different NoSQL databases
- Install and configure MongoDB

## Files
| File | Description |
|------|-------------|
| `part_a_cap_analysis.md` | CAP Theorem scenario analysis and database selection |
| `part_b_mongodb_operations.js` | MongoDB basic CRUD operations (run in mongosh) |

## Quick Start

### Start MongoDB
```bash
mongod --dbpath ./data --port 27017
```

### Connect with shell
```bash
mongosh
```

### Run Part B
Copy and paste commands from `part_b_mongodb_operations.js` into mongosh, or load the file:
```bash
mongosh --file part_b_mongodb_operations.js
```

## Deliverables
- [ ] CAP Theorem analysis report (PDF from `part_a_cap_analysis.md`)
- [ ] MongoDB connection screenshot
- [ ] Query results from basic operations
