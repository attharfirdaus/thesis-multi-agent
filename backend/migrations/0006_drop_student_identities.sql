-- The real identifier no longer lives in any managed database (DECISIONS.md, 2026-10-16): a privacy
-- review flagged this table as the highest-harm one in the system, and Atthar decided to move it to a
-- local, encrypted file next to the backend process rather than leave it in Neon. `app/ingest/identity_store.py`
-- is the new home; RLS covered this table while it existed here, so nothing else needs touching.
drop table if exists student_identities;
