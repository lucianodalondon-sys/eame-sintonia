    // ---- competitors
    /* §1 · Competitor Watch now reads the model, not the fixture. Measured:
       AM.collections.competitorActivities = 503 records, real 503 / demo 0, against
       the 72 fabricated D.ACTIVITIES rows it used to serve. The real type space is
       PAID 414 and ORGANIC_VIDEO 89 — there is no VIDEO, PEOPLE, EVENT or
       PRODUCT/PORTFOLIO type at all, so four of the six tabs and four of the six
       company count tiles have no content and are gone. */
    const CX = (k) => (APP0 && APP0[k]) ? APP0[k] : { records: [], count: 0 };
    const CACT = CX('competitorActivities');
    const CACTS = CACT.records;
    const CCOS = CX('competitorCompanies').records;
    const CPRD = CX('competitorProducts');
    const CPRODUCTS = CPRD.records;
    const CDENS = CX('competitorCropDensity');
    const CISS = CX('competitorIssueDensity');
    const CMX = CX('competitorMatrix');
    const CWM = CX('competitorWindowMoments').records;
    const CEVENTS = CX('futureEvents').records;
    const EN = s.lang === 'en';
    const TX = (it, en) => (EN ? en : it);
    /* THE NARRATIVE RULE · upstream prose is a Portuguese working note unless an
       approved localized variant exists. Measured on the event family: 18/18 NOTE
       and 18/18 PARTICIPATION_LAW arrive NOT_APPROVED_FOR_DISPLAY, so the event
       profile renders no prose at all today. */
    const cNar = (n) => (n && n.state === 'CLEAR') ? (EN ? (n.en || n.it) : (n.it || n.en)) : null;
    const uq = (a) => a.filter((v, i) => v !== null && v !== undefined && v !== '' && a.indexOf(v) === i);
    const UPC = (v) => String(v === null || v === undefined ? '' : v).trim().toUpperCase();
    const NODATE = TX('DATA NON OSSERVATA', 'DATE NOT OBSERVED');
    const NOTKNOWN = TX('NON NOTO', 'NOT KNOWN');

    /* §4 · presentation tokens only. The class itself is the record's own `type`. */
    const COMPCH = {
      'PAID': { c: CH['PAID'].c, t: CH['PAID'].t || CH['PAID'].c, i: CH['PAID'].i, n: T.chPaid || 'PAID' },
      'ORGANIC_VIDEO': { c: CH['VIDEO'].c, t: CH['VIDEO'].t || CH['VIDEO'].c, i: CH['VIDEO'].i, n: TX('VIDEO ORGANICO', 'ORGANIC VIDEO') }
    };
    const PLATL = { 'META_ADS_LIBRARY': 'Meta Ad Library', 'YOUTUBE': 'YouTube' };
    /* active is an upstream enum, not a boolean: ACTIVE 27 · INACTIVE 385 ·
       NOT_KNOWN 2 · absent on the 89 organic records. */
    const ADSTATE = { 'ACTIVE': TX('ATTIVO', 'ACTIVE'), 'INACTIVE': TX('NON ATTIVO', 'INACTIVE'), 'NOT_KNOWN': NOTKNOWN };
    const MONN = T.months || ['GEN', 'FEB', 'MAR', 'APR', 'MAG', 'GIU', 'LUG', 'AGO', 'SET', 'OTT', 'NOV', 'DIC'];
    const dLabel = (iso) => { const dd = AM ? AM.asDate(iso) : null; return dd ? (String(dd.getDate()).padStart(2, '0') + ' ' + MONN[dd.getMonth()] + ' ' + dd.getFullYear()) : null; };
    const monthKey = (iso) => { const dd = AM ? AM.asDate(iso) : null; return dd ? (MONN[dd.getMonth()] + ' ' + dd.getFullYear()) : null; };
    /* One clock. daysFromRef is negative in the past; a record with no start date is
       never placed at day 0 — it goes to an explicit DATA NON OSSERVATA bucket.
       Measured horizon: 1 record inside 7 days, 11 inside 30, 40 inside 60. The
       7-day promise the old strip made is a single record out of 503, which is why
       every recency widget here reads 30 days and says so in its own label. */
    const within = (a, n) => a.hasDate && a.daysFromRef !== null && a.daysFromRef <= 0 && a.daysFromRef >= -n;
    const OBS_WINDOW = 30;
    const STRANK = { 'WINDOW_OPEN': 0, 'NEXT_CYCLE': 1, 'DATE_UNKNOWN': 2, 'WINDOW_CLOSED': 3 };
    const STCOLOR = (k) => k === 'WINDOW_OPEN' ? '#00B152' : k === 'NEXT_CYCLE' ? '#00A0DF' : k === 'DATE_UNKNOWN' ? '#F5B317' : '#978B87';

    /* Presentation for one observed activity. It decorates; it derives no fact.
       Gone against the old actDeco(): headline, region, newly, duration,
       transcriptLabel, person*, event*, the timing verdict, the ADAMA RESPONSE
       verdict, the market temperature and caseId — not one of them exists on a
       real record. */
    const cAct = (a) => {
      const ch = COMPCH[a.type] || COMPCH['PAID'];
      const crops = a.cropsCanonical || [];
      const paid = a.type === 'PAID';
      const prodList = a.products || [];
      /* §7 + §13 · a shared crop name is not a relationship. A window link needs a
         canonical crop AND a species-level issue term equal to the window's own
         ISSUE_NAME. Measured: 30 of 503 records carry a species-level term, only 11
         carry one together with a resolved crop, and none of the 9 distinct terms
         equals a canonical ISSUE_NAME (the advertiser writes 'Plasmopara viticola',
         the window says 'Downy Mildew') — so this resolves for 0 of 503 records
         today. It is deliberately NOT relaxed to crop-only matching. */
      const relWin = ((a.speciesIssues || []).length && crops.length)
        ? (CWM.find(x => crops.indexOf(x.crop) >= 0 && (a.speciesIssues || []).some(i => UPC(i) === UPC(x.issue))) || null) : null;
      const verified = relWin ? (relWin.portfolioVerified || []) : [];
      return {
        id: a.id, type: a.type, company: a.company,
        /* the observed page name is real (414/503). On the 89 organic records there
           is none and the bare company name shows — no legal entity is invented. */
        companyLabel: a.displayName,
        platform: PLATL[a.platform] || a.platform,
        platformShort: PLATL[a.platform] || a.platform,
        typeL: ch.n,
        chColor: ch.c, chText: ch.t, chName: ch.n, chTint: ch.c + '18', chIcon: 'assets/icons/' + ch.i + '-white.png',
        /* tint only; the PAID / ORGANIC_VIDEO class itself is the record's own type
           field, and no fixture is read to produce it. */
        creativeBg: ch.c + '2E',
        /* uniform: the old height varied with a.days purely to imitate a creative
           wall. No creative asset is captured for any of the 503 records. */
        galleryH: '150px',
        when: a.hasDate ? dLabel(a.startDate) : NODATE,
        hasDate: !!a.hasDate,
        /* §9 · REACHED_IN_ITALY (414) may never read as TARGETED_ITALY, and the 89
           multi-country / unresolved records are never promoted into Italy. */
        countryL: a.geoClass === 'REACHED_IN_ITALY' ? ((T.PROV && T.PROV.REACHED_IN_ITALY) || 'REACHED IN ITALY') : TX('MULTIPAESE / NON RISOLTO', 'MULTI-COUNTRY / UNRESOLVED'),
        geoCaveat: a.geoCaveat || '',
        active: ADSTATE[UPC(a.active)] || NOTKNOWN,
        /* the advertiser's own public copy, verbatim and quoted (392/503, average 239
           characters). It is evidence — never parsed for a crop, an issue, a product
           or a claim, and never rewritten into a Sintonia headline. */
        headline: a.textExcerpt ? ('«' + a.textExcerpt + '»') : '',
        product: prodList[0] || '', hasProduct: !!prodList.length,
        crops, cropL: crops.map(cl).join(' · '), hasCrop: !!crops.length,
        /* §11 · the issue term is the advertiser's own word, rendered verbatim.
           il() would rewrite 'Plasmopara viticola' into a Sintonia label. */
        issues: a.issuesObserved || [], issueL: (a.issuesObserved || []).join(' · '), hasIssue: !!(a.issuesObserved || []).length,
        /* the badge slot no longer says NEWLY OBSERVED — there is no first-seen
           timestamp to diff against, only the advertiser's own start date. It
           carries the reach-is-not-targeting caveat instead. */
        hasNewly: paid, newly: TX('RAGGIUNTO ≠ TARGETIZZATO', 'REACHED ≠ TARGETED'),
        isPaid: paid, isOrganic: a.type === 'ORGANIC_VIDEO',
        isVideo: false, isPeople: false, isEvent: false,
        hasWindow: !!relWin,
        timing: relWin ? wst(relWin.status) : TX('NON VALUTABILE', 'NOT ASSESSABLE'),
        timingColor: relWin ? STCOLOR(relWin.status) : '#8F8886',
        leadLabel: relWin ? (cl(relWin.crop) + ' · ' + il(relWin.issue) + ' · ' + relWin.region)
          : TX('il record non dichiara coltura e avversità a livello di specie', 'the record states no crop and no species-level pest'),
        windowLabel: relWin ? (il(relWin.issue) + ' · ' + relWin.region) : '',
        goWindow: () => relWin && this.openWindow(relWin.windowId),
        /* §10 · the portfolio side comes from the label audit through the model, never
           from a demo case list. When the record cannot even name a crop and a pest
           the question is not askable, and the tile says that instead of answering it. */
        adamaResponse: !relWin ? TX('NON VALUTABILE', 'NOT ASSESSABLE')
          : verified.length ? TX('CORRISPONDENZA VERIFICATA SU ETICHETTA', 'VERIFIED LABEL MATCH')
          : TX('NESSUNA CORRISPONDENZA CONFERMATA IN QUESTA LETTURA', 'NO CONFIRMED MATCH IN THIS READING'),
        adamaColor: verified.length ? '#00B152' : '#B1A9A7',
        adamaProducts: !relWin ? TX('coltura e avversità non dichiarate nel record pubblico', 'crop and pest not stated in the public record')
          : verified.length ? verified.join(' + ') : (relWin.absenceRule || T.absenceRule || ''),
        /* a market temperature used to be stamped on every card from a crop that
           325 of 503 records do not have. The line is a link to the Market domain now,
           not a reading. */
        marketTemp: TX('VEDI →', 'VIEW →'), marketColor: '#8F8886',
        goMarket: () => this.go({ view: 'market' }),
        ctaL: a.url ? TX('VEDI ANNUNCIO →', 'VIEW AD →') : '',
        openCase: () => { if (a.url && typeof window !== 'undefined' && window.open) window.open(a.url, '_blank', 'noopener'); },
        openCompany: () => this.openCompany(a.company),
        openProduct: () => prodList[0] && this.openCProduct(prodList[0]),
        productOrHeadline: prodList[0] || TX('ASSET CREATIVO NON CATTURATO', 'CREATIVE ASSET NOT CAPTURED'),
        initials: initials(a.company || '')
      };
    };

    /* §1 · The 14 upstream company rows are 11 companies — the paid rows are
       title-case and the organic rows upper-case. The model merges them on the
       upper-case key and publishes both counters, and every merged total equals its
       activity count (BASF 138, FMC 102, Corteva 94, Bayer 86, Syngenta 55, UPL 13,
       Sipcam 6, Certis 4, Sumitomo 2, Gowan 2, Nufarm 1 = 503). */
    const actsOfKey = (key) => CACTS.filter(a => a.companyKey === key);
    const companies = CCOS.map(c2 => ({
      name: c2.name, label: c2.name, id: c2.name, key: c2.key,
      initials: initials(c2.name),
      count: c2.observedActivities, paid: c2.paidAdsReachingIt, organic: c2.organicVideosInCorpus,
      pages: c2.pages, crops: (c2.cropsObserved || []).map(cl),
      /* the advertiser's own issue words for this company, verbatim; the global
         search index reads them, so they must exist even when the array is empty. */
      issues: uq([].concat.apply([], actsOfKey(c2.key).map(a => a.issuesObserved || []))),
      /* a company "confidence" grade has no counterpart in COMP_COMPANIES; the header
         states the observation basis instead of a made-up score. */
      confidence: TX('COMUNICAZIONE PUBBLICA OSSERVATA', 'OBSERVED PUBLIC COMMUNICATION'),
      /* 5 companies (Sipcam, Certis, Sumitomo, Nufarm, Gowan) have no dated record at
         all: that reads DATA NON OSSERVATA and a dash, never 0. */
      last: c2.lastObserved ? dLabel(c2.lastObserved) : NODATE,
      first: c2.firstObserved ? dLabel(c2.firstObserved) : NODATE,
      recent30: c2.datedActivities ? c2.observedLast30 : '—',
      /* 6 tiles become 2. */
      countRows: [{ n: c2.paidAdsReachingIt, label: T.chPaid || 'PAID', go: () => this.compWith({ fCompany: c2.name, fType: 'PAID' }) },
                  { n: c2.organicVideosInCorpus, label: TX('VIDEO ORGANICI', 'ORGANIC VIDEOS'), go: () => this.compWith({ fCompany: c2.name, fType: 'ORGANIC_VIDEO' }) }],
      productObjs: (c2.products || []).slice().sort((x, y) => (y.activityCount || 0) - (x.activityCount || 0)).map(p2 => ({ name: p2.name, count: p2.activityCount, go: () => this.openCProduct(p2.name) })),
      /* Bayer has 86 observed items and 0 proven products. An empty box would read as
         "no products", so the state travels with it. */
      productsNote: c2.productState === 'PRODUCTS_PROVED' ? '' : TX('NESSUN PRODOTTO PROVATO IN QUESTA LETTURA', 'NO PRODUCT PROVED IN THIS READING'),
      /* content themes and company→case links have no real counterpart at all. */
      themes: [], cases: [],
      /* PARTICIPATION_LAW: a company without a line is NOT KNOWN, and future
         participation is never inferred from a past edition. Measured: all 14
         populated participation maps name ADAMA only, and exactly one event (Enovitis in
         Campo 2026) names a competitor at all — so this column is NON NOTO almost
         everywhere, which is the honest answer. The upstream confirmation sentence
         is a Portuguese research note and is never rendered; only the state is. */
      eventRows: CEVENTS.map(e2 => { const on = (e2.confirmedParticipationList || []).some(k2 => UPC(k2) === UPC(c2.name)); return { name: e2.name, state: on ? TX('CONFERMATO', 'CONFIRMED') : NOTKNOWN, color: on ? '#00B152' : '#B1A9A7', go: () => this.openEvent(e2.id) }; }),
      storyBorder: s.fCompany === c2.name ? '#009845' : 'rgba(151,139,135,0.45)',
      go: () => this.openCompany(c2.name),
      filter: () => this.setState({ fCompany: s.fCompany === c2.name ? '' : c2.name, compShown: 12 })
    }));

    /* §1 · the feed. fType is PAID / ORGANIC_VIDEO, fCrop is a canonical crop and
       fIssue is an observed term verbatim. A period filter only ever selects dated
       records; an undated record is excluded from it, never dated at 0. */
    const actsAll = CACTS.filter(a => (!s.fCompany || a.company === s.fCompany)
      && (!s.fType || a.type === s.fType)
      && (!s.fCrop || (a.cropsCanonical || []).indexOf(s.fCrop) >= 0)
      && (!s.fIssue || (a.issuesObserved || []).indexOf(s.fIssue) >= 0)
      && (!s.fPeriod || within(a, Number(s.fPeriod))))
      .sort((a, b) => (b.hasDate ? b.daysFromRef : -1e9) - (a.hasDate ? a.daysFromRef : -1e9));
    const compTabs = [['', TX('TUTTI', 'ALL')], ['PAID', T.chPaid || 'PAID'], ['ORGANIC_VIDEO', TX('VIDEO ORGANICI', 'ORGANIC VIDEOS')]].map(t2 => { const on = s.fType === t2[0] && s.compView === 'feed'; return { label: t2[1], count: CACTS.filter(a => (!t2[0] || a.type === t2[0]) && (!s.fCompany || a.company === s.fCompany)).length, color: on ? '#fff' : '#B1A9A7', bg: on ? 'rgba(0,152,69,0.25)' : 'transparent', border: on ? '#009845' : 'rgba(203,197,195,0.2)', go: () => this.setState({ fType: t2[0], compView: 'feed', compShown: 12 }) }; });
    const compViews = [['gallery', TX('RECORD PUBBLICITARI', 'AD RECORDS')], ['events', T.lblEventWatch || 'EVENT WATCH'], ['issue', TX('PER AVVERSITÀ', 'BY ISSUE')]].map(v2 => { const on = s.compView === v2[0]; return { label: v2[1], color: on ? '#fff' : '#B1A9A7', bg: on ? 'rgba(0,152,69,0.25)' : 'transparent', border: on ? '#009845' : 'rgba(203,197,195,0.2)', go: () => this.setState({ compView: on ? 'feed' : v2[0] }) }; });
    /* Grouped by observation month, plus one explicit group for the 89 records with
       no start date. They are real and counted; they simply cannot be placed on a
       timeline, so they are never folded into a dated group. */
    const groupOf = (a) => a.hasDate ? (monthKey(a.startDate) || NODATE) : NODATE;
    const compVisible = actsAll.slice(0, s.compShown);
    const feedGroups = uq(compVisible.map(groupOf)).map(l2 => ({ label: l2, items: compVisible.filter(a => groupOf(a) === l2).map(cAct), count: actsAll.filter(a => groupOf(a) === l2).length }));
    /* 12 chips instead of 7 (ALL + 11 real companies). The left number is the 30-day
       dated count — 7 days contains 1 record in the whole corpus — and the 5
       companies with no dated record show a dash, never a 0. */
    const compStrip = [{ label: T.cwAllCompetitors, neu: CACT.recent30, obs: CACTS.length, on: !s.fCompany, go: () => this.setState({ fCompany: '', compShown: 12 }) }]
      .concat(companies.map(c2 => ({ label: c2.name.toUpperCase(), neu: c2.recent30, obs: c2.count, on: s.fCompany === c2.name, go: () => this.setState({ fCompany: s.fCompany === c2.name ? '' : c2.name, compShown: 12 }) })))
      .map(x => ({ label: x.label, neu: x.neu, obs: x.obs, bg: x.on ? 'rgba(0,152,69,0.14)' : '#1C1817', border: x.on ? '#009845' : 'rgba(203,197,195,0.14)', rail: x.on ? '#009845' : 'rgba(151,139,135,0.45)', color: x.on ? '#fff' : '#D6D2D0', weight: x.on ? 700 : 600, go: x.go }));
    /* WHAT CHANGED · one tile, not six. Five of the old six types do not exist, and
       the sixth carries no date on any of its 89 records, so an organic tile could
       only ever print a fake 0. The surviving tile names its own 30-day window
       because the section header still says 7 days. */
    const changed7 = [{ type: 'PAID', label: (T.chPaid || 'PAID') + ' · ' + OBS_WINDOW + TX('G', 'D'), color: COMPCH['PAID'].c, icon: 'assets/icons/' + COMPCH['PAID'].i + '-white.png', n: CACTS.filter(a => a.type === 'PAID' && within(a, OBS_WINDOW)).length, go: () => this.setState({ fType: 'PAID', compView: 'feed', compShown: 12, fPeriod: String(OBS_WINDOW) }) }];
    const topMoves = (() => {
      const seen = {}; const out2 = [];
      CACTS.filter(a => within(a, OBS_WINDOW)).sort((a, b) => b.daysFromRef - a.daysFromRef).forEach(a => { const k2 = a.company + '|' + a.type; if (seen[k2] || out2.length >= 3) return; seen[k2] = 1; out2.push(a); });
      return out2.map((a, i) => { const dc = cAct(a); return { rank: '0' + (i + 1), company: dc.companyLabel, product: dc.product, chName: dc.chName, chColor: dc.chColor, chText: dc.chText, crop: dc.cropL, cropL: dc.cropL, when: dc.when, go: () => this.openCompany(a.company) }; });
    })();
    /* §8 · communication density = density inside monitored public communication.
       The HIGH / MEDIUM / LOW verdict is gone: the 14/8 thresholds and the /20
       denominator were fitted to a 72-row fixture and would call almost everything
       HIGH on 503 rows, and a three-level grade drifts into reading as commercial
       importance. The bar is relative to the largest observed row (Maize 67) and the
       panel publishes its own denominator. */
    const cropDensity = CDENS.records.map(r => ({ crop: r.crop, cropL: cl(r.crop), n: r.items, cos: r.companies, level: '', color: '#978B87', pct: r.sharePct + '%', go: () => this.setState({ fCrop: r.crop, compView: 'feed', compShown: 12 }) }));
    const cropDensityNote = TX(
      CDENS.unresolvedItems + ' record su ' + CDENS.denominator + ' non nominano alcuna coltura e ' + CDENS.genericItems + ' portano solo una parola ombrello dell’inserzionista (colture, cereali, frutta, ortaggi), mai promossa a coltura. Densità nella comunicazione pubblica monitorata: non è quota di mercato né importanza commerciale.',
      CDENS.unresolvedItems + ' of ' + CDENS.denominator + ' records name no crop and ' + CDENS.genericItems + ' carry only an advertiser umbrella word (colture, cereali, frutta, ortaggi), never promoted to a crop. Density inside monitored public communication: not market share, not commercial importance.');
    /* §7 · the window state is upstream's CURRENT_STATUS printed verbatim; the view
       no longer computes IN WINDOW / EARLY from a substring match between an issue
       name and a window name. The competitor side is the whole corpus for that crop,
       because there is no honest 30-day slice (11 dated records in 30 days across
       all crops). Only 2 of the windows that have observed communication are open. */
    const momentByCrop = {};
    CWM.filter(m => m.itemsObserved > 0).forEach(m => {
      const rk = STRANK[m.status] === undefined ? 9 : STRANK[m.status];
      const prev = momentByCrop[m.crop];
      /* one row per crop: three identical Olive rows for Puglia, Sicilia and Toscana
         say the same thing three times and push the other crops off the panel. */
      if (!prev || rk < prev.rk || (rk === prev.rk && Math.abs(m.daysToStart === null ? 9999 : m.daysToStart) < Math.abs(prev.m.daysToStart === null ? 9999 : prev.m.daysToStart))) momentByCrop[m.crop] = { rk, m };
    });
    const compMoments = Object.keys(momentByCrop).map(k2 => momentByCrop[k2])
      .sort((a, b) => a.rk - b.rk || b.m.itemsObserved - a.m.itemsObserved)
      .slice(0, 4).map(x => x.m)
      .map(m => ({
        crop: m.crop, cropL: cl(m.crop), region: m.region,
        days: wst(m.status), issue: m.issue, issueL: il(m.issue),
        cos: m.companiesObserved, acts: m.itemsObserved,
        /* §10 · the ADAMA side is the label audit and nothing else. 'n/d' is a state
           of the reading; it is never rendered as "ADAMA has no product". */
        prods: (m.portfolioVerified || []).length ? m.portfolioVerified.length : 'n/d',
        market: 'n/d', marketColor: '#8F8886',
        color: STCOLOR(m.status),
        go: () => this.openWindow(m.windowId)
      }));
    const co0 = companies.find(c2 => c2.name === s.companyId) || companies[0] || null;
    const co = co0 ? Object.assign({}, co0, { activities: actsOfKey(co0.key).slice().sort((a, b) => (b.hasDate ? b.daysFromRef : -1e9) - (a.hasDate ? a.daysFromRef : -1e9)).map(cAct) })
      : { name: '', label: '', id: '', key: '', initials: '', count: 0, paid: 0, organic: 0, pages: [], crops: [], confidence: '', last: NODATE, first: NODATE, recent30: '—', countRows: [], productObjs: [], productsNote: '', themes: [], cases: [], eventRows: [], activities: [], storyBorder: 'rgba(151,139,135,0.45)', go: () => {}, filter: () => {} };
    /* COMPETITOR × CROP · the model publishes 10 columns and a measured maxCell (22);
       the grid is capped at the 6 largest because the markup hard-codes six columns,
       and the crops left out are named in the footnote. 6 of the 11 companies have no
       crop-resolved activity at all — Syngenta has 55 observed items and not one of
       them names a crop. */
    const matrixKeys = (CMX.columns || []).slice(0, 6);
    const matrixCols = matrixKeys.map(cl);
    const matrixOmitted = (CMX.columns || []).slice(6).map(cl);
    const matrixMax = Math.max(1, CMX.maxCell || 1);
    const matrix = CMX.records.map(r => ({ company: r.company, cells: matrixKeys.map(cr => { const cell = (r.cells || []).find(x => x.crop === cr) || { n: 0 }; const ratio = cell.n / matrixMax; return { n: cell.n, crop: cr, dots: cell.n === 0 ? '·' : ratio >= 0.66 ? '●●●' : ratio >= 0.33 ? '●●' : '●', bg: cell.n === 0 ? 'rgba(255,255,255,0.03)' : ratio >= 0.66 ? 'rgba(151,139,135,0.55)' : ratio >= 0.33 ? 'rgba(151,139,135,0.35)' : 'rgba(151,139,135,0.18)', go: () => this.compWith({ fCompany: r.company, fCrop: cr }) }; }) }));
    const matrixNote = TX((CMX.allZeroCompanies || []).length + ' delle ' + CMX.records.length + ' aziende non hanno nessuna attività con coltura risolta.', (CMX.allZeroCompanies || []).length + ' of the ' + CMX.records.length + ' companies have no crop-resolved activity.')
      + (matrixOmitted.length ? TX(' Colture non in tabella: ', ' Crops not in the table: ') + matrixOmitted.join(', ') + '.' : '');

    /* EVENTS · 18 real events, of which 2 are still ahead (EIMA +69g, Vinitaly 2027
       +221g). SECTOR and EXHIBITOR_LIST_STATE arrive as Portuguese working
       vocabulary; a closed 6-value enum is mapped for display and free Portuguese
       prose is suppressed rather than shown to an Italian reader. */
    const SECTORL = { 'maquinas agricolas e de jardinagem': TX('macchine agricole e da giardinaggio', 'agricultural and garden machinery'), 'viticultura': TX('viticoltura', 'viticulture'), 'agricultura geral': TX('agricoltura generale', 'general agriculture'), 'hortifruti': TX('ortofrutta', 'fruit and vegetables'), 'vinho e destilados': TX('vino e distillati', 'wine and spirits'), 'demonstracao de campo do fabricante': TX('dimostrazione di campo del produttore', 'manufacturer field demonstration') };
    const EXHL = { 'NAO CONSULTADA': TX('ELENCO ESPOSITORI NON CONSULTATO', 'EXHIBITOR LIST NOT CONSULTED'), 'NAO APLICAVEL': '' };
    const evDeco = (e2) => {
      const confirmed = companies.filter(c2 => (e2.confirmedParticipationList || []).some(k2 => UPC(k2) === UPC(c2.name))).map(c2 => c2.name);
      const future = e2.daysToStart !== null && e2.daysToStart > 0;
      return {
        id: e2.id, name: e2.name, go: () => this.openEvent(e2.id),
        city: e2.location || '', region: 'Italia', site: e2.url || '',
        dates: e2.startDate ? (e2.endDate && e2.endDate !== e2.startDate ? dLabel(e2.startDate) + ' → ' + dLabel(e2.endDate) : dLabel(e2.startDate)) : NODATE,
        startDays: e2.daysToStart,
        countdown: e2.daysToStart === null ? NODATE : (future ? e2.daysToStart + TX(' g', ' d') : TX('CONCLUSO', 'PAST')),
        bucket: future ? TX('GIORNI ALL’EVENTO', 'DAYS TO EVENT') : TX('EDIZIONE PASSATA', 'PAST EDITION'),
        sector: SECTORL[e2.sector] || '',
        /* CROP_RELEVANCE is the unknown sentence on 5 of 18 rows; the model already
           nulls those, so nothing here has to filter a Portuguese sentinel. */
        crops: e2.cropRelevance ? [e2.cropRelevance] : [],
        exhibitorStatus: EXHL[UPC(e2.exhibitorListState)] !== undefined ? EXHL[UPC(e2.exhibitorListState)] : '',
        confirmed, confirmedCount: confirmed.length,
        confirmedLabel: confirmed.length ? confirmed.length + TX(' confermati', ' confirmed') : TX('partecipazione non nota', 'participation not known'),
        statusLabel: confirmed.length ? TX('ESPOSITORI CONFERMATI', 'CONFIRMED EXHIBITORS') : TX('PARTECIPAZIONE NON NOTA', 'PARTICIPATION NOT KNOWN'),
        statusColor: confirmed.length ? '#00B152' : '#B1A9A7',
        partSummary: confirmed.length ? confirmed.join(', ') : TX('non nota · mai dedotta dalle edizioni precedenti', 'not known · never inferred from previous editions'),
        partRows: companies.map(c2 => { const on = confirmed.indexOf(c2.name) >= 0; return { company: c2.name, state: on ? TX('CONFERMATO', 'CONFIRMED') : NOTKNOWN, color: on ? '#00B152' : '#B1A9A7' }; }),
        program: cNar(e2.note) || ''
      };
    };
    const upcomingEvents = CEVENTS.filter(e2 => e2.daysToStart !== null && e2.daysToStart > 0).sort((a, b) => a.daysToStart - b.daysToStart).map(evDeco);
    const eventCards = CEVENTS.slice().sort((a, b) => ((a.daysToStart === null || a.daysToStart < 0) ? 9999 : a.daysToStart) - ((b.daysToStart === null || b.daysToStart < 0) ? 9999 : b.daysToStart)).map(evDeco);
    /* No activity carries an eventId and no real record links to a case, so the
       BEFORE / DURING / AFTER story and the related-activity wall have nothing to
       show and are emptied rather than filled from a name match. */
    const evd0 = CEVENTS.find(e2 => e2.id === s.eventId) || CEVENTS[0] || null;
    const evd = evd0 ? Object.assign(evDeco(evd0), { cases: [], actCount: 0, activities: [], story: [] })
      : { id: '', name: '', go: () => {}, city: '', region: '', site: '', dates: NODATE, startDays: null, countdown: NODATE, bucket: '', sector: '', crops: [], exhibitorStatus: '', confirmed: [], confirmedCount: 0, confirmedLabel: '', statusLabel: '', statusColor: '#B1A9A7', partSummary: '', partRows: [], program: '', cases: [], actCount: 0, activities: [], story: [] };
    /* COMMUNICATION LEAD TIME is not measurable from this corpus. The earliest
       observation per company is set by the Meta Ad Library retention horizon, not by
       the company — UPL 2019-12-05, BASF 2023-03-08, Corteva 2024-11-26, Syngenta
       2025-07-29, Bayer 2025-08-28, FMC 2025-10-21 — and 5 companies have no dated
       record at all. Any "X days before the window" from that describes the archive.
       Emptied here; the card must be deleted from the markup. */
    const leadCrop = '';
    const leadTimes = [];
    const galleryItems = actsAll.map(cAct);
    /* COMPETITOR × ISSUE · 14 observed terms over 98 of 503 records, in the
       advertiser's own words. No PAID column (all 98 issue-bearing records are paid,
       so the column would repeat ITEMS), no ADAMA column (no observed term equals a
       canonical ISSUE_NAME, so a portfolio column could only be built by the view
       inventing a synonym table) and no case link (no observed term carries one). */
    const issueRows = CISS.records.map(r => ({ issue: r.issue, issueL: r.issue, scope: r.issueScope, count: r.items, paid: '', companies: r.companies, companiesLabel: r.companies.join(', '), adama: [], adamaLabel: '', go: () => this.compWith({ fIssue: r.issue }) }));
    const issueRowsNote = TX((CISS.denominator - CISS.coveredActivities) + ' record su ' + CISS.denominator + ' non nominano alcuna avversità. I termini sono le parole dell’inserzionista: mai tradotti, mai troncati.',
      (CISS.denominator - CISS.coveredActivities) + ' of ' + CISS.denominator + ' records name no pest or disease. The terms are the advertiser’s own words: never translated, never truncated.');
    /* COMPETITOR PRODUCT · 36 proven products, each with the upstream proof string.
       People mentions and ADAMA case links have no counterpart and are gone; first
       and last come from the paid records that actually name the product. */
    const actById = {};
    CACTS.forEach(a => { actById[a.id] = a; });
    const cp0 = CPRODUCTS.find(p2 => p2.name === s.cproductId) || CPRODUCTS[0] || null;
    const cpActs = cp0 ? (cp0.activityIds || []).map(i2 => actById[i2]).filter(Boolean) : [];
    const cp = cp0 ? {
      name: cp0.name, company: cp0.company, proof: cp0.proof,
      openCompany: () => this.openCompany(cp0.company),
      count: cp0.activityCount, paid: cpActs.filter(a => a.type === 'PAID').length, people: '',
      cropLabel: (cp0.cropsObserved || []).map(cl).join(', ') || TX('nessuna coltura dichiarata', 'no crop stated'),
      issueLabel: (cp0.issuesObserved || []).join(', ') || TX('nessuna avversità dichiarata', 'no pest stated'),
      first: cp0.firstSeen ? dLabel(cp0.firstSeen) : NODATE,
      last: cp0.lastSeen ? dLabel(cp0.lastSeen) : NODATE,
      activities: cpActs.map(cAct), cases: []
    } : { name: '', company: '', proof: '', openCompany: () => {}, count: 0, paid: 0, people: '', cropLabel: '', issueLabel: '', first: NODATE, last: NODATE, activities: [], cases: [] };
    /* Props the tail of renderVals still builds from the fixture, computed here so
       that edit is a one-word change. */
    const compTotal = CACTS.length;
    const compCropOptions = opts(TX('Tutte le colture', 'All crops'), CDENS.records.map(r => r.crop), cl);
    const compIssueOptions = opts(TX('Tutte le avversità', 'All issues'), CISS.records.map(r => r.issue));
    const compPeriodOptions = [{ v: '', l: T.cwAnyPeriod || 'Any period' }, { v: '30', l: TX('Ultimi 30 giorni', 'Last 30 days') }, { v: '90', l: TX('Ultimi 90 giorni', 'Last 90 days') }, { v: '365', l: TX('Ultimi 365 giorni', 'Last 365 days') }];
    const whatChanged = [];
