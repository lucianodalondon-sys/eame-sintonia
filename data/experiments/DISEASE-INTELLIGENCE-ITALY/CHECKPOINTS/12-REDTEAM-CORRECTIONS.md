# CHECKPOINT 12 — FINDINGS AGAINST MY OWN CLAIMS, VERIFIED BEFORE CONCEDING

Rule carried from `10-FINAL-RECONCILIATION.md`: *a finding against me needs the same
verification as a finding for me.* Every item below was re-run by me from the frozen RAW before
being accepted, and where my numbers differ from the reviewer's, **my numbers are the ones
recorded and the discrepancy is stated.**

---

## C1 — CONCEDED · "Case C has two NEGATIVE pairs" was wrong. It has nine.

27/36 positive means **9 of 36 pairs are not positive**. The figure 27/36 was printed by my own
script. I read the printout's *tail* — which shows only the bottom two rows — and reported the
tail as the negative set. Arithmetic I published contradicted itself in the same sentence.

**Corrected**: OIDIO province agreement = 27/36 positive, **9 non-positive**, mean ρ +0.245,
p 0.00067. The two most negative are Pisa–Pistoia −0.396 and Livorno–Pistoia −0.258.

---

## C2 — CONCEDED · "Three cases" is three case-runs over **two** independent field panels.

| measured on the frozen RAW | |
|---|---|
| OIDIO fields | 895 |
| PERONOSPORA fields | 896 |
| shared `id_field` | **894** (Jaccard 0.997) |
| shared `(id_field, date)` visit keys | **33 969 = 96.9 % of all OIDIO visits** |
| OIDIO ∩ BACTROCERA fields | **0** |

Case C is a second column on the same paper form as the calibration case — same scout, same
vineyard, same day. **Corrected claim**: the pipeline was exercised on 3 case-runs across
**2 independent field panels** (one vine, one olive). The olive panel is genuinely independent
and is what carries the generalization claim.

---

## C3 — CONCEDED · The generalization is across CROP and ISSUE, **not across GEOGRAPHY**.

Abruzzo cannot run the instrument at all: its `nome_area` values are **agro-zones**
(Teatino, Vastese, Pescarese, Frentano-Sangro, Peligno, Tollese-Ortonese…), a different
administrative partition from provinces, and **no area reaches 10 seasons** (best: Teatino 9,
Vastese 8) → **0 qualifying pairs**. All 108 pairs behind the three case-runs come from the same
9 Tuscan provinces and one API host.

**Corrected**: `ABRUZZO × PROVINCE_AGREEMENT = INSUFFICIENT_DATA (0 qualifying area pairs)`.
Nothing in this mission demonstrates geographic generalization. (The scale derivation *did*
generalize there — 0 unresolved labels — so this is a data-coverage limit, not a pipeline limit.)

---

## C4 — CONCEDED · `province_agreement.py` shipped a warrant that is factually false.

It asserted that "panel composition, observer identity and visit intensity are province-specific
and cannot manufacture cross-province agreement". Measured: `unipi` supplies rows in **all 10**
provinces of both vine cases; `ota` and `aprol` each appear in **10/10** provinces of the olive
case. That sentence was the *only* justification offered for treating the pairs as independent.

I re-ran the leave-shared-org-out test myself rather than adopt the reviewer's numbers:

```
OIDIO       all orgs 27/36 rho +0.245  ->  drop unipi      6/6 pairs  rho +0.537
BACTROCERA  all orgs 36/36 rho +0.770  ->  drop ota+aprol 36/36 pairs rho +0.731
```

The conclusion survives in both. **The warrant did not** — it is deleted and replaced by the
measurement. Noted honestly: dropping the shared org costs the vine case most of its power
(36 pairs → 6), so its survival is weaker evidence than the olive case's. The calibration case
uses an older index layout and was **not** re-run, so no number is claimed for it.

---

## C5 — CONFIRMED DEFECT, MEASURED IMPACT ZERO · zero-denominator visits served as `0`.

The olive outcome is a rate over `tot` (olives dissected). My own join of var 1 to var −1002:

```
v-1002 rows                          79 251
denominator == 0                      3 026
  of those, served as the value "0"   1 580
  of those, served NONZERO               416   (arithmetically undefined)
denominator 0 or unknown (guard drops) 3 206
```

*Discrepancy recorded*: the reviewer reported 2 351 / 2 324 / 27. I could not reproduce those
figures; the numbers above are mine, from the frozen RAW. **The structural claim reproduces; the
magnitudes do not, and I publish mine.**

