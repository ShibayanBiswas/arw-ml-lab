"""Target leakage via features — MI-15 (ARCHITECTURE §46.1, Intake §33.8)."""

from __future__ import annotations

MI15_RULE = "MI-15"
NEAR_PERFECT_CLF_ACC = 0.99
NEAR_PERFECT_REG_R2 = 0.98
TRANSFORM_IDENTITY_R2 = 0.999
POST_OUTCOME_RULE = "post_outcome_name"