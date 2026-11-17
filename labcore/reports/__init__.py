"""Report builder thin helpers (ARCHITECTURE §25 / §26)."""

from labcore.reports.builder import build_run_report
from labcore.reports.executive import (
    build_executive_html,
    render_executive_pdf,
    render_executive_pdf_b64,
)
from labcore.reports.formulas import build_formula_sheet, list_formula_entries
from labcore.reports.leaderboard_export import build_leaderboard_export_manifest
from labcore.reports.notebook import build_reproduction_notebook, notebook_to_json
from labcore.reports.reproduction_bundle import (
    build_reproduction_bundle_manifest,
    build_reproduction_bundle_zip,
    bundle_to_base64,
)

__all__ = [
    "build_run_report",
    "build_executive_html",
    "render_executive_pdf",
    "render_executive_pdf_b64",
    "build_reproduction_notebook",
    "notebook_to_json",
    "build_formula_sheet",
    "list_formula_entries",
    "build_leaderboard_export_manifest",
    "build_reproduction_bundle_manifest",
    "build_reproduction_bundle_zip",
    "bundle_to_base64",
]
