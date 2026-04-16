# =============================================================
# Lab 15 – Exercise 2: Advanced RAG — Chunking, Re-ranking,
#          Conversation Memory, Streaming
# Requires: OPENAI_API_KEY environment variable
# Run: python lab15_rag_advanced.py
# =============================================================

from sentence_transformers import SentenceTransformer, CrossEncoder
import pandas as pd
import numpy as np
import faiss
import os
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model  = SentenceTransformer('all-MiniLM-L6-v2')

# ─────────────────────────────────────────────────────────
# 1. Chunking strategies
# ─────────────────────────────────────────────────────────
def chunk_fixed(text, chunk_size=200, overlap=50):
    """Fixed-size word-level chunks with overlap."""
    words  = text.split()
    chunks = []
    step   = chunk_size - overlap
    for i in range(0, len(words), step):
        chunks.append(" ".join(words[i:i + chunk_size]))
        if i + chunk_size >= len(words):
            break
    return chunks

def chunk_sentences(text, max_sentences=3):
    """Sentence-boundary chunks."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [
        " ".join(sentences[i:i + max_sentences])
        for i in range(0, len(sentences), max_sentences)
    ]

# ─────────────────────────────────────────────────────────
# 2. Build chunked FAISS index
# ─────────────────────────────────────────────────────────
df     = pd.read_csv('../../datasets/articles.csv')
chunks = []   # list of dicts

for _, row in df.iterrows():
    for chunk_text in chunk_sentences(row['content'], max_sentences=3):
        if len(chunk_text.strip()) > 20:
            chunks.append({
                'article_id': row['id'],
                'title'     : row['title'],
                'category'  : row['category'],
                'chunk'     : chunk_text,
            })

chunks_df  = pd.DataFrame(chunks)
print(f"Total chunks: {len(chunks_df)}")

chunk_embs = model.encode(chunks_df['chunk'].tolist()).astype('float32')
dim        = chunk_embs.shape[1]

chunk_index = faiss.IndexFlatL2(dim)
chunk_index.add(chunk_embs)

# ─────────────────────────────────────────────────────────
# 3. Re-ranking with CrossEncoder
# ─────────────────────────────────────────────────────────
try:
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    RERANKER_AVAILABLE = True
    print("CrossEncoder re-ranker loaded.")
except Exception:
    RERANKER_AVAILABLE = False
    print("CrossEncoder not available — skipping re-ranking.")

def retrieve_and_rerank(query, top_k=5, rerank_k=3):
    query_emb = model.encode([query]).astype('float32')
    _, idxs   = chunk_index.search(query_emb, top_k * 2)

    candidates = [chunks_df.iloc[i].to_dict() for i in idxs[0] if i != -1]

    if RERANKER_AVAILABLE and candidates:
        pairs  = [(query, c['chunk']) for c in candidates]
        scores = reranker.predict(pairs)
        ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
        return [c for _, c in ranked[:rerank_k]]

    return candidates[:rerank_k]

# ─────────────────────────────────────────────────────────
# 4. Conversation memory (multi-turn RAG)
# ─────────────────────────────────────────────────────────
class RAGConversation:
    def __init__(self, max_history=6):
        self.history     = []
        self.max_history = max_history

    def chat(self, user_query):
        context_docs = retrieve_and_rerank(user_query)
        context_text = "\n\n".join(
            f"[{d['title']}]\n{d['chunk']}" for d in context_docs
        )

        messages = [
            {
                "role"   : "system",
                "content": (
                    "You are a knowledgeable assistant. Answer using the provided "
                    "context. Keep answers concise (2-3 sentences)."
                ),
            },
            {
                "role"   : "user",
                "content": f"Context:\n{context_text}",
            },
        ]

        # Inject conversation history
        messages += self.history[-self.max_history:]

        messages.append({"role": "user", "content": user_query})

        response = client.chat.completions.create(
            model    = "gpt-3.5-turbo",
            messages = messages,
            max_tokens  = 200,
            temperature = 0.3,
        )
        answer = response.choices[0].message.content

        self.history.append({"role": "user",      "content": user_query})
        self.history.append({"role": "assistant", "content": answer})

        return answer, context_docs

# ─────────────────────────────────────────────────────────
# 5. Streaming response
# ─────────────────────────────────────────────────────────
def rag_stream(query):
    context_docs = retrieve_and_rerank(query, top_k=3, rerank_k=2)
    context_text = "\n\n".join(
        f"[{d['title']}]\n{d['chunk']}" for d in context_docs
    )

    print(f"\nStreaming answer for: {query}")
    print("-" * 60)

    stream = client.chat.completions.create(
        model  = "gpt-3.5-turbo",
        stream = True,
        messages = [
            {"role": "system", "content": "Answer using only the context below."},
            {"role": "user",   "content": f"Context:\n{context_text}\n\nQuestion: {query}"},
        ],
        max_tokens  = 200,
        temperature = 0.3,
    )

    full = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)
        full += delta
    print()
    return full

# ─────────────────────────────────────────────────────────
# 6. Demo
# ─────────────────────────────────────────────────────────
print("\n=== Chunking Demo ===")
sample = df.iloc[0]['content']
print(f"Original ({len(sample.split())} words)")
print(f"Fixed chunks   : {len(chunk_fixed(sample))}")
print(f"Sentence chunks: {len(chunk_sentences(sample))}")

print("\n=== Re-ranked Retrieval ===")
query   = "machine learning algorithms"
top_docs = retrieve_and_rerank(query)
for d in top_docs:
    print(f"  [{d['category']}] {d['title']}: {d['chunk'][:80]}...")

print("\n=== Multi-turn Conversation ===")
conv = RAGConversation()
turns = [
    "What is machine learning?",
    "How does it relate to databases?",
    "Can you give a concrete example?",
]
for turn in turns:
    answer, _ = conv.chat(turn)
    print(f"User : {turn}")
    print(f"Bot  : {answer}\n")

print("\n=== Streaming RAG ===")
rag_stream("What are the best practices for database indexing?")
