# RT6 · PRODUCT · independent red team

Lens: can a valid agronomic reading be turned into an invalid commercial conclusion, by
accident, by a Market Development or Sales reader who is not trying to cheat?

I wrote none of this code. Everything below was run against the shipped engine on
`2026-09-06 ACTIVE_INFESTATION_COUNT`, Python 3.12 (`py`). Scripts are in this folder and
named in each METHOD line. Nothing under `engine/`, `CASES/` or `italia-portale/` was
modified; nothing was committed.

Base run: 10 provinces, 1,193 usable visits, 123,799 drupes dissected, window
2026-08-10 → 2026-09-06, ADAMA_RELEVANCE = NO, attention classes
INVESTIGATE 1 / MONITOR 3 / NO_ESCALATION 6 / UNKNOWN 0.

---

## A1 — G10 does not test anything the user receives

**CLAIM.** The tool says the banned vocabulary "is absent by construction, and gate G10
checks it". G10 checks a Python object that `di_report.py` never produces. It does not
look at layer 3, and it does not look at the rendered human text. Applying G10's own word
list, by G10's own method, to the three things a person actually receives, all three FAIL.

**METHOD.** `rt6_g10_coverage.py`. Word list and matching copied verbatim from
`tests/t2_gates.py:314` (uppercase substring). `tests/t2_gates.py:41` builds its cells with
bare `di_observe.cell(...)` — no `adama` key, no `attention` key.

**REPRODUCED: YES.**

**NUMBERS.**

| what was tested | G10 verdict | banned tokens found |
|---|---|---|
| `t2_gates.cells()` — the object G10 actually tests, never shipped | PASS | none |
| `OUT/report_ACTIVE_INFESTATION_COUNT_2026-09-06.json` — the shipped artifact | FAIL | ACT_NOW 20, SALES_READY 10, BUY 10, SELL 10, OPPORTUNITY 10, CONTACT_NOW 10, COMMERCIAL_OPPORTUNITY 10 |
| the layer-3 ADAMA object alone | FAIL | 7 tokens, 1–2 each |
| region card + 10 province cards (the human reading) | FAIL | OPPORTUNITY 22 |

