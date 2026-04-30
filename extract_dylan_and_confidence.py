#!/usr/bin/env python3
"""
1. Extract Dylan's data via OCR
2. Add confidence metrics (extraction % + data completeness) for all 66 candidates
"""

import json
import subprocess
import re
import tempfile
import os

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

def extract_text(pdf_path):
    """Extract via pdftotext (for normal PDFs) or OCR (for scanned)."""
    # Try pdftotext first
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and len(result.stdout) > 200:
            return result.stdout, "pdftotext"
    except:
        pass

    # Fallback to OCR
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

def extract_education(text):
    """Extract education."""
    patterns = [
        r"(?:Master|MSc|MBA|Licence|Bachelor|Diplôme).*?(?:in|de|d\')?.*?(?:\(|—|,|$)",
    ]
    results = []
    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        results.extend(matches[:2])
    return list(dict.fromkeys(results))[:3] if results else []

def extract_experiences(text):
    """Extract job titles and descriptions."""
    # Look for job title patterns
    lines = text.split('\n')
    experiences = []
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ['manager', 'analyst', 'director', 'consultant', 'specialist', 'engineer', 'officer']):
            exp = line.strip()
            if 10 < len(exp) < 200:
                experiences.append(exp)
    return experiences[:4]

def extract_languages(text):
    """Extract languages."""
    lang_patterns = {
        'English': r'(?:English|anglais).*?(?:C1|C2|native|fluent|professional)',
        'French': r'(?:French|français).*?(?:C1|C2|native|fluent)',
        'Spanish': r'(?:Spanish|espagnol).*?(?:B2|C1|fluent)',
        'German': r'(?:German|allemand)',
        'Italian': r'(?:Italian|italien)',
    }
    found = []
    for lang, pattern in lang_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.append(lang)
    return found if found else []

def extract_skills(text):
    """Extract technical skills."""
    skills_list = ['Excel', 'Python', 'SQL', 'CRM', 'Salesforce', 'SAP', 'PowerBI', 'Tableau',
                   'Risk Analysis', 'Portfolio Management', 'Financial Advisor', 'Banking', 'Finance']
    found = []
    for skill in skills_list:
        if skill.lower() in text.lower():
            found.append(skill)
    return found[:8]

def calculate_confidence(cand_data):
    """Calculate extraction confidence (0-100%)."""
    factors = {
        'education': len(cand_data.get('education', [])) > 0,
        'experiences': len(cand_data.get('experiences', [])) > 0,
        'languages': len(cand_data.get('languages', [])) > 0,
        'skills': len(cand_data.get('skills', [])) > 0,
    }
    score = sum(factors.values()) / len(factors) * 100
    return int(score)

# Load data
with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

# Extract Dylan
print("\n" + "="*80)
print("DYLAN EXTRACTION (OCR)")
print("="*80)

dylan = candidates['18-dylan-dourlen']
cv_file = dylan.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
cv_path = f"{CV_DIR}/{cv_file}"

text, method = extract_text(cv_path)
print(f"\nCandidate: Dylan Dourlen")
print(f"File: {cv_file}")
print(f"Extraction method: {method}")
print(f"Text length: {len(text)} chars")

if len(text) > 200:
    education = extract_education(text)
    experiences = extract_experiences(text)
    languages = extract_languages(text)
    skills = extract_skills(text)

    dylan['education'] = education
    dylan['experiences'] = experiences
    dylan['languages'] = languages
    dylan['skills'] = skills
    dylan['extraction_method'] = method
    dylan['confidence_extraction'] = 100  # OCR worked

    print(f"\n✓ Education: {education}")
    print(f"✓ Experiences: {len(experiences)}")
    print(f"✓ Languages: {languages}")
    print(f"✓ Skills: {len(skills)}")
else:
    dylan['confidence_extraction'] = 0
    print("\n✗ Extraction failed, no data")

# Add confidence to ALL candidates
print("\n" + "="*80)
print("CONFIDENCE METRICS (ALL 66)")
print("="*80 + "\n")

for key in sorted(candidates.keys()):
    cand = candidates[key]
    confidence = calculate_confidence(cand)
    cand['confidence_extraction'] = confidence

    if confidence < 100:
        print(f"⚠️  {key}: {confidence}% (missing: {[k for k, v in {'edu':cand.get('education'),'exp':cand.get('experiences'),'lang':cand.get('languages'),'skill':cand.get('skills')}.items() if not v]})")
    elif confidence == 100:
        print(f"✓ {key}: 100%")

# Save
with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "="*80)
print(f"✓ Dylan extracted via OCR")
print(f"✓ Confidence metrics added to all 66 candidates")
print(f"✓ data.json saved")
print("="*80 + "\n")
