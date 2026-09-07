# RT1 — RED TEAM, LENS: SEMANTICS

Independent adversarial review of the OBSERVATIONAL engine and of
`S1-SEMANTICS/SOURCE-SEMANTIC-SHEET.json`. I wrote none of this code. My job was to prove
the tool is measuring the wrong thing.

**It is.** The three columns the tool publishes are not counts of infested drupes. Since the
2020 season the source serves them as **percentages already divided by `tot`**, and the
source's own API publishes the SQL that computes them. The engine divides by `tot` a second
time. On the 92.99% of visits where `tot == 100` the two are the same number and nobody
notices; on the rest the published rate is wrong by a factor of `tot/100`.

The composition of `totale`, which the sheet writes UNKNOWN, is fully settled by data that
was one unauthenticated HTTP request away. The third component is not eggs, not exit holes
and not sterile stings — it is **dead first- and second-instar larvae**, i.e. pest
*mortality*, which for a crop-protection reader points the opposite way from pressure.

---

## VERSIONS AUDITED

The engine was being edited by another agent while I worked. Everything below was verified
against the raw data and against the source API, which do not depend on the engine version.
Code-level findings (§8, §9) were reproduced against:

| file | sha256 (first 16) |
|---|---|
| `engine/di_core.py` | `e56dc697a3d57acd` (also seen: `2ba3abc24895ee86`) |
| `engine/di_observe.py` | `8fb727f137b6e2d0` (also seen: `093d95c9684fbea3`) |
| `engine/di_render.py` | `b60ba28c9c6b73a0` |
| `S1-SEMANTICS/SOURCE-SEMANTIC-SHEET.json` | `b5c0a6b55356a53b` |

git HEAD at the start of the audit: `8efec08`.

The sheet grew from 9,039 to 11,382 bytes during the audit. The added keys are
`GROVE_IDENTITY` and `REGION_PROVINCES` (another lens's territory). Every block this report
attacks — `VARIABLES`, `UNIT_TRAP`, `SOURCE_ACTION_BANDS`, `SANITY_RULES_A_VISIT_MUST_PASS`,
`DECLARED_BY_THE_SOURCE_BUT_NEVER_COLLECTED`, `WHY_THIS_FILE_EXISTS`, `VISIT_KEY`, `SOURCE` —
is byte-identical to what I audited. **Every finding below stands against the sheet as it is
on disk right now.**

## WHAT I FETCHED

The sheet says, of the composition of `totale`:

> "vars 2 to 11 and 21 were never collected, so the composition of `totale` is UNKNOWN from
> the bytes on disk"
> WHAT_WOULD_SETTLE_IT: "collect id_survey_var 2,3,4,5,6,7,8,9,10,11,21 for the same visits
> and test the identity stage by stage"

I did exactly that. `REDTEAM/rt1_fetch_stages.py` pulled variables 2,3,4,5,6,7,8,9,10,11,21
for **all 21 seasons, 2006 through 2026** — **231 requests, 227 returned usable rows and were
stored**, no authentication, no key, no rate limit hit, ~2.9 s per request, 308 MB in
`REDTEAM/FETCH/`. Nothing was written outside `REDTEAM/`.

The 4 requests that did not return data were **var 21 (`ps`) for the 2017, 2018, 2019 and
2023 seasons**, which came back as a full row skeleton with every `val` empty — the shape
this source returns for a variable that is not in that season's schema. Every other request,
including all 21 seasons of the ten core stage variables, returned readable values.

**The thing the sheet declared unknowable took 11 minutes.**

---

# ACCUSATION 1 — `attiva`, `dannosa` and `totale` are PERCENTAGES, not counts. The engine divides by the sample size a second time.

**CLAIM.** The sheet's UNIT_TRAP says the opposite of the truth:

> "this engine NEVER reads the raw value as a percentage. It computes value / tot"
> "a dannosa of 6 out of 200 drupes is 3%, which the legend would paint yellow"

The source computes and serves `trunc(sum_of_stages / tot * 100, 1)`. A `dannosa` of 6 on a
`tot` of 200 **is 6%**. The engine publishes 3%.

**METHOD.**
- `REDTEAM/rt1_percent_proof.py` — two rival hypotheses (COUNT: `totale == sum(stages)`;
  PERCENT: `totale == 100*sum(stages)/tot`), separated only on visits where `tot != 100`.
- `REDTEAM/rt1_source_formula.py` — reads the live API's own `filter.survey_var.data` block.
- `REDTEAM/rt1_switch.py`, `REDTEAM/rt1_final_numbers.py` — season by season.

**REPRODUCED: YES.**

**NUMBERS.**

The source publishes the formula. Verbatim from
`https://agroambiente.info.regione.toscana.it/agro18/api/dati/get_aedita_data?...&survey_var=-1001&...`,
field `filter.survey_var.data[].json.calculated_field.value`:

```
attiva  = trunc( ((u + l1v + l2v)                                    / tot * 100), 1)
dannosa = trunc( ((l3v + l3m + pm + pv + fu)                         / tot * 100), 1)
totale  = trunc( ((u + l1v + l1m + l2v + l2m + l3v + l3m + pm + pv + fu) / tot * 100), 1)
```

with the source's own guard `where: val->>'tot'<>'' AND val->>'tot'<>'0' AND ...`.

Verified against the bytes, not just the metadata. Under the era rule (see Accusation 7) the
three identities hold in **75,657 of 75,657 visits (100.00%)** across 21 seasons — every
visit in the archive with `tot > 0` and all fourteen columns readable (the archive holds
79,251 visits; 3,594 are excluded for a null column or `tot == 0`).

On the visits that can tell the hypotheses apart (`tot != 100` and at least one stage
present), 2020–2026, metric `totale`:

| season | separating visits | PERCENT holds | COUNT holds |
|---|---|---|---|
| 2020 | 273 | 273 (100.0%) | 76 (27.8%) |
| 2021 | 127 | 127 (100.0%) | 0 (0.0%) |
| 2022 | 53 | 53 (100.0%) | 14 (26.4%) |
| 2023 | 61 | 61 (100.0%) | 10 (16.4%) |
| 2024 | 131 | 131 (100.0%) | 4 (3.1%) |
| 2025 | 92 | 92 (100.0%) | 0 (0.0%) |
| 2026 | 61 | 61 (100.0%) | 1 (1.6%) |

Individual rows, with the stage columns beside them:

| grove | date | tot | `totale` served | sum of the 10 stages | 100·sum/tot |
|---|---|---|---|---|---|
| 5716 | 2026-08-17 | 1400 | 0.2 | 3 | 0.214 |
| 9371 | 2026-08-11 | 460 | 10.6 | 49 | 10.652 |
| 6223 | 2024-09-06 | 500 | 16.2 | 81 | 16.200 |
| 5518 | 2020-07-30 | 600 | 9.5 | 57 | 9.500 |
| 4671 | 2020-07-28 | 3 | 66.6 | 2 | 66.67 |

Row 4671 is decisive on its own: a "count of drupes" of **66.6** out of **3** sampled.

**Impact on the published numbers, window 2026-08-10..2026-09-06:**

| province | metric | engine | correct | ratio |
|---|---|---|---|---|
| Grosseto | dannosa | 0.0578% | 0.0751% | ×1.30 |
| Pisa | totale | 2.0879% | 2.5709% | ×1.23 |
| Grosseto | totale | 1.9931% | 2.2393% | ×1.12 |
| Pisa | attiva | 1.0200% | 1.0708% | ×1.05 |
| Siena | attiva | 0.6909% | 0.6200% | ×0.90 |
| Siena | totale | 1.4633% | 1.3925% | ×0.95 |

**Impact on the source's own colour band**, over every province × 28-day window in the
archive that passes the engine's declared gates (≥8 visits, ≥400 drupes) — 6,633 windows,
of which 2,302 fall in the 2020+ era where the bug bites:

| metric | windows whose band changes | of the 2,302 windows in 2020+ |
|---|---|---|
| `totale` | 32 | 1.390% |
| `attiva` | 24 | 1.043% |
| `dannosa` | 10 | 0.434% |

Both directions, on real windows:

- Pistoia, window ending 2021-07-27: engine **12.34% RED**, correct **9.84% YELLOW**
  (24 visits, 1,920 drupes).
- Grosseto, window ending 2020-08-12: engine **9.40% YELLOW**, correct **10.48% RED**
  (557 visits, 62,484 drupes).
- Siena, window ending 2025-08-06: engine **10.48% RED**, correct **9.19% YELLOW**.
- Pisa, window ending 2025-08-20 (`dannosa`): engine **9.83% YELLOW**, correct **10.38% RED**.

On the 2026-09-06 publication itself **no band changes**: all ten provinces read green under
both readings. The error is real, systematic and directional; on this particular date it does
not cross a threshold.

**IMPACT: FATAL.** The engine's central arithmetic — the one sentence it exists to
print — is wrong on 7.01% of visits (5,543 of 79,074 with a readable `tot`), and the sheet's
UNIT_TRAP section states the inverse of the source's published formula as its governing rule.

**WHAT SURVIVES.** `tot` really is the denominator, proved by the source's own SQL. The
engine's `tot > 0` refusal matches the source's own `where` clause exactly. And the choice
to compute a rate rather than "share of sites above zero" is right — the sheet's criticism of
the previous pilot stands.

---

# ACCUSATION 2 — the composition of `totale` is not UNKNOWN, and the sheet's guess is wrong in all three of its parts

**CLAIM.** The sheet writes:

> "The source declares, in the same schema, the stage columns u (Uova, eggs), fu (fori di
> uscita, exit holes) and ps (punture sterili, sterile stings) - components that are
> infestation but neither still-alive nor damaging. That is a plausible reading of the gap
> and it is NOT proved here."

