#!/usr/bin/env python3
"""
Étape 6: Final end-to-end tests
- Data integrity
- PDF availability
- Display validation
"""

import json
import os

DATA_JSON = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json"
CV_DIR = "/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/cvs"

def test_data_integrity():
    """Verify scoreDetails.sum == matchingScore for all candidates."""
    print("\n1. DATA INTEGRITY TEST\n")

    with open(DATA_JSON) as f:
        data = json.load(f)

    candidates = data['candidates']
    errors = 0

    for key, cand in candidates.items():
        score_details = cand.get('scoreDetails', {})
        score_sum = sum(score_details.values())
        matching_score = cand.get('matchingScore', 0)

        if score_sum != matching_score:
            print(f"✗ {key}: sum({score_sum}) ≠ matchingScore({matching_score})")
            errors += 1

    if errors == 0:
        print(f"✓ All {len(candidates)} candidates: scoreDetails.sum == matchingScore")
    else:
        print(f"✗ {errors} mismatches found")

    return errors == 0

def test_pdf_availability():
    """Check PDF files for 5 test candidates."""
    print("\n2. PDF AVAILABILITY TEST\n")

    with open(DATA_JSON) as f:
        data = json.load(f)

    candidates = data['candidates']

    # Select 5 test candidates: 1st (01), 26th, 51st, 54th, 66th
    test_keys = ['01-orlane-degras', '26-aadnan-el-fahsi', '51-clement-assier', '54-elsa-gomez', '66-romain-poirier']

    missing = 0
    for key in test_keys:
        if key not in candidates:
            print(f"✗ {key}: not in data.json")
            missing += 1
            continue

        cand = candidates[key]
        cv_file = cand.get('cvFile', '').replace('recrutements/vie-usa-2026/cvs/', '')
        cv_path = os.path.join(CV_DIR, cv_file)

        if os.path.exists(cv_path):
            size_mb = os.path.getsize(cv_path) / (1024*1024)
            print(f"✓ {key}: {cv_file} ({size_mb:.1f} MB)")
        else:
            print(f"✗ {key}: {cv_file} not found")
            missing += 1

    if missing == 0:
        print(f"\n✓ All test PDFs available")
    else:
        print(f"\n✗ {missing} PDFs missing")

    return missing == 0

def test_ranking():
    """Verify top 15 ranking."""
    print("\n3. RANKING TEST\n")

    with open(DATA_JSON) as f:
        data = json.load(f)

    candidates = data['candidates']

    # Find top 15
    sorted_cands = sorted(candidates.items(), key=lambda x: -x[1]['matchingScore'])

    rank_errors = 0
    for idx, (key, cand) in enumerate(sorted_cands[:15]):
        expected_rank = idx + 1
        actual_rank = cand.get('rank')

        if actual_rank != expected_rank:
            print(f"✗ {key}: rank={actual_rank}, expected={expected_rank}")
            rank_errors += 1

    if rank_errors == 0:
        print(f"✓ Top 15 correctly ranked (1-15)")
        print(f"  1. {sorted_cands[0][1]['name']} ({sorted_cands[0][1]['matchingScore']}/12)")
        print(f"  2. {sorted_cands[1][1]['name']} ({sorted_cands[1][1]['matchingScore']}/12)")
        print(f"  3. {sorted_cands[2][1]['name']} ({sorted_cands[2][1]['matchingScore']}/12)")
    else:
        print(f"✗ {rank_errors} ranking errors")

    return rank_errors == 0

def test_metadata():
    """Verify metadata."""
    print("\n4. METADATA TEST\n")

    with open(DATA_JSON) as f:
        data = json.load(f)

    meta = data.get('metadata', {})

    checks = [
        ('total_candidates', 66),
        ('criteria_count', 6),
    ]

    errors = 0
    for key, expected in checks:
        actual = meta.get(key)
        if actual == expected:
            print(f"✓ {key}: {actual}")
        else:
            print(f"✗ {key}: {actual}, expected {expected}")
            errors += 1

    tier_dist = meta.get('tier_distribution', {})
    print(f"✓ Tier distribution: {tier_dist}")

    return errors == 0

def main():
    print("\n" + "="*80)
    print("ÉTAPE 6: END-TO-END TESTS")
    print("="*80)

    results = {
        'data_integrity': test_data_integrity(),
        'pdf_availability': test_pdf_availability(),
        'ranking': test_ranking(),
        'metadata': test_metadata(),
    }

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n✓ ALL TESTS PASSED — Ready for deployment")
    else:
        print(f"\n✗ {total-passed} test(s) failed — Fix before deployment")

    print("\n" + "="*80 + "\n")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
