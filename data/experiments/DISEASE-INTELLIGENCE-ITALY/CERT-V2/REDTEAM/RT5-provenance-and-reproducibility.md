# RT5 — PROVENANCE AND REPRODUCIBILITY

Independent red team. I did not write ENGINE/, CASES/ or CERT-V2/. I attacked both.
Nothing in ENGINE/, CASES/ or italia-portale/ was modified. Nothing was committed or pushed.
Every script named below is mine, written from scratch, under `CERT-V2/REDTEAM/rt5_*`.
I did not import or re-run any CERT-V2 script to produce a number in this report; I read them
only to check what they claimed.

Machine: Windows 11, Python 3.12, `core.autocrlf=true`. Repo `C:/cert-v2-disease-pressure`,
branch `claude/disease-pressure-certification-v2`, HEAD `61041f9` when I started. ENGINE/ and
CASES/ are byte-identical between `a4d19dd` (the commit the certification measures) and
`61041f9` — `git diff --name-status a4d19dd 61041f9` lists CERT-V2 files only. The
certification author committed three further times while I worked (through `54ff58c`);
`git diff --name-status 61041f9 54ff58c -- ENGINE CASES` is **empty**, and `ENGINE/gates.json`
at `54ff58c` is byte-identical to the copy I compared against (sha256 `4f186450088773de…`),
so every finding below holds against the current HEAD unchanged.

---

## 0. THE DECISIVE EXPERIMENT — A GENUINELY FRESH CLONE

**METHOD** `git clone --single-branch --branch claude/disease-pressure-certification-v2
C:/disease-local-collection-italy C:/rt5-clean-clone`, then `cd
data/experiments/DISEASE-INTELLIGENCE-ITALY/ENGINE && py gates.py`. New directory, new
checkout, no reuse of the worktree. Outputs preserved as
`REDTEAM/rt5_p0_gates_clean_clone.json` and `rt5_p0_gates_clean_clone_stdout.txt`;
the committed file as `rt5_p0_gates_committed.json`.

**REPRODUCED: NO.** 8 of 28 leaf fields differ.

| field | committed `ENGINE/gates.json` | clean clone |
|---|---|---|
| `GATES.C_REGIONAL_NOT_NATIONAL.EVIDENCE` (disagreeing season-cells) | **19** | **18** |
| `GATES.F_LABEL_NOT_PARAMETER_ARTEFACT.EVIDENCE` (olive stability) | **0.918** | **0.924** |
| `GATES.G_DISCRIMINATES_BETWEEN_SEASONS.EVIDENCE` (olive dominant share) | **0.424** | **0.432** |
| `GATES.J_NOT_DUPLICATE.VERDICT` | `NOT_TESTABLE` | **`FAIL`** |
| `GATES.J_NOT_DUPLICATE.ANSWER` | `PARTIALLY_OVERLAPS` | **`FAIL`** |
| `GATES.J_NOT_DUPLICATE.EVIDENCE` | 17 of 43 cases, 3 vine × Toscana, 0 olive targets | **"inventory not readable"** |
| `FAIL` | **1** | **2** |
| `NOT_TESTABLE` | **1** | **0** |

The vine case reproduced to the digit (F 0.596, G 0.806). `DESERVES_FUTURE_INTEGRATION = NO`
and `PORTAL_INTEGRATION = NO` survive in both.

The certification reported three of these eight (C, F, G) and attributed all of them to one
line. The other five come from a second, unrelated cause it found elsewhere but never carried
into its reproducibility verdict. Both are below.

---

## 1. REPRODUCIBILITY

### R1 — The committed gate numbers are not determined by the repository

**CLAIM** The certification's mechanism is correct: `current_pressure.denominator_guard`
(ENGINE/current_pressure.py:74) builds `den[id_survey]` while iterating an **unsorted**
`glob.glob()`, last-writer-wins, and `id_survey` is not unique across season files.
`load_rows` (line 112) sorts its glob; this one does not. It is the only unsorted glob in
ENGINE/ or CASES/.

**METHOD** `REDTEAM/rt5_p4_order.py`. I replay `denominator_guard`'s dict-building loop
verbatim under a chosen file order and swap in an equivalent guard. Validated against the
untouched shipped function driven through a patched `glob.glob` (`--mode validate`):
identical on ascending and on descending, both cases, to the digit. 33 fixed orders
(native, ascending, descending, 30 seeded permutations), each order held constant for the
whole run — which is what a filesystem does.

