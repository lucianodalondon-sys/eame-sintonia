# RT2 — INDEPENDENT RED TEAM, AGRONOMY LENS

Target claim, verbatim from `ENGINE/answer_sheet.py` run today (2026-09-06):

> "In the 28 days to 2026-09-06, official scouts scored 1168 visits for damaging olive-fly
> infestation across 469 monitored olive sites in Toscana. 34 of those sites had it present;
> 435 did not." — with 8 of 10 provinces passing the publication gate and the classes
> "TYPICAL / LOWER / HIGHER relative to the same window in prior seasons".

I did not write this code. Everything below was measured, not argued. Scripts are in
`C:/cert-v2-disease-pressure/data/experiments/DISEASE-INTELLIGENCE-ITALY/CERT-V2/REDTEAM/`.
Nothing in `ENGINE/`, `CASES/` or `italia-portale/` was modified; the one monkey-patch
(RT2-A10) is in-memory only. Two read-only GET sweeps were made against the pilot's own source
(`agroambiente.info.regione.toscana.it`) to recover strata the pilot discarded at collection
time; the cache is in `REDTEAM/DIFESA/`.

Arithmetic of the headline, re-derived independently (`rt2_a6`, and the check at the end of
this file): the window 2026-08-10..2026-09-06 holds **1201** raw var -1002 rows; the
denominator guard drops **8**; **1** has an unreadable value; **1192** survive; **24** of those
are Prato, which is `UNKNOWN_NO_DATA`, leaving **1168** — the headline number. **476** distinct
`id_field` are in the window, **469** outside Prato, so the phrase "monitored olive sites in
Toscana" silently excludes Prato's **7**. The three numbers in the sentence are internally
consistent and correctly kept apart. I could not break the arithmetic.

---

## SUMMARY TABLE

| # | Accusation | Reproduced | Impact |
|---|---|---|---|
| A1 | The WHEAT case is not Septoria. It is powdery mildew. | YES | **FATAL** |
| A2 | The published olive variable is the lagging one; the actionable one says something different | YES | **MAJOR** |
| A3 | "INCIDENCE" changed denominator from FRUIT to SITE and kept the word | YES | **MAJOR** (wording) / NONE (class) |
| A4 | Everything published today sits inside the source's own "no action" band | YES | **MAJOR** (interpretation) |
| A5 | A "province" in 2026 is not the same set of groves as in the baseline | YES | **MAJOR** |
| A6 | Defence regime cannot be checked for 14 of the 20 baseline seasons | YES | **MAJOR** (as an unknown) |
| A7 | The scouting organisations changed, and organisations disagree | YES | **MAJOR** |
| A8 | The unit of var -1002 is percent only because n=100; it is not always | YES | MINOR |
| A9 | Impossible values (negative infestation) are read as "pest absent" | YES | MINOR |
| A10 | The denominator is joined on a key that repeats across seasons | YES | MINOR |
| A11 | One 28-day window for three pathosystems with different cycles | YES | MINOR (declared, and the engine refuses out of season) |
| A12 | "TYPICAL/LOWER/HIGHER" — today the instrument publishes only LOWER | YES | MINOR |
| B1 | LOWER and TYPICAL have no effect-size floor; HIGHER does | YES | **MAJOR** |
| B2 | A "positive site" is often one damaged drupe in a hundred, and it does not repeat | YES | **MAJOR** |
| B3 | Sampling effort explains the class better than the disease does | for VINE yes, for OLIVE **NO** | NONE for olive |
| B4 | Number of organisations explains the class | for OLIVE **NO** | NONE for olive |

---

# PART 1 — AGRONOMY

## A1 — FATAL · The WHEAT case is powdery mildew, filed and reported as Septoria.

**CLAIM.** `CASES/FRUMENTO-SEPTORIA-TOSCANA`, published everywhere in the certification as
"WHEAT x Septoria x Toscana", collects and publishes `id_survey_var 372`. That variable is not
Septoria. The wrong disease is in the box.

**METHOD.** Read `CASES/FRUMENTO-SEPTORIA-TOSCANA/collection_index.json` — the pilot's own
metadata, already on disk — and confirmed against the live source
(`crop=19`, `survey_schema=74`). Commands are in this file's transcript; no script was needed
because the answer is in the pilot's own index.

**REPRODUCED: YES.**

**NUMBERS.**

- `survey_schema 74` on `crop 19 (Frumento)` is named by the source **"Oidio, Septoria e
  Fusariosi"** — one schema, three diseases. The schema does not identify the issue.
- The schema declares **8** variables. The pilot collected **1**:

| var | source name | collected by the pilot? |
|---|---|---|
| 371 | Localizzazione Oidio | no |
| **372** | **Intensità Oidio** | **YES — this is the published series** |
| 384 | Frequenza Oidio | no |
| 381 | Localizzazione Septoria | no |
| **382** | **Intensità Septoria** | **no** |
| **385** | **Frequenza Septoria** | **no** |
| 383 | Intensità Fusariosi | no |
| 386 | Frequenza Fusariosi | no |

