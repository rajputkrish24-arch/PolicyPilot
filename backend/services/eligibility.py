"""
eligibility.py - Eligibility Engine for PolicyPilot

Matches citizen profile against scheme eligibility criteria.
Uses rule-based logic with optional local LLM enhancement via Ollama.

Output format:
{
    "scheme_name": "...",
    "status": "Eligible" | "Not Eligible" | "Uncertain",
    "reason": "...",
    "benefits": "...",
    "documents_required": "...",
    "application_steps": "..."
}
"""

import json
import os
import re
import requests as http_requests

# Paths
SCHEMES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes")

# Ollama settings (local LLM - free) - load from environment
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


def check_eligibility_rule_based(profile, scheme):
    """
    Check eligibility using comprehensive rule-based logic.
    Compares citizen profile fields against scheme metadata and
    eligibility text to make clear Eligible/Not Eligible decisions.

    profile: dict with age, income, state, occupation, category
    scheme: dict with scheme data including metadata

    Returns: dict with status and reason
    """
    reasons = []
    eligible = True

    occupation = profile.get("occupation", "").lower()
    user_age = profile.get("age")
    user_income = profile.get("income")
    user_state = profile.get("state", "")
    user_category = profile.get("category", "").lower()
    scheme_name = scheme.get("scheme_name", scheme.get("name", "Unknown"))

    # --- STEP 1: Hard eligibility checks (automatic Not Eligible) ---

    # 1a. Age check
    min_age = scheme.get("metadata", {}).get("min_age")
    max_age = scheme.get("metadata", {}).get("max_age")

    if min_age is not None and user_age is not None:
        if user_age < min_age:
            eligible = False
            reasons.append(f"Age {user_age} is below minimum requirement of {min_age}")
        else:
            reasons.append(f"Age {user_age} meets minimum requirement of {min_age}")

    if max_age is not None and user_age is not None:
        if user_age > max_age:
            eligible = False
            reasons.append(f"Age {user_age} exceeds maximum limit of {max_age}")
        else:
            reasons.append(f"Age {user_age} is within maximum limit of {max_age}")

    # 1b. Income check
    max_income = scheme.get("metadata", {}).get("max_income")
    if max_income is not None and user_income is not None:
        if user_income > max_income:
            eligible = False
            reasons.append(f"Income Rs {user_income:,} exceeds limit of Rs {max_income:,}")
        else:
            reasons.append(f"Income Rs {user_income:,} is within limit of Rs {max_income:,}")

    # 1c. State check
    scheme_state = scheme.get("metadata", {}).get("state", "")
    if scheme_state and user_state:
        if scheme_state.lower() not in ["all india", "all"] and scheme_state.lower() != user_state.lower():
            eligible = False
            reasons.append(f"Scheme is for {scheme_state}, applicant is from {user_state}")
        else:
            reasons.append(f"State requirement met: {user_state}")

    # --- STEP 2: Occupation-scheme compatibility matrix ---
    # Defines which occupations CAN and CANNOT apply for each scheme category

    if eligible and occupation:
        scheme_category = scheme.get("metadata", {}).get("category", "").lower()

        # Occupation compatibility: which scheme categories each occupation can access
        occupation_access = {
            "farmer": {
                "can_access": ["farmer", "agriculture", "kisan", "insurance", "welfare", "pension", "housing", "health", "savings"],
                "cannot_access": ["business", "entrepreneur", "mudra", "student", "education", "women"],
            },
            "business": {
                "can_access": ["business", "entrepreneur", "mudra", "insurance", "housing", "savings", "health"],
                "cannot_access": ["farmer", "agriculture", "kisan", "student", "education", "women"],
            },
            "government": {
                "can_access": ["insurance", "health", "housing", "savings", "pension"],
                "cannot_access": ["farmer", "agriculture", "kisan", "welfare", "shram", "women", "student"],
            },
            "student": {
                "can_access": ["education", "scholarship", "student", "insurance", "health", "savings"],
                "cannot_access": ["farmer", "agriculture", "business", "entrepreneur", "mudra", "pension", "welfare", "women"],
            },
            "worker": {
                "can_access": ["pension", "insurance", "welfare", "shram", "labor", "health", "housing", "savings"],
                "cannot_access": ["farmer", "agriculture", "business", "entrepreneur", "student", "education", "women"],
            },
            "woman": {
                "can_access": ["women", "mahila", "sukanya", "ujjwala", "insurance", "health", "housing", "savings", "welfare"],
                "cannot_access": ["farmer", "agriculture", "business", "entrepreneur", "student", "education"],
            },
            "senior": {
                "can_access": ["pension", "insurance", "health", "welfare", "savings", "housing"],
                "cannot_access": ["farmer", "agriculture", "business", "entrepreneur", "student", "education", "women"],
            },
        }

        # Find matching occupation key
        occ_key = None
        for key in occupation_access:
            if key in occupation or occupation in key:
                occ_key = key
                break

        if occ_key and scheme_category:
            access_rules = occupation_access[occ_key]

            # Check if scheme category is in cannot_access list
            if any(cat in scheme_category for cat in access_rules["cannot_access"]):
                eligible = False
                reasons.append(
                    f"Scheme targets '{scheme_category}' category - not applicable for {occupation}"
                )
            # Check if scheme category is in can_access list
            elif any(cat in scheme_category for cat in access_rules["can_access"]):
                reasons.append(f"Scheme category '{scheme_category}' is applicable for {occupation}")
            # Category not in either list - use eligibility text analysis
            else:
                text_verdict = analyze_eligibility_text(scheme, occupation)
                if text_verdict == "not_eligible":
                    eligible = False
                    reasons.append(
                        f"Scheme eligibility criteria exclude {occupation} based on scheme description"
                    )
                elif text_verdict == "eligible":
                    reasons.append(f"Scheme is applicable for {occupation} based on eligibility text")
                else:
                    # Default: if no explicit exclusion found, mark as eligible
                    # with a note to verify
                    reasons.append(
                        f"No explicit exclusion found for {occupation} in '{scheme_category}' scheme - "
                        f"eligible but verify official guidelines"
                    )

    # --- STEP 3: Scheme-specific exclusion rules ---
    # These handle known exclusions that text analysis might miss

    # Special handling for PM-SYM (Shram Yogi)
    if eligible and ("shram" in scheme_name.lower() or "pm-sym" in scheme_name.lower()):
        # PM-SYM requires age 18-40 AND unorganized worker status
        if user_age and user_age > 40:
            eligible = False
            reasons.append(f"PM-SYM requires age 18-40, applicant age {user_age} exceeds limit")
        elif occupation and any(occ in occupation for occ in ["government", "private sector", "salaried"]):
            eligible = False
            reasons.append("PM-SYM is exclusively for unorganized sector workers - government/private employees are excluded")

    # Special handling for PMUY (Ujjwala) - women only, BPL only
    if eligible and ("ujjwala" in scheme_name.lower() or "pmuy" in scheme_name.lower()):
        # Must be female
        if occupation and any(occ in occupation for occ in ["man", "male", "government", "business", "private"]):
            eligible = False
            reasons.append("PMUY (Ujjwala) is exclusively for women from BPL families - not applicable")
        # Must be BPL (income check)
        elif user_income and user_income > 100000:
            eligible = False
            reasons.append(f"PMUY requires BPL status (income < Rs 100,000), your income Rs {user_income} exceeds limit")

    # General exclusion rules
    if eligible and occupation:
        exclusion_rules = get_scheme_exclusion_rules()
        scheme_key = scheme_name.lower()

        for rule in exclusion_rules:
            if any(keyword in scheme_key for keyword in rule["scheme_keywords"]):
                if any(occ in occupation for occ in rule["excluded_occupations"]):
                    eligible = False
                    reasons.append(rule["reason"])
                    break

    # --- STEP 4: BPL/Low-income scheme check for salaried persons ---

    if eligible and user_income and max_income:
        if max_income <= 100000 and occupation in ["government", "business", "engineer", "doctor", "lawyer"]:
            eligible = False
            reasons.append("Scheme targets BPL families - not applicable for salaried/professional occupations")

    # Determine final status (no more "Uncertain")
    status = "Eligible" if eligible else "Not Eligible"

    return {
        "scheme_name": scheme_name,
        "status": status,
        "reason": "; ".join(reasons) if reasons else "No specific eligibility criteria found",
        "benefits": scheme.get("metadata", {}).get("benefits", ""),
        "documents_required": "",
        "application_steps": "",
    }


