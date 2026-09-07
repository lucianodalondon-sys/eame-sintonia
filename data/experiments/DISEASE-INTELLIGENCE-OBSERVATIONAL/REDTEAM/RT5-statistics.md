# RT5 — RED TEAM, LENS: STATISTICS

Independent adversarial review of the observational engine
(`engine/di_core.py`, `engine/di_observe.py`). I wrote none of this code and did
not modify it. Everything below is reproduced by scripts in this folder.

---

## 0. WHAT I AUDITED, AND A WARNING ABOUT IT

**The engine changed while this audit was running.** At the start of the session
`di_core.load_visits` decided usability PER VISIT (any bad column killed the whole
visit). Partway through, it changed to PER MEASUREMENT. That moved real numbers:
Grosseto's 56-day pooled rate went from 0.7556% to 0.7630% because one visit
(grove 9133, 2026-08-03, ACTIVE 7 of 100, TOTAL 106 of 100) stopped being
discarded. Every number in this report was recomputed after the change.

Everything below is pinned to these exact bytes:

| file | sha256 |
|---|---|
| `engine/di_core.py` | `e56dc697a3d57acdb85b97f7aeb615f57021657c74dac31f95badc29caf2821b` |
| `engine/di_observe.py` | `8fb727f137b6e2d0593a21912a61e2220a8c8c04ce4f64ed33aa33bda2b52f39` |

Data: 79,251 visits loaded at `as_of` 2026-09-06; usable per measurement 75,663
(ACTIVE), 75,655 (DAMAGING), 75,565 (TOTAL).

**Harness and its own gate.** `di_observe.pooled()` rescans all 79,251 visits on
every call and `cell()` calls it ~90 times, so one province-cell costs ~1.5 s —
too slow for thousands of configurations. `rt5_lib.py` rebuilds the same
arithmetic on a per-province date-sorted index (~6 ms per cell, 250x). It is not
trusted on its word:

* `rt5_00_verify.py` — 10 of 10 provinces reproduce `di_observe.cell()` **exactly**
  at the declared configuration (value, n_visits, n_sites, drupes, baseline_n,
  matched seasons, n_lower, n_higher, historical_state, trend, trend points,
  publishable).
* `rt5_00b_verify_offdefault.py` — **0 mismatches across 70 province-configurations**
  at seven off-default settings (overlap 3 and 15, window 14 and 56, HIGH_PCTL 0.6,
  MIN_VISITS 60 + MIN_DRUPES 6000, MIN_BASELINE_SEASONS 2).

**Today's published output, reproduced:**

| province | rate % | n visits | groves | drupes | historical | trend |
|---|---|---|---|---|---|---|
| Arezzo | 0.1636 | 55 | 17 | 5,500 | TYPICAL (lower than 4 of 6) | UNKNOWN |
| Firenze | 0.0664 | 241 | 73 | 24,100 | BELOW_HISTORICAL (14 of 14) | STABLE_OBSERVED |
| Grosseto | 0.6575 | 320 | 157 | 34,720 | INSUFFICIENT_DATA | STABLE_OBSERVED |
| Livorno | 0.9216 | 153 | 77 | 15,300 | INSUFFICIENT_DATA | STABLE_OBSERVED |
| Lucca | 1.1509 | 53 | 14 | 5,300 | INSUFFICIENT_DATA | INCREASING_OBSERVED |
| Massa-Carrara | 0.566 | 40 | 10 | 5,300 | INSUFFICIENT_DATA | STABLE_OBSERVED |
| Pisa | 1.02 | 85 | 45 | 9,196 | INSUFFICIENT_DATA | STABLE_OBSERVED |
| Pistoia | 0.0278 | 36 | 16 | 3,600 | INSUFFICIENT_DATA | STABLE_OBSERVED |
| Prato | 0.0417 | 24 | 7 | 2,400 | INSUFFICIENT_DATA | UNKNOWN |
| Siena | 0.6909 | 186 | 61 | 18,383 | BELOW_HISTORICAL (14 of 17) | STABLE_OBSERVED |

---

## A1 — FIVE OF THE NINE DECLARED PARAMETERS CANNOT MOVE A PUBLISHED CLASS

**CLAIM.** The header says "EVERY parameter is declared here, emitted in PARAMS,
and varied by the sensitivity test. A parameter that never appears in the output
is a parameter nobody can audit." Five of the nine cannot change any published
`historical_state` at any value. Two of those five are the denominator gates
(`MIN_VISITS`, `MIN_DRUPES`) that the docstring presents as guarding the rate.

**METHOD.** `rt5_01_sweep.py`. One-at-a-time sweep of each of the nine parameters
over a wide grid; the ten province `historical_state` and `observed_trend` values
are recomputed at every value and compared with what the tool publishes today.

**REPRODUCED: YES.**

| parameter | values tried | values that move a **class** | values that move a **trend** | Firenze holds | Siena holds | Arezzo holds |
|---|---|---|---|---|---|---|
| `WINDOW_DAYS` | 16 | **13** | 15 | 16/16 | 10/16 | 7/16 |
| `MIN_VISITS` | 17 | **0** | 8 | 17/17 | 17/17 | 17/17 |
| `MIN_DRUPES` | 14 | **0** | 7 | 14/14 | 14/14 | 14/14 |
| `MIN_BASELINE_SEASONS` | 15 | **12** | 0 | 11/15 | 13/15 | 6/15 |
| `HIGH_PCTL` | 11 | **8** | 0 | 11/11 | 7/11 | 7/11 |
| `LOW_PCTL` | 11 | **0** | 0 | 11/11 | 11/11 | 11/11 |
| `TREND_MIN_WINDOWS` | 9 | **0** | 8 | 9/9 | 9/9 | 9/9 |
| `TREND_MIN_ABS_CHANGE_PCT` | 12 | **0** | 11 | 12/12 | 12/12 | 12/12 |
| `MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE` | 18 | **17** | 0 | 16/18 | 4/18 | 9/18 |

