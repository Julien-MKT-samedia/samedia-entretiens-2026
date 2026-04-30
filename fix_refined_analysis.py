#!/usr/bin/env python3
"""
Rebuild refined_analysis from correct scoreDetails
Ensure profil_marche never = 0 (min 1)
"""

import json

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

for key, cand in candidates.items():
    score_details = cand.get('scoreDetails', {})
    total = sum(score_details.values())

    # Ensure profil_marche is never 0 (config [1,2])
    if score_details.get('profil_marche') == 0:
        score_details['profil_marche'] = 1
        total = sum(score_details.values())
        print(f"⚠️  {key}: profil_marche fixed 0→1")

    # Verdict logic
    if total >= 7:
        verdict = 'GO'
    elif total >= 4:
        verdict = 'À ÉTUDIER'
    else:
        verdict = 'NO GO'

    # Rebuild refined_analysis
    cand['refined_analysis'] = {
        'total_score': total,
        'verdict': verdict,
        'scoreDetails': score_details.copy(),
    }

with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✓ refined_analysis rebuilt for all {len(candidates)} candidates")
print(f"✓ profil_marche violations fixed")
print(f"✓ data.json saved")
