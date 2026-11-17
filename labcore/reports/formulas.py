"""KaTeX formula sheet export (REP.T.FORMULAS / ARCHITECTURE §25, §41.4, §42)."""

from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict

Family = Literal["classification", "regression"]

_GOLD = "#c9a227"
_INK = "#1a1a1a"
_KATEX_CDN = "0.19.1"


class FormulaEntry(TypedDict):
    id: str
    title: str
    family: Family
    latex: str
    library: str


# Curated §41.4 / §42 headline metrics — LaTeX only; scores come from library runs.
FORMULA_CATALOG: tuple[FormulaEntry, ...] = (
    {
        "id": "CLE.M.01",
        "title": "Accuracy",
        "family": "classification",
        "latex": r"\mathrm{Accuracy}=\frac{TP+TN}{TP+TN+FP+FN}",
        "library": "sklearn.metrics.accuracy_score",
    },
    {
        "id": "CLE.M.03",
        "title": "Balanced accuracy",
        "family": "classification",
        "latex": r"\mathrm{BA}=\frac{1}{K}\sum_{k=1}^{K}\frac{TP_k}{TP_k+FN_k}",
        "library": "sklearn.metrics.balanced_accuracy_score",
    },
    {
        "id": "CLE.M.10",
        "title": "F1 score",
        "family": "classification",
        "latex": r"F_1=\frac{2PR}{P+R}",
        "library": "sklearn.metrics.f1_score",
    },
    {
        "id": "CLE.M.14",
        "title": "Matthews correlation (MCC)",
        "family": "classification",
        "latex": r"\mathrm{MCC}=\frac{TP\cdot TN-FP\cdot FN}{\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}}",
        "library": "sklearn.metrics.matthews_corrcoef",
    },
    {
        "id": "CLE.M.24",
        "title": "Log loss",
        "family": "classification",
        "latex": r"\mathcal{L}=-\frac{1}{N}\sum_{i=1}^{N}\sum_{k=1}^{K}y_{ik}\log p_{ik}",
        "library": "sklearn.metrics.log_loss",
    },
    {
        "id": "CLE.M.30",
        "title": "ROC AUC (binary)",
        "family": "classification",
        "latex": r"\mathrm{AUC}=\int_0^1 TPR(FPR)\,d(FPR)",
        "library": "sklearn.metrics.roc_auc_score",
    },
    {
        "id": "CLE.M.34",
        "title": "Average precision (PR-AUC)",
        "family": "classification",
        "latex": r"\mathrm{AP}=\sum_n (R_n-R_{n-1})P_n",
        "library": "sklearn.metrics.average_precision_score",
    },
    {
        "id": "REE.M.01",
        "title": "R²",
        "family": "regression",
        "latex": r"R^2=1-\frac{\sum_i(y_i-\hat y_i)^2}{\sum_i(y_i-\bar y)^2}",
        "library": "sklearn.metrics.r2_score",
    },
    {
        "id": "REE.M.02",
        "title": "RMSE",
        "family": "regression",
        "latex": r"\mathrm{RMSE}=\sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat y_i)^2}",
        "library": "numpy on sklearn.metrics.mean_squared_error",
    },
    {
        "id": "REE.M.03",
        "title": "MAE",
        "family": "regression",
        "latex": r"\mathrm{MAE}=\frac{1}{n}\sum_{i=1}^{n}|y_i-\hat y_i|",
        "library": "sklearn.metrics.mean_absolute_error",
    },
    {
        "id": "REE.M.07",
        "title": "MSE",
        "family": "regression",
        "latex": r"\mathrm{MSE}=\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat y_i)^2",
        "library": "sklearn.metrics.mean_squared_error",
    },
    {
        "id": "REE.M.09",
        "title": "MAPE",
        "family": "regression",
        "latex": r"\mathrm{MAPE}=\frac{100}{n}\sum_{i=1}^{n}\left|\frac{y_i-\hat y_i}{y_i}\right|",
        "library": "thin wrapper on residuals",
    },
)


def list_formula_entries(families: set[Family] | None = None) -> list[FormulaEntry]:
    if not families:
        return list(FORMULA_CATALOG)
    return [e for e in FORMULA_CATALOG if e["family"] in families]


def build_formula_sheet_html(
    *,
    title: str,
    entries: list[FormulaEntry],
    seed: int = 42,
) -> str:
    """Static HTML with KaTeX auto-render — reference only, no computed metrics."""
    created = datetime.now(UTC).isoformat()
    blocks = []
    for e in entries:
        blocks.append(
            f"""<article class="entry" id="{html.escape(e['id'])}">
<h3>{html.escape(e['title'])} <span class="muted">{html.escape(e['id'])}</span></h3>
<p class="muted">{html.escape(e['family'])} · <code>{html.escape(e['library'])}</code></p>
<div class="math">\\[{e['latex']}\\]</div>
</article>"""
        )
    body_entries = "\n".join(blocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html.escape(title)} — Formula sheet</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@{_KATEX_CDN}/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@{_KATEX_CDN}/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@{_KATEX_CDN}/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{delimiters: [
    {{left: '\\\\(', right: '\\\\)', display: false}},
    {{left: '\\\\[', right: '\\\\]', display: true}}
  ]}});"></script>
<style>
body {{ font-family: system-ui, sans-serif; color: {_INK}; max-width: 52rem; margin: 2rem auto; line-height: 1.5; }}
h1 {{ font-family: Georgia, serif; border-bottom: 2px solid {_GOLD}; padding-bottom: 0.25rem; }}
h3 {{ color: {_INK}; font-size: 1rem; margin-bottom: 0.25rem; }}
.muted {{ color: #666; font-size: 0.85rem; }}
.entry {{ border: 1px solid #ddd; border-radius: 0.5rem; padding: 0.75rem 1rem; margin: 0.75rem 0; }}
.math {{ margin-top: 0.5rem; overflow-x: auto; }}
footer {{ margin-top: 2rem; font-size: 0.8rem; color: #666; }}
</style>
</head>
<body>
<header>
<p class="muted">REP.T.FORMULAS · seed {seed} · Asia/Kolkata</p>
<h1>{html.escape(title)}</h1>
<p>Reference LaTeX for evaluation-suite metrics (ARCHITECTURE §41.4 / §42). Values are never fabricated here.</p>
</header>
{body_entries}
<footer>Generated at {html.escape(created)} · {len(entries)} entries · KaTeX {_KATEX_CDN}</footer>
</body>
</html>"""


def build_formula_sheet(
    *,
    title: str = "Metric formula sheet",
    families: list[str] | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    allowed: set[Family] = {"classification", "regression"}
    fam_set: set[Family] | None = None
    if families:
        picked = {f for f in families if f in allowed}
        fam_set = picked if picked else None
    entries = list_formula_entries(fam_set)
    html_doc = build_formula_sheet_html(title=title, entries=entries, seed=seed)
    family_counts: dict[str, int] = {}
    for e in entries:
        family_counts[e["family"]] = family_counts.get(e["family"], 0) + 1
    return {
        "id": "REP.T.FORMULAS",
        "seed": seed,
        "title": title,
        "timezone": "Asia/Kolkata",
        "created_at": datetime.now(UTC).isoformat(),
        "entries": entries,
        "numbers": {
            "count": len(entries),
            "by_family": family_counts,
            "entry_ids": [e["id"] for e in entries],
        },
        "html": html_doc,
        "disclaimer": "Formula reference only; metric values must come from library runs on FACTS.",
        "content_hash_inputs": json.dumps(
            {"seed": seed, "title": title, "ids": [e["id"] for e in entries]}, sort_keys=True
        ),
    }