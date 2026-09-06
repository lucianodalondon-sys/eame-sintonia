# CHECKPOINT 11 — DOES THE CAPABILITY DESERVE A FUTURE PLACE IN SINTONIA?

`PORTAL_INTEGRATION = NO` · no portal branch touched · no screen built · production untouched.

---

## FASE 1 — THE TWO ELECTED CASES

Elected from the existing acervo (`CENSUS/italy_census.json`, 25 Italian candidates already
ranked). **No new collection was needed to decide**, so none was opened.

| | CASE B (PEST) | CASE C (2nd DISEASE) |
|---|---|---|
| object | OLIVO × *Bactrocera oleae* × Toscana | VITE × Oidio × Toscana |
| crop / schema / var | 2 / 1 / −1002 "Infestazione Dannosa" | 3 / 8 / 39 "Presenza su foglie" |
| outcome observed | YES — destructive sample, 100 olives/visit | YES — ordinal presence scale |
| seasons | **20 complete + 2026 in progress** (see C7) | 20 (2006–2026, 2011 empty) |
| visits | 79 251, of which 2 928 in the unfinished 2026 | 35 065, of which **96.9 % are the same visit as a calibration-case observation** (see C2) |
| provinces | 9–10 | 9–10 |
| value mode | NUMERIC (`widget: numeric`) | ORDINAL (code table) |

Why these two and not others: the pest case is the only Italian candidate with a **true rate over
a known denominator**; the second disease case shares crop and region with the calibration case,
which isolates *issue* as the only variable that differs. That is the cleanest possible
generalization test **across issue** — and, as the red team established (C2, C3), it is *not* a
test across geography, and the vine cases share 96.9 % of their visits.

---

## FASE 2 — REUSE MEASURED, NOT CLAIMED

The same `collect_generic.py` → `run_case.py` → `province_agreement.py` → `current_pressure.py`
path ran all three cases. Reuse is measured by counting case-specific logic in the code:

```
case-conditional branches in the pipeline .......... 0   (grep -cE "if .*(TOSCANA|OIDIO|BACTROCERA|...)")
case names in executable lines ..................... 2   (the region's API base URL; the __main__ case list)
                                                          neither is a rule — one is a per-region
                                                          constant, the other is an argument
total pipeline code lines .......................... 776
```

```
CASES_TESTED ............................. 4  (see C20-C24: a 4th, genuinely unseen case was
                                              collected live and it BROKE the pipeline in four
                                              places before the fixes)
CASES_PASS_WITH_NO_RULE_CHANGE ........... 3  over 2 INDEPENDENT PANELS (see C2)
CASES_NEEDING_A_GENERIC_RULE_EXTENSION ... 1
PIPELINE_REUSE_RATE ...................... 3/4 = 75%   (100% was WRONG)
```

The ordinal scale is derived from the source's own code table by **label text**, surviving both
traps already met in this project: `order_n` is unreliable (media ranks below bassa) and the code
number is unreliable (50 = media, 51 = bassa). 5/5 code tables derived with no per-case rule,
including the band-vocabulary difference (`>15%` for peronospora bunch vs `>10%` for oidio).

**One defect, self-caught.** The first run of `current_pressure.py` returned UNKNOWN for every
province of the pest case, because it did not inherit `run_case.py`'s numeric fallback. The fix
is generic and reads the source's own metadata (`widget: numeric` → NUMERIC, code table →
ORDINAL, anything else → REFUSED), so it stays at zero case-specific rules. It is recorded here
because of *how* it failed: **loudly to UNKNOWN, never silently to zero.** That is the design
working, and it is the single most important behaviour in the whole module.

Internal consistency (province agreement, generic test, within-province year-shuffle permutation):

| case | positive pairs | mean ρ | p |
|---|---|---|---|
| BACTROCERA | 36/36 | +0.770 | 0.00033 |
| PERONOSPORA (calibration) | 36/36 | +0.622 | 0.00033 |
| OIDIO | 27/36 (**9 non-positive**, corrected — see C1) | +0.245 | 0.00067 |

**These are the mean-of-site-max metric. On `INCIDENCE`, the metric actually published, the
numbers are BACTROCERA ρ +0.449 and OIDIO ρ +0.229 (C9).** The claim that the pest case is
"stronger than the calibration case" is withdrawn — it compared different metrics.

**And OIDIO's agreement is withdrawn as evidence entirely (C11):** survey *effort* agrees across
its provinces at ρ +0.738 while the disease agrees at only +0.229, so its consistency is the
monitoring programme's, not the biology's. For BACTROCERA the disease (+0.449) exceeds effort
(+0.252), and it survives.

Leave-shared-organisation-out, because the old independence warrant was false (C4):
BACTROCERA drop `ota`+`aprol` → 36/36 ρ +0.731; OIDIO drop `unipi` → 6/6 ρ +0.537.

---

## FASE 4 — `CURRENT_PRESSURE`, THE EXACT DEFINITION

