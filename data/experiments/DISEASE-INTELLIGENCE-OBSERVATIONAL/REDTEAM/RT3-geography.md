# RT3 · RED TEAM · GEOGRAPHY

Independent lens. I wrote none of this code. My job was to put an observation in the wrong
place, or to show the tool cannot tell where a fact happened.

Target: `data/experiments/DISEASE-INTELLIGENCE-OBSERVATIONAL/engine/`
(`di_core.py`, `di_observe.py`, `di_report.py`, `run_pilot.py`, `di_render.py`, `di_adama.py`)
Raw: `data/experiments/DISEASE-INTELLIGENCE-ITALY/CASES/OLIVO-BACTROCERA-TOSCANA/RAW/`
AS_OF used throughout: `2026-09-06`, metric `ACTIVE_INFESTATION_COUNT`.

Scripts are in this folder, all prefixed `rt3_`. `rt3_lib.py` is the shared raw loader.
`rt3_05_counterfactual.py` writes a ~49 MB shadow copy of RAW under `REDTEAM/_shadow/` and
I deleted it afterwards; re-running the script recreates it.

## The denominators everything below is measured against

| thing | count |
|---|---|
| raw rows, 4 collected variables × 21 seasons × 84 files | 317,004 |
| visits, one per `(id_field, date)` | 79,251 |
| distinct `id_field` | 2,686 |
| distinct comuni (`admin_code`) | 187 |
| distinct `nome_area` values | 10 |
| distinct `name_5` sub-areas | 42 |
| visits in the current 28-day window (2026-08-10 … 2026-09-06) | 1,193 |
| groves in the current window | 478 |

The shipped baseline run, for reference:

```
province          rate%   n_vis  sites   drupes               hist  base_med%   matched   attention
Arezzo           0.1636      55     17     5500            TYPICAL     0.6418         6   MONITOR
Firenze          0.0664     241     73    24100   BELOW_HISTORICAL     1.4073        14   MONITOR
Grosseto         0.6575     320    157    34720  INSUFFICIENT_DATA     2.5627         2   NO_ESCALATION
Livorno          0.9216     153     77    15300  INSUFFICIENT_DATA     4.1552         1   NO_ESCALATION
Lucca            1.1509      53     14     5300  INSUFFICIENT_DATA     3.5238         3   INVESTIGATE
Massa-Carrara     0.566      40     10     5300  INSUFFICIENT_DATA     2.4008         1   NO_ESCALATION
Pisa               1.02      85     45     9196  INSUFFICIENT_DATA     2.8663         1   NO_ESCALATION
Pistoia          0.0278      36     16     3600  INSUFFICIENT_DATA     1.3308         0   NO_ESCALATION
Prato            0.0417      24      7     2400  INSUFFICIENT_DATA     0.6368         0   NO_ESCALATION
Siena            0.6909     186     61    18383   BELOW_HISTORICAL     1.2975        17   MONITOR
```

---

## ACCUSATION 1 — "`nome_area` disagrees with `admin_code`, so provinces are mislabelled"

**CLAIM (mine, going in):** the province string the engine groups by will disagree with the
ISTAT comune code, and some of those disagreements will be real mislabelling.

**METHOD:** `rt3_01_admin_vs_nomearea.py`, `rt3_02_vicchio_and_inventory.py`. Zero-pad
`admin_code` to 6 digits, take the first 3 as the ISTAT province, compare with `nome_area`
on all 79,251 visits. Classify every disagreement.

**REPRODUCED: NO** (for the "mislabelling" half).

**NUMBERS:**

- `admin_code` present and parseable: **79,251 / 79,251**. Non-Tuscan province prefix: **0 / 79,251**.
- `nome_area` agrees with the ISTAT province of `admin_code`: **77,850 / 79,251**.
- Disagrees: **1,401 / 79,251**. Every one of them is the 1992 Prato reform:

