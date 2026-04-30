#!/usr/bin/env python3
"""Add extraction_method to all candidates (pdftotext for most, OCR for Dylan)"""

import json

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

for key, cand in candidates.items():
    if not cand.get('extraction_method'):
        if key == '18-dylan-dourlen':
            cand['extraction_method'] = 'OCR'
        else:
            cand['extraction_method'] = 'pdftotext'

with open(DATA_JSON, 'w') as f:
    json.dump(data, f, indent=2)

print("✓ extraction_method added to all 66 candidates")
