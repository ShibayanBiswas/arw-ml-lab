"""Zip reproduction bundle — REP.T.BUNDLE / ST-UX-02 (ARCHITECTURE §46.4)."""

from __future__ import annotations

import base64
import hashlib
import json
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

from labcore.reports.notebook import build_reproduction_notebook, notebook_to_json

ARTEFACT_ID = "REP.T.BUNDLE"
STRESS_ID = "ST-UX-02"
LAB_DEFAULT_SEED = 42
LAB_TIMEZONE = "Asia/Kolkata"

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LOCK_PATH = _REPO_ROOT / "backend" / "requirements" / "worker-light.lock.txt"
_CORE_PREFIXES = ("numpy==", "pandas==", "scipy==", "scikit-learn==")

_REQUIRED_ZIP_ENTRIES = (
    "manifest.json",
    "config/run.json",
    "data/sha256.txt",
    "code/reproduce.py",
    "notebook/reproduction.ipynb",
    "environment/core-pins.txt",
)


def _core_pins_from_lock() -> str:
    if not _LOCK_PATH.is_file():
        return "# worker-light.lock.txt not found in repo\n"
    lines: list[str] = [
        "# Core ML pins from backend/requirements/worker-light.lock.txt (§46.4)\n",
        f"# source: {_LOCK_PATH.as_posix()}\n",
    ]
    for raw in _LOCK_PATH.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if any(stripped.startswith(p) for p in _CORE_PREFIXES):
            lines.append(stripped + "\n")
    if len(lines) == 2:
        lines.append("# lock unreadable — install from backend/requirements/worker-light.txt\n")
    return "".join(lines)


def _reproduce_py_stub(*, dataset_id: str, algorithm_key: str, seed: int) -> str:
    return (
        "#!/usr/bin/env python3\n"
        '"""Re-run hook — load dataset + contract from the lab store (do not refit on test)."""\n\n'
        f"SEED = {seed}\n"
        f'DATASET_ID = "{dataset_id}"\n'
        f'ALGORITHM_KEY = "{algorithm_key}"\n\n'
        "def main() -> None:\n"
        "    print('REP.T.BUNDLE stub', DATASET_ID, ALGORITHM_KEY, SEED)\n"
        "    print('Install environment/core-pins.txt then run the notebook.')\n\n"
        'if __name__ == "__main__":\n'
        "    main()\n"
    )


def _config_payload(
    *,
    dataset_id: str,
    algorithm_key: str,
    seed: int,
    facts: dict[str, Any] | None,
    data_hash: str | None,
) -> dict[str, Any]:
    facts = facts or {}
    payload: dict[str, Any] = {
        "dataset_id": dataset_id,
        "algorithm_key": algorithm_key,
        "seed": seed,
        "timezone": LAB_TIMEZONE,
        "facts": facts,
    }
    if data_hash:
        payload["data_sha256"] = data_hash
    return payload


def _data_hash(config: dict[str, Any]) -> str:
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_reproduction_bundle_zip(
    *,
    title: str,
    dataset_id: str,
    algorithm_key: str,
    seed: int = LAB_DEFAULT_SEED,
    facts: dict[str, Any] | None = None,
    pip_pins: list[str] | None = None,
    data_hash: str | None = None,
) -> bytes:
    """Return a zip byte stream (not uploaded)."""
    config = _config_payload(
        dataset_id=dataset_id,
        algorithm_key=algorithm_key,
        seed=seed,
        facts=facts,
        data_hash=data_hash,
    )
    digest = data_hash or _data_hash(config)
    config["data_sha256"] = digest

    nb = build_reproduction_notebook(
        title=title,
        dataset_id=dataset_id,
        algorithm_key=algorithm_key,
        seed=seed,
        facts=facts,
        pip_pins=pip_pins,
    )
    notebook_text = notebook_to_json(nb)

    manifest = {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "timezone": LAB_TIMEZONE,
        "dataset_id": dataset_id,
        "algorithm_key": algorithm_key,
        "data_sha256": digest,
        "files": list(_REQUIRED_ZIP_ENTRIES),
    }

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        zf.writestr("config/run.json", json.dumps(config, indent=2, sort_keys=True) + "\n")
        zf.writestr("data/sha256.txt", digest + "\n")
        zf.writestr("code/reproduce.py", _reproduce_py_stub(dataset_id=dataset_id, algorithm_key=algorithm_key, seed=seed))
        zf.writestr("notebook/reproduction.ipynb", notebook_text)
        zf.writestr("environment/core-pins.txt", _core_pins_from_lock())
    return buf.getvalue()


def bundle_to_base64(data: bytes) -> str:
    return base64.standard_b64encode(data).decode("ascii")


def assert_rep_bundle_zip_contract(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    blob = build_reproduction_bundle_zip(
        title="DS1 bundle",
        dataset_id="DS1",
        algorithm_key="lightgbm",
        seed=seed,
        facts={"seed": seed, "split": "oof"},
    )
    if not blob.startswith(b"PK"):
        raise ValueError("REP.T.BUNDLE: zip must start with PK header")
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        names = set(zf.namelist())
        missing = [p for p in _REQUIRED_ZIP_ENTRIES if p not in names]
        if missing:
            raise ValueError(f"REP.T.BUNDLE: zip missing entries {missing}")
        manifest = json.loads(zf.read("manifest.json"))
        if manifest.get("timezone") != LAB_TIMEZONE:
            raise ValueError("REP.T.BUNDLE: manifest must use Asia/Kolkata")
        if manifest.get("id") != ARTEFACT_ID:
            raise ValueError("REP.T.BUNDLE: manifest id mismatch")
        config = json.loads(zf.read("config/run.json"))
        if config.get("timezone") != LAB_TIMEZONE:
            raise ValueError("REP.T.BUNDLE: config must record Asia/Kolkata")
        sha_file = zf.read("data/sha256.txt").decode("utf-8").strip()
        if sha_file != config.get("data_sha256"):
            raise ValueError("REP.T.BUNDLE: data/sha256.txt must match config")
        pins = zf.read("environment/core-pins.txt").decode("utf-8")
        if "scikit-learn==" not in pins and _LOCK_PATH.is_file():
            raise ValueError("REP.T.BUNDLE: core-pins must list scikit-learn when lock exists")
        nb_text = zf.read("notebook/reproduction.ipynb").decode("utf-8")
        if "DS1" not in nb_text or "lightgbm" not in nb_text:
            raise ValueError("REP.T.BUNDLE: notebook must embed dataset + algorithm")
    return {"format": "zip", "byte_len": len(blob), "seed": seed, "n_files": len(_REQUIRED_ZIP_ENTRIES)}


def build_reproduction_bundle_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    check = assert_rep_bundle_zip_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "timezone": LAB_TIMEZONE,
        "checks": [check],
    }