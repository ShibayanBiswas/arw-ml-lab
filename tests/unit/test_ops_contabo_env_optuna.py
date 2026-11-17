"""OPS.CONTABO.OPTUNA — oneshot-c231."""

from labcore.ops.contabo_env_optuna_contract import assert_contabo_env_optuna


def test_deploy_contabo_lists_optuna_and_healthcheck() -> None:
    m = assert_contabo_env_optuna()
    assert m["id"] == "OPS.CONTABO.OPTUNA"
