# RT4 — DETERMINISM AND REPRODUCIBILITY

Independent red team. I wrote none of this code. My brief was to make the same bytes produce
two different answers, or to show that a published result cannot be reproduced from the
repository.

## Bench

| | |
|---|---|
| host | Windows 11 Pro 10.0.22000, NTFS, Git Bash |
| interpreter | Python 3.12.10 (tags/v3.12.10:0cc8128) [MSC v.1943 64 bit (AMD64)] |
| worktree | `C:/di-observational-v1`, branch `claude/disease-intelligence-observational-v1` |
| fresh clone A | `C:/rt4-fresh/clone8efec08` — pinned at **8efec08**, the commit whose `tests/t1_determinism.json` publishes the hash |
| fresh clone B | `C:/rt4-fresh/clone` — pinned at **b05b6cf**, HEAD while I worked |
| tamper shadow | `C:/rt4-fresh/tamper` — a copy of the 84 RAW files, **outside the repository**. `CASES/` was never written to |
| scripts | `REDTEAM/rt4_01_repro.py` … `rt4_11b.py`, plus `rt4_02_env_sweep.sh` and `SWEEP-RESULTS/` |

**Note on a moving target.** I started against commit `8efec08`. At 21:06, mid-audit, `HEAD`
advanced to `b05b6cf` and `engine/di_core.py` changed under me (commit `95c90ce`, per-measurement
validity). The working tree kept changing afterwards — files such as `engine/_patch_v2.py`,
`S1-SEMANTICS/s2_correct_sheet.py` and `tests/t4_independent_reproduction.py` appeared while I
worked. This is not an aside: it produced accusation A1.

Because of it, **every number in this report was taken in a pinned fresh clone**, not in the
working tree, and each accusation names its commit. The only things I read from the working tree
are the committed artifacts, via `git show`. I wrote nothing outside `REDTEAM/`; `engine/`,
`CASES/`, `S1-SEMANTICS/`, `tests/`, `OUT/` and `italia-portale/` were not modified by me. (The
one exception: I deleted six `*.opt-2.pyc` files from the gitignored `engine/__pycache__/` that
my own `PYTHONOPTIMIZE=2` run had created there, restoring it to its prior contents.)

---

## A1 — THE DETERMINISM RECEIPT DOES NOT NAME THE CODE IT CERTIFIES

**CLAIM ATTACKED.** "Same bytes, same result," evidenced by
`sha256 61ac20d6b5be53707ccc7261e4d0091d4ef72ed91ac4e6d78cd9b6db043546d8`.

**METHOD.** `rt4_01_repro.py` — my own payload builder, written from the stated definition, not
copied from `t1_determinism.py`. Run in fresh clone A (8efec08) and fresh clone B (b05b6cf),
same 84 data files, same as_of, same metrics.

