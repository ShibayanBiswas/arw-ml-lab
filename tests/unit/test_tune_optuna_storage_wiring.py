"""Tune worker passes OPTUNA_STORAGE_URL into run_optuna_tune (oneshot-c191)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TUNE = ROOT / "backend" / "worker" / "tasks" / "tune.py"
SETTINGS = ROOT / "backend" / "app" / "settings.py"
ENV_EXAMPLE = ROOT / ".env.example"


def test_tune_task_reads_optuna_storage() -> None:
    src = TUNE.read_text(encoding="utf-8")
    assert "optuna_storage_url" in src
    assert "storage=storage" in src
    assert "study_name" in src


def test_settings_and_env_example_document_optuna() -> None:
    assert "OPTUNA_STORAGE_URL" in SETTINGS.read_text(encoding="utf-8")
    assert "OPTUNA_STORAGE_URL" in ENV_EXAMPLE.read_text(encoding="utf-8")