All three named candidates are wrong. `u` is already inside `attiva`. `fu` is already inside
`dannosa`. `ps` is not inside `totale` at all.

**METHOD.** `REDTEAM/rt1_identity.py` (brute force over all 2,047 subsets of the 11 stage
variables), `REDTEAM/rt1_identity2.py`, `REDTEAM/rt1_final_numbers.py`.

**REPRODUCED: YES.**

**NUMBERS.**

```
totale - (attiva + dannosa)  ==  l1m + l2m
```

— dead first-instar larvae plus dead second-instar larvae.

- On the **34,555** visits where the gap is greater than zero: exact in **34,540 (99.96%)**.
- On all **75,657** stage-complete visits: exact in **75,642 (99.98%)**.
- Per season, on the visits with a positive gap: 98.80% (2006), 99.82% (2010), 99.68% (2015),
  99.66% (2020), 99.79% (2023), 99.94% (2024), 99.95% (2025), **100.00% (2026)**.

The sheet's three candidates, on the same 34,555 visits:

| candidate | exact |
|---|---|
| `u` (eggs) | 2,718 of 34,555 (7.87%) |
| `fu` (exit holes) | 1,535 of 34,555 (4.44%) |
| `u + fu` | 2,905 of 34,555 (8.41%) |
| **`l1m + l2m` (dead young larvae)** | **34,540 of 34,555 (99.96%)** |

This is also derivable in one line from the source's published SQL:
`totale − attiva − dannosa = (u+l1v+l1m+l2v+l2m+l3v+l3m+pm+pv+fu) − (u+l1v+l2v) − (l3v+l3m+pm+pv+fu) = l1m + l2m`.