Pre-registered in the module docstring before any output was read
(`ENGINE/current_pressure.py`).

```
INPUTS            official field-scouting visits only. One row = one visit to one monitored
                  field on one date. EvidenceRole = OFFICIAL_OBSERVATION.
                  No model, no forecast, no weather, no interpolation, no expert opinion.
TIME_WINDOW       the trailing 28 days ending at AS_OF, both ends inclusive.
                  AS_OF is an INPUT, never the clock, so every run is replayable.
REGIONAL_UNIT     province, inside one region. Never national. A province with no visits
                  does NOT inherit its neighbour.
BASELINE          the same month-day span in every prior season in the archive, same
                  province × crop × issue. A baseline season that itself fails MIN_SITES is
                  dropped, never filled. Current value is placed as a percentile in that
                  distribution (ties count as half — deterministic).
UPDATE_FREQUENCY  measured, not assumed: DATA_LATENCY_DAYS is emitted with every run.
                  Measured today = 2 days for both cases.
UNKNOWN_RULE      n_sites < MIN_SITES              -> UNKNOWN_NO_DATA      (no value at all)
                  usable baseline seasons < MIN_BASE -> UNKNOWN_NO_BASELINE (value, no class)
                  UNKNOWN is a published state. It is never rendered as zero, never as "low",
                  and the window is never widened until something appears.
EVIDENCE          per cell: n_visits, n_sites, source URL, and the sha256 of the raw file it
                  was computed from, verified against the collection index before use.

PARAMETERS (all of them)  WINDOW_DAYS=28  MIN_SITES=8  MIN_BASE=5  HIGH_P=0.80  LOW_P=0.20
```

### Is there hidden manual judgement? — measured, not asserted

The only judgement is those five parameters. Their influence was measured over a 135-point grid
(window 14–42 d × min_sites 5/8/12 × baseline depth 3/5/8 × thresholds .75/.80/.90):

```
BACTROCERA   MEAN_LABEL_STABILITY = 0.918   7/10 provinces identical at EVERY grid point
OIDIO        MEAN_LABEL_STABILITY = 0.596   Livorno/Lucca/Massa-Carrara flip L / TYPICAL / UNKNOWN
```

Reproducibility: two independent runs are byte-identical (`REPRODUCIBLE=True`), every raw file
hash-checked. **There is no hidden manual step. The judgement is five declared numbers, and its
size is now a measured quantity per province.**

### Is it degenerate? — the test that mattered most

A "pressure" that says the same thing every season is describing the archive's drift, not the
season. Replayed walk-forward at the same calendar date in every season, baseline = prior
seasons only:

```
BACTROCERA (06-09)   H=24  TYPICAL=57  L=43   DOMINANT_CLASS_SHARE 0.46  -> DISCRIMINATING
OIDIO      (15-07)   H=11  TYPICAL=69  L=44   DOMINANT_CLASS_SHARE 0.56  -> DISCRIMINATING
```

Provinces disagree **inside the same season** (2016: Arezzo H, Firenze TYPICAL, Livorno H,
Siena TYPICAL). Restricting the baseline to the last 10 seasons instead of all prior seasons
changes individual cells but not the character (0.42 vs 0.46) — so the statement is not an
artefact of the baseline length either.

---

## FASE 5 — EVOLUTION IS NOT JUST A PRETTY CHART

```
OIDIO        rho(year, incidence) = -0.814   rho(%georeferenced, incidence) = -0.737
BACTROCERA   rho(year, incidence) = -0.475   rho(%georeferenced, incidence) = -0.418
PERONOSPORA  rho(year, incidence) = -0.185   (no trend to confound)
```

The apparent multi-year decline is **collinear with the monitoring era** (% georeferenced runs
0 % in 2006–08 to 98 % from 2017). Therefore:

```
EVOLUTION as "which seasons were bad relative to each other"  = PROVED
EVOLUTION as "the disease is declining over 20 years"         = TREND_NOT_PROVED
```

A falling line would have been the easiest chart in the product and the most dishonest.

---

## FASE 6 — AUTOMATION, PROBED LIVE

`ENGINE/automation_probe.py`, run today against the live source:

| | measured |
|---|---|
| UPDATE_METHOD | one unauthenticated HTTPS GET, JSON, ~2 s |
| MANUAL_STEPS | 0 for a refresh (collection params are fixed per case) |
| verification | returned the current season **row-for-row identical** to what is stored: 2515 = 2515, 2928 = 2928 |
| DATA_LATENCY | 2 days to the latest observation |
| SOURCE_STABILITY | same endpoint and schema across 21 seasons and two regional instances |
| BREAKAGE_RISK | **real and already met twice**: the `difesa`/`tipo_elab` trap returns HTTP 200 + `ok:true` + 0 rows. The probe itself fell into it on its first run. Any refresh job MUST treat rowCount 0 as FAILURE, never as "no disease". |
| COST | €0, public regional API |

