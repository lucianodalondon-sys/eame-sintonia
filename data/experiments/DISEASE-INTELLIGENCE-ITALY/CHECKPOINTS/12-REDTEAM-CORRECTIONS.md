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
