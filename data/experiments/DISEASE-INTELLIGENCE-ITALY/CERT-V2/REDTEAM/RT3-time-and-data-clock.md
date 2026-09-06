# RT3 — TIME, LEAKAGE, AND THE DATA CLOCK

Independent red team, temporality lens. I did not write the code under test.
Nothing under `ENGINE/` or `CASES/` was modified; `git status` for both paths is clean and
`ENGINE/gates.json` has the same md5 before and after every run
(`55bedd3d5a113a872cc53539e7d278cf`). Every script referenced below lives in
`CERT-V2/REDTEAM/` and writes its raw numbers to a sibling `.json`.

Machine: win32, Python 3.12.10, `sys.getdefaultencoding` = utf-8,
`locale.getpreferredencoding(False)` = **cp1252**, `PYTHONUTF8` unset. That last fact is
load-bearing for accusation B4.

Denominators used throughout, so they are never ambiguous:

| set | rows |
|---|---|
| outcome-variable rows (what `load_rows(case, var)` returns) | olive 79,251 · vine 35,065 · wheat 5,817 · **total 120,133** |
| all rows in all RAW files, all variables | olive 317,004 · vine 70,130 · wheat 5,817 · **total 392,951** |
| RAW files on disk | olive 84 · vine 40 · wheat 14 · **total 138** |
| published province-cells today (2 certified cases x 10 provinces) | **20** |

---

## SUMMARY

| # | accusation | reproduced | impact |
|---|---|---|---|
| A1 | a clock reaches a published number | **NO** | NONE |
| A2 | the baseline window is broken when it crosses 31 December | **YES** | MAJOR (latent) |
| A3 | the 29 February rule changes the window length | **YES** | MINOR |
| A4 | gate B's "load-bearing" evidence is a confound, and gate B cannot fail | **YES** | MAJOR |
| A5 | hindcast leaks future seasons into a baseline | **NO** | NONE |
| A6 | the published class depends on when the archive was collected | **PARTLY** | MINOR |
| B1 | the freshness badge lies | **YES**, in two specific ways | MAJOR |
| B2 | gate H's freshness certification is pinned to a frozen date | **YES** | MAJOR |
| B3 | a failed refresh silently disables the hash chain / takes the case down | **YES** | MAJOR |
| B4 | write encoding and hash encoding disagree | **YES** | MAJOR |
| B5 | nothing records when a refresh was attempted or when data was collected | **YES (absent)** | MAJOR |

---

# LENS 1 — TIME AND LEAKAGE

## A1. "There is a path where the clock reaches a published number"

**CLAIM.** `AS_OF` is documented as an input, never `now`. I tried to find any path —
direct call, default argument, file mtime, transitive import — by which the system clock
reaches a published cell.

**METHOD.** `CERT-V2/REDTEAM/rt3_e1_clock_audit.py`, three independent layers:
AST scan of every `.py` in `ENGINE/` and `CASES/`; a runtime trap that replaces
`date.today`, `datetime.now`, `datetime.utcnow`, `datetime.today`, `time.time` and
`time.localtime` with functions that raise, then runs the whole publication path; and a
frozen-clock equivalence test under three different fake system clocks.

**REPRODUCED: NO.**

**NUMBERS.**
- AST: **10 of 10** `.py` files scanned. **3** clock calls in the entire pilot, all
  `time.time()`, all in `ENGINE/automation_probe.py` (lines 13, 41, 45). They feed one field,
  `seconds` (probe latency). Gate H reads `HTTP`, `ok`, `n_rows`, `non_null_values`,
  `SILENT_FAILURE` from that probe and never reads `seconds`. No cell carries it.
- Runtime trap: `load_rows` OK, `current_pressure` OK, `hindcast` OK, `sensitivity` OK —
  **4 of 4** stages complete with every clock function armed to raise.
- Frozen-clock equivalence: system clock set to 1999-01-01, 2026-09-06 and 2099-12-31 →
  **1 distinct output** of 3 runs, byte-identical, 9,770 bytes.
- Zero hits for `getmtime`, `st_mtime`, `os.stat` in `ENGINE/` and `CASES/`.

**IMPACT: NONE.**

**WHAT SURVIVES.** This is the strongest part of the build and I could not dent it. Replay is
real: the same `AS_OF` and the same archive give the same bytes on any machine clock.

The one thing worth recording is not a clock but a **frozen literal**. The only date default
argument in the pilot is `ENGINE/gates.py:20`:

```python
def evaluate(as_of=dt.date(2026, 9, 6)):
```

`ENGINE/answer_sheet.py:117` and `ENGINE/refresh_coverage.py:12` carry the same literal as a
CLI fallback. See B2 for what that does to gate H.

---

## A2. "The baseline window is wrong when the window crosses 31 December"

**CLAIM.** `current_pressure` computes `hi, lo = as_of, as_of - 27d` and builds each baseline
as `_shift_year(lo, y) .. _shift_year(hi, y)` — shifting the two endpoints into the same
calendar year **independently**. When `lo.year != hi.year` this produces `lo > hi`: an
interval of negative length that no row can ever fall inside.

