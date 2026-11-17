"""Report builder thin helpers (ARCHITECTURE §25 / §26)."""

from labcore.reports.builder import build_run_report
from labcore.reports.executive import (
    build_executive_html,
    render_executive_pdf,
    render_executive_pdf_b64,
)
from labcore.reports.formulas import build_formula_sheet, list_formula_entries
from labcore.reports.notebook import build_reproduction_notebook, notebook_to_json

__all__ = [
    "build_run_report",
    "build_executive_html",
    "render_executive_pdf",
    "render_executive_pdf_b64",
    "build_reproduction_notebook",
    "notebook_to_json",
    "build_formula_sheet",
    "list_formula_entries",
]
