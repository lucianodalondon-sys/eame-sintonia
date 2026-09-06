# RT4 — GEOGRAPHY AND SEMANTIC NORMALISATION

Independent red team. I did not write ENGINE/ or CASES/. Nothing under ENGINE/, CASES/ or
italia-portale/ was modified; every mutation below is an in-memory copy handed to the shipped
`current_pressure` through its own `_pre` argument, or a runtime monkeypatch of
`run_case.WORD_RANK` that is restored in a `finally` block.

Scripts, all under `CERT-V2/REDTEAM/`:

| script | what it measures |
|---|---|
| `rt4_geo_01_field_inventory.py` | population and agreement of every geographic field |
| `rt4_geo_02_istat_vs_label.py` | province string vs province implied by the ISTAT comune code |
| `rt4_geo_03_coords_and_provenance.py` | coordinates, field movement, whose province `nome_area` is |
| `rt4_sem_04_portal_vocabulary.py` | DATA vs ENGINE vs PORTAL, kept separate |
| `rt4_sem_05_ordinal_ladder.py` | every label in every code table, + vocabulary probe, + shuffle test |
| `rt4_06_impact_on_published.py` | does any of it reach a published number |
| `rt4_07_idfield_and_injection.py` | `id_field` collisions; category error demonstrated |
| `rt4_08_issue_label_and_order_n.py` | the SEPTORIA label; `order_n` vs the word ladder |
| `rt4_09_vicchio_exact.py` | the mislabel, exact filter, dense sweep |

**Corpus.** Three cases, all RAW files of the outcome variable of each:
OLIVO×BACTROCERA 79,251 rows (21 files, var −1002), VITE×OIDIO 35,065 rows (20 files, var 39),
FRUMENTO×"SEPTORIA" 5,817 rows (14 files, var 372). **Total 120,133 rows.**

**Headline.** Geography survives almost intact — the accusations of inheritance, of aggregation
above the province, and of source-location-passed-off-as-fact-location are all **refuted with
exact counts**. Semantics does not survive. The engine's output object contains no crop, no
issue and no region; the wheat case measures the wrong disease; and there is no guard at all in
the direction that matters — a nominal code table is silently accepted as an ordinal severity
ladder.

---

## PART 1 — GEOGRAPHY

### G-1. `nome_area` is the only geography the engine reads, and nothing cross-checks it

**CLAIM.** The published cell is keyed on a free-text province string. Every other geographic
field in the same row — the ISTAT comune code, the second province field, the comune name, the
sub-area, the coordinates, the recording organisation — is present, is populated, and is never
read. There is no reconciliation between them anywhere in the pipeline.

**METHOD.** `rt4_06_impact_on_published.py` (G1, G1b). For each of the three cases, corrupt one
row field at a time to the constant `"CORRUPTED"`, re-run the shipped `current_pressure` at
AS_OF 2026-09-06, and compare `json.dumps(..., sort_keys=True)`.

**REPRODUCED: YES.**

**NUMBERS.** Identical output after corrupting each of `admin_code`, `admin_code_3`, `name_3`,
`name_4`, `name_5`, `org_name`, `id_org`, `uid`, `cultivar`, `name`, `id_area` — **11 of 11
fields ignored, in 3 of 3 cases**. Only `nome_area` is load-bearing in all three cases
(`week` is additionally load-bearing in OLIVO alone, through `SEASON_STATE`). Source: the whole
of `ENGINE/current_pressure.py` contains exactly one geographic grouping statement, line 253,
`p = r.get("nome_area")`; `grep` for `lat|lon|admin_code|name_3|name_4|name_5|org_name` across
`ENGINE/*.py` returns no read of any of them outside `contracts.py` dataclass declarations.

**IMPACT: MAJOR.** Not because a number is currently wrong — G-2 shows the error rate is 30 rows
in 120,133 — but because the architecture has a single unverified point of entry for the one
dimension the product is sold on. The source ships a redundant, checkable ISTAT code in every
row and the engine discards it. G-2 is the proof that the redundancy would have caught a real
error.

**WHAT SURVIVES.** The choice of the province as the unit; the refusal to aggregate above it;
and the fact that `nome_area` is right 117,892 times out of 120,133.

---

### G-2. Thirty rows where the province string is wrong, and nothing notices

**CLAIM.** There exists a field whose province label disagrees with every other geographic
field in its own row, and the engine credits its visits to the wrong province.

**METHOD.** `rt4_geo_02_istat_vs_label.py` derives the province from the ISTAT comune code
(`admin_code`, province prefix: 45 Massa-Carrara, 46 Lucca, 47 Pistoia, 48 Firenze, 49 Livorno,
50 Pisa, 51 Arezzo, 52 Siena, 53 Grosseto, 100 Prato) and compares it to `nome_area`.
`rt4_09_vicchio_exact.py` measures the impact.

**REPRODUCED: YES.**

**NUMBERS.**
- Label agrees with the ISTAT code: **117,892 of 120,133 = 98.1346%**.
- Label disagrees: **2,241 of 120,133 = 1.8654%**, of which **2,211 are the Prato reform** (G-3)
  and **30 are a genuine mislabelling**.
- All 30 are one field, `id_field` 5082, comune **48049 VICCHIO** (`name_5` = Basso Mugello,
  province of Firenze), coordinates 43.992692 / 11.5226109, `org_name` = `unipi`,
  dates 2021-05-25 → 2024-07-08, case VITE×OIDIO.
