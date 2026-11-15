"""GET /api/v1/catalog/* — registry-driven catalogue (Phase 0: empty typed lists)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from labcore.registry import get_catalog

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])

_SECTIONS = (
    "algorithms",
    "encoders",
    "imputers",
    "scalers",
    "transforms",
    "cv",
    "metrics",
    "plots",
    "tests",
    "explainers",
    "datasets",
)


@router.get("")
def catalog_root() -> dict[str, Any]:
    cat = get_catalog()
    return cat.model_dump()


@router.get("/{section}")
def catalog_section(section: str) -> list[Any] | dict[str, Any]:
    if section not in _SECTIONS:
        raise HTTPException(status_code=404, detail=f"Unknown catalogue section: {section}")
    data = get_catalog().model_dump()
    return data[section]


@router.get("/algorithms/{key}")
def catalog_algorithm(key: str) -> dict[str, Any]:
    for algo in get_catalog().algorithms:
        if algo.key == key or algo.id == key:
            return algo.model_dump()
    raise HTTPException(status_code=404, detail=f"Algorithm not registered: {key}")
