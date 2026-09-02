**File written:** `C:\eame-sintonia\italia-portale\audit\blocks\portfolio.js` — `node audit/splice.mjs try portfolio` → **50/52 screen renders pass**; both Portafoglio renders (it + en) pass. The 2 failures (`it/en · Action brief: Cannot read properties of null (reading 'doc')`) are in the `brief` block, not mine.

## Legacy fixture reads removed
**None. There were zero.** My block (portale.html 3025–3048) already read only `AM.products`, `T` and `s`. It contains no `D.*`, no `window.ITALY_*`, no `@VISUAL_ONLY` marker and no `@EXPLICIT_DEMO` marker — verified by grep on the candidate file. `node audit/run.mjs --only=D1` reports 154 core `D.*` reads file-wide; none of them are in lines 3025–3048.

## Reads I kept with a marker
**None needed.** The one hardcoded presentation value I inherited — the per-category hex — was a literal in the block, not a fixture read. I replaced three of the four with `AM.CATEGORY_UI`:

| category | before (literal) | after | note |
|---|---|---|---|
| ERBICIDI | `#7DB41E` | `AM.CATEGORY_UI.weed.color` | identical value |
| FUNGICIDI | `#00A0DF` | `AM.CATEGORY_UI.disease.color` | identical value |
| INSETTICIDI | `#9D1D96` | `AM.CATEGORY_UI.pest.color` | identical value |
| SPECIALI | `#F89E18` | `#F89E18`, still a literal | SPECIALI is a catalog grouping with **no** canonical ISSUE_TYPE class, so `CATEGORY_UI` has nothing for it. Kept as the ADAMA accent. |
| *(unclassified)* | fell through to `#F89E18` | `AM.CATEGORY_UI.unknown.color` | bug fix: an unclassified product used to be tinted as if it were a Speciale. Measured 0/166 products hit this today, so it is a latent bug, not a visible change. |

## Measured numbers behind every decision
Run against the current `client/italy-app-model.js` (re-measured after the model grew to 1848 lines mid-task):

- `AM.products` **166** = 163 regulatory + 44 commercial, **41 joined by name**, 3 catalog-only, 122 registry-only.
- categories: ERBICIDI 91 · FUNGICIDI 46 · INSETTICIDI 23 · SPECIALI 6.
- `productRelationships` **236 rows**: VERIFIED_LABEL_MATCH **12**, RELATED_PORTFOLIO **217**, NO_CONFIRMED **7**, **LABEL_CHECK_NEEDED 0**.
- products carrying at least one row: verified **6**, related **19**, check-needed **0**, rejected **6**, **no relationship at all 140/166**.
- `matchState`: REGULATORY_MATCH_CONFIRMED 41 / REGULATORY_MATCH_NOT_FOUND 3 / absent 122.
- holders: regulatory 4 legal entities (ADAMA ITALIA 85, AGAN 35, MAKHTESHIM 26, DEUTSCHLAND 17). **On the 41 joined names the catalog holder and the registration holder are identical 41/41 — 0 conflicts.** So the guidance's "holder ≠ seller" case does not occur in this package; I publish the *link state* instead of inventing a reconciliation.
- `ai` filled 163/166 — the 3 empties are exactly BUDGE, EXELGROW, PARLEAF (`p.ai` is `undefined`, not `[]`).
- `expiry` filled 163/163; **15 already expired at REF 2026-09-02**, 41 expire before 2027-01-01. Not surfaced (see "what the data cannot support").

## What changes on screen (before → after)

1. **Regulatory tab count stops lying.** Before: `port.count = shown.length` (163) while `items = shown.slice(0, 60)`. The note line printed **"163/163" over 60 rendered cards**. After: cap raised to 240 (above the 166 the model holds) and `count = items.length`, so the tab reads **163/163 over 163 cards** and the ratio can never diverge again.

2. **Active substances stop being comma-jammed.** `p.ai` was handed the raw array; the template printed `PENDIMETHALIN,DIFLUFENICAN`. Now `PENDIMETHALIN + DIFLUFENICAN`.

3. **The three catalog-only Speciali say why they are blank.** BUDGE / EXELGROW / PARLEAF previously rendered `—` on the substance line. They now render `T.prodNotRegistered` — *"Non presente in questa lettura del registro"* / *"Not present in this registry reading"*. This is the domain guidance's "state the link state", per card, using an existing i18n key.

4. **The note line publishes the cross-tab link and a legend for the two bare glyphs.** The ✓ and △ on every card had **no legend anywhere on the screen**. New note:
   - commercial: `…Non dichiara completezza… · 41/44 → Registrato in Italia · ✓ CORRISPONDENZA VERIFICATA SU ETICHETTA · △ VERIFICA ETICHETTA NECESSARIA`
   - regulatory: `…non prova che il prodotto sia attualmente commercializzato. · 41/163 → Presente nel catalogo pubblico · ✓ … · △ …`

   Built from `T.PSTATE`, `T.prodRegistered`, `T.prodInCatalog` — fully localized, **no new i18n key**.

5. **Nothing removed from the grid.** All 166 products stay listed, including the 111+ that carry only crop-level relationships and the 140 that carry none. Architecture, both tabs, the category select and the card layout are byte-for-byte the same shape.

## The subcomponent that is dead and that I cannot kill
`portale.html:1419` — `{{ p.verified }} ✓ · {{ p.check }} △`.

`p.check` is `checkNeededLinks.length`, and the rebuilt relationship contract emits **zero LABEL_CHECK_NEEDED rows — 0 on 166/166 products**. The amber class only ever existed because a demo case named a product. So **the △ badge reads `0` on every card in the portal, in both tabs, in both languages, forever.** `p.verified` is also 0 on 160/166 (only COSAYR 200 SC, EVURE PRO, FORZA, MAVRIK EW, MAVRIK SMART, MAXENTIS carry a verified row). Meanwhile 19 products carry RELATED_PORTFOLIO rows and the card shows them as `0 ✓ · 0 △`.

I did **not** move the related count under the △ glyph — RELATED_PORTFOLIO ("registered on the crop, target use row not read") is not LABEL_CHECK_NEEDED, and relabelling it silently would be exactly the defect this migration exists to remove. I exposed `p.related` and `p.rejected` on every item so the markup edit is a one-line change.

### Markup edit still required (I cannot apply it)
`client/portale.html` line **1419**, inside the Portafoglio card:

```html
<span style="font-size:9.5px;color:#6E6663;padding-top:2px">{{ p.verified }} ✓ · {{ p.check }} △</span>
```
replace with
```html
<span style="font-size:9.5px;color:#6E6663;padding-top:2px">{{ p.verified }} ✓ · {{ p.related }} ○</span>
```

(drop `△`, gain `○` = RELATED_PORTFOLIO). If that lands, the legend clause in my note must change from `T.PSTATE.LABEL_CHECK_NEEDED` to `T.PSTATE.RELATED_PORTFOLIO` — one line in `audit/blocks/portfolio.js`, and I have kept it isolated in a `legend` const for exactly that reason. Until it lands, the note tells the reader honestly that △ means "label check needed" and that the count is zero.

## Spec items the data cannot support
- **Spec plan step 15** asks the note line to publish "12 windows verified, 6 to verify, 10 related-portfolio, 1 no confirmed match … out of 166", alongside `LV.AUDIT_DATE`. Those are **window-level** tallies belonging to the windows/case screens, not the Portafoglio, and `AM` does not expose `AUDIT_DATE` on the public contract (it lives on the new `labelVerdicts` collection object, which is **not** in `AM.collections` — I checked the 38 keys). Reading `window.ITALY_LABEL_VERDICTS` directly would be a raw-file read. I published the product-level facts the Portafoglio actually owns (41/44 and 41/163) instead. If `AM.collections.labelVerdicts` gets exported with `auditDate`, one line is enough to add it.
- **Expiry is still invisible.** 15 of 163 registrations expired before the 2026-09-02 reference date and 41 expire before 2027-01-01; the grid shows them with no mark. There is no free slot on the card and no i18n key for it, and inventing an English string on an Italian-default screen would break rule 11. **Recommendation:** add i18n keys `portExpired` / `portExpiringSoon` and a fourth line to the card, then I (or whoever assembles) can feed it from `p.expiry` + `AM.daysFrom`. Flagging it because showing a "verified label match" on an expired authorisation is a new false claim the portal would be making on its own.
- **SPECIALI is 6, not the 5 the guidance names.** The five catalog Speciali are BREVIS, BUDGE, EXELGROW, PARLEAF, POWERFILM (commercial tab shows exactly those five). The sixth is **LUMA-KL**, registry-only, which `CATEGORY_OF` maps to SPECIALI because its `line` is `OUTRA`. The regulatory tab therefore shows BREVIS, LUMA-KL, POWERFILM. I did **not** "fix" this — it is the model's derivation from a real field, and hiding LUMA-KL would be hiding a registration.
- **`strengthFor()` still returns `LABEL_CHECK_NEEDED`** as a fallback (`italy-app-model.js` line ~524: any product with *any* link on the same crop). My block does not call it, but any block that does will resurrect the amber class that the collection itself no longer contains — the two disagree. That is the model owner's to reconcile, and the spec's open question 6 (a fifth `NOT_ASSESSED` state) is still unanswered.

==========================================================================================

Block written to `C:\eame-sintonia\italia-portale\audit\blocks\nav.js` and validated.

## Validation
`node audit/splice.mjs try nav` → **50/52 screen renders pass**. The 2 failures (`it/en · Action brief`, `Cannot read properties of null (reading 'doc')`) are **pre-existing and not mine** — I proved it by removing `nav.js` and running `try signal`: identical 50/52 with the same two failures. Blocks spliced alongside mine at the time of the run: signal, product, portfolio, voci, future.

Fixture-read scan over the spliced scratch, restricted to my block's new line range (2602–2645): **0 `DATA_BEARING_CORE` reads, 0 mentions of any forbidden global.** Before, the same block held 2 (`D.FIELD_MESSAGES` at 2603, `D.WINDOW_KPI` at 2608) plus an untracked `window.ITALY_MARKET` read.

## Legacy fixture reads removed

| line | symbol | replaced by |
|---|---|---|
| 2603 | `D.FIELD_MESSAGES` | `AM.collections.fieldMessages.records` (provenance `SYNTHETIC_DEMO`, real 0, demo 18) |
| 2608 | `K.total` (= `D.KPI.total` = `D.CASES.length`) | `AM.counts.windows` |
| 2608 | `D.WINDOW_KPI.total` | `AM.counts.windows` |
| 2608 | `window.ITALY_MARKET.CROPS.length` | `AM.counts.marketObservations` |
| 2608 | `K.activities` (`D.KPI.activities`) | `AM.counts.competitorActivities` |
| 2608 | `K.records` (`D.KPI.records`) | `AM.counts.scienceRecords` |
| 2608 | `K.archive` (`D.KPI.archive`) | `AM.counts.archive` |
| 2608 | `K.orgs + K.people` (`D.KPI`) | `AM.counts.sources` |

Also removed the `AM ? … : 0` inline guards on future / voices / portfolio and replaced them with one helper, `navN(k)`, which returns the model count only when it is actually a number. It does **not** coalesce with `|| 0`, so a genuine zero renders as zero instead of being indistinguishable from a missing model.

**Reads kept with a marker: none.** My block has zero fixture reads, so no `@VISUAL_ONLY` or `@EXPLICIT_DEMO` marker was needed. Note the scanner is not comment-aware — my first draft failed the scan because the strings `D.FIELD_MESSAGES` and `ITALY_MARKET` appeared inside explanatory comments. I reworded them. **Any agent writing prose that names a fixture symbol will trip D1 the same way.**

## Before / after on screen (measured just now)

| nav item | before | after |
|---|---|---|
| Radar delle Opportunità | 29 | **29** (source changed only) |
| Radar Futuro | 3 | 3 |
| Finestre Colturali | 29 | **29** (source changed only) |
| Polso di Mercato | 8 | **77** |
| Voci dal Campo | 17 | 17 |
| Concorrenza | 72 | **503** |
| Intelligence Scientifica | 36 | **88** |
| Portafoglio | 166 | 166 |
| Archivio | 448 | **774** |
| Fonti | 92 | **31** |
| *INTEGRAZIONI · DEMO* → Rete Commerciale di Campo | 18 | 18 (still demo, still amber) |

Radar and Finestre look like a no-op. They are not: the 29 demo `CASES` are a 1:1 shadow of the 29 canonical windows, so the value coincides today and will diverge on the next data load. Do not "revert the no-op".

Numbers drift while the model is being rewritten by the other agent — `marketObservations` read 76 then 77 (a `WINE` row came back), `archive` read 773 then 774. That is the model moving, not my block.

## Decisions where I departed from the spec, or where the spec is stale

- **`market` badge = `AM.counts.marketObservations` (77), not a crop count.** The spec's markupImpact table predicted "market 8". There is no honest 8. The market-pulse fixture's 8 crop tabs include Tomato, Sugar Beet and Apple, for which the real corpus holds **zero** rows. I also measured that `marketObservations` records carry **no `crop` field at all** — only `group` (CEREAL 40 / OLIVE_OIL 36 / WINE 1) and `product` (14 distinct series, some of them raw codes like `BLTPAN|PAN` and `DUR|UNKNOWN`). So a crop-level badge cannot be derived without a projection that does not exist. **No `marketByCrop` projection has landed** — I re-read `italy-app-model.js` at the end: 38 collections, no `marketByCrop`, and `AM` still exposes only the documented top-level keys. If the market agent lands a crop-level projection, this badge should be re-pointed to it; until then 77 = "real price observations behind this screen".
- **The market fixture has already been stripped by another agent.** `window.ITALY_MARKET` no longer has `TEMP`, and its crop objects are down to `key/label/it/crop/color`. This is why the whole suite read 0/52 for a while — `mkCropTemp` (head, line 2574) and `mkTemp` (calendar, line 2653) still read the old shape. Those belong to the head and calendar agents. It also means the old market badge would now be counting label-only stubs.
- **`allMessages` now comes from the model, not the fixture.** I verified field-by-field that `AM.collections.fieldMessages.records` is identical to `D.FIELD_MESSAGES` on all 31 keys, including the joins downstream blocks read: `caseObj` filled on 10/18 in both, `signalObj` on 2/18 in both, `caseId` 9/18, `state`/`region`/`mtype`/`person` 18/18, `product` 10/18. States: CONNECTED 8, NEW SIGNAL 4, NEEDS VALIDATION 3, CLASSIFIED 3. No object identity is relied on anywhere (case block 2632, field block 3117/3124/3126/3130/3148 all compare by value), and the field screen rendered clean in both languages.
- **`archive` = 774 is an index, not a corpus.** `AM.collections.archive` has provenance `REAL_DERIVED`, note "index over the normalized model; no manufactured rows" — it re-indexes science, market, competitor, voices, events, news and windows. It is the right number for "rows the Archive screen lists", but it must never be added into a grand total elsewhere. That is the transparency-panel agent's problem, and the spec flags it as the highest-risk item in this domain.
- **Spec numbers that have already moved:** archive 740 → 774, marketObservations 77 → 76 → 77, sources 31 (stable), competitorActivities 503 (stable), scienceRecords 88 (stable).

## Contract
Still declared: `allMessages`, `navDef`, `navIntegrations`, `nav`, `navIntegrationItems`, `activeOf`, and `on` (unchanged `const on = activeOf[s.view] === n[0]` inside both maps). Verified live: active-state highlighting still works — view `competitors` lights only "Concorrenza" in the green group, view `field` lights nothing in green and "Rete Commerciale di Campo" in amber.

## Markup edit still required (I cannot apply it)

`client/portale.html` line 66:

```
<sc-for list="{{ nav }}" as="n" hint-placeholder-count="6">
```
→ `hint-placeholder-count="10"`

Purely cosmetic — it is the number of skeleton rows drawn before data arrives, and the list has 10 items. Nothing factual depends on it. **No other markup change is needed for this block:** lines 66–73 and 76–83 bind `n.label` / `n.count` / `n.go` / the colour props, all of which I still export with the same names and types. The amber INTEGRAZIONI · DEMO group at lines 75–83 is untouched and must not be merged back into the core nav.

## What the screen no longer shows

Nothing was removed from the nav — all 10 core entries and the 1 demo entry survive. What changed is that four badges now tell the truth and three of those are much larger, one much smaller. The "Fonti" badge dropping from 92 to 31 is the one that will read as a regression to anyone who memorised the demo: it fell because the old number summed 53 demo organizations with 39 demo people, and 7 of those "people" were invented ADAMA Technical Sales Representatives — internal staff, which §1 forbids from the core entirely. Real people are a separate collection (15 with documented role evidence, 60 OpenAlex researchers, 66 distinct names in the union) and belong on the Sources screen, counted separately, never folded into a badge labelled "Fonti".

==========================================================================================

**BLOCK WRITTEN:** `C:\eame-sintonia\italia-portale\audit\blocks\voci.js` — validates at **50/52** (`node audit/splice.mjs try voci`). Both remaining failures are `it · Action brief` / `en · Action brief` (`Cannot read properties of null (reading 'doc')`), which belong to the `brief` block, not mine. Both my screens (`voices`, it + en) render clean.

# 1 · Legacy fixture reads removed

**None — and that is the honest answer.** The old block (portale.html 3049–3081) already read only `AM.collections.voices`. It contained zero `D.*` / `window.ITALY_DEMO` / `ITALY_MARKET` / `ITALY_SCIENCE` reads, and zero RTV / Field Sales records. My block also reads **zero fixtures** and carries **zero `@VISUAL_ONLY` / `@EXPLICIT_DEMO` markers** — there was nothing worth keeping.

The damage on this screen was a different class: **the migration to `AM` was done but never re-measured against what `AM` actually returns.**

# 2 · What was actually on screen, measured (n=17, 17 real, 0 demo, 0 rejected, `REAL_SOURCE`, `ITALY_INGEST.VOICES`)

| # | old code | what the client saw | measured | now |
|---|---|---|---|---|
| a | `proves: v.proves \|\| ''` (3066) | **`[object Object]`** | 17/17 | i18n standing caveat, see §3 |
| b | `notProves: v.notProves \|\| ''` (3066) | **`[object Object]`** | 17/17 | idem |
| c | `roleLine: [v.role, v.organization]…` (3060) | **`NAO SEI · NAO SEI`** | `ROLE` 17/17 = `"NAO SEI"`, `ORGANIZATION` 17/17 = `"NAO SEI"` | `CANALE · <channel>` |
| d | `region: v.region \|\| …` (3064) | **`NAO SEI`** | `REGION` 17/17 = `"NAO SEI"` | `Regione non dichiarata` |
| e | `date: v.date \|\| v.dateRelative` (3062) | **`NAO SEI`** | `DATE` 17/17 = `"NAO SEI"` | `≈ N anni fa` |
| f | `crop: cl(v.crop)` (3063) | `DURUM_WHEAT` | `T.CROPS` is keyed on `"Maize"`/`"Grapevine"`, not on the tokens | `Frumento duro` / `Durum Wheat` |
| g | `issue: il(v.issue)` (3063) | `FLAVESCENCE`, `WEED` | `T.ISSUES` has no entry for any of the 3 tokens | `Flavescenza`, `Infestanti`, `Fusarium` |
| h | `caseGo/hasCase` (3068) | clickable dead route | `CASE_ID` present 17/17, **resolves 0/17** against `AM.collections.opportunities` (`IT-VINE-FLAVESCENCE` vs the real `IT-OPP-001..003`) | dropped |

**(a)/(b) are the headline.** `AM` normalises `WHAT_IT_PROVES` / `WHAT_IT_DOES_NOT_PROVE` through `narrative()`, so they are objects, and an object is truthy — `v.proves || ''` returned the object, and the template stringified it. Measured state: `NOT_APPROVED_FOR_DISPLAY` **17/17 on both fields**, `CLEAR` 0/17. So the mission's "do not render the Portuguese notes" was already satisfied by accident, at the cost of printing `[object Object]` 34 times.

**`RT3` did not catch this.** `checks.mjs:543` walks the props tree and recurses *into* objects; the string only materialises at template interpolation, which the harness does not perform. RT3 is a false green for any narrative object left in a props slot — worth a check that flags "a `{state,it,en}` object sitting in a leaf prop".

# 3 · The one judgement call I made — say no and I will flip it

`proves` / `notProves` now fall back to **`T.vociProvesDefault` / `T.vociNotProvesDefault`**, the two approved localized strings already shipped in `italy-i18n.js:225 / 509`. `nar()` is tried first, so approved per-record prose wins the day upstream supplies it.

Justification: `vociNotProvesDefault` ("Non prova incidenza regionale, domanda, efficacia di prodotto né tendenza di mercato. Un commentatore non è necessariamente un agricoltore.") is the single most important sentence on this screen given `PERSON_IDENTITY_STATE` = not-attributable 17/17 and `REGION` unknown 17/17. Deleting it makes the screen *less* honest. `vociProvesDefault` ("Questa dichiarazione è stata resa pubblicamente da questa fonte.") is exactly and only what `SOURCE_URL` 17/17 proves.

**Be clear about the cost:** these are collection-level rules, byte-identical on all 17 cards, not per-record findings. I expose `provesStanding` / `notProvesStanding` (`true` 17/17) so the caption can say so. If you want them gone entirely, set `hasProves`/`hasNotProves` from `nar()` alone and add the two `sc-if`s in §5 — the props are already there.

# 4 · What the screen no longer claims

- **No role, no organisation, ever.** Not one of the 17 records evidences either. The green line under the handle now says where the sentence was published (`CANALE · Agricoltura Innovativa`), with an explicit `CANALE`/`CHANNEL` prefix so a channel cannot be misread as an employer. Channel is real 17/17.
- **No region.** Fixed `Regione non dichiarata`, `hasRegion: false` on 17/17. §9 held: `COUNTRY_OF_FACT` is `NOT_KNOWN` on **15/17**, `IT` on only 2.
- **No calendar date.** `DATE` is the sentinel 17/17, so `AM.daysFrom()` is null 17/17 and `AM.REF` cannot position these records. The only temporal evidence is YouTube's own relative stamp, anchored to the crawl, not to 2026-09-02 — hence `≈` and never a computed date. `hasExactDate: false` on 17/17.
- **No opportunity link.** See (h).

**The new number the client will see, and should:** this "newsroom" is old. Measured spread — `≈1 anno` 2, `≈2` 1, `≈3` 2, `≈4` 4, `≈6` 4, `≈7` 3, `≈13` 1. Mode is 6–7 years. Without the stamp the screen reads as current, which is the bigger lie; that is why I kept it rather than blanking it.

**A number nobody had counted:** `person` handle == `channel` handle on **7/17** — the publisher replying under its own video, not an independent grower. Exposed as `isChannelOwner` / `channelOwnerCount`. All 7 are `TECHNICAL_REPLY`; all 7 `FIRST_PERSON_FIELD_REPORT` records are independent.

The featured/latest split is now that measurement, not `slice(0,2)`: **featured = the 2 most recent first-person field reports that are not the channel's own account** (`IT-VOICE-001` ≈1 anno, `IT-VOICE-003` ≈2 anni); latest = the other 15, newest first. It is an ordering over real fields, not a verdict. Nothing in `VOICES` says "featured" — if you want that claim gone, `hasFeatured:false` + all 17 into `latest` is one line and needs no markup change.

`themes` reconciles to 17: **Flavescenza 8 / Infestanti 8 / Fusarium 1** (was the same counts, unreadable tokens).

# 5 · Markup edits still required (I could not make them)

Four spots in `C:\eame-sintonia\italia-portale\client\portale.html`. None are blocking — my props are safe strings so nothing breaks today — but each is a claim the data does not carry.

1. **1456–1459** — the featured card's `{{ t.lblProves }}` / `{{ t.lblNotProves }}` rows are unguarded. Wrap the pair in `<sc-if value="{{ v.hasProves }}">` and `<sc-if value="{{ v.hasNotProves }}">`. Same at **1486–1487** for the latest card's not-proves row. Required only if you reject §3's fallback.
2. **1453** — the region chip `<span>{{ v.region }}</span>` is unguarded. Wrap in `<sc-if value="{{ v.hasRegion }}">`; it is `false` 17/17, so the chip disappears rather than printing "Regione non dichiarata" on every card.
3. **1430** — the hard-coded `ITALIA` badge next to the `VOCI DAL CAMPO` title. `COUNTRY_OF_FACT` is `NOT_KNOWN` on 15/17. This is the §9 `REACHED_IN_ITALY != TARGETED_ITALY` trap in literal form. Remove it or qualify it.
4. **1431 / `italy-i18n.js:240`** — `subVoices` reads "ciò che dicono agricoltori, tecnici e canali italiani". `ROLE` is unknown 17/17, so we cannot say any of them is a grower or an advisor. Suggested: *"Commenti pubblici raccolti su canali YouTube italiani. Ruolo e regione di chi scrive non sono verificabili."*

Two i18n values are also now mislabelled: `vociFeatured` "IN EVIDENZA" would be more honestly "PIÙ RECENTI · SEGNALAZIONI IN PRIMA PERSONA", and `vociLatest` "ULTIME VOCI" is misleading over 1–13-year-old material — "ALTRE VOCI" is truer. (`vociThemes` "TEMI EMERGENTI" is defined but never bound — good, leave it unbound; "emerging" over 13-year-old comments would be a fabrication.)

