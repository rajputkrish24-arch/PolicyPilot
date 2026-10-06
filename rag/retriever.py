"""
retriever.py - Similarity search retriever for RAG pipeline

Searches FAISS index for relevant scheme chunks given a query.
Uses sentence-transformers for query embedding and FAISS for search.
100% free and local.
"""

import json
import os
import hashlib
import numpy as np

# Model for query embedding (same as document embedding)
MODEL_NAME = "all-MiniLM-L6-v2"

# Data directories
EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "embeddings")
FAISS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "faiss")

# Try to import sentence-transformers, handle gracefully if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception as e:
    print(f"Warning: sentence-transformers not available ({e})")
    print("Retriever will use fallback hash-based embeddings")
    SENTENCE_TRANSFORMERS_AVAILABLE = False


def simple_hash_embedding(text, dim=384):
    """Simple fallback embedding using hash-based approach."""
    vec = np.zeros(dim, dtype=np.float32)
    for i, word in enumerate(text.lower().split()[:50]):
        h = hashlib.md5(word.encode()).hexdigest()
        for j in range(8):
            idx = (i * 8 + j) % dim
            val = int(h[j*4:(j+1)*4], 16) / 65535.0
            vec[idx] += val
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


class SchemeRetriever:
    """
    Retrieves relevant scheme chunks using FAISS similarity search.
    """

    def __init__(self, model_name=MODEL_NAME):
        self.model = None
        self.model_name = model_name
        self.index = None
        self.metadata = None
        self.chunk_ids = None

    def initialize(self):
        """
        Load model, FAISS index, and metadata.
        Call this before performing searches.
        """
        # Load embedding model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            print(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        else:
            print("Using fallback hash-based embeddings (demo mode)")

        # Load FAISS index
        import faiss
        index_path = os.path.join(FAISS_DIR, "scheme_index.faiss")
        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. "
                "Run vector_store.py first to build the index."
            )
        self.index = faiss.read_index(index_path)
        print(f"Loaded FAISS index with {self.index.ntotal} vectors")

        # Load metadata (chunk text and scheme info)
        meta_path = os.path.join(EMBEDDINGS_DIR, "chunk_metadata.json")
        if not os.path.exists(meta_path):
            raise FileNotFoundError(
                f"Metadata not found at {meta_path}. "
                "Run embedder.py first to generate metadata."
            )
        with open(meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        # Load chunk IDs
        ids_path = os.path.join(EMBEDDINGS_DIR, "chunk_ids.json")
        with open(ids_path, "r", encoding="utf-8") as f:
            self.chunk_ids = json.load(f)

        print("Retriever initialized successfully!")

    def embed_query(self, query):
        """
        Generate embedding for a search query.
        """
        if self.model is not None:
            embedding = self.model.encode([query], show_progress_bar=False)
            return embedding[0]
        else:
            # Fallback: use simple hash-based embedding
            return simple_hash_embedding(query)

    def search(self, query, top_k=5):
        """
        Search for relevant scheme chunks given a query string.
        Returns a list of result dicts with text, score, and metadata.
        """
        if self.index is None:
            raise RuntimeError("Index not loaded. Call initialize() first.")

        # Embed the query
        query_embedding = self.embed_query(query)

        # Normalize for cosine similarity
        query_vec = np.array([query_embedding], dtype=np.float32)
        norms = np.linalg.norm(query_vec, axis=1, keepdims=True)
        query_normalized = query_vec / norms

        # Search FAISS index
        distances, indices = self.index.search(query_normalized, top_k)

        # Build results
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx == -1:  # FAISS returns -1 for no result
                continue

            score = float(distances[0][i])
            meta = self.metadata[idx] if idx < len(self.metadata) else {}

            result = {
                "chunk_id": meta.get("chunk_id", ""),
                "scheme_name": meta.get("scheme_name", ""),
                "text": meta.get("text", ""),
                "score": score,
                "metadata": meta.get("metadata", {}),
            }
            results.append(result)

        return results

    def search_by_profile(self, profile, top_k=10):
        """
        Search for schemes relevant to a citizen profile.
        Constructs a query from profile fields and searches.
        """
        # Build search query from profile
        query_parts = []
        if profile.get("occupation"):
            query_parts.append(f"occupation {profile['occupation']}")
        if profile.get("state"):
            query_parts.append(f"state {profile['state']}")
        if profile.get("category"):
            query_parts.append(f"category {profile['category']}")
        if profile.get("age"):
            query_parts.append(f"age {profile['age']} years")
        if profile.get("income"):
            query_parts.append(f"income {profile['income']}")

        query = " ".join(query_parts)
        if not query:
            query = "government welfare scheme benefits eligibility"

        return self.search(query, top_k=top_k)


def get_retriever():
    """
    Factory function to get an initialized retriever.
    """
    retriever = SchemeRetriever()
    retriever.initialize()
    return retriever


if __name__ == "__main__":
    # Test the retriever
    retriever = SchemeRetriever()
    retriever.initialize()

    # Test search
    results = retriever.search("farmer scheme income support", top_k=3)
    print("\n--- Search Results ---")
    for r in results:
        print(f"\nScheme: {r['scheme_name']}")
        print(f"Score: {r['score']:.4f}")
        print(f"Text: {r['text'][:150]}...")

    # Test profile search
    profile = {"age": 45, "income": 150000, "state": "Gujarat", "occupation": "Farmer"}
    results = retriever.search_by_profile(profile, top_k=3)
    print("\n--- Profile Search Results ---")
    for r in results:
        print(f"\nScheme: {r['scheme_name']}")
        print(f"Score: {r['score']:.4f}")
