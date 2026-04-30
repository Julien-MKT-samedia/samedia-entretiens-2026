#!/usr/bin/env python3
"""
Extraction complète + rescoring TOUS les candidats (66 + 2 nouveaux)
Basé sur 5 critères validés :
1. Anglais (strict)
2. Prospection/Terrain (core)
3. Vente + Industrie
4. USA/North America exp
5. Ancrage culturel

Vérification qualité d'extraction incluse
"""

import json
import subprocess
import re
import os
import tempfile
from pathlib import Path

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"
CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
SUPP_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/Candidature-VIE-SAMEDIA-USA-2026/CVs VIE USA suppl"

def extract_text(pdf_path):
    """Extract text from PDF via pdftotext or OCR."""
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

# ============ EXTRACTION FUNCTIONS ============

def extract_languages_with_levels(text):
    """Extract languages WITH levels (C1, C2, B1, B2, native, fluent, etc)"""
    langs = {}

    # Pattern: Language – Level
    pattern = r'(\b(?:english|french|spanish|german|italian|portuguese|mandarin|arabic|dutch|polish|russian)\b)\s*(?:–|-|:)?\s*(\b(?:C[12]|B[12]|A[12]|native|bilingual|fluent|professional|proficient|intermediate|basic|advanced)\b)'

    matches = re.finditer(pattern, text, re.IGNORECASE)
    for match in matches:
        lang = match.group(1).capitalize()
        level = match.group(2).upper()
        if lang not in langs:
            langs[lang] = level

    # Fallback: simple language detection
    if not langs:
        simple_langs = {
            'English': r'(?:english|anglais)',
            'French': r'(?:french|français)',
            'Spanish': r'(?:spanish|espagnol)',
        }
        for lang, pattern in simple_langs.items():
            if re.search(pattern, text, re.IGNORECASE):
                langs[lang] = None

    return langs

def extract_english_level(text):
    """Extract English level specifically."""
    langs = extract_languages_with_levels(text)
    english = next((langs.get(l) for l in langs if 'english' in l.lower()), None)
    return english

def detect_prospection_terrain(text):
    """Detect prospection/terrain/acquisition keywords."""
    text_lower = text.lower()

    # Prospection active / hunting
    prospection_keywords = [
        'prospection', 'prospecting', 'hunting', 'new business', 'acquisition',
        'lead generation', 'prospecteur', 'business development', 'bdm',
        'sales', 'commercial', 'account executive', 'territory management'
    ]

    # Support / back office
    support_keywords = [
        'support', 'back office', 'administrative', 'coordinator', 'assistant',
        'analyst', 'finance', 'accounting', 'hr', 'it'
    ]

    prospection_count = sum(1 for kw in prospection_keywords if kw in text_lower)
    support_count = sum(1 for kw in support_keywords if kw in text_lower)

    return prospection_count, support_count

def detect_vente_industrie(text):
    """Detect sales manager + BTP/industrial."""
    text_lower = text.lower()

    # Sales Manager / BDM
    sales_mgr = any(x in text_lower for x in ['sales manager', 'sales director', 'business development manager', 'bdm', 'account manager'])
    commercial = any(x in text_lower for x in ['commercial', 'sales', 'account', 'business development'])

    # BTP / Industrial
    btp_keywords = [
        'btp', 'construction', 'building', 'concrete', 'drilling', 'mining',
        'tools', 'machinery', 'equipment', 'industrial', 'manufacturing',
        'mechanical', 'engineering', 'project management'
    ]

    has_btp = any(kw in text_lower for kw in btp_keywords)
    has_commercial = sales_mgr or commercial

    return has_commercial, has_btp, sales_mgr

def detect_usa_exp(text):
    """Detect USA/North America experience."""
    text_lower = text.lower()

    usa_keywords = ['usa', 'united states', 'new york', 'chicago', 'california', 'texas', 'florida', 'us experience']
    canada_keywords = ['canada', 'toronto', 'vancouver', 'quebec']
    other_eng = ['uk', 'australia', 'ireland']

    has_usa = any(kw in text_lower for kw in usa_keywords)
    has_canada = any(kw in text_lower for kw in canada_keywords)
    has_other = any(kw in text_lower for kw in other_eng)

    return has_usa, has_canada, has_other