**REPRODUCED: YES.**

| gate | committed | values over 33 fixed orders | count |
|---|---|---|---|
| C (disagreeing season-cells, both cases) | 19 | 18, 19 | 18×14, 19×19 |
| F (olive mean label stability) | 0.918 | 0.918, 0.924 | 0.918×16, 0.924×17 |
| G (olive dominant-class share) | 0.424 | 0.417, 0.424, 0.432, 0.439, 0.447, 0.455 | 2, 7, 15, 7, 1, 1 |
| F, G (vine) | 0.596, 0.806 | 0.596, 0.806 | 33 of 33 — never moves |

Descending order alone gives C=19 and G=0.424. **4 of 33 orders (seeds 15, 18, 21, 28)
reproduce all three committed olive values simultaneously: C=19, F=0.918, G=0.424.**

**NUMBERS (denominators).** 21 denominator files; 79,251 olive visits; 52,250 `id_survey`
keys in `den`; 14,649 keys appear in more than one season file; 2,443 carry conflicting
values; **1,759 keys flip DROP vs KEEP depending on which file is read last**, and
**5,687 of 79,251 visits (7.18%) hang on those 1,759 keys**. My recount of those four
figures matches the certification's H2 exactly (`rt5_p6_encoding_and_keytype.py`).

`REDTEAM/rt5_p10_drop_distribution.py` computes the reachable set of the guard's own
`dropped_zero_or_unknown_denominator` counter exactly (validated against the shipped
function: ascending 3,397, descending 3,873). Over 20,002 sampled orders: **1,152 distinct
values, minimum 2,892, maximum 4,443 — a spread of 1,551 rows, 1.96% of all visits.** The
committed `ENGINE/regional_coverage.json` records **3,206**; this checkout produces **3,397**;
3,206 was reached 5 times in 20,002 samples.

**IMPACT: FATAL** for the claim that a published number traces to a versioned artefact. The
repository does not fix the answer. Two honest people running the shipped code on the same
bytes get different published headline numbers, and nothing in the output says which they got.

**WHAT SURVIVES** The mechanism is one line and the fix is one word (`sorted`). The vine case,
which declares no denominator, is stable under every order tried. The defect is in the
denominator join, not in the pressure definition — the certification's scoping is right.

### R2 — The certification's conclusion is stronger than its evidence, in the wrong direction

**CLAIM** `p1_order_experiment.json` states: *"The committed value 0.918 was not reproduced
by ANY of the eight orders tried… It is not a property of the data; it is a property of the
machine that produced it."* The first half is a sampling result reported as a property.

**METHOD** `REDTEAM/rt5_p4_order.py` (33 fixed orders) and `rt5_p8_cert_harness.py`
(6 more).

**REPRODUCED: NO — the claim fails.** F = 0.918 occurs in **16 of 33** fixed orders. The
complete committed triple occurs in **4 of 33**. The committed answer-sheet numbers are all
reachable too (R6). The committed `regional_coverage.json` drop count 3,206 is reachable
(5 of 20,002).

**IMPACT: MAJOR** — against the certification, not the pilot. The correct statement is not
*irreproducible*; it is **under-determined**: the repository admits at least 2 values of F,
at least 6 of G, and at least 1,152 of the guard's drop count, and the committed artefact is
one draw from that set. That is a worse defect than "the number is wrong", because the number
is not wrong — it is simply not a function of anything versioned.

**WHAT SURVIVES** `REPRODUCIBLE_FROM_CLEAN_CHECKOUT: NO` is still the right verdict, for a
reason the certification stated only partly.

### R3 — A second cause the certification found and did not carry into its verdict: gates.py:241

**CLAIM** `ENGINE/gates.py:241` reads
`snap = "/home/user/eame-sintonia/italia-portale/client/meeting-intelligence-snapshot.json"` —
an absolute POSIX path. `os.path.exists(snap)` is False on any machine that is not that one,
and the fallback `jv = FAIL, "inventory not readable"` is emitted as a **FAIL**, not as
NOT_TESTABLE.

**METHOD** Section 0 (clean clone) plus `rt5_p5_nondeterminism.py` (N11).

