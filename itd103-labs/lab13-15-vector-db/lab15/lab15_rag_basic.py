# =============================================================
# Lab 15 – Exercise 1: Basic RAG (Retrieval-Augmented Generation)
# Requires: OPENAI_API_KEY environment variable
# Run: python lab15_rag_basic.py
# =============================================================

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import os

# ── OpenAI client (v1.x) ──────────────────────────────────
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# ── Load data & build FAISS index ─────────────────────────
df    = pd.read_csv('../../datasets/articles.csv')
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Encoding articles...")
embeddings = model.encode(df['content'].tolist()).astype('float32')

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
print(f"Index built: {index.ntotal} vectors")

# ─────────────────────────────────────────────────────────
# 1. Retrieval component
# ─────────────────────────────────────────────────────────
def retrieve(query, top_k=3):
    """Return top-k relevant article chunks for a query."""
    query_emb = model.encode([query]).astype('float32')
    distances, indices = index.search(query_emb, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            results.append({
                'title'   : df.iloc[idx]['title'],
                'category': df.iloc[idx]['category'],
                'content' : df.iloc[idx]['content'],
                'distance': float(distances[0][i]),
                'score'   : round(1 / (1 + float(distances[0][i])), 4),
            })
    return results

# ─────────────────────────────────────────────────────────
# 2. Generation component
# ─────────────────────────────────────────────────────────
def generate_answer(query, context_docs):
    """Generate an answer using retrieved context."""
    context = "\n\n".join(
        f"[{d['title']}]\n{d['content']}" for d in context_docs
    )

    system_msg = (
        "You are a helpful assistant. Answer the user's question using ONLY "
        "the provided context. If the context does not contain enough "
        "information, say so clearly."
    )
    user_msg = f"Context:\n{context}\n\nQuestion: {query}"

    response = client.chat.completions.create(
        model    = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ],
        max_tokens  = 300,
        temperature = 0.3,
    )
    return response.choices[0].message.content

# ─────────────────────────────────────────────────────────
# 3. Full RAG pipeline
# ─────────────────────────────────────────────────────────
def rag_query(query, top_k=3, verbose=True):
    """Retrieve → Augment → Generate."""
    docs   = retrieve(query, top_k)
    answer = generate_answer(query, docs)

    if verbose:
        print(f"\nQuestion: {query}")
        print("-" * 60)
        print("Retrieved context:")
        for d in docs:
            print(f"  [{d['score']:.3f}] {d['title']} ({d['category']})")
        print(f"\nAnswer:\n{answer}")
        print("=" * 60)

    return {"query": query, "context": docs, "answer": answer}

# ─────────────────────────────────────────────────────────
# 4. Test queries
# ─────────────────────────────────────────────────────────
test_queries = [
    "How can I improve database query performance?",
    "What are the benefits of regular exercise?",
    "What are the latest developments in artificial intelligence?",
]

print("\n=== Basic RAG Demo ===")
results = [rag_query(q) for q in test_queries]

# ─────────────────────────────────────────────────────────
# 5. Retrieval quality check
# ─────────────────────────────────────────────────────────
print("\n=== Retrieval Quality ===")
for res in results:
    categories = [d['category'] for d in res['context']]
    print(f"Q: {res['query'][:50]}...")
    print(f"   Top categories retrieved: {categories}\n")
