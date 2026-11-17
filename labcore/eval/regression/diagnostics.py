"""REE.T.RESIDUALS / RESID_TESTS / INFLUENCE — statsmodels + scipy."""

from __future__ import annotations

from typing import Any

import numpy as np


def residual_table(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    resid = y_true - y_pred
    rows = [
        {
            "i": int(i),
            "y_true": float(y_true[i]),
            "y_pred": float(y_pred[i]),
            "residual": float(resid[i]),
        }
        for i in range(len(y_true))
    ]
    return {"id": "REE.T.RESIDUALS", "rows": rows, "prediction_source": "oof"}


def residual_tests(
    y_true: np.ndarray, y_pred: np.ndarray, X: np.ndarray | None = None
) -> dict[str, Any]:
    """Run diagnostic tests; each row: name, statistic, pvalue, verdict."""
    import statsmodels.api as sm
    from scipy import stats
    from statsmodels.stats.diagnostic import (
        acorr_ljungbox,
        het_breuschpagan,
        het_goldfeldquandt,
        het_white,
        linear_harvey_collier,
        linear_reset,
    )

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    resid = y_true - y_pred
    tests: list[dict[str, Any]] = []

    def add(name: str, stat: float, p: float, alpha: float = 0.05) -> None:
        tests.append(
            {
                "test": name,
                "statistic": float(stat) if stat is not None and not np.isnan(stat) else None,
                "pvalue": float(p) if p is not None and not np.isnan(p) else None,
                "verdict": (
                    "reject_H0"
                    if p is not None and not np.isnan(p) and p < alpha
                    else (
                        "fail_to_reject_H0" if p is not None and not np.isnan(p) else "not_computed"
                    )
                ),
            }
        )

    if len(resid) >= 8:
        w, p = stats.shapiro(resid[:5000])
        add("Shapiro-Wilk", w, p)
    jb = sm.stats.jarque_bera(resid)
    add("Jarque-Bera", float(jb[0]), float(jb[1]))
    try:
        ad = stats.anderson(resid, dist="norm")
        # use statistic only; p approx via significance levels
        add("Anderson-Darling", float(ad.statistic), float("nan"))
        tests[-1]["verdict"] = (
            "reject_H0" if ad.statistic > ad.critical_values[2] else "fail_to_reject_H0"
        )
    except Exception:
        add("Anderson-Darling", float("nan"), float("nan"))

    # Need design matrix for hetero / RESET — use constant + y_pred
    exog = sm.add_constant(y_pred)
    try:
        bp = het_breuschpagan(resid, exog)
        add("Breusch-Pagan", float(bp[0]), float(bp[1]))
    except Exception:
        add("Breusch-Pagan", float("nan"), float("nan"))
    try:
        wh = het_white(resid, exog)
        add("White", float(wh[0]), float(wh[1]))
    except Exception:
        add("White", float("nan"), float("nan"))
    try:
        gq = het_goldfeldquandt(y_true, exog)
        add("Goldfeld-Quandt", float(gq[0]), float(gq[1]))
    except Exception:
        add("Goldfeld-Quandt", float("nan"), float("nan"))

    dw = float(sm.stats.stattools.durbin_watson(resid))
    tests.append(
        {
            "test": "Durbin-Watson",
            "statistic": dw,
            "pvalue": None,
            "verdict": "near_2_ok" if 1.5 < dw < 2.5 else "autocorr_suspected",
        }
    )
    try:
        lb = acorr_ljungbox(resid, lags=[10], return_df=True)
        add("Ljung-Box", float(lb["lb_stat"].iloc[0]), float(lb["lb_pvalue"].iloc[0]))
    except Exception:
        add("Ljung-Box", float("nan"), float("nan"))

    try:
        model = sm.OLS(y_true, exog).fit()
        reset = linear_reset(model, power=2, use_f=True)
        add("RESET", float(reset.fvalue), float(reset.pvalue))
    except Exception:
        add("RESET", float("nan"), float("nan"))
    try:
        model = sm.OLS(y_true, exog).fit()
        hc = linear_harvey_collier(model)
        add("Harvey-Collier", float(hc.statistic), float(hc.pvalue))
    except Exception:
        add("Harvey-Collier", float("nan"), float("nan"))

    # Runs test on sign of residuals
    try:
        from statsmodels.sandbox.stats.runs import runstest_1samp

        z, p = runstest_1samp(resid > 0, correction=True)
        add("Runs", float(z), float(p))
    except Exception:
        add("Runs", float("nan"), float("nan"))

    return {"id": "REE.T.RESID_TESTS", "tests": tests, "prediction_source": "oof"}


def influence_table(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """Cook's D / studentised residuals via statsmodels OLSInfluence."""
    import statsmodels.api as sm

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    exog = sm.add_constant(y_pred)
    model = sm.OLS(y_true, exog).fit()
    infl = model.get_influence()
    cooks = np.asarray(infl.cooks_distance[0])
    student = np.asarray(infl.resid_studentized_internal)
    leverage = np.asarray(infl.hat_matrix_diag)
    n_params = int(exog.shape[1])
    rows = [
        {
            "i": int(i),
            "cooks_d": float(cooks[i]),
            "studentised_resid": float(student[i]),
            "leverage": float(leverage[i]),
        }
        for i in range(len(y_true))
    ]
    return {
        "id": "REE.T.INFLUENCE",
        "rows": rows,
        "cooks_d_max": float(np.nanmax(cooks)),
        "n_params": n_params,
        "prediction_source": "oof",
    }
