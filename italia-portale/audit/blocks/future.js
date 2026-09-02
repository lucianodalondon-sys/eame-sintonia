    // ---- future
    /* §7 · PRESENTATION TOKENS. Authored here, never read from a fixture. They are a
       LOOKUP keyed by whatever status string a record actually carries — they do NOT
       define the vocabulary. When a status is absent or unknown the neutral tone wins,
       so an unrecognised value can never be dressed up as an assessment. */
    const F_ACCENT = { 'NEW SIGNAL': '#00A0DF', 'GAINING ATTENTION': '#00698F', 'MULTIPLE SIGNALS': '#9D1D96', 'WATCH CLOSELY': '#F5B317', 'NEEDS VALIDATION': '#F89E18', 'TIMING APPROACHING': '#7DB41E', 'PREPARE': '#00B152' };
    const F_ICON = { 'NEW SIGNAL': 'sun', 'GAINING ATTENTION': 'cloud', 'MULTIPLE SIGNALS': 'connect', 'WATCH CLOSELY': 'heat-sensitive', 'NEEDS VALIDATION': 'recycle-label', 'TIMING APPROACHING': 'rain', 'PREPARE': 'farm-management' };
    // rails and fills may be dark; text on #1C1817 uses the lightened partner
    const F_TEXT = Object.assign({}, F_ACCENT, { 'GAINING ATTENTION': '#00A0DF', 'MULTIPLE SIGNALS': '#C46ABE' });
    const F_MUTED = '#8F8886';
    /* Source-class tint and icon. Keyed on the REGISTRY type (IG.SOURCES.TYPE), which is
       a real enum, so a class that upstream never emitted simply never gets a card. */
    const F_SRC_TINT = { OFFICIAL: '#00B152', RESEARCH: '#00A0DF', RESEARCH_INSTITUTION: '#5CC3EE', MARKET: '#F5B317', TECHNICAL_MEDIA: '#9D1D96', FIELD: '#7DB41E', PEOPLE: '#C77BC3', COOPERATIVE: '#00783F', PRODUCER_ORG: '#93CC23', COMPETITOR: '#F89E18', COMPANY: '#978B87', ADAMA: '#009845' };
    const F_SRC_ICON = { OFFICIAL: 'recycle-label', RESEARCH: 'cloud', RESEARCH_INSTITUTION: 'cloud', MARKET: 'sell', TECHNICAL_MEDIA: 'sun', FIELD: 'farm-management', PEOPLE: 'connect', COOPERATIVE: 'farm-management', PRODUCER_ORG: 'sell', COMPETITOR: 'heat-sensitive', COMPANY: 'heat-sensitive', ADAMA: 'connect' };
    /* i18n bridge only, over TWO vocabularies that must stay visibly separate: the scenario
       fixture's ('Science', 'Field network', …) and the source registry's own enum
       ('OFFICIAL', 'RESEARCH', …). A class with no approved translation shows its own token
       rather than borrowing a neighbour's label — aliasing RESEARCH onto 'Science' produced
       two identically-named cards, one demo and one real. Reported: SRCTYPES/EVCHIP still
       lack the registry keys. */
    const fSrcTypeL = (k) => (T.SRCTYPES && T.SRCTYPES[k]) || (T.EVCHIP && T.EVCHIP[k]) || k;
    const fUnknownL = T.ksNotKnown || 'non noto';
    /* §7 · A narrative field is rendered only when upstream approved a localized text.
       Measured on this package: whyWatch / whoIsTalking / whatChanged / observedFacts /
       interpretation / unknown / portfolioConnection are NOT_APPROVED_FOR_DISPLAY on 3/3
       real signals, and nextWindow is NOT_ESTABLISHED on 2/3 — so today this returns null
       every time and the prose slots stay empty instead of leaking research notes. */
    const fNar = (n) => (n && n.state === 'CLEAR') ? (s.lang === 'en' ? (n.en || n.it) : (n.it || n.en)) : null;
    /* The pest/disease/weed class is a FACT and comes from the canonical ISSUE_TYPE.
       FUTURE_SIGNALS has no ISSUE_TYPE field at all, so every real card resolves to the
       neutral unknown token: grey rail, no icon, no category chip. The old code forced the
       fixture's disease token onto all three — including IT-FUT-003, ISSUE 'REGULATORIO'. */
    const fCatUI = (issueType) => { const u = AM.categoryOf(issueType); return Object.assign({}, u, { icon: u.iconAsset || '' }); };
    const fSrcReg = APP0 ? APP0.sources.records : [];
    const fSrcById = (id) => fSrcReg.find(x => x.sourceId === id || x.id === id) || null;
    const fWinReg = APP0 ? APP0.cropWindows.records : [];
    const fWstL = (k) => (T.WSTATUS && T.WSTATUS[k]) || k;
    const sigWL = (x) => { const st = (x.sourceTypes && x.sourceTypes.length) ? x.sourceTypes.map(fSrcTypeL) : (x.sourceType ? [srcL(x.sourceType)] : []); return Object.assign({}, x, { cropL: cl(x.crop), issueL: il(x.issue), sourceTypeL: st.join(' · '), sourceTypeUpperL: st.join(' · ').toUpperCase(), statusL: x.status ? fst(x.status) : '' }); };
    /* §7 · The real feed. Nothing is borrowed from the scenario fixture: what upstream did
       not supply is absent, and the card renders smaller. sourceIds resolve against the
       source registry, so the class shown on a card is traceable to a named source. */
    const realSigs = (APP0 ? APP0.futureSignals.records : []).map(f => {
      const ids = f.sourceIds || [], srcs = ids.map(fSrcById).filter(Boolean);
      return Object.assign({}, f, {
        isScenario: false, category: fCatUI(f.issueType),
        sourceRecords: srcs, sourceTypes: [...new Set(srcs.map(x => x.type).filter(Boolean))],
        sourceCount: srcs.length, unresolvedSources: ids.length - srcs.length,
        evidenceCount: (f.evidenceIds || []).length,
        /* FUTURE_SIGNALS carries no observation date (raw.DATE is undefined on 3/3). The
           registry's LATEST_OBSERVATION is when the SOURCE was last read, not when this
           signal was seen, so it is not promoted into an "updated" claim. */
        lastObserved: fUnknownL
      });
    });
    const scenarioSigs = s.showScenarios ? (APP0 && APP0.futureScenarios ? APP0.futureScenarios.records : []).map(x => Object.assign({}, x, { isScenario: true })) : [];
    const sigPool = realSigs.concat(scenarioSigs).map(sigWL);
    /* §7 · The status vocabulary is whatever the visible records actually carry. Measured:
       status is null on 3/3 real signals, so with scenarios off this array is EMPTY and the
       whole chip row disappears rather than advertising a seven-level assessment scale that
       upstream never produced. A stale filter value outside the vocabulary is ignored, so
       the feed can never be silently emptied by a filter with no chip left to clear it. */
    const fStatuses = [...new Set(sigPool.map(x => x.status).filter(Boolean))];
    const sigTypesOf = (x) => (x.sourceTypes && x.sourceTypes.length) ? x.sourceTypes : (x.sourceType ? [x.sourceType] : []);
    const fSources = [...new Set(sigPool.flatMap(sigTypesOf))];
    const fStatusOn = fStatuses.indexOf(s.futureStatus) >= 0 ? s.futureStatus : '';
    const fSourceOn = fSources.indexOf(s.futureSource) >= 0 ? s.futureSource : '';
    const sigAll = sigPool.filter(x => (!fStatusOn || x.status === fStatusOn) && (!fSourceOn || sigTypesOf(x).indexOf(fSourceOn) >= 0));
    const sigCountReal = realSigs.length, sigCountScenario = (APP0 && APP0.futureScenarios ? APP0.futureScenarios.count : 0);
    /* The Field Sales inbound module is an explicit, default-off demonstration (§5). Its
       badge is therefore allowed to mark a SCENARIO card and nothing else — measured, its
       two signal references are IT-SIG-003 / IT-SIG-005, both scenarios, but the gate is
       structural so a fixture edit can never light the badge on a real record. */
    const fieldSignalIds = allMessages.filter(m => m.signalObj).map(m => m.signalObj.id);
    /* §7 · A crop window is attached only when the signal NAMES one. The three real signals
       carry no window reference (NEXT_WINDOW is NOT_ESTABLISHED on 2 and unapproved on the
       third), and their crop vocabulary is upstream's — MAIS / TRIGO e TRIGO DURO /
       TRANSVERSAL — against canonical Maize / Wheat / Durum Wheat, so even the old name
       join matched 0 of 3. A shared crop name is not a relation; an id is. */
    const fWinOf = (x) => { if (x.isScenario) return x.window || null; const ref = x.windowId || x.cropWindowId || (Array.isArray(x.windowIds) ? x.windowIds[0] : null); return ref ? (fWinReg.find(w => w.windowId === ref || w.id === ref) || null) : null; };
    const visibleSignals = sigAll.slice(0, s.futureShown).map(x => {
      const wm = fWinOf(x);
      const why = x.isScenario ? (x.whyShort || null) : fNar(x.whyWatch);
      const prod = x.product && AM.findProduct(x.product) ? x.product : null;
      return Object.assign({}, x, {
        open: () => this.openSignal(x.id),
        /* "who is talking" is a people/voice claim. The real records carry no such
           breakdown, and grouping cited databases by class would not be one, so the row
           stays empty and the markup must hide it (see hasWho). */
        who: (x.isScenario ? (x.who || []) : []).map(g => Object.assign({}, g, { go: (e) => { e.stopPropagation(); this.openSignal(x.id, g.group); } })),
        hasWho: x.isScenario && (x.who || []).length > 0,
        whyShort: why, hasWhy: !!why,
        productLabel: prod || fUnknownL, hasProduct: !!prod,
        portfolioColor: prod ? '#00B152' : '#B1A9A7',
        goProduct: () => prod && this.openProduct(prod),
        hasWindow: !!wm,
        windowLine: (x.isScenario && x.windowLine) || (wm && (wm.windowLine || fWstL(wm.status))) || fUnknownL,
        goWindow: () => wm && this.openWindow(wm.id),
        sourceTypeUpper: sigTypesOf(x).join(' · ').toUpperCase(),
        /* The card hard-codes "{crop} · {region}". The model now nulls the two upstream
           REGION values that were research notes ("NAO SEI — o recorte cientifico e por
           afiliacao nacional…"), leaving region null on 2/3 real signals — so the slot
           states that it is not known instead of trailing an orphan separator. */
        region: x.region || fUnknownL, hasRegion: !!x.region,
        /* Guards for the two slots the markup still renders unconditionally: an unclassified
           record has no icon asset (url() would be an empty request) and no observation date
           at all, so both must be hidden rather than filled. */
        hasCategory: !!(x.category && x.category.label && x.category.icon),
        hasLastObserved: !!(x.isScenario && x.lastObserved),
        fromField: x.isScenario && fieldSignalIds.indexOf(x.id) >= 0,
        color: x.status ? (F_TEXT[x.status] || x.color || F_MUTED) : F_MUTED,
        accent: x.status ? (F_ACCENT[x.status] || x.color || F_MUTED) : F_MUTED,
        statusIcon: x.status ? 'assets/icons/' + (F_ICON[x.status] || 'cloud') + '-white.png' : ''
      });
    });
    /* Empty vocabulary -> empty array -> the sc-for renders nothing, including the ALL
       chip, because a lone "ALL · 3" filter that filters nothing is noise. */
    const futureStatusChips = !fStatuses.length ? [] : [{ key: '', label: T.frAll, color: '#B1A9A7', icon: 'farm-management' }].concat(fStatuses.map(k => ({ key: k, label: fst(k), color: F_ACCENT[k] || F_MUTED, icon: F_ICON[k] || 'cloud' }))).map(f => { const on = fStatusOn === f.key; return { label: f.label, count: f.key ? sigPool.filter(x => x.status === f.key).length : sigPool.length, icon: 'assets/icons/' + f.icon + '-white.png', accent: f.color, color: on ? '#fff' : '#D6D2D0', bg: on ? f.color + '26' : '#1C1817', border: on ? f.color : 'rgba(203,197,195,0.16)', weight: on ? 700 : 500, countColor: on ? '#fff' : (F_TEXT[f.key] || f.color), go: () => this.setState({ futureStatus: f.key, futureShown: 16 }) }; });
    /* §7 · Source convergence, counted from the registry classes the signals really cite.
       The old row was a fixed seven-name English taxonomy that no real record could match:
       with scenarios off all seven cards read 0. Measured now: OFFICIAL 3, RESEARCH 2 —
       IT-FUT-001/002 cite OpenAlex + Ministero, IT-FUT-003 cites CELLAR + Ministero. */
    const futureSourceKpis = fSources.map(k => ({ k, n: sigPool.filter(x => sigTypesOf(x).indexOf(k) >= 0).length })).sort((a, b) => b.n - a.n || String(a.k).localeCompare(String(b.k))).map(r => { const on = fSourceOn === r.k, tint = F_SRC_TINT[r.k] || F_MUTED; return { label: fSrcTypeL(r.k), count: r.n, accent: tint, icon: 'assets/icons/' + (F_SRC_ICON[r.k] || 'cloud') + '-white.png', bg: on ? tint + '1F' : '#1C1817', border: on ? tint : 'rgba(203,197,195,0.10)', numColor: tint, go: () => this.setState({ futureSource: on ? '' : r.k, futureShown: 16 }) }; });