**METHOD.** `rt3_e2_year_boundary.py` (arithmetic + reachability in the real archives),
`rt3_e10_winter_case.py` (a synthetic winter-active case fed to the unmodified engine).

**REPRODUCED: YES.**

**NUMBERS — the arithmetic.**

| AS_OF | current window | days | baseline window for y-1 | days |
|---|---|---|---|---|
| 2026-01-01 | 2025-12-05 .. 2026-01-01 | 28 | 2025-12-05 .. **2025-01-01** | **-337** |
| 2026-01-15 | 2025-12-19 .. 2026-01-15 | 28 | 2025-12-19 .. **2025-01-15** | **-337** |
| 2026-01-27 | 2025-12-31 .. 2026-01-27 | 28 | 2025-12-31 .. **2025-01-27** | **-337** |
| 2026-01-28 | 2026-01-01 .. 2026-01-28 | 28 | 2025-01-01 .. 2025-01-28 | 28 |

It fires on exactly **27 of 365** `AS_OF` dates per year (1–27 January), i.e. **7.4%** of the
calendar.

**NUMBERS — reachability in the shipped archives.** It cannot bite today, and I say so
plainly. Of **120,133** outcome-variable rows: rows dated in December or January = **7**
(olive 7 in January of 79,251; vine 0 of 35,065; wheat 0 of 5,817), and **0 of those 7** carry
a readable value. Running the engine at 2026-01-15 gives **10 of 10** provinces
`UNKNOWN_NO_DATA` in both certified cases — the current window is empty before the baseline is
ever reached, so the defect is masked by the absence of winter scouting.

**NUMBERS — made reachable.** Gate I certifies that the pipeline *generalizes*, so a
winter-active case is in scope. `rt3_e10_winter_case.py` builds one: 131,040 rows, 21 seasons,
12 sites in each of 10 provinces visited every 7 days in **every week of every year**,
incidence held near 0.33 with no trend. Fed to the **unmodified** engine, sweeping all 365
`AS_OF` days of 2026:

| | crossing days (1–27 Jan) | non-crossing days (28 Jan – 31 Dec) |
|---|---|---|
| days | 27 | 338 |
| provinces classed (min–max) | **0 – 0** of 10 | **10 – 10** of 10 |
| `UNKNOWN_NO_BASELINE` (min–max) | **10 – 10** of 10 | 0 – 0 of 10 |
| median `BASELINE_N` (min–max) | **0 – 0** | **20 – 20** |

A cliff from 20 usable baseline seasons to 0, on identical data, caused only by the calendar.
**270 of 3,650** province-days lost.

**IMPACT: MAJOR**, not FATAL. It fails to `UNKNOWN_NO_BASELINE` — the safe direction. No wrong
class is published; the capability simply goes dark for 7.4% of the year on any case that
scouts through the winter. It is invisible to the current gate set because all three archives
stop in October and gate I's unseen case (wheat) runs April–June only.

**WHAT SURVIVES.** The declared contract — "the SAME calendar window in every prior season" —
is honoured on the other 338 days, and the failure is loud in the output (`UNKNOWN_NO_BASELINE`
with `BASELINE_N: 0`), not silent in a number.

---

## A3. "The 29 February rule quietly changes the window length"

**CLAIM.** `_shift_year` maps 29 February to 28 February, which is declared. What is not
declared is that the current and baseline windows then have **different lengths**.

**METHOD.** `rt3_e2_year_boundary.py`, section `ARITHMETIC`.

**REPRODUCED: YES.**

**NUMBERS.** `AS_OF` = 2024-02-29 → current window 2024-02-02..2024-02-29 = **28 days**;
baseline window for 2023 = 2023-02-02..2023-02-28 = **27 days**. The current window carries one
extra day of exposure relative to every non-leap baseline season. For `AS_OF` = 2024-03-27
(`lo` = 29 Feb) both windows are 28 days, so only the case where **`hi`** is 29 February is
affected: **1 of 366** days in a leap year, **1 in 1,461** days overall.

Rows dated 29 February in the shipped archives: **0 of 120,133**. Unreachable today.

**IMPACT: MINOR.**

**WHAT SURVIVES.** The mapping itself is declared in the code
(`# 29 Feb -> 28 Feb, declared`), and the direction is conservative.

---

## A4. "Gate B's evidence is a confound, and gate B cannot detect what it certifies"

**CLAIM.** Gate B publishes this sentence:

> "…moving the cutoff forward changes **18** published province-cells — so the cutoff is
> LOAD-BEARING and this gate can detect its removal, which the previous version could not."

Moving `AS_OF` forward 30 days also moves the window's **lower** bound forward 30 days.
Cells would change even with no upper cutoff at all. Three sub-claims, all tested.

**METHOD.** `rt3_e3_gate_b_attack.py`. Gate B's predicate is transcribed verbatim from
`ENGINE/gates.py:63-84` with `current_pressure._window_value` swappable, and driven under
three engines. Additionally `rt3_e8_gates_time.py` drives the **real** `gates.evaluate`.

**REPRODUCED: YES, on all three sub-claims.**

**NUMBERS — (i) the confound is total.**

