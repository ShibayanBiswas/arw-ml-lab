-- Phase 1A intake tables exist with RLS enabled (db_harness shim: plan/is/finish only)
begin;
select plan(5);

select is(
  (to_regclass('public.column_roles') is not null),
  true,
  'column_roles exists'
);
select is(
  (to_regclass('public.schema_diffs') is not null),
  true,
  'schema_diffs exists'
);
select is(
  (to_regclass('public.intake_feedback') is not null),
  true,
  'intake_feedback exists'
);
select is(
  (
    select count(*)::int
    from information_schema.columns
    where table_schema = 'public'
      and table_name = 'dataset_versions'
      and column_name = 'parent_version_id'
  ),
  1,
  'parent_version_id exists'
);
select is(
  (select relrowsecurity from pg_class where oid = 'public.column_roles'::regclass),
  true,
  'column_roles has RLS'
);

select * from finish();
rollback;
