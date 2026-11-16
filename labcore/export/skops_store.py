"""Safe sklearn persistence via skops (§44 / SEC-06)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from skops.io import dump, load


def save_skops(estimator: Any, path: str | Path) -> dict[str, str | int]:
    """Persist estimator with skops; return path + sha256 + size."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dump(estimator, path)
    raw = path.read_bytes()
    return {
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "format": "skops",
    }


def load_skops(path: str | Path, *, expected_sha256: str | None = None) -> Any:
    """Load skops artefact; optionally verify sha256 before trust."""
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("skops artefact sha256 mismatch")
    return load(path)
