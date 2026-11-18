"""Contabo DL presets — oneshot-c271."""

from labcore.deep.contabo_presets import assert_contabo_presets_cpu_only, contabo_dl_preset


def test_contabo_presets_cpu_only() -> None:
    m = assert_contabo_presets_cpu_only(seed=42)
    assert m["quick"]["max_epochs"] == 5
    assert m["balanced"]["batch_size"] <= 256
    assert contabo_dl_preset("quick")["accelerator"] == "cpu"
