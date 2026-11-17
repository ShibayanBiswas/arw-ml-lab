"""Minimum CLE.P set for Eval Core — Plotly JSON from library numbers."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve, roc_curve


def plot_confusion(
    cm: list[list[float]],
    labels: list[str],
    *,
    title: str,
    plot_id: str = "CLE.P.CM",
) -> dict[str, Any]:
    import plotly.graph_objects as go

    z = np.asarray(cm, dtype=float)
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[str(l) for l in labels],
            y=[str(l) for l in labels],
            colorscale="Blues",
            text=z,
            texttemplate="%{text:.3g}",
        )
    )
    fig.update_layout(title=title, xaxis_title="Predicted", yaxis_title="True", height=420)
    return {"id": plot_id, "kind": "plot", "name": title, "plotly": fig.to_plotly_json()}


def plot_roc(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import auc

    fpr, tpr, _ = roc_curve(y_true, scores)
    a = auc(fpr, tpr)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"ROC AUC={a:.3f}"))
    fig.add_trace(
        go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="chance", line={"dash": "dash"})
    )
    fig.update_layout(title="ROC", xaxis_title="FPR", yaxis_title="TPR", height=400)
    return {
        "id": "CLE.P.ROC",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"auc": float(a)},
    }


def plot_pr(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import average_precision_score

    p, r, _ = precision_recall_curve(y_true, scores)
    ap = float(average_precision_score(y_true, scores))
    fig = go.Figure(go.Scatter(x=r, y=p, mode="lines", name=f"AP={ap:.3f}"))
    fig.update_layout(
        title="Precision-Recall", xaxis_title="Recall", yaxis_title="Precision", height=400
    )
    return {"id": "CLE.P.PR", "kind": "plot", "plotly": fig.to_plotly_json(), "numbers": {"ap": ap}}


def plot_reliability(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    frac_pos, mean_pred = calibration_curve(y_true, scores, n_bins=10, strategy="uniform")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mean_pred, y=frac_pos, mode="lines+markers", name="model"))
    fig.add_trace(
        go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="perfect", line={"dash": "dash"})
    )
    fig.update_layout(
        title="Reliability",
        xaxis_title="Mean predicted",
        yaxis_title="Fraction positive",
        height=400,
    )
    return {"id": "CLE.P.RELIABILITY", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_gains_lift(y_true: np.ndarray, scores: np.ndarray) -> list[dict[str, Any]]:
    """Cumulative gains + lift from ranked scores (library sort + thin arithmetic)."""
    import plotly.graph_objects as go

    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores, dtype=float)
    order = np.argsort(-s)
    y_sorted = y[order]
    n = len(y_sorted)
    cum_pos = np.cumsum(y_sorted)
    total_pos = max(int(cum_pos[-1]), 1)
    pct = np.arange(1, n + 1) / n
    gains = cum_pos / total_pos
    baseline = pct
    lift = gains / np.maximum(baseline, 1e-12)
    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(x=pct, y=gains, mode="lines", name="model"))
    fig_g.add_trace(
        go.Scatter(x=pct, y=baseline, mode="lines", name="baseline", line={"dash": "dash"})
    )
    fig_g.update_layout(
        title="Cumulative gains", xaxis_title="% population", yaxis_title="% positives", height=400
    )
    fig_l = go.Figure(go.Scatter(x=pct, y=lift, mode="lines", name="lift"))
    fig_l.add_hline(y=1.0, line_dash="dash")
    fig_l.update_layout(title="Lift", xaxis_title="% population", yaxis_title="Lift", height=400)
    return [
        {"id": "CLE.P.GAINS", "kind": "plot", "plotly": fig_g.to_plotly_json()},
        {"id": "CLE.P.LIFT", "kind": "plot", "plotly": fig_l.to_plotly_json()},
    ]


def plot_ks(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from scipy import stats

    y = np.asarray(y_true)
    s = np.asarray(scores, dtype=float)
    pos = s[y == 1] if set(np.unique(y)).issubset({0, 1}) else s[y == y.max()]
    neg = s[y == 0] if set(np.unique(y)).issubset({0, 1}) else s[y != y.max()]
    if len(pos) < 2 or len(neg) < 2:
        return {"id": "CLE.P.KS", "kind": "plot", "plotly": {}, "numbers": {"ks": None}}
    ks_stat, p = stats.ks_2samp(pos, neg)
    # ECDFs
    x = np.sort(np.concatenate([pos, neg]))
    ecdf_p = np.searchsorted(np.sort(pos), x, side="right") / len(pos)
    ecdf_n = np.searchsorted(np.sort(neg), x, side="right") / len(neg)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=ecdf_p, mode="lines", name="positive"))
    fig.add_trace(go.Scatter(x=x, y=ecdf_n, mode="lines", name="negative"))
    fig.update_layout(
        title=f"KS={ks_stat:.3f}", xaxis_title="Score", yaxis_title="ECDF", height=400
    )
    return {
        "id": "CLE.P.KS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"ks": float(ks_stat), "pvalue": float(p)},
    }


def plot_threshold_vs_metric(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import f1_score, precision_score, recall_score

    y = np.asarray(y_true)
    s = np.asarray(scores, dtype=float)
    thr = np.linspace(0.05, 0.95, 19)
    f1s, precs, recs = [], [], []
    for t in thr:
        pred = (s >= t).astype(int)
        f1s.append(float(f1_score(y, pred, zero_division=np.nan)))
        precs.append(float(precision_score(y, pred, zero_division=np.nan)))
        recs.append(float(recall_score(y, pred, zero_division=np.nan)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=thr, y=f1s, mode="lines", name="F1"))
    fig.add_trace(go.Scatter(x=thr, y=precs, mode="lines", name="Precision"))
    fig.add_trace(go.Scatter(x=thr, y=recs, mode="lines", name="Recall"))
    fig.update_layout(
        title="Threshold vs metric", xaxis_title="Threshold", yaxis_title="Score", height=400
    )
    return {"id": "CLE.P.THRESHOLD", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_det(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import det_curve

    fpr, fnr, _ = det_curve(y_true, scores)
    fig = go.Figure(go.Scatter(x=fpr, y=fnr, mode="lines", name="DET"))
    fig.update_layout(title="DET", xaxis_title="FPR", yaxis_title="FNR", height=400)
    return {"id": "CLE.P.DET", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_prob_density_by_class(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    import plotly.graph_objects as go

    y = np.asarray(y_true)
    s = np.asarray(scores, dtype=float)
    fig = go.Figure()
    for lab in sorted(np.unique(y)):
        fig.add_trace(go.Histogram(x=s[y == lab], name=str(lab), opacity=0.55, nbinsx=30))
    fig.update_layout(
        title="Score density by class",
        barmode="overlay",
        xaxis_title="Score",
        height=400,
    )
    return {"id": "CLE.P.PROB_DENS", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_per_class_prf(
    y_true: np.ndarray, y_pred: np.ndarray, labels: list[Any] | None = None
) -> dict[str, Any]:
    import plotly.graph_objects as go
    from sklearn.metrics import precision_recall_fscore_support

    labels = labels if labels is not None else sorted(np.unique(y_true).tolist())
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=np.nan
    )
    x = [str(l) for l in labels]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=p, name="Precision"))
    fig.add_trace(go.Bar(x=x, y=r, name="Recall"))
    fig.add_trace(go.Bar(x=x, y=f1, name="F1"))
    fig.update_layout(title="Per-class P/R/F1", barmode="group", height=400)
    return {"id": "CLE.P.PER_CLASS_PRF", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_per_class_bars(
    y_true: np.ndarray | list[np.ndarray],
    y_pred: np.ndarray | list[np.ndarray],
    *,
    labels: list[Any] | None = None,
) -> dict[str, Any]:
    """CLE.P.PER_CLASS_BARS — grouped P/R/F1 per class with ±1 std across folds when CV lists."""
    import plotly.graph_objects as go
    from sklearn.metrics import precision_recall_fscore_support

    if isinstance(y_true, np.ndarray):
        folds_true: list[np.ndarray] = [y_true]
        folds_pred: list[np.ndarray] = [y_pred]  # type: ignore[assignment]
    else:
        folds_true = [np.asarray(t).ravel() for t in y_true]
        folds_pred = [np.asarray(p).ravel() for p in y_pred]  # type: ignore[union-attr]
        if len(folds_true) != len(folds_pred):
            raise ValueError("y_true and y_pred fold lists must have the same length")

    if labels is None:
        seen: set[Any] = set()
        for yt in folds_true:
            for v in np.unique(yt):
                seen.add(v.item() if isinstance(v, np.generic) else v)
        labels = sorted(seen, key=str)

    per_fold_p: list[np.ndarray] = []
    per_fold_r: list[np.ndarray] = []
    per_fold_f1: list[np.ndarray] = []
    for yt, yp in zip(folds_true, folds_pred, strict=True):
        p, r, f1, _ = precision_recall_fscore_support(
            yt, yp, labels=labels, zero_division=np.nan
        )
        per_fold_p.append(p.astype(float))
        per_fold_r.append(r.astype(float))
        per_fold_f1.append(f1.astype(float))

    p_arr = np.vstack(per_fold_p)
    r_arr = np.vstack(per_fold_r)
    f1_arr = np.vstack(per_fold_f1)
    p_mean = np.nanmean(p_arr, axis=0)
    r_mean = np.nanmean(r_arr, axis=0)
    f1_mean = np.nanmean(f1_arr, axis=0)
    p_std = np.nanstd(p_arr, axis=0, ddof=1) if p_arr.shape[0] > 1 else np.zeros_like(p_mean)
    r_std = np.nanstd(r_arr, axis=0, ddof=1) if r_arr.shape[0] > 1 else np.zeros_like(r_mean)
    f1_std = np.nanstd(f1_arr, axis=0, ddof=1) if f1_arr.shape[0] > 1 else np.zeros_like(f1_mean)

    x = [str(l) for l in labels]
    fig = go.Figure()
    for name, mean, std, color in (
        ("Precision", p_mean, p_std, "#2e86ab"),
        ("Recall", r_mean, r_std, "#c9a227"),
        ("F1", f1_mean, f1_std, "#6b4e71"),
    ):
        fig.add_trace(
            go.Bar(
                x=x,
                y=mean,
                name=name,
                marker_color=color,
                error_y=dict(type="data", array=std, visible=True, thickness=1.2),
            )
        )
    n_folds = len(folds_true)
    title = "Per-class metrics"
    if n_folds > 1:
        title += f" (mean ± std, {n_folds} folds)"
    fig.update_layout(title=title, barmode="group", height=420, bargap=0.15)

    numbers: dict[str, Any] = {
        "n_folds": n_folds,
        "labels": [str(l) for l in labels],
        "precision_mean": {str(l): float(v) for l, v in zip(labels, p_mean, strict=True)},
        "recall_mean": {str(l): float(v) for l, v in zip(labels, r_mean, strict=True)},
        "f1_mean": {str(l): float(v) for l, v in zip(labels, f1_mean, strict=True)},
    }
    if n_folds > 1:
        numbers["precision_std"] = {str(l): float(v) for l, v in zip(labels, p_std, strict=True)}
        numbers["recall_std"] = {str(l): float(v) for l, v in zip(labels, r_std, strict=True)}
        numbers["f1_std"] = {str(l): float(v) for l, v in zip(labels, f1_std, strict=True)}

    return {
        "id": "CLE.P.PER_CLASS_BARS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": numbers,
    }


def plot_top_confusions(
    cm_counts: list[list[float]], labels: list[str], *, top_n: int = 10
) -> dict[str, Any]:
    """CLE.P.TOP_CONFUSIONS — largest off-diagonal pairs from sklearn confusion_matrix."""
    import plotly.graph_objects as go

    z = np.asarray(cm_counts, dtype=float)
    pairs: list[tuple[str, float]] = []
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            if i == j:
                continue
            pairs.append((f"{labels[i]}→{labels[j]}", float(z[i, j])))
    pairs.sort(key=lambda t: t[1], reverse=True)
    pairs = pairs[:top_n]
    fig = go.Figure(go.Bar(x=[p[0] for p in pairs], y=[p[1] for p in pairs]))
    fig.update_layout(
        title="Top confused pairs", xaxis_title="True→Pred", yaxis_title="Count", height=400
    )
    return {
        "id": "CLE.P.TOP_CONFUSIONS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"pairs": [{"pair": a, "count": b} for a, b in pairs]},
    }


def plot_class_pred_error(
    y_true: np.ndarray, y_pred: np.ndarray, labels: list[Any] | None = None
) -> dict[str, Any]:
    """CLE.P.CLASS_PRED_ERROR — stacked bar per true class (Yellowbrick design)."""
    import plotly.graph_objects as go
    from sklearn.metrics import confusion_matrix

    labels = labels if labels is not None else sorted(np.unique(y_true).tolist())
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    x = [str(l) for l in labels]
    fig = go.Figure()
    for j, pred_lab in enumerate(labels):
        fig.add_trace(go.Bar(x=x, y=cm[:, j], name=f"pred={pred_lab}"))
    fig.update_layout(
        title="Class prediction error",
        barmode="stack",
        xaxis_title="True class",
        yaxis_title="Count",
        height=400,
    )
    return {"id": "CLE.P.CLASS_PRED_ERROR", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_support_bars(y_true: np.ndarray, labels: list[Any] | None = None) -> dict[str, Any]:
    """CLE.P.SUPPORT_BARS — class counts in the evaluated split."""
    import plotly.graph_objects as go

    y = np.asarray(y_true)
    labels = labels if labels is not None else sorted(np.unique(y).tolist())
    counts = [int(np.sum(y == lab)) for lab in labels]
    fig = go.Figure(go.Bar(x=[str(l) for l in labels], y=counts))
    fig.update_layout(title="Class support", xaxis_title="Class", yaxis_title="Count", height=360)
    return {
        "id": "CLE.P.SUPPORT_BARS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"counts": dict(zip([str(l) for l in labels], counts, strict=True))},
    }


def plot_precision_at_k(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    """CLE.P.PRECISION_AT_K — precision and capture vs population %."""
    import plotly.graph_objects as go

    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores, dtype=float)
    order = np.argsort(-s)
    y_sorted = y[order]
    n = len(y_sorted)
    total_pos = max(int(y_sorted.sum()), 1)
    ks = np.linspace(0.05, 1.0, 20)
    prec_at, capture = [], []
    for k in ks:
        m = max(1, int(np.ceil(k * n)))
        top = y_sorted[:m]
        prec_at.append(float(top.mean()))
        capture.append(float(top.sum() / total_pos))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ks, y=prec_at, mode="lines", name="precision@k%"))
    fig.add_trace(go.Scatter(x=ks, y=capture, mode="lines", name="capture@k%"))
    fig.update_layout(
        title="Precision / capture @ k%",
        xaxis_title="% population",
        yaxis_title="Rate",
        height=400,
    )
    return {"id": "CLE.P.PRECISION_AT_K", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_confidence_errors(
    y_true: np.ndarray, y_pred: np.ndarray, scores: np.ndarray
) -> dict[str, Any]:
    """CLE.P.CONFIDENCE_ERRORS — p(pred) for correct vs wrong."""
    import plotly.graph_objects as go

    y = np.asarray(y_true)
    pred = np.asarray(y_pred)
    s = np.asarray(scores, dtype=float)
    if s.ndim == 2:
        conf = s[np.arange(len(pred)), pred.astype(int)] if s.shape[1] > 1 else s[:, 0]
    else:
        conf = np.where(pred.astype(int) == 1, s, 1.0 - s)
    correct = conf[y == pred]
    wrong = conf[y != pred]
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=correct, name="correct", opacity=0.55, nbinsx=25))
    fig.add_trace(go.Histogram(x=wrong, name="wrong", opacity=0.55, nbinsx=25))
    fig.update_layout(
        title="Confidence: correct vs wrong",
        barmode="overlay",
        xaxis_title="p(predicted)",
        height=400,
    )
    return {"id": "CLE.P.CONFIDENCE_ERRORS", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_learning_curve(
    estimator: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    cv: int = 3,
    seed: int = 42,
) -> dict[str, Any]:
    """CLE.P.LEARNING — sklearn ``learning_curve`` → Plotly."""
    import plotly.graph_objects as go
    from sklearn.model_selection import learning_curve

    train_sizes, train_scores, val_scores = learning_curve(
        estimator,
        X,
        y,
        cv=cv,
        random_state=seed,
        shuffle=True,
        n_jobs=1,
        train_sizes=np.linspace(0.3, 1.0, 5),
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=train_sizes,
            y=np.mean(train_scores, axis=1),
            error_y={"array": np.std(train_scores, axis=1, ddof=1)},
            mode="lines+markers",
            name="train",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=train_sizes,
            y=np.mean(val_scores, axis=1),
            error_y={"array": np.std(val_scores, axis=1, ddof=1)},
            mode="lines+markers",
            name="cv",
        )
    )
    fig.update_layout(
        title="Learning curve",
        xaxis_title="Train size",
        yaxis_title="Score",
        height=400,
    )
    return {
        "id": "CLE.P.LEARNING",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "train_sizes": train_sizes.tolist(),
            "train_mean": np.mean(train_scores, axis=1).tolist(),
            "val_mean": np.mean(val_scores, axis=1).tolist(),
        },
    }


def plot_validation_curve(
    estimator: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    param_name: str,
    param_range: list[Any],
    cv: int = 3,
) -> dict[str, Any]:
    """CLE.P.VALIDATION — sklearn ``validation_curve`` → Plotly."""
    import plotly.graph_objects as go
    from sklearn.model_selection import validation_curve

    train_scores, val_scores = validation_curve(
        estimator,
        X,
        y,
        param_name=param_name,
        param_range=param_range,
        cv=cv,
        n_jobs=1,
    )
    x = [str(p) for p in param_range]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=np.mean(train_scores, axis=1),
            error_y={"array": np.std(train_scores, axis=1, ddof=1)},
            mode="lines+markers",
            name="train",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=np.mean(val_scores, axis=1),
            error_y={"array": np.std(val_scores, axis=1, ddof=1)},
            mode="lines+markers",
            name="cv",
        )
    )
    fig.update_layout(
        title=f"Validation curve ({param_name})",
        xaxis_title=param_name,
        yaxis_title="Score",
        height=400,
    )
    return {
        "id": "CLE.P.VALIDATION",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"param_name": param_name, "param_range": x},
    }


def plot_report_heatmap(
    y_true: np.ndarray, y_pred: np.ndarray, labels: list[Any] | None = None
) -> dict[str, Any]:
    """CLE.P.REPORT_HEATMAP — class × {precision, recall, F1, support}."""
    import plotly.graph_objects as go
    from sklearn.metrics import precision_recall_fscore_support

    labels = labels if labels is not None else sorted(np.unique(y_true).tolist())
    p, r, f1, s = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=np.nan
    )
    z = np.vstack([p, r, f1, s / max(float(np.sum(s)), 1.0)])
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[str(l) for l in labels],
            y=["precision", "recall", "f1", "support_share"],
            colorscale="Blues",
            text=np.round(z, 3),
            texttemplate="%{text}",
        )
    )
    fig.update_layout(title="Classification report heatmap", height=360)
    return {"id": "CLE.P.REPORT_HEATMAP", "kind": "plot", "plotly": fig.to_plotly_json()}


def plot_cost_curve(
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    c_fp: float = 1.0,
    c_fn: float = 1.0,
) -> dict[str, Any]:
    """CLE.P.COST_CURVE — expected cost vs threshold (thin on sklearn roc_curve)."""
    import plotly.graph_objects as go
    from sklearn.metrics import roc_curve

    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores, dtype=float)
    fpr, tpr, thr = roc_curve(y, s)
    # Align thr length; sklearn may return thr shorter by one — pad with last
    if len(thr) < len(fpr):
        thr = np.r_[thr, thr[-1] if len(thr) else 0.5]
    n = len(y)
    pos = float(np.sum(y == 1))
    neg = float(n - pos)
    # Expected cost at each operating point: C_FP·FP + C_FN·FN
    fp = fpr * neg
    fn = (1.0 - tpr) * pos
    cost = c_fp * fp + c_fn * fn
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=thr, y=cost, mode="lines", name="expected cost"))
    best_i = int(np.nanargmin(cost)) if len(cost) else 0
    fig.add_vline(x=float(thr[best_i]), line_dash="dash", annotation_text="min cost")
    fig.update_layout(
        title="Expected cost vs threshold",
        xaxis_title="threshold",
        yaxis_title="expected cost",
        height=360,
    )
    return {
        "id": "CLE.P.COST_CURVE",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "c_fp": c_fp,
            "c_fn": c_fn,
            "best_threshold": float(thr[best_i]),
            "best_cost": float(cost[best_i]),
        },
    }


def plot_class_balance(
    counts_before: dict[str, int],
    counts_after: dict[str, int] | None = None,
) -> dict[str, Any]:
    """CLE.P.CLASS_BALANCE — class counts before/after resampling."""
    import plotly.graph_objects as go

    labels = sorted(set(counts_before) | set(counts_after or {}))
    fig = go.Figure()
    fig.add_trace(go.Bar(name="before", x=labels, y=[int(counts_before.get(l, 0)) for l in labels]))
    if counts_after is not None:
        fig.add_trace(
            go.Bar(name="after", x=labels, y=[int(counts_after.get(l, 0)) for l in labels])
        )
    fig.update_layout(
        barmode="group",
        title="Class balance",
        xaxis_title="class",
        yaxis_title="count",
        height=360,
    )
    return {
        "id": "CLE.P.CLASS_BALANCE",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"before": counts_before, "after": counts_after},
    }


def plot_metric_folds(fold_metrics: dict[str, list[float]]) -> dict[str, Any]:
    """CLE.P.METRIC_FOLDS — box/strip of each metric across folds."""
    import plotly.graph_objects as go

    fig = go.Figure()
    for name, vals in fold_metrics.items():
        v = [float(x) for x in vals if np.isfinite(x)]
        fig.add_trace(go.Box(y=v, name=name, boxpoints="all", jitter=0.3))
    fig.update_layout(title="Metric by fold", yaxis_title="score", height=400)
    means = {k: float(np.nanmean(v)) if len(v) else float("nan") for k, v in fold_metrics.items()}
    return {
        "id": "CLE.P.METRIC_FOLDS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"means": means},
    }


def plot_cm_cost(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    cost_matrix: np.ndarray,
    *,
    labels: list[Any] | None = None,
) -> dict[str, Any]:
    """CLE.P.CM_COST — cell = C_ij · N_ij from sklearn confusion_matrix."""
    import plotly.graph_objects as go
    from sklearn.metrics import confusion_matrix

    labels = labels if labels is not None else sorted(np.unique(np.r_[y_true, y_pred]).tolist())
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    C = np.asarray(cost_matrix, dtype=float)
    if C.shape != cm.shape:
        raise ValueError(f"cost_matrix shape {C.shape} != cm {cm.shape}")
    weighted = C * cm
    total = float(np.nansum(weighted))
    fig = go.Figure(
        data=go.Heatmap(
            z=weighted,
            x=[str(l) for l in labels],
            y=[str(l) for l in labels],
            colorscale="Reds",
            text=np.round(weighted, 2),
            texttemplate="%{text}",
        )
    )
    fig.update_layout(
        title=f"Cost-weighted CM (total={total:.2f})",
        xaxis_title="predicted",
        yaxis_title="true",
        height=400,
    )
    return {
        "id": "CLE.P.CM_COST",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"total_cost": total, "matrix": weighted.tolist()},
    }


def plot_cm_delta(
    y_true: np.ndarray,
    y_pred_a: np.ndarray,
    y_pred_b: np.ndarray,
    *,
    labels: list[Any] | None = None,
) -> dict[str, Any]:
    """CLE.P.CM_DELTA — confusion A − B (diverging)."""
    import plotly.graph_objects as go
    from sklearn.metrics import confusion_matrix

    labels = labels if labels is not None else sorted(np.unique(y_true).tolist())
    a = confusion_matrix(y_true, y_pred_a, labels=labels)
    b = confusion_matrix(y_true, y_pred_b, labels=labels)
    delta = a.astype(float) - b.astype(float)
    fig = go.Figure(
        data=go.Heatmap(
            z=delta,
            x=[str(l) for l in labels],
            y=[str(l) for l in labels],
            colorscale="RdBu",
            zmid=0,
            text=np.round(delta, 1),
            texttemplate="%{text}",
        )
    )
    fig.update_layout(title="CM delta (A − B)", height=400)
    return {
        "id": "CLE.P.CM_DELTA",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"delta": delta.tolist()},
    }


def plot_compare_bars(
    model_scores: dict[str, float],
    *,
    cis: dict[str, tuple[float, float]] | None = None,
    metric: str = "score",
) -> dict[str, Any]:
    """CLE.P.COMPARE_BARS — model comparison bars with optional 95% CI."""
    import plotly.graph_objects as go

    names = list(model_scores.keys())
    vals = [float(model_scores[n]) for n in names]
    err = None
    if cis:
        err = [
            [float(model_scores[n] - cis[n][0]) if n in cis else 0.0 for n in names],
            [float(cis[n][1] - model_scores[n]) if n in cis else 0.0 for n in names],
        ]
    fig = go.Figure(
        go.Bar(
            x=names,
            y=vals,
            error_y=(
                {"type": "data", "symmetric": False, "array": err[1], "arrayminus": err[0]}
                if err
                else None
            ),
        )
    )
    fig.update_layout(title=f"Model comparison ({metric})", yaxis_title=metric, height=360)
    return {
        "id": "CLE.P.COMPARE_BARS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"scores": model_scores, "cis": cis},
    }


def plot_pvalue_heatmap(
    fold_scores: dict[str, list[float]],
    *,
    higher_is_better: bool = True,
    metric: str = "accuracy",
    alpha: float = 0.05,
) -> dict[str, Any]:
    """CLE.P.PVALUE_HEATMAP — Nemenyi pairwise p-values with Holm adjustment."""
    import pandas as pd
    import plotly.graph_objects as go
    from scikit_posthocs import posthoc_nemenyi_friedman, sign_array

    from labcore.eval.regression.plots import _holm_adjust_symmetric

    df = pd.DataFrame({k: np.asarray(v, dtype=float) for k, v in fold_scores.items()})
    if df.shape[1] < 2 or df.shape[0] < 2:
        return {
            "id": "CLE.P.PVALUE_HEATMAP",
            "kind": "plot",
            "plotly": {
                "data": [],
                "layout": {"title": "P-value heatmap needs ≥2 models and ≥2 folds"},
            },
            "numbers": {"status": "not computed", "reason": "need ≥2 models and ≥2 folds"},
        }
    work = df if higher_is_better else -df
    names = list(work.columns)
    raw = np.asarray(posthoc_nemenyi_friedman(work.to_numpy()), dtype=float)
    raw_df = pd.DataFrame(raw, index=names, columns=names)
    holm = _holm_adjust_symmetric(raw_df.to_numpy(dtype=float))
    holm_df = pd.DataFrame(holm, index=names, columns=names)
    sig = sign_array(holm_df, alpha=alpha)
    text = np.where(
        sig == 1,
        np.char.add(np.round(holm, 3).astype(str), "*"),
        np.round(holm, 3).astype(str),
    )
    np.fill_diagonal(text, "—")
    fig = go.Figure(
        go.Heatmap(
            z=holm,
            x=names,
            y=names,
            colorscale="Viridis_r",
            zmin=0.0,
            zmax=1.0,
            text=text,
            texttemplate="%{text}",
            hovertemplate="%{y} vs %{x}<br>Holm p=%{z:.4f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Pairwise p-values ({metric}, Holm)",
        xaxis_title="Model",
        yaxis_title="Model",
        height=max(320, 56 * len(names)),
    )
    return {
        "id": "CLE.P.PVALUE_HEATMAP",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "status": "ok",
            "metric": metric,
            "higher_is_better": higher_is_better,
            "alpha": alpha,
            "nemenyi_pvalues": raw_df.to_dict(),
            "holm_pvalues": holm_df.to_dict(),
            "significant_pairs": sign_array(holm_df, alpha=alpha).tolist(),
        },
    }


def plot_discrimination(
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    n_splits: int = 20,
    seed: int = 42,
) -> dict[str, Any]:
    """CLE.P.DISCRIMINATION — precision/recall/F1/queue vs threshold (Yellowbrick-style)."""
    import plotly.graph_objects as go
    from sklearn.metrics import f1_score, precision_score, recall_score
    from sklearn.model_selection import StratifiedShuffleSplit

    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores, dtype=float)
    thresholds = np.linspace(0.05, 0.95, 19)
    prec_m: list[float] = []
    rec_m: list[float] = []
    f1_m: list[float] = []
    queue_m: list[float] = []
    bands: dict[str, tuple[list[float], list[float]]] = {
        "precision": ([], []),
        "recall": ([], []),
        "f1": ([], []),
        "queue_rate": ([], []),
    }
    sss = StratifiedShuffleSplit(n_splits=n_splits, test_size=0.5, random_state=seed)
    for t in thresholds:
        ps: list[float] = []
        rs: list[float] = []
        fs: list[float] = []
        qs: list[float] = []
        for _, idx in sss.split(s, y):
            yt, st = y[idx], s[idx]
            yp = (st >= t).astype(int)
            ps.append(float(precision_score(yt, yp, zero_division=np.nan)))
            rs.append(float(recall_score(yt, yp, zero_division=np.nan)))
            fs.append(float(f1_score(yt, yp, zero_division=np.nan)))
            qs.append(float(np.mean(yp)))
        for name, bucket, mean_l in (
            ("precision", ps, prec_m),
            ("recall", rs, rec_m),
            ("f1", fs, f1_m),
            ("queue_rate", qs, queue_m),
        ):
            arr = np.asarray(bucket, dtype=float)
            mean_l.append(float(np.nanmean(arr)))
            bands[name][0].append(float(np.nanpercentile(arr, 5)))
            bands[name][1].append(float(np.nanpercentile(arr, 95)))
    fig = go.Figure()
    for name, mean in (
        ("precision", prec_m),
        ("recall", rec_m),
        ("f1", f1_m),
        ("queue_rate", queue_m),
    ):
        lo, hi = bands[name]
        fig.add_trace(go.Scatter(x=thresholds, y=mean, mode="lines", name=name))
        fig.add_trace(
            go.Scatter(
                x=np.r_[thresholds, thresholds[::-1]],
                y=np.r_[hi, lo[::-1]],
                fill="toself",
                name=f"{name} band",
                line={"width": 0},
                showlegend=False,
                opacity=0.15,
            )
        )
    fig.update_layout(
        title="Discrimination threshold",
        xaxis_title="threshold",
        yaxis_title="metric",
        height=400,
    )
    return {
        "id": "CLE.P.DISCRIMINATION",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"thresholds": thresholds.tolist(), "f1_mean": f1_m},
    }


def plot_threshold_stability(
    fold_thresholds: list[float],
    *,
    method: str = "youden",
) -> dict[str, Any]:
    """CLE.P.THRESHOLD_STABILITY — per-fold optimal t* strip + mean ± std."""
    import plotly.graph_objects as go

    vals = [float(t) for t in fold_thresholds if np.isfinite(t)]
    mean = float(np.mean(vals)) if vals else float("nan")
    std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[method] * len(vals),
            y=vals,
            mode="markers",
            name="fold t*",
            marker={"size": 10},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[method],
            y=[mean],
            mode="markers",
            name="mean",
            error_y={"type": "data", "array": [std], "visible": True},
            marker={"symbol": "diamond", "size": 12},
        )
    )
    fig.update_layout(
        title=f"Threshold stability ({method})",
        yaxis_title="t*",
        height=360,
    )
    return {
        "id": "CLE.P.THRESHOLD_STABILITY",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"mean": mean, "std": std, "fold_thresholds": vals, "method": method},
    }


def plot_cm_folds(
    fold_cms: list[np.ndarray],
    *,
    labels: list[Any] | None = None,
) -> dict[str, Any]:
    """CLE.P.CM_FOLDS — per-fold confusion matrices (row-normalised small multiples)."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    if not fold_cms:
        raise ValueError("fold_cms must be non-empty")
    n = len(fold_cms)
    cols = min(3, n)
    rows = int(np.ceil(n / cols))
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[f"fold {i}" for i in range(n)])
    label_strs = [str(l) for l in (labels or list(range(fold_cms[0].shape[0])))]
    matrices = []
    for i, cm in enumerate(fold_cms):
        cm = np.asarray(cm, dtype=float)
        row_sums = cm.sum(axis=1, keepdims=True)
        row_sums = np.where(row_sums == 0, 1.0, row_sums)
        norm = cm / row_sums
        matrices.append(norm.tolist())
        r, c = divmod(i, cols)
        fig.add_trace(
            go.Heatmap(
                z=norm,
                x=label_strs,
                y=label_strs,
                colorscale="Blues",
                zmin=0,
                zmax=1,
                showscale=(i == 0),
            ),
            row=r + 1,
            col=c + 1,
        )
    fig.update_layout(title="Per-fold confusion (row-norm)", height=280 * rows)
    return {
        "id": "CLE.P.CM_FOLDS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"fold_cms_row_norm": matrices},
    }


