"""Contabo CPU-safe DL presets — DEPLOY_CONTABO §12 (oneshot-c271)."""

from __future__ import annotations

from typing import Any, Literal

PresetName = Literal["quick", "balanced"]

# Hard caps for the 8 GB VPS (CPU only).
CONTABO_BATCH_CAP = 256
CONTABO_TORCH_THREADS = 2
CONTABO_MAX_EPOCHS_QUICK = 5
CONTABO_MAX_EPOCHS_BALANCED = 20


def contabo_dl_preset(name: PresetName = "quick") -> dict[str, Any]:
    """Return preset hyperparameters; never enables GPU."""
    if name == "balanced":
        return {
            "name": "balanced",
            "max_epochs": CONTABO_MAX_EPOCHS_BALANCED,
            "batch_size": min(128, CONTABO_BATCH_CAP),
            "accelerator": "cpu",
            "torch_num_threads": CONTABO_TORCH_THREADS,
            "lab_gpu_worker": False,
        }
    return {
        "name": "quick",
        "max_epochs": CONTABO_MAX_EPOCHS_QUICK,
        "batch_size": min(64, CONTABO_BATCH_CAP),
        "accelerator": "cpu",
        "torch_num_threads": CONTABO_TORCH_THREADS,
        "lab_gpu_worker": False,
    }


def assert_contabo_presets_cpu_only(*, seed: int = 42) -> dict[str, object]:
    q = contabo_dl_preset("quick")
    b = contabo_dl_preset("balanced")
    for p in (q, b):
        if p["accelerator"] != "cpu":
            raise AssertionError("Contabo presets must be CPU-only")
        if p["lab_gpu_worker"]:
            raise AssertionError("Contabo presets must keep LAB_GPU_WORKER false")
        if int(p["batch_size"]) > CONTABO_BATCH_CAP:
            raise AssertionError("batch_size exceeds Contabo cap")
    return {"id": "OPS.CONTABO.DL_PRESETS", "seed": seed, "quick": q, "balanced": b}