A visit where nothing was dissected was entering the series as a **confirmed absence**.
`contracts.py` has forbidden exactly this twice since the engine was frozen
(`Missing.assert_not_coerced_to_zero`, `OutcomeRecord.validate`) — and **no runner imported
contracts.py**, so the frozen contracts were documentation, not code. That is the real failure.

**Fixed**: `denominator_guard()` now refuses any outcome row whose denominator is 0 or unknown.
**Measured effect, not assumed:**

```
today's published cells .................. 0 of 10 class changes
walk-forward EVOLUTION series ............ 2 of 200 cells changed (1.0%), both in 2013
```

Because CURRENT_PRESSURE takes the **site-max over a 28-day window**, a site with one phantom
zero almost always has a real scoring in the same window, and the phantom is absorbed. The
defect is real; the published conclusions do not rest on it. Both facts are reported together.

---

## C6 — CONFIRMED · an era break lives **inside** the olive outcome variable.

The same field event (nothing dissected) is encoded two different ways by era:

```
served as "0"   2006:182 2007:145 ... 2019:89  2020:11  2021+:0
served as null  2006-2019 all <=4     2020:88  2021:338 2022:247 2023:138 2024:84 2025:267
```

A clean switch at 2020. `run_case.py` skips nulls and keeps zeros, so pre-2020 seasons carried
phantom absences that post-2020 seasons do not. This is structurally the same era-proxy defect
already caught and honoured for Oidio (ρ(%georeferenced) = −0.737 → `TREND_NOT_PROVED`), and it
was **not** recorded anywhere. It is recorded now, and it reinforces `TREND_NOT_PROVED` for the
olive case rather than weakening it — the direction of the bias deflates the *older* seasons,
which is the opposite of what would be needed to manufacture today's LOWER_THAN_USUAL.

---

## C7 — CONFIRMED · 2026 is **not** a complete season and was counted as a peer.

```
2006-2025 last ISO week: 41-44 (median 43)      2026 last ISO week: 36 (2026-09-04)
```

Olive-fly damage accumulates in exactly the weeks 2026 does not yet have.

**Corrected headline**: CASE B = **20 complete seasons + 1 in progress**, 79 251 visits of which
2 928 belong to the in-progress season. The earlier "21 seasons" was wrong.

`season_completeness()` now derives the typical last week from the archive itself and flags any
season ending more than two weeks early. Run over the olive case it flags **exactly one** season
(2026, week 36 vs typical 43) and produces **no false positives** across the other twenty.

**CURRENT_PRESSURE is immune to this by construction** — it compares the same 28-day calendar
window across seasons, so an unfinished October cannot touch a 10 August–6 September comparison.
Season-level and trend views are not immune and now carry the flag.

---

## C8 — PARTIALLY REFUTED · "279 raw counts served as percentages, 68 values above 100".

Does not reproduce at that magnitude in my frozen data:

```
v-1002 numeric rows                     78 019
values > 100                                 3      (reviewer said 68)
visits with a denominator other than 100 2 287      (200, 50, 150, 300, 99 ...)
  max value on each non-100 denominator: 34, 40, 15, 19, 18  -- none above 100
```

What is true: 2 287 visits use a denominator other than 100, and 3 values exceed 100, which is
impossible for a percentage. What is not supported: that 279 visits publish an un-normalised raw
count with 68 of them above 100. **Recorded at the magnitude I can verify.**

The published metric is `INCIDENCE` = share of sites with value > 0, which is **invariant to
normalisation**. `SEVERITY` would not be, and `SEVERITY` is not published.

---

## WHAT THIS CHANGES IN THE VERDICT

Nothing in gates A–J flips. Three headline numbers were wrong and are corrected (season count,
negative-pair count, "three cases"), one claim is withdrawn entirely (geographic
generalization), one false warrant is deleted from the code, and two real data defects are now
guarded in code with their impact measured at 0/10 and 2/200 cells.

The capability's case rests where it did: **one region, two independent panels, the olive case
carrying it.**

---
---

# SECOND ROUND — four more, verified the same way

## C9 — CONCEDED, and this one changes a headline · the cases were compared **across metrics**.

The province-agreement test summarises a province-season as the **mean of site-maxima**. For an
ordinal case that is a mean of ordinals; for the olive case it is a mean of percentages. The
metric CURRENT_PRESSURE actually **publishes** is `INCIDENCE` — the share of sites with the issue
present. Re-run on the published metric:

