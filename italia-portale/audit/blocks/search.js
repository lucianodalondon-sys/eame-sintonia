    /* §15 · GLOBAL SEARCH · the eight hand-written fixture scans are gone.
       The old block scanned D.CASES(29 decorated), A_SIGREAL(3), D.PRODUCT_LIST(33),
       D.SCI_THEMES(10)+D.RECORDS(36), D.PEOPLE(39), D.COMPANIES(6), D.ARCHIVE(448) and
       D.SOURCES(53), and decided a route inside each scan. The index is now
       AM.searchIndex — measured 1078 entries over 15 kinds, built once in the model with
       diacritic-folded, sentinel-free terms — and this block does one filter, one group
       and one dispatch. The ARCHIVE group is deleted outright: AM.archive is a derived
       index over the same science / market / competitor / voice / event / news / window
       records the per-kind groups already reach, so an ARCHIVE group would have counted
       every hit twice. */
    /* Combining Diacritical Marks is U+0300..U+036F (768..879 decimal). Written as a code
       point range rather than a character class, because a class of combining marks is
       invisible in the source and does not survive a re-encode of this file. */
    const SFOLD = (x) => String(x == null ? '' : x).normalize('NFD').split('')
      .filter((c) => { const n = c.charCodeAt(0); return n < 768 || n > 879; }).join('').toLowerCase();
    /* Both sides of the comparison must fold identically or the index and the query
       drift: the model folds its terms, so 'Marzachi' has to reach 'Marzachì'. */
    const sQ = SFOLD(s.committedQuery || '').trim();

    /* A destination is READY only when its screen resolves the record's own id against
       the model, or lists that record among the rows it shows. Anything else would open a
       look-alike, which is the one failure this rewrite exists to prevent. Re-measured
       against every landed domain by opening all 1078 destinations and comparing the name
       on the detail screen with the name on the row: product 166/166, window 29/29,
       case 3/3, signal 3/3, event 18/18, company 11/11, source 31/31 and researcher 60/60
       resolve to the same entity, 0 mismatches. voice, resistance, science and news have
       no per-record screen and land on the list that visibly contains them (17 Voci cards,
       34 GIRE rows with gireAll, 88 science records, 8 news items).
       Withheld: channel (30). Channels are listed on no screen in the package — only 3 of
       the 30 are even named on a Voci card — so a channel hit would land nowhere. */
    const SEARCH_READY = {
      product: 1, case: 1, window: 1, signal: 1, voice: 1, resistance: 1,
      market: 1, company: 1, competitor: 1, event: 1,
      researcher: 1, source: 1, science: 1, news: 1,
      channel: 0
    };

    /* One dispatcher. Each kind opens the entity it names, or lands on the screen that
       visibly contains it — never a third thing. */
    const SGO = {
      product: (e) => this.openProduct(e.id),
      /* IT-OPP-001/002/003 are the only upstream-real opportunities and all three ids
         exist in the case view's pool, so the id resolves rather than falling through. */
      case: (e) => this.openCase(e.id),
      window: (e) => this.openWindow(e.id),
      signal: (e) => this.openSignal(e.id),
      /* Voci is a flat list of exactly the 17 real voices with no id anchor, so the hit
         lands on the page that contains it. It is not opened; it is not substituted. */
      voice: () => this.go({ view: 'voices' }),
      /* GIRE rows are collapsed to 8 of 34 by default, so 26 of 34 hits would land on a
         page that does not visibly contain the match. gireAll opens the full list. */
      resistance: () => this.go({ view: 'science', gireAll: true }),
      market: (e) => this.go({ view: 'market', mTab: 'crop', mCrop: e.routeArgs.mCrop }),
      company: (e) => this.openCompany(e.id),
      /* An observed communication is not a competitor PRODUCT: the model routes it to
         'cproduct' with an activityId, and openCProduct matches on a product NAME, so it
         would have opened the first competitor product for all 503. The feed filtered to
         the advertiser does contain the record. */
      competitor: (e) => this.compWith({ fCompany: e.meta }),
      event: (e) => this.openEvent(e.id),
      researcher: (e) => this.openPerson(e.id),
      source: (e) => this.openSource(e.id),
      /* No per-record science screen exists; the Scientific Intelligence page lists all
         88 records, so the hit lands on the page that contains it. */
      science: () => this.go({ view: 'science' }),
      /* The news list is the TECHNICAL_MEDIA group of the Sources screen; the alias the
         group chips already use is the one passed here, so the 8 items are on screen. */
      news: () => this.go({ view: 'sources', sourceGroup: 'NEWS & TRADE MEDIA' })
    };

    /* Presentation-only lookups, so a row can be labelled in the client's language from
       the record's own canonical keys instead of the model's raw display string. */
    const sBy = (recs) => { const m = {}; (recs || []).forEach((r) => { m[r.id] = r; }); return m; };
    const S_OPP = sBy(APP0 ? APP0.opportunities.records : []);
    const S_WIN = sBy(APP0 ? APP0.cropWindows.records : []);
    const S_MKT = sBy(APP0 ? APP0.marketObservations.records : []);
    const S_RES = sBy(APP0 ? APP0.resistance.records : []);
    const S_ACT = sBy(APP0 ? APP0.competitorActivities.records : []);
    const sIT = s.lang !== 'en';
    /* GIRE species and crop strings carry the researcher's Portuguese annotations after
       an em dash (measured: 12 of 34 crop strings run past 40 characters, one of them
       155). Cut at the dash only — §11: 'Schoenoplectus (Scirpus) mucronatus' must never
       be truncated at the parenthesis. */
    const sCut = (v) => String(v || '').split(/\s+[—–]\s+/)[0]
      /* The one Portuguese fragment left in 861 rows: "(sinonimi na ficha: A. patulus…)"
         on IT-RES-002. "na ficha" is the researcher saying where she read the synonyms —
         a source annotation, not part of the name — so those two words go and the whole
         synonym list stays. The parenthesis itself is never cut: §11. */
      .replace(/\(\s*sinonimi\s+na\s+ficha\s*:/i, '(sinonimi:').trim();
    /* The meta column is nowrap with no ellipsis of its own, so a 109-character
       institution chain would squeeze the label out of a 300px card. Capping is
       presentation: the full value is on the screen the row opens, and the ellipsis says
       out loud that there is more. Measured: 27 of 861 rows are longer than 60. */
    const sMeta = (v) => { const t = String(v == null ? '' : v).trim(); return t.length > 32 ? t.slice(0, 31) + '…' : t; };

    /* Per-kind row text. Anything not listed keeps the model's own label and meta. */
    const S_ROW = {
      case: (e) => { const o = S_OPP[e.id] || {};
        /* title / issue / crop are the analyst's Portuguese working text on 3/3 real
           opportunities ("Videira x Flavescência dourada, via o vetor Scaphoideus
           titanus"); the canonical keys are the localizable ones. IT-OPP-003 is
           portfolio-wide and has issueKey null and no crop, so it falls back to its id
           rather than to the Portuguese — the same rule the Field Sales panel uses. */
        return { label: [o.issueKey ? il(o.issueKey) : o.id, (o.regionKeys || []).join(', ')].filter(Boolean).join(' · '),
                 meta: (o.cropKeys || []).map(cl).join(', ') }; },
      window: (e) => { const w = S_WIN[e.id] || {};
        return { label: [il(w.issue), w.region].filter(Boolean).join(' · '), meta: cl(w.crop) }; },
      market: (e) => { const m = S_MKT[e.id] || {};
        /* the model's label leads with the raw series code ('BLTPAN|PAN'), which names
           nothing to a reader; cropKey is filled 77/77 and is localizable. */
        return { label: [cl(m.cropKey), m.market].filter(Boolean).join(' · '), meta: m.unit || '' }; },
      resistance: (e) => { const r = S_RES[e.id] || {};
        /* meta was the crop string, which is Portuguese prose on 12 of 34 rows. The
           botanical family is filled 34/34 and is Latin, so it is never translated. */
        return { label: sCut(r.species) || e.label, meta: r.family || '' }; },
      /* An observed communication was labelled with its PAGE name, so all 138 BASF
         records read "BASF Agricultural Solutions" — 11 distinct labels for 503 rows.
         The row now carries what the advertiser itself published: the product names it
         proves (102/503), else its own ad copy (392/503, never translated, ellipsized by
         the card), else the page name (111/503). 249 distinct labels. */
      competitor: (e) => { const a = S_ACT[e.id] || {};
        /* deduped in the order the advertiser listed them — uniq() sorts, and the order
           a company names its own products is not ours to rearrange. */
        const prods = (a.products || []).filter((p, i, arr) => arr.indexOf(p) === i);
        return { label: prods.length ? prods.join(' · ') : (String(a.text || '').replace(/\s+/g, ' ').trim() || a.displayName || e.label), meta: a.company || e.meta || '' }; },
      /* the source TYPE is a raw enum (OFFICIAL, TECHNICAL_MEDIA); the underscore is
         presentation noise, and the value itself is never invented here. */
      source: (e) => ({ label: e.label, meta: String(e.meta || '').replace(/_/g, ' ') }),
      company: (e) => ({ label: e.label,
        /* the count of observed public communications — §8: density inside monitored
           public communication, not market share and not commercial importance. */
        meta: (() => { const c = (companies || []).filter((x) => x.name === e.id)[0]; return c ? c.count + (sIT ? ' oss.' : ' obs.') : ''; })() })
    };

    /* Group order is fixed and deliberate: COMPETITOR carries 503 observed activities and
       would otherwise be the loudest answer to almost any crop word. */
    const SGROUP_DEF = [
      ['OPPORTUNITY', (T.lblOpportunities || 'OPPORTUNITIES').toUpperCase(), '#009845', () => this.radarWith({ showAll: true })],
      ['WINDOW', (T.navWindows || 'Crop Windows').toUpperCase(), '#978B87', () => this.go({ view: 'windows' })],
      ['PRODUCT', (T.navPortfolio || 'Portfolio').toUpperCase(), '#978B87', () => this.go({ view: 'portfolio' })],
      ['SIGNAL', (T.navFuture || 'Future Radar').toUpperCase(), '#978B87', () => this.go({ view: 'future' })],
      ['FIELD_VOICE', (T.navVoices || 'Field Voices').toUpperCase(), '#978B87', () => this.go({ view: 'voices' })],
      ['SCIENCE', (T.navScience || 'Scientific Intelligence').toUpperCase(), '#978B87', () => this.go({ view: 'science', gireAll: true })],
      ['PEOPLE', (T.lblPeople || 'PEOPLE').toUpperCase(), '#978B87', () => this.go({ view: 'sources', sourceGroup: 'PEOPLE', peopleCat: 'RESEARCHERS' })],
      ['COMPETITOR', (T.navCompetitors || 'Competitor Watch').toUpperCase(), '#978B87', () => this.compWith({})],
      ['MARKET', (T.navMarket || 'Market Pulse').toUpperCase(), '#978B87', () => this.go({ view: 'market' })],
      ['SOURCE', (T.navSources || 'Sources').toUpperCase(), '#978B87', () => this.go({ view: 'sources' })],
      /* the same wording the Sources group chip uses, so one thing has one name. */
      ['NEWS', sIT ? 'STAMPA E MEDIA TECNICI' : 'TRADE & TECHNICAL MEDIA', '#978B87', () => this.go({ view: 'sources', sourceGroup: 'NEWS & TRADE MEDIA' })],
      ['EVENT', ((T.navCompetitors || 'Competitor Watch') + ' · ' + (T.lblEventWatch || 'EVENT WATCH')).toUpperCase(), '#978B87', () => this.compWith({ compView: 'events' })]
    ];

    /* 8 of the 77 market observations resolve to no Market Pulse crop bucket ('Feed
       barley' 1 and the unresolved 'ORGFOUR|FEED' 7). Routing them to the Market screen
       would leave whatever crop is already selected on display — a different crop from
       the row that was clicked — so they are withheld rather than forced into a bucket. */
    const sRoutable = (e) => !!SEARCH_READY[e.kind] && !!SGO[e.kind] && (e.kind !== 'market' || !!(e.routeArgs && e.routeArgs.mCrop));
    const sShape = (e) => {
      const r = S_ROW[e.kind] ? S_ROW[e.kind](e) : { label: e.label, meta: e.meta || '' };
      const label = String(r.label || e.label || e.id), meta = String(r.meta == null ? '' : r.meta);
      /* matched on the FULL text, displayed capped: a truncated meta must never make a
         record unfindable by a word it really carries. */
      return { e, label, meta: sMeta(meta), hay: SFOLD(label + ' ' + meta) };
    };
    /* The row is matched on what the reader can SEE as well as on the index terms.
       Without it the search is only as Italian as the upstream record: the model indexes
       opportunity IT-OPP-001 on the analyst's Portuguese "flavescencia dourada", so the
       word printed on its own row — "Flavescenza Dorata", the canonical issue key — found
       nothing; and "frumento duro" missed 4 crop windows and 8 market observations whose
       crop is shown in Italian but indexed as the canonical key "Durum Wheat". */
    const sPool = (sQ.length >= 2 && AM) ? AM.searchIndex.filter(sRoutable).map(sShape) : [];
    const sHits = sPool.filter((r) => r.hay.indexOf(sQ) >= 0 || r.e.terms.some((t) => t.indexOf(sQ) >= 0));
    const sByGroup = {};
    sHits.forEach((r) => { (sByGroup[r.e.group] = sByGroup[r.e.group] || []).push(r); });

    /* The card shows 6 rows and prints the full count. With 503 competitor records that
       gap is the difference between a number and an answer, so the seventh row is an
       honest overflow link into the section — built from the existing item node, because
       the markup is frozen and its only spare slot is another item. */
    const SCAP = 6;
    const searchGroups = SGROUP_DEF.filter((g) => sByGroup[g[0]]).map(([key, label, color, goAll]) => {
      const list = sByGroup[key];
      const rows = list.slice(0, SCAP).map((r) => ({ label: r.label, meta: r.meta, go: () => SGO[r.e.kind](r.e) }));
      const over = list.length - rows.length;
      if (over > 0) rows.push({ label: '+ ' + over + (sIT ? ' altri risultati' : ' more results'), meta: (sIT ? 'VEDI TUTTO' : 'VIEW ALL') + ' →', go: goAll });
      return { label, color, count: list.length, items: rows, empty: false };
    });

    /* portfolio, product and voices had no entry, so the breadcrumb bar was blank on three
       of the twenty-six screens. The keys already exist in italy-i18n.js. */
    const titles = { portfolio: (T.navPortfolio || '').toUpperCase(), product: (T.navPortfolio || '').toUpperCase(), voices: (T.navVoices || '').toUpperCase(), radar: (T.navRadar || '').toUpperCase(), case: (T.navRadar || '').toUpperCase(), brief: 'ACTION BRIEF', field: (T.navField || '').toUpperCase(), windows: (T.navWindows || '').toUpperCase(), window: (T.navWindows || '').toUpperCase(), market: (T.navMarket || '').toUpperCase(), signal: (T.navFuture || '').toUpperCase(), future: (T.navFuture || '').toUpperCase(), competitors: (T.navCompetitors || '').toUpperCase(), company: (T.navCompetitors || '').toUpperCase(), event: (T.navCompetitors || '').toUpperCase() + ' · ' + (T.lblEventWatch || 'EVENT WATCH'), cproduct: (T.navCompetitors || '').toUpperCase(), science: (T.navScience || '').toUpperCase(), theme: (T.navScience || '').toUpperCase(), archive: (T.navArchive || '').toUpperCase(), sources: (T.navSources || '').toUpperCase(), source: (T.navSources || '').toUpperCase(), person: (T.navSources || '').toUpperCase() + ' · ' + (T.lblPeople || 'PEOPLE'), search: (T.lblSearch || 'SEARCH') };
    /* Every branch is evaluated before the view is picked, so each detail object is read
       through a guard: several domains now resolve to null on an unknown id instead of
       silently substituting record[0], and a bare .label would throw on the way there. */
    const cbG = (x) => x || {};
    const crumb = { signal: (cbG(sg).issue + ' · ' + cbG(sg).crop + ' · ' + cbG(sg).region).toUpperCase(), window: (cbG(wd).issue + ' · ' + cbG(wd).crop + ' · ' + cbG(wd).region).toUpperCase(), case: (cbG(cs).issue + ' · ' + cbG(cs).crop + ' · ' + cbG(cs).region).toUpperCase(), brief: br ? (br.doc + ' · ' + cbG(cs).issue + ' · ' + cbG(cs).region).toUpperCase() : '', company: String(cbG(co).label || '').toUpperCase(), event: String(cbG(evd).name || '').toUpperCase(), cproduct: (cbG(cp).company + ' · ' + cbG(cp).name).toUpperCase(), market: mp ? (mp.label + ' · ' + (s.mTab === 'industry' ? 'CROP PROTECTION MARKET' : 'CROP MARKET')).toUpperCase() : '', theme: String(cbG(th).title || '').toUpperCase(), source: String(cbG(sr).name || '').toUpperCase(), person: String(cbG(pr).label || '').toUpperCase(), search: s.committedQuery.toUpperCase() }[s.view] || '';

    /* §6 · ONE clock. todayLabel was D.fmt(D.TODAY) — a Date frozen inside the fixture,
       a second clock beside AM.REF. It is now derived from AM.referenceDate (2026-09-02),
       the single reference date the whole package is compiled against. The markup appends
       the year as a literal, so the shape stays "02 SET" exactly as before. */
    const REFP = String((AM && AM.referenceDate) || '2026-09-02').split('-');
    const REF_MON = T.months || ['GEN', 'FEB', 'MAR', 'APR', 'MAG', 'GIU', 'LUG', 'AGO', 'SET', 'OTT', 'NOV', 'DIC'];
    const todayLabel = (REFP[2] + ' ' + (REF_MON[Number(REFP[1]) - 1] || '')).trim().toUpperCase();

    return {
      nav, kpi: K, todayLabel, pageTitle: titles[s.view], crumb, hasCrumb: !!crumb,
      query: s.query, onQuery: (e) => this.setState({ query: e.target.value }), onQueryKey: (e) => { if (e.key === 'Enter' && s.query.trim()) this.go({ view: 'search', committedQuery: s.query }); },
      isSignal: s.view === 'signal', sg, hasEvidence: !!ev, ev: ev || {}, closeEvidence: () => this.setState({ evidenceIdx: null }),
      isProduct: s.view === 'product', pd: pd || {}, hasPd: !!pd,
      isPortfolio: s.view === 'portfolio', port: port || {}, hasPort: !!port,
      isVoices: s.view === 'voices', voices: voices || {}, hasVoices: !!voices,
      navIntegrations,
      navIntegrationItems,
      /* §14 · Inbound only. The control simulates RECEIPT, never a send. */
      fsFlow: [T.fsFlowIn, T.fsFlowReceived, T.fsFlowClassified, T.fsFlowLinked, T.fsFlowValidate].map((l, i, arr) => ({ label: l, sep: i < arr.length - 1 ? '→' : '' })),
      /* @EXPLICIT_DEMO Field Sales inbound demonstration, default off, feeds no real count.
         The pool is the model's fieldMessages collection — the same 18 records, every one
         carrying provenance SYNTHETIC_DEMO, so the demonstration is now readable as demo
         from the data itself instead of from the fixture it was pulled out of. */
      simulateInbound: () => { const pool = APP0 ? APP0.fieldMessages.records : []; if (!pool.length) return; const n = (s.extraMessages || []).length; this.setState({ extraMessages: (s.extraMessages || []).concat([pool[n % pool.length]]) }); },
      /* mpReview fed the sentence "Last source review {{ mpReview }}." from
         ITALY_MARKET.LAST_REVIEW, which is now undefined — the market fixture has been
         stripped to labels. No external source states when Sintonia last reviewed its own
         sources, so the value is empty and the markup line needs the sentence removed. */
      isMarket: s.view === 'market', mp: mp || {}, hasMp: !!mp, mpCropOptions, mpButtons, mCrop: s.mCrop, setMCrop: (e) => this.setState({ mCrop: e.target.value }), mpTabs, mIsCrop: s.mTab === 'crop', mIsIndustry: s.mTab === 'industry', cpm: cpMarketObj, mpReview: '', hasCsMarket: !!csMarket, csMarket: csMarket || {},
      /* `ladder` was D.LADDER cross-referenced with D.DEPT — an internal ADAMA playbook
         (90d MARKET DEVELOPMENT, 60d MARKETING…) presented beside external evidence. It
         is bound by no markup node (verified: the only ladder in the markup is
         wd.ladder, which the Crop Windows block builds), so it is declared empty rather
         than kept alive from the fixture. */
      isWindows: s.view === 'windows', isWindow: s.view === 'window', goWindows: () => this.go({ view: 'windows' }), calCrop: s.calCrop, calCropBtns, calRows, calRowCount: calRows.length, calNoRows: calRows.length === 0, calEmptyText, calEmptyCta, calHasEmptyCta: !!calEmptyCta, calEmptyGo, calClearBucket, calFilterLabel, calMonths, calYearMarks, calStrip, calKpis, calKpiNote, calMoments, calIssueColor: calCatColor, todayLeft, todayInView, calHorizons, calNav, calRangeLabel, calModes, calIsCalendar: s.calMode === 'calendar', calIsSeason: s.calMode === 'season', calSeason, calDetail: s.calDetail, toggleCalDetail: () => this.setState({ calDetail: !s.calDetail }), calDetailLabel: s.calDetail ? T.cwDeptOn : T.cwDeptOff, calMarketTemp: calMarket ? calMarket.temp : 'NOT ENOUGH DATA', calMarketColor: calMarket ? calMarket.color : '#8F8886', hasCalMarket: !!calMarket, goCalMarket: () => this.go({ view: 'market', mCrop: calMarket ? calMarket.key : 'maize', mTab: 'crop' }), hasCalDrawer: !!dw0, dw, closeCalDrawer: () => this.setState({ calRegion: null }), windowCropChips, windowBuckets, visibleWindows: wins, windowCount: wins.length, ladder: [], windowKpi: WK, earlyWindows, wd,
      isBrief: s.view === 'brief' && !!br, br: br || {}, isField: s.view === 'field', goField: () => this.go({ view: 'field' }), goTsr: () => this.go({ view: 'sources', sourceGroup: 'PEOPLE', peopleCat: 'TECHNICAL SALES REPRESENTATIVES' }),
      fieldMessages, fieldKpis, fieldStateChips, inboundFlow, tsrs, tsrCount: tsrs.length, fieldCases, showComposer: s.showComposer, toggleComposer: () => this.setState({ showComposer: !s.showComposer }), composerText: s.composerText, setComposer: (e) => this.setState({ composerText: e.target.value }), parsed, composerExamples,
      /* The composed message no longer carries a fabricated sales rep (D.TSR), a fixture
         issue category (D.CAT.pest) or a matched scenario object: the Field Sales screen
         reads none of them, and every one of them was a fact supplied by the fixture to a
         record the user had just typed. What survives is what the user wrote plus what
         parseField recognised, stamped DEMO. */
      sendComposer: () => { if (!parsed.caseObj && parsed.issue === '—') return; const c = parsed.caseObj; const m = { id: 'FM-' + Date.now(), region: c ? c.region : 'Italy', sub: 'demo', crop: c ? c.crop : '—', issue: parsed.issue, caseId: c && parsed.state === 'CONNECTED' ? c.id : null, relatedCase: c ? c.id : null, signalMatch: null, state: parsed.state, mins: 0, text: s.composerText, signal: parsed.signal, timing: c ? c.stage : '—', product: c ? c.primary : null, competitors: parsed.competitors && parsed.competitors.length ? parsed.competitors : null, person: 'Field Sales Rep · DEMO', color: parsed.color, when: 'just now' }; this.setState({ extraMessages: [m].concat(s.extraMessages), composerText: '', showComposer: false, fieldState: '' }); },
      /* §5 · The notification centre was six D.NOTIFICATIONS rows asserting current
         events — "FIELD SIGNAL CONNECTED · Flavescenza Dorata · Veneto · 38 min ago",
         "WINDOW UPDATE · European Corn Borer · FVG · 14 days remaining" — with fabricated
         relative timestamps that no clock produced and no source states. That is a demo
         fixture feeding a real current signal. Nothing external replaces it, so the panel
         is empty. The unread dot at markup line 147 is hardcoded and must be removed. */
      showNotifs: s.showNotifs, toggleNotifs: () => this.setState({ showNotifs: !s.showNotifs }), notifs: [],
      t: T, langBtns, dataState, dataStateTotals, showDataState: !!s.showDataState, toggleDataState: () => this.setState({ showDataState: !s.showDataState }), isRadar: s.view === 'radar', isCase: s.view === 'case', isFuture: s.view === 'future', isCompetitors: s.view === 'competitors', isCompany: s.view === 'company', isScience: s.view === 'science', isTheme: s.view === 'theme', isArchive: s.view === 'archive', isSources: s.view === 'sources', isSource: s.view === 'source', isPerson: s.view === 'person', isSearch: s.view === 'search',
      goRadar: () => this.go({ view: 'radar' }), goFuture: () => this.go({ view: 'future' }), goCompetitors: () => this.go({ view: 'competitors' }), goScience: () => this.go({ view: 'science' }), goSources: () => this.go({ view: 'sources' }), goPeople: () => this.go({ view: 'sources', sourceGroup: 'PEOPLE' }), goResearchers: () => this.go({ view: 'sources', sourceGroup: 'PEOPLE', peopleCat: 'RESEARCHERS' }),
      // radar
      fCrop: s.fCrop, fIssue: s.fIssue, fRegion: s.fRegion, fStatus: s.fStatus, fProduct: s.fProduct, fDept: s.fDept, sort: s.sort,
      setCrop: this.sel('fCrop'), setIssue: this.sel('fIssue'), setRegion: this.sel('fRegion'), setStatus: this.sel('fStatus'), setProduct: this.sel('fProduct'), setDept: this.sel('fDept'), setSort: (e) => this.setState({ sort: e.target.value }),
      /* The product and department pickers offered Object.keys(D.PRODUCTS) (33 fixture
         names) and Object.keys(D.DEPT) (6 fixture departments) as options over a list they
         do not describe: the filter runs against the opportunity rows, so a value absent
         from those rows is a filter that can only ever return nothing. Both option lists
         are now derived from the rows being filtered, which is also how the crop, issue
         and region pickers beside them already worked. */
      radarFilters: [
        { key: 'fCrop', icon: ICO('farm-management'), accent: '#7DB41E', value: s.fCrop, set: this.sel('fCrop'), options: opts(T.allCrops, uniq(CASES.map(c => c.crop)), cl) },
        { key: 'fIssue', icon: ICO('heat-sensitive'), accent: '#9D1D96', value: s.fIssue, set: this.sel('fIssue'), options: opts(T.allIssues, uniq(CASES.map(c => c.issue)), il) },
        { key: 'fRegion', icon: ICO('cloud'), accent: '#00A0DF', value: s.fRegion, set: this.sel('fRegion'), options: opts(T.allRegions, uniq(CASES.map(c => c.region))) },
        { key: 'fStatus', icon: ICO('sun'), accent: '#F5B317', value: s.fStatus, set: this.sel('fStatus'), options: [{ v: '', l: T.allStatuses }].concat(['WINDOW_OPEN', 'NEXT_CYCLE', 'DATE_UNKNOWN', 'WINDOW_CLOSED'].map(v => ({ v, l: wst(v) }))) },
        { key: 'fProduct', icon: ICO('recycle-label'), accent: '#00698F', value: s.fProduct, set: this.sel('fProduct'), options: opts(T.allProducts, uniq([].concat.apply([], CASES.map(c => c.products || [])))) },
        { key: 'fDept', icon: ICO('connect'), accent: '#978B87', value: s.fDept, set: this.sel('fDept'), options: opts(T.allDepartments, uniq([].concat.apply([], CASES.map(c => c.departments || []))), L) }
      ].map(f => ({ icon: f.icon, value: f.value, set: f.set, options: f.options, on: !!f.value,
        /* the chip prints the label of the option currently selected; no selection is the
           "all" state, which is options[0]. Written without the find-or-first-record shape
           so it cannot be mistaken for an entity silently substituting another. */
        label: (f.options.filter(o => o.v === f.value)[0] || f.options[0] || { l: '' }).l,
        bg: f.value ? f.accent + '1F' : '#1C1817', border: f.value ? f.accent : 'rgba(203,197,195,0.16)',
        rail: f.accent, color: f.value ? '#fff' : '#D6D2D0', weight: f.value ? 700 : 500 })),
      sortIcon: ICO('sell'),
      sortLabel: ({ relevant: T.sortRelevant, closing: T.sortClosing, newest: T.sortNewest, region: T.sortRegion, crop: T.sortCrop })[s.sort] || T.sortRelevant,
      cropOptions: opts(T.fltCrops || 'All crops', uniq(CASES.map(c => c.crop)), cl), issueOptions: opts(T.fltIssues || 'All issues', uniq(CASES.map(c => c.issue)), il), regionOptions: opts(T.allRegions || 'All regions', uniq(CASES.map(c => c.region))), statusOptions: opts(T.allStatuses || 'All statuses', ['WINDOW_OPEN', 'NEXT_CYCLE', 'DATE_UNKNOWN', 'WINDOW_CLOSED'], wst), productOptions: opts(T.allProducts, uniq([].concat.apply([], CASES.map(c => c.products || [])))), deptOptions: opts(T.allDepartments, uniq([].concat.apply([], CASES.map(c => c.departments || []))), L),
      hasFilters, clearFilters: () => this.setState({ fCrop: '', fIssue: '', fRegion: '', fStatus: '', fProduct: '', fDept: '' }),
      kpis, visibleCases, visibleCount: visibleCases.length, filteredCount: filtered.length, canShowAll: filtered.length > 12, showAllLabel: s.showAll ? (T.lblShowFirst || 'SHOW FIRST 12') : (T.lblViewAllShort || 'VIEW ALL') + ' ' + filtered.length + ' ' + (T.lblOpportunities || 'OPPORTUNITIES'), toggleAll: () => this.setState({ showAll: !s.showAll }), noResults: filtered.length === 0,
      regionTiles, regionRank, recentActivity, /* Routed through sigWL so the label fields exist; the global rename to .issueL /
      // .statusL had left this loop rendering blanks. */
      topSignals: A_SIGREAL.slice().sort((a, b) => a.lastDays - b.lastDays).slice(0, 6).map(sigWL).map(x => Object.assign({}, x, { when: LAGO(x.when) })),
      // case
      cs,
      // future
      visibleSignals, futureStatusChips, futureSourceKpis,
      sigCountReal, sigCountScenario, showScenarios: s.showScenarios, hasScenarios: sigCountScenario > 0,
      scenarioToggle: { label: s.showScenarios ? T.frHideScenarios : T.frShowScenarios,
        bg: s.showScenarios ? 'rgba(245,179,23,0.16)' : 'transparent', border: s.showScenarios ? '#F5B317' : 'rgba(203,197,195,0.22)',
        color: s.showScenarios ? '#F5B317' : '#B1A9A7', go: () => this.setState({ showScenarios: !s.showScenarios, futureShown: 16 }) }, moreSignals: sigAll.length > s.futureShown, remainingSignals: Math.max(0, sigAll.length - s.futureShown), loadMoreSignals: () => this.setState({ futureShown: s.futureShown + 16 }),
      // competitors
      companies, compStrip, changed7, topMoves, cropDensity, compMoments, compTabs, compViews, compIsFeed: s.compView === 'feed', compIsGallery: s.compView === 'gallery', compIsEvents: s.compView === 'events', compIsIssue: s.compView === 'issue', feedGroups, compEmpty: actsAll.length === 0, compTotal, allStoryBorder: s.fCompany ? 'rgba(151,139,135,0.45)' : '#009845', clearCompany: () => this.setState({ fCompany: '', compShown: 12 }), whatChanged, matrix, matrixCols, upcomingEvents, eventCards, leadTimes, leadCrop, galleryItems, issueRows, goEvents: () => this.go({ view: 'competitors', compView: 'events' }),
      moreActivities: actsAll.length > s.compShown, remainingActivities: Math.max(0, actsAll.length - s.compShown), loadMoreActivities: () => this.setState({ compShown: s.compShown + 12 }),
      compCropOptions, compIssueOptions, compPeriodOptions, fPeriod: s.fPeriod, setPeriod: this.sel('fPeriod'), hasCompFilters: !!(s.fCompany || s.fType || s.fCrop || s.fIssue || s.fPeriod), clearComp: () => this.setState({ fCompany: '', fType: '', fCrop: '', fIssue: '', fPeriod: '', compShown: 12 }),
      fCompany: s.fCompany, fType: s.fType, setCompany: this.sel('fCompany'), setType: this.sel('fType'), co, isEvent: s.view === 'event', evd, isCProduct: s.view === 'cproduct', cp,
      // science
      gireShown, gireMore, gireHasMore: gireMore > 0, gireStats, gireAllOpen: !!s.gireAll, toggleGire: () => this.setState({ gireAll: !s.gireAll }),
      sciThemes, sciThemeCount: sciThemes.length, sciTotal, sciCounts, sciTop, sciResistance, sciStrategic, sciWeed, sciHasWeed: sciWeed.length > 0, sciFilter: s.sciFilter, sciClear, sciFiltered: !!s.sciFilter, sciActivityNote, hasSciImpact: !!sciImpact, sciImpact: sciImpact || {}, sciCloseImpact, records, researchers, institutions, instCount: institutions.length, th,
      // archive
      archiveQuery: s.archiveQuery, setArchiveQuery: (e) => this.setState({ archiveQuery: e.target.value, archivePage: 0 }), aType: s.aType, aCrop: s.aCrop, aRegion: s.aRegion, aCompany: s.aCompany, setAType: this.sel('aType'), setACrop: this.sel('aCrop'), setARegion: this.sel('aRegion'), setACompany: this.sel('aCompany'),
      archiveTypes, archiveTypeOpts: archiveTypes.map(v => ({ v, l: arcT(v) })), archiveTypeChips, visibleArchive, archiveCount: archAll.length, archiveFrom: archAll.length ? page * PAGE + 1 : 0, archiveTo: Math.min(archAll.length, (page + 1) * PAGE), archivePrev: () => this.setState({ archivePage: Math.max(0, page - 1) }), archiveNext: () => this.setState({ archivePage: Math.min(pages - 1, page + 1) }),
      hasArchiveFilters: !!(aq || s.aType || s.aCrop || s.aRegion || s.aCompany || s.aCase || s.aSource), clearArchive: () => this.setState({ archiveQuery: '', aType: '', aCrop: '', aRegion: '', aCompany: '', aCase: '', aSource: '', archivePage: 0 }),
      hasDrawer: !!dr, dr, closeDrawer: () => this.setState({ archiveId: null }),
      // sources
      sourceKpis, sourceGroupChips, isPeople, isNews, newsPeriodChips, newsItems, isOrgs: !isPeople && !isNews, visibleSources, peopleCatChips, visiblePeople, sr, pr,
      // search
      searchGroups, searchTotal: sHits.length
    };
  }
}
