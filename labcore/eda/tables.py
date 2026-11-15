"""EDA.T.* table builders — ARCHITECTURE §10.1 (library-backed)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from sklearn.neighbors import LocalOutlierFactor
from statsmodels.stats.outliers_influence import variance_inflation_factor

from labcore.eda.context import EDAContext
from labcore.plots.artefact import Artefact, make_table_artefact

NOT_COMPUTED_TL = {"status": "not_computed", "reason": "tradinglab_phase_5"}

# Always-emitted base tables; target/sequential tables gated in build_all_tables
TABLE_IDS = (
    "EDA.T.OVERVIEW",
    "EDA.T.SCHEMA",
    "EDA.T.NUMSUMMARY",
    "EDA.T.CATSUMMARY",
    "EDA.T.NORMALITY",
    "EDA.T.DISTFIT",
    "EDA.T.MISSING",
    "EDA.T.OUTLIERS",
    "EDA.T.CORR",
    "EDA.T.MI",
    "EDA.T.VIF",
    "EDA.T.DUPES",
)
TARGET_TABLE_IDS = ("EDA.T.TARGET", "EDA.T.FEAT_TARGET", "EDA.T.WOE_IV")
SEQUENTIAL_TABLE_IDS = (
    "EDA.T.STATIONARITY",
    "EDA.T.AUTOCORR",
    "EDA.T.BREAKS",
    "EDA.T.FINSTATS",
)


def build_all_tables(ctx: EDAContext) -> list[Artefact]:
    """Always emit all 19 EDA.T.* ids; gated sections return not_applicable rows."""
    arts: list[Artefact] = [
        table_overview(ctx),
        table_schema(ctx),
        table_numsummary(ctx),
        table_catsummary(ctx),
        table_normality(ctx),
        table_distfit(ctx),
        table_missing(ctx),
        table_outliers(ctx),
        table_corr(ctx),
        table_mi(ctx),
        table_vif(ctx),
        table_dupes(ctx),
    ]
    if ctx.task.target:
        arts.extend([table_target(ctx), table_feat_target(ctx), table_woe_iv(ctx)])
    else:
        arts.extend(
            [
                _na_table("EDA.T.TARGET", "Target summary", "no_target"),
                _na_table("EDA.T.FEAT_TARGET", "Feature–target association", "no_target"),
                _na_table("EDA.T.WOE_IV", "WoE / IV", "no_target"),
            ]
        )
    if ctx.task.sequential:
        arts.extend(
            [
                table_stationarity(ctx),
                table_autocorr(ctx),
                table_breaks(ctx),
                table_finstats(ctx),
            ]
        )
    else:
        arts.extend(
            [
                _na_table("EDA.T.STATIONARITY", "Stationarity", "not_sequential"),
                _na_table("EDA.T.AUTOCORR", "Autocorrelation", "not_sequential"),
                _na_table("EDA.T.BREAKS", "Structural breaks", "not_sequential"),
                _na_table("EDA.T.FINSTATS", "Financial return stats", "not_sequential"),
            ]
        )
    return arts


def _na_table(artefact_id: str, title: str, reason: str) -> Artefact:
    return make_table_artefact(
        artefact_id,
        title,
        columns=["status", "reason"],
        rows=[{"status": "not_applicable", "reason": reason}],
        numbers={"status": "not_applicable", "reason": reason},
        edu_key=f"table.{artefact_id.lower()}",
    )


def table_overview(ctx: EDAContext) -> Artefact:
    df = ctx.df
    dup = int(df.duplicated().sum())
    const = sum(1 for c in ctx.schema if c.semantic_type == "constant")
    miss = float(df.isna().mean().mean())
    score = max(0.0, 100.0 - miss * 100 - min(dup / max(len(df), 1) * 50, 20) - const * 2)
    row = {
        "n_rows": len(df),
        "n_cols": df.shape[1],
        "memory_bytes": int(df.memory_usage(deep=True).sum()),
        "duplicate_rows": dup,
        "constant_cols": const,
        "missing_pct_mean": round(miss * 100, 4),
        "data_quality_score": round(score, 2),
        "sampled": ctx.sampled,
    }
    return make_table_artefact(
        "EDA.T.OVERVIEW",
        "Dataset overview",
        columns=list(row.keys()),
        rows=[row],
        numbers=row,
        edu_key="table.eda.overview",
    )


def table_schema(ctx: EDAContext) -> Artefact:
    rows = [c.model_dump() for c in ctx.schema]
    cols = list(rows[0].keys()) if rows else ["name"]
    return make_table_artefact(
        "EDA.T.SCHEMA",
        "Column dictionary",
        columns=cols,
        rows=rows,
        numbers={"n_cols": len(rows)},
        edu_key="table.eda.schema",
    )


def table_numsummary(ctx: EDAContext) -> Artefact:
    rows: list[dict[str, Any]] = []
    for col in ctx.numeric_cols:
        s = pd.to_numeric(ctx.df[col], errors="coerce")
        desc = s.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
        rows.append(
            {
                "column": col,
                "count": int(s.notna().sum()),
                "mean": _f(desc.get("mean")),
                "std": _f(desc.get("std")),
                "min": _f(desc.get("min")),
                "p1": _f(desc.get("1%")),
                "p5": _f(desc.get("5%")),
                "q1": _f(desc.get("25%")),
                "median": _f(desc.get("50%")),
                "q3": _f(desc.get("75%")),
                "p95": _f(desc.get("95%")),
                "p99": _f(desc.get("99%")),
                "max": _f(desc.get("max")),
                "iqr": _f(desc.get("75%") - desc.get("25%") if "75%" in desc else None),
                "skew": _f(float(s.skew())) if s.notna().sum() > 2 else None,
                "kurtosis_excess": _f(float(s.kurtosis())) if s.notna().sum() > 3 else None,
                "zeros_pct": _f(float((s == 0).mean() * 100)),
                "negatives_pct": _f(float((s < 0).mean() * 100)),
            }
        )
    cols = list(rows[0].keys()) if rows else ["column"]
    return make_table_artefact(
        "EDA.T.NUMSUMMARY",
        "Numeric summary",
        columns=cols,
        rows=rows,
        numbers={"n_numeric": len(rows)},
        edu_key="table.eda.numsummary",
    )


def table_catsummary(ctx: EDAContext) -> Artefact:
    rows: list[dict[str, Any]] = []
    for col in ctx.cat_cols:
        s = ctx.df[col].astype("object")
        vc = s.value_counts(dropna=True)
        probs = (vc / vc.sum()).values if len(vc) else np.array([])
        ent = float(stats.entropy(probs)) if len(probs) else 0.0
        max_ent = float(np.log(len(probs))) if len(probs) > 1 else 1.0
        rows.append(
            {
                "column": col,
                "n_unique": int(s.nunique(dropna=True)),
                "mode": str(vc.index[0]) if len(vc) else None,
                "mode_freq_pct": _f(float(vc.iloc[0] / max(len(s), 1) * 100)) if len(vc) else None,
                "entropy": _f(ent),
                "entropy_norm": _f(ent / max_ent) if max_ent else None,
                "rare_levels": int((vc / vc.sum() < 0.01).sum()) if len(vc) else 0,
            }
        )
    cols = list(rows[0].keys()) if rows else ["column"]
    return make_table_artefact(
        "EDA.T.CATSUMMARY",
        "Categorical summary",
        columns=cols,
        rows=rows,
        numbers={"n_categorical": len(rows)},
        edu_key="table.eda.catsummary",
    )


def table_normality(ctx: EDAContext) -> Artefact:
    rows: list[dict[str, Any]] = []
    for col in ctx.numeric_cols[:30]:
        s = pd.to_numeric(ctx.df[col], errors="coerce").dropna()
        if len(s) < 8:
            continue
        sample = s.sample(n=min(len(s), 5000), random_state=ctx.seed)
        tests: dict[str, Any] = {"column": col}
        for name, fn in [
            ("shapiro", lambda x: stats.shapiro(x) if len(x) <= 5000 else (np.nan, np.nan)),
            ("dagostino", lambda x: stats.normaltest(x)),
            ("jarque_bera", lambda x: stats.jarque_bera(x)),
        ]:
            try:
                stat, p = fn(sample)
                tests[f"{name}_stat"] = _f(float(stat))
                tests[f"{name}_p"] = _f(float(p))
                tests[f"{name}_verdict"] = "normal" if p > 0.05 else "non_normal"
            except Exception:
                tests[f"{name}_stat"] = None
                tests[f"{name}_p"] = None
                tests[f"{name}_verdict"] = "not_computed"
        rows.append(tests)
    cols = list(rows[0].keys()) if rows else ["column"]
    return make_table_artefact(
        "EDA.T.NORMALITY",
        "Normality tests",
        columns=cols,
        rows=rows,
        numbers={"n_tested": len(rows)},
        edu_key="table.eda.normality",
    )


def table_distfit(ctx: EDAContext) -> Artefact:
    dists = {
        "norm": stats.norm,
        "lognorm": stats.lognorm,
        "gamma": stats.gamma,
        "expon": stats.expon,
        "laplace": stats.laplace,
        "t": stats.t,
    }
    rows: list[dict[str, Any]] = []
    for col in ctx.numeric_cols[:15]:
        s = pd.to_numeric(ctx.df[col], errors="coerce").dropna()
        if len(s) < 20:
            continue
        sample = s.sample(n=min(len(s), 2000), random_state=ctx.seed).astype(float)
        best = None
        for dname, dist in dists.items():
            try:
                params = dist.fit(sample)
                loglik = float(np.sum(dist.logpdf(sample, *params)))
                k = len(params)
                aic = 2 * k - 2 * loglik
                if best is None or aic < best["aic"]:
                    best = {"column": col, "distribution": dname, "aic": _f(aic), "k": k}
            except Exception:
                continue
        if best:
            rows.append(best)
    cols = list(rows[0].keys()) if rows else ["column"]
    return make_table_artefact(
        "EDA.T.DISTFIT",
        "Best-fit distribution",
        columns=cols,
        rows=rows,
        numbers={"n_fit": len(rows)},
        edu_key="table.eda.distfit",
    )


def table_missing(ctx: EDAContext) -> Artefact:
    rows = []
    for c in ctx.schema:
        rows.append(
            {
                "column": c.name,
                "missing_count": int(ctx.df[c.name].isna().sum()),
                "missing_pct": round(c.pct_missing * 100, 4),
            }
        )
    return make_table_artefact(
        "EDA.T.MISSING",
        "Missingness",
        columns=["column", "missing_count", "missing_pct"],
        rows=rows,
        numbers={
            "by_column": {r["column"]: r["missing_pct"] for r in rows},
            "mean_missing_pct": _f(float(np.mean([r["missing_pct"] for r in rows])) if rows else 0),
        },
        edu_key="table.eda.missing",
    )


def table_outliers(ctx: EDAContext) -> Artefact:
    rows: list[dict[str, Any]] = []
    X_num = ctx.df[ctx.numeric_cols].apply(pd.to_numeric, errors="coerce")
    for col in ctx.numeric_cols:
        s = X_num[col].dropna()
        if len(s) < 10:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        iqr_share = float(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).mean())
        z = np.abs(stats.zscore(s, nan_policy="omit"))
        z_share = float((z > 3).mean()) if len(z) else 0.0
        med = float(s.median())
        mad = float(np.median(np.abs(s - med))) or 1e-9
        mz = 0.6745 * (s - med) / mad
        mz_share = float((np.abs(mz) > 3.5).mean())
        rows.append(
            {
                "column": col,
                "iqr_1_5_share": _f(iqr_share),
                "zscore_share": _f(z_share),
                "modified_z_share": _f(mz_share),
            }
        )
    # Multivariate IF / LOF on numeric matrix
    if_share = lof_share = None
    clean = X_num.dropna()
    if clean.shape[0] >= 30 and clean.shape[1] >= 2:
        if_model = IsolationForest(random_state=ctx.seed, contamination="auto")
        pred = if_model.fit_predict(clean)
        if_share = float((pred == -1).mean())
        lof = LocalOutlierFactor(n_neighbors=min(20, len(clean) - 1))
        lof_pred = lof.fit_predict(clean)
        lof_share = float((lof_pred == -1).mean())
    return make_table_artefact(
        "EDA.T.OUTLIERS",
        "Outliers",
        columns=list(rows[0].keys()) if rows else ["column"],
        rows=rows,
        numbers={
            "isolation_forest_share": if_share,
            "lof_share": lof_share,
            "n_cols": len(rows),
        },
        edu_key="table.eda.outliers",
    )


def table_corr(ctx: EDAContext) -> Artefact:
    cols = ctx.numeric_cols[:40]
    if len(cols) < 2:
        return make_table_artefact(
            "EDA.T.CORR",
            "Correlation matrices",
            columns=["note"],
            rows=[{"note": "insufficient_numeric_columns"}],
            numbers={},
            edu_key="table.eda.corr",
        )
    X = ctx.df[cols].apply(pd.to_numeric, errors="coerce")
    pearson = X.corr(method="pearson")
    spearman = X.corr(method="spearman")
    # distance correlation on a small subset
    dcor_mat = None
    try:
        import dcor

        sub = cols[:8]
        M = np.zeros((len(sub), len(sub)))
        for i, a in enumerate(sub):
            for j, b in enumerate(sub):
                xa = X[a].dropna()
                xb = X[b].dropna()
                idx = xa.index.intersection(xb.index)
                if len(idx) < 10:
                    M[i, j] = np.nan
                else:
                    M[i, j] = float(
                        dcor.distance_correlation(xa.loc[idx].values, xb.loc[idx].values)
                    )
        dcor_mat = {"columns": sub, "matrix": M.tolist()}
    except Exception:
        dcor_mat = None
    phik_mat = None
    try:
        ph = ctx.df[cols[:12]].phik_matrix(interval_cols=cols[:12])
        phik_mat = {"columns": list(ph.columns), "matrix": ph.values.tolist()}
    except Exception:
        phik_mat = None
    return make_table_artefact(
        "EDA.T.CORR",
        "Correlation matrices",
        columns=["method", "n_cols"],
        rows=[
            {"method": "pearson", "n_cols": len(cols)},
            {"method": "spearman", "n_cols": len(cols)},
            {"method": "dcor", "n_cols": len(dcor_mat["columns"]) if dcor_mat else 0},
            {"method": "phik", "n_cols": len(phik_mat["columns"]) if phik_mat else 0},
        ],
        numbers={
            "pearson": pearson.values.tolist(),
            "spearman": spearman.values.tolist(),
            "columns": cols,
            "dcor": dcor_mat,
            "phik": phik_mat,
            "tradinglab_codependence": NOT_COMPUTED_TL,
        },
        edu_key="table.eda.corr",
    )


def table_mi(ctx: EDAContext) -> Artefact:
    tgt = ctx.task.target
    if not tgt or tgt not in ctx.df.columns:
        return make_table_artefact(
            "EDA.T.MI",
            "Mutual information with target",
            columns=["note"],
            rows=[{"note": "no_target"}],
            numbers={"tradinglab_mi": NOT_COMPUTED_TL},
            edu_key="table.eda.mi",
        )
    feats = [c for c in ctx.numeric_cols if c != tgt][:40]
    rows: list[dict[str, Any]] = []
    if not feats:
        return make_table_artefact(
            "EDA.T.MI",
            "Mutual information with target",
            columns=["note"],
            rows=[{"note": "no_numeric_features"}],
            numbers={"tradinglab_mi": NOT_COMPUTED_TL},
            edu_key="table.eda.mi",
        )
    X = ctx.df[feats].apply(pd.to_numeric, errors="coerce").fillna(0)
    y = ctx.df[tgt]
    if ctx.task.task in {"binary", "multiclass"}:
        y_enc = pd.Categorical(y).codes
        mi = mutual_info_classif(X, y_enc, random_state=ctx.seed)
    else:
        y_num = pd.to_numeric(y, errors="coerce").fillna(0)
        mi = mutual_info_regression(X, y_num, random_state=ctx.seed)
    for f, v in zip(feats, mi, strict=True):
        rows.append({"feature": f, "mi": _f(float(v))})
    rows.sort(key=lambda r: r["mi"] or 0, reverse=True)
    return make_table_artefact(
        "EDA.T.MI",
        "Mutual information with target",
        columns=["feature", "mi"],
        rows=rows,
        numbers={"mi": {r["feature"]: r["mi"] for r in rows}, "tradinglab_mi": NOT_COMPUTED_TL},
        edu_key="table.eda.mi",
    )


def table_vif(ctx: EDAContext) -> Artefact:
    cols = [c for c in ctx.numeric_cols if c != ctx.task.target][:25]
    X = ctx.df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    rows = []
    if X.shape[1] >= 2 and len(X) >= 10:
        Xn = (X - X.mean()) / (X.std(ddof=0).replace(0, 1))
        arr = Xn.values
        for i, col in enumerate(cols):
            try:
                v = float(variance_inflation_factor(arr, i))
            except Exception:
                v = float("nan")
            rows.append(
                {
                    "feature": col,
                    "vif": _f(v),
                    "flag": "high" if v and v > 10 else ("warn" if v and v > 5 else "ok"),
                }
            )
    return make_table_artefact(
        "EDA.T.VIF",
        "Multicollinearity (VIF)",
        columns=["feature", "vif", "flag"] if rows else ["note"],
        rows=rows or [{"note": "insufficient_data"}],
        numbers={"vif": {r.get("feature"): r.get("vif") for r in rows if "feature" in r}},
        edu_key="table.eda.vif",
    )


def table_target(ctx: EDAContext) -> Artefact:
    tgt = ctx.task.target
    assert tgt
    y = ctx.df[tgt]
    if ctx.task.task in {"binary", "multiclass"}:
        vc = y.value_counts(dropna=False)
        rows = [
            {"class": str(i), "count": int(c), "pct": _f(float(c / len(y) * 100))}
            for i, c in vc.items()
        ]
        return make_table_artefact(
            "EDA.T.TARGET",
            "Target summary",
            columns=["class", "count", "pct"],
            rows=rows,
            numbers={
                "n_classes": int(y.nunique(dropna=True)),
                "minority_share": ctx.task.minority_share,
                "imbalance_ratio": ctx.task.imbalance_ratio,
                "majority_baseline": _f(float(vc.max() / len(y))),
            },
            edu_key="table.eda.target",
        )
    s = pd.to_numeric(y, errors="coerce")
    row = {
        "count": int(s.notna().sum()),
        "mean": _f(float(s.mean())),
        "std": _f(float(s.std())),
        "skew": _f(float(s.skew())),
        "min": _f(float(s.min())),
        "max": _f(float(s.max())),
    }
    return make_table_artefact(
        "EDA.T.TARGET",
        "Target summary",
        columns=list(row.keys()),
        rows=[row],
        numbers=row,
        edu_key="table.eda.target",
    )


def table_feat_target(ctx: EDAContext) -> Artefact:
    tgt = ctx.task.target
    assert tgt
    rows = []
    y = ctx.df[tgt]
    for col in ctx.numeric_cols:
        if col == tgt:
            continue
        x = pd.to_numeric(ctx.df[col], errors="coerce")
        if ctx.task.task in {"binary", "multiclass"}:
            # point-biserial / ANOVA-ish: use correlation of codes
            y_codes = pd.Categorical(y).codes.astype(float)
            mask = x.notna() & np.isfinite(y_codes)
            if mask.sum() < 10:
                continue
            r, p = stats.pearsonr(x[mask], y_codes[mask])
            rows.append(
                {
                    "feature": col,
                    "stat": "point_biserial_approx",
                    "value": _f(float(r)),
                    "p": _f(float(p)),
                }
            )
        else:
            y_num = pd.to_numeric(y, errors="coerce")
            mask = x.notna() & y_num.notna()
            if mask.sum() < 10:
                continue
            r, p = stats.pearsonr(x[mask], y_num[mask])
            rows.append(
                {"feature": col, "stat": "pearson", "value": _f(float(r)), "p": _f(float(p))}
            )
    return make_table_artefact(
        "EDA.T.FEAT_TARGET",
        "Feature–target association",
        columns=["feature", "stat", "value", "p"] if rows else ["note"],
        rows=rows or [{"note": "insufficient"}],
        numbers={"n": len(rows)},
        edu_key="table.eda.feat_target",
    )


def table_woe_iv(ctx: EDAContext) -> Artefact:
    if ctx.task.task != "binary" or not ctx.task.target:
        return make_table_artefact(
            "EDA.T.WOE_IV",
            "WoE / IV",
            columns=["note"],
            rows=[{"note": "binary_target_required"}],
            numbers={},
            edu_key="table.eda.woe_iv",
        )
    try:
        from optbinning import OptimalBinning

        rows = []
        y = pd.Categorical(ctx.df[ctx.task.target]).codes
        for col in ctx.numeric_cols[:20]:
            if col == ctx.task.target:
                continue
            x = pd.to_numeric(ctx.df[col], errors="coerce")
            mask = x.notna() & (y >= 0)
            if mask.sum() < 30:
                continue
            ob = OptimalBinning(name=col, dtype="numerical", solver="cp")
            ob.fit(x[mask].values, y[mask])
            iv = float(ob.iv) if ob.iv is not None else None
            rows.append({"feature": col, "iv": _f(iv), "band": _iv_band(iv)})
        return make_table_artefact(
            "EDA.T.WOE_IV",
            "WoE / IV",
            columns=["feature", "iv", "band"] if rows else ["note"],
            rows=rows or [{"note": "no_features_fit"}],
            numbers={"iv": {r["feature"]: r["iv"] for r in rows if "feature" in r}},
            edu_key="table.eda.woe_iv",
        )
    except Exception as exc:
        return make_table_artefact(
            "EDA.T.WOE_IV",
            "WoE / IV",
            columns=["error"],
            rows=[{"error": str(exc)}],
            numbers={},
            edu_key="table.eda.woe_iv",
        )


def table_stationarity(ctx: EDAContext) -> Artefact:
    from statsmodels.tsa.stattools import adfuller, kpss

    series_col = ctx.task.target or (ctx.numeric_cols[0] if ctx.numeric_cols else None)
    if not series_col:
        return make_table_artefact(
            "EDA.T.STATIONARITY",
            "Stationarity",
            columns=["note"],
            rows=[{"note": "no_series"}],
            numbers={},
            edu_key="table.eda.stationarity",
        )
    s = pd.to_numeric(ctx.df[series_col], errors="coerce").dropna()
    rows = []
    try:
        adf_stat, adf_p, *_ = adfuller(s, autolag="AIC")
        rows.append(
            {
                "test": "ADF",
                "stat": _f(float(adf_stat)),
                "p": _f(float(adf_p)),
                "verdict": "stationary" if adf_p < 0.05 else "non_stationary",
            }
        )
    except Exception as exc:
        rows.append({"test": "ADF", "stat": None, "p": None, "verdict": f"error:{exc}"})
    try:
        kpss_stat, kpss_p, *_ = kpss(s, regression="c", nlags="auto")
        rows.append(
            {
                "test": "KPSS",
                "stat": _f(float(kpss_stat)),
                "p": _f(float(kpss_p)),
                "verdict": "non_stationary" if kpss_p < 0.05 else "stationary",
            }
        )
    except Exception as exc:
        rows.append({"test": "KPSS", "stat": None, "p": None, "verdict": f"error:{exc}"})
    # Phillips-Perron via arch if available
    try:
        from arch.unitroot import PhillipsPerron

        pp = PhillipsPerron(s)
        rows.append(
            {
                "test": "PP",
                "stat": _f(float(pp.stat)),
                "p": _f(float(pp.pvalue)),
                "verdict": "stationary" if pp.pvalue < 0.05 else "non_stationary",
            }
        )
    except Exception:
        rows.append({"test": "PP", "stat": None, "p": None, "verdict": "not_computed"})
    return make_table_artefact(
        "EDA.T.STATIONARITY",
        "Stationarity",
        columns=["test", "stat", "p", "verdict"],
        rows=rows,
        numbers={"series": series_col, "tests": rows},
        edu_key="table.eda.stationarity",
    )


def table_autocorr(ctx: EDAContext) -> Artefact:
    from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
    from statsmodels.stats.stattools import durbin_watson

    series_col = ctx.task.target or (ctx.numeric_cols[0] if ctx.numeric_cols else None)
    if not series_col:
        return make_table_artefact(
            "EDA.T.AUTOCORR",
            "Autocorrelation",
            columns=["note"],
            rows=[{"note": "no_series"}],
            numbers={},
            edu_key="table.eda.autocorr",
        )
    s = pd.to_numeric(ctx.df[series_col], errors="coerce").dropna()
    rows = []
    try:
        lb = acorr_ljungbox(s, lags=[5, 10, 20], return_df=True)
        for lag, row in lb.iterrows():
            rows.append(
                {
                    "test": "ljung_box",
                    "lag": int(lag),
                    "stat": _f(float(row["lb_stat"])),
                    "p": _f(float(row["lb_pvalue"])),
                }
            )
    except Exception as exc:
        rows.append({"test": "ljung_box", "lag": None, "stat": None, "p": None, "error": str(exc)})
    try:
        dw = float(durbin_watson(s - s.mean()))
        rows.append({"test": "durbin_watson", "lag": None, "stat": _f(dw), "p": None})
    except Exception:
        pass
    try:
        import nolds

        h = float(nolds.hurst_rs(s.values))
        rows.append({"test": "hurst", "lag": None, "stat": _f(h), "p": None})
    except Exception:
        rows.append({"test": "hurst", "lag": None, "stat": None, "p": None})
    try:
        arch_lm = het_arch(s, nlags=5)
        rows.append(
            {"test": "arch_lm", "lag": 5, "stat": _f(float(arch_lm[0])), "p": _f(float(arch_lm[1]))}
        )
    except Exception:
        pass
    return make_table_artefact(
        "EDA.T.AUTOCORR",
        "Autocorrelation",
        columns=["test", "lag", "stat", "p"],
        rows=[{k: r.get(k) for k in ["test", "lag", "stat", "p"]} for r in rows],
        numbers={"rows": rows},
        edu_key="table.eda.autocorr",
    )


def table_breaks(ctx: EDAContext) -> Artefact:
    series_col = ctx.task.target or (ctx.numeric_cols[0] if ctx.numeric_cols else None)
    rows: list[dict[str, Any]] = [
        {"method": "chow", **NOT_COMPUTED_TL},
        {"method": "cusum_csw", **NOT_COMPUTED_TL},
        {"method": "sadf", **NOT_COMPUTED_TL},
    ]
    if series_col:
        try:
            import ruptures as rpt

            s = pd.to_numeric(ctx.df[series_col], errors="coerce").dropna().values
            if len(s) >= 30:
                algo = rpt.Pelt(model="rbf").fit(s)
                bkps = algo.predict(pen=3)
                rows.append({"method": "ruptures_pelt", "breakpoints": bkps, "status": "ok"})
        except Exception as exc:
            rows.append({"method": "ruptures_pelt", "status": "error", "error": str(exc)})
    return make_table_artefact(
        "EDA.T.BREAKS",
        "Structural breaks",
        columns=["method", "status", "reason", "breakpoints"],
        rows=rows,
        numbers={"tradinglab": NOT_COMPUTED_TL, "rows": rows},
        edu_key="table.eda.breaks",
    )


def table_finstats(ctx: EDAContext) -> Artefact:
    close_col = None
    if ctx.task.ohlcv:
        close_col = ctx.task.ohlcv.get("close")
    if not close_col:
        for c in ctx.df.columns:
            if str(c).lower() in {"close", "adj close", "adj_close", "passengers"}:
                close_col = c
                break
    if not close_col:
        return make_table_artefact(
            "EDA.T.FINSTATS",
            "Financial return stats",
            columns=["note"],
            rows=[{"note": "no_price_column"}],
            numbers={"tradinglab_volatility": NOT_COMPUTED_TL},
            edu_key="table.eda.finstats",
        )
    px = pd.to_numeric(ctx.df[close_col], errors="coerce").dropna()
    rets = px.pct_change().dropna()
    if rets.empty:
        return make_table_artefact(
            "EDA.T.FINSTATS",
            "Financial return stats",
            columns=["note"],
            rows=[{"note": "empty_returns"}],
            numbers={"tradinglab_volatility": NOT_COMPUTED_TL},
            edu_key="table.eda.finstats",
        )
    ann = 252 if (ctx.task.frequency or "").startswith("daily") else 12
    mu = float(rets.mean() * ann)
    vol = float(rets.std(ddof=0) * np.sqrt(ann))
    sharpe = mu / vol if vol else None
    downside = rets[rets < 0]
    sortino = mu / (float(downside.std(ddof=0) * np.sqrt(ann)) or 1e-12)
    wealth = (1 + rets).cumprod()
    peak = wealth.cummax()
    dd = (wealth / peak - 1).min()
    var95 = float(np.quantile(rets, 0.05))
    cvar95 = float(rets[rets <= var95].mean()) if (rets <= var95).any() else None
    row = {
        "ann_return": _f(mu),
        "ann_vol": _f(vol),
        "sharpe": _f(sharpe),
        "sortino": _f(sortino),
        "max_drawdown": _f(float(dd)),
        "skew": _f(float(rets.skew())),
        "kurtosis": _f(float(rets.kurtosis())),
        "var_95_hist": _f(var95),
        "cvar_95_hist": _f(cvar95),
        "tradinglab_parkinson": NOT_COMPUTED_TL,
        "tradinglab_garman_klass": NOT_COMPUTED_TL,
        "tradinglab_yang_zhang": NOT_COMPUTED_TL,
    }
    return make_table_artefact(
        "EDA.T.FINSTATS",
        "Financial return stats",
        columns=list(row.keys()),
        rows=[{k: (v if not isinstance(v, dict) else v.get("status")) for k, v in row.items()}],
        numbers=row,
        edu_key="table.eda.finstats",
    )


def table_dupes(ctx: EDAContext) -> Artefact:
    df = ctx.df
    dup_rows = int(df.duplicated().sum())
    leak_feats = []
    tgt = ctx.task.target
    if tgt and tgt in df.columns and pd.api.types.is_numeric_dtype(df[tgt]):
        y = pd.to_numeric(df[tgt], errors="coerce")
        for col in ctx.numeric_cols:
            if col == tgt:
                continue
            x = pd.to_numeric(df[col], errors="coerce")
            mask = x.notna() & y.notna()
            if mask.sum() < 10:
                continue
            r = abs(float(x[mask].corr(y[mask])))
            if r > 0.98:
                leak_feats.append({"feature": col, "abs_corr": _f(r)})
    row = {
        "duplicate_rows": dup_rows,
        "leakage_suspects": leak_feats,
        "n_leakage_suspects": len(leak_feats),
    }
    return make_table_artefact(
        "EDA.T.DUPES",
        "Duplicates / leakage hints",
        columns=["duplicate_rows", "n_leakage_suspects"],
        rows=[{"duplicate_rows": dup_rows, "n_leakage_suspects": len(leak_feats)}],
        numbers=row,
        edu_key="table.eda.dupes",
    )


def _iv_band(iv: float | None) -> str:
    if iv is None:
        return "unknown"
    if iv < 0.02:
        return "useless"
    if iv < 0.1:
        return "weak"
    if iv < 0.3:
        return "medium"
    if iv < 0.5:
        return "strong"
    return "suspicious"


def _f(v: Any) -> float | None:
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
        return float(v)
    except Exception:
        return None
