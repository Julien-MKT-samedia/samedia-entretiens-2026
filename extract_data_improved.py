#!/usr/bin/env python3
"""
Étape 2: Extraction données améliorée pour candidats 52-66
- education, experiences, languages, skills
"""

import os
import json
import subprocess
import re

CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"
DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

# Patterns for extraction
EDUCATION_PATTERNS = [
    (r"(?:Master'?s?|M\.S\.|MSc|MBA|M\.A\.|MAI)\s+(?:in|of)?\s+([^,\n]{15,80})", 'Master'),
    (r"(?:Bachelor'?s?|B\.S\.|BSc|B\.A\.|BA|Licence|Licencié)\s+(?:in|of)?\s+([^,\n]{15,80})", 'Bachelor'),
    (r"(?:Diplôme|Certification|Cours|Formation|Degree)\s+(?:in|of)?\s+([^,\n]{20,80})", 'Degree'),
]

EXPERIENCE_TITLES = [
    r"Sales Manager", r"Business Development", r"Account Executive", r"Regional Manager",
    r"Commercial Director", r"Territory Manager", r"Sales Engineer",
    r"Sourcing Engineer", r"Project Manager", r"Field Engineer",
    r"Operations Manager", r"Technical Specialist", r"Consultant",
]

LANGUAGE_PATTERNS = [
    (r"English\s*[:-]?\s*([A-Z0-9,/ ]+)?", 'English'),
    (r"French\s*[:-]?\s*([A-Z0-9,/ ]+)?", 'French'),
    (r"Spanish\s*[:-]?\s*([A-Z0-9,/ ]+)?", 'Spanish'),
    (r"German\s*[:-]?\s*([A-Z0-9,/ ]+)?", 'German'),
    (r"Portuguese\s*[:-]?\s*([A-Z0-9,/ ]+)?", 'Portuguese'),
    (r"Italian\s*[:-]?\s*([A-Z0-9,/ ]+)?", 'Italian'),
    (r"Mandarin|Chinese\s*[:-]?\s*([A-Z0-9,/ ]+)?", 'Mandarin'),
    (r"Arabic\s*[:-]?\s*([A-Z0-9,/ ]+)?", 'Arabic'),
]

SKILLS_KEYWORDS = {
    'technical': [
        'Python', 'SQL', 'Excel', 'PowerBI', 'Tableau', 'SAP', 'ERP',
        'Salesforce', 'CRM', 'Hubspot', 'Jira', 'GitHub', 'AWS', 'Java',
        'JavaScript', 'C++', 'R', 'Power BI', 'Looker',
    ],
    'business': [
        'Negotiation', 'Leadership', 'Project Management', 'Communication',
        'Analysis', 'Sales', 'Marketing', 'Strategy', 'Business Development',
        'Account Management', 'Client Relations',
    ],
}

