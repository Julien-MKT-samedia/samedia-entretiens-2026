#!/usr/bin/env python3
import os
import json
import re
import sys
from pathlib import Path
import subprocess

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

SOURCE_DIR = Path("/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/Candidature-VIE-SAMEDIA-USA-2026/CVs VIE USA")
DEST_DIR = Path("/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026")
CVS_DIR = DEST_DIR / "cvs"
CVS_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    try:
        result = subprocess.run(['pdftotext', str(pdf_path), '-'],
                              capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return ""

def extract_text_from_docx(docx_path):
    if not HAS_DOCX:
        return ""
    try:
        doc = Document(docx_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return ""

def extract_text(file_path):
    if file_path.suffix.lower() == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() == '.docx':
        return extract_text_from_docx(file_path)
    return ""

def slugify(name):
    name = name.lower().strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name.strip('-')

def calculate_score(text):
    text_lower = text.lower()
    scores = {}

    # English (0-2)
    if any(kw in text_lower for kw in ['native english', 'native speaker', 'c1', 'c2', 'bilingual', 'native']):
        scores['english'] = 2
    elif any(kw in text_lower for kw in ['b1', 'b2', 'fluent', 'proficient', 'toefl', 'ielts', 'upper-intermediate', 'advanced english']):
        scores['english'] = 1
    else:
        scores['english'] = 0

    # Sales (0-2)
    if any(kw in text_lower for kw in ['b2b', 'sales manager', 'account executive', 'business development', 'account manager', 'commercial manager']):
        scores['sales'] = 2
    elif any(kw in text_lower for kw in ['sales', 'vente', 'commercial', 'retail', 'customer', 'client']):
        scores['sales'] = 1
    else:
        scores['sales'] = 0

    # Field/Prospection (0-2)
    if any(kw in text_lower for kw in ['prospecting', 'field', 'territory', 'prospection', 'terrain', 'hunting', 'new business', 'commercial']):
        scores['field'] = 2
    elif any(kw in text_lower for kw in ['support', 'back office', 'administrative']):
        scores['field'] = 1
    else:
        scores['field'] = 0

    # USA Immersion (0-2)
    if any(kw in text_lower for kw in ['usa', 'united states', 'new york', 'california', 'texas', 'florida', 'chicago', 'los angeles']):
        if any(k in text_lower for k in ['year', 'month', 'internship', 'experience', 'worked', 'lived']):
            scores['usa'] = 2
        else:
            scores['usa'] = 1
    elif any(kw in text_lower for kw in ['uk', 'canada', 'australia', 'ireland', 'new zealand']):
        scores['usa'] = 1
    else:
        scores['usa'] = 0

    # US Market Fit (1-2)
    if any(kw in text_lower for kw in ['construction', 'demolition', 'mining', 'drilling', 'concrete', 'stone', 'granite', 'marble', 'equipment', 'machinery', 'contractor', 'btp', 'tp']):
        scores['market_fit'] = 2
    else:
        scores['market_fit'] = 1

    # Cultural Anchoring (0-2)
    if any(kw in text_lower for kw in ['british', 'american', 'australian', 'canadian', 'irish', 'native english']):
        scores['culture'] = 2
    elif any(kw in text_lower for kw in ['international', 'expat', 'multinational', 'global']):
        scores['culture'] = 1
    else:
        scores['culture'] = 0

    total = sum(scores.values())
    return total, scores

def extract_name(folder_path):
    folder_name = folder_path.name
    match = re.match(r'^\d+\s+(.+)$', folder_name)
    return match.group(1).strip() if match else folder_name

def extract_email_phone(text):
    email = None
    phone = None
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        email = email_match.group()
    phone_match = re.search(r'(?:\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{4,}', text)
    if phone_match:
        phone = phone_match.group()
    return email, phone

def extract_education(text):
    # Try to find education lines
    education = None

    patterns = [
        r'(?:Master|M\.S|MBA|M\.Sc|Diploma|Bachelor|B\.S|Licence|Ingénieur|License|Master\'?s).*?(?:,|$)',
        r'(?:Université|University|École|School|College|Institut).*?(?:,|$)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            text_snippet = match.group().strip()
            if text_snippet:
                education = text_snippet[:100]
                break

    return education or "Non spécifié"

def extract_experiences(text):
    """Extract key experiences from CV"""
    experiences = []
    lines = text.split('\n')

    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Look for job titles/experience markers
        if any(kw in line_lower for kw in ['experience', 'position', 'role', 'manager', 'developer', 'engineer', 'coordinator', 'business', 'sales', 'commercial']):
            # Get this line + next non-empty line if it makes sense
            if 15 < len(line.strip()) < 150:
                experiences.append(line.strip())
                if len(experiences) >= 3:
                    break

    return experiences[:3]

def extract_skills(text):
    """Extract mentioned skills"""
    skills = []

    skill_keywords = [
        'sales', 'negotiation', 'prospecting', 'business development', 'account management',
        'python', 'excel', 'crm', 'salesforce', 'sap', 'project management',
        'communication', 'leadership', 'teamwork', 'problem-solving', 'analysis'
    ]

    text_lower = text.lower()

    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill)

    return list(set(skills))[:5]

def generate_tier1_questions(name, scores, experiences, education):
    """Tier 1: 6 catégories x 4-5 questions = ~25"""
    return {
        'communication': [
            f"{name}, parlez-nous de votre expérience dans la communication commerciale en anglais.",
            "Comment vous êtes-vous préparé pour des négociations en anglais ?",
            "Avez-vous une expérience de présentations commerciales devant des clients internationaux ?"
        ],
        'sales_business': [
            "Décrivez votre plus grand succès commercial. Comment avez-vous remporté ce marché ?",
            "Quel est votre approche pour développer un portefeuille de nouveaux clients ?",
            "Comment évaluez-vous et qualifiez-vous les opportunités B2B ?",
            "Parlez d'une situation où vous avez négocié un contrat important."
        ],
        'market_usa': [
            "Que savez-vous du marché américain des outils/équipements BTP ?",
            "Avez-vous une expérience directe aux USA ? Si oui, dans quels États/régions ?",
            "Comment comprenez-vous les différences entre le marché US et français/européen ?"
        ],
        'samedia_fit': [
            "Que connaissez-vous de SAMEDIA, ses produits et sa position marché ?",
            "Comment envisagez-vous d'aborder les clients dans le secteur construction/démolition ?",
            "Quelle région ou État des USA vous intéresse le plus pour cette mission ?"
        ],
        'motivation_carrier': [
            "Pourquoi souhaitez-vous faire un VIE aux USA spécifiquement ?",
            "Quel est votre objectif carrière à court et moyen terme ?",
            "Comment ce VIE s'inscrit-il dans votre parcours professionnel ?"
        ],
        'logistics': [
            "Durée souhaitée du VIE et votre disponibilité ?",
            "Avez-vous des contraintes géographiques (régions préférées/à éviter) ?",
            "Comment voyez-vous l'équilibre vie professionnelle/personnelle lors de ce VIE ?"
        ]
    }

def generate_tier2_questions(name, scores):
    """Tier 2: ~12 questions"""
    return {
        'basics': [
            f"Présentez-vous en une minute : formation, expérience clé, motivations.",
            "Quel est votre niveau d'anglais ? Avez-vous des certifications ?"
        ],
        'experience': [
            "Avez-vous une expérience de vente ou développement commercial ?",
            "Quelle expérience terrain ou de terrain avez-vous ?"
        ],
        'market': [
            "Connaissez-vous le marché USA ? De quelle manière ?",
            "Avez-vous des contacts ou réseaux aux USA ?"
        ],
        'samedia': [
            "Connaissez-vous SAMEDIA ou le secteur diamant/BTP ?",
            "Comment vous voyez-vous développer chez SAMEDIA ?"
        ],
        'motivation': [
            "Pourquoi ce VIE ? Pourquoi les USA particulièrement ?"
        ],
        'logistics': [
            "Durée souhaitée et date de disponibilité ?"
        ]
    }

def generate_tier3_questions():
    """Tier 3: 5 questions globales"""
    return {
        'general': [
            "Présentez-vous : formation, expérience professionnelle, motivations pour ce VIE (2-3 min).",
            "Quel est votre niveau d'anglais et comment pouvez-vous le justifier ?",
            "Avez-vous une expérience en vente, commercial ou prospection terrain ?",
            "Pourquoi SAMEDIA et pourquoi un VIE aux USA vous attire ?",
            "Durée souhaitée, date de départ possible, et secteurs/régions USA préférées ?"
        ]
    }

def process_all():
    candidates = {}
    folders = sorted([d for d in SOURCE_DIR.iterdir() if d.is_dir()])

    for idx, folder in enumerate(folders, 1):
        try:
            name = extract_name(folder)
            slug = slugify(name)

            # Trouver CV et LDM
            files = [f for f in folder.glob('*') if f.suffix.lower() in ['.pdf', '.docx']]
            cv_file = None
            ldm_file = None

            for f in files:
                name_lower = f.name.lower()
                if any(kw in name_lower for kw in ['cv', 'resume', 'curriculum']):
                    cv_file = f
                elif any(kw in name_lower for kw in ['ldm', 'letter', 'motivation', 'cover']):
                    ldm_file = f

            # Fallback
            if not cv_file and files:
                cv_file = files[0]
                ldm_file = files[1] if len(files) > 1 else None

            if not cv_file:
                print(f"[{idx:2d}] {name:30s} | SKIPPED: No CV found")
                continue

            # Extract text
            cv_text = extract_text(cv_file)
            ldm_text = extract_text(ldm_file) if ldm_file else ""
            combined = cv_text + "\n" + ldm_text

            if not cv_text:
                print(f"[{idx:2d}] {name:30s} | SKIPPED: Could not extract text")
                continue

            score, scores = calculate_score(combined)
            tier = 1 if score >= 7 else (2 if score >= 4 else 3)

            email, phone = extract_email_phone(combined)
            education = extract_education(combined)
            experiences = extract_experiences(combined)

            # Copy and rename files
            cv_dest_name = f"{slug}-cv{cv_file.suffix}"
            cv_dest = CVS_DIR / cv_dest_name
            cv_dest.write_bytes(cv_file.read_bytes())

            ldm_dest = None
            ldm_dest_name = None
            if ldm_file:
                ldm_dest_name = f"{slug}-ldm{ldm_file.suffix}"
                ldm_dest = CVS_DIR / ldm_dest_name
                ldm_dest.write_bytes(ldm_file.read_bytes())

            strengths = []
            if scores['english'] >= 2:
                strengths.append("Anglais natif/très avancé")
            if scores['english'] == 1:
                strengths.append("Anglais intermédiaire/avancé")
            if scores['sales'] >= 2:
                strengths.append("Expérience B2B confirmée")
            if scores['field'] >= 2:
                strengths.append("Profil terrain/prospection")
            if scores['usa'] >= 2:
                strengths.append("Expérience USA documentée")

            warnings = []
            if scores['english'] == 0:
                warnings.append("Niveau anglais à valider")
            if scores['sales'] == 0:
                warnings.append("Peu/pas d'expérience vente identifiée")
            if scores['field'] == 0:
                warnings.append("Pas de profil terrain documenté")
            if score <= 3:
                warnings.append("Score très faible (<4)")
            if score <= 5:
                warnings.append("Score faible (4-5) - nécessite validation")

            # Generate questions
            if tier == 1:
                questions = generate_tier1_questions(name, scores, experiences, education)
            elif tier == 2:
                questions = generate_tier2_questions(name, scores)
            else:
                questions = generate_tier3_questions()

            candidate = {
                'id': f"{idx:02d}-{slug}",
                'number': idx,
                'name': name,
                'tier': tier,
                'matchingScore': score,
                'scoreDetails': scores,
                'location': "USA (TBD)",
                'contact': {
                    'email': email,
                    'phone': phone
                },
                'education': education,
                'experiences': experiences,
                'strengths': strengths,
                'warnings': warnings,
                'cvFile': f"recrutements/vie-usa-2026/cvs/{cv_dest_name}",
                'ldmFile': f"recrutements/vie-usa-2026/cvs/{ldm_dest_name}" if ldm_dest else None,
                'questions': questions
            }

            candidates[candidate['id']] = candidate
            status = f"Score {score}/12 (T{tier})"
            print(f"[{idx:2d}] {name:30s} | {status:20s} | {email or 'N/A'}")

        except Exception as e:
            print(f"[{idx:2d}] ERROR: {e}")

    return candidates

def main():
    print("\n=== Processing 51 CVs for SAMEDIA VIE USA ===\n")
    candidates = process_all()

    tier1 = len([c for c in candidates.values() if c['tier'] == 1])
    tier2 = len([c for c in candidates.values() if c['tier'] == 2])
    tier3 = len([c for c in candidates.values() if c['tier'] == 3])

    data = {
        'metadata': {
            'total_candidates': len(candidates),
            'tier_distribution': {
                'tier1': tier1,
                'tier2': tier2,
                'tier3': tier3
            },
            'scoring_system': {
                'english_proficiency': '0-2 pts',
                'sales_experience': '0-2 pts',
                'field_prospection': '0-2 pts',
                'usa_immersion': '0-2 pts',
                'us_market_fit': '1-2 pts',
                'cultural_anchoring': '0-2 pts',
                'max_score': 12,
                'tier1_threshold': '≥7',
                'tier2_threshold': '4-6',
                'tier3_threshold': '<4'
            },
            'generated': '2026-04-29'
        },
        'candidates': candidates
    }

    output = DEST_DIR / 'data.json'
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    print(f"\n=== SUMMARY ===")
    print(f"Total candidates processed: {len(candidates)}")
    print(f"Tier 1 (score ≥7): {tier1}")
    print(f"Tier 2 (score 4-6): {tier2}")
    print(f"Tier 3 (score <4): {tier3}")
    print(f"\nGenerated: {output}")

    # Top 15
    top15 = sorted([c for c in candidates.values()], key=lambda x: x['matchingScore'], reverse=True)[:15]
    print(f"\n=== TOP 15 CANDIDATES ===")
    for i, c in enumerate(top15, 1):
        print(f"{i:2d}. {c['name']:30s} | Score {c['matchingScore']}/12 (T{c['tier']}) | {c['contact']['email'] or 'N/A'}")

if __name__ == '__main__':
    main()
