-- =============================================
-- SETUP BASE DE DONNÉES - Plateforme Candidature SAMEDIA
-- Colle ce SQL dans : Supabase Dashboard > SQL Editor > New Query > Run
-- =============================================

-- Table 1: Scores d'évaluation par critère
CREATE TABLE IF NOT EXISTS public.interview_scores (
  id BIGSERIAL PRIMARY KEY,
  user_name TEXT NOT NULL,
  candidate_id TEXT NOT NULL,
  criterion_key TEXT NOT NULL,
  score INTEGER CHECK (score >= 0 AND score <= 5),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_name, candidate_id, criterion_key)
);

-- Table 2: Notes de l'évaluateur par question
CREATE TABLE IF NOT EXISTS public.interview_notes (
  id BIGSERIAL PRIMARY KEY,
  user_name TEXT NOT NULL,
  candidate_id TEXT NOT NULL,
  question_key TEXT NOT NULL,
  note_text TEXT DEFAULT '',
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_name, candidate_id, question_key)
);

-- Table 3: Décisions finales par candidat
CREATE TABLE IF NOT EXISTS public.interview_decisions (
  id BIGSERIAL PRIMARY KEY,
  user_name TEXT NOT NULL,
  candidate_id TEXT NOT NULL,
  decision TEXT DEFAULT '',
  global_comment TEXT DEFAULT '',
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_name, candidate_id)
);

-- Activer Row Level Security
ALTER TABLE public.interview_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interview_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interview_decisions ENABLE ROW LEVEL SECURITY;

-- Politiques d'accès (ouvertes pour l'instant, pas d'auth)
CREATE POLICY "interview_scores_all" ON public.interview_scores FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "interview_notes_all" ON public.interview_notes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "interview_decisions_all" ON public.interview_decisions FOR ALL USING (true) WITH CHECK (true);
