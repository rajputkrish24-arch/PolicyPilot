"""
conflict.py - Conflict Detector for PolicyPilot

Detects conflicts between scheme eligibility rules when a citizen
qualifies for multiple schemes. Uses simple rule comparisons.

Conflict types detected:
- Income threshold conflicts (scheme A says income < X, scheme B says income < Y)
- Age range conflicts
- Mutual exclusivity (some schemes cannot be combined)
- Benefit overlap (same benefit from multiple schemes)

Output format:
{
    "conflict": true/false,
    "message": "...",
    "schemes_involved": ["...", "..."],
    "conflict_type": "..."
}
"""

import json
import os

# Paths
SCHEMES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes")


def detect_income_conflicts(eligible_results, profile):
    """
    Detect if income thresholds across eligible schemes create conflicts.
    E.g., one scheme requires income < 1.5L, another < 3L - both may apply
    but the stricter one might exclude the applicant from the other's benefits.
    """
    conflicts = []

    # Collect income thresholds from eligible/uncertain schemes
    income_limits = []
    for result in eligible_results:
        if result["status"] in ["Eligible", "Uncertain"]:
            scheme_details = load_scheme_details(result["scheme_name"])
            if scheme_details and scheme_details.get("max_income"):
                income_limits.append({
                    "scheme": result["scheme_name"],
                    "max_income": scheme_details["max_income"],
                })

    # Check if income limits vary significantly
    if len(income_limits) >= 2:
        incomes = [item["max_income"] for item in income_limits]
        min_limit = min(incomes)
        max_limit = max(incomes)

        # If the gap between limits is > 2x, flag as potential conflict
        if max_limit > min_limit * 2:
            lower_schemes = [i["scheme"] for i in income_limits if i["max_income"] == min_limit]
            higher_schemes = [i["scheme"] for i in income_limits if i["max_income"] == max_limit]

            conflicts.append({
                "conflict": True,
                "message": (
                    f"Income thresholds vary significantly across schemes. "
                    f"Schemes {lower_schemes} require income < Rs {min_limit:,}, "
                    f"while {higher_schemes} allow up to Rs {max_limit:,}. "
                    f"Verify income eligibility carefully."
                ),
                "schemes_involved": [i["scheme"] for i in income_limits],
                "conflict_type": "income_threshold",
            })

    return conflicts


def detect_age_conflicts(eligible_results, profile):
    """
    Detect if age ranges across eligible schemes create conflicts.
    """
    conflicts = []

    age_ranges = []
    for result in eligible_results:
        if result["status"] in ["Eligible", "Uncertain"]:
            scheme_details = load_scheme_details(result["scheme_name"])
            if scheme_details:
                min_age = scheme_details.get("min_age")
                max_age = scheme_details.get("max_age")
                if min_age is not None or max_age is not None:
                    age_ranges.append({
                        "scheme": result["scheme_name"],
                        "min_age": min_age or 0,
                        "max_age": max_age or 120,
                    })

    # Check for age range conflicts
    if len(age_ranges) >= 2:
        for i in range(len(age_ranges)):
            for j in range(i + 1, len(age_ranges)):
                a = age_ranges[i]
                b = age_ranges[j]

                # Check if age ranges don't overlap
                if a["max_age"] < b["min_age"] or b["max_age"] < a["min_age"]:
                    conflicts.append({
                        "conflict": True,
                        "message": (
                            f"Age ranges do not overlap between "
                            f"'{a['scheme']}' (age {a['min_age']}-{a['max_age']}) and "
                            f"'{b['scheme']}' (age {b['min_age']}-{b['max_age']}). "
                            f"Applicant age {profile.get('age')} may not qualify for both."
                        ),
                        "schemes_involved": [a["scheme"], b["scheme"]],
                        "conflict_type": "age_range",
                    })

    return conflicts


