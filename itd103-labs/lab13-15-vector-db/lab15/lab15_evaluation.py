# =============================================================
# Lab 15 – Exercise 3: RAG Evaluation — Precision, Recall,
#          Faithfulness, Answer Relevance
# Run: python lab15_evaluation.py
# =============================================================

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model  = SentenceTransformer('all-MiniLM-L6-v2')

# ── Build index (same as lab15_rag_basic) ─────────────────
df         = pd.read_csv('../../datasets/articles.csv')
embeddings = model.encode(df['content'].tolist()).astype('float32')
index      = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

def retrieve(query, top_k=3):
    q_emb = model.encode([query]).astype('float32')
    dists, idxs = index.search(q_emb, top_k)
    results = []
    for i, idx in enumerate(idxs[0]):
        if idx != -1:
            results.append({
                'id'      : int(df.iloc[idx]['id']),
                'title'   : df.iloc[idx]['title'],
                'category': df.iloc[idx]['category'],
                'content' : df.iloc[idx]['content'],
                'score'   : round(1 / (1 + float(dists[0][i])), 4),
            })
    return results

def generate_answer(query, docs):
    context = "\n\n".join(f"[{d['title']}]\n{d['content']}" for d in docs)
    resp = client.chat.completions.create(
        model    = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content":
                "Answer the question using ONLY the provided context. "
                "Be factual and concise."},
            {"role": "user", "content":
                f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        max_tokens  = 200,
        temperature = 0.1,
    )
    return resp.choices[0].message.content

# ─────────────────────────────────────────────────────────
# Ground-truth dataset  (query → relevant article IDs)
# ─────────────────────────────────────────────────────────
GROUND_TRUTH = [
    {
        "query"        : "How to optimize database queries?",
        "relevant_ids" : [1, 2],           # Database-category articles
        "ideal_answer" : "Use indexes and query optimization techniques.",
    },
    {
        "query"        : "What are benefits of exercise?",
        "relevant_ids" : [4],
        "ideal_answer" : "Regular exercise improves health and reduces disease risk.",
    },
    {
        "query"        : "Latest AI developments",
        "relevant_ids" : [3, 7],
        "ideal_answer" : "AI advances include deep learning and large language models.",
    },
    {
        "query"        : "Climate change solutions",
        "relevant_ids" : [9, 10],
        "ideal_answer" : "Renewable energy and carbon reduction help combat climate change.",
    },
    {
        "query"        : "Python programming tips",
        "relevant_ids" : [8],
        "ideal_answer" : "Python best practices include readable code and efficient libraries.",
    },
]

# ─────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────
def precision_at_k(retrieved_ids, relevant_ids, k):
    retrieved_k = retrieved_ids[:k]
    hits        = sum(1 for r in retrieved_k if r in relevant_ids)
    return hits / k if k else 0.0

def recall_at_k(retrieved_ids, relevant_ids, k):
    retrieved_k = retrieved_ids[:k]
    hits        = sum(1 for r in retrieved_k if r in relevant_ids)
    return hits / len(relevant_ids) if relevant_ids else 0.0

def semantic_similarity(text_a, text_b):
    """Cosine similarity between two text embeddings."""
    emb_a = model.encode([text_a]).astype('float32')
    emb_b = model.encode([text_b]).astype('float32')
    dot   = float(np.dot(emb_a[0], emb_b[0]))
    norm  = float(np.linalg.norm(emb_a[0]) * np.linalg.norm(emb_b[0]))
    return dot / norm if norm > 0 else 0.0

def faithfulness_score(answer, context_docs):
    """
    LLM-based faithfulness: ask GPT if the answer is grounded
    in the context (returns a 0-1 float).
    """
    context = "\n\n".join(f"[{d['title']}]\n{d['content'][:300]}" for d in context_docs)
    prompt  = (
        f"Context:\n{context}\n\n"
        f"Answer: {answer}\n\n"
        "On a scale of 0.0 to 1.0, how faithful is the answer to the context? "
        "Reply with ONLY the number."
    )
    try:
        resp = client.chat.completions.create(
            model    = "gpt-3.5-turbo",
            messages = [{"role": "user", "content": prompt}],
            max_tokens  = 10,
            temperature = 0.0,
        )
        return float(resp.choices[0].message.content.strip())
    except Exception:
        return 0.0

# ─────────────────────────────────────────────────────────
# Evaluate
# ─────────────────────────────────────────────────────────
print("=== RAG Evaluation ===\n")
records = []

for item in GROUND_TRUTH:
    query        = item["query"]
    relevant_ids = item["relevant_ids"]
    ideal_answer = item["ideal_answer"]

    docs          = retrieve(query, top_k=3)
    retrieved_ids = [d['id'] for d in docs]
    answer        = generate_answer(query, docs)

    p3  = precision_at_k(retrieved_ids, relevant_ids, k=3)
    r3  = recall_at_k(retrieved_ids, relevant_ids, k=3)
    f1  = 2 * p3 * r3 / (p3 + r3) if (p3 + r3) > 0 else 0.0
    ans_rel   = semantic_similarity(query, answer)
    faithf    = faithfulness_score(answer, docs)

    print(f"Query: {query}")
    print(f"  Retrieved IDs : {retrieved_ids}  |  Relevant: {relevant_ids}")
    print(f"  P@3={p3:.2f}  R@3={r3:.2f}  F1={f1:.2f}  "
          f"AnsRel={ans_rel:.2f}  Faithfulness={faithf:.2f}")
    print(f"  Answer: {answer[:120]}...")
    print()

    records.append({
        "query"        : query,
        "precision@3"  : round(p3, 4),
        "recall@3"     : round(r3, 4),
        "f1"           : round(f1, 4),
        "answer_relevance": round(ans_rel, 4),
        "faithfulness" : round(faithf, 4),
    })

# ─────────────────────────────────────────────────────────
# Summary table
# ─────────────────────────────────────────────────────────
results_df = pd.DataFrame(records)
print("=== Aggregate Metrics ===")
print(results_df.describe().loc[['mean', 'std']].to_string())
print()

avg = results_df[["precision@3","recall@3","f1","answer_relevance","faithfulness"]].mean()
print("Mean scores:")
for col, val in avg.items():
    print(f"  {col:<22}: {val:.4f}")

# Save results
out_path = "../../datasets/rag_evaluation_results.csv"
results_df.to_csv(out_path, index=False)
print(f"\nResults saved to: {out_path}")
