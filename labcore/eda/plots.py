"""EDA.P.* Plotly builders — ARCHITECTURE §10.2 (one+ artefact per plot group)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from labcore.eda.context import EDAContext
from labcore.plots.artefact import Artefact, empty_figure, make_plot_artefact

# §10.2 groups — every group must produce ≥1 artefact when data allows
PLOT_GROUP_IDS = (
    "univariate_numeric",
    "univariate_categorical",
    "missingness",
    "outliers",
    "bivariate",
    "multivariate",
    "target",
    "sequential",
    "quality",
)


def build_all_plots(ctx: EDAContext) -> list[Artefact]:
    arts: list[Artefact] = []
    arts.extend(_univariate_numeric(ctx))
    arts.extend(_univariate_categorical(ctx))
    arts.extend(_missingness(ctx))
    arts.extend(_outliers(ctx))
    arts.extend(_bivariate(ctx))
    arts.extend(_multivariate(ctx))
    arts.append(_quality_gauge(ctx))
    if ctx.task.target:
        arts.extend(_target_plots(ctx))
    if ctx.task.sequential:
        arts.extend(_sequential_plots(ctx))
    return arts


def _fig(
    ctx: EDAContext,
    artefact_id: str,
    title: str,
    fig: Any,
    numbers: dict[str, Any],
    *,
    group: str,
) -> Artefact:
    nums = {**numbers, "plot_group": group}
    return make_plot_artefact(
        artefact_id,
        title,
        fig,
        numbers=nums,
        edu_key=f"plot.{artefact_id.lower()}",
        sampled=ctx.sampled,
        render_png_flag=ctx.render_png,
    )


def _univariate_numeric(ctx: EDAContext) -> list[Artefact]:
    arts: list[Artefact] = []
    g = "univariate_numeric"
    for col in ctx.numeric_cols[:6]:
        s = pd.to_numeric(ctx.df[col], errors="coerce").dropna()
        if s.empty:
            continue
        hist = px.histogram(s, nbins=30, title=f"Histogram — {col}")
        arts.append(
            _fig(
                ctx,
                f"EDA.P.HIST.{col}",
                f"Histogram — {col}",
                hist,
                {"n": int(len(s)), "mean": float(s.mean())},
                group=g,
            )
        )
        # KDE overlay
        try:
            kde = stats.gaussian_kde(s.sample(n=min(len(s), 5000), random_state=ctx.seed))
            xs = np.linspace(float(s.min()), float(s.max()), 200)
            fig_kde = go.Figure()
            fig_kde.add_histogram(x=s, histnorm="probability density", name="hist", opacity=0.5)
            fig_kde.add_scatter(x=xs, y=kde(xs), mode="lines", name="kde")
            fig_kde.update_layout(title=f"Histogram+KDE — {col}")
            arts.append(
                _fig(
                    ctx,
                    f"EDA.P.HIST_KDE.{col}",
                    f"Histogram+KDE — {col}",
                    fig_kde,
                    {"n": int(len(s))},
                    group=g,
                )
            )
        except Exception:
            pass
        box = px.box(s, title=f"Box — {col}")
        arts.append(
            _fig(
                ctx, f"EDA.P.BOX.{col}", f"Box — {col}", box, {"median": float(s.median())}, group=g
            )
        )
        vio = px.violin(s, box=True, title=f"Violin — {col}")
        arts.append(
            _fig(ctx, f"EDA.P.VIOLIN.{col}", f"Violin — {col}", vio, {"n": int(len(s))}, group=g)
        )
        qq = stats.probplot(s.sample(n=min(len(s), 2000), random_state=ctx.seed), dist="norm")
        fig = go.Figure()
        fig.add_scatter(x=qq[0][0], y=qq[0][1], mode="markers", name="sample")
        fig.add_scatter(x=qq[0][0], y=qq[1][1] + qq[1][0] * qq[0][0], mode="lines", name="fit")
        fig.update_layout(title=f"Q-Q — {col}")
        arts.append(
            _fig(ctx, f"EDA.P.QQ.{col}", f"Q-Q — {col}", fig, {"slope": float(qq[1][0])}, group=g)
        )
        xs = np.sort(s.values)
        ys = np.arange(1, len(xs) + 1) / len(xs)
        ecdf = go.Figure(go.Scatter(x=xs, y=ys, mode="lines"))
        ecdf.update_layout(title=f"ECDF — {col}")
        arts.append(
            _fig(ctx, f"EDA.P.ECDF.{col}", f"ECDF — {col}", ecdf, {"n": int(len(xs))}, group=g)
        )
        # Boxen (letter-value)
        try:
            boxen = px.box(s, title=f"Boxen — {col}", points="outliers")
            arts.append(
                _fig(
                    ctx, f"EDA.P.BOXEN.{col}", f"Boxen — {col}", boxen, {"n": int(len(s))}, group=g
                )
            )
        except Exception:
            pass
    if ctx.numeric_cols:
        col = ctx.numeric_cols[0]
        s = pd.to_numeric(ctx.df[col], errors="coerce").dropna()
        from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

        frames = []
        for name, scaler in [
            ("raw", None),
            ("standard", StandardScaler()),
            ("minmax", MinMaxScaler()),
            ("robust", RobustScaler()),
        ]:
            v = s.values.reshape(-1, 1)
            out = v.ravel() if scaler is None else scaler.fit_transform(v).ravel()
            frames.append(pd.DataFrame({"value": out, "scaler": name}))
        cmp_df = pd.concat(frames, ignore_index=True)
        fig = px.violin(cmp_df, x="scaler", y="value", title=f"Scaler comparison — {col}")
        arts.append(
            _fig(
                ctx,
                f"EDA.P.SCALER_COMPARE.{col}",
                f"Scaler comparison — {col}",
                fig,
                {"column": col},
                group=g,
            )
        )
        # Transform preview
        tframes = []
        for name, series in [
            ("raw", s),
            ("log1p", np.log1p(s.clip(lower=0))),
            ("sqrt", np.sqrt(s.clip(lower=0))),
        ]:
            tframes.append(pd.DataFrame({"value": series.values, "transform": name}))
        tdf = pd.concat(tframes, ignore_index=True)
        tfig = px.histogram(
            tdf,
            x="value",
            color="transform",
            facet_col="transform",
            title=f"Transform preview — {col}",
        )
        arts.append(
            _fig(
                ctx,
                f"EDA.P.TRANSFORM.{col}",
                f"Transform preview — {col}",
                tfig,
                {"column": col},
                group=g,
            )
        )
    if not arts:
        arts.append(
            _fig(
                ctx,
                "EDA.P.UNIVARIATE_NUMERIC_EMPTY",
                "Univariate numeric",
                empty_figure("Univariate numeric", "No numeric columns"),
                {},
                group=g,
            )
        )
    return arts


def _univariate_categorical(ctx: EDAContext) -> list[Artefact]:
    arts: list[Artefact] = []
    g = "univariate_categorical"
    for col in ctx.cat_cols[:6]:
        vc = ctx.df[col].astype(str).value_counts().head(30)
        bar = px.bar(x=vc.index.astype(str), y=vc.values, title=f"Bar — {col}")
        arts.append(
            _fig(
                ctx,
                f"EDA.P.BAR.{col}",
                f"Bar — {col}",
                bar,
                {"levels": {str(k): int(v) for k, v in vc.items()}},
                group=g,
            )
        )
        cum = vc.cumsum() / vc.sum()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_bar(x=vc.index.astype(str), y=vc.values, name="count")
        fig.add_scatter(x=vc.index.astype(str), y=cum.values, name="cumulative", secondary_y=True)
        fig.update_layout(title=f"Pareto — {col}")
        arts.append(
            _fig(
                ctx,
                f"EDA.P.PARETO.{col}",
                f"Pareto — {col}",
                fig,
                {"n_levels": int(len(vc))},
                group=g,
            )
        )
        if len(vc) <= 8:
            donut = px.pie(
                names=vc.index.astype(str), values=vc.values, hole=0.45, title=f"Donut — {col}"
            )
            arts.append(
                _fig(
                    ctx,
                    f"EDA.P.DONUT.{col}",
                    f"Donut — {col}",
                    donut,
                    {"n_levels": int(len(vc))},
                    group=g,
                )
            )
        tree = px.treemap(
            names=vc.index.astype(str),
            parents=[""] * len(vc),
            values=vc.values,
            title=f"Treemap — {col}",
        )
        arts.append(
            _fig(
                ctx,
                f"EDA.P.TREEMAP.{col}",
                f"Treemap — {col}",
                tree,
                {"n_levels": int(len(vc))},
                group=g,
            )
        )
    if not arts:
        arts.append(
            _fig(
                ctx,
                "EDA.P.UNIVARIATE_CAT_EMPTY",
                "Univariate categorical",
                empty_figure("Univariate categorical", "No categorical columns"),
                {},
                group=g,
            )
        )
    return arts


def _missingness(ctx: EDAContext) -> list[Artefact]:
    g = "missingness"
    miss = ctx.df.isna().mean().sort_values(ascending=False)
    bar = px.bar(x=miss.index.astype(str), y=(miss.values * 100), title="Missingness % by column")
    heat = px.imshow(ctx.df.isna().astype(int).T, aspect="auto", title="Missingness matrix")
    # Nullity correlation
    null = ctx.df.isna().astype(int)
    ncorr = null.corr()
    nheat = px.imshow(ncorr, text_auto=".2f", title="Nullity correlation", aspect="auto")
    return [
        _fig(
            ctx, "EDA.P.MISS_BAR", "Missingness bar", bar, {"missing_pct": miss.to_dict()}, group=g
        ),
        _fig(
            ctx,
            "EDA.P.MISS_MATRIX",
            "Missingness matrix",
            heat,
            {"n_cols": int(ctx.df.shape[1])},
            group=g,
        ),
        _fig(
            ctx,
            "EDA.P.MISS_CORR",
            "Nullity correlation",
            nheat,
            {"n_cols": int(ncorr.shape[0])},
            group=g,
        ),
    ]


def _outliers(ctx: EDAContext) -> list[Artefact]:
    arts: list[Artefact] = []
    g = "outliers"
    for col in ctx.numeric_cols[:5]:
        s = pd.to_numeric(ctx.df[col], errors="coerce")
        fig = px.box(s, points="outliers", title=f"Outlier box — {col}")
        arts.append(
            _fig(
                ctx,
                f"EDA.P.OUTLIER_BOX.{col}",
                f"Outlier box — {col}",
                fig,
                {"n": int(s.notna().sum())},
                group=g,
            )
        )
        med = float(s.median())
        mad = float((s - med).abs().median()) or 1.0
        rz = 0.6745 * (s - med) / mad
        fig2 = px.scatter(x=s.index, y=rz, title=f"Robust z — {col}")
        arts.append(
            _fig(ctx, f"EDA.P.ROBUST_Z.{col}", f"Robust z — {col}", fig2, {"mad": mad}, group=g)
        )
    if len(ctx.numeric_cols) >= 2:
        from sklearn.ensemble import IsolationForest

        cols = ctx.numeric_cols[:8]
        X = ctx.df[cols].apply(pd.to_numeric, errors="coerce").dropna()
        if len(X) >= 30:
            iforest = IsolationForest(random_state=ctx.seed, contamination="auto")
            scores = -iforest.fit(X).score_samples(X)
            fig = px.histogram(scores, nbins=40, title="Isolation Forest scores")
            arts.append(
                _fig(
                    ctx,
                    "EDA.P.IF_SCORES",
                    "Isolation Forest scores",
                    fig,
                    {"n": int(len(scores))},
                    group=g,
                )
            )
    if not arts:
        arts.append(
            _fig(
                ctx,
                "EDA.P.OUTLIERS_EMPTY",
                "Outliers",
                empty_figure("Outliers", "No numeric columns"),
                {},
                group=g,
            )
        )
    return arts


def _bivariate(ctx: EDAContext) -> list[Artefact]:
    arts: list[Artefact] = []
    g = "bivariate"
    nums = ctx.numeric_cols
    if len(nums) >= 2:
        a, b = nums[0], nums[1]
        fig = px.scatter(ctx.df, x=a, y=b, trendline="ols", title=f"Scatter — {a} vs {b}")
        arts.append(
            _fig(
                ctx,
                f"EDA.P.SCATTER.{a}.{b}",
                f"Scatter — {a} vs {b}",
                fig,
                {"x": a, "y": b},
                group=g,
            )
        )
        fig2 = px.density_heatmap(ctx.df, x=a, y=b, title=f"Density — {a} vs {b}")
        arts.append(
            _fig(
                ctx,
                f"EDA.P.HEXBIN.{a}.{b}",
                f"Density — {a} vs {b}",
                fig2,
                {"x": a, "y": b},
                group=g,
            )
        )
    if ctx.cat_cols and nums:
        fig = px.box(
            ctx.df,
            x=ctx.cat_cols[0],
            y=nums[0],
            title=f"Grouped box — {nums[0]} by {ctx.cat_cols[0]}",
        )
        arts.append(
            _fig(ctx, f"EDA.P.GROUPED_BOX.{nums[0]}", str(fig.layout.title.text), fig, {}, group=g)
        )
        # Crosstab heatmap for two categoricals
        if len(ctx.cat_cols) >= 2:
            ct = pd.crosstab(
                ctx.df[ctx.cat_cols[0]].astype(str), ctx.df[ctx.cat_cols[1]].astype(str)
            )
            heat = px.imshow(
                ct, text_auto=True, title=f"Crosstab — {ctx.cat_cols[0]} × {ctx.cat_cols[1]}"
            )
            arts.append(
                _fig(
                    ctx,
                    f"EDA.P.CROSSTAB.{ctx.cat_cols[0]}.{ctx.cat_cols[1]}",
                    str(heat.layout.title.text),
                    heat,
                    {"shape": list(ct.shape)},
                    group=g,
                )
            )
    if not arts:
        arts.append(
            _fig(
                ctx,
                "EDA.P.BIVARIATE_EMPTY",
                "Bivariate",
                empty_figure("Bivariate", "Insufficient columns"),
                {},
                group=g,
            )
        )
    return arts


def _multivariate(ctx: EDAContext) -> list[Artefact]:
    arts: list[Artefact] = []
    g = "multivariate"
    nums = ctx.numeric_cols[:12]
    if len(nums) >= 2:
        corr = ctx.df[nums].apply(pd.to_numeric, errors="coerce").corr()
        heat = px.imshow(corr, text_auto=".2f", title="Pearson correlation heatmap", aspect="auto")
        arts.append(
            _fig(
                ctx,
                "EDA.P.CORR_HEATMAP",
                "Pearson correlation heatmap",
                heat,
                {"columns": nums, "matrix": corr.values.tolist()},
                group=g,
            )
        )
        # VIF bars
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor

            X = ctx.df[nums].apply(pd.to_numeric, errors="coerce").dropna()
            if len(X) >= 20 and X.shape[1] >= 2:
                Xn = (X - X.mean()) / (X.std(ddof=0).replace(0, 1))
                vifs = [float(variance_inflation_factor(Xn.values, i)) for i in range(Xn.shape[1])]
                fig = px.bar(x=nums, y=vifs, title="VIF bars")
                arts.append(
                    _fig(
                        ctx,
                        "EDA.P.VIF_BARS",
                        "VIF bars",
                        fig,
                        {"vif": dict(zip(nums, vifs, strict=True))},
                        group=g,
                    )
                )
        except Exception:
            pass
    if len(nums) >= 3:
        from sklearn.decomposition import PCA

        X = ctx.df[nums].apply(pd.to_numeric, errors="coerce").dropna()
        if len(X) >= 10:
            pca = PCA(n_components=min(3, X.shape[1]), random_state=ctx.seed)
            Z = pca.fit_transform(X)
            fig = px.scatter(x=Z[:, 0], y=Z[:, 1], title="PCA 2D projection")
            arts.append(
                _fig(
                    ctx,
                    "EDA.P.PCA_2D",
                    "PCA 2D projection",
                    fig,
                    {"explained_variance_ratio": pca.explained_variance_ratio_.tolist()},
                    group=g,
                )
            )
            scree = px.bar(
                x=list(range(1, len(pca.explained_variance_ratio_) + 1)),
                y=pca.explained_variance_ratio_,
                title="PCA scree",
            )
            arts.append(
                _fig(
                    ctx,
                    "EDA.P.PCA_SCREE",
                    "PCA scree",
                    scree,
                    {"explained_variance_ratio": pca.explained_variance_ratio_.tolist()},
                    group=g,
                )
            )
    fig = empty_figure("Feature clustering", "ONC / TradingLab clustering deferred to Phase 5")
    arts.append(
        _fig(
            ctx,
            "EDA.P.FEATURE_CLUSTER",
            "Feature clustering",
            fig,
            {"status": "not_computed", "reason": "tradinglab_phase_5"},
            group=g,
        )
    )
    return arts


def _target_plots(ctx: EDAContext) -> list[Artefact]:
    arts: list[Artefact] = []
    g = "target"
    tgt = ctx.task.target
    assert tgt
    if ctx.task.task in {"binary", "multiclass"}:
        vc = ctx.df[tgt].astype(str).value_counts()
        fig = px.bar(x=vc.index, y=vc.values, title=f"Class balance — {tgt}")
        arts.append(
            _fig(
                ctx,
                "EDA.P.CLASS_BALANCE",
                f"Class balance — {tgt}",
                fig,
                {"counts": vc.to_dict()},
                group=g,
            )
        )
    else:
        s = pd.to_numeric(ctx.df[tgt], errors="coerce")
        fig = px.histogram(s, nbins=40, title=f"Target distribution — {tgt}")
        arts.append(
            _fig(
                ctx,
                "EDA.P.TARGET_DIST",
                f"Target distribution — {tgt}",
                fig,
                {"mean": float(s.mean()), "std": float(s.std())},
                group=g,
            )
        )
    from sklearn.feature_selection import mutual_info_classif, mutual_info_regression

    feats = [c for c in ctx.numeric_cols if c != tgt][:15]
    if feats:
        X = ctx.df[feats].apply(pd.to_numeric, errors="coerce").fillna(0)
        if ctx.task.task in {"binary", "multiclass"}:
            mi = mutual_info_classif(X, pd.Categorical(ctx.df[tgt]).codes, random_state=ctx.seed)
        else:
            mi = mutual_info_regression(
                X, pd.to_numeric(ctx.df[tgt], errors="coerce").fillna(0), random_state=ctx.seed
            )
        fig = px.bar(x=feats, y=mi, title="Mutual information vs target")
        arts.append(
            _fig(
                ctx,
                "EDA.P.MI_BARS",
                "Mutual information vs target",
                fig,
                {"mi": dict(zip(feats, map(float, mi), strict=True))},
                group=g,
            )
        )
    return arts


def _sequential_plots(ctx: EDAContext) -> list[Artefact]:
    arts: list[Artefact] = []
    g = "sequential"
    tcol = ctx.task.time_column
    ycol = ctx.task.target
    if ctx.task.ohlcv:
        ycol = ctx.task.ohlcv.get("close", ycol)
    if not ycol or ycol not in ctx.df.columns:
        ycol = ctx.numeric_cols[0] if ctx.numeric_cols else None
    if not ycol:
        return [
            _fig(
                ctx,
                "EDA.P.SEQUENTIAL_EMPTY",
                "Sequential",
                empty_figure("Sequential", "No series column"),
                {},
                group=g,
            )
        ]
    df = ctx.df.copy()
    if tcol and tcol in df.columns:
        df[tcol] = pd.to_datetime(df[tcol], errors="coerce")
        df = df.sort_values(tcol)
        x = df[tcol]
    else:
        x = df.index
    y = pd.to_numeric(df[ycol], errors="coerce")
    line = go.Figure(go.Scatter(x=x, y=y, mode="lines", name=ycol))
    line.update_layout(title=f"Line — {ycol}")
    arts.append(
        _fig(ctx, "EDA.P.LINE", f"Line — {ycol}", line, {"n": int(y.notna().sum())}, group=g)
    )
    # Rolling mean/std
    roll = y.rolling(window=min(12, max(3, len(y) // 10)), min_periods=1)
    rfig = go.Figure()
    rfig.add_scatter(x=x, y=y, name="series", opacity=0.4)
    rfig.add_scatter(x=x, y=roll.mean(), name="roll_mean")
    rfig.add_scatter(x=x, y=roll.std(), name="roll_std")
    rfig.update_layout(title="Rolling mean/std")
    arts.append(_fig(ctx, "EDA.P.ROLLING", "Rolling mean/std", rfig, {}, group=g))
    from statsmodels.tsa.stattools import acf, pacf

    s = y.dropna()
    if len(s) >= 20:
        acf_v = acf(s, nlags=min(40, len(s) // 2), fft=True)
        pacf_v = pacf(s, nlags=min(40, len(s) // 2))
        fig_a = go.Figure(go.Bar(y=acf_v, name="ACF"))
        fig_a.update_layout(title="ACF")
        arts.append(_fig(ctx, "EDA.P.ACF", "ACF", fig_a, {"acf": acf_v.tolist()}, group=g))
        fig_p = go.Figure(go.Bar(y=pacf_v, name="PACF"))
        fig_p.update_layout(title="PACF")
        arts.append(_fig(ctx, "EDA.P.PACF", "PACF", fig_p, {"pacf": pacf_v.tolist()}, group=g))
        # Lag plot
        lag = pd.DataFrame({"y_t": s.values[1:], "y_t1": s.values[:-1]})
        lfig = px.scatter(lag, x="y_t1", y="y_t", title="Lag-1 plot")
        arts.append(_fig(ctx, "EDA.P.LAG", "Lag-1 plot", lfig, {"lag": 1}, group=g))
        try:
            from statsmodels.tsa.seasonal import STL

            stl = STL(s, period=12 if len(s) >= 24 else max(2, len(s) // 8)).fit()
            fig = make_subplots(rows=4, cols=1, shared_xaxes=True)
            fig.add_scatter(y=stl.observed, row=1, col=1, name="obs")
            fig.add_scatter(y=stl.trend, row=2, col=1, name="trend")
            fig.add_scatter(y=stl.seasonal, row=3, col=1, name="seasonal")
            fig.add_scatter(y=stl.resid, row=4, col=1, name="resid")
            fig.update_layout(title="STL decomposition", height=800)
            arts.append(_fig(ctx, "EDA.P.STL", "STL decomposition", fig, {"period": 12}, group=g))
        except Exception:
            pass
        # Periodogram
        try:
            from scipy.signal import periodogram

            freqs, power = periodogram(s.values)
            pfig = go.Figure(go.Scatter(x=freqs, y=power, mode="lines"))
            pfig.update_layout(title="Periodogram")
            arts.append(
                _fig(
                    ctx,
                    "EDA.P.PERIODOGRAM",
                    "Periodogram",
                    pfig,
                    {"n_freqs": int(len(freqs))},
                    group=g,
                )
            )
        except Exception:
            pass
    if ctx.task.ohlcv and all(k in ctx.task.ohlcv for k in ("open", "high", "low", "close")):
        o = ctx.task.ohlcv
        ts = df[o["time"]] if o.get("time") and o["time"] in df.columns else x
        candle = go.Figure(
            go.Candlestick(
                x=ts,
                open=pd.to_numeric(df[o["open"]], errors="coerce"),
                high=pd.to_numeric(df[o["high"]], errors="coerce"),
                low=pd.to_numeric(df[o["low"]], errors="coerce"),
                close=pd.to_numeric(df[o["close"]], errors="coerce"),
            )
        )
        candle.update_layout(title="OHLC candlestick")
        arts.append(_fig(ctx, "EDA.P.OHLC", "OHLC candlestick", candle, {"columns": o}, group=g))
        # Returns + drawdown
        close = pd.to_numeric(df[o["close"]], errors="coerce")
        rets = close.pct_change(fill_method=None).dropna()
        rdist = px.histogram(rets, nbins=50, title="Return distribution")
        arts.append(
            _fig(ctx, "EDA.P.RETURNS", "Return distribution", rdist, {"n": int(len(rets))}, group=g)
        )
        wealth = (1 + rets).cumprod()
        dd = wealth / wealth.cummax() - 1
        dfig = go.Figure(go.Scatter(y=dd.values, mode="lines", name="drawdown"))
        dfig.update_layout(title="Drawdown curve")
        arts.append(
            _fig(
                ctx, "EDA.P.DRAWDOWN", "Drawdown curve", dfig, {"min_dd": float(dd.min())}, group=g
            )
        )
    return arts


def _quality_gauge(ctx: EDAContext) -> Artefact:
    miss = float(ctx.df.isna().mean().mean())
    score = max(0.0, 100.0 - miss * 100)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Data quality"},
            gauge={"axis": {"range": [0, 100]}},
        )
    )
    return _fig(
        ctx,
        "EDA.P.QUALITY_GAUGE",
        "Data quality gauge",
        fig,
        {"score": score, "mean_missing": miss},
        group="quality",
    )
