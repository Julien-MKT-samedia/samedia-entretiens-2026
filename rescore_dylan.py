#!/usr/bin/env python3
"""
Rescore Dylan Dourlen with extracted data via OCR
"""

import json
import re

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def score_criteria(cand_data):
    """Score 6 criteria, each 0-2."""
    text = " ".join([
        " ".join(cand_data.get('education', [])),
        " ".join(cand_data.get('experiences', [])),
        " ".join(cand_data.get('languages', [])),
        " ".join(cand_data.get('skills', [])),
    ]).lower()

    scores = {}

    # 1. Langues
    text_lang = " ".join(cand_data.get('languages', [])).lower()
    if any(x in text_lang for x in ['c1', 'c2', 'native', 'bilingual']):
        scores['langues'] = 2
    elif any(x in text_lang for x in ['b1', 'b2', 'fluent', 'professional']):
        scores['langues'] = 1
    else:
        scores['langues'] = 0

    # 2. Vente
    if any(x in text for x in ['sales manager', 'business development', 'account executive', 'b2b']):
        scores['vente'] = 2
    elif any(x in text for x in ['sales', 'commercial', 'client']):
        scores['vente'] = 1
    else:
        scores['vente'] = 0

    # 3. Prospection
    if any(x in text for x in ['prospecting', 'field', 'territory', 'hunting', 'new business']):
        scores['prospection'] = 2
    elif any(x in text for x in ['support', 'back office']):
        scores['prospection'] = 1
    else:
        scores['prospection'] = 0

    # 4. USA Experience
    usa_text = text
    if any(x in usa_text for x in ['usa', 'united states', 'new york', 'los angeles', 'chicago']):
        scores['usa_exp'] = 2
    elif any(x in usa_text for x in ['uk', 'canada', 'australia', 'ireland']):
        scores['usa_exp'] = 1
    else:
        scores['usa_exp'] = 0

    # 5. Profil Marche (BTP/construction) — min 1
    if any(x in text for x in ['construction', 'mining', 'drilling', 'concrete', 'btp', 'machinery']):
        scores['profil_marche'] = 2
    else:
        scores['profil_marche'] = 1  # Default, never 0

    # 6. Ancrage culturel
    if any(x in text for x in ['british', 'american', 'australian', 'canadian', 'irish']):
        scores['ancrage_culturel'] = 2
    elif any(x in text for x in ['international', 'expat', 'multinational']):
        scores['ancrage_culturel'] = 1
    else:
        scores['ancrage_culturel'] = 0

    return scores

# Load & rescore Dylan
with open(DATA_JSON) as f:
    data = json.load(f)

dylan = data['candidates']['18-dylan-dourlen']

# Score
scores = score_criteria(dylan)
total = sum(scores.values())

# Update
dylan['scoreDetails'] = scores
dylan['matchingScore'] = total
dylan['refined_analysis'] = {
    'total_score': total,
    'verdict': 'GO' if total >= 7 else 'À ÉTUDIER' if total >= 4 else 'NO GO',
    'scoreDetails': scores.copy(),
}

print(f"\nDylan Dourlen Rescore:")
print("="*60)
print(f"Langues:         {scores['langues']}/2")
print(f"Vente:           {scores['vente']}/2")
print(f"Prospection:     {scores['prospection']}/2")
print(f"USA Exp:         {scores['usa_exp']}/2")
print(f"Profil Marche:   {scores['profil_marche']}/2")
print(f"Ancrage Culturel: {scores['ancrage_culturel']}/2")
print("-"*60)
print(f"TOTAL:           {total}/12")
print("="*60)

# Save
with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✓ Dylan rescored: {total}/12")
print(f"✓ data.json saved")
