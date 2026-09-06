# SHADOW UI SPEC — DISEASE & PEST INTELLIGENCE

**This is a specification, not a screen.** Nothing was built. `PORTAL_INTEGRATION = NO`.
It exists so that a future portal team inherits the *refusals* along with the feature, rather
than re-deriving them after shipping something wrong.

---

## THE ONE VIEW

A single view, scoped to one **REGION × CROP × ISSUE** chosen before anything renders. There is
no "all Italy" mode, no "all crops" mode and no "all issues" mode, because there is no such
number.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Toscana · olive · Bactrocera oleae (damaging infestation)                    │
│  Last 28 days to 6 Sep 2026 · official field scouting · updated 2 days ago    │
├──────────────────────────────────────────────────────────────────────────────┤
│  province        now      usual for the date    sites    state               │
│  Livorno        11.7%          88.9%              77     lower than usual    │
│  Siena          13.1%          51.9%              61     lower than usual    │
│  Grosseto        5.8%          46.3%             156     lower than usual    │
│  …                                                                            │
│  Massa-Carrara  30.0%          55.6%              10     not enough certainty │
│  Prato             —              —                7     no data              │
├──────────────────────────────────────────────────────────────────────────────┤
│  What this is: what scouts recorded on monitored sites. Not a forecast.       │
│  What we don't know: Prato is not monitored enough to say anything.           │
└──────────────────────────────────────────────────────────────────────────────┘
```

## RULES THE VIEW MUST OBEY

**R1 — UNKNOWN is a row, not a gap.** A province with no data appears in the table, with `—`
and the words "no data". It is never omitted, never zero, never grey-as-low, never interpolated
from neighbours, and never dropped from a map by leaving the polygon uncoloured in the same
palette as the low class.

**R2 — the site count sits next to every value.** 30.0% over 10 sites and 5.8% over 156 sites
are different statements and must look different.

**R3 — a withheld class says why.** "Not enough certainty" is shown when the class flips across
the parameter grid, together with the value and the usual-for-the-date. The user sees the
number and is told the *label* is not stable. Never silently promote it to a class.

**R4 — no forecast vocabulary.** Not *forecast*, *risk*, *previsione*, *rischio*, *outlook*,
*alert*, or an arrow implying where it is going next. The permitted verb tense is the past.

**R5 — the date is the headline, not a footnote.** "Last 28 days to 6 Sep 2026" and "updated 2
days ago" sit in the header. A view that cannot state its own latency must not render.

**R6 — no product placement.** No product name, no recommendation, no "consider treating"
anywhere on this view, until the regulatory lane delivers an approved use carrying
`REGISTRATION_ID`, `AUTHORIZED_USE_PROVED`, `SOURCE_PDF` and `SOURCE_HASH`. Today
`ADAMA_PRODUCT_RELATION = NOT_PROVED`.

**R7 — an in-progress season is labelled.** Any season chart including the current season shows
"season in progress, week N of ~M". The 28-day comparison is unaffected and says so.

**R8 — the evidence is one click away.** Every cell can show its n_visits, n_sites, window,
source URL and raw-file hash. A cell that cannot produce them is not rendered.

**R9 — the view refuses to render an unqualified cell.** If the elected REGION × CROP × ISSUE
has no province passing the publication gate, the view shows the values with all classes
withheld and states that no comparison can be published — as it would today for
`Toscana × vine × oidio`. **A screen that always has something to say is the failure mode this
whole mission exists to prevent.**

## WHAT WOULD HAVE TO BE TRUE BEFORE ANY OF THIS IS BUILT

1. Gate **J** answered — whether the portal already has this capability. It is currently
   `NOT_TESTABLE` because settling it means reading the portal inventory, which this mission is
   forbidden to touch. `NOT_TESTABLE` is not a pass.
2. A named owner for the refresh job, including the `rowCount == 0 → FAILURE` rule.
3. A decision on scope: **one cell qualifies today.** A view built for one cell in one region is
   a different product from a platform, and pretending otherwise is how `UNKNOWN` quietly becomes
   zero.
