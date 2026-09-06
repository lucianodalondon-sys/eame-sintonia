# VERDICT — "EVOLUÇÃO DE DOENÇAS" PILOT

Two pathosystem/region pairs were taken all the way through the same chain:
HISTORICAL RECONSTRUCTION → YEAR-BY-YEAR DATASET → BACKTEST → ANALOG YEARS → OUTLOOK.

## Summary

| | VITE × PERONOSPORA × VENETO | VITE × MILDIU × ANDALUCÍA |
|---|---|---|
| source | ARPAV *annate agrarie* | RAIF, Junta de Andalucía |
| outcome | prose adjectives | **`% cepas afectadas`, a number** |
| seasons found | 25 (26 documents) | **20** |
| Gate A | **DESCRIPTION_ONLY** (4 comparable) | outcome `BACKTEST_CANDIDATE_STRONG` (20) |
| backtest scoreable years | ~1 | **15** |
| `MODEL_HAS_SKILL` | not testable (no variance) | **NO** |
| why it stops | the outcome | **the horizon** |

## Veneto — `GATE_A_VERDICT = DESCRIPTION_ONLY`

The audit counted **`N_TRULY_COMPARABLE = 4`** of 25 seasons: **2009, 2016, 2021, 2025**.
Criterion: same construct, at least two of three scales agreeing on a level, and not flagged
as over-reach by any cross-check. The 14 seasons the evidence file flags as carrying explicit
severity reduce to 8 with an unconditional vine-hosted magnitude predicate — the ~1.4×
optimism predicted before the audit ran, confirmed and located.

**And the decisive finding is not the count. It is that the surviving column has no variance:
3 × LOW (2009, 2021, 2025) and 1 × MEDIUM (2016). Zero HIGH.** Even granting all four
seasons, there is nothing there to predict.

Four reasons the rest fall away, each verified rather than asserted:

1. **Assignability tracks authorship.** The co-authorship line *"Regione del Veneto, Settore
   Servizi Fitosanitari"* is absent from all 15 documents up to 2014 and present in all 11
   from 2015 — a perfect era split. Severity markers appear in 3 of 14 old documents against
   9 of 12 modern ones. The missing seasons are not missing at random.
2. **The top of every scale is a format artefact.** The only HIGH is 2002, the longest report
   in the corpus (32,553 chars, 4.5× the shortest), written month-by-month so the disease
   gets up to seven chances to trip an intensity word.
3. **The corpus falsifies the rescue rule at the one point it can be tested.** Exactly one
   season pairs scope language with a severity word: 2021, *"in tutti gli ambienti vitati,
   generalmente di **bassa** severità"*. Region-wide occurrence is compatible with the
   **lowest** band. Scope is not severity, and the source says so.
4. **Every severity sentence records disease after control**, across 25 years in which
   fungicide programmes changed enormously. The recent low end may be measuring modern spray
   schedules while the high end measures 2002's. No re-reading separates them.

Two corrections to my own instruments, found by the audit and recorded rather than buried:

- **My mechanical lexicon scan is not a usable floor.** Its failure mode is *polarity
  inversion* on exactly the sentences that matter: it matches `sever` inside
  *"generalmente di **bassa** severità"* and scores that season HIGH. Any cross-check that
  used it as a floor excluded 2021 — the corpus's single best-evidenced sentence — for a
  stemmer defect rather than for evidence.
- **My mechanical risk rule was under-inclusive.** It caught 2017 and nothing else. The
  audit found **thirteen risk-language instances across nine seasons**, four of which would
  flip a season's level. `RISK != PRESENCE` is a bigger contamination in this corpus than a
  single document.

Also settled: **ABOVE / NORMAL / BELOW is not constructible.** In 26 documents over 25
seasons, not one sentence compares vine peronospora to a norm, an average or a previous
year — ARPAV reserves that language for weather. `NORMAL` is an empty category.

**More ARPAV collection cannot fix any of this.** The route is exhausted: `bollettino-mese`
(264 documents, zero phytosanitary content — measured), `peronospora-vite` (VitiMeteo model
output = `MODELLED_RISK`), `agrometeoinforma` (no archive).

## Andalucía — the outcome is excellent, and the 12-month claim still fails

44,163 dated sampling rows parsed from the 171 MB RAIF export. 20 seasons, 374–3,727
observations each, as numbers.

**Validated twice, independently:**
- six provinces agree on which seasons were bad — all six pairs positive, mean ρ = +0.49,
  **permutation p = 0.0004**. Panel rotation (186 parcels → 18) cannot manufacture that.
- the index responds to rainfall exactly as downy-mildew epidemiology requires —
  ρ = +0.612, **p = 0.005** for season precipitation, five of seven weather features
  significant, all in the biologically correct direction.

**The backtest then returns NO.** 15 scoreable years under strict temporal validation:

```
BASELINE_CLIMATOLOGY   0.400
BASELINE_PERSISTENCE   0.267      <- no inoculum-carryover signal either
BASELINE_UNIFORM       0.333
best a-priori rule     0.400      permutation p = 0.244   -> ties, does not beat
OVERFIT_DEMONSTRATION  0.600      by choosing the feature after seeing the answers
```

`MODEL_HAS_SKILL = NO`, in both cutoff regimes, with `TARGET_SEASON_WEATHER_LEAKAGE = 0`
proved in code.

The ceiling probe settles **why**: a model allowed to cheat with the target season's own
weather reaches 0.55 (p = 0.040), while the honest antecedent model sits exactly at the
baseline. `PATHWAY_REAL_BUT_NOT_KNOWABLE_IN_ADVANCE` — nothing knowable before the season
starts carries information about how wet that season will be.

## What this means for the product

**A 12-month probabilistic peronospora outlook is not supported.** Not because the data are
poor — in Andalucía they are very good — but because the disease is driven by the season's
own rain, and the season's own rain is not forecastable a year ahead. That conclusion is
robust: it survived better data, more seasons, and a quantitative outcome.

The `OVERFIT_DEMONSTRATION` number is the one to remember: **0.60 accuracy is available to
anyone willing to pick the feature after seeing the answers.** A demo built that way would
look convincing and mean nothing.

**What the evidence does support:**
- an **auditable historical reconstruction** — the phase-segmented verbatim record all three
  run-A designers and the Gate A auditor independently converged on: one row per season, one
  cell per phase, each cell holding the literal Italian sentence and its dated period, with a
  hard rule that **a cell without its sentence is not published and is never filled by
  inference**;
- a statement of **what is and is not forecastable, with the measurement behind it**;
- the observation that the strong, real signal is **within-season**, which is what existing
  warning systems already serve.

Selling a 12M forecast on Monday would be selling a number this pilot has measured and
found absent.

## Discipline held

`sintonia/canonical` READ_ONLY and untouched. P0.2, meeting portal, Supabase, Passaporte,
Universal, motor-43 untouched. `MEETING_FREEZE` intact — this branch starts at the frozen
meeting head `5df09cb`, makes **zero deletions**, and every file it adds is under
`data/experiments/`. No credentials requested, none used, no authentication circumvented;
every source is open HTTP. No screen built, no portal integration.
