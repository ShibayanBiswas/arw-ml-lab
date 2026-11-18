"""q.predict.batch — chunked Prediction Studio scoring (ARCHITECTURE §45.8)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from labcore.ops.cancel_flags import cancel_flag_key_for_job, default_cancel_store
from labcore.ops.soft_time_limit import (
    PartialHolder,
    is_soft_time_limit_exc,
    save_best_so_far,
)
from labcore.predict.score import predict_batch
from labcore.predict.template import predictions_to_safe_csv
from labcore.predict.validate import validate_predict_frame

from backend.app.jobs_store import JOB_STORE
from backend.app.model_store import MODEL_STORE
from backend.worker.celery_app import celery_app

CHUNK = 10_000
MAX_ROWS = 1_000_000


@celery_app.task(name="lab.predict.batch", bind=True, queue="q.predict.batch")
def run_predict_batch_task(
    self,
    job_id: str,
    model_id: str,
    rows: list[dict[str, Any]],
    *,
    cancel_flag_key: str | None = None,
) -> dict[str, Any]:
    """Score up to 1M rows in chunks; cooperatively cancel via JOB_STORE + cancel flags."""
    _ = self
    holder = PartialHolder()
    flag_key = cancel_flag_key or cancel_flag_key_for_job(job_id)
    flags = default_cancel_store()
    JOB_STORE.update(
        job_id,
        status="running",
        progress=0.05,
        step="validate",
        event={"type": "progress", "pct": 0.05, "step": "validate"},
    )
    try:
        m = MODEL_STORE.get(model_id)
        if m is None:
            JOB_STORE.update(job_id, status="failed", error="model not found")
            raise FileNotFoundError(f"model {model_id} not found")

        if len(rows) > MAX_ROWS:
            JOB_STORE.update(
                job_id,
                status="failed",
                error=f"PV02: {len(rows)} rows > {MAX_ROWS}",
            )
            raise ValueError(f"PV02: {len(rows)} rows > {MAX_ROWS}")

        df = pd.DataFrame(rows)
        report = validate_predict_frame(
            df,
            m.feature_contract,
            required_names=m.feature_names,
            source_name="celery.batch.json",
            max_rows=MAX_ROWS,
        )
        if not report.ok or report.coerced is None:
            out = {"validation": report.to_dict(), "scored": False, "predictions": None}
            JOB_STORE.update(job_id, status="done", progress=1.0, result=out)
            return out

        work = report.coerced
        n = len(work)
        preds: list[Any] = []
        probas: list[Any] | None = None

        for start in range(0, n, CHUNK):
            job = JOB_STORE.get(job_id)
            if job is not None and getattr(job, "status", None) == "cancelled":
                JOB_STORE.update(
                    job_id,
                    status="cancelled",
                    progress=start / max(n, 1),
                    error="cancelled",
                )
                return {"scored": False, "cancelled": True, "n_done": start}
            if flags.is_cancelled(flag_key):
                JOB_STORE.update(
                    job_id,
                    status="cancelled",
                    progress=start / max(n, 1),
                    error="cancelled_flag",
                )
                flags.clear(flag_key)
                return {"scored": False, "cancelled": True, "n_done": start, "via": "cancel_flag"}

            chunk = work.iloc[start : start + CHUNK]
            scored = predict_batch(m.pipeline, chunk, feature_names=m.feature_names)
            preds.extend(scored["predictions"])
            p = scored.get("probabilities")
            if p is not None:
                if probas is None:
                    probas = []
                probas.extend(p)
            pct = min(0.95, 0.1 + 0.85 * ((start + len(chunk)) / max(n, 1)))
            holder.update(
                {
                    "n_done": len(preds),
                    "n_rows": n,
                    "predictions_partial": list(preds),
                    "probabilities_partial": list(probas) if probas is not None else None,
                    "scored": False,
                    "partial_checkpoint": True,
                }
            )
            JOB_STORE.update(
                job_id,
                progress=pct,
                step=f"score_{start}",
                event={"type": "progress", "pct": pct, "step": f"chunk {start}"},
            )

        out_df = work.copy()
        out_df["prediction"] = preds
        csv_text = predictions_to_safe_csv(out_df).decode("utf-8")
        result = {
            "validation": report.to_dict(),
            "scored": True,
            "refit": False,
            "n_rows": n,
            "predictions": preds,
            "probabilities": probas,
            "csv": csv_text,
            "chunk_size": CHUNK,
        }
        holder.update(result)
        JOB_STORE.update(
            job_id,
            status="done",
            progress=1.0,
            result=result,
            event={"type": "done", "pct": 1.0},
        )
        flags.clear(flag_key)
        return {"n_rows": n, "scored": True}
    except Exception as exc:
        if is_soft_time_limit_exc(exc):
            return save_best_so_far(
                job_update=JOB_STORE.update,
                experiment_update=None,
                job_id=job_id,
                experiment_id=None,
                partial=holder.value,
                seed=42,
            )
        JOB_STORE.update(
            job_id,
            status="error",
            error=str(exc),
            event={"type": "error", "message": str(exc)},
        )
        raise
