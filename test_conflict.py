import requests
import json

# Profile that triggers income conflicts
profile = {
    "age": 45,
    "income": 145000,
    "state": "Maharashtra",
    "occupation": "Government Employee",
    "category": "General"
}

print("Testing AI Conflict Resolution...")
print("=" * 60)

response = requests.post("http://127.0.0.1:8000/api/analyze", json=profile)
data = response.json()

print(f"✓ AI Enabled: {data.get('ai_enabled')}")
print(f"✓ AI Summary: {data.get('ai_summary') or 'N/A'}")
print()

print("CONFLICTS DETECTED:")
for c in data.get('conflicts', []):
    if c.get('conflict') and c.get('conflict_type') != 'none':
        print(f"\n  🚨 {c.get('conflict_type')}")
        print(f"     Priority: {c.get('priority', 'Medium')}")
        print(f"     Schemes: {c.get('schemes_involved')}")
        print(f"     AI Explanation: {c.get('ai_explanation') or 'N/A'}")
        print(f"     AI Recommendation: {c.get('ai_recommendation') or 'N/A'}")

print("\n" + "=" * 60)
print("If you see 'AI Explanation' and 'AI Recommendation', it's working!")