```
CAN_REFRESH_WITHOUT_RESEARCH_PROJECT = YES   (Toscana AgroAmbiente, both cases)
                                     = YES   (Abruzzo AgroAmbiente, same schema, verified earlier)
                                     = NOT_TESTED for every other Italian region
```

Data-quality facts recorded rather than smoothed: `var 50` on crop 3 / schema 8 returns
all-null values (peronospora does not live in that schema) and the module answers UNKNOWN
instead of inventing a scale; 15 of 2515 current-season rows carry a date **after today** and
are excluded by the cutoff.

---

## FASE 7 — REGIONALITY: THE CAPABILITY IS A PROPERTY OF THE CELL, NOT OF THE TOOL

Same code, same region, same day. Publication gate = label stability ≥ 0.80 **and** historical
coverage ≥ 0.60 (threshold declared; **set after seeing these two numbers — post-hoc, and said
so**).

```
OLIVO x BACTROCERA x TOSCANA   PUBLISHABLE 8/10 provinces
VITE  x OIDIO      x TOSCANA   PUBLISHABLE 0/10 provinces at 2026-09-06 (2/10 at mid-season)
Prato                          UNKNOWN in 37 of 37 season-evaluations across BOTH cases
```

Italy-level coverage, stated plainly:

```
REGIONS_WITH_PROVED_DATA  = 1    Toscana
REGIONS_PARTIAL           = 1    Abruzzo — schema replicates and the scale derives cleanly, but
                                 its nome_area is an AGRO-ZONE partition, not provinces, and no
                                 area reaches 10 seasons -> 0 qualifying pairs. The internal
                                 consistency test CANNOT RUN there (C3). It also does not
                                 co-move with Toscana (rho +0.190 p 0.67).
REGIONS_UNKNOWN           = 18   never tested

GEOGRAPHIC GENERALIZATION = NOT DEMONSTRATED. All 108 province pairs come from the same nine
Tuscan provinces and one API host.
```

**No national Italian pressure figure is produced, and the code cannot produce one.**

---

## FASE 3 — VALUE WITHOUT ANY FORECAST

`ENGINE/answer_sheet.py` computes the eight answers rather than writing them. Today,
2026-09-06, for the pest case:

1. **WHAT HAPPENED** — official scouts recorded damaging olive-fly infestation on 1 168 visits to 469 monitored olive sites in Toscana in the last 28 days.
2. **WHERE** — 9 provinces with data, Prato without. Province is the unit; no national figure exists.
3. **HOW MUCH** — Arezzo 0.000 (usual 0.36), Firenze 0.000 (usual 0.54), Grosseto 0.058 (usual 0.46), Livorno 0.117 (usual 0.89) …
4. **HOW IS IT EVOLVING** — within season: 4 rising, 4 flat, 1 falling vs the previous 28-day window. Across seasons: ranking PROVED, multi-year trend TREND_NOT_PROVED.
5. **PRESSURE HIGHER OR LOWER** — 8 provinces LOWER_THAN_USUAL, Massa-Carrara withheld as low-confidence, Prato UNKNOWN.
6. **WHAT CHANGED** — 9 of 10 provinces differ from the same date last season.
7. **SOURCE** — OFFICIAL_OBSERVATION, NOWCAST (never FORECAST), latency 2 days, 21 raw files hash-checked.
8. **WHAT WE DON'T KNOW** — Prato never classifiable; Massa-Carrara low-confidence; EARLY_WARNING, PRE_SEASON_OUTLOOK, NEXT_SEASON_OUTLOOK, MULTI_YEAR_TREND, any statement about unvisited fields, and ADAMA_PRODUCT_RELATION all NOT_PROVED; the panel is the monitored network, **not a random sample of the region**.

For the disease case on the same day the honest sheet publishes **nothing** — 0 provinces pass
the gate. A tool that stays silent when it cannot speak is the finding, not the failure.

---

## FASE 8 — AGRONOMIC VALUE vs ADAMA PRODUCT RELATION, KEPT SEPARATE

```
AGRONOMIC_INTELLIGENCE_VALUE = PROVED for OLIVO x BACTROCERA x TOSCANA
                                       (8 provinces, 20 complete seasons + 1 in progress,
                                        2-day latency, label stability 0.918,
                                        province agreement on the published metric rho +0.449,
                                        which exceeds the effort agreement of +0.252)
                             = NOT_PROVED for VITE x OIDIO x TOSCANA
                                       (0 provinces pass today's gate, label stability 0.651,
                                        and its province agreement is withdrawn because survey
                                        effort agrees more strongly than the disease does)

ADAMA_PRODUCT_RELATION       = NOT_PROVED
```
`NOT_PROVED` here means exactly one thing: no approved-use handoff has been received from the
regulatory lane (`claude/label-intelligence-v1-italy`), so no product may be attached to any
cell. It does **not** mean no relation exists, and it does **not** kill the capability — the
agronomic statement above stands entirely on its own without naming a single product.