| case | future rows | gate B counts changed | window slide **alone** explains | attributable to the **upper cutoff** |
|---|---|---|---|---|
| OLIVO x BACTROCERA | 0 of 79,251 | 9 of 10 | **9 of 10** | **0 of 10** |
| VITE x OIDIO | 15 of 35,065 | 9 of 10 | **9 of 10** | **0 of 10** |
| total | 15 | **18** | **18** | **0** |

"Window slide alone" = the identical 30-day move with every future-dated row physically
deleted from the archive. All 18 cells the gate offers as evidence for the cutoff change
without any future data existing. The residual attributable to the cutoff is **0 of 20**.

**NUMBERS — (ii) the cutoff is not load-bearing in fact.** Removing the upper bound of the
current window today changes **0 of 20** published cells (0 of 10 olive, 0 of 10 vine). The 15
future rows are one single day, 2026-09-07, 15 distinct `id_field`, **all decoding to 0.0**,
in Firenze (6) and Siena (9). Firenze already publishes 0.0 incidence over 29 sites and Siena
over 29 sites, so 6 and 9 more zeros move nothing.

**NUMBERS — (iii) the gate returns PASS with the cutoff removed.**

| engine | fut | used_fut | load_bearing | gate B verdict |
|---|---|---|---|---|
| shipped, unmodified | 15 | 15 | 18 | **PASS** |
| `hi` unbounded in **every** window | 15 | 15 | 18 | **PASS** |
| `hi` unbounded in the **current** window only | 15 | 15 | 18 | **PASS** |

Identical numbers in all three. Gate B is arithmetically incapable of detecting removal of the
cutoff, which is precisely the property its own comment claims it now has. The mechanism is
simple: `honest` and `leaked` are both computed by the patched engine, so both shift together
and still differ by the lower bound.

**CONFIRMED AGAINST THE REAL `gates.evaluate`, not my transcription.**
`rt3_e8_gates_time.py` runs `ENGINE/gates.py:evaluate()` end to end (live probes included) at
the default `AS_OF` and again with `_window_value`'s upper bound removed:

| | PASS | FAIL | NOT_TESTABLE | gate B |
|---|---|---|---|---|
| RUN1 default `AS_OF` | 8 | 2 | 0 | **PASS** |
| RUN3 **upper cutoff removed** | 8 | 2 | 0 | **PASS** |

**10 of 10** gate verdicts identical, and gate B emits the byte-identical evidence sentence —
"…changes 18 published province-cells — so the cutoff is LOAD-BEARING and this gate can detect
its removal" — in a run where the cutoff **has been removed**. (RUN1 reproduces the shipped
`ENGINE/gates.json` exactly on 9 of 10 gates; only J differs, FAIL here vs NOT_TESTABLE
shipped, because the portal snapshot it reads is at a Linux path absent on this machine.)

**A fourth defect, found only by the real run.** At `AS_OF + 30d` gate B returns
`NOT_TESTABLE` — and still prints:

> "**0** observations in the archive are dated after the cutoff, **0** of them inside the
> published window, and moving the cutoff forward changes **0** published province-cells —
> **so the cutoff is LOAD-BEARING and this gate can detect its removal**…"

The evidence string is a single f-string emitted unconditionally, with its conclusion written
into the template rather than derived from the verdict. It asserts "LOAD-BEARING" while
reporting 0, 0, 0. Anything reading `EVIDENCE` without also reading `VERDICT` is misinformed.

**A fifth, about fragility.** Gate B is testable today only because of those **15 rows of
35,065** dated 2026-09-07 in one case. Move `AS_OF` forward 30 days and `fut` drops to 0 and
the gate goes `NOT_TESTABLE`, which `gates.py`'s own header says "is NOT counted as a pass".
The gate's ability to run at all depends on the source happening to be one day ahead of the
chosen cutoff.

**Two aggravating findings from the same file.**

1. `CUTOFF_LABEL == "NOWCAST"` is still a conjunct of the predicate and is a **constant**.
   `Cutoff.is_forecast()` (`ENGINE/contracts.py:120`) returns
   `issue_date < target_window_start`; `current_pressure.py:263` constructs
   `Cutoff("current_pressure", as_of, lo, hi)` with `lo = as_of - 27d`, so the test is
   `as_of < as_of - 27d` — False for every input. Enumerated: **654** constructions over
   6 window lengths (1, 7, 14, 28, 42, 365 days) x 109 cutoff dates spanning 2006-2016 yield
   **1** distinct label, `NOWCAST`; `FORECAST` is unreachable. `gates.py` diagnoses exactly
   this about the old version of the gate and then leaves the term in the new one.
2. `Cutoff.assert_no_day_leakage` — the contract's *actual* enforcement of "no observation
   after the cutoff reaches a number" — is defined at `ENGINE/contracts.py:115` and has
   **0 callers** in `ENGINE/` and `CASES/`. `Cutoff` is instantiated exactly **once** in the
   whole pilot, only to call `.label()`.

Also: gate B sums `fut` **across** cases. Olive contributes **0 of 79,251** future rows, so
one case's 15 rows carry the conjunct for both. A per-case `fut > 0` would have made olive
`NOT_TESTABLE`.

