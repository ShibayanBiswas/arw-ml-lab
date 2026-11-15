-- ARW ML Lab core schema (docs/ARCHITECTURE.md §7, §32, §33, §37, §38, §40). Starting point for Phase 0;
-- extend with new migrations, never edit this file after it is applied.
create extension if not exists pgcrypto;

-- tenancy ---------------------------------------------------------------
create table public.organisations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

create table public.workspaces (
  id uuid primary key default gen_random_uuid(),
  organisation_id uuid not null references public.organisations(id) on delete cascade,
  name text not null,
  data_classification text not null default 'internal' check (data_classification in ('public','internal','restricted')),
  settings jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table public.workspace_members (
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('owner','admin','scientist','analyst','viewer')),
  created_at timestamptz not null default now(),
  primary key (workspace_id, user_id)
);

-- data ------------------------------------------------------------------
create table public.datasets (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  name text not null,
  description text,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create table public.dataset_versions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  dataset_id uuid not null references public.datasets(id) on delete cascade,
  version int not null,
  storage_path text not null,
  content_hash text not null,
  n_rows bigint,
  n_cols int,
  update_mode text check (update_mode in ('initial','append','replace','upsert')),
  profile jsonb,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),
  unique (dataset_id, version)
);

create table public.dataset_columns (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  dataset_version_id uuid not null references public.dataset_versions(id) on delete cascade,
  name text not null,
  ordinal int not null,
  inferred_type text,
  role text,
  stats jsonb
);

-- experiments & runs ----------------------------------------------------
create table public.experiments (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  dataset_version_id uuid references public.dataset_versions(id),
  name text not null,
  family text not null check (family in ('supervised','supervised_sequential','financial','unsupervised','time_series')),
  task_spec jsonb not null default '{}'::jsonb,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create table public.recipes (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  experiment_id uuid references public.experiments(id) on delete cascade,
  version int not null default 1,
  steps jsonb not null,
  created_at timestamptz not null default now()
);

create table public.jobs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  queue text not null,
  kind text not null,
  status text not null default 'queued' check (status in ('queued','running','succeeded','failed','cancelled')),
  content_hash text,
  progress numeric,
  params jsonb,
  error text,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),
  started_at timestamptz,
  finished_at timestamptz
);

create table public.runs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  experiment_id uuid not null references public.experiments(id) on delete cascade,
  recipe_id uuid references public.recipes(id),
  job_id uuid references public.jobs(id),
  algorithm_key text not null,
  params jsonb not null,
  cv_spec jsonb,
  seed int not null default 42,
  lib_versions jsonb,
  status text not null default 'queued',
  created_at timestamptz not null default now()
);

create table public.models (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  run_id uuid not null references public.runs(id) on delete cascade,
  storage_path text,
  format text,
  size_bytes bigint,
  created_at timestamptz not null default now()
);

create table public.model_metrics (
  id bigint generated always as identity primary key,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  run_id uuid not null references public.runs(id) on delete cascade,
  split text not null check (split in ('train','cv_mean','cv_std','test','oos')),
  metric text not null,
  value double precision not null
);

create table public.cv_folds (
  id bigint generated always as identity primary key,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  run_id uuid not null references public.runs(id) on delete cascade,
  fold int not null,
  n_train int, n_val int,
  metrics jsonb not null
);

create table public.tuning_trials (
  id bigint generated always as identity primary key,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  run_id uuid not null references public.runs(id) on delete cascade,
  trial int not null,
  params jsonb not null,
  value double precision,
  state text
);

create table public.artefacts (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  kind text not null,
  artefact_key text not null,
  run_id uuid references public.runs(id) on delete cascade,
  dataset_version_id uuid references public.dataset_versions(id) on delete cascade,
  spec_path text,
  png_path text,
  numbers jsonb,
  edu_key text,
  created_at timestamptz not null default now()
);

