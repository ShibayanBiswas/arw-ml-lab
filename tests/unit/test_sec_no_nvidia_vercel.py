"""SEC.NO.NVIDIA.VERCEL — oneshot-c203."""

from labcore.security.vercel_secret_guard import assert_no_nvidia_in_frontend, vercel_secret_manifest


def test_no_nvidia_in_frontend() -> None:
    out = assert_no_nvidia_in_frontend()
    assert out["hits"] == 0
    assert out["id"] == "SEC.NO.NVIDIA.VERCEL"


def test_manifest_seed() -> None:
    assert vercel_secret_manifest(seed=42)["seed"] == 42
