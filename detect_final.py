#!/usr/bin/env python3
"""
Détection finale CV vs LDM pour 52-66 — simple + robuste
"""

import os
import subprocess
import re

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"

def extract_text(pdf_path):
    """Extract text from PDF."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout[:1000] if result.returncode == 0 else ""
    except:
        return ""

def detect(text):
    """Classify as CV or LDM based on content patterns."""

    text_lower = text.lower()

    # Strong CV signals
    cv_signals = [
        r'\bexperience\b',
        r'\beducation\b',
        r'\bskills\b',
    ]

    # Strong LDM signals
    ldm_signals = [
        r'^dear (sir|madam|hiring)',
        r'application for',
        r'appl(y|ying|icant)',
        r'sincerely|cordialement',
    ]

    cv_count = sum(1 for s in cv_signals if re.search(s, text_lower, re.MULTILINE))
    ldm_count = sum(1 for s in ldm_signals if re.search(s, text_lower, re.MULTILINE))

    if cv_count >= 2:
        return "CV"
    elif ldm_count >= 2:
        return "LDM"
    elif cv_count > ldm_count:
        return "CV"
    elif ldm_count > cv_count:
        return "LDM"
    else:
        # Fallback: check filename
        return None

def main():
    print("\n" + "="*80)
    print("DÉTECTION FINALE CV vs LDM — CANDIDATS 52-66")
    print("="*80 + "\n")

    # Group by candidate number
    by_candidate = {}

    for f in sorted(os.listdir(CV_DIR)):
        match = re.match(r'^(5[2-9]|6[0-6])-(.+?)-(cv|ldm)\.pdf$', f)
        if not match:
            continue

        num, slug, type_named = match.groups()

        if num not in by_candidate:
            by_candidate[num] = []

        pdf_path = os.path.join(CV_DIR, f)
        text = extract_text(pdf_path)
        detected = detect(text)

        by_candidate[num].append({
            'file': f,
            'named': type_named.upper(),
            'detected': detected or "?",
            'preview': text[:80].replace('\n', ' ')
        })

    # Print results
    mismatches = []

    for num in sorted(by_candidate.keys()):
        print(f"#{num} {by_candidate[num][0]['file'].split('-')[1:3]}")

        for item in by_candidate[num]:
            match = "✓" if item['named'] == item['detected'] else "✗"
            print(f"  {match} {item['file']:45} → {item['detected']}")

            if item['named'] != item['detected'] and item['detected'] != "?":
                mismatches.append({
                    'file': item['file'],
                    'named': item['named'],
                    'detected': item['detected']
                })

        print()

    # Summary
    print("="*80)
    print("MISMATCHES")
    print("="*80 + "\n")

    if mismatches:
        for m in mismatches:
            print(f"⚠️  {m['file']}")
            print(f"    Named: {m['named']} | Detected: {m['detected']}\n")
    else:
        print("✓ No mismatches detected.\n")

if __name__ == "__main__":
    main()
