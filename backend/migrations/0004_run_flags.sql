-- 0004_run_flags.sql — where a submission's review flags live.
--
-- PRD §6: when a quote fails the evidence check twice, the score is saved *with* a "needs review"
-- flag rather than discarded, and FR-09 surfaces that flag in the results table. There was no column
-- for it, so without this the flag would be computed and thrown away.
--
-- jsonb list rather than a boolean, because the reasons differ: an unlocated quote, an agent that
-- produced nothing, a metacognitive indicator the agent was unsure about. The lecturer UI needs to say
-- which, not just that something is wrong.

alter table submissions
    add column if not exists review_flags jsonb not null default '[]'::jsonb;

comment on column submissions.review_flags is
    'Machine-written reasons this submission should be reviewed (PRD §6, FR-09). Never edited by hand.';
