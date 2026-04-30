#!/usr/bin/env python3
"""
Rescore ALL 68 candidates using Nicolas's strict logic
Based on 4 manual evaluations: Orlane, Baptiste, Elsa, Alvaro
"""

import json
import subprocess
import re
import os
import tempfile
from pathlib import Path

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"
CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"

def extract_text(pdf_path):
    """Extract text from PDF."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and len(result.stdout) > 200:
            return result.stdout, "pdftotext"
    except:
        pass

    # OCR fallback
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(
                ["pdftoppm", pdf_path, os.path.join(temp_dir, "page")],
                capture_output=True, timeout=30
            )
            images = [f for f in os.listdir(temp_dir) if f.startswith('page')]
            all_text = []
            for img in sorted(images):
                result = subprocess.run(
                    ["tesseract", os.path.join(temp_dir, img), "-"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    all_text.append(result.stdout)
            text = "\n".join(all_text)
            if len(text) > 200:
                return text, "OCR"
    except:
        pass

    return "", "failed"

# ============ NICOLAS-STRICT SCORING ============

def extract_english_level(text):
    """Extract English level specifically."""
    pattern = r'(\b(?:english|anglais)\b)\s*(?:–|-|:)?\s*(\b(?:C[12]|B[12]|A[12]|native|bilingual|fluent|professional|proficient|intermediate|basic|advanced)\b)'

    matches = re.finditer(pattern, text, re.IGNORECASE)
    for match in matches:
        return match.group(2).upper()

    # Fallback: simple detection
    if re.search(r'(?:english|anglais)', text, re.IGNORECASE):
        return "PRESENT"

    return None

def score_langues_nicolas(text):
    """Nicolas: 0=none/basic, 1=B1/B2/conversational, 2=C1/C2/native (very rare)"""
    level = extract_english_level(text)

    if not level:
        return 0

    level_lower = level.lower()

    # C1/C2/NATIVE/BILINGUAL = 2 (very strict)
    if any(x in level_lower for x in ['c1', 'c2', 'native', 'bilingual']):
        return 2

    # B1/B2/FLUENT/PROFESSIONAL/ADVANCED = 1
    if any(x in level_lower for x in ['b1', 'b2', 'fluent', 'professional', 'advanced']):
        return 1

    # INTERMEDIATE/BASIC/PRESENT = 0 (just presence, no level)
    return 0

def score_vente_nicolas(text):
    """Nicolas: 0=not sales, 1=has some sales/commercial, 2=strong sales mgr (rare)"""
    text_lower = text.lower()

    # STRONG sales manager = 2
    strong_sales = ['sales manager', 'business development manager', 'director of sales', 'sales director']
    if any(kw in text_lower for kw in strong_sales):
        return 2

    # Some sales/commercial = 1
    soft_sales = ['sales', 'commercial', 'account manager', 'bdm', 'business development', 'sales representative']
    if any(kw in text_lower for kw in soft_sales):
        return 1

    return 0

def score_prospection_nicolas(text):
    """Nicolas: 0=not hunting, 1=some hunting/acquisition, 2=strong hunter (rare)"""
    text_lower = text.lower()

    # STRONG prospection = 2
    strong_prospection = ['prospecteur', 'prospecting', 'new business', 'lead generation', 'business acquisition']
    if any(kw in text_lower for kw in strong_prospection):
        return 2

    # Some prospection = 1
    soft_prospection = ['prospection', 'hunting', 'acquisition', 'bdm', 'account executive']
    if any(kw in text_lower for kw in soft_prospection):
        return 1

    return 0

def score_usa_exp_nicolas(text):
    """Nicolas: 0=no USA, 1=??, 2=worked/lived USA with proof"""
    text_lower = text.lower()

    usa_indicators = ['usa', 'united states', 'new york', 'chicago', 'california', 'texas', 'florida', 'us-based', 'based in']

    has_usa_mention = any(indicator in text_lower for indicator in usa_indicators)

    if not has_usa_mention:
        return 0

    # Check for actual work/lived duration indicators
    work_proof = ['worked', 'worked in', 'worked for', 'employed', 'based in', 'lived in', 'years in', 'months in', 'experience', '20']
    has_proof = any(proof in text_lower for proof in work_proof)

    if has_proof:
        return 2  # Real USA experience

    # Just mention = 0 (not real experience)
    return 0

def score_ancrage_nicolas(text):
    """Nicolas: 0=local/French, 1=international/expat, 2=native USA/UK/etc"""
    text_lower = text.lower()

    # NATIVE = 2
    native_keywords = {
        'USA': ['american', 'american national', 'born in usa', 'born in united states', 'us national'],
        'UK': ['british', 'british national', 'british passport'],
        'OTHER': ['canadian', 'australian', 'irish national']
    }

    for country, keywords in native_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return 2

    # INTERNATIONAL/EXPAT = 1
    intl_keywords = ['expat', 'multinational', 'international', 'worked abroad', 'lived abroad', 'bilingual']
    if any(kw in text_lower for kw in intl_keywords):
        return 1

    return 0

def score_profil_marche_nicolas(text):
    """Nicolas: 1=default, 2=BTP/construction/industry"""
    text_lower = text.lower()

    btp_keywords = ['btp', 'construction', 'building', 'concrete', 'drilling', 'mining', 'machinery', 'equipment', 'industrial', 'manufacturing', 'heavy equipment']

    if any(kw in text_lower for kw in btp_keywords):
        return 2

    return 1  # Default

def score_candidate_nicolas(text):
    """Score using Nicolas's strict logic"""
    return {
        'langues': score_langues_nicolas(text),
        'vente': score_vente_nicolas(text),
        'prospection': score_prospection_nicolas(text),
        'usa_exp': score_usa_exp_nicolas(text),
        'ancrage_culturel': score_ancrage_nicolas(text),
        'profil_marche': score_profil_marche_nicolas(text),
    }

# ============ MAIN ============

print("\n" + "="*100)
print("RESCORE 68 CANDIDATS — LOGIQUE NICOLAS STRICTE")
print("="*100 + "\n")

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

print("Rescoring all 68 candidates...\n")

for key in sorted(candidates.keys()):
    if not key[0].isdigit():
        continue

    cand = candidates[key]
    cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
    cv_path = f"{CV_DIR}/{cv_file}"

    if not os.path.exists(cv_path):
        continue

    text, method = extract_text(cv_path)

    # Score
    scores = score_candidate_nicolas(text)
    total = sum(scores.values())

    cand['scoreDetails'] = scores
    cand['matchingScore'] = total

    # Update refined_analysis
    verdict = 'GO' if total >= 7 else 'À ÉTUDIER' if total >= 4 else 'NO GO'
    cand['refined_analysis'] = {
        'total_score': total,
        'verdict': verdict,
        'scoreDetails': scores.copy(),
    }

print("Recalculating ranking...")
sorted_cands = sorted(candidates.items(), key=lambda x: -x[1]['matchingScore'])

for idx, (key, cand) in enumerate(sorted_cands):
    if idx < 15:
        cand['rank'] = idx + 1
    else:
        cand['rank'] = 0

# Update metadata
data['metadata']['total_candidates'] = len(candidates)
data['metadata']['generated'] = '2026-04-30'

# Save
with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "="*100)
print("TOP 15 — LOGIQUE NICOLAS STRICTE")
print("="*100)

for idx, (key, cand) in enumerate(sorted_cands[:15]):
    print(f"  {idx+1}. {cand['name']:30} {cand['matchingScore']}/12")

print("\n" + "="*100)
print("✓ Rescore complete")
print("="*100 + "\n")
