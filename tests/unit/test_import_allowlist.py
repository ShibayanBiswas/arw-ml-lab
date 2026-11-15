"""CI guard (rule 70): every top-level import in labcore/backend is pinned in requirements."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "backend" / "requirements"
SCAN_DIRS = [ROOT / "labcore", ROOT / "backend"]

# Stdlib + first-party packages that are not PyPI deps
ALLOW_FIRST_PARTY = frozenset(
    {
        "labcore",
        "backend",
        "tests",
        "__future__",
    }
)

# Map import name -> requirements package name when they differ
IMPORT_TO_PACKAGE = {
    "jwt": "PyJWT",
    "PIL": "pillow",
    "yaml": "pyyaml",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "skimage": "scikit-image",
    "imblearn": "imbalanced-learn",
    "netcal": "netcal",
    "MLstatkit": "MLstatkit",
}


def _stdlib_names() -> set[str]:
    import sys

    names = set(sys.stdlib_module_names)  # type: ignore[attr-defined]
    names.update({"typing_extensions"})
    return names


def _pinned_packages() -> set[str]:
    pkgs: set[str] = set()
    for path in REQ_DIR.glob("*.txt"):
        if path.name.endswith(".lock.txt") or path.name == "README.md":
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r "):
                continue
            name = line.split("==")[0].split("[")[0].strip()
            if name:
                pkgs.add(name.lower().replace("_", "-"))
    return pkgs


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module.split(".")[0])
    return found


def test_imports_are_pinned() -> None:
    stdlib = _stdlib_names()
    pinned = _pinned_packages()
    assert pinned, "no requirements files found"
    offenders: list[str] = []
    for base in SCAN_DIRS:
        for py in base.rglob("*.py"):
            for name in _top_level_imports(py):
                if name in stdlib or name in ALLOW_FIRST_PARTY:
                    continue
                pkg = IMPORT_TO_PACKAGE.get(name, name)
                key = pkg.lower().replace("_", "-")
                if key not in pinned and name.lower().replace("_", "-") not in pinned:
                    offenders.append(f"{py.relative_to(ROOT)}: import {name} (pkg {pkg})")
    assert not offenders, "Unpinned imports:\n" + "\n".join(sorted(offenders))
