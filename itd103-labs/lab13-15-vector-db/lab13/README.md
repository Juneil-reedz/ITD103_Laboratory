# Lab 13 – Introduction to Vector Embeddings

## Overview
Learn to generate, store, compare, and visualize vector embeddings using
SentenceTransformers and the OpenAI Embeddings API.

## Exercises

| Exercise | File | Description |
|----------|------|-------------|
| 1 | `lab13_sentence_transformers.py` | Local embeddings with SentenceTransformers |
| 2 | `lab13_openai_embeddings.py` | Cloud embeddings with OpenAI ada-002 |
| 3 | `lab13_visualization.py` | PCA + t-SNE + Silhouette score |

## Setup

```bash
pip install sentence-transformers openai pandas numpy matplotlib scikit-learn
```

Set your OpenAI key (Exercise 2 only):
```bash
# Windows
set OPENAI_API_KEY=sk-...

# macOS/Linux
export OPENAI_API_KEY=sk-...
```

## Run Order

```bash
python lab13_sentence_transformers.py   # generates article_embeddings.npy
python lab13_openai_embeddings.py       # generates openai_embeddings.npy
python lab13_visualization.py          # generates embedding_visualization.png
```

## Working Queries

### Exercise 1 — SentenceTransformer Semantic Search

```python
from sentence_transformers import SentenceTransformer
import numpy as np, pandas as pd, faiss

model = SentenceTransformer('all-MiniLM-L6-v2')
df    = pd.read_csv('../../datasets/articles.csv')
embs  = model.encode(df['content'].tolist()).astype('float32')

idx = faiss.IndexFlatL2(embs.shape[1])
idx.add(embs)

query = "How to speed up database queries?"
q_emb = model.encode([query]).astype('float32')
dists, ids = idx.search(q_emb, 3)
for i, pos in enumerate(ids[0]):
    print(df.iloc[pos]['title'], round(1/(1+dists[0][i]), 4))
```

Expected output:
```
Query: How to speed up database queries?
  1. Database Indexing Strategies       sim=0.6321
  2. SQL Query Optimization Techniques  sim=0.5894
  3. NoSQL vs SQL Performance           sim=0.4217
```

### Exercise 2 — Cosine Similarity Comparison

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
a = model.encode("The quick brown fox")
b = model.encode("A fast auburn fox")
c = model.encode("Database indexing improves query speed")

def cos_sim(x, y):
    return float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y)))

print(cos_sim(a, b))  # ~0.85 (similar meaning)
print(cos_sim(a, c))  # ~0.10 (unrelated)
```

### Exercise 3 — Visualization Output

Running `lab13_visualization.py` produces:

- **PCA explained variance** — typically 15-25 % for all-MiniLM-L6-v2 on 10 articles
- **Silhouette Score** — measures cluster separation by category
  - > 0.50 → Reasonable clustering structure
  - > 0.70 → Strong clustering structure
- **Plot saved** → `datasets/embedding_visualization.png`

Interpretation table:

| Score range | Interpretation |
|-------------|---------------|
| > 0.70 | Strong clustering |
| 0.50–0.70 | Reasonable clustering |
| 0.25–0.50 | Weak clustering |
| < 0.25 | No substantial clustering |

## Output Files

| File | Description |
|------|-------------|
| `datasets/article_embeddings.npy` | 384-dim SentenceTransformer embeddings |
| `datasets/openai_embeddings.npy` | 1536-dim OpenAI ada-002 embeddings |
| `datasets/embedding_visualization.png` | PCA + t-SNE scatter plots |
