# OUTCOME-FIRST ELECTION — the alternative that should replace the Veneto target

Criterion applied throughout: **provability, not interest.** Not the most interesting
agronomic problem — the one that lets a forecast be *proved*.

## Elected: VITE × PERONOSPORA × TOSCANA

Regione Toscana **AgroAmbiente.info**, `survey_schema=7`, `survey_var=34` —
*"presenza su foglie di Peronospora"*, an ordinal class recorded by a technician on a dated
visit to a named vineyard: `49 nessuna / 50 bassa / 51 media / 52 alta`.

`OFFICIAL_OBSERVATION`. Open JSON API, no credentials.

### Verified by me, not accepted from the hunter

| season | records | vineyards | weeks | areas | % records with disease |
|---|---|---|---|---|---|
| 2008 | 3,346 | 233 | 27 | 10 | 36.0 |
| 2013 | 1,890 | 179 | 14 | 10 | 48.7 |
| 2017 | 1,263 | 177 | 19 | 10 | **6.6** |
| 2018 | 2,717 | 177 | 19 | 10 | 66.0 |
| 2023 | 2,145 | 180 | 18 | 10 | **79.4** |
| 2026 | 2,554 | 180 | 21 | 10 | 16.6 |

**18 seasons (2008–2026; 2011 genuinely missing), 36,924 dated georeferenced observations.**
Every record carries `lat`, `lon`, `date`, `week`, the ordinal `val`, the vineyard id, the
province and the cultivar.

### The parameter trap, recorded because it nearly cost the finding

`difesa=0` returns **HTTP 200, `ok:true`, and ZERO rows**. Only `difesa=all` returns data.
My first probe used `difesa=0`, got `rowCount: 0` for four separate years, and I was about
to record the hunter's claim as unreproducible. It was my parameters that were wrong, not
their count — with the right one, 2023 returns exactly the 2,145 rows they reported.

**HTTP 200 is not data, and a zero-row success is the most misleading response an API can
give.** Any future collection against this endpoint must assert `rowCount > 0`, never just
the status code.

## Why it beats every other candidate for this purpose

| | Veneto (incumbent) | Andalucía RAIF vine | **Toscana** |
|---|---|---|---|
| country | Italy | Spain | **Italy** |
| pathosystem | vite × peronospora | vite × mildiu | **vite × peronospora** |
| seasons | 25 docs, **4 comparable** | 20 | **18** |
| records/season | 1 sentence | 374–3,727 | 688–3,346 |
| panel stability | n/a | **collapses 186 → 18** | **stable ~175–180** |
| georeferenced | no | parcel codes | **lat/lon per record** |
| defence regime | unrecorded, unremovable | not in the export | **recorded per observation** |

Two things settle it. **The panel is stable** — Andalucía's decisive weakness is that its
network shrinks tenfold, so a regional mean moves with sample composition; Toscana holds
~175–180 vineyards across a decade. And **the defence regime is a field**, so the confound
that is structurally unremovable in Veneto — every severity statement records disease *after
control* — can here be stratified rather than merely disclosed.

The outcome also has real range: 6.6 % of records showing disease in 2017 against 79.4 % in
2023. That is a target with something to predict.

## What this does NOT change

The Andalucía result already answered the scientific question, and a better dataset does not
reopen it. There, on 20 quantitative seasons:

- antecedent weather → **0.400**, exactly the climatology baseline
- the season's own weather → **0.75**, p = 0.0002
- robust skill first appears **31 May**, once the primary-infection window has been observed

`PATHWAY_REAL_BUT_NOT_KNOWABLE_IN_ADVANCE`. Toscana is the right dataset to *replicate* that
on — in Italy, with a stable panel and the defence regime controlled — not a reason to
expect a different answer.

## `PC_REQUIRED_ROUTES` — 10 blocked routes, classified, none circumvented

| class | count | examples |
|---|---|---|
| `BROWSER_ENV_BLOCK` | 4 | the CKAN host `gdc-pdpopendata-ckan.paas.junta-andalucia.es` (502 through the proxy — the `www.juntadeandalucia.es` path works and was used instead), `raif.es` |
| `BOT_HEADLESS_BLOCK` | 4 | French BSV PDFs at `draaf.nouvelle-aquitaine…`, `plateforme-esv.fr`, `ecophytopic.fr`, Piemonte geoportal |
| `AUTH_REQUIRED` | 2 | `emergenzaxylella.it/Download/`, `odr.inrae.fr/agrilogue/dataset/vigicultures` |

**Nothing on this list was needed.** Every elected and ranked candidate was collected from
this container over open HTTP. No credentials were requested or used, and no authentication
was circumvented.

## Runners-up, all independently skeptic-tested

2. **Olivo × Bactrocera oleae × Andalucía** — 20 seasons, 12k–28k dissection counts/season.
   The single most data-rich object found; a physical fruit-dissection tally, uncircular.
3. **Olivo × Bactrocera oleae × Toscana** — 20 seasons; the skeptic returned an *empty*
   refutation list. Useful as a second-country replication of the same pest.
4. **Vite × mildiu × Andalucía** — 20 seasons, already fully parsed and backtested here.
5. **Lobesia botrana × Andalucía** — 20 seasons of continuous trap catches.

A circularity trap was found inside the RAIF tables and must be carried forward:
`0404 Mosca: IR (Índice de Riesgo)` and `1707 Repilo: Condiciones favorables` are **computed
model outputs**. Using either as a target would score a model against another model.