**IMPACT: MAJOR.** Not FATAL, because the gate's *verdict* is accidentally correct (A1 shows
the engine genuinely never transports time, and the window genuinely ends at `AS_OF`). What is
false is the gate's **evidence sentence** and its **claimed ability to fail**. A gate that
cannot fail is not evidence; it is decoration with a number attached. This is the fourth
tautology in this gate set by the file's own count, and it was introduced by the rewrite that
was meant to remove the third.

**WHAT SURVIVES.** The nowcast claim itself. A5 and A1 establish it by other means: no clock
path, and no baseline anywhere consumes a row dated at or after the season it is a baseline
for. Gate B is wrong about *why*, not about *what*.

---

## A5. "hindcast leaks future seasons into a baseline"

**CLAIM.** `hindcast()` replays the definition at the same calendar date in prior seasons with
"baseline = prior seasons only". I tried to show that some baseline for year Y contains an
observation dated year >= Y.

**METHOD.** `rt3_e4_leakage.py`. `current_pressure._window_value` is wrapped by a spy that
records, for every window it is asked to summarise, the set of calendar years of the rows it
actually **consumed** (passed the date filter *and* had a readable value) and the maximum date
consumed. The engine is then driven over every season present in each archive.

**REPRODUCED: NO.**

**NUMBERS.**
- OLIVO: **0 of 21** seasons leak. VITE: **0 of 20** seasons leak.
- In all 41 season-runs: the current window consumed exactly one calendar year (its own), its
  maximum consumed date was `<= AS_OF` in every case, and the set of baseline years at or
  after the run year was empty — `BASELINE_YEARS_AT_OR_AFTER_AS_OF_YEAR = []`, 41 of 41.
- Spot check of the monotone chain, olive: run year 2019 → baseline max date 2018-09-06;
  2020 → 2019-09-06; 2026 → 2025-09-05. Never inverted.

**IMPACT: NONE.**

**WHAT SURVIVES.** The walk-forward is genuinely walk-forward at the row level. This is the
second thing I could not break.

**One latent hazard, recorded honestly.** `hindcast`'s `recent_only` subset filter
(`current_pressure.py:362`) bounds only from **below**:

```python
sub = [r for r in pre[0] if r["_d"].year > y - 1 - (recent_only or 9999)]
```

At probe season 2016 with `recent_only=5`, **40,056** olive rows dated after 2016 survive into
the subset (**11,284** for vine at season 2017). They never reach a number, because
`current_pressure`'s baseline loop skips `y >= as_of.year` and the current window is
date-bounded — I verified this with the same spy. But the safety lives entirely in the
consumer, not in the filter, and the filter's name says otherwise. NOT KNOWN whether any
caller other than `hindcast` will ever pass a subset to `_pre`; what would settle it is a
`_pre` contract that refuses rows dated after the `as_of` it is handed.

---

## A6. "The published class depends on WHEN the archive was collected"

**CLAIM.** If the source revises history, or serves a different code table over time, then
every baseline and every percentile is a function of the collection date — and with no
`COLLECTED_AT` recorded anywhere (B5), that function's argument is unrecoverable.

**METHOD.** `rt3_e9_collection_time_dependence.py` re-fetches 6 vine and 6 olive seasons live
and compares to the archive by content hash and by per-visit `val`.
`rt3_e11_scale_drift.py` builds the ordinal scale from the stored code table and from the most
complete table the source serves today, and re-publishes under each.

**REPRODUCED: PARTLY.**

**NUMBERS — row revision.** **11 of 12** season probes returned content **identical** to the
archive: 0 delta rows, identical content hash, and **0 changed `val` in 29,448 common visits**
across vine 2015/2019/2020/2024/2025/2026 and olive 2015/2019/2020/2024/2025. The single
exception is the **open** season: olive 2026, 2,928 stored vs 2,928 live, **36 rows only in
stored and 36 only in live (1.2%)**, with 0 changed `val` among the 2,892 common — the open
season is being re-keyed or re-dated as it runs. Across all 12 probes: **32,340** common
visits, **0** with a changed `val`. Closed seasons behave as immutable over this observation
window.

**NUMBERS — scale drift.** The shipped vine index stores **16** codes; the source serves
**74** for 2025/2026 today. That looks alarming and is not: for `id_survey_var` 39 specifically
both tables yield the **same 4** codes with **identical** ordinals
(782 nessuna→0, 783 bassa→1, 784 media→2, 785 alta→3); **35,064 of 35,064** valued rows decode
identically under both; and re-publishing gives **0 of 10** cells with a different state and
**0 of 10** with a different value, under **both** INCIDENCE and SEVERITY. The 58 extra codes
belong to other variables of schema 8.

The mechanism remains real in principle: `build_scale` assigns
`ordinal = ranks.index(rank)`, so a table that gains a rank **between** two existing ones
renumbers every code above it, and `SEVERITY` is a mean of those ordinals. It does not bite
here because var 39's ladder is closed at four rungs.

**IMPACT: MINOR** for the two certified cases as they stand.

