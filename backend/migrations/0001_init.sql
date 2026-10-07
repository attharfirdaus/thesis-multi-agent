-- 0001_init.sql — data model of PRD section 10, plus auth.
--
-- Tenancy: every tenant-scoped table carries owner_id, and one uniform policy compares it with
-- app.current_user_id(). FORCE is set so the table owner is subject to the policy too; the
-- runtime role (thesis_app) is deliberately NOT the owner.
--
-- Deliberately NOT row-level-secured: users and sessions. Resolving a session token to a user
-- happens before any tenant context exists, so those two tables are reachable only through the
-- auth code path. Everything else is covered.

create schema if not exists app;

create or replace function app.current_user_id() returns uuid
language sql stable as $$
    select nullif(current_setting('app.current_user_id', true), '')::uuid
$$;

create table if not exists schema_migrations (
    version    text primary key,
    applied_at timestamptz not null default now()
);

-- ----------------------------------------------------------------------------- auth

create table users (
    id            uuid primary key default gen_random_uuid(),
    email         text not null unique check (email = lower(email)),
    name          text not null,
    role          text not null default 'lecturer' check (role in ('lecturer', 'admin')),
    password_hash text not null,
    created_at    timestamptz not null default now()
);

create table sessions (
    id           uuid primary key default gen_random_uuid(),
    user_id      uuid not null references users(id) on delete cascade,
    token_hash   bytea not null unique,
    csrf_token   bytea not null,
    created_at   timestamptz not null default now(),
    last_seen_at timestamptz not null default now(),
    expires_at   timestamptz not null
);
create index sessions_user_id_idx on sessions (user_id);

-- ----------------------------------------------------------------------------- teaching

create table rubric_versions (
    id          uuid primary key default gen_random_uuid(),
    owner_id    uuid not null references users(id) on delete cascade,
    version     integer not null,
    dimensions  jsonb not null,
    levels      jsonb not null,
    indicators  jsonb not null,
    descriptors jsonb not null,
    created_at  timestamptz not null default now(),
    unique (owner_id, version)
);

create table assignments (
    id                uuid primary key default gen_random_uuid(),
    owner_id          uuid not null references users(id) on delete cascade,
    title             text not null,
    course            text not null,
    prompt_text       text not null default '',
    rubric_version_id uuid references rubric_versions(id),
    created_at        timestamptz not null default now(),
    updated_at        timestamptz not null default now()
);
create index assignments_owner_idx on assignments (owner_id);

create table prompt_versions (
    id         uuid primary key default gen_random_uuid(),
    owner_id   uuid not null references users(id) on delete cascade,
    agent_name text not null,
    version    integer not null,
    template   text not null,
    created_at timestamptz not null default now(),
    unique (owner_id, agent_name, version)
);

create table submissions (
    id                    uuid primary key default gen_random_uuid(),
    owner_id              uuid not null references users(id) on delete cascade,
    assignment_id         uuid not null references assignments(id) on delete cascade,
    pseudonym             text not null,
    file_ref              text,
    raw_text              text,
    ai_output_text        text,
    student_analysis_text text,
    segmentation_status   text not null default 'pending'
                          check (segmentation_status in ('pending', 'segmented', 'confirmed', 'failed')),
    created_at            timestamptz not null default now()
);
create index submissions_owner_idx on submissions (owner_id);
create index submissions_assignment_idx on submissions (assignment_id);

-- The real identifier lives here and nowhere else. Owner-only, same policy mechanism.
create table student_identities (
    submission_id   uuid primary key references submissions(id) on delete cascade,
    owner_id        uuid not null references users(id) on delete cascade,
    real_identifier text not null
);
create index student_identities_owner_idx on student_identities (owner_id);

-- ----------------------------------------------------------------------------- runs

create table runs (
    id                 uuid primary key default gen_random_uuid(),
    owner_id           uuid not null references users(id) on delete cascade,
    assignment_id      uuid not null references assignments(id) on delete cascade,
    mode               text not null check (mode in ('single_agent', 'multi_agent')),
    model_config       jsonb not null default '{}'::jsonb,
    rubric_version_id  uuid references rubric_versions(id),
    prompt_version_ids uuid[] not null default '{}',
    started_at         timestamptz,
    finished_at        timestamptz,
    status             text not null default 'queued'
                       check (status in ('queued', 'running', 'done', 'failed')),
    created_at         timestamptz not null default now()
);
create index runs_owner_idx on runs (owner_id);
create index runs_assignment_idx on runs (assignment_id);