- In those 30 rows: `name_3` = Firenze, `admin_code_3` = 2 (Firenze), `admin_code` = 48049,
  `name_4` = VICCHIO, coordinates in the Mugello — and `nome_area` = **Siena**, `id_area` = 38
  (Siena). Every field but two says Firenze.
- These are the **only 30 rows in 120,133** where `nome_area ≠ name_3`, and the only 30 where
  `admin_code_3 ≠ id_area`. The source's own internal contradiction is exactly co-extensive with
  the error, and is never tested.
- Root cause: `id_field` 5082 carries **68 rows across two different vineyards** — 16 rows in
  GAIOLE IN CHIANTI (52013, Siena, correctly labelled Siena), 52 rows in VICCHIO (48049), of
  which 22 are correctly labelled Firenze and 30 inherit the Siena label of the other vineyard
  sharing the id.

**IMPACT: MINOR.** Correcting the 30 rows (Siena → Firenze) and sweeping every 7 days from
1 April to 31 October in each season 2021–2026: **1,860 province-cells checked, 108 changed
their `VALUE` or `n_sites` (5.81%), and 0 changed their published class.** At AS_OF 2026-09-06,
0 of 10 cells change. The mislabel is real, is invisible to every gate, and currently moves no
published label.

**WHAT SURVIVES.** Every published class in the sweep. The defect is a latent correctness hole,
not a live wrong answer.

---

### G-3. The Prato disagreement is a genuine administrative reform, not an error

**CLAIM (mine, tested and withdrawn).** The 2,211 rows where a Firenze-era ISTAT code carries
the label "Prato" might be mislabelling.

**METHOD.** `rt4_geo_02_istat_vs_label.py`, classifying each disagreement against the seven
comuni transferred to the new province of Prato (L. 187/1992): Prato, Cantagallo, Carmignano,
Montemurlo, Poggio a Caiano, Vaiano, Vernio.

**REPRODUCED: NO — this is a source-side legacy code, and the label is the modern truth.**

**NUMBERS.** 2,211 rows labelled Prato, **100% of them (2,211/2,211) served with a 48xxx
(Firenze-era) ISTAT code**; **0 rows anywhere in the 120,133 carry a modern 100xxx Prato code**.
The comuni are CARMIGNANO 1,422, VAIANO 242, PRATO 238, MONTEMURLO 232, POGGIO A CAIANO 77.
**0 comuni labelled Prato that do not belong to the province of Prato**, and **0 rows where a
Prato comune is labelled Firenze**. Cantagallo and Vernio appear 0 times (not monitored).

**IMPACT: NONE** on correctness. It does mean that any future integrity check written as
"ISTAT code must match the label" would raise **2,211 false alarms** unless it carries the
1992 reform table.

**WHAT SURVIVES.** The province labelling of all 2,211 Prato rows is correct.

---

### G-4. Coordinates are badly broken and reach nothing

**CLAIM.** Rows sit outside Tuscany, coordinates are transposed, and fields change position
between seasons.

**METHOD.** `rt4_geo_03_coords_and_provenance.py` against a generous Tuscany bounding box
(lat 42.20–44.50, lon 9.60–12.40, including the Arcipelago). Impact by
`rt4_06_impact_on_published.py` (G1).

**REPRODUCED: YES for the data defect. NO for any effect on a published number.**

**NUMBERS.**
- **41,846 of 120,133 rows (34.83%) have lat = lon = 0** — no georeference at all.
- Of the 78,287 georeferenced rows, **1,269 (1.621%) fall outside Tuscany**;
  **1,176 of those have lat < lon**, which is geometrically impossible in Tuscany
  (lat ≈ 42–44, lon ≈ 10–12).
- **92 rows are genuinely transposed**: swapping lat and lon puts them inside Tuscany
  (8 distinct points, e.g. `lat=10.093788, lon=44.038545`).
- The out-of-region rows concentrate in one season: **2006 = 1,084 of 1,269 (85.4%)**;
  the rest are 2013=33, 2015=25, 2016=50, 2017=32, 2018=28, 2019=7, 2020=10.
  The 2006 points take the form (4.x, 45.x) — a whole-season georeferencing break, not noise.
- One digit-typo survives to 2015: VITE `id_field` 3533 at `45.53393, 11.918` (true position
  `43.53393, 11.918`) — 222 km north, in Veneto.
- **Field movement:** of 2,362 georeferenced fields, **301 hold 2+ positions**, **205 move more
  than 1 km, 148 more than 10 km, 69 more than 100 km**, and **all 301 move between seasons**.
  Example: OLIVO `id_field` 1227 sits at (4.494711, 45.495981) in 2006 and (43.818833, 10.471017)
  from 2007 on — 5,206 km apart, same id, same "field".

**IMPACT: NONE on any published number, proven two ways.** Moving **every one of the 120,133
coordinates to the Sahara (23.4162, 25.6628)** produces byte-identical output in 3 of 3 cases;
**deleting the `lat` and `lon` keys entirely** produces byte-identical output in 3 of 3 cases.

**WHAT SURVIVES.** Everything the engine publishes. But `CASES/run_case.py:100` computes and
reports `pct_georef` from these coordinates, so any narrative built on "% georeferenced" is
built on a column with a 2006-wide break and 1,176 impossible values.

---

### G-5. Inheritance — REFUTED

**CLAIM.** A province with no visits in the window acquires a class from its neighbours.

**METHOD.** `rt4_06_impact_on_published.py` (G3). Every case × every year 2006–2026 × six
calendar dates (15 May, 15 Jun, 15 Jul, 15 Aug, 6 Sep, 15 Oct). For every emitted cell, assert
that a cell in HIGHER/TYPICAL/LOWER has `n_visits > 0` and `n_sites > 0`.