# 6 · Things the spec / model owe this screen

- **`audit/blocks/voci.spec.json` is the wrong spec.** Its single entry has `domain: "Helper relationships, visual tokens, Field Sales, reference date, localization"` and its 10 `fieldsThatDie` are all about `D.CAT`, `D.F_COLOR`, `D.GROUP_COLOR`, `D.FIELD_MESSAGES`, `D.REGION_STATS`, the competitor crop axis and the person activity history. Not one names `publicVoices`. I had no analyst spec and measured the domain from scratch; every number above is mine.
- **`AM` does not scrub the `"NAO SEI"` sentinel outside `narrative()`.** `UNKNOWN_SENTINEL` exists at `italy-app-model.js:97` but only `narrative()` applies it; plain `S()` fields pass it straight through. Every block consuming `role`/`organization`/`region`/`date` on any family is exposed to the same bug I just fixed locally. **This belongs in `S()` or in a shared exported `AM.kn()`, not in seventeen blocks.**
- **`CROP_BY_TOKEN` (`italy-app-model.js:413`) is not exported**, although its own comment says it is the map for "crop tokens used by SCIENCE / VOICES / THEMES", and the model already applies it to `scienceThemes` (1349) and `news` (1701) as `cropCanonical`. It is **not** applied to `publicVoices`. Please add `cropCanonical` to the voices adapter and export the table; my block carries a duplicate copy, marked as such, purely so it does not guess.
- **There is no issue-token label map anywhere.** I localize only the 3 tokens present (`WEED`→Infestanti/Weeds, `FLAVESCENCE`→Flavescenza/Flavescence, `FUSARIUM`→ left as the Latin genus per §11) and deliberately do **not** sharpen: `FUSARIUM` never becomes "Fusarium Head Blight", `FLAVESCENCE` never gains "dorata". Unmapped tokens render verbatim.
- **A likely upstream mis-tag, not mine to fix:** `IT-VOICE-001` is tagged `CROP=DURUM_WHEAT`, `ISSUE=FUSARIUM`, but its quote is *"Io ho usato la CORNALINA"* under an AIPO Verona video titled *"Utilizzo dello Spinosad - Spintor Fly"* — a **olive fruit fly** bait. It is currently the #1 featured card and the sole record behind the "Fusarium · 1" theme chip. Worth an ingest check.

**Note for whoever assembles:** `const nar` is already declared at renderVals top level by `audit/blocks/signal.js:14`. My `nar`, and every other helper I define, is scoped **inside the `if (AM) { … }` block** on purpose so it shadows instead of colliding. Do not hoist them. Contract names `k`, `themes`, `voices` are all still declared.

==========================================================================================

Block written to `C:\eame-sintonia\italia-portale\audit\blocks\product.js`. `node audit/splice.mjs try product` → 52/52 screens render in IT and EN; spliced solo it renders all 166 products in both languages with 0 throws.

## Fixture / dead reads removed

| old line | symbol | what replaced it |
|---|---|---|
| 3003–3004 | `D.WINDOWS.filter(...)`, `color: w.open ? …` | `AM.collections.cropWindows` (29 canonical), exact crop×issue join. Status now `wst(x.canonicalStatus)`, colour `x.ui.status.text`. The demo window record had no `canonicalStatus` key, so **all 9 products printed "DATA DA CONFERMARE" on every window** — now they print the real status (FINESTRA APERTA / CHIUSA / PROSSIMO CICLO). |
| 3002 | `region: l.region` | Model link rows have no `region` → **19/19 rendered relationship rows had a blank second line**. A label authorisation is national; and no region is derivable either (6 crop×issue keys carry >1 window in different regions). The line now carries the row's evidence, localized from the model's own English `evidence` string. |
| 3002 | `go: () => l.caseId && this.openCase(l.caseId)` | Link rows have no `caseId` → every row was inert. Now: exactly-one matching canonical window → `openWindow`; ambiguous or none → inert. Measured: **6 of 236 rows clickable, 230 inert.** |
| 3006–3007 | `r.SPECIES` / `r.SPECIES_IT` / `r.MECHANISM` | Model renamed these to `species`/`speciesIt`/`mechanism` → the resistance card rendered for **0 of 166 products**. Now `species`, genus **+ species** match (old code matched genus only, which would tie an *Amaranthus retroflexus* product to *Amaranthus palmeri* resistance — 49 products match on species vs 65 on genus). |
| 3007 | `mech: String(r.MECHANISM…).slice(0,44)` | `mechanism` is `NOT_APPROVED_FOR_DISPLAY` on **34/34** records. Line now carries `authority · regions`. |
| 3005, 3019 | `sigs`, `hasSigs` (`A_SIGREAL`) | Deleted. No markup binds `pd.sigs` anywhere in portale.html. |
| 3014 | `pd.moa` | Deleted. `e.regulatory.moa` and `.MODE_OF_ACTION_DECLARED` do not exist as keys (the record carries `hrac`/`frac`/`irac`), so it printed "NON OSSERVABILE" for 166/166 — into a slot no markup binds. |
| 3009 | `ai: e.ai \|\| T.prodNotObservable` | `ai` is an array → printed unseparated. Now `join(' + ')`. The 3 catalog-only products (BUDGE, EXELGROW, PARLEAF) read `T.ksNotKnown` ("non noto"), **not** "non osservabile" — an active ingredient is public, this catalog reading just didn't carry it. |

**Reads kept with a `@VISUAL_ONLY` / `@EXPLICIT_DEMO` marker: none.** The block reads only `AM`, `T`, `s`, and the earlier helpers `cl`/`il`/`wst`. Zero fixture reads (scanner run against the spliced scratch: 0).

## Before / after on screen

```
                          BEFORE        AFTER
products with verified card     6            6
products with related card      0 (no card) 19   <-- 16 of them see NOTHING today
products with check-needed card 0            0   <-- class is empty in the model
products with not-confirmed     6            6
products with "no relationship"140          140
windows card                    9            9   (statuses were all fake before)
resistance card                 0           49
relationship rows w/ blank line 19            0
```

Relationship collection today: **236 rows — 12 VERIFIED_LABEL_MATCH, 217 RELATED_PORTFOLIO, 7 NO_CONFIRMED_MATCH_CURRENT_READING, 0 LABEL_CHECK_NEEDED.** 26 of 166 products carry any row.

## Markup edits still required (I could not make them)

**1. BLOCKING — no card exists for RELATED_PORTFOLIO.** It is 217 of 236 rows and the *only* class 19 products have. For **16 products** (APYZA 500 WG, APYZA WG, BLAISE ULTRA, DURAVIS, ELTIRA, GLIPHOGAN TOP CL PFNPE, HERBITOTAL CL PFNPE, KOJAMI, LEBRON 0.5 G, PYXIDES WG, SCHERMO 0.5 G, SESTO GOLD, SHAMAL MK PLUS CL PFNPE, SPYRALE, STAVENTO, TAIFUN MK CL PFNPE) the CONNESSIONI DI PORTAFOGLIO section **renders an empty grid** — the heading with nothing under it. LEBRON 0.5 G has 25 real registry rows and shows none. I refused to fold them into the amber "RELAZIONI DA VERIFICARE" card (a registry use row is evidence, not a to-do) and refused to fire `pd.noRel` (that would be a lie). `pd.related` / `pd.hasRelated` / `pd.relatedCount` are computed and waiting.

Insert between line 1368 (`</sc-if>` closing the check-needed card) and line 1369 (`<sc-if value="{{ pd.hasRejected }}">`):

```html
          <sc-if value="{{ pd.hasRelated }}" hint-placeholder-val="{{ false }}">
          <div style="border-radius:14px;border:1px solid rgba(203,197,195,0.10);background:#1C1817;padding:14px 16px;display:flex;flex-direction:column;gap:9px;border-top:3px solid #5CC3EE">
            <span style="font-size:9.5px;font-weight:700;letter-spacing:0.11em;color:#5CC3EE">{{ t.prodRelatedRel }}</span>
            <sc-for list="{{ pd.related }}" as="r" hint-placeholder-count="2"><span onClick="{{ r.go }}" style="display:flex;flex-direction:column;gap:1px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);cursor:pointer"><span style="font-size:11.5px;font-weight:600;color:#fff">{{ r.crop }} · {{ r.issue }}</span><span style="font-size:9.5px;color:#8F8886">{{ r.region }}</span></span></sc-for>
          </div>
          </sc-if>
```

New i18n key needed (`prodRelatedRel`), next to `prodCheckRel` at italy-i18n.js:245 / :529:
- it: `'PORTAFOGLIO CORRELATO · REGISTRO'`
- en: `'RELATED PORTFOLIO · REGISTRY'`

(`#5CC3EE` is `AM.STRENGTH.RELATED_PORTFOLIO.color`, not a hand-picked colour.)

**2. `{{ r.region }}` at markup 1360, 1366, 1372 should be renamed `{{ r.evidence }}`.** The prop name now lies about its content — it holds the evidence line, deliberately, because a label authorisation has no region. I kept the name `region` only because the markup is frozen. Nothing renders differently after the rename; I will add the alias when you tell me.

**3. Italian crop names missing from `T.CROPS` (italy-i18n.js:70): Barley, Potato, Sorghum, Triticale.** 52 of 236 relationship rows sit on these crops and would print an English crop name in the Italian portal. **0 visible today** (all 52 are RELATED rows with no card) — this becomes visible the moment edit 1 lands.

## What the spec asked for that the data cannot support

- **`moaLabel` from hrac/frac/irac (70/163 products).** Real and worth having, but this screen has no MoA slot — `pd.moa` was never bound in markup. If you want it, add a fifth cell to the identity grid at markup 1345–1350 and I will feed it.
- **"Latin target + labelUrl on the check-needed rows".** There are 0 check-needed rows, and the product-entity link objects the model exposes carry only `{crop, issue, strength, evidence, source}` — no per-row target, reg number or clickable URL. On a RELATED row the `issue` **is** the Latin target (that is why MAXENTIS reads "Barley · *Blumeria graminis*"), and `source` is the label URL, but there is no anchor in the markup to hang it on.
- **`region` relabelled as the window's region.** Not derivable: 6 crop×issue keys map to more than one window in different regions.
- **A dose / stage / target-fit component.** Not built, per the spec's measurement (219/219 timing rows say the column was not extracted; `maxApp` null 219/219).

## Also true and unpleasant

- `pd.hasCheckNeeded` is wired but the amber card will never appear until the model's tier-3 LABEL_CHECK_NEEDED lands. Today the class is 0 rows.
- 230 of 236 relationship rows are inert while the markup still paints `cursor:pointer` on them. Fixing that needs a markup change I did not make.
- The resistance card merges GIRE's per-mechanism records by species (Lolium spp. alone has 5). GIRE's `regions` array is not a clean enum — of 37 distinct values, 6 carry a Portuguese research tail after an em dash and 5 a Portuguese parenthetical, plus one literal `NAO SEI`. I strip the tail, strip the parenthetical, drop the marker; 19 real Italian region names survive and 0 rows still leak Portuguese (verified across all 49 products).
- `pd.goOpps` → `radarWith({ fProduct: e.name })` is unchanged. Note the radar's product filter still only knows 33 names, so for 133 of 166 products the CTA lands on an unfiltered radar. That is the radar block's fix, not mine.
- `AM.ABSENCE_RULE` resolves to the English fallback (`RAW.LABEL_AUDIT.ABSENCE_RULE` is empty), so I did not pass it through — the not-confirmed card already prints the localized `t.absenceRule` ("Non trovato in questa lettura delle etichette. Non significa che ADAMA non abbia un prodotto."), which is what the rule requires.

==========================================================================================

Block written to `C:/eame-sintonia/italia-portale/audit/blocks/future.js` (122 lines). Validated: `node audit/splice.mjs try future` → **52/52 screen renders pass** with 13 blocks spliced (helpers, head, nav, calendar, windows, signal, market, product, portfolio, voci, brief, field, future).

## Legacy fixture reads removed (5 of 5 in my range — scanner now reports 0 `D.*` reads in lines 3132-3155)

| old line | symbol | replaced with |
|---|---|---|
| 3139 | `D.CAT.disease` (+ `cat:'disease'`, `color:'#00A0DF'`) | `AM.categoryOf(f.issueType)`. FUTURE_SIGNALS has **no ISSUE_TYPE field at all** → `CATEGORY_UI.unknown` on 3/3. IT-FUT-003's ISSUE is literally `REGULATORIO` and was being painted Disease-Control blue. |
| 3149 | `D.WINDOWS.find(...)` ×2 (crop+region, then crop-only fuzzy issue match) | `AM.collections.cropWindows`, resolved by **id only** (`windowId`/`cropWindowId`/`windowIds[0]`). Measured 0/3 real signals carry any window reference; `nextWindow` is `NOT_ESTABLISHED` on 2/3 and `NOT_APPROVED_FOR_DISPLAY` on the third. The old name join also matched 0/3 anyway — signal crops are upstream's `MAIS` / `TRIGO e TRIGO DURO` / `TRANSVERSAL`, cropWindows is canonical `Maize` / `Wheat` / `Durum Wheat`. |
| 3150 | `Object.keys(D.F_COLOR)` | `[...new Set(sigPool.map(x=>x.status).filter(Boolean))]`. **status is null on 3/3 real signals** → empty vocabulary. |
| 3151 | `D.F_COLOR` merged into `fColor` | deleted; locally-authored `F_ACCENT` is now a pure lookup, with `F_MUTED '#8F8886'` whenever status is absent or unrecognised. |

**Reads kept with a marker: none.** My block contains zero `D.*` reads, marked or unmarked. It touches the Field Sales demo only through the already-existing `allMessages` variable, and gates the result structurally (below).

## Also removed, not in the spec

- **The 7-name English source taxonomy** (`fSourceDef`: Science / Researchers / Field network / Regulatory / Technical media / Producer organizations / Competitor movement) and the dead ternary `f.sourceIds.length ? T.frUpstream : T.frUpstream`. Every real signal was stamped "INTELLIGENCE A MONTE" and **all seven KPI cards read 0** with scenarios off. Replaced by the classes the signals actually cite, resolved id→registry: IT-FUT-001/002 cite `IT-SRC-OPENALEX` (RESEARCH) + `IT-SRC-MINISTERO` (OFFICIAL); IT-FUT-003 cites `IT-SRC-CELLAR` + `IT-SRC-MINISTERO` (both OFFICIAL).
- **`productLabel: x.product || 'Check needed'`** — hard-coded English, and a verdict on a portfolio gap (§10). Now the product name only when the record names one *and* `AM.findProduct` resolves it; otherwise `T.ksNotKnown`. `goProduct` no longer routes to `radarWith({fStatus:'VALIDATE'})`, a filter value that no longer exists in any vocabulary.
- **`lastObserved: f.raw.DATE`** — `raw.DATE` is `undefined` on 3/3. The registry's `LATEST_OBSERVATION` (2026-07-30, 2026-08-24) is when the *source* was last read, not when the signal was seen, so it is not promoted into an "Updated" claim.
- **`fromField`** now requires `x.isScenario`. Measured, the 18 Field Sales messages reference `IT-SIG-003` and `IT-SIG-005` — both scenarios — so nothing changes today, but the gate is structural so a fixture edit can never light "NUOVO SEGNALE DI CAMPO" on a real record.
- **`region`** — the model now nulls the two upstream REGION values that were Portuguese research notes (`"NAO SEI — o recorte cientifico e por afiliacao nacional, nao por regiao de estudo"`). The card hard-codes `{{ crop }} · {{ region }}`, so null would have printed an orphan separator; it now prints `non noto` / `not known`.
- **Stale-filter guard**: `s.futureStatus` / `s.futureSource` are ignored unless the value is in the live vocabulary, so turning scenarios off cannot leave the feed empty with no chip left to clear the filter.

## Before / after on screen (measured on the spliced scratch, scenarios OFF = default)

| | before | after |
|---|---|---|
| status filter chips | 8 (ALL + 7), **all seven reading 0** | **0 — the entire row disappears** |
| source KPI cards | 7, **all reading 0** | 2 — `UFFICIALE:3`, `RESEARCH:2` (EN `OFFICIAL:3`, `RESEARCH:2`) |
| cards | 3 | 3 (`sigCountReal` unchanged) |
| card category rail / icon | Disease-Control blue `#00A0DF` + disease icon on 3/3 | neutral `#8F8886`, no icon, no category label on 3/3 |
| card source chip | `INTELLIGENCE A MONTE` on 3/3 | `RESEARCH · UFFICIALE`, `RESEARCH · UFFICIALE`, `UFFICIALE` |
| card status pill | blank (F_TEXT[null]) | blank, and now explicitly `''` with muted colour |
| NEXT WINDOW | blank (0/3 matched) | `non noto` / `not known` |
| PORTFOLIO | `Check needed` (English, 3/3) | `non noto` / `not known` |
| Updated | `—` | `non noto` (row should be hidden — see markup) |
| WHY WATCH / WHO IS TALKING | empty | still empty; now flagged `hasWhy:false` / `hasWho:false` on 3/3 |
| scenarios ON | 8 chips, 7 KPIs, 59 pooled | 8 chips, **9 KPIs** (7 scenario + 2 registry, deliberately not merged), 59 pooled, 16 shown, 43 remaining — unchanged behaviour |

## Markup edits still required (I cannot edit `client/portale.html`)

I export the guards; four one-line wraps are needed in the FUTURE RADAR card, all inside `<sc-for list="{{ visibleSignals }}" as="s">`:

1. **line 1530** — wrap the category icon span in `<sc-if value="{{ s.hasCategory }}">…</sc-if>`. `CATEGORY_UI.unknown.iconAsset` is `''`, so `background:url()` is an empty request on 3/3 real cards.
2. **line 1532** — wrap the whole WHY WATCH div in `<sc-if value="{{ s.hasWhy }}">…</sc-if>`. `whyWatch` is `NOT_APPROVED_FOR_DISPLAY` on 3/3, so the label "PERCHÉ OSSERVARE" currently renders above nothing.
3. **line 1533** — wrap the whole WHO IS TALKING div in `<sc-if value="{{ s.hasWho }}">…</sc-if>`. Real records carry no who-breakdown; the label renders above an empty chip row.
4. **line 1535** — wrap `<span>Updated {{ s.lastObserved }}</span>` in `<sc-if value="{{ s.hasLastObserved }}">`, **and** replace the hard-coded English `Updated` with `{{ t.frUpdated }}` (the key exists: `Aggiornato` / `Updated`).

Two further defects visible on my screen but owned elsewhere:

5. **line 1503** (header) — `{{ t.frSubA }} {{ kpi.signals }} monitored signals across Italy.` hard-codes an English tail that renders untranslated in Italian. `kpi.signals` comes from the `head` block.
6. **`nar` collision at assembly time** — `audit/blocks/head.js`, `signal.js`, `voci.js` and `competitor.js` each declare `const nar` in the same function scope; the splicer intermittently died on `Identifier 'nar' has already been declared`. My block uses `fNar` and is unaffected, but assembly will fail until three of those four are renamed. (A `cnt` collision in `field.js` appeared and was fixed mid-session.)

## What the spec asked for that the data cannot support

- **A status treatment.** The spec's open question ("plain DA VALIDARE, or does the dimension disappear?") — I chose disappear. `PROMOTED_TO_RADAR` is `"false"` on 3/3 and is a boolean, not a seven-level assessment; there is no honest derivation. The whole chip row including "TUTTI" is gone, because a lone `TUTTI · 3` filter that filters nothing is noise.
- **`AM.UI.SIGNAL_STATUS_COLOR`** (spec line 513) does not exist in `italy-app-model.js` — I re-read the file at the end of the session and `AM` still exports no `UI` key. The colour tables are authored locally in my block, as presentation, and never define the vocabulary.
- **i18n gap.** `T.SRCTYPES` / `T.EVCHIP` only cover the old scenario vocabulary; the registry enum (`RESEARCH`, `MARKET`, `COMPANY`, `PEOPLE`, `RESEARCH_INSTITUTION`, `COOPERATIVE`, `PRODUCER_ORG`, `TECHNICAL_MEDIA`, `COMPETITOR`, `ADAMA`) has no approved translation. `OFFICIAL` resolves via EVCHIP to `UFFICIALE`; `RESEARCH` shows its raw token in both languages. I deliberately did **not** alias `RESEARCH`→`Science`: with scenarios on that produced two identically-labelled KPI cards, one demo (10) and one real (2).
- **Upstream crop vocabulary.** `MAIS`, `TRIGO e TRIGO DURO`, `TRANSVERSAL` are not keys in `T.CROPS`, so the cards print upstream's uppercase Portuguese in both languages. Normalizing them to canonical crops is upstream work; doing it in a view would be exactly the quiet fixing this mission forbids.

## Blunt summary of what the screen no longer shows

With the demo toggle off, Future Radar is three grey cards. No category, no status, no status filter row, no "why watch" text, no "who is talking" chips, no window, no portfolio product, no observation date. What it does show is real and traceable: three issue names, three crop names, one region (`UE`), and which classes of named source each signal cites — OpenAlex, the Ministero della Salute register, and EUR-Lex CELLAR. Two of the seven original source cards survived; five were counting a taxonomy no real record could ever match.

==========================================================================================

**Block written:** `C:\eame-sintonia\italia-portale\audit\blocks\windows.js` (190 lines, replaces portale.html 2867-2888)
**Validation:** `node audit/splice.mjs try windows` → **52/52 screen renders pass** (IT + EN) with every other landed block spliced in. *Caveat below.*

---

## 1 · Legacy fixture reads removed (20 → 0)

Measured with the scanner's own rule (`\bD\s*\.SYM` on my block text): **0 fixture reads remain, and 0 markers were used.** Nothing in this block is `@VISUAL_ONLY` or `@EXPLICIT_DEMO` — I did not need to keep a single one.

| old line | symbol | replaced by |
|---|---|---|
| 2868 | `D.WINDOWS.find(caseId)` in `winFor` | `WROWS.find(w => w.legacyCaseId === caseId)` — `legacyCaseId` filled **29/29**, plus a null guard (the old call dereferenced `.id` on a miss and would have thrown) |
| 2870 | `this.decorate(w.c)` (case fixture decorated onto the window) | dropped; `wd.c` is rebuilt from `record.verifiedProducts` / `record.labelVerdictState` |
| 2870 | `w.open`, `w.remaining`, `w.days`, `w.prep` | `record.open` (upstream `CURRENT_STATUS`), `daysToEnd`, `daysToStart`, local planning rule |
| 2871 ×2 | `D.WINDOWS.filter` for `wins` | `AM.collections.cropWindows.records`, filtered on canonical `status` instead of the fabricated `bucket` |
| 2872 | `D.WINDOWS.map(w => w.crop)` | same collection; 10 canonical crops instead of 8 |
| 2873 ×2 | `D.WINDOWS.filter` for chip counts | same collection |
| 2874 | `D.WINDOW_KPI` | `WK` rebuilt from the four canonical statuses |
| 2875 | `WK.open/d30/d60/d90/d180/cycle` | four status buckets |
| 2876 ×2 | `D.WINDOWS.find(id) \|\| D.WINDOWS[0]` | `WROWS.find(w => w.id === s.windowId) \|\| null` — **the `|| [0]` fallback is gone** |
| 2878-2886 | `wd0.why`, `wd0.c.productObjs`, `wd0.ladder`, `wd0.signals`, `wd0.confirmed`, `wd0.category` | canonical fields + `record.verifiedProducts` / `record.regulatory` / `record.ui` |
| 2884 | `D.DEPT[...]` ×6 in `briefs` | two local hex constants — measured: `D.DEPT` held **one** colour pair (`#978B87` / `#C3BCBA`) for all six departments, so the read bought nothing |
| 2882 | `D.LADDER` via `wd0.ladder` | local `W_LADDER` constant, anchored on canonical `START_DATE` |
| 2887 | `D.WINDOWS.filter(w.early.state)` | `earlyWindows = []` |

I also consume the model's new projections rather than deriving them: `verifiedProducts`, `notFoundProducts`, `labelVerdictState`, `regulatory`, `coverageState`, `open`, `hasDates`, `sourceState`. I had derived all of these locally first (separator-folding `·` vs `/` by hand) and got **exactly the same 12 verified windows and 2 regulatory joins**, so I deleted my derivation and kept the model's.

---

## 2 · What the screen no longer shows

**CROP SCALE — gone (renders "non noto").** Every window claimed `HIGH` (26/29) or `MEDIUM` (3/29), derived from a hardcoded region whitelist and presented next to hectare figures credited to ISTAT. There is no area field in any real source.

**CONFIRMED WINDOW — was already dead code.** `confirmed` required `CROP_STAGE_CLASS` or `ISSUE_STAGE_CLASS` to be `OFFICIAL_OBSERVED_CURRENT` / `FIELD_REPORTED_CURRENT`; both are `NOT_OBSERVED` **29/29**. The old distribution was `EXPECTED WINDOW` 23 / `SEASONAL · UNCONFIRMED` 6. Now: `NORMA AGRONOMICA ATTESA` 24 / `DATA DA CONFERMARE` 5 — from `DATE_STATE`.

