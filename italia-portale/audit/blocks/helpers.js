  /* §22 · FIELD SALES INBOUND — THE LABELLED DEMONSTRATION, AND ONLY THAT.
     parseField() classifies a sentence a viewer types into the Integrazioni · Demo
     composer. It exists to show the routing, never to produce intelligence: its
     result is read by the Field screen alone and is never written into a
     collection, a count or a core card.
     What changed: it used to score the typed text against D.CASES (29 invented
     presentation cases) and D.COMPANIES (6 invented competitors). It now scores
     against the REAL vocabulary — the 3 upstream opportunities plus the 29
     canonical crop windows, and the 11 distinct companies actually observed in the
     monitored public communication corpus. Measured on the three example sentences
     the demo itself ships: 'olive … fruit fly' scores 5 on IT-WIN-0005
     (Olive / Olive Fruit Fly / Puglia), 'wheat … Septoria' scores 5 on IT-WIN-0014,
     and 'Bayer maize' scores 2 on IT-WIN-0002 plus the company Bayer. The
     demonstration therefore recognises MORE than it did, and every word it
     recognises is a word the real package contains.
     There is not one window.ITALY_DEMO read left in this function. */
  parseField(text) {
    const AM = this.M();
    const C = AM ? AM.collections : null;
    const T0 = (window.SINTONIA_I18N && window.SINTONIA_I18N[this.state.lang]) || {};
    const it = this.state.lang !== 'en';
    const cl = (k) => (T0.CROPS && T0.CROPS[k]) || k;
    const il = (k) => (T0.ISSUES && T0.ISSUES[k]) || k;
    const DASH = '—';
    const t = String(text || '').toLowerCase();
    /* Tokens shorter than 5 letters match half the dictionary; the old scorer used
       the same guard on Latin names and it is the reason 'mais' matches but 'ha'
       does not. Accented Italian and Portuguese letters are kept — the upstream
       package writes 'flavescência' and 'Piralide' and both must remain matchable. */
    const words = (v) => String(v || '').toLowerCase().split(/[^a-zÀ-ɏ]+/).filter((x) => x.length > 4);
    /* An opportunity is matched on its RESOLVED keys as well as its own wording.
       Measured and load-bearing: the upstream package writes IT-OPP-001 as
       'Videira' / 'Flavescência dourada …' in Portuguese, so an Italian message
       saying 'flavescenza dorata sulla vite' scored 2 against the opportunity and 5
       against canonical window IT-WIN-0001 — the demo could never reach the
       opportunity at all. The model publishes cropKeys ['Grapevine'], issueKey
       'Flavescenza Dorata' and regionKeys ['Lombardia','Veneto'] for exactly this,
       and with those in the haystack the same sentence reaches IT-OPP-001. */
    const pool = C
      ? C.opportunities.records.map((o) => ({
        id: o.id, kind: 'opportunity', issueType: o.issueType,
        /* Display the RESOLVED key when the model resolved exactly one, because the
           rest of the demo chain (T.CROPS, T.ISSUES, the crop-window lookup) is
           keyed on it — 'Grapevine' localizes to 'Vite', the upstream's own
           'Videira' localizes to nothing. Measured: 2 of 3 opportunities resolve a
           single cropKey and an issueKey; IT-OPP-003 resolves neither and keeps its
           published wording untouched. regionKeys is NOT substituted: IT-OPP-001
           resolves ['Lombardia','Veneto'] and taking [0] would drop the fact that
           the published region names Veneto as the principal one. */
        crop: (o.cropKeys && o.cropKeys.length === 1) ? o.cropKeys[0] : o.crop,
        issue: o.issueKey || o.issue, region: o.region,
        cropHay: [o.crop].concat(o.cropKeys || []), issueHay: [o.issue, o.issueKey], regionHay: [o.region].concat(o.regionKeys || []),
        primary: (o.productLinks || []).filter((l) => l.strength === 'VERIFIED_LABEL_MATCH').map((l) => l.name || l.product)[0] || null, stage: null
      }))
        .concat(C.cropWindows.records.map((r) => ({
          id: r.id, kind: 'window', crop: r.crop, issue: r.issue, region: r.region, issueType: r.issueType,
          cropHay: [r.crop], issueHay: [r.issue], regionHay: [r.region],
          primary: (r.verifiedProducts || [])[0] || null, stage: r.cropStage || null
        })))
      : [];
    /* Company names arrive twice in the corpus in two cases ('Bayer' and 'BAYER',
       measured: 14 rows collapse to 11 distinct companies). Folding them here keeps
       the demo from reporting the same competitor mention twice. */
    const seenCo = {};
    const companies = C ? C.competitorCompanies.records.reduce((a, co) => {
      const k = String(co.name || '').toUpperCase();
      if (k && !seenCo[k]) { seenCo[k] = 1; a.push(co.name); }
      return a;
    }, []) : [];
    const comp = companies.filter((n) => t.indexOf(String(n).toLowerCase()) >= 0);

    const anyWord = (hay) => (hay || []).some((v) => words(v).some((x) => t.indexOf(x) >= 0));
    const score = (r) => (anyWord(r.issueHay) ? 3 : 0) + (anyWord(r.cropHay) ? 2 : 0) + (anyWord(r.regionHay) ? 2 : 0);
    const hit = pool.map((r) => ({ r, n: score(r) })).sort((a, b) => b.n - a.n)[0];

    const signal = comp.length ? (it ? 'Menzione di un concorrente osservata' : 'Competitor mention observed')
      : /\bask|question|want|chiede|chiedono|domanda/.test(t) ? (it ? 'Domande dei clienti osservate' : 'Customer questions observed')
        : /interest|demand|option|opzion|what adama/.test(t) ? (it ? 'Interesse per un prodotto riportato' : 'Product interest reported')
          : (it ? 'Preoccupazione locale riportata' : 'Local concern reported');
    const checkLabel = (T0.PSTATE && T0.PSTATE.LABEL_CHECK_NEEDED) || 'LABEL CHECK NEEDED';

    if (!t.trim()) {
      return { issue: DASH, issueL: DASH, crop: DASH, cropL: DASH, region: DASH, signal: DASH, product: DASH,
        state: it ? 'In attesa di un messaggio' : 'Waiting for message', color: '#8F8886', caseObj: null, competitors: [] };
    }
    if (!hit || hit.n < 2) {
      const unrec = it ? 'Non riconosciuto' : 'Unrecognised';
      return { issue: unrec, issueL: unrec, crop: DASH, cropL: DASH, region: DASH, signal,
        product: checkLabel, state: 'NEEDS VALIDATION', color: '#009845', caseObj: null, competitors: comp };
    }
    const r = hit.r;
    /* A competitor named in the message is never auto-accepted; it goes to a human.
       CONNECTED needs crop AND issue AND region to line up (score 7) or crop+issue
       plus the region already implied by the record — the old threshold of 5 let a
       crop-only match call itself connected. */
    const state = comp.length ? 'NEEDS VALIDATION' : hit.n >= 5 ? 'CONNECTED' : 'NEW SIGNAL';
    /* The pest / disease / weed class is a fact: it rides on the matched record's
       own ISSUE_TYPE, so the demo message inherits a real classification. */
    const category = AM ? AM.categoryOf(r.issueType) : null;
    return {
      issue: comp.length ? (it ? 'Menzione di un concorrente · ' : 'Competitor mention · ') + comp.join(', ') : r.issue,
      issueL: comp.length ? (it ? 'Menzione di un concorrente · ' : 'Competitor mention · ') + comp.join(', ') : il(r.issue),
      crop: r.crop, cropL: cl(r.crop), region: r.region, signal,
      product: r.primary || checkLabel, state,
      color: { CONNECTED: '#009845', 'NEW SIGNAL': '#978B87', 'NEEDS VALIDATION': '#009845' }[state],
      /* Only an OPPORTUNITY id can open the opportunity screen. A canonical window
         match is a real match but it is not a case, so it carries no id and the
         composer cannot claim the message was connected to one. */
      caseObj: { id: r.kind === 'opportunity' ? r.id : null, windowId: r.kind === 'window' ? r.id : null,
        crop: r.crop, issue: r.issue, region: r.region, stage: r.stage, primary: r.primary, category },
      competitors: comp
    };
  }

  /* §3 · Every view reads the application model. ITALY_DEMO is now only the
     lowest-precedence input to that model, not the source the UI starts from. */
  D() { return window.ITALY_DEMO; }
  M() { return window.ITALY_APP_MODEL || null; }

  /* §6 · A product is an entity, not a radar filter. The model owns the key, so a
     name typed in any case opens the same entity the registry knows. */
  openProduct(name) {
    const AM = this.M();
    const e = AM && AM.findProduct ? AM.findProduct(name) : null;
    this.go({ view: 'product', productId: e ? e.key : String(name || '').trim().toUpperCase() });
  }

  /* §RT4 · NAVIGATION IS A STACK, NOT A JUMP.
     Every open* handler funnels through go(), so go() is the only place that has to
     remember where the user was. The snapshot is the whole previous state minus the
     stack itself, which is what makes back() restore filters and scroll targets and
     not just the view name. Depth is capped at 20 so a long session cannot grow the
     state object without bound. */
  go(patch) {
    const s = this.state || {};
    const snap = {};
    for (const k in s) if (k !== 'navHistory') snap[k] = s[k];
    const hist = (s.navHistory || []).concat([snap]).slice(-20);
    this.setState(Object.assign({ archiveId: null, showNotifs: false }, patch, { navHistory: hist }));
    if (typeof window !== 'undefined' && window.scrollTo) window.scrollTo(0, 0);
  }
  back() {
    const s = this.state || {};
    const hist = (s.navHistory || []).slice();
    const prev = hist.pop();
    if (!prev) return false;
    this.setState(Object.assign({}, prev, { navHistory: hist }));
    if (typeof window !== 'undefined' && window.scrollTo) window.scrollTo(0, 0);
    return true;
  }
  goBack() { return this.back(); }
  canGoBack() { return ((this.state || {}).navHistory || []).length > 0; }

  /* §6b · An entity route resolves against the model first. The portal still holds
     screens fed by the fixture, whose ids live in a different id space (SRC-01 vs
     IT-SRC-MINISTERO, RR-01 vs IT-PER-001), so an id the model does not know is
     passed through untouched instead of being swallowed — a dead link is visible,
     a silently ignored click is not. */
  _resolveId(records, id, alt) {
    const k = String(id || '').trim().toUpperCase();
    if (!k || !records) return id;
    for (const r of records) {
      if (String(r.id || '').toUpperCase() === k) return r.id;
      if (alt && String(r[alt] || '').toUpperCase() === k) return r.id;
    }
    return id;
  }
  openCase(id) {
    const C = this.M() ? this.M().collections : null;
    this.go({ view: 'case', caseId: C ? this._resolveId(C.opportunities.records, id, 'legacyCaseId') : id });
  }
  /* Line 2388 declares openWindow too; a class body keeps the LAST definition, so
     this one wins. The earlier declaration is now dead and should be deleted. */
  openWindow(id) {
    const C = this.M() ? this.M().collections : null;
    this.go({ view: 'window', windowId: C ? this._resolveId(C.cropWindows.records, id, 'legacyCaseId') : id });
  }
  openCompany(name) { this.go({ view: 'company', companyId: name }); }
  openTheme(id) {
    const C = this.M() ? this.M().collections : null;
    this.go({ view: 'theme', themeId: C ? this._resolveId(C.scienceThemes.records, id) : id });
  }
  openPerson(id) {
    const C = this.M() ? this.M().collections : null;
    const people = C ? C.researchers.records.concat(C.publicPeople.records) : null;
    this.go({ view: 'person', personId: people ? this._resolveId(people, id) : id });
  }
  openSource(id) {
    const C = this.M() ? this.M().collections : null;
    this.go({ view: 'source', sourceId: C ? this._resolveId(C.sources.records, id, 'sourceId') : id });
  }
  radarWith(f) { this.go(Object.assign({ view: 'radar', fCrop: '', fIssue: '', fRegion: '', fStatus: '', fProduct: '', fDept: '', showAll: true }, f)); }
  archiveWith(f) { this.go(Object.assign({ view: 'archive', archiveQuery: '', aType: '', aCrop: '', aRegion: '', aCompany: '', aCase: '', aSource: '', archivePage: 0 }, f)); }
  sel(key) { return (e) => this.setState({ [key]: e.target.value, showAll: true, archivePage: 0, compShown: 12 }); }

  /* §12 · THE ONE CARD DECORATOR, NOW SHAPE-TOLERANT.
     decorate() has to survive three record shapes at once, because the screens that
     feed it are being migrated one at a time:
       · the legacy presentation case  — Date objects, a fixture category, 40 props
       · a real opportunity            — 3 records, ISO-free, canonicalWindow null 3/3
       · a canonical crop window       — 29 records, ISO strings, ISSUE_TYPE 29/29
     Two rules hold across all three: it never throws on the thin shape, and it never
     invents a field the thin shape lacks. Every derived label falls back to a
     neutral token, never to a plausible guess.
     It also stopped MUTATING its argument. The old Object.assign(c, …) wrote 30
     presentation props onto whatever it was handed — which for a real record means
     writing UI state into AM.collections. It returns a copy now; verified idempotent
     because every value it reads is a raw source prop, never one it wrote. */
  decorate(c0) {
    const c = c0 || {};
    const AM = this.M();
    const T0 = (window.SINTONIA_I18N && window.SINTONIA_I18N[this.state.lang]) || {};
    const CW = c.canonicalWindow || c.canonical || null;
    const raw = (k, K) => (c[k] !== undefined && c[k] !== null ? c[k] : CW ? (CW[k] !== undefined && CW[k] !== null ? CW[k] : CW[K]) : null);

    /* §7 · pest / disease / weed is a CLASSIFICATION, therefore a fact. It comes
       from the canonical ISSUE_TYPE through AM.categoryOf and never from a colour
       table. Measured before the swap: on all 29 presentation cases the fixture's
       own `cat` agrees with the canonical ISSUE_TYPE 29/29, so not one card changes
       colour today — what changes is where the class comes from. A record with no
       ISSUE_TYPE resolves to the neutral token, whose label is null on purpose. */
    const issueType = c.issueType || (CW && (CW.issueType || CW.ISSUE_TYPE)) || null;
    const catUi = AM ? AM.categoryOf(issueType) : null;
    /* The markup writes the icon straight into url(); the model publishes the icon
       NAME in .icon and the asset path in .iconAsset, so the path is what a card
       needs. Pure presentation, no fact crosses here. */
    const category = catUi
      ? Object.assign({}, catUi, { icon: catUi.iconAsset || '' })
      : { key: 'unknown', label: null, color: '#8F8886', dark: '#3A3533', soft: '#B1A9A7', ink: '#fff', body: '#EDEAE9', muted: '#B1A9A7', icon: '', iconAsset: '' };
    const col = category.color;

    /* Date labels are presentation, so they are rebuilt per render rather than
       frozen at load — that is what lets the language switch without a reload. */
    const MON = T0.months || ['GEN', 'FEB', 'MAR', 'APR', 'MAG', 'GIU', 'LUG', 'AGO', 'SET', 'OTT', 'NOV', 'DIC'];
    const asD = (v) => {
      if (!v) return null;
      if (v instanceof Date) return isNaN(v.getTime()) ? null : v;
      if (typeof v !== 'string') return null;
      return AM && AM.asDate ? AM.asDate(v) : null;
    };
    const dfmt = (d) => (d ? String(d.getDate()).padStart(2, '0') + ' ' + MON[d.getMonth()] : null);
    const ws = asD(c.windowStart) || asD(raw('startDate', 'START_DATE'));
    const we = asD(c.windowEnd) || asD(raw('endDate', 'END_DATE'));
    const REF = AM ? AM.REF : null;
    const UNK_DATE = (T0.WSTATE && T0.WSTATE.DATE_UNKNOWN) || (T0.WSTATUS && T0.WSTATUS.DATE_UNKNOWN) || '—';

    /* §4 · Status TINT only. The status CODE is upstream's (CURRENT_STATUS) and the
       presentation layer may never derive ACT NOW / WINDOW OPEN / NEXT CYCLE. A
       record whose upstream status is null gets the neutral token and an empty
       label — an empty pill is honest, a guessed pill is not. Measured: status is
       null on 3/3 real opportunities, because none of the three joins to a
       canonical window (windowId null 3/3). */
    const UI = AM && AM.UI ? AM.UI : null;
    /* The model owns the tint table (AM.UI.STATUS); the local copy is only the
       fallback for the legacy status wording the fixture used before the canonical
       codes landed, and for the case where AM.UI is momentarily absent. */
    const ST_LEGACY = {
      'ACT NOW': { color: '#00783F', text: '#00B152', rank: 0 },
      'ACTION WINDOW OPENING': { color: '#00783F', text: '#00B152', rank: 1 },
      PREPARE: { color: '#00783F', text: '#00B152', rank: 2 },
      WATCH: { color: '#978B87', text: '#B1A9A7', rank: 3 },
      VALIDATE: { color: '#978B87', text: '#B1A9A7', rank: 4 },
      'NEXT CYCLE': { color: '#6E6663', text: '#8F8886', rank: 5 }
    };
    const status = raw('status', 'CURRENT_STATUS');
    /* rank is a SORT key read by the radar sorter; an unknown status must sort last,
       never first, so it does not jump the queue it was never assessed for. */
    const stNeutral = (UI && UI.STATUS && UI.STATUS.DEFAULT) || { color: '#978B87', text: '#B1A9A7', rank: 9 };
    const st = (c.st && typeof c.st === 'object') ? c.st
      : ((UI && UI.STATUS && UI.STATUS[status]) || ST_LEGACY[status] || stNeutral);
    const statusLabel = status ? ((T0.WSTATUS && T0.WSTATUS[status]) || (this._L ? this._L(status) : status) || String(status).replace(/_/g, ' ')) : '';
    /* Openness is READ from the upstream enum, never computed from today's date.
       `=== true` and not a truthy test on purpose: a canonical window publishes a
       boolean `open` (6/29 are open), while a decorated card publishes an `open`
       CLICK HANDLER under the same name, and a function is truthy. */
    const windowOpen = c.windowOpen === true || c.open === true || status === 'WINDOW_OPEN' || status === 'ACT_NOW';
    const daysLeft = typeof c.daysLeft === 'number' ? c.daysLeft
      : (we && REF) ? Math.round((we - REF) / 864e5) : null;

    /* §7 (product law) · Presentation MAY compute a pixel position from supplied
       dates. It may not draw a bar for a window whose dates nobody supplied, so a
       dateless record gets 0% — a bar of zero width, not a bar of invented width. */
    const progress = typeof c.progress === 'number' ? c.progress
      : (windowOpen && ws && we && REF && we > ws) ? Math.max(0, Math.min(100, Math.round((REF - ws) / (we - ws) * 100)))
        : 0;

    /* windowLine arrives as a CODE ('WINDOW_CLOSED', '43|daysRemaining'). The old
       decorator localized it into windowLineL but passed the raw code through as
       `windowLine` — and markup line 312 binds cs.windowLine, so the Italian case
       screen was printing the literal string WINDOW_CLOSED. Both names now carry
       the localized text. */
    const wline = (() => {
      const v = c.windowLine;
      if (!v) return '';
      if (v === 'DATE_TO_CONFIRM') return (T0.WSTATUS && T0.WSTATUS.DATE_UNKNOWN) || 'DATE TO CONFIRM';
      if (v === 'WINDOW_CLOSED') return (T0.WSTATUS && T0.WSTATUS.WINDOW_CLOSED) || 'WINDOW CLOSED';
      const p = String(v).split('|');
      return p.length === 2 ? p[0] + ' ' + (p[1] === 'daysRemaining' ? (T0.wDaysRemaining || 'days remaining') : (T0.wDaysToOpen || 'days to open')) : v;
    })();

    /* §19 · Product links. The relationship graph is the only authority, and the
       model now publishes the resolved verdict on the record itself — so when
       record.productLinks exists it is taken as-is and nothing is recomputed here.
       Measured on IT-OPP-001: 6 links, 4 LABEL_CHECK_NEEDED and 2
       VERIFIED_LABEL_MATCH, resolved through cropKey 'Grapevine' even though the
       opportunity writes its crop as 'Videira'.
       The fallback below only runs for a record that names ADAMA products with no
       resolved links. It asks AM.strengthFor, with one guard: strengthFor returns
       NO_CONFIRMED_MATCH_CURRENT_READING both when the label was read and the use
       was not found AND when the crop word is simply outside the relationship
       vocabulary. The second case is a vocabulary gap, not an absence, and printing
       absence there would be a false negative on a real ADAMA product — so it
       downgrades to LABEL_CHECK_NEEDED, the model's own declared fallback. */
    const strengthOf = (name, crop, issue) => {
      if (!AM || !AM.strengthFor) return 'LABEL_CHECK_NEEDED';
      const v = AM.strengthFor(name, crop, issue);
      if (v !== 'NO_CONFIRMED_MATCH_CURRENT_READING') return v;
      const e = AM.findProduct ? AM.findProduct(name) : null;
      const known = e && (e.links || []).some((l) => String(l.crop || '').toUpperCase() === String(crop || '').toUpperCase());
      return known ? v : 'LABEL_CHECK_NEEDED';
    };
    /* A canonical window carries the 163-label audit's own two verdict lists rather
       than a link array. Measured: 12/29 windows name at least one verified product
       and several name products the audit read and did NOT find — §10 says a
       not-found product is shown as NOT CONFIRMED IN THIS READING, never hidden and
       never rewritten as "ADAMA has no product". */
    const verdictLinks = []
      .concat((Array.isArray(c.verifiedProducts) ? c.verifiedProducts : []).map((n) => ({ name: n, strength: 'VERIFIED_LABEL_MATCH' })))
      .concat((Array.isArray(c.notFoundProducts) ? c.notFoundProducts : []).map((n) => ({ name: n, strength: 'NO_CONFIRMED_MATCH_CURRENT_READING' })));
    const links = Array.isArray(c.productLinks) && c.productLinks.length ? c.productLinks
      : verdictLinks.length ? verdictLinks
        : (Array.isArray(c.adamaProducts) ? c.adamaProducts : []).map((n) => ({ name: n, strength: strengthOf(n, c.crop, c.issue) }));
    const rankOf = (k) => (AM && AM.STRENGTH && AM.STRENGTH[k] ? AM.STRENGTH[k].rank : 9);
    const objOf = (l) => l.obj || (AM && AM.findProduct ? AM.findProduct(l.name || l.product) : null);
    const verified = links.filter((l) => l.strength === 'VERIFIED_LABEL_MATCH');
    /* A canonical window publishes its audited matches directly (measured: 3 of the
       first 5 windows carry one or two verified products). */
    const primary = c.primary || (verified[0] ? (verified[0].name || verified[0].product) : null)
      || (Array.isArray(c.verifiedProducts) ? c.verifiedProducts[0] : null) || null;
    /* The card's portfolio state is the BEST verdict among the links, not the first
       one in array order — IT-OPP-001 lists four LABEL_CHECK_NEEDED before its two
       VERIFIED matches, and reading links[0] would have understated it. */
    const bestStrength = links.length ? links.slice().sort((a, b) => rankOf(a.strength) - rankOf(b.strength))[0].strength : null;
    const portfolioState = c.portfolioState || c.labelVerdictState || bestStrength || null;
    const primaryObj = verified[0] ? objOf(verified[0]) : (primary && AM && AM.findProduct ? AM.findProduct(primary) : null);
    const aiText = (v) => (Array.isArray(v) ? v.join(' + ') : v) || null;
    const primaryAi = c.primaryAi || (primaryObj ? aiText(primaryObj.ai) : null);
    /* The registry publishes several actives per product, so "+ N more" counts the
       links the model actually resolved. Falling through to the literal 'single
       match' on a record with 6 links, as the old code did, understated the card. */
    const moreMatches = typeof c.moreMatches === 'number' ? c.moreMatches : Math.max(0, links.length - 1);

    return Object.assign({}, c, {
      category, st,
      wsLabel: dfmt(ws) || UNK_DATE,
      weLabel: dfmt(we) || UNK_DATE,
      cropL: (T0.CROPS && T0.CROPS[c.crop]) || c.crop || '',
      issueL: (T0.ISSUES && T0.ISSUES[c.issue]) || c.issue || '',
      regionLabel: c.regionLabel || c.region || '',
      statusL: statusLabel, statusLabel,
      dateStateL: (() => { const d = raw('dateState', 'DATE_STATE'); return d ? ((T0.DSTATE && T0.DSTATE[d]) || String(d).replace(/_/g, ' ')) : ''; })(),
      stageL: c.stage ? ((T0.OBSCLASS && T0.OBSCLASS[c.stage]) || String(c.stage).replace(/_/g, ' ')) : '',
      signalL: c.signal ? ((T0.OBSCLASS && T0.OBSCLASS[c.signal]) || String(c.signal).replace(/_/g, ' ')) : '',
      windowLine: wline, windowLineL: wline,
      windowOpen, daysLeft, progress, progressPct: progress + '%',
      open: () => this.openCase(c.id),
      when: (this._LAGO ? this._LAGO(c.when) : c.when) || '',
      agoLabel: (this._LAGO ? this._LAGO(c.ago) : c.ago) || '',
      /* The old expression fed c.we — a raw day OFFSET, measured 28 on IT-OPP-006
         whose real remainder is 43 — into a "days remaining" phrase. daysLeft is the
         field that actually means days remaining. */
      remainLabel: (windowOpen && typeof daysLeft === 'number' && this._LDAYS) ? this._LDAYS(daysLeft) : (c.remainingLabel || ''),
      updatedLabel: (this._LAGO && c.updatedLabel)
        ? String(c.updatedLabel).replace(/^Updated /, (this.state.lang === 'it' ? 'Aggiornato ' : 'Updated ')).replace(/(\d+)d ago/, this.state.lang === 'it' ? '$1g fa' : '$1d ago').replace(/^Updated today$/, this.state.lang === 'it' ? 'Aggiornato oggi' : 'Updated today')
        : (c.updatedLabel || ''),
      actions: (c.actions || []).map((a) => Object.assign({}, a, { dept: this._L ? this._L(a.dept) : a.dept, deptLabel: this._L ? this._L(a.dept) : a.dept })),
      departments: (c.departments || []).map((d) => (this._L ? this._L(d) : d)),
      evidenceLabel: c.evidenceLabel ? (this._L ? this._L(c.evidenceLabel) : c.evidenceLabel) : '',
      bg: category.dark, heroBg: category.dark,
      borderCol: col + '66', iconBg: col + '3A',
      /* An unclassified record hides the category chip instead of printing a guess.
         hasCategory is the flag markup 219 and 221 must gate on — until that guard
         lands, an unknown record renders an EMPTY neutral tab, never a wrong one. */
      hasCategory: !!category.label,
      catLabel: category.label ? String(this._L ? this._L(category.label) : category.label).toUpperCase() : '',
      /* §10 · Field Sales is a demo module and may not badge a core card. Measured:
         18 synthetic WhatsApp records mapped onto 8 case ids; nothing real replaces
         them. Forcing hasField false makes the sc-if at markup 238 drop the badge
         without touching the layout. The Field screen builds its own count. */
      hasField: false,
      primaryLabel: primary || ((T0.PSTATE && T0.PSTATE[portfolioState]) || (T0.PSTATE && T0.PSTATE.LABEL_CHECK_NEEDED) || 'LABEL CHECK NEEDED'),
      primaryAiL: primaryAi === 'AI_NOT_APPLICABLE' ? (T0.aiNotApplicable || 'active ingredient not applicable') : (primaryAi || ''),
      portfolioStateL: portfolioState ? ((T0.PSTATE && T0.PSTATE[portfolioState]) || String(portfolioState).replace(/_/g, ' ')) : '',
      /* §10 (product law) · Absence in this reading is not absence in the world —
         printed only when the model itself downgraded the primary. */
      portfolioNote: (c.primaryDowngraded || bestStrength === 'NO_CONFIRMED_MATCH_CURRENT_READING')
        ? (c.absenceRule || T0.absenceRule || (AM && AM.ABSENCE_RULE) || 'Absence in this reading is not absence in the world.') : '',
      productLinksL: links.map((l) => ({
        name: l.name || l.product, ai: aiText((objOf(l) || {}).ai), strength: l.strength,
        strengthL: (T0.PSTATE && T0.PSTATE[l.strength]) || String(l.strength).replace(/_/g, ' '),
        color: (AM && AM.STRENGTH && AM.STRENGTH[l.strength]) ? AM.STRENGTH[l.strength].color : '#B1A9A7'
      })),
      /* No primary means no count to show. The old else-branch returned the raw
         dictionary key 'portfolio', which rendered as visible English on every
         rejected card. */
      moreLabel: primary ? (moreMatches ? (this._LMORE ? this._LMORE(moreMatches) : '+ ' + moreMatches + ' more') : (this._L ? this._L('single match') : 'single match')) : '',
      /* The badge asset follows the classification, so it can no longer default to
         'disease-control' for a record nobody classified. */
      badgeVariant: category.icon ? category.key + '-control' : ''
    });
  }
