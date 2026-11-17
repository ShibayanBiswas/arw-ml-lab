"""Model load hardening — SEC-06 / §45.8, rule 60 (no user pickles)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Literal

from labcore.export.skops_store import load_skops

ARTEFACT_ID = "SEC.MODEL.LOAD"
POLICY_SEED = 42

SKLEARN_FORMAT = "skops"
TORCH_FORMAT = "torch_checkpoint"

FORBIDDEN_USER_SUFFIXES = frozenset({".pkl", ".pickle", ".joblib", ".dill", ".dat"})
LAB_STORE_ENTITIES = frozenset({"models", "artefacts"})

_STORAGE_KEY = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}/"
    r"(models|artefacts)/[0-9a-f-]{36}/[^/]+$",
    re.IGNORECASE,
)


class ModelLoadRejected(Exception):
    """Raised when a model artefact fails SEC-06 guards."""

    def __init__(self, message: str, *, code: str = "SEC-06") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


def sha256_file(path: str | Path) -> str:
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sha256(path: str | Path, expected_sha256: str) -> None:
    digest = sha256_file(path)
    if digest != expected_sha256.lower():
        raise ModelLoadRejected("artefact sha256 mismatch", code="SEC-06-SHA256")


def reject_user_model_upload(
    *,
    source: Literal["lab_store", "user_upload"] | None = None,
    path: str | Path | None = None,
) -> None:
    """v1 never deserialises user-uploaded model binaries."""
    if source == "user_upload":
        raise ModelLoadRejected("user-uploaded models are not accepted in v1", code="SEC-06-USER")
    if path is not None:
        suffix = Path(path).suffix.lower()
        if suffix in FORBIDDEN_USER_SUFFIXES:
            raise ModelLoadRejected(
                f"forbidden deserialization suffix {suffix!r}; use skops or signed checkpoints",
                code="SEC-06-FMT",
            )


def assert_lab_store_object_key(object_key: str) -> None:
    """Require Supabase Storage object paths `{workspace}/{entity}/{id}/{file}`."""
    key = object_key.strip().lstrip("/")
    if not _STORAGE_KEY.match(key):
        raise ModelLoadRejected(
            "model must be loaded from the lab artefact store path only",
            code="SEC-06-PATH",
        )


def assert_lab_store_path(path: str | Path) -> None:
    """Offline guard: path must include a lab store entity segment (`models/` or `artefacts/`)."""
    p = Path(path)
    parts = {part.lower() for part in p.parts}
    if not parts.intersection(LAB_STORE_ENTITIES):
        raise ModelLoadRejected(
            "local model path must live under models/ or artefacts/",
            code="SEC-06-PATH",
        )


def load_sklearn_lab(
    path: str | Path,
    *,
    expected_sha256: str,
    object_key: str | None = None,
    source: Literal["lab_store", "user_upload"] = "lab_store",
) -> Any:
    """Load a sklearn pipeline from the lab store via skops + sha256 (SEC-06)."""
    reject_user_model_upload(source=source, path=path)
    p = Path(path)
    if p.suffix.lower() != ".skops":
        raise ModelLoadRejected(
            f"sklearn models must use {SKLEARN_FORMAT!r} in v1",
            code="SEC-06-FMT",
        )
    if object_key is not None:
        assert_lab_store_object_key(object_key)
    else:
        assert_lab_store_path(p)
    verify_sha256(p, expected_sha256)
    return load_skops(p, expected_sha256=expected_sha256)


def load_torch_checkpoint(
    path: str | Path,
    *,
    expected_sha256: str,
    object_key: str | None = None,
    source: Literal["lab_store", "user_upload"] = "lab_store",
    map_location: str | None = "cpu",
) -> Any:
    """Load a DL checkpoint with `torch.load(..., weights_only=True)` after sha256 check."""
    import torch

    reject_user_model_upload(source=source, path=path)
    p = Path(path)
    if object_key is not None:
        assert_lab_store_object_key(object_key)
    else:
        assert_lab_store_path(p)
    verify_sha256(p, expected_sha256)
    return torch.load(p, map_location=map_location, weights_only=True)


def policy_manifest() -> dict[str, Any]:
    return {
        "artefact_id": ARTEFACT_ID,
        "seed": POLICY_SEED,
        "sklearn_format": SKLEARN_FORMAT,
        "torch_format": TORCH_FORMAT,
        "forbidden_user_suffixes": sorted(FORBIDDEN_USER_SUFFIXES),
        "torch_weights_only": True,
        "user_uploaded_models_v1": False,
    }