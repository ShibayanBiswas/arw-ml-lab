"""FE predictBatchJson must send Idempotency-Key — oneshot-c251."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "FE.PRED.IDEMPOTENCY"


def assert_fe_predict_batch_idempotency_header(
    *,
    api_ts: Path | None = None,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    text = (api_ts or root / "frontend" / "src" / "lib" / "api.ts").read_text(encoding="utf-8")
    if "export async function predictBatchJson" not in text:
        raise AssertionError(f"{ARTEFACT_ID}: predictBatchJson missing")
    # Slice the function body roughly
    start = text.index("export async function predictBatchJson")
    end = text.index("export async function predictBatchUpload", start)
    body = text[start:end]
    if 'Idempotency-Key' not in body and '"Idempotency-Key"' not in body:
        raise AssertionError(f"{ARTEFACT_ID}: predictBatchJson must set Idempotency-Key")
    return {"id": ARTEFACT_ID, "seed": 42, "ok": True}