The words come from two honest places: `di_adama.relevance()` returns
`FORBIDDEN_OUTPUTS_NOT_EMITTED = ['ACT_NOW','SALES_READY','BUY','SELL','COMMERCIAL_OPPORTUNITY','CONTACT_NOW']`
and it is stapled to all 10 cells; and `di_render.CANNOT_CONCLUDE` contains
"that there is a commercial opportunity" twice per card. Per cell: ACT_NOW 2 (once
standalone, once inside `CONTACT_NOW` — G10's substring method double-counts),
the rest 1 each, × 10 cells.

**IMPACT: MAJOR.** Not because the words are dangerous here — in context they are
disclaimers — but because the gate's coverage is zero over layer 3 and zero over the
renderer, which is exactly where a commercial sentence would be introduced. G10's own
mutation ("attach an ACT_NOW / SALES_READY block to a cell") is caught only if the block is
attached inside layer 1/2. Layer 3 attaches such a block to every cell today, legitimately,
and G10 never sees it. The gate is proved against a mutation it will never meet.

**WHAT SURVIVES.** The claim "the vocabulary is absent by construction" survives *as a
statement about intent*. The claim "gate G10 checks it" does not survive for any shipped
artifact. Also: no engine file raises or asserts on the vocabulary — the ban is a
convention, not an enforcement (`rt6_injection.py` §5).

---

## A2 — "0 product-label matches for the crop" is asserted, not measured, and it is wrong

**CLAIM.** Every province card prints: *"The wider object set from the same audit carries
11 olive objects and 0 product-label matches for the crop — its olive material is content
and scientific references."* The `0` is a hardcoded literal in a dict. No code counts it.
And it is factually wrong: the handoff contains one olive label-use relationship.

**METHOD.** `rt6_adama_both_ways.py` §3–4, `rt6_handoff_blindspot.py`,
`rt6_olive_label_hunt.py`, `rt6_resolve_itlbl1932.py` (extracts the file's `var P` string
table, 2,277 entries, and dereferences the object).

**REPRODUCED: YES.**

**NUMBERS.**

- `engine/di_adama.py:78` — `"product_label_matches_for_olive": 0,` — a literal. It is read
  back at line 115 and rendered as if measured.
- `italy-handoff-v21.js` is 5,905,630 chars and holds 2,030 distinct `IT-LBL-*` objects.
  **1 of 2,030** carries `CROP_ON_LABEL`: `IT-LBL-1932`.
- Fully resolved, IT-LBL-1932 is:
  `ENTITY_TYPE: LABEL_USE_RELATIONSHIP · PRODUCT_NAME: MORAINE · REGISTRATION_NUMBER: 018101 ·
  CROP_IDS: ["CROP_OLIVE"] · CROP_ON_LABEL: "OLIVO" · ISSUE_IDS: ["ISSUE_WEEDS_GENERIC"] ·
  TARGET_ON_LABEL: "INFESTANTI" · PROVENANCE: REAL_FACT · EVIDENCE_STATUS: EVIDENCE_DOCUMENTED`
  with a quoted label line and a `fitosanitari.salute.gov.it` URL.
- So the true count of product-label matches for the crop is **1 of 2,030**, not 0. It is a
  herbicide for weeds in olive groves, not an insecticide for the fly.
- The engine's scan is also structurally incomplete. Its regex `\{[^{}]*"CROP"...\}` cannot
  match an object containing a nested object or array: it sees **161 of 203** occurrences of
  the `"CROP"` key (79.3%). All 42 it misses are in the `CROP_*` namespace, and **3 of those
  42 are `CROP_OLIVE`**. The sentence "11 olive objects" is 11 in one namespace; there are
  at least 14. `CROP_OLIVE` appears 305 times in the file and `ISSUE_OLIVE_FLY` 12 times.

**IMPACT: MAJOR.** In a tool whose entire claim is "no fact without a measurement", a
rendered integer that no code computed is the exact failure mode it exists to prevent. And
the direction of the error matters commercially: a Market Development reader told "0
product-label matches for the crop" concludes ADAMA has nothing registered on olive in
Italy. ADAMA has MORAINE, registration 018101, on olive.

**WHAT SURVIVES.** The **NO verdict itself survives, and survives a harder test than the
one the engine ran.** I checked directly: of 2,030 label-use relationships, exactly one
names olive, and its target is weeds. No KLARTAN / MAVRIK object in the handoff carries an
olive crop id (the one apparent hit in `rt6_olive_label_hunt.py` is my brace-walker landing
on the top-level string table, not a real object). ADAMA_RELEVANCE = NO for
Olive × Olive Fruit Fly is correct. The verdict is right; the sentence under it is not.

---

## A3 — "NO" is a token the upstream deliberately refused to use, and the region card cuts the caveat off

**CLAIM.** Two compressions, one on top of the other. (1) The label audit's own vocabulary
for these three rows is `NO_CONFIRMED_MATCH_CURRENT_READING`; the engine compresses it to
the single token `NO`. (2) The region card prints `adama['reason'][:200]`, which severs the
entire scoping caveat.

**METHOD.** `rt6_adama_both_ways.py` §5–6; `engine/di_render.py:render_region`.

**REPRODUCED: YES.**

**NUMBERS.**

- `italy-label-verdicts.js` `verdict()` returns `NO_CONFIRMED_MATCH_CURRENT_READING` for a
  NOT_FOUND row. The bare string `'NO'` appears as a verdict value 0 times in that file.
- `adama['reason']` is 444 chars. The region card prints 200. **244 chars are cut**, and
  they are these:
  > *"…ABSENCE IN OUR READING IS NOT ABSENCE IN THE WORLD, and this NO is scoped to the
  > products actually adjudicated, not to the portfolio."*
- The region card's ADAMA line ends mid-word: `…the same audit carries 11 oli`.
- The region-level reader therefore receives the token **NO** and **0%** of the scoping
  caveat. The province cards receive 100% of it — but only 3 of 10 provinces get a card
  (see A6).
- The unprinted denominator: 19 triples were adjudicated (12 VERIFIED + 7 NOT_FOUND) over
  10 distinct product names. 3 of those 10 were checked for Olive × Olive Fruit Fly. The
  sentence says *"3 product(s) were checked"* and never says 3 of what. The handoff carries
  51 distinct `CATPRD_*` product ids; the portal snapshot carries 14.

**IMPACT: MAJOR.** The region card is the artifact an executive skims. It is the only place
the caveat is missing, and it is the place the token travels from.

**WHAT SURVIVES.** In the province cards the caveat is complete, prominent, and in capitals.
`portfolio_evidence` carries `scope_note`, `absence_rule` and
`default_for_anything_not_listed: LABEL_CHECK_NEEDED` in full — they are just never
rendered.

---

## A4 — INVESTIGATE for Lucca turns on 4 olives in 5,300

**CLAIM.** Lucca is the only INVESTIGATE and the only entry under *"a subir nas janelas já
ocorridas"*. Its historical comparison is INSUFFICIENT_DATA, its whole observation is inside
the source's GREEN band at 1.1509%, and its escalation rests on a margin of four infested
olives.

**METHOD.** `rt6_lucca_fragility.py` — remove infested olives from the current window one at
a time; then vary each declared parameter alone.

**REPRODUCED: YES.**

**NUMBERS.** Lucca: 61 infested of 5,300 drupes, 53 visits, 14 groves, **1 organisation**
(the thinnest evidence base of any publishable province, tied with Massa-Carrara). Last
observation 2026-08-31 — 6 days before `as_of`, the stalest of the three rendered cards.
Trend 0.0769% → 0.4464% → 1.1509%, change 1.0740 pp against a declared threshold of 1.0 pp:
a margin of 0.074 pp, or **7.4% over the line**.

| perturbation | trend | attention |
|---|---|---|
| shipped | INCREASING_OBSERVED | INVESTIGATE |
| −3 infested olives (of 61, in 5,300) | INCREASING_OBSERVED | INVESTIGATE |
| **−4 infested olives** | STABLE_OBSERVED | **NO_ESCALATION** |
| `TREND_MIN_ABS_CHANGE_PCT` 1.05 | INCREASING_OBSERVED | INVESTIGATE |
| `TREND_MIN_ABS_CHANGE_PCT` 1.1 | STABLE_OBSERVED | **NO_ESCALATION** |
| `WINDOW_DAYS` 14 / 21 / 35 / 42 | STABLE / STABLE / UNKNOWN / UNKNOWN | **NO_ESCALATION** ×4 |
| `MIN_PANEL_OVERLAP` 2 / 4 / 6 | history becomes TYPICAL | INVESTIGATE |

**4 of the 5 tested window lengths produce no escalation.** At
`TREND_MIN_ABS_CHANGE_PCT = 1.1` the whole region report's *"a subir"* list is empty and
INVESTIGATE count is 0 of 10.

**Is INVESTIGATE honest?** Arithmetically yes — the rule fired as printed and the rule is
printed. Editorially no, for three reasons, and they compound:

1. It is printed **inside the block headed `RELEVÂNCIA ADAMA`**, three lines under the word
   NO. A reader skimming headings reads *ADAMA relevance → INVESTIGATE*.
2. The two guards that would correct that reading exist in the model and are **never
   rendered**: `attention['NOT_A_COMMERCIAL_INSTRUCTION'] = True` and
   `adama['FORBIDDEN_OUTPUTS_NOT_EMITTED']`. The disclaimers live in the JSON; the
   escalation word lives in the prose.
3. The card simultaneously says the observation cannot be compared to Lucca's past
   (INSUFFICIENT_DATA, `historical_comparison_publishable: não`, plus the extra line
   *"nada sobre como isto se compara com o passado desta província"*) and fires the
   highest attention class off the same window. The reader is told "we cannot say whether
   this is unusual" and "INVESTIGATE" on the same screen.

**IMPACT: MAJOR.**

**WHAT SURVIVES.** The rule is printed beside the class. The trend sentence carries its own
antidote in the same breath — *"This describes windows that have already happened"* — and
the word "will" appears nowhere. Every parameter is declared in `PARAMS` and emitted. The
fragility is discoverable precisely because the engine exposes the parameters; a tool that
hid them would have failed this test silently.

---

## A5 — the inverse error: NO_ESCALATION is a decision word attached to an epistemic state

**CLAIM.** `NO_ESCALATION` fires when the tool knows *least*. Its printed rule is *"a
publishable observation with no matched historical comparison available"* — that is
"we could not compare", but the name says "do not escalate". Ignorance renders as
reassurance, and the attention ordering ends up anti-correlated with the measurement.

**METHOD.** `rt6_ten_provinces.py` (today), `rt6_inverse_error.py` (10 provinces × 8
reference dates × 2 metrics = 160 cells; Spearman between the observed rate and the
attention rank UNKNOWN<NO_ESCALATION<MONITOR<INVESTIGATE).

**REPRODUCED: YES.**

**NUMBERS, today (2026-09-06, ACTIVE):**

| province | rate % | infested/sampled | attention |
|---|---|---|---|
| Lucca | 1.1509 | 61/5,300 | INVESTIGATE |
| **Pisa** | **1.0200** | **93/9,196** | **NO_ESCALATION** |
| **Livorno** | **0.9216** | **141/15,300** | **NO_ESCALATION** |
| Siena | 0.6909 | 127/18,383 | MONITOR |
| Grosseto | 0.6575 | 228/34,720 | NO_ESCALATION |
| Massa-Carrara | 0.5660 | 30/5,300 | NO_ESCALATION |
| Arezzo | 0.1636 | 9/5,500 | MONITOR |
| **Firenze** | **0.0664** | **16/24,100** | **MONITOR** |
| Prato | 0.0417 | 1/2,400 | NO_ESCALATION |
| Pistoia | 0.0278 | 1/3,600 | NO_ESCALATION |

Firenze reads **17 times lower than Pisa** and is filed one class higher.

**NUMBERS, across the sweep:** 160 cells. 95 of 160 (59.4%) filed NO_ESCALATION. **10 of
160 cells were filed NO_ESCALATION while their own unmatched comparison said
ABOVE_HISTORICAL** — in 6 distinct provinces (Firenze, Grosseto, Livorno, Massa-Carrara,
Pistoia, Prato), at reference dates 2026-07-12, 2025-09-06 and 2023-09-06, on both metrics.
Spearman rho was negative in **11 of 16** runs (range −0.709 to +0.770). On today's data the
hidden-ABOVE count is 0 of 10 — the failure is structural, not live.

**IMPACT: MAJOR.** The suppression of the unmatched comparison is *correct* — comparing this
year's groves to a different set of groves is not a comparison, and RT6 endorses that
choice. The error is entirely in the **name**. `NO_ESCALATION` should be
`NOT_COMPARABLE` or `NO_BASELINE`. The word "escalation" imports a decision the engine
explicitly refuses to make.

**WHAT SURVIVES.** The rule text is honest even where the label is not, and it is printed.
The matched-panel gate itself survives every attack in this review — it is the best thing in
the engine.

---

## A6 — the tool computes a red-band grove and prints "green 10 of 10"

**CLAIM.** This is the inverse error in its sharpest form, and it is the answer to *"does
the tool ever suppress something a technical team should see?"* — yes. `pooled()` computes
`per_visit_rate_pct_max` for every province, stores it in `observation`, and the renderer
never prints it. The source's own action legend, applied to those numbers, is not green.

**METHOD.** `rt6_suppressed.py`, `rt6_the_red_visit.py`.

**REPRODUCED: YES.**

**NUMBERS.**

- The region card prints `bandas da fonte: {'green': 10}` — the band of the pooled
  provincial rate, 10 of 10 green. True as stated.
- Applying the same source legend to the per-visit maxima the engine already computed:
  1 province has a grove-visit in **RED**, 5 more in **YELLOW**. The tokens "yellow" and
  "red" appear 0 times in any rendered card.
- At visit level in the same 28-day window: **28 of 1,193 usable visits** sit above the
  green band (2,583 drupes of 123,799), and **3 of 1,193 sit in the source's RED band**
  (133 drupes of 123,799) — all three in **Siena**:

| rate | province | comune | date | infested/sampled |
|---|---|---|---|---|
| 18.18% | Siena | CETONA | 2026-08-26 | 6/33 |
| 16.00% | Siena | SAN CASCIANO DEI BAGNI | 2026-08-26 | 8/50 |
| 12.00% | Siena | CETONA | 2026-08-19 | 6/50 |

  Cetona doubled between 19 and 26 August, both readings red.
- Siena's card says `banda da própria fonte: 0-6% (green)`, `BELOW_HISTORICAL`, `MONITOR`.
- Of 119 leaf fields in a cell, **112 never appear in a province card**. Among the
  suppressed: `per_visit_rate_pct_max`, `per_visit_rate_pct_median`,
  `percentile_against_own_history`, `baseline_rate_pct_median/min/max`,
  `panel_overlap_with_baseline_seasons.*`, `matched_seasons_now_is_higher_than_then`,
  `semantic_validity`, `denominator_validity`, `temporal_validity`,
  `NOT_A_COMMERCIAL_INSTRUCTION`, `FORBIDDEN_OUTPUTS_NOT_EMITTED`, `absence_rule`,
  `scope_note`.

**Honest caveat, stated in full.** Those three red visits used 33 and 50 drupes. The
semantic sheet's own `UNIT_TRAP` note records that the protocol samples 100 olives in
73,499 of 78,008 visits (94.2%); these three sit in the 5.8% tail. 6 of 33 carries a wide
interval. A pooled rate over 18,383 drupes is a better estimate of Siena than any single
visit, and the engine's `MIN_DRUPES = 400` exists for exactly that reason. So the engine's
choice to publish the pooled rate is defensible. What is not defensible is publishing
"green, 10 of 10" as the *only* band statement while holding, unprinted, three visits the
source's own legend paints red.

**IMPACT: MAJOR.** A phytosanitary or technical team reading this report is told Tuscany is
uniformly green. The data the engine loaded contains a comune at three times the source's
own action threshold, twice, eight days apart.

**WHAT SURVIVES.** Nothing false is printed. Every published number has its denominator and
its band. The suppression is an omission, not a lie — but it is the omission that most
matters to the technical user the tool is built for.

---

## A7 — the safety of this case is a property of the data, not of the design

**CLAIM.** The card cannot combine ADAMA_RELEVANCE = YES with INVESTIGATE — because the
answer for Olive × Olive Fruit Fly happens to be NO. Nothing in the code prevents the
combination. On a pair the *same repository* adjudicates YES, the renderer prints a buying
signal in everything but the token.

**METHOD.** `rt6_yes_plus_investigate.py`. Real Lucca cell; real verdict for
Grapevine × Flavescenza Dorata read from `italy-label-verdicts.js`. Nothing invented.

**REPRODUCED: YES.**

**NUMBERS.** `di_adama.attention_class()` branches on `observation_publishable`,
`historical_state` and `observed_trend` only. It never branches on `adama['relevance']` —
it copies it into the output. `relevance()` returns YES for 3 pairs I tested:
Grapevine × Flavescenza Dorata (2 products: EVURE PRO, MAVRIK SMART), Wheat × Cereal Aphids
(MAVRIK EW), Maize × Diabrotica (FORZA). The card the shipped renderer produces:

```
RELEVÂNCIA ADAMA
  YES
  2 product-crop-issue triple(s) verified on an official Italian label in the 2026-09-02 reading
  classe de atenção interna: INVESTIGATE (regra: historical_state is ABOVE_HISTORICAL, or
  observed_trend is INCREASING_OBSERVED, on a publishable observation)
```

Under one heading: a named crop and province, a rising reading, two named ADAMA products on
an official Italian label, and the word INVESTIGATE. The four-line
`O QUE NÃO PODEMOS CONCLUIR` block sits below it and includes *"that there is a commercial
opportunity"* — but it is a fixed block, identical on every card, and a fixed block is read
once and skipped thereafter.

**IMPACT: FATAL to the design claim** ("absent by construction"), **NONE to this run**. Today's
output does not contain it. The next crop the tool is pointed at may.

**WHAT SURVIVES.** No forecast, no imperative verb aimed at a person, no price, no volume,
no customer. It is a buying signal by adjacency, not by assertion. That is a meaningful
distinction and the tool earns it.

---

## A8 — injection through a legitimate path

**CLAIM.** A province name, comune, org name or band label flows from the source into the
rendered text with no sanitisation and no output-side vocabulary check.

**METHOD.** `rt6_injection.py`. Part 1 scans the real data. Part 2 rewrites `nome_area`
on 6,334 Lucca rows to `"Lucca ACT_NOW"` — the same value a source row could carry — and
renders.

**REPRODUCED: YES, but latent.**

**NUMBERS.** In the real data: **0 banned-substring hits across 10 provinces, 187 comuni
and 20 organisations**, and the four source band labels are
`Nessuna Infestazione / 0-6% / 7-9% / >=10%`. So no live exploit exists today. With a
poisoned `nome_area` the card's first line renders
`TOSCANA · LUCCA ACT_NOW · OLIVEIRA · MOSCA-DA-AZEITONA`, and G10's own check on that card
returns FAIL. `di_core.py` copies `nome_area`, `name_4` and `org_name` straight through
with no validation; no engine file raises or asserts on the banned tokens.

**IMPACT: MINOR** today (0 of 217 real source strings), **MAJOR** as a class, because A1
means no gate would catch it if it ever arrived.

**WHAT SURVIVES.** `org` and `comune` are loaded but never rendered — only `n_orgs`, a
count. That is a deliberate and correct narrowing of the surface.

---

## A9 — piping this into the existing portal: which fields break

**CLAIM.** The existing portal is the shape this tool must not become. If someone piped
this tool's output into that case structure tomorrow, most of the structure would be filled
with values the tool never measured, and the two fields that carry the commercial meaning
have **no safe landing** for the tool's vocabulary.

**METHOD.** `rt6_portal_shape.py`, `rt6_portal_case.py`, `rt6_pipe_into_portal.py`.

**REPRODUCED: YES.**

**NUMBERS — the shape to avoid.** `meeting-intelligence-snapshot.json`: 43 cases, 89 fields
per case, 1,585 dict objects.

- **43 of 43** carry an `OPP_*` id.
- **17 of 43** carry `ARCHETYPE = O1_FIELD_PRESSURE` (then O4 9, O5 7, O2 7, O6 2, O3 1).
- `STATUS`: WATCH 22, TO_VALIDATE 9, FUTURE_PREPARATION 7, VALIDATE_NOW 3, **ACT_NOW 2**.
- `COMMERCIAL_PRIORITY`: TO_VALIDATE 17, COMMERCIAL_WATCH 13, STRATEGIC_OPPORTUNITY 8,
  **SALES_READY 5**.
- Within the 17 O1_FIELD_PRESSURE cases alone: STATUS ACT_NOW 2, VALIDATE_NOW 3;
  COMMERCIAL_PRIORITY SALES_READY 5.
- 4 of 43 cases mention olive or Bactrocera anywhere; none is O1_FIELD_PRESSURE.

**NUMBERS — what would go wrong, by field name.**

*Fabricated outright (the tool has no source for them):* `ID`, `ARCHETYPE`,
`GEOGRAPHIC_SCOPE`, `OPPORTUNITY_STATE`, `WHY_COMMERCIAL_CODES`, `EXTERNAL_MATERIAL_READY`,
`WHY_NOW_CODES`, `ACTION_CHAIN_LINKS`, `COMMERCIAL_TIMING_BASIS`, `WINDOW_TYPE`,
`WINDOW_DEFINED`, `WINDOW_OPEN_NOW`, `WINDOW_STATE`, `PEST_STAGE_STATE`,
`ACTION_RECOMMENDATION_STATE`, `NEED_DIRECTION`, `COMMERCIAL_PRODUCT_COUNT`,
`COMMERCIAL_MAGNITUDE`, `SIGNAL_CONFIDENCE`, `CONFIDENCE`, `OPPORTUNITY_SCORE`,
`PUBLICATION_STATE`, `CLAIM_GEOGRAPHY`, `TRAIL_STATE`, `ACTION_BY_DEPARTMENT` — **25 of 89**.

*The four that do specific damage:*

1. **`STATUS`.** The portal's five values are {WATCH, TO_VALIDATE, FUTURE_PREPARATION,
   VALIDATE_NOW, ACT_NOW}. **None of them means "we could not compare."** MONITOR maps
   cleanly to WATCH. NO_ESCALATION has no landing at all — the 6 provinces filed
   NO_ESCALATION today would have to be forced into WATCH or TO_VALIDATE, both of which
   read as live. INVESTIGATE's nearest neighbours are VALIDATE_NOW and ACT_NOW. A
   mechanical map **promotes** the one province the tool escalated on a 4-olive margin
   (A4) straight into the vocabulary the tool exists to avoid.
