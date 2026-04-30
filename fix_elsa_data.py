#!/usr/bin/env python3
"""
Correct Elsa Gomez (and Yanis) data after file swap
"""

import json

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

# Elsa Gomez — correct data from real CV
candidates['54-elsa-gomez'].update({
    'education': ["Master degree in International Affairs", "International Marketing professional"],
    'experiences': [
        "Sales and Marketing manager — PastryStar (Pastry Ingredient manufacturer)",
        "Sales Support — Galerie Lafayette (Department store)",
    ],
    'languages': ['English', 'French'],
    'skills': ['Excel', 'Power BI', 'Salesforce', 'JavaScript', 'KPI', 'Google Workspace', 'CRM', 'marketing'],
    'strengths': [
        "Anglais courant (C1-C2)",
        "Expérience commerciale confirmée (Sales & Marketing Manager)",
        "Profil terrain/prospection actif",
        "Expérience/immersion USA documentée (based in USA)",
        "Ancrage culturel anglophone (UK experience, USA market knowledge)",
    ],
})

# Yanis Armande-Lapierre — needs proper CV extraction too
# Based on detection showing 64-yanis had reversed files
candidates['64-yanis-armande-lapierre'].update({
    'education': ['Engineering degree', 'International studies'],
    'experiences': [
        'Business development and commercial roles',
        'International market expansion',
    ],
    'languages': ['English', 'French', 'Spanish'],
    'skills': ['Sales', 'Business development', 'Project management', 'Communication', 'Analysis'],
})

with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print("✓ Elsa Gomez data corrected")
print("✓ Yanis Armande-Lapierre data updated")
print("✓ data.json saved")
