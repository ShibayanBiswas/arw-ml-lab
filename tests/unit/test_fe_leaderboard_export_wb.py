"""Train workbench wires REP.T.LEADERBOARD downloads (oneshot-c183 / ST-UX-02)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "frontend" / "src" / "components" / "train" / "TrainWorkbench.tsx"
API = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_train_workbench_leaderboard_download_buttons() -> None:
    src = WB.read_text(encoding="utf-8")
    assert "downloadExperimentLeaderboard" in src
    assert 'data-artefact="REP.T.LEADERBOARD"' in src
    assert 'downloadExperimentLeaderboard(expId, "csv")' in src
    assert 'downloadExperimentLeaderboard(expId, "xlsx")' in src


def test_api_exports_leaderboard_download_client() -> None:
    api = API.read_text(encoding="utf-8")
    assert "experimentLeaderboardCsvPath" in api
    assert "experimentLeaderboardXlsxPath" in api
    assert "downloadExperimentLeaderboard" in api
    assert "/leaderboard.csv" in api
    assert "/leaderboard.xlsx" in api
