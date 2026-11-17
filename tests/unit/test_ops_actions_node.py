"""OPS.ACTIONS.NODE — oneshot-c224."""

from labcore.ops.actions_node_runtime_contract import assert_actions_node_contract


def test_workflows_bumped_off_node20_actions() -> None:
    m = assert_actions_node_contract()
    assert m["id"] == "OPS.ACTIONS.NODE"
