# RT1 — RED TEAM: THE STATISTICS AND THE EFFECT FLOOR

Independent attack on `ENGINE/current_pressure.py` and on the certification files
`CERT-V2/p4_cell_state_by_date.json` and `CERT-V2/p5_effect_floor.json`.
I wrote none of the code under attack. Nothing in `ENGINE/` or `CASES/` was modified;
the engine was only called, and the effect floor was switched off through its own
declared parameter `min_positive_sites`.

## 0. BASE OF EVERY NUMBER BELOW, AND THE PROOF THE BASE IS THE PILOT'S OWN

I re-derived the whole step-4 sweep from the raw archives with my own transcription of the
window / percentile arithmetic, keeping the things the shipped output discards: the full
baseline vector per cell, the split of the percentile into (below, equal, above), and the
INTEGER number of positive sites.

- script: `CERT-V2/REDTEAM/rt_core.py` → `CERT-V2/REDTEAM/rt_cells.json`
- equality check: `CERT-V2/REDTEAM/rt_verify.py`

Result: 750/750 cells match `p4_cell_state_by_date.json` on the same keys, with **0
mismatches** on STATE, STATE_WITHOUT_FLOOR, PERCENTILE, BASELINE_N, n_sites, n_visits, and 0
mismatches on VALUE and BASELINE_MEDIAN for every one of the 282 classified cells (the only
differences are that the shipped output omits VALUE on the 380 `UNKNOWN_NO_DATA` cells and
reports a baseline median on the 88 `UNKNOWN_NO_BASELINE` cells; neither is published as a
class). **p4 and p5 are honestly computed from the shipped engine.** Every attack below is
therefore an attack on the definition and on the certification's reasoning, not on arithmetic.

Sample: 3 crops x 30 dates x (10 + 10 + 5) provinces = 750 province-dates.
468/750 (62.4%) are never classified (380 `UNKNOWN_NO_DATA`, 88 `UNKNOWN_NO_BASELINE`).
**282 classified cells** carry every published class. Of those, 40 are HIGHER by rank, 31
survive the floor.

---

# LENS 1 — STATISTICS

## CLAIM S-1 — The HIGHER calls occur at exactly the rate pure chance produces; the certification never measured chance at all.

CLAIM:
Across the certification's own 282 classified cells, the number of `HIGHER_THAN_USUAL` calls
is not larger than the number an exchangeability null — in which the current season is
interchangeable with its own baselines — produces, so the pilot has no evidence that a HIGHER
call marks anything other than the top of a rank.

METHOD:
`CERT-V2/REDTEAM/rt_stats.py` (section A5) and `CERT-V2/REDTEAM/rt_stability.py` (section S2).
Exact leave-one-out randomisation: for each cell, take the set of usable seasons at the same
calendar window (the prior baselines plus the current one) and enumerate all n+1 assignments
of the role "current"; each assignment yields a class under the identical rule (including the
floor). Under exchangeability all n+1 are equally likely, so the mean over assignments is the
exact null probability of each class for that cell. Expectations are summed over cells;
Monte-Carlo p-values use 20,000 draws.
I searched the whole pilot for any pre-existing chance calculation
(`grep -rn "permut|multiplic|by chance|exchangeab|false discovery"` over `*.py *.md *.json`,
excluding REDTEAM): there is permutation code for the *season-agreement* claim
(`CASES/province_agreement.py`, `TOSCANA/horizon.py`) but **none anywhere for the
current-pressure class frequency**.

REPRODUCED: YES

NUMBERS:
| set | classified cells | HIGHER observed | HIGHER expected under the null | obs/exp |
|---|---|---|---|---|
| all | 282 | 40 (floor off) | 62.6 | 0.64 |
| all | 282 | 31 (shipped) | 46.3 | 0.67 |
| walk-forward replays only (6 Sep 2007-2025) | 150 | 36 (floor off) | 36.5 | **0.99** |
| walk-forward replays only | 150 | 31 (shipped) | 33.4 | 0.93 |
| live 2026 dates only | 132 | 4 (floor off) | 26.1 | 0.15 |
| live 2026 dates only | 132 | **0 (shipped)** | 12.8 | 0.00 |

Null spread for the whole sample (20,000 draws): 2.5th / 50th / 97.5th percentile = 49 / 62 / 76
HIGHER calls. Observed 40 sits below the 2.5th percentile.
`LOWER_THAN_USUAL`: observed 79 vs 46.0 expected — the only class in excess of chance
(no null draw in 20,000 reached 79).

IMPACT: **MAJOR** (FATAL to one specific sentence).
It invalidates any reading of p5/p4 as evidence that HIGHER marks an unusual season. In the
walk-forward replay — the very grid gate G uses — HIGHER fires 36 times where chance fires
36.5. It does not invalidate the *definition*: a percentile statement is expected to fire at
its nominal rate under exchangeability. What is fatal is that the certification presents 31
kept HIGHER calls as a demonstrated signal without ever computing the 33.4 that chance alone
supplies.
Caveat stated plainly: the Monte-Carlo p-values treat the 282 cells as independent and they
are not (25 province-cells x 30 dates; the eleven 2026 windows overlap). The **expected
counts are unbiased under any dependence** (linearity of expectation); only the p-values are
optimistic. The sub-samples in the table are exactly the dependence-reduced views.

WHAT_SURVIVES:
The percentile is still a correct, replayable description of where the current window sits in
its own history, and the excess of LOWER (79 vs 46.0) is a real departure from exchangeability
— the archive's recent windows genuinely rank low against their own past. The instrument is
detecting *something*; it is the HIGHER arm, the one the pilot says "can trigger spending",
that carries no excess over chance.