| `nome_area` | legacy code | comune | rows |
|---|---|---|---|
| Prato | 048009 | CARMIGNANO | 664 |
| Prato | 048047 | VAIANO | 228 |
| Prato | 048034 | PRATO | 224 |
| Prato | 048029 | MONTEMURLO | 222 |
| Prato | 048051 | POGGIO A CAIANO | 63 |

  All five comuni are in the province of Prato (100) today; the source still serves the
  legacy Firenze (048) code. **`nome_area` is the modern-correct answer here and
  `admin_code` is the stale one.**

- **Genuine mislabelled rows: 0 / 79,251.**
- Supporting checks, all clean: `name_3` equals `nome_area` on **79,251 / 79,251**;
  `admin_code_3` and `id_area` are 1:1 with `nome_area` (10 ↔ 10 ↔ 10); **0** comune codes
  appear under two `nome_area` values; **0** comune names carry two codes; **0** of the 42
  `name_5` sub-areas span two provinces.

**IMPACT: NONE.** No published number is wrong because of a `nome_area` ↔ `admin_code`
disagreement.

**WHAT SURVIVES:** the province label in this dump is internally consistent with the
comune code on every row, and the only divergence is a documented 1992 boundary change that
the source resolves the right way round.

### 1b — the prior audit's "30 rows of VICCHIO under Siena"

**CLAIM (from the previous audit, handed to me):** 30 rows where comune 48049 VICCHIO, a
comune of Firenze, is filed under Siena.

**METHOD:** `rt3_02_vicchio_and_inventory.py`. Searched **all 317,004 raw rows of all four
variables, undeduplicated**, three independent ways.

**REPRODUCED: NO.**

**NUMBERS:**

- rows with `admin_code` = 048049: **0 / 317,004**
- rows whose `name_4` contains "VICCHIO": **0 / 317,004**
- rows with `nome_area` = Siena and a non-052 `admin_code`: **0 / 317,004**
- rows with a 048 code filed anywhere other than Firenze or Prato: **0 / 317,004**

Province 048 in this dump holds 35 comuni, numbered exactly as legacy ISTAT numbered them
(048001 BAGNO A RIPOLI … 048050 VINCI, 048051 POGGIO A CAIANO). 048049 is Vicchio in real
ISTAT and is simply **absent from this dataset** — Vicchio is Mugello, not olive country.

**IMPACT: NONE — but the claim itself is a defect.** A number that does not exist was
carried into a hand-off as fact. I could not tell from the artefacts whether the earlier
audit used a different dump, a different comune table, or was simply wrong; **NOT KNOWN**.

### 1c — what the "obvious" geographic fix would do

**CLAIM:** an auditor who "corrects" the province from `admin_code` improves the output.

**METHOD:** `rt3_05_counterfactual.py`, variant `ISTAT`: re-attribute every visit's province
from `admin_code` and re-run the real engine.

**REPRODUCED: YES — and it makes things worse.**

**NUMBERS:** 1,401 / 79,251 visits move. Then:

- **the province of Prato disappears from the output entirely** (10 published provinces → 9)
- Firenze: rate 0.0664 % → 0.0642 %; visits 241 → 265; groves 73 → 80; drupes 24,100 → 26,500;
  infested drupes 16 → 17; unmatched baseline median 1.4073 % → 1.2868 %

**IMPACT: MAJOR (as a warning, not as a present defect).** The engine has no rule saying
which of two geographies wins, so whoever next "fixes" the geography can silently delete a
province. Nothing in the output would say a province had been deleted (see Accusation 5).

**WHAT SURVIVES:** the shipped choice (group by `nome_area`) is the correct one here.

---

## ACCUSATION 2 — "The engine cannot tell where a fact happened, because it reads nothing geographic except one string"

**CLAIM:** `lat`, `lon`, `admin_code`, `admin_code_3`, `name_3`, `name_4`, `name_5` are never
used for anything. The tool has no independent check on place at all.

**METHOD:** `rt3_05_counterfactual.py`, variant `NOGEO`. Physically delete those fields —
plus `id_area`, `cultivar`, `name` — from every raw row on disk into a shadow RAW, then run
the real `di_core.load_visits` → `di_observe.cell` → `di_render` over it and diff every
published field.

**REPRODUCED: YES.**

**NUMBERS:** **3,170,040 geographic values deleted** across 84 files. Then:

- visits loaded: 79,251 before, **79,251** after
- every published field on every one of the 10 province cells: **identical**
- the rendered regional report: **string-identical**

**IMPACT: MAJOR.** Not because a number is wrong today, but because this is the mechanism
by which every other finding below reaches print undetected. `di_core` does copy
`admin_code` and `name_4` into each visit record (`comune_code`, `comune`) — and then
nothing ever reads them, renders them, or checks them.

**WHAT SURVIVES:** the observation itself. The engine's own claim is that it groups by the
source's province string, and it does exactly that, with no hidden second geography.

---

## ACCUSATION 3 — "The coordinates are broken and nobody would know"

**CLAIM:** a large share of rows carry coordinates that are not where the row says it is.

**METHOD:** `rt3_04_coordinates.py`. Tuscany box lat 42.20–44.50, lon 9.60–12.45; Italy box
lat 35.4–47.1, lon 6.6–18.6. Transposition test: does swapping lat and lon rescue the row?
Comune coherence: `rt3_09_spatial_coherence.py` (max pairwise distance between the distinct
usable points of one comune).

**REPRODUCED: YES.**

**NUMBERS:**

- `lat`/`lon` missing or unparseable: **0 / 79,251**
- inside the Tuscany box: **53,009 / 79,251**
- **outside the Tuscany box: 26,242 / 79,251 (33.1 %)** — and **all 26,242 are outside Italy
  altogether**
- of those, **25,044 / 79,251 (31.6 %) sit at exactly `0.0, 0.0`** — Null Island, the Gulf of
  Guinea
- transposed lat/lon? **No.** Swapping rescues only **33 / 26,242** into Tuscany, and **0**
  land in Italy-but-not-Tuscany. The remaining 1,198 bad rows are in some other system
  entirely (2006 example: FILATTIERA, Massa-Carrara, `lat=4.14464 lon=45.91210`; its 2007
  row for the same grove reads `44.36780, 9.92028`). I could not identify the projection;
  **NOT KNOWN**.
- by season — the damage is concentrated in exactly the seasons the baseline leans on:

| season | in box | out of box |
|---|---|---|
| 2006 | **0** | 4,459 |
| 2007 | 806 | 2,612 |
| 2008 | 542 | 3,382 |
| 2009 | 541 | 4,071 |
| 2010 | 375 | 3,681 |
| 2011 | 369 | 3,842 |
| 2012 | 255 | 2,065 |
| 2013 | 1,921 | 521 |
| 2014–2026 | 48,200 | 1,609 |

