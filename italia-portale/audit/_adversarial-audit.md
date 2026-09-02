# ADVERSARIAL AUDIT · `client/portale.html`

**Read-only. Nothing edited.** Measured against `client/portale.html` sha1 `dc4b63d09c327c` (16:15). ⚠️ **The file changed 5 times while I audited** (7 different sha1s between 15:45 and 16:15) — other agents are still editing. Every finding below was re-verified on the final read unless marked otherwise. All measurements come from `audit/lib/harness.mjs` `mount()`/`vals()`, driving the real render, not from grep.

The structural suite reports 47/48. Every finding below is invisible to it.

---

## BLOCKER · 1 · ~92 interface labels render blank right now

**Screens:** case, windows, window, field, market, product, voices, future, competitors, company, science, theme, archive, sources, news, orgs, person (14 of 26)

The markup binds 287 distinct `t.*` keys. **101 of them resolve to `undefined` in BOTH languages** (≈92 real, ≈9 are `sc-for as="t"` loop aliases). Agents replacing hardcoded English with i18n keys are adding the binding and not adding the string.

```
walk markup lines 50..2175, collect {{ t.X }}, resolve against vals().t for it and en
→ 101 keys undefined/empty in both
```

Live casualties include:
- Opportunity detail: `t.lblPortfolioMatches`, `t.lblNoConfirmedFor`, `t.caseNotFound`, `t.lblRegionalContext`, `t.lblNuts2`, `t.lblRegion`, `t.lblRegisteredShort` — the "no confirmed ADAMA label position" sentence is now an empty span.
- Window detail: `t.wdFactual`, `t.wdFactLabel`, `t.wdFactCycle`, `t.wdExpected`, `t.wdUnknown` — the entire *WHAT IS FACTUAL · EXPECTED · UNKNOWN* row is three blank columns.
- Field Sales: 18 keys (`t.fsIntro`, `t.fsStructures`, `t.fsCompIssue…fsCompResult`, `t.fsComposerCaveat`) — the whole explanatory column is blank.
- Competitor: `t.cwMatrixTitle`, `t.cwColIssue/Items/Companies`, `t.cwContext`, `t.cwProductsObserved`, `t.cwCropsObserved`.
- Science: 8 table headers. Archive: `t.lblPrev`, `t.lblNext` (unlabelled pagination buttons).

**Why it violates the law:** §3 — a smaller truthful screen beats a dense fake one, but a *blank* label under a populated value is neither; the reader guesses what the number means.
**Smallest fix:** add the 92 keys to both locale blocks of `client/italy-i18n.js`; add a check that resolves every `{{ t.X }}` in the markup against both locales (MK1 only proves the `t` object exists).

---

## BLOCKER · 2 · The Opportunity screen denies two label matches the portal itself proves

**Screen:** `case` (IT-OPP-001, Vite × Flavescenza Dorata) vs `window` (IT-WIN-0001, same crop × issue)

```
vals({view:'case',  caseId:'IT-OPP-001'}).cs
  → primaryLabel "VERIFICA ETICHETTA NECESSARIA", noPrimary true, matchCount 6
  → all six alternatives stamped "VERIFICA ETICHETTA NECESSARIA"
vals({view:'window',windowId:'IT-WIN-0001'}).wd.c
  → {primaryLabel:"EVURE PRO · MAVRIK SMART", label:"CORRISPONDENZA VERIFICATA SU ETICHETTA", matchCount:2}
AM.strengthFor('MAVRIK SMART','Grapevine','Flavescenza Dorata') → VERIFIED_LABEL_MATCH
AM.strengthFor('MAVRIK SMART', csCropK, csIssueK)              → NO_CONFIRMED_MATCH_CURRENT_READING
```

