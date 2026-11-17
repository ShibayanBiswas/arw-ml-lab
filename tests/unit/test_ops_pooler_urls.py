"""OPS.POOLER.URLS — oneshot-c202."""

from backend.app.settings import Settings
from labcore.ops.pooler_urls import assert_pooler_contract


def test_pooler_contract() -> None:
    m = assert_pooler_contract()
    assert m["id"] == "OPS.POOLER.URLS"
    assert "transaction" in m["api"]


def test_resolved_optuna_uses_session_on_worker() -> None:
    s = Settings(
        SERVICE_ROLE="worker-train",
        DATABASE_URL="postgresql://tx/db",
        DATABASE_URL_SESSION="postgresql://session/db",
        OPTUNA_STORAGE_URL="",
    )
    assert s.resolved_optuna_storage_url() == "postgresql://session/db"


def test_explicit_optuna_wins() -> None:
    s = Settings(
        SERVICE_ROLE="worker-train",
        DATABASE_URL_SESSION="postgresql://session/db",
        OPTUNA_STORAGE_URL="postgresql://optuna/db",
    )
    assert s.resolved_optuna_storage_url() == "postgresql://optuna/db"
