#!/usr/bin/env python3
"""
SUPER STRICT rescore — match Nicolas exactly
Nicolas est TRÈS conservateur. Default = 0, count seulement évidence solide.
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
            return result.stdout, "pdftotext"
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
                return text, "OCR"
    except:
        pass

    return "", "failed"

def extract_english_level(text):
    """Extract English level — EXACT patterns only."""
    pattern = r'(?:english|anglais|english level|level)\s*(?:–|-|:|=)?\s*([A-Z]2|[A-Z]1|native|bilingual|fluent)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def score_langues_super_strict(text):
    """
    SUPER STRICT:
    2 = native OR bilingual ONLY
    1 = C1 OR C2 OR B1/B2/FLUENT/PROFESSIONAL
    0 = everything else (no level mentioned = 0)
    """
    level = extract_english_level(text)
    if not level:
        return 0

    level_lower = level.lower()

    # ONLY native/bilingual = 2
    if any(x in level_lower for x in ['native', 'bilingual']):
        return 2

    # C1/C2/B1/B2/FLUENT/PROFESSIONAL = 1
    if any(x in level_lower for x in ['c1', 'c2', 'b1', 'b2', 'fluent', 'professional']):
        return 1

    # Everything else = 0
    return 0

def score_vente_super_strict(text):
    """
    SUPER STRICT:
    2 = 'Sales Manager' OR 'Director of Sales' (explicit title)
    1 = 'Commercial' OR 'BDM' OR 'Account Manager' (explicit role)
    0 = everything else (marketing alone = 0)
    """
    text_lower = text.lower()

    # Exact titles for 2
    if any(x in text_lower for x in ['sales manager', 'director of sales', 'sales director']):
        return 2

    # Roles for 1
    if any(x in text_lower for x in ['commercial manager', 'account manager', 'bdm', 'business development manager']):
        return 1

    # Generic "sales" or "commercial" alone = 0 (too vague)
    return 0

def score_prospection_super_strict(text):
    """
    SUPER STRICT:
    2 = 'Prospecteur' OR explicit 'prospecting' (French/English commercial hunting)
    1 = 'new business' OR 'lead generation' OR 'acquisition' in context of sales
    0 = everything else
    """
    text_lower = text.lower()

    # Strong indicator for 2
    if any(x in text_lower for x in ['prospecteur', 'prospecting', 'new business development']):
        return 2

    # Weak indicator for 1
    if any(x in text_lower for x in ['new business', 'lead generation', 'acquisition', 'hunting']):
        # But NOT if it's just a buzzword — need context
        # For now, give 1 if found
        return 1

    return 0

def score_usa_exp_super_strict(text):
    """
    SUPER STRICT:
    2 = WORKED/LIVED in USA + years/months/duration mentioned
    1 = (never used by Nicolas)
    0 = everything else (just mention of USA = 0)
    """
    text_lower = text.lower()

    # Need explicit work/lived + USA + duration
    usa_work = any(x in text_lower for x in ['worked in usa', 'worked in united states', 'based in usa', 'based in united states', 'lived in usa'])

    if usa_work:
        # Check for duration
        duration = any(x in text_lower for x in ['years', 'months', '20', 'year', 'month', 'experience'])
        if duration:
            return 2

    # Just mention of USA cities/general = 0
    return 0

def score_ancrage_super_strict(text):
    """
    SUPER STRICT:
    2 = native USA/UK/CAN/AUS/etc (explicit nationality/passport)
    1 = explicit 'expat' OR 'multinational' OR 'international'
    0 = everything else (default, French local)
    """
    text_lower = text.lower()

    # Native for 2
    if any(x in text_lower for x in ['american', 'american national', 'british', 'british national', 'canadian', 'australian']):
        return 2

    # International for 1
    if any(x in text_lower for x in ['expat', 'multinational', 'international']):
        return 1

    return 0

def score_profil_marche_super_strict(text):
    """
    SUPER STRICT:
    2 = explicit BTP/construction/mining/drilling/concrete
    1 = default (no explicit industry mentioned)
    """
    text_lower = text.lower()

    if any(x in text_lower for x in ['btp', 'construction', 'mining', 'drilling', 'concrete', 'building', 'heavy equipment']):
        return 2

    return 1

def score_candidate_super_strict(text):
    return {
        'langues': score_langues_super_strict(text),
        'vente': score_vente_super_strict(text),
        'prospection': score_prospection_super_strict(text),
        'usa_exp': score_usa_exp_super_strict(text),
        'ancrage_culturel': score_ancrage_super_strict(text),
        'profil_marche': score_profil_marche_super_strict(text),
    }

# ============ MAIN ============

print("\n" + "="*100)
print("RESCORE 68 — SUPER STRICT (match Nicolas exactly)")
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

    text, method = extract_text(cv_path)
    scores = score_candidate_super_strict(text)
    total = sum(scores.values())

    cand['scoreDetails'] = scores
    cand['matchingScore'] = total

    verdict = 'GO' if total >= 7 else 'À ÉTUDIER' if total >= 4 else 'NO GO'
    cand['refined_analysis'] = {
        'total_score': total,
        'verdict': verdict,
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

print("\n✓ Done")
