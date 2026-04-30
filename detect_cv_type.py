#!/usr/bin/env python3
"""
Détecte CV vs LDM pour candidats 52-66.
Analyse premiers 200 chars du texte extrait.
"""

import os
import subprocess
import json
import re

# Répertoire CVs
CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"

# Patterns pour détection
CV_INDICATORS = [
    r"experience|employment|work history|career",
    r"education|degree|bachelor|master|diplôme|licence",
    r"skills|competencies|expertise|technical",
    r"phone|email|linkedin|github|portfolio",
    r"summary|objective|profile",
    r"\d{1,2}/\d{1,2}/\d{4}",  # dates MM/DD/YYYY
]

LDM_INDICATORS = [
    r"dear sir|dear madam|dear hiring|dear employer|chère",
    r"yours sincerely|yours faithfully|cordialement|salutations",
    r"i am writing|i am applying|je posule|j'applique",
    r"motivation|interested in|keen to|enthusiastic",
    r"looking forward|à bientôt|au plaisir",
]

def extract_pdf_text(pdf_path, num_lines=5):
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.split('\n')[:num_lines]
            return '\n'.join(lines)
    except Exception as e:
        pass
    return None

def score_document(text):
    """Score document as CV (1.0) or LDM (0.0)."""
    if not text:
        return None

    text_lower = text.lower()

    cv_score = sum(1 for pattern in CV_INDICATORS if re.search(pattern, text_lower, re.I))
    ldm_score = sum(1 for pattern in LDM_INDICATORS if re.search(pattern, text_lower, re.I))

    # Retourne True = CV, False = LDM, None = unclear
    if cv_score > ldm_score + 1:
        return True
    elif ldm_score > cv_score + 1:
        return False
    else:
        return None

def main():
    results = {}

    # Lister tous PDFs 52-66
    files = sorted([f for f in os.listdir(CV_DIR) if f.startswith(('5[2-9]', '6[0-6]'))])
    files = [f for f in sorted(os.listdir(CV_DIR)) if re.match(r'^(5[2-9]|6[0-6])-', f) and f.endswith('.pdf')]

    for pdf_file in files:
        match = re.match(r'^(\d+)-(.*?)-(cv|ldm)\.pdf$', pdf_file)
        if not match:
            continue

        num, name, doc_type = match.groups()
        pdf_path = os.path.join(CV_DIR, pdf_file)

        # Extract text
        text = extract_pdf_text(pdf_path)

        if text:
            is_cv = score_document(text)
            first_chars = text[:200].replace('\n', ' ')

            key = f"{num}-{name}"
            if key not in results:
                results[key] = {}

            results[key][doc_type] = {
                "file": pdf_file,
                "detected_as": "CV" if is_cv else ("LDM" if is_cv is False else "UNCLEAR"),
                "cv_score": is_cv,
                "preview": first_chars[:100]
            }

    # Print results
    print("\n" + "="*80)
    print("DÉTECTION CV vs LDM — CANDIDATS 52-66")
    print("="*80 + "\n")

    for candidate in sorted(results.keys()):
        print(f"📋 {candidate.upper()}")
        for doc_type, data in results[candidate].items():
            detected = data['detected_as']
            status = "✓" if (doc_type == "cv" and detected == "CV") or (doc_type == "ldm" and detected == "LDM") else "⚠️"
            print(f"  {status} {doc_type.upper():3} → {detected:8} | {data['preview'][:60]}...")
        print()

    # Résumé mismatches
    print("\n" + "="*80)
    print("MISMATCHES DÉTECTÉS (fichier vs contenu)")
    print("="*80 + "\n")

    mismatches = []
    for candidate, docs in results.items():
        for doc_type, data in docs.items():
            detected = data['detected_as']
            if (doc_type == "cv" and detected == "LDM") or (doc_type == "ldm" and detected == "CV"):
                mismatches.append({
                    "candidate": candidate,
                    "file": data['file'],
                    "named_as": doc_type.upper(),
                    "actually": detected
                })

    if mismatches:
        for m in mismatches:
            print(f"⚠️  {m['candidate']}")
            print(f"    File: {m['file']}")
            print(f"    Named: {m['named_as']} | Detected: {m['actually']}\n")
    else:
        print("✓ Pas de mismatch — tous les fichiers correctement nommés.\n")

    # JSON export pour usage script suivant
    with open(os.path.join(CV_DIR, "detection_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Résultats sauvegardés: detection_results.json")

if __name__ == "__main__":
    main()
