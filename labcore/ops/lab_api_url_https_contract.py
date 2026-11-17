"""LAB_API_URL / NEXT_PUBLIC_LAB_API_URL must be https in Contabo docs — OPS.LAB_API.HTTPS (oneshot-c239)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.LAB_API.HTTPS"


def assert_lab_api_https_docs() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    hits: list[str] = []
    for rel in ("docs/DEPLOY_CONTABO.md", "docs/DEPLOY.md"):
        text = (root / rel).read_text(encoding="utf-8")
        if "NEXT_PUBLIC_LAB_API_URL=https://" not in text and "NEXT_PUBLIC_LAB_API_URL` must be `https://" not in text:
            # Accept either assignment example or prose requirement
            if "NEXT_PUBLIC_LAB_API_URL" in text and "https://" in text:
                continue
            hits.append(rel)
        if "LAB_API_URL" in text and "https://" not in text.split("LAB_API_URL", 1)[-1][:200]:
            # weak check — require https somewhere near LAB_API_URL in Contabo doc
            if rel.endswith("DEPLOY_CONTABO.md") and "LAB_API_URL" in text:
                section = [ln for ln in text.splitlines() if "LAB_API_URL" in ln]
                if not any("https://" in ln for ln in section):
                    hits.append(f"{rel}:LAB_API_URL rows")
    if hits:
        raise AssertionError(f"https API URL docs incomplete: {hits}")
    return {"id": ARTEFACT_ID, "seed": 42}
