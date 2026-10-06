"""
ai_conflict_analyzer.py - AI-enhanced conflict analysis

Uses Ollama (local LLM) to provide intelligent conflict analysis
beyond simple rule-based detection.
"""

import json
import os
import re
import requests
from typing import List, Dict

# Ollama configuration - load from environment
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


def is_ollama_available() -> bool:
    """Check if Ollama server is running and model is loaded."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            return any(OLLAMA_MODEL in name for name in model_names)
        return False
    except:
        return False


def analyze_conflicts_with_llm(rule_conflicts: List[Dict], profile: Dict) -> Dict:
    """
    Analyze rule-based conflicts using AI for deeper insights.
    
    Args:
        rule_conflicts: List of conflicts detected by rule-based system
        profile: Citizen profile dictionary
    
    Returns:
        AI-enhanced conflict analysis with priorities and recommendations
    """
    
    if not is_ollama_available():
        print("Ollama not available for conflict analysis, using rule-based")
        return fallback_analysis(rule_conflicts)
    
    prompt = build_conflict_analysis_prompt(rule_conflicts, profile)
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 600
                }
            },
            timeout=60
        )
        
        result = response.json()
        ai_response = result.get("response", "")
        
        return parse_ai_response(ai_response, rule_conflicts)
        
    except Exception as e:
        print(f"AI conflict analysis failed: {e}")
        return fallback_analysis(rule_conflicts)


def build_conflict_analysis_prompt(rule_conflicts: List[Dict], profile: Dict) -> str:
    """Build comprehensive prompt for AI conflict analysis."""
    
    profile_text = f"""CITIZEN PROFILE:
- Age: {profile.get('age', 'Not specified')}
- Annual Income: Rs {profile.get('income', 'Not specified')}
- State: {profile.get('state', 'Not specified')}
- Occupation: {profile.get('occupation', 'Not specified')}
- Category: {profile.get('category', 'Not specified')}"""
    
    conflicts_text = "DETECTED CONFLICTS:\n"
    for i, conflict in enumerate(rule_conflicts, 1):
        conflicts_text += f"""
{i}. Type: {conflict.get('conflict_type', 'Unknown')}
   Message: {conflict.get('message', '')}
   Schemes: {conflict.get('schemes_involved', [])}
   Is Real Conflict: {conflict.get('conflict', False)}"""
    
    return f"""You are an expert Indian government scheme advisor. Analyze these conflicts for a citizen.

{profile_text}

{conflicts_text}

For each conflict, determine:
1. Is this a REAL conflict or just different target groups?
2. Priority: High, Medium, or Low
3. What action should the citizen take?
4. Explain in simple Hindi-English mix (Hinglish) that common citizens understand

