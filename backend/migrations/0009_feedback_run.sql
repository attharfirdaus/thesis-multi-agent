-- 0009_feedback_run.sql — which run wrote a submission's feedback (2026-11-10).
--
-- `feedback` is one row per submission, but the results screen and the export are per run: without this
-- column an older run, or a baseline run that produces no feedback at all, exported the feedback of
-- whichever multi-agent run came last. Null on rows written before this migration, which keep being
-- shown everywhere as before.
alter table feedback add column if not exists run_id uuid references runs(id) on delete set null;

-- Lookups the screens make on every row and had no index for.
create index if not exists feedback_submission_idx on feedback (submission_id);
create index if not exists lecturer_reviews_score_idx on lecturer_reviews (system_score_id);
create index if not exists jobs_submission_idx on jobs (submission_id);