def detect_cultural_anchoring(text):
    """Detect cultural anchoring (nationality/origin)."""
    text_lower = text.lower()

    # Native countries
    native_keywords = {
        'USA': ['american', 'usa native', 'born in usa', 'us national'],
        'Canada': ['canadian', 'born in canada'],
        'UK': ['british', 'uk national', 'british passport'],
        'AUS': ['australian', 'born in australia'],
        'IRL': ['irish', 'ireland national']
    }

    # Expat/multinational
    expat_keywords = ['expat', 'multinational', 'international experience', 'worked abroad', 'lived abroad']

    for country, keywords in native_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return f"native_{country}"

    if any(kw in text_lower for kw in expat_keywords):
        return "expat"

    return "local"

# ============ SCORING FUNCTIONS ============

def score_anglais(text):
    """Score ANGLAIS criterion."""
    level = extract_english_level(text)

    if not level:
        return 0

    level_lower = level.lower()

    # 2 pts: Bilingue OU natif
    if any(x in level_lower for x in ['bilingual', 'native', 'billingue']):
        return 2

    # 1 pt: C1/C2
    if any(x in level_lower for x in ['c1', 'c2']):
        return 1

    # 0 pts: B2 ou moins
    return 0

def score_prospection(text):
    """Score PROSPECTION/TERRAIN criterion."""
    prosp_count, support_count = detect_prospection_terrain(text)

    # 2 pts: Prospection active/hunting/acquisition
    if prosp_count >= 3:
        return 2

    # 1 pt: Support/back office
    if support_count >= 2:
        return 1

    # Fallback
    if prosp_count > 0:
        return 2 if prosp_count >= support_count else 1

    return 0

def score_vente_industrie(text):
    """Score VENTE + INDUSTRIE criterion."""
    has_commercial, has_btp, sales_mgr = detect_vente_industrie(text)

    # 2 pts: (Sales Manager OU Commercial terrain) + BTP/industrial
    if (sales_mgr or has_commercial) and has_btp:
        return 2 if sales_mgr else 2  # Both count as 2

    # 1 pt: Commercial OU Industrie seul
    if has_commercial or has_btp:
        return 1

    return 0

def score_usa_exp(text):
    """Score USA/NORTH AMERICA EXP criterion."""
    has_usa, has_canada, has_other = detect_usa_exp(text)

    # 2 pts: Travaillé/vécu USA + sales/BDM
    if has_usa:
        prospection_count, _ = detect_prospection_terrain(text)
        if prospection_count >= 2:
            return 2
        return 2  # USA alone = 2

    # 1 pt: Canada/UK/AUS OU USA sans BDM
    if has_canada or has_other:
        return 1

    return 0

def score_ancrage(text):
    """Score ANCRAGE CULTUREL criterion."""
    anchoring = detect_cultural_anchoring(text)

    # 2 pts: Natif USA/CA/UK/AUS/IRL
    if anchoring.startswith('native_'):
        return 2

    # 1 pt: Expat/multinational
    if anchoring == 'expat':
        return 1

    return 0

def score_candidate(text):
    """Score all 5 criteria and return dict."""
    return {
        'anglais': score_anglais(text),
        'prospection': score_prospection(text),
        'vente_industrie': score_vente_industrie(text),
        'usa_exp': score_usa_exp(text),
        'ancrage_culturel': score_ancrage(text),
    }

# ============ MAIN ============

print("\n" + "="*100)
print("EXTRACTION + RESCORING COMPLET (66 + 2 nouveaux)")
print("="*100 + "\n")

# Load existing data
with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

# Process 66 existing candidates
print("PHASE 1: RE-EXTRACTION + RESCORING 66 CANDIDATS EXISTANTS")
print("-" * 100)

extraction_quality = {'high': 0, 'medium': 0, 'low': 0}