Load-bearing for the published class: exactly four — `WINDOW_DAYS`,
`MIN_BASELINE_SEASONS`, `HIGH_PCTL`, `MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE`.

Three specific mechanisms, all read off the source:

1. **`LOW_PCTL` is dead code on the published path.** It appears only at
   `di_observe.py:151`, inside the *unmatched* branch. Line 223 then does
   `ana["historical_state"] = ana["historical_state_matched"]`, and the matched
   branch (line 214-216) tests `share_lower >= HIGH_PCTL` for BELOW and
   `higher/len >= HIGH_PCTL` for ABOVE. `LOW_PCTL` never runs on the number that
   is printed. Sweeping it over 0.00–0.50 changes nothing, in any province.
2. **`MIN_VISITS` and `MIN_DRUPES` do not gate the historical claim.** The matched
   loop (lines 179-195) applies only the overlap test to `b_all`; there is no
   `n_visits >= MIN_VISITS` and no `drupes_sampled >= MIN_DRUPES`. The `enough`
   flag is computed at line 132 but only reaches `quality.publishable`. Set
   `MIN_VISITS=60, MIN_DRUPES=6000` and the engine still hands Arezzo
   `historical_state = TYPICAL` while `quality.publishable = False`
   (55 visits, 5,500 drupes). A class survives on a window the engine's own
   quality layer refuses to publish.
3. **The emitted `params` are not the params used.** Line 284 returns
   `"params": dict(PARAMS)` — the module global, not the `params=` argument. Run
   `cell(..., params={...,"WINDOW_DAYS":14})` and the cell reports
   `params.WINDOW_DAYS = 28` alongside a window of `['2026-08-24','2026-09-06']`,
   which is 14 days. Any sensitivity table built from the emitted field is
   mislabelled.

**IMPACT: MAJOR.** Not fatal to a number, fatal to the audit story. The two
declared denominator gates are advertised as protecting the comparison and do
not touch it; one parameter is inert; and the emitted parameter block can lie
about the run that produced it.

**WHAT SURVIVES.** The four load-bearing parameters are genuinely load-bearing
and the sweep is possible at all, which is more than most pipelines allow. The
`enough` flag does correctly gate `quality.publishable`.

---

## A2 — "LOWER THAN 14 OF 14" IS A SIGN TEST WITH THE WRONG NULL

**CLAIM.** "Lower than 14 of 14 matched seasons" reads like p = 2 × 0.5^14 ≈
0.0001. It is not. The 14 comparisons share one current window, so they are not
14 independent pairs. The honest null for one new observation against k old ones
is the uniform rank, which gives p ≈ 0.20 — 1,600 times weaker.

**METHOD.** `rt5_02_signtest.py`. Three nulls, plus a magnitude-aware
per-season test the counting rule discards:

* **A. Naive sign test** — binomial, the null the phrase invites.
* **B. Exchangeable-season rank** — the rule fires when at most *m* prior seasons
  read higher; under exchangeability the current season's rank among the k+1 is
  uniform, so P = (m+1)/(k+1).
* **C. Grove cluster bootstrap** — B = 5,000, resampling the shared **groves**
  with replacement (drupes within a grove are not independent), recomputing every
  matched rate and re-running the tool's own counting rule.

**REPRODUCED: YES.**

| province | k | lower | higher | A: naive sign | B: exchangeable rank | C: bootstrap verdict |
|---|---|---|---|---|---|---|
| Firenze | 14 | 14 | 0 | p = 1.22e-04 | fires if ≤2 of 14 higher → **3/15 = 0.200** | BELOW 5,000/5,000 (**100.0%**) |
| Siena | 17 | 14 | 3 | p = 1.27e-02 | fires if ≤3 of 17 higher → **4/18 = 0.222** | BELOW 1,802/5,000 (**36.0%**), TYPICAL 64.0% |
| Arezzo | 6 | 4 | 2 | p = 6.88e-01 | fires if ≤1 of 6 higher → **2/7 = 0.286** | BELOW 471/5,000 (9.4%), TYPICAL 90.6% |

Bootstrap "lower" counts: Firenze median 14, 95% interval [13, 14] of 14; Siena
median **13**, [11, 15] of 17 — the published 14 sits *above* the median of its
own resampling distribution, and 13/17 = 0.765 is below the 0.80 threshold;
Arezzo median 4, [2, 5] of 6.

The counting rule also throws away magnitude. Two of Firenze's 14 "lower"
seasons are not distinguishable from noise on their own drupe counts:

* 2012 — 1 of 3,700 vs 2 of 4,000 (two-proportion p = 0.610)
* 2022 — 12 of 13,800 vs 23 of 13,500 (p = 0.054)

while 2014 is 4 of 4,300 vs 440 of 4,000. Under the rule they count the same:
one tick each.

**IMPACT: FATAL for Siena, FATAL for Arezzo's TYPICAL as a statement about
level, MAJOR for the class as a statistic in general, NONE for Firenze.**

