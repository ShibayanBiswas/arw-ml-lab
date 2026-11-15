-- Private storage buckets; object path convention: {workspace_id}/{entity}/{id}/{file}
insert into storage.buckets (id, name, public)
values ('datasets','datasets',false), ('artefacts','artefacts',false), ('models','models',false),
       ('reports','reports',false), ('plots','plots',false)
on conflict (id) do nothing;

create policy lab_objects_read on storage.objects for select to authenticated
  using (bucket_id in ('datasets','artefacts','models','reports','plots')
         and public.is_member(((storage.foldername(name))[1])::uuid));

create policy lab_objects_insert on storage.objects for insert to authenticated
  with check (bucket_id in ('datasets','reports')
              and public.has_role(((storage.foldername(name))[1])::uuid, array['owner','admin','scientist','analyst']));

create policy lab_objects_delete on storage.objects for delete to authenticated
  using (bucket_id in ('datasets','artefacts','models','reports','plots')
         and public.has_role(((storage.foldername(name))[1])::uuid, array['owner','admin']));
-- artefacts, models and plots are written by Render workers with the service-role key (bypasses RLS).
