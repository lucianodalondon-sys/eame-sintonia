
### Markup edit still required (I cannot apply it)
`client/portale.html` line **1419**, inside the Portafoglio card:
```html
<span style="font-size:9.5px;color:#6E6663;padding-top:2px">{{ p.verified }} ✓ · {{ p.check }} △</span>
```
replace with
```html
<span style="font-size:9.5px;color:#6E6663;padding-top:2px">{{ p.verified }} ✓ · {{ p.related }} ○</span>
```
(drop `△`, gain `○` = RELATED_PORTFOLIO). If that lands, the legend clause in my note must change from `T.PSTATE.LABEL_CHECK_NEEDED` to `T.PSTATE.RELATED_PORTFOLIO` — one line in `audit/blocks/portfolio.js`, and I have k

### Markup edit still required (I cannot apply it)
`client/portale.html` line 66:
```
<sc-for list="{{ nav }}" as="n" hint-placeholder-count="6">
```
→ `hint-placeholder-count="10"`
Purely cosmetic — it is the number of skeleton rows drawn before data arrives, and the list has 10 items. Nothing factual depends on it. **No other markup change is needed for this block:** lines 66–73 and 76–83 bind `n.

### 5 · Markup edits still required (I could not make them)
Four spots in `C:\eame-sintonia\italia-portale\client\portale.html`. None are blocking — my props are safe strings so nothing breaks today — but each is a claim the data does not carry.
1. **1456–1459** — the featured card's `{{ t.lblProves }}` / `{{ t.lblNotProves }}` rows are unguarded. Wrap the pair in `<sc-if value="{{ v.hasProves }}">` and `<sc-if value="{{ v.hasNotProves }}">`. Same at **1486–1487
2. **1453** — the region chip `<span>{{ v.region }}</span>` is unguarded. Wrap in `<sc-if value="{{ v.hasRegion }}">`; it is `false` 17/17, so the chip disappears rather than printing "Regione non dichiarata" on every ca
3. **1430** — the hard-coded `ITALIA` badge next to the `VOCI DAL CAMPO` title. `COUNTRY_OF_FACT` is `NOT_KNOWN` on 15/17. This is the §9 `REACHED_IN_ITALY != TARGETED_ITALY` trap in literal form. Remove it or qualify it
4. **1431 / `italy-i18n.js:240`** — `subVoices` reads "ciò che dicono agricoltori, tecnici e canali italiani". `ROLE` is unknown 17/17, so we cannot say any of them is a grower or an advisor. Suggested: *"Commenti pubbli
Two i18n values are also now mislabelled: `vociFeatured` "IN EVIDENZA" would be more honestly "PIÙ RECENTI · SEGNALAZIONI IN PRIMA PERSONA", and `vociLatest` "ULTIME VOCI" is misleading over 1–13-year-old material — "ALT

### Markup edits still required (I could not make them)
**1. BLOCKING — no card exists for RELATED_PORTFOLIO.** It is 217 of 236 rows and the *only* class 19 products have. For **16 products** (APYZA 500 WG, APYZA WG, BLAISE ULTRA, DURAVIS, ELTIRA, GLIPHOGAN TOP CL PFNPE, HER
Insert between line 1368 (`</sc-if>` closing the check-needed card) and line 1369 (`<sc-if value="{{ pd.hasRejected }}">`):
```html
          <sc-if value="{{ pd.hasRelated }}" hint-placeholder-val="{{ false }}">
          <div style="border-radius:14px;border:1px solid rgba(203,197,195,0.10);background:#1C1817;padding:14px 16px;display:flex;flex-direction:column;gap:9px;border-top:3px solid #5CC3EE">
            <span style="font-size:9.5px;font-weight:700;letter-spacing:0.11em;color:#5CC3EE">{{ t.prodRelatedRel }}</span>
            <sc-for list="{{ pd.related }}" as="r" hint-placeholder-count="2"><span onClick="{{ r.go }}" style="display:flex;flex-direction:column;gap:1px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);curs
          </div>
          </sc-if>