**REPRODUCED: YES.** Gate J goes `NOT_TESTABLE → FAIL`; the tally line goes
`PASS=8 FAIL=1 NOT_TESTABLE=1` → **`PASS=8 FAIL=2 NOT_TESTABLE=0`**.

**IMPACT: MAJOR.** The certification found this path twice — `p2_gate_inventory` defect T5
and `p14_artifact_inventory` `NOT_REPRODUCIBLE_REFERENCES` — but `p1_drift_cause.json` and
`p1_order_experiment.json`, the two artefacts offered as the reproducibility finding, quantify
only C, F and G and dispose of gate J in one sentence ("a separate and simpler cause"). The
measured consequence — the tally line a reader would quote — is published nowhere.

**WHAT SURVIVES** The substance of gate J is intact. A byte copy is tracked in this repo at
`italia-portale/client/meeting-intelligence-snapshot.json`, and recomputing gate J's walk over
it reproduces the committed evidence exactly: **43 cases, 17 `O1_FIELD_PRESSURE`, 3 vine ×
Toscana, 0 olive targets.** One relative path fixes the gate.

### R4 — gates.json is a function of the repository AND a third-party server

**CLAIM** Gate H re-probes `https://agroambiente.info.regione.toscana.it/agro18/api/dati/get_aedita_data`
live, three times, inside `evaluate()`. The gate result therefore depends on what a server
returns on the day of the run.

**METHOD** `REDTEAM/rt5_p11_gate_h_offline.py`. `automation_probe.API` is rebound in-process
to an unresolvable host — what an offline clone, a firewalled runner or a source outage looks
like to the shipped code — and gate H's predicate, copied verbatim from gates.py, is evaluated
on the result.

**REPRODUCED: YES.**

| condition | reachable | control tripped | gate H |
|---|---|---|---|
| live, today, this machine | 2/2 | True | PASS |
| source unreachable | 0/2 | False | **FAIL** |

**NUMBERS** Committed gates.json: `PASS=8 FAIL=1 NOT_TESTABLE=1`. Clean checkout with network:
`PASS=8 FAIL=2 NOT_TESTABLE=0`. Clean checkout without network: **`PASS=7 FAIL=3
NOT_TESTABLE=0`**.

**IMPACT: MAJOR.** A certification artefact that cannot be regenerated offline is not an
artefact of the repository.

**WHAT SURVIVES** Probing live is a deliberate and defensible choice — the certification's own
comment says the previous version passed with a dead endpoint and yesterday's JSON on disk.
The defect is that the result is written into a committed file with no record of the probe
response it depended on.

### R5 — Other machine dependences: what I found, measured, and what it is worth

`REDTEAM/rt5_p5_nondeterminism.py`, `rt5_p6_encoding_and_keytype.py`.