**WHAT SURVIVES.** Firenze. Its 14/14 is not carried by the counting rule — it is
carried by magnitude. On the matched panels Firenze reads 0.027%–0.108% now
against 0.05%–11.0% then, and 11 of the 14 per-season two-proportion tests are
below 1e-05. The cluster bootstrap returns BELOW_HISTORICAL 5,000 times out of
5,000. Firenze's verdict is right for reasons the tool does not use.

---

## A3 — SIENA'S BELOW_HISTORICAL EXISTS ONLY AT THE DECLARED OVERLAP OF 8

**CLAIM.** `MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE = 8` is not on a plateau for
Siena. It is a spike. Both neighbouring values say TYPICAL.

**METHOD.** `rt5_01_sweep.py`, `rt5_06_gates.py`.

**REPRODUCED: YES.**

| overlap | 1 | 2 | 3 | 4 | 5 | 6 | 7 | **8** | 9 | 10 | 12 | 14 | 16+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Firenze | BE | BE | BE | BE | BE | BE | BE | **BE** | BE | BE | BE | BE | BE to 25 |
| **Siena** | BE | BE | BE | TY | TY | TY | TY | **BE** | TY | TY | TY | TY | INSUF |
| Arezzo | TY | TY | TY | TY | TY | TY | TY | **TY** | TY | INSUF | INSUF | INSUF | INSUF |

Siena keeps its published class at **4 of the 18** overlap values tried, and its
two immediate neighbours (7 and 9) both say TYPICAL. Under `HIGH_PCTL` the same
knife edge: Siena is BELOW at 0.50–0.80 and TYPICAL from 0.85 up — 14/17 =
0.8235 clears the declared 0.80 by 0.0235. Under `WINDOW_DAYS`, Siena is TYPICAL
at 7, 10, 14, 17, 21, 24 and BELOW only from 28 up (10 of 16 values).

**IMPACT: FATAL for Siena.**

**WHAT SURVIVES.** Firenze is BELOW_HISTORICAL at every overlap from 1 to 25 and
at every `WINDOW_DAYS` from 7 to 91 and every `HIGH_PCTL` from 0.50 to 1.00 —
16/16, 18/18 and 11/11 respectively. It fails only when the gate is set so hard
that nothing speaks at all (overlap ≥ 30, or `MIN_BASELINE_SEASONS` ≥ 15).

---

## A4 — ONE INFESTED DRUPE FLIPS SIENA

**CLAIM.** The published class is a step function of 17 sign comparisons, one of
which is decided in the fourth decimal place. A single drupe changes the headline.

**METHOD.** `rt5_08_fragility.py`. For each speaking province: for every visit in
the current 28-day window, add or remove k infested drupes at that one visit,
re-run the whole engine path, binary-search the smallest k that changes the class
(the perturbation is monotone in k, so the search is exact).

**REPRODUCED: YES.**

| province | published | minimal single-visit change | becomes | against |
|---|---|---|---|---|
| **Siena** | BELOW_HISTORICAL | **add 1 infested drupe** (grove 1165, 2026-08-11, Montalcino, which recorded 4 of 100) | **TYPICAL** | 127 infested of 18,383 sampled |
| Firenze | BELOW_HISTORICAL | add 18 infested drupes (grove 2240, 2026-08-10, Montelupo Fiorentino, recorded 0 of 100) | TYPICAL | 16 infested of 24,100 |
| Arezzo | TYPICAL | add 74 infested drupes (grove 4018, 2026-08-12, Cortona, recorded 0 of 100) | ABOVE_HISTORICAL | 9 infested of 5,500 |

The mechanism for Siena is the 2020 comparison: now **79 of 6,633 = 1.19100%**
against then **98 of 8,200 = 1.19512%**. Margin 0.0041 percentage points;
two-proportion p = 0.982. One more infested drupe on the now side makes it
80/6,633 = 1.2061% > 1.19512%, so that season flips from "lower" to "higher",
14/17 becomes 13/17 = 0.7647 < 0.80, and the province becomes TYPICAL.

**IMPACT: FATAL for Siena. MINOR for Firenze** (18 drupes is more than the 16 the
province actually recorded, so the flip needs the observation to roughly double).
**MINOR for Arezzo** (74 drupes is eight times what the province recorded).

**WHAT SURVIVES.** Firenze and Arezzo are not one-drupe results. The published
verdict for Firenze requires the true rate to be materially different from what
was measured before it moves.

---

## A5 — POOLING IS A CHOICE OF WEIGHTS, AND SIENA DOES NOT SURVIVE IT

**CLAIM.** `sum(infested)/sum(sampled)` weights a grove by how often it was
visited. Change to any of the obvious alternatives and verdicts move.

**METHOD.** `rt5_03_pooling.py`. Four alternative point estimators recomputed
end to end — current window, every baseline season, every matched panel, and the
trend: mean of per-visit rates, median of per-visit rates, mean of per-grove
means, median of per-grove means.

**REPRODUCED: YES.**

| province | pooled | mean/visit | median/visit | mean/grove | median/grove |
|---|---|---|---|---|---|
| Firenze | **BELOW** (14/14) | BELOW (14/14) | TYPICAL (7/14) | BELOW (13/14) | TYPICAL (11/14) |
| **Siena** | **BELOW** (14/17) | **TYPICAL** (13/17) | **TYPICAL** (11/17) | **TYPICAL** (13/17) | BELOW (14/17) |
| Arezzo | TYPICAL (4/6) | TYPICAL | TYPICAL (2/6) | TYPICAL | TYPICAL |