def plot_cm_cv(
    fold_cms: list[np.ndarray],
    *,
    labels: list[Any] | None = None,
) -> dict[str, Any]:
    """CLE.P.CM_CV — cell = mean ± std of row-normalised rate across folds."""
    import plotly.graph_objects as go

    if not fold_cms:
        raise ValueError("fold_cms must be non-empty")
    norms = []
    pooled = np.zeros_like(fold_cms[0], dtype=float)
    for cm in fold_cms:
        cm = np.asarray(cm, dtype=float)
        pooled += cm
        row_sums = cm.sum(axis=1, keepdims=True)
        row_sums = np.where(row_sums == 0, 1.0, row_sums)
        norms.append(cm / row_sums)
    stack = np.stack(norms, axis=0)
    mean = np.nanmean(stack, axis=0)
    std = np.nanstd(stack, axis=0, ddof=1) if len(norms) > 1 else np.zeros_like(mean)
    label_strs = [str(l) for l in (labels or list(range(mean.shape[0])))]
    text = np.array(
        [
            [f"{mean[i, j]:.2f}±{std[i, j]:.2f}" for j in range(mean.shape[1])]
            for i in range(mean.shape[0])
        ]
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=mean,
            x=label_strs,
            y=label_strs,
            colorscale="Blues",
            zmin=0,
            zmax=1,
            text=text,
            texttemplate="%{text}",
            customdata=pooled,
            hovertemplate="true=%{y} pred=%{x}<br>mean=%{z:.3f}<br>pooled=%{customdata}<extra></extra>",
        )
    )
    fig.update_layout(title="CV-aggregated CM (mean±std row-norm)", height=400)
    return {
        "id": "CLE.P.CM_CV",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "mean": mean.tolist(),
            "std": std.tolist(),
            "pooled_counts": pooled.tolist(),
        },
    }