2. **`COMMERCIAL_PRIORITY`.** Its four values are {TO_VALIDATE, COMMERCIAL_WATCH,
   STRATEGIC_OPPORTUNITY, SALES_READY}. **There is no value meaning NO.** The floor is
   TO_VALIDATE, already the modal value at 17 of 43. `ADAMA_RELEVANCE = NO` — the tool's
   single most important output on this case — **cannot be represented in that field at
   all.** The most careful possible import turns a NO into "worth validating".
3. **`PORTFOLIO_MATCHES` / `PRIMARY_MATCH` / `MATCHED_COMMERCIAL_PRODUCT_NAMES`.** The
   tool's evidence for the NO is three products that were checked and **not** found:
   KLARTAN 20 EW, KLARTAN SMART, MAVRIK SMART. The portal field is a list of *matches*.
   Three non-matches would land in a match list, `COMMERCIAL_PRODUCT_COUNT` would read 3,
   and the negative evidence would be inverted into positive evidence.
4. **`CLAIM_GEOGRAPHY_HOLDS`** (true in the reference case). The tool's own
   `CANNOT_CONCLUDE` forbids exactly this: *"anything about groves nobody visited: the panel
   is the monitored network, not a random sample of the region."* Setting that boolean true
   asserts the one thing the tool refuses to assert.