**EARLY MARKET SIGNAL — emptied.** Measured **9 of 29** windows read `FIELD REPORTED`, and every one was sourced from the 18 synthetic `FIELD_MESSAGES`. The fallback counted competitor communications on the crop and printed them as a market signal (rule 8). `wd.fieldMessages` is now `[]` on all 29. **This card has no `sc-if` guard — see markup edits.**

**PORTFOLIO READINESS — 8 rows → 4.** `Italy authorization: CONFIRMED · demo pack`, `Label window: CONFIRMED`, `Current crop timing: CURRENT/EXPECTED` and `Field signal: REPORTED/WAITING` were four fabricated regulatory and agronomic verdicts. What survives: the audited label verdict, plus three rows that now say `NON OSSERVABILE DA FONTI ESTERNE` instead of `NOT CONNECTED` (which implied a missing plug rather than a design boundary).

**PRODUCTS TO PREPARE — 27 windows → 12.** The old list came from the case fixture's `productObjs` and ranked its first entry `PRIMARY MATCH` with no verdict behind the word. Only `VERIFIED_LABEL_MATCH` products are shown now; **17 of 29** windows fall to the rule-10 empty state ("Portfolio check needed — no confirmed ADAMA label position"). `wd.c.matchCount` is 0 on 17, 1 on 10, 2 on 2.

**FUTURE RADAR SIGNALS — 17 windows → 0.** `D.SIGNALS` is the 56-record set the model fences as `DEMO_SCENARIO`. Real supply is 3 `futureSignals` for the whole country, whose `region` literally reads `"NAO SEI — o recorte cientifico e por afiliacao nacional..."` and whose every prose field is `NOT_APPROVED_FOR_DISPLAY`. There is no honest join. `noSignals` is true 29/29.

**AGRONOMIC CLOCK "ACT NOW" — gone.** Old `prep` distribution was `ACT NOW` **21**, `VALIDATE` 6, `PREPARE` 1, `TOO EARLY` 1 — because `days = Math.max(0, daysToOpen)` clamped all 16 closed and all 5 date-unknown windows to 0. Verified on the rendered payloads: **0 occurrences of `ACT NOW` / `AGIRE ORA`.**

**Buckets 6 → 4**, and the true picture is unflattering: `FINESTRA APERTA` 6 · `FINESTRA CHIUSA` **16** · `PROSSIMO CICLO` 2 · `DATA DA CONFERMARE` 5. (Old `WINDOW_KPI`: open 6, d30 **21**, d60 1, d90 0, d180 0, cycle 1.)

**`earlyWindows`, `windowCropChips`, `windowBuckets`, `WK`, `wins` render nothing.** Verified over markup lines 51-2374: `visibleWindows`, `windowCount`, `windowKpi`, `windowBuckets`, `windowCropChips`, `earlyWindows` have **zero bindings**. They are still declared (contract), now computing over canonical records instead of 9 `D.WINDOWS` + 2 `D.WINDOW_KPI` reads.

---

## 3 · What the screen gained

**A real regulatory act, on 2 of 29 windows.** IT-WIN-0001 (Veneto, `DDR n. 13645 2026-05-14`, *presente in archivio*, `IT-SRC-REGIONAL`) and IT-WIN-0008 (Piemonte, `Determinazione Dirigenziale n. 280 2026-03-16`, *fonte primaria letta*, `IT-SRC-PIEMONTE`). **A crop+region join alone reaches 3** — the third is IT-WIN-0020, Grapevine/Veneto **Downy Mildew**, which would have printed the Flavescenza decree on a fungicide window. The issue test is load-bearing. The other 27 windows get an explicit "nessuna fonte collegata" row, which is honest: `SOURCE_IDS` is empty 29/29.

**WHY PREPARE NOW: 6 confident rows → 5 sourced rows.** Every row is now an upstream value or a stated absence: `CURRENT_STATUS` + `STATUS_REASON`, `DATE_STATE` + `DATE_CONFIDENCE`, the label verdict (with `ABSENCE_RULE` attached when there is none), the observation class (`NON OSSERVATO`), and the regulatory act or its absence.

**MOA codes are labelled.** The card printed a bare `3` next to the word "registered"; it now reads `IRAC 3`, `FRAC 11/3`.

**Stale deep links no longer lie.** `openWindow('WIN-001')` used to silently render IT-WIN-0001; it now renders an empty `—` shell.

---

## 4 · Markup edits still required (I could not make them)

1. **Line 756 — delete `· CROP SCALE {{ wd.scale }}`.** Until then it reads "NORMA AGRONOMICA ATTESA · CROP SCALE non noto". This is the one place where I had to leave a subcomponent alive that should be omitted.
2. **Lines 767-773 — delete the entire EARLY MARKET SIGNAL card** (`grid-column:span 4` div, including the duplicate `PREPARATION RECOMMENDATION / EARLY MARKET SIGNAL` two-cell grid at 771). It has no `sc-if`, so it currently renders as a headed empty box. After deletion the row goes from 4+4+4 to two cards; if you want the grid to stay balanced, widen WHY to span 5 and READINESS to span 7 — no new component.
3. **Line 758** — `Known from label · {{ wd.c.matchCount }} registered matches` is hardcoded English and now reads "0 registered matches" on 17 of 29 windows. Suggest guarding it with `wd.noProducts` or moving the count into `wd.c.label`.
4. **Line 800** — the empty state says "window driven by the annual cycle **and the case record**". The case record is no longer a source for this window; drop the clause.
5. **Lines 803-806 (WHAT IS FACTUAL · EXPECTED · UNKNOWN)** — hardcoded strings that no longer hold. `Crop × region relevance` under FACTUAL rested on the hectare fixture; `Monitoring season start` under EXPECTED rested on `MONITORING_WINDOW`, which is `NOT_APPROVED_FOR_DISPLAY` **7/7**. Both should move or go.
6. **Line 759** — the caption "Business rule (demo configuration), not an agricultural fact" is correct and should stay, but it is hardcoded English in the Italian UI.

---

## 5 · Honest gaps, and where I diverged from the spec

- **`statusReason` renders in English inside the Italian UI** (why-row 1: *"Reference date 2026-09-02 falls after END_DATE"*). There are exactly 5 distinct strings. I did **not** invent Italian for them — mistranslating an audit's stated reason is worse than showing it in English. This needs 5 i18n keys. (I did move it off the AGRONOMIC CLOCK tile, which now carries `Validato 02 SET 2026` from `LAST_VALIDATED`, filled 29/29 — that removed the duplication.)
- **Spec said 11 windows resolve a verified product; the measured number is 12.** `IT-WIN-0016` (Wheat / *Cereal Aphids · BYDV Risk*) joins `MAVRIK EW` once the `·`↔`/` separator difference is folded. The model now does this fold itself. Nothing looser is folded: `Diabrotica` is **not** `Diabrotica Larvae`, so IT-WIN-0004 and IT-WIN-0018 stay empty.
- **The BUSINESS PREPARATION CLOCK is kept, reframed, not removed** — as the spec asked. The 90-day lead and 5 rungs are declared as a local planning constant (no fixture read) and anchored on canonical `START_DATE`. **5 windows with no start date get an empty ladder and a `—` clock.** I deliberately avoided `ACT NOW`, `WINDOW OPEN` and `NEXT CYCLE` (rule 7); for the 22 windows whose start has passed the label is `ANTICIPO SCADUTO` / `LEAD TIME ELAPSED`, which is a statement about the planning lead, not about the crop. Distribution: `ANTICIPO SCADUTO` 22 · `PREPARARE` 1 · `PIANIFICARE` 1 · `—` 5. **This still is not `AM.preparation` with `SINTONIA_INTERPRETATION` provenance** — that projection has not landed in the model; when it does, this block should read it instead of its local constant.
- **`observedStage` is null 29/29** and I render nothing for it, as the model intends. No placeholder.

---

## 6 · Blocking issue owned by another agent

`audit/blocks/competitor.js:290` reads `(e2.cropRelevance || []).filter(...)`, but `italy-app-model.js:1691` now returns `cropRelevance` as a **scalar** (`UNK(...)`) — the array is `cropRelevanceList` (line 1692). This throws on **every one of the 52 screen renders**, including mine, and it fails identically with my block removed. With `competitor.js` set aside, my block validates **52/52**.

==========================================================================================

Block written and validated. Here is the report.

**File:** `C:/eame-sintonia/italia-portale/audit/blocks/field.js` (170 lines, replaces portale.html 3095–3131)
**Validation:** `node /tmp/subset.mjs helpers nav windows signal market product portfolio voci brief field future` → **52/52 screen renders pass**. (`node audit/splice.mjs try field` currently reports 0/52 from *other* blocks — see "broken by colleagues" below; the last clean group run including my final text was 52/52.)
**Fixture scan of my block only:** 1 read, `TSR`, classified `EXPLICIT_DEMO`. Was 4 core reads + 1 forbidden global.

---

## Legacy fixture reads removed

| was | line | replaced by |
|---|---|---|
| `allMessages` (built at 2603 from `D.FIELD_MESSAGES`) | 3118, 3123–3126, 3131 | `demoMessages = s.extraMessages.concat(AM.collections.fieldMessages.records)` — built locally, so my block no longer depends on the nav block's `allMessages` surviving |
| `D.WINDOWS.find(x => x.crop === m.crop)` | 3103 | `APP0.cropWindows.records.find(...)`. Safe: all 8 demo crop names exist in the canonical set (18/18 messages resolve) |
| `window.ITALY_MARKET.CROPS.find(...)` — a forbidden global | 3108 | **deleted.** `marketObservations` is 76 commodity price rows keyed `BLTPAN\|PAN` / GROUP, not by crop name. There is no honest crop→market join, so the MARKET PULSE chip is gone |
| `D.FIELD_KPI` (`FK.connected`, `FK.newSignals`, `FK.validation`) | 3123–3124 | every tile counted off the pool the screen is showing |
| `D.CAT` (indirectly, via `CASES`→`decorate`→`c.category`) | 3131 | `o.ui` from the model (falls back to `AM.categoryOf`) |
| `CASES` = `D.CASES` (29 demo opportunities) | 3131 | `APP0.opportunities.records` (3 real) |

## Reads kept, with a marker

```js
const tsrs = /*@EXPLICIT_DEMO Field Sales cast, default-off module, feeds no real count*/ D.TSR.map(...)
```
The 7 technical sales reps are the demonstration's cast and the mission assigns them here. They are not in the model, they carry `provenance: SYNTHETIC_DEMO`, initial `D`, org `… · DEMO`, no phone number, no outbound action. Verified: the scanner classifies this read `EXPLICIT_DEMO`, not `DATA_BEARING_CORE`.

## What changes on screen (all measured)

| component | before | after |
|---|---|---|
| KPI "Connected to opportunities" | **8** | **3** — 9 of 18 messages carry a `caseId`, but only `IT-OPP-001/002/003` exist in the model; `IT-OPP-004/006/007/009/021` are demo-only. Tile relabelled "Collegati a un'opportunità reale" |
| KPI "Products mentioned" | 7 (any string) | 7 (only names that resolve in `AM.findProduct`; 10/10 do today, so the number is unchanged but the definition is now enforced) |
| state filter chips | 4 chips summing to 15 of 18 | 5 chips summing to 18 — the pool holds a fourth state, `CLASSIFIED` (3 records), that the hard-coded `fStates` array never exposed. **3 of 18 messages were unreachable by any filter.** Derived from the pool now |
| "WHERE THIS SIGNAL WENT" chips | up to 5 per card; 10 of 18 cards hit the `slice(0,5)` cap. Labels seen: OPPORTUNITY, CROP WINDOWS, PRODUCT, MARKET PULSE, SOURCES, FUTURE RADAR, COMPETITOR WATCH | max 3 (sizes 3/2/1). **FUTURE RADAR, MARKET PULSE and SOURCES are gone.** 0 of 18 messages resolve to a real future signal — the three real ones are Fusarium/mycotoxin on maize, Fusarium/DON on wheat, and one regulatory record; there is no Diabrotica and no Septoria. MARKET PULSE had no real join. SOURCES pointed at the demo TSR people sitting on the core Fonti screen |
| card footer `targetLabel` | `Opportunity · Flavescenza Dorata · Veneto` for demo cases, `Future Radar · issue · region` otherwise | the opportunity id when it resolves, else the canonical crop window, else `DA VALIDARE`. It never names a destination that does not exist |
| "FIELD SIGNALS ADDED TO OPPORTUNITIES" panel | **8 rows**, 40 evidence chips (5 per row: field/science/official/people/market) | **3 rows, 0 evidence chips.** The 5 vanished rows are demo opportunities. The chips are empty because `evidence` is `undefined` on 3/3 real opportunity records — the tally only ever existed on the demo fixture, and one of its five buckets was literally `field`. The count now renders `1 · DEMO` so it cannot be read as part of that opportunity's evidence |
| row labels in that panel | `il(o.issue)` / `cl(o.crop)` | canonical `issueKey` / `cropKeys` / `regionKeys`. The `title`, `issue` and `crop` fields are the analyst's **Portuguese** working text on 3/3 real opportunities ("Videira x Flavescência dourada, via o vetor Scaphoideus titanus"). Where a canonical key is missing (IT-OPP-003 has `issueKey: null`, empty crops) the row falls back to the record id and `non noto` — never to the Portuguese |
| inbound flow strip | 5 hard-coded English steps: FIELD SALES / RTV · MESSAGE IN · SINTONIA CLASSIFIES · BECOMES A SOURCE · ROUTED | the mission's contract, localized: **MESSAGGIO IN ARRIVO → RICEVUTO → CLASSIFICATO → COLLEGATO → DA VALIDARE**. Sub-lines now state the containment ("Sintonia riceve. Non invia messaggi da questo modulo.", "solo a finestre, prodotti e aziende che esistono davvero", "nessun messaggio diventa evidenza senza validazione") |
| TSR rows | all 7 opened the **core Person screen**; two were labelled `Marco R.` / `Luca F.` | `go` is a no-op, `hasProfile: false`. Names that read like employees are stamped `· DEMO`. Message counts now include composer additions; `2h ago` now reads `2h fa` in Italian (`LAGO` covers today/Nd/Nmo/N min but not hours) |
| composer "ISSUE" and "CROP" boxes | **blank** — the markup binds `parsed.issueL` / `parsed.cropL`, and `parseField` has never returned them | filled (`Mosca dell'olivo` / `Olivo`). `parsed.state`, `.issue`, `.caseObj`, `.signal`, `.color`, `.competitors` are untouched because `sendComposer` branches on the raw enums; `stateL` / `signalL` are added alongside |
| composer example texts, card enums and caveats | English on an Italian-default screen | Italian when `lang === 'it'`. The three Italian examples were tested against `parseField` and score ≥ 4, so they still resolve. Localized: 8 `mtype`, 5 `channel`, 8 `signal`, 1 `proves`, the 4 `validation` caveats. **Not localized: the 17 `timing` phrases** (stage vocabulary) |

## Inertness

Snapshot of `provenanceSummary`, `counts`, opportunity record shape, crop-window count and field-message count **before and after** 3 × `simulateInbound()` + 1 × `sendComposer()`: **unchanged**. Every chip filter renders in both languages.

## Markup edits still required (I cannot apply them)

1. **portale.html:913** — `WHERE THIS SIGNAL WENT` is a false claim. Nothing routed anywhere; nothing mutates. Change the heading to an i18n key meaning *CONTESTO CORRELATO · il messaggio non è stato instradato* / *RELATED CONTEXT — this message was not routed*, and wrap lines 911–916 in `<sc-if value="{{ m.hasRelated }}">` (the prop is already exported).
2. **portale.html:921** — remove the `IN SOURCES → PEOPLE` link (`goTsr`, owned by the search block). TSRs are demo people; that link puts them on a core screen next to real ORCID researchers.
3. **portale.html:922** — drop `cursor:pointer` on the TSR row, or guard with `{{ t.hasProfile }}`. `t.go` is now a no-op.
4. **portale.html:869 / 867** — bind `{{ parsed.stateL }}` and `{{ parsed.signalL }}` instead of `{{ parsed.state }}` / `{{ parsed.signal }}`.
5. **italy-i18n.js `lblFieldSignalsAdded`** — "SEGNALI DI CAMPO AGGIUNTI ALLE OPPORTUNITÀ" asserts an addition that does not happen. Should read something like "OPPORTUNITÀ REALI CITATE DAI MESSAGGI DIMOSTRATIVI".
6. Hardcoded English I cannot reach from the block: **817** (intro paragraph), **855** (`WHATSAPP · FIELD MESSAGE (SIMULATED)` — the `(SIMULATED)` marker must survive translation), **871**, **878** `ORIGINAL FIELD MESSAGE`, **884** `SINTONIA CLASSIFICATION`, `HEARD FROM`, `Safe reading`, `Timing context`, `Proves`, **930** `VIEW INTELLIGENCE →`.

## For other agents