**Root cause, exactly:** `AM.lookups.OPP_ISSUE` is still keyed on the Portuguese source string —
`"FLAVESCENCIA DOURADA, VIA O VETOR SCAPHOIDEUS TITANUS"` — while the opportunity record now carries the Italian `"Flavescenza dorata, tramite il vettore Scaphoideus titanus"`. `csIssueOf()` misses, so the guard at `portale.html:~3316` (`csFold(w.issue) === csFold(csIssueK0)`) refuses the canonical window, and `csIssueK` falls back to the free-text prose. `strengthFor` then keys on prose and returns NO_CONFIRMED_MATCH for all six.

The code comment at `portale.html:~3280` predicted this failure verbatim ("*the screen would state the opposite of the audited label reading (§10)*") — it is now live because the record was translated and the lookup was not.

**Why it violates the law:** §10 inverted — the portal prints *no confirmed ADAMA position* over a match it can prove, on the one mandatory-control case in the package.
**Smallest fix:** in `client/italy-app-model.js`, add the Italian key to `OPP_ISSUE` (`"FLAVESCENZA DORATA, TRAMITE IL VETTORE SCAPHOIDEUS TITANUS" → "Flavescenza Dorata"`). Better: fold the record ISSUE through `AM.issueTerms` before comparing, so a translated record cannot break the join again. `AM.lookups.OPP_CROP` has the same Portuguese-only shape (`"VIDEIRA"`) and only survives because `rec.cropKeys[0]` covers it.

---

## BLOCKER · 3 · The printable Action Brief contradicts itself and names 4 unrelated products

**Screen:** `brief` (IT-OPP-001 / MARKETING) — the artefact with a *Download PDF* button.

```
br.sections["ADAMA PORTFOLIO RELEVANCE"] → 6 products, each with active substance,
   label crops, IRAC group, authorisation, expiry and a live fitosanitari.salute.gov.it link
br.sections["CLAIMS WE CAN SUPPORT"]     → ["No confirmed label match — communication must not name a product."]
```

Same page. Then, per product, against `AM.findProduct(n).links`:

| product | Grapevine × Flavescenza Dorata | its actual links |
|---|---|---|
| KLARTAN 20 EW | **none** | Olive / Olive Fruit Fly · NO_CONFIRMED_MATCH |
| KLARTAN SMART | **none** | Olive / Olive Fruit Fly · NO_CONFIRMED_MATCH |
| TAU AL 240 EW | **none** | *(no links at all)* |
| MAVRIK EW | **none** | Wheat / Cereal Aphids |
| MAVRIK SMART | VERIFIED_LABEL_MATCH | ✓ |
| EVURE PRO | VERIFIED_LABEL_MATCH | ✓ |

Four of six are presented as ADAMA portfolio relevance for a leafhopper-vectored phytoplasma on the strength of a shared active substance / a crop name in the label crop list. The label targets printed under them are all aphids.

Also on this document: it is **100% English** in Italian mode, the title reads `Flavescenza Dorata · Grapevine · Veneto` (the case screen says *Vite*), and label crops print as raw enums `ALFALFA, APPLE, BARLEY, GRAPEVINE, POTATO, SUGARBEET, TRITICALE, WHEAT_GENERIC`.

**Why it violates the law:** §13 (relationship from a name match), §11 (crop name translated inconsistently across two screens), §3.
**Smallest fix:** filter `br.facts.products` to links whose `strength === 'VERIFIED_LABEL_MATCH'` for this crop × issue and list the rest under a separate *da verificare* heading; localize the brief's section scaffolding; use `cl(crop)` for the title. Fixing BLOCKER 2 will also make the "claims" line correct.

---

## BLOCKER · 4 · "WHAT CHANGED · LAST 7 DAYS" shows 11; the real 7-day count is 1

**Screen:** `competitors` · props `t.cwWhatChanged`, `changed7`

```
t.cwWhatChanged → "COSA È CAMBIATO · ULTIMI 7 GIORNI"
changed7        → [{label:"A PAGAMENTO · 30G", n:11}]
competitorActivities |daysFromRef| <= 7  → 1
competitorActivities |daysFromRef| <= 30 → 11
```

