"""FE.NAV.COVERAGE — oneshot-c219."""

from labcore.ux.nav_coverage import assert_nav_coverage


def test_every_modules_nav_leaf_is_routed() -> None:
    m = assert_nav_coverage()
    assert m["id"] == "FE.NAV.COVERAGE"
    assert m["leaves"] > 50
    assert m["missing"] == []