| # | dependence | measurement | impact |
|---|---|---|---|
| N1/E1 | **Text `open()` with no `encoding=`** — 25 `open(` calls across 10 files in ENGINE/ and CASES/, **0** with an explicit encoding. Decoding follows the platform locale (this box: cp1252; a Linux box: utf-8). | 20 of 84 olive files and 2 of 40 vine files parse **differently** under the two encodings. The only field affected is `name` (448 + 10 rows). `nome_area`, `date`, `val`, `id_survey`, `id_field`, `week` are unaffected; the 10 distinct province names across the three cases (Arezzo, Firenze, Grosseto, Livorno, Lucca, Massa-Carrara, Pisa, Pistoia, Prato, Siena) are pure ASCII. | **MINOR** (latent). No published number moves today. One accented province name or one accented outcome label in a future region makes it load-bearing. |
| — | **`core.autocrlf=true` with no `.gitattributes` covering CASES/** | `collection_index.json` is rewritten on Windows checkout: git blob 22,170 bytes → 23,101 bytes on disk (931 LF→CRLF). The RAW payloads survive only because **0 of 138 RAW files contain a single CR or LF byte** — they are single-line JSON, so there is nothing to convert. The repo's own `.gitattributes` protects `italia-portale/BASELINE/**` and `italia-portale/client/**` with `-text` for exactly this reason, and does not cover `CASES/`. | **MINOR** (latent). The hash chain survives by an accident of formatting. A future collection that pretty-prints RAW JSON makes every clean Windows checkout raise `REFUSED: … does not match its collected sha256` on the first file. |
| N3 | `PYTHONHASHSEED` | Same olive run under seeds 0, 1, 12345 in three subprocesses: **3 of 3 outputs byte-identical.** | **NONE** |
| N4 | **`id_survey` arrives as both `int` and `str`** — `den` holds 26,415 int keys and 25,835 str keys; **225 of 52,025** survey ids appear under both types, so 225 surveys hold two independent denominator entries. | I predicted a silent join miss and was wrong: **0 of 79,251** outcome rows fail to find a key, and **0** miss only because of key type. | **MINOR**, and order-independent — no sorting fixes it. |
| N5/N6 | Date and week parsing (`date.fromisoformat`, `int(week)`) — a Python-version hazard | 120,133 dated rows across the three cases: **100% plain `YYYY-MM-DD`**; **0** unparseable `week` values. | **NONE** |
| N7 | Float summation order | Exists in `SEVERITY` only (`mean(vals)`). `INCIDENCE` is `sum(1 for v in vals if v>0)/len(vals)` — integer counts. **No caller passes `metric="SEVERITY"`;** gates.py, answer_sheet.py and refresh_coverage.py all use the default. | **NONE** |
| N9 | **CWD-relative artefact writes** — `gates.py` → `gates.json`, `answer_sheet.py` → `answer_sheet.json`, `refresh_coverage.py` → `regional_coverage.json`, all `open("…","w")` against the CWD; and `answer_sheet.py`/`gates.py`/`refresh_coverage.py` reach the data through `"../CASES/…"`. | Run from anywhere but `ENGINE/`, the scripts either fail to find the cases or write the artefact somewhere else and leave the committed copy stale. | **MINOR** |

Nothing in ENGINE/ or CASES/ reads `os.environ`, `getenv`, `datetime.now`, `date.today` or a
temp directory. `AS_OF` really is an input, not the clock — that claim holds.

### R6 — "0 of 10 published cells change" is true of the class and false of a published number

**CLAIM** `p1_order_experiment.json` reassures: *"0 of 10 province cells change class with
file order on 2026-09-06."* `p1_drift_cause.json` records `CELLS_THAT_CHANGE_WITH_FILE_ORDER: 0`.
Both count **class** changes. `ENGINE/answer_sheet.json` question 3 (`3_HOW_MUCH`) publishes
`VALUE` **and `BASELINE_MEDIAN`** for each province.

**METHOD** `REDTEAM/rt5_p9_published_values.py` — 43 file orders, one `current_pressure` call
each, every published field compared.

**REPRODUCED: YES, partly for them and partly against them.**

| field | province cells that move over 43 orders |
|---|---|
| `STATE`, `VALUE`, `n_sites`, `n_visits`, `PERCENTILE`, `BASELINE_N` | **0 of 10** |
| `BASELINE_MEDIAN` | **3 of 10** — Arezzo (2 values), Grosseto (6 values: 0.4633 … 0.4762), Livorno (4 values) |

Every committed answer-sheet number is reachable, Grosseto's `BASELINE_MEDIAN = 0.4633`
included. Regenerating `ENGINE/answer_sheet.json` with the code committed beside it
(`rt5_p7_stale_artefacts.py`) gives **2 of 272 leaf fields different**: Grosseto
`BASELINE_MEDIAN` 0.4633 → 0.4762, and `MEAN_LABEL_STABILITY` 0.918 → 0.924.

**IMPACT: MINOR.** The certification's sentence is literally true. It is also the sentence a
reader will take as "today's published cells are safe", and one of the two numbers printed
next to each published value is not.

**WHAT SURVIVES** The eight published classes and their values are stable across every order I
tried. The instrument's answer today does not move; its context number does.

---

## 2. PROVENANCE

### P1 — `RAW_SHA256` is not the hash of the file the number came from

**CLAIM** `current_pressure.py:26` promises each cell carries *"the sha256 of the raw file it
was computed from"*. Lines 286-288 build it as:

```python
"RAW_FILES":  sorted(meta["hashes"]),
"RAW_SHA256": sorted(meta["hashes"].values())[:1] and
              list(sorted(meta["hashes"].items()))[-1],
```

`X and Y` returns `Y` when `X` is truthy. The left operand — a one-element list holding the
numerically lowest hash — is computed, used as a non-empty guard, and thrown away. What ships
is the `(filename, sha256)` **pair of the alphabetically last outcome file**.

**METHOD** `REDTEAM/rt5_p2_evidence_block.py` (expression in isolation, then the shipped
module, then a recomputation of which files really supplied each province's rows) and
`rt5_p3_tamper.py` test T5.

**REPRODUCED: YES.**

- `RAW_SHA256` = `['c2_s1_v-1002_2026.json', '249ce769…']` (olive) and
  `['c3_s8_v39_2026.json', '374c5463…']` (vine). Not a hash — a two-item list.
- **1 distinct EVIDENCE block across all 9 published cells** in each case. It carries no
  per-province information at all.
- `RAW_FILES` names **21 of the 84** files in the olive case and **20 of 40** in the vine case.
- Every province's number rests on more files than the one named: Arezzo's olive value uses 1
  window file and **20 baseline files**.
- Under hindcast — which is how gates C and G are computed — the field is simply wrong:
  `as_of` 2015-09-06 and 2020-09-06 both still report `c2_s1_v-1002_2026.json`. It is right
  for 2026 only because `2026` sorts last.
- On an empty hash dict the expression returns `[]`, not `None`.
- The docstring also promises "first/last observation date". The block contains
  `SOURCE, ROLE, RAW_FILES, RAW_SHA256, WINDOW` and no dates.

**IMPACT: MAJOR.** The one field whose job is to bind a published number to a byte sequence
binds every number to the same arbitrary file.

**WHAT SURVIVES** `RAW_FILES` does name the complete outcome-variable file set, and those
files *are* hash-checked on load. The chain is recoverable; it is just not what the field says.

### P2 — 50.1% of the olive pipeline's input bytes are never hash-checked, and tampering with them changes a published cell

**CLAIM** `load_rows` hashes only `*_v{var_id}_*.json`. `denominator_guard` opens
`*_v{denom_var}_*.json` and hashes nothing — even though `collection_index.json` holds their
sha256.

**METHOD** `REDTEAM/rt5_p1_hash_coverage.py` (inventory) and `rt5_p3_tamper.py` (tamper, in a
throwaway copy; ENGINE/ and CASES/ untouched).

**REPRODUCED: YES.**

| case | hashed | read but never hashed | unhashed share of bytes |
|---|---|---|---|
| OLIVO-BACTROCERA-TOSCANA | 21 files / 29,918,763 B | **21 files / 30,013,423 B** | **50.1%** |
| VITE-OIDIO-TOSCANA | 20 files / 13,140,422 B | 0 | 0% |
| FRUMENTO-SEPTORIA-TOSCANA | 14 files / 2,205,364 B | 0 | 0% |

Tamper T2: in a sandbox copy I set the first 400 non-null `val` entries of
`c2_s1_v1_2026.json` (a denominator file, listed in the index **with** a sha256) to `0`.

- The pipeline **ran, silently**. No refusal, no warning.
- Guard drops went 3,397 → 3,793 (+396).
- **Arezzo moved from `LOWER_THAN_USUAL`, value 0.0, to `UNKNOWN_NO_DATA`, value `None`** — a
  published cell destroyed by editing a file the integrity check never looks at.

Control T1: the same edit to an **outcome** file was refused —
`ValueError: REFUSED: c2_s1_v-1002_2026.json does not match its collected sha256`. The check
works; it is aimed at half the input.

**IMPACT: FATAL.** A published province cell cannot be traced to a verified artefact. Half the
bytes behind it are unverified, and altering them changes the answer without complaint.

**WHAT SURVIVES** The hashes exist in the index. `denominator_guard` needs the same four lines
`load_rows` already has.

### P3 — Two more conditions under which the check silently does not run

**CLAIM** `if by_file.get(base) and by_file[base] != h: raise`. Two falsy escapes:
(a) the file is on disk but absent from the index → `.get()` returns `None`; (b) the file is in
the index with `sha256: null`/`""` → falsy. Either way the comparison is skipped, not failed.

**METHOD** `rt5_p3_tamper.py` T3 and T4 — corrupt an outcome file, then remove its index entry
(T3) or null its hash (T4).

**REPRODUCED: YES.** Both ran to completion with no refusal. (In these two runs the corrupted
values happened to decode to nothing usable, so no state moved; the point is that the guard did
not fire, and T2 shows what happens when the changed bytes do matter.)

**NUMBERS in the shipped tree today:** 84 of 84, 40 of 40 and 14 of 14 index entries carry a
real sha256. **0 files are currently in either escape state.** The door is open; nothing is
walking through it.

**IMPACT: MAJOR (latent).** The condition is a missing-file or missing-hash away, and a
missing hash is exactly what a failed or partial re-collection produces.

**WHAT SURVIVES** No mismatch exists anywhere today: I recomputed all 138 RAW sha256s against
the three indexes and found **0 mismatches**.

### P4 — Gate E's evidence is a hardcoded sentence, and it is false

**CLAIM** Gate E's predicate is `a == b`, two `current_pressure` runs inside one process. Its
`EVIDENCE` is a string literal: *"byte-identical re-run; AS_OF is an input not the clock; every
raw file sha256-checked against the collection index"* — no part of which the predicate
computes.

**REPRODUCED: YES.** By P2, "every raw file sha256-checked" is false for the olive case: 21 of
42 files read are never checked. And because both runs happen in one process against one
directory listing, gate E is structurally unable to detect the order dependence of R1: it
returned PASS on the clean clone whose F and G both differ from the committed values.

**IMPACT: MAJOR.** The gate named REPRODUCIBLE passed on the run that proved the pilot is not.

**WHAT SURVIVES** "AS_OF is an input not the clock" is true and I verified it (R5: no clock
read anywhere in ENGINE/ or CASES/).

### P5 — Nothing records which raw rows produced a province's value

**CLAIM** A third party cannot recompute one published cell from the published record.

**METHOD** `rt5_p2_evidence_block.py`.

**REPRODUCED: YES.** The emitted record per cell is `VALUE, n_sites, n_visits, EVIDENCE
{SOURCE, ROLE, RAW_FILES, RAW_SHA256, WINDOW}, BASELINE_SEASONS, BASELINE_N, BASELINE_MEDIAN,
PERCENTILE, STATE`. There are **0** row-level identifiers: no `id_field`, no `id_survey`, no
contributing dates, no per-file breakdown. The evidence block is identical for all 9 cells. The
denominator files — which decide whether each of 79,251 visits counts at all — are named in
**0** cells.

To recompute Arezzo's olive value a third party needs: the 21 outcome files (named), the 21
denominator files (not named), **and the order in which the denominator files were read** (not
recorded anywhere, and by R1 it changes the answer). The first is available; the second and
third are not.

**IMPACT: MAJOR.**

**WHAT SURVIVES** `n_sites`, `n_visits`, `BASELINE_SEASONS` and `PERCENTILE` are enough to
audit the arithmetic *given* the row set. The missing piece is the row set.

### P6 — Committed artefacts that disagree with the code committed beside them

**METHOD** `REDTEAM/rt5_p7_stale_artefacts.py` plus `git log` per file.

| artefact | last written at | code changed after | result |
|---|---|---|---|
| `ENGINE/answer_sheet.json` | `5c90455` | `current_pressure.py` at `e44515d` and `a4d19dd` | **2 of 272 leaf fields differ** from a fresh run: Grosseto `BASELINE_MEDIAN` 0.4633 → 0.4762; `MEAN_LABEL_STABILITY` 0.918 → 0.924 |
| `ENGINE/gates_final.txt` | `e44515d` | `gates.py` at `5cf2e48` and `a4d19dd` | **contradicts `ENGINE/gates.json` in the same commit**: it records `PASS G_DISCRIMINATES_BETWEEN_SEASONS` and the tally `PASS=9 FAIL=0 NOT_TESTABLE=1`, while gates.json records `FAIL` and `PASS=8 FAIL=1 NOT_TESTABLE=1` |
| `CASES/gates_final.txt` | `e44515d` | — | agrees with gates.json on all 10 gates |
| `ENGINE/regional_coverage.json` | `9833ba0` | — | records guard drop 3,206; this checkout gives 3,397 (see R1) |

**IMPACT: MAJOR.** `ENGINE/gates_final.txt` is the most flattering artefact in the tree —
nine passes, no failures — and it is stale by two commits. A reader who opens the `.txt`
instead of the `.json` reads a verdict the project has already retracted.

**WHAT SURVIVES** The `.json` is the one the code writes and it is current. `answer_sheet.json`
is wrong in 2 of 272 fields, and both are numbers R1 already explains.

### P7 — No collection timestamp anywhere

All three `collection_index.json` files carry request keys
`file, n_rows, ok, rowCount, sha256, var, year` and index keys
`api, codes, crop, requests, schema, vars` (plus `DENOMINATOR_VAR` for olive). There is
**no `collected_at`, no `refresh_attempt_at`, no `source_published_at`** in any of the three.
The bytes are hashed; *when they were fetched* is not recorded. The certification found this
too (`p14_artifact_inventory.json`). **IMPACT: MINOR** for today's frozen archive, MAJOR the
moment a refresh happens.

---

## 3. ERRORS IN THE CERTIFICATION ITSELF

### E1 — The headline order experiment used a harness no filesystem can imitate, and it is what hid the answer

`CERT-V2/_probe_order.py`, which produced the six seeded rows of `p1_order_experiment.json`:

```python
rnd = random.Random(seed)
cp.glob.glob = lambda p,**k: (lambda L:(rnd.shuffle(L),L)[1])(list(real(p,**k)))
```

One shared `Random`, **reshuffled on every call**. `sensitivity()` runs `current_pressure` 135
times and each call re-globs, so each of the 135 grid points is scored against a *different*
denominator join; `hindcast()` does the same once per season. A directory listing is stable
within a process — that stability is the entire premise of the "different machine, different
order" argument the experiment is making.

**METHOD** `REDTEAM/rt5_p8_cert_harness.py` runs both harnesses over the same 6 seeds.

| harness | GATE_F (olive) | GATE_G (olive) | GATE_C |
|---|---|---|---|
| FIXED — one order for the whole run | **0.918, 0.924** | 0.417, 0.424, 0.432, 0.447 | 18, 19 |
| PERCALL — the certification's | **0.919, 0.921, 0.922, 0.923** | 0.424, 0.432, 0.439, 0.447 | 18, 19 |
| as published by the certification | 0.918, 0.921, 0.922, 0.923, 0.924 | 0.424, 0.432, 0.439, 0.447 | 18, 19 |

The two F sets are **disjoint**. Across 39 fixed orders (33 in `rt5_p4_order.py` + 6 here) I
never observed 0.919, 0.921, 0.922 or 0.923. **Three of the five F values in the
certification's published table are artefacts of its own harness** — no file order produces
them. And the same blending is why it never found 0.918: averaging across orders inside one
stability grid lands strictly between the two attainable values, so the harness both
manufactured values that cannot occur and concealed the one it declared unreachable.

**IMPACT: MAJOR** on the certification. The finding (order dependence) stands; the table of
observed values does not.

### E2 — The script behind the headline table is not in the repository

`CERT-V2/.gitignore` excludes `_probe_*.py`, `_time_eval.py`, `_verify_m03.py`,
`_drive_mutations.sh`, `_run_light*.sh`. **7 scripts present on disk are unversioned**, and one
of them is `_probe_order.py`, which `p1_order_experiment.json` names as its source
("the six-seed shuffle recorded here"). A clean clone of this branch contains the conclusion
and not the instrument. A certification whose central artefact is irreproducible from the
repository is making the pilot's mistake.

### E3 — Claims that overstate what was measured

| certification text | measured |
|---|---|
| "The committed value 0.918 was not reproduced by ANY of the eight orders tried" | 16 of 33 fixed orders reproduce it; 4 of 33 reproduce C, F and G together |
| "It is not a property of the data; it is a property of the machine that produced it" | It is a property of the data **under an order the repository does not fix**. Under-determined, not machine-specific |
| `DISTINCT_VALUES_OBSERVED.GATE_G_olive_dom: [0.424, 0.432, 0.439, 0.447]` | at least 6 values: 0.417 and 0.455 also occur under fixed orders |
| `GATE_NUMBERS_BY_FILE_ORDER` records `GATE_C_disagreeing: null` for asc and desc | C is order-dependent and descending order alone gives the committed C=19; it was never checked |
| "a byte-identical copy is tracked in this repository" (p2 defect T5, about the /home/user snapshot) | **NOT KNOWN** — the referent does not exist on any machine I can reach, so byte-identity cannot be established. What I *can* verify: the in-repo copy reproduces gate J's four published numbers exactly (43 / 17 / 3 / 0) |

### E4 — Two of the certification's own numbers I checked and confirmed

`p1_drift_cause.json` H2 (52,250 keys / 14,649 multi-file / 2,443 conflicting / 1,759 flipping
DROP vs KEEP) is reproduced **exactly** by my independent recount, and its asc/desc gate
numbers (F 0.924 both, G 0.432 asc / 0.424 desc) are reproduced exactly. Those parts of
`p1_drift_cause.py` use a genuine fixed order and are sound; the defect is confined to
`_probe_order.py`.

---

## 4. WHAT I COULD NOT BREAK

Five attacks of mine failed. I report them as failures.

1. **The diagnosis itself.** I tried to find a second cause for the C/F/G drift and there
   isn't one. `denominator_guard`'s unsorted glob is the only unsorted glob in ENGINE/ or
   CASES/, and the vine case — which declares no denominator — returned F = 0.596 and
   G = 0.806 in **33 of 33** orders and in the clean clone. The certification's scoping is
   correct.

2. **The stale-artefact hypothesis for `gates.json`.** I suspected `gates.json` at `a4d19dd`
   was carried over rather than regenerated, because F=0.918 and G_olive=0.424 appear
   unchanged at `193689c`, `5c90455`, `e44515d` and `a4d19dd`, across a commit that added the
   effect-size floor `MIN_POSITIVE_SITES`. Measured (`rt5_p7_stale_artefacts.py`): the floor
   changes **0 of 200** olive walk-forward cells and **5 of 190** vine cells, moving G_vine
   from 0.667 to 0.806 — which is precisely the change recorded between `193689c` and
   `a4d19dd`. `a4d19dd` was an honest full re-run. Hypothesis falsified.

3. **A silent join miss from mixed key types.** `den` holds 26,415 `int` and 25,835 `str`
   keys and 225 ids appear as both, so I expected outcome rows to miss their denominator.
   **0 of 79,251** rows miss, and **0** miss by type alone. Falsified.

4. **Encoding, hash seed, float order, date parsing.** `PYTHONHASHSEED` 0/1/12345 gives
   3 byte-identical outputs. 120,133 dated rows are 100% plain ISO and 0 `week` values are
   unparseable. Float summation order exists only in `SEVERITY`, which no caller requests.
   The cp1252/utf-8 split touches 22 of 138 RAW files but only the `name` field; all 10
   province names are ASCII. None of these moves a published number today.

5. **Today's ten published cells.** Across 43 file orders, `STATE`, `VALUE`, `n_sites`,
   `n_visits`, `PERCENTILE` and `BASELINE_N` moved in **0 of 10** cells. The outcome-file
   sha256 check fires correctly when the bytes change (T1 refused). All 138 RAW files match
   their recorded hashes: **0 mismatches**. Gate J's substance survives its broken path.

### NOT KNOWN

- **Which denominator file order produced the committed `a4d19dd` numbers.** 4 of 33 orders
  reproduce the triple, so the committed values are consistent with the shipped code; I cannot
  tell whether that machine's listing order was one of them or whether something else
  contributed. *Settled by* recording, in the output, the sha256 of the ordered list of files
  actually read — then any run declares its own order and the question disappears.
- **Whether `/home/user/eame-sintonia/.../meeting-intelligence-snapshot.json` is byte-identical
  to the tracked copy.** *Settled by* the original machine printing its sha256, or by the code
  using the tracked copy so the question stops mattering.
- **Whether the locale-encoding hazard can ever reach a published number.** It cannot in these
  three cases. *Settled by* one region whose province or code labels carry an accent — and by
  then it will be settled the expensive way.
- **The full reachable set of gate F.** I observed exactly two values in 39 fixed orders; 21!
  orders exist. *Settled by* enumerating the 1,759 flip keys' winning files rather than
  sampling permutations.

---

### Scripts (all under `CERT-V2/REDTEAM/`, all mine, all re-runnable)

`rt5_p1_hash_coverage.py` · `rt5_p2_evidence_block.py` · `rt5_p3_tamper.py` ·
`rt5_p4_order.py` (`--mode validate` first) · `rt5_p5_nondeterminism.py` ·
`rt5_p6_encoding_and_keytype.py` · `rt5_p7_stale_artefacts.py` · `rt5_p8_cert_harness.py` ·
`rt5_p9_published_values.py` · `rt5_p10_drop_distribution.py` · `rt5_p11_gate_h_offline.py`

Each writes a `.json` of the same name. Clean-clone outputs:
`rt5_p0_gates_clean_clone.json`, `rt5_p0_gates_clean_clone_stdout.txt`,
`rt5_p0_gates_committed.json`. Clone at `C:/rt5-clean-clone`.
