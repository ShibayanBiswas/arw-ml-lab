"""OPS.UPTIME.EXTERNAL — oneshot-c199."""

from labcore.ops.uptime_monitor import assert_uptime_contract, uptime_manifest


def test_uptime_contract_offline() -> None:
    m = assert_uptime_contract()
    assert m["id"] == "OPS.UPTIME.EXTERNAL"
    assert m["health_path"] == "/healthz"
    assert m["hosted_configured"] is False


def test_uptime_manifest_seed() -> None:
    assert uptime_manifest(seed=42)["seed"] == 42
