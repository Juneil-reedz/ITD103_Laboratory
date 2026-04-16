# Lab 9: Real-World Graph Application

## Objectives
- Build an e-commerce recommendation system
- Implement fraud detection patterns
- Combine graph traversal with business logic

## Files
| File | Description |
|------|-------------|
| `part_a_product_graph.cql` | Create products, customers, purchases, views, bought-with edges |
| `exercise1_collaborative_filtering.cql` | "Also bought", similar customers, popularity-weighted recs |
| `exercise2_content_based_filtering.cql` | Category similarity, viewed-not-bought, cross-sell |
| `exercise3_fraud_detection.cql` | Shared identifiers, velocity fraud, ring detection |

## Run Order
```bash
cypher-shell -u neo4j -p password -f part_a_product_graph.cql
cypher-shell -u neo4j -p password -f exercise1_collaborative_filtering.cql
cypher-shell -u neo4j -p password -f exercise2_content_based_filtering.cql
cypher-shell -u neo4j -p password -f exercise3_fraud_detection.cql
```

## Graph Model
```
(Customer)-[:PURCHASED {date, quantity}]->(Product)
(Customer)-[:VIEWED    {timestamp}]     ->(Product)
(Product) -[:BOUGHT_WITH {frequency}]  ->(Product)
(Customer)-[:SHARES_IP | SHARES_PHONE | SHARES_ADDRESS]->(Customer)
```

## Recommendation Strategies
| Strategy | Approach |
|----------|----------|
| Collaborative Filtering | Find customers with shared purchases; recommend what they bought |
| Content-Based | Recommend products in the same category or similar price range |
| Cross-Sell | Use `BOUGHT_WITH` edges to surface bundle recommendations |
| Re-engagement | Identify viewed-but-not-purchased products for follow-up |

## Fraud Signals Detected
| Pattern | Detection Method |
|---------|-----------------|
| Identity ring | 2+ shared attributes (IP, phone, address) |
| Velocity fraud | 3+ purchases in rapid succession |
| Synthetic identity | Account created within 3 days of a connected account |

## Deliverables
- [ ] Complete recommendation system implementation
- [ ] Fraud detection query results
- [ ] Performance analysis report