- **calendar block (2635–2866)** — `portale.html:2773` in the spliced file still has `const fms = c.kase ? D.FIELD_MESSAGES.filter(...)`, feeding the Crop Windows "WHY PREPARE NOW?" row. Unmarked core read; the spec says delete it.
- **search block (3376–3459)** — lines 3401 (`simulateInbound`) and 3406 (`sendComposer`) still read `D.FIELD_MESSAGES` and `D.TSR` with no marker: 3 `DATA_BEARING_CORE` reads. They need `/*@EXPLICIT_DEMO …*/`. Worse, `sendComposer` ends with `category: c ? c.category : D.CAT.pest` — an unclassified composer message is stamped **Pest Control**. That is a demo fixture supplying a pest/disease classification; it should be `AM.CATEGORY_UI.unknown`.
- **head block (2532)** and **helpers `decorate()`** (`hasField: c.fieldCount > 0`) still touch the field fixture; both are on the spec's list.
- **Name collision that will break `assemble`:** `const nar` is declared in both `audit/blocks/signal.js:14` and `audit/blocks/competitor.js:21` at the same scope → `Identifier 'nar' has already been declared`.
- **Currently breaking every screen:** `(e2.cropRelevance || []).filter is not a function` from the head/calendar work in progress. Not mine.
- **Model gap for the helpers agent:** `AM.categoryOf` does not recognise `FITOPLASMA` (IT-OPP-001's `issueType`), so a phytoplasma opportunity renders as the unknown token with no icon. The matcher tests for `PHYTOPLASMA` but not the Italian/Portuguese spelling. I did **not** add my own classifier — §2 forbids me inventing a classification.

## Contract

All eight meaningful names on the MUST STILL DEFINE line are still declared: `composerExamples`, `fieldCases`, `fieldKpis`, `fieldMessages`, `fieldStateChips`, `inboundFlow`, `parsed`, `tsrs`. `mk`, `out` and `w` on that line were block-scoped `const`s **inside** the `wentFor` arrow function — never readable by a later block. `mk` and `out` no longer exist (the market chip and the accumulator were rewritten); `w` survives as a local in `relatedFor`.

## What the spec asked for that the data cannot support

- Plan item 10 says to keep the demo pool alive for "the `navIntegrations` count (2606) and the `dataState` demo row (2532)". Both are outside my range and both still read `D.FIELD_MESSAGES` directly; my block no longer feeds them.
- The spec treats "Connected to opportunities" as a survivable demo number. It is not, at 8: five of the eight opportunities it counts do not exist. I cut it to 3 and say why in the code comment.
- Nothing real can replace the removed FUTURE RADAR / MARKET PULSE / SOURCES chips. The Field Sales screen is now visibly thinner: fewer chips per card, five fewer opportunity rows, no evidence chips at all on the rows that remain. That is the honest state of a demo module that touches nothing.

==========================================================================================

`audit/blocks/brief.js` is written and validating: **`node audit/splice.mjs try brief` → 52/52 screen renders pass** (all currently landed blocks: helpers, head, nav, case, calendar, windows, signal, market, product, portfolio, voci, brief, field, future, competitor, science).

# BRIEF · report

## 1 · The measured failure, and what actually caused it

`portale.html:3082-3094` resolved its case as `CASES.find(c => c.id === s.caseId) || CASES[1]` over `D.CASES` — the 29-record demo fixture. Two separate defects:

- **the throw**: `others: … window.ITALY_BRIEFS.build(a.dept, cs0).doc` dereferenced `.doc` on a `build()` that returns `null` for any department key the generator does not own. Both `it` and `en` *Action brief* screens were dead.
- **the silent one, worse**: `|| CASES[1]` meant a real opportunity id with no demo twin printed **a different case's document**, under the requested id's breadcrumb.

Both are gone. The case is resolved **by id only**, from `AM.collections.opportunities`, with no neighbour fallback. An unresolved id or an unknown department leaves `br = null`; `portale.html:3404` already reads `isBrief: s.view === 'brief' && !!br`, so the screen hides instead of throwing. Verified: `caseId:'NOPE'` → `isBrief false`, no throw; `briefDept:'BOGUS'` → `isBrief false`, no throw.

## 2 · The trap I found and blocked — 1 brief in 3 was about to carry another case's agronomy

`italy-briefs.js` (the other agent's, now landed) resolves the canonical window with `cropWindows.legacyCaseId === c.id`. Those `legacyCaseId`s are the **legacy 29-case numbering** `IT-OPP-001..029`. The three real upstream opportunities **reuse that same id space**. Id equality is therefore a coincidence, not a relation. Measured:

| id | window found | window crop / region | opportunity `cropKeys` / `regionKeys` | verdict |
|---|---|---|---|---|
| IT-OPP-001 | IT-WIN-0001 | Grapevine / Veneto | `["Grapevine"]` / `["Lombardia","Veneto"]` | **agrees** |
| IT-OPP-002 | IT-WIN-0002 | Maize / Friuli-Venezia Giulia | `["Maize"]` / `["Friuli-Venezia Giulia"]` | **agrees** |
| IT-OPP-003 | IT-WIN-0029 | Durum Wheat / Toscana | `[]` / `[]` | **FALSE** |

Real `IT-OPP-003` is the national ADAMA authorisation-expiry calendar. Unguarded, its brief printed *"Fusarium Head Blight · Durum Wheat · Toscana"*, `NEXT_CYCLE`, and the 2027-05-01 → 2027-05-25 dates of a wheat case. `winFor()` now requires the window's crop to be in `o.cropKeys` **and** its region in `o.regionKeys` (the model's own declared synonym tables). Unverified, the id does not travel and the document says `WINDOW NOT ESTABLISHED`.

## 3 · Legacy fixture reads removed

| was | now |
|---|---|
| `3086 D.DEPT[s.briefDept].color` — unmarked, counted DATA_BEARING_CORE | one marked read, `/*@VISUAL_ONLY …*/ D.DEPT` (scanner confirms `klass: VISUAL_ONLY`) |
| `3085/3087/3092 cs0` — the whole document was built from a `D.CASES` record: `happening, why, know, watch, stage, signal, label, ws/we, windowLine, evidence{field,official,science,people,market}, adjacent, competitors[], fieldMessages[], origin, updatedLabel, latin, source, status` | **all gone.** The generator receives 8 keys, all facts or explicit absence |
| `3087 cs0.st.color` (demo status colour) → priority pill | `b.accentColor` = the canonical window's own `ui.color` |
| `3092 cs0.actions` (4 rows of fabricated what/why/when per case) | `window.ITALY_BRIEFS.departments` — 5 rows, the template catalogue |
| `3092 build(a.dept, cs0).doc` | `build(dp, b.case)` with the null row skipped |

**Reads KEPT, with marker and justification** — exactly two, both non-factual:
- `/*@VISUAL_ONLY department accent and soft ink only; the department list itself comes from ITALY_BRIEFS.departments and no fact is read from this table*/ D.DEPT` — section-header accent and the sidebar row ink. The list of departments is not read from it.
- `/*@EXPLICIT_DEMO the 29 legacy presentation cases, provenance DEMO_SCENARIO, reachable only behind the Future Radar scenario switch and never counted as opportunities*/ APP0.opportunityScenarios.records` — gated on `s.showScenarios` (default `false`). Not a `D.*` read; marked anyway so the intent is reviewable.

## 4 · What the screen no longer shows — be blunt

Measured over `AM.collections.opportunities.records` (n = 3, `real: 3`, `demo: 0`):

- **All ten narrative fields are `NOT_APPROVED_FOR_DISPLAY` on 3/3** (`whatIsHappening, whyItMatters, currentEvidence, marketContext, competitorContext, scienceContext, fieldVoices, whatWeKnow, whatWeDoNotKnow, interpretations`). So *what is happening*, *why it matters now*, *what we know* and *what still needs validation* carry **no prose at all**. The generator prints its own honest `NON NOTO` line in their place.
- **`status` null 3/3, `canonicalWindow` null 3/3, `windowId` null 3/3.** The priority pill reads `WINDOW_CLOSED` / `NEXT_CYCLE` only where my join guard passed; on IT-OPP-003 it reads `NOT_ESTABLISHED`.
- **Field Sales signals: 18 → 0.** No ingested field-message collection exists anywhere; all 18 are `SYNTHETIC_DEMO`. Every real brief now says so.
- **Competitor rows: 5 fabricated rows per case → 0.** The 503-item corpus is real but the model does not attribute it to a case; the brief prints the corpus size and states that per-case attribution is not established.
- **Evidence counters** (`field/official/science/people/market`, previously invented integers scaled to `v * 14` bars) → gone from the brief entirely.
- **`IT-OPP-003`'s document title is three repeated `NON NOTO — not established in the Sintonia model`.** Ugly, and correct: it has no crop (upstream deliberately left it out of `OPP_CROP`), no issue key, no region key and no defensible window. I did **not** paper over it.

**What got better, measured:** on IT-OPP-001 the six declared TAU-FLUVALINATE products now resolve through the model's synonym table to **2 `VERIFIED_LABEL_MATCH` (MAVRIK SMART, EVURE PRO) and 4 `LABEL_CHECK_NEEDED`** — corroborated independently by `IT-WIN-0001.verifiedProducts = ["EVURE PRO","MAVRIK SMART"]`. I reorder `products` by `strengthRank` so the verified two lead (order is presentation; grades and names are not restated). Per §10 no product is hidden, and since the model ranks none above another, **no "primary portfolio match" is asserted** — `primary: null`.

Whole-package check across **36 generated documents** (3 cases × 6 departments × 2 languages): **0** occurrences of `null` / `undefined` / `[object Object]`, **0** demo strings (`WhatsApp`, `Demo profile`, `Field Sales Rep · demo`), **0** Portuguese narrative leaks. The only "Flavesc" hits are the Italian `Flavescenza Dorata` from the canonical window, never the upstream's `Flavescência dourada`.

## 5 · One clock, and the outbound-request count

`italy-briefs.js` now contains **0** `new Date(` and stamps `b.generated` from `AM.referenceDate` = `2026-09-02`. My earlier override is removed — there is one clock and it is the model's.

Outbound: `grep -noE "tel:|\+39[ 0-9]{6,}|whatsapp\.me|wa\.me"` over `client/*.js client/*.html` → **0 hits**. The brief has no send action. The `Share` button remains a `mailto:` that opens the user's own mail client pre-filled and sends nothing.

## 6 · Safety net, and what it costs

A small guard drops any produced line that interpolated a value we do not have (`null` / `undefined` / `NaN` / `[object Object]`) and drops a section left with nothing. **Measured today it removes 0 lines of 481 and 0 sections of 180** — it is a regression guard, not a live edit. When it does fire, `b.summary` is re-derived from the kept sections, reusing the generator's own header line verbatim so Copy / Share / PDF cannot drift from the screen.

## 7 · Markup

**No markup change is required.** `isBrief: s.view === 'brief' && !!br` and `br: br || {}` at line 3404 already give exactly the hide-don't-throw contract I needed, and every `{{ br.* }}` binding in markup 496-528 (`dept, doc, generated, title, role, priColor, priority, pages, purpose, sections[].hUpper/lines/bullets, accent, showLoop, download, copyLabel, copy, share, others[]`) is still supplied.

## 8 · For the owners of other files — things I could not fix from here

1. **`client/italy-app-model.js` · the opportunity↔window join never fires.** The adapter does `windowByLegacyCase[U(o.LEGACY_CASE_ID)]`, but the three opportunities' `LEGACY_CASE_ID` is `IT-HERO-001..003` while canonical windows carry `legacyCaseId = IT-OPP-0NN`. Result: `canonicalWindow`, `windowId` and `status` are **null on 3/3**, and `relationships` never emits a `RELATED_CROP_WINDOW` row for any opportunity (that push is guarded by `o.canonicalWindow`). If you fix it, use `cropKeys`/`regionKeys` agreement, not id equality — id equality is right on 2 of 3 and false on 1.
2. **`client/italy-app-model.js` · `windowText` is the literal string `"[object Object]"` on 3/3.** `S(o.WINDOW)` stringifies an object. The three enums are already exposed correctly as `windowApplication / windowMonitoring / windowNextCycle`; `windowText` should be dropped or composed.
3. **`client/italy-briefs.js` · `F()` should fall back to `c.crop` / `c.issue` / `c.region` when `win(c)` returns null**, instead of building a title from three `UNK`. I already pass those three on the routed record — canonical keys only (`cropKeys[0]`, `issueKey`, `regionKeys.join(' · ')`), never the raw Portuguese columns. They are `null` on IT-OPP-003, so even with the fallback that one stays honestly unknown.
4. **`client/italy-briefs.js` · consider replacing the single `Primary portfolio match` meta slot** with the label-audit grades: on IT-OPP-001 two products are `VERIFIED_LABEL_MATCH` and nothing ranks one above the other, so the slot is currently always empty on real cases.
5. **`client/italy-briefs.js` · the whole document is English in both languages.** `s.lang` never reaches it. Rule 11 says Italian is default; that is a real gap in that file, not in this block.
6. **i18n debt.** `SINTONIA_I18N.it.CROPS['Videira']` is `undefined` (`['Grapevine']` is `'Vite'`). Any screen that renders a real opportunity's raw `crop` / `issue` / `region` will print the analyst's Portuguese. I route around it here by using the model's canonical keys — other blocks should too.
7. **Not mine, seen in passing while validating:** the untouched `search` block at `portale.html:3378`-era does `CASES.filter(c => … c.products.join(' '))` and the rewritten `head` block's `CASES` records no longer carry `products` — that throws on *Global search*, and because the harness reuses one component instance the leftover `committedQuery` then made *Action brief* fail too. With the *Global search* screen excluded, all other screens were green throughout. Two colleagues also briefly collided on a renderVals-scope `const nar` (`signal.js` and `competitor.js`) and on `e2.cropRelevance`; both cleared before my final run.

Files: `C:\eame-sintonia\italia-portale\audit\blocks\brief.js` (the block), scratch build at `C:\eame-sintonia\italia-portale\audit\.scratch\portale.brief.html`.

==========================================================================================

Block written, validated, and passing.

**File:** `C:/eame-sintonia/italia-portale/audit/blocks/market.js` (replaces `client/portale.html` lines 2908–2996)
**Validation:** `node audit/splice.mjs try market` → **52/52 screen renders pass** (it + en), spliced with helpers, head, nav, case, calendar, windows, signal, market, product, portfolio, voci, brief, field, future, competitor, science.

---

## 1. Legacy fixture reads removed

**All 6 `window.ITALY_DEMO` reads in this block are gone (6 → 0).** Verified with `scan.mjs` on the block range before, and `grep -c '\bD\s*\.'` = 0 on the new file.

| old line | symbol | replaced by |
|---|---|---|
| 2945 | `D.WINDOWS.filter(w => w.crop === mc.crop)` (RELATED CROP WINDOWS) | `AM.collections.cropWindows.records` filtered on `crop`, sorted by canonical status |
| 2946 | `D.CASES.filter(c => c.crop === mc.crop)` (caseCount) | `AM.collections.opportunities.records` filtered on the model's `cropKeys` |
| 2947 ×2 | `D.PRODUCTS[n].targets` (portfolio chips) | `AM.collections.portfolioLinksByCrop` (`products`, `productCount`) |
| 2948 | `D.F_COLOR[x.status]` (mSignals colours) | deleted — subcomponent removed |
| 2949 | `D.WINDOWS…sort()` (nextW / adamaStance ladder) | same canonical collection, canonical `CURRENT_STATUS` |

**`window.ITALY_MARKET` went from supplying the entire screen to supplying nothing but the tab strip.** The other agent had already stripped the file; what remained and I still refused to read: `MK.GAPS` and `MK.COVERAGE` (measured coverage prose — facts, so regenerated in-block), `MK.CP_MARKET` / `MK.FEASIBILITY` (the feasibility table still named ISMEA, BMTI, JRC MARS, ICQRF, Agrofarma as routes — none registered; rebuilt in-block), `MK.SEM` / `MK.TONE_SEM` / `MK.FRESH_COLOR` / `MK.ICON` (a market-effect palette labelled POSITIVE/NEGATIVE/WATCH — replaced by two local coverage tokens so no verdict can leak back in), `MK.NOT_OBSERVABLE` (already in i18n as `t.cannotProveList`).

## 2. The one read I kept, with a marker

```js
const MK = /*@VISUAL_ONLY crop tab strip identity only — key, label, Italian label, colour. No number, date, unit, state, source or verdict on this screen is read from the fixture.*/ window.ITALY_MARKET;
```
Only `MK.CROPS[].{key,label,it,color,crop}` is touched, and only to build `mpButtons` / `mpCropOptions`. `crop` is the join key to `cropWindows` and `marketByCrop`; every number attached to a tab comes from the model. No `@EXPLICIT_DEMO` reads at all.

## 3. What the model supplied (it landed mid-task — I re-read it and rewrote against it)

The model agent shipped `marketObservations` with `cropKey / periodStart / periodEnd / isCurrentSeries / stoppedYear / hasStage / hasPublicationDate`, plus `marketByCrop` (14 rows), `portfolioLinksByCrop` (14 rows) and `marketSummaries` (5 rows). I consume all four. **Nothing is derived in the view that the model already derives.** Two things I still derive locally and declare: the reference-quote pick (dominant product definition × latest live `periodEnd`), and the chart grouping.

**One spec correction:** the spec (and my first measurement) said `IT-MKT-077` — the only Grapevine row — was rejected for having no `PRODUCT`, giving **76** accepted rows and Grapevine 0. The model now accepts it: **77 rows**, Grapevine 1, and a third unit `Euro / HL.` re-enters the set. That row is a series stopped in 2025, so Grapevine renders 1 observation, 0 current, no price card, no chart, and a stopped-series badge.

## 4. Measured numbers that change on screen

| | before (fixture) | after (measured) |
|---|---|---|
| hero 40px value | a verdict: PRESSURED / BALANCED / MIXED SIGNALS | the ingested row count: Olive 36, Wheat 13, Maize 11, Durum 8, Barley 8, Grapevine 1, Tomato/Sugar Beet/Apple **0** |
| tab badge | ↑ ↔ ↓ ↕ arrows | the same row count per tab |
| price chart | 23 values, 20 of which exist nowhere in the real data | per-piazza bars in ONE definition + ONE unit: Wheat 12, Maize 10, Barley 7, Durum 6, Olive 8; **no card** for Grapevine, Tomato, Sugar Beet, Apple |
| piazza table | fixture rows | every ingested row: Olive 36, Wheat 13, Maize 11, Durum 8, Barley 8, Grapevine 1 — 12 of 77 badged "serie ferma dal YYYY · l'ultima quotazione non è un prezzo attuale" |
| portfolio count | Maize 11, Grapevine 8, Wheat 6, Olive 3, Tomato 1, Sugar Beet 5, Apple 1, Durum 9 | Maize **3**, Grapevine **1**, Wheat **5**, Olive **4**, Tomato **7**, Sugar Beet **3**, Apple **2**, Durum **3**, Barley **5** |
| "COMMERCIAL PREPARATION" | a days-threshold ladder (ACT / ACTIVATE / PREPARE / PLAN) | canonical `CURRENT_STATUS` only: FINESTRA APERTA / PROSSIMO CICLO / FINESTRA CHIUSA / DATA DA CONFERMARE / NESSUNA FINESTRA MAPPATA |
| opportunities button | demo case count | 1 (Grapevine), 1 (Maize), **0 everywhere else** |
| source map | 10 rows (ISMEA, CUN, BMTI, ICQRF, JRC MARS, Agrofarma…) | **1 row**: IT-SRC-AGRIFOOD |
| feasibility audit | 18 routes crediting unregistered sources | 11 rows, 1 YES + 1 PARTIAL + 9 NO, sources `—` where nothing is connected |
| tabs | 8 | **9** — Barley added (8 real current observations, `marketViewKey: null`, otherwise invisible) |

## 5. Components emptied, and the measured reason

`forces` (`hasForces:false`) and `spark` (`hasSpark:false`) disappear cleanly through existing `sc-if` guards. `csMarket = null` switches off the market-context strip on the opportunity-case screen through `hasCsMarket`. Everything else below has **no guard** — the props are honest but the frame survives until the markup is cut:

- **production / yield / stocks** — no production, area, yield or stock record exists anywhere in the ingest.
- **supply & trade** — imports and exports were already 0% bars on every crop.
- **farmer sentiment** — ISMEA is not among the 31 registered sources; the −1.4 index had no record.
- **input cost pressure** — this was the dangerous one: the Baltic Dry card printed `2,843` with a date and `state:'OBSERVED'`, indistinguishable from a real observation. `inputs: []`.
- **market trajectory** and **outlook 3–6 months** — no forward-looking source is ingested at all.
- **what changed / commentary** — no ingested change log; the commentary was an explicit "Sintonia reading" of sources never ingested.
- **Italy economic context** — ISTAT is registered but contributes 0 of the 77 rows.
- **industry metrics** (`cpm.metrics: []`) — 9 Agrofarma figures, no source, no record.
- **mSignals** — already dead: real `futureSignals` crops read `MAIS` / `TRANSVERSAL` against tab crops `Maize` / `Durum Wheat`, and `status` is null on all 3.
- **`MK.INTERNAL`** — SELL-IN, SELL-OUT, CRM/PIPELINE, ORDERS, DISTRIBUTOR INVENTORY. Already gone from the fixture; **not re-exported** on `cpMarketObj` (`'internal' in cpm === false`).

Fixed in passing: the live bug at markup 1224 — the builder emitted `issue`, the markup reads `w.issueL`, so the window label was blank. `mWins` now emits `issueL` through `il()`.

## 6. Markup edits I could not make — please apply

I own no markup. These are the exact lines where a dead frame or a now-false caption survives.

| line | edit | why |
|---|---|---|
| **971** | delete the pill `◇ SINTONIA INTERPRETATION · NOT AN OBSERVED FACT` | the 40px hero value is now a measured count of ingested rows; calling it an interpretation is wrong (it under-claims, so it is safe to ship, but it is wrong) |
| **976** | relabel `WHY SINTONIA READS IT THIS WAY` → `COSA ABBIAMO OSSERVATO` / `WHAT WE ACTUALLY OBSERVED` | the six tiles are now pure coverage counts (observations, piazze, product definitions, units, stopped series, rows without STAGE), not reasoning toward a verdict. **Be blunt: this is the one place I repurposed a component rather than emptying it**, because `mp.drivers: []` would leave a titled card with nothing inside and rule 3 offers no third option without a markup cut. If you prefer the strict reading, set `drivers: []` and delete lines 973–996 instead. |
| **991–995** | delete the legend row (`MARKET EFFECT`, `◇ interpretation · ○ forecast · — no data`, `colour follows market effect…`) | `mp.semLegend` is `[]`; there is no market-effect colour code left to explain |
| **1042–1058** | delete the PRODUCTION · YIELD · STOCKS card | |
| **1060–1077** | delete the SUPPLY & TRADE card | |
| **1079–1095** | delete the FARMER SENTIMENT card (header hardcodes `SECTOR LEVEL ONLY`) | |
| **1097–1110** | delete the INPUT COST PRESSURE card (header hardcodes `PARTIAL COVERAGE`, now false) | |
| **1114–1126** | delete the MARKET TRAJECTORY strip | |
| **1128–1146** | delete the MARKET OUTLOOK · NEXT 3–6 MONTHS section | |
| **1210** | delete the green `MARKET ENVIRONMENT` tile | it renders `{{ mp.temp }}` + `{{ mp.sem.label }} FOR THE GROWER`, which now reads "36 · OSSERVAZIONI INGERITE FOR THE GROWER". Nonsense in any wording I can supply from props. |
| **1241** | relabel the button away from `{{ t.lblOpportunities }}` | the upstream record's own `forbiddenLabel` reads: do not call these an opportunity. Its `caseLabel` is `CONVERGENCIA QUE MERECE INVESTIGACAO`. I kept the honest count (1 / 1 / 0…) rather than zeroing it, but the word must change. |
| **1246–1263** | delete the WHAT CHANGED card and the commentary block under it | |
| **1270–1273** | delete the ITALY ECONOMIC CONTEXT list | |
| **1288–1300** | delete the `cpm.metrics` 3-column grid (keep intro + READ WITH CARE) | |
| **3402** | `mpReview: MK ? MK.LAST_REVIEW : ''` → `mpReview: AM ? AM.referenceDate : ''` | **This one ships broken today.** `MK.LAST_REVIEW` no longer exists in the stripped fixture, so line 1279 currently renders "Last source review **undefined**." It was also a second clock, which rule 6 forbids. Line 3402 belongs to the `search` block (3376–3459), which is not yet written — please route it to that owner or apply directly. |

## 7. What the spec asked for that the data cannot support

- **A sparkline.** Dead, permanently. It needs 3+ points in one series; the ingest holds exactly one row per piazza per product. `hasSpark:false` on every crop, and no view change can fix it — it needs a new ingestion.
- **`price.geo`.** `GEOGRAPHY` is the identical analyst string `"IT — praca nomeada"` on all 77 rows, and it is Portuguese. The `BARI (PUGLIA)` / `ITALY` line has no real equivalent; I print the piazza name instead.
- **Clickable label URLs on the portfolio chips.** `portfolioLinksByCrop` carries `labels[product] → labelUrl`, but markup 1231 renders a plain chip with `p.name` and an `onClick` that opens the product screen. Not worth a markup change; noted.
- **Dropping the empty tabs.** Tomato, Sugar Beet and Apple stay in the strip with a `0` badge and a hero that says "Nessuna osservazione di prezzo ingerita per questa coltura". Hiding them entirely would need a markup/nav decision, and they still carry real crop windows (Sugar Beet has 2 open ones) and real portfolio links (Tomato 7 products), so an empty *market* tab is not an empty *crop*.

## 8. Things I found that belong to other owners

- **Portuguese in the data.** `seriesWarning` (`"esta praca parou de cotar…"`), `geography`, and `sources[].frequency` (`semanal`, `anual`, `anual/mensal`) are Portuguese values that would render raw. I never print the first two and I map the third; **other screens reading `sources[].frequency` will leak Portuguese to the Italian client.**
- **`WHEAT_GENERIC` double-count.** 9 label rows are counted for both Wheat and Durum Wheat. The model declares it on `sharedGenericRows`; I publish it in the gaps list rather than hiding it.
- **A gap worth reading.** For every crop, the number of products with an *authorised-use row read* is far below the number of registrations that *name the crop*: Olive 4 vs 12, Grapevine 1 vs 61, Maize 3 vs 36, Tomato 7 vs 57. That difference is what has not yet been read row by row, and it is now printed as a gap instead of smoothed away.
- **Cross-screen temperature bleed.** `mkCropTemp` (2574 → markup 679), `mkTemp` (2653 → 732, 2762), `compMoments` market (3169 → 1693) and `mkTempFor` (3191/3204/3226 → 2132) all still expect `MK.CROPS[].temp`, which no longer exists in the fixture. Those are the calendar, competitor and science owners' blocks, not mine.

==========================================================================================

Block written and validated: **52/52 screen renders pass** (IT + EN, 26 screens), plus a hand-run sweep of all 29 windows × 2 languages × drawer/season/detail/scroll states — 0 failures.

File: `C:\eame-sintonia\italia-portale\audit\blocks\calendar.js` (452 lines, replacing portale.html 2635–2866).

---

## 1 · Legacy fixture reads removed

The block went from **22 data-bearing `D.*` reads to 0**. Measured with `audit/lib/scan.mjs` over `client/portale.html` lines 2635–2866 (before) and over the spliced scratch range (after). The only surviving `D.*` uses are `D.fmt` and `D.inkOn`, which the scanner classifies as helpers.

| line | symbol (×n) | replaced by |
|---|---|---|
| 2671, 2686–2699, 2708, 2717, 2812, 2836 | `D.CROP_CAL` ×8 | `AM.collections.windowCalendarRows.records` — 29 rows |
| 2664–2669, 2740, 2767, 2826, 2861 | `D.CASES` ×6 | nothing. Product links now come from `row.verifiedProducts`; the case→window link is deleted (see §5) |
| 2666 | `D.OBSERVED` ×1 | nothing. `observedStage` is null 29/29 |
| 2667 | `D.SOURCES` ×1 | `row.regulatory.sourceId` (2/29) else "nessuna fonte collegata" |
| 2646 | `D.PREP_LEAD` ×1 | `AM.preparation.leadDays` |
| 2652, 2703, 2861 | `D.DEPT` ×2 | `AM.preparation.departments[].color` |
| 2740 | `D.FIELD_MESSAGES` ×1 | nothing. `fieldCount` is a hard 0 |
| 2827 | `D.CAT` ×1 | `row.ui` (from `AM.categoryOf(ISSUE_TYPE)`) |
| 2687 | `D.WINDOWS` ×1 | nothing (the `windows` block owns that record) |
| 2647, 2688 | `window.ITALY_MARKET` ×2 (via `mkTemp`) | nothing. `calMarket = null` |

**Zero `@VISUAL_ONLY` / `@EXPLICIT_DEMO` markers were needed** — the block keeps no fixture read at all. Note for the scanner: I had to phrase `CROP_CAL` and `PREP_LEAD` without the `D.` prefix in the comments, because `scanFile` regexes raw lines and would have counted the prose as two core reads.

Also removed: the fallback `new Date('2026-09-02T00:00:00')` clock. `CAL_TODAY = AM ? AM.REF : null` and every consumer guards, so there is no second clock at all now.

---

## 2 · What the screen no longer shows (blunt list)

- **Hectares and crop scale.** `~350k ha · HIGH` is gone from the row, the season card and the drawer. There is no area field anywhere real; `windowCalendarRows.areaState` is `NOT_EXTERNALLY_OBSERVABLE` 29/29. `r.ha` and `r.scale` are `null`.
- **The crop-cycle band** (Sowing → Harvest) and the **weed band**. No upstream source: `cropStage` and `issueStage` are null 29/29.
- **The white observed dot**, `r.hasObs`, `r.obsMark`. 0/29 windows carry an observed stage.
- **The monitoring dashed band.** The 5 upstream `MONITORING_WINDOW` values all arrive `NOT_APPROVED_FOR_DISPLAY` (Portuguese analyst prose), so per the narrative rule nothing renders.
- **The mandatory/regulatory band.** Upstream publishes a *dated act*, not a dated span. Drawing a bar would invent a duration, so the act renders as text (row source line, drawer `know`/`sources`) and `r.hasMand` is permanently false.
- **The five business buckets** ACT NOW / ACTIVATE / PREPARE / PLAN / NEXT CYCLE, and `bState()`. Replaced by the four canonical statuses. I confirmed the spec's arithmetic charge independently: the old ladder read `days = max(0, daysToOpen)`, so all 16 closed and all 5 date-unknown windows landed on day 0 and were labelled ACT NOW — **21 of 29 rows were wrong**.
- **20 fixture rows** vanish; 2 genuinely new crops appear. Wheat drops from 5 fixture regions to 2 canonical windows, Durum Wheat from 6 to 4. Rice and Soybean join the rail for the first time (both herbicide windows) and I drew two new crop marks for them in the ADAMA icon language.
- **The drawer's EARLY SIGNAL, VIEW OPPORTUNITY and GENERATE BRIEF.** `dw.early` is `NON OSSERVATO`, `dw.fieldCount` 0, `dw.hasCase` false.
- **The season view's eight phenology phase cards.** Replaced by one card per canonical window of the selected crop + one PRE-SEASON interpretation card. The section survives with real content instead of dying.

---

## 3 · Before / after numbers that change on screen

| | before | after |
|---|---|---|
| rows in the universe | 40 (8 crops × regions) | **29** (10 crops, 9 regions) |
| crops on the rail | 8 | **10** (+ Rice, Soybean) |
| rows that draw a window bar | 40 (2027 manufactured for passed ones) | **24**; 5 draw nothing and read DATA DA CONFERMARE |
| rows labelled ACT NOW | 21 | **0** — presentation no longer emits that string |
| KPI buckets | 5 invented + 2 context | 6 OPEN · 16 CLOSED · 2 NEXT CYCLE · 5 DATE UNKNOWN + 12 verified + 27 norm-only |
| rows with an observed stage | 10 (fixture) | **0** |
| rows with an ADAMA product | 40 (case fixture) | **12**, 6 distinct names |
| rows with a regulatory act | 1 fixture crop | **2** real (IT-WIN-0001 Veneto, IT-WIN-0008 Piemonte) |
| header strip | 5 fixture counts | 29 canonical / 24 dated / 12 verified / 2 regulatory / **0 observed** |

I measured **12** windows with a verified label match, not the spec's 11 — the model's `verdictKey` already folds `·` / `/`, so IT-WIN-0016 `Cereal Aphids · BYDV Risk` matches MAVRIK EW. Distinct products: EVURE PRO, MAVRIK SMART, COSAYR 200 SC, FORZA, MAXENTIS, MAVRIK EW.

---

## 4 · The preparation clock — kept, relabelled, never deleted

`AM.preparation` landed while I was working (provenance `SINTONIA_INTERPRETATION`, `observable: false`) and the block now reads it rather than owning constants. Every consumer carries the fence:

- lane text: `PREPARAZIONE · 90g · INTERPRETAZIONE SINTONIA`, title = `preparation.basis`
- row / moment / drawer: `prepLine` = `INTERPRETAZIONE SINTONIA · preparazione da 12 Mar · 90g`
- department bars and `deptPlan`: every label ends `· INTERPRETAZIONE SINTONIA`
- offsets anchor on the canonical `startDate`; **the whole block is omitted for the 5 rows without one** (`preparation.omittedWindows`)
- `dw.owner` is now the department whose interpretation range contains 2026-09-02, suffixed with the fence, else `—`. It is no longer derived from a day-count ladder.

The green preparation bar keeps its colour, height and position in the timeline. Only its claim changed.

---

## 5 · Two judgement calls where I departed from the spec

**(a) I did not link a window to an opportunity.** The spec's risk note says the ids do not overlap; the model's own join (`opportunity.LEGACY_CASE_ID` = `IT-HERO-00n` vs `window.legacyCaseId` = `IT-OPP-00n`) resolves **0 of 3**. But the reverse key `window.legacyCaseId === opportunity.id` resolves **3**, and two of them are genuine (IT-WIN-0001 ↔ IT-OPP-001 Grapevine/Flavescenza Veneto; IT-WIN-0002 ↔ IT-OPP-002 Maize/ECB FVG). The third is a plain id collision: IT-WIN-0029 (Durum Wheat / Toscana / Fusarium) against IT-OPP-003, which is the *national authorization-expiry* opportunity. A join that is 2/3 right is not a join, so `dw.hasCase = false` and two buttons disappear. **This belongs in the model, gated on region agreement, not in a view.**

**(b) I kept the ADAMA lane on the timeline, as a verdict badge.** The spec did not ask for it. The bar spans the canonical window because that is the only span upstream published; the bar *text* is `MAXENTIS · CORRISPONDENZA VERIFICATA SU ETICHETTA` and the title says the bar follows the canonical window, **not a use instruction**. If you judge that still over-claims, deleting `lane('adama', …)` is a one-line removal.

**(c) `STATUS_REASON` and `REGULATORY_ACT_STATE` are localized.** Both arrive in a non-Italian working vocabulary (`Reference date … falls after END_DATE`; `JA_NO_ACERVO`, `CITADO_EM_FONTE_SECUNDARIA`). Neither is a public quote, a source title, a product name or a Latin name, so rule 11 applies. I mapped the 5 and 3 measured values exactly, verbatim fallback for anything new. The act *names* (`DDR n. 13645 2026-05-14`) are never translated.

---

## 6 · MARKUP EDITS STILL REQUIRED — I could not apply these

Six of these are **mandatory**: without them the screen prints a dead fixture shape or an unqualified business claim. Line numbers are `client/portale.html`.

**MUST — a dead fixture shape is still in the literal text**

1. **649** — `<span …>~{{ r.ha }}k ha · {{ r.scale }}</span>` → `<span …>{{ r.issueL }}</span>`. Otherwise renders `~k ha · `. (`r.ha`/`r.scale` are null by design so it degrades visibly rather than lying.)
2. **704** — `~{{ r.ha }}k ha · {{ r.scale }} · {{ r.coverage }}` → `{{ r.issueL }} · {{ r.coverage }}`
3. **719** — `~{{ dw.ha }}k ha · {{ dw.scale }} crop relevance` → `{{ dw.dateStateL }} · {{ dw.coverage }}`
4. **680** — `MARKET <b style="color:{{ r.marketColor }}">{{ r.marketTemp }}</b> · FIELD {{ r.fieldCount }}` → `{{ r.sourceLine }}` (I define `r.sourceLine`; interim placeholders are `—` and `0`, neutral but pointless)

**MUST — an unqualified business claim**

5. **726** — `Commercial lead time {{ dw.leadDays }} days · preparation from {{ dw.prepFrom }}` → `{{ dw.prepLine }}`. "Commercial lead time" asserts channel behaviour that is not externally observable.
6. **723** — the green box: `background:#009845` → `background:{{ dw.stateBg }}` and the caption `COMMERCIAL STATE` → `{{ dw.stateCap }}`. Today a **closed** window still renders in bright ADAMA green under the words "commercial state". `dw.stateBg` is the model's own `ui.status.color`.

**SHOULD — text that now describes lanes that no longer exist**

7. **591** — `{{ t.cwBucketNote }}` → `{{ calKpiNote }}`. `t.cwBucketNote` still says *"40 righe coltura × regione su 8 colture"* and describes the deleted 0–30/31–60/61–120 thresholds. I build `calKpiNote` bilingually from the live counts, so no `italy-i18n.js` edit is needed and no other agent is disturbed.
8. **714** — `{{ t.cwFootNote }}` → `{{ calFootNote }}`, **plus** add `calFootNote,` to the props object at 3403. `t.cwFootNote` describes expected cycles, weed windows and observed markers — all removed. I define `calFootNote`; it is currently unreachable.
9. **611–624 legend** — delete the `t.cwLegCycle`, `t.cwLegObs`, `t.cwLegWeed`, `t.cwLegMon` and `t.cwLegReg` entries. Those five lanes are never drawn now. Keep `cwLegIssue`, `cwLegApp`, `cwLegBiz`, `cwLegDept`.
10. **736** — the hardcoded English `Portfolio check needed — no confirmed ADAMA position for this crop × issue.` → `{{ dw.noProductsText }}`, which renders the rule-10 wording plus the absence rule.
11. **732** — the MARKET PULSE tile has no honest value left. Suggest: caption → `PORTFOLIO`, value → `{{ dw.matchLabel }}`, note → the absence rule. `dw.marketTemp` is `—` in the meantime.
12. **731** — the EXPECTED CYCLE TODAY tile is computed from the deleted stage table. `dw.expectedNow` now returns the *date state* (`NORMA AGRONOMICA ATTESA`), which reads acceptably under the existing `agronomic norm` footnote — but the caption should become `{{ dw.dateStateCap }}` / value `{{ dw.dateStateL }}` / note `{{ dw.dateConfidenceL }}`. Props are defined.

**SHOULD — one state default**

13. **2386** — `calStart: 7` → `calStart: 4`. With 16 of 29 windows already closed, a viewport that starts at the reference month shows an empty timeline for more than half the rows. The fixture hid this by manufacturing a 2027 occurrence for every passed window; the truthful data cannot. I already changed `calNav.today` (mine) to frame the reference month a third of the way in — `Math.round(8 - calH/3)` — but the *initial* state is not in my block.

---

## 7 · Outstanding data questions the screen cannot answer

- **`sourceIds` is empty on 29/29 windows**, and the model tags `sourceState: NOT_EXTERNALLY_OBSERVABLE` — which reads oddly: a window *does* have sources in principle, they are just not attached. The drawer says "nessuna fonte collegata a questa finestra" on 27 rows. Consider inheriting the joined regulatory act's source id, or leaving it and fixing the label.
- **Three real regional acts are invisible.** Lombardia, Trentino and Emilia-Romagna Flavescenza have named, dated, primary-or-secondary-sourced acts in `currentFieldSignals` but no canonical window, so they appear nowhere on this screen. They are real facts being hidden because the window audit has not caught up.
- **Every free-text field on the 7 upstream field-signal rows is `NOT_APPROVED_FOR_DISPLAY` or `NOT_ESTABLISHED`.** I render none of them, per the narrative rule. That is why the monitoring lane is gone entirely rather than "on 2 rows" as the spec hoped — there is no *date*, only Portuguese prose.
- **The 10 `D.OBSERVED` rows** (Consorzio Brunello, ERSA FVG, Regione Veneto bulletins) cite plausible real sources but are not in the ingested pack. If they are real, promoting them upstream would light `observedStage` up on roughly 8 of 29 rows with no view change — the single highest-value data question here.
- `WINDOW_TYPE` is `APPLICATION` on 29/29. Until MONITORING and REGULATORY exist as first-class window records, the monitoring and regulatory lanes cannot come back as lanes.

==========================================================================================

**Block written:** `C:/eame-sintonia/italia-portale/audit/blocks/helpers.js` (411 lines, replaces portale.html 2394-2463). Validation: `node audit/splice.mjs try helpers` → **52/52 screen renders pass** with 17 landed blocks.

## Legacy fixture reads removed

The scanner (`audit/lib/scan.mjs`) measured the old block at **2 DATA_BEARING_CORE reads** out of 154 in the whole file. Both are gone; the block now contributes **0**, and it needs **no `@VISUAL_ONLY` / `@EXPLICIT_DEMO` marker at all**.

| line | symbol | replaced by |
|---|---|---|
| 2396 | `D.CASES` (29 invented cases, scored for the composer) | `AM.collections.opportunities` (3) + `AM.collections.cropWindows` (29), matched on the model's resolved `cropKeys` / `issueKey` too |
| 2397 | `D.COMPANIES` (6 invented competitors) | `AM.collections.competitorCompanies` — 14 rows folded case-insensitively to 11 distinct observed companies |

Also gone, though it was never a `D.*` read: `decorate()` took its pest/disease/weed class from `c.category`, a table the fixture authored. It now comes from `AM.categoryOf(ISSUE_TYPE)`. **Measured before swapping: the fixture's own `cat` agrees with the canonical `ISSUE_TYPE` on 29/29 cases, so not one card changes colour today** — only the provenance of the class changes. `c.st` (status tint) moved to `AM.UI.STATUS`, which landed mid-session with the same hexes.

Kept: `D() { return window.ITALY_DEMO; }` — the accessor itself, required by BLOCK-CONTRACTS (`head` does `const D = this.D()`). It is a binding, not a read.

## Components removed or emptied, with the measured reason

- **Field Sales badge on every radar card** (markup 238, `sc-if c.hasField`). `hasField` is now hard `false`. 18 synthetic WhatsApp records mapped onto 8 case ids; nothing real replaces them. The Field screen builds its own count and is untouched.
- **Category chip + icon circle** (markup 219, 221) go empty for an unclassified record. `AM.CATEGORY_UI.unknown.label` is `null` on purpose. 2 of the 3 real opportunities are unclassified (`FITOPLASMA`, and IT-OPP-003 whose `ISSUE_TYPE` is literally `"NAO SEI"`). New prop `hasCategory` is the flag markup must gate on.
- **Status pill** renders empty, not guessed, when upstream `CURRENT_STATUS` is null. Measured null on **3/3 real opportunities**, because none joins a canonical window (`windowId` null 3/3). `st.rank` falls back to 9 so an unassessed record sorts last, never first.
- **Window progress bar** is `0%` for a dateless record. Presentation may compute a pixel position from supplied dates (rule 7); it may not draw a bar for dates nobody supplied.
- **Date labels** fall to the `DATE_UNKNOWN` token ("DATA DA CONFERMARE") rather than a blank or a guess.

## Before/after that will actually show on screen

- **Opportunity screen, application window line.** Markup 312 binds `cs.windowLine`, and the old decorator localized only `windowLineL`, passing the raw code through under `windowLine`. The Italian screen was printing the literal string `WINDOW_CLOSED` (and `43|daysRemaining`). Now: `FINESTRA CHIUSA` / `43 giorni rimanenti`.
- **Field composer preview.** Markup 865/866 bind `parsed.issueL` and `parsed.cropL`; `parseField` never produced them, so both cells were empty. Now filled and localized.
- **`remainLabel`** was fed `c.we` — a raw day *offset*, measured 28 on IT-OPP-006 whose real remainder is 43. Now fed `daysLeft`. (Prop is unbound in markup; fixed anyway.)
- **`moreLabel`** on a real record with 6 resolved product links said "corrispondenza unica". Now "+ 5 altri". Counted off the resolved links, not a fixture field.
- **parseField reach.** IT-OPP-001 is written upstream as `Videira` / `Flavescência dourada…` in Portuguese, so an Italian message scored 2 against it and 5 against window IT-WIN-0001 — the opportunity was unreachable. Matching also on the model's `cropKeys ['Grapevine']` / `issueKey 'Flavescenza Dorata'` makes "flavescenza dorata sulla vite" land on **IT-OPP-001**, and "Bayer maize" on **IT-OPP-002**. The three example sentences the demo ships still classify (5, 5, 2 + Bayer).
- **`decorate()` no longer mutates its argument.** The old `Object.assign(c, …)` wrote ~30 presentation props onto whatever it was handed — for a real record that means writing UI state into `AM.collections`. Verified: **0/3 opportunity records polluted**, and re-decorating is idempotent because every value read is a raw source prop.

## What decorate does with each shape (all verified, none throws — including `{}` and `null`)

| | legacy case | real opportunity | canonical window |
|---|---|---|---|
| category | pest (from canonical ISSUE_TYPE) | **unknown, chip hidden** | pest |
| dates | 10 GIU — 20 LUG | **DATA DA CONFERMARE** | 10 GIU — 20 LUG |
| status | FINESTRA CHIUSA | **empty** | FINESTRA CHIUSA |
| portfolio | EVURE PRO, +5 altri | MAVRIK SMART, +5 altri | EVURE PRO, +1 altri |

For a canonical window with no link array, links are built from the audit's own two verdict lists (`verifiedProducts` / `notFoundProducts`; **12/29 windows name at least one verified product**), so §10 holds — a not-found product renders as NOT CONFIRMED IN THIS READING and is never hidden.

`AM.strengthFor` returns `NO_CONFIRMED_MATCH_CURRENT_READING` both when the label was read and the use not found, **and** when the crop word is simply outside the relationship vocabulary. My fallback downgrades the second case to `LABEL_CHECK_NEEDED` — printing absence there would be a false negative on a real ADAMA product. The model has since landed the same fix itself (`resolvedThrough: "OPP_CROP/OPP_ISSUE:VIDEIRA"`), so my path only runs for records without resolved links.

## Markup edits still required — I could not apply them

1. **portale.html 219 and 221** — wrap the category chip and the icon circle in `<sc-if value="{{ c.hasCategory }}" hint-placeholder-val="{{ true }}">…</sc-if>`. Until then an unclassified record renders an empty neutral tab and `background:url()`. This is the one place my "kill the prop, the sc-if hides it" trick does not work, because those two nodes have no guard.
2. **portale.html 238** — the `sc-if c.hasField` branch (`{{ t.lblField }} {{ c.fieldCount }}`) is now permanently false. Delete it.
3. **portale.html 2388** — `openWindow(id) { this.go({ view: 'window', windowId: id }); }` is now a dead duplicate. **My block redefines `openWindow` later in the same class body, so JS keeps mine.** I did this deliberately (the spec asked openWindow to resolve against the model, but line 2388 is outside my range); flagging it loudly so 2388 gets deleted rather than left as a confusing shadow.
4. **A back control has no home.** `back()`, `goBack()` and `canGoBack()` exist and RT4 passes (`radar → product → back() → radar`, filters restored, empty stack returns `false`). But nothing binds them. The `search` block owns the returned props object and must add `hasBack: this.canGoBack(), goBack: () => this.back()`, plus a header control in the markup.

## What the spec asked for that I could not do here

The `helpers.spec.json` plan is a **whole-domain** plan (15 steps: the `AM.UI` token migration, future-signal status, source group, person history, the competitor crop axis, the localization backlog). Almost all of it lives in other agents' line ranges. Inside 2394-2463 I could only do steps 7 (classification) and 10 (Field Sales containment, the card half). Its step 1 asked me to add `AM.UI` — another agent landed it during this session, so I read `AM.UI.STATUS` with a local fallback. Two notes on it: **`AM.UI.fmtDate` returns `null` for a `Date` object** (measured) and the legacy cases carry `Date` objects, so `decorate` keeps its own formatter, which accepts both; and `AM.UI.STATUS` has no keys for the fixture's space-separated legacy wording (`'ACT NOW'`, `'PREPARE'`, `'WATCH'`, `'VALIDATE'`, `'NEXT CYCLE'`), so a small legacy table survives locally as a fallback.

One caveat on the numbers: spliced **alone** into the frozen shared file, only 6/52 screens render — `sg0.whyWatch` is now a narrative object where the frozen signal block expects an array. **That failure is identical on the unmodified baseline block (6/52 there too)**, so it is the shared file drifting against the rewritten model, not my block. With colleagues' blocks present it is 52/52.

==========================================================================================

`C:\eame-sintonia\italia-portale\audit\blocks\competitor.js` — 347 lines, replaces portale.html 3156-3187. `node audit/splice.mjs try competitor` = **52/52 screen renders pass** (17 blocks spliced, IT + EN).

# COMPETITOR WATCH — what I did

## Fixture reads removed: all of them
The block had **32 lines and 32 fixture reads**. It now has **zero**. `grep -c 'D\.'` over my block returns 1 hit, and it is inside a comment.

| removed | line | replaced by |
|---|---|---|
| `D.ACTIVITIES` ×19 | 3157–3179 | `AM.collections.competitorActivities` (503 real / 0 demo, vs 72 fabricated) |
| `D.COMPANIES` ×4 | 3157, 3163–64, 3178 | `AM.collections.competitorCompanies` (11 merged rows) |
| `D.CASES` | 3169 | deleted — no company/product/activity links to a case |
| `D.CROP_COLS` ×2 | 3168, 3169 | `AM.collections.competitorCropDensity` (11 crops, not 6) |
| `D.WINDOWS` ×2 | 3169, 3177 | `AM.collections.competitorWindowMoments` (canonical status verbatim) |
| `D.MATRIX` | 3171 | `AM.collections.competitorMatrix` (11 companies × 11 crops, maxCell 22) |
| `D.EVENTS` ×4 | 3157, 3174–75, 3182 | `AM.collections.futureEvents` (18 real) |
| `D.ISSUE_ROWS` | 3180 | `AM.collections.competitorIssueDensity` (14 observed terms) |
| `D.CPRODUCTS` ×2 | 3185 | `AM.collections.competitorProducts` (36 proven) |
| `actDeco` (head block, reads `D.CASES`/`D.WINDOWS`/`D.EVENTS` in the original) | 3157–3186 | my own local `cAct`, so the domain does not depend on another agent's decorator |

**Reads kept with a marker: none.** I removed the one `@VISUAL_ONLY` marker I had written — the type colour/icon comes from the `CH` literal declared in the head block, not from `window.ITALY_DEMO`, so a marker would have been noise.

## Components removed or emptied, and the measured reason

- **PEOPLE, EVENT, VIDEO and PRODUCT/PORTFOLIO tabs** — measured type distribution is PAID 414 / ORGANIC_VIDEO 89 and nothing else. 7 pills → 3.
- **Company count grid: 6 tiles → 2.** Same reason. Bayer now reads PAID 69 / VIDEO ORGANICI 17 = 86.
- **`a.isVideo` overlay (duration + "transcript available")** — 0/503 records carry a duration, a transcript, a title or a view count. Guard is now permanently false. (Note: the head block's `actDeco` sets `isVideo:true` for ORGANIC_VIDEO, which would render an empty play button and "YouTube ·". Mine does not. Flagging the divergence.)
- **`a.isPeople` and `a.isEvent` blocks** — 0 records of either type, 0 `eventId` anywhere.
- **NEWLY OBSERVED badge** — there is no first-seen-by-Sintonia timestamp to diff; a start date is when the advertiser started. **I repurposed the badge slot** to carry `RAGGIUNTO ≠ TARGETIZZATO` (paid only). Same pill, true content, no markup change — but the binding name `a.newly` is now a lie and should be renamed.
- **COMMUNICATION TIMING verdict** (IN WINDOW / EARLY / APPROACHING) — §7 violation built on a substring match. A window link now needs a canonical crop **and** a species-level issue equal to the window's `ISSUE_NAME`. **Measured: 30/503 records carry a species term, only 11 carry one with a resolved crop, and none of the 9 distinct terms equals a canonical ISSUE_NAME** ("Plasmopara viticola" vs "Downy Mildew"). So it resolves for **0 of 503**. I did not relax it to crop-only matching.
- **ADAMA RESPONSE = "VERIFIED PORTFOLIO RESPONSE"** — was `D.CASES[].productLinks`. Now driven by `competitorWindowMoments.portfolioVerified` (the label audit through the model). Because the window link resolves 0 times, every card prints `NON VALUTABILE / "coltura e avversità non dichiarate nel record pubblico"` — a statement about the record, not "ADAMA has no product" (§10). The verified/absence branches are implemented and will light up the day upstream ships an issue synonym table.
- **MARKET PULSE line** — keyed off a crop that 320/503 records do not have. `marketTemp` is now `VEDI →`: a link, not a reading.
- **HIGH / MEDIUM / LOW density verdict** — thresholds 14/8 and denominator /20 were fitted to 72 rows; on 503 almost everything is HIGH, and a grade drifts into commercial importance (§8). `c.level` is now `''`; bars are relative to the observed max (Maize 67).
- **COMMUNICATION LEAD TIME card** — `leadTimes = []`, `leadCrop = ''`. Not measurable: per-company first observation is the Meta Ad Library retention horizon, not the company (UPL 2019-12-05, BASF 2023-03-08, Corteva 2024-11-26, Syngenta 2025-07-29, Bayer 2025-08-28, FMC 2025-10-21) and 5 companies have no dated record at all.
- **ISSUE table PAID column and ADAMA PORTFOLIO column** — all 98 issue-bearing records are PAID (column would repeat ITEMS); no observed term maps to a canonical ISSUE_NAME. Both set to `''`.
- **Company "themes" and "confidence"** — no counterpart in COMP_COMPANIES. `themes: []`; `confidence` now states the basis ("COMUNICAZIONE PUBBLICA OSSERVATA").
- **Company → cases, cproduct → cases, event → cases** — all `[]`. A shared crop is not a relationship (§13).
- **Event BEFORE/DURING/AFTER story and RELATED ACTIVITY wall** — `story: []`, `actCount: 0`, `activities: []`. No activity carries an eventId.
- **cproduct "People mentions"** — `''`.
- **`whatChanged` prop** — `[]`. It is exported at 3441 and rendered nowhere.

## Before → after numbers that change on screen

| | before | after |
|---|---|---|
| corpus | 72 | **503** (414 PAID · 89 ORGANIC_VIDEO) |
| company chips | 7 | **12** (ALL + 11) |
| "WHAT CHANGED" tiles | 6 | **1** (A PAGAMENTO · 30G = **11**; inside 7 days there is exactly **1** record) |
| crop density rows | 6 | **11** (Maize 67, Grapevine 42, Olive 24, Citrus 15, Tomato 12, Sunflower 9, Apple 5, Sugar Beet 4, Rice 3, Peach 2, Wheat 1) |
| matrix | 6×6 hand-written | **11 companies**, 6 columns shown of 11, ramp from maxCell 22; **6 companies are all-zero** (Syngenta has 55 items and not one names a crop) |
| issue rows | hand-written | **14** advertiser terms over 98/503 records |
| events | 5 demo | **18 real**, only **2** ahead (EIMA +69g, Vinitaly 2027 +221g); exactly **1** event names a competitor (Enovitis → Syngenta), all other rows are NON NOTO |
| competitor products | 14 invented | **36 proven** |
| feed groups | fake day labels | 29 month groups + a final **DATA NON OSSERVATA · 89** |
| card fields | ~14 decorated facts | crop chip on 132/503, issue chip on 98/503, product chip on 102/503, quoted ad text on 392/503, date on 414/503 |

**Be blunt: most cards are now nearly empty.** A typical PAID card shows page name, Meta Ad Library, a date, RAGGIUNTO IN ITALIA, the advertiser's own Italian copy in guillemets, and two tiles that say NON VALUTABILE. That is what the data supports.

## Markup edits still required (I cannot apply them)

Everything below is cosmetic-or-worse breakage that survives because the literal text is hard-coded. **Nothing false renders without these**, but several boxes render empty or with a dangling separator.

1. **1633** — fPeriod `<option>`s are 7/30/60. On real data 7d = 1 record. Bind to `{{ compPeriodOptions }}` (I export it: any / 30 / 90 / 365).
2. **1650** — `t.cwWhatChanged` says "ULTIMI 7 GIORNI"; the tile is 30 days. Change the i18n string. `t.cwNewlyObs` ("osservato di recente da Sintonia") is also wrong — the number is the advertiser's own start date.
3. **1683** — delete `<span ...>{{ c.level }}</span>` (now always empty).
4. **1684** — replace the static density caption with `{{ cropDensityNote }}` (I export it: "320 record su 503 non nominano alcuna coltura e 51 portano solo una parola ombrello…").
5. **1693** — replace `{{ m.cos }} competitors communicating · {{ m.acts }} items in 30d · ADAMA {{ m.prods }} matches · market <b>{{ m.market }}</b>` with `{{ m.cos }} aziende osservate · {{ m.acts }} elementi nel corpus · ADAMA · corrispondenze verificate {{ m.prods }}`. **"items in 30d" is false** (it is the whole corpus) and `m.market` is a stub `n/d` only because the literal word "market" is hard-coded. `m.prods` prints `n/d` when the audit has no verified triple, to avoid "ADAMA 0 matches".
6. **1722** — wrap the big `{{ a.product }}` in `<sc-if value="{{ a.hasProduct }}">`; it is empty on 401/503.
7. **1723 / 1725 / 1726** — delete the `a.isVideo`, `a.isPeople` and `a.isEvent` blocks (guards are permanently false; deletion is cleanup).
8. **1724** — change "Organic post · {{ a.platform }} · no image captured" to "Video organico · …".
9. **1727** — add a small `TESTO PUBBLICO ORIGINALE` label above `{{ a.headline }}`; it is now a verbatim advertiser quote, not a Sintonia headline.
10. **1728** — wrap `{{ a.cropL }}` in `<sc-if value="{{ a.hasCrop }}">` and `{{ a.issueL }}` in `<sc-if value="{{ a.hasIssue }}">`, otherwise 320 and 405 cards render empty grey pills. Rename the `{{ a.newly }}` badge (it now carries the reach caveat; `{{ a.geoCaveat }}` is available for a title attribute).
11. **1730–1732** — **delete the two-tile grid** (COMMUNICATION TIMING + ADAMA RESPONSE), or gate it on `{{ a.hasWindow }}`. Both labels are hard-coded and today both tiles read NON VALUTABILE on every card.
12. **1734** — delete `MARKET PULSE · <b>{{ a.marketTemp }}</b>`.
13. **1747 + 1748** — `matrixCols` must come from my block (see tail edits). The `repeat(6,1fr)` grid is fine — I cap at 6 columns and name the rest in `{{ matrixNote }}` (also needs a slot at 1746).
14. **1753–1759** — **delete the whole COMMUNICATION LEAD TIME card**, including the hard-coded ADAMA "Internal review · not connected" row (which also implies a private-data gap §1 says should not exist) and the caption using `{{ leadCrop }}`.
15. **1787 + 1788** — rewrite both `grid-template-columns:1.4fr 60px 60px 1.6fr 1.4fr 110px` to 3 columns; delete `{{ r.paid }}`, the `{{ t.lblPortfolio }}` header and `{{ r.adamaLabel }}`. Keep "CONTEXT →" — `r.go` now filters the feed by that term. Add `{{ issueRowsNote }}` as a footer.
16. **1799** — "Visible activity in Italy · last movement {{ co.last }} · {{ co.recent30 }} items in 30 days" is hard-coded English and must tolerate `co.recent30 === '—'` (5 companies have no dated record).
17. **1800** — `repeat(6,90px)` → `repeat(2,90px)`.
18. **1804** — add `{{ co.productsNote }}` ("NESSUN PRODOTTO PROVATO IN QUESTA LETTURA"); Bayer has 86 items and 0 proven products, and an empty box reads as "no products".
19. **1806** — delete the OBSERVED CONTENT THEMES card. **1809** — delete RELATED OPPORTUNITY CASES.
20. **Event detail** — delete the EVENT STORY card, the RELATED ACTIVITY section, and the `{{ evd.cases }}` card.
21. **cproduct detail** — delete the "People mentions" tile and change `repeat(4,120px)` → `repeat(3,120px)`; delete the `{{ cp.cases }}` card.

**Tail edits (search block, 3441–3443 — not mine to write):**
`compTotal: D.ACTIVITIES.length` → `compTotal,` · `whatChanged: D.WHAT_CHANGED` → drop the prop · `matrixCols: D.CROP_COLS` → `matrixCols,` · `compCropOptions: opts(...)` → `compCropOptions,` · `compIssueOptions: opts(...)` → `compIssueOptions,` · add `cropDensityNote, matrixNote, issueRowsNote, compPeriodOptions` · drop `leadTimes, leadCrop` once the card dies. **Until `matrixCols` is switched, the matrix headers (Grapevine, Maize, Wheat, Olive, Tomato, Apple) do not match my cells (Maize, Grapevine, Olive, Citrus, Tomato, Sunflower)** — that is the one edit that produces a *wrong* screen, not just an empty one. The search block also reads `c.issues` on company objects; I now supply it (it crashed otherwise).

## Things the spec asked for that the data cannot support, plus what I found

- **Issue synonym table is the blocker.** Without it, `relatedWindows` is 0/503 and the ADAMA-portfolio column on the issue table cannot exist. Everything is wired and will populate the moment it lands.
- **`ADS_REACHING_IT` is an occurrence count, not an ad count.** Measured: Exirel `ADS_REACHING_IT = 36` but only **26 distinct activities** name it; Arc 26 → 11; Spectrum 13 → 8. **16 of 36 products diverge.** I render the model's derived `activityCount`, so the company card and the product page agree — but the number the upstream table publishes is larger. Someone should decide which is the product's real reach.
- **The model's crop table was missing *Helianthus annuus* while I was working** (9 activities, 5 of which were classified `NOT_OBSERVED` — "names no crop" — when they name a binomial). The model agent has since fixed it; density is now 11 crops and `cropResolvedCount` is 132. Worth a regression note.
- **Portuguese working vocabulary is still leaking into event fields.** `SECTOR` arrives as "maquinas agricolas e de jardinagem" / "hortifruti" / "vinho e destilados" — I map that closed 6-value enum for display and suppress everything else. `EXHIBITOR_LIST_STATE` "161 marcas, segundo a UIV" is free Portuguese prose and is **suppressed entirely**, so the Enovitis card shows no exhibitor line. `CROP_RELEVANCE` renders verbatim tags including the Portuguese "CEREAIS" and "FRUTA E HORTALICAS"; I did **not** translate those (they are upstream taxonomy, not prose) and they will read wrong to an Italian client. These are upstream i18n debts, not view bugs.
- **`T.CROPS` has no entry for Citrus or Peach**, so those two render untranslated on an Italian screen.
- Answering the spec's open question 6: I kept the CREATIVE GALLERY, relabelled the pill to RECORD PUBBLICITARI, made every tile a uniform 150px, and each tile without a product reads `ASSET CREATIVO NON CATTURATO`. It is 503 uniform text tiles. If you would rather it die, the pill is one line in `compViews`.
- I collapsed compMoments to **one row per crop** (the raw projection gave three identical Olive rows for Puglia, Sicilia and Toscana, pushing every other crop off a 4-row panel). Result: Maize · Lombardia · FINESTRA APERTA (67 items), Olive · Puglia · FINESTRA APERTA (24), Sugar Beet · Veneto · FINESTRA APERTA (4), Wheat · Puglia · PROSSIMO CICLO (1 item, 1 verified ADAMA product).

==========================================================================================

**File written:** `C:\eame-sintonia\italia-portale\audit\blocks\head.js` (556 lines) · `node audit/splice.mjs try head` → **52/52 screen renders pass** with all 18 blocks spliced.

---

## 1 · Legacy fixture reads removed

| was (line in the old block) | symbol | replaced by |
|---|---|---|
| 2515 `const CASES = D.CASES.map(decorate)` | `D.CASES` (29 rows) | `AM.collections.opportunities.records` (3) `.map(mkOpp).map(decorate)` |
| 2526‑34 `dataState` | `window.ITALY_INGEST`, `window.ITALY_CANONICAL`, `D.ACTIVITIES`, `D.ARCHIVE`, `D.FIELD_MESSAGES` | `AM.provenanceSummary` (45 layers, model‑supplied label + real/derived/demo + isIndex) |
| 2549 `const K = D.KPI` | `D.KPI` (25 hand‑kept counters) | `AM.counts`, `AM.collections.cropWindows.statusCounts/regionCounts`, `AM.labelVerdicts`, `AM.collections.competitorActivities.recent30/recent7/undatedCount/italyReachCount`, `AM.collections.sources.groups/accessCounts` |
| 2564 `regionTiles = D.REGION_STATS.map(...)` | `.cases`, `.signals`, `.color` | `AM.UI.REGION_GRID` (geometry) + `cropWindows.regionCounts` (numbers) + `opportunities[].regionKeys` |
| 2565 `regionRank … b.signals` | `D.REGION_STATS[].signals` | deleted — see markup edit below |
| 2610 `winMatch` (inside actDeco) | `D.WINDOWS` + keyword guessing | deleted; 0 of 503 real activities carry a `windowId` |
| 2612‑35 `actDeco` | `D.CASES.find(...).products` (ADAMA response), `window.ITALY_MARKET` (temp), `a.headline`, `a.transcript`, `D.EVENTS` | model `productLinks`/absence rule, `AM.marketByCrop`, `a.text`, removed, `AM.collections.futureEvents` |
| 2637 `recentActivity = D.ACTIVITIES…` | 72 demo rows sorted by an authored `days` | 414 dated real records sorted by `daysFromRef` against `AM.REF` |

**Fixture reads left in the block: one.** Verified with the D1 scanner against the spliced scratch file — `DATA_BEARING_CORE = 0` inside my lines.

## 2 · Reads kept, with markers

- `/*@VISUAL_ONLY 4x5 grid geometry and the 2-3 letter tile labels …*/ D.REGION_STATS` — **fallback only**, unreachable while `AM.UI.REGION_GRID` exists. It supplies `name/col/row/short` and nothing else; every number on the map comes from `cropWindows[].region`.
- `/*@EXPLICIT_DEMO legacy presentation cases, default off (state.showScenarios) …*/ APP0.opportunityScenarios.records` — read through the model's `DEMO_SCENARIO` collection, gated on `s.showScenarios` (already `false` in state), and excluded from `K.total`.
- `D.setMonths(T.months)` — month abbreviations; the scanner classes it as a helper and does not count it.

## 3 · Before → after, on screen

| | before | after |
|---|---|---|
| radar cards | 29 | **3** (29 in scenario mode: 3 real + 26 — the demo reuses ids IT‑OPP‑001/002/003, so those 3 are dropped rather than shadowing the real ones) |
| KPI 1 *Opportunità attive* | 29 | **3** |
| KPI 2‑5 window status | 6 / 2 / 5 / 16 | **unchanged values, changed source** (`statusCounts`, not a demo shadow) |
| KPI 6 *Corrispondenze verificate* | 13 | **12** (`AM.labelVerdicts.verifiedCount`) |
| KPI 7 *Collegamenti di portafoglio* | 80 | **236** (`productRelationships`: 12 verified · 7 not found · 217 related — which is exactly what the card's own sub‑line, "tutte le relazioni, verifica compresa", claims) |
| KPI 8 *Movimenti · 30g* | 43 | **11**, with a new sub‑line: *"89 record senza data di inizio, esclusi · solo attività con data"* |
| data‑state rows | 6 | **45** |
| data‑state totals | 244 real / 29 derived / 491 demo | **1580 / 42 / 103** over 28 source layers; 774 archive‑index rows and 623 contained/derived‑view rows shown but excluded |
| region rank | Veneto 6 **+7 signals**, Puglia 6 +2, ER 4 +8, Piemonte 3 +9 … | Veneto 6 / Puglia 6 / ER 4 / Lombardia 3 / Piemonte 3 / Sicilia 3 / Toscana 2 — **+0 signals everywhere** |
| latest competitor moves | BASF "oggi", BASF "oggi", BASF "oggi", FMC "1g fa" … | Bayer 7g · Bayer 9g · FMC/Exirel 9g · FMC/Exirel 9g · Corteva/Mais 19g · FMC/Arc 21g |

## 4 · What the screen no longer shows

Gone from every radar card and from `actDeco`: the five evidence bars and the word *Strong*; the seeded‑PRNG competitor rows; the executive timeline (dates were arithmetic on two invented integers); the department action map and `fDept`; `adjacent[]`; `origin`; `latin`; the free‑text `source` line; the "COMMUNICATION TIMING" verdict; the "ADAMA RESPONSE" claim; the "MARKET PULSE" temperature; the authored `headline`; the "transcript available" badge.

The three surviving cards carry **no window dates, no status pill and a 0%-width progress bar** — measured, `canonicalWindow` is null 3/3 because the model joins opportunities to windows on `LEGACY_CASE_ID` and the real records carry `IT-HERO-001/002/003`, which no canonical window has.

## 5 · Markup edits still required (I cannot apply them)

1. **`portale.html:264`** — delete `<span style="color:#8F8886;font-size:10px;font-variant-numeric:tabular-nums">+{{ r.signals }} signals</span>`. Until it goes, every rank row renders the literal English "+0 signals". I emit `signals: 0` because that is the measured truth (all 3 real future signals carry REGION `NAO SEI` ×2 / `UE` ×1), but the span should not exist.
2. **`portale.html:122`** — raise `hint-placeholder-count` on the `dataState` `sc-for` from `6` to `45`.
3. **After `portale.html:135`** — add one footnote span bound to `{{ dataStateTotals.note }}`. Without it the columns visibly fail to add up, because the 15 excluded rows keep their numbers on screen.
4. **`portale.html:1729‑1733`** (competitor card) — delete the "COMMUNICATION TIMING", "ADAMA RESPONSE" and "MARKET PULSE" boxes. I fill them with honest UNKNOWNs (`NON VALUTATO`, the absence rule, `DATI NON SUFFICIENTI`) so no box renders empty under a hard‑coded English label, but three labelled boxes that always say "not assessed" on 503 cards is worse than not having them.
5. **`portale.html:196`** — `hint-placeholder-count="8"` still correct (8 cards kept).

## 6 · i18n keys owed by `italy-i18n.js`

- `kpiConvergences` / `kpiConvergencesSub`. All 3 records carry `FORBIDDEN_LABEL = 'nao chamar de "oportunidade Italia" nem de "oportunidade comercial"'`, and the card currently reads **"Opportunità attive"**. I read `T.kpiConvergences || T.kpiTotal`, so the moment the key lands the label fixes itself. **This is the one place the block still prints a word the data forbids.**
- `DSLAYER` (a per‑layer label map) — I read it first, then fall back to the model's Italian `label` and to an English map I keep locally.
- `APPWIN` — the three upstream `WINDOW.APPLICATION` tokens. My local map covers them (`APPLICAZIONE CHIUSA PER IL 2026` / `APERTA MA STRETTA` / `NON APPLICABILE`).
- `dsNote` should be rewritten: it explains a mostly‑demo panel that is now mostly real.

## 7 · Things I did differently from the spec, and why

- **KPI cards 2‑5 no longer filter the radar.** They count crop windows (their own sub‑lines say "finestra agronomica aperta ora"), and 0 of 3 radar records has a canonical status — a status filter would always return an empty screen. They now navigate to the crop‑windows view.
- **The spec's "region tiles are navigation only" is too pessimistic.** The model now projects `opportunities[].regionKeys` (`["Lombardia","Veneto"]`, `["Friuli-Venezia Giulia"]`, `[]`), so I kept `radarWith({fRegion})` and made the filter match `regionKeys` as well as `region`. Veneto → 1 card, Lombardia → 1 card, verified. `regionLabel` still shows the source's own sentence ("Veneto (principal) + Lombardia") because it says which region is primary and which is scale.
- **Card 7 kept, repointed at 236, not deleted and not repointed at 219.** `productRelationships` (CANONICAL, 12 + 7 + 217) is literally "all relationships, verification included". `regulatoryLinks` (219) is a different table and is exposed as `K.regulatoryLinks` for whoever wants it.
- **The transparency panel excludes far more than the spec anticipated.** The model grew to 45 layers while I worked; a naive sum reads 2347. I exclude 4 contained layers, 11 derived re‑cuts, the `people` union (66 = researchers 60 ∪ publicPeople 15, 9 shared) and the archive index — each row still shown, each carrying the row it belongs to.
- **`AM.provenanceTotals` (real 2040) is not used**: it sums `productsRegulatory` (163) and `productsCommercial` (44) alongside the `products` join (166) they are inside. I compute my own over the 28 source layers.

## 8 · What the data cannot support

- **IT‑OPP‑003 renders in Portuguese.** Crop reads `Portfólio ADAMA Itália (transversal, não é uma cultura)` and issue `Calendário de vencimento das autorizações`. `AM.lookups.OPP_CROP/OPP_ISSUE` has no entry because it genuinely is not a crop. Cards 1 and 2 do resolve (Vite / Flavescenza Dorata, Mais / Piralide del mais). Upstream needs `CROP_IT` / `ISSUE_IT` on that record, or the record needs a different screen.
- **All six narrative fields are `NOT_APPROVED_FOR_DISPLAY` on all 3 records** — the upstream prose is Portuguese working notes with no IT/EN variant. `happening` and `why` are therefore null on every card, and no amount of view work changes that.
- **No per‑region signal count exists.** Not derivable, not approximable.
- **No 7‑day competitor strip is possible**: the real corpus yields 1 record in 7 days (the fixture claimed 18). `K.movements7` is exposed for whoever wants to try.

## 9 · Cross‑block conflicts for you to arbitrate

1. **`nav.js` sets the radar badge to `AM.counts.windows` = 29** while my radar KPI card 1 reads 3. The left nav will say 29 next to a screen holding 3 cards. One of us has to move; I think the nav badge should be `counts.opportunities`.
2. **`competitor.js` and `signal.js` both declare `const nar` at `renderVals` top level** — the two collide and `splice try` fails with *"Identifier 'nar' has already been declared"* whenever both are present. Not mine (I renamed mine to `narOf`), but it will break assembly.
3. **The highest‑value model change left undone:** the model joins opportunities to canonical windows on `LEGACY_CASE_ID` only, and the real records carry `IT-HERO-00x`. But `cropKeys` + `issueKey` + `regionKeys` now line up exactly with real windows — `Grapevine / Flavescenza Dorata / Veneto` is `IT-WIN-0001`, `Maize / European Corn Borer / Friuli-Venezia Giulia` is `IT-WIN-0002`. Adding that join upstream would restore real start dates, end dates and `CURRENT_STATUS` to 2 of the 3 cards. **I did not add it** — a crop-name match is not a relationship (§13), and this is the model owner's call, not the view's.

==========================================================================================

Block written to `C:\eame-sintonia\italia-portale\audit\blocks\case.js` (312 lines). `node audit/splice.mjs try case` → **52/52 screen renders pass** with all 18 landed blocks spliced.

## Legacy fixture reads removed

The original block had **3 `DATA_BEARING_CORE` reads**; the new block has **0** (scanner-verified on the spliced file).

| was | line | replaced by |
|---|---|---|
| `D.REGION_STATS` (miniMap fill from a fixture region list + `cs0.adjacent`) | 2625 | `AM.UI.REGION_GRID` (coordinates only) + `record.regionKeys` for the highlight |
| `D.SOURCES` filtered by `x.cov`/`x.topics` against the demo crop | 2627 | `AM.collections.sources` resolved from the record's declared `SOURCE_IDS` (3/3, all resolve) |
| `D.SCI_THEMES.filter(t => t.cases.includes(cs0.id))` | 2628 | `relatedThemes: []` — no real theme declares a case |
| `CASES.find(...) \|\| CASES[1]` (silent fallback to demo case #2) | 2615 | `AM.collections.opportunities` first, `opportunityScenarios` only when `s.showScenarios`, else a self-reporting `hasCase:false` |
| `cs0.evidence`, `cs0.competitors`, `cs0.actions`, `cs0.departments`, `cs0.realObs`, `cs0.tl`, `cs0.origin`, `cs0.adjacent`, `cs0.primaryObj`, `allMessages` join | 2617-2632 | deleted or replaced (below) |

**Reads I kept with a marker:** none against `window.ITALY_DEMO` — the block no longer touches `D` at all. One `@EXPLICIT_DEMO` marker sits on `APP0.opportunityScenarios` (not a fixture alias, so the scanner ignores it) to document that scenario mode is opt-in and badges itself through `cs.isScenario`.

## Two measurements that changed my design (both contradict the spec's draft)

**1. `canonicalWindow` is null on 3/3, and the model's join key is wrong.** The adapter joins `windowByLegacyCase[U(o.LEGACY_CASE_ID)]`, but the opportunities write `LEGACY_CASE_ID = 'IT-HERO-001..003'` while all 29 canonical windows declare `LEGACY_CASE_ID = 'IT-OPP-001..029'` — i.e. the opportunity **id**. Without a window there are no dates, no `CURRENT_STATUS`, no stage classes and no canonical vocabulary. I honour the declared edge locally but **refuse it unless both the canonical crop and the canonical issue agree**, because the id space collides: window `IT-OPP-003` is Durum Wheat × Fusarium Head Blight while real `IT-OPP-003` is the authorisation-expiry calendar. Result: windows link on 001 and 002, correctly not on 003. **Model fix needed:** join on `o.ID`, keep the crop/issue guard.

**2. Trusting `ADAMA_PRODUCTS` alone would have printed the opposite of the audit.** Measured `AM.strengthFor`:

```
('Grapevine','Flavescenza Dorata')  MAVRIK SMART VERIFIED · EVURE PRO VERIFIED · 4 others NO_CONFIRMED
('Videira', Portuguese ISSUE)       all six NO_CONFIRMED_MATCH_CURRENT_READING
('Maize','European Corn Borer')     COSAYR 200 SC VERIFIED   ← IT-OPP-002's ADAMA_PRODUCTS is []
```
So the block resolves the vocabulary through the model's **declared** tables (`lookups.OPP_CROP`, `lookups.OPP_ISSUE`) and unions the record's declared products with the label-audit links. IT-OPP-002 now shows a real verified match instead of "no confirmed ADAMA label position" (§10). IT-OPP-002's `CURRENT_EVIDENCE` prose claims six products; that prose is **not** parsed.

## Components removed or emptied, with the measured reason

- **Evidence bars + `evChips` + `cs.source` attribution** → `[]`. The 5 numbers per case were hand-typed in `italy-demo-data.js` and then bumped by a `REAL_FACT`-stamped literal. Nothing upstream is comparable. The hero tile now reads `REGISTRATA · NON PONDERATA / 4 osservazioni collegate` (real `CURRENT_EVIDENCE` count 4/4/3); the word *Strong* is gone. The panel footer carries `Fonti dichiarate: 3 · lavori scientifici misurati: GRAPEVINE PHYTOPLASMA 135, SCAPHOIDEUS TITANUS 66 · nessuna misura di convergenza`.
- **Competitor activity panel** → `[]`. `italy-demo-data.js:317` builds company, item count, recency and type from a seeded PRNG. The 503 real activities need a crop synonym table for `Vitis vinifera` / `colture` that does not exist.
- **Action map, department chips, all six GENERATE BRIEF buttons** → `[]`. Static `ACTIONS[cat]` table with `{crop}`/`{product}` substitution; internal workflow, not external intelligence (§1).
- **Executive timeline (`cs.tl`)** → `[]`. Four dates from arithmetic on two invented integers.
- **Origin tile (`cs.origin`)** → `''`. Fixture integer claiming provenance history that does not exist.
- **Field Signals panel** → `fieldMessages: []`, `fieldCount: 0`, `noField: false`. A demo inbox on a real record; `noField:false` suppresses the hardcoded English empty-state.
- **`cs.latin`** → the record's own ISSUE, but only when client-safe. Survives on IT-OPP-002 (`Piralide (Ostrinia nubilalis) e Diabrotica virgifera virgifera`, binomials intact, never split at `(`); suppressed on 001 (`via o vetor…`) and 003.
- **`cs.adjacentLabel`** → `''`. Was a region claim and a recommendation in one fixture array.
- **`cs.label` (LABEL TIMING)** → `T.PSTATE.LABEL_CHECK_NEEDED`. `LABEL_TRIGGER` and `LABEL_SOURCE` are null on all 29 canonical windows; a spray timing no label supports is the highest-consequence fabrication on this page.
- **`know` / `watch`** → one honest line each (`"4 elementi registrati · testo non ancora localizzato"`). `WHAT_WE_KNOW` 4/4/3 and `WHAT_WE_DO_NOT_KNOW` 5/3/3 exist and every entry is Portuguese, so the entries cannot render; the count is a fact and the debt is stated instead of hidden.
- **`happening` / `why`** → `WHAT_IS_HAPPENING.CONTENT` and `WHY_IT_MATTERS.NOTE` hidden (untranslated prose 3/3). What survives is `STATE` (`SEGNALE CORRENTE`), the real observation block (`Bollettino vite Veneto n. 19 — 13/08/2026 · 17g fa`, 3/3), and the `MANDATORY` boolean (true/false/false).

## Before → after on screen

| | before (demo case IT-OPP-001) | after (real IT-OPP-001 / 002 / 003) |
|---|---|---|
| headline | Flavescenza Dorata | Flavescenza Dorata · Piralide del mais · **IN ATTESA DI LOCALIZZAZIONE** |
| updated | `Aggiornato 1g fa` (invented) | 17g / 18g / 6g — real `FRESHNESS_DAYS` of the source document |
| evidence | `Strong · 19 osservazioni collegate` | `REGISTRATA · NON PONDERATA · 4 / 4 / 3` |
| portfolio matches | 5 (fixture) | **6 / 1 / 0** |
| primary | fixture `primary` | MAVRIK SMART (VERIFIED) / COSAYR 200 SC (VERIFIED) / none |
| competitors | 3 rows | 0 |
| action map | 6 department cards | 0 |
| timeline | 4 points | 0 |
| sources | 5, matched by demo topic string | 3, resolved from declared `SOURCE_IDS` |
| region map | case region + 2-4 "adjacent" tinted | Lombardia+Veneto / Friuli-Venezia Giulia / **none** |

## Markup edits still required (I cannot apply them)

1. **line 315 — DELETE the ORIGIN tile.** It hardcodes `Future Radar · {{ cs.origin }}d ago`; with `origin` empty it renders `Future Radar · d ago`. There is no honest value for that sentence.
2. **line 299** — add an inner `<sc-if value="{{ cs.hasCase }}">` so an unresolved id shows an empty state (`cs.missingId` is exposed) instead of a skeleton.
3. **lines 320, 323** — remove the `deptChips` / `evChips` rows and the `{{ t.lblWhoLooks }}` / `{{ t.lblSupported }}` headings; the arrays are permanently empty.
4. **lines 419-423** — the `FORZA DELL'EVIDENZA` panel now has an empty `sc-for` above `{{ cs.source }}`. Drop the `sc-for`, keep the line.
5. **lines 441-452 (Competitor activity), 454-465 (Action map), 470-476 (Executive timeline), 402-408 (Field Signals)** — four panels whose headings and English sub-labels now sit over empty grids. Remove them.
6. **line 314** — `{{ cs.evidenceTotal }} {{ t.lblConnObs }}` reads "4 osservazioni collegate"; they are evidence statements, not observations. Reword `lblConnObs`.
7. **line 352 / 361-362** — the masked window bar draws 0% for IT-OPP-003. Guard it with a new `cs.hasWindow`-style `sc-if`; I expose `cs.windowLine` carrying `nessuna finestra canonica collegata`.
8. **English hardcoded in markup, still visible:** line 378 `Label context · … · dose and interval per label record`; line 396-398 `No confirmed ADAMA label position matched…` (add `{{ cs.absenceRule }}`, which I now expose); line 393 `Registered · {{ p.moa }}`; line 391 `Single registered match for this crop × target.` (fires on IT-OPP-002); line 433 `Major {{ cs.cropL }} area · ISTAT regional scale` — an unsourced claim template that should die; line 434 `Validate next` heading over an empty value; line 366 `{{ cs.matchCount }} portfolio matches`; line 425 `REGIONAL CONTEXT · NUTS-2 precision`.
9. **line 305** — a `DEMO SCENARIO` badge bound to `cs.isScenario` when scenario mode is on.
10. **line 2869 (windows block, not markup)** — `cs.goWindow = () => this.openWindow(winFor(cs0.id).id)` overwrites the honest link I set (`openWindow(csWinRec.windowId)`) and routes to a demo window. And `openWindow` resolves against `D.WINDOWS`, so `IT-WIN-0001` will not open. That belongs to the windows agent.

## What the spec asked for that the data cannot support

- **`CASE_LABEL` chip** (spec: "add it here, it is the record instructing the UI how it may be named"). I do **not** render it. `CONVERGENCIA QUE MERECE INVESTIGACAO` is Portuguese and trips the language guard, and it is identical on 3/3 so it differentiates nothing. `FORBIDDEN_LABEL` is likewise not rendered — it is an instruction to the interface, and I obey it: the word *opportunity* never appears in anything this block emits.
- **`SCIENCE_CONTEXT` as a label/value list** — no slot exists in the markup wide enough (the evidence rows give the label 56px). The numeric members are folded into `cs.source` instead. `BRIDGE_TESTED` is excluded: it is a Portuguese sentence that explicitly says the bridge was *not* proven, and printing it beside two counts would read as a finding.
- **`INTERPRETATIONS`** (spec: "what the real records offer instead of actions") — 2 entries on 3/3, all Portuguese, no slot, not rendered.
- **The `LOMBARDIA` / `VENETO` / `BASIS` regional-decree strings on IT-OPP-001** are the single most actionable content in the whole package (mandatory treatment windows, decree numbers, EU regulation article) and **none of it reaches the screen** because it has no approved localization. This is the highest-value item on the narrative-debt list.
- **Region text stays Portuguese-flavoured**: `Veneto (principal) + Lombardia`, `Friuli-Venezia Giulia (sinal) · vale do Pó (escala)`, `Itália (nacional)`. The audit's marker list does not catch these and I chose not to widen it there, because dropping the field would lose the primary/secondary and scale distinctions and leave IT-OPP-003 with no geography at all. The map highlight uses the model's canonical `regionKeys`, so no invented region is claimed — but upstream should supply `REGION_IT`.
- **`ISSUE_TYPE 'FITOPLASMA'`** is not classified by `categoryOf()` (it tests `PHYTOPLASMA`, not the Portuguese spelling), so IT-OPP-001 would render neutral-grey with no category name. I take the category from the linked **canonical** window instead (CANONICAL outranks REAL_SOURCE), which gives PEST. A one-token fix in `categoryOf` would make that unnecessary.
- **IT-OPP-003 loses its headline entirely.** `Calendário de vencimento das autorizações` and its CROP sentence both fail the guard; the H1 reads `IN ATTESA DI LOCALIZZAZIONE` and the crop reads `Non è una coltura · portafoglio trasversale`. I did not translate them — a renderer inventing localizations is exactly what the narrative rule forbids. Upstream needs `TITLE_IT` / `ISSUE_IT`.

Verified: 0 Portuguese strings and 0 stray English in `cs` / `cs0` / `crumb` across all 26 screens × 2 languages; no `new Date()`; no forbidden global; no `.find(...) || X[0]`; `cs` and `cs0` both still defined per `BLOCK-CONTRACTS.md`, and the brief screen (which consumes `cs0`) renders in both languages.

==========================================================================================

Block written to `C:\eame-sintonia\italia-portale\audit\blocks\science.js` (501 lines, replacing portale.html 3188–3316). `node audit/splice.mjs try science` → **52/52 screen renders pass**. Fixture reads inside my block: **0** (verified by running `audit/lib/scan.mjs` over the spliced scratch, lines 5918–6414).

# FIXTURE READS REMOVED

| old line | symbol | replaced by |
|---|---|---|
| 3189 | `window.ITALY_SCIENCE` (`SB`) — `SB.B`, `SB.REL`, `SB.EXTRA_THEMES`, `SB.RECORD_REL`, `SB.ACTIVITY_NOTE` | **nothing.** Every field it fed (rel, short, why, shows, notShows, changes, owners, actions, limits, moa) is a business verdict no external source states. Deleted, not re-sourced. |
| 3190 | `SB.REL[k]` colours | `AM.categoryOf(...)` / `AM.CATEGORY_UI` (canonical ISSUE_TYPE → pest/disease/weed) |
| 3191 | `window.ITALY_MARKET.CROPS` / `.SEM` / `.TEMP_SEM` (`mkTempFor`) | nothing — the model states no market verdict/temperature is derivable. `market` renders `NESSUN VERDETTO DI MERCATO DERIVATO`; the Market Pulse link stays as navigation. |
| 3196 | `D.WINDOWS` (`winFor2`, substring match on issue words) | `AM.collections.cropWindows` + an explicit 4-entry issue-token→window-issue map; status printed verbatim through `wst()` |
| 3199–3238 | `D.SCI_THEMES` (10), `SB.EXTRA_THEMES` (3), `D.CAT`, `D.inkOn`, `D.RECORDS` | `AM.collections.scienceThemes` (5) |
| 3244 | `window.ITALY_INGEST.RESISTANCE` / `.PRODUCTS` | `AM.collections.resistance` (34) + `AM.products` (91 HERBICIDA) |
| 3304 | `D.SCI_THEMES` (`sciDetailThemes`) | deleted; `th` resolves from `scienceThemes` by key with **no fallback to [0]** |
| 3309 | `D.RECORDS` (36; 24 seed()-generated) | `AM.collections.scienceRecords` (88), sorted by real `publishedAt` desc |
| 3310 | `D.PEOPLE` (`people`) | `AM.collections.people` (66) — landed in model v3.1 while I worked |
| 3311 | `D.PEOPLE` filtered `p.role === 'Researcher'` | `AM.collections.researchers` via `people` — **note: that filter is now dead code upstream, `role` is null 60/60 after the model's UNK() guard** |
| 3312 | `D.INSTITUTIONS` (12 hardcoded) | `AM.collections.scienceInstitutions` (6), local tally kept as fallback |

**Reads I kept with a marker: none.** No `@VISUAL_ONLY`, no `@EXPLICIT_DEMO` in this block.

# COMPONENTS REMOVED OR EMPTIED — measured reason

- **`sciTop` → `[]`** ("MOST IMPORTANT FOR ADAMA NOW", 4 cards). Ranked the fixture's 8-step ladder. Nothing external ranks a research theme by importance to a company. Not re-ranked by works count — that would be the same claim with a different number under it.
- **`sciStrategic` → `[]`** ("STRATEGIC SCIENCE & PORTFOLIO GAPS"). `isStrategic` was a fixture flag; a per-theme "gap" would be an absolute negative built on a navigation join.
- **`opportunityLine`, `caseObjs`, `caseCount` → `''` / `[]` / `'—'`.** The theme↔opportunity link exists only in `italy-demo-data.js:372-381` `cases: [...]`. `IG.SCIENCE` has no case field, `IG.THEMES` has none, the 3 opportunities have no theme key. Kills 5 UI blocks.
- **`record.related` / `openCase` → empty object + no-op.** Fixture assigned it by `caseObjs[i % length]` — a modulo.
- **`record.why` → author; `record.locationShort` → venue.** The generated sentence asserted timing/pressure relevance; the study region was invented 45% of the time. Both replacements 88/88 real.
- **`record.bizRel` → `''`.** No source states business relevance for a paper.
- **`theme.trend` / `trendColor` → `'—'` / neutral.** `IG.THEMES` has WORKS, AUTHORS_IT, AUTHORS_WITH_ORCID, AUTHORS_ACTIVE_SINCE_2024 — four point-in-time counts from **one** query. No earlier headcount exists, so no movement is computable. Deliberately did **not** substitute AUTHORS_ACTIVE_SINCE_2024.
- **`researcher.bizUse` / `bizWhy`** — was "POTENTIAL EXPERT TO WATCH" + "technical watch and possible expert engagement" attached to a named real person. Replaced by `worksInScope + themeLabel` and the source's own `IDENTITY_STATUS` (never upgraded to "confirmed").
- **`institution.type`** — fixture decided it by `name.startsWith('CREA')`. Replaced by what the row actually is: "affiliazione del primo autore".
- **GIRE mode-of-action (`mech`, `moaGroups`)** — the old code regex-matched HRAC groups out of `MECHANISM`. **Measured: 34/34 arrive `NOT_APPROVED_FOR_DISPLAY`** (Portuguese working note with the fact inline). That is parsing a research note for a fact. Now `sciNar(r.mechanism) || 'MECCANISMO NON PUBBLICATO'` — the gate, so an approved text would render if one ever lands. **I did not fall back to `CITATION` either: 18/34 citations also contain analyst text** (`literal:`, `a ficha`, `NAO SEI`).

# BEFORE / AFTER ON SCREEN

| | before | after |
|---|---|---|
| `sciTotal` / `sciThemeCount` | 13 | **5** |
| `sciCounts` chips | 8 business-relevance classes | **3 canonical target classes** (Pest 3 · Disease 1 · Weed 1) |
| `sciTop` | 4 ranked cards | **0** |
| `sciStrategic` | 3 rows | **0** |
| `sciResistance` | 2 fixture themes | **1 real theme** (WEED_HERBICIDE_RESISTANCE) |
| `records` | 36 (24 fabricated) | **88 real**, sorted 2026→2019 |
| `researchers` panel | 14 (half "Demo profile") | 8 shown of **60 real**, sorted by real LAST_ACTIVITY |
| `institutions` / `instCount` | 12 | **6** (2 of them not Italian) |
| `people` (archive/person screens) | fixture | **66** (60+15 merged on folded name, 9 collisions) |
| GIRE | 34 cases, 30 linked, 91 herbicides | **unchanged: 34 / 30 / 91** |
| theme detail records | fixture rows | 43 / 40 / **0 / 0 / 0** — three theme pages now empty |
| theme detail institutions | fixture | 11–12 chips, **names only, no works number** |

New honest values on the theme cards: portfolio verdicts read from the audited windows — VINE_FLAVESCENCE `VERIFIED` (EVURE PRO, MAVRIK SMART), DURUM_FUSARIUM `VERIFIED` (MAXENTIS), MAIZE_BORER `VERIFIED` (COSAYR 200 SC, FORZA), OLIVE_BACTROCERA `NO CONFIRMED MATCH IN THIS READING` + absence rule (3 not-found verdicts), WEED_HERBICIDE_RESISTANCE `LABEL CHECK NEEDED` (no canonical window exists, so the label question was never asked — Rule 10).

`sciActivityNote` now carries the caption the spec called the highest-consequence item, recomputed in code so it cannot go stale: *"88 record scientifici, 7 autori distinti e 6 affiliazioni distinte (2019–2026). È la lista di pubblicazioni di 7 ricercatori, non un censimento della scienza italiana…"*

# MARKUP EDITS STILL REQUIRED (I cannot apply them)

These render as empty text or a dangling separator until applied. In priority order:

1. **line 2064 + 2071** — delete the 5th column of the RECENT RESEARCH table: header `<span>RELATED CASE</span>`, the grid template's 5th track (`minmax(72px,1.4fr)` in **both** the header div and the row div), and the whole `<span onClick="{{ r.openCase }}">{{ r.related.issueL }} · {{ r.related.region }}</span>`. **88 rows currently render a bare " · ".**
2. **line 2064 + 2069** — delete the 4th column (`BUSINESS RELEVANCE` header + `{{ r.bizRel }}` span + its track). If you'd rather keep the column, I already ship `r.materialRoleL` (88/88 real, 6 controlled values) — rename the header to `RUOLO DEL MATERIALE / MATERIAL ROLE` and bind that.
3. **line 2168** — same deletion in the theme detail: `<span onClick="{{ r.openCase }}">{{ r.related.issueL }} · {{ r.related.region }}</span>` and its `minmax(0,150px)` track.
4. **line 1996 and 2054** — delete `<span …>{{ TH.opportunityLine }}</span>` and `CURRENT COMMERCIAL OPPORTUNITY · {{ TH.opportunityLine }}`.
5. **line 2133** — delete the `{{ t.lblRelatedOpps }}` / `{{ sciImpact.opportunityLine }}` tile in the impact drawer.
6. **line 2162** — delete the whole `{{ th.trend }}` / "Publication movement" tile. **line 2163** — delete the `{{ th.caseCount }}` / `{{ t.lblConnOpps }}` tile.
7. **line 2176-2177** — delete the CONNECTED OPPORTUNITY CASES card (renders as a header over nothing).
8. **line 1952** — `SCIENCE → BUSINESS` strip label and `{{ sciTotal }} classified themes · counts reconcile`: rename to something like `SCIENZA · TEMI MONITORATI` and `{{ sciTotal }} temi bibliometrici`. The counts do reconcile (5 = 5 = sum of sciCounts), but "SCIENCE → BUSINESS" no longer describes what is under it.
9. **line 1969** — the `MOST IMPORTANT FOR ADAMA NOW` strip header now sits above an empty grid: delete the strip.
10. **line 2055-2056** — the STRATEGIC SCIENCE card is now header + footer only: delete the card.
11. **line 2062** — add next to `RECENT RESEARCH · {{ kpi.records }} RECORDS` the depth caveat. `{{ sciActivityNote }}` carries the sentence but renders further up the page (line 1976).
12. **line 2083** — `INSTITUTIONS · {{ instCount }}` needs the caption that these are first-author affiliations, not study locations, and that two of the six are not Italian. `{{ i.type }}` already says the first half per row.
13. **line 2179** — MONITOR NEXT promises "movement into Future Radar signals". No movement is measurable; rewrite without it. `{{ th.instCount }}` now means institutions in the OpenAlex theme profile (11–12), a different denominator from the 6 on the home screen.
14. **line 1987** — `{{ t.lblAdamaExposure }} · {{ TH.moaNote }}`: the note now explains that overlap is botanical genus, not mechanism. Reads correctly as-is, but "ADAMA EXPOSURE" is a strong label for it.

# WHAT THE SPEC ASKED FOR THAT I DIVERGED ON

- **Spec said "GIRE block: NO CHANGE, it is already real."** It is not fully. The HRAC mode-of-action was regex-derived from a Portuguese research note that the model gates as `NOT_APPROVED_FOR_DISPLAY` on 34/34. I removed the derivation. The mission's domain guidance overrides the spec here.
- **Spec's open question — keep `ITALY_SCIENCE.B` for the 5 mapped themes.** I removed it entirely. `window.ITALY_SCIENCE` is on the mission's FORBIDDEN READS list and the D1 scanner enforces it. This is the single biggest visible deletion and it is a product-owner call: the authored `short` / `why` / `shows` / `notShows` / `changes` / `actions` / `limits` prose is gone from 5 real themes as well as 5 orphan ones. If the owner rules that authored interpretation is allowed under a labelled heading, restoring it for the 5 mapped keys is a contained change to `sciBuild`.
- **Spec suggested printing the works count on the per-theme institution chips.** I do not. **Measured: theme 001's top entry is 177 while the theme's own WORKS is 135** — it is not a subset and the source never says what it counts. Printing "177" beside "135 Topic-linked works" invites the wrong subtraction.
- **Species display.** The old block preferred `SPECIES_IT` over the binomial in Italian. I reversed it: the Latin binomial always shows (Rule 11), the Italian vernacular moves beside the crop. Three separate `Lolium spp.` records all read "Loietto" before and were indistinguishable.

# TWO MODEL DEFECTS I MEASURED (not mine to fix)

1. **`resistance.multiple` is true on 34/34** because `!!S(r.MULTIPLE_RESISTANCE)` coerces a non-empty Portuguese sentence. At least 10 of those sentences literally begin **"NAO SEI"** ("I don't know") and 5 more say cross-resistance but explicitly *not* multiple. Any screen binding `multiple` publishes "multiple resistance" for records whose source says the opposite. I do not read the field. Needs an `UNK()`-style guard at the model boundary.
2. **`publicPeople.role` and `.org` leak Portuguese.** `UNK()` only catches "NÃO SEI". Measured 4 of 5 non-null roles are working prose (`coordenador do GIRE`, `membro do GIRE`, `responsavel do setor`, `formacao declarada em Scienze Agrarie...`) and 1 of 15 orgs is a description (`canal proprio de viticultura`). These survive into `AM.collections.people`, which the archive/person screens read. I guard both locally (`role: null`; an org with no capital letter resolves to "non noto") — the guard belongs in the model so every view gets it.

Also worth flagging to the archive owner: `AM.collections.scienceRecords[].publishedAt` is now 88/88 populated, which silently fixes 88 previously date-less archive rows.

==========================================================================================

Block written and validated. Report follows.

---

# archive · sources · news · people — engineering report

**File:** `C:\eame-sintonia\italia-portale\audit\blocks\archive.js` (470 lines, replaces `client/portale.html` 3317–3375)
**Validation:** `node audit/splice.mjs try archive` → **52/52 screen renders pass** (26 screens × it/en, spliced with all 17 colleague blocks).
**Fixture reads in my block: 0.** Regex-verified against the D1 scanner's own pattern (`\b(D)\s*(?:\.\s*ident|\[)`) — zero hits, so zero `@VISUAL_ONLY` / `@EXPLICIT_DEMO` markers were needed. Every mention of the old fixture in my comments was rewritten to `ITALY_DEMO.X` so the scanner (which does not strip comments) cannot count a comment as a read.
All 21 contract names still declared: `PAGE, aq, archAll, archiveTypeChips, archiveTypes, dr, isNews, isPeople, newsItems, newsPeriodChips, page, pages, peopleCatChips, pr, sgp, sourceGroupChips, sourceKpis, sr, visibleArchive, visiblePeople, visibleSources`.

---

## 1 · Every legacy fixture read removed, and what replaced it

| Old line | Symbol read | Replaced by |
|---|---|---|
| 3318 | `D.ARCHIVE` (448 rows, 420 procedurally generated) | `A_ARCHIVE0` = `AM.collections.archive.records` — **774 rows, real 774 / demo 0, 0 duplicate ids** |
| 3318 | `a.type` filter (9 legacy types) | `a.kind` (8 real kinds) |
| 3318 | `a.region` filter clause | **deleted** |
| 3318 | text query over `title + summary + source + product` | `title + crop + issue + company + source` |
| 3320–3329 | `archDeco` — `isDemo`, `sourceL`, `sourceRoute`, `descriptor`, `title.split(' · ').map(translate)` | all deleted; real titles are publisher/author strings and are no longer re-composed |
| 3331 | hardcoded 9-value `archiveTypes` array | 8 measured kinds |
| 3332 | `D.ARCHIVE.find(a => a.type === t).typeColor` | `record.ui.color`; the unguarded `.find(...).typeColor` (a latent throw — `'News article'` already had no chip) is gone |
| 3333 | `D.ARCHIVE.find(a => a.id === s.archiveId)` | `arcRows.find(a => a.id === recordKey)` |
| 3337 | drawer link `ADAMA PRODUCT` | **deleted** — 0/774 rows carry one |
| 3336 | drawer link `FUTURE SIGNAL` | **deleted** — 0/774 (demo assigned by `i % 5 === 4`) |
| 3340 | drawer link `RESEARCH TOPIC` via `D.SCI_THEMES` | **deleted** — reached through the demo case |
| 3344–3346 | hardcoded 8 group chips incl. `EVENTS & TRADE FAIRS` | `AM.collections.sources.groups` — 7 real groups + ALL |
| 3348–3350 | `D.NEWS.filter(n => n.days <= …)` period chips | **deleted**, `newsPeriodChips = []` |
| 3351 | `D.NEWS` + `n.use[]` CTA routing | `AM.collections.news` (8), CTA now points at the publisher in the source registry |
| 3352 | `D.SOURCES` (53) | `AM.collections.sources` (31) |
| 3362–3365 | `K.orgs/people/...` from `D.KPI` | `K` from the head block (now model-derived) + the 66-person directory count |
| 3367 | `D.SOURCES.find(...) \|\| D.SOURCES[0]` | resolved on `sourceId`, **no silent fallback** (see §4) |
| 3368 | `srItems = D.ARCHIVE.filter(a => a.sourceId === sr0.id)` | real `sourceId` join against the archive index |
| 3369 | `sr.cases` from `cov` + `topics` against demo `CASES` | **`[]`** |
| 3370 | `people.find(...) \|\| people[0]` | resolved on `id`, **no silent fallback** |
| 3372 | `pr.history` — 5 fabricated dated rows from `lastDays + k*9` against `D.TODAY` | **deleted**, `history: []` (this also broke §6, one clock) |
| 3354–3359 | `PCAT_IT` / `pCats` — 9 legacy people categories | 4 real `roleCat` values + ALL |

**People:** I do **not** rebuild the directory. The science block (`audit/blocks/science.js:408`) now publishes `people` — the same merge my spec prescribed (`researchers` 60 ∪ `publicPeople` 15, diacritic-folded name, 9 overlaps → **66**). Reading it instead of building a second one is what keeps the Science screen and the People directory naming the same humans. Cross-checked against the model's own brand-new `AM.collections.people` (66; `RESEARCHERS 62 · INSTITUTIONAL EXPERTS 2 · COMPANY PEOPLE 1 · INFLUENCERS / CREATORS 1`) — identical counts and identical `roleCat` keys, so the `goResearchers` deep link (`peopleCat: 'RESEARCHERS'`) still lands.

---

## 2 · Reads I kept, with a marker

**None.** No `@VISUAL_ONLY` and no `@EXPLICIT_DEMO` marker appears in this block. Colour, order and layout all come from `record.ui` (model-authored, §4) or from local label maps I wrote.

---

## 3 · UI components removed or emptied, and the measured reason

| Component | State | Measured reason |
|---|---|---|
| Archive **region `<select>`** (markup 2195) | filter clause deleted; the control is now inert until the markup is removed | a region exists on **29 of 774** rows. Everything else has `'NAO SEI'`, a country, or an ad-reach country the package itself flags `AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY` (§9). Filtering on it would read as "no record from Veneto", which is false — it is *unknown*. |
| Archive **row subtitle, region half** | now carries the **issue** label | same 29/774. See the loud warning in §5 — this is a binding-name hack I could not avoid without editing markup. |
| Archive **drawer prose paragraph** | replaced by the verbatim original public text; **365 of 774 rows show nothing** | the 420 demo summaries were template prose. Reality has an original text on two kinds only: competitor ad copy 392/503 and public-voice transcript 17/17 = **409/774**. News `SINTONIA_SUMMARY` is `NOT_APPROVED_FOR_DISPLAY` on **8/8**. SCIENCE, MARKET, EVENT, WINDOW, RESISTANCE render nothing. |
| Archive **drawer region tag** | `''` | as above |
| Archive **drawer links** ADAMA PRODUCT / FUTURE SIGNAL / RESEARCH TOPIC | deleted | 0/774 each |
| Sources **"WHAT SINTONIA OBTAINS" column** | **empty on 31/31 rows** | `ROLE` is a Portuguese Sintonia note, `NOT_APPROVED_FOR_DISPLAY` on 26/31 and `NOT_ESTABLISHED` on 5. The 5 read "non noto"; the 26 render nothing. The column should be deleted from the markup. |
| Source-detail **CROPS / TOPICS card** | `topics: []` | there is no crop or topic field on the registry in any form |
| Source-detail **RELATED OPPORTUNITIES card** | `cases: []` | the only real reverse link names 3 sources; the demo built the rest from `cov` + `topics` |
| News **TODAY / 7 / 30-day chips** | `newsPeriodChips = []` | against `AM.REF` 2026-09-02 the newest item is **126 days old**; the set spans −126 to −2016 days and 1 of 8 has no date. All three chips read 0 and the 30-day default emptied the feed. |
| News **region chip** | `''` | `REGION = 'NAO SEI'` on 8/8 |
| News **"ORIGINATING SOURCE"** | `''` | no equivalent field; `CONTENT_KIND_MEANING` answers a different question and was not repurposed under the old label |
| News **`use[]` CTA routing** | replaced | "RELATED OPPORTUNITY →" asserted that an article supports a case. No field carries it. |
| Person **RECENT SIGNALS · SOURCE HISTORY** (5 rows) | `history: []` | five dates and five sentences generated from one integer |
| Person **CONNECTED OPPORTUNITY CASES** / **CONNECTED FUTURE SIGNALS** cards + both header KPIs | `[]`, counters read **`—` not `0`** | no person→opportunity or person→signal edge exists anywhere upstream; the demo built it with `CASES.filter(x => x.crop === r.crop)`. `—` because the absence of an edge in this package is not a measured zero. |
| Person **PUBLICATIONS · TOPIC** card | shown for **1 person of 60** | the ORCID join into the 88 `scienceRecords` resolves only for Massimo Blandino (25 works). The other 59 omit the card; `WORKS_IN_SCOPE` is a count and is not dressed as a list. |
| Person/People **Platform**, **Crops**, **Issues** cells | `'—'` | no person record carries a platform; `crops []` and `issues []` measured 60/60. `THEME` is the scope of the OpenAlex query, not a declared crop, and is shown only where the label says "tema monitorato". |
| Person/People **Region** | "non osservabile" / "regione non osservabile da fonti esterne" | `FACT_REGION` is `'NÃO SEI — a afiliação é do AUTOR, não do estudo'` on 60/60, and the source's own `LIMITATIONS` says the same |
| People **identity badge** | three-valued state, not "real identity" | `ORCID_PRESENT_NOT_RESOLVED_HERE` 54, `NO_ORCID_IN_SOURCE` 6. "Real identity" overstated an ORCID nobody resolved. |
| People **5 legacy category chips** | gone | agronomists/engineers, technical advisors, field experts, producer voices and the 7 ADAMA sales reps all have **zero** real members |
| **D.TSR on the People directory** | absent, `isTsr` permanently false | internal staff, §1 keeps them out of the external core; they stay on the labelled Field Sales screen |

---

## 4 · Things I fixed that the spec did not ask for

- **RESISTANCE (34 rows) did not exist when the spec was written.** Its `crop` is a GIRE field note carrying the Portuguese reading note inline (`'Riso (arroz) — "Sistema colturale: riso."'`), 34/34, and the model tags all of them `cropVocab: 'UPPER_CODE'`, **which they are not**. I cut at the reading note, drop the Portuguese gloss in brackets and refuse anything still carrying prose punctuation; 33 survive as short Italian (`riso`, `uliveto`, `grano duro e tenero`), tagged `IT_SOURCE_TEXT`. Its `date` is likewise prose (`'1994 — literal: "Primo caso accertato nel 1994."'`); only a leading 4-digit year — a fact the source states — is taken.
- **RESISTANCE titles.** 5 of 34 append a Portuguese reading note after an em dash (`'Lolium spp. — a ficha especifica…'`) and 1 writes its synonym list with a Portuguese connector. Cut at the em dash, connector relabelled `sinonimi:`. **The parenthetical synonym list is kept in full** — §11 forbids truncating a taxonomic name at `(`.
- **Portuguese leak through object spread.** The source record carries `roleText`, `limitationsText` and `raw.*` — the working notes behind the two narrative fields. A spread handed all of them to the template layer even though nothing binds them. `srcDeco` now **builds** its row instead of spreading. Same for the archive row's raw `crop`/`title`, which are overwritten rather than shadowed.
  Measured after the fix: **0 Portuguese hits over 58 renders** of my props (archive, all 8 kinds' drawers, sources, people, news, source detail, person detail, it+en) and **0 over all 774 drawers** except 8 false positives which are verbatim **Italian** competitor ad copy (`"Cosa rende unico Velsinum?"`) that the heuristic misreads. `undefined` / `[object Object]` in my props: **0**.
- **Source frequency vocabulary.** The 6 declared cadences are written in the package's working Portuguese (`semanal`, `anual + boletins`). A cadence word is not a product, company, Latin name, quote or source title, so §11 does not protect it — localized. Unmapped values render verbatim.
- **Issue tokens.** `T.ISSUES` does not hold the SCREAMING_SNAKE tokens SCIENCE/VOICE use, so `il()` printed `FLAVESCENCE` / `DOWNY_MILDEW` raw. Localized following the rule the Voci block already set: FUSARIUM and SEPTORIA stay the Latin genus, FLAVESCENCE does **not** become "flavescenza dorata", WEED does **not** become a named weed programme.
- **Silent fallback (check R2).** `sr0` and `pr0` no longer end in `|| X[0]`. A `sourceId` or `personId` that does not resolve now renders "Fonte non trovata nel registro" / "Persona non trovata" instead of quietly putting another institution's masthead — or another human's name — on the page. Identity is never swapped.
- **Sort.** The real index had no sort at all (push order — the first page was 20 science papers). Three bands, all arithmetic over supplied dates against `AM.referenceDate` and never `new Date()`: observed captures newest-first (554), then rows dated after the reference date soonest-first (36 — expected windows and scheduled events, which are forecasts not captures), then 184 undated grouped by kind. **Note:** `AM.REF` is a `Date` object, not a string — comparing `dateISO > AM.REF` silently coerces and always returns false. I use `AM.referenceDate`. Worth telling the other agents.

---

## 5 · Markup edits still required — I could not make these

**REQUIRED (visible defect until applied):**

1. **`portale.html:2263`** — `{{ n.date }} 2026 · real` on every news card. Two of the eight items are from 2021 and 2022 and one has no date; the template prints `"2021-02-24 2026"`. Change to `{{ n.date }}` and delete the ` 2026 · real` decoration — provenance belongs in the data-state panel, not as card jewellery.
2. **`portale.html:2195`** — DELETE the whole region `<select>`. Its filter clause is gone, so it is now an inert control that appears to do something. Also drop `aRegion` / `setARegion` from `audit/blocks/search.js:243`, `hasArchiveFilters` and `clearArchive` (`search.js:245`), `archiveWith` (`portale.html:2422`) and `state` (`portale.html:2382`).
3. **`portale.html:2210`** and **`2312`** — `{{ a.cropL }} · {{ a.region }}` → `{{ a.subtitle }}`. I export `subtitle` already. **Until this lands, `archDeco` puts the ISSUE label into the `region` slot** so the subtitle reads "crop · issue" as the analysis prescribed. That field is marked `⚠ NOT A REGION` in the source. It is the one thing in this block I am not comfortable with, and it goes away the moment the binding is renamed.
4. **`portale.html:2348`** — the hardcoded note *"Demo profile — a neutral sensor profile, not a real individual"* is now **false**: these are 66 real, publicly named people. Replace with the affiliation caveat (`AM.collections.people.affiliationCaveat`: "The affiliation belongs to the author, not to the study") or delete.
5. **`portale.html:2288`** — `{{ s.related }} cases` in the sources table. The number is now archive rows joined on `sourceId` (Meta 414, OpenAlex 88, AgriFood 77, YouTube 106, GIRE 34) — not cases. Change the literal to `elementi` / `records`.

**STRONGLY RECOMMENDED:**

6. **`portale.html:2194`** — crop `<select>` must bind `{{ archiveCropOptions }}` instead of `{{ cropOptions }}`, and `audit/blocks/search.js:283` must export it (I declare it). `cropOptions` is measured **4 entries** built from the radar's cases; against this index it reaches only the 29 canonical WINDOW rows. My options list is grouped and labelled by vocabulary (`Vitis vinifera · nome latino`) so the client can see these are separate packages talking, not one taxonomy. Mitigation already in place: the `aCrop` filter also matches the **upstream-declared** canonical (`competitorActivities.cropsCanonical` 132/503, `news.cropCanonical` 3/8, WINDOW canonical by construction) — **164 rows reachable by a canonical crop name**, and not one mapping invented by me.
7. **`portale.html:2196`** — company `<select>` may keep `{{ companies }}`: the competitor block now publishes all **11** real companies, so nothing is unreachable. `archiveCompanyOptions` is declared as a fallback if that changes.
8. **`portale.html:2282` / `2298`** — delete the "WHAT SINTONIA OBTAINS" column and the source-detail line under it. Empty on 31/31.
9. **`portale.html:2283` / `2301`** — rename the column header **COVERAGE → GEOGRAFIA**. `'IT'` means the source is Italian, not that it covers all Italian crops.
10. **`portale.html:2223`** — render only non-empty tags. Crop is empty on 416/774 and issue on 534/774, so the drawer often shows three empty pills.
11. **`portale.html:2265` / `2266`** — delete the news region chip and the "ORIGINATING SOURCE" half of that footer grid; both are permanently blank. Move the "EDITORIAL TYPE" badge up onto the card body — it is the one thing that got *better*: 3 of 8 items are ADAMA Italia publishing about its own products, 1 is Bayer (`COMPANY_PROVIDED`), 1 is `BRANDED_CONTENT`, only 3 are `EDITORIAL`.
12. **`portale.html:2251` / `2323`** — drop the Platform and Region cells from the person card and header, and relabel "Crops"/"Issues" as "Tema monitorato" / "Opere nel recorte". Until then those four cells read `—`.
13. **`portale.html:2255` / `2332` / `2335`** — the "N opportunities · N signals" line and the two header KPI tiles read `—`. Delete them.
14. **`portale.html:2325`** — the header tile labelled `t.lblLastObserved` ("Last observed") now shows `LAST_ACTIVITY`, which is the date of the last **indexed work in the monitored theme**, not an observation of that person. Relabel (`ultima opera indicizzata nel tema`).
15. **`italy-i18n.js:78` and `:363`** — add `ARCHTYPES` entries for the 8 real kinds (`COMPETITOR, SCIENCE, MARKET, RESISTANCE, WINDOW, EVENT, VOICE, NEWS`). `en.ARCHTYPES` is measured **`{}`** and `it.ARCHTYPES` holds only the 9 dead legacy keys, so `arcT()` falls through to the raw token. My **chips** are localized locally, but the type `<select>` (built in the search block via `arcT`) will show raw tokens until this lands. Also reword `arcSub`: "connected to opportunities, signals, products, competitors and research" is now partly false — products and signals connect to no archive row.
16. **`portale.html:480`** — "VIEW IN ARCHIVE →" from an opportunity detail lands on a **one-row** list (`legacyCaseId` is 29/774, exactly one row per `IT-OPP-001..029`), and that row is not an observed capture: its `sourceProvenance` is `CANONICAL`, it has no url, and its source reads `ITALY_CANONICAL`. Either accept the honest single row or relabel the link so it stops promising per-case evidence.

---

## 6 · Before / after on screen

| | before | after |
|---|---|---|
| Archive rows | 448 (real 28 / **demo 420**) | **774 (real 774 / demo 0)** |
| Archive pages | 23 | **39** |
| Type chips | 9 legacy types, 1 kind with no chip | **8 measured kinds** |
| Rows with a source | demo `sourceId` | **725 / 774 (93.7 %)** real registry ids |
| Rows with a parseable date | — | **590 / 774 (76.2 %)**; 184 print a dateState token, never a fabricated date |
| Rows with a crop | — | **358 / 774**, across **5 vocabularies** that are labelled as such |
| Rows with a company | 6 demo companies | **503 / 774**, 11 real companies |
| "CONNECTED TO" green case link | 351 / 448 | **29 / 774** — 745 rows read the company or `—` |
| Drawer body text | 448 rows of template prose | **409 rows** of verbatim original public text; **365 show nothing** |
| Sources | 53 | **31** (26 open routes, 5 restricted — 3 of the 5 are ADAMA, Bayer and Syngenta sites) |
| Sources backing ≥1 archive row | — | **10 of 31**; the "related" column is zero on **21** — two thirds of the registry is a listening list, not a feeding list |
| "People monitored" | 39 (incl. 7 invented ADAMA reps + 18 seeded profiles) | **66** real, publicly named |
| People category chips | 9 (5 with zero members) | **5** (ALL + 4) |
| News items | 9 curated | **8** real; **0** recency chips (was 3, all reading 0) |
| Person "SOURCE HISTORY" | 5 dated rows per person | **0** |

---

## 7 · What the spec asked for that the data cannot support

- **A working region dimension anywhere in this domain.** Archive, news and people all lose it. Nothing replaces it.
- **A single clean crop dropdown.** The spec was right and I did not soften it: 5 vocabularies, and I refuse to map them onto each other. Only the 164 rows where *upstream* declared a canonical crop are reachable through a canonical name.
- **A recency control on news.** Impossible over 8 records spanning five years.
- **`source.related` as "N cases".** The only honest join is to archive rows, and it is zero for 21 of 31 sources.
- **`WHAT SINTONIA OBTAINS`.** There is no client-ready text for it on any of the 31 records.
- **A per-person topic sentence.** The closest real substitute is `themeLabel + worksInScope`, which is a scope statement plus a count. That is what I render, labelled as such.

## 8 · Data debts I am reporting, not fixing

- `italy-app-model.js` tags all 34 RESISTANCE rows `cropVocab: 'UPPER_CODE'`. They are free Italian/Portuguese source wording. Should be its own vocabulary tag upstream.
- News `ISSUE` values leak the working language: `"infestanti resistentes"`, `"resistencia a ACCasi e ALS"` (2 of 8). Near-Italian, but not Italian. Upstream fix, not a view fix — I render them verbatim rather than silently editing a fact.
- News `CROP` tokens `CEREAIS` (Portuguese) and `ORTICOLE` have no `cropCanonical`; they render as raw tokens.
- `AM.REF` is a `Date`; `AM.referenceDate` is the ISO string. Any block comparing `dateISO > AM.REF` is silently always-false.

==========================================================================================

Done. Block written, validated, and (since the block phase closed mid-task) applied to the shared file.

**Files**
- `C:\eame-sintonia\italia-portale\audit\blocks\search.js` — the block (309 lines)
- `C:\eame-sintonia\italia-portale\client\portale.html` lines **6892–7196** — byte-identical to the block file (verified by diff)

---

## 1 · Legacy fixture reads removed (line = old portale.html)

| line | symbol removed | replaced by |
|---|---|---|
| 3376–3385 | the whole 8-scan `searchGroups` array | `AM.searchIndex` → one filter, one group-by, one dispatcher |
| 3377 | `CASES` (=`D.CASES.map(decorate)`, 29 rows, 26 `DEMO_SCENARIO`) | `AM.searchIndex` kind `case` — **2** upstream-real opportunities |
| 3379 | `D.PRODUCT_LIST` (33) | kind `product` — **166** (163 registry + 3 catalog-only) |
| 3380 | `D.SCI_THEMES` (10) + `D.RECORDS` (36) | kinds `science` (88) + `resistance` (34) = **122** |
| 3381 | `people` (=`D.PEOPLE`, 39, ids `RR-01`/`P-13`/`TSR-1`) | kind `researcher` — **60**, ids `IT-PER-001…` |
| 3382 | `companies` demo scan | kind `company` — **11** (adds Sipcam, Certis, Sumitomo, Nufarm, Gowan) + 503 observed activities |
| 3383 | `D.ARCHIVE` (448) | **deleted, not replaced** (see §3) |
| 3384 | `D.SOURCES` (53) | kind `source` — **31** |
| 3391 | `todayLabel: D.fmt(D.TODAY)` — a second clock frozen in the fixture | `AM.referenceDate` → `"02 SET"`, identical string, one clock |
| 3399 | `simulateInbound: D.FIELD_MESSAGES[…]` | `APP0.fieldMessages.records` — same 18 rows, each carrying `SYNTHETIC_DEMO` |
| 3404 | `ladder: D.LADDER.map(… D.DEPT[…].soft)` | `ladder: []` — internal ADAMA playbook, and **bound by no markup node** |
| 3407 | `sendComposer: D.TSR.find(…)`, `D.CAT.pest`, `A_SCEN.find(…)` | removed; the composed message keeps only what the user typed + what `parseField` recognised, stamped DEMO |
| 3408 | `notifs: D.NOTIFICATIONS` (6) | `notifs: []` (see §3) |
| 3418, 3441 | `Object.keys(D.PRODUCTS)` (33), `Object.keys(D.DEPT)` (6) | derived from the rows actually being filtered |
| 3443 | `D.CROP_COLS`, `D.ACTIVITIES`, `D.WHAT_CHANGED`, `D.ACTIVITIES.length` | the Competitor block's real `compCropOptions`, `compIssueOptions`, `whatChanged`, `matrixCols`, `compTotal` |
| 3402 | `mpReview: MK.LAST_REVIEW` | `''` — `ITALY_MARKET.LAST_REVIEW` is now `undefined`; the fixture was stripped |

`grep -c "\bD\.[A-Z_]"` on the block = 10, **all inside comments**. D1 / D2 / S1 / S2 / S3 / N3 all pass.

## 2 · Reads KEPT with a marker
**None.** The block has zero live `D.*`, `ITALY_DEMO`, `ITALY_INGEST`, `ITALY_CANONICAL`, `ITALY_MARKET`, `ITALY_SCIENCE`, `ITALY_REAL` reads. The one `@EXPLICIT_DEMO` comment sits on `simulateInbound`, which now reads the model's provenance-tagged `fieldMessages` collection instead of the raw fixture, so the demonstration is readable as demo *from the data*.

## 3 · Components removed or emptied, with the measured reason

- **ARCHIVE search group (448 rows) — deleted.** `AM.archive` is a derived index over the same science / market / competitor / voice / event / news / window records the per-kind groups now reach directly. Keeping it would have double-counted every hit in `searchTotal`, and it carries no region and no product field at all — two of the five things that group used to search on do not exist in reality.
- **Notification centre (6 rows) — emptied.** They asserted current events with fabricated relative timestamps no clock produced (`"FIELD SIGNAL CONNECTED · Flavescenza Dorata · Veneto · 38 min ago"`, `"WINDOW UPDATE · European Corn Borer · FVG · 14 days remaining"`). §5: a demo fixture feeding a real current signal.
- **`ladder` (5 rows) — emptied.** An internal ADAMA playbook (90d MARKET DEVELOPMENT → 14d SALES/RTV) sitting beside external evidence, and bound by no markup node (the only `ladder` the markup renders is `wd.ladder`, built by the Crop Windows block).
- **Department filter — now 1 option.** Derived from the opportunity rows instead of `D.DEPT`; the real opportunity records carry no department, so the picker offers only "Tutti i reparti". Honest and empty.
- **`mpReview` — empty string.** Nothing external states when Sintonia last reviewed its own sources.
- **CHANNEL kind (30) — withheld from search.** Channels are listed on no screen in the package; only 3 of the 30 are even named on a Voci card.
- **8 of 77 market observations — withheld.** `Feed barley` (1) and the unresolved `ORGFOUR|FEED` (7) resolve to no Market Pulse crop bucket; routing them would leave a *different* crop on screen than the row clicked.

## 4 · Before / after numbers that change on screen

| | before | after |
|---|---|---|
| searchable universe | **657** rows, 654 of them fixture | **1039** real, routable rows (index 1077, 38 withheld) |
| groups | 8, hardcoded English | up to 12, localized from `SINTONIA_I18N`, only groups with hits emitted |
| ADAMA products | 33 | **166** |
| opportunities | 29 | **2** — the only upstream-real ones. A search for "Septoria" or "Cercospora" now returns zero opportunities. That is the honest number. |
| sources | 53 (25 of the real 31 unopenable) | **31**, all opening the source named |
| researchers | 39 demo, all 60 real ones opening the *same* demo person | **60**, each opening itself |
| competitor communications | 0 searchable | **503** + 11 companies |
| crop windows / market / news / events | 0 searchable | **29 / 69 / 8 / 18** |
| competitor row labels | 11 distinct strings for 503 rows ("BASF Agricultural Solutions" ×138) | **249 distinct** — the products the ad proves (102/503), else the advertiser's own copy (392/503), else the page name |
| overflow | card printed "503" and showed 6 rows, no way to the rest | 6 rows + `+ 497 altri risultati · VEDI TUTTO →` into the section |
| breadcrumb | blank on Portafoglio, Product Intelligence, Voci | named (`titles` had no entry for those three views) |

Routing verified by brute force: **all 1039 destinations opened and compared against the row that opened them — 0 mismatches** (product 166/166, window 29/29, case 2/2, signal 3/3, event 18/18, company 11/11, source 31/31, researcher 60/60 resolve the exact entity; voice, resistance, science, news land on the list that visibly contains the record — 17/17 Voci cards, 34/34 GIRE rows with `gireAll`, 88/88 science records, 8/8 news items, 503/503 activities present in the company-filtered feed). Then **481 simulated clicks across 23 queries × 2 languages: 0 render failures, 0 rows containing `undefined` / `[object Object]` / a `NAO SEI` sentinel.**

Two matching changes worth naming, both measured:
- The row is matched on **what the reader sees**, not only on the index terms. Without it, `"flavescenza"` found nothing in OPPORTUNITY (the model indexes IT-OPP-001 on the analyst's Portuguese *"flavescencia dourada"*), and `"frumento duro"` missed 4 crop windows and 8 market observations whose crop is shown in Italian but indexed as the canonical key `Durum Wheat`.
- Diacritic folding on both sides: `Marzachi` reaches `Marzachì`.

## 5 · Portuguese working prose kept off the screen
`PT1` and `PT2` now pass (0 hits over 52 renders). Specifically in this block:
- OPPORTUNITY rows use `issueKey` + `regionKeys` + `cropKeys`, never `title` / `issue` / `crop` — those are Portuguese on 3/3 real opportunities (*"Videira x Flavescência dourada, via o vetor Scaphoideus titanus"*). Same rule the Field Sales panel already uses.
- GIRE rows: species cut at the em/en dash only, **never at `(`** (§11 — `Schoenoplectus (Scirpus) mucronatus` survives). Meta was the crop string, Portuguese prose on 12 of 34 rows, one of them 155 characters; it is now the botanical **family**, filled 34/34 and Latin. One residue remains handled by name: `(sinonimi na ficha: …)` on IT-RES-002 — the two Portuguese words go, the whole synonym list stays.

## 6 · Markup edits still required (I could not edit the markup)

1. **`portale.html:2358`** — hardcoded English, and now factually wrong:
   `{{ searchTotal }} connected items across opportunities, signals, products, science, people, archive and sources.`
   *archive* no longer exists as a group and five groups are missing (windows, voices, market, news, events). Replace both strings with i18n keys (`t.searchResultsFor`, `t.searchTotalNote`) and add them to `italy-i18n.js` **it + en** with wording that does not enumerate groups.
2. **`portale.html:147`** — the notification bell's unread dot is a hardcoded green circle. With `notifs: []` it now permanently claims unread notifications that do not exist. Delete the `<span>`.
3. **`portale.html:1279`** — `{{ t.cannotProveList }} Last source review {{ mpReview }}.` now renders "Last source review ." Remove the sentence (it is also untranslated English).
4. *Optional:* `portale.html:2360` `hint-placeholder-count="6"` → `8`; up to 12 groups can now appear.

I did **not** need the `g.empty` node: the overflow row is delivered as a seventh item in `g.items`, so the card geometry, the border-top accent, the dotted separators and the grid are untouched. `MK1` (every markup-bound prop still returned) and `MK2` pass.

## 7 · Things the spec asked for that the data cannot support
- **Per-voice detail.** The Voci screen has no id anchor, so a voice hit can only land on the list. It does contain all 17.
- **Theme routing for science.** Only 83/88 science records carry a `themeKey`, and only 2 of the 5 real themes are represented; routing there would be a coin flip. Science hits land on the section, which lists all 88.
- **Competitor activity → `cproduct`.** The model routes activities to `route: 'cproduct'` with an `activityId`, but `openCProduct` matches on a product *name* — all 503 would have opened the first competitor product. I override it to the company-filtered feed, which contains the record. **This is the one place I deliberately ignore the model's `route` field; the model should be corrected.**
- **Company `crops` / `issues`.** No such fields at company level. Searching "which competitor talks about maize" now answers at the activity level.

## 8 · Notes for whoever integrates
- Failures still open in `audit/run.mjs` (36/42) and **none belong to search**: `F3` (Future), `R2` ×3 (Competitor — `companies[0]`, `CEVENTS[0]`, `CPRODUCTS[0]` at portale.html 5827/5878/5903), `L1` (Crop Windows renders "Internal stock" / "Scorte interne" at 806 and 4332 — private ADAMA data on a core screen), `L3` (Science block, portale.html:6203, `.split('(')[0]` on `speciesIt` — truncates a taxonomic name at `(`), `RT3` (Field block, `fieldCases.*.windowText` renders `[object Object]` — an unhandled narrative object, and it appears on **all 26 screens** because `fieldCases` is a global prop), `B3` (CDN).
- `match` at portale.html ~2541 is now **dead** — it had no caller outside the eight scans I deleted. The `head` block owns that line.
- `SEARCH_READY` is the integration lever: one line per kind. Only `channel: 0` is currently off.
- The model was still being edited while I worked. `AM.searchIndex` went 611 → 1078 → 1077 entries and opportunities 3 → 2 mid-session. Nothing in my block hardcodes an id or a count, so it followed each change; the `IT-OPP-003` fallback-to-id branch is dormant but still correct if a crop-less opportunity returns.