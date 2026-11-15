"""AC: rule engine flags Titanic Age ~19.9% and Cabin ~77%."""

from __future__ import annotations

from labcore.data.samples import load_sample_frame
from labcore.insights.rules import run_eda_rules


def test_titanic_missingness_rules() -> None:
    df, task, schema = load_sample_frame("DS3")
    insights = run_eda_rules(df, schema, task)
    age = next(i for i in insights if i.column == "Age" and i.rule_id.startswith("missing."))
    assert age.value is not None
    assert 19.0 <= age.value <= 21.0
    cabin = next(i for i in insights if i.column == "Cabin" and i.rule_id == "missing.high")
    assert cabin.value is not None
    assert 75.0 <= cabin.value <= 80.0
