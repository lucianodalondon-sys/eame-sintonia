# RT2 — RED TEAM, LENS: TIME

Independent adversarial audit of the DISEASE-INTELLIGENCE-OBSERVATIONAL engine. I wrote none
of this code. Goal: get a future observation, a wrong date, a stale reading or a fake clock
into a published number.

Every accusation below carries a runnable script in this folder and the JSON it produced.
Nothing under `CASES/`, `engine/` or `italia-portale/` was modified; the last section proves
it with a byte fingerprint.

---

## 0. THE TARGET MOVED THREE TIMES DURING THIS AUDIT — READ THIS FIRST

`engine/di_core.py` and `engine/di_observe.py` were edited **while I was attacking them**.
Three distinct versions ran during this session. Every finding below is pinned to the sha256
of the bytes it was measured against.

| when (local) | di_core.py | di_observe.py | di_refresh.py | what changed |
|---|---|---|---|---|
| V1 20:24–20:51 | `e56dc697a3d5…` | `8fb727f137b6…` | `81f8240a01c4…` | as first read |
| V2 20:51–~21:2x | `2e1acc17e261…` | `093d95c9684f…` | `81f8240a01c4…` | per-measurement usability; **trend rule replaced: the 1.0 pp threshold became non-overlapping Wilson 95% intervals** |
| V3 current | `2ba3abc24895ee86f176f0e0182ebc4a29b81cc39e47c46e6bb486294d05f7c4` | `093d95c9684fbea3ee08a13a929fc979d3b6cb126f6d45638f7d9a9dc27977f7` | `81f8240a01c428fae98c71e28c995815c8cf4cd28ccdbc96e937e773fd769258` | province name validated against a canonical list |

`di_refresh.py` did **not** change at any point. Every refresh finding (T-11 … T-17) is against
`81f8240a01c4…`, which is the shipped file right now.

**This is itself a time finding.** An audit that cannot name the bytes it audited proves
nothing. Two of my accusations (T-8, T-9) exist only because I can point at V1 and at V3 and
say which numbers each produced.

---

## T-1 · THE WALL CLOCK ON THE PATH TO A PUBLISHED NUMBER

**CLAIM.** Something in the analysis path reads `date.today()` / `datetime.now()` /
`time.time()`, so the answer depends on when you run it, not on `as_of`.

**METHOD.** `rt2_clock.py`. I replace the `datetime` and `time` modules in `sys.modules`
with shims whose *now* entry points (`date.today`, `datetime.now`, `datetime.utcnow`,
`datetime.today`, `datetime.fromtimestamp`, `time.time`, `time.time_ns`, `time.localtime`,
`time.gmtime`) raise `ClockArmed`, while `date.fromisoformat`, `date()`, `timedelta` and the
rest of the arithmetic keep working. Then I run the whole pipeline: `load_sheet` →
`load_visits` → `cell` for all 10 provinces → `render_region` + `render_province`. Arming is
self-tested first (`dt.date.today()` must raise before the run counts). I also re-ran the
report twice, 2 seconds apart, and compared the output bytes.

**REPRODUCED: NO.**

**NUMBERS.**
- Arming verified: `ARMING_WORKS: true`.
- Pipeline with the clock armed to raise: **COMPLETED**. 79,251 visits loaded, 10 of 10
  provinces produced a cell, 21,743 characters of human reading rendered, and every published
  percentage came out (Arezzo 0.1636, Firenze 0.0664, Grosseto 0.6575, Livorno 0.9216,
  Lucca 1.1509, Massa-Carrara 0.566, Pisa 1.02, Pistoia 0.0278, Prato 0.0417, Siena 0.6909).
- `di_report.py 2026-09-06 ACTIVE_INFESTATION_COUNT` run twice, 2 s apart:
  both outputs sha256 `6c25f8ee7ddf68a8294f8a3eb5cbbd930b6231e0208dc331dd4e70fdd3c2153c`.
  Byte-identical. No timestamp is written into the published artifact.
- The only clock in the whole tree is in `di_refresh.py` (`time.time()` for a duration,
  `datetime.now(timezone.utc)` for the collection stamp). With the clock armed, the refresh
  path **DIED** as designed — which is the proof that the arming was live during the
  analysis run that survived it.
- `di_report.py` and `di_core.py` default `as_of` to a **hardcoded** `dt.date(2026, 9, 6)`,
  not to today.

**IMPACT: NONE.**

**WHAT SURVIVES.** `as_of is an argument, never a clock` is true for every number a reader
sees. This one I could not break, and I tried the strongest version of the test — not a grep,
an execution with the clock booby-trapped.

---

## T-2 · THE 28-DAY WINDOW ACROSS 31 DECEMBER

**CLAIM.** `_win()` builds the current window with `timedelta` (correct across new year), then
`_shift(lo, y)` and `_shift(hi, y)` move the two endpoints into a prior season **independently**
by replacing the year on each. When `lo` and `hi` sit in different calendar years, both land in
the same year and the shifted window has `lo > hi`. The previous engine had a -337-day baseline
window here.

**METHOD.** `rt2_yearcross.py`. Three parts. (1) The arithmetic, enumerated for 39 consecutive
`as_of` days around 1 January. (2) The real archive, at four January `as_of` dates. (3) A
**synthetic case built to make the baseline rich**: 9 seasons, the same 20 groves, visited
every single day from 1 December to 31 January, 100 drupes each, 5 infested — a constant 5.0%,
identical in every season — run through the real `di_core.load_visits` and `di_observe.cell`.
If the baseline machinery worked, every January `as_of` would find 8 prior seasons.

**REPRODUCED: YES.**

**NUMBERS.**
- 27 of the 39 `as_of` days tested have a window crossing 31 December. For **27 of 27** of
  them the shifted baseline window is impossible. Worst case: `as_of` 2026-01-01, current
  window 2025-12-05 → 2026-01-01 (28 days), baseline window for season 2020
  **2020-12-05 → 2020-01-01 = -338 days**.
- Over a full year this is **27 of 365 possible `as_of` dates = 7.4%**.
- Synthetic case, identical data on both sides:

  | as_of | window | crosses? | observation | baseline seasons found | matched | historical |
  |---|---|---|---|---|---|---|
  | 2026-01-15 | 2025-12-19 → 2026-01-15 | **yes** | 5.0% on 560 visits | **0 of 8** | 0 | INSUFFICIENT_DATA |
  | 2026-01-28 | 2026-01-01 → 2026-01-28 | no | 5.0% on 560 visits | **8 of 8** | 8 | TYPICAL |

  Same groves, same rate, same everything. Thirteen days of `as_of` apart, and the whole
  historical layer disappears.
- **The published reason is wrong about why.** At `as_of` 2026-01-15 the tool prints:
  *"0 prior seasons share at least 8 groves with this window, below the declared minimum of 5.
  A comparison against a different set of groves is not a comparison, so none is published."*
  The groves are literally identical. The cause is that the window is -338 days long.