---

## CLAIM S-2 — 114 of 282 published labels depend on a tie convention the pre-registered contract does not state and no gate measures.

CLAIM:
The percentile uses mid-rank ties (`below + 0.5 * equal`); switching to either of the two other
standard conventions changes 114 of 282 published labels, and the module's own pre-registered
docstring never names the rule.

METHOD:
`CERT-V2/REDTEAM/rt_stats.py` section A3. Every classified cell reclassified under
(a) shipped `below + 0.5*equal`, (b) `below` only, (c) `below + equal`.
Contract check: `ENGINE/current_pressure.py` lines 5-36 (the "pre-registered here, before any
output was read" block) says only "The current value is placed as a percentile inside that
historical distribution". The tie rule appears in the code at line 296 and in prose in
`CHECKPOINTS/11-CURRENT-PRESSURE-AND-GENERALIZATION.md` ("ties count as half — deterministic"),
but in neither place is its influence measured, and it is not one of the five parameters
`sensitivity()` varies.

REPRODUCED: YES

NUMBERS:
133/282 cells (47.2%) have at least one baseline season exactly tied with the current value.
Class counts under the three conventions:

| convention | HIGHER | TYPICAL | LOWER |
|---|---|---|---|
| shipped, below + 0.5·equal | 40 | 163 | 79 |
| below only | 40 | 70 | **172** |
| below + equal | **68** | 155 | 59 |

Labels that change: 93/282 under (b), 48/282 under (c), **114/282 (40.4%) under at least one**.
Direction is asymmetric: 0/40 HIGHER calls exist only because of the half-tie, but 20/79 LOWER
calls do.
988 tied baseline pairs exist in the sample; 980 of them (99.2%) are a shared value of exactly
zero, i.e. "no site was positive this year and none was positive that year either".

IMPACT: **MAJOR**.
It invalidates gate F's evidence sentence ("the published label does not depend on arbitrary
parameters", measured over a 135-point grid): the grid varies window, min_sites, baseline
depth and the two thresholds, and holds fixed the one convention that moves 40% of the labels.
It does not touch the HIGHER calls.

WHAT_SURVIVES:
Mid-rank is the defensible choice, and the HIGHER arm is completely insensitive to it (0/40).
The claim is about the certification's completeness, not about the convention being wrong.

---

## CLAIM S-3 — LOWER_THAN_USUAL is arithmetically unreachable in 107 of 282 published cells, so the three-class scale is not a scale.

CLAIM:
Because incidence cannot go below zero and ties count as half, a cell whose baseline is more
than 40% zeros can never be called `LOWER_THAN_USUAL` no matter what the scouts record, and
this is true of 107 of the 282 classified cells.

METHOD:
`CERT-V2/REDTEAM/rt_stats.py` section A2. For each cell I enumerated every *achievable*
incidence (k/n_sites for k = 0..n_sites) and asked which classes it could produce against that
cell's real baseline vector.

REPRODUCED: YES

NUMBERS:
- 107/282 (37.9%) of classified cells: **no achievable value produces LOWER**.
- 0/282: HIGHER is unreachable (by rank alone — see F-5 for what the floor does to this).
- The arithmetic: with a current value of 0 and z zeros among n baselines, p = 0.5·z/n, so
  LOWER (p ≤ 0.20) requires z ≤ 0.4n. At n = 5 that is z ≤ 2; at n = 20, z ≤ 8.
- 133/282 cells have a current value of exactly 0. Of those, **92 are published as
  `TYPICAL_FOR_THE_DATE`** and 41 as LOWER. "Not one monitored field had the issue" is
  published as "typical for the date" 92 times.

IMPACT: **MAJOR**.
It invalidates the symmetry the output implies. `TYPICAL_FOR_THE_DATE` silently merges two
states a user would never merge — "middling pressure" and "zero pressure, as in most years".
Any downstream product that colours TYPICAL as amber-between-green-and-red is mis-rendering 92
cells in this sample.

WHAT_SURVIVES:
Nothing here is a false statement: a zero equal to the historical typical value genuinely is
typical. The defect is expressive, not arithmetical, and it does not touch HIGHER.

---

## CLAIM S-4 — The percentile's resolution is one baseline season; 83 of 282 labels are less than one season from flipping.

CLAIM:
With 5 to 20 baseline seasons the percentile moves in steps of 0.5/n (0.10 at n=5), so single
seasons, not distributions, decide the published class.

METHOD: `CERT-V2/REDTEAM/rt_stats.py` section A1. For each cell I computed the slack, in whole
seasons, between the rank score and the nearest threshold that changes the class.

REPRODUCED: YES

NUMBERS:
BASELINE_N ranges 5..20, median 13; the grid step is 0.10 at n=5 and 0.025 at n=20. 20 cells
sit at the floor of n=5.
**83/282 (29.4%)** labels have less than one season of slack: 17 HIGHER (of 40), 25 LOWER (of
79), 41 TYPICAL (of 163). Put plainly, in 17 of the 40 HIGHER calls, one baseline season
moving from below the current value to above it removes the call.
At n = 5 the threshold p ≥ 0.80 is reached by beating 4 of the 5 prior seasons — or by beating
3 and tying 2.
Independent confirmation from a different direction (`rt_stability.py` S1, non-parametric
bootstrap of the site sample, 1,000 replicates per cell): resampling the monitored fields
changes the published class with mean probability 0.100 for HIGHER cells (0.151 if the
baseline seasons are resampled too), and **7 of the 31 shipped HIGHER calls have a greater
than 25% chance of not being HIGHER** on a redraw of the same province.

IMPACT: **MINOR to MAJOR** — MINOR against the definition (a small-n percentile is honestly
labelled as such and BASELINE_N is published), MAJOR against the sentence "31 kept" being read
as 31 solid calls.

WHAT_SURVIVES:
BASELINE_N is emitted on every cell, and MIN_BASE=5 is declared. A user who reads
BASELINE_N can see the resolution. Nothing is hidden; nothing is quantified either.

---

## CLAIM S-5 — Gate G ("the statement discriminates between seasons", dominant class share ≤ 0.75) has no power: a labeller that ignores the data passes it.

CLAIM:
The 0.75 bar cannot separate a real season signal from noise; it can only fail a nearly
constant labeller.

METHOD: `CERT-V2/REDTEAM/rt_gateg.py`. Gate G's own grid (the 6-September walk-forward,
2007-2026, every province, per crop) with (i) the exact leave-one-out exchangeability null,
20,000 draws, and (ii) three synthetic labellers.