**REPRODUCED: NO.**

**NUMBERS.** **3,150 province-cells checked. 1,352 cells had 0 visits in the window; 919 cells
carried a class; violations = 0.** Not one classed cell had zero visits or zero sites.
Additionally, **0 provinces present in the archive were ever missing from an output object** —
a province with data somewhere always appears, as UNKNOWN when the window is empty, rather than
silently vanishing.

**IMPACT: NONE.** The contract's "a province with no visits in the window does not inherit its
neighbour" holds by construction (`current_pressure.py:271-278`) and holds empirically.

**WHAT SURVIVES.** The claim, fully.

---

### G-6. Aggregation above the province — REFUTED

**CLAIM.** Some path produces a regional or national figure.

**METHOD.** `rt4_06_impact_on_published.py` (G4), plus grep of `ENGINE/*.py` and `CASES/*.py`.

**REPRODUCED: NO.**

**NUMBERS.** Across all three cases the set of keys ever emitted under `PROVINCES` is exactly
the **10 Tuscan province names**; **non-province keys = 0**. There is no summation over
provinces anywhere in `current_pressure.py`; `answer_sheet.py:56` hardcodes
`"REGIONAL_UNIT": "province", "NEVER": "no national figure is produced"`.

**IMPACT: NONE.**

**WHAT SURVIVES.** The claim. Note the mirror-image problem in S-6 below: the portal has no
province-level token at all, so the thing the engine is careful to produce is the thing the
portal cannot render.

---

### G-7. "The province of the recording organisation" — REFUTED

**CLAIM.** `nome_area` might be the province of the org that recorded the visit, not of the field.

**METHOD.** `rt4_geo_03_coords_and_provenance.py` (part C): for each candidate key, ask whether
`nome_area` is a mathematical function of it.

**REPRODUCED: NO, decisively.**

**NUMBERS.** `nome_area` is **not** a function of `org_name`: of 27 distinct org values,
**18 span two or more provinces**, and 4 span all ten (`unipi`, `ota`, `aprol`, and the null
org). `unipi` alone records in Grosseto 2,070, Livorno 2,105, Pisa 2,605, Massa-Carrara 610,
Arezzo 1,716, Firenze 2,228, Lucca 737, Pistoia 572, Prato 331, Siena 2,015. `org_name` is null
on **60,647 of 120,133 rows (50.48%)**, so for half the corpus there is no org to inherit from.
By contrast `nome_area` **is** a function of `admin_code` for 195 of 196 comuni (the exception
is 48049 Vicchio, G-2) and of `name_5` for 42 of 43 sub-areas (exception: Basso Mugello, the
same field).

**IMPACT: NONE.** `nome_area` is the province of the FIELD, not of the source. The accusation
fails.

**WHAT SURVIVES.** The provenance claim, with the single 30-row exception already counted.

---

### G-8. `id_field` is the site key and is not unique to a field

**CLAIM.** `current_pressure.py:195` groups by `id_field` to count "monitored sites". That id is
reused across different comuni, so "one site" is sometimes two farms.

**METHOD.** `rt4_07_idfield_and_injection.py` (H1, H1b).

**REPRODUCED: YES for the data defect. NO for any effect on a published number.**

**NUMBERS.**
- OLIVO: **25 of 2,686 id_field values (0.931%) carry 2+ comuni**, covering **1,962 of 79,251
  rows (2.476%)**.
- VITE: **52 of 895 (5.81%)**, covering **4,159 of 35,065 rows (11.861%)**.
- FRUMENTO: **0 of 285**.
- Worst example: OLIVO `id_field` 4380 spans four comuni — Bucine, Capolona, Cortona, Monte San
  Savino.
- **Windows in which one `id_field` held two comuni at once: 0**, over 21 years × 6 dates × 3
  cases. The reuse is sequential across seasons, never simultaneous.
- Tightening the site key to `(id_field, admin_code)` changes **0 of the 25 cells published at
  AS_OF 2026-09-06** (OLIVO 10 provinces + VITE 10 + FRUMENTO 5).

**IMPACT: MINOR.** `n_sites` is never inflated or deflated inside a window. But the identity
"same site, previous season" that the baseline rests on is not guaranteed: for 77 field ids the
2006 site and the 2020 site are different farms.

**WHAT SURVIVES.** Every `n_sites` figure currently published.

---

## PART 2 — SEMANTIC NORMALISATION

### S-1. The output object does not know what it is about. FATAL.

**CLAIM.** Asked which of REGION / CROP / ISSUE / DATE `current_pressure` carries, the answer is
DATE, and a province string. It carries no crop and no issue at all.

**METHOD.** `rt4_sem_04_portal_vocabulary.py` (Q1, Q2). Inspect the emitted object; then execute
`ENGINE/gates.py:26` verbatim.

**REPRODUCED: YES.**

**NUMBERS.** The 12 top-level keys of `current_pressure`'s output are `AS_OF`, `CUTOFF_LABEL`,
`DATA_LATENCY_DAYS`, `DENOMINATOR_GUARD`, `EVIDENCE_ROLE`, `METRIC`, `PARAMS`, `PROVINCES`,
`SEASON_STATE`, `SOURCE`, `VALUE_MODE`, `WINDOW`. The 9 per-province keys are `BASELINE_MEDIAN`,
`BASELINE_N`, `BASELINE_SEASONS`, `EVIDENCE`, `PERCENTILE`, `STATE`, `VALUE`, `n_sites`,
`n_visits`.