def extract_text(pdf_path):
    """Extract text from PDF."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else ""
    except:
        return ""

def extract_education(text):
    """Extract education entries."""
    education = []
    lines = text.split('\n')

    for line in lines[:100]:  # Check first 100 lines
        for pattern, degree_type in EDUCATION_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                program = match.group(1).strip() if match.lastindex else degree_type
                program = re.sub(r'\s+', ' ', program)[:60]
                if program and len(program) > 5:
                    education.append(program)
                    break

    return education[:3] if education else ["Not specified"]

def extract_experiences(text):
    """Extract job experiences."""
    experiences = []
    lines = text.split('\n')

    for line in lines[:200]:  # Check first 200 lines
        for title in EXPERIENCE_TITLES:
            if re.search(title, line, re.IGNORECASE):
                line_clean = line.strip()[:100]
                if line_clean and len(line_clean) > 10:
                    experiences.append(line_clean)
                    break

    return experiences[:3] if experiences else []

def extract_languages(text):
    """Extract languages with levels if available."""
    languages = set()
    text_lower = text.lower()

    for pattern, lang in LANGUAGE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            languages.add(lang)

    return sorted(list(languages)) or ['Not specified']

def extract_skills(text):
    """Extract technical and soft skills."""
    skills = set()
    text_lower = text.lower()

    for skill in SKILLS_KEYWORDS['technical']:
        if re.search(re.escape(skill), text, re.IGNORECASE):
            skills.add(skill)

    for skill in SKILLS_KEYWORDS['business']:
        if re.search(re.escape(skill), text, re.IGNORECASE):
            skills.add(skill)

    return sorted(list(skills))[:8] or ['Communication', 'Analysis']

def infer_strengths(score_details):
    """Generate strengths based on scoreDetails."""
    strengths = []

    labels = {
        'langues': {2: 'Anglais courant (C1-C2)', 1: 'Anglais professionnel (B1-B2)', 0: 'English basics'},
        'vente': {2: 'Expérience commerciale confirmée (manager)', 1: 'Expérience vente (commercial)', 0: 'No sales'},
        'prospection': {2: 'Profil terrain/prospection actif', 1: 'Support commercial', 0: 'No field'},
        'usa_exp': {2: 'Expérience/immersion USA documentée', 1: 'Expérience anglophone confirmée', 0: 'No experience'},
        'profil_marche': {2: 'Profil marché USA très adapté', 1: 'Profil marché adapté', 0: 'N/A'},
        'ancrage_culturel': {2: 'Ancrage culturel anglophone', 1: 'Expérience internationale', 0: 'No anchoring'},
    }

    for criterion, score in score_details.items():
        if score >= 1:
            strength = labels.get(criterion, {}).get(score, '')
            if strength:
                strengths.append(strength)

    return strengths[:5]

def main():
    print("\n" + "="*80)
    print("ÉTAPE 2: EXTRACTION DONNÉES AMÉLIORÉE (52-66)")
    print("="*80 + "\n")

    with open(DATA_JSON) as f:
        data = json.load(f)

    candidates = data['candidates']
    sorted_keys = sorted(candidates.keys(), key=lambda k: int(k.split('-')[0]))

    updated = 0

    for cand_key in sorted_keys:
        if not cand_key.startswith(('52-', '53-', '54-', '55-', '56-', '57-', '58-', '59-', '60-', '61-', '62-', '63-', '64-', '65-', '66-')):
            continue

        cand = candidates[cand_key]
        cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
        cv_path = os.path.join(CV_DIR, cv_file) if cv_file else None

        if not cv_path or not os.path.exists(cv_path):
            print(f"⚠️  {cand_key:30} CV not found")
            continue

        text = extract_text(cv_path)

        if not text:
            print(f"⚠️  {cand_key:30} Extraction failed")
            continue

        # Extract data
        education = extract_education(text)
        experiences = extract_experiences(text)
        languages = extract_languages(text)
        skills = extract_skills(text)
        strengths = infer_strengths(cand.get('scoreDetails', {}))

        # Update candidate
        if not cand.get('education') or cand.get('education') == ['Not specified']:
            cand['education'] = education
            updated += 1

        if not cand.get('experiences'):
            cand['experiences'] = experiences[:3]
            updated += 1

        if not cand.get('languages') or cand.get('languages') == ['Not specified']:
            cand['languages'] = languages
            updated += 1

        if not cand.get('skills') or len(cand.get('skills', [])) < 2:
            cand['skills'] = skills
            updated += 1

        if not cand.get('strengths') or cand.get('strengths') == ['Not specified']:
            cand['strengths'] = strengths
            updated += 1

        # Fix warnings
        if cand.get('warnings') is None:
            cand['warnings'] = []
            updated += 1

        print(f"✓ {cand_key:30} Education={len(education)}, Experiences={len(experiences)}, Skills={len(skills)}")

    # Save
    with open(DATA_JSON, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ {updated} updates made")
    print(f"✓ data.json saved")

if __name__ == "__main__":
    main()