REPRODUCED: YES

NUMBERS:
| crop | cells | observed dominant share | shipped gate verdict | null share 2.5/50/97.5 | P(a no-season-effect null passes gate G) |
|---|---|---|---|---|---|
| OLIVE | 132 | 0.432 | PASS | 0.439 / 0.523 / 0.606 | **1.0000** |
| VINE | 36 | 0.806 | FAIL | 0.667 / 0.778 / 0.889 | 0.3367 |
| both | 168 | 0.512 | — | 0.506 / 0.577 / 0.649 | 1.0000 |

(My OLIVE share 0.432 vs the shipped 0.424 in `ENGINE/gates.json`; VINE matches exactly at
0.806. The shipped verdict is already FAIL because of VINE.)
Synthetic labellers on the same grid: a **uniform random labeller that never looks at the data**
has median dominant share 0.369 and passes 2000/2000; a "nominal 20/60/20 rank labeller"
has median 0.601 and passes 2000/2000; only an always-TYPICAL labeller fails (0/2000).
The minimum possible dominant share with three classes is 0.333, so the bar 0.75 sits
two-thirds of the way to the degenerate end.
Where OLIVE's "discrimination" actually comes from: observed 31 HIGHER vs 31.6 expected under
the null (ratio 0.98), 44 LOWER vs 31.6 expected. Every bit of the departure is in the LOWER
class.

IMPACT: **MAJOR**.
It invalidates gate G's evidence sentence as a discrimination test. Gate G is a
non-degeneracy check and should be described as one. It does not invalidate the gate's
verdict, which is already FAIL for vine.

WHAT_SURVIVES:
OLIVE's observed 0.432 is below the null's 2.5th percentile, so the olive labels are more
evenly spread than 97.5% of null draws. That is a genuine, if modest, departure — and gate G,
as written, cannot tell you that, because it would have passed either way.

---

## CLAIM S-6 — 69 of 282 published labels change under an equally defensible definition of the same quantity.

CLAIM:
INCIDENCE is "share of sites whose MAXIMUM over every visit in the 28 days exceeds zero", which
is mechanically monotonic in how often scouts happened to visit. Recomputing the identical
pipeline with one visit per site changes 69 of 282 labels.

METHOD: `CERT-V2/REDTEAM/rt_effort.py`. Whole sweep recomputed with the earliest readable
observation per site inside the window, everything else identical (same window, same
MIN_SITES, same baseline rule, same thresholds, same floor).

REPRODUCED: YES

NUMBERS:
282 cells classified under both definitions, 0 lost. **69/282 (24.5%) change class.**
Confusion: HIGHER→HIGHER 25, HIGHER→TYPICAL 6, TYPICAL→HIGHER 15, TYPICAL→LOWER 8,
LOWER→LOWER 39, **LOWER→TYPICAL 40**, TYPICAL→TYPICAL 149.
25 of the 31 shipped HIGHER calls (80.6%) survive.
Magnitude example, OLIVE / Arezzo / 2011-09-06: incidence 0.825 under the shipped metric,
0.075 with one visit per site — the same window, the same fields.
Direct effort measurement (from the same cells): the within-cell rank correlation between
visits-per-site and the published incidence is positive in 74 of 115 province-window series,
mean Spearman +0.101, median +0.122.

IMPACT: **MAJOR** for the LOWER arm, **MINOR** for the HIGHER arm.
Honest limit on this finding: it is *definition* sensitivity, not proven effort confounding.
The two mechanisms are entangled — dropping repeat visits both removes the effort channel and
creates more zero-vs-zero ties, which pushes LOWER toward TYPICAL (see S-2/S-3), and the
direct effort comparison below (WHAT I COULD NOT BREAK, item 6) went the *other* way. I cannot
separate them with the data on disk.

WHAT_SURVIVES:
The metric is declared, applied identically to current and baseline windows, and its
definition is the same one used for the season outcome. Four fifths of the HIGHER calls are
invariant to it.

---

## CLAIM S-7 — The class tracks how many fields were visited, through the tie mechanism.

CLAIM:
The probability of a HIGHER call rises with n_sites, and the mechanism is the tie term: in
provinces with 8-14 monitored sites, 39.2% of baseline seasons tie exactly with the current
value, against 3.1% in provinces with 40+ sites, and each tie pins the percentile toward 0.5
and manufactures TYPICAL.

METHOD: `CERT-V2/REDTEAM/rt_stats.py` section A6 plus the tie-vs-n_sites cross-tabulation in
the same run.

REPRODUCED: YES, for the mechanism; PARTLY for the effect, which is confounded with crop.

