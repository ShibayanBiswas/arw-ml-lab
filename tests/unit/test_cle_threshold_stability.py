"""CLE.P.THRESHOLD_STABILITY."""

from __future__ import annotations

from labcore.eval.classification.plots import plot_threshold_stability


def test_threshold_stability():
    art = plot_threshold_stability([0.42, 0.45, 0.40, 0.48], method="youden")
    assert art["id"] == "CLE.P.THRESHOLD_STABILITY"
    assert 0.3 < art["numbers"]["mean"] < 0.6
    assert art["numbers"]["std"] >= 0