**Why it matters agronomically, not just arithmetically.** The gap is *mortality*. Dead young
larvae are the infestation that failed — killed by heat, by a natural enemy, or by a
treatment. Across the whole archive, dead first- and second-instar larvae are **273,903 of
712,720 stage findings (38.43%)** of everything `totale` counts. Per season the share ranges
from **20.48% (2006, 6,282 of 30,674)** to **66.32% (2026, 3,814 of 5,751)**. In 2026 two
thirds of the tool's `TOTAL_INFESTATION_COUNT` is dead insects.

A province whose `totale` is high because larvae are dying and a province whose `totale` is
high because larvae are alive are the same number in this tool. For a crop-protection reader
they are opposite situations.

**IMPACT: FATAL.** `TOTAL_INFESTATION_COUNT` mixes live pressure with kill. The sheet says
`totale` CAN_USE_FOR "an observed rate of any infestation" without qualification.

**WHAT SURVIVES.** The sheet was right that `totale` is not `attiva + dannosa`, right that a
third component exists, and right to write UNKNOWN rather than guess. It was wrong to stop
there when the settling data was public and free.

---

# ACCUSATION 3 — `attiva` is not "infestation that is still alive"

**CLAIM.** The sheet's MEANING for var −1001: "drupes carrying infestation that is still
alive on the day of the visit", CAN_USE_FOR "the state of the pest AT the visit".

The source's formula is `attiva = (u + l1v + l2v) / tot * 100`. Live third-instar larvae
(`l3v`) and live pupae (`pv`) are **excluded** from `attiva` and placed in `dannosa`. Eggs
(`u`), which have not hatched and are not yet in the flesh, are **included**.

**METHOD.** `REDTEAM/rt1_meaning.py`, `REDTEAM/rt1_final_numbers.py`.

**REPRODUCED: YES.**

**NUMBERS.** Over 75,657 stage-complete visits, 2006–2026:

- Live individuals recorded (`u+l1v+l2v+l3v+pv`): **329,035**.
- Inside `attiva`: **260,212 (79.08%)**.
- **Outside `attiva`, and counted as `dannosa` instead: 68,823 (20.92%)** — every one of them
  a living insect on the day of the visit.
- Visits where a live third-instar larva or a live pupa was present: **18,798**. On
  **2,737 of them (14.56%)** `attiva` reads exactly **0**.
- Eggs are **95,089 of 260,212 (36.54%)** of `attiva`'s mass.

`attiva` is not "alive". It is **"eggs and pre-damaging larvae"** — the young end of the
cohort. That is a useful thing, and it is not what the sheet says it is.

