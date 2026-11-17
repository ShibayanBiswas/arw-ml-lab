"""SEC.ZAP.BASELINE — OWASP ZAP config contract (oneshot-c145)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SEC_DIR = ROOT / "tests" / "security"


def _load_yaml(name: str) -> dict:
    return yaml.safe_load((SEC_DIR / name).read_text(encoding="utf-8"))


def test_manifest_tags_sec_zap_baseline() -> None:
    manifest = json.loads((SEC_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["id"] == "SEC.ZAP.BASELINE"
    assert manifest["seed"] == 42
    names = {c["file"] for c in manifest["configs"]}
    assert "zap-baseline.yaml" in names
    assert "zap-baseline-lab-api.yaml" in names


def test_frontend_zap_baseline_excludes_lab_api_proxy() -> None:
    doc = _load_yaml("zap-baseline.yaml")
    ctx = doc["env"]["contexts"][0]
    assert ctx["name"] == "arw-ml-lab-public"
    joined = "\n".join(ctx["excludePaths"])
    assert "/api/" in joined
    rule_ids = {int(r["id"]) for r in doc["rules"]}
    assert 10015 in rule_ids


def test_lab_api_zap_baseline_covers_healthz_and_catalog() -> None:
    doc = _load_yaml("zap-baseline-lab-api.yaml")
    ctx = doc["env"]["contexts"][0]
    joined = "\n".join(ctx["includePaths"])
    assert "healthz" in joined
    assert "catalog" in joined
    excluded = "\n".join(ctx["excludePaths"])
    assert "openapi" in excluded