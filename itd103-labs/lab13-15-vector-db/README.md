# Labs 13-15 – Vector Databases & RAG Systems

## Overview

This section covers vector embeddings, local and cloud vector databases,
and Retrieval-Augmented Generation (RAG) pipelines.

## Lab Summary

| Lab | Topic | Key Tools |
|-----|-------|-----------|
| [Lab 13](lab13/) | Vector Embeddings | SentenceTransformers, OpenAI ada-002, PCA, t-SNE |
| [Lab 14](lab14/) | Vector Databases | FAISS (Flat/IVF/HNSW/PQ), Pinecone |
| [Lab 15](lab15/) | RAG Systems | FAISS + GPT-3.5, CrossEncoder, Evaluation |

## Quick Start

### 1. Install all dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API keys

```bash
# Windows
set OPENAI_API_KEY=sk-...
set PINECONE_API_KEY=pcsk_...

# macOS/Linux
export OPENAI_API_KEY=sk-...
export PINECONE_API_KEY=pcsk_...
```

### 3. Run labs in order

```bash
# Lab 13
cd lab13
python lab13_sentence_transformers.py
python lab13_openai_embeddings.py
python lab13_visualization.py

# Lab 14
cd ../lab14
python lab14_faiss_basic.py
python lab14_faiss_advanced.py
python lab14_pinecone_setup.py
python lab14_pinecone_advanced.py

# Lab 15
cd ../lab15
python lab15_rag_basic.py
python lab15_rag_advanced.py
python lab15_evaluation.py
```

## Dataset

`datasets/articles.csv` — 10 articles across 5 categories:

| Category | Articles |
|----------|----------|
| Database | SQL Query Optimization, Database Indexing Strategies, NoSQL vs SQL |
| Technology | Introduction to Machine Learning, Deep Learning Fundamentals, AI in Healthcare |
| Health | Benefits of Regular Exercise, Nutrition and Diet Tips |
| Environment | Climate Change Solutions, Renewable Energy Trends |

## Generated Files

| File | Created by | Description |
|------|-----------|-------------|
| `datasets/article_embeddings.npy` | Lab 13 Ex.1 | 384-dim SentenceTransformer embeddings |
| `datasets/openai_embeddings.npy` | Lab 13 Ex.2 | 1536-dim OpenAI ada-002 embeddings |
| `datasets/embedding_visualization.png` | Lab 13 Ex.3 | PCA + t-SNE scatter plots |
| `datasets/faiss_flat.index` | Lab 14 Ex.1 | Exact flat FAISS index |
| `datasets/faiss_ivf.index` | Lab 14 Ex.1 | IVF approximate FAISS index |
| `datasets/faiss_hnsw.index` | Lab 14 Ex.2 | HNSW graph FAISS index |
| `datasets/faiss_pq.index` | Lab 14 Ex.2 | Product quantization FAISS index |
| `datasets/rag_evaluation_results.csv` | Lab 15 Ex.3 | Per-query RAG evaluation scores |

## Key Concepts

### Embedding Models
- **all-MiniLM-L6-v2** — 384-dim local model, fast, no API key needed
- **text-embedding-ada-002** — 1536-dim OpenAI cloud model, high quality

### FAISS Index Types
| Type | Search | Best for |
|------|--------|---------|
| Flat | Exact | Small datasets, ground truth |
| IVF | Approximate | Medium datasets, good speed/accuracy tradeoff |
| HNSW | Approximate | Large datasets, fastest queries |
| PQ | Approximate | Memory-constrained environments |

### RAG Pipeline
```
Query → Embed → Retrieve (FAISS/Pinecone) → Rerank → Augment Prompt → LLM → Answer
```

### Evaluation Metrics
- **Precision@K** — relevance of retrieved documents
- **Recall@K** — coverage of all relevant documents
- **Faithfulness** — answer grounded in context (LLM judge)
- **Answer Relevance** — semantic similarity of answer to query
