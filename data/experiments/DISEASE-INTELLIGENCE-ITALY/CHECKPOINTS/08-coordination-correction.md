# CHECKPOINT 8 — COORDINATION CORRECTION (two corrections against my own record)

## Correction 1 — the local collection state was mislabelled

I wrote *"the local collection is NOT in the repository"* under a heading that read as a
verdict on existence. Absence from `origin` is not absence in the world. Corrected:

```
LOCAL_COLLECTION_BRANCH = claude/disease-local-collection-italy
LOCAL_COLLECTION_STATE  = RUNNING / LOCAL_ONLY_OR_HANDOFF_NOT_PUSHED
                          (NOT "DOES_NOT_EXIST")
```

The three negative searches remain valid **as searches of `origin`** and nothing more. The
branch is expected; it has not been pushed yet. I stop hunting for it in other branches.

## Correction 2 — I over-read an empty file into a project-wide limitation

This is the more serious one. I wrote that crop and target *"remain unverified"* and that
`CROP_MATCH = NOT_PROVED` was *"blocked by the label-uses REAL_GAP"*, citing
`FUNGICIDE-LABEL-USES.json` (empty, `STATE: REAL_GAP`) from
`claude/eame-competitor-public-communication`.

**That file proves only that one old branch lacked the reading. It does not prove the
project cannot verify Vite × Peronospora.** A different mission —
`claude/label-intelligence-v1-italy` @ `d08668c8` (2026-09-06) — carries a
`pilot-label-intelligence/` package whose structure I probed for shape only:

- `LAYER_OWNERSHIP` separating `REGISTRY` / `REGISTRY_HISTORY` / `LABEL_DOCUMENT` /
  `CROP_X_TARGET` / `DOSE`
- `TOTAL_USE_ROWS`, split into `USE_ROWS_FROM_TABLE_GEOMETRY` vs
  `USE_ROWS_FROM_TEXT_INFERENCE` — a provenance distinction that matters
- `IT-DOSES.json` with 163 `LABELS` entries carrying `REGISTRATION_ID`, `PRODUCT`,
  `PARSE_STATE`, and a `DOSE_RULE_VALIDATION` block reporting `CONTRADICTED` counts
- a presence probe finds peronospora and vite mentions in that package

**No value from that branch is consumed here, and none is treated as evidence.** Its
existence is enough to retract my over-reading. `CROP_MATCH` and `TARGET_MATCH` are
`NOT_PROVED` **in this mission because I have not received a handoff** — not because the
project lacks the capability.

## The two handoffs this mission is waiting for

They answer different questions and neither proves the other.

```
FIELD / DISEASE DATA  +  METEO / LEAF WETNESS  +  ADAMA REGULATORY LABEL
                              -> INTELLIGENCE RELATION
```

### A · COLLECTION HANDOFF — from `claude/disease-local-collection-italy`

Resolves the **epidemiological** hypothesis. Required per dataset:

| field | why |
|---|---|
| `SOURCE`, `AUTHORITY`, `REGION`, `STATION` | the geographic join must be defensible, and `PRODUCT_MUST_BE_REGIONAL = YES` |
| `VARIABLE`, `UNIT`, `TEMPORAL_RESOLUTION` | leaf wetness in hours/day is not leaf wetness in a class |
| `YEAR_RANGE`, `MISSINGNESS` | a gap is `NOT_KNOWN`, never zero |
| `OBSERVED_OR_MODELLED` | a modelled wetness estimate is a `PREDICTOR`, not ground truth |
| `RAW_PRESERVED`, `HASH` | so the recount can be reproduced |

Leaf wetness is classified `PREDICTOR`. It is never disease ground truth.

**It cannot reopen 12M.** Wetness observed *during* a season cannot improve a forecast issued
12 months earlier. `12M_SKILL = NO` stays closed unless a variable arrives that is genuinely
available *before* the 12-month cutoff.

### B · REGULATORY / LABEL HANDOFF — from `claude/label-intelligence-v1-italy`

Resolves the **regulatory/portfolio** context. One structured row per authorised use:

```
PRODUCT              =
REGISTRATION_ID      =
ACTIVE_INGREDIENTS   =
CROP                 =   must resolve to VITE
TARGET               =   must resolve to PERONOSPORA (Plasmopara viticola)
AUTHORIZED_USE_PROVED=   YES / NO / NOT_PROVED
SOURCE_PDF           =
SOURCE_HASH          =
EVIDENCE             =   page/table locator
PROOF_STATE          =
```

Additionally required, because that package already distinguishes them and the distinction is
load-bearing: whether each row came from **table geometry** or from **text inference**. A row
inferred from prose is weaker evidence than a row read from a label's use table, and the two
must not be merged.

The Label V1 UI is **not** an authority for this mission. Only a versioned structured artifact is.

## Promotion criteria — all five, or no promotion

```
ADAMA_PRODUCT_RELATION = PLAUSIBLE_NOT_PROVED     (unchanged)
```

Today this rests on `FIELD_ACTIVE_SUBSTANCE_OVERLAP` only — 8 of 28 observed actives, 55.6 %
of non-copper applications. That is not `PROVED_ADAMA_PRODUCT_USE`.

Promotion to `PROVED` requires **all five**:

1. an ADAMA substance/product proved;
2. the product registered in Italy;
3. **VITE** proved on the label;
4. **PERONOSPORA** proved as the target;
5. official evidence recoverable.

A lexical match is not proof of any of them.

## Frozen while waiting

```
FIRST_PROVED_CUTOFF       = NONE
12M_SKILL                 = NO
PREDICTIVE_HORIZON_PROVED = NO
PRODUCT_MUST_BE_REGIONAL  = YES
ADAMA_PRODUCT_RELATION    = PLAUSIBLE_NOT_PROVED
PORTAL_INTEGRATION        = NO
COMMERCIAL_CLAIM          = NONE
```
