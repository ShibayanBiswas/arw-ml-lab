"""MC-dropout thin wrapper — oneshot-c260."""

from __future__ import annotations

import torch
from torch import nn

from labcore.uncertainty.mc_dropout import ARTEFACT_ID, mc_dropout_predict


class _Tiny(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.fc = nn.Linear(2, 1)
        self.drop = nn.Dropout(p=0.5)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # noqa: ANN401
        return self.fc(self.drop(x))


def test_mc_dropout_mean_std_shape() -> None:
    torch.manual_seed(42)
    m = _Tiny()
    x = torch.randn(4, 2)
    out = mc_dropout_predict(m, x, n_samples=20, seed=42)
    assert out["id"] == ARTEFACT_ID
    assert out["refit"] is False
    assert len(out["mean"]) == 4
    assert len(out["std"]) == 4
    # With dropout, std should be non-zero for at least some rows across samples
    assert any(s > 0 for row in out["std"] for s in (row if isinstance(row, list) else [row]))