NUMBERS:
All cells, floor OFF: P(HIGHER) = 7/71 (9.9%) at 8-14 sites, 22/150 (14.7%) at 15-39,
11/61 (18.0%) at 40+.
Share of baseline seasons exactly tied with the current value: 0.392 at 8-14 sites, 0.293 at
15-39, **0.031** at 40+. Mean n_sites is 20.7 in cells that have a tie and 41.8 in cells that
do not.
Confounding, stated honestly: mean incidence also rises across those buckets (0.089 / 0.305 /
0.381) and the buckets are not crop-balanced. Within OLIVE alone, P(HIGHER) floor-off is
0.083 / 0.259 / 0.180 across the three buckets — not monotonic. So the *tie* mechanism is
demonstrated; a clean n_sites→class effect independent of crop and incidence is **NOT KNOWN**.
What would settle it: cells matched on crop, calendar window and true incidence with different
n_sites — the archive has too few to do this at MIN_SITES=8.
Rounding is NOT the cause: all 988 tied baseline pairs are exactly equal before INCIDENCE is
rounded to 4 decimals (0 artificial ties).

IMPACT: **MINOR**, and NOT KNOWN for the strong version.

WHAT_SURVIVES:
The published incidence is a census of the monitored fields in the window, not an estimate of
a wider population, and n_sites is emitted on every cell.

---

# LENS 2 — THE EFFECT FLOOR (MIN_POSITIVE_SITES = 5)

## CLAIM F-1 — p5's two headline tests ("0 failing open, 0 failing closed") are the floor's own predicate read back, and cannot return anything but 0.

CLAIM:
`FALSE_POSITIVE_TEST` ("a HIGHER call the floor KEPT although fewer than 5 sites are positive")
and `FALSE_NEGATIVE_TEST` ("withheld although 5 or more are positive") are logical identities
of the rule under test, not measurements of it.

METHOD:
Read of `CERT-V2/p4_date_and_floor.py` lines 172-215 against `ENGINE/current_pressure.py`
lines 307-311: `kept` is defined as `STATE == HIGHER`, which the engine grants only when
`n_sites * INCIDENCE >= 5`; `kept_with_thin_base` then filters `kept` on
`n_positive_sites < 5`. The two conditions are complements of the same inequality.
Empirical demonstration that the tests are inert for **every** floor value:
`CERT-V2/REDTEAM/rt_floor.py` re-runs both tests at T = 0,1,...,20,25,30,40,50,70 and at
4.5, 5.5, 6.5.

REPRODUCED: YES

NUMBERS:
Across all 29 floor values swept, "fails open" = 0 in **29/29** cases. "Fails closed" = 0 in
**26/29** cases; the three exceptions (2 cells at T=1, 2 at T=4, 2 at T=30) are floating-point,
not substantive — see F-9. At the shipped T=5 both are 0, as p5 reports.
So p5's two tests would have printed 0 and 0 for a floor of 1, of 5, of 20 or of 70.

IMPACT: **FATAL** to the sentence "with 0 failing open and 0 failing closed".
It invalidates that sentence as evidence for MIN_POSITIVE_SITES=5, and with it the word
"PROVED" in the certification's summary of step 5. It does not invalidate the floor itself,
which may still be a good rule for other reasons.

WHAT_SURVIVES:
The rest of p5 — the positive-site distributions of the kept and withheld sets — is real
measurement, and it is blind in the sense p5 claims (it includes dates and a crop that did not
motivate the floor).

---

## CLAIM F-2 — The "clean gap" (kept min 7, withheld max 4) is a property of the floor's own definition plus a coincidence, and it does not select the value 5.

CLAIM:
The floor guarantees withheld < T ≤ kept, so the only non-tautological content of the reported
gap is that no kept call has exactly 5 or 6 positive sites; and a sweep shows the data actually
prefers a floor of 11-18, which yields a gap almost three times larger.

METHOD: `CERT-V2/REDTEAM/rt_floor.py` (F2/F3), sweeping the floor over T = 0..70 and recording
the partition of the 40 rank-HIGHER cells, the gap, and the number of distinct outcomes.

REPRODUCED: YES

NUMBERS:
Histogram of positive sites over all 40 rank-HIGHER cells:
`1:3, 2:2, 3:1, 4:3, 7:1, 10:1, 18:1, 20:1, 22:1, 23:3, 24:2, 26:2, 29:1, 30:2, 31:2, 32:1,
33:1, 34:3, 35:3, 41:1, 46:1, 52:1, 55:1, 59:1, 69:1`

| floor T | kept | withheld | kept min | withheld max | gap |
|---|---|---|---|---|---|
| 4 | 32 | 8 | 4 | 4 | 0 |
| **5, 6, 7** | **31** | **9** | **7** | **4** | **3** |
| 8, 9, 10 | 30 | 10 | 10 | 7 | 3 |
| **11 … 18** | 29 | 11 | 18 | 10 | **8** |
| 19, 20 | 28 | 12 | 20 | 18 | 2 |

T ∈ {5, 6, 7} produce the identical partition, so the certification's evidence identifies the
floor only to within three integers. Over T = 0..70 there are **27 distinct outcomes**; the
"clean gap" criterion, applied consistently, prefers T = 11-18 (gap 8) over T = 5 (gap 3).

IMPACT: **MAJOR**.
It invalidates the gap as evidence for the value 5. Combined with F-1, nothing in p5
distinguishes 5 from 6, 7, or 11.

WHAT_SURVIVES:
The partition itself is stable: any floor from 5 to 18 keeps 29-31 of the 40 and withholds the
same handful of thin calls. The *decision* is robust even though the *value* is not identified.

---

## CLAIM F-3 — The floor does not improve the calls' excess over chance; it shrinks signal and noise in the same proportion.

