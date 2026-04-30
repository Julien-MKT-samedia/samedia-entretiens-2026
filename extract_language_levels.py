#!/usr/bin/env python3
"""
Re-extract languages WITH LEVELS from all CVs
Format: English C2, French B1, etc.
"""

import subprocess
import json
import re
import tempfile
import os

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def extract_text(pdf_path):
    """Extract via pdftotext or OCR."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and len(result.stdout) > 200:
            return result.stdout
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
            return "\n".join(all_text)
    except:
        pass
    return ""

def extract_languages_with_levels(text):
    """Extract languages with levels (C1, C2, B1, B2, Native, Fluent, etc.)"""
    if not text:
        return []

    langs = []

    # Pattern: Language – Level / Language – Level (common format)
    pattern = r'(\b(?:english|french|spanish|german|italian|portuguese|mandarin|arabic|dutch|polish|russian)\b)\s*(?:–|-|:)?\s*(\b(?:C[12]|B[12]|A[12]|native|bilingual|fluent|professional|proficient|intermediate|basic|advanced)\b)'

    matches = re.finditer(pattern, text, re.IGNORECASE)
    found = {}
    for match in matches:
        lang = match.group(1).capitalize()
        level = match.group(2).upper()
        if lang not in found:
            found[lang] = level

    # If no matches, try simpler pattern
    if not found:
        simple_langs = {
            'English': r'(?:english|anglais)',
            'French': r'(?:french|français)',
            'Spanish': r'(?:spanish|espagnol)',
            'German': r'(?:german|allemand)',
            'Italian': r'(?:italian|italien)',
            'Portuguese': r'(?:portuguese|portugais)',
            'Mandarin': r'(?:mandarin|chinois)',
            'Arabic': r'(?:arabic|arabe)',
        }
        for lang, pattern in simple_langs.items():
            if re.search(pattern, text, re.IGNORECASE):
                found[lang] = None

    return found

def format_languages(lang_dict):
    """Format as list for display"""
    result = []
    for lang, level in lang_dict.items():
        if level:
            result.append(f"{lang} {level}")
        else:
            result.append(lang)
    return result

# Process all candidates
with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

print("\n" + "="*100)
print("LANGUAGE EXTRACTION WITH LEVELS")
print("="*100 + "\n")

changes = 0
for key in sorted(candidates.keys()):
    cand = candidates[key]
    cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
    cv_path = f"{CV_DIR}/{cv_file}"

    if not os.path.exists(cv_path):
        continue

    text = extract_text(cv_path)
    langs = extract_languages_with_levels(text)

    if langs:
        lang_list = format_languages(langs)
        old_langs = cand.get('languages', [])

        # Only show if changed
        if lang_list != old_langs:
            print(f"{key:30} {cand.get('name', '?'):30}")
            print(f"  OLD: {old_langs}")
            print(f"  NEW: {lang_list}")
            cand['languages'] = lang_list
            changes += 1

with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n{'='*100}")
print(f"✓ {changes} candidates updated with language levels")
print(f"✓ data.json saved")
print(f"{'='*100}\n")