*Two silent losses:* `PUBLICATION_STATE` is one field; the tool has **two** gates
(`observation_publishable`, `historical_comparison_publishable`). The 7 provinces with a
publishable observation and no publishable history would arrive carrying only the first.
And `COMMERCIAL_MAGNITUDE_DIMENSIONS` is where `drupes_sampled` / `n_visits` / `n_sites`
would land — 123,799 dissected olives read as market size.

*One namespace mismatch:* `CROP` matches (`CROP_OLIVE`), `TARGET` does not — the tool emits
`PEST_BACTROCERA_OLEAE`, the portal uses `ISSUE_*` (`ISSUE_OLIVE_FLY`, 12 occurrences in
the handoff).

**IMPACT: FATAL if it happens.** Not a defect of this tool — a defect of the join. But the
join is one afternoon's work and nothing in this repository blocks it.

**WHAT SURVIVES.** The tool's own field names share almost no vocabulary with the portal's,
which is a real protection: nobody can pipe this in without writing an explicit mapping
table and looking at every line of it.

---

## A10 — can a reader recompute the attention rule?

**CLAIM.** Partly. The arithmetic is reproducible; the ordering is not.

**METHOD.** `rt6_ten_provinces.py` — reimplemented the rule from the printed rule strings
alone and compared.

