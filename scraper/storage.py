"""
storage.py - JSON file storage for scheme data

Handles saving and loading scheme data from JSON files.
Simple, free, no database required.
"""

import json
import os

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "schemes")
os.makedirs(DATA_DIR, exist_ok=True)


def save_schemes(schemes, filename="all_schemes.json"):
    """
    Save a list of scheme dicts to a JSON file.
    """
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schemes, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(schemes)} schemes to {filepath}")
    return filepath


def load_schemes(filename="all_schemes.json"):
    """
    Load schemes from a JSON file.
    Returns a list of scheme dicts.
    """
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        schemes = json.load(f)
    print(f"Loaded {len(schemes)} schemes from {filepath}")
    return schemes


def add_scheme(scheme, filename="all_schemes.json"):
    """
    Add a single scheme to the JSON file.
    """
    schemes = load_schemes(filename)
    schemes.append(scheme)
    save_schemes(schemes, filename)
    return schemes


def search_schemes(query, filename="all_schemes.json"):
    """
    Simple text search across scheme data.
    Searches name, eligibility, benefits, and category fields.
    """
    schemes = load_schemes(filename)
    query_lower = query.lower()
    results = []

    for scheme in schemes:
        # Search in multiple fields
        searchable = (
            scheme.get("name", "") + " " +
            scheme.get("eligibility", "") + " " +
            scheme.get("benefits", "") + " " +
            scheme.get("category", "") + " " +
            scheme.get("state", "")
        ).lower()

        if query_lower in searchable:
            results.append(scheme)

    return results


def get_scheme_by_name(name, filename="all_schemes.json"):
    """
    Find a scheme by its exact name.
    """
    schemes = load_schemes(filename)
    for scheme in schemes:
        if scheme.get("name", "").lower() == name.lower():
            return scheme
    return None


def get_all_scheme_names(filename="all_schemes.json"):
    """
    Get a list of all scheme names.
    """
    schemes = load_schemes(filename)
    return [s.get("name", "Unknown") for s in schemes]


if __name__ == "__main__":
    # Test storage functions
    schemes = load_schemes()
    print(f"\nScheme names: {get_all_scheme_names()[:5]}")

    # Test search
    results = search_schemes("farmer")
    print(f"\nFarmer schemes found: {len(results)}")
    for r in results:
        print(f"  - {r['name']}")
