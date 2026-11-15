-- Minimal stand-ins for Supabase auth/storage schemas and a tiny pgTAP shim, so migrations and
-- supabase/tests/*.sql can run on a plain Postgres without Docker. The real check is `supabase test db`.
do $$ begin
  if not exists (select 1 from pg_roles where rolname='authenticated') then create role authenticated nologin; end if;
  if not exists (select 1 from pg_roles where rolname='anon') then create role anon nologin; end if;
  if not exists (select 1 from pg_roles where rolname='service_role') then create role service_role nologin bypassrls; end if;
end $$;
create schema auth;
create table auth.users (id uuid primary key, email text);
create function auth.uid() returns uuid language sql stable as $$ select nullif(current_setting('request.jwt.claims', true)::json->>'sub','')::uuid $$;
create function auth.role() returns text language sql stable as $$ select coalesce(current_setting('request.jwt.claims', true)::json->>'role','anon') $$;
create schema storage;
create table storage.buckets (id text primary key, name text, public boolean, file_size_limit bigint, allowed_mime_types text[]);
create table storage.objects (id uuid primary key default gen_random_uuid(), bucket_id text references storage.buckets(id), name text, owner uuid);
alter table storage.objects enable row level security;
create function storage.foldername(name text) returns text[] language sql immutable as $$ select (string_to_array(name,'/'))[1:array_length(string_to_array(name,'/'),1)-1] $$;
grant usage on schema public, auth, storage to authenticated, anon, service_role;
grant all on all tables in schema storage to authenticated, service_role;
grant execute on all functions in schema auth to authenticated, anon;
alter default privileges in schema public grant all on tables to authenticated, anon, service_role;
alter default privileges in schema public grant all on sequences to authenticated, anon, service_role;
alter default privileges in schema public grant execute on functions to authenticated, anon, service_role;
-- minimal pgTAP shim (plan/is/lives_ok/throws_ok/finish)
create table public._tap (n serial, ok boolean, msg text);
grant all on public._tap, public._tap_n_seq to authenticated;
create function plan(int) returns text language sql as $$ select '1..'||$1 $$;
create function is(anyelement, anyelement, text) returns text language plpgsql as $$
begin insert into public._tap(ok,msg) values ($1 is not distinct from $2, $3); return case when $1 is not distinct from $2 then 'ok - ' else 'NOT OK - ' end || $3 || ' (got '||coalesce($1::text,'null')||')'; end $$;
create function lives_ok(text, text) returns text language plpgsql as $$
begin execute $1; insert into public._tap(ok,msg) values (true,$2); return 'ok - '||$2;
exception when others then insert into public._tap(ok,msg) values (false,$2); return 'NOT OK - '||$2||' ('||sqlerrm||')'; end $$;
create function throws_ok(text, text, text, text) returns text language plpgsql as $$
begin execute $1; insert into public._tap(ok,msg) values (false,$4); return 'NOT OK - '||$4||' (no error)';
exception when others then insert into public._tap(ok,msg) values (sqlstate=$2,$4); return case when sqlstate=$2 then 'ok - ' else 'NOT OK - ' end||$4||' ('||sqlstate||' '||sqlerrm||')'; end $$;
create function finish() returns text language sql as $$ select 'done' $$;
