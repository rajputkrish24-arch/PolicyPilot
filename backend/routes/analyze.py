"""
analyze.py - API route handlers for PolicyPilot

Endpoints:
- POST /analyze: Analyze citizen profile for scheme eligibility
- GET /schemes: List all available schemes
- GET /schemes/{name}: Get details of a specific scheme
- GET /health: Health check endpoint
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import json
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.services.eligibility import analyze_eligibility, load_scheme_details
from backend.services.conflict import detect_conflicts

# Try to import AI enhancement
try:
    from backend.services.ai_conflict_analyzer import enhance_eligibility_with_ai, is_ollama_available
    ai_available = True
except ImportError:
    ai_available = False

# Try to import retriever, fall back gracefully
try:
    from rag.retriever import SchemeRetriever
    retriever_available = True
except ImportError:
    retriever_available = False

# Paths
SCHEMES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes")

# Router
router = APIRouter()

# Global retriever instance
_retriever = None


def get_retriever():
    """Get or initialize the scheme retriever."""
    global _retriever
    if _retriever is None and retriever_available:
        try:
            _retriever = SchemeRetriever()
            _retriever.initialize()
        except Exception as e:
            print(f"Could not initialize retriever: {e}")
            _retriever = None
    return _retriever


# ---- Pydantic Models ----

class CitizenProfile(BaseModel):
    """Citizen profile input model."""
    age: int = Field(..., description="Age of the citizen", example=45)
    income: int = Field(..., description="Annual income in Rs", example=150000)
    state: str = Field(..., description="State of residence", example="Gujarat")
    occupation: str = Field(..., description="Occupation", example="Farmer")
    category: Optional[str] = Field(None, description="Social category", example="General")

class EligibilityResult(BaseModel):
    """Single scheme eligibility result."""
    scheme_name: str
    status: str  # "Eligible", "Not Eligible"
    reason: str
    benefits: str = ""
    documents_required: str = ""
    application_steps: str = ""
    ai_tip: str = ""
    ai_overall_advice: str = ""
    ai_enhanced: bool = False

class ConflictResult(BaseModel):
    """Conflict detection result."""
    conflict: bool
    message: str
    schemes_involved: List[str] = []
    conflict_type: str = ""
    priority: str = "Medium"
    is_real_conflict: bool = False
    ai_explanation: str = ""
    ai_recommendation: str = ""

class AnalyzeResponse(BaseModel):
    """Full analysis response."""
    eligible_schemes: List[EligibilityResult] = []
    conflicts: List[ConflictResult] = []
    total_schemes_checked: int = 0
    ai_summary: str = ""
    ai_enabled: bool = False


# ---- Endpoints ----

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_profile(profile: CitizenProfile):
    """
    Analyze a citizen's profile against government schemes.
    Returns eligible schemes, benefits, and any conflicts.
    """
    retriever = get_retriever()

    if retriever:
        # Use FAISS retriever for semantic search
        retrieved = retriever.search_by_profile(profile.dict(), top_k=10)
    else:
        # Fallback: load all schemes from JSON
        retrieved = load_all_schemes_as_chunks()

    if not retrieved:
        raise HTTPException(
            status_code=503,
            detail="No scheme data available. Run the scraper and RAG pipeline first."
        )

    # Run eligibility analysis
    eligibility_results = analyze_eligibility(profile.dict(), retrieved)

    # AI eligibility enhancement (tips and advice)
    ai_enabled = False
    ai_summary = ""
    print(f"DEBUG: AI available = {ai_available}")
    if ai_available:
        try:
            print("DEBUG: Calling enhance_eligibility_with_ai...")
            eligibility_results = enhance_eligibility_with_ai(eligibility_results, profile.dict())
            ai_enabled = any(r.get("ai_enhanced") for r in eligibility_results)
            print(f"DEBUG: AI eligibility enhanced = {ai_enabled}")
        except Exception as e:
            print(f"AI eligibility enhancement failed: {e}")

    # Detect conflicts (with AI enhancement)
    conflicts = detect_conflicts(eligibility_results, profile.dict())

    # Get AI summary from conflict analysis
    try:
        print("DEBUG: Calling AI conflict analysis...")
        from backend.services.ai_conflict_analyzer import analyze_conflicts_with_llm
        ai_conflict_result = analyze_conflicts_with_llm(conflicts, profile.dict())
        print(f"DEBUG: AI conflict result = {ai_conflict_result.get('ai_enhanced') if ai_conflict_result else 'None'}")
        if ai_conflict_result and ai_conflict_result.get("ai_enhanced"):
            ai_summary = ai_conflict_result.get("summary", "")
            conflicts = ai_conflict_result.get("conflicts", conflicts)
            ai_enabled = True
            print(f"DEBUG: AI summary from conflicts = {ai_summary[:100]}...")
    except Exception as e:
        print(f"AI conflict summary failed: {e}")

    # If no conflict summary but we have eligibility advice, use that as summary
    if not ai_summary and ai_enabled:
        # Get overall_advice from first eligible scheme with ai_enhanced
        for result in eligibility_results:
            if result.get("ai_enhanced") and result.get("ai_overall_advice"):
                ai_summary = result.get("ai_overall_advice")
                print(f"DEBUG: AI summary from eligibility advice = {ai_summary[:100]}...")
                break

    return AnalyzeResponse(
        eligible_schemes=eligibility_results,
        conflicts=conflicts,
        total_schemes_checked=len(retrieved),
        ai_summary=ai_summary,
        ai_enabled=ai_enabled,
    )


@router.get("/schemes")
async def get_all_schemes():
    """
    Get all available government schemes.
    Returns scheme names and basic info.
    """
    filepath = os.path.join(SCHEMES_DIR, "all_schemes.json")
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail="No schemes found. Run the scraper first."
        )

    with open(filepath, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    # Return summary (not full text) for listing
    summary = []
    for scheme in schemes:
        summary.append({
            "name": scheme.get("name", ""),
            "category": scheme.get("category", ""),
            "state": scheme.get("state", ""),
            "benefits": scheme.get("benefits", "")[:100] + "..." if len(scheme.get("benefits", "")) > 100 else scheme.get("benefits", ""),
        })

    return {"schemes": summary, "total": len(summary)}


@router.get("/schemes/{scheme_name:path}")
async def get_scheme_details(scheme_name: str):
    """
    Get detailed information about a specific scheme.
    """
    details = load_scheme_details(scheme_name)
    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"Scheme '{scheme_name}' not found."
        )
    return details


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    retriever_status = "available" if get_retriever() else "unavailable"
    schemes_count = 0

    filepath = os.path.join(SCHEMES_DIR, "all_schemes.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            schemes_count = len(json.load(f))

    return {
        "status": "healthy",
        "retriever": retriever_status,
        "schemes_loaded": schemes_count,
    }


# ---- Helper Functions ----

def load_all_schemes_as_chunks():
    """
    Fallback: load all schemes from JSON as chunk-like objects.
    Used when FAISS retriever is not available.
    """
    filepath = os.path.join(SCHEMES_DIR, "all_schemes.json")
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    chunks = []
    for scheme in schemes:
        chunk = {
            "scheme_name": scheme.get("name", "Unknown"),
            "text": scheme.get("full_text", ""),
            "metadata": {
                "name": scheme.get("name", ""),
                "category": scheme.get("category", ""),
                "state": scheme.get("state", ""),
                "min_age": scheme.get("min_age"),
                "max_age": scheme.get("max_age"),
                "max_income": scheme.get("max_income"),
            }
        }
        chunks.append(chunk)

    return chunks
