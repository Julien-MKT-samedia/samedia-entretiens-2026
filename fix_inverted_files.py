#!/usr/bin/env python3
"""
Swap cvFile/ldmFile for candidates where files are inverted
Based on detection results: if -ldm.pdf detected as CV, swap them
"""

import json
import subprocess
import re

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def extract_text(pdf_path, lines=10):
    """Extract first lines from PDF."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout[:500] if result.returncode == 0 else ""
    except:
        return ""

def is_ldm(text):
    """Detect if text is a letter of motivation."""
    text_lower = text.lower()
    ldm_patterns = [
        r"^(dear|chère|monsieur|madame)",  # Salutation at start
        r"subject.*application",
        r"i am writing|i am applying|applying for",
        r"yours sincerely|cordialement|salutations",
    ]

    count = sum(1 for p in ldm_patterns if re.search(p, text_lower, re.MULTILINE | re.IGNORECASE))
    return count >= 2

def main():
    print("\n" + "="*80)
    print("FIX: SWAP INVERTED CV/LDM FILES")
    print("="*80 + "\n")

    with open(DATA_JSON) as f:
        data = json.load(f)

    candidates = data['candidates']
    swaps = 0

    for cand_key in sorted(candidates.keys()):
        if not cand_key.startswith(('52-', '53-', '54-', '55-', '56-', '57-', '58-', '59-', '60-', '61-', '62-', '63-', '64-', '65-', '66-')):
            continue

        cand = candidates[cand_key]
        cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
        cv_path = f"{CV_DIR}/{cv_file}"

        text = extract_text(cv_path)

        if not text:
            continue

        # Check if cvFile is actually a LDM
        if is_ldm(text):
            # Swap: cvFile → ldmFile, ldmFile → cvFile
            old_cv = cand.get('cvFile')
            old_ldm = cand.get('ldmFile')

            # Generate swapped paths
            if old_cv and old_ldm:
                # Both exist, swap them
                cand['cvFile'] = old_ldm
                cand['ldmFile'] = old_cv
                print(f"✓ {cand_key:30} SWAPPED")
                print(f"    cvFile: {old_cv} → {old_ldm}")
                swaps += 1
            elif old_cv and not old_ldm:
                # Only cvFile, try to create ldmFile by swapping -cv/-ldm
                if '-cv.pdf' in old_cv:
                    ldm_file = old_cv.replace('-cv.pdf', '-ldm.pdf')
                    cand['cvFile'] = ldm_file
                    cand['ldmFile'] = old_cv
                    print(f"✓ {cand_key:30} INVERTED (created ldmFile)")
                    print(f"    cvFile: {old_cv} → {ldm_file}")
                    swaps += 1

    # Re-extract data for swapped candidates
    print(f"\n✓ {swaps} files swapped")
    print(f"\nRe-extracting data...")

    from extract_data_improved import extract_education, extract_experiences, extract_languages, extract_skills, infer_strengths

    for cand_key in sorted(candidates.keys()):
        if not cand_key.startswith(('52-', '53-', '54-', '55-', '56-', '57-', '58-', '59-', '60-', '61-', '62-', '63-', '64-', '65-', '66-')):
            continue

        cand = candidates[cand_key]
        cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
        cv_path = f"{CV_DIR}/{cv_file}"

        if not cv_path or not cv_file or '-cv.pdf' not in cv_file:
            continue

        text = extract_text(cv_path)
        if not text:
            continue

        # Only update if swapped (crude check)
        if is_ldm(extract_text(f"{CV_DIR}/{cand_key.split('-')[0]}-{cand_key.split('-')[1]}-cv.pdf")):
            # This was swapped, re-extract
            cand['education'] = extract_education(text)
            cand['experiences'] = extract_experiences(text)
            cand['languages'] = extract_languages(text)
            cand['skills'] = extract_skills(text)
            cand['strengths'] = infer_strengths(cand.get('scoreDetails', {}))
            print(f"✓ Re-extracted {cand_key}")

    # Save
    with open(DATA_JSON, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ data.json updated")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
