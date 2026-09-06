# CHECKPOINT 6 — LOCAL COLLECTION RECONCILIATION

## A · The local collection is NOT in the repository

The mission states the local collection finished. **It is not on origin, and I will not
invent it.** Three independent searches, all negative:

| search | result |
|---|---|
| branch `claude/disease-local-collection-italy` on origin | **ABSENT** |
| `LOCAL-DISEASE-COLLECTION-HANDOFF.md` across **every** remote branch | **ABSENT** |
| any file matching `bagnatur` / `leaf.?wet` / `stazion` across **every** remote branch | **ABSENT** |

The branches pushed on 2026-09-06 are `disease-intelligence-italy-overnight` (mine),
`label-intelligence-v1-italy`, `sintonia/canonical`, `pilot-disease-evolution-vite-veneto`,
`salvaguarda/*` — none is a disease collection. The only other `HANDOFF` files on any branch
belong to unrelated ADAMA catalogue missions.

```
LOCAL_COLLECTION_HEAD      = NOT_FOUND
HANDOFF_PATH               = NOT_FOUND
HANDOFF_HASH               = NOT_APPLICABLE
READY_FOR_INTELLIGENCE     = NO
LOCAL_COLLECTION_RECEIVED  = NO
LOCAL_COLLECTION_RECONCILED = NO
```

**This is a negative finding with proof, not a collection failure on my side.** Either the
work has not been pushed, or it landed under a name none of these three searches reaches. It
cannot be consumed until it exists.

Everything that depended on it is therefore blocked, and named:

```
LEAF_WETNESS_STATIONS     = NOT_RECEIVED
LEAF_WETNESS_YEARS        = NOT_RECEIVED
LEAF_WETNESS_DAILY_ROWS   = NOT_RECEIVED
LEAF_WETNESS_INCREMENTAL_VALUE = NOT_TESTABLE — the variable was never received
```

`NOT_TESTABLE` is not `NO`. The question remains open and worth answering when the data
arrives.

## B · What I did instead of stalling

Three of the four horizons the mission asks for do **not** need leaf wetness. Tuscan
observations are weekly per vineyard, so *"given the season up to week W, what does week
W+k look like?"* is answerable from data already collected. All four were tested.

### The mandatory persistence baseline, made deliberately strong

For a k-week-ahead warning the null hypothesis is **"nothing changes"** — a grower already
knows what their vineyard looked like last week. A warning product must beat that.

### Target = RISE (does incidence increase more than the training-median rise?)

Nested temporal validation: for test season Y, training seasons are strictly < Y; the rule,
its thresholds and the rise threshold are all fitted on training seasons only.

| horizon | pairs | seasons | model | persistence | majority | model wins | sign-test p | state |
|---|---|---|---|---|---|---|---|---|
| **7D** | 284 | 16 | 0.576 | 0.556 | 0.444 | 5/16 | 0.910 | `NOT_PROVED` |
| **14D** | 278 | 16 | 0.535 | 0.533 | 0.467 | 4/16 | 0.989 | `NOT_PROVED` |
| **21D** | 269 | 16 | 0.577 | 0.503 | 0.497 | 4/16 | 0.989 | `NOT_PROVED` |
| **30D** | 255 | 16 | 0.530 | 0.494 | 0.506 | 4/16 | 0.982 | `NOT_PROVED` |

**The model loses more often than it wins** — 4 to 5 seasons out of 16. The mean-accuracy
edge over persistence (0.02–0.07) is an artefact of averaging, and the sign test across
seasons destroys it.

### Target = LEVEL — and this shows exactly why

| horizon | MAE persistence | MAE week-climatology |
|---|---|---|
| 7D | **0.0466** | 0.1291 |
| 14D | **0.0703** | 0.1438 |
| 21D | **0.0884** | 0.1525 |
| 30D | **0.1133** | 0.1688 |

Persistence beats week-climatology at every horizon by roughly 3× at 7 days. The *level* of
disease is almost entirely "whatever it was last week". Persistence error grows steadily with
horizon (0.047 → 0.113), so the season genuinely does evolve — **but nothing available
predicts that evolution.**

## C · The 12-month question stays closed

Leaf wetness observed *during* a season cannot improve a forecast issued 12 months earlier,
and no variable available before a 12-month cutoff arrived. Per the mission's own rule:

```
12M_SKILL = NO   (unchanged, unreopened)
```

## D · Geography — unchanged and unchallenged

```
PREDICTOR_GEOGRAPHY = 8 reanalysis points inside named Tuscan provinces (MERRA-2, not ERA5)
OUTCOME_GEOGRAPHY   = vineyard -> comune (ISTAT) -> province -> Toscana
JOIN_METHOD         = regional mean of predictor points -> regional outcome
JOIN_LIMITATION     = PRODUCT_MUST_BE_REGIONAL. Toscana and Abruzzo do not co-move
                      (rho = +0.190, p = 0.67). No Italy-wide aggregate is permitted.
```

## E · Module states

```
HISTORICAL_INTELLIGENCE  = PROVED
EVOLUTION_MONITOR        = PROVED (as an observational record, not a model)
CURRENT_PRESSURE_MONITOR = PROVED (it is a measurement, not a prediction)
EARLY_WARNING_7D         = NOT_PROVED
EARLY_WARNING_14D        = NOT_PROVED
EARLY_WARNING_21D        = NOT_PROVED
EARLY_WARNING_30D        = NOT_PROVED
PRE_SEASON_OUTLOOK       = NOT_PROVED
12M_OUTLOOK              = NO
PREDICTIVE_HORIZON_PROVED = NO
```

The retraction stands untouched: `FIRST_PROVED_CUTOFF = NONE`. Nothing here rehabilitates
the withdrawn 31 May result, and nothing was tested that could have.
