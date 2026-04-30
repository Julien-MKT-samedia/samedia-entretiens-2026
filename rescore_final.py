#!/usr/bin/env python3
"""
FINAL RESCORE — Logique Nicolas strict
langues: 2=native/bilingual, 1=C1/C2, 0=rest
"""

import json
import subprocess
import re
import os
import tempfile

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"
CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"

def extract_text(pdf_path):
    try:
        result = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and len(result.stdout) > 200:
            return result.stdout
    except:
        pass

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(["pdftoppm", pdf_path, os.path.join(temp_dir, "page")], capture_output=True, timeout=30)
            images = [f for f in os.listdir(temp_dir) if f.startswith('page')]
            all_text = []
            for img in sorted(images):
                result = subprocess.run(["tesseract", os.path.join(temp_dir, img), "-"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    all_text.append(result.stdout)
            text = "\n".join(all_text)
            if len(text) > 200:
                return text
    except:
        pass

    return ""

def extract_english_level(text):
    """Extract exact English level from CV."""
    pattern = r'(?:english|anglais|english level|level)\s*(?:–|-|:|=)?\s*([A-Z]2|[A-Z]1|native|bilingual|fluent|c2|c1)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def score_langues_final(text):
    """
    2 = native OR bilingual (explicit)
    1 = C1 OR C2 (explicit)
    0 = everything else
    """
    level = extract_english_level(text)
    if not level:
        return 0

    level_lower = level.lower()

    # ONLY native/bilingual = 2
    if any(x in level_lower for x in ['native', 'bilingual']):
        return 2

    # C1 or C2 = 1
    if any(x in level_lower for x in ['c1', 'c2']):
        return 1

    # Everything else = 0
    return 0

def score_vente_final(text):
    """
    2 = Sales Manager / Director of Sales
    1 = Commercial / BDM / Account Manager
    0 = rest
    """
    text_lower = text.lower()

    if any(x in text_lower for x in ['sales manager', 'director of sales', 'sales director']):
        return 2

    if any(x in text_lower for x in ['commercial manager', 'account manager', 'bdm', 'business development manager']):
        return 1

    return 0

def score_prospection_final(text):
    """
    2 = Prospecteur / Prospecting (explicit hunting)
    1 = new business / lead generation / acquisition
    0 = rest
    """
    text_lower = text.lower()

    if any(x in text_lower for x in ['prospecteur', 'prospecting', 'new business development']):
        return 2

    if any(x in text_lower for x in ['new business', 'lead generation', 'acquisition', 'hunting']):
        return 1

    return 0

def score_usa_exp_final(text):
    """
    2 = worked/lived USA + duration/years mentioned
    1 = (unused)
    0 = rest
    """
    text_lower = text.lower()

    # Explicit USA work
    usa_work = any(x in text_lower for x in ['worked in usa', 'worked in united states', 'based in usa', 'lived in usa', 'miami'])

    if usa_work:
        # Check for real experience indicator
        duration = any(x in text_lower for x in ['year', 'month', '20', 'experience'])
        if duration:
            return 2

    return 0

def score_ancrage_final(text):
    """
    2 = native USA/UK/CAN/AUS (explicit)
    1 = expat / multinational / international
    0 = default (French local)
    """
    text_lower = text.lower()

    # Native = 2
    if any(x in text_lower for x in ['american', 'american national', 'british', 'canadian', 'australian']):
        return 2

    # International = 1
    if any(x in text_lower for x in ['expat', 'multinational', 'international', 'trilingual']):
        return 1

    return 0

def score_profil_marche_final(text):
    """
    2 = BTP/construction/mining/drilling
    1 = default
    """
    text_lower = text.lower()

    if any(x in text_lower for x in ['btp', 'construction', 'mining', 'drilling', 'concrete', 'heavy equipment']):
        return 2

    return 1

def score_candidate_final(text):
    return {
        'langues': score_langues_final(text),
        'vente': score_vente_final(text),
        'prospection': score_prospection_final(text),
        'usa_exp': score_usa_exp_final(text),
        'ancrage_culturel': score_ancrage_final(text),
        'profil_marche': score_profil_marche_final(text),
    }

# ============ MAIN ============

print("\n" + "="*100)
print("RESCORE FINAL — 68 CANDIDATS (logique Nicolas)")
print("="*100 + "\n")

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

for key in sorted(candidates.keys()):
    if not key[0].isdigit():
        continue

    cand = candidates[key]
    cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
    cv_path = f"{CV_DIR}/{cv_file}"

    if not os.path.exists(cv_path):
        continue

    text = extract_text(cv_path)
    scores = score_candidate_final(text)

    # Manual override for Orlane (01-orlane-degras)
    if key == '01-orlane-degras':
        scores['langues'] = 0

    total = sum(scores.values())

    cand['scoreDetails'] = scores
    cand['matchingScore'] = total
    cand['refined_analysis'] = {
        'total_score': total,
        'verdict': 'GO' if total >= 7 else 'À ÉTUDIER' if total >= 4 else 'NO GO',
        'scoreDetails': scores.copy(),
    }

print("Ranking...")
sorted_cands = sorted(candidates.items(), key=lambda x: -x[1]['matchingScore'])

for idx, (key, cand) in enumerate(sorted_cands):
    cand['rank'] = (idx + 1) if idx < 15 else 0

data['metadata']['total_candidates'] = len(candidates)

with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print("\nTOP 15:")
for idx, (key, cand) in enumerate(sorted_cands[:15]):
    print(f"  {idx+1}. {cand['name']:30} {cand['matchingScore']}/12")

print("\n✓ Rescore complete")
