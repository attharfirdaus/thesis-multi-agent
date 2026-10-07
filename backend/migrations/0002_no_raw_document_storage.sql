-- 0002_no_raw_document_storage.sql
--
-- Requirement (architecture decision 2026-10-07): uploaded documents are processed in memory and
-- then discarded. No uploaded file, no filename and no unredacted extracted text is persisted.
--
-- `file_ref` pointed at a stored upload, and there is no object storage in this architecture.
-- `raw_text` held the unredacted extraction — precisely the artefact this project must not keep.
-- The two redacted segments stay, because scores and their evidence offsets point at them
-- (FR-08, FR-10) and the lecturer review screen reads them.

alter table submissions drop column if exists file_ref;
alter table submissions drop column if exists raw_text;

comment on column submissions.ai_output_text is
    'Redacted AI-output segment. Never the original document.';
comment on column submissions.student_analysis_text is
    'Redacted student-analysis segment; Evidence offsets point into this text.';
