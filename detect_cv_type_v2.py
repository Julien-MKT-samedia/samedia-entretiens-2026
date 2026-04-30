#!/usr/bin/env python3
"""
Détecte CV vs LDM v2 — meilleure détection + croise avec data.json
"""

import os
import subprocess
import json
import re

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def extract_pdf_text(pdf_path, lines=10):
    """Extract first N lines from PDF."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout[:800]  # First 800 chars
    except:
        pass
    return None

def detect_document_type(text):
    """
    Returns: 'CV', 'LDM', or 'UNCLEAR'

    CV signals:
    - section headers: experience, education, skills, languages, technical, profile, summary
    - employment dates/positions
    - bullet-point lists

    LDM signals:
    - salutation: dear, chère, monsieur, madame
    - purpose phrases: application, applying, interested, motivated
    - closing: yours, cordialement, salutations
    """

    if not text:
        return "UNCLEAR"

    text_lower = text.lower()

    # CV strong signals
    cv_strong = [
        r'\bexperience\b|\bwork history\b|\bcareer\b|\bprofessional history\b',
        r'\beducation\b|\bdegrees?\b|\bstudies\b|\bcourses?\b|\buniversit',
        r'\bskills\b|\bcompetencies?\b|\btechnical\b|\blanguages?\b',
    ]

    # LDM strong signals
    ldm_strong = [
        r'^\s*(dear|chère|monsieur|madame|sir|madam)',  # Start with salutation
        r'\bappl(ying|ication|icant)\b|\bapply\b|\bapplicant\b',
        r'\b(candidate|applying for|interested in|enthusiastic|keen to)\b',
        r'(sincerely|cordialement|salutations|yours faithfully)',  # Closing
    ]

    # CV bullets/structure
    cv_structure = [
        r'^[\s]*[-•*]\s+\w+',  # bullet points
        r'^[\s]*\d{4}[-–]\d{4}',  # date ranges
    ]

    cv_score = 0
    ldm_score = 0

    for pattern in cv_strong:
        if re.search(pattern, text_lower, re.MULTILINE):
            cv_score += 2

    for pattern in ldm_strong:
        if re.search(pattern, text_lower, re.MULTILINE):
            ldm_score += 2

    for pattern in cv_structure:
        if re.search(pattern, text_lower, re.MULTILINE):
            cv_score += 1

    # Decision
    if cv_score >= 3 and cv_score > ldm_score:
        return "CV"
    elif ldm_score >= 3 and ldm_score > cv_score:
        return "LDM"
    elif cv_score > ldm_score and cv_score >= 2:
        return "CV"
    elif ldm_score > cv_score and ldm_score >= 2:
        return "LDM"
    else:
        return "UNCLEAR"

def load_data_json():
    """Load data.json to check current file references."""
    with open(DATA_JSON) as f:
        data = json.load(f)
    return data

def main():
    data = load_data_json()

    # Build map: number -> candidate
    candidates = {}
    for cand in data.get('candidates', []):
        num = cand.get('number')
        if 52 <= num <= 66:
            candidates[num] = {
                'name': cand.get('name'),
                'cvFile': cand.get('cvFile'),
                'ldmFile': cand.get('ldmFile'),
            }

    results = {}

    # Check each PDF pair
    for num in sorted(candidates.keys()):
        cand_info = candidates[num]
        name = cand_info['name']

        prefix = f"{num:02d}-"
        expected_files = [f for f in os.listdir(CV_DIR) if f.startswith(prefix) and f.endswith('.pdf')]

        results[num] = {
            'candidate': name,
            'expected_cvFile': cand_info['cvFile'],
            'expected_ldmFile': cand_info['ldmFile'],
            'detected': {}
        }

        for pdf_file in sorted(expected_files):
            pdf_path = os.path.join(CV_DIR, pdf_file)
            text = extract_pdf_text(pdf_path)
            doc_type = detect_document_type(text)

            # Extract -cv or -ldm from filename
            if '-cv.pdf' in pdf_file:
                file_type = 'CV'
            elif '-ldm.pdf' in pdf_file:
                file_type = 'LDM'
            else:
                file_type = '?'

            results[num]['detected'][file_type] = {
                'filename': pdf_file,
                'detected_as': doc_type,
                'match': "✓" if (file_type == doc_type) else "✗"
            }

    # Print report
    print("\n" + "="*90)
    print("CV/LDM DETECTION REPORT — CANDIDATS 52-66")
    print("="*90 + "\n")

    mismatches = []

    for num in sorted(results.keys()):
        r = results[num]
        print(f"#{num:02d} {r['candidate'].upper():30}")
        print(f"     data.json CV:  {r['expected_cvFile']}")
        print(f"     data.json LDM: {r['expected_ldmFile']}")

        for file_type in ['CV', 'LDM']:
            if file_type in r['detected']:
                d = r['detected'][file_type]
                status = d['match']
                print(f"     {status} {file_type:3} {d['filename']:40} → {d['detected_as']}")

                if d['match'] == '✗':
                    mismatches.append({
                        'num': num,
                        'name': r['candidate'],
                        'file': d['filename'],
                        'named': file_type,
                        'detected': d['detected_as']
                    })
        print()

    # Summary
    print("="*90)
    print(f"MISMATCHES: {len(mismatches)}")
    print("="*90 + "\n")

    if mismatches:
        for m in mismatches:
            print(f"⚠️  #{m['num']} {m['name']}")
            print(f"    {m['file']}")
            print(f"    Named: {m['named']} | Detected: {m['detected']}")
            print()
    else:
        print("✓ Tous les fichiers correspondent à leur nom.\n")

    # Save results
    with open(os.path.join(CV_DIR, "detection_v2.json"), "w") as f:
        json.dump(results, f, indent=2)

    print(f"✓ Résultats: {CV_DIR}/detection_v2.json")

if __name__ == "__main__":
    main()
