# =============================================================
# Lab 14 – Exercise 3: Pinecone Setup & Basic Operations
# Requires: PINECONE_API_KEY environment variable
# Run: python lab14_pinecone_setup.py
# =============================================================

from pinecone import Pinecone, ServerlessSpec
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

# ── Init ───────────────────────────────────────────────────
api_key = os.getenv('PINECONE_API_KEY')
if not api_key:
    raise EnvironmentError(
        "PINECONE_API_KEY not set.\n"
        "Set it with: set PINECONE_API_KEY=your-key-here  (Windows)"
    )

pc         = Pinecone(api_key=api_key)
model      = SentenceTransformer('all-MiniLM-L6-v2')
INDEX_NAME = "itd103-articles"
DIMENSION  = 384

# ── Create index ───────────────────────────────────────────
existing = [i.name for i in pc.list_indexes()]
print(f"Existing indexes: {existing}")

if INDEX_NAME not in existing:
    pc.create_index(
        name      = INDEX_NAME,
        dimension = DIMENSION,
        metric    = "cosine",
        spec      = ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Created index: {INDEX_NAME}")
else:
    print(f"Index '{INDEX_NAME}' already exists")

index = pc.Index(INDEX_NAME)
print(f"Index stats: {index.describe_index_stats()}")

# ── Load & upload vectors ──────────────────────────────────
df = pd.read_csv('../../datasets/articles.csv')
print(f"\nUploading {len(df)} vectors...")

vectors = []
for _, row in tqdm(df.iterrows(), total=len(df)):
    embedding = model.encode(row['content']).tolist()
    metadata  = {
        'title'   : row['title'],
        'category': row['category'],
        'content' : row['content'][:500]
    }
    vectors.append((str(row['id']), embedding, metadata))

# Upload in batches of 100
batch_size = 100
for i in range(0, len(vectors), batch_size):
    index.upsert(vectors=vectors[i:i + batch_size])

print(f"Upload complete.")
print(f"Final stats: {index.describe_index_stats()}")

# ── Query function ─────────────────────────────────────────
def query_pinecone(query, top_k=3, category=None):
    query_emb = model.encode(query).tolist()
    filter_q  = {"category": {"$eq": category}} if category else None

    results = index.query(
        vector           = query_emb,
        top_k            = top_k,
        filter           = filter_q,
        include_metadata = True,
        include_values   = False
    )
    return results

# ── Test queries ───────────────────────────────────────────
queries = [
    "How to optimize database queries?",
    "What are healthy lifestyle choices?",
    "Latest advancements in artificial intelligence"
]

print("\n=== Pinecone Search Results ===")
for q in queries:
    print(f"\nQuery: {q}")
    print("-" * 55)
    results = query_pinecone(q)
    for match in results['matches']:
        print(f"  Score   : {match['score']:.4f}")
        print(f"  Title   : {match['metadata']['title']}")
        print(f"  Category: {match['metadata']['category']}")
        print()