- **DATE: carried** (`AS_OF`, `WINDOW`, `CUTOFF_LABEL`).
- **REGION: not carried.** The only geographic token is the `PROVINCES` dict key, which is the
  raw `nome_area` string. There is no region field. "TOSCANA" appears nowhere in the object.
- **CROP: not carried.** 0 keys.
- **ISSUE: not carried.** 0 keys.

In the raw data, **0 of 19 row keys name the crop, 0 name the issue, 0 name the region**, in all
three cases. The crop signal is `collection_index.crop` — an integer (2, 3, 19). The issue signal
is the *name of the survey variable*, which for OLIVO is `"Dannosa"` and for VITE is
`"Presenza su foglie"` — neither of which names Bactrocera or oidio.

`ENGINE/gates.py:26` reads:

```python
sheets[name] = answer_sheet(d, v, as_of, "issue", "crop", "region")
```

Executed, this produces as the answer sheet's first published sentence, verbatim:

> `In the 28 days to 2026-09-06, official scouts scored 342 visits for issue across 165 monitored crop sites in region. 0 of those sites had it present; 165 did not.`

**IMPACT: FATAL.** The three placeholders are the crop, the issue and the region. They are
supplied as literal English filler and the gate harness that certifies the module runs on that
output. The numbers in the sentence (342, 165, 0, 165) are correct; the sentence does not say
what they are about.

**WHAT SURVIVES.** The arithmetic, the province partition, the date window, the UNKNOWN states,
and `SOURCE` (a real URL). Everything that makes the number *meaningful to a reader* is absent.

---

### S-2. The wheat case measures the wrong disease. FATAL.

**CLAIM.** `CASES/FRUMENTO-SEPTORIA-TOSCANA` does not measure Septoria.

**METHOD.** `rt4_sem_04_portal_vocabulary.py` (Q1) and `rt4_08_issue_label_and_order_n.py` (I1).

**REPRODUCED: YES.**

**NUMBERS.** The case collects **exactly one variable, `id_survey_var` 372**, whose name in the
source's own schema 74 is **`"Intensità Oidio"`** — powdery mildew. The Septoria variable
**`id_survey_var` 382, `"Intensità Septoria"`, exists in the same schema and was never
collected** (`RAW/` contains only `c19_s74_v372_*`; the collection index records 14 successful
and 7 empty requests, all for var 372). The full schema 74 offers 371 Localizzazione Oidio,
372 Intensità Oidio, 384 Frequenza Oidio, 381 Localizzazione Septoria, 382 Intensità Septoria,
385 Frequenza Septoria, 383 Intensità Fusariosi, 386 Frequenza Fusariosi. The case picked the
first of the eight and named the directory after the third disease in the schema title.

The issue string is assigned by hand at `CERT-V2/p4_date_and_floor.py:38`:

```python
("TOSCANA", "WHEAT", "SEPTORIA",
 os.path.join(HERE, "..", "CASES", "FRUMENTO-SEPTORIA-TOSCANA"), 372)]
```

It is not read from the source. `CERT-V2/p4_cell_state_by_date.json` consequently contains
**150 records carrying `ISSUE: "SEPTORIA"`**, all TOSCANA×WHEAT, of which **9 carry a published
class (`TYPICAL_FOR_THE_DATE`)**, 137 `UNKNOWN_NO_DATA` and 4 `UNKNOWN_NO_BASELINE`.
`CERT-V2/p12_negative_controls.json` states the cell as
`"TOSCANA x WHEAT x SEPTORIA x 2026-09-06"`.

**IMPACT: FATAL** for the semantic claim, and it is the exact failure the pipeline was
supposedly hardened against — `run_case.py:31` calls this case "the first case this pipeline was
not built for" and rebuilt the label parser for it, without noticing that the variable being
parsed is a different disease from the one in the directory name.

Note that `ENGINE/gates.py` gates only OLIVO and VITE, so no *gate* verdict rests on the wheat
cell; the CERT-V2 step-4 artifact and the negative-control artifact do.

**WHAT SURVIVES.** The 9 published wheat cells are arithmetically correct statements about
**oidio on wheat**. Only the name is wrong. Renaming the case and the literal fixes it; no
recomputation is needed.

---

### S-3. Nothing stops a nominal code table from becoming a severity ladder. FATAL.

**CLAIM.** `assert_scale_decodes` guards one direction only — a NUMERIC variable that is really
serving code ids. There is no guard in the other direction: an ORDINAL-mode variable whose code
table is a nominal list, not a ladder. The engine will publish a disease class from it.

**METHOD.** `rt4_07_idfield_and_injection.py` (H2). VITE `id_survey_var` 42 is
`"prodotto" / "prodotto utilizzato"` — **which fungicide the grower applied**. It was never
collected, so it cannot be run on its own RAW files. I therefore re-coded the 35,065 real VITE
var-39 rows onto the var-42 code table (782→306 `nessuno`, 783→307 `zolfo`, 784→309
`quinoxifen`, 785→311 `strobilurine`), preserving dates, provinces and field ids, and handed
them to the shipped `current_pressure` through `_pre`. This tests the engine's logic, not the
data. It is an injection and I label it as one.

**REPRODUCED: YES.**

**NUMBERS.** `value_mode` returns **ORDINAL** (a code table exists, therefore it is ordinal).
`assert_scale_decodes` returns immediately (it only fires in NUMERIC mode).
`assert_outcome_admissible` passes (var 42 *is* a declared survey variable).
`build_scale` resolves **1 of 8 labels** — `nessuno` → ordinal 0 — and drops
`zolfo, IBE, quinoxifen, dinocap, strobilurine, Ampelomices q., altro`. Every dropped value is
then MISSING, so `INCIDENCE` = share of sites with max > 0 = **0.0 by construction, forever**.

