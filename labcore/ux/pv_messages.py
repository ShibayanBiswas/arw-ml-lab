"""Stable PV code → plain-language hints for the UI (ST-UX-03 / §46.4)."""

from __future__ import annotations

# Codes emitted by ``labcore.predict.validate`` (implemented slice; not invented metrics).
IMPLEMENTED_PV_CODES: tuple[str, ...] = (
    "PV01",
    "PV02",
    "PV03",
    "PV04",
    "PV05",
    "PV06",
    "PV07",
    "PV08",
    "PV09",
    "PV10",
    "PV11",
    "PV12",
    "PV13",
    "PV14",
    "PV15",
    "PV16",
)

PV_MESSAGES: dict[str, dict[str, str]] = {
    "PV01": {
        "title": "File type or archive rejected",
        "fix": "Upload CSV, TSV, XLSX, or Parquet within size limits; avoid zip bombs.",
    },
    "PV02": {
        "title": "Upload too large",
        "fix": "Split the batch, reduce row count, or use the async batch job.",
    },
    "PV03": {
        "title": "Encoding or headers invalid",
        "fix": "Save as UTF-8 CSV with unique column names and a consistent delimiter.",
    },
    "PV04": {
        "title": "Required features missing",
        "fix": "Match column names to the feature contract template (case-insensitive).",
    },
    "PV05": {
        "title": "Unexpected columns or target leak",
        "fix": "Drop extra columns and remove the training target from the upload.",
    },
    "PV06": {
        "title": "Type coercion failed",
        "fix": "Fix numeric, boolean, or categorical values for the listed column.",
    },
    "PV07": {
        "title": "Categorical value out of vocabulary",
        "fix": "Use only values seen in training or map to the documented categories.",
    },
    "PV08": {
        "title": "Numeric value out of range",
        "fix": "Keep numbers within the contract min/max or clip before upload.",
    },
    "PV09": {
        "title": "Required value missing",
        "fix": "Fill non-nullable feature cells referenced by the contract.",
    },
    "PV10": {
        "title": "Input looks out of distribution",
        "fix": "Review extreme values; predictions may be flagged as uncertain.",
    },
    "PV11": {
        "title": "Batch feature drift",
        "fix": "Compare PSI/KS against the training reference; retrain if drift is high.",
    },
    "PV12": {
        "title": "Sequential history issue",
        "fix": "Parse the time column, sort within series, remove duplicate timestamps, and supply enough lookback rows for lag features.",
    },
    "PV13": {
        "title": "Forecast horizon rejected",
        "fix": "Request a horizon within HorizonGuard h_max for the series length and frequency.",
    },
    "PV14": {
        "title": "Duplicate row keys",
        "fix": "Remove duplicate identifiers or aggregate rows before upload.",
    },
    "PV15": {
        "title": "Formula-like cells sanitised",
        "fix": "Leading = + - @ cells are escaped on export; no action required.",
    },
    "PV16": {
        "title": "Identifier-like columns present",
        "fix": "Identifier values are never sent to VLM/LLM prompts; mask or drop before export if needed.",
    },
}


def pv_message_for_code(code: str) -> dict[str, str]:
    msg = PV_MESSAGES.get(code)
    if msg is None:
        raise KeyError(f"unknown PV code for UI map: {code!r}")
    return msg