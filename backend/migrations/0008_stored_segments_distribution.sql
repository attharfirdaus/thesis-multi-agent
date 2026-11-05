-- 0008_stored_segments_distribution.sql — two Bab III items migration 0007 left derived (2026-11-05).
--
-- Stored segmentation (KF-05, Bab III.6): the analysis is split into identified sentence segments and the
-- split is STORED before any measurement starts, so the raters and every run label the same units even if
-- the segmentation rule changes later. A JSON list of {index, start, end, text}; null on rows imported
-- before this migration, which the worker fills from the same rule before it scores them.
alter table submissions add column if not exists analysis_segments jsonb;

-- Level distribution (KF-07, Bab III.6): the submission-level cognitive summary is the highest level AND
-- the spread of segments over the three level groups (lower / medium / higher order, Xu Li dkk., 2026).
-- Set only on the text-level cognitive row (`segment_index` null), e.g. {"rendah": 3, "menengah": 2, "tinggi": 0}.
alter table system_scores add column if not exists distribution jsonb;