The engine **did not refuse**. At AS_OF 2026-09-06 it published, stamped
`EVIDENCE_ROLE: OFFICIAL_OBSERVATION`:

| province | STATE | VALUE | n_sites | PERCENTILE |
|---|---|---|---|---|
| Arezzo | TYPICAL_FOR_THE_DATE | 0.0 | 20 | 0.5 |
| Firenze | TYPICAL_FOR_THE_DATE | 0.0 | 29 | 0.5 |
| Grosseto | TYPICAL_FOR_THE_DATE | 0.0 | 20 | 0.5 |
| Livorno | TYPICAL_FOR_THE_DATE | 0.0 | 21 | 0.5 |
| Lucca | TYPICAL_FOR_THE_DATE | 0.0 | 9 | 0.5 |
| Massa-Carrara | TYPICAL_FOR_THE_DATE | 0.0 | 8 | 0.5 |
| Pisa | TYPICAL_FOR_THE_DATE | 0.0 | 19 | 0.5 |
| Pistoia | TYPICAL_FOR_THE_DATE | 0.0 | 10 | 0.5 |
| Prato | UNKNOWN_NO_DATA | — | 4 | — |
| Siena | TYPICAL_FOR_THE_DATE | 0.0 | 29 | 0.5 |

**9 of 10 provinces published a class. 121 classed cells** across the 2010–2026 walk-forward at
15 July (121 TYPICAL, 38 UNKNOWN_NO_DATA, 11 UNKNOWN_NO_BASELINE). Every published value is 0.0.

**IMPACT: FATAL.** This is precisely the failure mode `assert_scale_decodes` was written to
prevent — its docstring says the module's "central design claim is that it fails loudly to
UNKNOWN rather than quietly to a number" — reproduced through the unguarded door. The failure is
*worse* than the one that was fixed: the frumento bug published `SITE_INCIDENCE 1.000`, which is
absurd on its face; this publishes **0.000, a confident, plausible, well-evidenced "no disease
here"** for a variable that records what was sprayed.

**Latency of the risk, stated honestly:** var 42 is not collected, so no shipped number is
currently wrong from this. The missing guard is a property of the shipped code, and S-2 shows the
pipeline does get pointed at a variable from a schema without checking what it means.

**WHAT SURVIVES.** The three currently-collected outcome variables (−1002, 39, 372) are genuine
ordinal severity scales, so no live cell is affected.

---

### S-4. A "where on the plant" variable is read as a severity ladder

**CLAIM.** `id_survey_var` 371 / 381 are `Localizzazione` — *where on the wheat plant* the
infection sits. The ladder matches `bassa` and `alta` inside "Parte bassa" / "Parte alta" and
turns a position into a severity.

**METHOD.** `rt4_sem_05_ordinal_ladder.py` (A) and `rt4_07_idfield_and_injection.py` (H2b),
same injection technique as S-3, using the real FRUMENTO rows re-coded onto the var-371 table.

**REPRODUCED: YES.**

**NUMBERS.** For var 371 the engine builds `{No: 0, "Parte bassa": 1, "Parte alta": 2}` and drops
`Penultima foglia`, `Ultima foglia`, `Spiga` — **3 of 6 labels**. "Parte bassa" is the *lower
part of the canopy* and receives a LOW severity; "Parte alta" is the *upper part* and receives a
HIGH one. The three positions that matter most agronomically — penultimate leaf, flag leaf and
ear, which carry the yield — are the three the ladder cannot read, so they become MISSING.
For var 381 the engine resolves **1 of 5 labels** (`No` → 0), which makes INCIDENCE structurally
0.000 for every province forever.

On the injected walk-forward at 1 June, the engine published **HIGHER_THAN_USUAL in 4 cells** —
Arezzo 2020 (VALUE 1.0), Grosseto 2020 (0.4118), Grosseto 2023 (0.375), Arezzo 2024 (0.5833) —
alongside 17 TYPICAL. The `MIN_POSITIVE_SITES = 5` effect-size floor did not withhold them.

**IMPACT: MAJOR, latent.** HIGHER_THAN_USUAL is, in this engine's own words, "the only word here
that can trigger spending". It fires off a variable that says where the fungus is, not how much
of it there is. Vars 371 and 381 are not collected, so no live cell is affected.

**WHAT SURVIVES.** Nothing about the ladder's ability to tell an intensity scale from a location
scale. The `value_mode` test ("has a code table ⟹ ordinal") is the whole of the check.

---

### S-5. Every label in the three real code tables, and the rank it receives

**CLAIM.** The ladder resolves labels *wrongly*, not merely incompletely.

**METHOD.** `rt4_sem_05_ordinal_ladder.py` (A). Ten ordinal code tables + one nominal table,
57 labels. "True order" is taken from the source's own `order_n` and its own icon colour ramp
(`no.gif` → green → yellow → orange → red → red triangle).

**REPRODUCED: YES.**

**NUMBERS. 37 of 57 labels resolve; 20 of 57 do not.** Per variable:

| case | var | meaning | in scale | dropped |
|---|---|---|---|---|
| VITE | 39 | Presenza su foglie | 4/4 | — |
| VITE | 40 | presenza su grappoli | 4/4 | — |
| VITE | 42 | **prodotto (fungicide applied)** | **1/8** | zolfo, IBE, quinoxifen, dinocap, strobilurine, Ampelomices q., altro |
| FRUM | 371 | **Localizzazione Oidio** | **3/6** | Penultima foglia, Ultima foglia, Spiga |
| FRUM | 372 | Intensità Oidio | 4/6 | **50 - gravissina, 75 - completa** |
| FRUM | 381 | **Localizzazione Septoria** | **1/5** | Terzultima/Penultima/Ultima foglia, Spiga |
| FRUM | 382 | Intensità Septoria | 4/6 | **50 - gravissima, 75 - completa** |
| FRUM | 383 | Intensità Fusariosi | 4/6 | **50 - gravissima, 90 - completa** |
| FRUM | 384 | Frequenza Oidio | 4/4 | — |
| FRUM | 385 | Frequenza Septoria | 4/4 | — |
| FRUM | 386 | Frequenza Fusariosi | 4/4 | — |

The pattern in the three intensity variables is the one that matters: **the ladder reads the
bottom four rungs and is blind to the top two.** `grave` is in `WORD_RANK`; `gravissima` is not,
and `\bgrave\b` does not match inside it; `completa` is not. Those two rungs are the source's
own red (`cub_rd`) and red-triangle (`tri_rd`) bands — an epidemic. A visit that recorded
"50 - gravissima" enters `_window_value` as MISSING; if that site also recorded "Nessuna"
earlier in the same 28-day window, the site-max is 0 and the site is published as **negative**.

**IMPACT on live numbers: MINOR, measured.** Of 5,817 var-372 observations, **3 carry code 1629
("50 - gravissina") and 0 carry 1605 ("75 - completa") — 3 of 5,817 = 0.0516%**. Restoring the
missing words (`gravissima`/`gravissina` → 4, `completa` → 5) changes **0 of the 5 wheat cells
published today and 0 of 70 walk-forward cells** (14 seasons × 5 provinces) at 1 June 2013–2026.
VITE var 39 has **0 unresolved labels and 0 affected observations**.

**IMPACT overall: MAJOR, latent.** The defect is inert only because 2013–2026 in Tuscany contained
almost no severe wheat mildew. The ladder is unreadable in exactly the seasons the product exists
to detect.

**WHAT SURVIVES.** All 10 currently published cells and all 70 walk-forward wheat cells, and the
whole of the VITE and OLIVO series.

---

### S-6. Italian ordinal vocabulary the ladder does not know, and the ones it inverts

**METHOD.** `rt4_sem_05_ordinal_ladder.py` (B), 48 probe labels. Ranks: 0 = absent,
1 = low, 2 = medium, 3 = high.

**REPRODUCED: YES.** The three asked for explicitly:

| label | rank received | correct? |
|---|---|---|
| `Assente/Bassa` | **0** | matches `assente` (7 chars) before `bassa` (5); the "low" half is discarded |
| `Molto alta` | **3** | same rank as bare `Alta` — "very high" and "high" collapse onto one ordinal |
| `Nulla` | **None — UNRESOLVED** | `Nulla` means *zero*. It is dropped from the scale, so a recorded absence becomes MISSING, and the site leaves the denominator entirely instead of counting as a negative |

**True inversions found:**

- **`Non si rileva`** ("is not detected") → **rank 3, ALTA**. `WORD_RANK` contains `"si": 3`, and
  `\bsi\b` matches the reflexive pronoun. A negative observation is published as the highest
  severity.
- **`Nessuna/Alta` → 0** and **`Alta/Nessuna` → 0**: the longer word always wins regardless of
  the label's own order, so a range that reaches "alta" is read as "absent".
- **`Medio-alta` → 3** but **`Media-Alta` → 2**. Two spellings of the same band, two different
  ranks, because `medio` is not in `WORD_RANK` and `media` is.

**Unresolved (29 of 48), all plausible Italian survey vocabulary:** `Nulla`, `Bassissima`,
`Altissima`, `Elevatissima`, `Trascurabile`, `Diffusa`, `Forte`, `Debole`, `Intensa`, `Assenza`,
`Presente`, `Non rilevata`, `Non rilevato`, `Nessun sintomo`, `Sintomi assenti`, `0 - nulla`,
`gravissima`, `gravissina`, `completa`, `Sporadica`, `Localizzata`, `Generalizzata`, `Focolai`,
`Iniziale`, `Avanzata`, `n.d.`, `N.D.`, `Non applicabile`, `Da verificare`.
Note `Assente` resolves but `Assenza` does not; `Nessuna` resolves but `Nulla` does not.

**IMPACT: MINOR on the current corpus** (none of these labels occur in the three cases'
code tables), **MAJOR as a generalisation risk** — the module's stated purpose is "one code path
for every REGION × CROP × ISSUE", and the ladder is a 13-word dictionary.

**WHAT SURVIVES.** The 37 labels it does resolve, it resolves in the correct relative order —
see S-8.

---

### S-7. Does the ordinal derivation depend on the order of the code table? — REFUTED, with a caveat

**METHOD.** `rt4_sem_05_ordinal_ladder.py` (C). 200 random shuffles of the full `codes` list per
variable, 11 variables across 2 cases (OLIVO has no code table), comparing the resulting scale.

**REPRODUCED: NO.** The derived scale is **identical under all 200 shuffles for all 11
variables**. `build_scale` assigns `ordinal = ranks.index(rank)` over a *sorted set*, which is
order-independent.