Trend flips too: Lucca INCREASING → STABLE under both medians; Pisa STABLE →
INCREASING under both means.

Weight concentration in the published window (Kish effective groves):
Firenze 66.2 of 73, Siena 53.2 of 61, Grosseto 121.4 of 157, Massa-Carrara
6.5 of 10, Prato 6.4 of 7 (top grove carries 16.7% of the denominator, top five
carry 83.3%). Visits per grove run 1 to 4.

**Which is right.** The medians are **not** a defensible alternative on this data
and I say so against my own interest: the per-visit median is exactly **0.0 in all
ten provinces today**, because most visits find no infested drupe. An estimator
with no resolution cannot arbitrate. That leaves pooled, mean-per-visit and
mean-per-grove. Because 92.99% of all 79,074 visits with a denominator sample
exactly 100 drupes (Firenze's window: 241 of 243 visits at exactly 100), pooling
by drupes and averaging over visits are near-identical — the weighting question
here is really visits-per-grove, not drupes-per-visit. **Mean-per-grove is the
better estimator** if the grove is the sampling unit, which the matched-panel
design itself asserts. On that estimator Siena is TYPICAL.

**IMPACT: MAJOR for Siena** (fails 2 of the 3 non-degenerate estimators,
including the one its own design logic implies). **MINOR for Firenze** (survives
all 3 non-degenerate estimators). **NONE for Arezzo.**

---

## A6 — SEASONALITY: SIENA HOLDS ITS CLASS ON 13 OF 57 DAYS

**CLAIM.** The window is anchored on a calendar day. Ask on a different day and
you get a different answer.

**METHOD.** `rt5_04_seasonality.py`. `as_of` slid day by day from −28 to +28 (57
publication days), all ten provinces recomputed each time.

**REPRODUCED: YES.**

| province | keeps published class | classes seen across ±28 days |
|---|---|---|
| Firenze | **51 of 57** | BELOW (51), INSUFFICIENT (6) — never TYPICAL, never ABOVE |
| **Siena** | **13 of 57** | TYPICAL (39), BELOW (13), INSUFFICIENT (5) |
| **Arezzo** | **20 of 57** | BELOW (32), TYPICAL (20), INSUFFICIENT (5) |

Siena's class over offsets −28…+28:
`TTTTTTTTTTTTTTTBBTTTTTTTBBBBBTTTTTTBBBTTBBBTTTTTTTTT.....`
Offset 0 — the published day — is the **last day of a five-day BELOW run**.
Publishing on 2026-09-07 gives TYPICAL. Publishing on 2026-09-13 gives BELOW again.

Arezzo is worse in a different way: its **modal** verdict across the 57 days is
BELOW_HISTORICAL (32 days), not the published TYPICAL (20 days).

**IMPACT: FATAL for Siena and Arezzo.** A class that holds on 13 of 57 adjacent
publication days is a description of the calendar, not of the groves.

**WHAT SURVIVES.** Firenze never once reads TYPICAL or ABOVE in the whole ±28-day
band. Its six non-BELOW days are INSUFFICIENT_DATA at the far right edge, where
the window runs past the end of the archive.

---

## A7 — RIGHT-EDGE TRUNCATION: I PREDICTED A BIAS AND IT IS NOT THERE

**CLAIM (mine).** The archive stops on 2026-09-04 but the window runs to
2026-09-06, so the current side is short 3–4 days while every matched baseline
window is complete. On a rising curve that should bias the current side downward
and manufacture BELOW_HISTORICAL.

**METHOD.** `rt5_04_seasonality.py` part (b). For each matched season, truncate
the **baseline** window to the same elapsed-days coverage the current season
actually has, then re-run the counting rule.

**REPRODUCED: NO.**

| province | last observation | dead days | days covered | published | baseline cut to match |
|---|---|---|---|---|---|
| Firenze | 2026-09-02 | 4 | 24 of 28 | BELOW, 14 of 14 | BELOW, **14 of 14** |
| Siena | 2026-09-03 | 3 | 25 of 28 | BELOW, 14 of 17 | BELOW, **14 of 17** |
| Arezzo | 2026-09-02 | 4 | 24 of 28 | TYPICAL, 4 of 6 | TYPICAL, **4 of 6** |

Not one comparison moves. The reason is in part (c): at this point in the
season the curve is not steep. Median week-on-week change over 20 prior seasons
is −0.056 pp (Firenze), +0.036 pp (Siena), +0.120 pp (Arezzo), +0.029 pp
(Grosseto), +0.347 pp (Livorno), −0.035 pp (Pisa). Early September is near the
flat part, not on a cliff.

**IMPACT: NONE.**

**WHAT SURVIVES.** The whole accusation. The 28-day window anchored here is not
distorted by the ragged right edge, and the engine's `as_of` discipline (nothing
after `as_of`, ever) does what it claims.

---

## A8 — `TREND_MIN_ABS_CHANGE_PCT = 1.0` IS NOT CALIBRATED TO THIS QUANTITY

**CLAIM.** A fixed threshold in percentage points, on a quantity whose scale
moves by a factor of ~30 between seasons, is not a rule — it is a different rule
every year. Today it is nearly mute; in 2007 it was nearly always on.

**METHOD.** `rt5_05_trend.py`. Every province and every window-end date in the
archive (7-day step, 2006–2026), the tool's own gates applied, the end-to-end
change over three consecutive 28-day windows recorded; 2,437 province-windows
for ACTIVE, 2,437 for DAMAGING, 2,435 for TOTAL.

