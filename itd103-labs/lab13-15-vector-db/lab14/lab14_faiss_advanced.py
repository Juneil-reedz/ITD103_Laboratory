# =============================================================
# Lab 14 – Exercise 2: Advanced FAISS — Index Types & Benchmarks
# Run AFTER lab14_faiss_basic.py
# Run: python lab14_faiss_advanced.py
# =============================================================

import faiss
import numpy as np
import pandas as pd
import time
from sentence_transformers import SentenceTransformer

# ── Load data ──────────────────────────────────────────────
df         = pd.read_csv('../../datasets/articles.csv')
model      = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['content'].tolist()).astype('float32')
dimension  = embeddings.shape[1]

# ── Build indexes ──────────────────────────────────────────

# 1. HNSW (Hierarchical Navigable Small World)
print("Building HNSW index...")
index_hnsw = faiss.IndexHNSWFlat(dimension, 32)
index_hnsw.hnsw.efConstruction = 40
index_hnsw.hnsw.efSearch        = 16
index_hnsw.add(embeddings)
faiss.write_index(index_hnsw, "../../datasets/faiss_hnsw.index")

# 2. Product Quantization (memory-efficient)
print("Building PQ index...")
nlist = 5
m     = 8   # must divide dimension (384 / 8 = 48 ✓)
quantizer = faiss.IndexFlatL2(dimension)
index_pq  = faiss.IndexIVFPQ(quantizer, dimension, nlist, m, 8)
index_pq.train(embeddings)
index_pq.add(embeddings)
faiss.write_index(index_pq, "../../datasets/faiss_pq.index")

# ── Load all indexes ───────────────────────────────────────
indexes = {
    'Flat': faiss.read_index("../../datasets/faiss_flat.index"),
    'IVF' : faiss.read_index("../../datasets/faiss_ivf.index"),
    'HNSW': faiss.read_index("../../datasets/faiss_hnsw.index"),
    'PQ'  : faiss.read_index("../../datasets/faiss_pq.index"),
}

# ── Benchmark ──────────────────────────────────────────────
def benchmark(query, index, name, reps=200):
    query_emb = model.encode([query]).astype('float32')

    # Warm-up
    for _ in range(10):
        index.search(query_emb, 3)

    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        index.search(query_emb, 3)
        times.append((time.perf_counter() - t0) * 1000)

    return {
        'index'      : name,
        'avg_ms'     : round(np.mean(times), 4),
        'std_ms'     : round(np.std(times), 4),
        'vectors'    : getattr(index, 'ntotal', 'N/A'),
        'dimension'  : dimension,
    }

query   = "database performance optimization"
results = [benchmark(query, idx, name) for name, idx in indexes.items()]

print("\n=== Benchmark Results ===")
header = f"{'Index':<8} {'Avg(ms)':<12} {'Std(ms)':<12} {'Vectors':<10} {'Dim':<6}"
print(header)
print("-" * len(header))
for r in results:
    print(f"{r['index']:<8} {r['avg_ms']:<12} {r['std_ms']:<12} {r['vectors']:<10} {r['dimension']:<6}")

# ── Accuracy vs ground truth ───────────────────────────────
print("\n=== Accuracy vs Flat (ground truth) ===")
query_emb = model.encode([query]).astype('float32')
_, gt     = indexes['Flat'].search(query_emb, 10)
gt_set    = set(gt[0])

for name, index in indexes.items():
    if name == 'Flat':
        continue
    _, res   = index.search(query_emb, 10)
    overlap  = len(set(res[0]) & gt_set)
    accuracy = overlap / len(gt_set)
    print(f"  {name:<6}: {accuracy:.0%} overlap with ground truth ({overlap}/10)")
