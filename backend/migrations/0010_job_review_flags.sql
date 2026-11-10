-- 0010_job_review_flags.sql — review flags per run, and which quotes could not be located (2026-11-10).
--
-- `submissions.review_flags` holds what the newest evaluation said, so an older run's results showed
-- the flags of a later one. A job is one submission inside one run, which is the grain a flag has, so
-- the flags are stored there as well; `submissions.review_flags` stays as "the latest", which is what
-- the assignment screen lists.
--
-- `unlocated_quotes` is the list behind the `evidence_unverified` flag: `{source, segment, quote}` for
-- every quote the evidence check could not find. It was computed, counted and dropped, so the lecturer
-- was told a quote was missing without being told which.
alter table jobs
    add column if not exists review_flags     jsonb not null default '[]'::jsonb,
    add column if not exists unlocated_quotes jsonb not null default '[]'::jsonb;

-- Jobs finished before this migration: the submission's current flags belong to its newest finished job.
update jobs j
set review_flags = s.review_flags
from submissions s
where s.id = j.submission_id
  and j.status = 'done'
  and j.updated_at = (
      select max(j2.updated_at) from jobs j2 where j2.submission_id = j.submission_id and j2.status = 'done'
  );
