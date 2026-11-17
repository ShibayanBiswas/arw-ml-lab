"""AI.NVIDIA.TIMEOUT — oneshot-c237."""

from labcore.ai.nvidia_timeout_contract import assert_nvidia_client_timeout


def test_nvidia_httpx_timeout_under_10s() -> None:
    m = assert_nvidia_client_timeout()
    assert m["id"] == "AI.NVIDIA.TIMEOUT"
    assert m["timeout_s"] < 10.0
