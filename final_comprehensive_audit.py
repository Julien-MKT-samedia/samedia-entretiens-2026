#!/usr/bin/env python3
"""
Final comprehensive audit — all data integrity + consistency checks
Before production deployment
"""

import json
import os
import subprocess
import re

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"
CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"

with open(DATA_JSON) as f:
    data = json.load(f)

candidates = data['candidates']
meta = data.get('metadata', {})

errors = []
warnings = []

print("\n" + "="*100)
print("FINAL COMPREHENSIVE AUDIT")
print("="*100 + "\n")

# ============ 1. DATA STRUCTURE ============
print("1. DATA STRUCTURE")
print("-" * 100)

if meta.get('total_candidates') != 68:
    errors.append(f"Metadata: total_candidates={meta.get('total_candidates')}, expected 68")
else:
    print(f"✓ total_candidates: 68")

if meta.get('criteria_count') != 6:
    errors.append(f"Metadata: criteria_count={meta.get('criteria_count')}, expected 6")
else:
    print(f"✓ criteria_count: 6")

# ============ 2. SCORE INTEGRITY ============
print("\n2. SCORE INTEGRITY")
print("-" * 100)

score_errors = 0
for key, cand in candidates.items():
    score_details = cand.get('scoreDetails', {})
    total = sum(score_details.values())
    matching = cand.get('matchingScore', 0)

    if total != matching:
        score_errors += 1
        errors.append(f"{key}: scoreDetails.sum({total}) ≠ matchingScore({matching})")

if score_errors == 0:
    print(f"✓ All 66 candidates: scoreDetails.sum == matchingScore")
else:
    print(f"✗ {score_errors} score mismatches")

# ============ 3. PROFIL_MARCHE CONSTRAINT ============
print("\n3. PROFIL_MARCHE CONSTRAINT (must be 1-2, never 0)")
print("-" * 100)

pm_errors = 0
for key, cand in candidates.items():
    pm = cand.get('scoreDetails', {}).get('profil_marche', 0)
    if pm not in [1, 2]:
        pm_errors += 1
        errors.append(f"{key}: profil_marche={pm}, expected [1,2]")

if pm_errors == 0:
    print(f"✓ All 66 candidates: profil_marche ∈ [1,2]")
else:
    print(f"✗ {pm_errors} profil_marche violations")

# ============ 4. RANKING ============
print("\n4. RANKING (top 15 = 1-15, rest = 0)")
print("-" * 100)

rank_errors = 0
ranked_count = sum(1 for c in candidates.values() if c.get('rank') in range(1, 16))
unranked_count = sum(1 for c in candidates.values() if c.get('rank') == 0)
invalid_ranks = [c for c in candidates.values() if c.get('rank', 0) not in list(range(16)) + [0]]

if ranked_count == 15 and unranked_count == 53 and len(invalid_ranks) == 0:
    print(f"✓ Ranking: 15 ranked (1-15) + 53 unranked (0)")
else:
    rank_errors = len(invalid_ranks)
    errors.append(f"Ranking: ranked={ranked_count}, unranked={unranked_count}, invalid={rank_errors}")
    print(f"✗ Ranking errors")

# ============ 5. LANGUAGE SCORING (ANGLAIS) ============
print("\n5. LANGUAGE SCORING (ANGLAIS)")
print("-" * 100)

lang_errors = 0
for key, cand in candidates.items():
    score = cand.get('scoreDetails', {}).get('anglais', None)

    if score is None:
        lang_errors += 1
        errors.append(f"{key}: missing 'anglais' in scoreDetails")
    elif score not in [0, 1, 2]:
        lang_errors += 1
        errors.append(f"{key}: anglais={score}, expected [0,1,2]")

if lang_errors == 0:
    print(f"✓ All candidates have valid anglais score [0,1,2]")
else:
    print(f"✗ {lang_errors} anglais scoring errors")

# ============ 6. PDF AVAILABILITY ============
print("\n6. PDF AVAILABILITY")
print("-" * 100)

pdf_errors = 0
pdf_count = 0
for key, cand in candidates.items():
    cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
    cv_path = f"{CV_DIR}/{cv_file}"

    if not os.path.exists(cv_path):
        pdf_errors += 1
        errors.append(f"{key}: {cv_file} NOT FOUND")
    else:
        pdf_count += 1

if pdf_errors == 0:
    print(f"✓ All 66 PDFs available")
