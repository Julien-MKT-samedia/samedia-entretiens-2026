#!/usr/bin/env python3
"""
Audit English levels across all candidates
Check consistency: C1/C2 should all score 2, B1/B2 should score 1, etc.
"""

import json
import re

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']

# Categorize by English level
levels = {
    'C1/C2': [],
    'B1/B2': [],
    'Basic': [],
    'Not detected': [],
}

print("\n" + "="*100)
print("ENGLISH LEVELS AUDIT")
print("="*100 + "\n")

for key, cand in sorted(candidates.items()):
    langs = cand.get('languages', [])
    score = cand.get('scoreDetails', {}).get('langues', 0)

    # Find English entry
    english_entry = None
    for lang in langs:
        if 'english' in lang.lower() or 'anglais' in lang.lower():
            english_entry = lang
            break

    if not english_entry:
        levels['Not detected'].append((key, cand.get('name', '?'), score))
    elif any(x in english_entry.lower() for x in ['c1', 'c2', 'native', 'bilingual']):
        levels['C1/C2'].append((key, cand.get('name', '?'), english_entry, score))
    elif any(x in english_entry.lower() for x in ['b1', 'b2', 'fluent', 'professional']):
        levels['B1/B2'].append((key, cand.get('name', '?'), english_entry, score))
    else:
        levels['Basic'].append((key, cand.get('name', '?'), english_entry, score))

# Report
print("C1/C2 (should all score 2):")
print("-" * 100)
c1_errors = []
for key, name, level, score in levels['C1/C2']:
    status = "✓" if score == 2 else "✗"
    print(f"{status} {key:30} {name:30} {level:30} → {score}/2")
    if score != 2:
        c1_errors.append((key, name, level, score))

print(f"\nB1/B2 (should score 1-2):")
print("-" * 100)
b_errors = []
for key, name, level, score in levels['B1/B2']:
    status = "✓" if score in [1, 2] else "✗"
    print(f"{status} {key:30} {name:30} {level:30} → {score}/2")
    if score not in [1, 2]:
        b_errors.append((key, name, level, score))

print(f"\nBasic English:")
print("-" * 100)
for key, name, level, score in levels['Basic']:
    print(f"  {key:30} {name:30} {level:30} → {score}/2")

print(f"\nNot detected (no English):")
print("-" * 100)
for key, name, score in levels['Not detected']:
    print(f"  {key:30} {name:30} → {score}/2")

# Summary
print("\n" + "="*100)
print("SUMMARY")
print("="*100)
print(f"C1/C2: {len(levels['C1/C2'])} candidates ({len(c1_errors)} scoring errors)")
print(f"B1/B2: {len(levels['B1/B2'])} candidates ({len(b_errors)} scoring errors)")
print(f"Basic: {len(levels['Basic'])} candidates")
print(f"No English: {len(levels['Not detected'])} candidates")

if c1_errors or b_errors:
    print(f"\n⚠️  ERRORS FOUND: {len(c1_errors) + len(b_errors)} candidates")
    print("\nErrors to fix:")
    for key, name, level, score in c1_errors + b_errors:
        print(f"  {key}: {name} — {level} scores {score}/2 (should be 2)")
else:
    print("\n✓ All English levels consistent")

print("=" * 100 + "\n")
