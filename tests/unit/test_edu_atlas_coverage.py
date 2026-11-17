"""EDU.ATLAS.COVERAGE — oneshot-c209."""

from labcore.education.atlas_coverage import assert_atlas_coverage, atlas_manifest


def test_atlas_coverage_floor() -> None:
    out = assert_atlas_coverage()
    assert out["n_entries"] >= 20
    assert out["id"] == "EDU.ATLAS.COVERAGE"


def test_atlas_manifest_seed() -> None:
    assert atlas_manifest(seed=42)["seed"] == 42
