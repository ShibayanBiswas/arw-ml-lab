"""KaTeX formula sheet export (REP.T.FORMULAS)."""

from __future__ import annotations

from labcore.reports.formulas import build_formula_sheet, list_formula_entries


def test_formula_catalog_seed_and_ids() -> None:
    sheet = build_formula_sheet(seed=42)
    assert sheet["id"] == "REP.T.FORMULAS"
    assert sheet["seed"] == 42
    assert sheet["numbers"]["count"] == len(list_formula_entries())
    assert "CLE.M.01" in sheet["numbers"]["entry_ids"]
    assert "REE.M.01" in sheet["numbers"]["entry_ids"]


def test_formula_sheet_html_tags_artefact() -> None:
    sheet = build_formula_sheet(title="Demo", families=["classification"], seed=42)
    assert sheet["numbers"]["count"] == 7
    html_doc = sheet["html"]
    assert "REP.T.FORMULAS" in html_doc
    assert "katex" in html_doc
    assert "CLE.M.14" in html_doc
    assert "REE.M.01" not in html_doc