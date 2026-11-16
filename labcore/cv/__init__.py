"""CV catalogue — sklearn schemes + purged / CPCV (ARCHITECTURE §13)."""

from labcore.cv.purged import CombinatorialPurgedKFold, PurgedKFold, ml_get_train_times
from labcore.cv.schemes import CV_SCHEME_IDS, build_splitter, list_cv_schemes, nested_default
from labcore.cv.visualise import plot_cv_folds

__all__ = [
    "CV_SCHEME_IDS",
    "CombinatorialPurgedKFold",
    "PurgedKFold",
    "build_splitter",
    "list_cv_schemes",
    "ml_get_train_times",
    "nested_default",
    "plot_cv_folds",
]
