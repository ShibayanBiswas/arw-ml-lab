"""Thin Phase 2 algorithm registry — ≥10 R*/C* with defaults (seed 42)."""

from __future__ import annotations

from typing import Any

from labcore.registry.spec import AlgorithmSpec, ParamSpec


def _p(name: str, typ: str, default: Any, help_key: str, **kw: Any) -> ParamSpec:
    return ParamSpec(name=name, type=typ, default=default, help_key=help_key, **kw)  # type: ignore[arg-type]


def thin_algorithm_specs() -> list[AlgorithmSpec]:
    from labcore.deep.registry import deep_algorithm_specs
    from labcore.registry.algorithms_extra import extra_algorithm_specs

    rs = _p("random_state", "int", 42, "seed")
    base: list[AlgorithmSpec] = [
        AlgorithmSpec(
            id="R1",
            key="reg.ridge",
            family="regression",
            name="Ridge",
            library="sklearn",
            estimator="sklearn.linear_model.Ridge",
            params=[_p("alpha", "float", 1.0, "ridge_alpha", low=1e-4, high=100, log=True), rs],
            supports={"regression"},
            needs_scaling=True,
            edu_key="reg.ridge",
            tags=["linear"],
        ),
        AlgorithmSpec(
            id="R2",
            key="reg.lasso",
            family="regression",
            name="Lasso",
            library="sklearn",
            estimator="sklearn.linear_model.Lasso",
            params=[_p("alpha", "float", 0.001, "lasso_alpha", low=1e-5, high=10, log=True), rs],
            supports={"regression"},
            needs_scaling=True,
            edu_key="reg.lasso",
            tags=["linear"],
        ),
        AlgorithmSpec(
            id="R3",
            key="reg.elasticnet",
            family="regression",
            name="ElasticNet",
            library="sklearn",
            estimator="sklearn.linear_model.ElasticNet",
            params=[
                _p("alpha", "float", 0.001, "en_alpha", low=1e-5, high=10, log=True),
                _p("l1_ratio", "float", 0.5, "en_l1", low=0.0, high=1.0),
                rs,
            ],
            supports={"regression"},
            needs_scaling=True,
            edu_key="reg.elasticnet",
            tags=["linear"],
        ),
        AlgorithmSpec(
            id="R10",
            key="reg.rf",
            family="regression",
            name="RandomForestRegressor",
            library="sklearn",
            estimator="sklearn.ensemble.RandomForestRegressor",
            params=[
                _p("n_estimators", "int", 100, "rf_trees", low=50, high=500),
                _p("max_depth", "int_or_none", None, "rf_depth"),
                rs,
            ],
            supports={"regression"},
            edu_key="reg.rf",
            tags=["tree"],
        ),
        AlgorithmSpec(
            id="R15",
            key="reg.histgbm",
            family="regression",
            name="HistGradientBoostingRegressor",
            library="sklearn",
            estimator="sklearn.ensemble.HistGradientBoostingRegressor",
            params=[_p("max_iter", "int", 100, "hgb_iter", low=50, high=500), rs],
            supports={"regression"},
            handles_missing=True,
            edu_key="reg.histgbm",
            tags=["boosting"],
        ),
        AlgorithmSpec(
            id="R20",
            key="reg.xgb",
            family="regression",
            name="XGBRegressor",
            library="xgboost",
            estimator="xgboost.XGBRegressor",
            params=[
                _p("n_estimators", "int", 100, "xgb_trees", low=50, high=500),
                _p("learning_rate", "float", 0.1, "xgb_lr", low=0.01, high=0.3, log=True),
                _p("max_depth", "int", 6, "xgb_depth", low=2, high=12),
                rs,
            ],
            supports={"regression"},
            edu_key="reg.xgb",
            tags=["boosting"],
        ),
        AlgorithmSpec(
            id="R21",
            key="reg.lgbm",
            family="regression",
            name="LGBMRegressor",
            library="lightgbm",
            estimator="lightgbm.LGBMRegressor",
            params=[
                _p("n_estimators", "int", 100, "lgbm_trees", low=50, high=500),
                _p("learning_rate", "float", 0.1, "lgbm_lr", low=0.01, high=0.3, log=True),
                rs,
            ],
            supports={"regression"},
            edu_key="reg.lgbm",
            tags=["boosting"],
        ),
        AlgorithmSpec(
            id="C1",
            key="clf.logistic",
            family="classification",
            name="LogisticRegression",
            library="sklearn",
            estimator="sklearn.linear_model.LogisticRegression",
            params=[
                _p("C", "float", 1.0, "logreg_C", low=1e-3, high=100, log=True),
                _p("max_iter", "int", 500, "logreg_iter"),
                rs,
            ],
            supports={"binary", "multiclass"},
            needs_scaling=True,
            edu_key="clf.logistic",
            tags=["linear"],
        ),
        AlgorithmSpec(
            id="C10",
            key="clf.rf",
            family="classification",
            name="RandomForestClassifier",
            library="sklearn",
            estimator="sklearn.ensemble.RandomForestClassifier",
            params=[
                _p("n_estimators", "int", 100, "rf_trees", low=50, high=500),
                _p("max_depth", "int_or_none", None, "rf_depth"),
                _p("class_weight", "categorical", "balanced", "rf_cw", choices=["balanced", None]),
                rs,
            ],
            supports={"binary", "multiclass"},
            edu_key="clf.rf",
            tags=["tree"],
        ),
        AlgorithmSpec(
            id="C15",
            key="clf.histgbm",
            family="classification",
            name="HistGradientBoostingClassifier",
            library="sklearn",
            estimator="sklearn.ensemble.HistGradientBoostingClassifier",
            params=[_p("max_iter", "int", 100, "hgb_iter", low=50, high=500), rs],
            supports={"binary", "multiclass"},
            handles_missing=True,
            edu_key="clf.histgbm",
            tags=["boosting"],
        ),
        AlgorithmSpec(
            id="C20",
            key="clf.xgb",
            family="classification",
            name="XGBClassifier",
            library="xgboost",
            estimator="xgboost.XGBClassifier",
            params=[
                _p("n_estimators", "int", 100, "xgb_trees", low=50, high=500),
                _p("learning_rate", "float", 0.1, "xgb_lr", low=0.01, high=0.3, log=True),
                _p("max_depth", "int", 6, "xgb_depth", low=2, high=12),
                rs,
            ],
            supports={"binary", "multiclass"},
            edu_key="clf.xgb",
            tags=["boosting"],
        ),
        AlgorithmSpec(
            id="C21",
            key="clf.lgbm",
            family="classification",
            name="LGBMClassifier",
            library="lightgbm",
            estimator="lightgbm.LGBMClassifier",
            params=[
                _p("n_estimators", "int", 100, "lgbm_trees", low=50, high=500),
                _p("learning_rate", "float", 0.1, "lgbm_lr", low=0.01, high=0.3, log=True),
                _p(
                    "class_weight",
                    "categorical",
                    "balanced",
                    "lgbm_cw",
                    choices=["balanced", None],
                ),
                rs,
            ],
            supports={"binary", "multiclass"},
            edu_key="clf.lgbm",
            tags=["boosting"],
        ),
        AlgorithmSpec(
            id="C22",
            key="clf.catboost",
            family="classification",
            name="CatBoostClassifier",
            library="catboost",
            estimator="catboost.CatBoostClassifier",
            params=[
                _p("iterations", "int", 100, "cb_iter", low=50, high=500),
                _p("learning_rate", "float", 0.1, "cb_lr", low=0.01, high=0.3, log=True),
                _p("depth", "int", 6, "cb_depth", low=2, high=10),
                rs,
            ],
            supports={"binary", "multiclass"},
            edu_key="clf.catboost",
            tags=["boosting"],
        ),
        AlgorithmSpec(
            id="R30",
            key="reg.catboost",
            family="regression",
            name="CatBoostRegressor",
            library="catboost",
            estimator="catboost.CatBoostRegressor",
            params=[
                _p("iterations", "int", 100, "cb_iter", low=50, high=500),
                _p("learning_rate", "float", 0.1, "cb_lr", low=0.01, high=0.3, log=True),
                _p("depth", "int", 6, "cb_depth", low=2, high=10),
                rs,
            ],
            supports={"regression"},
            edu_key="reg.catboost",
            tags=["boosting"],
        ),
    ]
    return base + extra_algorithm_specs() + deep_algorithm_specs()


