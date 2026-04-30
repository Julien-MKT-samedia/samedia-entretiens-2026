#!/usr/bin/env python3
"""
Étape 3: Cleanup data.json — metadata + nulls
"""

import json

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def main():
    print("\n" + "="*80)
    print("ÉTAPE 3: CLEANUP DATA.JSON")
    print("="*80 + "\n")

    with open(DATA_JSON) as f:
        data = json.load(f)

    candidates = data['candidates']

    # Cleanup
    warning_fixes = 0
    ldm_fixes = 0
    refined_analysis_fixes = 0

    for cand_key, cand in candidates.items():
        # Fix warnings: null → []
        if cand.get('warnings') is None:
            cand['warnings'] = []
            warning_fixes += 1

        # Fix ldmFile: ensure null consistency
        if cand.get('ldmFile') is None:
            pass  # OK
        elif cand.get('ldmFile') == '':
            cand['ldmFile'] = None
            ldm_fixes += 1

        # Fix refined_analysis if missing/broken
        if not cand.get('refined_analysis'):
            cand['refined_analysis'] = {
                'total_score': cand.get('matchingScore', 0),
                'verdict': 'À évaluer',
            }
            refined_analysis_fixes += 1

    # Metadata
    tier_dist = {'Tier1': 0, 'Tier2': 0, 'Tier3': 0}
    for cand in candidates.values():
        tier = cand.get('tier', 'Tier3')
        if isinstance(tier, int):
            tier = 'Tier3'
        tier_dist[tier] = tier_dist.get(tier, 0) + 1

    data['metadata'] = {
        'total_candidates': len(candidates),
        'tier_distribution': tier_dist,
        'criteria_count': 6,
        'scoring_system': data.get('metadata', {}).get('scoring_system', {}),
    }

    # Save
    with open(DATA_JSON, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✓ warnings null→[]: {warning_fixes}")
    print(f"✓ ldmFile fixes: {ldm_fixes}")
    print(f"✓ refined_analysis fixes: {refined_analysis_fixes}")
    print(f"✓ Metadata updated: total={len(candidates)}, criteria=6")
    print(f"✓ Tier distribution: {tier_dist}")
    print(f"✓ data.json saved")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