```
New i18n key needed (`prodRelatedRel`), next to `prodCheckRel` at italy-i18n.js:245 / :529:
- it: `'PORTAFOGLIO CORRELATO · REGISTRO'`
- en: `'RELATED PORTFOLIO · REGISTRY'`
(`#5CC3EE` is `AM.STRENGTH.RELATED_PORTFOLIO.color`, not a hand-picked colour.)
**2. `{{ r.region }}` at markup 1360, 1366, 1372 should be renamed `{{ r.evidence }}`.** The prop name now lies about its content — it holds the evidence line, deliberately, because a label authorisation has no region. I
**3. Italian crop names missing from `T.CROPS` (italy-i18n.js:70): Barley, Potato, Sorghum, Triticale.** 52 of 236 relationship rows sit on these crops and would print an English crop name in the Italian portal. **0 visi

### Markup edits still required (I cannot edit `client/portale.html`)
I export the guards; four one-line wraps are needed in the FUTURE RADAR card, all inside `<sc-for list="{{ visibleSignals }}" as="s">`:
1. **line 1530** — wrap the category icon span in `<sc-if value="{{ s.hasCategory }}">…</sc-if>`. `CATEGORY_UI.unknown.iconAsset` is `''`, so `background:url()` is an empty request on 3/3 real cards.
2. **line 1532** — wrap the whole WHY WATCH div in `<sc-if value="{{ s.hasWhy }}">…</sc-if>`. `whyWatch` is `NOT_APPROVED_FOR_DISPLAY` on 3/3, so the label "PERCHÉ OSSERVARE" currently renders above nothing.
3. **line 1533** — wrap the whole WHO IS TALKING div in `<sc-if value="{{ s.hasWho }}">…</sc-if>`. Real records carry no who-breakdown; the label renders above an empty chip row.
4. **line 1535** — wrap `<span>Updated {{ s.lastObserved }}</span>` in `<sc-if value="{{ s.hasLastObserved }}">`, **and** replace the hard-coded English `Updated` with `{{ t.frUpdated }}` (the key exists: `Aggiornato` / 
Two further defects visible on my screen but owned elsewhere:
5. **line 1503** (header) — `{{ t.frSubA }} {{ kpi.signals }} monitored signals across Italy.` hard-codes an English tail that renders untranslated in Italian. `kpi.signals` comes from the `head` block.
6. **`nar` collision at assembly time** — `audit/blocks/head.js`, `signal.js`, `voci.js` and `competitor.js` each declare `const nar` in the same function scope; the splicer intermittently died on `Identifier 'nar' has a

### 4 · Markup edits still required (I could not make them)
1. **Line 756 — delete `· CROP SCALE {{ wd.scale }}`.** Until then it reads "NORMA AGRONOMICA ATTESA · CROP SCALE non noto". This is the one place where I had to leave a subcomponent alive that should be omitted.
2. **Lines 767-773 — delete the entire EARLY MARKET SIGNAL card** (`grid-column:span 4` div, including the duplicate `PREPARATION RECOMMENDATION / EARLY MARKET SIGNAL` two-cell grid at 771). It has no `sc-if`, so it curr
3. **Line 758** — `Known from label · {{ wd.c.matchCount }} registered matches` is hardcoded English and now reads "0 registered matches" on 17 of 29 windows. Suggest guarding it with `wd.noProducts` or moving the count 
4. **Line 800** — the empty state says "window driven by the annual cycle **and the case record**". The case record is no longer a source for this window; drop the clause.
5. **Lines 803-806 (WHAT IS FACTUAL · EXPECTED · UNKNOWN)** — hardcoded strings that no longer hold. `Crop × region relevance` under FACTUAL rested on the hectare fixture; `Monitoring season start` under EXPECTED rested 
6. **Line 759** — the caption "Business rule (demo configuration), not an agricultural fact" is correct and should stay, but it is hardcoded English in the Italian UI.
---

### Markup edits still required (I cannot apply them)
1. **portale.html:913** — `WHERE THIS SIGNAL WENT` is a false claim. Nothing routed anywhere; nothing mutates. Change the heading to an i18n key meaning *CONTESTO CORRELATO · il messaggio non è stato instradato* / *RELAT
2. **portale.html:921** — remove the `IN SOURCES → PEOPLE` link (`goTsr`, owned by the search block). TSRs are demo people; that link puts them on a core screen next to real ORCID researchers.
3. **portale.html:922** — drop `cursor:pointer` on the TSR row, or guard with `{{ t.hasProfile }}`. `t.go` is now a no-op.
4. **portale.html:869 / 867** — bind `{{ parsed.stateL }}` and `{{ parsed.signalL }}` instead of `{{ parsed.state }}` / `{{ parsed.signal }}`.
5. **italy-i18n.js `lblFieldSignalsAdded`** — "SEGNALI DI CAMPO AGGIUNTI ALLE OPPORTUNITÀ" asserts an addition that does not happen. Should read something like "OPPORTUNITÀ REALI CITATE DAI MESSAGGI DIMOSTRATIVI".
6. Hardcoded English I cannot reach from the block: **817** (intro paragraph), **855** (`WHATSAPP · FIELD MESSAGE (SIMULATED)` — the `(SIMULATED)` marker must survive translation), **871**, **878** `ORIGINAL FIELD MESSAG

### 6. Markup edits I could not make — please apply
I own no markup. These are the exact lines where a dead frame or a now-false caption survives.
| line | edit | why |
|---|---|---|
| **971** | delete the pill `◇ SINTONIA INTERPRETATION · NOT AN OBSERVED FACT` | the 40px hero value is now a measured count of ingested rows; calling it an interpretation is wrong (it under-claims, so it is safe to ship
| **976** | relabel `WHY SINTONIA READS IT THIS WAY` → `COSA ABBIAMO OSSERVATO` / `WHAT WE ACTUALLY OBSERVED` | the six tiles are now pure coverage counts (observations, piazze, product definitions, units, stopped series
| **991–995** | delete the legend row (`MARKET EFFECT`, `◇ interpretation · ○ forecast · — no data`, `colour follows market effect…`) | `mp.semLegend` is `[]`; there is no market-effect colour code left to explain |
| **1042–1058** | delete the PRODUCTION · YIELD · STOCKS card | |
| **1060–1077** | delete the SUPPLY & TRADE card | |
| **1079–1095** | delete the FARMER SENTIMENT card (header hardcodes `SECTOR LEVEL ONLY`) | |
| **1097–1110** | delete the INPUT COST PRESSURE card (header hardcodes `PARTIAL COVERAGE`, now false) | |
| **1114–1126** | delete the MARKET TRAJECTORY strip | |
| **1128–1146** | delete the MARKET OUTLOOK · NEXT 3–6 MONTHS section | |
| **1210** | delete the green `MARKET ENVIRONMENT` tile | it renders `{{ mp.temp }}` + `{{ mp.sem.label }} FOR THE GROWER`, which now reads "36 · OSSERVAZIONI INGERITE FOR THE GROWER". Nonsense in any wording I can suppl
| **1241** | relabel the button away from `{{ t.lblOpportunities }}` | the upstream record's own `forbiddenLabel` reads: do not call these an opportunity. Its `caseLabel` is `CONVERGENCIA QUE MERECE INVESTIGACAO`. I kept
| **1246–1263** | delete the WHAT CHANGED card and the commentary block under it | |
| **1270–1273** | delete the ITALY ECONOMIC CONTEXT list | |
| **1288–1300** | delete the `cpm.metrics` 3-column grid (keep intro + READ WITH CARE) | |
| **3402** | `mpReview: MK ? MK.LAST_REVIEW : ''` → `mpReview: AM ? AM.referenceDate : ''` | **This one ships broken today.** `MK.LAST_REVIEW` no longer exists in the stripped fixture, so line 1279 currently renders "Las

### 6 · MARKUP EDITS STILL REQUIRED — I could not apply these
Six of these are **mandatory**: without them the screen prints a dead fixture shape or an unqualified business claim. Line numbers are `client/portale.html`.
**MUST — a dead fixture shape is still in the literal text**
1. **649** — `<span …>~{{ r.ha }}k ha · {{ r.scale }}</span>` → `<span …>{{ r.issueL }}</span>`. Otherwise renders `~k ha · `. (`r.ha`/`r.scale` are null by design so it degrades visibly rather than lying.)
2. **704** — `~{{ r.ha }}k ha · {{ r.scale }} · {{ r.coverage }}` → `{{ r.issueL }} · {{ r.coverage }}`
3. **719** — `~{{ dw.ha }}k ha · {{ dw.scale }} crop relevance` → `{{ dw.dateStateL }} · {{ dw.coverage }}`
4. **680** — `MARKET <b style="color:{{ r.marketColor }}">{{ r.marketTemp }}</b> · FIELD {{ r.fieldCount }}` → `{{ r.sourceLine }}` (I define `r.sourceLine`; interim placeholders are `—` and `0`, neutral but pointless)
**MUST — an unqualified business claim**
5. **726** — `Commercial lead time {{ dw.leadDays }} days · preparation from {{ dw.prepFrom }}` → `{{ dw.prepLine }}`. "Commercial lead time" asserts channel behaviour that is not externally observable.
6. **723** — the green box: `background:#009845` → `background:{{ dw.stateBg }}` and the caption `COMMERCIAL STATE` → `{{ dw.stateCap }}`. Today a **closed** window still renders in bright ADAMA green under the words "co
**SHOULD — text that now describes lanes that no longer exist**
7. **591** — `{{ t.cwBucketNote }}` → `{{ calKpiNote }}`. `t.cwBucketNote` still says *"40 righe coltura × regione su 8 colture"* and describes the deleted 0–30/31–60/61–120 thresholds. I build `calKpiNote` bilingually f
8. **714** — `{{ t.cwFootNote }}` → `{{ calFootNote }}`, **plus** add `calFootNote,` to the props object at 3403. `t.cwFootNote` describes expected cycles, weed windows and observed markers — all removed. I define `calFo
9. **611–624 legend** — delete the `t.cwLegCycle`, `t.cwLegObs`, `t.cwLegWeed`, `t.cwLegMon` and `t.cwLegReg` entries. Those five lanes are never drawn now. Keep `cwLegIssue`, `cwLegApp`, `cwLegBiz`, `cwLegDept`.
10. **736** — the hardcoded English `Portfolio check needed — no confirmed ADAMA position for this crop × issue.` → `{{ dw.noProductsText }}`, which renders the rule-10 wording plus the absence rule.
11. **732** — the MARKET PULSE tile has no honest value left. Suggest: caption → `PORTFOLIO`, value → `{{ dw.matchLabel }}`, note → the absence rule. `dw.marketTemp` is `—` in the meantime.
12. **731** — the EXPECTED CYCLE TODAY tile is computed from the deleted stage table. `dw.expectedNow` now returns the *date state* (`NORMA AGRONOMICA ATTESA`), which reads acceptably under the existing `agronomic norm` 
**SHOULD — one state default**
13. **2386** — `calStart: 7` → `calStart: 4`. With 16 of 29 windows already closed, a viewport that starts at the reference month shows an empty timeline for more than half the rows. The fixture hid this by manufacturing
---

### Markup edits still required — I could not apply them
1. **portale.html 219 and 221** — wrap the category chip and the icon circle in `<sc-if value="{{ c.hasCategory }}" hint-placeholder-val="{{ true }}">…</sc-if>`. Until then an unclassified record renders an empty neutral
2. **portale.html 238** — the `sc-if c.hasField` branch (`{{ t.lblField }} {{ c.fieldCount }}`) is now permanently false. Delete it.
3. **portale.html 2388** — `openWindow(id) { this.go({ view: 'window', windowId: id }); }` is now a dead duplicate. **My block redefines `openWindow` later in the same class body, so JS keeps mine.** I did this deliberat
4. **A back control has no home.** `back()`, `goBack()` and `canGoBack()` exist and RT4 passes (`radar → product → back() → radar`, filters restored, empty stack returns `false`). But nothing binds them. The `search` blo

### Markup edits still required (I cannot apply them)
Everything below is cosmetic-or-worse breakage that survives because the literal text is hard-coded. **Nothing false renders without these**, but several boxes render empty or with a dangling separator.
1. **1633** — fPeriod `<option>`s are 7/30/60. On real data 7d = 1 record. Bind to `{{ compPeriodOptions }}` (I export it: any / 30 / 90 / 365).
2. **1650** — `t.cwWhatChanged` says "ULTIMI 7 GIORNI"; the tile is 30 days. Change the i18n string. `t.cwNewlyObs` ("osservato di recente da Sintonia") is also wrong — the number is the advertiser's own start date.
3. **1683** — delete `<span ...>{{ c.level }}</span>` (now always empty).
4. **1684** — replace the static density caption with `{{ cropDensityNote }}` (I export it: "320 record su 503 non nominano alcuna coltura e 51 portano solo una parola ombrello…").
5. **1693** — replace `{{ m.cos }} competitors communicating · {{ m.acts }} items in 30d · ADAMA {{ m.prods }} matches · market <b>{{ m.market }}</b>` with `{{ m.cos }} aziende osservate · {{ m.acts }} elementi nel corpu
6. **1722** — wrap the big `{{ a.product }}` in `<sc-if value="{{ a.hasProduct }}">`; it is empty on 401/503.
7. **1723 / 1725 / 1726** — delete the `a.isVideo`, `a.isPeople` and `a.isEvent` blocks (guards are permanently false; deletion is cleanup).
8. **1724** — change "Organic post · {{ a.platform }} · no image captured" to "Video organico · …".
9. **1727** — add a small `TESTO PUBBLICO ORIGINALE` label above `{{ a.headline }}`; it is now a verbatim advertiser quote, not a Sintonia headline.
10. **1728** — wrap `{{ a.cropL }}` in `<sc-if value="{{ a.hasCrop }}">` and `{{ a.issueL }}` in `<sc-if value="{{ a.hasIssue }}">`, otherwise 320 and 405 cards render empty grey pills. Rename the `{{ a.newly }}` badge (
11. **1730–1732** — **delete the two-tile grid** (COMMUNICATION TIMING + ADAMA RESPONSE), or gate it on `{{ a.hasWindow }}`. Both labels are hard-coded and today both tiles read NON VALUTABILE on every card.
12. **1734** — delete `MARKET PULSE · <b>{{ a.marketTemp }}</b>`.
13. **1747 + 1748** — `matrixCols` must come from my block (see tail edits). The `repeat(6,1fr)` grid is fine — I cap at 6 columns and name the rest in `{{ matrixNote }}` (also needs a slot at 1746).
14. **1753–1759** — **delete the whole COMMUNICATION LEAD TIME card**, including the hard-coded ADAMA "Internal review · not connected" row (which also implies a private-data gap §1 says should not exist) and the caption
15. **1787 + 1788** — rewrite both `grid-template-columns:1.4fr 60px 60px 1.6fr 1.4fr 110px` to 3 columns; delete `{{ r.paid }}`, the `{{ t.lblPortfolio }}` header and `{{ r.adamaLabel }}`. Keep "CONTEXT →" — `r.go` now 
16. **1799** — "Visible activity in Italy · last movement {{ co.last }} · {{ co.recent30 }} items in 30 days" is hard-coded English and must tolerate `co.recent30 === '—'` (5 companies have no dated record).
17. **1800** — `repeat(6,90px)` → `repeat(2,90px)`.
18. **1804** — add `{{ co.productsNote }}` ("NESSUN PRODOTTO PROVATO IN QUESTA LETTURA"); Bayer has 86 items and 0 proven products, and an empty box reads as "no products".
19. **1806** — delete the OBSERVED CONTENT THEMES card. **1809** — delete RELATED OPPORTUNITY CASES.
20. **Event detail** — delete the EVENT STORY card, the RELATED ACTIVITY section, and the `{{ evd.cases }}` card.
21. **cproduct detail** — delete the "People mentions" tile and change `repeat(4,120px)` → `repeat(3,120px)`; delete the `{{ cp.cases }}` card.
**Tail edits (search block, 3441–3443 — not mine to write):**
`compTotal: D.ACTIVITIES.length` → `compTotal,` · `whatChanged: D.WHAT_CHANGED` → drop the prop · `matrixCols: D.CROP_COLS` → `matrixCols,` · `compCropOptions: opts(...)` → `compCropOptions,` · `compIssueOptions: opts(..

### 5 · Markup edits still required (I cannot apply them)
1. **`portale.html:264`** — delete `<span style="color:#8F8886;font-size:10px;font-variant-numeric:tabular-nums">+{{ r.signals }} signals</span>`. Until it goes, every rank row renders the literal English "+0 signals". I
2. **`portale.html:122`** — raise `hint-placeholder-count` on the `dataState` `sc-for` from `6` to `45`.
3. **After `portale.html:135`** — add one footnote span bound to `{{ dataStateTotals.note }}`. Without it the columns visibly fail to add up, because the 15 excluded rows keep their numbers on screen.
4. **`portale.html:1729‑1733`** (competitor card) — delete the "COMMUNICATION TIMING", "ADAMA RESPONSE" and "MARKET PULSE" boxes. I fill them with honest UNKNOWNs (`NON VALUTATO`, the absence rule, `DATI NON SUFFICIENTI`
5. **`portale.html:196`** — `hint-placeholder-count="8"` still correct (8 cards kept).

### Markup edits still required (I cannot apply them)
1. **line 315 — DELETE the ORIGIN tile.** It hardcodes `Future Radar · {{ cs.origin }}d ago`; with `origin` empty it renders `Future Radar · d ago`. There is no honest value for that sentence.
2. **line 299** — add an inner `<sc-if value="{{ cs.hasCase }}">` so an unresolved id shows an empty state (`cs.missingId` is exposed) instead of a skeleton.
3. **lines 320, 323** — remove the `deptChips` / `evChips` rows and the `{{ t.lblWhoLooks }}` / `{{ t.lblSupported }}` headings; the arrays are permanently empty.
4. **lines 419-423** — the `FORZA DELL'EVIDENZA` panel now has an empty `sc-for` above `{{ cs.source }}`. Drop the `sc-for`, keep the line.
5. **lines 441-452 (Competitor activity), 454-465 (Action map), 470-476 (Executive timeline), 402-408 (Field Signals)** — four panels whose headings and English sub-labels now sit over empty grids. Remove them.
6. **line 314** — `{{ cs.evidenceTotal }} {{ t.lblConnObs }}` reads "4 osservazioni collegate"; they are evidence statements, not observations. Reword `lblConnObs`.
7. **line 352 / 361-362** — the masked window bar draws 0% for IT-OPP-003. Guard it with a new `cs.hasWindow`-style `sc-if`; I expose `cs.windowLine` carrying `nessuna finestra canonica collegata`.
8. **English hardcoded in markup, still visible:** line 378 `Label context · … · dose and interval per label record`; line 396-398 `No confirmed ADAMA label position matched…` (add `{{ cs.absenceRule }}`, which I now exp
9. **line 305** — a `DEMO SCENARIO` badge bound to `cs.isScenario` when scenario mode is on.
10. **line 2869 (windows block, not markup)** — `cs.goWindow = () => this.openWindow(winFor(cs0.id).id)` overwrites the honest link I set (`openWindow(csWinRec.windowId)`) and routes to a demo window. And `openWindow` re

### MARKUP EDITS STILL REQUIRED (I cannot apply them)
These render as empty text or a dangling separator until applied. In priority order:
1. **line 2064 + 2071** — delete the 5th column of the RECENT RESEARCH table: header `<span>RELATED CASE</span>`, the grid template's 5th track (`minmax(72px,1.4fr)` in **both** the header div and the row div), and the w
2. **line 2064 + 2069** — delete the 4th column (`BUSINESS RELEVANCE` header + `{{ r.bizRel }}` span + its track). If you'd rather keep the column, I already ship `r.materialRoleL` (88/88 real, 6 controlled values) — ren
3. **line 2168** — same deletion in the theme detail: `<span onClick="{{ r.openCase }}">{{ r.related.issueL }} · {{ r.related.region }}</span>` and its `minmax(0,150px)` track.
4. **line 1996 and 2054** — delete `<span …>{{ TH.opportunityLine }}</span>` and `CURRENT COMMERCIAL OPPORTUNITY · {{ TH.opportunityLine }}`.
5. **line 2133** — delete the `{{ t.lblRelatedOpps }}` / `{{ sciImpact.opportunityLine }}` tile in the impact drawer.
6. **line 2162** — delete the whole `{{ th.trend }}` / "Publication movement" tile. **line 2163** — delete the `{{ th.caseCount }}` / `{{ t.lblConnOpps }}` tile.
7. **line 2176-2177** — delete the CONNECTED OPPORTUNITY CASES card (renders as a header over nothing).
8. **line 1952** — `SCIENCE → BUSINESS` strip label and `{{ sciTotal }} classified themes · counts reconcile`: rename to something like `SCIENZA · TEMI MONITORATI` and `{{ sciTotal }} temi bibliometrici`. The counts do r
9. **line 1969** — the `MOST IMPORTANT FOR ADAMA NOW` strip header now sits above an empty grid: delete the strip.
10. **line 2055-2056** — the STRATEGIC SCIENCE card is now header + footer only: delete the card.
11. **line 2062** — add next to `RECENT RESEARCH · {{ kpi.records }} RECORDS` the depth caveat. `{{ sciActivityNote }}` carries the sentence but renders further up the page (line 1976).
12. **line 2083** — `INSTITUTIONS · {{ instCount }}` needs the caption that these are first-author affiliations, not study locations, and that two of the six are not Italian. `{{ i.type }}` already says the first half pe
13. **line 2179** — MONITOR NEXT promises "movement into Future Radar signals". No movement is measurable; rewrite without it. `{{ th.instCount }}` now means institutions in the OpenAlex theme profile (11–12), a differen
14. **line 1987** — `{{ t.lblAdamaExposure }} · {{ TH.moaNote }}`: the note now explains that overlap is botanical genus, not mechanism. Reads correctly as-is, but "ADAMA EXPOSURE" is a strong label for it.

### 5 · Markup edits still required — I could not make these
**REQUIRED (visible defect until applied):**
1. **`portale.html:2263`** — `{{ n.date }} 2026 · real` on every news card. Two of the eight items are from 2021 and 2022 and one has no date; the template prints `"2021-02-24 2026"`. Change to `{{ n.date }}` and delete 
2. **`portale.html:2195`** — DELETE the whole region `<select>`. Its filter clause is gone, so it is now an inert control that appears to do something. Also drop `aRegion` / `setARegion` from `audit/blocks/search.js:243`
3. **`portale.html:2210`** and **`2312`** — `{{ a.cropL }} · {{ a.region }}` → `{{ a.subtitle }}`. I export `subtitle` already. **Until this lands, `archDeco` puts the ISSUE label into the `region` slot** so the subtitle
4. **`portale.html:2348`** — the hardcoded note *"Demo profile — a neutral sensor profile, not a real individual"* is now **false**: these are 66 real, publicly named people. Replace with the affiliation caveat (`AM.coll
5. **`portale.html:2288`** — `{{ s.related }} cases` in the sources table. The number is now archive rows joined on `sourceId` (Meta 414, OpenAlex 88, AgriFood 77, YouTube 106, GIRE 34) — not cases. Change the literal to
**STRONGLY RECOMMENDED:**
6. **`portale.html:2194`** — crop `<select>` must bind `{{ archiveCropOptions }}` instead of `{{ cropOptions }}`, and `audit/blocks/search.js:283` must export it (I declare it). `cropOptions` is measured **4 entries** bu
7. **`portale.html:2196`** — company `<select>` may keep `{{ companies }}`: the competitor block now publishes all **11** real companies, so nothing is unreachable. `archiveCompanyOptions` is declared as a fallback if th
8. **`portale.html:2282` / `2298`** — delete the "WHAT SINTONIA OBTAINS" column and the source-detail line under it. Empty on 31/31.
9. **`portale.html:2283` / `2301`** — rename the column header **COVERAGE → GEOGRAFIA**. `'IT'` means the source is Italian, not that it covers all Italian crops.
10. **`portale.html:2223`** — render only non-empty tags. Crop is empty on 416/774 and issue on 534/774, so the drawer often shows three empty pills.
11. **`portale.html:2265` / `2266`** — delete the news region chip and the "ORIGINATING SOURCE" half of that footer grid; both are permanently blank. Move the "EDITORIAL TYPE" badge up onto the card body — it is the one 
12. **`portale.html:2251` / `2323`** — drop the Platform and Region cells from the person card and header, and relabel "Crops"/"Issues" as "Tema monitorato" / "Opere nel recorte". Until then those four cells read `—`.
13. **`portale.html:2255` / `2332` / `2335`** — the "N opportunities · N signals" line and the two header KPI tiles read `—`. Delete them.
14. **`portale.html:2325`** — the header tile labelled `t.lblLastObserved` ("Last observed") now shows `LAST_ACTIVITY`, which is the date of the last **indexed work in the monitored theme**, not an observation of that pe
15. **`italy-i18n.js:78` and `:363`** — add `ARCHTYPES` entries for the 8 real kinds (`COMPETITOR, SCIENCE, MARKET, RESISTANCE, WINDOW, EVENT, VOICE, NEWS`). `en.ARCHTYPES` is measured **`{}`** and `it.ARCHTYPES` holds o
16. **`portale.html:480`** — "VIEW IN ARCHIVE →" from an opportunity detail lands on a **one-row** list (`legacyCaseId` is 29/774, exactly one row per `IT-OPP-001..029`), and that row is not an observed capture: its `sou
---

### 6 · Markup edits still required (I could not edit the markup)
1. **`portale.html:2358`** — hardcoded English, and now factually wrong:
   `{{ searchTotal }} connected items across opportunities, signals, products, science, people, archive and sources.`
   *archive* no longer exists as a group and five groups are missing (windows, voices, market, news, events). Replace both strings with i18n keys (`t.searchResultsFor`, `t.searchTotalNote`) and add them to `italy-i18n.js
2. **`portale.html:147`** — the notification bell's unread dot is a hardcoded green circle. With `notifs: []` it now permanently claims unread notifications that do not exist. Delete the `<span>`.
3. **`portale.html:1279`** — `{{ t.cannotProveList }} Last source review {{ mpReview }}.` now renders "Last source review ." Remove the sentence (it is also untranslated English).
4. *Optional:* `portale.html:2360` `hint-placeholder-count="6"` → `8`; up to 12 groups can now appear.
I did **not** need the `g.empty` node: the overflow row is delivered as a seventh item in `g.items`, so the card geometry, the border-top accent, the dotted separators and the grid are untouched. `MK1` (every markup-boun