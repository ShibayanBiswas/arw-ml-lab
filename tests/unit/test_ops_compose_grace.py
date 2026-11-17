"""OPS.COMPOSE.GRACE — oneshot-c232."""

from labcore.ops.compose_grace_contract import assert_compose_stop_grace


def test_compose_workers_have_300s_stop_grace() -> None:
    m = assert_compose_stop_grace()
    assert m["id"] == "OPS.COMPOSE.GRACE"
