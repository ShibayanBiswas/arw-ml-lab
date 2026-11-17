"""Preprocess home route wires TrainWorkbench instead of ModulePlaceholder."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "frontend" / "src" / "app" / "(lab)" / "[module]" / "[page]" / "page.tsx"


def test_preprocess_home_in_recipe_block() -> None:
    src = PAGE.read_text(encoding="utf-8")
    idx = src.find('slug === "preprocess"')
    assert idx >= 0
    chunk = src[idx : idx + 420]
    assert 'page === "home"' in chunk
    assert "TrainWorkbench" in chunk