The tile prints a 24px `+11` under a header that says *last 7 days*. `portale.html:~5789` self-documents it: *"The surviving tile names its own 30-day window because the section header still says 7 days."* The three `topMoves` cards beneath it are also the 30-day set.

**Why it violates the law:** a falsehood on screen — a different denominator than the label implies.
**Smallest fix:** change `t.cwWhatChanged` to `· ULTIMI 30 GIORNI` in both locales (the honest 7-day tile would read `+1`).

---

## MAJOR · 5 · The Radar's headline region panel ranks the wrong fact and 5 of 7 rows lead nowhere

**Screen:** `radar` · props `t.lblAttention`, `regionRank`

```
t.lblAttention → "DOVE SI CONCENTRA L’ATTENZIONE ADAMA?"  (subtitle: "clicca una regione per filtrare")
regionRank     → Puglia 6 · Veneto 6 · Emilia-Romagna 4 · Lombardia 3 · Piemonte 3 · Sicilia 3 · Toscana 2
                 (regionTiles.cases is assigned WIN_REGION[name] — the crop-window count, not opportunities)
click each → visibleCases: Puglia 0, Veneto 1, Emilia-Romagna 0, Lombardia 1, Piemonte 0, Sicilia 0, Toscana 0
```

The panel that leads the Opportunity Radar ranks regions by canonical crop-window count under a heading about where ADAMA's attention is concentrated. Five of seven rows open an empty radar. Separately, the radar's own `regionOptions` dropdown offers only `Friuli-Venezia Giulia` and `Lombardia` — Veneto, which the tile filters to successfully, is not in it.

**Why it violates the law:** §12/§13 — the number does not measure what the heading claims, and the affordance promises records that do not exist.
**Smallest fix:** rename the panel to name what it counts (*finestre colturali per regione*), or set `cases: o` (the opportunity count) and stop lighting tiles that filter to zero.

---

## MAJOR · 6 · 222 hardcoded English text nodes still in the Italian interface

**Screens:** 22 of 26 view blocks. Worst: science 51, signal 40, competitors 36, market 33, windows 21, event 18, cproduct 17, company 17, window 16, brief 15, theme 12.

Sample, all rendered verbatim with `lang: 'it'`: `PRODUCTS OBSERVED` · `CROPS OBSERVED` · `EVENT PARTICIPATION` · `FULL TIMELINE · N ITEMS` · `Visible activity in Italy · last movement X · N items in 30 days` · `MOST IMPORTANT FOR ADAMA NOW` · `STRATEGIC SCIENCE & PORTFOLIO GAPS` · `WHAT IS DRIVING THE MARKET` · `PRODUCTION · YIELD · STOCKS` · `Competitors confirmed` · `EVENT STORY · before → during → after` · `Never inferred from previous editions. ADAMA participation: internal data required.` · `PORTFOLIO CLOCK` · `PRODUCTS TO PREPARE · real Italy portfolio relationships only`.

**Why the suite misses it:** `I2` checks only the Future screen and `PT1`/`I5` walk `renderVals()` props — a literal inside the markup template never becomes a prop. `renderVals()` is the only surface the suite sees.

**Smallest fix:** add a check that extracts literal text nodes from the markup region (between `</style>` and the `data-dc-script` tag) and fails on any node ≥4 letters that is not a proper noun. That check would also have caught BLOCKER 1's converse.

---

## MAJOR · 7 · Hollow frames — titled panels with permanently nothing inside

Measured by rendering **every record** of each collection and keeping only props empty on 100% of them, then intersecting with the markup's own bindings:

| screen | prop | empty on | what the user sees |
|---|---|---|---|
| signal | `sg.status`, `sg.sourceTypeUpper` | 3/3 | status badge row with no status |
| signal | `sg.who` | 3/3 | *OBSERVED · FACTS FROM SOURCES* → empty |
| signal | `sg.whyWatch` | 3/3 | *WAITING FOR / NOT YET KNOWN* → empty |
| signal | `sg.trail` | 3/3 | *WHAT CHANGED · WHY NOW* → empty |
| signal | `sg.promotion` | 3/3 | *OPPORTUNITY STATUS* → empty |
| person | `pr.issues`, `pr.related`, `pr.signals`, `pr.history`, `pr.messages` | 60/60 | 5 empty sections |
| source | `sr.topics`, `sr.cases` | 31/31 | 2 empty sections |
| event | `evd.program` | 18/18 | *EVENT PROFILE* → empty |
| window | `wd.signals` | 29/29 | (has a `wd.noSignals` fallback — OK) |
| product | `pd.checkNeeded` | 166/166 | empty chip row |
| theme | `th.caseObjs`, `th.trendUpper` | 5/5 real themes | *RELATED CASE* column blank |
| windows | `wd.ladder` | 5/29 | *ADVANCE WARNING · WHO STARTS WHEN* → empty |

The Future Radar detail — the only drill-down the Future module has, and it has exactly 3 records — is 6 empty frames. The whole `sg.*` narrative family carries `state: NOT_APPROVED_FOR_DISPLAY` upstream and correctly renders nothing, but the frames were left standing.

**Note:** concurrent agents removed the Opportunity-detail and Market-Pulse hollow blocks between 15:45 and 16:15. Earlier in the session `case` had 11 (`cs.competitors`, `cs.actions`, `cs.tl`, `cs.deptChips`, `cs.evChips`, `cs.evBars`, `cs.relatedThemes`, plus `Future Radar · {{cs.origin}}d ago` rendering as literally "Future Radar · d ago"), and `market` had 10. Verify they stayed removed.

**Smallest fix:** delete the frame, or wrap each in the `sc-if has*` pattern the Market Pulse already uses (`mp.hasForces`).

---

## MAJOR · 8 · Person directory: 65 of 66 pages have an empty body; 1 of 66 is flagged a researcher

**Screen:** `sources → people → person`, driven through the real `visiblePeople[].go()` handlers.

```
66 person pages open, 0 crash
isResearcher === true on 1 of 66 — while collections.researchers holds 60 records
65 of 66 have issues[]=[] related[]=[] history[]=[] themeRecords[]=[]
e.g. IT-PER-001 "Cristina Marzachì": isResearcher false, role null, theme null, worksInScope 30
```

`PUBLICATIONS · TOPIC` is guarded by `sc-if pr.isResearcher`, so it is suppressed on 59 real researchers who do have publications in the model.

**Smallest fix:** derive `pr.isResearcher` from membership in `collections.researchers` (by id or ORCID/OpenAlex id), not from whatever field it reads now.

---

## MAJOR · 9 · Field Sales links a message to a crop window with a different issue

**Screen:** `field` · prop `fieldMessages[].targetLabel`

```
msg Maize / Diabrotica            → "FINESTRE COLTURALI · Piralide del mais · Friuli-Venezia Giulia"
msg Grapevine / Downy Mildew      → "FINESTRE COLTURALI · Flavescenza Dorata · Veneto"
msg Maize / Weed control          → "FINESTRE COLTURALI · Piralide del mais · Friuli-Venezia Giulia"
msg Sugar Beet / Weed control     → "FINESTRE COLTURALI · Cercosporiosi · Veneto"
msg Grapevine / Crop stage        → "FINESTRE COLTURALI · Flavescenza Dorata · Veneto"
```

`portale.html:~5347`: `winOf = m => cropWindows.records.find(x => x.crop === m.crop)` — first window with a matching **crop name**, ignoring the issue. 7 of 15 window-routed messages assert a window whose issue is unrelated to the message; a herbicide question routes to an insect window, a fungal disease routes to a phytoplasma window.

**Why it violates the law:** §13 — two records sharing a crop name is not a relationship, and `targetLabel` states the target issue as fact.
**Smallest fix:** require `x.crop === m.crop && x.issue === canonicalIssue(m.issue)`; when it misses, fall back to `T.fsFlowValidate` as the code already does for the no-window case.

---