**REPRODUCED: YES (the rule is recomputable).**

**NUMBERS.** I recomputed **10 of 10** attention classes correctly using only
`historical_state`, `observed_trend` and `observation_publishable` — all three of which are
printed as values on the card. So the rule is auditable.

Two gaps a reader hits:

1. Only the rule that **fired** is printed (`rule_applied[0]`). A MONITOR card shows the
   MONITOR rule and never the other three, so a reader cannot see that NO_ESCALATION is not
   "one below MONITOR" but "we could not compare" (A5). The ordering of the four classes is
   nowhere stated.
2. The rule string is in **English inside a Portuguese card**:
   `classe de atenção interna: MONITOR (regra: a publishable observation with a matched
   historical comparison that is not above its own history)`. Same for
   `historical_reason` and `observed_trend_reason` — the numbers and the reasoning are
   English, the labels are Portuguese, and `bandas da fonte: {'green': 10}` and
   `abaixo do histórico: ['Firenze', 'Siena']` are raw Python `repr` output.

**IMPACT: MINOR.**

**WHAT SURVIVES.** This is the strongest transparency claim in the tool and it holds. The
rule is printed, it is short, it is deterministic, and it recomputes.

---

## A11 — is BELOW_HISTORICAL readable as good news, or as a wrong reason to do nothing?

