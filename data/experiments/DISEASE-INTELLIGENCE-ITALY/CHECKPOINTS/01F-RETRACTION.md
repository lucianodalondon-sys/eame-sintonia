# RETRACTION — the 31 May result does not survive its own red team

`CHECKPOINT 01F` claimed `FIRST_PROVED_CUTOFF = 31_MAY` (accuracy 0.733, p = 0.0019,
clearing Bonferroni). **That claim is withdrawn.** Ten adversaries, each reproducing against
the real data, and 41 agents in total, found a fatal defect in my own engine plus several
serious ones. Every one below was independently reproduced.

## The fatal defect: the feature was chosen using the answers

`horizon.py` picked `(feature, direction)` by `argmax` of accuracy **across all scored
years**, then reported that as out-of-sample skill. The prediction credited to 2012 was made
with a feature selected using 2013–2026 outcomes. A forecaster standing on 31 May 2012 could
not have known that `ytd_wet_spells_2d` would be the winner — it is 1 of 20, and the most
biologically obvious a-priori choice scores 0.533.

Nesting the selection inside the walk-forward — choosing the feature for year Y using only
years < Y — is the whole correction, and it is decisive:

| cutoff | ORACLE (as published) | **CAUSAL (honest)** | p | McNemar vs baseline |
|---|---|---|---|---|
| `PREV_SEASON_END` | 0.400 | 0.364 | 0.598 | 1.000 |
| `31_JAN` | 0.467 | 0.545 | 0.158 | 1.000 |
| `28_FEB` | 0.467 | 0.364 | 0.719 | 1.000 |
| `31_MAR` | 0.600 | 0.455 | 0.407 | 1.000 |
| `30_APR` | 0.600 | 0.455 | 0.361 | 1.000 |
| **`31_MAY`** | **0.733** | **0.545** | **0.188** | 1.000 |
| `30_JUN` | 0.667 | 0.636 | 0.063 | 0.688 |

```
FIRST_PROVED_CUTOFF = None      (every cutoff REFUTED)
12M_SKILL           = NO        (unchanged, and now on sounder ground)
```

## The other confirmed findings against me

- **The published p was wrong and seed-dependent.** Exact enumeration over all 630,630
  relabellings gives **p = 0.0023865**, not the printed 0.00195. Against a 0.0025 gate that
  is a 4.5 % margin, and the Monte Carlo's own noise is three times it: **roughly 40 % of RNG
  seeds print `NOT_PROVED` on identical data.** The verdict was decided by `seed=7`.
- **One vineyard decides it.** 2014 sits at 79/156 = 0.50641 against a training cut of
  0.5115. Move a single vineyard to 80/156 and `PROVED` disappears. **17 of 20 single-season
  deletions** collapse the verdict.
- **I changed a pre-registered rule after seeing the result.** I described `STRICT` as "the
  first rule I wrote". Git is more damning: `STRICT` was **committed at 69e1eae, before the
  weather data existed** — it was the pre-registration. A file written by the pre-change
  engine at 05:35:04 carries the identical 31 May row and reports `FIRST_PROVED_CUTOFF: null`;
  `horizon.py` was edited at 05:36:27. The same numbers were on disk labelled `None` before
  the edit and `31_MAY` after.
- **The direction search did undeclared work.** Locking direction to +1 as biology dictates
  collapses `PREV_SEASON_END` from 0.600 to 0.400 — *below* baseline. Three of seven
  `beats_baseline` rows existed only because "a wetter previous summer predicts *less*
  mildew" was allowed into the search.
- **Nothing ever compared the model to a baseline.** `beats_baseline` was a bare `>`. Exact
  McNemar against the best baseline: **p = 0.289**. The claim was 11/15 versus 8/15.
- **The Bonferroni denominator omitted the cutoff axis** (0.05/20 while `FIRST_PROVED_CUTOFF`
  is an argmin over 7 cutoffs). The corrected family is 70, threshold 0.000714.
- **My docstring lied.** It said "asserted, then re-proved independently". There was not one
  `assert` in the directory. There are now, and they fail loudly.

## The cross-country "replication" is also withdrawn

I reported that Toscana's 31 May "replicates" the Andalucía benchmark. The Andalucía horizon
curve **used the same oracle-selection procedure** — best-of-N features per issue date,
scored on all years. So the two results were not independent evidence converging; they were
**the same methodological error, made twice, agreeing with itself.** That is the opposite of
a replication and I should have seen it before writing it down.

## What SURVIVES, unaffected

The red team attacked these and did not break them. They do not depend on the horizon engine:

- **`TARGET_SEASON_WEATHER_LEAKAGE = 0`.** Instrumented and confirmed: latest contributing
  weather day minus cutoff is 0 at every in-season cutoff, −61 at `PREV_SEASON_END`. The
  winter clamp is load-bearing — removing it fires 20 violations, so the detector is not
  vacuous.
- **The outcome itself.** 20 seasons, 42,415 visits; provinces agree 36/36 (joint test
  p = 0.0012 on the reviewers' own recomputation); observer-independent (ρ = −0.011 with
  organisation count); defence regime explains 0.4–5 % of variance against the season's
  91–99 %.
- **`12M_SKILL = NO`** — strengthened, not weakened. Under honest selection the pre-season
  cutoffs score 0.364–0.545 against a 0.4667 baseline.
- **`PRODUCT_MUST_BE_REGIONAL = YES`** — Toscana and Abruzzo remain uncorrelated (ρ = +0.190).

## Standing conclusion

**A real, well-measured, regionally-coherent disease signal exists in Tuscan vineyards. No
horizon at which it becomes predictable from weather has been proved — not 12 months, not
pre-season, and not 31 May.** The honest product is historical and observational, not
predictive.

`horizon.py` is left in the tree unmodified as the record of what was wrong.
`horizon2.py` is the corrected engine.
