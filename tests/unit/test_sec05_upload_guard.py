"""SEC-05 — XLSX zip-bomb guard + defusedxml (ST-SEC-05 / oneshot-c150)."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from defusedxml.common import EntitiesForbidden

from labcore.predict.validate import check_zip_bomb, load_predict_table
from labcore.security.upload_guard import (
    ARTEFACT_ID,
    XlsxUploadRejected,
    ZIP_BOMB_RATIO,
    ZIP_BOMB_UNCOMPRESSED,
    assess_zip_totals,
    ensure_defused_xml_stdlib,
    inspect_xlsx_archive,
)

def test_artefact_id() -> None:
    assert ARTEFACT_ID == "SEC.UPLOAD.GUARD"


def test_assess_zip_totals_seed_42_limits() -> None:
    ok = assess_zip_totals(compressed=1_000, uncompressed=50_000)
    assert not ok.rejected
    assert ok.ratio == 50.0

    high_ratio = assess_zip_totals(
        compressed=1_000,
        uncompressed=int(1_000 * ZIP_BOMB_RATIO) + 1,
    )
    assert high_ratio.rejected

    huge = assess_zip_totals(
        compressed=1_000,
        uncompressed=ZIP_BOMB_UNCOMPRESSED + 1,
    )
    assert huge.rejected


def test_inspect_rejects_inflated_zip_bomb(tmp_path: Path) -> None:
    bomb = tmp_path / "evil.xlsx"
    payload = b"\x00" * (2 * 1024 * 1024)
    with zipfile.ZipFile(bomb, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("xl/worksheets/sheet1.xml", payload)
    with pytest.raises(XlsxUploadRejected, match="zip-bomb"):
        inspect_xlsx_archive(bomb)


def test_inspect_accepts_small_xlsx_zip(tmp_path: Path) -> None:
    ok_path = tmp_path / "ok.xlsx"
    with zipfile.ZipFile(ok_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("xl/workbook.xml", b"<workbook/>")
        zf.writestr("xl/worksheets/sheet1.xml", b"<worksheet><sheetData/></worksheet>")
    stats = inspect_xlsx_archive(ok_path)
    assert stats.uncompressed > 0
    assert not stats.rejected


def test_check_zip_bomb_pv01_issue(tmp_path: Path) -> None:
    bomb = tmp_path / "evil.xlsx"
    payload = b"\x00" * (2 * 1024 * 1024)
    with zipfile.ZipFile(bomb, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sheet.xml", payload)
    issue = check_zip_bomb(bomb)
    assert issue is not None
    assert issue.code == "PV01"
    assert issue.severity == "block"


def test_load_predict_table_rejects_zip_bomb(tmp_path: Path) -> None:
    bomb = tmp_path / "evil.xlsx"
    payload = b"\x00" * (2 * 1024 * 1024)
    with zipfile.ZipFile(bomb, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sheet.xml", payload)
    with pytest.raises(ValueError, match="zip-bomb"):
        load_predict_table(bomb)


def test_defused_xml_blocks_entities() -> None:
    ensure_defused_xml_stdlib()
    from xml.etree.ElementTree import fromstring

    with pytest.raises(EntitiesForbidden):
        fromstring(b'<!DOCTYPE foo [<!ENTITY xxe "e">]><foo>&xxe;</foo>')