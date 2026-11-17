"""Worker egress allow-list (ARCHITECTURE OPS-14 / ST-OPS-08).

Dataset download hosts are derived from ``data/samples/urls.txt``. Platform hosts
(NVIDIA API catalog, Supabase project endpoints) are matched by suffix rules so
workers can reach storage/DB/VLM without opening generic internet egress.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

DATASET_URLS_REL = "data/samples/urls.txt"
ARTEFACT_ID = "OPS.EGRESS.ALLOWLIST"

# OPS-14 static platform hosts (build-time PyPI is out of scope for runtime checks)
STATIC_HOSTS = frozenset(
    {
        "integrate.api.nvidia.com",
    }
)

# Hostname suffixes allowed for Supabase API, Auth, Storage, pooler
SUPABASE_HOST_SUFFIXES = (
    ".supabase.co",
    ".storage.supabase.co",
)


class EgressDeniedError(PermissionError):
    """Raised when a worker URL is outside the OPS-14 allow-list."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def host_from_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.hostname:
        msg = f"invalid url: {url!r}"
        raise ValueError(msg)
    return parsed.hostname.lower()


def parse_urls_txt(text: str) -> frozenset[str]:
    hosts: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        hosts.add(host_from_url(parts[1]))
    return frozenset(hosts)


def load_dataset_hosts(
    urls_path: Path | None = None,
    *,
    root: Path | None = None,
) -> frozenset[str]:
    root = root or _repo_root()
    path = urls_path or (root / DATASET_URLS_REL)
    return parse_urls_txt(path.read_text(encoding="utf-8"))


def _host_allowed(host: str, dataset_hosts: frozenset[str]) -> bool:
    h = host.lower()
    if h in STATIC_HOSTS or h in dataset_hosts:
        return True
    return any(h.endswith(sfx) for sfx in SUPABASE_HOST_SUFFIXES)


def build_egress_allowlist(
    *,
    root: Path | None = None,
    extra_hosts: frozenset[str] | None = None,
) -> frozenset[str]:
    """Union of static platform hosts and every host in ``urls.txt``."""
    hosts = set(STATIC_HOSTS)
    hosts.update(load_dataset_hosts(root=root))
    if extra_hosts:
        hosts.update(h.lower() for h in extra_hosts)
    return frozenset(hosts)


def check_egress_url(
    url: str,
    allowlist: frozenset[str] | None = None,
    *,
    root: Path | None = None,
) -> str:
    """Return the hostname when the URL is permitted; raise ``EgressDeniedError`` otherwise."""
    host = host_from_url(url)
    dataset_hosts = allowlist or load_dataset_hosts(root=root)
    if _host_allowed(host, dataset_hosts):
        return host
    raise EgressDeniedError(f"egress blocked for host {host!r} (OPS-14)")


def egress_policy_manifest(*, seed: int = 42, root: Path | None = None) -> dict[str, object]:
    dataset_hosts = load_dataset_hosts(root=root)
    allowlist = sorted(build_egress_allowlist(root=root))
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "dataset_hosts_n": len(dataset_hosts),
        "allowlist_n": len(allowlist),
        "static_hosts": sorted(STATIC_HOSTS),
        "supabase_suffixes": list(SUPABASE_HOST_SUFFIXES),
    }