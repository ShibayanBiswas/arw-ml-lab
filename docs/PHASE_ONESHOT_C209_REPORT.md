# Phase oneshot-c209 — EDU.ATLAS.COVERAGE

## Built
- `labcore/education/atlas_coverage.py` — floor on Logic Atlas entries + math field presence.
- Unit tests.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_edu_atlas_coverage.py -v --tb=short
============================== 2 passed in 1.27s ==============================
```

## Deviations
Does not yet map every registry algorithm key → explanation (follow-up when catalogue education pack lands).

## TODOs
Expand atlas to full registry key set; fail CI on missing algorithm education.