- `collection_index.json["requests"]` contains exactly one distinct `var`: **372**.
- The Septoria code tables are **already inside the pilot's own collection index** — var 382
  (1592 Nessuna, 1594 "5 - lieve", 1595 "10 - media", 1596 "25 - grave", 1597 "50 -
  gravissima", 1598 "75 - completa") and var 385 (1634 Nessuna, 1635 "Bassa <5%", 1636 "Media
  5-25%", 1637 "Alta >25%"). The pilot downloaded the Septoria metadata, named the directory
  after Septoria, and fetched the Oidio column.
- The two series are not interchangeable. Over seasons 2019 + 2022 + 2025, the same **1316**
  visit rows carry:
  - **var 372 (Oidio, the published one)**: 1303 "Nessuna", 13 "5 - lieve" — **13 of 1316
    (0.99%)** positive.
  - **var 382 (Septoria, never collected)**: 404 "Nessuna", 601 "5 - lieve", 266 "10 - media",
    42 "25 - grave", 3 "50 - gravissima" — **912 of 1316 (69.3%)** positive, and **45 of 1316
    (3.4%)** at "25 - grave" or worse.
- Consequence for the certification's own conclusion. The wheat case is used as "the first case
  this pipeline was not built for" and as a negative control. It is neither: it is a
  near-all-zero column (**487 of 5,817 archive rows non-"Nessuna", 8.37%** — 299 "5 - lieve",
  153 "10 - media", 32 "25 - grave", 3 unresolved) standing in for a
  disease that is present in most Tuscan wheat visits. The published `outcomes_v372.json`
  reports SITE_INCIDENCE 0.000 in 6 of 14 seasons; on Septoria that would have been impossible.

**IMPACT: FATAL** for the wheat cell and for every sentence in the certification that names
Septoria. It does not touch the olive claim.

**WHAT SURVIVES.** The *machinery* the wheat case exercised — the code-vs-magnitude guard
(`assert_scale_decodes`), the word-ladder extension — is unaffected; those are real and they
work. What does not survive is any statement of the form "the engine generalised to wheat x
Septoria". It generalised to wheat x oidio, on a column that is 99% "Nessuna". Renaming the
directory does not fix it; the Septoria columns (382, 385) have to be collected and the case
re-run before any wheat sentence is published.

**Secondary defect found in the same case.** The source's own label for code 1629 is
`"50 - gravissina"` — a typo for *gravissima*. The word ladder in `CASES/run_case.py` has no
entry for either spelling, so the code is UNRESOLVED and the numeric fallback reads the **code
id** as a magnitude. **3 rows in 2024** carry it, and the published artifact
`CASES/FRUMENTO-SEPTORIA-TOSCANA/outcomes_v372.json` therefore records
`"2024": {"SITE_INCIDENCE": 0.2292, "SITE_MAX_MEAN": 34.3958}` — a mean of site maxima of 34.4
on a scale whose top resolved rank is 3. `1629 / 48 sites = 33.9`. `current_pressure()` is
immune (it runs the variable in ORDINAL mode and returns `None` for an unresolved code), so the
published *classes* are unaffected; the published *season table* is not. IMPACT: MINOR, but it
is a live instance of the exact failure the pilot says it fixed.

---

## A2 — MAJOR · The pilot published the receipt, not the decision.

**CLAIM.** `crop 2 / survey_schema 1` is named by the source **"Infestazione Mosca"** and
derives three summaries from the same destructive fruit sample:

- `-1001 attiva` — "Infestazione Attiva", the live, still-killable population;
- `-1002 dannosa` — "Infestazione Dannosa", damage already inflicted on the drupe;
- `-1003 totale`.

A Bactrocera spray decision is taken on **attiva**. **Dannosa** is what is left after the
decision was not taken. The pilot publishes **-1002**.

**METHOD.** `REDTEAM/rt2_a3_lagging_vs_actionable.py` — joins the two variables on `id_survey`
and then re-runs `ENGINE/current_pressure.py` unchanged on -1001.

**REPRODUCED: YES.**

**NUMBERS.** Over **50,794** visits carrying both variables readably:

- `attiva > dannosa`: **21,234 / 50,794 (41.8%)**
- `attiva == dannosa`: **20,072 / 50,794 (39.5%)**
- `attiva < dannosa`: **9,488 / 50,794 (18.7%)**
- **`attiva` present while `dannosa` reads zero: 15,095 / 50,794 (29.7%)**. The engine's rule is
  `INCIDENCE = share of sites whose max value > 0`, so it files every one of those 15,095 visits
  as *no infestation*.

The disagreement is phenological, not random — share of visits with a positive reading, by month:

| month | visits | attiva > 0 | dannosa > 0 |
|---|---|---|---|
| 6 | 364 | 0.0577 | 0.0027 |
| 7 | 11,852 | 0.4381 | 0.0256 |
| 8 | 16,463 | 0.5273 | 0.2555 |
| 9 | 15,914 | 0.6847 | 0.5425 |
| 10 | 6,191 | 0.7007 | 0.6695 |

In July the published variable sees **2.6%** of visits while the actionable one sees **43.8%**.
That is the structural reason the pilot's C26 finding (HIGHER firing off four groves out of 119
on 2026-07-15) happened at all: it was percentiling a variable that is blind in July.

Today's sheet, same engine, same day, same window, only the variable changed:

| province | -1002 dannosa (published) | -1001 attiva |
|---|---|---|
| Arezzo | 0.000 | **0.2941** (5 of 17 groves) |
| Firenze | 0.000 | **0.1644** (12 of 73) |
| Grosseto | 0.0577 | 0.3694 |
| Livorno | 0.1169 | 0.5844 |
| Lucca | 0.000 | **0.5000** (7 of 14) |
| Massa-Carrara | 0.300 | 0.900 |
| Pisa | 0.1111 | 0.6444 |
| Pistoia | 0.000 | 0.0625 |
| Siena | 0.1311 | 0.5246 |

**IMPACT: MAJOR.** Not because the class moves — it does not (see WHAT SURVIVES) — but because
the published **value** is presented as "the pressure". Question 3 of the answer sheet renders
Arezzo, Firenze, Lucca and Pistoia as **0.000**, and a reader takes that as "no olive fly".
The source, on the same visits, says half the Lucca panel and 29% of the Arezzo panel carry a
live, still-killable population. If the product of this instrument is an advisory, publishing
the lagging variable is publishing the one number a grower can no longer act on.

**WHAT SURVIVES.** The **class** is robust to the choice: running `current_pressure` on -1001
gives **the identical class in 9 of 9 classified provinces** (8 LOWER, Massa-Carrara TYPICAL,
Prato UNKNOWN). So "pressure is lower than usual" survives; "the incidence is 0.000" does not.

---

## A3 — MAJOR (wording) · The word INCIDENCE changed denominator and kept the word.

**CLAIM.** In agronomy, incidence is *affected units / units examined* at a stated unit. The
source measures exactly that at the FRUIT level: var -1002 is a reading on a destructive sample
whose size the source declares in `var 1 "tot" — "Olive campionate"`. The engine discards the
magnitude, computes *share of SITES whose maximum reading exceeds zero*, and publishes it under
`METRIC: "INCIDENCE"`. The denominator moved from fruit to site; the word did not.

**METHOD.** `REDTEAM/rt2_a1_variable_semantics.py`, `REDTEAM/rt2_a5_incidence_word_and_metric.py`.

**REPRODUCED: YES.**

**NUMBERS.**

- `var 1` is declared: `{"id_survey_var": 1, "var_name": "tot", "description": "Olive
  campionate"}`, and `collection_index.json` declares `DENOMINATOR_VAR: 1`. So the source **does**
  publish a denominator and the pilot **does** wire it up. The rate is a rate.