**REPRODUCED: NO** (the hash does not survive the repository's own next commit).

**NUMBERS.**

| engine commit | data bytes | hash produced |
|---|---|---|
| 8efec08 | identical, 84 of 84 files byte-identical | `61ac20d6…3546d8` ✅ matches the published hash |
| b05b6cf | identical, 84 of 84 files byte-identical | `e21711b959ed647d65834326c2f21fce4f138885de458bbf7c06e435f77c60b3` |

`n_visits` 79,251 in both. Visits usable moved 75,600 → 75,683 (a definition change, not a data
change). `tests/t1_determinism.json` contains **0 fields** naming a commit, a code hash, an
interpreter version or a sheet version — I searched for `commit`, `git`, `SHEET_VERSION`,
`python`: none present (`rt4_06_provenance.json` → `C_COMPLETENESS`).

**IMPACT: MAJOR.** A reader who runs the test today gets a different hash and has no way to tell
whether determinism broke or the code moved. The receipt certifies nothing it can be checked
against.

**WHAT SURVIVES.** The *property* is real. At the pinned commit the hash reproduces exactly,
from a fresh clone, in a different directory, on source bytes that are not even identical (see
A7). The defect is in the receipt, not in the engine.

---

## A2 — THE COMMITTED REPORT CANNOT BE REGENERATED AT ITS OWN COMMIT

**CLAIM ATTACKED.** That the published answer is reproducible from the repository.

**METHOD.** Fresh clone B at `b05b6cf`. Ran the documented command verbatim:
`py engine/di_report.py 2026-09-06 ACTIVE_INFESTATION_COUNT`. Diffed the result leaf by leaf
against `git show HEAD:…/OUT/report_ACTIVE_INFESTATION_COUNT_2026-09-06.json`
(`rt4_05_freshclone_diff.py`, no sampling — every leaf).

**REPRODUCED: NO.**

**NUMBERS.**

- 3,690 leaves committed, 3,700 leaves regenerated.
- **55 of the 3,687 shared leaves carry a different value.**
- 3 leaves present only in the committed file; 13 present only in the regenerated file (the
  schema itself changed: `n_visits_usable_for_rates` → `n_visits_usable_by_measurement`).
- **7 of the 10 province cells** have at least one changed number: Firenze, Grosseto, Livorno,
  Lucca, Massa-Carrara, Pisa, Siena.
- Largest move on a rate: **Massa-Carrara baseline 2014, 3.1842 % → 4.7538 %, +1.5696 percentage
  points.**
- A published *sentence* changed, not only a field:
  `observed_trend_reason` for Grosseto, `0.5876% -> 0.8249% -> 0.6575%` became
  `0.5876% -> 0.8374% -> 0.6575%`.
- `baseline_rate_pct_max` changed for Grosseto (6.1228 → 6.1174) and Lucca (16.6792 → 16.6481).

**IMPACT: MAJOR.** The repository ships an answer its own current code does not produce, and the
artifact carries nothing that would let a reader detect it.

**WHAT SURVIVES.** No *verdict* flipped, checked field by field over all 10 cells:
`observation.value_pct`, `observation.infested_drupes`, `observation.drupes_sampled`,
`observation.n_visits`, `observation.source_band`, `analysis.historical_state`,
`analysis.historical_state_matched`, `analysis.historical_state_unmatched`,
`analysis.observed_trend`, `attention.attention_class`, `adama.relevance`,
`quality.observation_publishable`, `quality.historical_comparison_publishable` — **0 of these 13
fields differ in any of the 10 cells.** All 55 changed leaves sit in `baseline_detail`,
`matched_panel_comparisons`, `observed_trend_points` (prior windows, not the current one),
`panel_overlap_with_baseline_seasons`, `baseline_rate_pct_max`, or the two
`observed_trend_reason` sentences that quote those prior windows. The headline observation for
every province is unchanged.

---

## A3 — THE PYTHONHASHSEED EVIDENCE POINTS AT A FILE THAT WAS NEVER COMMITTED

**CLAIM ATTACKED.** "5 PYTHONHASHSEED values in separate processes."

**METHOD.** `git log --all --diff-filter=A --name-only` over the whole repository history for
`t1_determinism.sh`; `git ls-tree -r HEAD` over the experiment directory.

**REPRODUCED: NO — the stated evidence does not exist.**

**NUMBERS.** `t1_determinism.py` line 17 says the hash seed is *"driven by t1_determinism.sh"*.
`t1_determinism.json` field `B_HASH_SEED` says *"varied across processes by t1_determinism.sh;
see its output"*. `t1_determinism.sh` appears in **0 of the repository's commits**, on any
branch. Its output appears in **0 files**. `t1b_hashseed.py` exists and would do the job, but has
no runner and no recorded result. The number 5 appears nowhere.

**IMPACT: MAJOR** as evidence. The single most important environment variable in the claim is
backed by a missing artifact.

**WHAT SURVIVES.** I tested the property myself and it holds — see "What I could not break".

---

## A4 — 8 UNHASHED INPUTS, INCLUDING THE SEMANTIC SHEET

**CLAIM ATTACKED.** "Every input file is hashed and the hash matches disk."

**METHOD.** `rt4_06_provenance.py` — coverage, agreement and completeness kept apart.
`rt4_07_tamper.py` / `rt4_08_boundary_and_bands.py` for the demonstration.

**REPRODUCED: PARTLY.** Coverage and agreement hold exactly; completeness does not.

**NUMBERS.**

- Coverage: **84 of 84** RAW files carry a published sha256. Exactly **21 per variable × 4
  variables**. `raw_files_on_disk_with_NO_published_hash`: **0**. The four globs match **84 of the
  84** files present; **0** files in `RAW/` are never matched.
- Agreement: **0 mismatches in 84**, **0 published files absent from disk**.
- Completeness: **8 inputs the answer demonstrably depends on carry no hash anywhere in the
  artifact** —
  `S1-SEMANTICS/SOURCE-SEMANTIC-SHEET.json`, `engine/di_core.py`, `engine/di_observe.py`,
  `engine/di_adama.py`, `engine/di_render.py`, `engine/di_report.py`,
  `italia-portale/client/italy-label-verdicts.js`,
  `italia-portale/client/italy-handoff-v21.js`.
- Demonstration that the sheet is load-bearing: moving **one number** in
  `SOURCE_ACTION_BANDS` (green upper edge 6 → 0.05) repaints Firenze's published band from
  **`0-6%` green to `7-9%` yellow** at the real published rate of 0.0664 %. Nothing objects; no
  receipt in the artifact would show it.
- The ADAMA verdict (`NO`, printed in every one of the 10 cells, with counts quoted from a
  5,919,126-byte JS file) rests entirely on two unhashed files.

**IMPACT: MAJOR.** The 84-file claim is honest and exact for the RAW data. It is not the whole
input.

**WHAT SURVIVES.** The previous engine's failure — hashing only the outcome variable and leaving
half its inputs unverified — is **not** repeated. All four variables are hashed, including the
denominator. That is a real repair.

---

## A5 — THE HASH CHECK IS CIRCULAR: NOTHING IS EVER VERIFIED

**CLAIM ATTACKED.** "The hash matches disk."

**METHOD.** Grepped every `sha256` line in `engine/*.py` for a comparison. Then tampered for
real: `rt4_07_tamper.py` on the shadow copy outside the repository.

**REPRODUCED: NO — there is no verification step to reproduce.**

**NUMBERS.**

- Lines in the reader (`di_core`, `di_observe`, `di_adama`, `di_render`, `di_report`) that compare
  a sha256 against a stored expectation: **0**. The engine computes the hash *from the same disk
  it reads*, so agreement is guaranteed by construction. (`di_refresh.py` line 126 does compare
  `new_hash == prev_hash`, but that is the collector deciding whether to promote a fetch, not the
  reader verifying the archive.)
- Tamper T1 — changed **one** `val` in **one** of 84 files, from `2.0` to `99`, on visit
  `(id_field 5121, 2026-09-01)`, inside the published 28-day window:
  - Firenze published rate **0.0664 % → 0.4689 %** (+0.4025 pp)
  - `infested_drupes` **16 → 113** over the same 24,100 sampled
  - **`historical_state` flipped `BELOW_HISTORICAL` → `TYPICAL`**
  - engine raised nothing, warned nothing
  - the recorded hash for that file did change (`0320dac2…` → `0cb3c934…`)

**IMPACT: MAJOR.** One edited number in one of 84 files silently flips a published verdict. It is
detectable only by a human diffing today's receipt against a previous one — the tool performs no
such check.

**WHAT SURVIVES.** The recorded hash *does* move with the bytes, so an external verifier holding
a prior manifest would catch it. The material for a check exists; the check does not.

---

## A6 — `int()` ON A FLOAT SUM: A PUBLISHED COUNT THAT MOVES WITH SUMMATION ORDER

**CLAIM ATTACKED.** That the pooled rate and its counts are invariant to the order visits are
summed in.

**METHOD.** `rt4_04_float_order.py`. This is a different experiment from the tool's: the tool
permutes **file** order, which the loader re-sorts away (see E1). I permute **the addends
themselves**, which nothing re-sorts — as published, reversed, sorted ascending by value, sorted
descending, and two fixed shuffles — across every province × metric × window the report builds.

**REPRODUCED: YES — one window breaks.**

**NUMBERS.**

- Non-integer numerator values in the archive: **975 of 234,063** read. Non-integer denominators:
  **0 of 79,251**. So float addition is *not* exact here and order can matter.
- Windows tested: **669**.
- Windows where any of the 6 orders changed the exact float sum: **36 of 669**.
- Windows where a **published** number moved: **1 of 669** —

  `TOTAL_INFESTATION_COUNT`, **Grosseto**, the **current** window, 319 addends:

  | order | float sum | published `infested_drupes` | published `rate_pct` |
  |---|---|---|---|
  | as published / reversed / asc / shuffle a / shuffle b | `690.0` | **690** | 1.9931 |
  | sorted descending by value | `689.9999999999999` | **689** | 1.9931 |

  Cause: `di_observe.pooled` line 87 does `int(num)`, which **truncates**. A sum one ULP below an
  integer loses a whole drupe.
- Same cause, and it reaches the published report today (`rt4_12_int_truncation.py`, pinned at
  8efec08). Of the **30** province × metric cells in the current window `2026-08-10 … 2026-09-06`,
  **4 publish an `infested_drupes` that is a truncated fraction**:

  | metric | province | float numerator | published count | lost | published rate |
  |---|---|---|---|---|---|
  | ACTIVE | Grosseto | 228.3 | **228** | 0.3 | 0.6575 % |
  | ACTIVE | Pisa | 93.8 | **93** | 0.8 | 1.0200 % |
  | DAMAGING | Pisa | 9.9 | **9** | 0.9 | 0.1077 % |
  | TOTAL | Massa-Carrara | 213.2 | **213** | 0.2 | 4.0226 % |

  The two ACTIVE rows are in the committed report. So the sentence a human reads — *"228 de
  34720 azeitonas dissecadas"* — and the rate printed one line above it are computed from
  different numerators. For Pisa DAMAGING the printed count is 9 % below the number the printed
  rate is built on.

**IMPACT: MAJOR.** A published integer count is decided by floating-point truncation, not by the
data. `round()` instead of `int()` removes it entirely.

**WHAT SURVIVES.** **0 of 669** windows changed their published `rate_pct` under any of the 6
orders. The rate — the headline number — is order-stable across the whole archive.

---

## A7 — THE ENGINE AND THE SEMANTIC SHEET DO NOT COME OUT OF GIT AS THEY WENT IN

**CLAIM ATTACKED.** That a hash taken in the working tree would reproduce from the repository.

**METHOD.** In fresh clone B, compared each file's **git blob** (`git show b05b6cf:<path>`)
against the **bytes the checkout put on disk**. No dirty worktree involved, so this is
reproducible from the commit alone. Read `.gitattributes`.

**REPRODUCED: NO — the bytes differ, for every code and sheet file.**

**NUMBERS.** Commit `b05b6cf`, fresh clone:

| file | git blob | on disk after checkout | delta | CRLF pairs on disk |
|---|---|---|---|---|
| `engine/di_core.py` | 10,446 | 10,671 | +225 | 225 |
| `engine/di_observe.py` | 15,259 | 15,548 | +289 | 289 |
| `engine/di_report.py` | 2,490 | 2,539 | +49 | 49 |
| `engine/di_render.py` | 5,844 | 5,967 | +123 | 123 |
| `engine/di_adama.py` | 7,628 | 7,776 | +148 | 148 |
| `S1-SEMANTICS/SOURCE-SEMANTIC-SHEET.json` | 9,039 | 9,189 | +150 | 150 |

The delta equals the CRLF count exactly in **6 of 6** files. `core.autocrlf` is on in this
environment (stated in `.gitattributes` itself). `.gitattributes` protects
`italia-portale/BASELINE/**` and `italia-portale/client/**` with `-text`; it protects neither the
engine nor the sheet.

The working tree is additionally inconsistent with itself: at the same commit, 2 of the 6 files
were on disk with CRLF and 4 with LF (rewritten after checkout), and `git status` reports the
tree clean either way, because git normalises on compare.

**IMPACT: MINOR today, blocking for the fix to A1/A4.** No number changes: `json.load` and
Python's universal newlines both ignore it. But the moment the sheet or the code is hashed —
which A4 requires — the hash taken in a working tree will not reproduce in a fresh clone.

**WHAT SURVIVES.** **0 of 84 RAW data files differ** between the git blob and the checkout, and
**0 of 84** differ between worktree and fresh clone. The data that feeds the numbers is
byte-stable through git — the RAW files are single-line JSON with no newlines to convert — and
the two ADAMA inputs (5,919,126 and 3,282 bytes) are protected by `.gitattributes` and come out
identical. Every published sha256 in the provenance block therefore *does* reproduce from a
fresh clone.

---

## A8 — THE ACTION-BAND TABLE HAS A HOLE, AND THE ARCHIVE LANDS IN IT

**CLAIM ATTACKED.** That the source's own band is always applied to a published rate.

**METHOD.** `rt4_08_boundary_and_bands.py` probes `di_core.band_for` across the interval;
`rt4_09_residual.py` then scores every one of the 669 real windows.

**REPRODUCED: YES.**

**NUMBERS.** The bands are `[0,0]`, `[0.01, 6)`, `[6, 10)`, `[10, ∞)`. A rate strictly between
**0 and 0.01 %** matches no band and `band_for` returns `None`. Probed: `1e-09`, `0.001`,
`0.0018`, `0.005`, `0.0099`, `0.00999999` → all `None`.
`di_render.render_province` line 38 then does `o['source_band']['label']` with no guard — a
`TypeError`, not a missing line.

Reachability is not theoretical: **1 of 669 windows** already lands in the hole —
`DAMAGING_INFESTATION_COUNT`, Grosseto, baseline 2024, 3.6 over 44,649 = **0.0081 %**, band
`None`. One infested drupe over the largest observed window denominator (55,707) gives
0.0018 %, also inside the hole.

**IMPACT: MINOR at this as_of, and it is a crash rather than a wrong number.** `source_band` is
computed only for the **current** window; the hit is in a baseline window, where `band_for` is
not called. Measured at `2026-09-06`: **0 of 10** current-window rates fall in the hole, and the
smallest is Pistoia at **0.0278 %** — 2.8× above the edge. The next province to drop below
0.01 % takes the renderer down.

**WHAT SURVIVES.** The `UNIT_TRAP` reasoning in the sheet is sound and the engine honours it: it
never reads a raw count as a percentage, and it refuses when `tot <= 0`. The hole is an
off-by-one-hundredth in the band table, not a unit error.

---

## A9 — SMALLER MEASURED DEPENDENCIES

| # | finding | numbers | impact |
|---|---|---|---|
| A9a | `glob` is **case-insensitive** on this NTFS filesystem: one file named `c2_s1_V1_2099.json` is matched by the loader's pattern `*_v1_*.json`. On a case-sensitive filesystem it would not be. Same bytes, different platform, different file set (`rt4_10`). **0** such files exist in `CASES` today. | 1 probe file, 2 patterns, both match | MINOR (portability) |
| A9b | The loaded payload is **not invariant to the order the four variables are requested in**: 3 permutations → 3 hashes (`rt4_09` D). Cause: `any_row = next((per_var[c][k]['row'] for c in wanted …))` — the first variable holding the key supplies the visit's date, province, comune, org and week, and nothing checks the four agree. | The difference is **cosmetic**: only the *order* of `exclusion_reasons` in **25 of 79,251** visits. **0** visits differ in date, province, comune, org, week, `usable_for_rates` or any measurement value. Separately: over **79,251 of 79,251** keys the four files **never** disagree about any of those fields (`rt4_10` D2). At HEAD `exclusion_reasons` is `sorted()`, so even this is gone. | MINOR (unguarded assumption that holds) |
| A9c | The printed human report is **not** printable under every console encoding: `PYTHONIOENCODING=ascii` and `cp437` (a common Windows codepage) raise `UnicodeEncodeError` on `infestação` / `última` / `PRÓPRIA`; `cp1252` mangles them. | 2 of 4 encodings tested crash, 1 of 4 corrupts | MINOR (the JSON is written with explicit `encoding="utf-8"` and is unaffected; the rendered *string* hashes identically in all 22 sweep conditions) |
| A9d | A same-key, **same-value** duplicate row is accepted in silence: the guard fires only on a *different* value. Injected one; loader returned 79,251 keys, raised nothing, counted nothing, reported nothing (`rt4_07` T3). | 1 injected, 0 reported | MINOR |
| A9e | On this machine `py` resolves to `C:\actions-runner-2\…\python.exe` but binds a stdlib under `C:\Users\London1\…\Python312\Lib`, and emits `Could not find platform independent libraries <prefix>` on every run. The artifact records **no** interpreter identity. | 1 interpreter registered, 2 stdlib trees observed | MINOR (environmental, but A1's fix should record the interpreter) |

---

# ERRORS IN THE TOOL'S OWN TESTS

**E1 — Condition A ("8 file orders") is a tautology and cannot fail.**
`t1_determinism.py` replaces `di_core.glob.glob` with 8 permuting functions. But
`di_core._read_variable` line 71 reads
`for fn in sorted(glob.glob(pattern)):` — it re-sorts immediately. All 8 conditions read the 84
files in one and the same ascending order. The test cannot distinguish a correct engine from any
other engine that also sorts.

I ran the test the tool could not: `rt4_11_real_file_order.py` shadows `di_core.sorted` so the
sort is genuinely removed, then feeds 6 real orders.
Result: **6 orders → 6 different payload hashes** (only `ascending` reproduces `61ac20d6…`).
`rt4_11b.py` then separates receipt from answer:

| quantity | distinct values over the 6 orders |
|---|---|
| whole payload | **6** |
| every published **number** (payload minus provenance) | **1** |
| provenance file-name set | **1** |
| provenance sha256 set | **1** |

So the sort **is** load-bearing for the artifact's bytes — the provenance `files` list is built in
read order — and is **not** load-bearing for any number. The tool's test proves neither.

**E2 — Condition D ("an injected collision must RAISE") never calls the loader.**
`t1_determinism.py` lines 80–106 define a wrapper `poisoned()` **which is never called**, then
`assert "JoinConflict" in src` (a text grep of the source file), then builds two rows in the test
body, re-implements the guard inline, and raises `di_core.JoinConflict` **itself**. The
`except` clause catches the test's own exception. It proves the test can raise. It proves nothing
about `_read_variable`.

I ran the real thing (`rt4_07_tamper.py` T2): appended a row to
`c2_s1_v-1001_2026.json` in the shadow copy with an existing key `(5995, '2026-07-29')` and value
`7.0` against the original `0.0`, then called `di_core._read_variable`. It raised
`JoinConflict: REFUSED: visit key (5995, '2026-07-29') appears twice in variable -1001 with
different values (0.0 then 7.0)…`. **The guard works. The tool's evidence for it does not.**

**E3 — The determinism test covers 3 of the 6 engine modules.**
`t1_determinism.py` hashes only `di_core.load_visits` + `di_observe.cell`. It never imports
`di_adama`, `di_report` or `di_render`. The ADAMA block, the per-cell provenance block and the
human-readable text — the artifact a person actually reads — are outside the certified surface. I
extended the probe to all three (`rt4_01_repro.py`: `EXT_REPORT_HASH`, `EXT_RENDERED_TEXT_HASH`)
and both are stable across all 22 conditions, so nothing was hiding there — but the tool did not
know that.

**E4 — `B_HASH_SEED` cites an artifact that does not exist.** See A3.

**E5 — `NOT_TESTED_HERE` is incomplete.** It lists two exclusions ("a non-Windows filesystem", "a
non-UTF8 locale for READING"). It does not mention that the code version is unrecorded (A1), that
`di_adama`/`di_render`/`di_report` are untested (E3), that addend order is untested (A6), or that
condition A is neutralised by the loader's own sort (E1).

---

# WHAT I COULD NOT BREAK

Each of these is a claim I attacked and failed to break, with the measurement.

**1. The hash itself, at the commit it was published at.** Fresh clone A (`8efec08`), a directory
the code had never seen, source bytes that differ from the working tree's (A7). My own
independently written payload builder. Result:
`61ac20d6b5be53707ccc7261e4d0091d4ef72ed91ac4e6d78cd9b6db043546d8`. Exact match.

**2. The environment.** 22 separate processes, `rt4_02_env_sweep.sh`, raw outputs in
`REDTEAM/SWEEP-RESULTS/`:

- `PYTHONHASHSEED` = 0, 1, 2, 3, 7, 42, 4294967295, and `random` three times (10 conditions)
- `PYTHONUTF8` on and off; `PYTHONIOENCODING=cp1252`
- `LC_ALL`/`LANG` = `C`, `tr_TR.UTF-8` (the dotted-I locale), `de_DE.UTF-8` with
  `LC_NUMERIC=de_DE.UTF-8` (comma decimal separator)
- `TZ` = `Pacific/Kiritimati` (UTC+14) and `Etc/GMT+12` (UTC−12) — 26 hours apart
- `PYTHONDONTWRITEBYTECODE`, `PYTHONOPTIMIZE=2`, `PYTHONINTMAXSTRDIGITS=640`
- run concurrently in batches of 7, which also races `__pycache__` writes

**Distinct core hashes: 1 of 22. Distinct extended-report hashes: 1 of 22. Distinct
rendered-text hashes: 1 of 22.** `n_visits` 79,251 and `ADAMA_RELEVANCE` `NO` in all 22.

**3. The visit key, verified on the raw bytes without the engine** (`rt4_03_key_uniqueness.py`).
For **each** of the four variables:

| variable | files | rows | rows with a null key | distinct `(id_field, date)` | repeated keys |
|---|---|---|---|---|---|
| 1 `tot` | 21 | 79,251 | 0 | **79,251** | **0** |
| −1001 `attiva` | 21 | 79,251 | 0 | **79,251** | **0** |
| −1002 `dannosa` | 21 | 79,251 | 0 | **79,251** | **0** |
| −1003 `totale` | 21 | 79,251 | 0 | **79,251** | **0** |

The claim is exact. Further: `id_field` is `int` in **79,251 of 79,251** rows and `date` is `str`
in **79,251 of 79,251**, so the loader's sort key `(str(date), str(id_field))` is injective —
**0 collisions in 79,251** — and no set-iteration order can leak into the visit order. This was my
main attack route on `PYTHONHASHSEED` and it is closed by the data.

**4. The collision guard.** It raises on real files with a real injected collision (E2).

**5. Float summation order, on the rate.** 669 windows × 6 orders. **0 of 669** changed their
published `rate_pct`. The two windows that sit **exactly** on a 4-decimal rounding boundary —
Siena ACTIVE baseline 2025 at `549/9600 = 5.71875` and Livorno TOTAL baseline 2020 at
`1798/6400 = 28.09375`, both exact ties in rational arithmetic (`rt4_08` A) — are built from
**0 non-integer addends out of 102 and 64** respectively (`rt4_09` A). Their sums are exact in
binary floating point, so no order can move them by even one ULP, and round-half-to-even settles
them identically on any IEEE-754 platform. The tie risk and the order risk exist; on this archive
they do not intersect. Only `int()` truncation broke (A6).

**6. Hidden state.** I grepped the engine for `open(…,'w'/'a')`, `makedirs`, `shutil`,
`os.remove`, `os.rename`, `pickle`, `shelve`, `sqlite`, `tempfile`, `mkstemp`, `listdir`,
`scandir`, `walk`. The documented command `di_report.py` writes exactly **one** file,
`OUT/report_{metric}_{as_of}.json` (the other entry point, `run_pilot.py`, writes one more,
`OUT/pilot_…json`), and **reads nothing it wrote**. **0** caches, **0** temp files, **0** lock
files, **0** databases. The only `glob` in the whole engine is `di_core.py` line 71, and it is
sorted on the same line.
The only implicit written-and-read state is `engine/__pycache__`, which is CPython's, not the
engine's — and `PYTHONDONTWRITEBYTECODE=1` gives the same hash.

**7. Absolute paths, the clock and the environment.** Grepped for `C:\`, `/home/`, `/tmp/`,
`/Users/`, `D:\`, `os.getcwd`, `getenv`, `environ`, `time.time`, `datetime.now`, `date.today`,
`random.`, `uuid` across `engine/` and `S1-SEMANTICS/*.py`. **4 hits, all 4 in
`engine/di_refresh.py`** (`time.time` for request duration, `datetime.now` for the collection
clock) — the collector, which the reader never calls. The reader path contains **0** absolute
paths, **0** clock reads and **0** environment reads. `as_of` is an argument, never a clock, as
claimed.

**8. Provenance coverage of the RAW data.** 84 of 84 files hashed, 21 per variable × 4, 0
mismatches against disk, 0 files in `RAW/` unmatched by the four globs. The previous engine's
50.1 % gap is genuinely closed for the data.

---

## NOT KNOWN

- Whether the answer holds on a **case-sensitive filesystem** (Linux/macOS). A9a shows the glob
  binds differently there. I could not test it on this host.
- Whether the answer holds on a **different Python minor version** (3.11, 3.13) or a different
  libm. Only 3.12.10 is installed here. The exact-tie windows (point 5) are exactly representable
  and should be safe; the 35 windows whose float sums already move with order are not proved safe
  across libms — the published rate survived 6 orders on *this* libm only.
- Whether `t1_determinism.sh` ever existed outside git. It is absent from every commit; I cannot
  say whether it was run and discarded, or never written.
- What the correct value of Grosseto TOTAL `infested_drupes` is — 689 or 690. The exact rational
  sum of 319 addends would settle it; the float sum does not.
