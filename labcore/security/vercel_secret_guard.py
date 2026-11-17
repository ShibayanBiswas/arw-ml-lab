"""Vercel must never hold NVIDIA_API_KEY — SEC / §40.8 (oneshot-c203).

Scans frontend source and ``.env.example`` for forbidden client-side AI keys.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "SEC.NO.NVIDIA.VERCEL"
FORBIDDEN = (
    "NVIDIA_API_KEY",
    "NEXT_PUBLIC_NVIDIA",
    "NEXT_PUBLIC_OPENAI",
    "NEXT_PUBLIC_AI_API",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _scan_text(label: str, text: str) -> list[str]:
    hits: list[str] = []
    for token in FORBIDDEN:
        if token in text:
            hits.append(f"{label}: {token}")
    return hits


def assert_no_nvidia_in_frontend() -> dict[str, Any]:
    root = _repo_root() / "frontend"
    hits: list[str] = []
    scan_roots = [
        root / "src",
        root / ".env.example",
        root / ".env.local.example",
        root / "README.md",
    ]
    files: list[Path] = []
    for item in scan_roots:
        if item.is_file():
            files.append(item)
        elif item.is_dir():
            for path in item.rglob("*"):
                if path.is_file() and path.suffix.lower() in {
                    ".ts",
                    ".tsx",
                    ".js",
                    ".jsx",
                    ".mjs",
                    ".env",
                    ".md",
                }:
                    files.append(path)
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        hits.extend(_scan_text(rel, text))
    env_ex = _repo_root() / ".env.example"
    if env_ex.is_file():
        # .env.example may document NVIDIA for the *server* — only forbid NEXT_PUBLIC forms
        text = env_ex.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token.startswith("NEXT_PUBLIC_") and token in text:
                hits.append(f".env.example: {token}")
    if hits:
        raise AssertionError("forbidden client AI secrets: " + "; ".join(hits[:10]))
    return {"id": ARTEFACT_ID, "scanned": "frontend/", "forbidden": list(FORBIDDEN), "hits": 0}


def vercel_secret_manifest(*, seed: int = 42) -> dict[str, object]:
    check = assert_no_nvidia_in_frontend()
    return {**check, "seed": seed}