def detect_mutual_exclusivity(eligible_results):
    """
    Detect mutually exclusive schemes.
    Some government schemes cannot be availed simultaneously.
    """
    conflicts = []

    # Known mutually exclusive scheme pairs
    exclusive_pairs = [
        ("PM-SYM", "NPS Swavalamban"),  # Both are pension schemes for unorganized sector
    ]

    eligible_names = [
        r["scheme_name"] for r in eligible_results
        if r["status"] in ["Eligible", "Uncertain"]
    ]

    for pair in exclusive_pairs:
        matching = [name for name in eligible_names if any(p in name for p in pair)]
        if len(matching) >= 2:
            conflicts.append({
                "conflict": True,
                "message": (
                    f"Schemes '{matching[0]}' and '{matching[1]}' may be mutually exclusive. "
                    f"Both provide similar benefits and may not be availed together. "
                    f"Check official guidelines."
                ),
                "schemes_involved": matching,
                "conflict_type": "mutual_exclusivity",
            })

    return conflicts


def detect_benefit_overlap(eligible_results):
    """
    Detect if multiple eligible schemes provide similar benefits.
    This is informational - not necessarily a conflict.
    """
    conflicts = []
    benefit_keywords = {
        "pension": [],
        "insurance": [],
        "subsidy": [],
        "loan": [],
        "housing": [],
        "health": [],
    }

    for result in eligible_results:
        if result["status"] in ["Eligible", "Uncertain"]:
            benefits = result.get("benefits", "").lower()
            scheme_name = result["scheme_name"]

            for keyword in benefit_keywords:
                if keyword in benefits:
                    benefit_keywords[keyword].append(scheme_name)

    for keyword, schemes in benefit_keywords.items():
        if len(schemes) > 1:
            conflicts.append({
                "conflict": False,  # Informational, not a true conflict
                "message": (
                    f"Multiple schemes provide {keyword} benefits: {schemes}. "
                    f"Verify if these can be combined or if only one can be availed."
                ),
                "schemes_involved": schemes,
                "conflict_type": "benefit_overlap",
            })

    return conflicts


def detect_conflicts(eligible_results, profile):
    """
    Main function: detect all types of conflicts across eligible schemes.
    Rule-based detection + optional AI enhancement.

    eligible_results: list of eligibility result dicts
    profile: citizen profile dict

    Returns: list of conflict dicts (with optional AI fields)
    """
    all_conflicts = []

    # Run all rule-based conflict detectors
    all_conflicts.extend(detect_income_conflicts(eligible_results, profile))
    all_conflicts.extend(detect_age_conflicts(eligible_results, profile))
    all_conflicts.extend(detect_mutual_exclusivity(eligible_results))
    all_conflicts.extend(detect_benefit_overlap(eligible_results))

    # If no conflicts found, add a clean status
    if not all_conflicts:
        all_conflicts.append({
            "conflict": False,
            "message": "No conflicts detected between eligible schemes.",
            "schemes_involved": [],
            "conflict_type": "none",
        })

    # Try AI enhancement
    try:
        from .ai_conflict_analyzer import analyze_conflicts_with_llm
        ai_result = analyze_conflicts_with_llm(all_conflicts, profile)
        if ai_result and ai_result.get("ai_enhanced"):
            # Return AI-enhanced conflicts as a flat list
            return ai_result.get("conflicts", all_conflicts)
    except Exception as e:
        print(f"AI conflict enhancement skipped: {e}")

    return all_conflicts


def load_scheme_details(scheme_name):
    """
    Load full scheme details from JSON.
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
    # Test conflict detector
    test_results = [
        {
            "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "status": "Eligible",
            "reason": "Age and income meet requirements",
            "benefits": "Rs 6,000 per year in three installments",
        },
        {
            "scheme_name": "Pradhan Mantri Awas Yojana (PMAY)",
            "status": "Eligible",
            "reason": "Income within EWS/LIG limits",
            "benefits": "Subsidy of Rs 2.67 lakh on home loan interest",
        },
        {
            "scheme_name": "Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM)",
            "status": "Eligible",
            "reason": "Unorganized worker, income below threshold",
            "benefits": "Monthly pension of Rs 3,000 after age 60",
        },
    ]

    test_profile = {"age": 45, "income": 150000, "state": "Gujarat", "occupation": "Farmer"}

    conflicts = detect_conflicts(test_results, test_profile)
    for c in conflicts:
        print(json.dumps(c, indent=2))