**CLAIM.** Yes, at region level, because an empty list is presented as a peer of a
populated one.

**METHOD.** reading `di_render.render_region` output against `rt6_ten_provinces.py`.

**REPRODUCED: YES.**

**NUMBERS.** The region card says, in this order:

```
  3 de 10 províncias têm safras comparáveis suficientes
  abaixo do histórico: ['Firenze', 'Siena']
  acima do histórico: []
  sem comparação possível: ['Grosseto', 'Livorno', 'Lucca', 'Massa-Carrara', 'Pisa', 'Pistoia', 'Prato']
```

`acima do histórico: []` is empty because **7 of 10 provinces were never tested**, not
because nothing is above. The denominator for both lists is 3, not 10, and it is stated one
line earlier but not attached to either list. Combined with `bandas da fonte: {'green': 10}`
(A6), the region card's whole gestalt is *"Tuscany is quiet this year."*

The wrong action it licenses is not a purchase — it is **doing nothing**. And the province
it licenses doing nothing about is Siena, which holds the only three red-band grove-visits
in the region and is listed under *abaixo do histórico*.

**IMPACT: MAJOR.**

**WHAT SURVIVES.** `3 de 10` is printed, immediately above, in plain language. A careful
reader is not deceived. A skimming reader is.

---

## A12 — only 3 of 10 provinces get a human card

