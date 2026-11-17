"""pred_threshold from feature contract — oneshot-c256."""

from labcore.predict.threshold_label import pred_threshold_from_contract


def test_pred_threshold_from_contract() -> None:
    assert pred_threshold_from_contract({"pred_threshold": 0.42}) == 0.42
    assert pred_threshold_from_contract({"uncertainty": {"pred_threshold": 0.7}}) == 0.7
    assert pred_threshold_from_contract({}) is None
