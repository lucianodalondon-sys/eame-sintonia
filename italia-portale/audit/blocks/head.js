  renderVals() {
    const AM = this.M();
    const APP0 = AM ? AM.collections : null;
    const A_ARCHIVE0 = APP0 ? APP0.archive.records : [];
    const A_SIGREAL = APP0 ? APP0.futureSignals.records : [];
    const A_SCEN = APP0 && APP0.futureScenarios ? APP0.futureScenarios.records : [];

    /* §3 · ITALY_APP_MODEL is now the only place this block takes a fact from.
       ITALY_DEMO survives as `D` because eleven later blocks still declare against
       it; inside THIS block it is read exactly twice, both times for pure layout
       (month abbreviations, the 4x5 region grid), and both reads are marked. */
    const D = this.D(); if (!D) return {};
    const s = this.state;
    const T = (window.SINTONIA_I18N && window.SINTONIA_I18N[s.lang]) || (window.SINTONIA_I18N && window.SINTONIA_I18N.it) || {};
    if (D.setMonths && T.months) D.setMonths(T.months);
    /* Crop and issue display names. The raw value stays the filter key, so filtering,
       window matching and cross-tool lookups are untouched. A name the map does not
       carry passes through verbatim — that is how Latin binomials (Zea mays, Olea
       europaea), which are 100% of the crop strings on the 503 real competitor
       records, survive untranslated as §11 requires. */
    const cl = (k) => (T.CROPS && T.CROPS[k]) || k;
    /* Canonical codes are language-independent; only the label is localized. */
    const wst = (k) => (T.WSTATUS && T.WSTATUS[k]) || String(k || '').replace(/_/g, ' ');
    const dst = (k) => (T.DSTATE && T.DSTATE[k]) || String(k || '').replace(/_/g, ' ');
    const obs = (k) => (T.OBSCLASS && T.OBSCLASS[k]) || String(k || '').replace(/_/g, ' ');
    const wline = (v) => { if (!v) return ''; if (v === 'DATE_TO_CONFIRM' || v === 'WINDOW_CLOSED') return wst(v === 'DATE_TO_CONFIRM' ? 'DATE_UNKNOWN' : v); const p = String(v).split('|'); return p.length === 2 ? p[0] + ' ' + (p[1] === 'daysRemaining' ? T.wDaysRemaining : T.wDaysToOpen) : v; };
    const arcT = (k) => (T.ARCHTYPES && T.ARCHTYPES[k]) || k;
    const il = (k) => (T.ISSUES && T.ISSUES[k]) || k;
    const srcL = (k) => (T.SRCTYPES && T.SRCTYPES[k]) || k;
    const fst = (k) => (T.FSTATUS && T.FSTATUS[k]) || k;
    const evc = (k) => (T.EVCHIP && T.EVCHIP[k]) || k;
    const WL = (o) => Object.assign({}, o, { cropL: cl(o.crop), issueL: il(o.issue) });
    /* Label maps for values generated in logic. Crop names, pathogens, product names, regions and
       source titles are NOT translated — they stay in the form the source publishes them. */
    const IT_LAB = {
      'ACT NOW': 'AGIRE ORA', 'ACTION WINDOW OPENING': 'FINESTRA IN APERTURA', 'PREPARE': 'PREPARARE',
      'WATCH': 'OSSERVARE', 'VALIDATE': 'VALIDARE',
      'Pest Control': 'Controllo Insetti', 'Disease Control': 'Controllo Malattie', 'Weed Control': 'Controllo Infestanti',
      'Strong': 'Forte', 'Good': 'Buona', 'Building': 'In costruzione',
      'MARKET DEVELOPMENT': 'SVILUPPO MERCATO', 'SALES / RTV': 'VENDITE / RTV', 'TECHNICAL / SCIENCE': 'TECNICO / SCIENZA',
      'REGULATORY / PORTFOLIO': 'REGOLATORIO / PORTAFOGLIO', 'MARKETING': 'MARKETING', 'SUPPLY': 'SUPPLY CHAIN',
      'FIELD SALES': 'RETE DI CAMPO',
      'FIELD': 'CAMPO', 'SCIENCE': 'SCIENZA', 'OFFICIAL': 'UFFICIALE', 'PEOPLE': 'PERSONE', 'MARKET': 'MERCATO',
      'Check needed': 'Verifica necessaria', 'single match': 'corrispondenza unica',
      'NEW SIGNAL': 'NUOVO SEGNALE', 'GAINING ATTENTION': 'ATTENZIONE CRESCENTE', 'MULTIPLE SIGNALS': 'SEGNALI MULTIPLI',
      'WATCH CLOSELY': 'OSSERVARE DA VICINO', 'NEEDS VALIDATION': 'DA VALIDARE', 'TIMING APPROACHING': 'TEMPISTICA VICINA',
      'ALL': 'TUTTI', 'Science': 'Scienza', 'Researchers': 'Ricercatori', 'Field network': 'Rete di campo',
      'Regulatory': 'Regolatorio', 'Technical media': 'Media tecnici', 'Producer organizations': 'Organizzazioni di produttori',
      'Competitor movement': 'Movimenti concorrenza'
    };
    const L = (v) => (s.lang === 'it' && IT_LAB[v]) ? IT_LAB[v] : v;
    const LDAYS = (n) => s.lang === 'it' ? n + ' giorni rimanenti' : n + ' days remaining';
    const LAGO = (str) => { if (s.lang !== 'it' || !str) return str; return String(str).replace(/^today$/, 'oggi').replace(/(\d+)d ago/, '$1g fa').replace(/(\d+)mo ago/, '$1 mesi fa').replace(/(\d+) min ago/, '$1 min fa'); };
    const LMORE = (n) => s.lang === 'it' ? '+ ' + n + ' altri' : '+ ' + n + ' more';
    const ITX = s.lang !== 'en';
    const EITHER = (it, en) => ITX ? it : en;
    /* §THE NARRATIVE RULE · never print n.it unless the upstream approved it. */
    const narOf = (n) => (n && AM && n.state === AM.KNOWLEDGE.CLEAR) ? (s.lang === 'en' ? (n.en || n.it) : (n.it || n.en)) : null;
    /* One clock. Ages are measured against AM.REF (2026-09-02), never new Date(). */
    const daysAgo = (iso) => { const d = AM ? AM.daysFrom(iso) : null; return d === null ? null : -d; };
    const agoLbl = (n) => n === null ? null : n <= 0 ? EITHER('oggi', 'today') : ITX ? n + 'g fa' : n + 'd ago';
    this._L = L; this._LDAYS = LDAYS; this._LAGO = LAGO; this._LMORE = LMORE;

    /* ════════ §1 · THE RADAR FEED ════════════════════════════════════════════
       Was: ITALY_DEMO.CASES.map(decorate) — 29 hand-authored fixture cases whose issue,
       region, evidence bars, competitor rows, timeline, action map and product
       links were all authored in italy-demo-data.js. The real feed is
       AM.collections.opportunities: 3 records.

       Measured on those 3, and every one of these facts shapes the code below:
       · LEGACY_CASE_ID is IT-HERO-001/002/003 and matches none of the 29 canonical
         windows (which carry IT-OPP-001..029), so canonicalWindow is null 3/3 —
         no start date, no end date, no CURRENT_STATUS, no progress.
       · whatIsHappening / whyItMatters / currentEvidence / whatWeKnow /
         whatWeDoNotKnow / interpretations are NOT_APPROVED_FOR_DISPLAY 3/3: the
         upstream prose is Portuguese working notes with no IT/EN variant.
       · WHAT_IS_HAPPENING is an OBJECT the model has not projected yet, and it is
         the only real date on the record: OBSERVATION_DATE + FRESHNESS_DAYS +
         DOCUMENT present 3/3 (17d, 18d, 6d). Read from record.raw until the model
         exposes it — noted as model debt, not invented here.
       · ADAMA_PRODUCTS is filled on 1 of 3 (6 names); the other two are empty.
       · CROP / ISSUE / REGION are the upstream's Portuguese strings ("Videira",
         "Milho grão", "Veneto (principal) + Lombardia"). They are facts, so they
         render verbatim. Inventing an Italian translation here would be the
         presentation layer authoring agronomy. */
    const REAL_OPPS = APP0 ? APP0.opportunities.records : [];
    /* The upstream declares WINDOW.APPLICATION per record. It is NOT CURRENT_STATUS,
       so §7 forbids promoting it into the canonical WINDOW_OPEN / NEXT_CYCLE
       vocabulary: it is shown verbatim, localized only as an enum label, and it
       never enters `status` (which stays null) nor any status count. */
    const APPWIN_LAB = {
      CLOSED_FOR_2026: ['APPLICAZIONE CHIUSA PER IL 2026', 'APPLICATION CLOSED FOR 2026'],
      OPEN_BUT_NARROW: ['APPLICAZIONE APERTA MA STRETTA', 'APPLICATION OPEN BUT NARROW'],
      NOT_APPLICABLE: ['NON APPLICABILE', 'NOT APPLICABLE']
    };
    const appwin = (k) => { if (!k) return null; if (T.APPWIN && T.APPWIN[k]) return T.APPWIN[k]; const p = APPWIN_LAB[k]; return p ? EITHER(p[0], p[1]) : String(k).replace(/_/g, ' '); };
    /* §4 · the pest/disease/weed tile is decorate()'s job: it calls
       AM.categoryOf(issueType) itself, so this block passes the FACT (issueType) and
       never a colour. Measured: 2 of the 3 real records resolve to the neutral token
       (ISSUE_TYPE 'FITOPLASMA', and the literal 'NAO SEI'), whose label is empty on
       purpose — the sentinel must never print as a category name.

       §11 · The upstream writes CROP, ISSUE and REGION in its own working Portuguese
       ("Videira", "Milho grão", "Flavescência dourada, via o vetor Scaphoideus
       titanus", "Veneto (principal) + Lombardia"). The model resolves all three into
       controlled keys — cropKeys, issueKey, regionKeys — so nothing is guessed here.
       Coverage measured: cropKeys 2/3, issueKey 2/3, regionKeys 2/3. The third record
       is IT-OPP-003, whose "crop" is the ADAMA Italy portfolio itself and whose region
       is the whole country; it has no keys because it genuinely has none, and it is
       rendered in the upstream's own words rather than forced into a vocabulary it
       does not belong to. The upstream strings survive as cropRaw / issueRaw. */
    const mkOpp = (o, i) => {
      const w = o.canonicalWindow || null;
      const fresh = (typeof o.freshnessDays === 'number') ? o.freshnessDays : daysAgo(o.observationDate);
      const prods = o.adamaProducts || [];
      /* §10 · an empty ADAMA_PRODUCTS is NOT "ADAMA has no product". It is the audit's
         NO_CONFIRMED_MATCH_CURRENT_READING, and decorate() prints the absence rule
         underneath it. Measured: 6 named products on IT-OPP-001 (2 VERIFIED_LABEL_MATCH
         in the model's own productLinks), 0 on the other two. */
      const pState = prods.length ? 'LABEL_CHECK_NEEDED' : 'NO_CONFIRMED_MATCH_CURRENT_READING';
      return {
        id: o.id, n: i, hero: i === 0,
        crop: (o.cropKeys || [])[0] || o.crop, issue: o.issueKey || o.issue,
        cropRaw: o.crop, issueRaw: o.issue, cropKeys: o.cropKeys || [],
        /* regionKeys is the canonical list the upstream free text resolves to
           (["Lombardia","Veneto"] · ["Friuli-Venezia Giulia"] · []). The label keeps
           the source's own sentence — it says which region is primary and which is
           scale, and the presentation layer may not throw that away — while the keys
           are what the region filter and the region map match on. */
        region: (o.regionKeys || [])[0] || o.region, regionKeys: o.regionKeys || [],
        regionLabel: o.region,
        issueType: o.issueType, cat: (o.ui && o.ui.key) || 'unknown',
        latin: '', /* no upstream taxonomic field; §11 forbids parsing one out of the ISSUE string */
        /* §7 · The upstream declares WINDOW.APPLICATION per record, projected by the
           model as windowApplication (CLOSED_FOR_2026 · OPEN_BUT_NARROW ·
           NOT_APPLICABLE). It is NOT CURRENT_STATUS, so it may not be promoted into
           the canonical WINDOW_OPEN / NEXT_CYCLE vocabulary: it is shown verbatim as a
           localized enum, and `status` stays null so it can never reach a status count.
           Measured: canonicalWindow is null 3/3, because the model joins opportunities
           to windows on LEGACY_CASE_ID (IT-HERO-00x) and no window carries one. So
           there is no start date, no end date and no progress on any of the three. */
        canonical: w, windowId: o.windowId || null, status: null,
        applicationWindow: o.windowApplication || null, applicationWindowL: appwin(o.windowApplication),
        monitoringWindow: o.windowMonitoring || null, nextCycleWindow: o.windowNextCycle || null,
        dateState: w ? w.dateState : null, dateConfidence: w ? w.dateConfidence : null,
        statusReason: w ? w.statusReason : null, lastValidated: w ? w.lastValidated : null,
        windowStart: null, windowEnd: null, windowOpen: false, hasDates: false,
        ws: 0, we: 0, daysLeft: null, daysToOpen: null, progress: 0, windowLine: '',
        /* observedStage is real on 1 of 3 ("maturazione lattea a fisiologica — BBCH
           65-75" on IT-OPP-002); the other two read NOT_OBSERVED rather than blank. */
        stage: o.observedStage || 'NOT_OBSERVED', signal: 'NOT_OBSERVED',
        /* no `st` is supplied on purpose: decorate() derives the pill tint from the
           upstream status, and a null status must sort LAST (rank 9), not first. */
        /* the only real recency on the record is the age of its source document —
           17d, 18d and 6d, measured 3/3. It is labelled as a document age, not as an
           "updated" timestamp, because nothing here records an internal edit. */
        updated: fresh === null ? 999 : fresh, observationDate: o.observationDate || null,
        sourceDocument: o.happeningDocument || null, sourceIds: o.sourceIds || [],
        updatedLabel: fresh === null ? '' : EITHER('documento di ' + fresh + ' giorni fa', 'document ' + fresh + 'd old'),
        when: agoLbl(fresh === null ? null : fresh), ago: agoLbl(fresh === null ? null : fresh),
        remainingLabel: '',
        /* the model's own productLinks carry the audited verdict per product; the raw
           name list travels beside it so decorate() and the product filter agree. */
        products: prods, adamaProducts: prods, productLinks: o.productLinks || [],
        primary: null, primaryObj: null,
        primaryAi: (o.adamaActiveSubstance || []).join(' · ') || null,
        portfolioState: pState, primaryDowngraded: !prods.length, primaryRejected: false,
        verifiedCount: o.verifiedProductCount || 0,
        /* decorate() promotes the strongest verdict to `primary`; the rest of the
           upstream ADAMA_PRODUCTS list is the "+ N altri" count. */
        matchCount: prods.length, moreMatches: Math.max(0, prods.length - 1), alternatives: [],
        /* §2 · every one of these was fixture-authored — hand-typed evidence bars, a
           seeded-PRNG competitor list, an arithmetic timeline, a department action map
           and a 2-4 region adjacency claim. They are declared empty so the later blocks
           keep compiling and their sc-if guards hide the panels. */
        evidence: {}, evidenceTotal: 0, evidenceLabel: null, know: [], watch: [],
        timeline: [], tl: [], adjacent: [], competitors: [], actions: [], departments: [],
        realObs: null, source: null, happening: narOf(o.whatIsHappening), why: narOf(o.whyItMatters),
        label: null, origin: null, fieldCount: 0,
        caseLabel: o.caseLabel || null, forbiddenLabel: o.forbiddenLabel || null,
        provenance: o.provenance, isScenario: false
      };
    };
    const A_OPPREAL = REAL_OPPS.map(mkOpp);
    const realIds = A_OPPREAL.reduce((a, c) => { a[c.id] = 1; return a; }, {});
    /* §5 · the 29 legacy presentation cases, behind an explicit default-OFF switch.
       3 of the 29 reuse the ids of the real records (IT-OPP-001/002/003), so they are
       dropped rather than shadowing them: 26 scenarios join 3 real records. */
    const A_OPPSCEN = (s.showScenarios && APP0 && APP0.opportunityScenarios)
      ? /*@EXPLICIT_DEMO legacy presentation cases, default off (state.showScenarios), read through the model's DEMO_SCENARIO collection; they feed no count on this screen*/ APP0.opportunityScenarios.records.filter((c) => !realIds[c.id])
      : [];
    const CASES = A_OPPREAL.concat(A_OPPSCEN).map(c => this.decorate(c));

    /* §19 · Live switch. The reload existed only because date strings were built once at
       module load; decorate() now re-derives them per render, so state alone is enough. */
    const setLang = (l) => {
      try { localStorage.setItem('sintonia_lang', l); } catch (e) {}
      if (document && document.documentElement) document.documentElement.lang = l;
      this.setState({ lang: l });
    };

    /* ════════ §2 · THE TRANSPARENCY PANEL ════════════════════════════════════
       Was: six hand-written rows counting the fixture — ITALY_DEMO.ACTIVITIES (72) while 503
       real competitor records existed, ITALY_DEMO.ARCHIVE, ITALY_DEMO.FIELD_MESSAGES — with no row at
       all for opportunities, so the panel could be opened on a fully demo radar and
       would not say so. It reported 244 real / 491 demo.

       It is now generated from AM.provenanceSummary, which publishes its own Italian
       label plus the real / derived / demo split and an isIndex flag, so the panel
       can never drift from the model again.

       The overlap is the real danger, and it grew with the model: 45 layers are now
       exposed and a naive sum reads 2347. `products` (166) is the join of
       productsRegulatory (163) and productsCommercial (44); regulatoryFuture (163)
       is the expiry column of that same registry; labelVerdicts (19) is the audited
       slice of productRelationships (236); eleven REAL_DERIVED layers are
       aggregations over a source layer already counted (windowCalendarRows and
       windowsByRegion over cropWindows, marketByCrop and marketSummaries over
       marketObservations, five competitor cuts over competitorActivities,
       scienceInstitutions over scienceRecords, portfolioLinksByCrop over
       regulatoryLinks); `people` (66) is the de-duplicated union of researchers (60)
       and publicPeople (15); and archive (774) re-indexes eight layers at once.
       Every one of those rows is SHOWN with its number and EXCLUDED from the total,
       carrying the row it belongs to. A total that silently double counts would be a
       larger lie than the one being fixed. */
    const CONTAINED = {
      productsRegulatory: 'products', productsCommercial: 'products',
      regulatoryFuture: 'productsRegulatory', labelVerdicts: 'productRelationships'
    };
    /* a re-cut is not a subset of rows, it is an aggregation OVER rows already counted */
    const RECUT = {
      portfolioLinksByCrop: 'regulatoryLinks',
      windowCalendarRows: 'cropWindows', windowsByRegion: 'cropWindows',
      marketByCrop: 'marketObservations', marketSummaries: 'marketObservations',
      competitorCropDensity: 'competitorActivities', competitorIssueDensity: 'competitorActivities',
      competitorMatrix: 'competitorActivities', competitorWindowMoments: 'competitorActivities',
      communicationAxis: 'competitorActivities',
      scienceInstitutions: 'scienceRecords'
    };
    /* people is the union of two lists that are NOT the same kind of evidence — 15
       names with documented identity AND role, 60 OpenAlex researchers, 9 shared —
       so it is neither contained in one nor summable with the other. */
    const UNION_OF = { people: ['researchers', 'publicPeople'] };
    const DS_EN = {
      productsRegulatory: 'Products · registry', productsCommercial: 'Products · catalogue',
      productRelationships: 'Product relationships', products: 'Portfolio',
      labelVerdicts: 'Label audit', regulatoryLinks: 'Authorized use rows',
      portfolioLinksByCrop: 'Authorized use rows by crop',
      cropWindows: 'Canonical crop windows', currentFieldSignals: 'Field readings and regional acts',
      cropEconomicWeight: 'Label reach by crop', windowCalendarRows: 'Window calendar',
      windowsByRegion: 'Windows by region', marketObservations: 'Price observations',
      marketByCrop: 'Market by crop', marketSummaries: 'Market analysis (handoff)',
      competitorActivities: 'Observed public communication', competitorCompanies: 'Observed companies',
      competitorProducts: 'Competitor products named', competitorCropDensity: 'Density by crop',
      competitorIssueDensity: 'Density by issue', competitorMatrix: 'Company x crop matrix',
      competitorWindowMoments: 'Window x competitor', communicationAxis: 'Published vocabulary',
      scienceRecords: 'Science records', researchers: 'Researchers', scienceThemes: 'Bibliometric themes',
      resistance: 'Confirmed resistance cases', scienceInstitutions: 'Institutions (author affiliation)',
      publicVoices: 'Public voices', publicChannels: 'Public channels',
      publicPeople: 'People with public evidence', people: 'People / Researchers',
      regulatoryFuture: 'Authorization expiries', agrometConditions: 'Agrometeorological conditions',
      futureEvents: 'Sector events', opportunities: 'Upstream convergences', futureSignals: 'Future signals',
      sources: 'Source registry', news: 'Trade press', relationships: 'Declared relationships',
      clientSafeCrossings: 'Audited crossings', archive: 'Archive (index)',
      futureScenarios: 'Presentation scenarios', opportunityScenarios: 'Presentation cases',
      fieldMessages: 'Field Sales integration (demonstration)'
    };
    const PS = (AM && AM.provenanceSummary) ? AM.provenanceSummary : [];
    const PS_LAB = PS.reduce((a, r) => { a[r.layer] = r.label || r.layer; return a; }, {});
    /* Italian is the model's own label; English falls back to it rather than to the
       raw collection key, so a missing translation never ships a camelCase name. */
    const dsLab = (k) => (T.DSLAYER && T.DSLAYER[k]) || (ITX ? (PS_LAB[k] || DS_EN[k] || k) : (DS_EN[k] || PS_LAB[k] || k));
    const PROV_NOTE = {
      cropWindows: [T.dsNormNote || 'norme agronomiche attese', 'expected agronomic norms'],
      productsRegulatory: [T.dsLabelNote || 'registro etichette ufficiali', 'official label registry'],
      fieldMessages: [T.dsSimNote || 'simulati', 'simulated']
    };
    const dsRow = (r) => {
      const k = r.layer;
      const contained = CONTAINED[k], recut = RECUT[k], union = UNION_OF[k];
      const isIndex = !!r.isIndex;
      const pn = PROV_NOTE[k];
      const note = contained ? EITHER('compreso in ' + dsLab(contained), 'included in ' + dsLab(contained))
        : recut ? EITHER('vista su ' + dsLab(recut) + ' · non sommata', 'a view over ' + dsLab(recut) + ' · not summed')
          : union ? EITHER('unione di ' + union.map(dsLab).join(' + ') + ' · non sommata', 'union of ' + union.map(dsLab).join(' + ') + ' · not summed')
            : isIndex ? EITHER('indice sul modello · non sommato', 'index over the model · not summed')
              : (pn ? EITHER(pn[0], pn[1]) : (r.total === 0 ? EITHER('nessuna tabella a monte', 'no upstream table yet') : ''));
      const out = !!(contained || recut || union || isIndex);
      return { layer: dsLab(k), key: k, real: r.real, derived: r.derived, demo: r.demo, total: r.total,
        note, provenance: r.provenance, contained: !!contained, isRecut: !!recut, isIndex, inTotal: !out };
    };
    const dataState = PS.map(dsRow).sort((a, b) =>
      (a.inTotal ? 0 : 1) - (b.inTotal ? 0 : 1) || (b.demo - a.demo) || (b.total - a.total) || a.layer.localeCompare(b.layer));
    const dsInTotal = dataState.filter((r) => r.inTotal);
    const dataStateTotals = dsInTotal.reduce((a, r) => ({ real: a.real + r.real, derived: a.derived + r.derived, demo: a.demo + r.demo }), { real: 0, derived: 0, demo: 0 });
    dataStateTotals.indexRows = dataState.filter((r) => r.isIndex).reduce((a, r) => a + r.total, 0);
    dataStateTotals.notSummed = dataState.filter((r) => !r.inTotal && !r.isIndex).reduce((a, r) => a + r.total, 0);
    dataStateTotals.total = dataStateTotals.real + dataStateTotals.derived + dataStateTotals.demo;
    dataStateTotals.layers = dataState.length;
    dataStateTotals.sourceLayers = dsInTotal.length;
    /* The footnote the markup still has to render (see the report): without it the
       columns visibly do not add up, because the excluded rows keep their numbers. */
    dataStateTotals.note = EITHER(
      'Totale su ' + dsInTotal.length + ' livelli di origine. Escluse le viste derivate e l’indice di archivio (' + dataStateTotals.indexRows + ' righe), che rileggono record già contati.',
      'Total over ' + dsInTotal.length + ' source layers. Derived views and the archive index (' + dataStateTotals.indexRows + ' rows) are excluded because they re-read records already counted.');
    const langBtns = ['it', 'en'].map(l => ({ label: l.toUpperCase(), bg: s.lang === l ? '#00783F' : 'transparent', color: s.lang === l ? '#fff' : '#B1A9A7', go: () => setLang(l) }));

    const uniq = (a) => [...new Set(a)].sort();
    /* Option labels are translated; the value stays the raw key so filtering is unaffected. */
    const opts = (label, vals, map) => [{ v: '', l: label }].concat(vals.map(v => ({ v, l: map ? map(v) : v })));
    const q = s.committedQuery.trim().toLowerCase();
    const match = (txt) => txt.toLowerCase().includes(q);

    /* ---- radar filtering
       A record answers a region filter on its canonical regionKeys when it has them
       (IT-OPP-001 resolves to both Lombardia AND Veneto, and would be invisible under
       a single-value match) and on its own region string otherwise, which is what the
       legacy scenario rows still carry. */
    const inRegion = (c, r) => !r || c.region === r || (Array.isArray(c.regionKeys) && c.regionKeys.indexOf(r) >= 0);
    let filtered = CASES.filter(c => (!s.fCrop || c.crop === s.fCrop) && (!s.fIssue || c.issue === s.fIssue) && inRegion(c, s.fRegion) && (!s.fStatus || c.status === s.fStatus) && (!s.fProduct || c.products.includes(s.fProduct)) && (!s.fDept || c.departments.includes(s.fDept)));
    const sorters = { relevant: (a, b) => a.st.rank - b.st.rank || a.evidenceTotal < b.evidenceTotal ? 1 : -1, closing: (a, b) => (a.windowOpen ? a.we : 999 + a.ws) - (b.windowOpen ? b.we : 999 + b.ws), newest: (a, b) => a.updated - b.updated, region: (a, b) => String(a.region || '').localeCompare(String(b.region || '')), crop: (a, b) => String(a.crop || '').localeCompare(String(b.crop || '')) };
    filtered = filtered.slice().sort(s.sort === 'relevant' ? (a, b) => (a.st.rank - b.st.rank) || (b.evidenceTotal - a.evidenceTotal) : sorters[s.sort]);
    const visibleCases = s.showAll ? filtered : filtered.slice(0, 12);
    const hasFilters = !!(s.fCrop || s.fIssue || s.fRegion || s.fStatus || s.fProduct || s.fDept);

    /* ════════ §3 · THE COUNTERS ══════════════════════════════════════════════
       Was: K = ITALY_DEMO.KPI, a hand-maintained object inside the demo file. Every number
       below now names the model collection it comes from, so the next data load
       moves it without anyone editing a view. Where the fixture and the model
       agree (29 windows, 6 open, 2 next cycle, 5 date-unknown, 16 closed) the
       value does not change on screen — the SOURCE did, and that is the point. */
    const cnt = (k) => (AM && AM.counts && AM.counts[k] !== undefined) ? AM.counts[k] : 0;
    const recs = (k) => (APP0 && APP0[k]) ? APP0[k].records : [];
    const tally = (arr, f) => arr.reduce((a, r) => { const v = r[f]; if (v === null || v === undefined) return a; a[v] = (a[v] || 0) + 1; return a; }, {});
    const WIN_STATUS = (APP0 && APP0.cropWindows.statusCounts) || tally(recs('cropWindows'), 'status');
    const WIN_REGION = (APP0 && APP0.cropWindows.regionCounts) || tally(recs('cropWindows'), 'region');
    /* The model publishes the source-group tally with its own Italian labels and the
       access tally beside it, so the seven group counts and the "how many of the
       monitored routes actually open" figure come from one place. Measured: FIELD 10 ·
       MARKET 6 · OFFICIAL 5 · RESEARCH 4 · TECHNICAL_MEDIA 4 · OWN 1 · PEOPLE 1 = 31,
       and GREEN 26 · BLOCKED 3 · PARTIAL 1 · NOT_REACHED 1. */
    const SRC_GROUPS = (APP0 && APP0.sources.groups) || [];
    const SRC_GROUP = SRC_GROUPS.length ? SRC_GROUPS.reduce((a, g) => { a[g.key] = g.count; return a; }, {}) : tally(recs('sources'), 'group');
    const SRC_ACCESS = (APP0 && APP0.sources.accessCounts) || tally(recs('sources'), 'accessStatus');
    const REL = recs('productRelationships');
    const relBy = tally(REL, 'strength');
    const LV = (AM && AM.labelVerdicts) ? AM.labelVerdicts : {};
    /* Recency is measured once, against AM.REF. 89 of the 503 competitor records
       (17.7%, all ORGANIC_VIDEO, all MULTI_COUNTRY_OR_UNRESOLVED) carry no start
       date and can never enter a recency count — the KPI sub-line says so. */
    const CA = (APP0 && APP0.competitorActivities) || { records: [] };
    const ACTS = CA.records;
    const actAge = (a) => (a.daysFromRef !== null && a.daysFromRef !== undefined) ? -a.daysFromRef : daysAgo(a.startDate);
    const ACTS_DATED = ACTS.filter((a) => actAge(a) !== null && actAge(a) >= 0);
    /* the model computes the same windows against the same REF; the local filter is
       only the fallback, and both agree at 11 / 1 / 89 today. */
    const ACT_UNDATED = (typeof CA.undatedCount === 'number') ? CA.undatedCount : ACTS.length - ACTS_DATED.length;
    const recentN = (d) => (d === 30 && typeof CA.recent30 === 'number') ? CA.recent30
      : (d === 7 && typeof CA.recent7 === 'number') ? CA.recent7
        : ACTS_DATED.filter((a) => actAge(a) <= d).length;
    const K = {
      /* the radar's own subject */
      total: cnt('opportunities'),
      scenarios: cnt('opportunityScenarios'),
      /* canonical crop-window status — upstream CURRENT_STATUS, tallied once */
      windows: cnt('cropWindows'),
      windowOpen: WIN_STATUS.WINDOW_OPEN || 0, windowClosed: WIN_STATUS.WINDOW_CLOSED || 0,
      nextCycle: WIN_STATUS.NEXT_CYCLE || 0, dateUnknown: WIN_STATUS.DATE_UNKNOWN || 0,
      regions: Object.keys(WIN_REGION).length,
      /* portfolio · the label audit, not the demo case links. AM.labelVerdicts is
         the audit itself (12 verified · 7 not found · 19 assessed); the relationship
         tally is the same 12 counted a second way and is the fallback. */
      links: cnt('productRelationships'),
      regulatoryLinks: cnt('regulatoryLinks'),
      matches: LV.verifiedCount !== undefined ? LV.verifiedCount : (relBy.VERIFIED_LABEL_MATCH || 0),
      notConfirmed: LV.notFoundCount !== undefined ? LV.notFoundCount : (relBy.NO_CONFIRMED_MATCH_CURRENT_READING || 0),
      assessed: LV.assessedCount !== undefined ? LV.assessedCount : 0,
      withMatch: Object.keys(REL.filter((r) => r.strength === 'VERIFIED_LABEL_MATCH').reduce((a, r) => { a[r.windowId || (r.crop + '|' + r.issue)] = 1; return a; }, {})).length,
      /* competitor */
      movements: recentN(30), movements7: recentN(7), undated: ACT_UNDATED,
      /* §9 · REACHED_IN_ITALY (414) and the 89 multi-country / unresolved records are
         two different claims and are never summed into "observed in Italy". */
      italyReach: (typeof CA.italyReachCount === 'number') ? CA.italyReachCount : 0,
      activities: cnt('competitorActivities'), companies: cnt('competitorCompanies'),
      /* science · archive · registry */
      records: cnt('scienceRecords'), researchers: cnt('researchers'), archive: cnt('archive'),
      signals: cnt('futureSignals'), events: cnt('futureEvents'), news: cnt('news'),
      /* two non-equivalent sets, never summed: 15 names with documented identity AND
         role, and 60 OpenAlex researchers (54 ORCID_PRESENT_NOT_RESOLVED_HERE). The
         model's de-duplicated union is 66, exposed separately so a screen that needs
         one number does not add 15 + 60 and publish 75. */
      orgs: cnt('sources'), people: cnt('publicPeople'), peopleUnion: cnt('people'),
      channels: cnt('publicChannels'),
      official: SRC_GROUP.OFFICIAL || 0, research: SRC_GROUP.RESEARCH || 0,
      field: SRC_GROUP.FIELD || 0, media: SRC_GROUP.TECHNICAL_MEDIA || 0,
      market: SRC_GROUP.MARKET || 0, own: SRC_GROUP.OWN || 0,
      routesOpen: SRC_ACCESS.GREEN || 0, routesBlocked: (SRC_ACCESS.BLOCKED || 0) + (SRC_ACCESS.NOT_REACHED || 0) + (SRC_ACCESS.PARTIAL || 0)
    };
    const ICO = (n) => 'assets/icons/' + n + '-white.png';
    /* Card 1 may not be called an "opportunity": all 3 records carry
       FORBIDDEN_LABEL = do not call this an Italian or a commercial opportunity.
       T.kpiConvergences is the key italy-i18n.js still owes us; until it lands the
       old label is the fallback. */
    const kpiTotalLab = T.kpiConvergences || T.kpiTotal;
    const kpiTotalSub = T.kpiConvergencesSub || EITHER('convergenze che meritano indagine', 'convergences that merit investigation');
    const movSub = EITHER(
      ACT_UNDATED + ' record senza data di inizio, esclusi · solo attività con data',
      ACT_UNDATED + ' records have no start date and are excluded · dated activity only');
    const kpiDef = [
      [K.total, kpiTotalLab, '#009845', '#00B152', 'farm-management', kpiTotalSub],
      /* Canonical buckets. These four describe the 29 CROP WINDOWS, which is what
         their own i18n sub-lines already say ("finestra agronomica aperta ora").
         They are not radar filters any more: 0 of 3 real records join a canonical
         window, so a status filter on the radar would always return nothing. */
      [K.windowOpen, wst('WINDOW_OPEN'), '#00B152', '#00B152', 'rain', T.kpiOpenSub],
      [K.nextCycle, wst('NEXT_CYCLE'), '#00A0DF', '#00A0DF', 'sun', T.kpiNextSub],
      [K.dateUnknown, wst('DATE_UNKNOWN'), '#F5B317', '#F5B317', 'heat-sensitive', T.kpiUnknownSub],
      [K.windowClosed, wst('WINDOW_CLOSED'), '#978B87', '#B1A9A7', 'connect', T.kpiClosedSub],
      [K.matches, T.kpiVerified, '#00B152', '#00B152', 'recycle-label', T.kpiVerifiedSub],
      [K.links, T.kpiLinks, '#9D1D96', '#C46ABE', 'sell', T.kpiLinksSub],
      [K.movements, T.kpiMovements, '#978B87', '#B1A9A7', 'cloud', movSub]
    ];
    const goWindows = () => this.go({ view: 'windows' });
    const kpiGo = [() => this.radarWith({}), goWindows, goWindows, goWindows, goWindows, () => this.go({ view: 'portfolio' }), () => this.go({ view: 'portfolio' }), () => this.compWith({})];
    const kpis = kpiDef.map((k, i) => ({ value: k[0], label: k[1], color: k[3], rail: k[2], tint: k[2] + '1A', icon: ICO(k[4]), sub: k[5], go: kpiGo[i] }));

    /* ════════ §4 · THE REGION MAP ════════════════════════════════════════════
       Was: ITALY_DEMO.REGION_STATS, 20 rows carrying an invented per-region `cases` count
       and a `signals` count that summed to 56 — exactly ITALY_DEMO.SIGNALS, the demo
       scenario feed. Measured, the 3 real future signals carry no Italian region
       at all (two "NAO SEI", one "UE"), so a real per-region signal count is 0
       everywhere and there is no derivation to make. The tile number is now the
       canonical crop-window count per region: 9 of 20 regions are lit, the same 9
       that are lit today, summing to 29. */
    /* Geometry now comes from AM.UI.REGION_GRID, so there is no fixture read left on
       this map at all. The fallback keeps the block standalone if that projection is
       ever rolled back, and is marked because it is layout and nothing else. */
    const REGION_GRID = (AM && AM.UI && AM.UI.REGION_GRID)
      ? AM.UI.REGION_GRID.map(r => ({ name: r.name, col: r.col, row: r.row, short: r.short }))
      : /*@VISUAL_ONLY 4x5 grid geometry and the 2-3 letter tile labels for Italy's 20 administrative regions; every NUMBER on this map comes from AM.collections.cropWindows[].region*/ D.REGION_STATS.map(r => ({ name: r.name, col: r.col, row: r.row, short: r.short }));
    /* Two real numbers per region, kept separate because they are different facts:
       `windows` is the canonical crop-window count (29 across 9 regions) and `cases`
       is how many of the 3 radar records resolve to that region through regionKeys
       (Veneto 1 · Lombardia 1 · Friuli-Venezia Giulia 1, and 0 everywhere else).
       The tile is lit by windows, because a map lit by 3 records would be a blank map. */
    const oppByRegion = CASES.reduce((a, c) => { (c.regionKeys && c.regionKeys.length ? c.regionKeys : [c.region]).forEach((r) => { if (r) a[r] = (a[r] || 0) + 1; }); return a; }, {});
    const regionTiles = REGION_GRID.map(r => {
      const n = WIN_REGION[r.name] || 0;
      const o = oppByRegion[r.name] || 0;
      return {
        name: r.name, short: r.short, gc: r.col + 1, gr: r.row + 1,
        windows: n, cases: n, opportunities: o, active: n > 0,
        /* the '+N signals' span this feeds must be deleted from the markup: there is
           no per-region signal count to derive — all 3 real future signals carry
           REGION 'NAO SEI' x2 and 'UE' x1, so the honest value is 0 everywhere. */
        signals: 0,
        color: n > 0 ? '#6E6663' : 'rgba(255,255,255,0.05)', border: n > 0 ? '#6E6663' : 'rgba(255,255,255,0.10)',
        textColor: n > 0 ? '#fff' : '#B1A9A7',
        go: () => this.radarWith({ fRegion: r.name })
      };
    });
    const regionRank = regionTiles.filter(r => r.windows > 0).sort((a, b) => b.windows - a.windows || a.name.localeCompare(b.name)).slice(0, 7);
    const initials = (n) => String(n || '').split(' ').map(w => w[0]).filter(Boolean).join('').slice(0, 3).toUpperCase();

    /* ════════ §5 · COMPETITOR COMMUNICATION ═════════════════════════════════
       Channel metadata is presentation (§4). ORGANIC_VIDEO is added because it is
       one of the two real TYPE values (PAID 414 · ORGANIC_VIDEO 89); the other
       keys stay for the screens still passing legacy rows in. */
    const CH = {
      'PAID': { c: '#00A0DF', i: 'sell', n: T.chPaid }, 'ORGANIC': { c: '#7DB41E', i: 'connect', n: T.chOrganic },
      'ORGANIC_VIDEO': { c: '#9D1D96', t: '#C46ABE', i: 'sun', n: T.chVideo || T.chOrganic },
      'VIDEO': { c: '#9D1D96', t: '#C46ABE', i: 'sun', n: T.chVideo }, 'PEOPLE': { c: '#F5B317', i: 'farm-management', n: T.chPeople },
      'EVENT': { c: '#00698F', t: '#00A0DF', i: 'cloud', n: T.chEvent }, 'PRODUCT / PORTFOLIO': { c: '#F89E18', i: 'recycle-label', n: T.chProduct }
    };
    const TIMING = { 'IN WINDOW': '#00B152', 'APPROACHING WINDOW': '#F5B317', 'EARLY': '#00A0DF', 'POST WINDOW': '#978B87', 'NO TIMING MATCH': '#8F8886' };
    /* §8/§13 · market "temperature" was an editorial fixture (window.ITALY_MARKET)
       being read as if it measured demand. M2 now points at the model projection
       that will replace it; until that projection lands mkCropTemp returns null and
       every consumer already renders its own "not enough data" branch. */
    const M2 = (AM && AM.marketByCrop) ? AM.marketByCrop : null;
    const mkCropTemp = (crop) => { if (!M2 || !crop) return null; return M2[crop] || M2[String(crop).toUpperCase()] || null; };
    const EVBY = recs('futureEvents').reduce((a, e) => { a[e.id] = e; return a; }, {});
    const NOT_ASSESSED = EITHER('NON VALUTATO', 'NOT ASSESSED');
    const noWindowLead = EITHER(
      'nessuna finestra canonica collegata a questo record',
      'no canonical window is linked to this record');
    const noMatchLab = (T.PSTATE && T.PSTATE.NO_CONFIRMED_MATCH_CURRENT_READING) || 'NO CONFIRMED MATCH IN THE CURRENT READING';
    const absenceRule = T.absenceRule || (AM ? AM.ABSENCE_RULE : '') || '';
    const notEnough = EITHER('DATI NON SUFFICIENTI', 'NOT ENOUGH DATA');
    /* actDeco · aligned with the real record shape. Removed: the winMatch() keyword
       guess that turned a shared word into an agronomic timing verdict (0 of 503 real
       records carry a windowId), the ADAMA-response claim built from a demo case's
       product list, the market temperature, the invented headline and the
       "transcript available" badge. What is left is what the record actually says. */
    const actDeco = (a) => {
      const ch = CH[a.type] || CH['PAID'];
      const cropsArr = a.cropsCanonical || a.crops || (a.crop ? [a.crop] : []);
      const issuesArr = a.issuesObserved || a.issues || (a.issue ? [a.issue] : []);
      const prodsArr = a.products || (a.product ? [a.product] : []);
      const age = actAge(a);
      const hasDate = age !== null;
      const ev = a.eventId ? EVBY[a.eventId] : null;
      const demoRec = AM ? AM.isDemo(a, a.provenance) : !!a.isDemo;
      /* §9 · REACHED_IN_ITALY (414) is not the same claim as the 89 multi-country
         or unresolved records, and the two must never merge into "observed in Italy". */
      const reached = a.geoClass ? a.geoClass === 'REACHED_IN_ITALY' : null;
      return Object.assign({}, a, {
        cropL: cropsArr.map(cl).join(' · ') || null, issueL: issuesArr.map(il).join(' · ') || null,
        crops: cropsArr, issues: issuesArr,
        countryL: (T.PROV && T.PROV[a.country]) || a.country || null,
        isDemo: demoRec,
        ctaL: demoRec ? (T.ctaDemo || 'DEMONSTRATION EXAMPLE') : (a.cta || (T.ctaViewCase || 'VIEW RELATED CASE →')),
        provL: (T.PROV && T.PROV[a.provenance]) || a.provenance,
        provColor: demoRec ? '#F5B317' : '#00B152',
        chColor: ch.c, chText: ch.t || ch.c, chIcon: 'assets/icons/' + ch.i + '-white.png', chName: ch.n, chTint: ch.c + '18',
        color: ch.c,
        geoClass: a.geoClass || null, reachedItaly: reached,
        reachLabel: reached === null ? null : reached ? EITHER('raggiunto in Italia', 'reached in Italy') : EITHER('multi-paese o non risolto', 'multi-country or unresolved'),
        hasDate, when: hasDate ? agoLbl(age) : null,
        dateNote: hasDate ? null : EITHER('nessuna data di inizio pubblicata', 'no published start date'),
        /* the ad copy as published — an original public quote, never translated, and
           never manufactured: the demo's authored `headline` is overwritten here so a
           legacy row cannot smuggle one through the spread above */
        headline: a.text || null, productOrHeadline: prodsArr[0] || a.text || null,
        /* the short label a one-line strip can carry. Never the ad copy: measured,
           392 of 503 records have text and it runs to several lines with emoji.
           products (102 records) then crops (183) then the channel name. */
        observed: prodsArr.join(' + ') || cropsArr.map(cl).join(' · ') || ch.n || null,
        transcriptLabel: null,
        /* no agronomic verdict is derivable: kept as an explicit UNKNOWN so the box
           never reads as a measured timing */
        timing: NOT_ASSESSED, timingColor: TIMING['NO TIMING MATCH'],
        leadLabel: noWindowLead, windowLabel: '', hasWindow: false, goWindow: () => {},
        adamaResponse: noMatchLab, adamaColor: '#B1A9A7', adamaProducts: absenceRule,
        marketTemp: notEnough, marketColor: '#B1A9A7', goMarket: () => this.go({ view: 'market' }),
        openCompany: () => this.openCompany(a.company), openCase: () => a.caseId && this.openCase(a.caseId),
        openProduct: () => a.product && this.openCProduct(a.product),
        openPerson: () => a.personId && this.openPerson(a.personId), openEvent: () => a.eventId && this.openEvent(a.eventId),
        initials: initials(a.company),
        isPaid: a.type === 'PAID', isVideo: a.type === 'VIDEO' || a.type === 'ORGANIC_VIDEO',
        isOrganic: a.type === 'ORGANIC', isPeople: a.type === 'PEOPLE', isEvent: a.type === 'EVENT',
        hasProduct: !!prodsArr.length, product: prodsArr[0] || null,
        personInitials: a.person ? initials(String(a.person).replace('Demo profile · ', '')) : '',
        eventDates: ev ? ev.date : '', eventCity: ev ? ev.location : '',
        partColor: a.participation && String(a.participation).startsWith('CONFIRMED') ? '#00B152' : '#B1A9A7',
        cta: a.type === 'PAID' ? 'VIEW AD →' : (a.type === 'VIDEO' || a.type === 'ORGANIC_VIDEO') ? 'WATCH →' : a.type === 'PEOPLE' ? 'VIEW MENTION →' : a.type === 'EVENT' ? 'VIEW EVENT →' : a.type === 'ORGANIC' ? 'VIEW POST →' : 'VIEW RECORD →',
        platformShort: String(a.platform || '').split(' · ').pop(),
        /* layout only: a stable tile height from the record id, so the gallery keeps
           its masonry rhythm without a fabricated "days" integer driving it */
        galleryH: (150 + (String(a.id || a.company || '').split('').reduce((h, c2) => (h * 31 + c2.charCodeAt(0)) % 9973, 7) % 90)) + 'px'
      });
    };
    /* Was: ITALY_DEMO.ACTIVITIES (72 demo rows) sorted by an authored `days` integer. Now the
       real corpus, newest first. Only dated records can be ranked by recency, which
       excludes the 89 undated ORGANIC_VIDEO rows — stated on the KPI card above. */
    const recentActivity = ACTS_DATED.slice().sort((a, b) => actAge(a) - actAge(b)).slice(0, 6).map(actDeco);