| case | mean-of-site-max (what I headlined) | **INCIDENCE (what I publish)** |
|---|---|---|
| BACTROCERA | 36/36, ρ **+0.770** | 35/36, ρ **+0.449** |
| OIDIO | 27/36, ρ +0.245 | 26/36, ρ +0.229 |

**Corrected**: the internal-consistency evidence supporting the *published* metric for the olive
case is **ρ +0.449**, not +0.770. The claim "stronger than the calibration case (+0.622)" is
**withdrawn** — it compared a mean-of-percentages against a mean-of-ordinals. The olive case
still beats the vine case on both metrics; it is no longer claimed to beat the calibration case
on any.

## C10 — CONCEDED · **Gate A was self-certifying**, and it failed against my own source.

`current_pressure.py` wrote `EVIDENCE_ROLE = OFFICIAL_OBSERVATION` into every output as a
**constant**. Nothing checked it. Fed a rainfall series it would have stamped a weather number
as an official field observation and **passed its own gate A**.

Fixed and tested. `assert_outcome_admissible()` now requires two things:
```
MODELLED_RISK as outcome   -> REFUSED (contracts.EvidenceRole)
FORECAST as outcome        -> REFUSED
non-survey variable        -> REFUSED (not in this case's survey-schema metadata)
legitimate outcome         -> OFFICIAL_OBSERVATION
```
Gate A is re-evaluated **after** the fix and passes. Before the fix it was not enforced, and the
earlier PASS was worth nothing. Said plainly rather than quietly re-run.

## C11 — CONFIRMED, and it is the strongest single discriminator found · **effort agreement**.

Does survey *effort* (visits per site) agree across provinces more than the disease does? If it
does, the "internal consistency" is consistency of the monitoring programme, not of the biology.

```
OIDIO       EFFORT 36/36 rho +0.738   DISEASE 26/36 rho +0.229   -> EFFORT AGREES MORE
BACTROCERA  EFFORT 29/36 rho +0.252   DISEASE 35/36 rho +0.449   -> disease exceeds effort
```

**Oidio's province agreement is not separable from survey effort and is hereby withdrawn as
evidence.** The olive case passes cleanly: its biological signal is roughly twice the effort
signal. This is the sharpest evidence in the whole mission that the capability belongs to the
*cell*, not the tool, and it points the same way as every other test: **the olive case carries
it, the oidio case does not.**

## C12 — CONFIRMED as latent, **did not fire** · numeric fallback on unmapped ordinal codes.

`run_case.py` falls back to `float(val)` when a code is not in the derived scale — which would
turn a code **id** (e.g. 782) into a magnitude. Checked directly: the oidio scale covers
`['782','783','784','785']` and `['786','787','788','789']` with **zero unmapped values in
35 064 rows**. The bug is real and never fired here. `current_pressure.read_value()` is already
immune by construction — it decides ORDINAL vs NUMERIC up front from the source's metadata and
returns MISSING for an unmapped code rather than a number.

## C13 — CONFIRMED for the calibration archive, **not** for the two new cases · one file per (var, year).

`glob(*_v{var}_*.json)` keeps whatever the pattern matches. Measured: the two new cases have
**exactly 1** file per (var, year); the calibration archive `TOSCANA/RAW/` has up to **4** per
key (287 files over 140 keys). The generic runner was never pointed at that archive — the
calibration case has its own scripts — but the defect is real for reuse and is recorded rather
than argued away.

---

## STANDING AFTER BOTH ROUNDS

Withdrawn: geographic generalization (C3); "stronger than the calibration case" (C9); **oidio's
province agreement as evidence** (C11).
Corrected: season count (C7), negative-pair count (C1), "three cases" (C2), the published
metric's ρ (C9).
Fixed in code: false independence warrant (C4), zero-denominator guard (C5), season-completeness
flag (C7), enforced evidence role (C10).
Refuted or not reproduced at the stated magnitude: C8, C12, C13 (latent only).

Gates: still 9 PASS / 0 FAIL / 1 NOT_TESTABLE — but gate A now passes **because it is enforced**,
not because it was asserted.

---
---

# THIRD ROUND — the tautology, the dead code, and an over-claiming sentence

## C14 — CONCEDED · **Gate B was arithmetically incapable of failing.**

`B_NOT_SOLD_AS_FORECAST` tested `CUTOFF_LABEL == "NOWCAST"`. `Cutoff.label()` returns
`FORECAST` only when the issue date precedes the target window — and the window is *built*
ending at the issue date. The gate could not fail. **The single guarantee this project most
needs was a tautology.**

