"""NVIDIA client HTTP timeout must stay under 10s — AI.NVIDIA.TIMEOUT (oneshot-c237)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ARTEFACT_ID = "AI.NVIDIA.TIMEOUT"


def assert_nvidia_client_timeout() -> dict[str, Any]:
    text = (Path(__file__).resolve().parents[2] / "labcore" / "ai" / "client.py").read_text(
        encoding="utf-8"
    )
    m = re.search(r"httpx\.Client\(timeout=([0-9.]+)\)", text)
    if not m:
        raise AssertionError("NvidiaAIClient must set httpx Client timeout")
    timeout = float(m.group(1))
    if timeout >= 10.0:
        raise AssertionError(f"NVIDIA chat timeout {timeout}s must be < 10 for numbers-only AC")
    return {"id": ARTEFACT_ID, "seed": 42, "timeout_s": timeout}
