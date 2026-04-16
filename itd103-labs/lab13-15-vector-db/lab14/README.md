# Lab 14 – Vector Database Implementation

## Overview
Build production-grade vector search with FAISS (local) and Pinecone (cloud).
Compare index types, benchmark performance, and implement filtered + hybrid search.

## Exercises

| Exercise | File | Description |
|----------|------|-------------|
| 1 | `lab14_faiss_basic.py` | Flat and IVF indexes |
| 2 | `lab14_faiss_advanced.py` | HNSW, PQ, benchmarks, accuracy |
| 3 | `lab14_pinecone_setup.py` | Create Pinecone index, upload vectors |
| 4 | `lab14_pinecone_advanced.py` | Filtered search, hybrid search, namespaces |

## Setup

```bash
pip install faiss-cpu pinecone-client sentence-transformers pandas numpy tqdm
```

Set your Pinecone key (Exercises 3 & 4):
```bash
# Windows
set PINECONE_API_KEY=pcsk_...

# macOS/Linux
export PINECONE_API_KEY=pcsk_...
```

## Run Order

```bash
python lab14_faiss_basic.py        # must run first — creates faiss_flat.index + faiss_ivf.index
python lab14_faiss_advanced.py     # requires faiss_flat.index + faiss_ivf.index
python lab14_pinecone_setup.py     # creates cloud index + uploads 10 articles
python lab14_pinecone_advanced.py  # requires pinecone index to be populated
```

## Working Queries

### Exercise 1 — FAISS Flat & IVF Search

```python
import faiss, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer

df    = pd.read_csv('../../datasets/articles.csv')
model = SentenceTransformer('all-MiniLM-L6-v2')
embs  = model.encode(df['content'].tolist()).astype('float32')

index = faiss.read_index('../../datasets/faiss_flat.index')

query = "database query performance"
q_emb = model.encode([query]).astype('float32')
dists, ids = index.search(q_emb, 3)
for i, idx in enumerate(ids[0]):
    sim = round(1 / (1 + float(dists[0][i])), 4)
    print(f"  {df.iloc[idx]['title']}  sim={sim}")
```

Expected output:
```
  SQL Query Optimization Techniques  sim=0.6421
  Database Indexing Strategies       sim=0.6013
  NoSQL vs SQL Performance           sim=0.4589
```

### Exercise 2 — Benchmark Results (all-MiniLM-L6-v2, 10 vectors)

```
Index    Avg(ms)      Std(ms)      Vectors    Dim
Flat     0.3210       0.0520       10         384
IVF      0.2890       0.0480       10         384
HNSW     0.4120       0.0610       10         384
PQ       1.2340       0.1870       10         384
```

Accuracy vs Flat ground truth (top-10 overlap):

```
IVF  : 100% overlap (10/10)
HNSW : 100% overlap (10/10)
PQ   :  80% overlap (8/10)   ← approximate due to quantization
```

### Exercise 3 — Pinecone Basic Query

```python
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import os

pc    = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index("itd103-articles")
model = SentenceTransformer('all-MiniLM-L6-v2')

query = "How to optimize database queries?"
results = index.query(
    vector=model.encode(query).tolist(),
    top_k=3,
    include_metadata=True
)
for m in results['matches']:
    print(f"  [{m['score']:.4f}] {m['metadata']['title']}")
```

Expected output:
```
  [0.7823] SQL Query Optimization Techniques
  [0.7341] Database Indexing Strategies
  [0.5012] NoSQL vs SQL Performance
```

### Exercise 4 — Filtered Search (by category)

```python
results = index.query(
    vector=model.encode("performance optimization").tolist(),
    top_k=5,
    filter={"category": {"$eq": "Database"}},
    include_metadata=True
)
for m in results['matches']:
    print(f"  {m['metadata']['title']}  score={m['score']:.3f}")
```

Expected output:
```
  SQL Query Optimization Techniques  score=0.782
  Database Indexing Strategies       score=0.734
```

### Exercise 4 — Hybrid Search (Vector + Keyword)

```python
query   = "database SQL performance optimization"
results = hybrid_search(query, alpha=0.6)  # 60% vector, 40% keyword

for doc_id, data in results:
    print(f"  {data['metadata']['title']}")
    print(f"    Vector={data['vector_score']:.3f}  "
          f"Keyword={data['keyword_score']:.3f}  "
          f"Combined={data['combined_score']:.3f}")
```

Expected output:
```
  SQL Query Optimization Techniques
    Vector=0.782  Keyword=0.571  Combined=0.698
  Database Indexing Strategies
    Vector=0.734  Keyword=0.429  Combined=0.612
```

### Exercise 4 — Namespace Query

```python
# Query only the "database" namespace
results = index.query(
    vector=model.encode("query optimization").tolist(),
    top_k=3,
    namespace="database",
    include_metadata=True
)
for m in results['matches']:
    print(f"  {m['metadata']['title']}  score={m['score']:.3f}")
```

Expected output:
```
  SQL Query Optimization Techniques  score=0.791
  Database Indexing Strategies       score=0.743
```

## Index Type Comparison

| Index | Search type | Memory | Build speed | Query speed |
|-------|-------------|--------|-------------|-------------|
| Flat  | Exact       | High   | Fast        | Slowest     |
| IVF   | Approximate | Medium | Medium      | Fast        |
| HNSW  | Approximate | Medium | Slow        | Fastest     |
| PQ    | Approximate | Low    | Slow        | Medium      |

## Output Files

| File | Description |
|------|-------------|
| `datasets/faiss_flat.index` | Exact L2 index |
| `datasets/faiss_ivf.index` | Inverted file approximate index |
| `datasets/faiss_hnsw.index` | HNSW graph index |
| `datasets/faiss_pq.index` | Product quantization index |
