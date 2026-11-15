-- Helper used by storage policies: a malformed folder name returns NULL (policy denies) instead of raising 22P02.
create or replace function public.try_uuid(t text) returns uuid
language plpgsql immutable set search_path = public as $$
begin
  return t::uuid;
exception when others then
  return null;
end $$;