## MAJOR · 10 · Event detail prints "0 Competitors confirmed" for an exhibitor list never consulted

**Screen:** `event`, all 18 records

```
17/18 → evd.confirmedCount = 0
 5/18 → exhibitorStatus "ELENCO ESPOSITORI NON CONSULTATO"
13/18 → exhibitorStatus ""   ← the "Exhibitor list" tile is a label with nothing under it
18/18 → evd.program "" · evd.story [] · evd.cases [] · evd.actCount 0 · evd.activities []
```

A 24px `0` under *Competitors confirmed*, beside a blank *Exhibitor list* tile, reads as "no competitor is exhibiting". The evidence only says the list was not read.

**Smallest fix:** print `—` plus the absence rule when `exhibitorStatus` is not `CONSULTATO`; delete or guard the four empty panels.

---

## MAJOR · 11 · Window detail prints an untranslated status reason, and `reasonL()` is bypassed

**Screen:** `window`, all 29 · prop `wd.statusReason`, `wd.why[].t`

```
IT-WIN-0001 → "FINESTRA CHIUSA · Reference date 2026-09-02 falls after END_DATE"
IT-WIN-0005 → "FINESTRA APERTA · Reference date falls inside the expected window · NOT an observation"
IT-WIN-0024 → "DATA DA CONFERMARE · No biological calendar entry for this issue"
IT-WIN-0029 → "PROSSIMO CICLO · The 2026 flowering window has passed; next relevant window is the 2027 campaign"
```

`REASON_IT` (`portale.html:~3820`) already holds all five translations and `reasonL()` applies them — but the `wd.why` builder (`~4266`) concatenates `wdR.statusReason` **raw**, while the calendar builder (`~4102`, `~4117`) correctly calls `reasonL()`.

**Smallest fix:** one call — `t: wst(wdR.status) + (wdR.statusReason ? ' · ' + reasonL(wdR.statusReason) : '')`.

---

## MAJOR · 12 · The competitor density panel never publishes its denominator

**Screen:** `competitors` · props `cropDensity`, `cropDensityNote`

```
cropDensityNote is COMPUTED at portale.html:~5744 and NEVER RETURNED from renderVals() → undefined
cropDensity[0] = {crop:"Maize", n:67, cos:5, pct:"100%", level:""}
CDENS.denominator 503 · unresolvedItems 320 · genericItems 51
```

The bar for Maize fills 100% of the track. The note that would explain it — *320 of 503 records name no crop and 51 carry only an advertiser umbrella word* — is dead code. The code comment claims "*the panel publishes its own denominator*"; it does not. `c.level` is `''`, leaving an empty span where the density grade used to be.

**Why it violates the law:** §8 — a full bar next to *Mais* reads as share of the universe when it is 67/503 with 371 records unattributable.
**Smallest fix:** add `cropDensityNote` to the returned props and bind it under the list; drop the empty `{{ c.level }}` span.

---

## MINOR · 13 · A stale Future link renders "UNDEFINED · UNDEFINED · UNDEFINED"

```
tryVals({view:'signal', signalId:'NO-SUCH'}) → ok, crumb "UNDEFINED · UNDEFINED · UNDEFINED"
```
`case`, `window`, `source`, `person`, `theme` all handle this correctly (*CASO NON TROVATO*, *FONTE NON TROVATA NEL REGISTRO*, …). `company`, `event` and `cproduct` render a blank page with no explanation (`crumb ""` / `" · "`). RT3 only checks the happy path.

**Smallest fix:** give `signal` the same `missingId` branch the case view has; add the ghost-id state to the RT3 matrix.

---

## MINOR · 14 · Italian left in English mode

```
vals({view:'signal', lang:'en'}).sg.factLoc       → "non ancora stabilito"
vals({view:'signal', lang:'en'}).sg.whyWatchState → "lettura interna, non pubblicabile"
```
Everything else flagged in EN mode is correctly untranslated per §11 (original grower quotes, source names such as *Ministero della Salute — Banca dati prodotti fitosanitari*, Latin binomials, GIRE region lists).