**REPRODUCED: YES.**

Archive-wide the threshold is not strict at all: `|change| ≥ 1.0 pp` in
**1,702 of 2,437** ACTIVE province-windows (69.84%), and a direction is named
(monotone AND ≥1.0 pp) in **872 of 2,437** (35.78%). Median |change| is 2.05 pp,
p90 is 7.50 pp, max is 33.86 pp. A threshold of 6.41 pp would be needed to name
a direction in only the top fifth of monotone cases.

But the SAME 1.0 pp threshold, season by season, share of province-windows that
name a direction:

| metric | 2006 | 2007 | 2012 | 2016 | 2019 | 2022 | 2024 | 2025 | **2026** |
|---|---|---|---|---|---|---|---|---|---|
| ACTIVE | 60% | 38% | 12% | 35% | 63% | 60% | 26% | 36% | **8%** |
| DAMAGING | 90% | 95% | 28% | 79% | 82% | 54% | 36% | 65% | **0%** |
| TOTAL | 92% | 54% | 50% | 60% | 85% | 84% | 41% | 62% | 77% |

The rule's selectivity swings from 0% to 95% with nothing changing but the
season's scale. That is the signature of an absolute threshold on a
multiplicative quantity.

The consequences today are visible without any statistics:

* **Pisa**: 0.04 → 0.5022 → 1.02, monotone, a **25.5-fold** rise. Change 0.98 pp.
  Misses the threshold by **0.02 pp**. Published **STABLE_OBSERVED**.
* **Siena**: 0.0 → 0.2718 → 0.6909, monotone increasing. Published **STABLE_OBSERVED**.
* **Massa-Carrara**: 0.0 → 0.7838 → 0.566. Published STABLE_OBSERVED.
* **Lucca**: 0.0769 → 0.4464 → 1.1509, change 1.074 pp. Published
  **INCREASING_OBSERVED** — it clears the bar by 0.074 pp. Lucca and Pisa are
  0.09 pp apart in end-to-end change and get opposite labels.

`TREND_MIN_WINDOWS` is separately fragile: at 3 it names a direction for Lucca;
at 4 or more, **8 of the 10 provinces change label** (the loop asks for
`TREND_MIN_WINDOWS + 1` windows and requires `TREND_MIN_WINDOWS` to pass the
gates, so raising it starves the sequence).

**IMPACT: MAJOR.** Not fatal — the word chosen is `STABLE_OBSERVED`, not
"stable", and the reason string prints the actual sequence, so the reader can
see 0.04 → 0.5022 → 1.02 for themselves. But the label contradicts the numbers
printed beside it, and a reader who skims labels will be misled.

**WHAT SURVIVES.** The trend layer never says "will". The reason string carries
the whole sequence and the delta, so the label is falsifiable on sight. And the
monotonicity requirement is real: only 42.22% of ACTIVE province-windows are
monotone, so the direction test is not vacuous.

---

## A9 — THE TWO SILENCING GATES, AND WHAT THEY ARE ACTUALLY SELECTING

**CLAIM.** `MIN_PANEL_OVERLAP = 8` and `MIN_BASELINE_SEASONS = 5` silence 7 of
10 provinces. Worse, the overlap gate is not selecting "comparable seasons" — it
is selecting **recent** seasons, because the monitored network grows.

**METHOD.** `rt5_06_gates.py` (full 2-D surface), `rt5_10_panel_recency.py`
(Spearman of season year against shared-grove count, and matched vs unmatched).

**REPRODUCED: YES.**

Trade-off surface, provinces speaking of 10 / of those how many BELOW, with
`MIN_BASELINE_SEASONS = 5`:

| overlap | 1 | 2 | 3 | 4 | 5 | 6 | 7 | **8** | 9 | 10 | 12 | 15 | 20 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| speaking | 8 | 7 | 7 | 5 | 5 | 5 | 4 | **3** | 3 | 2 | 2 | 2 | 1 | 1 |
| of which BELOW | 5 | 4 | 4 | 2 | 2 | 2 | 1 | **2** | 1 | 1 | 1 | 2 | 1 | 1 |

At overlap 1 the eight speakers are Firenze BE (20/20), Grosseto BE (19/20),
Livorno BE (4/5), Massa-Carrara BE (5/5), Siena BE (16/20), Arezzo TY (7/12),
Lucca TY (15/20), Pisa TY (7/11). Loosening the gate produces **more**
BELOW verdicts, not fewer.

**The gate is a recency filter.** Spearman correlation between season year and
number of groves shared with the current window:

| province | Spearman | seasons admitted | earliest admitted |
|---|---|---|---|
| Firenze | 0.989 | 14 of 20 | 2012 |
| Lucca | 0.949 | 3 of 20 | 2023 |
| Arezzo | 0.946 | **6 of 20** | **2020** |
| Pisa | 0.944 | 1 of 20 | 2025 |
| Grosseto | 0.938 | 2 of 20 | 2024 |
| Siena | 0.884 | 17 of 20 | 2009 |
| Livorno | 0.756 | 1 of 20 | 2025 |
| Massa-Carrara | 0.667 | 1 of 14 | 2025 |
| Pistoia / Prato | 0.378 | 0 of 20 | — |

Arezzo's shared-grove counts run 0,0,0,0,0,1,0,0,0,2,2,3,7,7,9,9,10,13,14,15 for
2006…2025. The gate admits exactly 2020–2025 — a six-year tail. The label says
"its own history"; the arithmetic uses the last six years.

