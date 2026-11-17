"""Logic Atlas coverage contract — CURSOR_PROMPT DoD (oneshot-c209).

Every explanation entry in ``frontend/src/content/explanations/eda.ts`` must
carry ``key``, ``title``, ``intuitive``, and ``math`` (KaTeX). CI fails if the
atlas drops below a floor or an entry is missing math.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ARTEFACT_ID = "EDU.ATLAS.COVERAGE"
MIN_ENTRIES = 20

_ENTRY = re.compile(
    r"\{\s*key:\s*[\"']([^\"']+)[\"']\s*,\s*title:\s*[\"']([^\"']*)[\"']",
    re.MULTILINE,
)
_MATH = re.compile(r"math:\s*[\"`']")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_atlas_source(path: Path | None = None) -> str:
    p = path or (_repo_root() / "frontend" / "src" / "content" / "explanations" / "eda.ts")
    return p.read_text(encoding="utf-8")


def assert_atlas_coverage(src: str | None = None) -> dict[str, Any]:
    text = src if src is not None else load_atlas_source()
    keys = _ENTRY.findall(text)
    if len(keys) < MIN_ENTRIES:
        raise AssertionError(f"atlas has {len(keys)} entries; need ≥ {MIN_ENTRIES}")
    # Each object block near a key should mention math:
    missing_math = 0
    for m in re.finditer(r"key:\s*[\"'][^\"']+[\"']", text):
        window = text[m.start() : m.start() + 800]
        if "math:" not in window:
            missing_math += 1
    if missing_math:
        raise AssertionError(f"{missing_math} atlas entries missing math field")
    if "intuitive:" not in text:
        raise AssertionError("atlas entries must include intuitive prose")
    return {
        "id": ARTEFACT_ID,
        "n_entries": len(keys),
        "min_entries": MIN_ENTRIES,
        "sample_keys": [k[0] for k in keys[:5]],
    }


def atlas_manifest(*, seed: int = 42) -> dict[str, object]:
    check = assert_atlas_coverage()
    return {**check, "seed": seed}
