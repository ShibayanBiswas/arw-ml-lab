-- Phase 2 BFF auth tables exist with RLS
begin;
select plan(3);
select is((to_regclass('public.lab_app_users') is not null), true, 'lab_app_users exists');
select is((to_regclass('public.lab_otps') is not null), true, 'lab_otps exists');
select is(
  (select relrowsecurity from pg_class where oid = 'public.lab_app_users'::regclass),
  true,
  'lab_app_users has RLS'
);
select * from finish();
rollback;