create table public.registered_models (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  name text not null,
  model_id uuid not null references public.models(id),
  alias text check (alias in ('champion','challenger','archived')),
  approved_by uuid references auth.users(id),
  model_card jsonb,
  created_at timestamptz not null default now()
);

create table public.predictions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  model_id uuid not null references public.models(id),
  mode text not null check (mode in ('single','batch','what_if','forecast')),
  input_path text,
  output_path text,
  summary jsonb,
  created_at timestamptz not null default now()
);

create table public.reports (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  title text not null,
  template text,
  storage_path text,
  created_at timestamptz not null default now()
);

-- AI insights, intake, suitability, decisions, AI usage ------------------
create table public.insights (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  stage text not null,
  scope jsonb not null,
  input_hash text not null,
  provider text,
  model_name text,
  prompt_version text not null,
  mode text not null default 'ai' check (mode in ('ai','numbers_only')),
  output jsonb not null,
  created_at timestamptz not null default now(),
  unique (workspace_id, input_hash, model_name, prompt_version)
);

create table public.insight_feedback (
  id bigint generated always as identity primary key,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  insight_id uuid not null references public.insights(id) on delete cascade,
  user_id uuid references auth.users(id),
  rating smallint check (rating in (-1, 1)),
  comment text,
  created_at timestamptz not null default now()
);

create table public.intake_proposals (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  dataset_version_id uuid not null references public.dataset_versions(id) on delete cascade,
  proposal jsonb not null,
  status text not null default 'proposed' check (status in ('proposed','confirmed','edited','rejected')),
  created_at timestamptz not null default now()
);

create table public.suitability_reports (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  dataset_version_id uuid not null references public.dataset_versions(id) on delete cascade,
  asset text,
  status text not null check (status in ('SUITABLE','SUITABLE_WITH_CAUTIONS','NOT_SUITABLE')),
  report jsonb not null,
  thresholds jsonb not null,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create table public.decisions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  run_id uuid references public.runs(id) on delete cascade,
  decision_point text not null check (decision_point ~ '^VD([1-9]|1[0-2])$'),
  status text not null check (status in ('proposed','blocked','approved','edited','rejected','auto_applied','reverted')),
  baseline jsonb,
  proposal jsonb,
  guard_results jsonb,
  final_choice jsonb,
  inputs_hash text not null,
  image_artefact_ids uuid[],
  prompt_version text,
  provider text,
  model_name text,
  latency_ms int,
  decided_by uuid references auth.users(id),
  decided_at timestamptz,
  created_at timestamptz not null default now()
);

create table public.decision_feedback (
  id bigint generated always as identity primary key,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  decision_id uuid not null references public.decisions(id) on delete cascade,
  user_edit jsonb,
  comment text,
  created_at timestamptz not null default now()
);

create table public.ai_usage (
  id bigint generated always as identity primary key,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  user_id uuid references auth.users(id),
  provider text not null,
  model text not null,
  feature text not null,
  prompt_tokens int,
  completion_tokens int,
  images int,
  latency_ms int,
  cached boolean not null default false,
  status text not null,
  created_at timestamptz not null default now()
);

create table public.ai_model_health (
  provider text not null,
  model text not null,
  ok boolean not null,
  latency_ms int,
  error text,
  checked_at timestamptz not null default now(),
  primary key (provider, model)
);

create table public.audit_log (
  id bigint generated always as identity primary key,
  workspace_id uuid references public.workspaces(id) on delete cascade,
  user_id uuid references auth.users(id),
  action text not null,
  entity text,
  entity_id text,
  detail jsonb,
  created_at timestamptz not null default now()
);

-- helpful indexes
create index on public.dataset_versions (workspace_id, dataset_id);
create index on public.runs (workspace_id, experiment_id);
create index on public.model_metrics (run_id, metric);
create index on public.artefacts (workspace_id, run_id);
create index on public.jobs (workspace_id, status);
create index on public.ai_usage (workspace_id, created_at);
create index on public.decisions (workspace_id, run_id);