- `var 1` is **100** in **48,195 of 52,077 (92.55%)** of visits, 0 in **2,066 (3.97%)**, and one
  of 1,880 other values otherwise.
- The engine's own units string is honest — `"share of monitored sites with the issue present"` —
  but the machine-readable field it emits is `METRIC: "INCIDENCE"`, and
  `CASES/effort_confound.py` line 43 comments the same quantity `# INCIDENCE, as published`.

**IMPACT: MAJOR on the wording, NONE on the class.** Re-running the identical engine with
`metric="SEVERITY"` (the mean of the site-max readings, i.e. the source's own magnitude)
changes **0 of 10** provinces:

| province | INCIDENCE class / value | SEVERITY class / value | severity baseline median |
|---|---|---|---|
| Arezzo | LOWER 0.000 | LOWER 0.000 | 0.667 |
| Firenze | LOWER 0.000 | LOWER 0.000 | 1.395 |
| Grosseto | LOWER 0.0577 | LOWER 0.109 | 1.574 |
| Livorno | LOWER 0.1169 | LOWER 0.221 | 4.854 |
| Lucca | LOWER 0.000 | LOWER 0.000 | 5.115 |
| Massa-Carrara | TYPICAL 0.300 | TYPICAL 0.900 | 2.600 |
| Pisa | LOWER 0.1111 | LOWER 0.220 | 4.606 |
| Pistoia | LOWER 0.000 | LOWER 0.000 | 2.667 |
| Siena | LOWER 0.1311 | LOWER 0.213 | 1.723 |

**WHAT SURVIVES.** The metric is defensible as a *detection rate*; it just must not be called an
incidence, because the source has a real one and it is being thrown away. Replace the key
`INCIDENCE` with `SITE_DETECTION_RATE` and the sentence becomes true.

---

## A4 — MAJOR · Everything published today is inside the source's own "no action" band.

**CLAIM.** The word "damaging" in the headline carries an economic implication. The source
attaches its own colour legend to this exact variable, embedded in `collection_index.json`:

```
0     -> "Nessuna Infestazione"   #FFFFFF
0.01  -> "0-6%"                   #4CAF50  green
6     -> "7-9%"                   #FFEB3B  yellow
10    -> ">=10%"                  #F44336  red
```

**METHOD.** `REDTEAM/rt2_a2_unit_and_impossible_values.py`, `REDTEAM/rt2_a5_...py`.

**REPRODUCED: YES.**

**NUMBERS, published window 2026-08-10..2026-09-06.**

| province | sites | positive | sites >= 6% (yellow) | sites >= 10% (RED) | highest reading anywhere |
|---|---|---|---|---|---|
| Arezzo | 17 | 0 | 0 | 0 | 0.0 |
| Firenze | 73 | 0 | 0 | 0 | 0.0 |
| Grosseto | 156 | 9 | 0 | 0 | 5.0 |
| Livorno | 77 | 9 | 0 | 0 | 5.0 |
| Lucca | 14 | 0 | 0 | 0 | 0.0 |
| Massa-Carrara | 10 | 3 | 0 | 0 | 5.0 |
| Pisa | 45 | 5 | 0 | 0 | 3.0 |
| Pistoia | 16 | 0 | 0 | 0 | 0.0 |
| Prato | 7 | 0 | 0 | 0 | 0.0 |
| Siena | 61 | 8 | 0 | 0 | 3.0 |
| **TOTAL** | **476** | **34** | **0** | **0** | **5.0** |

**0 of 476** monitored sites reach the source's yellow band; **0 of 476** reach red. The single
worst grove in Tuscany read 5% of sampled drupes.

And the *baseline* is in the same band: the province-level severity medians for this window
across 20 seasons are 0.667 – 5.115 % of drupes — all green. So `LOWER_THAN_USUAL` is a
comparison between two states that the source itself paints as requiring no action.

Over the whole archive, the same legend applied to all **51,026** readable -1002 values:
`0 Nessuna` **33,652 (65.95%)**, green 0–6 **11,284 (22.11%)**, yellow 6–10 **2,729 (5.35%)**,
red >=10 **3,361 (6.59%)**. So the binary `>0` test pools the 22.11% the source calls green with
the 6.59% it calls red, and calls all of it "the issue present".

**IMPACT: MAJOR on interpretation.** The error here is not alarmism — it is *false precision*.
The honest headline for 6 September 2026 is "nothing anywhere in Tuscany is above the source's
own lowest action band", and a percentile class is a decorative way of not saying it.

**WHAT SURVIVES.** The class direction (LOWER) is correct and consistent with the raw table.
Nothing in the archive contradicts "less than usual". What must be added beside it is the
absolute band, which the engine has and does not print.

---

## A5 — MAJOR · A "province" in 2026 is not the same set of groves as in the baseline.

**CLAIM.** The baseline is defined as "the same calendar window in prior seasons, same
province". If the panel rotates, that compares places, not years.

**METHOD.** `REDTEAM/rt2_b3_panel_orgs_effort.py` (overlap), `REDTEAM/rt2_b4_matched_panel.py`
(is the rotation real, and the matched-grove counterfactual).

**REPRODUCED: YES.**

**NUMBERS.**

First, the identifier is genuine. `id_field` persists across seasons — whole-season Jaccard by
year lag: lag 1 **0.534** (20 pairs), lag 2 0.328, lag 3 0.216, lag 5 0.142, lag 10 0.051,
lag 15 0.033, lag 20 0.012. A re-issued identifier would give ~0 at lag 1. **2,682** distinct
groves ever appear; a season carries 217–541 of them. The rotation is real turnover.

Overlap of the 2026 window panel with the baseline seasons, same window:

| province | 2026 sites | median Jaccard vs the 20 baselines | median SHARED groves |
|---|---|---|---|
| Arezzo | 17 | 0.037 | 2.0 |
| Firenze | 73 | 0.162 | 19.0 |
| Grosseto | 156 | 0.016 | 4.0 |
| **Livorno** | 77 | **0.000** | **0.0** |
| Lucca | 14 | 0.064 | 2.0 |
| Massa-Carrara | 10 | 0.079 | 1.5 |
| Pisa | 45 | 0.011 | 1.0 |
| **Pistoia** | 16 | **0.000** | **0.0** |
| **Prato** | 7 | **0.000** | **0.0** |
| Siena | 61 | 0.131 | 12.5 |

Median year-on-year Jaccard over all provinces: **0.524** across **167** adjacent-season pairs.
About half the panel turns over every year, so after twenty years essentially nothing is shared.

**The counterfactual.** Recompute each baseline season using only the groves it shares with the
2026 window panel (paired comparison, same places, same calendar):

| province | current | class AS PUBLISHED (base_n) | class MATCHED (matched base_n) |
|---|---|---|---|
| Arezzo | 0.0000 | LOWER (20) | **TYPICAL** (6) |
| Firenze | 0.0000 | LOWER (20) | LOWER (14) |
| Grosseto | 0.0577 | LOWER (20) | **UNKNOWN_NO_BASELINE** (2) |
| Livorno | 0.1169 | LOWER (20) | **UNKNOWN_NO_BASELINE** (1) |
| Lucca | 0.0000 | LOWER (20) | **UNKNOWN_NO_BASELINE** (3) |
| Massa-Carrara | 0.3000 | TYPICAL (8) | **UNKNOWN_NO_BASELINE** (1) |
| Pisa | 0.1111 | LOWER (20) | **UNKNOWN_NO_BASELINE** (1) |
| Pistoia | 0.0000 | LOWER (20) | **UNKNOWN_NO_BASELINE** (0) |
| Siena | 0.1311 | LOWER (20) | LOWER (17) |

**7 of the 9 classified provinces change class.** Six of them fall to
`UNKNOWN_NO_BASELINE` because fewer than `MIN_BASE = 5` prior seasons contain `MIN_SITES = 8` of
today's groves.

And the longitudinal panel that would support a like-for-like statement barely exists — groves
in the 2026 window that also appear in the window in >= 5 prior seasons:

| province | 2026 sites | of which longitudinal | >= 8? |
|---|---|---|---|
| Arezzo | 17 | 9 | YES |
| Firenze | 73 | 29 | YES |
| Grosseto | 156 | 6 | no |
| Livorno | 77 | **1** | no |
| Lucca | 14 | 7 | no |
| Massa-Carrara | 10 | 3 | no |
| Pisa | 45 | 3 | no |
| Pistoia | 16 | **0** | no |
| Prato | 7 | **0** | no |
| Siena | 61 | 18 | YES |

**3 of 10** provinces have a real panel. Livorno's published sentence — LOWER_THAN_USUAL, value
0.1169, baseline median 0.8889, 20 baseline seasons — rests on a comparison in which the typical
baseline season shares **zero** groves with today's panel and exactly **one** grove is present in
five or more prior seasons.

**IMPACT: MAJOR**, and it is the strongest single objection to the olive claim after A1. The
word "usual" carries a place. It does not have one here.

**WHAT SURVIVES.** Firenze and Siena survive the matched-grove test unchanged, and Arezzo only
softens to TYPICAL. If the claim is restated as "*this year's monitored network reads lower than
the network read at this date in prior seasons*" it is defensible on all 8. If it is stated as
"*pressure in Livorno is lower than usual*", the province-level reading is not supported by a
province-level panel.

**Important correction against my own case.** I looked for the obvious mechanism — that newly
recruited groves are cleaner — and **did not find it**. See A5b.

### A5b — the recruitment-bias mechanism does NOT reproduce (a survival)

`REDTEAM/rt2_b5_new_groves_and_orgs.py`. Site incidence in the 10 Aug–6 Sep window pooled over
2006–2026, by how many prior seasons the grove had:

| tenure | site-windows | positive | incidence |
|---|---|---|---|
| first appearance | 2,482 | 1,192 | **0.4803** |
| 1–2 prior | 2,389 | 1,339 | 0.5605 |
| 3–5 prior | 1,384 | 755 | 0.5455 |
| > 5 prior | 1,060 | 541 | **0.5104** |

New groves read lower than >5-prior groves in only **7 of 15** seasons with >= 8 sites in both
buckets, mean difference **−0.0215**. That is not a bias I can convict on. The panel rotation is
a *comparability* problem, not a demonstrated downward bias.

---

## A6 — MAJOR (as an unknown) · The defence regime cannot be checked for 14 of the 20 baseline seasons.

**CLAIM.** `CASES/collect_generic.py` calls the source with `"difesa": "all"` for every case, so
the archive on disk carries **no defence regime at all**. Bactrocera is the pathosystem where the
regime matters most: an organic grove has spinosad bait and kaolin, an integrated grove has the
full insecticide set. Pooling them and then percentiling seasons is only valid if the mix is
constant, and the pilot never measured it.

**METHOD.** `REDTEAM/rt2_c1_fetch_difesa.py` (read-only collection of the stratum the pilot
discarded; cache in `REDTEAM/DIFESA/difesa_map.json`), `REDTEAM/rt2_c2_difesa_analysis.py`.

**REPRODUCED: YES for the gap. NO for a demonstrated bias.**

**NUMBERS.** The source offers `difesa ∈ {all, bio, integrato, integrato_volontario}` and it is a
real server-side filter (2025, var -1002: all 3553, bio 644, integrato 1897,
integrato_volontario 0; a bogus value returns 0 rows with `ok:true`, so the filter must never be
trusted blind — the labels used here come from the source's own filter table).

Coverage, after the engine's denominator guard:

| season | rows | bio | integrato | NOT_DECLARED | labelled share | bio share of labelled |
|---|---|---|---|---|---|---|
| 2006–2017 | 2,210–5,029 each | **0** | **0** | all | **0.0000** | — |
| 2018 | 4,861 | 1 | 0 | 4,860 | 0.0002 | — |
| 2019 | 3,917 | 0 | 0 | 3,917 | 0.0000 | — |
| 2020 | 4,420 | 924 | 3,445 | 51 | 0.9885 | 0.2115 |
| 2021 | 3,649 | 935 | 2,618 | 96 | 0.9737 | 0.2632 |
| 2022 | 3,607 | 828 | 2,649 | 130 | 0.9640 | 0.2381 |
| 2023 | 2,850 | 843 | 1,783 | 224 | 0.9214 | 0.3210 |
| 2024 | 3,922 | 832 | 2,921 | 169 | 0.9569 | 0.2217 |
| 2025 | 3,286 | 632 | 1,646 | 1,008 | **0.6932** | 0.2774 |
| 2026 | 2,870 | 392 | 1,387 | 1,091 | **0.6199** | 0.2203 |

Two separate problems. (i) **14 of the 20 baseline seasons carry no regime at all**, so the
stability of the mix over the baseline is **NOT KNOWN** and cannot be made known from this
source. (ii) The coverage that did exist has **collapsed**, from 98.9% in 2020 to **62.0%** in
2026 — and the collapse lands squarely on the provinces being published: in the 2026 window,
**74 of Livorno's 77 sites** and **39 of Pisa's 45** are `NOT_DECLARED`.

The regime effect itself, measured where it can be (2020–2026, same province, same 28-day
window, >= 8 sites in both regimes, **25** such province-windows): biologico reads higher in
**11 of 25**; **median difference +0.000**, mean **+0.005**, range **−0.288 … +0.358**.

**IMPACT: MAJOR as an unknown, not as a proven bias.** The median effect is zero, so I cannot
convict the baseline of a regime shift. But individual province-windows swing by up to 0.358 —
larger than most of the year-to-year gaps the class is built on — and for 14 of 20 baseline
seasons the mix is unmeasurable in principle.

**WHAT WOULD SETTLE IT.** Nothing in this source. The regime would have to come from the
regional register of *aziende in biologico / produzione integrata* joined to `id_field`, or from
the Servizio Fitosanitario's own grove register. Until then the correct output field is
`DEFENCE_REGIME_MIX: NOT_KNOWN for baseline seasons 2006-2019`, published, not omitted.

**WHAT SURVIVES.** `survey_schema 3` on crop 2 is named "Trattamenti mosca" and was never
touched by this pilot. If the question is "was the low reading caused by spraying?", that schema
is where the answer lives and it is one collector call away.

---

## A7 — MAJOR · The scouting organisations changed, and organisations disagree with each other.

**CLAIM.** An organisation is a protocol: different crews, different grove lists, different
diligence. If the mix changes, the province series changes with it.

**METHOD.** `REDTEAM/rt2_b3_panel_orgs_effort.py`, `REDTEAM/rt2_b5_new_groves_and_orgs.py`.

**REPRODUCED: YES.**

**NUMBERS.**

Organisations active in the 10 Aug–6 Sep window, by season: 6 (2006), 4, 5, 6, 6, 5,
**2 (2012–2014)**, 3 (2015–2019), **12 (2020)**, 11, 11, 9, 11, 11, **9 (2026)**. **19** distinct
organisations ever. There is a hard era break at 2020 (the count quadruples) and continuous
churn: 2026 gained "PIF Chianti Classico" and lost Apot, Biodistertto FIesole and ERATA.

Per province, 2026 vs baseline median: Siena **6 vs 2**, Pisa **4 vs 1**, Firenze 4 vs 2,
Grosseto 3 vs 1, Pistoia 2 vs 1.5 — but Livorno **2 vs 3** and Lucca **1 vs 2.5**.

Do organisations disagree? Within one province and the *same four weeks*, restricted to
organisations with >= 8 sites each — **44** such province-windows:

- median spread between the highest- and lowest-reading organisation: **0.191**
- maximum spread: **0.765**

Worked examples, all inside one province and one 28-day window:

- 2020 Grosseto: `ota 0.000 (n=18)`, `OLMA 0.291 (n=127)`, `Apot 0.480 (n=25)`, `org 0.625 (n=8)`
- 2020 Pistoia: `ota 0.455 (n=11)` vs `Apot 1.000 (n=15)`
- 2021 Firenze: `ota 0.290 (n=31)`, `montalbano 0.455 (n=11)`, `Assoprolfipo 0.889 (n=18)`
- 2008 Firenze: `montalbano 0.000 (n=9)` vs `aprol 0.556 (n=9)`

**IMPACT: MAJOR.** The observer explains up to 0.765 of the published quantity inside a single
province-month — larger than the gap between today's Livorno value (0.1169) and its baseline
median (0.8889) is *not*, but comfortably larger than most of the class-deciding gaps elsewhere.
Combined with A5 (the panel rotates) this is one confound, not two: the new groves arrive
attached to new organisations.

**WHAT SURVIVES.** The *number of organisations* does **not** rank the olive seasons — see B4.
So the org mix is a plausible mechanism whose net effect on the season ranking I could not
demonstrate.

---

## A8 — MINOR · The unit of var -1002 is a percentage only because n is usually 100.

**CLAIM.** The source's legend labels this variable in per cent. Whether the served number is a
percentage or a raw count of infested drupes is undecidable in 92.55% of visits, because in
those the denominator is exactly 100 and the two are the same number.

**METHOD.** `REDTEAM/rt2_a1_variable_semantics.py`, `REDTEAM/rt2_a2_unit_and_impossible_values.py`.

**REPRODUCED: YES.**

**NUMBERS.** Among **17,283** positive visits with a usable denominator:

- denominator exactly 100: **16,791 / 17,283**, and all 16,791 are trivially consistent with both
  readings.
- denominator **not** 100: **492 / 17,283**. Of those, only **165 / 492** are an exact multiple
  of `100 / tot`, i.e. only a third are readable as a percentage of the declared sample.
  Examples: `(dannosa 5.0, tot 24)`, `(5.0, 50)`, `(3.0, 94)`, `(1.0, 107)`, `(2.0, 80)` — none of
  which is a valid percentage of its own denominator, and `(3.0, 1000)`.
- By denominator: tot=200 → **60/60** consistent; tot=50 → 47/61; tot=60 → **6/31**; tot=150 →
  **3/20**; tot=102 → **0/17**; tot=101 → **0/13**; tot=99 → **0/8**.

**IMPACT: MINOR.** It does not touch the published INCIDENCE (a `>0` test is invariant to the
scale factor). It does touch any SEVERITY reading and any sentence that says "% of olives".

**WHAT SURVIVES.** The censused claim that this series has "a true fixed denominator (n=100
destructively sampled fruit per visit)" is right for **92.55%** of visits and wrong for the rest,
and the exceptions are internally inconsistent. State the denominator as *"100 drupes in 92.55%
of visits; 3.97% sampled nothing and are dropped; the remaining 3.48% carry a denominator whose
relation to the served value does not check out."*

---

## A9 — MINOR · Impossible values, and negatives read as "pest absent".

**METHOD.** `REDTEAM/rt2_a2_unit_and_impossible_values.py`.

**REPRODUCED: YES.**

**NUMBERS**, over **50,801** readable values of var -1002:

- **negative**: 3 — `−3.0` (2025-09-03, Livorno), `−1.0` (2025-09-09, Pisa), `−1.0` (2026-07-22,
  Livorno). Neither a percentage nor a count of infested drupes can be negative.
- **greater than 100**: 2 — `107.0` with tot 100 (2014-10-08, Arezzo), and `140.0` **with tot 10**
  (2025-08-06, Firenze).
- companion variables: `-1001 attiva` min −2.0 max 101.0 (1 negative, 1 over 100);
  `-1003 totale` min −3.0 max 254.0 (3 negative, **38** over 100).

The engine's test is `value > 0`, so each negative is filed as a **confirmed absence** of the
pest — the exact failure mode `contracts.Missing.NEVER_ZERO` exists to prevent, arriving through
a different door than the one that was guarded.

**IMPACT: MINOR** — 3 visits in 50,801, none inside the published window.

**WHAT SURVIVES.** Everything. But the correct behaviour for a physically impossible value is
`REFUSED`, not silent inclusion at the "clean" end of the scale.

---

## A10 — MINOR · The denominator is joined on a key that repeats across seasons.

**CLAIM.** `denominator_guard()` builds one dictionary over every year's file,
`den[r["id_survey"]] = ...`, then tests `den.get(r.get("id_survey"))`. `id_survey` is unique
*within* a season file and re-used *across* seasons.

**METHOD.** `REDTEAM/rt2_a6_denominator_join_key.py` (measure), `REDTEAM/rt2_a7_fixed_key_counterfactual.py`
(in-memory monkey-patch to a `(season, id_survey)` key; nothing on disk changed).

**REPRODUCED: YES.**

**NUMBERS.** Var -1002 has **79,251** rows and only **52,025** distinct `id_survey` strings.
Building the guard's dictionary exactly as the engine does (raw JSON type, no coercion):

- distinct keys **52,250**; keys written by more than one season **14,649**; var-1 rows involved
  in a collision **41,650**;
- collisions where the two seasons **disagree** about whether the denominator is usable: **1,759**;
- var -1002 visits whose keep/drop verdict can therefore flip: **2,499**, all of them in
  **2006–2019**.

The archive is accidentally half-protected: the source changed the JSON type of `id_survey` at
the 2019/2020 boundary (int through 2019, string from 2020), and a Python dict keys `5` and
`"5"` separately, so the two eras cannot collide with each other.

Guard effect overall: **3,397 / 79,251** visits dropped (the engine's docstring says 3,026 have a
zero denominator; the extra 371 are unreadable/missing). Inside the published window:
**8 / 1,201**.

Counterfactual with the season-scoped key: dropped rises 3,397 → **3,558**;
**today's cells that differ: 0 / 10**; walk-forward hindcast at 6 September 2006–2025:
**1 / 200 cells differ** — (2021, Grosseto, HIGHER → TYPICAL).

**IMPACT: MINOR.** Real defect, negligible published effect. Same shape as the pilot's own C15.

---

## A11 — MINOR · One 28-day window for three pathosystems.

**METHOD.** `REDTEAM/rt2_a4_phenology_window.py`.

**REPRODUCED: YES**, but it is a declared parameter and the engine behaves correctly out of
season.

**NUMBERS.** Weeks holding >= 0.5% of that case's visits, and what 4 weeks is worth:

| case | ISO weeks | calendar | readable visits | 28 days as a share of the scouting season |
|---|---|---|---|---|
| OLIVE x Bactrocera | 27–43 | ~30 Jun – 26 Oct | 78,019 | **0.24** |
| VINE x oidio | 17–38 | ~21 Apr – 21 Sep | 35,064 | **0.18** |
| WHEAT x "Septoria" (=oidio) | 14–25 | ~31 Mar – 22 Jun | 5,810 | **0.33** |

The olive positive share climbs monotonically through the campaign — w27 8/1157, w32 937/6015,
w36 2902/6294, w43 421/674 — so a window straddling weeks 33–36 sits on the steepest part of the
ramp and the reading depends on where inside the window the visits fell.

Three consequences, and only the first is a problem:

1. **Wheat.** A 28-day window is a third of the entire wheat scouting season, and the T2 (flag
   leaf) decision window for a Septoria programme is about 3 weeks. A 28-day trailing window
   delivers its first full reading after the decision it would inform. The engine's answer on
   2026-09-06 — `UNKNOWN_NO_DATA` in all 5 provinces, latency 81 days — is correct behaviour, but
   the window length is wrong for the crop even in season.
2. **Vine.** On 6 September the vine window (weeks 33–36) is the tail of the oidio season
   (peak week 27, 2,445 visits; week 36, 944). See B1 for what the engine emits there.
3. **Olive.** 24% of the campaign, four survey rounds at the weekly cadence these programmes run.
   Defensible.

**WHAT SURVIVES — and this one is a genuine failure of my own attack.** I predicted the window's
*internal* composition would be biased in 2026 and it is not (`rt2_b1`). Mean ISO week of the
visits inside the window, 2026 vs the baseline median, per province: shifts of −0.44 to +0.08
weeks, **mean |shift| 0.12 weeks**. Re-running the baseline restricted to only the ISO weeks 2026
actually has inside the window changes **0 of 9** classes. The calendar-alignment attack fails.

I also predicted that "dannosa" accumulates within a season and so a trailing window is really
season-to-date. **That is wrong too**: of 5,751 olive site-seasons that went positive,
**2,677 (46.5%)** later read zero again, and 9,846 of 70,151 consecutive visit pairs fell. The
variable is a fresh ~100-fruit sample each visit, so it is noisy, not cumulative. (For vine the
relapse rate is 404/519 = 0.778; for wheat 11/82 = 0.134.)

**IMPACT: MINOR** for olive and vine. The wheat window length is a real design problem but it is
downstream of A1 — the wheat case has to be rebuilt anyway.

---

## A12 — MINOR · "TYPICAL / LOWER / HIGHER" — today the instrument publishes only LOWER.

The claim advertises a three-way class. On 2026-09-06 the publication gate emits
(`CERT-V2/p4b_publication_gate_by_date.json`, re-run and confirmed):

```
PUBLISHED 8/10 : Arezzo, Firenze, Grosseto, Livorno, Lucca, Pisa, Pistoia, Siena
                 -> LOWER_THAN_USUAL, all eight
WITHHELD       : Massa-Carrara (would be TYPICAL; stability 0.644, coverage 0.19)
UNKNOWN        : Prato
```

No province is published TYPICAL and none HIGHER. The three-way phrasing describes the
instrument's vocabulary, not today's output. **IMPACT: MINOR**, but the sentence as written
implies a discrimination that today's sheet does not exhibit.

---

# PART 2 — FALSE-SIGNAL AVOIDANCE

## B1 — MAJOR · `HIGHER` has an effect-size floor. `LOWER` and `TYPICAL` do not.

**CLAIM.** `MIN_POSITIVE_SITES = 5` is applied in exactly one place:

```python
if st == HIGHER and (cur["n_sites"] * v) < min_positive_sites:
    st = TYPICAL
```

`LOWER_THAN_USUAL` and `TYPICAL_FOR_THE_DATE` can therefore be published on **zero** detections
against a baseline that is itself almost all zeros. `LOWER` is the word that today's entire
olive sheet is made of, and it is the word that can stop a spend.

**METHOD.** `REDTEAM/rt2_d1_false_signal.py`, cross-checked against the pilot's own
`CERT-V2/p4b_publication_gate_by_date.json`.

**REPRODUCED: YES.**

**NUMBERS.** Across six as-of dates in 2026 for both cases, **57** classified cells rest on
**<= 3 positive sites** and are classed something other than LOWER. The ones that matter are the
ones the pilot's own gate actually publishes:

**Exhibit 1 — OLIVE, 2026-08-01, gate publishes 6/10, all TYPICAL_FOR_THE_DATE:**

| province | class published | sites | positive sites |
|---|---|---|---|
| Arezzo | TYPICAL_FOR_THE_DATE | 17 | **0** |
| Firenze | TYPICAL_FOR_THE_DATE | 64 | **0** |
| Grosseto | TYPICAL_FOR_THE_DATE | 130 | 1 |
| Livorno | TYPICAL_FOR_THE_DATE | 40 | 2 |
| Pistoia | TYPICAL_FOR_THE_DATE | 9 | **0** |
| Siena | TYPICAL_FOR_THE_DATE | 44 | **0** |

Four provinces published as "typical for the date" for *damaging olive-fly infestation* with not
one grove of 17, 64, 9 and 44 respectively carrying a detection.

**Exhibit 2 — VINE, 2026-09-06.** `current_pressure` classifies **9 of 10** provinces —
5 TYPICAL and 4 LOWER — **every one of them on 0.0 positive sites**. Massa-Carrara is
`LOWER_THAN_USUAL` on **8** vineyards, **0** positive, **5** baseline seasons, percentile 0.200 —
which decomposes to exactly two of those five prior seasons also reading zero. "There is less
powdery mildew than usual in Massa-Carrara" is being derived from a 3-versus-2 split of five
prior Septembers in which nobody found any either.

**IMPACT: MAJOR — with one important mitigation.** The pilot's *publication gate*
(stability >= 0.80 AND historical coverage >= 0.60) blocks the whole vine sheet on that date:
`VINE 0/10`. So Exhibit 2 never reaches a reader. Exhibit 1 does: the olive TYPICALs on
2026-08-01 pass the gate and are published. The gate is doing real work, and it is not doing it
via the effect-size floor — the floor never fires on these cells because they are not HIGHER.

**WHAT SURVIVES.** The asymmetry is arguably deliberate and defensible — HIGHER triggers spending,
LOWER does not. But `TYPICAL_FOR_THE_DATE` on 0 of 64 groves is not a pressure statement, it is
a "nothing found" statement, and the sheet does not distinguish them. The fix is one line: apply
the same floor to every class, or emit `NOTHING_DETECTED` as its own state.

---

## B2 — MAJOR · A "positive site" is often one damaged drupe in a hundred, and it does not repeat.

**METHOD.** `REDTEAM/rt2_d1_false_signal.py`.

**REPRODUCED: YES.**

**NUMBERS.** Distribution of the site-max value among **3,827** positive site-windows
(10 Aug – 6 Sep, all seasons, 7,315 site-windows in total):

| site-max reading | count | share of positives |
|---|---|---|
| exactly 1 (one drupe in ~100) | 781 | **0.2041** |
| 2 | 619 | 0.1617 |
| 3–5 | 1,010 | 0.2639 |
| 6–9 (source YELLOW) | 595 | 0.1555 |
| >= 10 (source RED) | 805 | **0.2103** |

**79% of what the published metric counts as "the issue present" is below the source's own
action band.**

Reliability of the `>0` flag — same grove, consecutive visits <= 10 days apart, same season,
**59,720** pairs:

- the flag **flips** between the two visits: **8,898 / 59,720 = 0.1490**
- positive then zero, which cannot happen biologically (a damaged drupe does not heal):
  **2,985 / 59,720 = 0.0500**
- among visits reading **1–2** (one or two drupes in ~100), the next visit within 10 days reads
  **zero**: **2,077 / 7,810 = 0.2659**

That is exactly what binomial sampling of ~100 fruit predicts: at a true 1% infestation,
P(0 damaged in 100) ≈ 0.366. The `>0` flag is a **detection event with roughly 27% false-negative
rate at low true infestation**, not a state.

**IMPACT: MAJOR.** Today's Grosseto value is 9 positive of 156, Livorno 9 of 77, Siena 8 of 61.
On this measured flip rate, re-visiting the same groves a week later would move those counts by
several sites in either direction, and the percentile against a 20-season baseline is being read
to four decimal places.

**WHAT SURVIVES.** The direction. The measurement noise is symmetric and the baseline was built
with the same instrument, so it does not bias the *class*; it widens the uncertainty around it,
and no uncertainty is published. There is no confidence interval anywhere in the output.

---

## B3 — Effort confound: reproduced exactly, and it **does not** convict the olive case.

**METHOD.** `CASES/effort_confound.py` re-run unchanged through
`REDTEAM/rt2_b3_panel_orgs_effort.py`, plus a third arm on -1001 that the pilot never ran.

**REPRODUCED: YES — the pilot's numbers are exact.**

| case | EFFORT pairs / pos / rho | DISEASE pairs / pos / rho | verdict |
|---|---|---|---|
| OIDIO (var 39) | 36 / 36 / **+0.738** | 36 / 26 / **+0.229** | EFFORT WINS |
| BACTROCERA (var -1002) | 36 / 29 / **+0.252** | 36 / 35 / **+0.449** | disease exceeds effort |
| BACTROCERA attiva (var -1001) | 36 / 29 / +0.251 | 36 / 34 / +0.345 | disease exceeds effort |

The pilot's C11 / checkpoint-12 figures (+0.738 vs +0.229 for vine; +0.449 vs +0.252 for olive)
reproduce to three decimals from committed code. The extra arm on the actionable variable also
holds, with a smaller margin.

**IMPACT: NONE for olive.** I tried to make effort explain the olive class and failed.

---

## B4 — Does effort or organisation count rank the seasons? For olive, no.

**METHOD.** `REDTEAM/rt2_d1_false_signal.py`, part D1d. Per province, over the 10 Aug – 6 Sep
window of every season with >= 8 sites, Spearman between the published incidence and three
effort measures.

**REPRODUCED: YES (as a negative for olive, mixed for vine).**

| case | mean rho(inc, n_sites) | mean rho(inc, visits/site) | mean rho(inc, n_orgs) |
|---|---|---|---|
| OLIVE, 9 provinces, 9–21 seasons each | **+0.003** | **−0.113** | **−0.099** |
| VINE, 5 provinces, 8–14 seasons each | **−0.320** | −0.040 | **+0.213** |

For olive the strongest single-province effort correlation is Arezzo +0.475 on n_sites and
Firenze −0.499 on visits/site — opposite signs, no coherent story. For vine, Grosseto shows
rho(inc, n_orgs) = **+0.857** over 8 seasons, which is the kind of number that should stop a
publication on its own.

**IMPACT: NONE for the olive claim. Reinforces the pilot's own withdrawal of the vine case.**

---

# WHAT I COULD NOT BREAK

Listed with the numbers, because a red team that reports only its hits is not a red team.

1. **The headline arithmetic.** 1201 raw rows in the window → 8 dropped by the denominator guard
   → 1 unreadable → 1192 → minus Prato's 24 = **1168 visits**; **469** sites outside Prato
   (476 including it); **34** positive sites. All three reconcile. The 2026-09-06 correction
   that split "visits scored" from "sites with the issue present" is real and holds.

2. **The effort confound**, both directions, reproduced from committed code to three decimals
   (B3). The olive case genuinely has disease agreement (+0.449) above effort agreement (+0.252).

3. **The calendar-alignment attack fails.** Mean |shift| in the within-window mean ISO week,
   2026 vs baseline, is **0.12 weeks**; re-running the baseline on only the weeks 2026 actually
   has changes **0 of 9** classes (`rt2_b1`). I expected this to be the kill and it was not.

4. **The recruitment-bias mechanism fails.** New groves read 0.4803 (n=2,482) against 0.5104
   (n=1,060) for groves with >5 prior seasons; new reads lower in only **7 of 15** seasons, mean
   difference **−0.0215** (`rt2_b5`). The panel rotation is a comparability problem, not a
   demonstrated downward bias.

5. **The "dannosa accumulates" hypothesis is wrong.** 2,677 of 5,751 positive olive site-seasons
   (46.5%) later read zero again (`rt2_a4`). A trailing window is not a season-to-date
   accumulation on this variable.

6. **Variable choice does not move the class.** -1001 attiva vs -1002 dannosa: **0 of 9**
   classified provinces change (`rt2_a3`).

7. **Metric choice does not move the class.** INCIDENCE vs SEVERITY: **0 of 10** provinces change
   (`rt2_a5`).

8. **The denominator join-key defect does not move the class.** Season-scoped key: **0 of 10**
   today, **1 of 200** hindcast cells (`rt2_a7`).

9. **The class on 6 September does carry seasonal information.** Walk-forward hindcast classes
   at 6 September, cross-tabulated against the same province's site incidence in the last 28 days
   that season actually had (`rt2_b2`):

   | class published 6 Sep | cells | median season-end incidence |
   |---|---|---|
   | HIGHER_THAN_USUAL | 31 | **0.972** |
   | TYPICAL_FOR_THE_DATE | 56 | 0.896 |
   | UNKNOWN_NO_BASELINE | 47 | 0.889 |
   | LOWER_THAN_USUAL | 36 | **0.527** |

   Within-province rank correlation between the 6 September class and the season-end incidence:
   Arezzo +0.714, Firenze +0.836, Grosseto +0.336, Livorno +0.607, Lucca +0.575, Pisa +0.761,
   Pistoia +0.639, Siena +0.489 — **mean +0.620 over 8 provinces, 15 seasons each**. Only
   **3 of 36** LOWER cells ended the season in that province's worst third, and there is a median
   of **39 days** of scouting still to come after 6 September (min 13, max 57).

   Caveat that must travel with this number: the "outcome" is the *same instrument* read later,
   not an independent damage or yield record. It is internal consistency, not validation. **No
   independent register of olive-fly damage in Tuscany by province and season exists in this
   repository**, so the instrument's true skill is **NOT KNOWN**. What would settle it: the
   frantoio-level *resa* and *acidità* records, or the ARTEA / OP olive-oil quality returns, joined
   to province and season.

10. **The hindcast is not degenerate.** At 6 September across 2006–2025: 123 classified cells,
    H=31, TYPICAL=56, L=36, dominant class share **0.455** — DISCRIMINATING by the module's own
    0.75 threshold.

11. **The 15 post-cutoff rows, the season-completeness flag, the sha256 refusal and the
    `assert_outcome_admissible` gate** all behave as documented; I did not find a way past them.

12. **`Prato` is honestly UNKNOWN**, on 7 sites, on every date I tested, in both cases.

---

# THE THREE SENTENCES I WOULD NOT LET SHIP AS WRITTEN

1. **"WHEAT x Septoria x Toscana"** — it is wheat x *oidio*. `var 382` and `var 385` are the
   Septoria columns, they return data, their code tables are already in the pilot's own index,
   and they were never fetched. (A1, FATAL.)

2. **"…relative to the same window in prior seasons"** — same calendar window, largely *different
   groves*. Median shared groves between the 2026 window panel and the typical baseline season:
   Livorno **0**, Pistoia **0**, Prato **0**, Pisa **1**, Massa-Carrara **1.5**, Arezzo 2, Lucca 2,
   Grosseto 4, Siena 12.5, Firenze 19. Under a matched-grove baseline **7 of 9** classes change.
   (A5, MAJOR.)

3. **"scored N visits for damaging olive-fly infestation"** with values rendered as 0.000 — the
   source's *active* infestation variable, on the identical visits, reads 0.294 in Arezzo, 0.500
   in Lucca and 0.164 in Firenze, and **0 of 476** sites in the window reach the source's own
   lowest action band. Both facts belong beside the class and neither is printed. (A2 + A4, MAJOR.)