def analyze_eligibility_text(scheme, occupation):
    """
    Analyze the scheme's eligibility text to determine if an occupation
    is explicitly included or excluded.

    Returns: "eligible", "not_eligible", or "unknown"
    """
    eligibility_text = scheme.get("text", "").lower()
    if not eligibility_text:
        return "unknown"

    # Keywords that indicate the scheme is restricted to specific groups
    restriction_indicators = [
        "only for", "restricted to", "exclusively for", "specifically for",
        "available only", "meant for", "designed for", "targeted at",
        "not for", "not applicable", "not eligible", "excluded",
        "should not be", "must not be", "cannot be",
    ]

    # Check for explicit exclusion of the occupation
    exclusion_patterns = [
        "not for " + occupation,
        occupation + " are not eligible",
        occupation + " are not covered",
        "excluding " + occupation,
        "not available for " + occupation,
        "should not be a " + occupation,
        "must not be a " + occupation,
        "cannot be a " + occupation,
    ]

    for pattern in exclusion_patterns:
        if pattern in eligibility_text:
            return "not_eligible"

    # Check for professional exclusion patterns
    professional_exclusions = [
        "professionals like doctors, engineers",
        "professional tax payer",
        "holding any constitutional post",
        "covered under any statutory social security",
        "income tax payee",
    ]

    salaried_keywords = ["government", "salaried", "employed", "private sector", "public sector"]
    if occupation in salaried_keywords:
        for pattern in professional_exclusions:
            if pattern in eligibility_text:
                return "not_eligible"

    # Check for explicit inclusion
    inclusion_patterns = [
        "all citizens", "any indian citizen", "all indian citizens",
        "universal", "open to all", "everyone", "any person",
        "all residents", "general public",
    ]

    for pattern in inclusion_patterns:
        if pattern in eligibility_text:
            return "eligible"

    # Check if occupation is directly mentioned as eligible
    if occupation in eligibility_text:
        return "eligible"

    return "unknown"


