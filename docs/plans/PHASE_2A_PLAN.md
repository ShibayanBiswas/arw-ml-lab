# Phase 2A — Deep Learning thin smoke + deploy sync

Approved plan: `phase_2a_dl_thin_d6951192` (thin slice; full §34 deferred to 2A-cont).

## Locked decisions

1. **Thin before full §34:** Lightning engine + pytorch-tabular for **T1 MLP / T3 TabNet / T4 FT-Transformer**, plus **Q2 LSTM / Q7 TCN** window smokes. Full T*/Q* matrix, DL.P catalogue, MC-dropout/ensembles → 2A-cont.
2. **Libraries only (rule 70):** pytorch-tabular configs, Lightning Trainer + EarlyStopping + Tuner LR finder, `torch.nn.LSTM`, `pytorch-tcn.TCN`. No from-scratch estimators.
3. **TabPFN:** hidden unless `TABPFN_ENABLED=true` (licence). Spec registered but filtered from `GET /catalog`.
4. **GPU:** models tagged `resources.gpu=true` refuse with HTTP 422 when no GPU worker is registered; thin CPU smokes use AdamW defaults on CPU.
5. **Deploy sync (ADR-0006):** after green commit, push `origin/main` and confirm Vercel READY.

## Workstreams

0. Plan + ADR-0009 + PROGRESS  
1. `labcore/deep/` engine + registry specs + catalogue wire  
2. DS3/DS12/DS30 smokes, LR finder, early-stop, TabPFN/GPU guards, tests  
3. Report, commit `phase 2a: dl thin smoke`, push, Vercel READY, STOP

## Acceptance (thin)

- [ ] T1/T3/T4 instantiate with defaults; Quick smoke on DS3 (clf) and DS12 (reg) on CPU  
- [ ] Q2 LSTM + Q7 TCN on windowed DS30; purge/embargo window test (no label-horizon overlap)  
- [ ] LR finder returns suggested LR + numbers; early stopping restores best epoch  
- [ ] TabPFN absent from catalog when disabled; GPU-only request → HTTP 422  
- [ ] Commit + push + Vercel READY
