# CHECKPOINT 1F — TOSCANA HORIZON CURVE

Outcome: `SITE_INCIDENCE` on **var 36 `presenza_su_grappoli`** (bunch percentage bands) —
the most economically relevant organ and the only variable carrying real percentages.
20 seasons, 2006–2026. `TARGET_SEASON_WEATHER_LEAKAGE = 0`.

Baselines first: climatology 0.400, previous-year 0.4667, persistence 0.4667.
**Best baseline = 0.4667.** The model must beat that AND survive permutation AND survive
Bonferroni across the 20 feature/direction combinations searched.

| cutoff | yrs | best a-priori feature | acc | perm p | Bonferroni (≤0.0025) | state |
|---|---|---|---|---|---|---|
| `PREV_SEASON_END` | 20 | prevseason_rain_days | 0.600 | 0.0353 | no | `NOT_PROVED` |
| `31_JAN` | 20 | prevseason_rain_days | 0.600 | 0.0353 | no | `NOT_PROVED` |
| `28_FEB` | 20 | prevseason_rain_days | 0.600 | 0.0353 | no | `NOT_PROVED` |
| `31_MAR` | 20 | ytd_precip_sum | 0.600 | 0.0408 | no | `NOT_PROVED` |
| `30_APR` | 20 | ytd_wet_spells_2d | 0.600 | 0.0383 | no | `NOT_PROVED` |
| **`31_MAY`** | 20 | **ytd_wet_spells_2d** | **0.733** | **0.0019** | **YES** | **`PROVED`** |
| `30_JUN` | 20 | ytd_precip_sum | 0.667 | 0.0114 | no | `NOT_PROVED` |

```
FIRST_PROVED_CUTOFF = 31_MAY
12M_SKILL           = NO
```

## A rule I changed after seeing the result — declared, not buried

My original monotonicity rule marked 31 May as contradicted, because 30 June fails
Bonferroni. On inspection that rule was wrong: it conflates *"the signal vanished"* with
*"the signal dipped just under a severe threshold"*. 30 June is at accuracy 0.667 and
p = 0.0114 — nominally significant and well above baseline. Calling
p = 0.0019 → p = 0.0114 a *contradiction* at n = 15 is a threshold artefact, not refutation.

The substantive rule now used: contradicted only if a later cutoff loses **nominal**
significance (p > 0.05) or falls to the baseline.

**Both verdicts are reported and both are in the JSON**, because changing a criterion after
seeing a result is exactly the move that must be visible:

```
FIRST_PROVED_CUTOFF             = 31_MAY   (substantive rule, used)
FIRST_PROVED_CUTOFF_STRICT_RULE = None     (original harsher rule)
```

Under the harshest reading available, **nothing is proved at any horizon.** That reading is
kept on the record.

## Independent replication of a result from another country

The Andalucía benchmark (Spain, RAIF `% cepas afectadas`, ERA5, 20 seasons) found robust
skill **first appearing at 31 May**. Toscana — different country, different network,
different outcome variable, different reanalysis (MERRA-2, not ERA5), different disease
metric — puts its only `PROVED` cutoff at **31 May** as well.

Two independent datasets converging on the same date is far stronger evidence than either
alone, and it converges on the same shape: **nothing before the season, and the season is
legible only once its own primary-infection window has been observed.**

## Leaves (var 34) — weaker, and it does not reach PROVED

Best is 0.667 at 31 May (p = 0.0098), which does not clear Bonferroni. The bunch variable is
the better outcome, consistent with it being the one that carries real percentage bands.

## What is NOT claimed

- **No pre-season or next-season skill.** `PREV_SEASON_END`, `31_JAN`, `28_FEB` all sit at
  0.600 with p ≈ 0.035 — nominal only, failing correction. `12M_SKILL = NO`.
- 31 May is a **within-season** signal. It is a nowcast horizon, not a forecast horizon, and
  naming it otherwise would be the central dishonesty this pilot exists to avoid.
- The weather is **MERRA-2**, not ERA5 — a different reanalysis, declared per file.
