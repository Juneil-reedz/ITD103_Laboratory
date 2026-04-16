# =============================================================
# Lab 13 – Exercise 1: Sentence Transformers Embeddings
# Run: python lab13_sentence_transformers.py
# =============================================================

from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────
DATASET_PATH   = '../../datasets/articles.csv'
EMBEDDING_PATH = '../../datasets/article_embeddings.npy'

# ── Load dataset ───────────────────────────────────────────
df = pd.read_csv(DATASET_PATH)
print(f"Loaded {len(df)} articles")
print(df[['id', 'title', 'category']].to_string(index=False))

# ── Initialize model ───────────────────────────────────────
print("\nLoading SentenceTransformer model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')   # Lightweight, 384-dim

# ── Generate embeddings ────────────────────────────────────
print("\nGenerating embeddings...")
sentences  = df['content'].tolist()
embeddings = model.encode(sentences, show_progress_bar=True)

# Save for use in later exercises
os.makedirs(os.path.dirname(EMBEDDING_PATH), exist_ok=True)
np.save(EMBEDDING_PATH, embeddings)
print(f"\nEmbeddings shape: {embeddings.shape}")
print(f"Saved to: {EMBEDDING_PATH}")

# ── Similarity search ──────────────────────────────────────
def semantic_search(query, top_k=3):
    query_embedding = model.encode(query)
    cosine_scores   = util.cos_sim(query_embedding, embeddings)[0]
    top_indices     = np.argsort(-cosine_scores.numpy())[:top_k]

    print(f"\nQuery: '{query}'")
    print("-" * 55)
    for rank, idx in enumerate(top_indices, 1):
        print(f"Rank {rank} | Score: {cosine_scores[idx]:.4f}")
        print(f"  Title   : {df.iloc[idx]['title']}")
        print(f"  Category: {df.iloc[idx]['category']}")
        print()

# ── Test queries ───────────────────────────────────────────
queries = [
    "How to improve database performance?",
    "What are the benefits of healthy food?",
    "Latest trends in artificial intelligence",
    "Environmental and climate issues"
]

print("\n=== Semantic Search Results ===")
for q in queries:
    semantic_search(q)

# ── Pairwise similarity matrix ─────────────────────────────
print("=== Pairwise Similarity (excerpt) ===")
sim_matrix = util.cos_sim(embeddings, embeddings).numpy()

print("\nMost similar article pairs:")
pairs = []
for i in range(len(df)):
    for j in range(i + 1, len(df)):
        pairs.append((sim_matrix[i][j], df.iloc[i]['title'], df.iloc[j]['title']))

pairs.sort(reverse=True)
for score, t1, t2 in pairs[:5]:
    print(f"  {score:.4f} | {t1}  ↔  {t2}")
