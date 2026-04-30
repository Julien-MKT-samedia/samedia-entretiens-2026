-- ============================================
-- MIGRATION V2: Add recruitment_id to Supabase tables
-- ============================================

-- Add recruitment_id column to interview_scores
ALTER TABLE interview_scores
ADD COLUMN recruitment_id TEXT NOT NULL DEFAULT 'ouest-2026';

-- Add recruitment_id column to interview_notes
ALTER TABLE interview_notes
ADD COLUMN recruitment_id TEXT NOT NULL DEFAULT 'ouest-2026';

-- Add recruitment_id column to interview_decisions
ALTER TABLE interview_decisions
ADD COLUMN recruitment_id TEXT NOT NULL DEFAULT 'ouest-2026';

-- Update UNIQUE constraints to include recruitment_id
-- First, drop existing constraints
ALTER TABLE interview_scores
DROP CONSTRAINT interview_scores_user_name_candidate_id_criterion_key_key;

ALTER TABLE interview_notes
DROP CONSTRAINT interview_notes_user_name_candidate_id_question_key_key;

ALTER TABLE interview_decisions
DROP CONSTRAINT interview_decisions_user_name_candidate_id_key;

-- Add new UNIQUE constraints with recruitment_id
ALTER TABLE interview_scores
ADD UNIQUE(recruitment_id, user_name, candidate_id, criterion_key);

ALTER TABLE interview_notes
ADD UNIQUE(recruitment_id, user_name, candidate_id, question_key);

ALTER TABLE interview_decisions
ADD UNIQUE(recruitment_id, user_name, candidate_id);

-- Create index on recruitment_id for faster queries
CREATE INDEX idx_interview_scores_recruitment ON interview_scores(recruitment_id);
CREATE INDEX idx_interview_notes_recruitment ON interview_notes(recruitment_id);
CREATE INDEX idx_interview_decisions_recruitment ON interview_decisions(recruitment_id);
