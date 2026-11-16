"""Unsupervised learning thin wrappers (ARCHITECTURE §18)."""

from labcore.unsupervised.anomaly import fit_anomaly
from labcore.unsupervised.clustering import fit_clustering
from labcore.unsupervised.dr import fit_dr

__all__ = ["fit_clustering", "fit_dr", "fit_anomaly"]