**WHAT SURVIVES.** For closed seasons the archive is a faithful snapshot, and the ordinal
scale for the certified variables is collection-date independent. I attacked this and failed.

**NOT KNOWN:** whether the source ever revises a **closed** season. Twelve probes on one day
cannot establish immutability. What would settle it: record a `COLLECTED_AT` per file and
re-run this comparison at intervals, so a revision is detectable instead of inferred.

---

# LENS 2 — THE DATA CLOCK AND REFRESH

## B1. "The freshness badge lies"

**CLAIM.** `DATA_LATENCY_DAYS` is the only number certifying that a capability named
CURRENT_PRESSURE is current. I established what it is actually made of by corrupting copies,
not by reading the docstring.

**METHOD.** `rt3_e7_latency_provenance.py`. Eight copies of VITE-OIDIO-TOSCANA under
`REDTEAM/_lat/`, each mutated one way, each re-indexed so the sha256 guard does not mask the
experiment. `CASES/` never touched.

**REPRODUCED: YES — in two specific ways, after confirming the docstring's own claim is true.**

**NUMBERS — what it is made of.** Control: latency **2**, 9 of 10 provinces classed.

| mutation | latency | classed |
|---|---|---|
| every file's mtime backdated **5 years** | **2** (unchanged) | 9 of 10 |
| newest year's `val` column nulled (2,515 of 2,515 rows, dates untouched) | 2 → **375** | 0 of 10 |
| newest year's file deleted | 2 → **375** | 0 of 10 |
| newest year's observation dates shifted back 400 days | 2 → **375** | 0 of 10 |
| 50 future-dated rows added | **2** (never negative) | 9 of 10 |

So: latency is `AS_OF` minus the date of the **latest readable value at or before AS_OF**. File
mtime is provably **not** an input. The docstring's claim — measured from the latest readable
value, not the latest date present — **holds**. Good.

**NUMBERS — lie 1: one row resets the badge for a product that publishes nothing.** Backdate
the newest year by 400 days, then add **one single readable row** dated at `AS_OF`, in Arezzo:

> latency **0 days**, and **10 of 10** provinces publish `UNKNOWN_NO_DATA`.

A badge reading "0 days fresh" over a product with zero published cells.

**NUMBERS — lie 2: the badge is region-wide, and attaches to no cell.** Backdate **9 of 10**
provinces by 900 days, leave only Siena current:

> latency **4 days**, **1 of 10** provinces classed.

The single published `DATA_LATENCY_DAYS` is a region-wide *maximum freshness*. A reader who
sees "4 days" beside a Firenze cell is wrong by 900 days. It is computed once over all rows of
all provinces (`current_pressure.py:259-260`), never per province, and the per-province record
carries no latency field of its own.

**NUMBERS — lie 3: `AS_OF` is a free input and there is no `COLLECTED_AT`.** An archive frozen
on disk reports latency 2 whenever the caller passes the matching `AS_OF`. Nothing in the
system can contradict that (see B5).

**IMPACT: MAJOR.**

**WHAT SURVIVES.** The one thing the docstring promised — immunity to an all-empty measurement
column faking a 2-day-fresh source — is real and I confirmed it: nulling 2,515 of 2,515 values
moves the badge from 2 to 375 days. That specific past defect is genuinely fixed.

---

## B2. "Gate H's freshness certification is pinned to a frozen date"

**CLAIM.** `gates.evaluate(as_of=dt.date(2026, 9, 6))`. Gate H requires
`DATA_LATENCY_DAYS <= 21`. What happens as real time passes?

**METHOD.** `rt3_e7_latency_provenance.py` (`AS_OF_SWEEP_ARCHIVE_FROZEN`) sweeps the predicate;
`rt3_e8_gates_time.py` drives the **real** `gates.evaluate` at the default and at +30 days.

**REPRODUCED: YES.**

**NUMBERS — the predicate, archive frozen at the state certified today.**

| AS_OF | latency | `latency <= 21` | provinces classed |
|---|---|---|---|
| +0d (2026-09-06) | 2 | **True** | 9 of 10 |
| +7d | 6 | True | 9 of 10 |
| +21d | 20 | True | **3 of 10** |
| +22d | 21 | True | **1 of 10** |
| +30d | 29 | **False** | 0 of 10 |
| +60d | 59 | False | 0 of 10 |
| +180d | 179 | False | 0 of 10 |
| +365d | 364 | False | 0 of 10 |
| +730d | 729 | False | 0 of 10 |

**NUMBERS — the real `gates.evaluate`, run end to end at `AS_OF + 30d`** (`rt3_e8_gates_time.py`):

| | PASS | FAIL | NOT_TESTABLE | gate H | latency per case |
|---|---|---|---|---|---|
| default `AS_OF` 2026-09-06 | 8 | 2 | 0 | **PASS** | olive **2**, vine **2** |
| `AS_OF` 2026-10-06 (+30d) | 6 | 3 | 1 | **FAIL** | olive **32**, vine **29** |

Three findings, and they point in opposite directions, so all three are stated.

1. **The predicate does work.** Given a later `AS_OF`, gate H goes red at +30 days. It is not
   frozen-true by construction.