CLAIM:
If the floor were a discriminator it would raise the ratio of observed HIGHER calls to the
number chance produces. It does not.

METHOD: `CERT-V2/REDTEAM/rt_stability.py` section S2 — the S-1 exchangeability null recomputed
with the floor applied inside the null, at each floor value.

REPRODUCED: YES

NUMBERS:
| floor | observed HIGHER | expected under null | obs/exp |
|---|---|---|---|
| 0 (off) | 40 | 62.6 | 0.639 |
| 3 | 35 | 51.6 | 0.679 |
| **5 (shipped)** | **31** | **46.3** | **0.670** |
| 8 | 30 | 40.6 | 0.738 |
| 15 | 29 | 35.3 | 0.821 |
| 20 | 28 | 28.3 | 0.990 |
| 50 | 4 | 2.4 | 1.690 |

Going from no floor to the shipped floor moves the ratio from 0.639 to 0.670 — a change of
0.031 — while removing 9 calls. At no floor value below 50 does the pipeline emit more HIGHER
calls than chance.

IMPACT: **MAJOR**.
It invalidates "effect-size floor" as a claim about statistical discrimination. The floor is a
severity threshold — a policy about how much disease is worth telling someone about — and
should be defended as one. If "excess over chance" were the criterion, the sweep selects
T ≈ 20, not 5.

WHAT_SURVIVES:
A severity threshold is a legitimate and arguably necessary product decision. The floor
demonstrably removes the specific pathology it was built for (see WHAT I COULD NOT BREAK).

---

## CLAIM F-4 — On the certification's own sample the floor is indistinguishable from a flat rule "incidence must be at least 50%".

CLAIM:
The floor is presented as an effect size scaled by sample size (`n_sites * INCIDENCE`), but on
these 40 cells it partitions them identically to a rule that ignores n_sites entirely.

METHOD: `CERT-V2/REDTEAM/rt_floor.py` section F4 — the floor's partition compared against
plain incidence thresholds and against raised MIN_SITES.

REPRODUCED: YES

NUMBERS:
Incidence of the 31 kept HIGHER calls: min 0.550, then 0.574, 0.788, 0.825, … up to 1.000.
Incidence of the 9 withheld: 0.0147, 0.0244, 0.0336, 0.0833, 0.1333, 0.1429, 0.1667, 0.300,
0.400.
The rule "INCIDENCE < 0.50 → not HIGHER" reproduces the floor's partition **exactly**
(symmetric difference 0 of 40). Nearer thresholds are close but not identical (0.20/0.25/0.30:
symmetric difference 2; 0.15: 3; 0.10: 5).
So every HIGHER call this pilot publishes has at least 55% of its monitored fields positive.
That fact is nowhere in p5, which reports positive-site counts (min 7, median 31, max 69) and
monitored-site counts separately but never their ratio.

IMPACT: **MAJOR** to the floor's stated rationale, **NONE** to its output.
The n_sites-scaling is doing no work on this sample. It will start doing work the moment a
province with 200 monitored sites and 3% incidence appears — where the floor says HIGHER and a
50% incidence rule says no. No such cell exists in the 750.

WHAT_SURVIVES:
The resulting partition is a strong one, and the fact that every published HIGHER call rests on
≥55% incidence is the single most reassuring number I found. It should be in the certification.

---

## CLAIM F-5 — The floor creates a new failure: it makes HIGHER unreachable for small provinces, and it silences two of the three crops entirely.

CLAIM:
The floor imposes a per-province incidence bar of 5/n_sites, which in a 10-site province is 50%
and in a 119-site province is 4.2%; for 66 of 282 classified cells that bar is higher than any
incidence ever recorded in that province at that calendar window.

METHOD: `CERT-V2/REDTEAM/rt_floor.py` section F5 — for every classified cell, the incidence the
floor demands (5/n_sites) against the maximum incidence over all usable seasons at that same
window in that same province.

REPRODUCED: YES

NUMBERS:
The bar by province size: 8 sites → 0.625, 10 → 0.500, 12 → 0.417, 15 → 0.333, 20 → 0.250,
30 → 0.167, 41 → 0.122, 68 → 0.074, 119 → 0.042.
**66/282 (23.4%)** of classified cells demand an incidence higher than anything on record there:
- by province size: **39/71 (54.9%)** at 8-14 monitored sites, 24/150 at 15-39, 3/61 at 40+;
- by crop: 55/107 (51.4%) of VINE cells, 10/166 of OLIVE, 1/9 of WHEAT.

Consequence on the published output: after the floor, **VINE never emits a HIGHER call at any
of the 30 dates (0/107 classified cells) and WHEAT never emits one (0/9)**. All 31 HIGHER calls
in the certification's sample are OLIVE.
Effect of the floor on HIGHER rate by province size (floor off → shipped): 9.9% → 2.8% at 8-14
sites, 14.7% → 14.0% at 15-39, 18.0% → 13.1% at 40+. The burden falls 5x harder on the
smallest provinces.

IMPACT: **MAJOR**.
It invalidates the implicit claim that the floor is neutral across cells. It converts a
regional instrument into one that can only speak for provinces with dense monitoring, and it
does so silently — a province where HIGHER is unreachable is published as
`TYPICAL_FOR_THE_DATE`, indistinguishable from a province where HIGHER was reachable and the
evidence did not support it.

WHAT_SURVIVES:
The direction is conservative: the floor errs toward silence, which is the right direction for
a word that triggers spending. And a 10-site province genuinely cannot support a confident
statement about a 4% incidence — the floor is not wrong to be sceptical there, only silent
about being sceptical.

---

