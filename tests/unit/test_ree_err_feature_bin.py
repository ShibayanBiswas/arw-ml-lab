"""REE.P.ERR_FEATURE_BIN — MAE by feature bin."""

from __future__ import annotations

import numpy as np
from fairlearn.metrics import MetricFrame
from sklearn.metrics import mean_absolute_error

from labcore.eval.regression.plots import plot_err_feature_bin


def test_err_feature_bin_matches_metricframe():
    rng = np.random.default_rng(42)
    n = 120
    y = rng.normal(0, 1, n)
    feat = rng.uniform(0, 10, n)
    pred = y + feat * 0.05 + rng.normal(0, 0.3, n)
    art = plot_err_feature_bin(y, pred, feat, feature_name="feat_x", n_bins=6)
    assert art["id"] == "REE.P.ERR_FEATURE_BIN"
    assert np.isfinite(art["numbers"]["overall_mae"])

    labels = np.digitize(
        feat,
        np.quantile(feat, np.linspace(0, 1, 7))[1:-1],
        right=True,
    )
    mf = MetricFrame(
        metrics=mean_absolute_error,
        y_true=y,
        y_pred=pred,
        sensitive_features=labels,
    )
    for k, v in art["numbers"]["by_group"].items():
        assert abs(v - float(mf.by_group[int(k)])) < 1e-9