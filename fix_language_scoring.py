#!/usr/bin/env python3
"""
Fix language scoring based on extracted levels
C1/C2/NATIVE/BILINGUAL = 2
B1/B2/FLUENT/PROFESSIONAL/ADVANCED = 1 (conservative) or 2 (if clearly advanced)
Basic/INTERMEDIATE = 0 or 1
"""

import json

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def score_english(languages_list):
    """Score English based on extracted level from languages list"""
    if not languages_list:
        return 0

    # Find English entry
    for lang in languages_list:
        if 'english' in lang.lower():
            lang_lower = lang.lower()

            # C1/C2 → 2
            if any(x in lang_lower for x in ['c1', 'c2', 'native', 'bilingual']):
                return 2

            # B1/B2/FLUENT/PROFESSIONAL/ADVANCED → 2 (advanced enough for USA context)
            if any(x in lang_lower for x in ['b1', 'b2', 'fluent', 'professional', 'advanced']):
                return 2

            # INTERMEDIATE/BASIC → 0 or 1
            if any(x in lang_lower for x in ['intermediate', 'basic']):
                return 1

            # Plain "English" no level = assume intermediate = 1
            return 1

    return 0

# Load and rescore
with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

print("\n" + "="*100)
print("LANGUAGE SCORING FIX")
print("="*100 + "\n")

changes = 0
for key in sorted(candidates.keys()):
    cand = candidates[key]
    languages = cand.get('languages', [])
    new_score = score_english(languages)
    old_score = cand.get('scoreDetails', {}).get('langues', 0)

    if new_score != old_score:
        print(f"{key:30} {cand.get('name', '?'):30}")
        print(f"  Languages: {languages}")
        print(f"  OLD: {old_score}/2 → NEW: {new_score}/2")

        # Update scoreDetails and total
        cand['scoreDetails']['langues'] = new_score
        total = sum(cand['scoreDetails'].values())
        cand['matchingScore'] = total

        # Update refined_analysis
        verdict = 'GO' if total >= 7 else 'À ÉTUDIER' if total >= 4 else 'NO GO'
        cand['refined_analysis'] = {
            'total_score': total,
            'verdict': verdict,
            'scoreDetails': cand['scoreDetails'].copy(),
        }
        changes += 1

# Save
with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n{'='*100}")
print(f"✓ {changes} candidates' language scores fixed")
print(f"✓ matchingScores recalculated")
print(f"✓ refined_analysis updated")
print(f"✓ data.json saved")
print(f"{'='*100}\n")
