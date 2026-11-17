"""Upload hardening — zip/XML bombs for XLSX (SEC-05 / §45.3 PV01, rule 60)."""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ARTEFACT_ID = "SEC.UPLOAD.GUARD"

# §45.3 PV01 / §46.3 SEC-05
ZIP_BOMB_RATIO = 100
ZIP_BOMB_UNCOMPRESSED = 500 * 1024 * 1024

_DEFUSED = False


@dataclass(frozen=True)
class ZipBombAssessment:
    compressed: int
    uncompressed: int
    ratio: float

    @property
    def rejected(self) -> bool:
        return (
            self.uncompressed > ZIP_BOMB_UNCOMPRESSED
            or self.ratio > ZIP_BOMB_RATIO
        )


class XlsxUploadRejected(Exception):
    """Raised when an XLSX/ZIP archive fails SEC-05 guards."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


def assess_zip_totals(compressed: int, uncompressed: int) -> ZipBombAssessment:
    base = max(compressed, 1)
    return ZipBombAssessment(
        compressed=compressed,
        uncompressed=uncompressed,
        ratio=uncompressed / base,
    )


def _open_zip(source: Path | bytes) -> zipfile.ZipFile:
    if isinstance(source, Path):
        return zipfile.ZipFile(source)
    return zipfile.ZipFile(io.BytesIO(source))


def inspect_xlsx_archive(source: Path | bytes) -> ZipBombAssessment:
    """Return zip statistics or raise ``XlsxUploadRejected`` (calamine read is separate)."""
    try:
        with _open_zip(source) as zf:
            compressed = sum(i.compress_size for i in zf.infolist())
            uncompressed = sum(i.file_size for i in zf.infolist())
    except zipfile.BadZipFile as exc:
        raise XlsxUploadRejected(
            "invalid XLSX/ZIP archive",
            details={"reason": str(exc)},
        ) from exc
    assessment = assess_zip_totals(compressed, uncompressed)
    if assessment.rejected:
        raise XlsxUploadRejected(
            "zip-bomb guard: XLSX compression ratio or size rejected",
            details={
                "uncompressed": assessment.uncompressed,
                "compressed": assessment.compressed,
                "ratio": assessment.ratio,
            },
        )
    return assessment


def ensure_defused_xml_stdlib() -> None:
    """Harden stdlib XML before any openpyxl write (defusedxml SEC-05)."""
    global _DEFUSED
    if _DEFUSED:
        return
    from defusedxml import defuse_stdlib

    defuse_stdlib()
    _DEFUSED = True