Rewritten to test something the source can violate: the archive **does** contain future-dated
observations, and none may reach a published cell.

```
the archive contains 15 observations dated after the cutoff,
15 of them inside the published window; the cutoff excludes every one.
```

Remove the cutoff filter and the gate fails. That is what a gate is for.

## C15 — CONCEDED · `denominator_guard` and `season_completeness` were **dead code**.

I wrote both, measured their impact, reported the measurement — and never called them. The
`FAILURE != ZERO` protection existed as a function nobody invoked, which is the same failure as
`contracts.py` existing and no runner importing it (C5). Both are now wired into
`current_pressure()`. A case declares its denominator variable in its collection index; when it
does **not**, the output carries `DENOMINATOR_DECLARED = NO` so the absence is visible instead
of assumed harmless.

## C16 — CONCEDED · the headline sentence over-claimed, and contradicted its own table.

It read: *"scouts recorded damaging olive-fly infestation on 1 168 visits"*. 1 168 is the number
of visits **scored for** the issue, not the number that found it — and the same sheet reported
four of those provinces at incidence 0.000. Rewritten to keep three numbers apart: visits
scored, sites monitored, sites with the issue present.

## C17 — CONCEDED · `Capability.route` stamped `CURRENT_PRESSURE_MONITOR = PROVED` on the
strength of an outcome existing at all.

An archive that stopped in 2009 would have been certified a *current* pressure monitor. Now it
requires three measured things — latency ≤ 21 days, label stability ≥ 0.80, and at least one
regional unit passing the publication gate:

```
olive case measured today      -> PROVED
oidio case measured today      -> NOT_PROVED
archive with no recent data    -> NOT_PROVED
never measured                 -> NOT_TESTABLE      (never measured is never proved)
```

## C18 — CONCEDED · `sensitivity()` varied four of five parameters. Baseline depth was a silent sixth.

`MIN_BASE` was held at 5 across the whole grid. Now varied over {3, 5, 8}, so the grid is
**135 points**, not 45. The stability numbers move slightly against me and the new ones are the
ones published:

```
BACTROCERA  0.927 -> 0.918        OIDIO  0.651 -> 0.596
```

## C19 — CONCEDED · the per-cell `EVIDENCE` clause was declared and not emitted.

The definition promised per-cell evidence; the output carried it only at the top level. Each
published cell now carries its own source, role, window and raw-file hash. A cell that cannot
produce them is not rendered (spec rule R8).

---
---

# FOURTH ROUND — the pipeline met a case it had never seen, and lost

The mission's own reuse claim was tested the only way it can honestly be tested: by collecting a
**genuinely new** Italian case live and running it through the unmodified pipeline.
**FRUMENTO × Septoria × Toscana** (crop 19, schema 74, var 372) — a different crop, a different
schema, a different scale vocabulary, never seen by any of this code.

It failed, in four separate places, and each failure is now fixed and re-tested.

## C20 — FATAL, CONCEDED · the module published a confident, wrong statement.

Run on the new case as shipped, `current_pressure.py` printed:

```
Arezzo    TYPICAL_FOR_THE_DATE  val=1.0  sites=12  base_n=13  med=1.0
Grosseto  TYPICAL_FOR_THE_DATE  val=1.0  sites=24  base_n=13  med=1.0
```

**"100 % of monitored wheat sites have Septoria, and that is typical for the date."** The
underlying values were `1599` and `1628` — *code ids*, not measurements. The source declares
`id_survey_var 372` as `widget: numeric` and then serves codes; the module read them as
magnitudes, every value was `> 0`, and it published.

**This breaks the central design claim of the whole mission** — that the module fails *loudly to
UNKNOWN* rather than quietly to a number. It did not fail loudly. It failed quietly and
confidently, on the first case it had never seen.

*Recorded honestly*: the reviewing lens reported this against variable **385**, which does not
exist in schema 74 at all. With 385 the module **refused** correctly. I had to find the real
variable (372) to reproduce the finding — and it reproduces, and it is worse than reported,
because 372 is a legitimate, declared variable of the schema.

**Fix**: `assert_scale_decodes()` — in NUMERIC mode, if ≥ 90 % of the observed values are
`id_survey_code` values *of this very case*, the variable is coded-but-mis-declared and the
module refuses. Generic; no case knowledge.

