# BACKUP — Snapshot V1 Ouest-2026

## Date capture
29 avril 2026

## Contenu préservé

### Candidats (7)
1. **Nicolas GUILBAULT** — 41 ans, Bégrolles 49
   - Matching: 8.5/10
   - Expérience: 20 ans relation client, TC chez Berner
   - CV: ResumeNicolasGUILBAULT (1).pdf

2. **Valentin CHARRIER** — 42 ans, Saint Aubin 85
   - Matching: 7/10
   - Expérience: VRP TC 4 ans Specimat, ex-gérant
   - CV: CVValentinCHARRIER.pdf

3. **Axel BALLIGAND** — ~35 ans, Sevremont 85
   - Matching: 6/10
   - Expérience: VRP 250-300k€/an, dessinateur batiment
   - CV: ResumeAxelBalligand.pdf

4. **Melvin BARBEAU** — 28 ans, Bellevigny 85
   - Matching: 7/10
   - Expérience: BTS TC outillage, Bigmat, coach foot
   - CV: ResumeMelvinBarbeau (1).pdf

5. **Sébastien CHARTIER** — ~45 ans, Beaucouzé 49
   - Matching: 6.5/10
   - Expérience: 6 ans Point.P, chef d'entreprise carrelage, 10+ ans TC
   - CV: CVSébastienChartier.pdf

6. **Louis PANNETIER** — 26 ans, La Verrie 85
   - Matching: 5/10
   - Expérience: BTS TC, Routhiau chauffage/sanitaire, junior
   - CV: ResumeLouisPANNETIER.pdf

7. **Luigi POIROUT** — 23 ans, Montbert 44
   - Matching: 4.5/10
   - Expérience: Point.P 18 mois, associé batiment familial, très junior
   - CV: CVLuigiPoirout.pdf

### Critères (7)
- Présentation (coeff 2)
- Localisation (coeff 2)
- Technique (coeff 2)
- Commerce (coeff 3)
- Package (coeff 1)
- Mobilité (coeff 2)
- Préparation entretien (coeff 2)
**MAX SCORE: 80 points**

### Questions par candidat
- 6 catégories : motivation, experience, technique, secteur, softskills, specifiques
- 30-40 questions/candidat
- Totalement personnalisées par profil

### Fonctionnalités V1
✓ Modale sélection utilisateur (Cédrick, Bruno)
✓ 4 modules : Fiche synthèse, Questions, Scoring, Tableau comparatif
✓ PDF viewer avec zoom + fullscreen
✓ Focus mode (timer, navigation par catégorie)
✓ Supabase multi-users (scores, notes, decisions)
✓ Scoring interactif (8 critères × 5 notes)
✓ Export PDF
✓ Keyboard shortcuts

### Structure Supabase V1
3 tables (sur SGHFEWGV) :
- interview_scores(user_name, candidate_id, criterion_key, score)
- interview_notes(user_name, candidate_id, question_key, note_text)
- interview_decisions(user_name, candidate_id, decision, global_comment)

**RLS**: DISABLED (open access)

## Migration V2 ✓
- Données candidats → recrutements/ouest-2026/data.json
- Critères → recrutements/ouest-2026/config.json
- PDFs → recrutements/ouest-2026/cvs/
- Structure → data-loader.js chargement dynamique
- Supabase → +recruitment_id pour multi-recrutements

## État sauvegarde
- **Données**: toutes extraites dans JSON ✓
- **CVs**: 7 PDFs copiés vers cvs/ ✓
- **Config**: config.json + data.json en place ✓
- **Original index.html**: intact (2407 lignes) ✓
