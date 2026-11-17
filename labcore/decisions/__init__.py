"""VLM decision agent guards (ARCHITECTURE §38)."""

from labcore.decisions.baseline import rule_baseline_proposal
from labcore.decisions.guards import apply_deterministic_guards

__all__ = ["apply_deterministic_guards", "rule_baseline_proposal"]
