#!/usr/bin/env python3
"""Recalculate ranking after score changes"""

import json

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

# Sort by matchingScore descending
sorted_cands = sorted(candidates.items(), key=lambda x: -x[1]['matchingScore'])

# Assign ranks: 1-15 for top 15, 0 for rest
for idx, (key, cand) in enumerate(sorted_cands):
    if idx < 15:
        cand['rank'] = idx + 1
    else:
        cand['rank'] = 0

with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "="*100)
print("RANKING RECALCULATED")
print("="*100 + "\n")

print("Top 15:")
for idx, (key, cand) in enumerate(sorted_cands[:15]):
    print(f"  {idx+1}. {cand['name']:30} {cand['matchingScore']}/12")

print(f"\n✓ Rankings fixed")
print(f"✓ data.json saved")
print("=" * 100 + "\n")
