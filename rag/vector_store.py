"""
vector_store.py - FAISS vector store for scheme embeddings

Stores and manages vector embeddings using FAISS (Facebook AI Similarity Search).
100% free, runs locally, no paid vector databases.
"""

import json
import os
import numpy as np
import faiss

# Data directories
EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "embeddings")
FAISS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "faiss")
os.makedirs(FAISS_DIR, exist_ok=True)


def build_faiss_index(embeddings, use_gpu=False):
    """
    Build a FAISS index from embeddings.
    Uses IndexFlatIP for inner product similarity (cosine-like).
    Returns the FAISS index object.
    """
    # Normalize embeddings for cosine similarity via inner product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / norms

    # Get embedding dimension
    dimension = embeddings.shape[1]
    print(f"Building FAISS index: dimension={dimension}, vectors={len(embeddings)}")

    # Create index - IndexFlatIP for cosine similarity (after normalization)
    index = faiss.IndexFlatIP(dimension)
    index.add(normalized.astype(np.float32))

    print(f"FAISS index built with {index.ntotal} vectors")
    return index


def build_faiss_index_l2(embeddings):
    """
    Build a FAISS index using L2 distance.
    Alternative to cosine similarity.
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))
    print(f"FAISS L2 index built with {index.ntotal} vectors")
    return index


def save_faiss_index(index, filename="scheme_index.faiss"):
    """
    Save FAISS index to disk.
    """
    filepath = os.path.join(FAISS_DIR, filename)
    faiss.write_index(index, filepath)
    print(f"FAISS index saved to {filepath}")


def load_faiss_index(filename="scheme_index.faiss"):
    """
    Load FAISS index from disk.
    Returns the FAISS index object.
    """
    filepath = os.path.join(FAISS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"FAISS index not found: {filepath}")
        return None
    index = faiss.read_index(filepath)
    print(f"FAISS index loaded: {index.ntotal} vectors")
    return index


def search_index(index, query_embedding, top_k=5):
    """
    Search the FAISS index for similar vectors.
    Returns distances and indices of top_k results.
    """
    # Normalize query for cosine similarity
    query = np.array([query_embedding], dtype=np.float32)
    norms = np.linalg.norm(query, axis=1, keepdims=True)
    query_normalized = query / norms

    # Search
    distances, indices = index.search(query_normalized, top_k)

    return distances[0], indices[0]


def build_index_from_embeddings():
    """
    Main function: load embeddings and build FAISS index.
    """
    # Load embeddings
    npy_path = os.path.join(EMBEDDINGS_DIR, "embeddings.npy")
    if not os.path.exists(npy_path):
        print("Embeddings not found. Run embedder.py first.")
        return None

    embeddings = np.load(npy_path)
    print(f"Loaded embeddings: shape={embeddings.shape}")

    # Build index
    index = build_faiss_index(embeddings)

    # Save index
    save_faiss_index(index)

    return index


if __name__ == "__main__":
    index = build_index_from_embeddings()
    if index:
        print(f"\nFAISS index ready with {index.ntotal} vectors")
