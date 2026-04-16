# =============================================================
# Lab 14 – Exercise 1: Basic FAISS Index
# Run AFTER lab13_sentence_transformers.py
# Run: python lab14_faiss_basic.py
# =============================================================

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# ── Load data ──────────────────────────────────────────────
df    = pd.read_csv('../../datasets/articles.csv')
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Generating embeddings...")
embeddings = model.encode(df['content'].tolist()).astype('float32')
print(f"Embeddings shape: {embeddings.shape}")

dimension = embeddings.shape[1]

# ── Index 1: Flat (exact search) ───────────────────────────
index_flat = faiss.IndexFlatL2(dimension)
index_flat.add(embeddings)
print(f"\nFlat index  : {index_flat.ntotal} vectors")

# ── Index 2: IVF (approximate, faster at scale) ────────────
nlist     = 5   # small dataset — keep nlist small
quantizer = faiss.IndexFlatL2(dimension)
index_ivf = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)
index_ivf.train(embeddings)
index_ivf.add(embeddings)
index_ivf.nprobe = 3
print(f"IVF index   : {index_ivf.ntotal} vectors")

# ── Save indexes ───────────────────────────────────────────
faiss.write_index(index_flat, "../../datasets/faiss_flat.index")
faiss.write_index(index_ivf,  "../../datasets/faiss_ivf.index")
print("Indexes saved to datasets/")

# ── Search function ────────────────────────────────────────
def search_faiss(query, index, k=3):
    query_emb = model.encode([query]).astype('float32')
    distances, indices = index.search(query_emb, k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            results.append({
                'rank'      : i + 1,
                'title'     : df.iloc[idx]['title'],
                'category'  : df.iloc[idx]['category'],
                'distance'  : float(distances[0][i]),
                'similarity': round(1 / (1 + float(distances[0][i])), 4)
            })
    return results

# ── Test queries ───────────────────────────────────────────
queries = [
    "How to make databases faster?",
    "What are healthy food options?",
    "Latest technology trends",
    "Environmental issues and solutions"
]

print("\n=== FAISS Search Results ===")
for query in queries:
    print(f"\nQuery: {query}")
    print("-" * 55)

    flat_results = search_faiss(query, index_flat)
    print("Flat Index:")
    for r in flat_results:
        print(f"  {r['rank']}. {r['title']} [{r['category']}]  sim={r['similarity']}")

    ivf_results = search_faiss(query, index_ivf)
    print("IVF Index:")
    for r in ivf_results:
        print(f"  {r['rank']}. {r['title']} [{r['category']}]  sim={r['similarity']}")
