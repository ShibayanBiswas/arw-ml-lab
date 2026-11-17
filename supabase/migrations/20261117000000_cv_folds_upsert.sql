-- OPS-04 / ST-OPS-03: idempotent cv_folds writes keyed by (run_id, fold, algorithm_key).
-- Expand → migrate → contract: add column + unique index; app upserts via ON CONFLICT.

alter table public.cv_folds
  add column if not exists algorithm_key text not null default '';

-- Backfill empty keys stay '' so legacy rows remain unique per (run, fold).
create unique index if not exists cv_folds_run_fold_algo_uidx
  on public.cv_folds (run_id, fold, algorithm_key);

comment on column public.cv_folds.algorithm_key is
  'Registry algorithm key; with fold forms the Celery retry upsert key (OPS-04).';