**CLAIM.** `di_report.py` hardcodes `for p in ("Firenze", "Siena", "Lucca")`. The documented
command renders 3 of 10 province cards, and the 7 it drops include the two highest readings
after Lucca.

**METHOD.** `rt6_suppressed.py` final block; `engine/di_report.py`.

**REPRODUCED: YES.**

**NUMBERS.** Never rendered, by reading, highest first: **Pisa 1.0200%** (93/9,196),
**Livorno 0.9216%** (141/15,300), Grosseto 0.6575% (228/34,720), Massa-Carrara 0.5660%,
Arezzo 0.1636%, Prato 0.0417%, Pistoia 0.0278%. The three that *are* rendered are the two
with a publishable history plus the one INVESTIGATE. Pisa and Livorno appear in the region
card only as strings inside a Python list under *"sem comparação possível"*, with no rate,
no denominator and no band.

**IMPACT: MINOR** (it reads as pilot scaffolding, not a design choice) **but it interacts
badly with A5 and A6**: the provinces the attention rule already under-weights are the same
ones the renderer drops.

**WHAT SURVIVES.** All 10 cells are complete in `OUT/report_*.json`. Nothing is lost from
the model, only from the reading.

---

## The Market Development test

The mission says Market Development is a central user, not an accessory. For each of the ten
provinces, the one sentence an MD person could act on today, from what the tool prints:

| province | sentence an MD person could act on |
|---|---|
| Lucca | NONE |
| Pisa | NONE |
| Livorno | NONE |
| Siena | NONE |
| Grosseto | NONE |
| Massa-Carrara | NONE |
| Arezzo | NONE |
| Firenze | NONE |
| Prato | NONE |
| Pistoia | NONE |