- This does **not** produce a wrong number: `lo > hi` matches no row, so `pooled()` returns
  `None` and the season is skipped. It fails **closed** on the number and fails **loud and
  wrong** on the explanation. That is a different bug from the previous engine's.
- Reachability on THIS case: in the ACTIVE variable, of 79,251 rows, December carries **0**
  and January carries **7**. **7 of 79,251 = 0.009%**. The crossing window contains almost no
  observation, so on the olive archive the defect is unreachable in practice.

**IMPACT: MAJOR as code, NONE on this case.** MAJOR because the same engine is meant to take
other crops and other regions: any pest whose scouting season crosses new year (citrus, olive
in the southern hemisphere, protected crops, anything monitored year-round) loses its entire
historical layer for 27 days a year and is told the groves rotated.

**WHAT SURVIVES.** The current window itself is correct across the boundary (`_win` uses
`timedelta`). The trend windows are correct across the boundary (they use `timedelta` too —
confirmed: at `as_of` 2026-01-15 the trend points are 2025-12-18 and 2026-01-15, correctly
spanning the year). Only `_shift`, used by the baseline and the matched panel, is affected.

**FIX, one line:** shift by the same number of years on both endpoints and preserve the span —
e.g. `slo = _shift(lo, y); shi = slo + (hi - lo)`.

---

## T-3 · 29 FEBRUARY

**CLAIM.** `_shift()`'s `except ValueError: return d.replace(year=y, day=28)` is a
day-of-month rewrite, not a date fix. Leap years corrupt the baseline.

**METHOD.** `rt2_leap_and_stale.py`, parts L1/L2/L2b/L2c. (1) Enumerate every date in
2020-01-01 … 2028-12-31 (3,288 days) on which `replace(year=2026)` raises. (2) Enumerate the
current and baseline window LENGTHS for four leap-sensitive `as_of` values. (3) A synthetic
case with a constant 5.0% and 20 groves visited every day of every year 2020–2028, to isolate
what the missing day costs. (4) Measure how many real baseline season-cells sit close enough
to the gate that losing one day would drop them.

**REPRODUCED: PARTIALLY — the fallback is correct, the window-length asymmetry is real.**

**NUMBERS.**
- The fallback fires on exactly **3 of 3,288** dates scanned: 2020-02-29, 2024-02-29,
  2028-02-29. All are 29 February, so `day=28` is right for **3 of 3**. The construct is
  fragile (it rewrites the day, not "the last day of that month") but currently unreachable
  for any other date.
- Window length asymmetry: of **16** baseline windows examined, **7** differ in length from
  the current window. Worst difference: **1 of 28 days = 3.6%**. Example: `as_of` 2028-03-10,
  current window 2028-02-12 → 2028-03-10 = 28 days; baseline windows for 2025, 2026, 2027 are
  27 days each.
- Synthetic constant-5.0% case, `as_of` 2028-03-10: every baseline season reports exactly
  5.0% (the rate is unaffected), but the denominators split
  **56,000 drupes (2020, 2024 — leap) vs 54,000 (2021, 2022, 2023, 2025, 2026, 2027)** —
  exactly one visit-day of 20 groves × 100 drupes.
- Real archive: of **194** baseline season-cells across the 10 provinces, **1** sits close
  enough to the gate that a 27-day window would drop it — Prato 2025, at exactly
  **8 visits (MIN_VISITS = 8)** and 800 drupes.

**IMPACT: MINOR.** The rate is a ratio, so a missing day changes the denominator, not the
number. It only bites where a season sits exactly on a gate: 1 of 194 today.

**WHAT SURVIVES.** 29 February is genuinely handled, and it is declared in a comment rather
than silent. The engine does not crash, does not skip the season, and does not produce a
negative window on any leap date.

---

## T-4 · A FUTURE-DATED OBSERVATION IN A PUBLISHED NUMBER

**CLAIM.** Gate G4 says this is impossible. G4 injects the future row into `loaded["visits"]`
— i.e. **after** `di_core` has already filtered — and then checks only
`observation.value_pct` and `observation.n_visits` for one province. It never tests the raw
bytes, the baseline windows, the matched panel, the trend, or the other 9 provinces.