- **12 of 187 comuni have not one usable coordinate in 21 seasons** (MASSA, PODENZANA,
  MASSA E COZZILE, PESCIA, FUCECCHIO, CASCINA, CASTELNUOVO DI VAL DI CECINA, CHIANNI,
  CRESPINA, MONTOPOLI IN VAL D'ARNO, LATERINA, SAN GIOVANNI VALDARNO).
- comune spatial coherence, over the 155 comuni with ≥2 distinct usable points: **54 / 155**
  span more than 10 km, **16 / 155** more than 20 km, **10 / 155** more than 30 km,
  **5 / 155** more than 40 km. Worst: 051034 SANSEPOLCRO, **110.1 km over 2 points**.

**IMPACT ON PUBLISHED NUMBERS: NONE**, proved by Accusation 2 — delete the coordinates
entirely and the output does not move by one digit.
**IMPACT ON THE TOOL'S CLAIM TO KNOW WHERE THINGS HAPPENED: MAJOR.** A third of the dump
cannot be placed on a map at all, and the tool neither knows nor says so. Any downstream
consumer that plots these points puts 25,044 Tuscan olive observations in the Atlantic.

**WHAT SURVIVES:** the 2014→2026 coordinates are mostly usable (48,200 in box vs 1,609 out),
which is what made Accusation 5 testable at all.

### 3b — one real row filed in the wrong province

**CLAIM:** at least one observation is published under a province it did not happen in.

**METHOD:** `rt3_10_wrong_province_row.py`.

**REPRODUCED: YES.**

**NUMBERS:** `id_field` **4553**, 22 visits, 2013-08-01 … 2014-10-08, site name
`'Via San Gregorio - '`.

- filed as: comune **051034 SANSEPOLCRO**, province **Arezzo**, sub-area **'Val Tiberina'**
- coordinate: **43.85375, 10.84490**
- that point is **0.6 km** from the median point of **047009 MONSUMMANO TERME, province
  Pistoia**, and **55.0 km** from Sansepolcro's own median point. The eight nearest comuni to
  it are all in Pistoia or Firenze; not one is in Arezzo.
- it reaches the published Arezzo baseline in seasons **2013 and 2014**:
  2013 season rate **0.9474 % → 0.9091 %** with it included;
  2014 season rate **2.8889 % → 3.0118 %** with it included.
- the published headline numbers do **not** move: `baseline_rate_pct_median` 0.6418 % either
  way, `historical_state` TYPICAL either way, `matched_panel_seasons` 6 either way.

**IMPACT: MINOR on today's numbers, MAJOR on the guarantee.** The tool published an
observation under Arezzo that its own data says happened in Pistoia, and there is no rule
anywhere that could have caught it.

---

## ACCUSATION 4 — "`id_field` is not a stable identity, so the MATCHED PANEL is worse than the unmatched baseline, not better"

This is the one that matters. The published historical statement is the matched-panel one
(`di_observe.py`: `ana["historical_state"] = ana["historical_state_matched"]`), and its only
evidence that a grove is the same grove is an integer.

**METHOD:** `rt3_03_idfield_identity.py` (identity across the whole dump),
`rt3_06_matched_panel_integrity.py` (identity inside the 45 matched comparisons the engine
actually publishes), `rt3_07_matched_impact.py` (re-run the engine's own matched logic with
non-identical groves removed).

**REPRODUCED: YES.**

### 4a — `id_field` moves

| what changes within one `id_field` | id_field | of 2,686 | visits | of 79,251 |
|---|---|---|---|---|
| **province** (`nome_area`) | **1** | 2,686 | 19 | 79,251 |
| **comune** (`admin_code`) | **25** | 2,686 | 1,962 | 79,251 |
| sub-area (`name_5`) | 12 | 2,686 | 814 | 79,251 |
| site name | 269 | 2,686 | 18,151 | 79,251 |
| cultivar | 66 | 2,686 | 7,475 | 79,251 |
| recording organisation | 438 | 2,686 | 30,241 | 79,251 |

The province-crossing one is the clean proof of **recycling**:

```
id_field 5700
  2019-07-15 .. 2019-10-14   Firenze  048011 CERRETO GUIDI  'Via Fonda - oliveto'   43.763134, 10.876856   org None
  2020-07-15 .. 2020-10-07   Pisa     050024 PALAIA         'Toiano - oliveto'      43.587278, 10.811019   org ota
  20.26 km apart. Different comune, different province, different name, different organisation.
```

Not a boundary change, not a GPS correction: one integer, two groves.
`id_field` **4380** carries **four** comuni across **49.07 km**.

Coordinate drift, over the 2,523 `id_field` with ≥2 coordinate-bearing visits:
**286** move at all, **266** move more than 500 m, **258** more than 1 km, **251** more than
5 km, **240** more than 20 km. (The extreme tail is the corrupt 2006 coordinates of
Accusation 3, not 240 relocated groves — but the engine cannot tell those two cases apart
either.)

Absence gaps, a recycling signature: **191 / 2,686** `id_field` vanish for ≥2 seasons and come
back. Worst is `id_field` 3325 — seen 2008-2010, then nothing until 2019.

Of the **478** groves in the current window, **36** have at some point changed
province/comune or moved more than 500 m.

### 4b — what that does inside the 45 matched comparisons the engine publishes

`rt3_06_matched_panel_integrity.py`, checking each shared grove's comune and coordinate in
the *now* window against the *then* window:

| | count | of 836 grove-slots |
|---|---|---|
| verifiably the same place (≤ 500 m) | 736 | 836 |
| **`then` coordinate unusable (0,0 or out of box) — sameness has no evidence beyond the integer** | **60** | 836 |
| moved more than 500 m between the two windows | 40 | 836 |
| **changed comune between the two windows** | **30** | 836 |

It is worst exactly where the comparison is longest:

- **Firenze 2012**: 10 shared groves, **8** of them have an unusable 2012 coordinate.
- **Siena 2009–2012**: 7–8 of every 8–9 shared groves unusable.
- **Siena, every season 2009–2023 except 2024**: `id_field` 3628 is counted as the same grove
  while its comune reads 052002 ASCIANO then and 052026 RAPOLANO TERME now (1.32 km).
- **Arezzo 2020 and 2021**: 9 shared groves, only 4 verifiably the same place; `id_field` 5135
  moved **35.8 km**, 5757 moved **15.4 km** *and* changed comune.

### 4c — DOES IT REACH A PUBLISHED NUMBER? YES

`rt3_07_matched_impact.py` re-runs the engine's own matched logic three ways.
`STRICT` = drop shared groves that changed comune or moved > 500 m (an unusable coordinate is
*not* treated as evidence of a move). `PARANOID` = also drop groves whose `then` coordinate is
unusable, so every kept grove is positively verified.

| province | AS SHIPPED | STRICT | PARANOID |
|---|---|---|---|
| **Arezzo** | **TYPICAL** (6 seasons) | **INSUFFICIENT_DATA** (4) | **INSUFFICIENT_DATA** (4) |
| Firenze | BELOW_HISTORICAL (14) | BELOW_HISTORICAL (14) | BELOW_HISTORICAL (13) |
| **Siena** | **BELOW_HISTORICAL** (17, lower in 14 of 17) | **TYPICAL** (12, lower in 8 of 12) | **TYPICAL** (11, lower in 7 of 11) |
| Lucca | INSUFFICIENT_DATA (3) | INSUFFICIENT_DATA (3) | INSUFFICIENT_DATA (1) |
| Grosseto | INSUFFICIENT_DATA (2) | INSUFFICIENT_DATA (1) | INSUFFICIENT_DATA (1) |
| Livorno / Massa-Carrara / Pisa / Pistoia / Prato | unchanged | unchanged | unchanged |

Grove-slots removed: Arezzo 18 (STRICT) / 19 (PARANOID); Siena 22 / 75; Firenze 19 / 49.

Downstream, `di_adama.attention_class` (verified, not inferred):
**Arezzo MONITOR → NO_ESCALATION.** Siena stays MONITOR, but the published sentence changes
from "below its own history" to "typical".

**Honest caveat about mechanism.** Two things happen at once when groves are dropped: the
pooled rate on the remaining groves changes, *and* some seasons fall under
`MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE = 8` and leave the comparison entirely (Siena 17 → 12
seasons, Arezzo 6 → 4). Both are real consequences of the identity failure, but they are
different mechanisms and the table above does not separate them.

**IMPACT: FATAL to the matched-panel claim as currently worded.** Two of the three provinces
with a published matched historical state change that state once groves that are demonstrably
not the same place are removed. The engine's own comment says *"Comparing this year's groves
against a different set of groves and calling the difference a change in pressure is a
mistake, not a nuance."* — that is exactly right, and the engine then does it, because
`id_field` equality is not grove equality and nothing checks it.

**WHAT SURVIVES:** **Firenze**. BELOW_HISTORICAL in all three modes, 14 / 14 / 13 seasons,
lower in every single matched season under every mode. That one is real.
The matched panel is also still **better than the unmatched baseline** — under AS_SHIPPED,
Arezzo's unmatched state is BELOW_HISTORICAL while its matched state is TYPICAL, i.e. the
matching already caught something. The problem is that it does not go far enough, not that it
points the wrong way.

---

## ACCUSATION 5 — "A province can go missing and no reader could tell"

**CLAIM:** Tuscany has 10 provinces. The engine derives its province list from the data, so a
province that stops arriving is not reported as missing — it is reported as never having
existed.

**METHOD:** `rt3_08_org_and_labels.py`, `rt3_05_counterfactual.py` variant `BLANK`.

**REPRODUCED: YES.**

**NUMBERS:**

- the string `Massa-Carrara` appears **0 times** in the engine source. `PROVINCES` appears
  **0 times**. There is **no declared list of Tuscany's provinces anywhere in the engine.**
  Both `run_pilot.py` and `di_report.py` do
  `sorted({v["province"] for v in visits if v["province"]})`.
- baseline regional report: `10 de 10 províncias com observação publicável`, rising = `['Lucca']`
- with every Lucca row absent: `9 de 9 províncias com observação publicável`, rising = `[]`

  The denominator moves with the numerator, so coverage still reads 100 %. And the province
  that vanished was **the only INCREASING_OBSERVED trend in Tuscany and the only INVESTIGATE
  attention class in the whole run**.
- the `if v["province"]` filter silently drops any visit with an empty or null province and
  **the count is never emitted anywhere**. In this dump it drops **0 / 79,251** — so it is a
  latent hole, not a present error.
- one partial mitigation: `di_report.py` hard-codes `for p in ("Firenze", "Siena", "Lucca")`
  and raises `StopIteration` if one of the three is absent. That is a crash, which is louder
  than silence — but it only covers 3 of 10 provinces, and `run_pilot.py` (which writes the
  JSON) stays quiet.

**IMPACT: MAJOR.** A silent loss of a province is indistinguishable, in the output, from a
province that was never monitored.

---

## ACCUSATION 6 — "I can make the engine attribute an observation to the wrong province and publish it"

**METHOD:** `rt3_05_counterfactual.py` (INJECT), `rt3_08_org_and_labels.py` (b, d). All three
change only the province string and run the real engine and the real renderer.

**REPRODUCED: YES, three ways, none of them caught by anything.**

**6a — moving real observations to another province.** 192 Siena visits in the current window
relabelled `Prato`:

| | Prato before | Prato after |
|---|---|---|
| rate | 0.0417 % | **0.6159 %** (×14.8) |
| visits | 24 | 210 |
| groves | 7 | 68 |
| drupes dissected | 2,400 | 20,783 |
| organisations | 2 | 6 |

Siena's cell collapses: `observation_publishable` True → **False**, historical
BELOW_HISTORICAL → INSUFFICIENT_DATA, matched seasons 17 → 0, trend STABLE_OBSERVED →
UNKNOWN, attention MONITOR → **UNKNOWN**. The rendered Prato card reads
*"0.6159 % das azeitonas amostradas … base: 210 visitas a 68 olivais, 6 organizações"* for a
province whose real monitored network in that window is **7 groves in 4 comuni**
(`rt3_09` d: CARMIGNANO 12 visits, VAIANO 4, MONTEMURLO 4, PRATO 4). Nothing in the output
flags it.

**6b — a whitespace/case variant splits one province into two.** `.strip()` appears **0 times**
in the engine source; there is no normalisation of the province string. Relabelling 97 recent
Siena visits as `'SIENA '` yields **11 provinces in Tuscany**, both publishable:

```
'SIENA '  rate=0.9643  n_vis=95  hist=INSUFFICIENT_DATA  publishable=True
'Siena'   rate=0.4088  n_vis=91  hist=BELOW_HISTORICAL   publishable=True
```

The real Siena reading (0.6909 %) appears nowhere; the reader sees two different provinces
with two different verdicts.

**6c — a province outside the region.** Relabelling 5,192 Pistoia visits `Bologna` publishes
a cell with `country=Italy`, `region=Toscana`, `province=Bologna`, `publishable=True`, and the
renderer prints the headline **`TOSCANA · BOLOGNA · OLIVEIRA · MOSCA-DA-AZEITONA`**. `country`
and `region` are literals in `di_observe.cell`; `province` is a raw pass-through string that
is never validated against anything.

**IMPACT: MAJOR.** These are injections, not present defects — but 6b in particular needs no
attacker at all: one inconsistent capitalisation from the upstream API silently splits a
province's panel in half and changes its published verdict.

---

## ACCUSATION 7 — "`nome_area` is the recording organisation's province, not the field's"

**CLAIM:** the province tracks who filed the record, not where the grove is.

**METHOD:** `rt3_08_org_and_labels.py`, cross-tabulating `org_name` and `id_org` against
`nome_area`.

**REPRODUCED: NO.**

**NUMBERS:**

- organisations recording in more than one province: **14 of 21**. `ota` (id_org 11) and
  `aprol` (id_org 12) each record in **all 10** provinces; `Apot` in 8; `terreetruria` in 7.
- provinces served by more than one organisation: **10 of 10**.
- and `nome_area` matches the field's own comune code on **77,850 / 79,251**.

`nome_area` tracks the **field**. Not the organisation.

**IMPACT: NONE.**

**Two side findings from the same table, outside my remit but worth one line each:**
`org_name` is null on **43,212 / 79,251** visits, and `pooled()` counts orgs with
`if v["org"]`, so the published `n_orgs` counts only *named* organisations and undercounts.
And `org_name` "ARSIA" carries two different `id_org` values (4 and 9), so `org_name` is not a
stable key either.

---

## WHAT I COULD NOT BREAK

1. **The province label itself.** I could not find one row whose `nome_area` contradicts its
   own `admin_code` for any reason other than the 1992 Prato reform: 77,850 / 79,251 agree,
   1,401 / 79,251 are the reform, **0 / 79,251** are mislabelling. `name_3`, `admin_code_3`
   and `id_area` all corroborate `nome_area` on 79,251 / 79,251. Grouping by `nome_area` is
   the right choice, and the naive "fix" of grouping by `admin_code` deletes the province of
   Prato.

2. **The prior audit's Vicchio finding.** 0 hits in 317,004 rows, by three independent
   searches. I could not reproduce it and I could not find any variant of it.

3. **The four variables agree on geography.** All 79,251 visit keys are present in all four
   collected variables and **0** of them disagree on any of `nome_area`, `admin_code`,
   `name_3`, `admin_code_3`, `name_4`, `name_5`, `lat`, `lon`, `org_name`, `id_org`. There is
   no join that could mix a Siena denominator with a Firenze count.

4. **The comune inventory.** 187 comuni, **0** codes shared by two provinces, **0** names
   carrying two codes, **0** comune numbers outside the range its province historically used,
   **0** of 42 sub-areas spanning two provinces. This is a clean administrative hierarchy.

5. **Firenze's matched historical statement.** BELOW_HISTORICAL survives every attack I made
   on grove identity — 14 seasons as shipped, 14 STRICT, 13 PARANOID, and the current window
   reads lower than *every* one of them under *every* mode. Firenze's 0.0664 % is the most
   defensible published number in the run.

6. **The engine's honesty about not matching.** Six of ten provinces are already published as
   INSUFFICIENT_DATA with the reason spelled out, and `di_render` adds
   *"os olivais monitorizados hoje não são os de então"* to exactly those cards. The gate is
   real and it fires. My finding is that the threshold is set on **how many** groves overlap
   and never on **whether the overlapping ones are the same place** — not that there is no gate.

7. **Making a bad geography change a number without touching the province string.** Every
   coordinate corruption in Accusation 3 — 26,242 out-of-box rows, 25,044 at Null Island, 12
   comuni with no usable point at all — reaches **zero** published digits. Deleting 3,170,040
   geographic values from disk changes nothing. The engine is geographically blind in both
   directions: it cannot be misled by a bad coordinate, and it cannot be corrected by a good one.

**Open, undecided, NOT KNOWN:**

- What coordinate system the 1,198 non-zero bad coordinates are in. Not WGS84, not a lat/lon
  swap (33 / 26,242 rescued), not any projection I could fit.
- Whether the 25 comune-changing `id_field` are recycled identifiers or genuine re-sitings of
  the same farm's monitoring point. `id_field` 5700 (two provinces, two names, two
  organisations, 20 km) is recycling on the evidence; the sub-kilometre ones (3628, 5342,
  5721) could be either, and the source carries nothing that would decide it.
- Whether any grove sits on the wrong side of a real province boundary. I have no
  authoritative boundary polygon offline, so I tested comune-median distance instead
  (270 / 53,009 in-box rows more than 25 km from the median point of their own comune, all of
  them `id_field` 4554 and 4553). A proper point-in-polygon test against ISTAT boundaries has
  not been done.
- Whether the earlier audit that produced the Vicchio number was run against a different dump.
