# =============================================================
# Lab 13 – Exercise 3: Embedding Visualization
# Run AFTER lab13_sentence_transformers.py
# Run: python lab13_visualization.py
# =============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import LabelEncoder

# ── Load data ──────────────────────────────────────────────
embeddings = np.load('../../datasets/article_embeddings.npy')
df         = pd.read_csv('../../datasets/articles.csv')

print(f"Embeddings shape : {embeddings.shape}")
print(f"Articles loaded  : {len(df)}")
print(f"Categories       : {df['category'].unique()}")

# ── Dimensionality reduction ───────────────────────────────
print("\nRunning PCA...")
pca           = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)
print(f"PCA explained variance: {pca.explained_variance_ratio_.sum():.2%}")

print("Running t-SNE...")
tsne           = TSNE(n_components=2, random_state=42, perplexity=5)
embeddings_tsne = tsne.fit_transform(embeddings)

# ── Plot ───────────────────────────────────────────────────
categories     = df['category'].unique()
colors         = plt.cm.Set2(np.linspace(0, 1, len(categories)))
category_color = {cat: colors[i] for i, cat in enumerate(categories)}

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

for ax, data, title, xlabel, ylabel in [
    (axes[0], embeddings_2d,   'PCA Visualization',   'PC1',    'PC2'),
    (axes[1], embeddings_tsne, 't-SNE Visualization', 't-SNE1', 't-SNE2')
]:
    for cat in categories:
        mask = df['category'] == cat
        ax.scatter(
            data[mask, 0], data[mask, 1],
            color=category_color[cat], label=cat, alpha=0.8, s=100
        )

    # Annotate with article IDs
    for idx, row in df.iterrows():
        ax.annotate(
            str(row['id']),
            (data[idx, 0], data[idx, 1]),
            fontsize=9, fontweight='bold',
            xytext=(4, 4), textcoords='offset points'
        )

    ax.set_title(f'{title} of Article Embeddings', fontsize=13)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
output_path = '../../datasets/embedding_visualization.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {output_path}")
plt.show()

# ── Cluster quality ────────────────────────────────────────
le = LabelEncoder()
labels = le.fit_transform(df['category'])

silhouette_avg = silhouette_score(embeddings, labels)
print(f"\nSilhouette Score: {silhouette_avg:.4f}")

if silhouette_avg > 0.7:
    print("Interpretation: Strong clustering structure")
elif silhouette_avg > 0.5:
    print("Interpretation: Reasonable clustering structure")
elif silhouette_avg > 0.25:
    print("Interpretation: Weak clustering structure")
else:
    print("Interpretation: No substantial clustering structure")

# ── Per-category analysis ──────────────────────────────────
print("\nPer-category article distribution:")
print(df.groupby('category')['title'].apply(list).to_string())
