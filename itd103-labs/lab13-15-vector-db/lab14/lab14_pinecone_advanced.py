# =============================================================
# Lab 14 – Exercise 4: Pinecone Advanced — Filtered & Hybrid Search
# Run AFTER lab14_pinecone_setup.py
# Run: python lab14_pinecone_advanced.py
# =============================================================

from pinecone import Pinecone
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# ── Init ───────────────────────────────────────────────────
pc    = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index("itd103-articles")
model = SentenceTransformer('all-MiniLM-L6-v2')
df    = pd.read_csv('../../datasets/articles.csv')

# ─────────────────────────────────────────────────────────
# 1. Filtered Search
# ─────────────────────────────────────────────────────────
def filtered_search(query, category_filter=None, min_score=0.0, top_k=5):
    query_emb = model.encode(query).tolist()
    filter_q  = {"category": {"$eq": category_filter}} if category_filter else None

    results = index.query(
        vector=query_emb, top_k=top_k,
        filter=filter_q, include_metadata=True
    )
    return [m for m in results['matches'] if m['score'] >= min_score]

print("=== Filtered Search ===")

print("\n1. 'performance' in Database category:")
for m in filtered_search("performance optimization", category_filter="Database"):
    print(f"  {m['metadata']['title']} (Score: {m['score']:.3f})")

print("\n2. 'health' in Health category (min score 0.5):")
for m in filtered_search("health and wellness", category_filter="Health", min_score=0.5):
    print(f"  {m['metadata']['title']} (Score: {m['score']:.3f})")

# ─────────────────────────────────────────────────────────
# 2. Hybrid Search (Vector + Keyword)
# ─────────────────────────────────────────────────────────
def hybrid_search(query, alpha=0.7, top_k=5):
    """alpha = weight for vector score; (1-alpha) = keyword weight"""
    query_emb     = model.encode(query).tolist()
    vector_results = index.query(
        vector=query_emb, top_k=10, include_metadata=True
    )

    query_words = set(query.lower().split())
    scores      = {}

    for match in vector_results['matches']:
        doc_id   = match['id']
        content  = match['metadata']['content'].lower()
        title    = match['metadata']['title'].lower()

        kw_score = (
            len(query_words & set(content.split())) / len(query_words) * 0.7 +
            len(query_words & set(title.split()))   / len(query_words) * 0.3
        )

        scores[doc_id] = {
            'metadata'      : match['metadata'],
            'vector_score'  : match['score'],
            'keyword_score' : kw_score,
            'combined_score': alpha * match['score'] + (1 - alpha) * kw_score
        }

    return sorted(scores.items(), key=lambda x: x[1]['combined_score'], reverse=True)[:top_k]

print("\n=== Hybrid Search ===")
query   = "database SQL performance optimization"
results = hybrid_search(query, alpha=0.6)

print(f"Query: {query}")
print("-" * 60)
for doc_id, data in results:
    print(f"ID: {doc_id} | {data['metadata']['title']}")
    print(f"  Vector={data['vector_score']:.3f}  "
          f"Keyword={data['keyword_score']:.3f}  "
          f"Combined={data['combined_score']:.3f}")

# ─────────────────────────────────────────────────────────
# 3. Update & Delete
# ─────────────────────────────────────────────────────────
print("\n=== Update & Delete Operations ===")

TEST_ID = "test_001"

# Insert test vector
index.upsert(vectors=[(
    TEST_ID,
    model.encode("This is a test document about vector databases.").tolist(),
    {'title': 'Test Doc', 'category': 'Test', 'content': 'test content'}
)])
print(f"Inserted: {TEST_ID}")

# Update
index.upsert(vectors=[(
    TEST_ID,
    model.encode("Updated content about semantic search and AI.").tolist(),
    {'title': 'Updated Test Doc', 'category': 'Updated', 'content': 'updated content'}
)])
print(f"Updated : {TEST_ID}")

# Delete
index.delete(ids=[TEST_ID])
print(f"Deleted : {TEST_ID}")

# ─────────────────────────────────────────────────────────
# 4. Namespace Management
# ─────────────────────────────────────────────────────────
print("\n=== Namespace Management ===")

namespaces = df['category'].str.lower().unique()
for ns in namespaces:
    ns_df    = df[df['category'].str.lower() == ns]
    vectors  = [
        (str(row['id']),
         model.encode(row['content']).tolist(),
         {'title': row['title'], 'category': row['category'], 'content': row['content'][:500]})
        for _, row in ns_df.iterrows()
    ]
    if vectors:
        index.upsert(vectors=vectors, namespace=ns)
        print(f"  Uploaded {len(vectors)} vectors to namespace '{ns}'")

print("\nQuerying 'database' namespace:")
results = index.query(
    vector    = model.encode("query optimization").tolist(),
    top_k     = 3,
    namespace = "database",
    include_metadata = True
)
for match in results['matches']:
    print(f"  {match['metadata']['title']} (Score: {match['score']:.3f})")