## C21 — SERIOUS, CONCEDED · the collector froze the wrong code table.

`collect_generic.py` latched the code table from the **first response carrying the key**. For a
case whose archive starts after 2006 that is the *empty* table of a year with no data — after
which the pipeline has no scale at all. Measured on the new case: `codes 0, vars 0`, while 2013
and 2026 both return a perfectly good 4-code ordinal ladder.

It is not only an empty-year problem. **The source's code table is year-dependent**: crop 3 /
schema 8 grows from 16 codes in 2006 to 74 in 2025. My own shipped oidio index carries **16** —
the 2006 table. It happened to map every value in that case (0 unmapped in 35 064 rows), so no
harm was done, but that was luck, not design.

**Fix**: take the **most complete** table seen across all responses, not the first.
On the new case that moves it from 9 codes to 41, and the scale then derives correctly.

## C22 — CONCEDED · `PIPELINE_REUSE_RATE = 100%` was wrong. It is **75%**.

With the collector fixed, the new case still would not decode: its labels are **compound** —
`Nessuna / Bassa <5% / Media 5-25% / Alta >25%` — a ladder word *and* a band in one string. The
parser matched only a bare word or a bare band and resolved **1 of 4** codes.

**Fix**: look for a ladder word anywhere in the label, then a band anywhere. Generic, not a rule
about wheat. The new case now derives:

```
1599 -> 0 'Nessuna'   1628 -> 1 '5 - lieve'   1602 -> 2 '10 - media'   1603 -> 3 '25 - grave'
14 seasons, 9 distinct SITE_INCIDENCE values — a real, varying series
```

**Two labels remain unresolved**: `'50 - gravissina'` (a typo for *gravissima* in the source) and
`'75 - completa'`. Those observations are dropped as MISSING, which **understates severity** in
the worst seasons. Stated, not hidden.

**Corrected accounting:**
```
CASES_TESTED ............................. 4
CASES_PASS_WITH_NO_RULE_CHANGE ........... 3
CASES_NEEDING_A_GENERIC_RULE_EXTENSION ... 1
PIPELINE_REUSE_RATE ...................... 3/4 = 75%     (was claimed 100%)
case-conditional branches ................ 0             (this part holds)
```

## C23 — FATAL, CONCEDED · **gate H tested the opposite of refreshability.**

It required `delta_rows == 0`. The olive case gains **~310 rows/week**. So a source that
published this week's scouting would **FAIL** the gate and a source that had **died** would
**PASS** it. The gate was inverted.

It also trusted `rowCount 0` as the only silent-failure shape. The source's real one is worse:
**HTTP 200 + `ok:true` + full rowCount + every value null**, which the shipped probe reported as
a healthy 2 515-row response.

**Fix**: three silent-failure shapes are now detected — zero rows; full rowCount with an all-null
value column; and a top-level `ok:false` carrying a message the client was discarding. And the
bogus probe entry that had been shipping as a *pass* is now a **deliberate negative control**
that must trip on every run:

```
NEGATIVE-CONTROL-nonexistent-var  HTTP=200 ok=False rows=2515 non_null=0
                                  <-- FULL_ROWCOUNT_BUT_EVERY_VALUE_NULL
```
Gate H now passes only if the control **did** trip. Without that line the gate could not show it
is able to fail.

## C24 — CONCEDED · **gate I was a hardcoded `PASS` constant.**

```python
g["I_GENERALIZES"] = {"VERDICT": PASS, "EVIDENCE": "3/3 cases ... 100%"}
```

The gate certifying the generalization claim asserted its own conclusion. **This is the third
tautology in the same gate set** — after A certified itself (C10) and B could not fail (C14).
That is a pattern, not three accidents: *when I wrote a gate for a claim I believed, I wrote it
so it agreed with me.*

**Fix**: gate I now runs the unseen 4th case end-to-end and fails if the case does not run or if
its series never varies — which is exactly what it did before C20–C22 were fixed. It also
reports the 75 % reuse rate instead of the 100 % it used to assert.

---

## STANDING AFTER FOUR ROUNDS

```
PASS = 9   FAIL = 0   NOT_TESTABLE = 1     (gate J, still unanswered)
```

Every gate now rests on a test that can fail, and three of them are only in that state because
the red team found they were not. The verdict is unchanged — but it is now worth something it
was not worth this morning.

**The most important thing found in this whole mission is not a number.** It is that the module's
proudest property — *fails loudly to UNKNOWN, never quietly to zero* — was **false** the first
time it met a case it had not been built for, and I would not have discovered that by testing it
on the cases I chose for it.

