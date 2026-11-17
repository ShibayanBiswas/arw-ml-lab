# Phase oneshot-c210 — EDA numbers-only insight button

## Built
- `RuleInsightsPanel` calls `runInsights` (prefer_mock / numbers-only) with FACTS derived from rule alert values.
- `data-artefact="AI.NUMBERS.ONLY"` on the panel.

## Tests
FE-only; backend numbers-only contracts green in c200.

## Deviations
Needs live lab-api for browser prove (Contabo blocked).