def get_scheme_exclusion_rules():
    """
    Returns a list of scheme-specific exclusion rules.
    Each rule defines: scheme keywords, excluded occupations, and reason.
    """
    return [
        {
            "scheme_keywords": ["kisan", "pm-kisan", "pmkisan"],
            "excluded_occupations": ["government", "doctor", "engineer", "lawyer", "teacher", "business"],
            "reason": "PM-KISAN is exclusively for farmers with cultivable land - not eligible for non-farm occupations",
        },
        {
            "scheme_keywords": ["shram", "pm-sym", "shram yogi"],
            "excluded_occupations": ["government", "private sector", "engineer", "doctor", "lawyer", "teacher"],
            "reason": "PM-SYM is for unorganized sector workers only - government/organized sector employees are excluded",
        },
        {
            "scheme_keywords": ["ujjwala", "pmuy"],
            "excluded_occupations": ["man", "male"],
            "reason": "Ujjwala Yojana is exclusively for women from BPL families",
        },
        {
            "scheme_keywords": ["sukanya"],
            "excluded_occupations": ["man", "male"],
            "reason": "Sukanya Samriddhi Yojana is for girl children only",
        },
        {
            "scheme_keywords": ["nps", "swavalamban", "national pension"],
            "excluded_occupations": ["government"],
            "reason": "Government employees already have statutory pension coverage - NPS Swavalamban is for unorganized sector",
        },
        {
            "scheme_keywords": ["mudra", "pmmi"],
            "excluded_occupations": [],
            "reason": "",
        },
        {
            "scheme_keywords": ["jan arogya", "pmjay", "ayushman"],
            "excluded_occupations": ["government"],
            "reason": "Ayushman Bharat targets deprived families - government employees typically have CGHS/ESI coverage",
        },
    ]


