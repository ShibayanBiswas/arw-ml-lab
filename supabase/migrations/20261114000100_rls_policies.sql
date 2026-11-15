-- Row-level security: every workspace-scoped table is visible only to members (docs/ARCHITECTURE.md §39.5).
create or replace function public.is_member(ws uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.workspace_members m where m.workspace_id = ws and m.user_id = auth.uid());
$$;

create or replace function public.has_role(ws uuid, roles text[])
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.workspace_members m
                 where m.workspace_id = ws and m.user_id = auth.uid() and m.role = any(roles));
$$;

alter table public.organisations enable row level security;
create policy org_read on public.organisations for select
  using (exists (select 1 from public.workspaces w where w.organisation_id = organisations.id and public.is_member(w.id)));

alter table public.workspaces enable row level security;
create policy ws_read on public.workspaces for select using (public.is_member(id));
create policy ws_admin on public.workspaces for update using (public.has_role(id, array['owner','admin']));

alter table public.workspace_members enable row level security;
create policy wm_read on public.workspace_members for select using (public.is_member(workspace_id));
create policy wm_admin on public.workspace_members for all
  using (public.has_role(workspace_id, array['owner','admin']))
  with check (public.has_role(workspace_id, array['owner','admin']));

-- generic policies for workspace-scoped tables
do $$
declare t text;
begin
  foreach t in array array[
    'datasets','dataset_versions','dataset_columns','experiments','recipes','jobs','runs','models',
    'model_metrics','cv_folds','tuning_trials','artefacts','registered_models','predictions','reports',
    'insights','insight_feedback','intake_proposals','suitability_reports','decisions','decision_feedback',
    'ai_usage','audit_log']
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy %I on public.%I for select using (public.is_member(workspace_id))', t || '_read', t);
    execute format('create policy %I on public.%I for insert with check (public.has_role(workspace_id, array[''owner'',''admin'',''scientist'',''analyst'']))', t || '_insert', t);
    execute format('create policy %I on public.%I for update using (public.has_role(workspace_id, array[''owner'',''admin'',''scientist'',''analyst'']))', t || '_update', t);
    execute format('create policy %I on public.%I for delete using (public.has_role(workspace_id, array[''owner'',''admin'']))', t || '_delete', t);
  end loop;
end $$;

-- audit_log and ai_usage are append-only for users
drop policy if exists audit_log_update on public.audit_log;
drop policy if exists audit_log_delete on public.audit_log;
drop policy if exists ai_usage_update on public.ai_usage;
drop policy if exists ai_usage_delete on public.ai_usage;

-- ai_model_health is global, read-only for signed-in users; written by the backend (service role bypasses RLS)
alter table public.ai_model_health enable row level security;
create policy ai_model_health_read on public.ai_model_health for select using (auth.role() = 'authenticated');
