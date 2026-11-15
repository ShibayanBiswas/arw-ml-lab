"""Deep-learning AlgorithmSpecs — T1/T3/T4 + Q2/Q7 + TabPFN/GPU stubs (thin)."""

from __future__ import annotations

from typing import Any

from labcore.registry.spec import AlgorithmSpec, ParamSpec


def _p(name: str, typ: str, default: Any, help_key: str, **kw: Any) -> ParamSpec:
    return ParamSpec(name=name, type=typ, default=default, help_key=help_key, **kw)  # type: ignore[arg-type]


def deep_algorithm_specs() -> list[AlgorithmSpec]:
    seed = _p("seed", "int", 42, "seed")
    lr = _p("learning_rate", "float", 1e-3, "dl_lr", low=1e-5, high=1e-2, log=True)
    return [
        AlgorithmSpec(
            id="T1",
            key="dl.mlp",
            family="classification",
            name="MLP (CategoryEmbedding)",
            library="pytorch-tabular",
            estimator="labcore.deep.tabular.fit_tabular",
            params=[
                _p("layers", "str", "64-32", "mlp_layers"),
                _p("activation", "categorical", "ReLU", "mlp_act", choices=["ReLU", "LeakyReLU"]),
                _p("dropout", "float", 0.1, "mlp_dropout", low=0.0, high=0.5),
                _p("use_batch_norm", "bool", True, "mlp_bn"),
                lr,
                seed,
            ],
            supports={"classification", "regression"},
            needs_scaling=True,
            edu_key="dl.mlp",
            tags=["deep", "tabular", "cpu"],
            resources={"gpu": False, "mem_gb": 2},
        ),
        AlgorithmSpec(
            id="T3",
            key="dl.tabnet",
            family="classification",
            name="TabNet",
            library="pytorch-tabular",
            estimator="labcore.deep.tabular.fit_tabular",
            params=[
                _p("n_d", "int", 8, "tabnet_nd", low=8, high=64),
                _p("n_a", "int", 8, "tabnet_na", low=8, high=64),
                _p("n_steps", "int", 3, "tabnet_steps", low=3, high=10),
                _p("gamma", "float", 1.3, "tabnet_gamma", low=1.0, high=2.0),
                _p(
                    "mask_type",
                    "categorical",
                    "sparsemax",
                    "tabnet_mask",
                    choices=["sparsemax", "entmax"],
                ),
                lr,
                seed,
            ],
            supports={"classification", "regression"},
            edu_key="dl.tabnet",
            tags=["deep", "tabular", "cpu"],
            resources={"gpu": False, "mem_gb": 2},
        ),
        AlgorithmSpec(
            id="T4",
            key="dl.ft_transformer",
            family="classification",
            name="FT-Transformer",
            library="pytorch-tabular",
            estimator="labcore.deep.tabular.fit_tabular",
            params=[
                _p("input_embed_dim", "int", 16, "ft_embed", low=8, high=64),
                _p("num_heads", "int", 2, "ft_heads", low=1, high=8),
                _p("num_attn_blocks", "int", 1, "ft_blocks", low=1, high=6),
                _p("attn_dropout", "float", 0.1, "ft_attn_drop", low=0.0, high=0.5),
                lr,
                seed,
            ],
            supports={"classification", "regression"},
            edu_key="dl.ftt",
            tags=["deep", "tabular", "cpu"],
            resources={"gpu": False, "mem_gb": 4},
        ),
        AlgorithmSpec(
            id="Q2",
            key="seq.lstm",
            family="sequential",
            name="LSTM",
            library="torch",
            estimator="labcore.deep.sequential.fit_sequential",
            params=[
                _p("lookback", "int", 16, "lstm_lookback", low=8, high=128),
                _p("horizon", "int", 1, "lstm_horizon", low=1, high=10),
                _p("hidden", "int", 32, "lstm_hidden", low=16, high=256),
                _p("layers", "int", 1, "lstm_layers", low=1, high=4),
                lr,
                seed,
            ],
            supports={"regression", "classification"},
            edu_key="seq.lstm",
            tags=["deep", "sequential", "cpu"],
            resources={"gpu": False, "mem_gb": 2},
        ),
        AlgorithmSpec(
            id="Q7",
            key="seq.tcn",
            family="sequential",
            name="TCN",
            library="pytorch-tcn",
            estimator="labcore.deep.sequential.fit_sequential",
            params=[
                _p("lookback", "int", 16, "tcn_lookback", low=8, high=128),
                _p("horizon", "int", 1, "tcn_horizon", low=1, high=10),
                _p("channels", "int", 32, "tcn_channels", low=16, high=128),
                _p("levels", "int", 2, "tcn_levels", low=2, high=8),
                _p("kernel", "int", 3, "tcn_kernel", choices=[2, 3, 5]),
                lr,
                seed,
            ],
            supports={"regression", "classification"},
            edu_key="seq.tcn",
            tags=["deep", "sequential", "cpu"],
            resources={"gpu": False, "mem_gb": 2},
        ),
        # Hidden unless TABPFN_ENABLED=true
        AlgorithmSpec(
            id="T13",
            key="dl.tabpfn",
            family="classification",
            name="TabPFN",
            library="tabpfn",
            estimator="labcore.deep.guards.tabpfn_enabled",
            params=[seed],
            supports={"classification"},
            max_rows_hint=10_000,
            edu_key="dl.tabpfn",
            tags=["deep", "foundation", "licence-gated"],
            resources={"gpu": True, "mem_gb": 8},
            enabled_env="TABPFN_ENABLED",
        ),
        # GPU-only stub for 422 routing (full xLSTM deferred to 2A-cont / optional-gpu)
        AlgorithmSpec(
            id="Q12",
            key="seq.xlstm",
            family="sequential",
            name="xLSTM (GPU)",
            library="xlstm",
            estimator="labcore.deep.guards.assert_gpu_allowed",
            params=[seed],
            supports={"regression"},
            edu_key="seq.xlstm",
            tags=["deep", "sequential", "gpu"],
            resources={"gpu": True, "mem_gb": 16},
        ),
    ]
