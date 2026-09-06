# DISEASE & PEST INTELLIGENCE — CAPABILITY CONTRACT

**Status:** candidate for *future* integration. `PORTAL_INTEGRATION = NO`.
No screen exists. No portal branch was touched. Production was not touched.

This document is the contract a portal team would have to honour if the capability were ever
admitted. It is written so that a reader can tell, for any cell, whether the tool may speak.

---

## 1. WHAT THIS CAPABILITY IS

> For one **region × crop × issue**, and one **province** inside that region, it states what
> official field scouts recorded in the **last 28 days**, and whether that is **higher, typical
> or lower** than the same 28 calendar days in prior seasons of that same province.

That is the whole claim. It is a **NOWCAST of the monitored network**, not a forecast, not a
statement about fields nobody visited, and not a statement about a region as a whole.

## 2. WHAT IT IS NOT — every one of these is measured, not assumed

| claim | state | why |
|---|---|---|
| EARLY_WARNING | `NOT_PROVED` | `FIRST_PROVED_CUTOFF = None` after the oracle-selection defect was found and the 31 May result retracted |
| PRE_SEASON / NEXT_SEASON OUTLOOK | `NOT_PROVED` | never demonstrated out of sample |
| 12-month skill | `NO` | |
| multi-year TREND | `TREND_NOT_PROVED` | the decline is collinear with monitoring era (ρ(%georef) = −0.737 for oidio, −0.418 for the olive case) |
| a national Italian figure | **impossible by construction** | Toscana and Abruzzo do not co-move (ρ +0.190, p 0.67) |
| geographic generalization | **NOT DEMONSTRATED** | all 108 province pairs come from the same 9 Tuscan provinces and one API host; Abruzzo's units are agro-zones and no area reaches 10 seasons |
| ADAMA_PRODUCT_RELATION | `NOT_PROVED` | no approved-use handoff from the regulatory lane; **no product may be attached to any cell** |

## 3. THE DEFINITION THE PORTAL WOULD HAVE TO RENDER

```
INPUTS            official field-scouting visits only. EvidenceRole = OFFICIAL_OBSERVATION,
                  ENFORCED: MODELLED_RISK and FORECAST are refused, and a variable absent from
                  the case's survey-schema metadata is refused.
TIME_WINDOW       trailing 28 days ending at AS_OF (an input, never the clock)
REGIONAL_UNIT     province. A silent province NEVER inherits its neighbour.
BASELINE          the same month-day span in every prior season of the same province × crop ×
                  issue; a baseline season failing MIN_SITES is dropped, never filled
UNKNOWN_RULE      n_sites < 8            -> UNKNOWN_NO_DATA
                  usable baselines < 5   -> UNKNOWN_NO_BASELINE
                  UNKNOWN is PUBLISHED. Never zero, never "low", never hidden by widening
                  the window until something appears.
EVIDENCE          per cell: n_visits, n_sites, window, source URL, role, raw-file sha256
PARAMETERS        WINDOW_DAYS 28 · MIN_SITES 8 · MIN_BASE 5 · HIGH_P 0.80 · LOW_P 0.20
```

## 4. THE PUBLICATION GATE — when the tool is allowed to speak

A province cell may show a **CLASS** only if **both** hold:

```
LABEL_STABILITY   >= 0.80   (share of a 135-point parameter grid giving the same class)
HISTORICAL_COVERAGE >= 0.60 (share of past seasons where the same date was classifiable)
```

Otherwise the cell shows its **VALUE and baseline median** with the class **withheld**, or
`UNKNOWN`. Threshold declared, and declared **post-hoc** — it was set after seeing the two
cases' stability numbers. That is a limitation, not a footnote.

Measured on the same day with the same code:

| cell | publishable provinces |
|---|---|
| OLIVO × *Bactrocera oleae* × Toscana | **8 / 10** |
| VITE × Oidio × Toscana | **0 / 10** |

**The capability is a property of the cell, not of the tool.** A portal that ships it must ship
it per cell, and must be able to show nothing.

## 5. THE ONE CELL THAT CURRENTLY QUALIFIES

```
REGION  Toscana        CROP  olive        ISSUE  Bactrocera oleae, damaging infestation
SEASONS 20 complete + 2026 in progress    VISITS 79 251
LATENCY 2 days         LABEL_STABILITY 0.918      PUBLISHABLE 8/10 provinces
INTERNAL CONSISTENCY on the published metric: rho +0.449, which EXCEEDS the
  agreement of survey effort itself (+0.252) — the test oidio fails
CURRENT_PRESSURE_MONITOR = PROVED
```

Every other cell examined is `NOT_PROVED`, `INSUFFICIENT_DATA` or `NOT_TESTABLE`. Notably
`VITE × Oidio × Toscana` is **NOT_PROVED**: its province agreement is withdrawn because survey
*effort* agrees across its provinces (ρ +0.738) far more strongly than the disease does (+0.229).

## 6. REFRESH CONTRACT

```
METHOD    one unauthenticated HTTPS GET per (crop, schema, var, year), ~2 s, EUR 0
LATENCY   2 days to the latest observation
VERIFIED  the live call reproduced the stored season row-for-row (2515=2515, 2928=2928)
MANDATORY rowCount 0 with HTTP 200 and ok:true is a FAILURE, never "no disease".
          This trap has now caught this project three times, including the automation probe
          written to test for it.
SEASONS   a season whose last week falls more than 2 weeks short of the archive's typical last
          week is flagged IN_PROGRESS_OR_TRUNCATED and may not be drawn as a peer of completed
          seasons. CURRENT_PRESSURE is immune by construction; season and trend views are not.
```

## 7. NON-NEGOTIABLES FOR ANY FUTURE SCREEN

1. Never render `UNKNOWN` as `0`, as a blank, or as a pale shade of "low".
2. Never colour a province that has no data, and never interpolate one from its neighbours.
3. Never show an Italy-level number. There isn't one.
4. Never use the words *forecast*, *risk*, *previsione* or *rischio* for this capability.
5. Never attach a product to a cell until the regulatory lane delivers an approved use with
   `PROOF_STATE` and `SOURCE_HASH`.
6. Show the number of monitored sites next to every value. A percentage over 8 sites and one
   over 156 are not the same statement.
7. State on the view that the panel is the **monitored network**, not a random sample of the
   region.
