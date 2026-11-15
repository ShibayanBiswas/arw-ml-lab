-- pgTAP: Prediction Studio RLS (run with `supabase test db`)
begin;
select plan(10);

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
insert into public.experiments (id, workspace_id, name, family) values
  ('eeeeeeee-0000-0000-0000-00000000000a', 'aaaaaaaa-0000-0000-0000-00000000000a', 'exp-a', 'supervised');
insert into public.runs (id, workspace_id, experiment_id, algorithm_key, params) values
  ('dddddddd-0000-0000-0000-00000000000a', 'aaaaaaaa-0000-0000-0000-00000000000a', 'eeeeeeee-0000-0000-0000-00000000000a', 'clf.logreg', '{}');
insert into public.models (id, workspace_id, run_id) values
  ('cccccccc-0000-0000-0000-00000000000a', 'aaaaaaaa-0000-0000-0000-00000000000a', 'dddddddd-0000-0000-0000-00000000000a');
insert into public.model_signatures (model_id, workspace_id, task, feature_contract, contract_hash) values
  ('cccccccc-0000-0000-0000-00000000000a', 'aaaaaaaa-0000-0000-0000-00000000000a', 'binary', '{"features":[]}', 'h');
insert into public.prediction_jobs (id, workspace_id, model_id, mode) values
  ('bbbbbbbb-0000-0000-0000-00000000000a', 'aaaaaaaa-0000-0000-0000-00000000000a', 'cccccccc-0000-0000-0000-00000000000a', 'batch');
insert into public.prediction_results (workspace_id, prediction_job_id, row_index, prediction) values
  ('aaaaaaaa-0000-0000-0000-00000000000a', 'bbbbbbbb-0000-0000-0000-00000000000a', 0, '{"y_hat":1}');

set local role authenticated;
set local request.jwt.claims = '{"sub":"11111111-1111-1111-1111-111111111111","role":"authenticated"}';
select is((select count(*) from public.prediction_results)::int, 1, 'member of A reads A results');
select is((select count(*) from public.model_signatures)::int, 1, 'member of A reads the contract');
select lives_ok($$insert into public.prediction_jobs (workspace_id, model_id, mode)
                  values ('aaaaaaaa-0000-0000-0000-00000000000a', 'cccccccc-0000-0000-0000-00000000000a', 'single')$$,
                'analyst can create a prediction job');
select throws_ok($$insert into public.prediction_results (workspace_id, prediction_job_id, row_index, prediction)
                   values ('aaaaaaaa-0000-0000-0000-00000000000a', 'bbbbbbbb-0000-0000-0000-00000000000a', 1, '{}')$$,
                 '42501', null, 'users cannot write prediction results (worker only)');
select throws_ok($$insert into public.model_metrics (workspace_id, run_id, split, metric, value)
                   values ('aaaaaaaa-0000-0000-0000-00000000000a', 'dddddddd-0000-0000-0000-00000000000a', 'test', 'auc', 0.99)$$,
                 '42501', null, 'users cannot fabricate metrics');
select throws_ok($$insert into storage.objects (bucket_id, name) values ('predictions', 'not-a-uuid/input.csv')$$,
                 '42501', null, 'malformed storage path is denied, not a cast error');
select lives_ok($$insert into storage.objects (bucket_id, name)
                  values ('predictions', 'aaaaaaaa-0000-0000-0000-00000000000a/bbbbbbbb-0000-0000-0000-00000000000a/input.csv')$$,
                'analyst can upload a prediction input to own workspace');
with u as (update public.prediction_jobs set status = 'succeeded' returning 1)
select is((select count(*) from u)::int, 0, 'users cannot change prediction job status (worker only)');

set local request.jwt.claims = '{"sub":"22222222-2222-2222-2222-222222222222","role":"authenticated"}';
select is((select count(*) from public.prediction_jobs)::int, 0, 'member of B cannot see A prediction jobs');
select is((select count(*) from public.prediction_results)::int, 0, 'member of B cannot see A results');

select * from finish();
rollback;