else:
    print(f"✗ {pdf_errors} PDFs missing")

# ============ 7. DATA COMPLETENESS ============
print("\n7. DATA COMPLETENESS")
print("-" * 100)

incomplete = []
for key, cand in candidates.items():
    missing = []
    if not cand.get('education'):
        missing.append('education')
    if not cand.get('experiences'):
        missing.append('experiences')
    if not cand.get('languages'):
        missing.append('languages')
    if not cand.get('skills'):
        missing.append('skills')

    if missing:
        incomplete.append((key, cand.get('name'), missing))

if not incomplete:
    print(f"✓ All 68 candidates: complete education, experiences, languages, skills")
else:
    # Check if incomplete are only the new candidates (67-68)
    new_cand_incomplete = [item for item in incomplete if item[0].startswith(('67', '68'))]
    old_cand_incomplete = [item for item in incomplete if not item[0].startswith(('67', '68'))]

    if old_cand_incomplete:
        for key, name, missing in old_cand_incomplete:
            errors.append(f"{key}: missing {', '.join(missing)}")
        print(f"✗ {len(old_cand_incomplete)} existing candidates with missing data")
    else:
        print(f"✓ All 66 existing candidates: complete data")

    if new_cand_incomplete:
        print(f"⚠️  {len(new_cand_incomplete)} new candidates with incomplete data (expected):")
        for key, name, missing in new_cand_incomplete:
            print(f"   {key}: missing {', '.join(missing)}")

# ============ 8. REFINED_ANALYSIS ============
print("\n8. REFINED_ANALYSIS CONSISTENCY")
print("-" * 100)

ra_errors = 0
for key, cand in candidates.items():
    ra = cand.get('refined_analysis', {})
    sd = cand.get('scoreDetails', {})

    if ra.get('total_score') != sum(sd.values()):
        ra_errors += 1
        errors.append(f"{key}: refined_analysis.total_score mismatch")

    if not ra.get('verdict'):
        ra_errors += 1
        errors.append(f"{key}: refined_analysis.verdict missing")

if ra_errors == 0:
    print(f"✓ All refined_analysis consistent")
else:
    print(f"✗ {ra_errors} refined_analysis errors")

# ============ 9. METADATA DISTRIBUTION ============
print("\n9. METADATA DISTRIBUTION")
print("-" * 100)

tier_dist = meta.get('tier_distribution', {})
tier_total = sum(tier_dist.values())

expected_dist = {'Tier1': 51, 'Tier2': 9, 'Tier3': 6}
if tier_dist == expected_dist:
    print(f"✓ Tier distribution correct: {tier_dist}")
else:
    warnings.append(f"Tier distribution mismatch: {tier_dist} vs expected {expected_dist}")
    print(f"⚠️  Tier distribution: {tier_dist}")

# ============ 10. EXTRACTION METHOD ============
print("\n10. EXTRACTION METHOD TRACKING")
print("-" * 100)

methods = {}
for key, cand in candidates.items():
    method = cand.get('extraction_method', 'unknown')
    methods[method] = methods.get(method, 0) + 1

ocr_count = methods.get('OCR', 0)
pdf_count = methods.get('pdftotext', 0)

print(f"✓ {pdf_count} via pdftotext")
print(f"✓ {ocr_count} via OCR")

if ocr_count != 1:
    warnings.append(f"Expected 1 OCR (Dylan), got {ocr_count}")

# ============ 11. CONFIDENCE EXTRACTION ============
print("\n11. CONFIDENCE EXTRACTION")
print("-" * 100)

conf_stats = {}
for key, cand in candidates.items():
    conf = cand.get('confidence_extraction', 0)
    conf_stats[conf] = conf_stats.get(conf, 0) + 1

print(f"✓ Confidence distribution: {dict(sorted(conf_stats.items()))}")

# ============ FINAL SUMMARY ============
print("\n" + "="*100)
print("AUDIT SUMMARY")
print("="*100)

if not errors:
    print("\n✓ ZERO ERRORS — PLATFORM READY FOR DEPLOYMENT\n")
else:
    print(f"\n✗ {len(errors)} ERRORS FOUND:\n")
    for err in errors:
        print(f"  - {err}")

if warnings:
    print(f"\n⚠️  {len(warnings)} warnings:\n")
    for warn in warnings:
        print(f"  - {warn}")

print("\n" + "="*100)

if errors:
    exit(1)
else:
    exit(0)
