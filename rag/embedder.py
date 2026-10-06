"""
embedder.py - Embedding generation module for RAG pipeline

Generates vector embeddings using sentence-transformers (all-MiniLM-L6-v2).
100% free and runs locally - no paid APIs.
"""

import json
import os
import numpy as np

# Model name - free, lightweight, runs on CPU
MODEL_NAME = "all-MiniLM-L6-v2"

# Data directories
CHUNKS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chunks")
EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "embeddings")
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# Try to import sentence-transformers, handle gracefully if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception as e:
    print(f"Warning: sentence-transformers not available ({e})")
    print("Falling back to simple hash-based embeddings (demo mode)")
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


def simple_hash_embedding(text, dim=384):
    """
    Simple fallback embedding using hash-based approach.
    Not as good as neural embeddings but works without torch.
    """
    import hashlib
    vec = np.zeros(dim, dtype=np.float32)
    # Use multiple hash functions for different positions
    for i, word in enumerate(text.lower().split()[:50]):  # First 50 words
        h = hashlib.md5(word.encode()).hexdigest()
        for j in range(8):
            idx = (i * 8 + j) % dim
            val = int(h[j*4:(j+1)*4], 16) / 65535.0
            vec[idx] += val
    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def load_embedding_model(model_name=MODEL_NAME):
    """
    Load the SentenceTransformer model.
    Downloads the model on first run (free, ~80MB).
    Subsequent runs use cached model.
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("Sentence-transformers not available, using fallback")
        return None
    
    print(f"Loading embedding model: {model_name}")
    print("First run will download the model (~80MB). Please wait...")
    model = SentenceTransformer(model_name)
    print(f"Model loaded successfully. Embedding dimension: {model.get_sentence_embedding_dimension()}")
    return model


def generate_embeddings(chunks, model=None):
    """
    Generate embeddings for a list of chunk records.
    Each chunk has a 'text' field that gets embedded.
    Returns numpy array of embeddings and list of chunk IDs.
    """
    if model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
        model = load_embedding_model()

    # Extract text from chunks
    texts = [chunk["text"] for chunk in chunks]
    chunk_ids = [chunk["chunk_id"] for chunk in chunks]

    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    if model is not None:
        # Use sentence-transformers
        embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
        embeddings = np.array(embeddings, dtype=np.float32)
    else:
        # Fallback: use simple hash-based embeddings
        print("Using fallback hash-based embeddings (demo mode)")
        embeddings = np.array([simple_hash_embedding(text) for text in texts], dtype=np.float32)
    
    print(f"Embeddings shape: {embeddings.shape}")
    return embeddings, chunk_ids


def save_embeddings(embeddings, chunk_ids, metadata_list=None):
    """
    Save embeddings and metadata to disk.
    Uses numpy format for vectors and JSON for metadata.
    """
    # Save numpy array
    npy_path = os.path.join(EMBEDDINGS_DIR, "embeddings.npy")
    np.save(npy_path, embeddings)
    print(f"Saved embeddings to {npy_path}")

    # Save chunk IDs mapping
    ids_path = os.path.join(EMBEDDINGS_DIR, "chunk_ids.json")
    with open(ids_path, "w", encoding="utf-8") as f:
        json.dump(chunk_ids, f, indent=2)
    print(f"Saved chunk IDs to {ids_path}")

    # Save metadata if provided
    if metadata_list:
        meta_path = os.path.join(EMBEDDINGS_DIR, "chunk_metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata_list, f, indent=2, ensure_ascii=False)
        print(f"Saved metadata to {meta_path}")


def load_embeddings():
    """
    Load saved embeddings and metadata from disk.
    Returns embeddings array, chunk IDs, and metadata.
    """
    npy_path = os.path.join(EMBEDDINGS_DIR, "embeddings.npy")
    ids_path = os.path.join(EMBEDDINGS_DIR, "chunk_ids.json")
    meta_path = os.path.join(EMBEDDINGS_DIR, "chunk_metadata.json")

    if not os.path.exists(npy_path) or not os.path.exists(ids_path):
        print("Embeddings not found. Run embedder.py first.")
        return None, None, None

    embeddings = np.load(npy_path)
    with open(ids_path, "r", encoding="utf-8") as f:
        chunk_ids = json.load(f)

    metadata = None
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    print(f"Loaded embeddings: shape={embeddings.shape}")
    return embeddings, chunk_ids, metadata


def run_embedder():
    """
    Main function: load chunks, generate embeddings, save to disk.
    """
    # Load chunks
    chunks_path = os.path.join(CHUNKS_DIR, "scheme_chunks.json")
    if not os.path.exists(chunks_path):
        print("Chunks not found. Run chunker.py first.")
        return

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks")

    # Load model and generate embeddings
    model = load_embedding_model()
    embeddings, chunk_ids = generate_embeddings(chunks, model)

    # Extract metadata from chunks
    metadata_list = [
        {
            "chunk_id": chunk["chunk_id"],
            "scheme_name": chunk["scheme_name"],
            "text": chunk["text"],
            "metadata": chunk.get("metadata", {}),
        }
        for chunk in chunks
    ]

    # Save everything
    save_embeddings(embeddings, chunk_ids, metadata_list)
    print("\nEmbedding generation complete!")


if __name__ == "__main__":
    run_embedder()
