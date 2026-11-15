"""CV scheme registry — sklearn only (ARCHITECTURE §13.1 subset)."""

from __future__ import annotations

from typing import Any, Literal

from sklearn.model_selection import (
    GroupKFold,
    KFold,
    LeaveOneOut,
    RepeatedKFold,
    RepeatedStratifiedKFold,
    ShuffleSplit,
    StratifiedKFold,
    StratifiedShuffleSplit,
    TimeSeriesSplit,
)

CVScheme = Literal[
    "holdout",
    "kfold",
    "stratified_kfold",
    "repeated_kfold",
    "repeated_stratified_kfold",
    "group_kfold",
    "shuffle_split",
    "stratified_shuffle_split",
    "time_series_split",
    "leave_one_out",
    "nested",
]

CV_SCHEME_IDS: list[str] = [
    "holdout",
    "kfold",
    "stratified_kfold",
    "repeated_kfold",
    "repeated_stratified_kfold",
    "group_kfold",
    "shuffle_split",
    "stratified_shuffle_split",
    "time_series_split",
    "leave_one_out",
    "nested",
]


def list_cv_schemes() -> list[dict[str, str]]:
    names = {
        "holdout": "Hold-out",
        "kfold": "KFold",
        "stratified_kfold": "StratifiedKFold",
        "repeated_kfold": "RepeatedKFold",
        "repeated_stratified_kfold": "RepeatedStratifiedKFold",
        "group_kfold": "GroupKFold",
        "shuffle_split": "ShuffleSplit",
        "stratified_shuffle_split": "StratifiedShuffleSplit",
        "time_series_split": "TimeSeriesSplit",
        "leave_one_out": "LeaveOneOut",
        "nested": "Nested CV (outer)",
    }
    return [{"id": k, "name": names[k]} for k in CV_SCHEME_IDS]


def nested_default(n_train: int) -> bool:
    """MI-03: nested CV on by default for n < 2000."""
    return n_train < 2000


def build_splitter(
    scheme: str,
    *,
    n_splits: int = 5,
    seed: int = 42,
    task: str = "binary",
    n_repeats: int = 2,
) -> Any:
    """Return a sklearn splitter (or None for holdout — caller uses train_test_split)."""
    key = scheme.lower()
    if key in ("holdout",):
        return None
    if key in ("nested",):
        # Outer splitter; inner handled by tune
        key = "stratified_kfold" if task != "regression" else "kfold"
    if key == "kfold":
        return KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    if key == "stratified_kfold":
        return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    if key == "repeated_kfold":
        return RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)
    if key == "repeated_stratified_kfold":
        return RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)
    if key == "group_kfold":
        return GroupKFold(n_splits=n_splits)
    if key == "shuffle_split":
        return ShuffleSplit(n_splits=n_splits, test_size=0.2, random_state=seed)
    if key == "stratified_shuffle_split":
        return StratifiedShuffleSplit(n_splits=n_splits, test_size=0.2, random_state=seed)
    if key == "time_series_split":
        return TimeSeriesSplit(n_splits=n_splits)
    if key == "leave_one_out":
        return LeaveOneOut()
    raise ValueError(f"unknown cv scheme: {scheme}")


def default_scheme_for_task(task: str) -> str:
    return "stratified_kfold" if task != "regression" else "kfold"