**IMPACT: FATAL** for the sentence the renderer prints. `di_render.render_province` writes
`"{value}% das azeitonas amostradas com infestação viva"` ("% of the sampled olives with
live infestation") for `ACTIVE_INFESTATION_COUNT`. That sentence is false in two ways at
once: the unit is not olives (Accusation 6) and the set is not "live".

**WHAT SURVIVES.** `attiva` is genuinely the *earlier* half of the cohort and genuinely
distinct from `dannosa`. The sheet's instinct — that these two columns are not
interchangeable and that the previous pilot published the wrong one — is right.

---

# ACCUSATION 4 — `dannosa` is not a purely lagging record; 38.53% of it is live insects

**CLAIM.** The sheet: `dannosa` CANNOT_USE_FOR "the current state of the pest - it is a
lagging record."

`dannosa = l3v + l3m + pm + pv + fu` contains `l3v` (live third-instar larvae) and `pv`
(live pupae).

**METHOD.** `REDTEAM/rt1_meaning.py`, `REDTEAM/rt1_final_numbers.py`.

**REPRODUCED: YES.**

**NUMBERS.** Summed mass of `dannosa` over 75,657 visits: **178,605** findings, of which
**68,823 (38.53%)** are live individuals (`l3v + pv`). Only `fu` (exit holes) is
unambiguously historical.

**IMPACT: MAJOR.** The sheet's prohibition is over-strong in one direction and the derived
statement "dannosa is damage already present" is over-strong in the other: more than a third
of it is an insect still in the fruit.

**WHAT SURVIVES.** The measured claim in the sheet — "24,834 of 78,012 visits (31.8%) have
attiva > 0 while dannosa reads 0" — is a real and correctly reported observation. The two
columns do describe different phases.

---

# ACCUSATION 5 — `ps` (sterile stings) is outside `totale`, and the tool is blind to it

**CLAIM.** The sheet lists `ps` among the plausible components of the gap.

**METHOD.** `REDTEAM/rt1_identity2.py`, `REDTEAM/rt1_final_numbers.py`.

**REPRODUCED: YES.**

**NUMBERS.** On the **17,992** visits where `ps > 0`:

- `totale == sum(10 core stages) + ps`: **0 of 17,992 (0.00%)**
- `totale == sum(10 core stages)`, `ps` excluded: **17,992 of 17,992 (100.00%)**

The source's published SQL for `totale` contains no `ps` term.

**100,214 sterile stings** are recorded on those visits and are invisible to every rate this
tool publishes. A sterile sting is real damage — the fruit is punctured and open to rot even
though no larva develops.

**IMPACT: MAJOR.** `TOTAL_INFESTATION_COUNT` is not "infestation of any kind"; it is
"infestation of any kind except sterile stings". Nothing in the sheet or the output says so.

**Related, and worse for the archive's future:** `ps` (var 21) **no longer exists** in the
live schema. The live variable list for crop 2 / schema 1 today is
`[-1004, -1003, -1002, -1001, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14]`; the archived one is
`[-1003, -1002, -1001, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 21]`. Var 21 was removed; vars
**−1004** (`ul1v`, "Infestazione U+l1v") and **14** (`u+p`, "uova con prolasioptera") were
added. See Accusation 10.

---

# ACCUSATION 6 — the unit is "stage findings per 100 olives", not "percent of sampled drupes"

**CLAIM.** `di_observe.cell` labels the observation `"unit": "percent of sampled drupes"`
and `di_render` prints "% das azeitonas amostradas". The source sums *per-stage tallies*. A
single drupe holding an egg and a live first-instar larva is counted in `u` and in `l1v`, and
therefore **twice** in `totale`. This is true even on the 92.99% of visits where the
arithmetic is otherwise correct.

**METHOD.** `REDTEAM/rt1_identity2.py`, `REDTEAM/rt1_final_numbers.py`.

**REPRODUCED: YES.**

**NUMBERS.** Over 75,657 stage-complete visits:

- Visits with **three or more distinct stages present at once**: **33,436 (44.19%)**.
- Visits where `sum(10 core stages) > tot` — literally more findings than olives sampled, and
  impossible if the unit were drupes: **65 of 75,657**. Example: grove 5977, 2026-08-09,
  Firenze, `tot = 100`, stages `u=22 l1v=12 l1m=76 l2v=2 l3v=2` = 114, `totale` served = 114.
- `sum(core)/tot`: median 0.0400, p99 0.7400, **max 18.0000**.
- In the 2020+ era, `totale` exceeds 100 (a percentage above 100%) on **24 of 24,594** visits.

The pest is *Bactrocera oleae*, which usually lays one egg per drupe, so findings ≈ drupes
most of the time. "Most of the time" is not a unit definition, and the sheet's `UNIT:
"count of drupes, out of tot"` is not what the source computes.

**IMPACT: FATAL** for the published sentence; **MINOR** for the numeric value at low
infestation, where stages rarely coexist.

**WHAT SURVIVES.** At low pressure — which is where all ten provinces sit on 2026-09-06 —
the difference between "findings per 100 olives" and "percent of olives" is small. It is not
small at the 10%+ readings the source's own red band is designed to flag, which is exactly
where the tool is supposed to be useful.

---

# ACCUSATION 7 — the unit CHANGES between the baseline seasons and now. The engine compares two different quantities.

**CLAIM.** The engine's baseline (`di_observe.cell`, `first_year=2006`) compares the current
28-day window with the same calendar window in every season back to 2006, using one formula.
The source changed its convention between the 2019 and 2020 seasons.

**METHOD.** `REDTEAM/rt1_switch.py` — all 21 seasons of stage data, decided on the separating
visits only (`tot != 100`, at least one stage present).

**REPRODUCED: YES.**

**NUMBERS.** Metric `totale`, separating visits, per season:

| era | seasons | separating visits | COUNT holds | PERCENT holds |
|---|---|---|---|---|
| pre-switch | 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019 | 738 | **100.0% in every single season** | 0.0–34.8% |
| post-switch | 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 798 | 0.0–27.8% | **100.0% in every single season** |

The same clean break appears independently for `attiva` (975 separating visits) and for
`dannosa` (468). The switch is between the 2019 and 2020 seasons, with no season straddling
it.

So the value/`tot` formula the engine uses is **right for 2006–2019 and wrong for 2020–2026**,
and the baseline comparison is between the two.

Share of visits with `tot != 100` per province-season (the only visits where the eras
disagree) reaches **79% (Massa-Carrara, 2018)**, **78% (Massa-Carrara, 2023)**,
**57% (Massa-Carrara, 2017)**, **52% (Massa-Carrara, 2020)**, **24% (Livorno, 2014)**,
**24% (Siena, 2024)**, **23% (Grosseto, 2022)**. Massa-Carrara's baseline and its current
window are in different units for the majority of their visits.

**IMPACT: FATAL** for `historical_state` in provinces with a high share of `tot != 100`
visits. On the 2026-09-06 run, the matched-panel direction (this window higher or lower than
a prior season on the shared groves) **flips for 1 of 2 comparable seasons in Grosseto and 1
of 17 in Siena** under the corrected reading; no province's published verdict changes.

**WHAT SURVIVES.** The engine's insistence on a matched panel — comparing the same groves,
and refusing to publish a comparison when fewer than 5 seasons share ≥8 groves — is the
single best decision in this codebase and it limits the blast radius here. Provinces built
almost entirely on `tot == 100` visits (Firenze: 0–5% non-100 in every season; Prato: 0–4%)
are unaffected.

---

# ACCUSATION 8 — the pooled rate is carried by a handful of visits, and one grove moves a province

**CLAIM.** `sum(infested)/sum(sampled)` over the window is presented as "the observation".
It is dominated by a small minority of visits, and the sheet and the renderer never say so.

**METHOD.** `REDTEAM/rt1_pooling.py`, window 2026-08-10..2026-09-06, metric `attiva`.

**REPRODUCED: YES.**

**NUMBERS.**

| province | visits | pooled | mean of per-visit rates | **median** | visits reading exactly 0 | visits carrying half the numerator |
|---|---|---|---|---|---|---|
| Arezzo | 55 | 0.1636% | 0.1636% | **0.0000%** | 49 of 55 | 3 |
| Firenze | 241 | 0.0664% | 0.0664% | **0.0000%** | 228 of 241 | 5 |
| Grosseto | 320 | 0.6575% | 0.7035% | **0.0000%** | 223 of 320 | 23 |
| Livorno | 153 | 0.9216% | 0.9216% | **0.0000%** | 81 of 153 | 18 |
| Lucca | 53 | 1.1509% | 1.1509% | **0.0000%** | 36 of 53 | 5 |
| Massa-Carrara | 40 | 0.5660% | 0.7500% | **0.0000%** | 24 of 40 | 5 |
| Pisa | 85 | 1.0200% | 1.0781% | **0.0000%** | 45 of 85 | 10 |
| Pistoia | 36 | 0.0278% | 0.0278% | **0.0000%** | 35 of 36 | 1 |
| Prato | 24 | 0.0417% | 0.0417% | **0.0000%** | 23 of 24 | 1 |
| Siena | 186 | 0.6909% | 0.8451% | **0.0000%** | 132 of 186 | 13 |

**The median per-visit rate is exactly 0.0000% in all ten provinces.** The engine computes
`per_visit_rate_pct_median` and puts it in the JSON; the renderer never prints it.

Delete the single largest-contributing grove and re-pool:

| province | with it | without it | change |
|---|---|---|---|
| Pistoia | 0.0278% | **0.0000%** | −100.0% |
| Prato | 0.0417% | **0.0000%** | −100.0% |
| Arezzo | 0.1636% | 0.1154% | −29.5% |
| Lucca | 1.1509% | 0.8367% | −27.3% |
| Massa-Carrara | 0.5660% | 0.4286% | −24.3% |
| Firenze | 0.0664% | 0.0549% | −17.4% |
| Siena | 0.6909% | 0.6284% | −9.0% |
| Pisa | 1.0200% | 0.9426% | −7.6% |
| Livorno | 0.9216% | 0.8533% | −7.4% |
| Grosseto | 0.6575% | 0.6255% | −4.9% |

**Pistoia's published observation is 1 infested finding in 3,600.** **Prato's is 1 in 2,400.**
Both come from a single grove and a single visit; both go to exactly zero if that grove is
removed. Both pass the engine's declared gates, because `MIN_DRUPES = 400` and
`MIN_VISITS = 8` constrain only the denominator. There is no gate on the numerator.

**Organisation concentration in the same window:**

- **Lucca**: 5,300 of 5,300 drupes (100.0%) and 61 of 61 infested findings (100.0%) come from
  one organisation, `ota`, at 14 groves.
- **Livorno**: `terreetruria` supplies 14,700 of 15,300 drupes (96.1%) and 131 of 141
  findings (92.9%).
- **Siena**: `Cetona` supplies 1,483 of 18,383 drupes (8.1%) but 51 of 127 findings (40.2%);
  its own rate is 3.4390% against `terreetruria`'s 0.0000% on 3,200 drupes in the same
  province and window.

**And the one escalation the whole region produces rests on 0.074 percentage points.**
Lucca is the only province classed `INVESTIGATE`, because `observed_trend =
INCREASING_OBSERVED`. Its three windows are:

| window ending | rate | numerator / denominator | visits | groves | non-zero visits |
|---|---|---|---|---|---|
| 2026-07-12 | 0.0769% | 1 / 1,300 | 13 | 13 | 1 |
| 2026-08-09 | 0.4464% | 25 / 5,600 | 56 | 14 | 12 |
| 2026-09-06 | 1.1509% | 61 / 5,300 | 53 | 14 | 17 |

Change = **1.074 percentage points** against `TREND_MIN_ABS_CHANGE_PCT = 1.0`. Raise the
declared threshold by 0.08 pp and the verdict becomes `STABLE_OBSERVED` and the attention
class drops from `INVESTIGATE` to `NO_ESCALATION`. The first window has 13 visits at 13
groves — one visit each — against 53–56 visits in the later two, so the series is also
comparing a thin sample with a thick one. All three windows are one organisation.

**IMPACT: MAJOR.** The pooled rate is defensible as an estimator. Publishing it as
"the observation", without the median, without the non-zero visit count, and without a
numerator gate, is not.

**WHAT SURVIVES.** Pooling with a real denominator beats the previous pilot's
"share of sites above zero" — the sheet's argument for that change is correct. The engine
does record `n_sites`, `n_orgs`, `per_visit_rate_pct_median` and `per_visit_rate_pct_max` in
the JSON. The information exists; the renderer discards most of it.

---

# ACCUSATION 9 — making the engine accept what it should refuse. Four ways in.

**METHOD.** `REDTEAM/rt1_refusal.py`. All fixtures built under `REDTEAM/FAKECASE/` from
copies and deleted afterwards; the archive was not touched.

**First, what genuinely works.** `di_core.var_for` refuses `'EGG_COUNT'`,
`'Infestazione Attiva'`, `'attiva'` and `-1001`. `di_core._read_variable` refuses raw
`id_survey_var = 2`. **REPRODUCED: the refusal works as advertised.**

### 9a. The sheet's prohibitions are decorative — the code never reads them

**CLAIM.** The sheet says var 1 CANNOT_USE_FOR "any measure of disease - it is how many
olives were looked at, not what was found". `di_report.py` takes the metric from `sys.argv[2]`
and passes it through unchecked.

**REPRODUCED: YES.**

```
py di_report.py 2026-09-06 "SAMPLE_SIZE / DENOMINATOR"
```

produces, for Firenze:

```
  100.0% das azeitonas amostradas com dano registado
  banda da própria fonte: >=10% (red)
```

Occurrences of `CANNOT_USE_FOR` in `di_core.py` + `di_observe.py`: **0**. Of `CAN_USE_FOR`:
**0**. Of `crop_id` or `survey_schema_id`: **0**. The sheet's CAN/CANNOT lists are prose that
no code path consults.

**IMPACT: MAJOR.** The stated guarantee is "no column enters the engine unless it has an
entry here". The realised guarantee is "no column enters unless it has an entry" — the
*direction* of use is unenforced.

### 9b. The file glob ignores crop and schema

**CLAIM.** `di_core._read_variable` builds `RAW/*_v{var_id}_*.json`. Nothing checks the
`c{crop}_s{schema}` prefix that `di_refresh.refresh_one` itself writes
(`fn = f"c{crop}_s{schema}_v{var}_{year}.json"`). A file from a different crop and a different
survey schema, carrying the same variable number, is loaded as olive-fly data.

**REPRODUCED: YES.** Dropping `c7_s99_v-1001_2026.json` and `c7_s99_v1_2026.json` (crop 7,
schema 99) into a case's `RAW/`:

- visits 2,928 → 3,328 (+400)
- **Firenze `ACTIVE_INFESTATION_COUNT`: 0.0664% → 33.2712%**
- **source band: green → red**
- no warning, no exception, no exclusion counter
- the alien file is listed under `provenance.source_files` with its sha256, and the
  provenance block still names the olive API and `crop id 2`

**IMPACT: MAJOR.** This is precisely the failure the sheet's WHY_THIS_FILE_EXISTS describes —
"a directory called FRUMENTO-SEPTORIA collected id_survey_var 372, which that same case's own
metadata calls 'Intensita' Oidio'. The engine believed the folder name." The engine still
believes the folder, just one level down: it believes the directory, and reads any file in it
whose name contains `_v1_`.

### 9c. `band_for` has a hole between 0 and 0.01, and the renderer crashes in it

**CLAIM.** `di_core.band_for` returns `None` for `0 < pct < 0.01`.
`di_render.render_province` line 38 does `o['source_band']['label']` unconditionally.

**REPRODUCED: YES.**

| rate | band returned |
|---|---|
| 0% | `Nessuna Infestazione` |
| **0.004%** | **None** |
| **0.0099%** | **None** |
| 0.01% | `0-6%` |
| 6.0% | `7-9%` ← label contradicts the number |
| 6.5% | `7-9%` ← label contradicts the number |

`di_render.render_province` on a cell with `value_pct = 0.004`:
`TypeError: 'NoneType' object is not subscriptable`.

Not hypothetical. Scanning every gate-passing province × 28-day window in the archive:

- `dannosa`: **113 windows** land in `0 < rate < 0.01`
- `attiva`: **3 windows** (Siena ending 2015-07-22, 0.0089%, 112 visits, 11,200 drupes;
  Siena ending 2015-07-27; Arezzo ending 2015-08-05)
- `totale`: **3 windows**

Each would raise `TypeError` in the province renderer. Under the corrected percent reading,
Grosseto's `dannosa` windows ending 2024-09-06, 2024-09-07 and 2024-09-10 move *out* of the
hole (0.0082% → 0.0134%), so the bug and Accusation 1 interact.

Separately, the "7-9%" label on the band that actually starts at 6 is the **source's own**
inconsistency, faithfully copied. The engine can print `6.4%` and `banda da própria fonte:
7-9%` in adjacent lines. **This one is the source's fault and the engine's problem.**

**IMPACT: MAJOR** (an unhandled crash on real archive data), **MINOR** for the label
contradiction.

### 9d. A `NaN` in the source passes every sanity gate

**CLAIM.** `di_core._num` is `float(str(v).replace(",", "."))`. `float("nan")` succeeds.
`nan < 0` is `False` and `nan > n` is `False`, so both sanity rules pass and the visit is
marked usable.

**REPRODUCED: YES.** `_num('nan') = nan`, `_num('NaN') = nan`, `_num('Infinity') = inf`.
A single Prato row set to `"nan"` does not produce a named refusal — it produces
`ValueError: cannot convert float NaN to integer` from `di_observe.pooled`
(`"infested_drupes": int(num)`), taking down the whole run.

Also on that line: `int(num)` **truncates**. Fractional values are real in the archive —
`totale` is non-integer in **483 of 78,010** readable rows (0.619%), `attiva` in
**340 of 78,034** (0.436%), `dannosa` in **152 of 78,019** (0.195%) — and **19 of them fall
inside the 2026-08-10..2026-09-06 publication window**. The published numerator is
`int(sum)` while the published rate uses the untruncated sum, so the two disagree.

**IMPACT: MINOR** for `NaN` (I have no evidence the source emits it); **MINOR** for the
truncation, which mis-states the printed numerator by up to 1 without changing the rate.

---

# ACCUSATION 10 — the sheet's evidence is a stale, truncated copy of the metadata that settles everything

**CLAIM.** The sheet's SOURCE block cites `"collection_index.json 'vars' block, served by the
API itself"`. That archived block is missing the field that defines the meaning of all three
published columns, and has been superseded.

**METHOD.** `REDTEAM/rt1_source_formula.py` — one live request, diffed against
`CASES/OLIVO-BACTROCERA-TOSCANA/collection_index.json`.

**REPRODUCED: YES.**

**NUMBERS.**

| what the sheet says | what the live API serves |
|---|---|
| var −1003 `SOURCE_DESCRIPTION: null` — "totale (no description)" | `description: "Infestazione Totale"` |
| var −1001/−1002/−1003 `json` = a `style` block only | `json` = `{"calculated_field": {"value": "<the SQL>", "where": "..."}, "style": [...]}` |
| var 1 `tot` "carries no colour legend, unlike the three infestation columns" | var 1 carries a style: `0-3%` / `3-9%` / `>=10%` — **every one of the 16 live variables carries a style** |
| 15 variables declared | 16: var 21 (`ps`) removed; **−1004** (`ul1v`, "Infestazione U+l1v") and **14** (`u+p`, "uova con prolasioptera") added |
| SOURCE_ACTION_BANDS `0.01/6/10` | unchanged for −1001/−1002/−1003 — **this part is correct** |

The single field that would have prevented Accusations 1, 2, 3, 4, 5 and 7 —
`calculated_field.value` — is present in the live metadata and absent from the archived copy
the sheet reads. The sheet's method ("the source's own metadata proves the meanings") is
right. Its execution read a truncated snapshot and never asked again.

**And nothing in the refresh cycle can notice.** `di_refresh` documents six outcomes
including `SCHEMA_CHANGED` ("the variables or the code table moved"). Grepping `di_refresh.py`:
`SCHEMA_CHANGED` appears on line 25 (docstring) and line 42 (constant) and is **never
assigned as a status anywhere**. `validate()` extracts `filt = js.get("filter")` and returns
it; `refresh_one()` unpacks it into a variable named `filt` on line 111 and never uses it.
The schema *has* changed — a variable was removed and two were added — and the named outcome
for exactly that event is unreachable code.

**IMPACT: MAJOR.**

**WHAT SURVIVES.** The band thresholds the sheet copied (`0.01`, `6`, `10`) are still exactly
what the source serves for the three published variables. The sheet's claim that the legend
labels are percentages is **correct** — and, read together with the formula, it is the clue
that should have overturned the UNIT_TRAP conclusion.

---

# ACCUSATION 11 — five columns enter the engine with no sheet entry, in violation of the sheet's founding rule

**CLAIM.** WHY_THIS_FILE_EXISTS: "From now on no column enters the engine unless it has an
entry here, and every entry carries the evidence that produced it. A column with no entry is
REFUSED, not guessed."

**METHOD.** `REDTEAM/rt1_meaning.py` — extract every `row.get("...")` in `di_core.py` and
test membership in the sheet.

**REPRODUCED: YES.**

| column read by `di_core` | used as | in the sheet? |
|---|---|---|
| `val` | the measurement | YES |
| `date` | the visit key, the as_of cut | YES |
| **`nome_area`** | **`province` — the entire unit of publication** | **NO** |
| **`name_4`** | `comune` | **NO** |
| **`admin_code`** | `comune_code` | **NO** |
| **`org_name`** | `org`, and `n_orgs` in the published output | **NO** |
| **`week`** | carried into every visit record | **NO** |

`nome_area` is the column the whole report is grouped by, and it has no entry, no evidence
line and no CANNOT_USE_FOR. The rule the sheet was written to enforce is broken by the file
the sheet governs.

**IMPACT: MAJOR** as a governance failure. The semantic content of `nome_area` mostly holds
up — see below.

---

# ACCUSATION 12 — `nome_area` and `admin_code` disagree about the province on 1,401 rows

**CLAIM.** The engine publishes by `nome_area` and emits `admin_code` as `comune_code` in the
same record, without checking that they agree.

**METHOD.** `REDTEAM/rt1_bandflip.py` — every row's `admin_code` mapped to its ISTAT province
prefix (6-digit) and compared with `nome_area`.

**REPRODUCED: YES.**

**NUMBERS.** Over 79,251 rows: agrees **77,850 (98.232%)**, disagrees **1,401 (1.768%)**,
unresolvable **0**.

Every disagreement is one-directional: `nome_area = "Prato"` against comune codes in the
`048` (Firenze) block — CARMIGNANO 48009 (664 rows), VAIANO 48047 (228), PRATO 48034 (224),
MONTEMURLO 48029 (222), POGGIO A CAIANO 48051 (63). Prato became a province in 1992; these
comuni still carry pre-1992 Firenze codes in the source. `nome_area` is the correct modern
attribution and `admin_code` is the stale one, so the engine's choice is right — by luck, not
by a check.

**IMPACT: MINOR.** No published number is wrong. Two province attributions ship in the same
record and nothing reconciles them.

**WHAT SURVIVES.** `nome_area` is the province, in 98.232% agreement with an independent
authority, and the residual is explained.

---

# ACCUSATION 13 — is `tot` really the sample size? Yes. Attempt failed.

**CLAIM (mine, to be tested).** `tot` might be a total count of something other than the
olives dissected.

**METHOD.** `REDTEAM/rt1_tot.py` — distribution, behaviour where `tot != 100`, per-org and
per-season stability; plus the source's published SQL.

**REPRODUCED: NO. The sheet is right.**

**NUMBERS.**

- `tot` is an integer in **79,074 of 79,074 readable rows (100.000%)** — zero non-integer
  values, unlike all three infestation columns.
- `tot == 100` in **73,531 of 79,074 readable (92.99%)**; on the sheet's own denominator of
  visits with all four columns readable, **73,499 of 78,008 (94.2198%)** — the sheet's "94.2%"
  is exactly reproduced.
- The source divides by it: `.../ ((val->>'tot')::decimal) * 100`. `tot` is the source's own
  denominator, by the source's own definition.
- The source guards it: `where: val->>'tot'<>'' AND val->>'tot'<>'0'` — the same rule the
  engine adopted independently.
- Stable across organisations (`terreetruria` 100.0% at `tot == 100` over 1,903 visits;
  `ERATA` 99.2% over 1,040; the lowest is `Confoliva` at 81.2% over 963) and across seasons
  (88.4% in 2021 to 96.3% in 2012, median `tot` = 100 in all 21 seasons).

**Two caveats the sheet does not carry.** (a) The extreme values are implausible as sample
sizes and look like keying errors: `tot = 1400`, `1010`, `1007`, `1001` (six occurrences),
`1000`, and at the other end `tot = 1` (8 visits), `2` (6), `3`. The `100x` family is
consistent with a stray keystroke on `100`. (b) Since the switch, a wrong `tot` corrupts the
value the source *stores*, not just the rate the engine computes, so it is unrecoverable.

**IMPACT: NONE** for the accusation; the sheet's SAMPLE_SIZE reading is confirmed by
independent evidence the sheet did not have.

---

# ACCUSATION 14 — could `attiva` be a count of INSECTS rather than of drupes?

**CLAIM (the assignment's question).** A drupe can hold more than one larva, so "attiva"
might count individuals.

**METHOD.** `REDTEAM/rt1_identity2.py`, `REDTEAM/rt1_final_numbers.py`, plus the source's SQL.

**REPRODUCED: PARTIALLY — and the honest answer has two levels.**

**What is settled:** `attiva` is not a count of anything. It is
`trunc((u + l1v + l2v)/tot*100, 1)` — a **percentage of a sum of three stage tallies**. Proved
in 75,657 of 75,657 visits (100.00%) and published as SQL by the source.

**What is NOT KNOWN:** whether each individual stage tally (`u`, `l1v`, …) counts
*individuals* or *drupes containing that stage*. The bytes constrain it but do not decide it:

- 65 of 75,657 visits have `sum(10 stages) > tot`, which rules out "drupes" as a *global*
  reading of the sum but is consistent with either reading of a single column plus
  multi-stage drupes.
- Field 5977, 2026-08-09, Firenze: `tot = 100`, `l1m = 76`, `u = 22`, `l1v = 12`, `l2v = 2`,
  `l3v = 2`, sum 114. Either 114 individuals in 100 olives, or 114 drupe-stage pairs across at
  most 100 drupes. Both are possible.
- The Italian field-guide convention for this survey — count each individual found on
  dissection — favours "individuals", but that is domain knowledge, not evidence from this
  source.

**WHAT WOULD SETTLE IT:** the Regione Toscana field protocol / scheda di rilievo for
`survey_schema 1`, or an `id_survey_var` recording "drupes infested" separately from the
stage tallies. Var **−1004** (`ul1v`, "Infestazione U+l1v"), new in the live schema, is
another server-side percentage of a stage sum and does not help. I could not settle it from
the API.

**IMPACT: MAJOR** — because the sheet's `UNIT: "count of drupes, out of tot"` is stated as
established fact and is not established. **NOT KNOWN** is the correct entry.

---

# WHAT I COULD NOT BREAK

1. **`tot` is the sample size.** I attacked it directly (Accusation 13) and it held on
   independent evidence the sheet never saw: the source's own SQL divides by it. Integer in
   79,074 of 79,074 readable rows. The sheet's `94.2198%` reproduces exactly.

2. **The visit key.** `(id_field, date)` is unique. The loader reads files in sorted order and
   raises `JoinConflict` rather than letting the filesystem pick a winner. I could not
   produce a silent collision from the archive.

3. **The `as_of` discipline.** `as_of` is an argument, never a clock; rows dated after it are
   dropped before anything else and counted. I found no path by which a future-dated row
   reaches a published number.

4. **The refusal mechanism itself.** `var_for` and `_read_variable` refuse unknown canonical
   names and unknown variable ids exactly as documented. Every bypass I found (§9) goes
   *around* the check, never through it.

5. **The matched-panel rule.** Restricting the historical comparison to groves present in both
   windows, and refusing to publish when fewer than 5 prior seasons share ≥8 groves, is
   correct and it is what contains the damage from Accusation 7. Seven of the ten provinces
   correctly publish no historical comparison at all.

6. **The band thresholds.** `0.01 / 6 / 10` are still exactly what the live API serves for
   variables −1001, −1002 and −1003. The sheet copied them faithfully. The "7-9%" label that
   starts at 6 is the source's own inconsistency, not the sheet's.

7. **The refusal to forecast.** I found no `will`, no forecast, no `ACT_NOW`, no
   `SALES_READY`, no `COMMERCIAL_OPPORTUNITY` on any path. `CANNOT_CONCLUDE` is printed
   unconditionally and the ADAMA layer cannot change the agronomy.

8. **The 55.67% / 44.33% arithmetic.** `attiva + dannosa == totale` in 43,424 of 78,008
   (55.67%), is less in 34,583 (44.33%), is greater in 1. Exactly as the sheet reports. The
   sheet's *observation* was right; only its *interpretation* of the gap was wrong.

9. **The engine is deterministic** on a fixed archive and a fixed `as_of`. Two loads in one
   process and two loads under `PYTHONHASHSEED=1` and `PYTHONHASHSEED=2` all produced the
   identical digest `87cbd3b8c50c29c6` over the full loaded structure.

---

## THE ONE-LINE VERDICT

The sheet's method is right and its central conclusion is inverted. It noticed that the
source's colour legend is denominated in percent, noticed that this "only works because
`tot == 100`", and then adopted the rule *"never read the raw value as a percentage"* —
when the correct inference from its own observation was that **the raw value already is a
percentage**, which is what the source's published SQL says and what 75,657 of 75,657
visits confirm.

Every remaining semantic error follows from stopping one HTTP request short of the metadata
that says so.

---

## SCRIPTS

All in `REDTEAM/`, all read-only outside `REDTEAM/`:

| script | what it does |
|---|---|
| `rt1_lib.py` | shared loader: archive + fetched stage variables into one visit table |
| `rt1_fetch_stages.py` | fetches vars 2,3,4,5,6,7,8,9,10,11,21 from the live API into `REDTEAM/FETCH/` |
| `rt1_identity.py` | brute force over all 2,047 subsets of the stage variables |
| `rt1_identity2.py` | the three identities and the gap on the full stage-complete set |
| `rt1_percent_proof.py` | COUNT vs PERCENT, decided on `tot != 100` visits |
| `rt1_switch.py` | the 2019→2020 convention switch, season by season |
| `rt1_source_formula.py` | the source's own SQL, and live-vs-archived metadata diff |
| `rt1_tot.py` | is `tot` the sample size |
| `rt1_noninteger.py` | the fractional infestation values |
| `rt1_protocol_break.py` | the `tot > 100` visits with their stage columns |
| `rt1_pooling.py` | pooled vs mean vs median, grove and organisation concentration |
| `rt1_impact.py`, `rt1_impact2.py` | what the finding does to published numbers and bands |
| `rt1_bandflip.py` | band changes and the `0 < rate < 0.01` hole, archive-wide; ISTAT check |
| `rt1_meaning.py` | liveness of `attiva`/`dannosa`; columns with no sheet entry |
| `rt1_stability.py` | is the formula stable across seasons; Lucca's trend |
| `rt1_refusal.py` | the four ways past the refusal (builds and deletes `REDTEAM/FAKECASE/`) |
| `rt1_final_numbers.py` | the consolidated numbers quoted above |
