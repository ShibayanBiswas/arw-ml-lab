-- Local development seed (supabase db reset). No real users or client data.
insert into public.organisations (id, name) values ('00000000-0000-0000-0000-000000000001', 'ARW ML Lab (local)')
on conflict do nothing;
insert into public.workspaces (id, organisation_id, name, data_classification)
values ('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'Sandbox', 'internal')
on conflict do nothing;
