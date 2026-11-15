-- Prediction Studio (docs/ARCHITECTURE.md §45): feature contracts, prediction jobs and results.
-- Batch and single predictions are recorded here; the legacy `predictions` table stays as a summary/audit view.

create table public.model_signatures (
  model_id uuid primary key references public.models(id) on delete cascade,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  contract_version text not null default '1.0',
  task text not null,
  feature_contract jsonb not null,           -- docs/contracts/feature_contract.schema.json
  contract_hash text not null,               -- sha256 of the canonical JSON; part of the prediction cache key
  preprocessing_hash text,
  mlflow_model_uri text,                     -- optional: models:/<name>/<version> when MLflow is enabled
  created_at timestamptz not null default now()
);

create table public.prediction_jobs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  model_id uuid not null references public.models(id) on delete restrict,
  job_id uuid references public.jobs(id) on delete set null,   -- Celery job (batch only)
  mode text not null check (mode in ('batch','single','what_if','forecast')),
  status text not null default 'queued'
    check (status in ('queued','validating','needs_review','running','succeeded','failed','cancelled')),
  input_path text,                           -- Storage: predictions/{workspace}/{prediction_job}/input.{csv,xlsx,parquet}
  input_sha256 text,
  input_rows int check (input_rows is null or input_rows >= 0),
  options jsonb not null default '{}'::jsonb, -- confidence level, threshold, horizon, shap_top_k, ood_method, output_format
  validation_report jsonb,                   -- missing/extra columns, dtype errors, unseen categories, OOD summary
  output_path text,                          -- Storage: predictions/{workspace}/{prediction_job}/output.{csv,xlsx}
  output_rows int,
  progress numeric check (progress is null or (progress >= 0 and progress <= 1)),
  error text,
  idempotency_key text,                      -- sha256(model_id, input_sha256, options); duplicate submits return the same job
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),
  started_at timestamptz,
  finished_at timestamptz,
  expires_at timestamptz not null default (now() + interval '30 days')  -- retention (§45.8)
);
create unique index prediction_jobs_idem on public.prediction_jobs (workspace_id, idempotency_key)
  where idempotency_key is not null;
create index prediction_jobs_ws_created on public.prediction_jobs (workspace_id, created_at desc);
create index prediction_jobs_model on public.prediction_jobs (model_id);

-- Single/what-if rows are stored in full; batch jobs store at most the first 1 000 rows here
-- (the complete table is the output file in Storage).
create table public.prediction_results (
  id bigint generated always as identity primary key,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  prediction_job_id uuid not null references public.prediction_jobs(id) on delete cascade,
  row_index int not null,
  row_key text,                              -- value of the id column if the contract has one
  prediction jsonb not null,                 -- y_hat | class + proba | forecast | cluster | embedding
  interval jsonb,                            -- {level, lower, upper} or {quantiles:{...}} or conformal set
  confidence jsonb,                          -- margin, entropy, max_proba, threshold, gauge value
  flags jsonb,                               -- {ood: bool, ood_score, drift_features:[...], unseen_categories:[...], clipped:[...]}
  explanation jsonb,                         -- top-k SHAP contributors {feature, value, shap}
  created_at timestamptz not null default now(),
  unique (prediction_job_id, row_index)
);
create index prediction_results_job on public.prediction_results (prediction_job_id);

-- RLS (same pattern as 20261114000100_rls_policies.sql); viewers can read, analysts+ can create.
do $$
declare t text;
begin
  foreach t in array array['model_signatures','prediction_jobs','prediction_results'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy %I on public.%I for select using (public.is_member(workspace_id))', t || '_read', t);
    execute format('create policy %I on public.%I for insert with check (public.has_role(workspace_id, array[''owner'',''admin'',''scientist'',''analyst'']))', t || '_insert', t);
    execute format('create policy %I on public.%I for update using (public.has_role(workspace_id, array[''owner'',''admin'',''scientist'',''analyst''])) with check (public.has_role(workspace_id, array[''owner'',''admin'',''scientist'',''analyst'']))', t || '_update', t);
    execute format('create policy %I on public.%I for delete using (public.has_role(workspace_id, array[''owner'',''admin'']))', t || '_delete', t);
  end loop;
end $$;

-- A prediction row must belong to the same workspace as its job (prevents cross-workspace inserts by id guessing).
create or replace function public.check_prediction_result_ws() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from public.prediction_jobs j where j.id = new.prediction_job_id and j.workspace_id = new.workspace_id) then
    raise exception 'prediction_job % not in workspace %', new.prediction_job_id, new.workspace_id using errcode = '42501';
  end if;
  return new;
end $$;
create trigger prediction_results_ws before insert or update on public.prediction_results
  for each row execute function public.check_prediction_result_ws();

-- Private bucket for prediction inputs/outputs: 50 MB cap, tabular types only.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('predictions', 'predictions', false, 52428800,
        -- Windows browsers often label .csv as application/vnd.ms-excel; content is re-checked by magic bytes (PV01)
        array['text/csv','text/plain','application/vnd.ms-excel',
              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
              'application/vnd.apache.parquet','application/octet-stream'])
on conflict (id) do nothing;

create policy predictions_objects_read on storage.objects for select to authenticated
  using (bucket_id = 'predictions' and public.is_member(public.try_uuid((storage.foldername(name))[1])));
create policy predictions_objects_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'predictions'
              and public.has_role(public.try_uuid((storage.foldername(name))[1]), array['owner','admin','scientist','analyst']));
-- outputs are written by the Render worker with the service-role key; deletes by owner/admin or the retention job.
create policy predictions_objects_delete on storage.objects for delete to authenticated
  using (bucket_id = 'predictions' and public.has_role(public.try_uuid((storage.foldername(name))[1]), array['owner','admin']));