2. **Nobody will give it a later `AS_OF`.** `gates.evaluate()` called with no argument — which
   is how `gates.py.__main__` calls it, `ENGINE/gates.py:278` — uses the hardcoded literal and
   will report `latency = 2` in 2027, in 2030, forever. The certification does not expire; it
   has to be manually re-aimed at the present, and nothing in the repository does that.
3. **It certifies "fresh" over an almost-empty product.** At +21d the predicate is still True
   with **3 of 10** provinces classed; at +22d still True with **1 of 10**. Latency and
   publishability are decoupled, so "the data is current" can be certified while 90% of the
   product is UNKNOWN.

**IMPACT: MAJOR.**

**WHAT SURVIVES.** The threshold is real, measured, and reads a number that genuinely tracks
observation recency. Before this gate existed, no gate read `DATA_LATENCY_DAYS` at all.

---

## B3. "A refresh that fails silently disables the hash chain, or takes the case down"

**CLAIM.** `CASES/collect_generic.py` is the refresh path. I drove it with a patched
`urllib.request.urlopen` under four scenarios and then asked `load_rows()` what it believes.

**METHOD.** `rt3_e6_refresh_lab.py`. Byte copies of VITE-OIDIO-TOSCANA under `REDTEAM/_lab/`;
the **shipped** `collect_generic.py` is executed against each copy via `runpy` with the network
replaced. `CASES/` never touched.

**REPRODUCED: YES.**

**Baseline (untouched copy):** 40 files, **40 of 40** hash-verified, last readable observation
2026-09-07, latency 2, **9 of 10** classed.

| scenario | index | hash chain | `load_rows` | published |
|---|---|---|---|---|
| **A GOOD** — source replays exactly the archived rows, 2006-2026 | 21 requests, 20 with file | 19 verified, **1 MISMATCH**, 20 unchecked | **RAISES** `REFUSED: c3_s8_v39_2012.json does not match its collected sha256` | **nothing — capability down** |
| **B NULLS** — HTTP 200, `ok:true`, full rowCount, every `val` null | 21 requests, **0** with file, **20 `REFUSED_WRITE`** | **0 verified, 40 of 40 unchecked** | OK, last obs 2026-09-07 | latency **2**, **9 of 10** classed — *identical to healthy* |
| **C DOWN** — `urlopen` raises | 21 requests, all `ok:false`, `codes:null`, `vars:null` | 0 verified, 40 unchecked | **RAISES** `REFUSED: var 39 is neither coded nor numeric in the source metadata` | **nothing — capability down** |
| **D PARTIAL** — good refresh of the last 2 years (the normal operator action) | 2 requests, 2 with file | 2 verified, **38 of 40 unchecked** | OK | latency 2, 9 of 10 classed |

**Four separate defects, each with its own consequence.**

1. **The null-response guard works, and hides its own success.** In B the collector correctly
   refused all 20 writes and printed `REFUSED to write var 39 <year>: N rows, 0 readable
   values`. The last good observation **survived**. But the product a consumer sees is
   **byte-identical** to a healthy one — same latency 2, same 9 classed cells — and the only
   record that the source went dark is a `REFUSED_WRITE` key in an index with **no timestamp**.
   Standing in front of the output, you cannot tell that the source has been dead for a month.
2. **Any refresh that does not re-request every file silently disables the hash chain.**
   `load_rows` skips verification when a file is absent from the index —
   `if by_file.get(base) and by_file[base] != h:` (`current_pressure.py:115`). Missing key →
   `None` → falsy → **no check**. Measured: **40 of 40** unchecked after a null refresh,
   **38 of 40** unchecked after an ordinary partial refresh. The chain degrades quietly
   instead of refusing.
3. **A transient outage destroys the case's decoding metadata.**
   `collect_generic.py:72` rewrites `collection_index.json` unconditionally at the end,
   including `codes` and `vars`, even when **21 of 21** requests failed. Every raw observation
   file is intact on disk and the capability is still down, because the scale is gone. Not
   recoverable without a successful re-collection.
4. **A perfectly successful refresh kills the case on this machine.** Scenario A — see B4.

**IMPACT: MAJOR.** Note that three of the four failures are **loud** (a raised `REFUSED`), which
is the design philosophy working. The dangerous one is B, which is silent by construction:
the correct refusal to write is indistinguishable downstream from a healthy day.

**WHAT SURVIVES.** The `FULL_ROWCOUNT_BUT_EVERY_VALUE_NULL` detector fires exactly as
advertised — 20 of 20 refusals — and the last good observation is never overwritten by a null
response. That defence is real.

---

## B4. "The write encoding and the hash encoding disagree"

**CLAIM.** `collect_generic.py` lines 67–68:

```python
open(os.path.join(raw, fn), "w").write(blob)                  # locale encoding
rec["sha256"] = hashlib.sha256(blob.encode()).hexdigest()     # UTF-8, always
```

`open(..., "w")` with no `encoding=` uses `locale.getpreferredencoding(False)`. On this machine
that is **cp1252**. The bytes written and the bytes hashed then differ for any non-ASCII
character.

