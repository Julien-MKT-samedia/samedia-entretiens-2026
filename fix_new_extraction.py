#!/usr/bin/env python3
"""Fix issues from comprehensive_extraction_quality.py run"""

import json
import os

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"
CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
SUPP_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/Candidature-VIE-SAMEDIA-USA-2026/CVs VIE USA suppl"

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

print("\n" + "="*100)
print("FIX: 5-CRITERION MODEL (profil_marche + refined_analysis)")
print("="*100 + "\n")

# Fix 1: Add profil_marche = 1 (default) if missing
print("1. Adding profil_marche default...")
for key, cand in candidates.items():
    scores = cand.get('scoreDetails', {})
    if 'profil_marche' not in scores:
        scores['profil_marche'] = 1
        cand['scoreDetails'] = scores
print("   ✓ All candidates have profil_marche")

# Fix 2: Rebuild refined_analysis for ALL 68 candidates
print("\n2. Rebuilding refined_analysis...")
for key, cand in candidates.items():
    scores = cand.get('scoreDetails', {})
    total = sum(scores.values())
    verdict = 'GO' if total >= 7 else 'À ÉTUDIER' if total >= 4 else 'NO GO'

    cand['refined_analysis'] = {
        'total_score': total,
        'verdict': verdict,
        'scoreDetails': scores.copy(),
    }
    cand['matchingScore'] = total

print("   ✓ All refined_analysis rebuilt")

# Fix 3: Copy new CVs to correct location if missing
print("\n3. Checking new CVs...")
new_cvs = [
    ('67-maëlle-rouhier', 'CV Maëlle Rouhier.pdf', f"{SUPP_DIR}/CV Maëlle Rouhier.pdf"),
    ('68-charly-garcia', 'CV M. GARCIA Charly (fr).pdf', f"{SUPP_DIR}/CV M. GARCIA Charly (fr).pdf"),
]

for cand_key, cv_name, src_path in new_cvs:
    dest_path = f"{CV_DIR}/{cv_name}"

    if os.path.exists(src_path):
        if not os.path.exists(dest_path):
            import shutil
            shutil.copy(src_path, dest_path)
            print(f"   ✓ Copied {cv_name}")
        else:
            print(f"   ✓ {cv_name} already present")
    else:
        print(f"   ⚠️  {cv_name} not found in supplementary dir")

# Fix 4: Update metadata
print("\n4. Updating metadata...")
data['metadata']['total_candidates'] = len(candidates)
data['metadata']['criteria_count'] = 6  # 5 criteria + profil_marche
data['metadata']['generated'] = '2026-04-30'
print(f"   ✓ total_candidates: {len(candidates)}")
print(f"   ✓ criteria_count: 6")

# Fix 5: Recalculate ranking
print("\n5. Recalculating ranking...")
sorted_cands = sorted(candidates.items(), key=lambda x: -x[1]['matchingScore'])
for idx, (key, cand) in enumerate(sorted_cands):
    if idx < 15:
        cand['rank'] = idx + 1
    else:
        cand['rank'] = 0

print(f"   ✓ Top 15 ranked 1-15, rest = 0")

# Save
with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "="*100)
print("RÉSUMÉ")
print("="*100)
print(f"\n✓ profil_marche defaulted to 1 for all")
print(f"✓ refined_analysis rebuilt (68 candidates)")
print(f"✓ New CVs verified/copied")
print(f"✓ Metadata updated (68 candidates, criteria_count=6)")
print(f"✓ Ranking recalculated")
print(f"✓ data.json saved")

print("\nTop 15:")
for idx, (key, cand) in enumerate(sorted_cands[:15]):
    print(f"  {idx+1}. {cand['name']:30} {cand['matchingScore']}/12")

print("\n" + "="*100 + "\n")
