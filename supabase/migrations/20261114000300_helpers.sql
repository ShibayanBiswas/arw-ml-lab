-- Helper used by storage policies: a malformed folder name returns NULL (policy denies) instead of raising 22P02.
create or replace function public.try_uuid(t text) returns uuid
language plpgsql immutable as $$
begin
  return t::uuid;
exception when others then
  return null;
end $$;
