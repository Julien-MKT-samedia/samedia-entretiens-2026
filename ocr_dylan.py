#!/usr/bin/env python3
"""
OCR extract Dylan Dourlen's scanned PDF using tesseract
"""

import subprocess
import json

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def ocr_pdf(pdf_path):
    """Extract text from scanned PDF using tesseract."""
    try:
        result = subprocess.run(
            ["tesseract", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception as e:
        print(f"✗ OCR failed: {e}")
        return ""

# Load data
with open(DATA_JSON) as f:
    data = json.load(f)

# Extract Dylan's PDF path
dylan = data['candidates']['18-dylan-dourlen']
cv_file = dylan.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
cv_path = f"{CV_DIR}/{cv_file}"

print(f"\nOCR: {cv_file}")
print("=" * 80)

# OCR extract
text = ocr_pdf(cv_path)
chars = len(text)

print(f"Extracted: {chars} chars\n")

if chars < 200:
    print("✗ OCR failed, too few chars")
    print(f"Manual review needed for {cv_file}")
else:
    print(text[:500])
    print("\n... [rest truncated]")
    print(f"\n✓ {chars} chars extracted via OCR")

print("=" * 80)