def plot_cm_multilabel(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    label_names: list[str] | None = None,
) -> dict[str, Any]:
    """CLE.P.CM_MULTILABEL — per-label 2×2 from sklearn multilabel_confusion_matrix."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from sklearn.metrics import multilabel_confusion_matrix

    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)
    mcm = multilabel_confusion_matrix(yt, yp)
    n = mcm.shape[0]
    names = label_names or [f"L{i}" for i in range(n)]
    cols = min(4, n)
    rows = int(np.ceil(n / cols))
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=names[:n])
    for i in range(n):
        r, c = divmod(i, cols)
        fig.add_trace(
            go.Heatmap(
                z=mcm[i],
                x=["pred0", "pred1"],
                y=["true0", "true1"],
                colorscale="Blues",
                text=mcm[i],
                texttemplate="%{text}",
                showscale=(i == 0),
            ),
            row=r + 1,
            col=c + 1,
        )
    fig.update_layout(title="Multilabel 2×2 CMs", height=260 * rows)
    return {
        "id": "CLE.P.CM_MULTILABEL",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {"matrices": mcm.tolist(), "labels": names},
    }


def plot_multilabel_bars(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    label_names: list[str] | None = None,
) -> dict[str, Any]:
    """CLE.P.MULTILABEL_BARS — per-label F1 bars + label-cardinality histogram."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from sklearn.metrics import f1_score

    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)
    n_labels = yt.shape[1]
    names = label_names or [f"L{i}" for i in range(n_labels)]
    f1 = f1_score(yt, yp, average=None, zero_division=np.nan)
    support = yt.sum(axis=0).astype(int)
    cardinality = yt.sum(axis=1).astype(int)
    card_vals, card_counts = np.unique(cardinality, return_counts=True)
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.55, 0.45],
        subplot_titles=("Per-label F1", "Label cardinality (true)"),
        vertical_spacing=0.12,
    )
    fig.add_trace(
        go.Bar(x=names, y=f1, name="F1", showlegend=False),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Histogram(
            x=cardinality,
            xbins=dict(start=float(card_vals.min()) - 0.5, end=float(card_vals.max()) + 1.5, size=1),
            name="count",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.update_yaxes(title_text="F1", row=1, col=1)
    fig.update_xaxes(title_text="Labels", row=1, col=1)
    fig.update_xaxes(title_text="Labels per sample", row=2, col=1)
    fig.update_yaxes(title_text="Samples", row=2, col=1)
    fig.update_layout(title="Multilabel metrics", height=520)
    label_density = float(yt.mean())
    return {
        "id": "CLE.P.MULTILABEL_BARS",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "per_label_f1": {n: float(v) for n, v in zip(names, f1, strict=True)},
            "support": {n: int(v) for n, v in zip(names, support, strict=True)},
            "label_density": label_density,
            "cardinality_hist": {
                str(int(k)): int(c) for k, c in zip(card_vals, card_counts, strict=True)
            },
        },
    }


def plot_conformal(
    y_true: np.ndarray,
    prediction_sets: np.ndarray,
    *,
    class_labels: list[Any] | None = None,
    confidence_level: float | None = None,
) -> dict[str, Any]:
    """CLE.P.CONFORMAL — set-size histogram + per-class coverage (MAPIE set format)."""
    import plotly.graph_objects as go
    from mapie.metrics.classification import (
        classification_coverage_score,
        classification_mean_width_score,
    )
    from plotly.subplots import make_subplots

    yt = np.asarray(y_true).ravel()
    ps = np.asarray(prediction_sets, dtype=bool)
    if ps.ndim == 3 and ps.shape[-1] == 1:
        ps = ps[..., 0]
    if ps.ndim != 2 or len(yt) != ps.shape[0]:
        raise ValueError("prediction_sets must be (n_samples, n_classes) matching y_true length")
    n_classes = ps.shape[1]
    labels = class_labels or [str(i) for i in range(n_classes)]
    if len(labels) != n_classes:
        raise ValueError("class_labels length must match prediction_sets columns")
    label_to_idx = {lbl: i for i, lbl in enumerate(labels)}
    try:
        true_idx = np.array([label_to_idx[v] for v in yt])
    except KeyError as exc:
        raise ValueError(f"true label not in class_labels: {exc.args[0]}") from exc

    set_sizes = ps.sum(axis=1).astype(int)
    overall_cov = float(np.asarray(classification_coverage_score(yt, ps)).ravel()[0])
    mean_width = float(classification_mean_width_score(ps))

    per_class_cov: dict[str, float | None] = {}
    for j, name in enumerate(labels):
        mask = true_idx == j
        if not np.any(mask):
            per_class_cov[name] = None
        else:
            per_class_cov[name] = float(np.mean(ps[mask, j]))

    size_vals, size_counts = np.unique(set_sizes, return_counts=True)
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.45, 0.55],
        subplot_titles=("Prediction set size", "Coverage by true class"),
        vertical_spacing=0.12,
    )
    fig.add_trace(
        go.Histogram(
            x=set_sizes,
            xbins=dict(
                start=float(size_vals.min()) - 0.5,
                end=float(size_vals.max()) + 1.5,
                size=1,
            ),
            name="count",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    cov_y = [per_class_cov[n] for n in labels]
    fig.add_trace(
        go.Bar(
            x=list(labels),
            y=cov_y,
            name="coverage",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    if confidence_level is not None:
        fig.add_hline(
            y=confidence_level,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"target {confidence_level:.0%}",
            row=2,
            col=1,
        )
    fig.update_xaxes(title_text="Set size (# classes)", row=1, col=1)
    fig.update_yaxes(title_text="Samples", row=1, col=1)
    fig.update_xaxes(title_text="True class", row=2, col=1)
    fig.update_yaxes(title_text="Empirical coverage", range=[0, 1.05], row=2, col=1)
    title = "Conformal prediction sets"
    if confidence_level is not None:
        title += f" ({confidence_level:.0%} nominal)"
    fig.update_layout(title=title, height=520)

    return {
        "id": "CLE.P.CONFORMAL",
        "kind": "plot",
        "plotly": fig.to_plotly_json(),
        "numbers": {
            "overall_coverage": overall_cov,
            "mean_set_size": mean_width,
            "set_size_hist": {
                str(int(k)): int(c) for k, c in zip(size_vals, size_counts, strict=True)
            },
            "coverage_per_class": per_class_cov,
            "confidence_level": confidence_level,
            "n_samples": int(len(yt)),
        },
    }