create table agent_traces (
    id            uuid primary key default gen_random_uuid(),
    owner_id      uuid not null references users(id) on delete cascade,
    run_id        uuid not null references runs(id) on delete cascade,
    submission_id uuid references submissions(id) on delete cascade,
    agent_name    text not null,
    input_ref     text,
    output_json   jsonb,
    latency_ms    integer,
    error         text,
    created_at    timestamptz not null default now()
);
create index agent_traces_owner_idx on agent_traces (owner_id);
create index agent_traces_run_idx on agent_traces (run_id);

-- NOTE for phase 4: this table is written by the pipeline and read by the owner, so it stays
-- under RLS. The background worker that claims queued jobs therefore needs either a BYPASSRLS
-- role or a separate claim query outside tenant context.
create table jobs (
    id            uuid primary key default gen_random_uuid(),
    owner_id      uuid not null references users(id) on delete cascade,
    run_id        uuid not null references runs(id) on delete cascade,
    submission_id uuid references submissions(id) on delete cascade,
    status        text not null default 'queued'
                  check (status in ('queued', 'running', 'done', 'failed')),
    attempts      integer not null default 0,
    last_error    text,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);
create index jobs_owner_idx on jobs (owner_id);
create index jobs_run_idx on jobs (run_id);

-- ----------------------------------------------------------------------------- results

create table system_scores (
    id               uuid primary key default gen_random_uuid(),
    owner_id         uuid not null references users(id) on delete cascade,
    run_id           uuid not null references runs(id) on delete cascade,
    submission_id    uuid not null references submissions(id) on delete cascade,
    dimension        text not null check (dimension in ('cognitive', 'metacognitive')),
    indicator        text,
    level            text not null,
    confidence       numeric(4, 3) check (confidence is null or (confidence >= 0 and confidence <= 1)),
    rationale        text,
    explanation_type text,
    created_at       timestamptz not null default now()
);
create index system_scores_owner_idx on system_scores (owner_id);
create index system_scores_submission_idx on system_scores (submission_id);
create unique index system_scores_unique_idx
    on system_scores (run_id, submission_id, dimension, coalesce(indicator, ''));

create table evidence (
    id              uuid primary key default gen_random_uuid(),
    owner_id        uuid not null references users(id) on delete cascade,
    system_score_id uuid not null references system_scores(id) on delete cascade,
    start_offset    integer not null check (start_offset >= 0),
    end_offset      integer not null check (end_offset >= start_offset),
    quote           text not null
);
create index evidence_owner_idx on evidence (owner_id);
create index evidence_score_idx on evidence (system_score_id);

create table lecturer_reviews (
    id              uuid primary key default gen_random_uuid(),
    owner_id        uuid not null references users(id) on delete cascade,
    system_score_id uuid not null references system_scores(id) on delete cascade,
    action          text not null check (action in ('accept', 'override')),
    new_level       text,
    reason          text,
    reviewed_at     timestamptz not null default now(),
    -- FR-11: an override always carries a short reason; the system score itself is never overwritten.
    constraint lecturer_reviews_reason_required check (action <> 'override' or (reason is not null and length(btrim(reason)) > 0))
);
create index lecturer_reviews_owner_idx on lecturer_reviews (owner_id);

create table feedback (
    id             uuid primary key default gen_random_uuid(),
    owner_id       uuid not null references users(id) on delete cascade,
    submission_id  uuid not null references submissions(id) on delete cascade,
    generated_text text not null,
    edited_text    text,
    edited_by      uuid references users(id),
    exported_at    timestamptz,
    created_at     timestamptz not null default now()
);
create index feedback_owner_idx on feedback (owner_id);

-- ----------------------------------------------------------------------------- tenancy

do $$
declare
    t text;
    tenant_tables text[] := array[
        'rubric_versions', 'assignments', 'prompt_versions', 'submissions', 'student_identities',
        'runs', 'agent_traces', 'jobs', 'system_scores', 'evidence', 'lecturer_reviews', 'feedback'
    ];
begin
    foreach t in array tenant_tables loop
        execute format('alter table %I enable row level security', t);
        execute format('alter table %I force row level security', t);
        execute format(
            'create policy tenant_isolation on %I using (owner_id = app.current_user_id()) '
            'with check (owner_id = app.current_user_id())', t);
    end loop;
end $$;

-- Grants for the runtime role, if it exists in this database.
do $$
begin
    if exists (select 1 from pg_roles where rolname = 'thesis_app') then
        execute 'grant usage on schema public, app to thesis_app';
        execute 'grant select, insert, update, delete on all tables in schema public to thesis_app';
        execute 'grant usage, select on all sequences in schema public to thesis_app';
        execute 'grant execute on all functions in schema app to thesis_app';
    end if;
end $$;