## CLAIM F-6 — All 31 "kept" HIGHER calls are historical replays of one crop; the floor has never let a HIGHER call through in the live season.

CLAIM:
The certification's headline ("withheld 9, kept 31") describes a kept set that contains zero
live 2026 calls and zero non-olive calls, so the "kept" arm proves nothing about the product's
live behaviour or its generality across crops.

METHOD: `CERT-V2/REDTEAM/rt_floor.py` section F6, splitting the 40 rank-HIGHER cells by date
(the 11 dates in the live 2026 season vs the 19 walk-forward 6-September replays of 2007-2025)
and by crop. Cross-checked against p5's own `BY_CROP` block, which already shows
`OLIVE|KEPT_HIGHER: 31` and no `VINE|KEPT_HIGHER` or `WHEAT|KEPT_HIGHER` key.

REPRODUCED: YES

NUMBERS:
- HIGHER calls kept, in the live 2026 season, across 11 dates and 3 crops: **0**.
- HIGHER calls kept, in the 2007-2025 walk-forward replays: **31, all OLIVE**.
- Rank-HIGHER calls that occurred in the live 2026 season: 4 (Firenze, Grosseto, Livorno olive
  on 2026-07-15; Arezzo wheat on 2026-04-15). The floor withheld **4 of 4**.
- The floor's 9 withheld split 4 live / 5 historical; its 31 kept split 0 live / 31 historical.

Verified directly against the certification's own file, not only against my recomputation —
counting `STATE == HIGHER_THAN_USUAL` in `CERT-V2/p4_cell_state_by_date.json`:
0 in 2026, 31 in the hindcast, `Counter({'OLIVE': 31})` by crop, and 4 rank-HIGHER
(`STATE_WITHOUT_FLOOR`) in 2026.

