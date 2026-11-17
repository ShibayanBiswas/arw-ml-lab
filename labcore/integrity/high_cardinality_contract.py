"""High-cardinality categoricals — MI-10 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from labcore.integrity.high_cardinality_policy import (
    HIGH_CARD_ENCODER_PROPOSALS,
    HIGH_CARDINALITY_LEVELS,
    LAB_DEFAULT_SEED,
    MI10_RULE,
    ONE_HOT_MAX_LEVELS,
    is_high_cardinality,
    is_identifier_like_uniqueness,
    make_one_hot_encoder,
    n_levels,
    one_hot_output_within_cap,
    propose_categorical_encoders,
)
from labcore.predict.contract import assert_no_identifier_values, build_feature_contract, looks_identifier
from labcore.preprocess.recipe import RecipeSpec, compile_recipe

ARTEFACT_ID = "MI.HIGH.CARD"
STRESS_ID = "ST-ML-02"


class HighCardinalityContractError(ValueError):
    """Raised when MI-10 offline kit contract is violated."""


def assert_mi10_encoder_proposals_above_50(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-10: > 50 levels proposes target / hashing / count (not only one-hot)."""
    _ = seed
    proposals = propose_categorical_encoders(HIGH_CARDINALITY_LEVELS + 10)
    if proposals != list(HIGH_CARD_ENCODER_PROPOSALS):
        raise HighCardinalityContractError(
            f"MI-10: n>50 must propose {HIGH_CARD_ENCODER_PROPOSALS}, got {proposals}",
        )
    low = propose_categorical_encoders(20)
    if low != ["one_hot"]:
        raise HighCardinalityContractError("MI-10: n≤50 must default to one_hot proposal")
    return {
        "mi_rule": MI10_RULE,
        "n_levels_high": HIGH_CARDINALITY_LEVELS + 10,
        "proposals_high": proposals,
        "proposals_low": low,
        "seed": seed,
    }


def assert_mi10_onehot_capped_at_30(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-10: one-hot uses infrequent bucket when levels exceed 30."""
    rng = np.random.default_rng(seed)
    n_levels_fixture = ONE_HOT_MAX_LEVELS + 25
    cats = [f"L{i}" for i in range(n_levels_fixture)]
    weights = rng.uniform(size=n_levels_fixture)
    weights /= weights.sum()
    series = pd.Series(rng.choice(cats, size=400, p=weights))
    if n_levels(series) <= ONE_HOT_MAX_LEVELS:
        raise HighCardinalityContractError("MI-10: fixture must exceed 30 levels")
    enc = make_one_hot_encoder(n_levels(series), seed=seed)
    stats = one_hot_output_within_cap(enc, series)
    if not stats["within_cap"]:
        raise HighCardinalityContractError(
            f"MI-10: one-hot output {stats['n_output_features']} exceeds cap {ONE_HOT_MAX_LEVELS}",
        )
    plain = make_one_hot_encoder(10, seed=seed)
    narrow = pd.Series(["a", "b", "a", "c"])
    narrow_stats = one_hot_output_within_cap(plain, narrow)
    if narrow_stats["n_output_features"] != 3:
        raise HighCardinalityContractError("MI-10: low-cardinality one-hot must be exact levels")
    return {
        "mi_rule": MI10_RULE,
        "n_levels_fixture": int(stats["n_levels"]),
        "n_output_features": stats["n_output_features"],
        "seed": seed,
    }


def assert_mi10_identifier_excluded_by_default(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-10 / §45.2: identifier-like columns excluded; contract stores no cell values."""
    n = 100
    ids = [f"id-{i}" for i in range(n)]
    df = pd.DataFrame({"ticket_id": ids, "age": np.linspace(20, 60, n)})
    s = df["ticket_id"]
    if not is_identifier_like_uniqueness(s):
        raise HighCardinalityContractError("MI-10: ticket_id fixture must be identifier-like")
    if not looks_identifier("ticket_id", s):
        raise HighCardinalityContractError("MI-10: looks_identifier must flag ticket_id")
    contract = build_feature_contract(df, dataset_id="SYN", task="regression", target=None, seed=seed)
    assert_no_identifier_values(contract)
    id_feats = [f for f in contract["features"] if f.get("kind") == "identifier_like"]
    if not id_feats or id_feats[0].get("role") != "excluded_by_default":
        raise HighCardinalityContractError("MI-10: identifier_like must be excluded_by_default")
    return {
        "mi_rule": MI10_RULE,
        "identifier_column": "ticket_id",
        "n_identifier_features": len(id_feats),
        "seed": seed,
    }


def assert_mi10_high_card_flag_and_target_recipe(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-10: high-cardinality detected; ``compile_recipe`` supports target encoder wiring."""
    rng = np.random.default_rng(seed)
    cats = [f"C{i}" for i in range(60)]
    series = pd.Series(rng.choice(cats, size=200))
    if not is_high_cardinality(series):
        raise HighCardinalityContractError("MI-10: 60-level fixture must be high-cardinality")
    X = pd.DataFrame({"cat": series, "num": rng.normal(size=200)})
    pipe, _, meta = compile_recipe(X, RecipeSpec(categorical_encoder="target", seed=seed))
    steps = [name for name, _ in pipe.steps]
    if "pre" not in steps:
        raise HighCardinalityContractError("MI-10: recipe must compile pre step")
    return {
        "mi_rule": MI10_RULE,
        "n_levels": 60,
        "recipe_encoder": "target",
        "pipeline_steps": steps,
        "meta_drop_constant": bool(meta.get("dropped_constant")),
        "seed": seed,
    }


def assert_high_cardinality_contract(*, seed: int = LAB_DEFAULT_SEED) -> list[dict[str, object]]:
    return [
        assert_mi10_encoder_proposals_above_50(seed=seed),
        assert_mi10_onehot_capped_at_30(seed=seed),
        assert_mi10_identifier_excluded_by_default(seed=seed),
        assert_mi10_high_card_flag_and_target_recipe(seed=seed),
    ]


def high_cardinality_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    checks = assert_high_cardinality_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI10_RULE,
        "seed": seed,
        "checks": checks,
    }