**Caveat, which is a real defect:** the ordinal is a **dense re-rank of the surviving labels, not
an absolute level**. Removing one code shifts every code above it. Measured on var 384: with the
full table `{Nessuna 0, Bassa <10% 1, Media 10-25% 2, Alta >25% 3}`; with `Bassa` removed,
`{Nessuna 0, Media 10-25% 1, Alta >25% 2}` — "Media" now occupies the ordinal that meant "Bassa".
This is exactly what the S-5 truncation does to vars 372/382/383: dropping the top two rungs
leaves `grave` at ordinal 3 out of 3 instead of 3 out of 5, so **"grave" is published as the
scale maximum**. It does not affect `INCIDENCE` (a `> 0` test) but it does affect `SEVERITY`
(`mean` of site maxima), which is a selectable metric.

There is one order dependence, in the source code rather than in the data: `derive_rank`'s
compound-label loop iterates `sorted(WORD_RANK.items(), key=lambda kv: -len(kv[0]))`, and ties of
equal length are broken by `WORD_RANK`'s literal insertion order —
`moderata, nessuna, nessuno, assente, elevata, scarsa, bassa, lieve, media, grave, alta, no, si`.
Reordering that dict literal would change `Bassa/Media` from 1 to 2.

---

### S-8. The source shipped a correct order and the engine threw it away

**CLAIM.** `CASES/run_case.py:9-13` rejects the source's `order_n` as unreliable and derives the
ladder from label text instead. That trade is a net loss on every certified case.

**METHOD.** `rt4_08_issue_label_and_order_n.py` (I2, I2b).

**REPRODUCED: YES.**

**NUMBERS.** Sorting each code table by the source's own `order_n` yields the correct severity
order in **10 of 10 ordinal code tables in the three cases, covering 57 of 57 labels — 0 wrong**.
The word ladder covers **37 of 57**. `order_n` gets right every label the ladder drops, including
`50 - gravissima` (order_n 50), `75 - completa` (75), `Ultima foglia` (55) and `Spiga` (66).

The counter-example cited in the docstring — *"order_n is unreliable (peronospora leaf: media=3
ranks below bassa=5)"* and *"the code NUMBER is unreliable (50=media, 51=bassa)"* — **is real,
but it is not in any of the three certified cases.** I searched every JSON in
`DISEASE-INTELLIGENCE-ITALY/` for a code table where `order_n(media) < order_n(bassa)`:
**exactly one hit, `ABRUZZO/collection_index.json`, `id_survey_var` 34, with
`nessuna=49, media=50, bassa=51, alta=52`.** In the three certified cases the only `media`/`bassa`
pair is VITE var 39, where `order_n` is `bassa=3, media=5` — the correct order.

**IMPACT: MAJOR (design).** A defence against one table in a fourth, uncertified case
(ABRUZZO) costs the loss of 20 of 57 labels in the three cases that are certified, including
every top-severity rung. `order_n` is also the only signal that would have ordered the
localizzazione scales (S-4) correctly, since their order is agronomic and unavailable from the
words. It would *not* have caught S-3 — `order_n` on the fungicide list is 306…313, a perfectly
ordered nominal sequence — so neither signal distinguishes ordinal from nominal. That check does
not exist at all.

**WHAT SURVIVES.** The word ladder is genuinely more robust than `order_n` on the ABRUZZO table.
The correct design is to use both and refuse when they disagree; the current design uses the
weaker one alone.

---

### S-9. DATA vs ENGINE vs PORTAL — the three questions, kept separate

**METHOD.** `rt4_sem_04_portal_vocabulary.py`. `italia-portale/client/meeting-intelligence-snapshot.json`
read only, 43 cases.

| | OLIVO × BACTROCERA | VITE × OIDIO | FRUMENTO × (var 372) |
|---|---|---|---|
| **Q1 does the DATA have a crop signal?** | Yes, weakly: `collection_index.crop = 2`, an integer. `cultivar` populated on 5,083/79,251 rows (6.41%) with values like "Frantoio Leccino Moraiolo" | `crop = 3`; `cultivar` on 139/35,065 (0.40%), all "Sangiovese" | `crop = 19`; `cultivar` on 2,745/5,817 (47.19%), 70 wheat varieties |
| **Q1 does the DATA have an issue signal?** | Only the variable name `"Dannosa"` + `schema = 1`. Bactrocera is named nowhere | Only `"Presenza su foglie"` + `schema = 8`. Oidio is named nowhere | `"Intensità Oidio"` + `schema = 74` — and the directory says Septoria (S-2) |
| **Q1 region signal?** | None. 0 of 19 row keys. Only `nome_area` (province) | same | same |
| **Q2 does the ENGINE canonicalise it?** | **No.** 0 crop keys, 0 issue keys, 0 region keys in the output object (S-1) | same | same |
| **Q3 can the PORTAL render it?** | CROP: **`CROP_OLIVE` exists**. ISSUE: **ABSENT** — 0 olive targets in the whole vocabulary | CROP: **`CROP_GRAPEVINE`**. ISSUE: **`ISSUE_POWDERY_MILDEW` exists** | CROP: **`CROP_WHEAT_GENERIC`**. ISSUE for Septoria: **ABSENT**; for the disease actually measured (oidio), `ISSUE_POWDERY_MILDEW` exists |

