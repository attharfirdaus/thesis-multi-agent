-- 0003_ingest.sql — audit of what redaction removed, plus per-submission import warnings.
--
-- Only *counts* are recorded here. The removed values are deliberately not stored anywhere:
-- the whole point of FR-04 is that an identifier is deleted, not filed.

create table redaction_events (
    id            uuid primary key default gen_random_uuid(),
    owner_id      uuid not null references users(id) on delete cascade,
    submission_id uuid not null references submissions(id) on delete cascade,
    cls           text not null,
    count         integer not null check (count > 0),
    created_at    timestamptz not null default now()
);
create index redaction_events_submission_idx on redaction_events (submission_id);
create index redaction_events_owner_idx on redaction_events (owner_id);

-- Extraction caveats (a page with no text layer, a file that failed to parse). The uploaded file is
-- discarded, so these cannot be recomputed later — they have to be captured at import time.
alter table submissions
    add column if not exists import_warnings jsonb not null default '[]'::jsonb;

-- The tenancy loop in 0001_init.sql ran before this table existed, so it needs its own policies.
alter table redaction_events enable row level security;
alter table redaction_events force row level security;
create policy tenant_isolation on redaction_events
    using (owner_id = app.current_user_id())
    with check (owner_id = app.current_user_id());

do $$
begin
    if exists (select 1 from pg_roles where rolname = 'thesis_app') then
        execute 'grant select, insert, update, delete on redaction_events to thesis_app';
    end if;
end $$;
