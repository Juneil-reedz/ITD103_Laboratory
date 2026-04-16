# Lab 15 – RAG System & LLM Integration

## Overview
Build a Retrieval-Augmented Generation (RAG) pipeline that combines FAISS
vector search with OpenAI GPT to answer questions grounded in a document corpus.
Implement advanced features (chunking, re-ranking, streaming) and evaluate quality.

## Exercises

| Exercise | File | Description |
|----------|------|-------------|
| 1 | `lab15_rag_basic.py` | Basic RAG pipeline (retrieve → augment → generate) |
| 2 | `lab15_rag_advanced.py` | Chunking, re-ranking, conversation memory, streaming |
| 3 | `lab15_evaluation.py` | Precision@K, Recall@K, faithfulness, answer relevance |

## Setup

```bash
pip install sentence-transformers openai faiss-cpu pandas numpy
# Optional: re-ranker (Exercise 2)
pip install sentence-transformers[cross-encoder]
```

Set your OpenAI key:
```bash
# Windows
set OPENAI_API_KEY=sk-...

# macOS/Linux
export OPENAI_API_KEY=sk-...
```

## Run Order

```bash
python lab15_rag_basic.py       # basic retrieve + generate
python lab15_rag_advanced.py    # chunked index, rerank, streaming, chat
python lab15_evaluation.py      # metrics against ground-truth set
```

> Exercises 1-3 build their own FAISS index from `datasets/articles.csv`
> each run — no dependency on Lab 14 files required.

## Working Queries

### Exercise 1 — Basic RAG

```python
from lab15_rag_basic import rag_query

result = rag_query("How can I improve database query performance?")
```

Expected output:
```
Question: How can I improve database query performance?
------------------------------------------------------------
Retrieved context:
  [0.642] SQL Query Optimization Techniques (Database)
  [0.601] Database Indexing Strategies (Database)
  [0.421] NoSQL vs SQL Performance (Database)

Answer:
Based on the articles, you can improve database query performance by creating
appropriate indexes on frequently queried columns, rewriting inefficient queries,
and using query execution plans to identify bottlenecks.
============================================================
```

### Exercise 2 — Chunked Retrieval with Re-ranking

```python
from lab15_rag_advanced import retrieve_and_rerank

docs = retrieve_and_rerank("machine learning algorithms", top_k=5, rerank_k=3)
for d in docs:
    print(f"[{d['category']}] {d['title']}: {d['chunk'][:80]}...")
```

Expected output:
```
[Technology] Introduction to Machine Learning: Machine learning algorithms learn
[Technology] Deep Learning Fundamentals: Neural networks are a subset of machine...
[Technology] AI in Healthcare: Artificial intelligence applications include...
```

### Exercise 2 — Multi-turn Conversation

```python
from lab15_rag_advanced import RAGConversation

conv = RAGConversation()

answer, _ = conv.chat("What is machine learning?")
print(f"Bot: {answer}")

answer, _ = conv.chat("How does it relate to databases?")
print(f"Bot: {answer}")

answer, _ = conv.chat("Give a concrete example.")
print(f"Bot: {answer}")
```

Expected output:
```
Bot: Machine learning is a subset of AI that enables computers to learn from
     data without being explicitly programmed, using algorithms like decision
     trees, neural networks, and clustering.

Bot: Machine learning connects to databases through training data storage,
     feature engineering pipelines, and model serving — databases power the
     data layer that feeds ML systems.

Bot: A recommendation engine like Netflix uses a database of viewing history,
     trains an ML model on that data, and stores predictions back in the DB
     for fast retrieval at request time.
```

### Exercise 2 — Streaming RAG

```python
from lab15_rag_advanced import rag_stream

rag_stream("What are the best practices for database indexing?")
```

Expected output (streamed token by token):
```
Streaming answer for: What are the best practices for database indexing?
------------------------------------------------------------
Database indexing best practices include: creating indexes on columns used
in WHERE clauses and JOIN conditions, avoiding over-indexing which slows writes,
using composite indexes for multi-column queries, and regularly monitoring
index usage statistics to remove unused indexes.
```

### Exercise 3 — Evaluation Metrics

```python
# Runs against 5 ground-truth Q&A pairs
python lab15_evaluation.py
```

Expected output:
```
Query: How to optimize database queries?
  Retrieved IDs : [1, 2, 5]  |  Relevant: [1, 2]
  P@3=0.67  R@3=1.00  F1=0.80  AnsRel=0.72  Faithfulness=0.95

Query: What are benefits of exercise?
  Retrieved IDs : [4, 6, 3]  |  Relevant: [4]
  P@3=0.33  R@3=1.00  F1=0.50  AnsRel=0.68  Faithfulness=0.91
...

Mean scores:
  precision@3           : 0.5300
  recall@3              : 0.9000
  f1                    : 0.6200
  answer_relevance      : 0.7100
  faithfulness          : 0.9200
```

## RAG Architecture

```
User Query
    │
    ▼
[Embedding Model]  ← all-MiniLM-L6-v2
    │
    ▼
[FAISS Index]  ─→  Top-K Chunks
    │
    ▼
[Re-ranker]  ←─  CrossEncoder (optional)
    │
    ▼
[Context Assembly]
    │
    ▼
[OpenAI GPT-3.5]  ─→  Grounded Answer
```

## Evaluation Metrics Reference

| Metric | Formula | What it measures |
|--------|---------|-----------------|
| Precision@K | hits / K | Fraction of retrieved docs that are relevant |
| Recall@K | hits / total_relevant | Fraction of relevant docs retrieved |
| F1 | 2·P·R / (P+R) | Harmonic mean of precision & recall |
| Answer Relevance | cosine_sim(query, answer) | How well the answer addresses the query |
| Faithfulness | LLM judge (0–1) | Whether the answer is grounded in context |

## Output Files

| File | Description |
|------|-------------|
| `datasets/rag_evaluation_results.csv` | Per-query evaluation scores |
