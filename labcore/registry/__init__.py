"""Registry: AlgorithmSpec / ParamSpec and catalogue builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from labcore.registry.spec import AlgorithmSpec, ParamSpec

__all__ = ["AlgorithmSpec", "ParamSpec", "Catalog", "get_catalog"]

if TYPE_CHECKING:
    from labcore.registry.catalog import Catalog


def __getattr__(name: str) -> object:
    if name == "Catalog":
        from labcore.registry.catalog import Catalog as _Catalog

        return _Catalog
    if name == "get_catalog":
        from labcore.registry.catalog import get_catalog as _get_catalog

        return _get_catalog
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)