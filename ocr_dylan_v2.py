#!/usr/bin/env python3
"""
OCR Dylan via PDF → PNG → tesseract (handles protected PDFs)
"""

import subprocess
import json
import os
import tempfile

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def pdf_to_ppm(pdf_path, temp_dir):
    """Convert PDF pages to PPM images."""
    try:
        result = subprocess.run(
            ["pdftoppm", pdf_path, os.path.join(temp_dir, "page")],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"✗ PDF convert failed: {e}")
        return False

def ocr_images(image_dir):
    """OCR all PPM images in directory."""
    try:
        result = subprocess.run(
            ["tesseract", os.path.join(image_dir, "page-*.ppm"), "-"],
            capture_output=True,
            text=True,
            timeout=60,
            shell=False
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception as e:
        print(f"✗ OCR failed: {e}")
        return ""

# Load data
with open(DATA_JSON) as f:
    data = json.load(f)

dylan = data['candidates']['18-dylan-dourlen']
cv_file = dylan.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
cv_path = f"{CV_DIR}/{cv_file}"

print(f"\nOCR (with PDF conversion): {cv_file}")
print("=" * 80)

# Temp dir for images
with tempfile.TemporaryDirectory() as temp_dir:
    print("1. Converting PDF → PNG...")
    if not pdf_to_ppm(cv_path, temp_dir):
        print("✗ PDF conversion failed")
        exit(1)

    # List generated files
    images = [f for f in os.listdir(temp_dir) if f.startswith('page')]
    print(f"   ✓ {len(images)} pages converted")

    print("2. Running tesseract on images...")
    # OCR each image separately (safer)
    all_text = []
    for img in sorted(images):
        img_path = os.path.join(temp_dir, img)
        try:
            result = subprocess.run(
                ["tesseract", img_path, "-"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                all_text.append(result.stdout)
        except:
            pass

    text = "\n".join(all_text)

chars = len(text)
print(f"\n✓ Extracted: {chars} chars\n")

if chars > 200:
    print(text[:500])
    print("\n... [rest truncated]\n")
    print(f"✓ Success: {chars} chars extracted")
else:
    print("✗ Still failed — PDF may be protected/corrupted")
    print("Manual data entry needed")

print("=" * 80)