_DEEP_LIBRARIES = frozenset(
    {"pytorch-tabular", "pytorch-tcn", "torch", "tabpfn", "xlstm", "pytorch-forecasting"}
)


class DeepModelHandle:
    """Placeholder for DL specs — fitted via labcore.deep runners, not sklearn __init__."""

    def __init__(self, key: str, params: dict[str, Any]) -> None:
        self.key = key
        self.params = params

    def get_params(self, deep: bool = True) -> dict[str, Any]:  # noqa: ARG002
        return dict(self.params)


def build_estimator(spec: AlgorithmSpec, params: dict[str, Any] | None = None) -> Any:
    """Instantiate estimator from AlgorithmSpec (import string)."""
    import importlib

    defaults = {p.name: p.default for p in spec.params}
    if params:
        defaults.update(params)
    if spec.library in _DEEP_LIBRARIES or "deep" in spec.tags:
        return DeepModelHandle(spec.key, defaults)

    mod_name, _, cls_name = spec.estimator.rpartition(".")
    mod = importlib.import_module(mod_name)
    cls = getattr(mod, cls_name)
    # Drop None class_weight
    if defaults.get("class_weight") is None:
        defaults.pop("class_weight", None)
    # xgboost / lgbm verbosity
    if "xgboost" in spec.library:
        defaults.setdefault("verbosity", 0)
        defaults.setdefault("n_jobs", 1)
    if "lightgbm" in spec.library:
        defaults.setdefault("verbosity", -1)
        defaults.setdefault("n_jobs", 1)
    if "catboost" in spec.library:
        # CatBoost uses random_seed, not random_state
        if "random_state" in defaults:
            defaults["random_seed"] = defaults.pop("random_state")
        defaults.setdefault("verbose", False)
        defaults.setdefault("allow_writing_files", False)
        defaults.setdefault("thread_count", 1)
    if spec.key.startswith("clf.logistic"):
        defaults.setdefault("solver", "lbfgs")
    return cls(**defaults)