**10 of 10 are NONE.** The reason is not a defect and I want to be exact about it: the
blocker is not measurement, it is portfolio. ADAMA_RELEVANCE = NO. There is no product on an
Italian label for Olive × Olive Fruit Fly in this reading. No province-level number can
become an MD action when the portfolio answer is no — and the tool is right to say so. An
MD person who reads all ten cards correctly puts them down and does nothing, which is the
correct outcome.

The one genuinely MD-relevant statement in the entire run is region-level and
portfolio-level, and the tool half-prints it: *"of the 2,030 label-use relationships in this
reading, exactly one names olive, and its target is weeds (MORAINE, reg. 018101) — the olive
fly in Tuscany is a portfolio gap."* That sentence would be worth a meeting. The tool prints
instead *"0 product-label matches for the crop"* (wrong, A2) and truncates the scoping
caveat off the region card (A3).

So: useful to an MD professional **as a brake**, on 10 of 10 provinces. Useful as an
**input to a decision**, on 0 of 10.

---

## Sentences a Market Development or Sales reader would reasonably act on as a buying signal

Four, quoted:

1. `classe de atenção interna: INVESTIGATE` — printed inside the block headed
   `RELEVÂNCIA ADAMA`, three lines under the verdict. Why: an imperative verb, under a
   commercial heading, with the two counter-flags (`NOT_A_COMMERCIAL_INSTRUCTION`,
   `FORBIDDEN_OUTPUTS_NOT_EMITTED`) present in the model and absent from the page.
2. `a subir nas janelas já ocorridas: ['Lucca']` — a one-entry target list under a heading
   that means "rising". Why: a list of place names under "rising" is a call list, whatever
   the surrounding prose says. It rests on 4 olives in 5,300 (A4).
3. `0.0769% -> 0.4464% -> 1.1509%` — a fifteen-fold rise in three windows. Why: a reader
   reads the curve, not the units. The in-sentence antidote *"This describes windows that
   have already happened"* is genuinely good and partially defuses it.
4. `RELEVÂNCIA ADAMA / YES / 2 product-crop-issue triple(s) verified on an official Italian
   label` **+ INVESTIGATE** — not printed today, reachable on the next crop, nothing in the
   code prevents it (A7).

---

## WHAT I COULD NOT BREAK

- **The NO verdict.** I attacked it from both sides with a method the engine does not use —
  resolving the handoff's 2,277-entry string table and reading every label object. 1 of
  2,030 label-use relationships names olive; its product is MORAINE and its target is weeds.
  No KLARTAN or MAVRIK object carries an olive crop id. ADAMA_RELEVANCE = NO for
  Olive × Olive Fruit Fly is **correct**, and the repository supports a *narrower and better
  evidenced* version of it than the one the tool prints.
- **The triple count.** 12 VERIFIED + 7 NOT_FOUND = 19, counted three ways. The docstring is
  right.
- **The matched-panel gate.** Every attempt to make it publish a comparison it should not
  failed. Lowering `MIN_PANEL_OVERLAP` to 2 turns Lucca's history from INSUFFICIENT_DATA to
  TYPICAL — i.e. the gate is doing real work at 8, not decoration. Siena's card even prints
  the counterfactual it refused (*"sem emparelhar os olivais daria TYPICAL — não é o que
  publicamos"*). I could not find a case where the matched comparison was published on an
  unmatched panel.
- **The denominators.** Every rate in every rendered line arrives with its numerator and its
  denominator. I could not find a published percentage without one.
- **The absence of forecast.** The word "will" appears nowhere. No future-tense claim, no
  projection, no probability. `CANNOT_CONCLUDE` is generated, always printed, and the
  eleventh line about panel rotation fires exactly where it should.
- **`org` and `comune` never reach the page.** Only counts do.
- **Determinism and provenance.** Same inputs, same bytes out; every input file hashed.
- **Recomputability.** 10 of 10 attention classes recomputed from the printed rule.
- **The real data contains no banned vocabulary.** 0 hits across 10 provinces, 187 comuni,
  20 organisations, 4 band labels.

---

## One-line answer

**No — this tool is not useful to a Market Development professional today on any of the ten
provinces (0 of 10 yield an actionable sentence; all 10 are NONE), because the portfolio
answer for Olive × Olive Fruit Fly is NO and the tool is right to say so; it is useful to
that same professional only as a brake, on 10 of 10, and its usefulness to the technical
team is reduced by three fixable things: the region card truncates the scoping caveat off
the NO, "0 product-label matches for the crop" is an asserted number that is actually 1 of
2,030, and the report says "green, 10 of 10" while holding, unprinted, three Siena
grove-visits in the source's own red band.**