**METHOD.** `rt2_future.py`. I put the poison in the **raw JSON files** so it must pass
`di_core`'s own filter. Five rows appended to `c2_s1_v{1,-1001,-1002,-1003}_2026.json` in a
full copy of the real archive, all in Firenze, all reading **100,000 infested of 100,000
sampled = 100%**, dated 2026-09-07 (1 day out), 2026-09-20 (G4's own date), 2026-12-31,
2027-08-20 and 2099-08-20. Then I compare **17 published fields** (value, visits, sites,
drupes, infested, last_observation, per-visit max, source band, baseline_n, baseline median,
matched panel seasons, historical state, trend, every trend point, panel overlap) for **10
provinces × 2 metrics = 20 cells**. I also probe what `date.fromisoformat` accepts, and count
how many real rows deviate from bare `YYYY-MM-DD`.

**REPRODUCED: NO.**

**NUMBERS.**
- **5 of 5** poison rows dropped, counted in
  `n_rows_dropped_because_dated_after_as_of = 5` (clean run: 0).
- **0 of 17** fields moved on Firenze. `FIELDS_THAT_MOVED: []`, `IDENTICAL: true`.
- **0 of 20** cells moved across all provinces and both metrics.
- Date parser (Python 3.12.10): accepts `2026-09-07`, `20260907`, `2026-W38-1`,
  `0001-01-01`, `9999-12-31`; rejects `2026-09-07T23:59:59`, `2026-09-07T00:00:00+14:00`,
  `2026-250`, `2026-09`, `2026-9-7`, leading/trailing space, `2026-02-30`. **0** accepted
  strings map a future date onto a past one.
- No timezone surface: `di_core` never constructs a `datetime`, and **0 of 317,004** rows in
  the real archive carry a date that is not a bare `YYYY-MM-DD`.

**IMPACT: NONE.**

**WHAT SURVIVES.** `NOTHING AFTER AS_OF` holds in the place G4 does not look. This is the
strongest thing in the engine. I attacked it at the bytes, not at the seam G4 tests, and it
did not move.

**One honest caveat, not a defect.** The filter is relative to `as_of`. A row that was future
when it was written stops being future once `as_of` passes it, and the archive is never
re-audited. Measured at `as_of` 2028-08-20 with the 2027-08-20 poison row present: baseline
seasons 21 clean / 21 poisoned, baseline max 11.9787% clean / 11.9787% poisoned — the row
happened to fall outside that window. **NOT KNOWN** whether a poison row aimed exactly at a
future baseline window would move a number then; what would settle it is a run at an `as_of`
chosen so the poisoned date lands inside `_shift(lo,y)…_shift(hi,y)`, plus a decision about
whether "was future when collected" should be recorded at all. It is not recorded today.

---

## T-5 · THE FUTURE DOES REACH ONE PUBLISHED CLOCK

**CLAIM.** `di_refresh.validate()` computes `latest_observation = max(r["date"] for r in
dated)` with **no `as_of` bound and no date parsing**. `refresh_one` writes it into the
record as `LAST_GOOD_OBSERVATION_AT`, and `promote()` writes that into
`collection_index.json`.

**METHOD.** `rt2_future.py`, F4/F4b/F4c. Feed `validate()` and `refresh_one()` payloads with
(a) a row dated 2099-01-01, (b) mixed date formats plus a non-date string, (c) a date field
that is an `int` on one row and a `str` on another.

**REPRODUCED: YES, three ways.**

**NUMBERS.**
- (a) Payload = 1 row dated 2026-09-04 + 1 row dated **2099-01-01**. Verdict `OK`.
  `LAST_GOOD_OBSERVATION_AT` written into the index: **`"2099-01-01"`**. Status
  `NEW_OBSERVATIONS`. Nothing objected.
- (b) Payload = `["2026-09-04", "20260905", "not-a-date"]`. Verdict `OK`.
  `latest_observation` = **`"not-a-date"`**. `max()` runs over raw strings; no row is parsed
  as a date anywhere in `validate()`.
- (c) Payload = one `str` date and one `int` date. `validate()` raises
  **`TypeError: '>' not supported between instances of 'int' and 'str'`**. `fetch()` promises
  never to raise; `validate()` carries no such guard and `refresh_one` calls it with no
  `try`, so the whole refresh run dies on a payload the source can plausibly emit.

**IMPACT: MAJOR on the audit trail, NONE on the agronomy.** No published percentage moves
(T-4). But `LAST_GOOD_OBSERVATION_AT` is one of the six clocks the tool advertises, its name
asserts *good*, and it is the field a reader would use to ask "how fresh is this archive". It
can be set to 2099, or to a string that is not a date.

**WHAT SURVIVES.** The clock is separate from the agronomic filter, so poisoning it does not
poison the numbers.

**FIX:** parse each date with `dt.date.fromisoformat`, drop unparseable ones into a named
rejection, and refuse (or flag) any row dated after the collection date.

---

## T-6 · "N CONSECUTIVE WINDOWS" IS NEVER CHECKED

**CLAIM.** The trend loop builds 4 candidate windows ending at `as_of`, `as_of-28`,
`as_of-56`, `as_of-84`, and keeps the ones passing `MIN_VISITS` / `MIN_DRUPES`. A failing
window is **skipped, not treated as a break in the chain**. The published sentence then says
*"over N consecutive 28-day windows"* and nothing has checked that they are consecutive. The
monotonicity test then runs on a sequence with a deleted middle.

**METHOD.** `rt2_trend.py` (T1) scans 10 provinces × 220 `as_of` days = 2,200 combinations on
the real archive, through the real `di_observe.pooled`. `rt2_hole.py` then builds a synthetic
case designed to trigger it — three rich windows and one starved window in the middle — and
runs the **real** `di_core.load_visits` + `di_observe.cell`.

**REPRODUCED: YES on synthetic, NO on the real archive.**

**NUMBERS.**
- Real archive: **0 of 2,200** province × `as_of` combinations produce a hole (re-checked on
  V3: still **0 of 2,200**). The olive network is dense enough that a window either passes or
  the ones around it fail too.
- Synthetic case, real engine (`di_core 2ba3abc24895ee86`, `di_observe 093d95c9684fbea3`):

  | candidate | window end | visits | drupes | rate | passes gate? |
  |---|---|---|---|---|---|
  | i=0 | 2026-09-06 | 80 | 8,000 | 5.0% | yes |
  | i=1 | 2026-08-09 | 80 | 8,000 | 3.0% | yes |
  | i=2 | 2026-07-12 | 4 | 400 | **9.0%** | **no** (4 < MIN_VISITS 8) |
  | i=3 | 2026-06-14 | 80 | 8,000 | 1.0% | yes |

  Published window ends: **2026-06-14, 2026-08-09, 2026-09-06** — gaps of **56 and 28 days**.
  Published sentence, verbatim:
  *"1.0% -> 3.0% -> 5.0% over 3 consecutive 28-day windows ending 2026-09-06; change 4.0
  percentage points. … they do not overlap, so a direction is named."*
  Published trend: **INCREASING_OBSERVED**.
- The true observed sequence was **1.0 → 9.0 → 3.0 → 5.0**, which is not monotone at all. The
  highest reading in the series was deleted for failing a sample-size gate, and the direction
  was then named on what was left, while the prose asserted a consecutiveness the engine
  never tested.
- Downstream: `INCREASING_OBSERVED` sets `attention_class = INVESTIGATE`.

**IMPACT: MAJOR.** It is the one place I got the tool to name a direction from a series it
does not actually have. It is latent on this archive (0 of 2,200) and live on any sparser
network — and sparser networks are exactly where a gate fails one window at a time.

**WHAT SURVIVES.** `observed_trend_points` carries `window_end` for every point, so a reader
who subtracts them **can** catch it. The renderer prints the sentence, not the ends, so a
human reading the report cannot.

**FIX:** either break the chain at the first failing window (`break` instead of skip), or
assert `all(gap == WINDOW_DAYS)` and downgrade to UNKNOWN otherwise, or stop using the word
"consecutive" and print the gaps.

---

## T-7 · A DIRECTION FROM 2 POINTS WHEN THE MINIMUM IS 3

**CLAIM.** The tool can be made to name a direction from fewer points than it declares.

**METHOD.** `rt2_trend.py` T2/T2b: 2,200 province × `as_of` combinations, tabulated by
(number of points kept, label emitted); then the parameter itself pushed to 2.

**REPRODUCED: NO.**

**NUMBERS.**
- By point count over 2,200 combinations: 0 points → UNKNOWN ×1,541; 1 point → UNKNOWN ×309;
  2 points → UNKNOWN ×269; 3 points → INCREASING ×7, STABLE ×74.
  **0 of 2,119** sub-three-point cells named a direction.
- `TREND_MIN_WINDOWS` is used as **both** the loop bound (`range(P+1)`) and the minimum
  (`len(pts) < P`), so the loop can never build fewer candidates than the minimum requires.
  Setting it to 2 still produced 3 points, because the archive filled all 3 built windows.

**IMPACT: NONE.**

**WHAT SURVIVES.** The 3-point minimum. It holds because the parameter is structurally tied
to the loop, not because someone remembered to check.

---

## T-8 · `TREND_MIN_ABS_CHANGE_PCT = 1.0` HIDING A REAL RISE

**CLAIM.** An absolute 1.0-percentage-point threshold on a quantity that lives near 1% calls
a real rise STABLE.

**METHOD.** `rt2_trend.py` T3/T3b against **V1**: all 10 provinces at `as_of` 2026-09-06 with
denominators, plus a scan of 81 publishable trend-cells over 10 provinces × 220 `as_of` days.
Two-proportion z on first vs last window. Then `rt2_trend2.py` re-measured on **V3**.

**REPRODUCED: YES on V1. FIXED during this audit (V2).**

**NUMBERS — V1, the shipped rule at the time.**

| province | sequence (%) | Δ pp | monotone up | infested / sampled, first → last | rel. change | z | label V1 | attention V1 |
|---|---|---|---|---|---|---|---|---|
| **Pisa** | 0.04 → 0.5022 → 1.02 | **0.98** | yes | 1/2,500 → 94/9,196 | **×25.6** | **4.85** | **STABLE_OBSERVED** | **NO_ESCALATION** |
| Lucca | 0.0769 → 0.4464 → 1.1509 | **1.074** | yes | 1/1,300 → 61/5,300 | ×15.0 | 3.60 | INCREASING_OBSERVED | **INVESTIGATE** |
| Siena | 0.0 → 0.2718 → 0.6909 | 0.6909 | yes | 0/3,100 → 127/18,383 | from zero | 4.64 | STABLE_OBSERVED | MONITOR |

  **0.02 percentage points of Δ separated INVESTIGATE from NO_ESCALATION.** Pisa's rise was
  more extreme than Lucca's in relative terms (×25.6 vs ×15.0) and more significant
  (z = 4.85 vs 3.60), and Pisa was the one called stable. The regional summary line
  *"a subir nas janelas já ocorridas"* listed `['Lucca']` and omitted Pisa.

- Over the 220-day scan: **30 of 81** publishable trend-cells were monotone non-decreasing and
  labelled STABLE_OBSERVED. Largest such hidden rise: **0.9875 pp** (Pisa at `as_of`
  2026-09-01, 0.0 → 0.4831 → 0.9875), i.e. **0.0125 pp** under the threshold.
- **The other side, argued with numbers.** All 30 finish under **0 of 30** crossings of the
  source's own first coloured band. The source's legend is
  `0` / `0.01–6%` (green) / `6–10%` (yellow) / `≥10%` (red). Siena's 0.6909% sits **5.3091 pp**
  below yellow; Pisa's 1.02% sits **4.98 pp** below. Nobody sprays on a move from 0.0% to
  0.69%. An absolute rule expressed in the units of the decision is defensible; a
  significance rule that fires at z = 4.6 on a change of 0.69 pp will fire every season and
  will mean nothing operationally. The correct answer is both numbers side by side, which is
  what the engine now does.

**NUMBERS — V3, after the fix.** The rule is now: non-overlapping Wilson 95% intervals on the
first and last window, **and** monotone. `TREND_MIN_ABS_CHANGE_PCT` is no longer consulted.
Labels that changed: **Pisa** STABLE → INCREASING_OBSERVED, **Siena** STABLE →
INCREASING_OBSERVED. Firenze, Grosseto, Livorno, Massa-Carrara, Pistoia stay STABLE (their
intervals overlap or they are not monotone); Lucca stays INCREASING. Siena's attention class
moved from MONITOR to **INVESTIGATE**.

**IMPACT: MAJOR (V1) → NONE (V3).**

**WHAT SURVIVES.** The V1 rule never invented a rise; it only suppressed one. And the
suppressed rises were all far below the source's own action band, so no spray decision turned
on it. That is why this is MAJOR and not FATAL.

**Residual, RT-statistics territory but it is what now decides the direction:** the Wilson
interval is computed over **drupes** as if each were an independent trial. Siena's last
window: **18,383 drupes** treated as independent, from **186 visits** to **62 groves**, at
98.8 drupes per visit. Clustering is not modelled, so "the intervals do not overlap" is
easier to achieve than the sentence implies. **NOT KNOWN** how much narrower than the truth
the interval is; what would settle it is the design effect computed from the between-grove
variance of the per-visit rates.

---

## T-9 · A DEAD PARAMETER STILL PUBLISHED IN EVERY CELL

**CLAIM.** After the V2 fix, `TREND_MIN_ABS_CHANGE_PCT` is declared, documented, and emitted
in the `params` block of every published cell, and changes nothing.

**METHOD.** `rt2_trend2.py` N2. Grep for every use in `di_observe.py`, then run the real
`cell()` with the parameter at 0.0, at 1.0 and at 9999.0.

**REPRODUCED: YES.**

**NUMBERS.**
- Lines mentioning it in `di_observe.py`: **1** — its own declaration,
  `"TREND_MIN_ABS_CHANGE_PCT": 1.0, # percentage points; below this the change is called STABLE`.
  Zero uses.
- Emitted in every cell's `params` block: **yes**, value **1.0**.
- Siena's trend at parameter = 0.0 → INCREASING_OBSERVED; at 1.0 → INCREASING_OBSERVED;
  at 9999.0 → INCREASING_OBSERVED. Moving it across **four orders of magnitude** changes
  nothing.
- The module docstring, still in the file: *"EVERY parameter is declared here, emitted in
  PARAMS, and varied by the sensitivity test. A parameter that never appears in the output is
  a parameter nobody can audit."*

**IMPACT: MINOR, but it is an auditability defect of exactly the kind the file was written to
prevent.** A parameter that appears in the output and controls nothing is worse than one that
never appears: an auditor reading `params` will believe a 1.0 pp threshold is in force and
will explain a STABLE label with a rule that is not running. A sensitivity test that varies it
will report "insensitive" and mean "disconnected".

**WHAT SURVIVES.** Every other parameter in `PARAMS` is live — `WINDOW_DAYS`, `MIN_VISITS`,
`MIN_DRUPES`, `MIN_BASELINE_SEASONS`, `HIGH_PCTL`, `LOW_PCTL`, `TREND_MIN_WINDOWS`,
`MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE` all changed behaviour when I moved them.

**FIX:** delete it, or note in the comment that the rule was replaced and keep it only as a
recorded historical parameter with `"UNUSED"` beside the value.

---

## T-10 · STALENESS: AN ARCHIVE 400 DAYS OLD

**CLAIM.** The tool reports `last_observation` but has **no latency threshold anywhere**, so a
400-day-old archive is published as today's reading and nothing goes red.

**METHOD.** `rt2_leap_and_stale.py` S1/S2/S3 and `rt2_stale_middle.py`. I shift every date in
a copy of the real archive so its newest observation is 400 days before `as_of`, then 60, 29,
28, 27, 21, 14, 7 and 0 days, and run the real pipeline including `attention_class`. I grep
the whole engine (49,389 bytes across six modules) for any staleness construct. I measure the
real revisit interval so that any proposed threshold has a number under it.

**REPRODUCED: NO for the 400-day case. YES for the 1–27 day band.**

**NUMBERS.**
- Staleness 400 days: **0 of 10** provinces publish. Every `value_pct` is `null`, every
  `n_visits` is 0, `historical_state` is INSUFFICIENT_DATA, `observed_trend` is UNKNOWN,
  `attention_class` is UNKNOWN. Same at 60, 29 and 28 days.
- **The 28-day window is itself the latency gate.** An observation older than
  `WINDOW_DAYS - 1 = 27` days cannot enter the current window, so the tool goes silent at 28
  days of staleness without ever using the word. That is a defensible design — but it is
  undocumented and it is a side effect, not a decision.
- The band the tool does **not** handle, measured:

  | staleness | Firenze | Siena |
  |---|---|---|
  | 0 d | 0.0664% · 241 visits · 24,100 drupes · last obs 4 d before as_of · MONITOR | 0.6909% · 186 visits · 18,383 drupes · 3 d · INVESTIGATE |
  | 14 d | 0.0873% · 126 visits · 12,600 drupes · **16 d** · MONITOR | 0.9643% · 95 visits · 9,333 drupes · **15 d** · INVESTIGATE |
  | 21 d | 0.1587% · 63 visits · 6,300 drupes · **23 d** · MONITOR | 0.7917% · 48 visits · 4,800 drupes · **22 d** · INVESTIGATE |
  | 27 d | not publishable | not publishable |

  At 21 days of staleness the tool publishes a headline percentage on a window that is 75%
  empty, prints *"última observação: 2026-08-14"*, and never subtracts that from
  *"data de referência: 2026-09-06"*. Across all provinces the published percentage moved by
  up to **+0.63 / −0.66 pp** versus the fresh reading.
- Engine grep, 49,389 bytes: `MAX_AGE` 0, `STALE`/`stale` 0, `latency`/`LATENCY` 0,
  `freshness` 0, `age_days` 0, `MAX_LAG` 0, `too_old` 0. `last_observation` is computed,
  emitted and printed, and **compared to nothing**.

**IS THE ABSENCE A DEFECT OR A DEFENSIBLE CHOICE? A number either way.**
- Defensible: the 28-day window already refuses anything older than 27 days, and a redundant
  threshold would be a second place to get it wrong.
- Defect: between 1 and 27 days the reader is shown a number with no age. The archive's own
  revisit rhythm gives the threshold its number — over **2,430** grove-to-grove revisit
  intervals from **373** groves with more than one 2026 visit: **median 7 days**
  (1,243 of 2,430 intervals are exactly 7), **p90 = 9**, **p99 = 21**, max 92. The real
  archive at `as_of` 2026-09-06 is **2 days** old.
- So: a network that has produced nothing for **14 days** has missed two weekly rounds, which
  is beyond p90 for a single grove and far beyond it for a whole province. **14 days** is the
  defensible alarm; **21 days** (p99) is the latest defensible one; **28** is too late because
  by then the tool has already gone silent and the silence looks like "no data" rather than
  "the network stopped".

**IMPACT: MINOR.** No wrong number is published. An old number is published without its age.

**FIX, one field, no new parameter:** emit
`days_since_last_observation = (as_of - last_observation).days` in the observation block and
print it beside the date. Whether it should gate publication is a decision for the owner; the
number is 14.

**WHAT SURVIVES.** Nothing 28 days old or older can be published. The 400-day attack fails
completely: **0 of 10** provinces.

---

## T-11 · THE REFRESH LETS THE ARCHIVE GO BACKWARDS  ← the worst one

**CLAIM.** `di_refresh.validate()` checks that the payload is JSON, that `ok` is not false,
that there is at least one row, at least one readable value and at least one date. It does
**not** compare the payload to what canonical already holds. A response that is 200 OK,
`ok: true`, well-formed, and **short** is promoted, and canonical loses everything the
response omitted. `t3_refresh.py` simulates "new_rows" (one row added) and never simulates
"fewer rows".

**METHOD.** `rt2_refresh.py` R2/R2b and `rt2_refresh2.py` R2c, on a lab copy of the real
archive. Canned transports that return (a) the first 10 of 2,928 real rows, (b) exactly 1
row, (c) **the 2,245 of 2,928 real rows whose value is zero** — the shape a filtered or
partially-restored backend produces. Then the real `promote()`, then the real
`load_visits` + `cell` to see what gets published.

**REPRODUCED: YES.**

**NUMBERS.**
- (a) Source returns **10 of 2,928 rows = 0.34%**. Verdict `OK`, status
  **`NEW_OBSERVATIONS`**, promoted. Canonical rows after: **10**. Firenze's published reading
  goes from **0.0% on 241 visits / 24,100 drupes** to **`null` on 0 visits / 0 drupes**.
  `LAST_GOOD_OBSERVATION_AT` goes **backwards**, 2026-09-04 → 2026-08-26. Nothing flagged it.
- (b) Source returns **1 row**. Same: `NEW_OBSERVATIONS`, promoted, canonical rows after: **1**.
- (c) The dangerous one — the archive does not go silent, it **publishes a wrong number**.
  Source returns **2,245 of 2,928 rows = 76.7%** (all the zero-valued ones). Verdict `OK`,
  status `NEW_OBSERVATIONS`, promoted:

  | province | before | after |
  |---|---|---|
  | Siena | **0.6909%** · 127 infested / 18,383 drupes · 186 visits · band green · trend INCREASING_OBSERVED | **0.0%** · 0 / 13,200 · 132 visits · band **"Nessuna Infestazione"** · trend STABLE_OBSERVED |
  | Pisa | **1.02%** · 93 / 9,196 · 85 visits · band green · trend INCREASING_OBSERVED | **0.0%** · 0 / 4,787 · 45 visits · band **"Nessuna Infestazione"** · trend STABLE_OBSERVED |

  Both stay `observation_publishable: true`. Both clear `MIN_VISITS = 8` and
  `MIN_DRUPES = 400` with room to spare. `last_observation` is unchanged (2026-09-03 /
  2026-09-02), so even the freshness field looks right. Nothing in the six refresh outcomes
  fires: **`anything_refused_it: false`**.
- `t3_refresh.py` simulates this shape: **no**. Its `new_rows` scenario appends one row dated
  2026-09-05 and asserts the answer *changed*. There is no scenario in which the answer
  changes in the wrong direction.

**IMPACT: FATAL.** This is the only path I found that puts a **wrong agronomic number** in
front of a reader. "A failed or empty refresh cannot overwrite a good archive" is true. A
**successful-looking but incomplete** refresh can, and the guarantee as written does not cover
it. The archive spans 84 files; one refresh cycle can regress all 84.

**WHAT SURVIVES.** Staging is real: the file is written to `staging/RAW` and only `promote()`
moves it. The bad payload does reach canonical, but through the front door, not by accident.
The hash chain records what happened, so the damage is *detectable after the fact* — the
`previous_sha256` field is on the record.

**FIX:** compare against the previous snapshot before promoting. A completed season is
monotone: for any `year < current_year`, refuse a payload with fewer rows than canonical. For
the current season, refuse (or escalate to a named seventh outcome, `SOURCE_INCOMPLETE`) when
`n_rows < previous_n_rows` or when `max(parsed dates)` goes backwards. Both numbers are
already in the index (`n_rows`, `rowCount` on all 84 entries).

---

## T-12 · THE YEAR ECHO IS PARSED AND THROWN AWAY

**CLAIM.** `validate()` returns four values, the fourth being `filt` — the source's echo of
the filter it applied, including the year. `refresh_one` unpacks it and never reads it again.

**METHOD.** `rt2_refresh2.py` R5. Request `year=2019`; the transport answers with the real
2026 payload and `"filter": {"year": 2026, "crop": 2}`.

**REPRODUCED: YES.**

**NUMBERS.**
- Requested year **2019**; the source echoed `{"year": 2026, "crop": 2}`.
- `refresh_one` uses `filt`: **no** (zero references after the unpack).
- File written: **`c2_s1_v-1002_2019.json`**. Observation years actually inside it:
  **`["2026"]`** — every row. Status `NEW_OBSERVATIONS`, promoted, index updated to say the
  2019 season was collected.

**IMPACT: MAJOR.** The values are not corrupted — `di_core` reads dates from rows, never from
filenames — so the 2026 rows deduplicate against the real 2026 file. But the **2019 season is
now silently absent** from the archive while the index asserts it is present, and the baseline
loop will simply find one fewer prior season and blame grove rotation, exactly as in T-2. The
check is already sitting in a local variable.

**WHAT SURVIVES.** Because the visit key is `(id_field, date)` and dates come from rows, a
mislabelled file cannot inject a wrong-year observation into a window. Filenames carry no
authority anywhere in `di_core`.

**FIX:** `if filt and filt.get("year") not in (None, year): return SCHEMA_CHANGED/INVALID_DATA`.

---

## T-13 · THE SIX CLOCKS ARE FOUR, AND TWO OF THEM ARE ONE

**CLAIM.** The docstring names six clocks and says they are *"kept apart and never collapsed
into one date"*.

**METHOD.** `rt2_refresh.py` R3/R3b. Enumerate the keys of a real `refresh_one` record; run it
against a transport that sleeps 2.0 s and compare the stamps to the wall clock before and
after the call; run it against a transport that raises.

**REPRODUCED: YES.**

**NUMBERS.**
- Of the six declared clocks, present in the record: `COLLECTION_TIME` yes,
  `SOURCE_PUBLICATION_TIME` yes (`"UNKNOWN"`), `SOURCE_UPDATE_TIME` yes (`"UNKNOWN"`),
  `LAST_GOOD_OBSERVATION_AT` yes, **`OBSERVATION_TIME` no**, **`PROCESSING_TIME` no**.
  **4 of 6.** (`OBSERVATION_TIME` is fairly per-row and lives in the data; `PROCESSING_TIME`,
  documented as *"when this snapshot was written"*, simply does not exist.)
- `REFRESH_ATTEMPT_AT` and `COLLECTION_TIME` are the **same string**, both
  `2026-09-07T00:15:23+00:00`, because `now` is computed on the first line of `refresh_one`
  and reused. The call returned at `00:15:25` — the transport took 2.0 s.
  `COLLECTION_TIME_is_stamped_BEFORE_the_request: true`. With `timeout=90` the stamp can
  precede the actual collection by up to 90 seconds.
- On a failed fetch: status `SOURCE_UNAVAILABLE`, and a `COLLECTION_TIME` of
  `2026-09-07T00:15:25+00:00` is emitted anyway, **for a collection that never happened**.

**IMPACT: MINOR.** Nobody is misled by 2 seconds. The claim in the docstring is what is wrong:
two of the six clocks are not emitted, and two of the emitted ones are byte-identical by
construction, which is the definition of collapsed.

**WHAT SURVIVES.** `SOURCE_PUBLICATION_TIME` and `SOURCE_UPDATE_TIME` are honestly `UNKNOWN`
rather than quietly filled with the collection time. That is the failure mode this section of
the design was written to prevent, and it holds.

**FIX:** stamp `COLLECTION_TIME` after the transport returns, add `PROCESSING_TIME` at the
moment the blob is written, and omit `COLLECTION_TIME` on `SOURCE_UNAVAILABLE`.

---

## T-14 · THE CANONICAL ARCHIVE HAS NO CLOCK AT ALL

**CLAIM.** *"the index is MERGED, every entry keeps its own clock"*.

**METHOD.** `rt2_refresh.py` R4. Count the fields on all 84 entries of the real
`CASES/OLIVO-BACTROCERA-TOSCANA/collection_index.json`.

**REPRODUCED: YES.**

**NUMBERS.**
- Index entries: **84**. Entries carrying `COLLECTION_TIME`: **0**. `REFRESH_ATTEMPT_AT`:
  **0**. `LAST_GOOD_OBSERVATION_AT`: **0**. `SOURCE_PUBLICATION_TIME`: **0**.
  `SOURCE_UPDATE_TIME`: **0**. `PROCESSING_TIME`: **0**. `sha256`: **84 of 84**.
- The only keys present on any entry: `file`, `n_rows`, `ok`, `rowCount`, `sha256`, `var`,
  `year`.
- **0 of 84 files in the canonical archive record when they were fetched.** For 100% of the
  data behind every published number, "how old is this collection" is unanswerable.

**IMPACT: MAJOR for the audit claim, NONE for the numbers.** The merge machinery is correct —
it preserves whatever is there — but there is nothing there yet. The claim describes the code,
not the archive. The first real refresh will start filling it, one file at a time, leaving a
mixed archive in which 1 entry has a clock and 83 do not, which is harder to read than either
extreme.

**WHAT SURVIVES.** All 84 entries carry a `sha256`, and T-15 confirms the merge does not drop
fields. So *what* was collected is fully pinned even though *when* is not.

---

## T-15 · IDEMPOTENCE

**CLAIM (mine, the one I was asked to test).** Run the refresh twice against identical bytes
and prove canonical is untouched both times, or find where it is not.

**METHOD.** `rt2_refresh.py` R1/R1b and `rt2_refresh2.py` R1c. A lab copy of the archive with
the **real `collection_index.json` copied byte for byte**. A transport that serves back
exactly what canonical holds. `refresh_one` + `promote` three times, hashing **every file
under canonical** (not just RAW) before, between and after.

**REPRODUCED: PARTIALLY — RAW is idempotent; the index is not, once.**

**NUMBERS.**
- Runs 1, 2 and 3: status **`NO_UPDATE`** each time, `promoted: []` each time.
  **RAW files whose bytes changed: 0, across all three runs.** The core promise holds.
- But the real index does move on the **first** no-op: bytes identical **false**,
  23,101 bytes before and after, sha `4ecd1b4f0e36f13e` → `807ad9bd303e0662`. Entry count
  84 → 84, same set of entries, **0** fields lost. What changed is the **order**: the shipped
  index is grouped by variable (`c2_s1_v-1003_2006.json` first); `promote()` writes
  `[by_file[f] for f in sorted(by_file)]`, so it comes back sorted by filename
  (`c2_s1_v-1001_2006.json` first).
- The **second** no-op is a true no-op: bytes identical **true**. So it is a one-time
  normalisation, not drift.
- The record says **`canonical_touched: false`** on the very run that rewrote a file inside
  `canonical_dir`. `promote()` writes the index **unconditionally**, even when it promotes
  nothing.
- `t3_refresh.py` cannot see this: its `answer()` hashes `load_visits` output, which never
  reads `collection_index.json`. And its `build_lab()` writes its own index with
  `json.dump(indent=1)` in already-sorted order, so the lab starts in the normalised state
  and the reordering is invisible by construction.

**IMPACT: MINOR.** No observation is lost, no field is dropped, the second run is stable. But
`canonical_touched: false` is a false statement about a file that changed, and it is the field
an operator would trust.

**WHAT SURVIVES.** Idempotence on the data itself, which is the part that matters: **0 RAW
bytes changed over three identical refreshes**, and `NO_UPDATE` correctly detected each time
by hash comparison against canonical.

**FIX:** `if not promoted: return` before the `json.dump`, and set `canonical_touched` from
what actually happened rather than from the branch taken.

---

## T-16 · ATTACKING `t3_refresh.py` ITSELF

**CLAIM.** Five of six scenarios use canned transports. Ask what shape the real source
produces that the cans do not.

**METHOD.** Read the test; enumerate its scenarios; construct each missing shape and run it
through the real `di_refresh`.

**REPRODUCED: YES — five failure shapes the test does not simulate, four of them reachable.**

| shape the source can produce | simulated by t3? | what the real code does | my evidence |
|---|---|---|---|
| 200 OK, `ok:true`, **fewer rows than canonical** | **no** | promoted; canonical regresses; a wrong number is published | T-11, `rt2_refresh.py` R2, `rt2_refresh2.py` R2c |
| 200 OK with a row dated in the **future** | **no** (its `new_rows` row is dated 2026-09-05, before AS_OF) | `LAST_GOOD_OBSERVATION_AT` = the future | T-5, `rt2_future.py` F4 |
| `date` present but **not a date string** | **no** | `latest_observation` = `"not-a-date"` | T-5, F4b |
| `date` of **mixed type** (int and str) | **no** | uncaught `TypeError` kills the run | T-5, F4c |
| payload for the **wrong year** (the API ignores a filter) | **no** | written under the requested year's filename | T-12, `rt2_refresh2.py` R5 |

Two further blind spots in the test's *assertions* rather than its inputs:
- `answer()` hashes `{k: v for k, v in loaded.items() if k != "visits"}`, which never reads
  `collection_index.json`. Any change to the index is invisible to
  `CANONICAL_UNCHANGED` (T-15).
- The verdict `every_bad_refresh_left_canonical_intact_and_readable` excludes `new_rows` from
  the check, so the one scenario that *does* write to canonical is the one nobody checks for
  damage.

Minor hygiene: after the `new_rows` scenario the lab is left mutated on disk (`build_lab()` is
called in the `else` branch only), and `build_lab()` writes the literal string
`"recorded at build time"` into a field named `LAST_GOOD_OBSERVATION_AT`.

**IMPACT: MAJOR.** The test is honest about the five-of-six canning and it does prove the
scenarios it runs. But the shape most likely to actually occur in production — a partially
successful backend answering 200 with less data — is the one it does not have, and that shape
is the FATAL finding.

**WHAT SURVIVES.** The six named outcomes are genuinely distinguished; the live probe
scenario means "is the endpoint alive" is measured, not assumed; and the mutation discipline
in `t2_gates.py` (every gate ships with an executioner, and G7's v1 mutation is documented as
a no-op that proved nothing) is the strongest testing idea in this repository. My criticism is
that the discipline was applied to the gates and not to `t3`.

---

## T-17 · THE TRAILING WINDOW HAS NOT FINISHED COLLECTING

**CLAIM.** The newest trend window ends at `as_of`, but the data does not. Its last days are
still arriving, so the newest point is computed on a shorter effective window than the ones it
is compared against.

**METHOD.** `rt2_trend.py` T4/T4b. For all 10 provinces, measure the gap between each window's
end and its last observation. Then take 19 **complete** windows and recompute each with its
last 4 days removed — what an `as_of` set 4 days earlier would have seen.

**REPRODUCED: YES, and it is small, and it points the other way.**

**NUMBERS.**
- Dead trailing days in the newest window at `as_of` 2026-09-06: Lucca 6, Massa-Carrara 6,
  Arezzo 4, Firenze 4, Pisa 4, Pistoia 4, Prato 4, Siena 3, Grosseto 2, Livorno 2.
  Range across all 29 measured windows: **1 to 6 days**.
- What the last 4 days of a window are worth: **0.0% to 18.1%** of its drupes.
  Worst: Grosseto's window ending 2026-07-12, **3,350 of 18,550 drupes = 18.1%**.
  In 9 of 19 windows the last 4 days carry **0** drupes — weekly scouting means the tail of a
  window is often empty by design, not by lag.
- Effect on the rate: median difference (full minus truncated) **0.0 pp**, max **+0.0343 pp**,
  min **−0.0703 pp**. In **18 of 19** windows the truncated (still-filling) version reads
  **equal or higher** than the settled one. So an in-flight window is more likely to read
  **high and settle down** than the reverse.
- Against the decision scale: 0.0703 pp is **7%** of the old 1.0 pp trend threshold and
  **1.2%** of the distance from Siena's reading to the source's yellow band.

**IMPACT: MINOR.**

**WHAT SURVIVES.** The window is a fixed calendar span, not "the last N observations", so a
late-arriving row lands in the window it belongs to rather than shifting the frame. That is
the right design.

**NOT KNOWN:** whether a re-run tomorrow, after the source has filled in 2026-09-03…06, would
move today's published Firenze number. There is exactly **one vintage** of this archive on
disk, so late arrival cannot be measured, only bounded by the truncation experiment above.
What would settle it: keep two dated snapshots of the same `year=2026` payload and diff the
rows. `di_refresh`'s `previous_sha256` field makes this cheap to start doing today.

---

## WHAT I COULD NOT BREAK

Stated as measurements, not as reassurance.

1. **The wall clock never touches a published number.** With `date.today`, `datetime.now`,
   `datetime.utcnow`, `time.time` and four more armed to raise, the full pipeline completed
   and produced all 10 provinces. Two runs 2 seconds apart are byte-identical
   (`6c25f8ee7ddf68a8…`). The published artifact contains no timestamp. `as_of` defaults to a
   hardcoded date, not to today.

2. **No future-dated observation reaches an agronomic number.** Five rows reading 100%
   infestation, dated 1 day to 26,780 days after `as_of`, placed in the raw bytes: **5 of 5**
   dropped and counted, **0 of 17** published fields moved, **0 of 20** province × metric
   cells moved. The date parser accepts nothing that disguises a future date as a past one,
   and **0 of 317,004** real rows use a format that could.

3. **The 3-window trend minimum holds.** **0 of 2,119** sub-three-point cells named a
   direction, over 2,200 province × `as_of` combinations.

4. **A 400-day-old archive publishes nothing.** **0 of 10** provinces. The 28-day window is a
   hard, if accidental, latency gate at 28 days.

5. **The RAW archive is idempotent.** Three consecutive refreshes against identical bytes:
   `NO_UPDATE` three times, **0** RAW files changed.

6. **A bad payload never reaches canonical.** Network error → `SOURCE_UNAVAILABLE`;
   `ok:false` → `SOURCE_EMPTY`; all-null values → `SOURCE_EMPTY`; non-JSON → `INVALID_DATA`.
   Canonical untouched in all four. (What passes is a payload that is *good but incomplete* —
   T-11.)

7. **Filenames carry no authority.** Every date comes from a row. A file named for the wrong
   year cannot inject a wrong-year observation into a window (T-12); a mutated file order
   cannot change the answer (G3, and my own year-cross and hole labs read files in whatever
   order the OS gave them and matched).

8. **29 February is genuinely handled.** The fallback fires on **3 of 3,288** dates scanned,
   all of them 29 February, and `day=28` is correct for all 3.

9. **I did not modify anything I was told not to.** Byte fingerprint of
   `CASES/OLIVO-BACTROCERA-TOSCANA`: **86 files, 0 changed** across the whole session
   (`rt2_refresh.py` measures this before and after its own lab runs). `git status` on
   `DISEASE-INTELLIGENCE-ITALY/` and `italia-portale/` is empty. Nothing committed, nothing
   pushed. All lab directories created under `REDTEAM/` were deleted.
   (`tests/t1_determinism.json`, `tests/t2_gates.json`, `tests/t2_gates.py` and
   `tests/t4_independent_reproduction.py` do show as modified in `git status` — not by me.
   No RT2 script reads or writes anything outside `REDTEAM/`, and I never executed the test
   suite. Those edits belong to whoever was changing the engine during this session, per
   section 0.)

---

## SCOREBOARD

| # | accusation | reproduced | impact |
|---|---|---|---|
| T-11 | a valid-but-incomplete refresh silently regresses the archive and publishes 0.0% | YES | **FATAL** |
| T-2 | the 28-day window across 31 Dec gives a -338-day baseline window | YES | MAJOR (code) / NONE (this case) |
| T-6 | "N consecutive windows" is asserted in prose and never checked | YES (synthetic) / NO (real: 0 of 2,200) | MAJOR |
| T-8 | the 1.0 pp trend rule hid a ×25.6 monotone rise (z=4.85) and cost Pisa its INVESTIGATE | YES on V1 | MAJOR → fixed in V2 |
| T-12 | the source's year echo is parsed and discarded | YES | MAJOR |
| T-14 | 0 of 84 canonical entries record when they were fetched | YES | MAJOR (audit) |
| T-16 | t3 does not simulate the failure shape that matters | YES | MAJOR |
| T-5 | a future-dated row sets `LAST_GOOD_OBSERVATION_AT` to 2099 | YES | MAJOR (audit) / NONE (agronomy) |
| T-9 | `TREND_MIN_ABS_CHANGE_PCT` is published in every cell and controls nothing | YES | MINOR |
| T-10 | a 1–27 day stale reading is published with no age | YES | MINOR |
| T-13 | 4 of 6 clocks emitted; 2 of them byte-identical, stamped before the fetch | YES | MINOR |
| T-15 | the first no-op promote rewrites the index while reporting `canonical_touched: false` | YES | MINOR |
| T-17 | the newest window is 1–6 days short of data; the tail is worth ≤18.1% of drupes | YES | MINOR |
| T-3 | 29 February corrupts the baseline | PARTIAL (1 day of 28 = 3.6%; 1 of 194 seasons at risk) | MINOR |
| T-1 | the wall clock reaches a published number | **NO** | NONE |
| T-4 | a future observation reaches a published number | **NO** | NONE |
| T-7 | a direction is named from 2 points | **NO** | NONE |

**Ranked repairs.** (1) T-11: compare row count and max date against the previous snapshot
before promoting; both numbers are already on all 84 index entries. (2) T-6: break the trend
chain at the first failing window, or assert the 28-day gaps. (3) T-2: `shi = slo + (hi - lo)`.
(4) T-12: one `if` on `filt["year"]`. (5) T-9: delete the dead parameter. (6) T-10: emit
`days_since_last_observation`; the defensible alarm is 14 days (p90 of grove revisit is 9,
p99 is 21).

---

### Scripts and outputs in this folder

| script | what it proves | output |
|---|---|---|
| `rt2_clock.py` | the clock armed to raise; analysis survives, refresh dies | `rt2_clock.json` |
| `rt2_yearcross.py` | -338-day baseline windows; synthetic winter case | `rt2_yearcross.json` |
| `rt2_leap_and_stale.py` | 29 Feb; 400-day archive; revisit intervals | `rt2_leap_and_stale.json` |
| `rt2_stale_middle.py` | the 1–27 day staleness band | `rt2_stale_middle.json` |
| `rt2_future.py` | future rows in the raw bytes; the date parser; the refresh clocks | `rt2_future.json` |
| `rt2_trend.py` | the 1.0 pp rule on V1; consecutiveness scan; trailing-window tail | `rt2_trend.json` |
| `rt2_trend2.py` | the same attacks on V3; the dead parameter | `rt2_trend2.json` |
| `rt2_hole.py` | "3 consecutive windows" that are 56 and 28 days apart | `rt2_hole.json` |
| `rt2_refresh.py` | idempotence; truncated payload; the six clocks; the 84 entries | `rt2_refresh.json` |
| `rt2_refresh2.py` | the index reorder; the truncation that publishes 0.0%; winter mass | `rt2_refresh2.json` |

Every script recreates its own lab and deletes it. None writes to `CASES/`, `engine/`,
`tests/` or `italia-portale/`.