**METHOD.** `rt3_e5_encoding.py` (census + end-to-end reproduction), plus scenario A of
`rt3_e6_refresh_lab.py` (the live consequence).

**REPRODUCED: YES.**

**NUMBERS — the disagreement.** Writing a real 3-row sample taken from
`OLIVO-BACTROCERA-TOSCANA/RAW/c2_s1_v-1001_2020.json`:

- bytes on disk **1,112**; bytes hashed **1,118**
- recorded sha256 `f90920…052f`; sha256 of the file on disk `f7488b…a296` — **disagree**
- the written file **no longer parses as UTF-8**: `'utf-8' codec can't decode byte 0x92`

Per-character: `à` is `e0` in cp1252 and `c3a0` in UTF-8; `’` is `92` vs `e28099`; `ì` `ec` vs
`c3ac`. Every accented Italian character differs. `č` cannot be encoded in cp1252 at all — this
script's own `print` crashed on it, which is the same failure one layer up.

**NUMBERS — how much of the real archive is exposed.** **458 of 392,951** rows (**0.117%**) in
**22 of 138** RAW files contain non-ASCII: olive 448 of 317,004 in 20 of 84 files; vine 10 of
70,130 in 2 of 40 files; wheat **0** of 5,817 in 0 of 14 files. Characters seen: `’` x248,
`à` x210. The three `collection_index.json` files contain **0** non-ASCII characters.

**NUMBERS — the live consequence.** Scenario A of the refresh lab: the source replays exactly
what is already archived — the most successful refresh imaginable — and afterwards

> `load_rows` raises `ValueError: REFUSED: c3_s8_v39_2012.json does not match its collected
> sha256`

**1 of 20** rewritten files mismatched, and one mismatch takes the whole case down because the
check is inside the file loop. The capability is destroyed by a refresh that changed nothing.

**Three qualifications, all in the code's favour.**

1. **No published number is affected today.** All 458 non-ASCII rows carry it in exactly one
   field, `name` (a free-text field label the engine never reads). `nome_area`, `date`, `val`
   and `id_field` are pure ASCII in **every** row of **every** file. Reading the shipped
   archives on this cp1252 machine mangles 458 of 392,951 rows in a field nobody uses; the ten
   province keys come back clean and the current output is unchanged.
2. **It fails loud.** A hard `REFUSED`, not a wrong number.
3. **It is machine-dependent.** The shipped files are genuinely UTF-8 on disk (bytes
   `e2 80 99` for `’`), and `gates.py:241` points at `/home/user/…`, so they were collected on
   a UTF-8 host where the bug is dormant. It arms itself the moment anyone refreshes on
   Windows.

**Why this was not found before:** the previous CERT-V2 refresh lab (`CERT-V2/p6_refresh_and_clock.py`)
exercised FRUMENTO — the one case with **0 of 5,817** non-ASCII rows. The bug was invisible to
it by luck of case selection.

**A related fact from the same census.** The shipped indexes' request objects carry exactly
`file, n_rows, ok, rowCount, sha256, var, year` — they have **no** `non_null_values` and no
`REFUSED_WRITE` key, both of which the current collector always writes. **The archives being
certified were not produced by the collector being certified.**

**IMPACT: MAJOR.**

**WHAT SURVIVES.** The sha256 chain does its job: it caught the corruption immediately and
refused rather than serving mangled data. The defect is in the writer, not the verifier.

---

## B5. "Nothing records when a refresh was attempted, or when the data was collected"

**CLAIM.** Is there any field anywhere recording `REFRESH_ATTEMPT_AT`, `REFRESH_STATUS`,
`LAST_GOOD_OBSERVATION_AT`, `SOURCE_PUBLISHED_AT` or `COLLECTED_AT`?

**METHOD.** Name search across `ENGINE/`, `CASES/` and every produced artifact; plus the key
inventory printed by `rt3_e6_refresh_lab.py` for every scenario.

**REPRODUCED: YES — proven ABSENT.**

**NUMBERS.**
- All five names: **0** occurrences in `ENGINE/`, **0** in `CASES/`, **0** in any case
  artifact. They occur only inside CERT-V2's own prior red-team files
  (`p6_refresh_and_clock.py/.json`, `p14_artifact_inventory.py/.json`) — that is, only in
  documents *reporting their absence*.
- The three shipped `collection_index.json` top-level keys are exactly
  `api, codes, crop, requests, schema, vars` (plus `DENOMINATOR_VAR` for olive). Request keys
  are exactly `file, n_rows, ok, rowCount, sha256, var, year`. **No timestamp of any kind**, at
  either level, in any of the three.
- `HAS_ANY_TIMESTAMP_FIELD` was empty in **5 of 5** refresh-lab audits (baseline + four
  scenarios).
- **0** hits for `getmtime`, `st_mtime`, `os.stat` in `ENGINE/` and `CASES/` — so file mtime is
  not used as a fallback either, which B1 confirmed experimentally.

**Consequence, stated concretely.** Given an output that says `DATA_LATENCY_DAYS: 2`, there is
no artifact in the repository that can answer: *when was this archive fetched?*, *was a refresh
attempted since?*, *did it fail?*, *when did the source last publish?* The badge describes the
distance between a chosen `AS_OF` and an observation date. It says nothing about the pipeline
being alive. Scenario B of the refresh lab is exactly this gap made concrete: source dead,
badge reading 2 days, product unchanged.

