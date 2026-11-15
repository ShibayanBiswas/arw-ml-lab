-- Phase 1A: intake detail tables (§33.13) + dataset_versions lineage.

alter table public.dataset_versions
  add column if not exists parent_version_id uuid references public.dataset_versions(id);

-- Expand kit intake_proposals to §33.13 shape (additive).
alter table public.intake_proposals
  add column if not exists rules_version text not null default 'intake-1.0',
  add column if not exists llm_model text,
  add column if not exists prompt_version text,
  add column if not exists detector_output jsonb not null default '{}'::jsonb,
  add column if not exists llm_output jsonb,
  add column if not exists merged jsonb not null default '{}'::jsonb,
  add column if not exists validator_report jsonb,
  add column if not exists user_overrides jsonb,
  add column if not exists confirmed_by uuid references auth.users(id),
  add column if not exists confirmed_at timestamptz,
  add column if not exists confidence_overall double precision;

-- Align status enum values with §33.13 (keep kit values + superseded).
alter table public.intake_proposals drop constraint if exists intake_proposals_status_check;
alter table public.intake_proposals
  add constraint intake_proposals_status_check
  check (status in ('proposed','edited','confirmed','superseded','rejected'));

create table if not exists public.column_roles (
  proposal_id uuid not null references public.intake_proposals(id) on delete cascade,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  column_name text not null,
  role text,
  confidence double precision,
  tags text[],
  reasons jsonb,
  included boolean not null default true,
  encoder text,
  transform text,
  primary key (proposal_id, column_name)
);

create table if not exists public.schema_diffs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  dataset_id uuid not null references public.datasets(id) on delete cascade,
  from_version_id uuid references public.dataset_versions(id),
  to_version_id uuid references public.dataset_versions(id),
  changes jsonb not null,
  drift jsonb,
  severity text,
  breaking boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.intake_feedback (
  id bigint generated always as identity primary key,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  proposal_id uuid not null references public.intake_proposals(id) on delete cascade,
  accepted boolean,
  overrides jsonb,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

-- RLS
alter table public.column_roles enable row level security;
create policy column_roles_read on public.column_roles for select using (public.is_member(workspace_id));

alter table public.schema_diffs enable row level security;
create policy schema_diffs_read on public.schema_diffs for select using (public.is_member(workspace_id));

alter table public.intake_feedback enable row level security;
create policy intake_feedback_read on public.intake_feedback for select using (public.is_member(workspace_id));
create policy intake_feedback_insert on public.intake_feedback for insert
  with check (public.has_role(workspace_id, array['owner','admin','scientist','analyst']));

-- Worker-only writes for column_roles / schema_diffs (no user insert/update policies).
-- intake_proposals already hardened in 20261115000100_hardening.sql.
