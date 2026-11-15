-- pgTAP RLS tests: run with `supabase test db`
begin;
select plan(4);

insert into auth.users (id, email) values
  ('11111111-1111-1111-1111-111111111111', 'a@example.com'),
  ('22222222-2222-2222-2222-222222222222', 'b@example.com');
insert into public.organisations (id, name) values ('aaaaaaaa-0000-0000-0000-000000000001', 'Org');
insert into public.workspaces (id, organisation_id, name) values
  ('aaaaaaaa-0000-0000-0000-00000000000a', 'aaaaaaaa-0000-0000-0000-000000000001', 'WS-A'),
  ('aaaaaaaa-0000-0000-0000-00000000000b', 'aaaaaaaa-0000-0000-0000-000000000001', 'WS-B');
insert into public.workspace_members values
  ('aaaaaaaa-0000-0000-0000-00000000000a', '11111111-1111-1111-1111-111111111111', 'analyst', now()),
  ('aaaaaaaa-0000-0000-0000-00000000000b', '22222222-2222-2222-2222-222222222222', 'viewer', now());
insert into public.datasets (workspace_id, name) values
  ('aaaaaaaa-0000-0000-0000-00000000000a', 'ds-a'), ('aaaaaaaa-0000-0000-0000-00000000000b', 'ds-b');

set local role authenticated;
set local request.jwt.claims = '{"sub":"11111111-1111-1111-1111-111111111111","role":"authenticated"}';
select is((select count(*) from public.datasets)::int, 1, 'user A sees only workspace A datasets');
select is((select name from public.datasets limit 1), 'ds-a', 'user A sees ds-a');

set local request.jwt.claims = '{"sub":"22222222-2222-2222-2222-222222222222","role":"authenticated"}';
select is((select count(*) from public.datasets)::int, 1, 'user B sees only workspace B datasets');
select throws_ok(
  $$insert into public.datasets (workspace_id, name) values ('aaaaaaaa-0000-0000-0000-00000000000b', 'x')$$,
  '42501', null, 'viewer cannot insert');

select * from finish();
rollback;