**IMPACT: MAJOR.** The silence is not neutral. Seven provinces are silenced by a
criterion that correlates with when the network was built, not with how
comparable the seasons are.

**WHAT SURVIVES.** The gate exists for a real reason and the code says so plainly
(lines 158-167): in some provinces this season shares a median of zero groves
with a typical prior season, and comparing different groves and calling the
difference a change in pressure would be worse. Refusing to speak is the right
instinct; the threshold is what I am attacking, not the instinct.

---

## A10 — THE ENGINE'S OWN ALTERNATIVE COMPARISON CONTRADICTS TWO OF THE THREE PUBLISHED CLASSES

**CLAIM.** `di_observe.cell()` computes a second historical comparison —
`historical_state_unmatched`, the same calendar window against the full network,
all prior seasons — and then overwrites it. For two of the three provinces that
speak today, that discarded comparison says the **opposite** of what is published.

**METHOD.** `rt5_10_panel_recency.py`.

**REPRODUCED: YES.**

| province | PUBLISHED (matched) | k | DISCARDED (full network) | k | 2026 rate | prior median | lower than |
|---|---|---|---|---|---|---|---|
| **Arezzo** | **TYPICAL** | 6 | **BELOW_HISTORICAL** | 20 | 0.1636% | 0.6418% | **19 of 20** |
| Firenze | BELOW_HISTORICAL | 14 | BELOW_HISTORICAL | 20 | 0.0664% | 1.4073% | 20 of 20 |
| **Siena** | **BELOW_HISTORICAL** | 17 | **TYPICAL** | 20 | 0.6909% | 1.2975% | **15 of 20** |
| Grosseto | INSUFFICIENT_DATA | — | BELOW_HISTORICAL | 20 | 0.6575% | 2.5627% | 18 of 20 |
| Livorno | INSUFFICIENT_DATA | — | BELOW_HISTORICAL | 20 | 0.9216% | 4.1552% | 20 of 20 |
| Lucca | INSUFFICIENT_DATA | — | BELOW_HISTORICAL | 20 | 1.1509% | 3.5238% | 17 of 20 |
| Massa-Carrara | INSUFFICIENT_DATA | — | TYPICAL | 14 | 0.566% | 2.4008% | 10 of 14 |
| Pisa | INSUFFICIENT_DATA | — | BELOW_HISTORICAL | 20 | 1.02% | 2.8663% | 16 of 20 |
| Pistoia | INSUFFICIENT_DATA | — | BELOW_HISTORICAL | 20 | 0.0278% | 1.3308% | 20 of 20 |
| Prato | INSUFFICIENT_DATA | — | BELOW_HISTORICAL | 20 | 0.0417% | 0.6368% | 19 of 20 |