def check_eligibility_llm(profile, scheme_text):
    """
    Check eligibility using local LLM (Ollama + Mistral).
    Falls back to rule-based if Ollama is not running.

    This is OPTIONAL - the system works with rule-based logic alone.
    """
    try:
        # Check if Ollama is running
        response = http_requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if response.status_code != 200:
            print("Ollama not running, using rule-based logic")
            return None
    except http_requests.ConnectionError:
        print("Ollama not available, using rule-based logic")
        return None

    # Build prompt for the LLM
    prompt = f"""You are a government scheme eligibility expert. Analyze if the citizen is eligible for this scheme.

CITIZEN PROFILE:
- Age: {profile.get('age', 'Not specified')}
- Annual Income: Rs {profile.get('income', 'Not specified')}
- State: {profile.get('state', 'Not specified')}
- Occupation: {profile.get('occupation', 'Not specified')}
- Category: {profile.get('category', 'Not specified')}

SCHEME DETAILS:
{scheme_text}

Determine eligibility. Respond in this exact JSON format:
{{"status": "Eligible" or "Not Eligible" or "Uncertain", "reason": "brief explanation"}}"""

    try:
        response = http_requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 200}
            },
            timeout=30
        )
        result = response.json()
        llm_output = result.get("response", "")

        # Try to extract JSON from LLM response
        json_match = re.search(r'\{[^}]+\}', llm_output)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"LLM eligibility check failed: {e}")

    return None


def analyze_eligibility(profile, retrieved_schemes):
    """
    Main function: analyze eligibility for all retrieved schemes.

    profile: dict with age, income, state, occupation, category
    retrieved_schemes: list of scheme dicts from retriever

    Returns: list of eligibility results
    """
    results = []

    for scheme in retrieved_schemes:
        # Rule-based check (always runs, always returns Eligible or Not Eligible)
        result = check_eligibility_rule_based(profile, scheme)

        # Load full scheme details from JSON for benefits, docs, steps
        scheme_details = load_scheme_details(result["scheme_name"])
        if scheme_details:
            result["benefits"] = scheme_details.get("benefits", "Not available")
            result["documents_required"] = scheme_details.get("documents_required", "Not available")
            result["application_steps"] = scheme_details.get("application_steps", "Not available")

        results.append(result)

    # Sort: Eligible first, then Not Eligible
    status_order = {"Eligible": 0, "Not Eligible": 1}
    results.sort(key=lambda x: status_order.get(x["status"], 2))

    return results


def load_scheme_details(scheme_name):
    """
    Load full scheme details from the JSON file.
    """
    filepath = os.path.join(SCHEMES_DIR, "all_schemes.json")
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    for scheme in schemes:
        if scheme.get("name", "").lower() == scheme_name.lower():
            return scheme

    return None


if __name__ == "__main__":
    # Test eligibility engine
    test_profile = {
        "age": 45,
        "income": 150000,
        "state": "Gujarat",
        "occupation": "Farmer",
        "category": "General",
    }

    # Simulate retrieved schemes
    test_schemes = [
        {
            "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "text": "Small and marginal farmer families with cultivable land holding up to 2 hectares. Age above 18 years. Income less than Rs 2,00,000 per annum.",
            "metadata": {
                "min_age": 18,
                "max_income": 200000,
                "state": "All India",
                "category": "Farmer",
            }
        },
        {
            "scheme_name": "Sukanya Samriddhi Yojana (SSY)",
            "text": "Girl child below 10 years of age. Must be an Indian citizen.",
            "metadata": {
                "max_age": 10,
                "state": "All India",
                "category": "Savings",
            }
        },
    ]

    results = analyze_eligibility(test_profile, test_schemes)
    for r in results:
        print(json.dumps(r, indent=2))
