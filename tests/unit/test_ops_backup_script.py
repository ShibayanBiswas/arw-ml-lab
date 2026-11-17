"""OPS.BACKUP.SCRIPT — oneshot-c221."""

from labcore.ops.backup_script_contract import assert_backup_script


def test_backup_contabo_script_covers_section_10() -> None:
    m = assert_backup_script()
    assert m["id"] == "OPS.BACKUP.SCRIPT"
