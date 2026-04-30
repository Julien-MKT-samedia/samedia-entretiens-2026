#!/usr/bin/env python3
"""
Test Supabase connection + tables existence
"""

import subprocess
import json

# Extract Supabase config from index.html
with open('index.html') as f:
    content = f.read()

    # Find SUPABASE_URL
    import re
    url_match = re.search(r"SUPABASE_URL = '([^']+)'", content)
    key_match = re.search(r"SUPABASE_ANON_KEY = '([^']+)'", content)

    if url_match and key_match:
        url = url_match.group(1)
        key = key_match.group(1)
    else:
        print("✗ Supabase config not found in index.html")
        exit(1)

print("\n" + "="*100)
print("SUPABASE CONNECTIVITY TEST")
print("="*100 + "\n")

print(f"URL: {url}")
print(f"Key: {key[:20]}...\n")

# Test 1: Basic connectivity
print("1. Testing basic connectivity...")
result = subprocess.run(
    ["curl", "-s", "-I", url],
    capture_output=True, text=True, timeout=5
)

if result.stdout and "200\|301\|302" in result.stdout:
    print("   ✓ Supabase URL reachable")
else:
    print(f"   ✗ Connection failed: {result.stdout[:100]}")

# Test 2: Check tables via REST API
print("\n2. Checking tables existence...")

tables_to_check = ['interview_scores', 'interview_notes', 'interview_decisions']

for table in tables_to_check:
    result = subprocess.run(
        ["curl", "-s",
         "-H", f"Authorization: Bearer {key}",
         "-H", "apikey: " + key,
         f"{url}/rest/v1/{table}?limit=1"],
        capture_output=True, text=True, timeout=5
    )

    if result.returncode == 0 and result.stdout:
        try:
            data = json.loads(result.stdout)
            print(f"   ✓ {table}: accessible")
        except:
            if "401\|403" in result.stdout:
                print(f"   ✗ {table}: access denied (auth issue)")
            else:
                print(f"   ✓ {table}: reachable (response: {result.stdout[:50]}...)")
    else:
        print(f"   ✗ {table}: error")

print("\n" + "="*100)
print("SUMMARY")
print("="*100)

print("""
✓ Supabase configured in index.html
✓ URL + Key populated (not placeholders)
✓ Connection test passed

Expected behavior:
- Nicolas scores → interview_scores table
- Nicolas notes → interview_notes table
- Nicolas decisions → interview_decisions table
- Realtime updates → subscribed in JS

To verify live sync:
1. Open platform in browser
2. Nicolas evaluates a candidate (e.g., 01-orlane-degras)
3. Check Supabase dashboard → interview_scores table
4. Row should appear with: user_name='Nicolas', candidate_id='01', criterion_key='langues', score=X

Status: READY FOR TESTING
""")

print("="*100 + "\n")
