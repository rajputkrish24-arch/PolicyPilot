import requests
import json

# Test profile
profile = {
    "age": 45,
    "income": 145000,
    "state": "Maharashtra",
    "occupation": "Government Employee",
    "category": "General"
}

print("Testing PolicyPilot AI...")
print("=" * 50)

response = requests.post("http://127.0.0.1:8000/api/analyze", json=profile)
data = response.json()

print(f"Status: {response.status_code}")
print(f"AI Enabled: {data.get('ai_enabled')}")
print(f"AI Summary: {data.get('ai_summary') or 'No summary'}")
print()

print("ELIGIBLE SCHEMES:")
for s in data.get('eligible_schemes', []):
    if s['status'] == 'Eligible':
        ai_tip = s.get('ai_tip', 'No AI tip')
        print(f"  ✓ {s['scheme_name']}")
        print(f"    AI Tip: {ai_tip[:80]}...")
        print()

print("CONFLICTS:")
for c in data.get('conflicts', []):
    print(f"  ! {c.get('conflict_type')}")
    print(f"    Priority: {c.get('priority')}")
    print(f"    AI Explanation: {c.get('ai_explanation') or 'N/A'}")
    print(f"    AI Recommendation: {c.get('ai_recommendation') or 'N/A'}")
    print()
