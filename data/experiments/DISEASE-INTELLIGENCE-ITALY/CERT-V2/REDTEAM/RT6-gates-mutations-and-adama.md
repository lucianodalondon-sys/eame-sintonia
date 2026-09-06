# RT6 — MUTATION / TAUTOLOGY AND ADAMA PORTFOLIO

Independent red team. I did not write `ENGINE/gates.py` and I did not write `CERT-V2/p3_mutation.py`.
Everything below was re-measured on this checkout. Nothing in `ENGINE/`, `CASES/` or
`italia-portale/` was modified; nothing was deployed or committed.

Scripts are all under `CERT-V2/REDTEAM/` and each writes its own JSON next to it:

| script | what it does |
|---|---|
| `rt6_mutate.py` | five NEW mutations (R01–R05), one process each, shipped `gates.evaluate()` unchanged |
| `rt6_gate_b_cutoff.py` | gate B: future rows, cutoff removal, gate B's own counter recomputed under M03 |
| `rt6_gate_d_zero.py` | gate D: what the UNKNOWN counter counts, and whether `Missing.NEVER_ZERO` can raise |
| `rt6_gate_e_order.py` | gate E: the predicate's shape, and whether M27 changes any published byte |
| `rt6_gate_f_any.py` | gate F: per-province label stability on the full 135-point grid |
| `rt6_gate_j_verdict_space.py` | gate J: both branches executed, the set of reachable verdicts |
| `rt6_mutation_validity.py` | replays M20, M22, M23, M24, M26, M27 and measures the diff each makes |
| `rt6_adama_portfolio.py` | what the handoff adjudicates; the portfolio denominator; signal→opportunity |
| `rt6_adama_link_state.py` | re-derives all 43 shipped `PRODUCT_LINK_STATE` values through the handoff |
| `rt6_adama_olive_bigger_reading.py` | asks the 2,030-pair corpus the olive-fly question |
| `_rt6_v21_vocab.py` | crop/target vocabulary of the 2,030-pair corpus (support for the above) |

Headline: **five new mutations, five survivors.** Gates A, C, F, H and I — the five the
certification reports as healthy — all failed to detect an attack aimed squarely at what each
one claims to protect. Gate J cannot return PASS at all. The certification's own M03 and M07
survivals reproduce, M27's survival is guaranteed by construction rather than measured, and one
of the certification's mutations (M20) is a **no-op on the olive case**, which is the case the
whole delivery rests on.

---

## 1. GATE TABLE A..J

`CAN_IT_FAIL` / `CAN_IT_PASS` = is there any input to the predicate as written that produces
that verdict.