Arezzo is at the **2nd lowest of its 21 seasons** in this calendar window (only
2012's 0.0923% is lower) and the tool calls it TYPICAL, because the six recent
seasons that clear the overlap gate happen to include four low ones (2020 0.667%,
2021 0.4375%, 2022 0.1667%, 2024 0.25%) and exclude 2016 (5.42%) and 2007 (3.91%).

**IMPACT: FATAL for the per-province class as published.** Two of the three
speaking provinces carry a class that the engine's own second method reverses.
The engine picks one and does not print the disagreement in the headline. Both
methods are defensible; publishing one without the other is not.

**WHAT SURVIVES.** Firenze agrees both ways, on 14 matched seasons and on 20
unmatched, at 0.0664% against a prior median of 1.4073% and a prior minimum of
0.1286%. And the engine does store `historical_state_unmatched` in the JSON —
the disagreement is discoverable, just not surfaced.

---

## A11 — MULTIPLICITY: THE DIRECTIONAL CALL FIRES AT ALMOST EXACTLY THE CHANCE RATE

**CLAIM.** The tool is a walk-forward screen: 10 provinces × 3 metrics × every
date it is asked, with no correction. Across the whole archive it emits
ABOVE/BELOW at 0.97 times the rate a null of exchangeable seasons would.

**METHOD.** `rt5_07_multiplicity.py`. The complete screen re-run over the
archive: 2010-04-01 to 2026-09-06, every 7 days, all 10 provinces, all 3 metrics.
Expected count computed per cell as (m+1)/(k+1) per tail, where k is that cell's
own matched-season count and m the largest number of contrary seasons the rule
still tolerates.

**REPRODUCED: YES.**

* publication dates: **858**
* cells run: **25,740**
* INSUFFICIENT_DATA: **22,934 of 25,740 (89.1%)** — the tool is silent nine times
  in ten
* cells with a class: **2,806**; TYPICAL 1,370 (48.8%), BELOW 506 (18.0%),
  ABOVE 930 (33.1%)
* **directional calls observed: 1,436 of 2,806 speaking cells (51.2%)**
* **expected under exchangeability: 1,482 (52.8%), split 741 BELOW + 741 ABOVE**
* **observed / expected = 0.97**
* dates on which at least one province+metric fires: **229 of 858 (26.7%)**
* observed BELOW:ABOVE = **506:930 = 0.54:1**; the null is 1:1

Class churn between consecutive weekly publications, ACTIVE metric only:
Pisa 22 of 96 (22.9%), Pistoia 11 of 47 (23.4%), Grosseto 36 of 189 (19.0%),
Livorno 4 of 22 (18.2%), Arezzo 8 of 49 (16.3%), Siena 32 of 212 (15.1%),
Lucca 4 of 28 (14.3%), Firenze 29 of 221 (13.1%). Roughly one publication in six
changes a province's historical class from the week before.

**Today's family-wise null** (`rt5_09_today_null.py`), ACTIVE metric, the three
speaking provinces (P(BELOW) = 0.200, 0.222, 0.286):

* expected BELOW headlines on a nothing-happening day: **0.708**
* P(0) = 0.4445, P(1) = 0.4159, P(2) = 0.1270, P(3) = 0.0127
* observed 2, so **P(≥2) = 0.140**
* **P(at least one BELOW headline on a nothing-happening day) = 0.556**

Across all three metrics: 7 BELOW observed of 9 speaking cells against 2.124
expected, nominal P(≥7) = 0.0009 — **but I do not claim that p-value**. The three
metrics are three measurements of the same infestation on the same visits and are
strongly dependent; the independence the calculation assumes is false. The honest
statement is that the direction agrees across metrics, not that it does so at
p = 0.0009.

**IMPACT: FATAL for the directional class as evidence.** A screen whose
positive rate matches its own null rate to within 3% is not detecting anything by
firing. The 0.80 threshold, at the typical k of 6–17, permits 2 to 4 contrary
seasons, which under exchangeability is a 20–29% per-tail event — so the call is
the default state, not the exception.

**WHAT SURVIVES.** The BELOW:ABOVE asymmetry (0.54:1) is not chance and is not
explained by the null; it reflects a real upward drift across the archive that
the walk-forward baseline sees. And the 89.1% silence rate means the tool is
conservative about speaking at all — the multiplicity problem is bounded by that.

---

## A12 — VERDICTS I FLIPPED BY A DEFENSIBLE CHANGE OF METHOD

Collected, with the change that does it. Every one of these is a change I would
defend in front of a statistician, not a knob turned to get an answer.

| verdict | flipped to | by what |
|---|---|---|
| **Siena BELOW_HISTORICAL** | TYPICAL | grove cluster bootstrap (64.0% of 5,000 draws) |
| **Siena BELOW_HISTORICAL** | TYPICAL | mean of per-grove means, the estimator its own matched design implies |
| **Siena BELOW_HISTORICAL** | TYPICAL | mean of per-visit rates |
| **Siena BELOW_HISTORICAL** | TYPICAL | overlap 7 or 9 instead of 8 |
| **Siena BELOW_HISTORICAL** | TYPICAL | `HIGH_PCTL` 0.85 instead of 0.80 |
| **Siena BELOW_HISTORICAL** | TYPICAL | publishing on 2026-09-07, or on 39 of 57 nearby days |
| **Siena BELOW_HISTORICAL** | TYPICAL | one extra infested drupe at one visit |
| **Siena BELOW_HISTORICAL** | TYPICAL | the engine's own full-network comparison (15 of 20, 0.75 < 0.80) |
| **Arezzo TYPICAL** | BELOW_HISTORICAL | the engine's own full-network comparison (19 of 20) |
| **Arezzo TYPICAL** | BELOW_HISTORICAL | `WINDOW_DAYS` 42 or more |
| **Arezzo TYPICAL** | BELOW_HISTORICAL | `HIGH_PCTL` 0.65 or less |
| **Arezzo TYPICAL** | BELOW_HISTORICAL | publishing on 32 of the 57 nearby days |
| Firenze STABLE_OBSERVED | — | not flipped by any estimator or threshold tried |
| Lucca INCREASING_OBSERVED | STABLE_OBSERVED | either median estimator, or threshold ≥ 1.1 pp |
| Pisa STABLE_OBSERVED | INCREASING_OBSERVED | either mean estimator, or threshold ≤ 0.98 pp |
| 7 × INSUFFICIENT_DATA | 5 speak, of which 3 BELOW | overlap 1–3 instead of 8 |

**Siena's BELOW_HISTORICAL falls to eight independent, defensible changes of
method. I could not flip Firenze's with any of them.**

---

## WHAT I COULD NOT BREAK

Stated plainly, because it is the more important half.

**1. The 2026 season really is the lowest in the archive, and it is not close.**
Toscana pooled over all provinces, same 10 Aug – 6 Sep window
(`rt5_09_today_null.py`):

| season | rate | infested / sampled | groves |
|---|---|---|---|
| 2007 | 8.1968% | 6,664 / 81,300 | 289 |
| 2014 | 9.1178% | 5,271 / 57,810 | 199 |
| 2016 | 6.8077% | 6,789 / 99,726 | 343 |
| 2025 | 5.5356% | 5,940 / 107,305 | 382 |
| 2024 | 0.6334% | 736 / 116,196 | 338 |
| 2012 | 0.5851% | 395 / 67,510 | 201 |
| **2026** | **0.5711%** | **707 / 123,799** | **477** |

**2026 is lower than 20 of 20 prior seasons region-wide**, and it is measured on
the **largest network in the archive** (477 groves, 123,799 drupes — more than
any prior season except 2018's 160,414). This is not a thin-sample artefact and
it is not a panel artefact: it holds on the full network, on every province, and
on every estimator.

**2. Every one of the ten provinces is below its own prior median** on the
full-network comparison, including the seven the tool silences: Firenze lower
than 20 of 20, Livorno 20 of 20, Pistoia 20 of 20, Arezzo 19 of 20, Prato 19 of 20,
Grosseto 18 of 20, Lucca 17 of 20, Pisa 16 of 20, Siena 15 of 20,
Massa-Carrara 10 of 14. Relaxing the gates makes the picture *more* uniformly
low, not less.

**3. Firenze's BELOW_HISTORICAL survives everything I have.**
Rate 0.0664% (16 infested of 24,100 drupes, 241 visits, 73 groves) — the lowest
of its 21 seasons, against a prior median of 1.4073% and a prior minimum of
0.1286%. It holds at every overlap 1–25 (18/18), every `WINDOW_DAYS` 7–91
(16/16), every `HIGH_PCTL` 0.50–1.00 (11/11), on 51 of 57 adjacent publication
days, on 3 of 3 non-degenerate estimators, on 5,000 of 5,000 cluster-bootstrap
draws, on both the matched and the unmatched comparison, on all three metrics,
and it needs 18 extra infested drupes — more than the 16 the province actually
recorded — to move.

**4. The right-edge truncation bias I went looking for does not exist.** Cutting
every baseline season to the current season's actual coverage changes not one of
the 37 matched comparisons across the three speaking provinces.

**5. `as_of` discipline holds.** Nothing dated after `as_of` enters any
computation; the loader counts what it drops; the trend windows are all in the
past and the word "will" appears nowhere in the output.

**6. The engine is honest about the panel problem.** Lines 158-167 name the
rotating network as a real threat and refuse to compare different groves. The
threshold chosen is wrong for Siena and wrong for Arezzo, but the instinct is
right and the refusal is explicit rather than silent.

**7. The observation layer is sound.** A rate with a real denominator, per
visit, with the exclusions counted and named, is a genuine improvement over
"share of sites above zero". The unit `percent of sampled drupes` is carried
everywhere and the source's own band is applied to a percentage, never a count.

**8. The whole thing is reproducible.** I rebuilt `cell()` from scratch and it
agreed with the engine on 10 of 10 provinces at the declared configuration and on
70 of 70 province-configurations away from it. Nothing in the engine is hidden,
random, or clock-dependent. Every accusation above was possible only because the
code let me make it.

---

## THE ONE-LINE VERDICT

**The season is real. The province classes are not.**
Toscana's 2026 olive-fly pressure is the lowest of 21 seasons on the largest
network ever sampled, and that survives every attack in this document. Of the
three classes published today, **one (Firenze) is robust, one (Siena) falls to a
single drupe and to eight other defensible changes of method, and one (Arezzo)
is contradicted by the engine's own second comparison and is not even the modal
answer across nearby publication days.** The directional class as a mechanism
fires at 0.97 times its own chance rate across 2,806 archive cells, so it should
not be read as evidence on its own. What should be published is the number with
its denominator, the full-history rank, and the disagreement between the two
comparisons — not a single word per province.

---

## FILES

| file | what it does |
|---|---|
| `rt5_lib.py` | indexed re-implementation of `di_observe.cell()`, alternative estimators, engine pin note |
| `rt5_00_verify.py` / `.json` | proves the harness reproduces the engine at the declared configuration; records engine sha256 |
| `rt5_00b_verify_offdefault.py` / `.json` | proves it at 7 off-default configurations; documents the `publishable=False` + class quirk and the emitted-params bug |
| `rt5_01_sweep.py` / `.json` / `rt5_01_out.txt` | A1, A3 — nine-parameter one-at-a-time sweep |
| `rt5_02_signtest.py` / `.json` / `rt5_02_out.txt` | A2 — three nulls plus per-season two-proportion tests |
| `rt5_03_pooling.py` / `.json` / `rt5_03_out.txt` | A5 — five estimators end to end, weight concentration |
| `rt5_04_seasonality.py` / `.json` / `rt5_04_out.txt` | A6, A7 — `as_of` slide, truncation, curve steepness |
| `rt5_05_trend.py` / `.json` / `rt5_05_out.txt` | A8 — trend threshold calibration over the whole archive |
| `rt5_06_gates.py` / `.json` / `rt5_06_out.txt` | A9 — 2-D gate trade-off surface, raw overlap counts |
| `rt5_07_multiplicity.py` / `.json` / `rt5_07_out.txt` | A11 — 25,740-cell walk-forward screen, observed vs expected |
| `rt5_08_fragility.py` / `.json` / `rt5_08_out.txt` | A4 — minimal single-visit perturbation, narrowest margins |
| `rt5_09_today_null.py` / `.json` / `rt5_09_out.txt` | A11, and the season table that survives everything |
| `rt5_10_panel_recency.py` / `.json` / `rt5_10_out.txt` | A9, A10 — recency filter, matched vs unmatched |
| `_cache_visits.pkl` | loader cache; rebuilt by `rt5_00_verify.py` (never sweep against a stale one) |

Reproduce in order: `py rt5_00_verify.py`, `py rt5_00b_verify_offdefault.py`,
then any of `rt5_01` … `rt5_10`. Python 3.12, no third-party packages.

## NOT KNOWN

* Whether the low 2026 reading reflects weather, control practice, a change in
  scouting behaviour, or a change in how the source records a zero. This lens
  reads numbers; it cannot separate those.
* Whether the network's growth to 477 groves in 2026 changed *which kinds* of
  grove are sampled (e.g. better-managed ones). The archive as read here carries
  no grove attributes that would let me test it.
* Whether the true grove-level infestation distribution is over-dispersed enough
  to widen the cluster bootstrap intervals further. I resampled groves, which
  handles clustering, but not repeated visits within a grove across the window.
* The correct multiple-comparison correction for a walk-forward screen with
  overlapping 28-day windows and three dependent metrics. I reported the raw
  observed-versus-expected ratio instead of inventing one.
