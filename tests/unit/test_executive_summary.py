"""Executive summary HTML/PDF (REP.T.EXECUTIVE)."""

from __future__ import annotations

from labcore.reports.executive import build_executive_html, render_executive_pdf


def test_executive_html_embeds_facts_seed_42():
    facts = {"cv_mean_roc_auc": 0.88, "seed": 42, "split": "oof"}
    html_doc = build_executive_html(
        title="DS3 champion",
        stage="supervised",
        facts=facts,
        seed=42,
    )
    assert "REP.T.EXECUTIVE" in html_doc
    assert "0.88" in html_doc
    assert "seed 42" in html_doc
    assert "<script" not in html_doc.lower()


def test_executive_pdf_when_weasyprint_available():
    html_doc = build_executive_html(
        title="PDF probe",
        stage="supervised",
        facts={"seed": 42},
        seed=42,
    )
    try:
        pdf = render_executive_pdf(html_doc)
    except ModuleNotFoundError:
        return
    except Exception as exc:  # noqa: BLE001
        msg = str(exc).lower()
        assert "pango" in msg or "gobject" in msg or "font" in msg or "weasyprint" in msg
        return
    assert pdf[:4] == b"%PDF"