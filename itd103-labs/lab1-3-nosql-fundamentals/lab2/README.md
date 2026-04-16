# Lab 2: Document Database Design

## Objectives
- Design document schemas
- Implement relationships in MongoDB
- Practice CRUD operations

## Files
| File | Description |
|------|-------------|
| `part_b_implementation.js` | Full schema implementation and queries (run in mongosh) |

## Schema Design Decisions

### E-Commerce Product Catalog
- **Variants** → **Embedded** (always fetched with product, small bounded array)
- **Reviews** → **Embedded** (usually read alongside the product, bounded in size)
- **Orders → Products** → **Referenced** by `product_id` (products change independently)

### Blog System
- **Author** → **Embedded snapshot** (captures name/email at time of post)
- **Comments** → **Embedded array** with nested `replies` array
- **Tags** → **Embedded string array** (simple values, queried with multikey index)

## Quick Start
```bash
mongosh --file part_b_implementation.js
```
Or manually paste sections into mongosh.

## Deliverables
- [ ] Schema design diagrams
- [ ] Complete MongoDB implementation code
- [ ] Query execution results