**IMPACT: MAJOR.**

**WHAT SURVIVES.** `ok`, `rowCount`, `n_rows`, `non_null_values` and `REFUSED_WRITE` do record
the *shape* of the last refresh outcome per request. What is missing is exclusively the
**time** axis — and one `REFRESH_ATTEMPT_AT` plus `REFRESH_STATUS` per request, written even
when the request fails, would close B3.1, B3.3 and most of B5 at once.

---

# WHAT I COULD NOT BREAK

Stated as plainly as the accusations, because these are the load-bearing parts.

1. **`AS_OF` is genuinely an input, never the clock.** Three independent methods agree:
   3 clock calls exist in 10 files and all 3 are an elapsed-seconds probe field that no gate
   reads; the full publication path (`load_rows`, `current_pressure`, `hindcast`,
   `sensitivity`) completes **4 of 4** stages with `date.today`, `datetime.now`,
   `datetime.utcnow`, `datetime.today`, `time.time` and `time.localtime` all armed to raise;
   and three system clocks 100 years apart give **1 distinct output**, byte-identical.
   I could not find a path. I do not believe one exists.

2. **The walk-forward does not leak at the row level.** **0 of 21** olive seasons and
   **0 of 20** vine seasons leak. In all 41 runs the current window consumed only its own
   calendar year with max date `<= AS_OF`, and no baseline consumed a year at or after the
   season it serves. This is the claim most systems of this shape get wrong, and this one
   gets it right.

3. **Latency is measured from the last readable value, exactly as documented.** Nulling
   2,515 of 2,515 values in the newest year moves the badge from 2 days to 375 and drops all
   10 provinces to UNKNOWN. The specific defect that docstring was written to close is closed.

4. **The silent-failure detector fires.** HTTP 200 with `ok:true`, full rowCount and every
   value null produced **20 of 20** write refusals and the last good observation survived
   intact.

5. **Closed seasons are immutable and the ordinal scale is collection-date independent**, over
   the observation I was able to make: **11 of 12** season probes byte-identical, **0** changed
   `val` in 30,315 common visits; and although the schema code table grew 16 → 74, var 39's
   ladder is the same 4 codes with the same ordinals, **35,064 of 35,064** rows decoding
   identically and **0 of 10** cells changing under either metric.

6. **The sha256 chain catches real corruption.** It is what detected B4, and it refused rather
   than serving mangled data. The failure is in the writer's encoding, never in the verifier.

7. **Everything that fails, except one case, fails loud.** Of the four refresh scenarios,
   three end in a raised `REFUSED` and one ends in a correct refusal to write. The single
   silent path is scenario B's *downstream appearance*, not its handling.

---

# NOT KNOWN

- **Whether the source ever revises a closed season.** Twelve probes on one day cannot
  establish immutability. *Settled by:* a `COLLECTED_AT` per file plus a scheduled re-comparison,
  so a revision becomes detectable rather than inferred.
- **Whether the year-boundary defect (A2) would ever be reached by a real deployed case.**
  It is unreachable in all three archives (7 Dec/Jan rows of 120,133, 0 readable) and fully
  reachable in a plausible synthetic one. *Settled by:* running the engine against one real
  winter-monitored crop x issue.
- **Whether any consumer of the output reads `DATA_LATENCY_DAYS` per province.** There is only
  a region-wide value to read. *Settled by:* inspecting the consuming UI, which is out of scope
  for this lens.
- **Why gate G FAILs at every `AS_OF` I tested** (default, +30d, and with the cutoff removed —
  3 of 3 runs). It is a real FAIL in the shipped `ENGINE/gates.json` too, so it is not something
  I introduced, but discrimination between seasons is outside this lens and I did not
  investigate it. *Settled by:* the discrimination/effect-size lens.
- **Whether the 36 re-keyed rows in olive 2026 (A6) are corrections or re-pivots.** `val` is
  unchanged on every common visit, so no measurement moved; the visit identity did.
  *Settled by:* asking the source what `id_survey` means for an open season.

---

# THE THREE THINGS I WOULD FIX FIRST

Ordered by damage per line of code, not by severity label.

1. **`collect_generic.py:67`** — `open(path, "w", encoding="utf-8")`. One keyword argument.
   It is the difference between a refresh that works on any machine and a refresh that
   destroys the case on Windows.
2. **`collect_generic.py:72`** — do not overwrite `codes`/`vars` when the requests that would
   populate them all failed, and add `REFRESH_ATTEMPT_AT` + `REFRESH_STATUS` per request,
   written even on failure. Closes B3.1, B3.3 and most of B5.
3. **`gates.py` gate B** — the predicate must compare two runs at the **same** `AS_OF` that
   differ **only** in the upper bound. As written it compares two different windows and
   attributes the difference to the cutoff; measured, **0 of 20** cells are attributable to
   the cutoff and **18 of 18** to the window sliding, and the gate returns PASS with the
   cutoff removed.
