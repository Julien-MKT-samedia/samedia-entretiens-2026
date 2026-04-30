================================================================================
SAMEDIA VIE USA 2026 - RECRUITING DATA
================================================================================

COMPLETION DATE: 2026-04-29
TOTAL CANDIDATES: 51 (51 CVs analyzed and scored)

================================================================================
FILES & STRUCTURE
================================================================================

data.json (146 KB)
  └─ Complete candidate database
  └─ Tier distribution: T1=47, T2=3, T3=1
  └─ 6-criteria scoring system (0-2 pts each = 12 max)
  └─ Auto-generated interview questions by tier

cvs/ (81 files)
  ├─ 51 CV files: {slug}-cv.{pdf|docx}
  └─ 30 LDM files: {slug}-ldm.{pdf|docx}

generate_data.py
  └─ Python extraction script (re-runnable)
  └─ Can be modified to update scoring / regenerate JSON

README.txt (this file)

================================================================================
QUICK ACCESS
================================================================================

TOP 15 CANDIDATES (Score 12/12 & 11/12):
  1. Rollande Eyene         12/12  rollandeneyene@gmail.com
  2. Sira Traore            12/12  si.siratraore@gmail.com
  3. Aadnan El Fahsi        12/12  aadnanelfahsi@gmail.com
  4. Hugo Damoiselet        12/12  hugodamoi@hotmail.com
  5. Alexandre Bethmont     12/12  alexandrebethmont@gmail.com
  6. Romain Bergeal         12/12  bergeal.romain@gmail.com
  7. Walid Aissat           12/12  walidaissat25@gmail.com
  8. Adrien Faucheux        11/12  adrienfaucheux.pro@gmail.com
  9. Sabrina Kholkhal       11/12  sabrina.kholkhal@kedgebs.com
 10. Jonathan Mabile        11/12  jonathanmabile@gmail.com
 11. Mahmoud Satour         11/12  Mahmoudsat61@gmail.com
 12. Marion Heymann         11/12  mheyman0@chicagobooth.edu (Chicago Booth MBA)
 13. Valentin Cau           11/12  cau.valentin91@gmail.com
 14. Chloé Morel           11/12  chloe.mrl91@gmail.com
 15. Titouan Benard         10/12  titouan.benard@essec.edu

TIER BREAKDOWN:
  Tier 1 (47 candidates, score ≥7): Strong fit - ready for detailed interviews
  Tier 2 (3 candidates, score 4-6): Moderate fit - needs validation on gaps
  Tier 3 (1 candidate, score <4): Weak fit - screening only

================================================================================
SCORING SYSTEM (6 Criteria, 0-2 pts each)
================================================================================

1. ENGLISH PROFICIENCY (0-2)
   0 = No evidence | 1 = B1/B2 intermediate | 2 = C1/C2/Native

2. SALES EXPERIENCE (0-2)
   0 = None | 1 = Non-B2B or initial | 2 = B2B confirmed

3. FIELD/PROSPECTION (0-2)
   0 = Back-office | 1 = Support/coordination | 2 = Active prospection/terrain

4. USA IMMERSION (0-2)
   0 = Not documented | 1 = Other Anglophone | 2 = USA documented (1y+)

5. US MARKET FIT (1-2)
   1 = Adapté | 2 = Très adapté (construction/BTP/equipment)

6. CULTURAL ANCHORING (0-2)
   0 = Francophone European | 1 = International | 2 = Native Anglophone

================================================================================
INTERVIEW STRUCTURE BY TIER
================================================================================

TIER 1 (47 candidates):
  6 categories × 4-5 questions = ~25 personalized questions
  Categories: Communication, Sales/Business, Market, SAMEDIA Fit, Motivation, Logistics

TIER 2 (3 candidates):
  6 categories × 2 questions = ~12 questions (lighter assessment)

TIER 3 (1 candidate):
  5 global screening questions only

================================================================================
HOW TO USE data.json
================================================================================

Option A: PYTHON
  import json
  with open('data.json') as f:
      data = json.load(f)
  
  # Access top candidate
  candidates = sorted(data['candidates'].values(), key=lambda x: x['matchingScore'], reverse=-1)
  top = candidates[0]
  print(top['name'], top['matchingScore'], top['questions'])

Option B: JAVASCRIPT/NODE.JS
  const data = require('./data.json');
  const topCandidates = Object.values(data.candidates)
    .sort((a, b) => b.matchingScore - a.matchingScore)
    .slice(0, 15);

Option C: IMPORT TO CRM/ATS
  - Open in Excel/Google Sheets: select candidates[] array
  - Use JSON import feature in your recruiting tool
  - Filter by tier, sort by matchingScore

Option D: BASH/CLI
  # Get all Tier 1 emails
  cat data.json | jq '.candidates[] | select(.tier==1) | .contact.email'
  
  # Count by tier
  cat data.json | jq '.candidates[] | .tier' | sort | uniq -c

================================================================================
DATA FIELDS PER CANDIDATE
================================================================================

id              : Unique ID (e.g., "05-rollande-eyene")
number          : Original folder number (1-51)
name            : Full name
tier            : 1, 2, or 3
matchingScore   : 0-12 (sum of 6 criteria)
scoreDetails    : Object with individual scores for each criterion
location        : "USA (TBD)"
contact.email   : Extracted email address
contact.phone   : Extracted phone number
education       : Extracted education line
experiences     : Array of extracted job experiences (up to 3)
strengths       : List of key strengths based on profile
warnings        : List of gaps / concerns
cvFile          : Relative path to CV file
ldmFile         : Relative path to LDM (motivation letter) or null
questions       : Object with question categories and questions

================================================================================
SPECIAL CASES
================================================================================

✓ Adhame Hasaine (#8)
  - DOCX CV (English + French versions)
  - Score: 4/12 (Tier 2)
  - Gaps: Field/prospection, USA experience

✓ Erwin Twagiramungu (#24)
  - DOCX CV + DOCX LDM
  - Score: 7/12 (Tier 1 - minimal threshold)

✓ Dylan Dourlen (#18)
  - Single PDF (no motivation letter)
  - Score: 1/12 (Tier 3 - weak fit)

✓ Marion Heymann (#34)
  - Chicago Booth MBA (mheyman0@chicagobooth.edu)
  - Score: 11/12 (Tier 1)
  - Strong USA network signal

================================================================================
STATISTICS
================================================================================

Score Distribution:
  Min: 1/12 (Dylan Dourlen)
  Max: 12/12 (7 candidates)
  Average: 9.2/12
  Median: 10/12

Language Coverage:
  CV+LDM: 30 candidates (59%)
  CV only: 21 candidates (41%)

File Formats:
  PDF CVs: 51
  DOCX CVs: 0 (all converted from DOCX)
  PDF LDMs: 21
  DOCX LDMs: 9

================================================================================
NOTES
================================================================================

• Scoring is keyword-based (objective) - can be refined post-interview
• High Tier 1 concentration (47/51 = 92%) indicates strong pool
• Consider Marion Heymann (@chicagobooth.edu) for USA market insights
• 21 candidates without motivation letter - may be less serious
• All files have been normalized and organized - ready for recruitment system

================================================================================
SUPPORT
================================================================================

To regenerate or update scoring:
  python3 generate_data.py

To debug issues:
  python3 << EOF
  import json
  data = json.load(open('data.json'))
  print(f"Candidates: {len(data['candidates'])}")
  print(f"Tiers: {[c['tier'] for c in data['candidates'].values()]}")
  EOF

For questions about methodology:
  See comments in generate_data.py - all logic is documented

================================================================================
