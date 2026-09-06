# ARBITER-V2 — INDEPENDENT RULING ON THE DISEASE-PRESSURE INSTRUMENT AND ITS CERTIFICATION

I wrote none of `ENGINE/`, none of `CASES/`, none of `CERT-V2/`, and none of `REDTEAM/`.
I read them and I ran them. Nothing under `ENGINE/`, `CASES/` or `italia-portale/` was
modified; every mutation below is an in-memory monkeypatch in a separate process, and the one
clean checkout is a `git clone` into `C:/tmp/arbclone`, outside the repository. Nothing was
committed or pushed.

Machine: Windows 11, Python 3.12, `locale.getpreferredencoding(False)` = **cp1252**, network
reachable (gate H's live probes returned 200). Repository `C:/cert-v2-disease-pressure`, branch
`claude/disease-pressure-certification-v2`.

**HEAD moved while I was ruling.** When I started, HEAD was `a8b9650`. Two further commits
landed during my run — `54ff58c` ("the cutoff changes 0 of 20 cells, not 5 of 10") and
`098b4de` ("my step-1 headline was wrong, and the probe behind it was not in git"). My clean
checkout and every gate run below are at **`098b4de`**. `ENGINE/` and `CASES/` are byte-identical
between `a4d19dd` (the pilot commit under test) and `098b4de` — `git diff --stat` returns
nothing — so the instrument I judged is the instrument the certification measured.

**RT5 exists.** `REDTEAM/RT5-provenance-and-reproducibility.md`, 6 lenses in total (RT1–RT6),
all present. `p17_delivery.json`'s `INDEPENDENT_RED_TEAM_REPORTS` lists only five and omits
RT5; that field is stale.

---

# PART 1 — WHAT I CHECKED MYSELF

Sixteen checks. Each was run, not read. Every number carries its denominator.

## 1.1 CLEAN CHECKOUT — does the repository's own code reproduce the repository's own numbers?

I cloned the branch into `C:/tmp/arbclone` and ran `gates.evaluate()` there, and separately in
the working tree.

| number | committed `ENGINE/gates.json` | my clean clone | my working tree | RT5's clean clone |
|---|---|---|---|---|
| gate C disagreeing season-cells | **19** | **18** | **18** | **18** |
| gate F olive label stability | **0.918** | **0.924** | **0.924** | **0.924** |
| gate G olive dominant-class share | **0.424** | **0.432** | **0.432** | **0.432** |
| gate J verdict | **NOT_TESTABLE** | **FAIL** | **FAIL** | **FAIL** |
| tally | 8 PASS / 1 FAIL / 1 NT | **8 PASS / 2 FAIL** | **8 PASS / 2 FAIL** | 8 PASS / 2 FAIL |

Three of the certification's headline numbers and one gate verdict do not reproduce.
My clone and my working tree agree with each other to the digit and with RT5, and both
disagree with the artefact committed in the repository. **CLEAN_CHECKOUT_REPRODUCIBLE = NO,
confirmed independently.** Full suite runtime 320 s (working tree) and 385 s (clone).

## 1.2 THE CAUSE OF THE DRIFT — I re-derived it from the raw archive

`current_pressure.denominator_guard` (lines 74–79) assigns `den[r["id_survey"]]` while
iterating an **unsorted** `glob.glob()`, so the last file the filesystem hands over wins the
key. Counting the denominator variable (var 1) of the olive case myself:

- 21 denominator files, **79,251** denominator rows, **52,250** distinct `id_survey` keys
- **14,649 / 52,250** keys appear in more than one file
- **2,443 / 52,250** keys carry conflicting values
- **1,759 / 52,250** keys are conflicts where the disagreement flips DROP vs KEEP
  (example key 3787: values `{0, 100}` across `c2_s1_v1_2006/2007/2008/2012.json`)

The certification's `DRIFT_CAUSE` numbers reproduce exactly. Its commit message calls the cause
"the machine". **That is the wrong noun.** The machine only chooses among the answers the
instrument has left open. Joining a denominator on a key that is not unique is a defect of the
instrument, and the filesystem is merely the coin it tosses.

I then ran the shipped engine under three fixed file orders:

| glob order | rows dropped by the guard (of 79,251) | gate G olive | gate C disagreeing | today's 10 published olive cells |
|---|---|---|---|---|
| sorted ascending | 3,397 | 0.432 | 14 | 8 LOWER / 1 TYPICAL / 1 UNKNOWN |
| sorted descending | 3,873 | 0.424 | 15 | identical |
| shuffled (seed 7) | 3,565 | 0.432 | 15 | identical |

**476 rows of 79,251 (0.60%) move in or out of the analysis purely on file order.** The
certification numbers move with them. **Today's published cells do not: 0 of 10 changed.**
Both halves matter and I will not collapse them.

## 1.3 MUTATION TESTING — five mutations I wrote myself, run through the shipped suite

Baseline, unmutated, this machine: **8 PASS / 2 FAIL** (G and J fail), `DESERVES = NO`.

| my mutation | property destroyed | gate that names it | its verdict | suite tally |
|---|---|---|---|---|
| **AM1** the live window loses its upper bound (the cutoff, isolated — baselines untouched) | B | B_NOT_SOLD_AS_FORECAST | **PASS** | **9 PASS / 1 FAIL** |
| **AM2** `read_value` returns 0.0 for a missing or unreadable value (FAILURE == ZERO) | D | D_UNKNOWN_IS_VISIBLE | **PASS** | 8 PASS / 2 FAIL |
| **AM3** file order fixed but reversed | E | E_REPRODUCIBLE | **PASS** | 8 PASS / 2 FAIL |
| **AM4** every observation date shifted one year forward | — | (no gate) | — | 8 PASS / 2 FAIL |
| **AM5** source URL and every sha256 stripped from the emitted evidence | — | (no gate) | — | 8 PASS / 2 FAIL |

**Five of five survived.** Three of them destroy the exact property a gate names, and that gate
still returned PASS. Two of them destroy properties no gate claims at all: the suite cannot
tell that every date in the archive is wrong by a year, and cannot tell that provenance has
been deleted.

Two details are worse than the table:

- Under **AM1**, gate B printed, with the cutoff removed: *"moving the cutoff forward changes
  18 published province-cells — so the cutoff is LOAD-BEARING and this gate can detect its
  removal."* The sentence is false in the mutant and the gate passed anyway. The 18 cells move
  because advancing AS_OF by 30 days slides the window's **lower** bound; the number gate B
  offers as proof of its subject measures something else. The certification reached the same
  conclusion independently in `p3b_cutoff_correction.json`, committed at `54ff58c` while I was
  running. We agree.
- Under **AM1** the suite score **improved**, from 8 PASS / 2 FAIL to 9 PASS / 1 FAIL, because
  the unbounded window pushed the vine case's dominant-class share from 0.806 to 0.472 and gate
  G flipped to PASS. **A suite in which breaking the product raises the score is not a suite.**

## 1.4 GATE J CANNOT PASS — proved by exhaustion, not by argument

`gates.py` line 242 sets `jv = FAIL, "inventory not readable"`; line 257 can only replace it
with `("PARTIALLY_OVERLAPS", ...)`. Line 264 then maps anything outside `(PASS, FAIL,
NOT_TESTABLE)` to `NOT_TESTABLE`. `jv[0]` therefore takes exactly two values in the whole
program, and both are enumerated:

```
jv[0]=FAIL                -> published VERDICT=FAIL
jv[0]=PARTIALLY_OVERLAPS  -> published VERDICT=NOT_TESTABLE
```

**PASS is unreachable. 2 of 2 branches, 0 of them PASS.** Line 241 also reads the hardcoded
absolute path `/home/user/eame-sintonia/italia-portale/client/meeting-intelligence-snapshot.json`
while a byte-identical file sits at `italia-portale/client/meeting-intelligence-snapshot.json`
in this very repository — which is why the gate reads FAIL on a clean checkout and
NOT_TESTABLE on the author's machine.

## 1.5 GATE F CERTIFIES ONE CASE, NOT THE LABEL

`gates.py` line 130: `PASS if any(v >= STAB_MIN for v in ok.values())`. Measured, both runs:
olive **0.924**, vine **0.596**, against a declared `STAB_MIN` of **0.80** over a 135-point
parameter grid. The vine label is a parameter artefact by the certification's own threshold and
gate F passes on the olive case alone. `any()` where the gate's name promises `all()`.

## 1.6 THE WHEAT CASE MEASURES THE WRONG DISEASE

`CASES/FRUMENTO-SEPTORIA-TOSCANA` holds **14 RAW files, all `c19_s74_v372_*`**, and nothing
else. Read from the case's own `collection_index.json`:

| id_survey_var | source's own name |
|---|---|
| **372** | **Intensità Oidio** ← what the case collects, and what gate I runs |
| 382 | Intensità Septoria ← never collected |

`gates.py` line 221 calls `season_outcomes(unseen, 372)`. **The gate that certifies "it
generalizes" runs on a case whose ISSUE label is wrong.** RT2 (A1) and RT4 (S-2) both found
this and both are right. The arithmetic on the 14 seasons is sound; only the name of the
disease is false. Renaming the directory and the literals fixes it with no recomputation — but
until that is done, one of the four dimensions of the identity is wrong on the case that
carries gate I.

Two of the six codes of var 372 — `'50 - gravissina'` (a source-side typo for *gravissima*) and
`'75 - completa'` — fall off the word ladder and become MISSING rather than *severe*. Magnitude,
honestly: **3 rows of 5,817 (0.05%)**. Real, and small.

## 1.7 THE ENGINE PUBLISHES A DISEASE CLASS FROM THE FUNGICIDE COLUMN

RT4's S-3 is an injection and labels itself one. I rebuilt it from scratch rather than running
RT4's script. VITE `id_survey_var 42` is `prodotto` — **which fungicide the grower sprayed**.
`build_scale` resolves **1 of its 8 codes** (`nessuno` → 0) and drops `zolfo, IBE, quinoxifen,
dinocap, strobilurine, Ampelomices q., altro`. I recoded the real var-39 rows onto that code
table and handed them to the shipped `current_pressure` through its own `_pre` argument:

```
ENGINE REFUSED? NO.   ROLE STAMPED: OFFICIAL_OBSERVATION
Arezzo TYPICAL_FOR_THE_DATE 0.0 (20 sites) ... Siena TYPICAL_FOR_THE_DATE 0.0 (29 sites)
-> 9 published classes, 1 UNKNOWN
```

My table is identical to RT4's, cell for cell. **9 of 10 provinces receive a disease class,
stamped as an official field observation, computed from a spray-diary column.** `value_mode`
returns ORDINAL because a code table exists; `assert_scale_decodes` returns immediately because
it only fires in NUMERIC mode. There is no guard in this direction at all.

## 1.8 THE CODE-VS-VALUE GUARD IS UNREACHABLE ON ALL THREE SHIPPED CASES

| case | var | VALUE_MODE | does `assert_scale_decodes` execute? |
|---|---|---|---|
| OLIVO-BACTROCERA | −1002 | NUMERIC | enters, then returns at `if not code_ids` — the olive index has **0** code entries |
| VITE-OIDIO | 39 | ORDINAL | returns at line 155, `mode != "NUMERIC"` |
| FRUMENTO-"SEPTORIA" | 372 | ORDINAL | returns at line 155 |

**0 of 3 shipped cases reach the guard's test.** Its share-of-values-that-are-code-ids on the
olive case is **0.0000** against a firing threshold of 0.90, and the set it compares against is
empty. `p7`'s `GUARD_IS_REACHABLE_ON_ANY_REAL_CASE: false` is correct.

A smaller point, for the record: the guard's own docstring says var 372 "declares
widget=numeric". In the shipped `collection_index.json` var 372 declares `widget: 'select'`.
The narrative that justifies the guard does not match the metadata now on disk.

## 1.9 THE PUBLISHED OLIVE CELL — all eight readings are LOWER

Reproduced from the raw archive at AS_OF 2026-09-06, latency 2 days:

| province | STATE | value | sites | baseline seasons | baseline median | percentile |
|---|---|---|---|---|---|---|
| Arezzo | LOWER_THAN_USUAL | 0.0000 | 17 | 20 | 0.3600 | 0.100 |
| Firenze | LOWER_THAN_USUAL | 0.0000 | 73 | 20 | 0.5385 | 0.025 |
| Grosseto | LOWER_THAN_USUAL | 0.0577 | 156 | 20 | 0.4762 | 0.100 |
| Livorno | LOWER_THAN_USUAL | 0.1169 | 77 | 20 | 0.8889 | 0.000 |
| Lucca | LOWER_THAN_USUAL | 0.0000 | 14 | 20 | 0.8077 | 0.000 |
| Massa-Carrara | TYPICAL (withheld, stability) | 0.3000 | 10 | 8 | 0.5556 | 0.375 |
| Pisa | LOWER_THAN_USUAL | 0.1111 | 45 | 20 | 0.7778 | 0.000 |
| Pistoia | LOWER_THAN_USUAL | 0.0000 | 16 | 20 | 0.5556 | 0.025 |
| Prato | UNKNOWN_NO_DATA | — | 7 | — | — | — |
| Siena | LOWER_THAN_USUAL | 0.1311 | 61 | 20 | 0.5192 | 0.100 |

**8 of 8 published provinces read LOWER_THAN_USUAL. 0 read HIGHER.** The headline "8/10" is
eight provinces saying *there is less olive fly than usual*, not eight provinces with something
to act on.

## 1.10 THE SOURCE'S OWN LEGEND PUTS EVERY SITE BELOW ITS LOWEST ACTION BAND

The legend is embedded in the case's own metadata for var −1002:
`0 = Nessuna Infestazione` · `0.01 = 0-6% (green)` · `6 = 7-9% (yellow)` · `10 = >=10% (red)`.
In the published window 2026-08-10..2026-09-06:

| | sites | positive (>0) | ≥6 yellow | ≥10 red | worst reading |
|---|---|---|---|---|---|
| all ten provinces | **476** | **34** | **0** | **0** | **5.0** |

**0 of 476 monitored sites reach yellow. 0 of 476 reach red.** The worst grove in Tuscany read
5% of sampled drupes. Across the whole readable archive (**75,825** values after the guard):
`0 Nessuna` 48,325 (63.73%), green 18,009 (23.75%), yellow 4,373 (5.77%), red 5,118 (6.75%) —
so the binary `>0` test that defines INCIDENCE pools the 23.75% the source paints green with
the 6.75% it paints red. RT2's A4 reproduces. 4 impossible (negative) values exist and are read
as "pest absent".

## 1.11 THE EFFECT FLOOR — I disagree with the certification's own retraction, and the floor is still not proved

I rebuilt every classified cell myself across 3 cases × 3 calendar dates × all seasons:
**533 classified cells with a percentile**, of which **86 are rank-HIGHER** and **33 are
withheld by the shipped floor** (`n_sites × incidence < 5`).

| test | `p5b`'s answer (282-cell sample) | my answer (533-cell sample) |
|---|---|---|
| integer floors t∈0..70 giving the shipped partition | **5, 6, 7** | **only 5** |
| distinct partitions over t∈0..70 | 27 | 36 |
| plain incidence threshold that reproduces the floor exactly | **0.41, 0 disagreements** | **none exists**; best is 0.251 with **12 of 86** disagreements |

**The certification's own self-criticism does not generalise.** On a wider sample the floor is
*not* a disguised incidence threshold, and the number 5 *is* singled out among 71 integers.
I say so because the rule is to run it and name who is right, and here the certifier was too
hard on itself.

That does not rescue the floor. It is still **NOT PROVED**, for reasons I verified directly:

- It is **absent from the emitted `PARAMS` block** (which lists only `WINDOW_DAYS, MIN_SITES,
  MIN_BASE, HIGH_P, LOW_P`) and absent from `sensitivity()`'s 135-point grid. **Gate F has
  never varied it.** A parameter outside the grid is a parameter the label is never tested
  against.
- **402 of 533 classified cells** could not clear the floor at their current value. (The
  `p17` phrasing "arithmetically impossible" is too strong: 0 of 533 have `n_sites < 5`, so no
  cell is *structurally* barred — `MIN_SITES = 8` already prevents that.)
- Of the 53 HIGHER calls that survive it, **0 are in 2026** and 48 of 53 are olive.
- No independent register of olive-fly or oidio pressure exists in this repository, so its
  false-negative rate is **NOT KNOWN** and no number can be offered.

## 1.12 EXCHANGEABILITY — the LOWER arm carries a real excess, the HIGHER arm does not

For each of the 9 published olive province-cells I enumerated all n+1 leave-one-out assignments
of the role "current" among {the 20 baselines + this season}, which gives the exact null
probability of each class under exchangeability:

```
per-province P_null(LOWER) = 0.238  (0.222 for Massa-Carrara, baseline n=8)
observed LOWER = 8 of 9        expected under the null = 2.13
```

The 9 provinces share a season and a region and are not independent, so I offer no p-value —
but the direction is unambiguous. RT1 found the same thing on its 282-cell sample: LOWER
observed 79 vs 46.0 expected, with no draw in 20,000 reaching 79, while HIGHER in the
walk-forward fired **36 times where chance supplies 36.5** (obs/exp = 0.99). **The arm that
would trigger spending is the arm with no excess over chance.**

## 1.13 THE TIE CONVENTION DOES NOT TOUCH TODAY'S PUBLISHED CELL

RT1's S-2 shows 114 of 282 labels move under a different tie rule. I re-ran the shipped cell
under all three conventions:

```
Arezzo half=L below=L below+eq=L  (4 tied baselines) ... Siena half=L below=L below+eq=L
cells whose class depends on the tie convention: 0 of 9
```

RT1's finding is real for the certification sample and **does not reach the published
statement**. Both facts stand.

## 1.14 THE ENGINE'S OUTPUT CARRIES THE DATE AND NOTHING ELSE OF THE IDENTITY

```
TOP-LEVEL KEYS: AS_OF, CUTOFF_LABEL, DATA_LATENCY_DAYS, DENOMINATOR_GUARD, EVIDENCE_ROLE,
                METRIC, PARAMS, PROVINCES, SEASON_STATE, SOURCE, VALUE_MODE, WINDOW
CROP: ABSENT   ISSUE: ABSENT   REGION: ABSENT   COUNTRY: ABSENT   AS_OF: PRESENT
```

`gates.py` line 26 calls `answer_sheet(d, v, as_of, "issue", "crop", "region")` with those three
literal placeholder strings, so the sentence the gate suite certifies is, verbatim:

> "In the 28 days to 2026-09-06, official scouts scored 1168 visits for **issue** across 469
> monitored **crop** sites in **region**. 34 of those sites had it present; 435 did not."

Grepping `ENGINE/` and `CASES/` for any crop canonicalisation returns exactly one hit, and it is
gate J reading the *portal's* vocabulary. `OLIVO`, `VITE`, `FRUMENTO` are never mapped to
`CROP_OLIVE`, `CROP_GRAPEVINE`, `CROP_WHEAT`. **3 crops in the data, 0 canonicalised.**

## 1.15 GEOGRAPHY IS NOT INVENTED — but provinces with no data vanish rather than being published UNKNOWN

The published unit is `nome_area`, the source's own province field for the monitored field. No
inheritance occurs. But on the wheat case at 2026-05-15:

```
Arezzo TYPICAL · Firenze UNKNOWN_NO_DATA · Grosseto TYPICAL · Pisa UNKNOWN_NO_BASELINE · Siena UNKNOWN_NO_DATA
PROVINCES IN THE OUTPUT: 5 of Tuscany's 10.   ABSENT ENTIRELY, not even UNKNOWN: 5
```

`p9`'s sentence — "five of five unmonitored provinces stayed UNKNOWN and none acquired a
neighbour's class" — is **half right**. None inherited a neighbour's class, which is the
important half and I confirm it. But they did not "stay UNKNOWN": `current_pressure` builds
`by_prov` from the rows themselves, so a province with zero rows never enters the output at
all. **Absence from a dictionary is not a published UNKNOWN**, and gate D passes on the cases
where some *other* province happens to be UNKNOWN for a different reason.

Coordinates: **4,792 of 317,004** olive rows fall outside a Tuscany bounding box and **100,176**
sit at (0,0). None of it reaches a published number, because the engine reads no coordinate
anywhere. RT4's count of **30 rows in 120,133** disagreeing with the ISTAT comune code is the
right order of magnitude for the semantic error, and `p9`'s `GEOGRAPHY_GATE = FAIL` over
30/120,133 is a fair FAIL on *provenance*, not on the province labels themselves.

## 1.16 REFRESH DOES NOT FAIL CLOSED, AND ON THIS MACHINE IT WOULD BRICK A CASE

`collect_generic.py` lines 60–63 do refuse to write a full-rowCount / all-null response. That
guard works. Three things defeat it:

- Line 31 rebuilds `idx` from scratch and line 72 rewrites it. Any archived file **not
  re-requested** loses its index entry, and `load_rows` line 115 only verifies a file `if
  by_file.get(base)`. **The hash chain silently shrinks after every partial refresh and nothing
  reports it.**
- Line 67 writes with `open(..., "w")` — platform encoding — while line 68 records
  `sha256(blob.encode())` — UTF-8. I ran this: on a cp1252 machine the two differ. **22 of 138**
  archived RAW files contain non-ASCII bytes; refreshing any of them here produces
  `REFUSED: does not match its collected sha256` and the case stops loading. It fails closed,
  and permanently.
- There is **no refresh state at all**: grepping `collect_generic.py` for attempt time, status,
  last-good marker or collected-at returns one hit, and it is `time.sleep`. **Failing closed
  requires knowing that you failed.**

Latency itself is honest: `current_pressure` line 259 takes the newest **readable** observation,
not the newest row and not the file mtime. But `gates.evaluate(as_of=dt.date(2026, 9, 6))` is a
hardcoded default and nothing in the suite reads a real clock, so gate H's
`DATA_LATENCY_DAYS <= 21` certification returns the same answer in 2027 and in 2040. **A
capability named CURRENT_PRESSURE is certified current forever.**

## 1.17 NEGATIVE CONTROLS WORK

| control | result |
|---|---|
| olive at 2026-03-15 (scouting not started) | **10 of 10** provinces UNKNOWN_NO_DATA, latency 149 d |
| olive at 2001-09-06 (archive starts 2006) | **10 of 10** UNKNOWN_NO_DATA |
| `evidence_role=MODELLED_RISK` | **REFUSED** — "RISK_FORECAST != DISEASE_PRESENCE" |
| `evidence_role=FORECAST` | **REFUSED** |
| `evidence_role=CONTEXT` | **REFUSED** |
| var 999999 (not a survey variable) | **REFUSED** — "A predictor is not an outcome" |

**6 of 6 said no. 0 false positives.** This is the strongest part of the instrument and I
confirm it without qualification.

## 1.18 THE ADAMA RELATION — I measured it wider than the certification stated it

`p10_adama_relation.py` opens only `italy-label-verdicts.js` (19 adjudicated triples). The same
repository ships `italy-handoff-v21.js`. I parsed it myself:

- **2,030** label × use pairs, **102** distinct products
- pairs on the OLIVE crop: **1 of 2,030** — MORAINE, target `INFESTANTI` (weeds); a herbicide
- occurrences of `BACTROCERA`, `OLEAE`, `MOSCA DELL'`, `OLIVE FRUIT FLY` anywhere in the
  2,030 pairs: **0, 0, 0, 0**
- the three products p10 names: KLARTAN 20 EW **80** pairs, KLARTAN SMART **88**, MAVRIK SMART
  **91** — across beet, brassicas, carrot, rape, cucurbits, alfalfa, strawberry, apple, potato,
  vine. **Never olive.**

RT6's numbers reproduce exactly. `ADAMA_PRODUCT_RELATION = NOT_FOUND` is **correct**, and the
absence rule (*absence in our reading is not absence in the world*) is the right rule. But the
sentence is **narrower than the measurement the repository contains**: p10 says "three named
products were checked", when the repository holds a 2,030-pair, 102-product corpus in which the
olive fruit fly does not appear once. The error is in the safe direction — it understates the
evidence for NOT_FOUND — but it is not stated at the width that was measured.

---

# PART 2 — RULINGS

One line of verdict, then the number that settles it.

**CLEAN_CHECKOUT_REPRODUCIBLE — NO.**
My clean clone of `098b4de` returns gate C = 18, gate F = 0.924, gate G = 0.424→0.432, gate J =
FAIL; the committed `ENGINE/gates.json` says 19, 0.918, 0.424, NOT_TESTABLE. 3 headline numbers
and 1 gate verdict differ, and the tally moves from 8/1/1 to 8/2/0.

**ARE THE GATES NON-TAUTOLOGICAL, AND CAN EACH BOTH PASS AND FAIL — NO.**
Gate **J** cannot PASS: 2 of 2 reachable values of `jv[0]` map to FAIL or NOT_TESTABLE.
Gate **B** cannot FAIL on its own subject: it returned PASS with the cutoff removed (AM1) while
printing that the cutoff is load-bearing. Gate **F** is `any()` over 2 cases and passes on
0.924 while the other case sits at 0.596 against its own declared 0.80. Gates **A, C, D, E, G,
H, I** can in principle move; only **G** actually did so on shipped data (FAIL, vine 0.806 >
0.75).

**MUTATION_TESTING — DOES NOT WORK.**
5 of 5 of my own mutations survived. 3 of 3 gates whose named property I destroyed returned
PASS. 2 of 2 cross-cutting mutations (dates shifted a year; provenance stripped) produced an
identical verdict set. And AM1 raised the score from 8 PASS to 9 PASS.

**DATE AS PART OF THE IDENTITY — PASS, and it is the only part that is.**
`AS_OF` is present in the output object, is an input and never the clock (RT3 found 3 clock
calls in 10 files, all `time.time()` in `automation_probe`, none reaching a cell), the window is
emitted, and 22 of 25 cells change state across dates. `CROP`, `ISSUE`, `REGION` and `COUNTRY`
are all ABSENT from the same object.

**EFFECT_FLOOR — NOT PROVED.**
It is absent from the emitted `PARAMS`, absent from the 135-point sensitivity grid, and
therefore never varied by gate F. 402 of 533 classified cells cannot clear it at their current
value; 0 of its 53 surviving HIGHER calls are in 2026. Separately: the certification's grounds
for calling it a disguised incidence threshold (0.41, 0 disagreements on 282 cells) **do not
hold** on my 533-cell sample, where no threshold reproduces it and the best is 0.251 with 12 of
86 disagreements. Not proved, and not proved bogus either — undetermined, on the evidence in
this repository.

**REFRESH_FAIL_CLOSED — FAIL.**
0 refresh-state fields exist (no attempt time, status, or last-good marker). The hash chain
degrades silently after any partial refresh. And on a cp1252 machine the write encoding and the
hash encoding disagree, so refreshing any of the **22 of 138** RAW files containing non-ASCII
bytes bricks the case.

**LATENCY_TRUTHFUL — PASS on the measurement, FAIL on the certification.**
`DATA_LATENCY_DAYS` is computed from the newest *readable* observation (line 259), which is the
honest definition. But gate H compares it to a hardcoded `as_of = 2026-09-06`, so the freshness
certification never expires.

**CODE_VS_VALUE — FAIL.**
The guard executes on 0 of 3 shipped cases. There is no guard in the opposite direction, and I
reproduced **9 of 10** provinces receiving a disease class stamped `OFFICIAL_OBSERVATION` from
the `prodotto` (fungicide-applied) column.

**CROP / ISSUE / REGION NORMALISATION — FAIL.**
3 crops in the data, **0** canonicalised. The output object carries none of the three. And the
ISSUE of one of the three cases is simply wrong: `FRUMENTO-SEPTORIA` collects var 372,
*Intensità Oidio*, in 14 of 14 files.

**GEOGRAPHY — NOT INVENTED, BUT NOT COMPLETE.**
No inheritance: I confirm 0 provinces acquired a neighbour's class. The unit is the source's own
`nome_area`. **However**, 5 of Tuscany's 10 provinces are absent from the wheat output entirely
rather than published UNKNOWN, and 30 rows of 120,133 disagree with the ISTAT code in their own
row, which nothing cross-checks. Geography is honest and unverified.

**NEGATIVE CONTROLS — PASS.**
6 of 6 refusals and out-of-season UNKNOWNs verified by me, 0 false positives. False-negative
rate **NOT KNOWN**: settling it needs an independent register of olive-fly and oidio pressure in
Tuscany by province and date, which this repository does not contain and which the source under
test cannot supply about itself.

**ADAMA_PRODUCT_RELATION for OLIVE × OLIVE FRUIT FLY — NOT_FOUND, correct, and NOT stated at
the width measured.**
0 of 2,030 pairs name the olive fruit fly; 1 of 2,030 touches the olive crop and it is a
herbicide. The claim is true and understated: `p10` cites 3 products when the repository
supports a statement over 102.

**DOES THE AGRONOMIC MEASUREMENT SURVIVE — PARTLY, AND NOT AS A REASON TO ACT.**
The arithmetic survives: I reproduced the 1,168 / 469 / 34 headline decomposition and RT1
reports 750 of 750 cells matching on an independent transcription. The direction survives: 8 of
9 published provinces read LOWER against an exchangeability expectation of 2.13. What does not
survive is the implication of the word *damaging*: **0 of 476** monitored sites reach the
source's own yellow band and **0 of 476** reach red, so LOWER_THAN_USUAL compares two states the
source itself paints as requiring no action.

---

# PART 3 — THE THREE QUESTIONS, SEPARATED

## (a) Is there a real phenomenon in the data? **YES.**

Twenty-one seasons of official field scouting (2006-07-17 to 2026-09-04, 317,004 olive rows)
show a genuine, replayable departure from exchangeability in the 28-day window ending
2026-09-06: 8 of 9 province-cells rank LOWER where chance supplies 2.13, and RT1's independent
282-cell sample finds LOWER at 79 observed vs 46.0 expected with no draw in 20,000 reaching 79.
Provinces genuinely disagree with each other (18 season-cells in the walk-forward), so the
provincial unit is doing work a national figure could not. The phenomenon is **"how this
season's scouting ranks against the same calendar window in its own past, by province"** — and
it is real.

Two limits belong to the phenomenon itself, not to the instrument. First, only the LOWER arm
carries excess over chance; HIGHER fires at 36 where chance gives 36.5. Second, everything
measured on 2026-09-06 sits inside the source's no-action band, so the real phenomenon is
*quiet season*, not *pressure event*.

## (b) Is the INSTRUMENT sound? **NO.**

It refuses well (6 of 6 negative controls), it keeps its unknowns honest where it sees data, it
never reads the clock, and its latency definition is right. Against that: it publishes a
disease class from a spray-diary column; its code-vs-value guard runs on 0 of 3 cases; it joins
its denominator on a key that collides 2,443 times in 52,250 and lets the filesystem break the
tie for 476 rows in 79,251; it carries no crop, no issue and no region in its output; one of its
three cases has the wrong disease in the box; it drops whole provinces from the output instead
of publishing them UNKNOWN; and one refresh on a cp1252 machine takes a case offline
permanently. These are defects of construction, not of interpretation.

## (c) Is the CERTIFICATION sound? **NO.**

Its own suite returns 8 PASS / 2 FAIL / `DESERVES = NO` and it says so plainly — that much is
honest. But the suite cannot do the job its name claims: 5 of 5 mutations I wrote survived, 3 of
them destroying the exact property a gate names, and one of them *improved* the score. One gate
cannot pass at all. One gate's evidence sentence is a measurement of a different quantity. And
the committed numbers do not reproduce from the committed code.

The certification's virtues should be recorded too, because they are unusual: it withdrew its
own `EFFECT_FLOOR = PROVED`, it conceded three red-team findings in one commit, it published
`p3b_cutoff_correction.json` correcting its own mutation against itself, and it committed a
`.gitignore` note explaining that excluding a script while publishing its number is the exact
defect it exists to catch. It also over-corrected once: its retraction of the effect floor as "a
plain incidence threshold of 0.41" does not survive a wider sample.

**A NO on (b) and (c) is not a NO on (a).** The phenomenon is in the archive and it can be
measured. What cannot yet be trusted is this build of the measuring device, and this build of
the device that measures the device.

---

# PART 4 — VERDICT

# NOT_YET

The hypothesis is alive. The instrument does not close.

Against the stated bar for YES_SCOPED, the failures are: the clean checkout does not reproduce;
gate J cannot pass and gate B cannot fail on its subject; mutation testing does not work; the
effect is not proved; refresh does not fail closed; latency is factual but its certification is
frozen; a code table becomes a severity ladder; the crop is not canonicalised and one issue is
misnamed. Any one of these forbids YES_SCOPED. There are eight.

It is not NO. NO would require the phenomenon to be unrecoverable, and it is not: 21 seasons of
official scouting are on disk with a verified hash chain, the class direction is correct against
the raw table, the departure from exchangeability in the LOWER arm is large and replayable, the
negative controls fire, and every defect above has a bounded, mechanical fix.

## What is missing, in the order it must be done

1. **Make the denominator join deterministic.** Key on `(file_year, id_survey)`, or on whatever
   tuple the source guarantees unique, and fail loudly on a collision. Until this is fixed no
   certification number is stable: 2,443 of 52,250 keys conflict and 476 of 79,251 rows move on
   file order alone. Everything below is unmeasurable before it.
2. **Fix the two gates that cannot move.** Gate J must have a reachable PASS and must read the
   inventory from a repository-relative path, not `/home/user/...`. Gate B must compare the
   published cells with and without the cutoff *at the same AS_OF* — the counterfactual it uses
   today measures the lower bound of the window.
3. **Re-run mutation testing until it kills.** The bar is: each gate must FAIL under a mutation
   that destroys the property it names. AM1, AM2 and AM3 in this ruling are three that must go
   red and are currently green. Add gates for the two properties nothing owns — date integrity
   and provenance integrity (AM4, AM5).
4. **Rename the wheat case, or collect var 382.** `FRUMENTO-SEPTORIA-TOSCANA` measures
   *Intensità Oidio*. Either the box gets the right label or it gets the right disease. This
   needs no recomputation, only a decision.
5. **Add the guard in the missing direction.** An ORDINAL variable whose code table is a nominal
   list must be REFUSED, not ranked. The test that would have caught it: if the resolved scale
   has fewer than 2 distinct ordinals, or resolves under half its codes, refuse. Today it
   resolves 1 of 8 and publishes.
6. **Publish the absolute band beside the class.** The engine has the source's own legend in its
   metadata and does not print it. "LOWER_THAN_USUAL, and 0 of 476 sites are above the source's
   lowest action band" is the honest sentence; the class alone is false precision.
7. **Put the effect floor in `PARAMS` and in the sensitivity grid**, then re-run gate F. A
   parameter the stability test never varies has never been tested.
8. **Give refresh a state.** `REFRESH_ATTEMPT_AT`, `REFRESH_STATUS`, `LAST_GOOD_OBSERVATION_AT`,
   `COLLECTED_AT`. Merge the index instead of rebuilding it, so the hash chain does not shrink
   in silence. And write with `encoding="utf-8"` so the sha256 matches the bytes on disk.
9. **Carry the identity in the object.** `COUNTRY`, `REGION`, `CROP`, `ISSUE` alongside `AS_OF`,
   with the crop canonicalised to the portal's vocabulary. Emit every province of the region,
   including those with zero rows, as `UNKNOWN_NO_DATA`.
10. **Unfreeze the certification clock.** Gate H must compare latency to a real `now`, or the
    suite must refuse to certify freshness at all.
11. **Then, and only then, re-run the suite from a clean clone** and require the committed
    artefacts to be byte-identical to what that clone produces.

Two things must be settled by evidence this repository does not contain, and no amount of
further work on the code will settle them:

- **The false-negative rate is NOT KNOWN.** It needs an independent register of olive-fly and
  oidio pressure in Tuscany by province and date. The source under test cannot referee itself.
- **Whether a HIGHER call means anything is NOT KNOWN.** In the walk-forward, HIGHER fires 36
  times where chance supplies 36.5. Settling it needs either an outcome series (damage, yield,
  treatment decisions) to validate against, or a stated decision rule that only uses the LOWER
  arm, which is the arm that carries a real excess.

---

# PART 5 — SCOPE, IF ANY OF THIS IS CARRIED FORWARD

Nothing here is cleared for publication. This scope describes only what the evidence in this
repository can support once the eleven items above are done — not what may be shown to anyone
today.

**PROVED_COUNTRIES** — Italy, and only through one regional source. 1 country, 1 source.

**PROVED_REGIONS** — Toscana only. 10 provinces named in the archive: Arezzo, Firenze,
Grosseto, Livorno, Lucca, Massa-Carrara, Pisa, Pistoia, Prato, Siena. Typically 8 of 10 clear
the publication gate on the olive case; 5 of 10 appear at all on the wheat case.

**PROVED_CROPS** — Olive (`OLIVO`) alone, and only for the walk-forward-discriminating case
(dominant-class share 0.432 ≤ 0.75). Vine (`VITE`) is **NOT PROVED**: 0.806 > 0.75 on gate G
and 0.596 < 0.80 on gate F's own stability threshold. Wheat (`FRUMENTO`) is **NOT PROVED**: no
gate rests on it and its issue is misnamed.

**PROVED_ISSUES** — *Bactrocera oleae*, damaging infestation (var −1002), on olive. One issue.
Oidio on vine is not proved. Septoria on wheat was never collected. Oidio on wheat is measured
and unlabelled.

**PROVED_DATE_RANGE** — observations 2006-07-17 .. 2026-09-04 for olive (21 seasons);
2006-05-02 .. 2026-09-07 for vine (20 seasons); 2013-04-23 .. 2026-06-17 for wheat
(14 seasons). Statements are proved only for a 28-day trailing window ending at an explicit
AS_OF inside the scouting season. Outside it the instrument correctly returns 10 of 10 UNKNOWN,
and that is not a result about the field.

**PROVED_SOURCE_TYPES** — one unauthenticated public REST endpoint,
`agroambiente.info.regione.toscana.it/agro18/api/dati/get_aedita_data`, serving official field
scouting only. `EvidenceRole = OFFICIAL_OBSERVATION`. One source, one schema family.

## NOT_PROVED

- **Forecasting of any kind.** EARLY_WARNING, PRE_SEASON_OUTLOOK, NEXT_SEASON_OUTLOOK. This is
  detection of what scouts already recorded, and its own answer sheet says so.
- **MULTI_YEAR_TREND.** Confounded with monitoring era; the pilot itself records the retraction.
- **Any statement about fields nobody visited.** The panel is the monitored network, not a
  random sample of Tuscany's area.
- **Any HIGHER_THAN_USUAL call.** 0 published in 2026, and no excess over chance in the
  walk-forward.
- **Italy beyond Toscana.** An Abruzzo directory exists; no gate and no engine path reads it.
- **Any other crop, any other issue, any other region, any other source.**
- **Any commercial reading.** `ADAMA_PRODUCT_RELATION = NOT_FOUND` on the one cell that passes
  the agronomic gate: 0 of 2,030 label-use pairs in this repository name the olive fruit fly.
  A disease-pressure signal is not an opportunity, and this instrument may not make it one.
- **Portal integration.** `PORTAL_INTEGRATION = NO`, and gate J additionally reports a coverage
  inversion — the portal already ships provincial vine × Toscana field-pressure cases, the very
  cell this capability is not proved on, and has no vocabulary for the olive cell it can measure.

---

*Ruled at HEAD `098b4de`. Every number above was produced by a command I ran, in the runs
described. Where I disagree with the certification (the effect-floor equivalence) and where I
disagree with the red team's framing (none materially; RT1–RT6 reproduced on every point I
re-ran) I have said so and shown the number. Where the answer is not in this repository —
false-negative rate, the meaning of a HIGHER call — I have written NOT KNOWN and said what
would settle it.*
