#!/usr/bin/env python3
"""
Re-score tous 66 candidats avec logique stricte generate_data.py
"""

import os
import json
import subprocess
import re

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

# Scoring rules — strict keyword matching
SCORING_RULES = {
    'langues': {
        2: [r'\bnative\b', r'\bC[12]\b', r'\bfluent in english\b', r'\bbilingual\b', r'\benglish native\b'],
        1: [r'\bB[12]\b', r'\bfluent\b', r'\bproficient\b', r'\bTOEFL\b', r'\bIELTS\b', r'\b(5\.5|6\.5|7|8)[.\d]*\b'],
    },
    'vente': {
        2: [r'\bB2B\b', r'\bsales manager\b', r'\bbusiness development\b', r'\baccount executive\b', r'\bsales director\b'],
        1: [r'\bsales\b', r'\bcommercial\b', r'\bclient-facing\b', r'\bcustomer\b', r'\bselling\b'],
    },
    'prospection': {
        2: [r'\bprospect', r'\bfield\b', r'\bterritorialb', r'\bhunt', r'\bnew business\b', r'\bpresales\b'],
        1: [r'\bsupport\b', r'\bback.?office\b', r'\badmin\b', r'\binternal\b'],
    },
    'usa_exp': {
        2: [r'\bUSA\b', r'\bUnited States\b', r'\bNew York\b', r'\bCalifornia\b', r'\bworked.*USA\b', r'\blived.*USA\b'],
        1: [r'\bUK\b', r'\bCanada\b', r'\bAustralia\b', r'\bIreland\b', r'\bSingapore\b'],
    },
    'profil_marche': {
        2: [r'\bconstruction\b', r'\bmining\b', r'\bdrilling\b', r'\bconcrete\b', r'\bBTP\b', r'\bmachinery\b', r'\bexcavation\b'],
        1: [],  # Default to 1 (never 0)
    },
    'ancrage_culturel': {
        2: [r'\bBritish\b', r'\bAmerican\b', r'\bAustralian\b', r'\bCanadian\b', r'\bIrish\b', r'\bnative english\b'],
        1: [r'\binternational\b', r'\bexpat\b', r'\bmultinational\b', r'\bglobal\b', r'\bcross.?cultural\b'],
    },
}

def extract_cv_text(pdf_path):
    """Extract text from PDF CV."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else ""
    except:
        return ""

def score_criterion(text, criterion):
    """Score a criterion (0, 1, or 2) based on text content."""

    text_lower = text.lower()
    rules = SCORING_RULES.get(criterion, {})

    # Check score 2 first
    for pattern in rules.get(2, []):
        if re.search(pattern, text_lower, re.IGNORECASE):
            return 2

    # Check score 1
    for pattern in rules.get(1, []):
        if re.search(pattern, text_lower, re.IGNORECASE):
            return 1

    # Special case: profil_marche defaults to 1 if nothing found
    if criterion == 'profil_marche':
        return 1

    # Default: 0
    return 0

def calculate_matching_score(score_details):
    """Sum scoreDetails values."""
    return sum(score_details.values())

def assign_tier(score):
    """Assign tier based on score."""
    if score >= 7:
        return "Tier1"
    elif 4 <= score < 7:
        return "Tier2"
    else:
        return "Tier3"

def main():
    print("\n" + "="*80)
    print("RE-SCORING ALL 66 CANDIDATES")
    print("="*80 + "\n")

    # Load current data.json
    with open(DATA_JSON) as f:
        data = json.load(f)

    candidates = data['candidates']
    scores_updated = 0
    scores_changed = 0

    # Sort candidates by key (01, 02, ..., 66)
    sorted_keys = sorted(candidates.keys(), key=lambda k: int(k.split('-')[0]))

    for cand_key in sorted_keys:
        cand = candidates[cand_key]

        # Get CV file path
        cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
        cv_path = os.path.join(CV_DIR, cv_file) if cv_file else None

        if not cv_path or not os.path.exists(cv_path):
            print(f"⚠️  {cand_key:30} SKIP (CV not found)")
            continue

        # Extract text
        text = extract_cv_text(cv_path)

        if not text:
            print(f"⚠️  {cand_key:30} SKIP (PDF extraction failed)")
            continue

        # Score all criteria
        old_scores = cand.get('scoreDetails', {})
        new_scores = {
            'langues': score_criterion(text, 'langues'),
            'vente': score_criterion(text, 'vente'),
            'prospection': score_criterion(text, 'prospection'),
            'usa_exp': score_criterion(text, 'usa_exp'),
            'profil_marche': score_criterion(text, 'profil_marche'),
            'ancrage_culturel': score_criterion(text, 'ancrage_culturel'),
        }

        new_total = calculate_matching_score(new_scores)
        old_total = cand.get('matchingScore', 0)

        # Update data
        cand['scoreDetails'] = new_scores
        cand['matchingScore'] = new_total
        cand['tier'] = assign_tier(new_total)

        scores_updated += 1

        if new_total != old_total:
            scores_changed += 1
            status = "✓" if new_total > old_total else "✗" if new_total < old_total else "="
            print(f"{status} {cand_key:30} {old_total} → {new_total} ({cand.get('tier')})")
        else:
            print(f"  {cand_key:30} {new_total} (unchanged)")

    # Assign ranks (top 15)
    ranked = sorted(
        [(k, candidates[k]['matchingScore']) for k in sorted_keys],
        key=lambda x: -x[1]
    )

    for idx, (cand_key, score) in enumerate(ranked[:15]):
        candidates[cand_key]['rank'] = idx + 1

    for cand_key in sorted_keys:
        if candidates[cand_key]['rank'] == 0:  # Not yet ranked, so >15
            candidates[cand_key]['rank'] = 0

    # Update metadata
    tier_dist = {'Tier1': 0, 'Tier2': 0, 'Tier3': 0}
    for cand in candidates.values():
        tier = cand.get('tier', 'Tier3')
        if isinstance(tier, int):
            tier = 'Tier3'
        tier_dist[tier] = tier_dist.get(tier, 0) + 1

    data['metadata']['criteria_count'] = 6
    data['metadata']['tier_distribution'] = tier_dist

    # Save updated data.json
    with open(DATA_JSON, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n" + "="*80)
    print(f"✓ {scores_updated} candidates scored")
    print(f"✓ {scores_changed} scores changed")
    print(f"✓ Tier distribution: Tier1={tier_dist['Tier1']} Tier2={tier_dist['Tier2']} Tier3={tier_dist['Tier3']}")
    print(f"✓ Top 15 ranked")
    print(f"✓ data.json updated")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
