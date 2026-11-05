-- 0007_thesis_alignment.sql — the data the thesis's Bab III method needs (2026-11-03).
--
-- Segment scores (Bab III.6). The student's analysis is scored sentence segment by sentence segment;
-- the text-level score is derived from the segment labels. Both live in `system_scores`: a row with
-- `segment_index` null is the text-level score the lecturer reviews, a row with a segment index is one
-- unit's label — the unit the expert raters label too. The segment's own offsets are stored with it, so
-- the units a run scored stay fixed even if the segmentation rule changes later.
alter table system_scores
    add column if not exists segment_index integer check (segment_index is null or segment_index >= 1),
    add column if not exists segment_start integer check (segment_start is null or segment_start >= 0),
    add column if not exists segment_end   integer check (segment_end is null or segment_end >= segment_start);
drop index if exists system_scores_unique_idx;
create unique index system_scores_unique_idx
    on system_scores (run_id, submission_id, dimension, coalesce(indicator, ''), coalesce(segment_index, 0));

-- Evaluation-set exclusion (Tabel III.4). Null means the submission is in the evaluation set.
alter table submissions
    add column if not exists exclusion_reason text
    check (exclusion_reason is null
           or exclusion_reason in ('calibration_source', 'author_own', 'unreadable_or_unsegmentable'));

-- Repetitions (Bab III.2.4, III.9): R runs created together with one configuration share a group, and
-- R is fixed when the group is created. A final-evaluation run (III.1) references only frozen versions.
-- `model_unavailable` marks a run whose model the provider no longer serves (KNF-04).
alter table runs
    add column if not exists repetition_group  uuid,
    add column if not exists repetition_index  integer not null default 1 check (repetition_index >= 1),
    add column if not exists repetitions       integer not null default 1 check (repetitions >= 1),
    add column if not exists final_evaluation  boolean not null default false,
    add column if not exists model_unavailable boolean not null default false;
create index if not exists runs_repetition_group_idx on runs (repetition_group);

alter table rubric_versions add column if not exists frozen_at timestamptz;
alter table prompt_versions add column if not exists frozen_at timestamptz;

-- A lecturer's comment on a score (KF-08). Separate from `lecturer_reviews`, whose newest row is the
-- score's current judgement: a comment is not a judgement and must not hide an override.
create table if not exists score_comments (
    id              uuid primary key default gen_random_uuid(),
    owner_id        uuid not null references users(id) on delete cascade,
    system_score_id uuid not null references system_scores(id) on delete cascade,
    body            text not null check (length(btrim(body)) > 0),
    created_at      timestamptz not null default now()
);
create index if not exists score_comments_score_idx on score_comments (system_score_id);
create index if not exists score_comments_owner_idx on score_comments (owner_id);

alter table score_comments enable row level security;
alter table score_comments force row level security;
create policy tenant_isolation on score_comments
    using (owner_id = app.current_user_id())
    with check (owner_id = app.current_user_id());

do $$
begin
    if exists (select 1 from pg_roles where rolname = 'thesis_app') then
        execute 'grant select, insert, update, delete on score_comments to thesis_app';
    end if;
end $$;
