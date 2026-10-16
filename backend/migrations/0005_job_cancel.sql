-- 0005_job_cancel.sql — a run and its jobs can be cancelled.
--
-- The lecturer's cancel control (2026-10-16) needs an outcome of its own. Both tables constrain `status`
-- with a check, so the value has to be added to the constraint: without this a cancel could only be
-- recorded as *failed* or as a run that mysteriously stopped, and the thesis would have to guess which
-- happened. `cancelled` is terminal, and it means "the queue stopped here", which is why an in-flight
-- submission may still land afterwards — that is one graded submission, not a resumed run.

alter table runs drop constraint runs_status_check;
alter table runs add constraint runs_status_check
    check (status in ('queued', 'running', 'done', 'failed', 'cancelled'));

alter table jobs drop constraint jobs_status_check;
alter table jobs add constraint jobs_status_check
    check (status in ('queued', 'running', 'done', 'failed', 'cancelled'));