---
---

# FIFTH ROUND — the conclusion itself was wrong

## C25 — FATAL, CONCEDED · **"one cell qualifies" is a property of the DATE, not of the cell.**

The mission's headline finding — olive 8/10 publishable, vine 0/10, therefore *the capability
belongs to the cell* — was measured at a single `AS_OF`: **6 September 2026**, which is simply
today. Re-run with the identical code and the identical declared gate at other dates in the same
season, **the verdict inverts.** My own re-run:

```
AS_OF        OLIVE pub   stab   lat | VINE pub   stab   lat
2026-06-01           0  1.000   227 |        5  0.849     0
2026-06-15           0  1.000   241 |        6  0.842     0
2026-07-01           0  0.864     0 |        4  0.764     0
2026-07-15           2  0.833     0 |        3  0.698     0
2026-08-01           6  0.816     1 |        1  0.584     3
2026-08-15           7  0.856     1 |        3  0.637     8
2026-09-06           8  0.918     2 |        0  0.596     2
```

On **15 June the vine cell publishes 6 provinces and the olive cell publishes none.** 6 September
is the peak of the olive-fly season and roughly two months past the end of the oidio season. I
did not choose the date to flatter the result — it is today — but the result is a property of the
date all the same, and I presented it as a property of the cell. Checkpoint 11 disclosed
"(2/10 at mid-season)" for the vine in a single parenthesis; the measured mid-season figure is
**5–6/10**, and on those dates the olive figure is **zero**.

Note also that OLIVE stability reads a perfect **1.000** on 1 and 15 June — with latency 227 and
241 days and nothing publishable. A stability of 1.000 there means "consistently UNKNOWN", not
"consistently right". A headline stability number is meaningless without the latency beside it.

**What survives, and what does not.**
- Does **not** survive: "the olive cell qualifies and the vine cell does not"; "one cell
  qualifies"; the 8/10-vs-0/10 contrast as evidence for the cell principle.
- **Survives, sharpened**: the capability is a property of **REGION × CROP × ISSUE × DATE**. On
  any given day only a few cells can be published, and which ones changes through the season.
- **Survives, and is date-independent**: C11. The vine case's province agreement is confounded
  by survey effort (effort ρ +0.738 vs disease ρ +0.229) — computed over whole seasons, so it
  holds on every date, including the June dates where the vine passes the publication gate.
  **Passing the publication gate is not the same as having trustworthy internal consistency**,
  and I had conflated the two.

**Commercial consequence, which is worse than the scientific one**: the olive campaign runs late
June to late October. For roughly eight months a year the olive view has nothing to render and
would read "updated 241 days ago". A single-cell feature is dark most of the year; a
continuously-useful feature needs several cells — which is precisely what "one cell qualifies"
denies.

## C26 — CONCEDED · **`HIGHER_THAN_USUAL` can fire on four groves out of 119.**

The class is a pure rank statistic with **no floor on the size of the effect**. Early in the
season every baseline is a run of zeros, so a single detection scores percentile ~1.0 and is
published as HIGHER. At `AS_OF 2026-07-15` the engine emits HIGHER for Grosseto on **4 of 119
sites** (readings 9/6/5/2 %), for Firenze on **1 of 68**, for Livorno on **1 of 41** — and not
one of those six sites reaches the source's own red band of ≥10 %. Grosseto's HIGHER clears the
publication gate and would be rendered.

`HIGHER_THAN_USUAL` is the only word in the vocabulary that can trigger spending. The declared
`UNKNOWN_RULE` guards `n_sites` and baseline depth; **nothing guards a degenerate all-zero
baseline, and the publication gate tests stability and coverage, not effect size.**

## C27 — CONCEDED · the published variable is the **lagging** one, and the choice was never justified.

The source exposes `-1001 attiva` (live, still-killable population) and `-1002 dannosa` (damage
the fruit already carries) from the same visit. I published `dannosa`. My own join:

```
51 021 visits with both readings:  attiva > 0 in 57.8%   dannosa > 0 in 32.7%
attiva > 0 AND dannosa == 0:       16 461 visits = 32.3%
mentions of 'attiva' or '-1001' in any .md of this experiment: ZERO
```

Same day, same engine: Lucca reads **0.000** on the published variable and **0.500** on the live
one; Livorno 0.117 vs 0.584. All 79 251 rows of `-1001` were fetched, hashed and stored, and no
rationale for the choice exists anywhere.

