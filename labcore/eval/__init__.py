"""Evaluation suites — ARCHITECTURE §41 / §42 (library-backed)."""

from labcore.eval.classification.suite import run_classification_eval
from labcore.eval.regression.suite import run_regression_eval

__all__ = ["run_classification_eval", "run_regression_eval"]