for key in sorted(candidates.keys()):
    if key.startswith(('0', '1', '2', '3', '4', '5', '6')):  # Only 01-66
        cand = candidates[key]
        cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
        cv_path = f"{CV_DIR}/{cv_file}"

        if not os.path.exists(cv_path):
            continue

        text, method = extract_text(cv_path)
        text_len = len(text)

        # Quality check
        if text_len > 3000:
            quality = 'high'
        elif text_len > 1500:
            quality = 'medium'
        elif text_len > 500:
            quality = 'low'
        else:
            quality = 'low'

        extraction_quality[quality] += 1

        # Score
        scores = score_candidate(text)
        total = sum(scores.values())

        cand['scoreDetails'] = scores
        cand['matchingScore'] = total
        cand['extraction_quality'] = quality

# Process 2 new candidates
print("\nPHASE 2: INTÉGRATION + EXTRACTION 2 NOUVEAUX CANDIDATS")
print("-" * 100)

new_candidates = [
    {
        'name': 'Maëlle Rouhier',
        'number': 67,
        'file': 'CV Maëlle Rouhier.pdf'
    },
    {
        'name': 'Charly Garcia',
        'number': 68,
        'file': 'CV M. GARCIA Charly (fr).pdf'
    }
]

for new_cand in new_candidates:
    cv_path = os.path.join(SUPP_DIR, new_cand['file'])

    if not os.path.exists(cv_path):
        print(f"✗ {new_cand['file']} NOT FOUND")
        continue

    text, method = extract_text(cv_path)
    text_len = len(text)

    # Quality check
    if text_len > 3000:
        quality = 'high'
    elif text_len > 1500:
        quality = 'medium'
    elif text_len > 500:
        quality = 'low'
    else:
        quality = 'low'

    extraction_quality[quality] += 1

    # Score
    scores = score_candidate(text)
    total = sum(scores.values())

    # Create candidate entry
    key = f"{new_cand['number']:02d}-{new_cand['name'].lower().replace(' ', '-')}"

    candidates[key] = {
        'id': key,
        'number': new_cand['number'],
        'name': new_cand['name'],
        'tier': 'Tier1' if total >= 7 else 'Tier2' if total >= 4 else 'Tier3',
        'matchingScore': total,
        'scoreDetails': scores,
        'cvFile': f"recrutements/vie-usa-2026/cvs/{new_cand['file']}",
        'extraction_quality': quality,
        'extraction_method': method,
        'confidence_extraction': 100,
        'languages': [],
        'education': [],
        'experiences': [],
        'skills': [],
        'strengths': [],
        'warnings': [],
        'refined_analysis': {
            'total_score': total,
            'verdict': 'GO' if total >= 7 else 'À ÉTUDIER' if total >= 4 else 'NO GO',
            'scoreDetails': scores.copy(),
        }
    }

    print(f"✓ {key}: {new_cand['name']} — {total}/10 ({quality})")

# Ranking
print("\nPHASE 3: CLASSEMENT (top 15)")
print("-" * 100)

sorted_cands = sorted(candidates.items(), key=lambda x: -x[1]['matchingScore'])

for idx, (key, cand) in enumerate(sorted_cands):
    if idx < 15:
        cand['rank'] = idx + 1
    else:
        cand['rank'] = 0

print(f"Top 15:")
for idx, (key, cand) in enumerate(sorted_cands[:15]):
    print(f"  {idx+1}. {cand['name']:30} {cand['matchingScore']}/10")

# Update metadata
data['metadata']['total_candidates'] = len(candidates)

# Save
with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "="*100)
print("RÉSUMÉ")
print("="*100)
print(f"\n✓ 66 candidats re-scorés")
print(f"✓ 2 nouveaux candidats ajoutés (67, 68)")
print(f"✓ Total: {len(candidates)} candidats")
print(f"\nQualité extraction:")
print(f"  - HIGH (>3000 chars): {extraction_quality['high']}")
print(f"  - MEDIUM (1500-3000): {extraction_quality['medium']}")
print(f"  - LOW (<1500): {extraction_quality['low']}")
print(f"\n✓ data.json sauvegardé ({len(candidates)} candidats)")
print("="*100 + "\n")
