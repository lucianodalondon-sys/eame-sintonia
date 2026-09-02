    // ---- signal detail
    /* §18 · A real Future card opens the SAME real entity. The pool the detail
       resolves from is exactly the pool the feed showed, so an unresolved id
       reports itself as missing instead of quietly opening a neighbour. */
    const sgPool = (APP0 ? APP0.futureSignals.records : []).concat(s.showScenarios && APP0 && APP0.futureScenarios ? APP0.futureScenarios.records : []);
    const sg0 = sgPool.find(x => x.id === s.signalId) || null;
    const sgMissing = !!s.signalId && !sg0;
    /* Upstream signals and presentation scenarios have different shapes. The
       scenario keeps its rich demo structure; the real record has far less, and
       renders far less. Nothing is ever borrowed across that line. */
    const sgIsScenario = !!(sg0 && AM && AM.isDemo(sg0, 'REAL_SOURCE'));
    /* A narrative field is only shown when upstream approved a localized
       version. Otherwise the state is shown, never the raw research note. */
    const nar = (n) => (n && n.state === 'CLEAR') ? (s.lang === 'en' ? (n.en || n.it) : (n.it || n.en)) : null;
    const narState = (n) => !n ? null : n.state === 'CLEAR' ? null
      : n.state === 'NOT_ESTABLISHED' ? (T.notEstablished || 'non ancora stabilito')
      : (T.notApprovedForDisplay || 'lettura interna, non pubblicabile');
    const SRC_TINT = { OFFICIAL: '#00B152', SCIENCE: '#00A0DF', MARKET: '#F5B317', MEDIA: '#9D1D96', FIELD: '#7DB41E', COMPETITOR: '#F89E18' };
    const srcTint = (x) => SRC_TINT[String((x && (x.group || x.type)) || '').toUpperCase().split(/[^A-Z]/)[0]] || '#978B87';
    const srcGo = (src) => () => src.kind === 'source' ? this.openSource(src.id) : src.kind === 'person' ? this.openPerson(src.id) : src.kind === 'news' ? this.go({ view: 'sources', sourceGroup: 'NEWS & TRADE MEDIA' }) : src.kind === 'company' ? this.openCompany(src.id) : src.kind === 'field' ? this.go({ view: 'field' }) : this.openSource(src.id);
    /* Real signals cite SOURCE_IDS. Those resolve against the registry, so the
       source list on a real card is traceable rather than described. */
    const sgSourceRecords = sgIsScenario ? ((sg0 || {}).sources || [])
      : ((sg0 || {}).sourceIds || []).map(id => (APP0 ? APP0.sources.records.find(x => x.sourceId === id || x.id === id) : null)
        || { id, name: id, group: null, unresolved: true });
    const sgSources = sgSourceRecords.filter(src => !s.sigGroup || src.group === s.sigGroup);
    const sgTrail = sgIsScenario ? ((sg0 || {}).trail || []) : [];
    const ev = (s.evidenceIdx != null && sgTrail[s.evidenceIdx]) ? sgTrail[s.evidenceIdx].ev : null;
    const sg = Object.assign({}, sg0, {
      isScenario: sgIsScenario, isReal: !!sg0 && !sgIsScenario,
      /* the six narrative panels: text when approved, state when not, nothing when absent */
      whyWatchText: nar((sg0 || {}).whyWatch), whyWatchState: narState((sg0 || {}).whyWatch),
      whoIsTalkingText: nar((sg0 || {}).whoIsTalking), whatChangedText: nar((sg0 || {}).whatChanged),
      observedFactsText: nar((sg0 || {}).observedFacts), interpretationText: nar((sg0 || {}).interpretation),
      unknownText: nar((sg0 || {}).unknown), nextWindowText: nar((sg0 || {}).nextWindow),
      portfolioConnectionText: nar((sg0 || {}).portfolioConnection),
      promoteConditionText: nar((sg0 || {}).whatWouldPromoteIt),
      sourceTypeUpper: ((sg0 || {}).sourceType || '').toUpperCase(),
      /* A product panel needs a product entity that really exists in the model. */
      hasProduct: !!(sg0 && sg0.product && AM && AM.findProduct(sg0.product)),
      noProduct: !(sg0 && sg0.product && AM && AM.findProduct(sg0.product)),
      p: (() => { const e = sg0 && sg0.product && AM ? AM.findProduct(sg0.product) : null; return e ? Object.assign({}, e, { crops: (e.crops || []).join(', '), targets: (e.targets || []).join(' / ') }) : {}; })(),
      goProduct: () => (sg0 || {}).product ? this.openProduct((sg0 || {}).product) : this.radarWith({ fStatus: 'VALIDATE' }),
      goWindow: () => (sg0 || {}).window && this.openWindow((sg0 || {}).window.id),
      goTheme: () => (sg0 || {}).science ? this.openTheme((sg0 || {}).science) : this.go({ view: 'science' }),
      goCase: () => (sg0 || {}).matchCase && this.openCase((sg0 || {}).matchCase.id),
      /* who / trail / promotion exist only in the presentation scenario. On a
         real signal they stay empty and the markup hides the panel. */
      who: (sgIsScenario ? ((sg0 || {}).who || []) : []).map(g => Object.assign({}, g, { bg: s.sigGroup === g.group ? g.color : '#161312', go: () => this.setState({ sigGroup: s.sigGroup === g.group ? '' : g.group }) })),
      whyWatch: (sgIsScenario ? ((sg0 || {}).whyWatch || []) : []).map(y => ({ t: y.t, mark: y.warn ? '△' : y.ok ? '✓' : '○', color: y.warn ? '#978B87' : y.ok ? '#009845' : '#8F8886' })),
      trail: sgTrail.map((t, i) => Object.assign({}, t, { view: () => this.setState({ evidenceIdx: i }), border: i === sgTrail.length - 1 ? (sg0 || {}).color : s.evidenceIdx === i ? '#009845' : 'rgba(203,197,195,0.14)', bg: i === sgTrail.length - 1 ? ((sg0 || {}).color || '#978B87') + '22' : 'rgba(255,255,255,0.03)', numColor: i === sgTrail.length - 1 ? (sg0 || {}).color : '#8F8886' })),
      promotion: (sgIsScenario ? ((sg0 || {}).promotion || []) : []).map(p => ({ t: p.t, mark: p.ok ? '✓' : '□', color: p.ok ? '#009845' : '#8F8886' })),
      promoColor: (sg0 || {}).promoted ? '#009845' : '#978B87',
      /* Where the fact sits is only claimed when a source supports it. */
      factLoc: sgSourceRecords.some(x => !x.unresolved) ? ((sg0 || {}).region || (T.notEstablished || 'non ancora stabilito')) : (T.notEstablished || 'non ancora stabilito'),
      sourceCount: sgSources.length,
      sourceCards: sgSources.map(src => Object.assign({}, src, { color: srcTint(src), go: srcGo(src) })),
      unresolvedSources: sgSourceRecords.filter(x => x.unresolved).length,
      groupChips: [{ group: 'ALL', count: sgSourceRecords.length }].concat(sgIsScenario ? ((sg0 || {}).who || []) : []).map(g => { const on = (s.sigGroup || 'ALL') === g.group; return { group: g.group, count: g.count, border: on ? '#009845' : 'rgba(203,197,195,0.2)', bg: on ? 'rgba(0,152,69,0.25)' : 'transparent', textColor: on ? '#fff' : '#B1A9A7', go: () => this.setState({ sigGroup: g.group === 'ALL' ? '' : g.group }) }; })
    });