---

## MINOR · 15 · Raw Portuguese enum on the Crop Windows list

```
visibleWindows[].regulatory.actState → "JA_NO_ACERVO"
```
`ACT_STATE_LAB` (`portale.html:~3831`) already maps it to *già nell'archivio Sintonia* — the list binds the raw field instead of `actStateL(...)`.

---

## MINOR · 16 · The GIRE line mixes three denominators in one sentence

`"34 casi · 30 con sovrapposizione al portafoglio ADAMA · 91 erbicidi caricati"` — the 91 is `sciHerbTotal` (the ADAMA herbicide-label count), read as a subset of the 34 cases. Also `SHOW ALL {{n}} CASES · +{{n}} →` is still hardcoded English.

---

## Two things wrong with the suite itself

1. **`SCREENS` drives the Theme screen with a `scienceRecords` id.** `audit/checks.mjs:508` picks `scienceRecords.records[0].id` for `themeId`. With that id the screen renders `hasTheme:false`, `title:"Tema non trovato"`. So RT1, RT2, RT3, PT1, L3 and I5 all render a *not-found* page for `theme` and score it green — the Science drill-down is effectively untested. With a real id (`IT-THEME-001…005`) it populates. Use `collections.scienceThemes.records[0].id`.

2. **`PT1`'s marker list cannot see prose Portuguese.** Until ~16:00 the Opportunity breadcrumb read `PIRALIDE DEL MAIS · MAIS · FRIULI-VENEZIA GIULIA (SINAL) · VALE DO PÓ (ESCALA)` and PT1 reported *0 hits over 52 renders* — `sinal`, `escala`, `vale do`, `principal` are not in `PT_MARKERS`. Another agent fixed the data; the detector is still blind. A word-list detector will keep passing on the next one.

---

## Clean under test (verified, not assumed)

- **Field Sales does not touch core.** Snapshotted 10 screens and all 49 collections, drove `simulateInbound()` ×4 + `toggleComposer` + `setComposer` + `sendComposer` (5 messages injected, `fieldMessages` 18→23), re-rendered from a reset state: **0 screens changed, 0 collections changed, `AM.totals` unchanged.**
- **Demo scenario boundary holds.** Flipping `showScenarios` across 11 screens changes only `visibleCases`/`visibleCount`/`filteredCount` and the filter option lists. Every `kpi.*`, `nav`, `dataState*`, `windowKpi.*`, `compTotal`, `archiveCount`, `voices.*`, `port.*` number is byte-identical.
- **24 headline counts recompute exactly** from the records they claim to summarize: `italyReach 414`, `activities 503`, `companies 11`, `movements 11`, `movements7 1`, `undated 89`, `windows 29`, `windowOpen 6`, `matches 12`, `assessed 19`, `links 236`, `regulatoryLinks 219`, `records 88`, `researchers 60`, `people 15`, `peopleUnion 66`, `archive 774`, `events 18`, `news 8`, `channels 30`, `signals 3`, `scenarios 29`, `port.count 44`, `voices.count 17`. (`kpi.field 10` / `kpi.market 6` are source-group counts, correctly labelled — not message counts.)
- **Data State arithmetic reconciles:** 1580 real + 38 derived + 103 demo = 1721 total; 1721 + 623 not-summed + 774 index rows = 3118 = `AM.totals.total`, and the panel states the exclusion.
- **No agronomic state is invented in presentation.** Every `ACT NOW` / `WINDOW_OPEN` / `NEXT_CYCLE` string traces to upstream `CURRENT_STATUS`; the date arithmetic produces day counts and sort order only.
- **Absence wording is correct** wherever it appears: `"Non presente in questa lettura del registro"`, `"NESSUNA CORRISPONDENZA CONFERMATA NELLA LETTURA ATTUALE"` — 3 hits, all scoped to the reading. The problem is BLOCKER 2, where a *present* fact is reported as absent.