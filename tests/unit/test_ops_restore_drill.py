"""OPS.RESTORE.DRILL — oneshot-c198."""

from labcore.ops.restore_drill import assert_restore_drill_ready, restore_drill_manifest


def test_restore_drill_ready_offline() -> None:
    m = assert_restore_drill_ready()
    assert m["id"] == "OPS.RESTORE.DRILL"
    assert m["hosted_executed"] is False
    assert len(m["steps"]) >= 5
    assert "models" in m["buckets"]


def test_manifest_seed_42() -> None:
    m = restore_drill_manifest(seed=42)
    assert m["seed"] == 42