| gate | CAN_IT_FAIL | CAN_IT_PASS | MY VERDICT | reason, one line |
|---|---|---|---|---|
| A OUTCOME_IS_OBSERVED | YES (M01, M02) | YES | **BLIND** | it checks the role STRING and the variable ID; R05 replaced every one of 79,251 + 35,065 observed values with a calendar model and A stayed PASS |
| B NOT_SOLD_AS_FORECAST | YES (M15, M16 → NOT_TESTABLE) | YES | **BLIND** | `load_bearing` compares two runs that are BOTH mutated, so deleting the upper bound cannot drive it to 0; one of its four conjuncts (`CUTOFF_LABEL == "NOWCAST"`) is still arithmetically incapable of being False |
| C REGIONAL_NOT_NATIONAL | YES (M04, M05, M11) | YES | **BLIND** | the verdict reads `hind_disagree` (history) only; `disagreeing` (today's published cells) is computed and never used — R01 published one class per case and C printed "0/2 cases today" beside PASS |
| D UNKNOWN_IS_VISIBLE | YES (M06) | YES | **BLIND** | it counts whether ≥1 UNKNOWN exists, not whether the cells that should be UNKNOWN are; one appended fake cell satisfies it (M07 reproduced) |
| E REPRODUCIBLE | only under intra-process non-determinism (M08, M09) | YES | **TAUTOLOGICAL** | the predicate is `json.dumps(f(x)) == json.dumps(f(x))` inside one process; every deterministic defect passes it by construction |
| F LABEL_NOT_PARAMETER_ARTEFACT | YES (M10, M24) | YES | **BLIND** | `any(v >= 0.8)`, not `all`; R02 drove one case's label stability to 0.000 and F printed `{'OLIVO': 0.924, 'VITE': 0.0}` beside PASS |
| G DISCRIMINATES_BETWEEN_SEASONS | YES (it is failing now, 0.806 > 0.75) | YES (M12 positive control) | **VALID** | the only gate in the set with a demonstrated fail AND a demonstrated pass on the property itself |
| H REFRESHABLE_WITHOUT_RESEARCH | YES (M13, M14, M15, M16, M21) | YES | **BLIND** | it counts reachability, row deltas and non-null columns, never identity; R04 answered both refreshes with the OLIVE series and H reported "2/2 reachable, row counts held or grew" |
| I GENERALIZES | YES (M17, M18) | YES | **BLIND** | it checks the SHAPE of a returned dict (≥5 seasons, >1 distinct value); R03 replaced `season_outcomes` with a stub that never opens the case and I printed `scale derived by ['STUB_NEVER_READ_THE_CASE']` beside PASS |
| J NOT_DUPLICATE | YES | **NO** | **CANNOT_PASS** | `jv[0]` is assigned from exactly two literals, `FAIL` and `"PARTIALLY_OVERLAPS"`; the second maps to NOT_TESTABLE. PASS is unreachable, and the numbers it computes never enter the verdict |

---

## 2. ACCUSATIONS

### A1 — Gate B cannot detect the removal of its own cutoff (the certification's M03 claim, verified)

**CLAIM.** The certification reports M03 (`_window_value`'s upper bound moved to 2100-01-01) as
SURVIVED. It survives, and the reason is structural, not incidental: gate B's `load_bearing`
counter compares `live[name]` against `cp.current_pressure(..., as_of + 30d)`. Under the
mutation **both** sides are computed with the cutoff removed. The difference that remains is the
30-day shift of the window START (`lo`), which M03 never touches. No possible removal of the
upper bound can drive that counter to zero.

**METHOD.** `CERT-V2/REDTEAM/rt6_gate_b_cutoff.py` (out: `rt6_gate_b_cutoff.json`).

**REPRODUCED: YES.**

**NUMBERS.**
- Rows dated after the cutoff: **15 of 35,065** vine rows (all `2026-09-07`, Firenze and Siena),
  **0 of 79,251** olive rows. All 15 are inside the 28-day window, all 15 are readable, all 15
  survive the denominator guard. The certification's "15 … 15 of them inside the published
  window" is exact.
- Removing the cutoff changes the class of **5 of 10 vine cells** (Arezzo, Firenze, Grosseto,
  Pistoia, Siena — all `TYPICAL_FOR_THE_DATE` → `LOWER_THAN_USUAL`) and **1 of 10 olive cells**
  (Massa-Carrara, `TYPICAL` → `LOWER`). **6 of 20 published cells.** The certification's
  "5 of 10 vine cells" is exact.
- Only **2 of those 5** vine cells gain any data of their own (Firenze 74 → 80 visits, Siena
  81 → 90). The other **3 of 5** flip because the BASELINE windows also lose their upper bound
  and stretch to 2100. Removing the cutoff corrupts the comparison, not just the numerator.
- Gate B's predicate recomputed with M03 live: `fut=15, used_fut=15, load_bearing=18,
  all_labels_NOWCAST=True` → **PASS**.
- All 6 changed cells move TOWARDS `LOWER_THAN_USUAL`. The undetected failure mode is
  under-alarming.

**Two further defects inside gate B.**
1. `Cutoff.label()` returns `"FORECAST"` only when `issue_date < target_window_start`, i.e.
   `as_of < as_of - (window-1)`, which is impossible for any positive window. Gate B's own
   comment says this exact test "was arithmetically incapable of FAIL" — and the rewrite kept it
   as one of the four conjuncts.
2. `contracts.Cutoff.assert_no_day_leakage` exists and is **never called** anywhere in
   `current_pressure.py` (measured: `"assert_no_day_leakage" in src` → `False`). The engine ships
   a day-leakage guard and does not run it.

**IMPACT: MAJOR.** **WHAT_SURVIVES:** the measurement that 15 future-dated rows exist and that
the cutoff, when present, changes 6 of 20 cells. The claim in gate B's EVIDENCE string — "this
gate can detect its removal" — is false.

---

### A2 — Gate D counts one UNKNOWN and calls it a property (the certification's M07 claim, verified)

**CLAIM.** M07 v3 survives, and gate D's evidence cites an assertion that cannot raise.

**METHOD.** `CERT-V2/REDTEAM/rt6_gate_d_zero.py` (out: `rt6_gate_d_zero.json`).

**REPRODUCED: YES.**

**NUMBERS.**
- Shipped output on 2026-09-06: olive **10** province cells (8 LOWER, 1 TYPICAL, 1 UNKNOWN_NO_DATA);
  vine **10** cells (5 TYPICAL, 4 LOWER, 1 UNKNOWN_NO_DATA). The UNKNOWN is Prato in both cases.
- M07 v3 rewrites **1 of 1** UNKNOWN cell per case as `VALUE 0.0 / LOWER_THAN_USUAL` — 100 % of
  the cells the property applies to, but **2 of 20** published cells — and appends **1** synthetic
  `_ALIBI` cell per case. Gate D's counter then sees `{olive: 1, vine: 1}` → **PASS**.
- `Missing.assert_not_coerced_to_zero` has exactly **one** live call site,
  `ENGINE/current_pressure.py:274`, and it is called with two constants:
  `Missing.assert_not_coerced_to_zero(Missing.NOT_KNOWN, None)`. Probed: `(NOT_KNOWN, None)` →
  no exception; `(NOT_KNOWN, 0.0)` → raises; `(NOT_KNOWN, 0)` → raises;
  `(INSUFFICIENT_DATA, 0.0)` → raises. **The shipped call can never raise, for any input.**
  The other call site, `contracts.py:279`, is inside `OutcomeRecord`, which the engine's own
  docstring says no runner imports.

**IMPACT: MAJOR.** Gate D's headline sentence "Missing.NEVER_ZERO is asserted on every empty
cell" is literally true (the call happens) and operationally empty (it cannot fail). FAILURE ≠ ZERO
is documented, not enforced, on the published path.

**WHAT_SURVIVES:** the UNKNOWN cells are real and are published — Prato is genuinely visible in
both cases today.

---

### A3 — Gate E certifies that a function equals itself

**CLAIM.** Gate E's predicate compares `live` (computed earlier in the same `evaluate()` call)
with a fresh `current_pressure()` a few lines later, in the same process. Under any deterministic
mutation both sides carry the mutation, so they agree. M27's SURVIVED is therefore guaranteed
before it is run, and says nothing about file order; M09's KILLED only shows that an
*advancing* random generator makes two calls disagree.

**METHOD.** `CERT-V2/REDTEAM/rt6_gate_e_order.py` (out: `rt6_gate_e_order.json`).

**REPRODUCED: YES.** Gate E's exact predicate recomputed with M27 in force: `a == b` → **PASS**.

**NUMBERS.**
- M27 (glob order reversed) **does** change the published output: **3 of 10** olive cells change
  their published `BASELINE_MEDIAN` (Arezzo, Grosseto, Livorno); 0 of 10 change STATE, VALUE or
  `n_visits`. The vine case is byte-identical under every order (it declares no
  `DENOMINATOR_VAR`, and `load_rows` already uses `sorted(glob.glob(...))`).
- So the certification's earlier statement "0 of 10 province cells change class with file order"
  is true and **incomplete**: 3 of 10 olive cells change a published number that a reader sees as
  "the usual level".
- Gate E's own evidence sentence, "every raw file sha256-checked against the collection index",
  is supported for the files these two cases load: **21 of 21** olive files and **20 of 20** vine
  files carry a recorded sha256, and 0 files on disk are absent from the index. Gate E itself runs
  no hash check; the sentence describes `load_rows`.

**IMPACT: MAJOR** for the gate, **NONE** for the sha256 sentence.
**WHAT_SURVIVES:** the hash chain over the loaded files is complete. Cross-machine
reproducibility is simply not what gate E measures.

---

### A4 — Gate J cannot pass, and its analysis is discarded

**CLAIM.** Gate J is a file-existence check wearing a duplication analysis.

**METHOD.** `CERT-V2/REDTEAM/rt6_gate_j_verdict_space.py` (out:
`rt6_gate_j_verdict_space.json`). Both branches executed.

**REPRODUCED: YES.**

**NUMBERS.**
- Literals ever assigned to `jv[0]`: **2** — `FAIL` and `"PARTIALLY_OVERLAPS"`. The mapping
  `jv[0] if jv[0] in (PASS, FAIL, NT) else NT` sends the second to NOT_TESTABLE.
  **Reachable verdicts: {FAIL, NOT_TESTABLE}. PASS is unreachable.**
- The counts the gate computes — 43 cases, 17 `O1_FIELD_PRESSURE`, 3 vine × Toscana at
  provincial scope, 0 olive TARGETs — are correct and **never enter the verdict**. A portal with
  zero overlapping cases would still return `PARTIALLY_OVERLAPS` → NOT_TESTABLE.
- `evaluate()` grants `DESERVES_FUTURE_INTEGRATION = YES_SCOPED` only when `n_fail == 0 and
  n_pass >= 8`. Gate J can never contribute a pass, so the headline is decided by nine gates
  while presented as ten.

**IMPACT: MAJOR.** **WHAT_SURVIVES:** the coverage-inversion observation itself is factually
right, and it belongs in prose. It is not a gate.

---

### A5 — Five new mutations, five survivors (gates A, C, F, H, I)

**METHOD.** `CERT-V2/REDTEAM/rt6_mutate.py`, one process per mutation, shipped
`gates.evaluate()` called unchanged, results in `R01.json` … `R05.json`.
(`gates.py` resolves its cases as the relative path `"../CASES/…"`, so `evaluate()` only runs
from a directory that is a sibling of `CASES`; the driver `chdir`s to `CERT-V2` and records it.)

Every one of the five reports the same suite total: **PASS 8 / FAIL 2 / NOT_TESTABLE 0**
(G and J failing), `DESERVES_FUTURE_INTEGRATION = NO`, `CHANGED_GATES = []`.

| id | gate | property destroyed | outcome | the gate's own evidence, quoted from the run |
|---|---|---|---|---|
| R01 | C | on 2026-09-06 every classified province of a case is given the modal class — the published product is a national number wearing province labels. History untouched. | **SURVIVED** | "provinces … carry DIFFERENT classes in 16 season-cells of the walk-forward, and in **0/2 cases today**" — beside PASS |
| R02 | F | the vine case's label stability forced to 0.000 across the whole 135-point grid; olive untouched | **SURVIVED** | "mean label stability {'OLIVO…': 0.924, **'VITE…': 0.0**}" — beside PASS |
| R03 | I | `run_case.season_outcomes` replaced by a stub that never opens the unseen case and returns 14 fabricated seasons | **SURVIVED** | "14 seasons, 13 distinct SITE_INCIDENCE values … scale derived by **['STUB_NEVER_READ_THE_CASE']**" — beside PASS |
| R04 | H | every live refresh of a real case answered with the OLIVE series whatever was asked for; negative control untouched | **SURVIVED** | "2/2 probes reachable … row counts held or grew" — measured: vine delta **+413** (2,928 olive rows against 2,515 stored vine rows), olive delta 0, control still trips |
| R05 | A | every observed value replaced by a deterministic sinusoid of the day-of-year — a pure calendar model — with the role, the variable id and all four refusals left in place | **SURVIVED** | "four inadmissible inputs … [REFUSED ×4]" — beside PASS |

**REPRODUCED: YES** (five independent runs).

**IMPACT.**
- R05 / gate A — **FATAL to the gate's stated subject.** `current_pressure`'s own docstring says
  "Fed a rainfall series it would have stamped a weather model's number as an official field
  observation and passed its own gate A", and presents `assert_outcome_admissible` as the fix.
  The fix checks the role string and that the variable id is in `idx["vars"]`. It never looks at
  the numbers. R05 is that exact scenario with the paperwork in order, and gate A passes.
- R02 / gate F — **MAJOR.** Measured on the shipped data (`rt6_gate_f_any.py`), without any
  mutation: **8 of 18** classed province cells are already below `STAB_MIN = 0.80` —
  1 of 9 olive (Massa-Carrara 0.644) and **7 of 9 vine** (Massa-Carrara 0.207, Livorno 0.215,
  Lucca 0.259, Pistoia 0.489, Grosseto 0.630, Pisa 0.674, Firenze 0.778). Gate F says PASS with
  `any`; written as `all`, the same numbers give **FAIL**. Gate H's own docstring records that a
  list-truthiness-instead-of-`all()` bug was found and fixed there. It is still in F.
  Gate F's evidence also says "cells below 0.8 are withheld rather than published": the
  withholding set lives in `answer_sheet.publishable`, `gates.evaluate()` computes `sheets` and
  **never reads it** (the token `sheets` appears twice in `gates.py`, both on the assignment
  line), and `current_pressure.py` does not contain the string `STAB_MIN` at all.
- R01 / gate C, R03 / gate I, R04 / gate H — **MAJOR** each.

**WHAT_SURVIVES:** every one of these gates can still fail — M01/M02, M04/M05, M10/M24,
M13–M16, M17/M18 all kill their targets. They are not tautologies. They are narrower than their
sentences.

---

### A6 — A remaining no-op in the certification's own mutations: M20 never runs on the olive case

**CLAIM.** `p3_mutation.m20_values_replaced_by_code_ids` says "Every observed value is replaced
by an identifier from the source's own code table" and its recorded outcome is
`UNDETECTED_BY_SUITE`. On the OLIVE case it replaces nothing.

**METHOD.** `CERT-V2/REDTEAM/rt6_mutation_validity.py` (out: `rt6_mutation_validity.json`),
plus a direct read of both collection indexes.

**REPRODUCED: YES.**

**NUMBERS.**
- `OLIVO-BACTROCERA-TOSCANA/collection_index.json` carries **0 code entries**. `m20` builds
  `ids = [...]` from that list and guards the loop with `if ids:` — so **0 of 79,251** olive
  values are replaced. The whole olive output is byte-identical to the unmutated run
  (`whole_case_json_identical: true`, 0 of 10 cells touched).
- On the vine case it does work: **35,065 of 35,065** values replaced, **8 of 10** cells change
  STATE, latency 2 → 4 days.
- So M20's `UNDETECTED_BY_SUITE` is a statement about **one** of the two cases, and the silent one
  is the case the delivery's headline rests on.
- Second-order finding from the same measurement: OLIVO's `VALUE_MODE` is **NUMERIC** (no code
  table). `assert_scale_decodes` — the guard whose docstring says it is "PAID FOR BY the first
  case this pipeline was not built for" — begins `if not code_ids: return`. **On the olive case
  it can never fire**, because there are no code ids to compare against. The CODE-IS-NOT-VALUE
  guard is structurally inert on the one case that qualifies.

**IMPACT: MAJOR.** This is the same class of defect the certification already withdrew three
mutations for (m07 v1, m07 v2, m10 v1), and it is still in the shipped set.

**WHAT_SURVIVES:** the other five mutations I replayed are genuine, with their diffs measured on
20 published cells: M22 (dates +365) touches **20 of 20** cells, 16 of 20 change class;
M23 (source url + hashes removed) touches **18 of 20** and blanks the top-level `SOURCE` on both
cases; M24 (signal inverted) touches **18 of 20**, 10 of 20 change class; M26 (evidence link
broken) touches **18 of 20** (the 2 untouched are the UNKNOWN cells, which carry no `EVIDENCE`
key); M27 touches **3 of 20**.

---

## 3. ERRORS IN THE CERTIFICATION ITSELF

**E1 — `ENGINE/gates.json`, a committed artefact, is not reproducible from this repository.**
Gate J reads the hard-coded absolute path
`/home/user/eame-sintonia/italia-portale/client/meeting-intelligence-snapshot.json`. On this
checkout that resolves to `C:\home\user\...` and does not exist, so the shipped gate takes the
`FAIL, "inventory not readable"` branch. The committed `gates.json` records
`J = NOT_TESTABLE`, `PASS 8 / FAIL 1 / NOT_TESTABLE 1`. This checkout produces
`J = FAIL`, `PASS 8 / FAIL 2 / NOT_TESTABLE 0`. `git status` shows `gates.json` unmodified, so
this is the committed state, not local drift. All 28 mutant records and all five of my runs
report `J = FAIL`, and `p3_mutation.BASELINE` correctly hard-codes `J_NOT_DUPLICATE: "FAIL"` —
so the certification already knows, and the artefact was not regenerated. The headline
(`DESERVES_FUTURE_INTEGRATION = NO`) is unaffected; the per-gate line is wrong.
A byte-identical copy sits at `italia-portale/client/meeting-intelligence-snapshot.json` and M19
already proves the gate would run against it. This is the same defect the certification itself
recorded for gate I ("the evidence used to live in /tmp/WHEAT4 — outside git").

**E2 — `MUTANTS/M28.json` was a stale artefact recording an error, and was repaired while I
worked. Recorded for the record, then withdrawn.** When I first read it (18:12) it said
`OUTCOME: "MUTATION_RAISED", ERROR: "KeyError: 'SPECIFICITY'"` — `p3_mutation.py` had been
edited at 18:07 to add the `if target == "SPECIFICITY"` branch and `M28.json` still carried the
18:04 crash. It was regenerated at 18:14, concurrently with this review, and now correctly reads
`OUTCOME: "SPECIFICITY_OK"`, `CHANGED_GATES: []`. **No longer an error. IMPACT: NONE.** I leave
the entry in because the timestamps are the only evidence that the specificity control had no
valid recorded result for part of the certification's life.

**E3 — `MUTANTS/M25.json`: the suite crashes rather than failing when the archive is empty, and
the crash site is gate F.** `SUITE_CRASHED_NO_VERDICT`,
`TypeError: '>=' not supported between instances of 'NoneType' and 'float'`. The recorded
traceback names the line: `ENGINE/gates.py:130`,
`"VERDICT": PASS if any(v >= STAB_MIN for v in ok.values()) else FAIL`. `sensitivity()` returns
`MEAN_AGREEMENT = None` when no province is classified, and gate F compares `None >= 0.8`. This
is the same line as A5/R02: the `any(...)` that should be `all(...)` is also the line with no
None-guard. The certification records the outcome honestly; the engine still has no verdict for
"the source went dark", which is a state a live tool will eventually be in.
**IMPACT: MAJOR** (engine), **NONE** (certification's record of it).

**E4 — the certification's file-order finding is understated by one number.** `p1_order_experiment.json`
says "0 of 10 province cells change class with file order on 2026-09-06". True. It does not say
that **3 of 10** olive cells change their published `BASELINE_MEDIAN` between the ascending and
descending orders (measured in `rt6_gate_e_order.json`). The committed headline stability 0.918
is not reproduced here either — this checkout gives **0.924**, matching the certification's own
eight-order sweep, none of which produced 0.918.

**E5 — gate J's phrase "has no words for the cell we can [publish]" is half right.** The portal's
TARGET vocabulary has 0 olive issues (correct: the 9 distinct TARGETs are Botrytis, Downy mildew,
Powdery mildew, Grape moth, Codling moth, Corn borer, Diabrotica, Echinochloa, Scaphoideus). But
it does have `CROP_OLIVE`, on **3 of 43** cases — all national scope, all `TARGET: null`, none of
them `O1_FIELD_PRESSURE`. The inversion is real; the wording overstates it.

**E6 — `gates.evaluate()` computes `answer_sheet` for both cases and never uses it.** `sheets` is
assigned and read nowhere. It is roughly half the six-minute runtime, and it is where the
publication threshold (`STAB_MIN`/`COV_MIN`) actually lives — see A5/R02.

---

## 4. ADAMA PORTFOLIO

### What the handoff actually adjudicates

`italia-portale/client/italy-label-verdicts.js`, read directly (`rt6_adama_portfolio.py`):

- The unit is a **PRODUCT × CROP × ISSUE triple**, keyed `crop|issue|product`. Not a product, not
  a pair, not a portfolio.
- **19 triples total: 12 VERIFIED, 7 NOT_FOUND**, covering **10 distinct products** and
  **15 distinct crop × issue pairs**.
- The default for anything not listed is **`LABEL_CHECK_NEEDED`** — the file's own comment says
  "never a promotion".
- Four strength levels are defined; `verdict()` can return **three**. **`RELATED_PORTFOLIO` is
  defined and unreachable** from that function.
- Its own rule: "ABSENCE IN OUR READING ≠ ABSENCE IN THE WORLD."

### A7 — the word substitution is a real (small) overstatement

**CLAIM.** The handoff's verdict for the three olive triples is
`NO_CONFIRMED_MATCH_CURRENT_READING`. `p10_adama_relation.py` declares a three-value vocabulary
(`PROVED / NOT_FOUND / UNKNOWN`) and maps it to **`NOT_FOUND`**, dropping the `CURRENT_READING`
qualifier that the handoff's header exists to protect.

**METHOD.** `rt6_adama_portfolio.py`, section 2. **REPRODUCED: YES.**

**IMPACT: MINOR.** `p10_adama_relation.json` restores the qualifier in four explicit sentences
under `WHAT_THIS_DOES_NOT_SAY`, and `FINAL-DELIVERY-A-R.md:280` states
`NOT_FOUND != DOES_NOT_EXIST`. The field name is stronger than the evidence; the prose around it
is not.

**WHAT_SURVIVES:** the adjudication itself. `TRIPLES_MARKED_NOT_FOUND` = exactly the three rows
in the file; `TRIPLES_MARKED_VERIFIED` = empty. Nothing was invented.

### A8 — the claim is UNDERSTATED: a second, 100× larger reading of the same 163 labels sits unread in this repository

**CLAIM.** `p10_adama_relation.py` reads only the 19-triple file. `italy-app-model.js` says, in
its own comments (around lines 103950, 108200 and 3913):

> "The audit read 163 labels and published 236 relationships. The V2.1 label reader read the same
> labels and published 2.030 crop × target pairs, each carrying the sentence from the label that
> joins them."
> "PRODUCT_LINK_STATE is graded against the 2.030 label pairs; the 12-row audit below is what the
> portal had before those pairs existed."
> "WHEN TWO READINGS DISAGREE, THE ONE THAT READ MORE LABELS WINS."

The certification anchored `ADAMA_PRODUCT_RELATION` on the reading the portal's own model
declares the loser, and never opened the winner.

**METHOD.** `rt6_adama_olive_bigger_reading.py` and `_rt6_v21_vocab.py`, parsing
`italia-portale/client/italy-handoff-v21.js → productRelationships`.

**REPRODUCED: YES.**

**NUMBERS.**
- The corpus holds **2,030 label-use pairs** over **102 products**, **35 crops on label**
  (OLIVO among them) and **342 distinct targets**.
- Pairs on the OLIVE crop: **1 of 2,030** — `MORAINE`, target `malerb` / `INFESTANTI`
  (weeds), registration 018101.
- Pairs naming the olive fruit fly, on any crop: **0 of 2,030**. Of the 342 target strings, the
  only ones matching `mosc|bact|dac|fly|olea` are "Moscerino dei" and "mosca bianca" (whitefly),
  neither on olive.
- The three products the certification named: `KLARTAN 20 EW` **80** pairs, `KLARTAN SMART`
  **88**, `MAVRIK SMART` **91** — **0** of those 259 pairs on OLIVO. Their crops are
  barbabietola, brassicacee, carota, colza, cucurbitacee, erba medica, fragola, leguminose,
  melo, patata, vite.

**IMPACT: MINOR on the conclusion, MAJOR on the method.** The bigger reading **corroborates**
`NOT_FOUND` — it is the strongest possible outcome for the certification and it got there by
luck, not by checking. The stated scope ("three named products … the rest of the portfolio
UNKNOWN") is **too weak** for the evidence this repository holds: a defensible wider sentence is
*"across 102 ADAMA products and 2,030 crop × target label-use pairs read from the same 163
labels, the olive crop appears once — a herbicide use — and the olive fruit fly appears zero
times."* Against that, "three named products" understates by a factor of 34 in products and 107
in pairs. And had the larger corpus contained an olive-fly row, `p10` would have published a
false absence with no way of noticing.

**WHAT_SURVIVES:** `ADAMA_PRODUCT_RELATION = NOT_FOUND` for Olive × Olive Fruit Fly. Two
independent readings of the same labels agree. Nothing here was invented.

### A9 — the shipped portal turns field pressure into commercial opportunity, 17 times

**CLAIM.** `CERT-V2/p11_signal_is_not_opportunity.md` says `COMMERCIAL_OPPORTUNITY` "is not on
this list and this tool may never produce it". That is a guarantee about the CERT-V2 engine. The
destination it hands to already does the conversion.

**METHOD.** `rt6_adama_portfolio.py` section 4, over
`italia-portale/client/meeting-intelligence-snapshot.json`.

**REPRODUCED: YES.**

**NUMBERS.**
- **43 of 43** case IDs are prefixed `OPP_`. **17 of 43** carry `ARCHETYPE:
  O1_FIELD_PRESSURE` ("Pressione in campo").
- **17 of 17** field-pressure cases carry `OPPORTUNITY_STATE: OPPORTUNITY_CONFIRMED`;
  **5 of 17** carry `COMMERCIAL_PRIORITY: SALES_READY`; **13 of 17** name at least one commercial
  product (BANJO, FOLPAN GOLD, Lamdex Extra, MAVRIK SMART).
- `ACTION_RECOMMENDATION_STATE` over the 17: `START_RECOMMENDED` 5, `CONTINUE_RECOMMENDED` 1,
  `SUSPEND_RECOMMENDED` 1, `PROHIBITED_DECLARED` 2, `NOT_NEEDED_DECLARED` 3,
  `CONCLUDED_DECLARED` 2, `RECOMMENDATION_NOT_DECLARED` 3.
- The sharpest instance, quoted: `OPP_F8106D5E1767`, `O1_FIELD_PRESSURE`, `CROP_GRAPEVINE ×
  ISSUE_BOTRYTIS × REGION_TOSCANA`, provincial scope, `PUBLICATION_STATE: PUBLISHABLE`,
  `MATCHED_COMMERCIAL_PRODUCT_NAMES: ['BANJO']`,
  `ACTION_BY_DEPARTMENT.COMMERCIAL = {ACTION: 'CONTACT_NOW', WHY_CODE: 'CADEIA_COMPLETA',
  EVIDENCE: ['CATPRD_BANJO']}`. A field-pressure signal, in Toscana, at provincial scope,
  producing "contact now" with a named product. `OPP_5F31A63F844D` (Emilia-Romagna, same crop and
  issue) is the second.
- Classifier definition, `italia-portale/client/italy-science-business.js:10`:
  `'PORTFOLIO OPPORTUNITY': { … def: 'Evidence strengthens the relevance of a problem for which
  ADAMA has verified portfolio fit.' }`.
- Counter-example, for balance — `italy-real-intelligence.js:43`: "Management-intensity signal.
  No specific disease increase, product demand or ADAMA opportunity inferred." The restraint
  exists in that file.

**IMPACT: MAJOR, and outside the certification's control.** Gate J already notes the portal ships
3 vine × Toscana provincial field-pressure cases. What it does not say is that those cases are
`OPP_` records with `OPPORTUNITY_STATE`, `OPPORTUNITY_SCORE` and departmental actions attached.
`PORTAL_INTEGRATION = NO` is the only thing keeping the CERT-V2 numbers out of that structure.

**WHAT_SURVIVES:** nothing in `ENGINE/` or `CERT-V2/` produces a commercial state. I searched and
found none. `SHADOW_UI_SPEC.md:59` states "R6 — no product placement. No product name, no
recommendation, no 'consider treating'".

### A10 — is "no ADAMA product" read as "this cell does not matter"?

**In CERT-V2: NO.** I could not find it. `p11` says the honest statement is "not a softer one —
and not a harder one either". `p10` forbids both errors explicitly. `FINAL-DELIVERY-A-R.md:280`
says `NOT_FOUND != DOES_NOT_EXIST  nenhuma ausência foi convertida em inexistência`.
`answer_sheet.py` lists `ADAMA_PRODUCT_RELATION` under `8_WHAT_WE_DO_NOT_KNOW / NOT_PROVED`, not
as a filter.

**In the portal: partially, and it is measurable.** `WHY_NOW_CHAIN` has five links and
`VINCULO_COM_PORTFOLIO` (link to the portfolio) is one of them; a case without it collects the
code `SEM_VINCULO_COM_PORTFOLIO`. That code is on **29 of 43** cases. Among the 17 field-pressure
cases, **13** have the portfolio link and **4** do not. Effect on the visible score:
`OPPORTUNITY_SCORE` is 10 or 11 for the linked ones (10 × ten, 11 × three) and 10 for all four
unlinked ones — so the downgrade is **at most 1 point out of 11**, and all four unlinked cases
are still `OPPORTUNITY_CONFIRMED`. The user-facing label for the missing product is
`COMMERCIAL_PRODUCT_MISSING` → "Nessun prodotto del catalogo su questa coppia" / "No catalogue
product on this pair" (`italia-portale/client/meeting-labels.js:183`) — a statement about the
catalogue, not about the world. **IMPACT: MINOR.**

### A11 — the portal's product-relationship field cannot express a negative

**CLAIM.** `PRODUCT_LINK_STATE` is stamped `VERIFIED_LABEL_MATCH` on **42 of 43** cases and
`RELATED_PORTFOLIO` on 1. `meeting-labels.js:164-167` defines exactly those two values and no
third — there is no rendering for "not verified". **11 of 43** cases are stamped
`VERIFIED_LABEL_MATCH` while naming **zero** products (`COMMERCIAL_PRODUCT_COUNT = 0` on 12 of 43;
`PORTFOLIO_MATCHES` empty on 12 of 43), including all **3** olive cases, whose own
`INTELLIGENCE_BRIEF` carries the code `SEM_PORTFOLIO`.

**METHOD.** `rt6_adama_link_state.py` (out: `rt6_adama_link_state.json`).

**CAVEAT I must state.** Re-deriving all 43 through `italy-label-verdicts.verdict()` — with
case-folding and three synonyms granted in the audit's favour (grape moth → grapevine moth,
corn borer → european corn borer, scaphoideus → flavescenza dorata) — gives
**2 VERIFIED_LABEL_MATCH, 29 LABEL_CHECK_NEEDED, 12 with no product to ask about**: agreement on
2 of 43. **That is not by itself proof of overstatement**, because `italy-app-model.js` states
explicitly that `PRODUCT_LINK_STATE` is graded against the 2,030-pair corpus, not against the
19-triple file, and that the larger reading wins. The honest finding is narrower and still real:

1. two readings of the ADAMA product relationship are shipped in one repository and disagree on
   **29 of 43** cases;
2. the certification anchored on the smaller one (A8);
3. the field that renders the result has a two-value vocabulary in which the negative outcome
   cannot be displayed, and is stamped positive on 11 cases that name no product at all.

**IMPACT: MAJOR** (portal), **MINOR** (certification).

### A12 — the commercial framing overstates what the qualifying cell says

**CLAIM.** `p11` and `DISEASE-PEST-CAPABILITY-CONTRACT.md:30` both say, in bold, that "the one
cell that qualifies agronomically is one where our own label reading found nothing to sell". The
phrasing implies there is something to sell against.

**METHOD.** direct measurement, `rt6_gate_d_zero.py` / `rt6_mutation_validity.py` baseline block.

**REPRODUCED: YES.**

**NUMBERS.** On 2026-09-06 the olive cell publishes **8 LOWER_THAN_USUAL, 1
TYPICAL_FOR_THE_DATE, 1 UNKNOWN_NO_DATA — and 0 HIGHER_THAN_USUAL, out of 10 provinces**. The
vine cell publishes **5 TYPICAL, 4 LOWER, 1 UNKNOWN — 0 HIGHER out of 10**. **0 of 20 published
province-cells in the whole certification are above their own baseline.**

**IMPACT: MINOR**, but it is the kind of sentence that travels. The correct reading of the
qualifying cell is "olive-fly pressure in Toscana is at or below its usual level for the date in
9 of the 10 provinces we can speak about". A missing product is not a missed sale when the signal
points down.

**WHAT_SURVIVES:** the measurement. `p11` never claims the direction is up.

---

## 5. WHAT I COULD NOT BREAK

1. **Gate G is a valid gate.** It can fail (it is failing now: vine dominant-class share 0.806
   against a 0.75 ceiling) and it can pass (M12's positive control drives it to PASS). It is the
   only gate in the set with both demonstrated on its own subject.
2. **The refusals in gate A are real refusals.** `MODELLED_RISK`, `FORECAST`, `CONTEXT` and a
   non-survey variable are all rejected by the shipped module, 4 of 4, and M01/M02 kill the gate
   when the refusal is removed. My R05 got past gate A by keeping the paperwork honest and
   corrupting the numbers — it did not get past the refusals.
3. **The sha256 chain over the files these cases load is complete.** 21 of 21 olive files and
   20 of 20 vine files carry a recorded hash; 0 files on disk are missing from the index; a
   mismatch raises inside `load_rows` (M17 proves it end-to-end on the wheat case).
4. **The negative control in gate H is honest and still works.** Variable 50 in crop 3 / schema 8
   returns HTTP 200, `ok:true`, a full 2,515-row skeleton and 0 non-null values, and the detector
   trips on it on every run I made, including under R04.
5. **UNKNOWN really is published.** Prato is `UNKNOWN_NO_DATA` in both cases today, and M06
   (hiding UNKNOWNs) kills gate D.
6. **No CERT-V2 or ENGINE artefact converts a signal into a commercial state.** I searched the
   repository for "opportunit", "recommend", "raccomand", "suggest" and "commercial" and found no
   such conversion inside `ENGINE/`, `CASES/` or `CERT-V2/`. The conversions live in
   `italia-portale/` and predate this work.
7. **No CERT-V2 artefact treats "no ADAMA product found" as "this cell does not matter".** Every
   place I found states the opposite, explicitly.
8. **`ADAMA_PRODUCT_RELATION = NOT_FOUND` for Olive × Olive Fruit Fly is correct.** I attacked it
   from both directions and a second, independent, 2,030-pair reading of the same 163 labels
   agrees: 0 pairs name the olive fruit fly, on any crop, for any of 102 products.
9. **The certification's three self-withdrawn mutations were correctly withdrawn**, and the
   reasoning in their docstrings is right. I found a fourth of the same kind (M20 on the olive
   case) that was not caught.
10. **`p1_order_experiment.json`'s core finding stands.** The order dependence is in
    `denominator_guard`'s unsorted `glob.glob` with last-writer-wins, it affects only the case
    that declares a `DENOMINATOR_VAR`, and the committed 0.918 does not reproduce — this checkout
    gives 0.924, exactly as the certification's own sweep found.
