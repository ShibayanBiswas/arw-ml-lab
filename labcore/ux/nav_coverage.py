"""Every MODULES nav leaf must resolve to a real workbench — FE.NAV.COVERAGE (oneshot-c219)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ARTEFACT_ID = "FE.NAV.COVERAGE"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _modules_nav_leaves() -> dict[str, set[str]]:
    text = (_repo_root() / "frontend" / "src" / "lib" / "modules.ts").read_text(encoding="utf-8")
    # Split on routeSlug blocks
    blocks = re.split(r"routeSlug:\s*\"([^\"]+)\"", text)
    out: dict[str, set[str]] = {}
    # blocks: [preamble, slug1, body1, slug2, body2, ...]
    for i in range(1, len(blocks), 2):
        slug = blocks[i]
        body = blocks[i + 1] if i + 1 < len(blocks) else ""
        # Stop at next top-level module object end — take until next `id:` at module depth is hard;
        # instead collect { id: "..." } inside the first `nav: leaves(...)` of this body.
        nav_m = re.search(r"nav:\s*leaves\([^[]*\[(.*?)\]\s*\)", body, re.S)
        if not nav_m:
            continue
        ids = set(re.findall(r"\{\s*id:\s*\"([^\"]+)\"", nav_m.group(1)))
        out[slug] = ids
    return out


def _page_tsx_covered() -> dict[str, set[str]]:
    """Parse page.tsx slug/page equality checks that return a workbench (before ModulePlaceholder)."""
    text = (_repo_root() / "frontend" / "src" / "app" / "(lab)" / "[module]" / "[page]" / "page.tsx").read_text(
        encoding="utf-8"
    )
    # Drop the JSX fallback only (import also mentions ModulePlaceholder).
    cut_m = re.search(r"return\s*\(\s*<ModulePlaceholder", text)
    cut = text[: cut_m.start()] if cut_m else text
    covered: dict[str, set[str]] = {}

    # Pattern: slug === "X" && (page === "a" || ...)  OR  slug === "X" && page === "a"
    for m in re.finditer(
        r'slug\s*===\s*"([^"]+)"\s*&&\s*\(([^)]+)\)',
        cut,
    ):
        slug, inner = m.group(1), m.group(2)
        pages = set(re.findall(r'page\s*===\s*"([^"]+)"', inner))
        covered.setdefault(slug, set()).update(pages)

    for m in re.finditer(r'slug\s*===\s*"([^"]+)"\s*&&\s*page\s*===\s*"([^"]+)"', cut):
        covered.setdefault(m.group(1), set()).add(m.group(2))

    # Whole-module catch-alls: if (slug === "eda") / if (slug === "learn")
    for slug in ("eda", "learn"):
        if re.search(rf'if\s*\(\s*slug\s*===\s*"{slug}"\s*\)', cut):
            covered.setdefault(slug, set()).add("__ALL__")

    # data: individual if (page === ...) under slug === "data"
    data_block = re.search(r'if\s*\(\s*slug\s*===\s*"data"\s*\)\s*\{(.*?)\}', cut, re.S)
    if data_block:
        pages = set(re.findall(r'page\s*===\s*"([^"]+)"', data_block.group(1)))
        covered.setdefault("data", set()).update(pages)

    return covered


def assert_nav_coverage() -> dict[str, Any]:
    nav = _modules_nav_leaves()
    routed = _page_tsx_covered()
    missing: list[str] = []
    for slug, pages in sorted(nav.items()):
        r = routed.get(slug, set())
        if "__ALL__" in r:
            continue
        for p in sorted(pages):
            if p not in r:
                missing.append(f"{slug}/{p}")
    if missing:
        raise AssertionError(f"{ARTEFACT_ID}: unrouted nav leaves (would hit ModulePlaceholder): {missing}")
    return {
        "id": ARTEFACT_ID,
        "seed": 42,
        "modules": len(nav),
        "leaves": sum(len(v) for v in nav.values()),
        "missing": [],
    }