Respond ONLY in this JSON format, no other text:
{{
  "conflicts": [
    {{
      "type": "income_threshold",
      "priority": "Low",
      "is_real_conflict": false,
      "explanation": "Clear explanation",
      "recommendation": "Specific action"
    }}
  ],
  "summary": "Overall assessment in 1-2 sentences"
}}"""


def parse_ai_response(ai_response: str, original_conflicts: List[Dict]) -> Dict:
    """Parse AI response and merge with original conflict data."""
    
    try:
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            ai_analysis = json.loads(json_match.group())
            
            enhanced_conflicts = []
            for orig_conflict in original_conflicts:
                ai_insight = None
                for ai_conflict in ai_analysis.get('conflicts', []):
                    if ai_conflict.get('type') == orig_conflict.get('conflict_type'):
                        ai_insight = ai_conflict
                        break
                
                enhanced = orig_conflict.copy()
                if ai_insight:
                    enhanced.update({
                        'priority': ai_insight.get('priority', 'Medium'),
                        'is_real_conflict': ai_insight.get('is_real_conflict', True),
                        'ai_explanation': ai_insight.get('explanation', ''),
                        'ai_recommendation': ai_insight.get('recommendation', '')
                    })
                else:
                    enhanced.update({
                        'priority': 'Medium',
                        'is_real_conflict': orig_conflict.get('conflict', False),
                        'ai_explanation': '',
                        'ai_recommendation': ''
                    })
                
                enhanced_conflicts.append(enhanced)
            
            return {
                'conflicts': enhanced_conflicts,
                'summary': ai_analysis.get('summary', 'AI conflict analysis completed.'),
                'ai_enhanced': True
            }
    
    except Exception as e:
        print(f"Failed to parse AI conflict response: {e}")
    
    return fallback_analysis(original_conflicts)


def fallback_analysis(rule_conflicts: List[Dict]) -> Dict:
    """Fallback when AI is not available."""
    
    enhanced_conflicts = []
    for conflict in rule_conflicts:
        enhanced = conflict.copy()
        enhanced.update({
            'priority': 'Medium',
            'is_real_conflict': conflict.get('conflict', False),
            'ai_explanation': '',
            'ai_recommendation': ''
        })
        enhanced_conflicts.append(enhanced)
    
    return {
        'conflicts': enhanced_conflicts,
        'summary': 'Rule-based conflict detection completed.',
        'ai_enhanced': False
    }


def enhance_eligibility_with_ai(eligibility_results: List[Dict], profile: Dict) -> List[Dict]:
    """
    Use AI to add reasoning and recommendations to eligibility results.
    Only processes eligible schemes for better advice.
    """
    if not is_ollama_available():
        print("Ollama not available for eligibility enhancement")
        return eligibility_results
    
    eligible_schemes = [r for r in eligibility_results if r.get("status") == "Eligible"]
    if not eligible_schemes:
        return eligibility_results
    
    scheme_names = [r.get("scheme_name", "") for r in eligible_schemes]
    
    prompt = f"""You are an expert Indian government scheme advisor. A citizen has been found eligible for these schemes:

Profile: Age {profile.get('age')}, Income Rs {profile.get('income')}, Occupation: {profile.get('occupation')}, State: {profile.get('state')}

Eligible Schemes: {', '.join(scheme_names)}

For each scheme, provide:
1. A brief tip on how to apply (1 line)
2. One important thing to remember

Respond ONLY in JSON:
{{
  "tips": {{
    "scheme_name": "tip text"
  }},
  "overall_advice": "1-2 sentence overall advice for this citizen"
}}"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 400
                }
            },
            timeout=45
        )
        
        result = response.json()
        ai_response = result.get("response", "")
        
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            ai_data = json.loads(json_match.group())
            tips = ai_data.get("tips", {})
            overall_advice = ai_data.get("overall_advice", "")
            
            # Add AI tips to eligible results
            for result in eligibility_results:
                if result.get("status") == "Eligible":
                    scheme_name = result.get("scheme_name", "")
                    # Try matching with fuzzy key lookup
                    tip = ""
                    for key, value in tips.items():
                        if any(word in scheme_name.lower() for word in key.lower().split()):
                            tip = value
                            break
                        if any(word in key.lower() for word in scheme_name.lower().split()):
                            tip = value
                            break
                    
                    result["ai_tip"] = tip
                    result["ai_overall_advice"] = overall_advice
                    result["ai_enhanced"] = True
                else:
                    result["ai_tip"] = ""
                    result["ai_overall_advice"] = ""
                    result["ai_enhanced"] = False
            
            return eligibility_results
    
    except Exception as e:
        print(f"AI eligibility enhancement failed: {e}")
    
    return eligibility_results


if __name__ == "__main__":
    test_conflicts = [
        {
            "conflict": True,
            "message": "Income thresholds vary significantly across schemes.",
            "schemes_involved": ["PM-KISAN", "PMSBY"],
            "conflict_type": "income_threshold"
        }
    ]
    
    test_profile = {
        "age": 45,
        "income": 145000,
        "state": "Maharashtra",
        "occupation": "Government Employee",
        "category": "General"
    }
    
    result = analyze_conflicts_with_llm(test_conflicts, test_profile)
    print(json.dumps(result, indent=2))