**Measured honestly, the *class* is robust**: on 6 September both variables give 8 LOWER,
1 TYPICAL, 1 UNKNOWN. So the relative statement survives the choice; **the absolute number a
user would read does not**, and the choice of the damage-already-done variable over the
still-actionable one was never argued.

## C28 — CONCEDED · **gate J is answerable, and the answer is `PARTIALLY_OVERLAPS`.**

My reason for `NOT_TESTABLE` — "requires reading the portal's capability inventory, which this
mission is forbidden to touch" — was wrong twice. The mission forbids **modifying**, not
**reading**; and the inventory is in this branch's own working tree. Read-only, verified myself:

```
italia-portale/client/meeting-intelligence-snapshot.json
  43 cases, of which 17 carry ARCHETYPE = O1_FIELD_PRESSURE  ("Pressione in campo")
  including CROP_GRAPEVINE x ISSUE_POWDERY_MILDEW x REGION_TOSCANA at PROVINCIAL scope
  the complete TARGET vocabulary contains NO olive target
```

**Coverage inversion, and it is the sharpest thing found all day:** the portal already ships a
provincial *Field pressure* card for the cell my capability must stay **silent** on, and has no
vocabulary at all for the cell it can publish.

`J_NOT_DUPLICATE = PARTIALLY_OVERLAPS` — neither a pass nor a clean fail.

## C29 — CONCEDED · `ADAMA_PRODUCT_RELATION = NOT_PROVED` was stated for a **false reason**.

I wrote, twice, that no approved-use handoff had been received from the regulatory lane. **It
had.** `italia-portale/client/italy-label-verdicts.js` is in this working tree, applied
02 September 2026 from an audit of 163 official Italian labels, and it adjudicates **exactly my
qualifying cell**:

```
NOT_FOUND = [ ['Olive','Olive Fruit Fly','KLARTAN 20 EW'],
              ['Olive','Olive Fruit Fly','KLARTAN SMART'],
              ['Olive','Olive Fruit Fly','MAVRIK SMART'], ... ]
governed by: "ABSENCE IN OUR READING  ≠  ABSENCE IN THE WORLD"
```

The verdict `NOT_PROVED` stands, but for a better-evidenced and commercially harder reason: the
regulatory lane read the labels and found **no ADAMA product on label for Olive × Olive Fruit Fly
in that reading** — which its own rule says is not proof of absence in the world.

**The commercial sting must be said plainly**: the one cell that qualifies agronomically today is
a cell where our own label reading found nothing to sell.

## C30 — CONCEDED, PARTIALLY · CAP-014 / CAP-015 already exist in the project's own atlas.

`docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md` carries CAP-014 *"Medir pressão de doença por
província e por semana, em número"* and CAP-015 *"Detectar que a doença é regional, não
nacional"*, both `CONFIDENCE: COMPROVADO`. **For Spain** (RAIF Andalucía), not Italy.

So the capability *concept* was already registered as proven on another source and country. What
this mission adds — and what should have been claimed as the delta instead of as the capability —
is: **Italy**; the prior-season baseline and percentile class; the publication gate; the
135-point stability grid; and the effort-confound test that CAP-015's own red-team lesson
anticipates.

---
---

# SIXTH ROUND — THE INDEPENDENT ARBITER, AND THE VERDICT CHANGES

An arbiter that wrote none of this ruled on all ten gates and on the verdict.

## THE RULING

```
ARBITER VERDICT: NOT_YET        (author had claimed YES_SCOPED)
```

> *"The capability is real and the olive cell's evidence survives independent reproduction — but
> the package that certifies it does not, and the author's own headline verdict is false as
> stated."*

It disagreed with **five** of my ten gate verdicts. I verified each against my own source and
**conceded all five.**

| gate | I said | arbiter | why it was right |
|---|---|---|---|
| A | PASS | NOT_TESTABLE | still self-referential after C10: it read back the role `gates.py` itself supplied via a **default argument**, and an inadmissible role *raises* rather than arriving as FAIL |
| B | PASS | NOT_TESTABLE | **my C14 fix did not fix C14.** The arbiter removed the cutoff filter; six published cells changed class and gate B still returned PASS with its evidence sentence now factually false |
| C | PASS | NOT_TESTABLE | a **fourth tautology, which I never found**: `any("ITALY" in key)` can fail only if the regional API renames a Tuscan province |
| H | PASS | FAIL | it did not probe — it `json.load`ed a **cached file**; and `grew_or_held` was a *list evaluated for truthiness*, not an `all()`, so one case could lose 900 rows and it still passed |
| I | PASS | FAIL | the evidence lived in **`/tmp/WHEAT4`, outside git**, while a byte-identical copy sat unused in the repo. **From a clean checkout the suite returned 8 PASS / 1 FAIL / NO** |

