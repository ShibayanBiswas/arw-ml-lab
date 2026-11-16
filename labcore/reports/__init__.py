"""Report builder thin helpers (ARCHITECTURE §25 / §26)."""

from labcore.reports.builder import build_run_report
from labcore.reports.notebook import build_reproduction_notebook, notebook_to_json

__all__ = ["build_run_report", "build_reproduction_notebook", "notebook_to_json"]
