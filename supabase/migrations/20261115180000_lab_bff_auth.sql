-- Phase 2 BFF auth tables (ADR-0005) — roster users + OTP; not Supabase Auth
create table if not exists public.lab_app_users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  name text not null,
  role text not null default 'scientist',
  password_hash text not null,
  active_session_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.lab_otps (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.lab_app_users(id) on delete cascade,
  email text not null,
  code text not null,
  expires_at timestamptz not null,
  consumed boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists lab_otps_user_idx on public.lab_otps(user_id) where not consumed;

alter table public.lab_app_users enable row level security;
alter table public.lab_otps enable row level security;

-- Browser clients never read password hashes; service role / BFF only
create policy lab_app_users_deny_all on public.lab_app_users
  for all to authenticated, anon using (false) with check (false);
create policy lab_otps_deny_all on public.lab_otps
  for all to authenticated, anon using (false) with check (false);
