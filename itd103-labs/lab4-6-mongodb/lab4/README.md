# Lab 4: Advanced MQL Queries

## Objectives
- Master complex query operators
- Implement text search
- Work with geospatial queries

## Files
| File | Description |
|------|-------------|
| `part_a_import.sh` | Import `restaurants.json` into MongoDB |
| `exercise1_array_operators.js` | `$all`, `$size`, `$elemMatch`, `$addToSet`, `$push`, `$pull` |
| `exercise2_text_search.js` | Text index creation, `$text` search, regex queries |
| `exercise3_geospatial.js` | `2dsphere` index, `$near`, `$geoWithin`, `$box`, `$center` |

## Quick Start

```bash
# From itd103-labs/ root:
bash lab4-6-mongodb/lab4/part_a_import.sh

# Then in mongosh:
mongosh --file lab4-6-mongodb/lab4/exercise1_array_operators.js
mongosh --file lab4-6-mongodb/lab4/exercise2_text_search.js
mongosh --file lab4-6-mongodb/lab4/exercise3_geospatial.js
```

## Key Operators Reference
| Operator | Use Case |
|----------|----------|
| `$all` | Array contains ALL specified values |
| `$size` | Array has exact number of elements |
| `$elemMatch` | Array element matches multiple conditions |
| `$addToSet` | Add to array only if not already present |
| `$text` | Full-text search on text-indexed fields |
| `$near` | Find documents by proximity (sorted by distance) |
| `$geoWithin` | Find documents within a shape |

## Deliverables
- [ ] Complete query solutions
- [ ] Search implementation results
- [ ] Geospatial query results
