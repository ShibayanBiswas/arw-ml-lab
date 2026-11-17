"""OPS.DEPLOY.BACKUP_SCP — oneshot-c223."""

from labcore.ops.deploy_backup_scp_contract import assert_deploy_workflow_scps_backup


def test_deploy_scps_backup_script() -> None:
    m = assert_deploy_workflow_scps_backup()
    assert m["id"] == "OPS.DEPLOY.BACKUP_SCP"
