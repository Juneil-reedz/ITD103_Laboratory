# =============================================================
# Lab 13 – Exercise 2: OpenAI Embeddings
# Requires: OPENAI_API_KEY environment variable
# Run: python lab13_openai_embeddings.py
# =============================================================

import openai
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

# ── API key ────────────────────────────────────────────────
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise EnvironmentError(
        "OPENAI_API_KEY not set.\n"
        "Set it with: set OPENAI_API_KEY=your-key-here  (Windows)\n"
        "             export OPENAI_API_KEY=your-key-here (Linux/Mac)"
    )

# ── Helper ─────────────────────────────────────────────────
def get_openai_embedding(text, model="text-embedding-ada-002"):
    """Generate a single embedding via OpenAI API"""
    text = text.replace("\n", " ")
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']

# ── Load dataset ───────────────────────────────────────────
df = pd.read_csv('../../datasets/articles.csv')
print(f"Loaded {len(df)} articles")

# ── Generate embeddings ────────────────────────────────────
print("\nGenerating OpenAI embeddings (text-embedding-ada-002)...")
embeddings = []
for _, row in df.iterrows():
    embedding = get_openai_embedding(row['content'])
    embeddings.append(embedding)
    print(f"  ✓ {row['title'][:50]}")

embeddings = np.array(embeddings)
np.save('../../datasets/openai_embeddings.npy', embeddings)
print(f"\nEmbeddings shape: {embeddings.shape}")   # (10, 1536)

# ── Similarity search ──────────────────────────────────────
def openai_search(query, top_k=3):
    print(f"\nQuery: '{query}'")
    print("-" * 55)

    query_embedding   = get_openai_embedding(query)
    similarities      = cosine_similarity([query_embedding], embeddings)[0]
    df['similarity']  = similarities

    results = df.nlargest(top_k, 'similarity')[['title', 'category', 'similarity']]
    for _, row in results.iterrows():
        print(f"  Score: {row['similarity']:.4f} | {row['title']} [{row['category']}]")

queries = [
    "database optimization techniques",
    "healthy nutrition and lifestyle",
    "machine learning applications"
]

print("\n=== OpenAI Embedding Search Results ===")
for q in queries:
    openai_search(q)
