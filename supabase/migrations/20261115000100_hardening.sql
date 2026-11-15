-- Stress-test hardening (docs/STRESS_TEST.md, IDs ST-*). Applies after the core schema and Prediction Studio.

-- ST-SEC-01: computed results are written only by Render workers (service role bypasses RLS).
-- Users must not be able to insert or edit metrics, folds, trials, artefacts, models, signatures,
-- prediction results, AI usage or the audit log ("never fabricate", tamper-proof audit and budgets).
do $$
declare t text;
begin
  foreach t in array array['runs','models','model_metrics','cv_folds','tuning_trials','artefacts',
                           'model_signatures','prediction_results','ai_usage','audit_log','insights',
                           'suitability_reports','intake_proposals','decisions'] loop
    execute format('drop policy if exists %I on public.%I', t || '_insert', t);
    execute format('drop policy if exists %I on public.%I', t || '_update', t);
  end loop;
end $$;

-- ST-OPS-03: jobs are created by users through the API (which uses the user JWT), but only workers change
-- status/progress. Users request cancellation through an RPC that only flips cancel_requested.
alter table public.jobs
  add column if not exists cancel_requested boolean not null default false,
  add column if not exists attempts int not null default 0,
  add column if not exists heartbeat_at timestamptz,
  add column if not exists timeout_s int not null default 3600,
  add column if not exists idempotency_key text;
create unique index if not exists jobs_idem on public.jobs (workspace_id, idempotency_key)
  where idempotency_key is not null and status in ('queued','running');
drop policy if exists jobs_update on public.jobs;
drop policy if exists prediction_jobs_update on public.prediction_jobs;

create or replace function public.request_job_cancel(p_job uuid) returns void
language plpgsql security definer set search_path = public as $$
declare ws uuid;
begin
  select workspace_id into ws from public.jobs where id = p_job;
  if ws is null or not public.has_role(ws, array['owner','admin','scientist','analyst']) then
    raise exception 'not allowed' using errcode = '42501';
  end if;
  update public.jobs set cancel_requested = true where id = p_job and status in ('queued','running');
  update public.prediction_jobs set status = case when status = 'queued' then 'cancelled' else status end
   where job_id = p_job;
end $$;
revoke all on function public.request_job_cancel(uuid) from public;
grant execute on function public.request_job_cancel(uuid) to authenticated;

-- ST-SEC-02: storage policies used ((storage.foldername(name))[1])::uuid, which raises on a malformed path;
-- recreate them with try_uuid() so a bad path is simply denied.
drop policy if exists lab_objects_read on storage.objects;
drop policy if exists lab_objects_insert on storage.objects;
drop policy if exists lab_objects_delete on storage.objects;
create policy lab_objects_read on storage.objects for select to authenticated
  using (bucket_id in ('datasets','artefacts','models','reports','plots')
         and public.is_member(public.try_uuid((storage.foldername(name))[1])));
create policy lab_objects_insert on storage.objects for insert to authenticated
  with check (bucket_id in ('datasets','reports')
              and public.has_role(public.try_uuid((storage.foldername(name))[1]), array['owner','admin','scientist','analyst']));
create policy lab_objects_delete on storage.objects for delete to authenticated
  using (bucket_id in ('datasets','artefacts','models','reports','plots')
         and public.has_role(public.try_uuid((storage.foldername(name))[1]), array['owner','admin']));

-- ST-OPS-01: bucket-level size and type limits (the API also checks; defence in depth).
update storage.buckets set file_size_limit = 524288000,   -- 500 MB raw upload cap (§45.8, §39.4)
  allowed_mime_types = array['text/csv','text/plain','application/vnd.ms-excel',
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             'application/vnd.apache.parquet','application/octet-stream','application/json']
 where id = 'datasets';
update storage.buckets set file_size_limit = 104857600 where id in ('reports','plots','artefacts');
update storage.buckets set file_size_limit = 2147483648 where id = 'models';          -- 2 GB (DL checkpoints)
-- Hosted projects: the project-wide "Global file size limit" caps every bucket. Free plan = 50 MB max,
-- Pro and up = up to 500 GB (Supabase docs, checked Nov 2026). Set it to 2 GB on a Pro project (ST-OPS-02).

-- ST-PERF-01: evaluate auth.uid() once per statement instead of once per row (Supabase RLS guidance).
create or replace function public.is_member(ws uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.workspace_members m where m.workspace_id = ws and m.user_id = (select auth.uid()));
$$;
create or replace function public.has_role(ws uuid, roles text[])
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.workspace_members m
                 where m.workspace_id = ws and m.user_id = (select auth.uid()) and m.role = any(roles));
$$;
create index if not exists workspace_members_user on public.workspace_members (user_id, workspace_id);

-- ST-OPS-07: retention of prediction inputs/outputs (cron calls this daily; Storage objects are removed by the worker).
create or replace function public.expired_prediction_jobs() returns setof public.prediction_jobs
language sql stable security definer set search_path = public as $$
  select * from public.prediction_jobs where expires_at < now();
$$;
revoke all on function public.expired_prediction_jobs() from public, authenticated;