IMPACT: **MAJOR**.
It invalidates the generality the sample section of p5 claims ("includes dates, provinces and a
crop (WHEAT) that were NOT part of the sample that motivated the floor"). Those extra dates and
that extra crop appear only in the *withheld* arm. The discriminating behaviour — keeping broad
calls — was measured on one crop, in years already past.

WHAT_SURVIVES:
The 31 kept calls are still 31 genuine walk-forward evaluations with no leakage, and 2026 may
simply be a quiet olive year — the null comparison in S-1 (4 observed rank-HIGHER vs 26.1
expected in 2026) is consistent with a genuinely quiet season rather than with a broken floor.

---

## CLAIM F-7 — Three of the nine withheld calls are the highest incidence ever recorded in that province at that window, and they are published as "TYPICAL_FOR_THE_DATE".

CLAIM:
A user-facing false negative — the tool says "typical" about a record — occurs 3 times in the
certification's own 750-row sample, and p5's FALSE_NEGATIVE_TEST is definitionally incapable of
seeing any of them.

METHOD: `CERT-V2/REDTEAM/rt_floor.py` — for each withheld cell, the current incidence against
the maximum over all usable seasons at that same calendar window in that same province.

REPRODUCED: YES

NUMBERS:
| crop | date | province | incidence | percentile | sites | positive | historical max at this window | is a record |
|---|---|---|---|---|---|---|---|---|
| OLIVE | 2026-07-15 | Grosseto | 0.0336 | 1.000 | 119 | 4 | 0.0336 | **YES** |
| OLIVE | 2026-07-15 | Firenze | 0.0147 | 0.929 | 68 | 1 | 0.0385 | no |
| OLIVE | 2026-07-15 | Livorno | 0.0244 | 0.833 | 41 | 1 | 0.1111 | no |
| VINE | 2016-09-06 | Firenze | 0.1333 | 0.875 | 30 | 4 | 0.5714 | no |
| VINE | 2018-09-06 | Firenze | 0.1429 | 0.889 | 14 | 2 | 0.5714 | no |
| VINE | 2019-09-06 | Pisa | 0.3000 | 0.833 | 10 | 3 | 0.5278 | no |
| VINE | 2020-09-06 | Arezzo | 0.1667 | 0.900 | 12 | 2 | 0.3000 | no |
| VINE | 2020-09-06 | Grosseto | 0.4000 | 1.000 | 10 | 4 | 0.4000 | **YES** |
| WHEAT | 2026-04-15 | Arezzo | 0.0833 | 1.000 | 12 | 1 | 0.0833 | **YES** |

3 of 9 are records, **2 of the 3 are live 2026 dates**. p5 reports FALSE_NEGATIVES = 0 because
it defines a false negative as "withheld although ≥5 sites are positive", which the floor
forbids by construction (F-1).

Where the floor changes a decision that matters: **OLIVE / Grosseto / 2026-07-15** — 119
monitored groves, 4 positive, first appearance of the season, higher than the same window in
any of 17 prior seasons, published as `TYPICAL_FOR_THE_DATE`. Whether that is right is an
agronomic question (4 groves in 119 is not an outbreak; the certification's own note says none
of those groves reached the source's red band), but it is a decision, not a null operation.
Where the floor changes nothing that matters: **VINE / Firenze / 2018-09-06** — 14 sites, 2
positive, a replay of a season eight years past, changing a hindcast row that no one acts on.

IMPACT: **MAJOR**.
It invalidates "0 false negatives" as a claim about the instrument. The correct statement is
"0 false negatives *by a definition that cannot produce one*", and by a user's definition there
are 3.

WHAT_SURVIVES:
All three records are tiny in absolute terms (4/119, 4/10, 1/12). A reasonable person can
defend withholding all three. What cannot be defended is reporting the count as zero.

---

## CLAIM F-8 — The floor is an undeclared parameter: it is absent from the pre-registered PARAMETERS block, from the published PARAMS output, from the sensitivity grid gate F reads, and from the mutation suite.

CLAIM:
`ENGINE/current_pressure.py` declares "PARAMETERS (all of them, declared; sensitivity is
measured in sensitivity())" and lists four; MIN_POSITIVE_SITES is a fifth and is in none of the
places that sentence promises.

METHOD: direct reading plus
`grep -rn "MIN_POSITIVE_SITES|min_positive_sites"` over the whole pilot (`*.py *.md *.json`).

REPRODUCED: YES

NUMBERS:
The parameter appears in exactly 4 files: `ENGINE/current_pressure.py` (definition, signature,
the rule), `CERT-V2/p4_date_and_floor.py`, `CERT-V2/p5_effect_floor.json`, and nowhere else.
Specifically:
- `ENGINE/current_pressure.py` lines 28-32, the "PARAMETERS (all of them)" block: lists
  WINDOW_DAYS, MIN_SITES, MIN_BASE, HIGH_P/LOW_P. **Not the floor.**
- lines 265-266, the `PARAMS` dict written into every published cell: the same four.
  **Not the floor.** A consumer of the output cannot tell the floor was applied unless the cell
  happens to carry a `HIGHER_WITHHELD` string.
- `sensitivity()` lines 317-334: a 135-point grid over window (5) x min_sites (3) x
  min_base (3) x thresholds (3). The floor is held at 5 in all 135 points, so gate F's
  "the published label does not depend on arbitrary parameters" is measured with the most
  consequential parameter frozen.
- `CERT-V2/p3_mutation.py`, `p2_gate_inventory.py`, `p7_code_vs_value.py`: **0 hits.** The
  mutation suite never mutates the floor, so no gate is shown able to detect its removal.

IMPACT: **MAJOR**.
It invalidates the docstring's completeness claim and narrows gate F's evidence sentence. It
also means the value 5 has never been subjected to the treatment every other parameter got.

WHAT_SURVIVES:
The floor IS a named function argument with a default, it IS switchable, p4 switches it off
cleanly, and every withheld cell carries a human-readable `HIGHER_WITHHELD` sentence naming
the floor value. The mechanism is transparent; the bookkeeping around it is not.

---

## CLAIM F-9 — The floor compares a rounded product, so "5 positive sites" is not what it enforces.

CLAIM:
`cur["n_sites"] * v` uses INCIDENCE already rounded to 4 decimals, so a cell with exactly 5
positive sites fails the floor at 92 of the 192 site-counts from 8 to 199.

METHOD: `CERT-V2/REDTEAM/rt_floor.py` section F7 — enumeration of n where
`round(5/n, 4) * n < 5`, plus a search of the sample for affected cells.

REPRODUCED: YES

NUMBERS:
92 of the 192 values of n_sites in 8..199 are affected, including 11, 13, 14, 15, 17, 24, 26,
29, 119. Worked example: 5 positives of 11 sites → INCIDENCE 0.4545 → product 4.9995 < 5 →
withheld, although 5 sites are positive.
Cells in this sample where n_pos = 5 and the product is below 5: **2**
(OLIVE/Pisa/2026-09-06, 45 sites, product 4.99950; OLIVE/Grosseto/2022-09-06, 37 sites,
product 4.99870). Both are `LOWER_THAN_USUAL`, so the floor never fired on them and no
published label is wrong today.
Side effect: this is the *only* way p5's FALSE_NEGATIVE_TEST can ever return non-zero, because
that test compares `round(VALUE*n_sites, 1)`, which rounds 4.9995 back to 5.0. My sweep saw it
fire on exactly this edge at T = 1, 4 and 30 (2 cells each).

IMPACT: **MINOR**. Zero published labels affected in this sample; a latent off-by-epsilon.

WHAT_SURVIVES:
Everything. The defect is real and currently harmless, and the fix is one line
(`cur["n_sites"] * v` → the integer positive-site count, which `_window_value` already computes
and then throws away).

---

## COLLATERAL FINDING (outside my two lenses, reported because it touches the floor's sample)

The third crop in the effect-floor certification is labelled `WHEAT x SEPTORIA` everywhere
(`CASES/FRUMENTO-SEPTORIA-TOSCANA/`, `outcomes_v372.json`, `CERT-V2/p4_date_and_floor.py`
line 38, `p8_crop_semantics.json`), and it reads `id_survey_var = 372`. The source's own schema
in `CASES/FRUMENTO-SEPTORIA-TOSCANA/collection_index.json` declares:

- 372 = `Intensità Oidio` (powdery mildew intensity) — the variable actually read
- 382 = `Intensità Septoria` — the Septoria variable, never read

The code table confirms it: codes 1599/1628/1602/1603/1629/1605 belong to var 372 and
1592/1594/1595/1596/1597/1598 to var 382. So the pilot's "wheat x Septoria" cells measure
powdery mildew on wheat. One withheld row in `p5_effect_floor.json`
(WHEAT / SEPTORIA / 2026-04-15 / Arezzo) carries this label. I did not attack this systematically
— it belongs to a semantics lens, not mine — but it is load-bearing for p5's claim to have
tested "a crop that was NOT part of the sample that motivated the floor", because the ISSUE
attached to that crop is wrong.
**NOT KNOWN**: whether this is a naming slip or a collection slip. What would settle it: run
the same case on var 382 and compare — if 382 has data, the case was collecting the wrong
column; if 382 is empty for Toscana, the directory name is simply mislabelled.

---

# WHAT I COULD NOT BREAK

Each of these is an attack I ran and lost.

1. **The floor removes the exact pathology it was built for.** The motivating failure was
   "one detection scores percentile ~1.0 against a run of zeros and is published as HIGHER".
   Measured blind across all 750 cells: of the 31 shipped HIGHER calls, **0 have an all-zero
   baseline** and **0 have a zero baseline median**; the smallest incidence ever published as
   HIGHER is **0.550** and the smallest positive-site count is **7**. Without the floor, 1 of 40
   has an all-zero baseline and 8 of 40 have a zero median. The floor works.
   (`rt_stats.py` A4.)

2. **The floor is not redundant with MIN_SITES.** Raising MIN_SITES to 15 catches only 5 of the
   floor's 9 withheld calls, leaves 4 uncaught, and destroys 71 of 282 classified cells as
   collateral; at MIN_SITES=30 it still catches only 5 of 9 and destroys 183 of 282. No
   MIN_SITES value reproduces the floor's partition. (`rt_floor.py` F4.)

3. **Rounding creates no artificial ties.** I expected `round(INCIDENCE, 4)` to manufacture
   ties between different fractions. All **988 of 988** tied baseline pairs in the sample are
   exactly equal before rounding. The tie term is real, not a rounding artefact.

4. **No HIGHER call rests on the half-tie term.** 0 of 40 rank-HIGHER calls would lose the
   label if ties counted as strictly-not-below. The tie sensitivity is entirely in the LOWER
   and TYPICAL arms.

5. **The certification's own arithmetic is exact.** My independent transcription reproduces
   p4/p5 on 750/750 cells with 0 mismatches on 6 fields and 0 on VALUE/BASELINE_MEDIAN for all
   282 classified cells, and `n_positive_sites` in p4 agrees with the true integer positive
   count in 282/282 cases. There is no hidden fudge.

6. **The LOWER excess is not a simple survey-effort deficit.** I predicted that the current
   28-day window is scouted less intensively than the settled baseline windows, which would
   depress incidence mechanically and manufacture LOWER. Measured: current-window visits per
   site minus the baseline mean is **+0.013** for LOWER cells (median +0.168) and **-0.040**
   for HIGHER cells. The sign is the opposite of my hypothesis. The 79-vs-46 LOWER excess is
   **NOT KNOWN** in origin; what would settle it is a per-season register of scouting protocol
   changes, or an independent regional record of olive-fly and oidio pressure.

7. **Determinism and replayability.** Two independent computations of the same 750 cells,
   written by different hands from the same archive, agree cell for cell. AS_OF is genuinely an
   input; nothing reads the clock.

8. **Attainability of HIGHER by rank.** I expected to find baseline sizes at which p ≥ 0.80 is
   arithmetically unreachable. There are none: 0 of 282 cells. (LOWER is a different story —
   see S-3.)

---

# SUMMARY OF IMPACT

| # | claim | impact |
|---|---|---|
| F-1 | p5's "0 failing open / 0 failing closed" is the floor's own predicate | **FATAL** to that sentence |
| S-1 | HIGHER fires at the rate chance produces (36 vs 36.5 walk-forward) | MAJOR |
| S-2 | 114/282 labels depend on an unmeasured tie convention | MAJOR |
| S-3 | LOWER unreachable in 107/282 cells | MAJOR |
| S-5 | gate G passes a labeller that ignores the data, 2000/2000 | MAJOR |
| S-6 | 69/282 labels change under an effort-invariant metric | MAJOR (LOWER) / MINOR (HIGHER) |
| F-2 | the "clean gap" prefers a floor of 11-18, not 5 | MAJOR |
| F-3 | the floor does not raise obs/exp (0.639 → 0.670) | MAJOR |
| F-4 | the floor = "incidence ≥ 50%" on this sample | MAJOR to its rationale |
| F-5 | HIGHER structurally unreachable in 66/282 cells; 2 of 3 crops silenced | MAJOR |
| F-6 | 31/31 kept calls are one crop, zero live | MAJOR |
| F-7 | 3 records published as TYPICAL; p5 reports 0 false negatives | MAJOR |
| F-8 | the floor is absent from PARAMS, the sensitivity grid and the mutation suite | MAJOR |
| S-4 | 83/282 labels within one baseline season of flipping | MINOR-MAJOR |
| S-7 | class tracks n_sites through ties; clean effect NOT KNOWN | MINOR |
| F-9 | the floor compares a rounded product | MINOR |

The single sentence I would strike from the certification: *"with 0 failing open and 0 failing
closed"*. It cannot be false.
The single sentence I would add: *"every HIGHER call this instrument publishes rests on at
least 55% of the monitored fields being positive"* — which is true, is the strongest thing in
the data, and is nowhere in p5.

---

## FILES WRITTEN BY THIS RED TEAM (all under `CERT-V2/REDTEAM/`, nothing else touched)

| file | what it does |
|---|---|
| `rt_core.py` | rebuilds the 750-cell sweep keeping baselines, tie decomposition, integer positive counts → `rt_cells.json` |
| `rt_verify.py` | cell-for-cell equality against `p4_cell_state_by_date.json` |
| `rt_stats.py` | A1 resolution, A2 attainability, A3 ties, A4 zero baselines, A5 exchangeability null, A6 n_sites → `rt_stats.json` |
| `rt_floor.py` | F1-F7 floor sweep, gap, redundancy, structural unreachability, rounding → `rt_floor.json` |
| `rt_gateg.py` | gate G null distribution and synthetic labellers → `rt_gateg.json` |
| `rt_stability.py` | site-resampling bootstrap and the floor-vs-null ratio → `rt_stability.json` |
| `rt_effort.py` | the whole sweep recomputed with one visit per site → `rt_effort.json` |
