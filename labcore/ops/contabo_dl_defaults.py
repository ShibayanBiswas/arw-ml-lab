"""Contabo CPU-only DL defaults — DEPLOY_CONTABO §12 (oneshot-c208)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.CONTABO.DL_DEFAULTS"
DEFAULT_MAX_ROWS = 2_000_000
DEFAULT_TORCH_THREADS = 2
DEFAULT_BATCH_CAP = 256


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_compose_torch_threads() -> dict[str, object]:
    text = (_repo_root() / "docker-compose.prod.yml").read_text(encoding="utf-8")
    for key in ("TORCH_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        if key not in text:
            raise AssertionError(f"compose missing {key}")
    if 'TORCH_NUM_THREADS: "2"' not in text and "TORCH_NUM_THREADS: '2'" not in text:
        if "TORCH_NUM_THREADS: 2" not in text and 'TORCH_NUM_THREADS: "2"' not in text:
            raise AssertionError("TORCH_NUM_THREADS must be 2 on Contabo train")
    return {"torch_threads": DEFAULT_TORCH_THREADS}


def assert_env_example_limits() -> dict[str, object]:
    text = (_repo_root() / ".env.example").read_text(encoding="utf-8")
    # LAB_MAX_ROWS may be documented; TABPFN must default false
    if "TABPFN_ENABLED" in text and "true" in text.lower().split("TABPFN_ENABLED", 1)[-1][:40]:
        # only fail if default is true
        line = [ln for ln in text.splitlines() if ln.strip().startswith("TABPFN_ENABLED")]
        if line and "=true" in line[0].lower():
            raise AssertionError("TABPFN_ENABLED must default false")
    return {"tabpfn_default": "false_or_unset", "max_rows_hint": DEFAULT_MAX_ROWS}


def assert_doc_dl_defaults() -> dict[str, object]:
    text = (_repo_root() / "docs" / "DEPLOY_CONTABO.md").read_text(encoding="utf-8")
    for needle in ("batch ≤ 256", "TORCH_NUM_THREADS=2", "LAB_MAX_ROWS=2000000", "TABPFN_ENABLED=false"):
        if needle not in text:
            raise AssertionError(f"DEPLOY_CONTABO §12 missing {needle}")
    return {"doc": "DEPLOY_CONTABO §12"}


def assert_deep_router_small_epochs() -> dict[str, object]:
    """Smoke API must keep max_epochs default 1 and cap ≤ 5 (Contabo CPU)."""
    text = (_repo_root() / "backend" / "app" / "routers" / "deep.py").read_text(encoding="utf-8")
    if "max_epochs: int = Field(default=1" not in text:
        raise AssertionError("deep sequential smoke must default max_epochs=1")
    if "le=5" not in text:
        raise AssertionError("deep sequential smoke must cap max_epochs at 5")
    return {"max_epochs_default": 1, "max_epochs_cap": 5}


def contabo_dl_manifest(*, seed: int = 42) -> dict[str, Any]:
    checks = [
        assert_compose_torch_threads(),
        assert_env_example_limits(),
        assert_doc_dl_defaults(),
        assert_deep_router_small_epochs(),
    ]
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "batch_cap": DEFAULT_BATCH_CAP,
        "max_rows": DEFAULT_MAX_ROWS,
        "checks": checks,
    }


def assert_contabo_dl_defaults_contract() -> dict[str, object]:
    return contabo_dl_manifest(seed=42)
