"""Compile a recipe into an imblearn Pipeline (leakage-safe ColumnTransformer)."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict
from sklearn.compose import ColumnTransformer
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, RobustScaler, StandardScaler

ImputerKind = Literal["mean", "median", "most_frequent", "constant", "knn"]
ScalerKind = Literal["none", "standard", "robust", "minmax"]
EncoderKind = Literal["one_hot", "ordinal", "target"]
ResampleKind = Literal["none", "smote"]


class RecipeSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    numeric_imputer: ImputerKind = "median"
    categorical_imputer: ImputerKind = "most_frequent"
    categorical_encoder: EncoderKind = "one_hot"
    scaler: ScalerKind = "standard"
    drop_constant: bool = True
    resample: ResampleKind = "none"
    seed: int = 42
    # TargetEncoder cv folds (MI-02); used only when categorical_encoder=target
    target_encoder_cv: int = 5
    knn_n_neighbors: int = 5
    # Collapse rare categories before encoding (feature_engine RareLabelEncoder)
    rare_label_tol: float | None = None
    rare_label_n_categories: int | None = 10


def _split_columns(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    num, cat = [], []
    for c in X.columns:
        if pd.api.types.is_numeric_dtype(X[c]):
            num.append(c)
        else:
            cat.append(c)
    return num, cat


def drop_constant_columns(X: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    dropped: list[str] = []
    keep = []
    for c in X.columns:
        nuniq = X[c].nunique(dropna=True)
        if nuniq <= 1 or X[c].isna().all():
            dropped.append(c)
        else:
            keep.append(c)
    return X[keep].copy(), dropped


def compile_recipe(
    X: pd.DataFrame,
    recipe: RecipeSpec | None = None,
) -> tuple[Any, list[str], dict[str, Any]]:
    """Fit-ready pipeline (not fitted). Returns pipeline, feature columns, meta."""
    recipe = recipe or RecipeSpec()
    work = X.copy()
    dropped: list[str] = []
    if recipe.drop_constant:
        work, dropped = drop_constant_columns(work)
    num_cols, cat_cols = _split_columns(work)

    transformers: list[tuple[str, Any, list[str]]] = []
    if num_cols:
        if recipe.numeric_imputer == "knn":
            num_imputer: Any = KNNImputer(n_neighbors=int(recipe.knn_n_neighbors))
        else:
            num_imputer = SimpleImputer(strategy=recipe.numeric_imputer)
        num_steps: list[tuple[str, Any]] = [
            ("imputer", num_imputer),
        ]
        if recipe.scaler == "standard":
            num_steps.append(("scaler", StandardScaler()))
        elif recipe.scaler == "robust":
            num_steps.append(("scaler", RobustScaler()))
        elif recipe.scaler == "minmax":
            from sklearn.preprocessing import MinMaxScaler

            num_steps.append(("scaler", MinMaxScaler()))
        transformers.append(("num", Pipeline(num_steps), num_cols))

    if cat_cols:
        if recipe.categorical_encoder == "ordinal":
            enc: Any = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        elif recipe.categorical_encoder == "target":
            from sklearn.model_selection import KFold
            from sklearn.preprocessing import TargetEncoder

            enc = TargetEncoder(
                cv=KFold(
                    n_splits=recipe.target_encoder_cv,
                    shuffle=True,
                    random_state=recipe.seed,
                ),
                smooth="auto",
                target_type="auto",
            )
        else:
            enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        cat_steps: list[tuple[str, Any]] = [
            ("imputer", SimpleImputer(strategy=recipe.categorical_imputer)),
        ]
        if recipe.rare_label_tol is not None or recipe.rare_label_n_categories is not None:
            from feature_engine.encoding import RareLabelEncoder

            tol = float(recipe.rare_label_tol) if recipe.rare_label_tol is not None else 0.05
            cat_steps.append(
                (
                    "rare",
                    RareLabelEncoder(
                        tol=tol,
                        n_categories=int(recipe.rare_label_n_categories or 10),
                        replace_with="Rare",
                        missing_values="ignore",
                    ),
                )
            )
        cat_steps.append(("encoder", enc))
        cat_pipe = Pipeline(cat_steps)
        transformers.append(("cat", cat_pipe, cat_cols))

    pre = ColumnTransformer(transformers, remainder="drop")
    steps: list[tuple[str, Any]] = [("pre", pre)]
    if recipe.resample == "smote":
        from imblearn.over_sampling import SMOTE  # type: ignore[import-untyped]
        from imblearn.pipeline import Pipeline as ImbPipeline  # type: ignore[import-untyped]

        steps.append(("resample", SMOTE(random_state=recipe.seed)))
        pipe = ImbPipeline(steps)
    else:
        pipe = Pipeline(steps)
    meta = {
        "numeric_columns": num_cols,
        "categorical_columns": cat_cols,
        "dropped_constant": dropped,
        "recipe": recipe.model_dump(),
        "resample": recipe.resample,
    }
    return pipe, list(work.columns), meta