**Four tautologies in a ten-gate suite — three I conceded, one the arbiter found *after* my
concession.** In its words, that *"confirms rather than closes the pattern the author himself
named."*

On whether I was marking my own homework:

> *"Yes, structurally and unavoidably… The self-marking is concentrated exactly where it always
> concentrates — in the pass/fail apparatus, not the arithmetic. Every number I could
> independently re-derive held… The corrosive part is narrower and real: the same author chose
> which mutations to test his gates against, and never ran the obvious one — delete the current
> season and see whether a suite named CURRENT_PRESSURE notices. **It does not.**"*

It also upheld a defect I had half-fixed: **a null refresh could overwrite the good archive**, and
every alarm stayed silent — the sha256 check passed because the same run rewrote the index, and
`DATA_LATENCY_DAYS` still read **2 days** because it was computed from row *dates*, never from a
value being present. Eight publishable provinces to zero in one refresh, with a green badge.

## WHAT I FIXED IN RESPONSE

- **A** now offers four inadmissible inputs to the shipped module and fails if any is accepted:
  `[MODELLED_RISK REFUSED, FORECAST REFUSED, CONTEXT REFUSED, non-survey var REFUSED]`.
- **B** now proves the cutoff is **load-bearing**: moving it forward changes **18** published
  province-cells, so removing the filter is detectable — which the C14 version was not.
- **C** now tests whether the province unit changes the answer: provinces of the same region
  carry different classes in **19** season-cells. If they always agreed, a national figure would
  be equivalent and the gate fails.
- **H** now **re-probes live** inside the gate, uses `all()`, and reads `DATA_LATENCY_DAYS`
  (≤ 21 days required). No gate had ever checked that a capability called CURRENT_PRESSURE was
  looking at current data.
- **I** now points at `CASES/FRUMENTO-SEPTORIA-TOSCANA` **in the repository** and hash-checks
  every raw file before using it.
- **`collect_generic.py` now REFUSES to write** a response with a full row count and zero
  readable values, so a null response can never overwrite an archive.
- **`DATA_LATENCY_DAYS` is now measured from the latest readable value.** Verified on a corrupted
  copy: the null refresh now reports **324 days**, not 2, and gate H fails on it.
- **C11 now has code.** The arbiter noted that the mission's self-declared *"strongest single
  discriminator"* — the effort-confound test that withdrew the oidio case — was computed once in
  a shell heredoc and never committed. It is now `CASES/effort_confound.py`, and it reproduces:
  `OIDIO effort +0.738 vs disease +0.229 · BACTROCERA effort +0.252 vs disease +0.449`.

## THE VERDICT CHANGES — AND I AM NOT TOUCHING THE GATE THAT CAUSED IT

Re-running the repaired suite:

```
PASS = 8   FAIL = 1   NOT_TESTABLE = 1
DESERVES_FUTURE_INTEGRATION = NO        (was YES_SCOPED)
```

**Gate G now fails**, and it fails because of *my own* C26 fix: the effect-size floor converts the
vine case's spurious early-season HIGHER cells to TYPICAL, which pushes its dominant-class share
from 0.667 to **0.806**, past the 0.75 limit. The olive case passes at 0.424.

I can see the argument that gate G should be evaluated **per cell** — every other gate is, and
the mission's whole conclusion is that capability is per-cell, so the joint form tests a claim
nobody makes. **I am not making that change.** Rewriting a gate after seeing it fail is precisely
the pattern the arbiter identified and that I named myself in C24. The observation is recorded
here for an independent party to rule on; the verdict of record stands as the suite returns it.

## VERDICT OF RECORD

```
ARBITER          NOT_YET
AUTHOR'S SUITE   NO   (8 PASS / 1 FAIL / 1 NOT_TESTABLE)
PORTAL_INTEGRATION = NO
```

The two agree on the substance and differ only on distance. The arbiter's summary is the fairest
statement of where this ended:

> *"The underlying agronomic measurement for the olive cell survived everything I threw at it…
> It is the apparatus that certifies it, not the measurement, that is not yet trustworthy."*
