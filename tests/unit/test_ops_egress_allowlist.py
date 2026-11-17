"""OPS.EGRESS.ALLOWLIST — worker egress from urls.txt (ST-OPS-08 / oneshot-c149)."""

from __future__ import annotations

from pathlib import Path

import pytest

from labcore.ops.egress_allowlist import (
    ARTEFACT_ID,
    EgressDeniedError,
    build_egress_allowlist,
    check_egress_url,
    egress_policy_manifest,
    load_dataset_hosts,
    parse_urls_txt,
)

ROOT = Path(__file__).resolve().parents[2]
URLS = ROOT / "data" / "samples" / "urls.txt"


def test_urls_txt_parses_nonempty_host_set() -> None:
    hosts = load_dataset_hosts()
    assert len(hosts) >= 6
    assert "archive.ics.uci.edu" in hosts
    assert "raw.githubusercontent.com" in hosts


def test_check_allows_sample_url_and_nvidia() -> None:
    check_egress_url("https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data")
    check_egress_url("https://integrate.api.nvidia.com/v1/chat/completions")


def test_check_allows_supabase_suffix() -> None:
    check_egress_url("https://abcdefgh.supabase.co/rest/v1/runs")
    check_egress_url("https://project.storage.supabase.co/object/public/datasets/x.csv")


def test_check_blocks_unknown_host() -> None:
    with pytest.raises(EgressDeniedError, match="evil.example"):
        check_egress_url("https://evil.example.com/data.csv")


def test_build_allowlist_includes_static_and_dataset() -> None:
    combined = build_egress_allowlist()
    assert "integrate.api.nvidia.com" in combined
    assert "archive.ics.uci.edu" in combined


def test_manifest_contract_seed_42() -> None:
    manifest = egress_policy_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["dataset_hosts_n"] == len(load_dataset_hosts())
    assert manifest["allowlist_n"] == len(build_egress_allowlist())


def test_parse_urls_txt_minimal() -> None:
    text = "foo https://example.org/a.csv\n# comment\nbar https://x.y/z"
    hosts = parse_urls_txt(text)
    assert hosts == frozenset({"example.org", "x.y"})