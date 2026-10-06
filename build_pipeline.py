"""
build_pipeline.py - One-click pipeline to build the RAG index

Runs the full data pipeline:
1. Scrape scheme data (or use sample data)
2. Parse any PDFs
3. Merge scheme sources
4. Chunk text
5. Generate embeddings
6. Build FAISS index

Run: python build_pipeline.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


def run_step(name, func):
    """Run a pipeline step with error handling."""
    print(f"\n{'='*60}")
    print(f"STEP: {name}")
    print(f"{'='*60}")
    try:
        result = func()
        print(f"✓ {name} completed successfully")
        return result
    except Exception as e:
        print(f"✗ {name} failed: {e}")
        return None


def main():
    print("PolicyPilot - Data Pipeline Builder")
    print("=" * 60)

    # Step 1: Scrape schemes
    from scraper.scraper import run_scraper
    schemes = run_step("Scrape Schemes", lambda: run_scraper())

    # Step 2: Parse PDFs (if any)
    from scraper.pdf_parser import process_pdf_directory, merge_scheme_files
    run_step("Parse PDFs", lambda: process_pdf_directory())

    # Step 3: Merge all scheme sources
    all_schemes = run_step("Merge Schemes", lambda: merge_scheme_files())

    if not all_schemes:
        print("\nNo scheme data available. Cannot continue pipeline.")
        print("Check that scraper.py or sample data is available.")
        return

    # Step 4: Chunk text
    from rag.chunker import chunk_all_schemes
    chunks = run_step("Chunk Text", lambda: chunk_all_schemes())

    if not chunks:
        print("\nNo chunks created. Cannot continue pipeline.")
        return

    # Step 5: Generate embeddings
    from rag.embedder import run_embedder
    run_step("Generate Embeddings", lambda: run_embedder())

    # Step 6: Build FAISS index
    from rag.vector_store import build_index_from_embeddings
    index = run_step("Build FAISS Index", lambda: build_index_from_embeddings())

    # Summary
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print(f"{'='*60}")
    if all_schemes:
        print(f"  Schemes: {len(all_schemes)}")
    if chunks:
        print(f"  Chunks: {len(chunks)}")
    if index:
        print(f"  FAISS vectors: {index.ntotal}")
    print(f"\nYou can now start the backend:")
    print(f"  cd backend && uvicorn main:app --reload")


if __name__ == "__main__":
    main()
