"""Cooperative cancel flags for long predict jobs — ARCHITECTURE §45.8 / OPS-03.

Workers check a key each chunk. Routers set the flag when the user cancels.
Default store is in-process memory (tests + local); Redis when configured.
"""

from __future__ import annotations

import os
from typing import Protocol


class CancelFlagStore(Protocol):
    def set_cancelled(self, key: str) -> None: ...

    def is_cancelled(self, key: str) -> bool: ...

    def clear(self, key: str) -> None: ...


class MemoryCancelFlagStore:
    """Process-local cancel flags (unit tests + AUTH_BYPASS local API)."""

    def __init__(self) -> None:
        self._flags: set[str] = set()

    def set_cancelled(self, key: str) -> None:
        self._flags.add(key)

    def is_cancelled(self, key: str) -> bool:
        return key in self._flags

    def clear(self, key: str) -> None:
        self._flags.discard(key)


class RedisCancelFlagStore:
    """Redis GET/SET cancel flags. Values are the literal ``1`` with short TTL."""

    def __init__(self, url: str, *, ttl_seconds: int = 86_400) -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._ttl = int(ttl_seconds)

    def set_cancelled(self, key: str) -> None:
        self._client.set(key, "1", ex=self._ttl)

    def is_cancelled(self, key: str) -> bool:
        return self._client.get(key) == "1"

    def clear(self, key: str) -> None:
        self._client.delete(key)


_MEMORY = MemoryCancelFlagStore()
_OVERRIDE: CancelFlagStore | None = None


def set_cancel_store(store: CancelFlagStore | None) -> None:
    """Tests inject a store; ``None`` restores default resolution."""
    global _OVERRIDE
    _OVERRIDE = store


def default_cancel_store() -> CancelFlagStore:
    """Injected override → Redis when ``LAB_CANCEL_USE_REDIS`` → memory."""
    if _OVERRIDE is not None:
        return _OVERRIDE
    url = (os.environ.get("REDIS_URL") or "").strip()
    use_redis = os.environ.get("LAB_CANCEL_USE_REDIS", "").lower() in {"1", "true", "yes"}
    # Contabo compose sets LAB_CANCEL_USE_REDIS=true on workers (DEPLOY_CONTABO §7).
    if use_redis and url:
        try:
            return RedisCancelFlagStore(url)
        except Exception:  # noqa: BLE001 — never block predict on Redis outage
            return _MEMORY
    return _MEMORY


def cancel_flag_key_for_job(job_id: str) -> str:
    return f"lab:cancel:{job_id}"