**Geography is the sharpest mismatch.** The portal's `GEOGRAPHY` vocabulary is
`GEO_ITALY` (19), `GEO_EU` (7), `REGION_UMBRIA` (4), `REGION_FRIULI_VENEZIA_GIULIA` (3),
`REGION_EMILIA_ROMAGNA` (3), `REGION_TOSCANA` (3), `REGION_VENETO` (2), `REGION_LOMBARDIA` (2).
**There is no province-level token — 0 of 8 geography values name a province.** The engine's only
unit is the province, and it refuses to aggregate above it (G-6, correctly). So the one thing the
engine produces is the one granularity the portal has no word for, and rendering it would require
exactly the aggregation the contract forbids. `REGION_TOSCANA` would name the region the engine
never claims.

**IMPACT: MAJOR.** Not a defect in the engine; a statement that the engine's output is not
currently renderable without either a new province vocabulary in the portal or a contract
violation.

---

### S-10. `ENGINE/gates.py:241` hardcodes an absolute Linux path

**METHOD.** grep of `ENGINE/*.py` for absolute paths; comparison with the stored `gates.json`.

**REPRODUCED: YES.** Line 241 is
`snap = "/home/user/eame-sintonia/italia-portale/client/meeting-intelligence-snapshot.json"`.
On this checkout the file lives at
`C:\cert-v2-disease-pressure\italia-portale\client\meeting-intelligence-snapshot.json`, so
`os.path.exists(snap)` is False and gate J takes its default `(FAIL, "inventory not readable")`.
The stored `gates.json` records J as `NOT_TESTABLE` with the full PARTIALLY_OVERLAPS evidence,
i.e. it was generated where the path resolved.

**NUMBERS.** 1 of 10 gates. Stored verdicts: 8 PASS, 1 FAIL (G), 1 NOT_TESTABLE (J),
`DESERVES_FUTURE_INTEGRATION: "NO"`. Re-run here, J would become a second FAIL. Every other path
in `ENGINE/` is derived from `os.path.abspath(__file__)`.

**IMPACT: MINOR.** The headline verdict is already "NO" because of gate G, so the count of
failures changes but the conclusion does not. It does mean gate J is not reproducible off the
machine it was written on, which contradicts gate E's "byte-identical re-run" claim for the
suite as a whole.

---

## WHAT I COULD NOT BREAK

1. **Inheritance.** 3,150 province-cells across 3 cases × 21 years × 6 calendar dates.
   919 classed, 1,352 with zero visits, **0 violations**. No province ever acquired a class
   without visits of its own. The contract holds by construction and empirically.

2. **Aggregation above the province.** **0 non-province keys** ever emitted, across all three
   cases. No region total, no national total, no path to one.

3. **Source location passed off as fact location.** `nome_area` is **not** a function of
   `org_name` (18 of 27 orgs span 2+ provinces; 4 span all 10; org is null on 50.48% of rows).
   It **is** a function of `admin_code` for 195 of 196 comuni. The accusation fails: `nome_area`
   is the province of the field.

4. **Coordinates reaching a published number.** Moving all 120,133 points to the Sahara →
   byte-identical output, 3 of 3 cases. Deleting `lat`/`lon` → byte-identical, 3 of 3 cases.
   The 41,846 ungeoreferenced rows, the 1,269 out-of-region rows, the 1,176 impossible lat<lon
   rows, the 92 transposed rows and the 69 fields that jump more than 100 km all reach nothing.

5. **Code-table order dependence.** 200 shuffles × 11 variables → identical scale every time.

6. **`n_sites` integrity under `id_field` reuse.** 77 field ids carry 2+ comuni, but **0 windows**
   in 21 years × 6 dates × 3 cases hold two comuni under one id simultaneously, and tightening
   the site key changes **0 published cells**.

7. **The Prato reform.** All 2,211 rows correctly labelled; 0 Prato comuni mislabelled Firenze;
   0 non-Prato comuni labelled Prato.

8. **The relative order of the 37 labels the ladder does resolve.** In all 10 ordinal tables the
   surviving labels are in the correct order — the failures are truncation (S-5) and category
   error (S-3, S-4), never a scrambling of the rungs it reads.

9. **The arithmetic.** Every number I recomputed independently — n_sites, n_visits, incidence,
   percentile, baseline membership — matched the engine's.

---

## NOT KNOWN

- **What the 2006 coordinates actually are.** 1,084 rows in the form (4.x, 45.x). They are not a
  lat/lon transposition (swapping puts them in France, not Tuscany) and not a decimal shift I
  could identify. *What would settle it:* the source's own georeferencing changelog, or one
  ground-truthed field with a known 2006 position and a known 2007 position — `id_field` 1229
  is the best candidate: it holds exactly three positions across 21 seasons — 2006 at
  (4.566796, 45.558334), 2007–2012 at (43.8894, 10.602217), and 2013–2026 at
  (43.891183, 10.603431). The last two are 221 m apart, i.e. the same grove re-surveyed; the
  first is 5,203 km from both.

- **Whether `nome_area` = "Siena" on the 30 Vicchio rows is a source error or a collection
  error.** Every artefact I can reach is post-collection. *What would settle it:* re-fetching
  `id_survey` 256685 from the live API and reading `nome_area` in the response.

- **Whether `id_field` reuse is deliberate re-registration or id recycling.** 77 ids carry 2+
  comuni; I cannot tell whether the source retires and reissues ids. *What would settle it:* the
  API's field registry, or a `date_created` field on the field record.

- **Whether the 9 published `TOSCANA|WHEAT|SEPTORIA` cells were ever shown to anyone as Septoria.**
  They exist in `p4_cell_state_by_date.json`. *What would settle it:* the distribution list for
  that artifact.

- **Whether `Cantagallo` and `Vernio` (0 rows) are unmonitored or excluded.** *What would settle
  it:* the source's list of registered fields per comune, independent of observations.
