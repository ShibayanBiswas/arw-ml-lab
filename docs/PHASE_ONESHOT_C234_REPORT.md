# Phase oneshot-c234 — hosted frontend e2e smoke (Vercel)

## Built
- Re-ran `tests/e2e` (marker `e2e`) against `https://arw-ml-lab.vercel.app` while Contabo API remains blocked.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/e2e -q -m e2e --tb=line
..                                                                       [100%]
EXIT:0
```

## Contabo
Still blocked — no `CONTABO_HOST` / NVIDIA / Supabase migrate secrets; Actions billing still failing CI/Deploy.
