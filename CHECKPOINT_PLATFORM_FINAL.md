# Checkpoint: VIE USA 2026 Platform - Session Complete

**Date**: 2026-04-30
**Status**: Production Ready for Nicolas

---

## Session Summary

Transformed VIE USA 2026 recruitment platform from broken state to production-ready:

### Key Fixes
1. ✅ **Supabase integration** - New project (qdeffonyxxsdtcfpyaxe.supabase.co)
   - recruitment_id isolation for multi-recruitment support
   - DELETE+INSERT upsert strategy (handles score updates)
   - 3 tables: interview_scores, interview_notes, interview_decisions
   - RLS enabled with open policies

2. ✅ **LocalStorage disabled** - Supabase only as source of truth
   - Removed localStorage fallback (was causing data conflicts)
   - All data flows through Supabase exclusively
   - Clean start for Nicolas

3. ✅ **Score system fixed**
   - calcWeightedScore() - coeff=1 default (no more NaN)
   - Score priority: Nicolas's score > CV score (fallback)
   - MAX_SCORE = 12 (6 criteria × 2 points each)

4. ✅ **UI refined**
   - Auto-login Nicolas (no user selection modal)
   - 3 fiche sections: Lecture rapide / Scoring détaillé / Infos clés
   - Scoring table with PRE-SCORING (CV) vs NICOLAS columns
   - Question categories: 7 (motivation, international, commercial, marche_usa, autonomie, specifiques, generic)

5. ✅ **Exports working**
   - Individual PDF (fiche + scoring)
   - Dashboard PDF (stats + top 15)
   - Comparative table PDF (all 51 candidates)

6. ✅ **Sorting** - Candidates by CV score (scoreDetails sum), descending

---

## Data Structure

**File**: `/Users/juliendufau/Desktop/SAMEDIA-2026/CANDIDATURE-2026/recrutements/vie-usa-2026/data.json`
- 51 candidates
- Fields per candidate:
  ```json
  {
    "id": "candidate_id",
    "name": "Name",
    "location": "Location",
    "contact": { "email": "email", "phone": "phone" },
    "education": ["School1", "School2"],
    "languages": ["English", "French"],
    "skills": ["Skill1", "Skill2"],
    "scoreDetails": { "langues": 2, "vente": 2, ... },
    "justifications": { "english": "...", "sales": "...", ... },
    "strengths": ["Strength1", "Strength2"],
    "warnings": ["Warning1"],
    "rank": 1,
    "refined_analysis": { "total_score": 9, "verdict": "GO" }
  }
  ```

**Criteria** (config.json):
```json
6 criteria × scoreOptions [0,1,2] each
- langues (English)
- vente (Sales)
- prospection (Field)
- usa_exp (USA exp)
- profil_marche (Market fit)
- ancrage_culturel (Cultural anchor)
```

**Supabase Tables**:
- interview_scores: recruitment_id, user_name='Nicolas', candidate_id, criterion_key, score, updated_at
- interview_notes: recruitment_id, user_name='Nicolas', candidate_id, question_key, note_text, updated_at
- interview_decisions: recruitment_id, user_name='Nicolas', candidate_id, decision, global_comment, updated_at

---

## Deployment

**GitHub**: https://github.com/Julien-MKT-samedia/samedia-entretiens-2026
**Netlify**: https://samedia-entretiens-2026.netlify.app
**Live Branch**: main (auto-deploy on push)

**Recent commits**:
```
f7c4789 - Fix: Sort candidates by CV score (scoreDetails) instead of matchingScore
560bded - Fix: Score priority — Nicolas's score > CV score (fallback)
888212b - Fix: Disable localStorage — Supabase only as single source of truth
e457b42 - Fix: Implement DELETE+INSERT strategy for proper upsert (handles score updates)
550817d - Fix: Add default coeff=1 in calcWeightedScore to fix NaN total
33cc3ae - Fix: Recalc matchingScore after score change
fbfdd19 - Fix: Use insert with ignoreDuplicates instead of upsert to avoid malformed on_conflict
7d2358a - Fix: Remove onConflict parameter from Supabase upsert (let SDK auto-detect UNIQUE constraints)
```

---

## Current State

**Supabase**: CLEAN (all test data deleted)
- interview_scores: 0 rows
- interview_notes: 0 rows  
- interview_decisions: 0 rows

**localStorage**: DISABLED

**51 Candidates**: Loaded from data.json, sorted by CV score

**Nicolas**: Auto-logged in, ready to score

---

## For Next Session: Adding 51 New CVs

**Steps**:
1. Prepare new CV data in same format (data.json structure)
2. Create new recruitment_id (e.g., 'ouest-2026')
3. Update config.json if criteria differ
4. Update index.html with new recruitment_id in:
   - syncFromSupabase() filters
   - upsertScore/Note/Decision() payloads
   - BOOT section (if auto-login user changes)
5. Reset Supabase (or create new tables with new recruitment_id)
6. Deploy

**Files to modify**:
- `/recrutements/[new-recruitment]/data.json` (new candidates)
- `/recrutements/[new-recruitment]/config.json` (new criteria if needed)
- `index.html` (constants for new recruitment_id)

---

## Contact

**Platform**: https://samedia-entretiens-2026.netlify.app
**Supabase Project**: https://app.supabase.com/project/qdeffonyxxsdtcfpyaxe
**GitHub Repo**: https://github.com/Julien-MKT-samedia/samedia-entretiens-2026

**Nicolas mail sent** with platform guide.

---

## Critical Notes

- ✅ Supabase is source of truth (no localStorage)
- ✅ DELETE+INSERT upsert handles all score updates correctly
- ✅ Nicolas's scores override CV scores automatically
- ✅ All data auto-syncs + archives on Supabase
- ✅ PDF exports include full audit trail
- ✅ Candidates sorted by CV quality (descending)

---

End Checkpoint
