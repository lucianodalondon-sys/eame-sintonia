# PILOT — DISEASE EVOLUTION: VITE x PERONOSPORA x VENETO

**ISOLATION.** This directory is a sealed pilot. It does not read from, write to, or
depend on: `sintonia/canonical` (READ_ONLY, untouched), P0.2, the meeting portal,
Supabase, Passaporte, Universal, the 43-opportunity engine, or any branch in integration.
Nothing here is wired into any surface.

**BRANCH.** `claude/pilot-disease-evolution-vite-veneto`

## What this pilot is trying to prove

Not a 7-day spray warning. That already exists and is not what was asked for.

- **12M = NEXT-SEASON PROBABILISTIC OUTLOOK** — before the season starts, is the coming
  season more or less likely than usual to be a hard peronospora year?
- **24M = STRATEGIC RISK SCENARIO** — not a forecast, a scenario.

The chain is: HISTORICAL RECONSTRUCTION -> YEAR-BY-YEAR DATASET -> BACKTEST ->
ANALOG YEARS -> OUTLOOK. If the backtest fails, the chain stops there and we say so.

## Laws enforced

| law | where it is enforced |
|---|---|
| `RISK_FORECAST != DISEASE_PRESENCE` | evidence roles below; no bulletin is coded as an outcome |
| `SPREAD_FORECAST = NOT_PROVED` | nothing in this pilot claims spread |
| `TARGET_SEASON_WEATHER_LEAKAGE = FORBIDDEN` | `MODELS/build_features.py::assert_no_leakage`, re-proved independently of the builder |
| baseline before model | `MODELS/backtest.py::baselines`, run first; model must beat all of them |
| training only on years < Y | `MODELS/backtest.py::strict_temporal` is primary; LOYO reported only as optimistic bound |
| never invent a percentage | ordinal scales only, each with an explicit auditable marker-word table |
| no credentials, no auth bypass | every source here is open HTTP; blocked routes are classified, not circumvented |

## Evidence roles

- `OFFICIAL_OBSERVATION` — ARPAV *Andamento dell'annata agraria*, 12 PDFs 2014-2025.
  Region-wide prose narrative, written after the season. This is the only outcome source.
- `MODELLED_RISK` — none used. Deliberately.
- `FIELD_REPORTED` — none available.
- `SCENARIO` — the 24M product, when and if it exists.
- `NOT_KNOWN` — every year without an explicit severity statement. Silence is recorded as
  silence, never as "mild".

## Layout

```
RAW/          12 ARPAV annata-agraria PDFs, SHA256 in EVIDENCE/MANIFEST.json
NORMALIZED/   text extracted via pdfjs-dist
OBSERVATIONS/ verified per-year outcome quotes + the elected ordinal scale
WEATHER/      ERA5 1990-01-01..2025-12-31, 13149 days x 5 vars x 5 vine points
MODELS/       build_features.py (cutoff-respecting), backtest.py (hostile harness)
BACKTEST/     backtest_report.json
EVIDENCE/     MANIFEST.json, GEOGRAPHY_JOIN.md, gate decisions
PACKAGE/      demo package, only if the gates pass
```

## Gate A (not relaxable)

Comparable seasons available for the outcome:

| comparable seasons | verdict |
|---|---|
| >= 8 | `BACKTEST_CANDIDATE_STRONG` |
| 6-7 | `DEMO_ONLY` |
| 3-5 | `DESCRIPTION_ONLY` |
| < 3 | `NOT_USABLE_FOR_12M_OUTLOOK` |

"Has a PDF" is not a comparable season. "Mentions peronospora" is not a comparable season.

## Known circularity risk — declared up front

The ARPAV reports *explain* infections by the rain that caused them. If the season
severity class is largely a restatement of that same rainfall, then predicting the class
from ERA5 rainfall proves nothing. This is why the predictors are restricted to
**previous-season, autumn and winter** blocks and never to the target season itself: the
cutoff is what separates a real antecedent signal from a circular one.
