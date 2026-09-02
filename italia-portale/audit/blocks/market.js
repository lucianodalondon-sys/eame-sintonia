    // ---- market pulse
    /* §M · Market Pulse was an editorial fixture end to end. Measured before this rewrite:
       window.ITALY_MARKET carried no record id, no SOURCE_ID and no PROVENANCE, credited
       eight organisations of which none is among the 31 registered sources, and 20 of the
       23 values it charted existed nowhere in the ingested observations. Everything numeric
       below now comes from AM.collections.marketObservations (77 rows, all IT-SRC-AGRIFOOD,
       weekly) through the model's own marketByCrop projection. The fixture survives as the
       tab strip and nothing else. */
    const MK = /*@VISUAL_ONLY crop tab strip identity only — key, label, Italian label, colour. No number, date, unit, state, source or verdict on this screen is read from the fixture.*/ window.ITALY_MARKET;
    const mkIT = s.lang !== 'en';
    /* §M · Barley has 8 real current observations and no fixture tab, so the model reports
       marketViewKey null for it. The tab is declared here from the data rather than leaving
       8 measured rows with nowhere to be seen. Colour is presentation. */
    const MK_CROPS = ((MK && MK.CROPS) || []).map((c) => ({ key: c.key, label: c.label, it: c.it, crop: c.crop, color: c.color }))
      .concat([{ key: 'barley', label: 'Barley', it: 'Orzo', crop: 'Barley', color: '#B1A9A7' }]);

    /* §M · Presentation tokens are declared locally so that no market-effect verdict
       (POSITIVE / NEGATIVE / WATCH) can leak back in through the fixture's SEM palette.
       These say only whether an observation exists. */
    const MK_TOK = {
      on: { key: 'OBSERVED', color: '#00A0DF', line: '#00A0DF', tint: 'rgba(0,160,223,0.07)', border: 'rgba(0,160,223,0.36)', mark: '●', label: mkIT ? 'OSSERVAZIONI INGERITE' : 'INGESTED OBSERVATIONS' },
      off: { key: 'NONE', color: '#B1A9A7', line: '#978B87', tint: 'transparent', border: 'rgba(151,139,135,0.28)', mark: '—', label: mkIT ? 'NESSUNA OSSERVAZIONE' : 'NO OBSERVATION' },
    };
    const MK_FRESH = { CURRENT: '#00B152', RECENT: '#7DB41E', AGING: '#F89E18', HISTORICAL: '#978B87', 'NOT INGESTED': '#8F8886' };
    const mkNotIngested = mkIT ? 'NON INGERITO' : 'NOT INGESTED';
    const mkNum = (v) => (v === null || v === undefined ? '—' : Number(v).toLocaleString(mkIT ? 'it-IT' : 'en-GB', { maximumFractionDigits: 2 }));
    const mkPct = (v) => (v === null || v === undefined ? '—' : (v > 0 ? '+' : '') + mkNum(v) + '%');
    const mkDay = (iso) => (iso ? iso.slice(8, 10) + '/' + iso.slice(5, 7) + '/' + iso.slice(0, 4) : '—');
    /* REFERENCE_PERIOD is 'dd/mm/yyyy..dd/mm/yyyy' on 77/77 rows; the model already parsed
       periodStart / periodEnd, so the view only reformats them for display. */
    const mkSpan = (r) => (r.periodStart && r.periodEnd ? mkDay(r.periodStart) + ' – ' + mkDay(r.periodEnd) : (r.referencePeriod || '—'));
    const mkFreq = (f) => ({ semanal: mkIT ? 'settimanale' : 'weekly', anual: mkIT ? 'annuale' : 'annual', continua: mkIT ? 'continua' : 'continuous', irregular: mkIT ? 'irregolare' : 'irregular' }[f] || f || '—');

    const MK_OBS = APP0 ? APP0.marketObservations.records : [];
    const MK_BY = APP0 && APP0.marketByCrop ? APP0.marketByCrop.records : [];
    const MK_LINKS = APP0 && APP0.portfolioLinksByCrop ? APP0.portfolioLinksByCrop.records : [];
    const MK_SRC = (APP0 ? APP0.sources.records : []).filter((x) => x.type === 'MARKET');
    /* §M · Written market analysis exists upstream for 5 crops but only the manifest travels
       in this package. The mapping from the analyst's Italian file names is declared here. */
    const MK_SUM_CROP = { MAIS: 'Maize', 'FRUMENTO DURO': 'Durum Wheat', 'OLIVO / OLIO DI OLIVA': 'Olive', 'VITE / VINO': 'Grapevine', RISO: 'Rice' };
    const MK_SUMS = (APP0 && APP0.marketSummaries ? APP0.marketSummaries.records : []).map((r) => Object.assign({}, r, { cropName: MK_SUM_CROP[r.crop] || null }));

    let mp = null, mpCropOptions = [], mpTabs = [], mpButtons = [], csMarket = null;
    {
      const mc = MK_CROPS.filter((c) => c.key === s.mCrop)[0] || MK_CROPS[0] || { key: '', label: '', it: '', crop: '', color: '#978B87' };
      const EMPTY = { hasData: false, observationCount: 0, currentCount: 0, stoppedCount: 0, stoppedYears: [], piazzaCount: 0, piazze: [], units: [], stages: [], productDefinitions: [], latestPeriodEnd: null, daysSinceLatest: null, changeCoverage: { vsPrev: 0, vsYearAgo: 0, total: 0 }, sourceName: null, sourceFrequency: null };
      const cnt = (k) => (MK_BY.filter((x) => x.cropName === k)[0] || EMPTY);
      const B = cnt(mc.crop);
      const rows = MK_OBS.filter((x) => x.cropKey === mc.crop);
      const live = rows.filter((x) => x.isCurrentSeries);
      const N = B.observationCount, HAS = N > 0;
      const tok = HAS ? MK_TOK.on : MK_TOK.off;
      const srcName = B.sourceName || (MK_SRC.length ? MK_SRC[0].name : '—');
      const srcFreq = mkFreq(B.sourceFrequency || (MK_SRC.length ? MK_SRC[0].frequency : null));

      /* §M · The tab badge is the ingested row count, not a market arrow. Measured: Olive 36,
         Wheat 13, Maize 11, Durum Wheat 8, Barley 8, Grapevine 1 (and that one is a series
         stopped in 2025), Tomato 0, Sugar Beet 0, Apple 0. */
      mpCropOptions = MK_CROPS.map((c) => ({ v: c.key, l: c.label.toUpperCase() + '  ·  ' + cnt(c.crop).observationCount + (mkIT ? ' OSS.' : ' OBS.') }));
      mpButtons = MK_CROPS.map((c) => {
        const on = c.key === mc.key, n = cnt(c.crop).observationCount;
        return { label: c.label.toUpperCase(), arrow: String(n), arrowColor: on ? '#fff' : (n ? '#D6D2D0' : '#6E6663'),
          bg: on ? '#00783F' : '#1C1817', border: on ? '#009845' : 'rgba(203,197,195,0.16)', color: on ? '#fff' : (n ? '#D6D2D0' : '#8F8886'),
          rail: on ? '#fff' : (n ? c.color : '#6E6663'), weight: on ? 700 : 600, go: () => this.setState({ mCrop: c.key }) };
      });
      mpTabs = [['crop', mkIT ? 'MERCATO DELLA COLTURA' : 'CROP MARKET'], ['industry', mkIT ? 'MERCATO AGROFARMACI' : 'CROP PROTECTION MARKET']]
        .map((t) => { const on = s.mTab === t[0]; return { label: t[1], color: on ? '#fff' : '#B1A9A7', bg: on ? 'rgba(0,152,69,0.25)' : 'transparent', border: on ? '#009845' : 'rgba(203,197,195,0.2)', go: () => this.setState({ mTab: t[0] }) }; });

      /* §M · The hero used to print a market verdict (PRESSURED / BALANCED / MIXED SIGNALS).
         No verdict is derivable from a weekly price list with four trade stages and twelve
         dead series, so the hero carries coverage: how much was observed, and of what. */
      const coverLine = HAS
        ? (N + (mkIT ? ' osservazioni · ' : ' observations · ') + B.piazzaCount + (mkIT ? ' piazze · ' : ' markets · ') + B.currentCount + (mkIT ? ' su serie correnti' : ' on current series'))
        : (mkIT ? 'Nessuna osservazione di prezzo ingerita per questa coltura' : 'No price observation ingested for this crop');

      /* §M · Coverage tiles. Every value is a count of ingested rows: none is a driver, a
         reason or a market effect. The six fixture drivers per crop are gone. */
      const noStage = rows.filter((x) => !x.hasStage).length, noPub = rows.filter((x) => !x.hasPublicationDate).length;
      const tiles = HAS ? [
        { d: String(N), t: mkIT ? 'OSSERVAZIONI' : 'OBSERVATIONS', v: mkIT ? 'righe di prezzo settimanali ingerite' : 'weekly price rows ingested' },
        { d: String(B.piazzaCount), t: mkIT ? 'PIAZZE' : 'MARKETS', v: mkIT ? 'mercati distinti quotati' : 'distinct quoted markets' },
        { d: String(B.productDefinitions.length), t: mkIT ? 'DEFINIZIONI DI PRODOTTO' : 'PRODUCT DEFINITIONS',
          v: B.productDefinitions.length ? (mkIT ? 'non confrontabili tra loro' : 'not comparable with each other') : (mkIT ? 'il prodotto non è dichiarato sulla riga ingerita' : 'the ingested row declares no product') },
        { d: String(B.units.length), t: mkIT ? 'UNITÀ DI MISURA' : 'UNITS', v: B.units.join(' · ') || '—' },
        { d: String(B.stoppedCount), t: mkIT ? 'SERIE FERME' : 'STOPPED SERIES',
          v: B.stoppedCount ? (mkIT ? 'ultima quotazione ' + B.stoppedYears.join(', ') + ' · non è un prezzo attuale' : 'last quote ' + B.stoppedYears.join(', ') + ' · not a current price') : (mkIT ? 'tutte le serie sono correnti' : 'every series is current') },
        { d: String(noStage), t: mkIT ? 'SENZA STADIO' : 'STAGE MISSING', v: mkIT ? 'righe su ' + N + ' senza il punto di filiera del prezzo' : 'of ' + N + ' rows with no chain stage for the price' },
      ] : [
        { d: '0', t: mkIT ? 'OSSERVAZIONI' : 'OBSERVATIONS', v: mkIT ? 'nessuna riga di prezzo ingerita per questa coltura' : 'no price row ingested for this crop' },
      ];

      /* §M · Freshness is measured against AM.REF (2026-09-02) through the model's own
         daysSinceLatest — no new Date() anywhere. rank keeps the one ingested family first
         so the rail never opens on an empty cell. Four of five families are empty, and the
         rail now says so instead of labelling components that no longer exist. */
      const rank = { CURRENT: 0, RECENT: 1, AGING: 2, HISTORICAL: 3, 'NOT INGESTED': 4 };
      const ageOf = (d) => { if (d === null || d === undefined) return 'NOT INGESTED'; const a = Math.abs(d); return a <= 14 ? 'CURRENT' : a <= 60 ? 'RECENT' : a <= 365 ? 'AGING' : 'HISTORICAL'; };
      const fresh = [
        { k: mkIT ? 'PREZZI' : 'PRICES', period: B.latestPeriodEnd ? mkDay(B.latestPeriodEnd) : '—', state: ageOf(B.daysSinceLatest) },
        { k: mkIT ? 'PRODUZIONE / RESA' : 'PRODUCTION / YIELD', period: '—', state: 'NOT INGESTED' },
        { k: mkIT ? 'SCAMBI / SCORTE' : 'TRADE / STOCKS', period: '—', state: 'NOT INGESTED' },
        { k: mkIT ? 'COSTI DEGLI INPUT' : 'INPUT COSTS', period: '—', state: 'NOT INGESTED' },
        { k: mkIT ? 'FIDUCIA DEGLI AGRICOLTORI' : 'FARMER CONFIDENCE', period: '—', state: 'NOT INGESTED' },
      ].sort((a, b) => rank[a.state] - rank[b.state])
        .map((f) => Object.assign({}, f, { color: MK_FRESH[f.state] || '#8F8886', state: f.state === 'NOT INGESTED' ? mkNotIngested : f.state }));

      /* §M · One real record, never a repair. The reference quote is the most recent live row
         inside the crop's dominant product definition. GEOGRAPHY is the same analyst string
         on all 77 rows ('IT — praca nomeada'), so the piazza name is printed instead — the
         'BARI (PUGLIA)' / 'ITALY' geography line the old screen showed has no real equivalent. */
      const defCount = {}; live.forEach((x) => { defCount[x.product] = (defCount[x.product] || 0) + 1; });
      const domDef = Object.keys(defCount).sort((a, b) => defCount[b] - defCount[a] || a.localeCompare(b))[0] || null;
      const ref = live.filter((x) => x.product === domDef)
        .sort((a, b) => String(b.periodEnd).localeCompare(String(a.periodEnd)) || String(a.market).localeCompare(String(b.market)))[0] || null;
      const priceChanges = !ref ? [] : [
        ref.changeVsPrev === null || ref.changeVsPrev === undefined ? null : { k: mkIT ? 'VS QUOTAZIONE PRECEDENTE' : 'VS PREVIOUS QUOTE', v: mkPct(ref.changeVsPrev), color: '#EDEAE9' },
        ref.changeVsYearAgo === null || ref.changeVsYearAgo === undefined ? null : { k: mkIT ? 'VS ANNO PRECEDENTE' : 'VS YEAR AGO', v: mkPct(ref.changeVsYearAgo), color: '#EDEAE9' },
      ].filter(Boolean);

      /* §M · Per-piazza comparison inside ONE product definition and ONE unit. Cereals quote
         in TONNES, olive oil in €/100kg, wine in Euro/HL; nothing is converted and nothing is
         averaged. Fewer than 2 live bars means no card — that removes Grapevine (1 row, and
         it is a stopped series), Tomato, Sugar Beet and Apple. */
      const chart = (() => {
        if (!live.length) return null;
        const g = {}; live.forEach((x) => { const k = x.product + ' · ' + x.unit; (g[k] = g[k] || []).push(x); });
        const keys = Object.keys(g).sort((a, b) => g[b].length - g[a].length || a.localeCompare(b));
        const best = g[keys[0]];
        if (!best || best.length < 2) return null;
        const max = Math.max.apply(null, best.map((x) => x.price || 0)) || 1;
        const other = keys.length - 1;
        return {
          unit: best[0].unit,
          rows: best.slice().sort((a, b) => (b.price || 0) - (a.price || 0))
            .map((x) => ({ label: x.market, disp: x.priceRaw || mkNum(x.price), pct: Math.max(5, ((x.price || 0) / max) * 100) + '%', color: mc.color, series: x.product + ' · ' + mkSpan(x) })),
          legend: [{ name: best[0].product + ' · ' + best[0].unit, color: mc.color }],
          note: (mkIT
            ? best.length + ' piazze su ' + B.piazzaCount + ', una sola definizione di prodotto, una sola unità. Le piazze non sono intercambiabili — classe di qualità e punto della filiera differiscono — quindi questi valori non vanno mediati.'
            : best.length + ' of ' + B.piazzaCount + ' markets, one product definition, one unit. Markets are not interchangeable — quality class and chain stage differ — so these values must not be averaged.')
            + (other > 0 ? (mkIT ? ' Altre ' + other + ' definizioni di prodotto di questa coltura non sono in questo confronto.' : ' A further ' + other + ' product definitions of this crop are not in this comparison.') : ''),
        };
      })();

      /* §M · 12 of 77 rows carry SERIES_WARNING saying the last quote is not a current price.
         Every one of them is badged here; none can be read as today's price. */
      const stopNote = (y) => (mkIT ? 'serie ferma dal ' + y + ' · l’ultima quotazione non è un prezzo attuale' : 'series stopped in ' + y + ' · the last quote is not a current price');
      const regionRows = rows.slice()
        .sort((a, b) => (a.isCurrentSeries === b.isCurrentSeries
          ? String(a.product || '').localeCompare(String(b.product || '')) || String(a.market).localeCompare(String(b.market))
          : (a.isCurrentSeries ? -1 : 1)))
        .map((x) => ({ p: x.market, v: x.priceRaw || mkNum(x.price), d: mkPct(x.changeVsPrev),
          note: [x.product || (mkIT ? 'prodotto non dichiarato' : 'product not declared'), x.unit, mkSpan(x)].join(' · ') + (x.isCurrentSeries ? '' : ' · ' + stopNote(x.stoppedYear)) }));

      /* §M · Crop windows come from the canonical collection and the state shown is the
         canonical CURRENT_STATUS — never a days-threshold ladder invented in the view.
         5 of 29 canonical windows carry no dates, so the day count must be able to say so. */
      const wRank = { WINDOW_OPEN: 0, NEXT_CYCLE: 1, DATE_UNKNOWN: 2, WINDOW_CLOSED: 3 };
      const mWinAll = (APP0 ? APP0.cropWindows.records : []).filter((w) => w.crop === mc.crop)
        .sort((a, b) => (wRank[a.canonicalStatus] - wRank[b.canonicalStatus])
          || ((a.daysToEnd === null ? 9999 : Math.abs(a.daysToEnd)) - (b.daysToEnd === null ? 9999 : Math.abs(b.daysToEnd))));
      const wDays = (w) => (w.canonicalStatus === 'WINDOW_OPEN' && w.daysToEnd !== null ? w.daysToEnd
        : w.canonicalStatus === 'NEXT_CYCLE' && w.daysToStart !== null ? w.daysToStart : null);
      const wLabel = (w) => { const d = wDays(w); return d === null ? wst(w.canonicalStatus)
        : d + ' ' + (w.canonicalStatus === 'WINDOW_OPEN' ? (T.wDaysRemaining || 'days remaining') : (T.wDaysToOpen || 'days to open')); };
      const mWins = mWinAll.slice(0, 4).map((w) => ({ issue: w.issue, issueL: il(w.issue), region: w.region, daysLabel: wLabel(w),
        daysColor: w.canonicalStatus === 'WINDOW_OPEN' ? '#00B152' : '#E3F4EA', go: () => this.openWindow(w.id) }));
      const nextW = mWinAll[0] || null;
      const openCount = mWinAll.filter((w) => w.canonicalStatus === 'WINDOW_OPEN').length;

      /* §M · The portfolio panel used to list demo case products. It now lists the products
         that have an authorised-use row read on the official Italian label for this crop.
         The count moves materially and that is the point: Maize 11 -> 3, Grapevine 8 -> 1,
         Wheat 6 -> 5, Olive 3 -> 4, Tomato 1 -> 7, Sugar Beet 5 -> 3, Apple 1 -> 2,
         Durum Wheat 9 -> 3, plus Barley 5 on a tab that did not exist. */
      const PL = MK_LINKS.filter((x) => x.cropKey === mc.crop)[0] || null;
      const mProducts = (PL ? PL.products : []).slice(0, 10).map((n) => ({ name: n, targets: '', go: () => this.openProduct(n) }));
      /* Same crop seen through the registry's own crop list — a bigger number, because not
         every authorisation that names the crop has had its use rows read row by row. The
         difference is published as a gap instead of being smoothed away. */
      const REG_TOKENS = { maize: ['MAIZE'], durum: ['DURUM_WHEAT', 'WHEAT_GENERIC'], soft: ['COMMON_WHEAT', 'WHEAT_GENERIC'], olive: ['OLIVE'], wine: ['GRAPEVINE'], tomato: ['TOMATO'], sugarbeet: ['SUGARBEET'], apple: ['APPLE'], barley: ['BARLEY'] };
      const regToks = REG_TOKENS[mc.key] || [];
      const regCount = (APP0 ? APP0.productsRegulatory.records : []).filter((r) => (r.crops || []).some((c) => regToks.indexOf(c) >= 0)).length;

      /* §M · Upstream calls these "convergencia que merece investigacao" and its own record
         forbids the word opportunity. Only 3 exist in the whole application and only 2 name
         a crop; the model already resolved the analyst's Portuguese crop into cropKeys. */
      const mCases = (APP0 ? APP0.opportunities.records : []).filter((o) => (o.cropKeys || []).indexOf(mc.crop) >= 0);

      const sum = MK_SUMS.filter((x) => x.cropName === mc.crop)[0] || null;

      const gaps = [];
      if (HAS) {
        gaps.push(mkIT ? N + ' righe di prezzo settimanali da una sola fonte (' + srcName + '); nessuna seconda fonte conferma questi valori' : N + ' weekly price rows from a single source (' + srcName + '); no second source confirms these values');
        gaps.push(mkIT ? 'Di ogni serie è ingerita solo l’ultima riga, anche dove la fonte dichiara centinaia di punti a monte: non c’è storico su cui disegnare un andamento' : 'Only the latest row of each series is ingested, even where the source reports hundreds of points upstream: there is no history to draw a trend from');
        if (B.stoppedCount) gaps.push(mkIT ? B.stoppedCount + ' righe su ' + N + ' stanno su serie ferme (' + B.stoppedYears.join(', ') + '): la loro ultima quotazione non è un prezzo attuale' : B.stoppedCount + ' of ' + N + ' rows sit on stopped series (' + B.stoppedYears.join(', ') + '): their last quote is not a current price');
        if (B.productDefinitions.length > 1) gaps.push(mkIT ? B.productDefinitions.length + ' definizioni di prodotto distinte: non sono confrontabili e non vanno mediate' : B.productDefinitions.length + ' distinct product definitions: they are not comparable and must not be averaged');
        if (!B.productDefinitions.length) gaps.push(mkIT ? 'La riga ingerita non dichiara un prodotto, quindi non si sa a quale definizione il prezzo si riferisca' : 'The ingested row declares no product, so which definition the price refers to is unknown');
        if (noStage) gaps.push(mkIT ? 'STAGE assente su ' + noStage + ' righe su ' + N + ': il punto della filiera a cui il prezzo si riferisce è ignoto' : 'STAGE missing on ' + noStage + ' of ' + N + ' rows: the chain stage the price refers to is unknown');
        if (noPub) gaps.push(mkIT ? 'PUBLICATION_DATE assente su ' + noPub + ' righe su ' + N + ': si conosce solo il periodo di riferimento' : 'PUBLICATION_DATE missing on ' + noPub + ' of ' + N + ' rows: only the reference period is known');
      } else {
        gaps.push(mkIT ? 'Nessuna osservazione di prezzo ingerita per questa coltura' : 'No price observation ingested for this crop');
      }
      if (PL && regCount > PL.productCount) gaps.push(mkIT ? PL.productCount + ' prodotti hanno una riga di uso autorizzato letta per questa coltura, ma ' + regCount + ' autorizzazioni citano la coltura in etichetta: la differenza è ciò che non è ancora stato letto riga per riga' : PL.productCount + ' products have an authorised-use row read for this crop, but ' + regCount + ' authorisations name the crop on the label: the difference is what has not yet been read row by row');
      if (PL && PL.sharedGenericRows) gaps.push(mkIT ? PL.sharedGenericRows + ' di quelle righe vengono dall’etichetta generica «Frumento» e sono contate sia per il tenero sia per il duro' : PL.sharedGenericRows + " of those rows come from the generic 'Frumento' label and are counted for both common and durum wheat");
      if (sum) gaps.push(mkIT ? 'A monte esiste un’analisi scritta per questa coltura (' + sum.file + ', ' + mkNum(sum.chars) + ' caratteri) che non è caricata in questo pacchetto' : 'An upstream written analysis exists for this crop (' + sum.file + ', ' + mkNum(sum.chars) + ' characters) and is not loaded in this package');
      gaps.push(mkIT ? 'Nessuna serie di produzione, superficie, resa, scorte, import, export o bilancio di approvvigionamento è ingerita' : 'No production, area, yield, stock, import, export or supply-balance series is ingested');
      gaps.push(mkIT ? 'Nessuna serie di costo degli input, fiducia degli agricoltori o previsione di mercato è ingerita' : 'No input-cost, farmer-confidence or market-forecast series is ingested');

      const why = [];
      why.push(HAS
        ? (mkIT ? N + ' osservazioni di prezzo ingerite da ' + srcName + (B.latestPeriodEnd ? ', ultima settimana di riferimento ' + mkDay(B.latestPeriodEnd) + '.' : ', nessuna serie corrente.') : N + ' price observations ingested from ' + srcName + (B.latestPeriodEnd ? ', latest reference week ' + mkDay(B.latestPeriodEnd) + '.' : ', no current series.'))
        : (mkIT ? 'Nessuna osservazione di prezzo è ingerita per questa coltura.' : 'No price observation is ingested for this crop.'));
      why.push(mkIT
        ? mWinAll.length + ' finestre agronomiche canoniche per questa coltura, ' + openCount + ' aperte al ' + (AM ? AM.referenceDate : '') + '.'
        : mWinAll.length + ' canonical agronomic windows for this crop, ' + openCount + ' open at ' + (AM ? AM.referenceDate : '') + '.');
      why.push(mkIT
        ? (PL ? PL.productCount : 0) + ' prodotti ADAMA hanno una riga di uso autorizzato letta sull’etichetta ufficiale per questa coltura.'
        : (PL ? PL.productCount : 0) + ' ADAMA products have an authorised-use row read on the official label for this crop.');
      why.push(mkIT
        ? 'Il prezzo pubblico è contesto economico: non è domanda, non è ordini, non è scorte e non è quota di mercato.'
        : 'A public price is economic context: it is not demand, not orders, not stock and not market share.');

      mp = {
        key: mc.key, label: (mkIT ? (mc.it || mc.label) : mc.label), it: mc.it, crop: mc.crop, color: mc.color,
        sem: tok, tempColor: tok.color, temp: String(N),
        latestPeriod: B.latestPeriodEnd ? mkDay(B.latestPeriodEnd) : (mkIT ? 'NESSUNA SERIE CORRENTE' : 'NO CURRENT SERIES'),
        drivers: tiles.map((x) => Object.assign({}, x, { color: HAS ? mc.color : '#8F8886', sem: { tint: 'rgba(255,255,255,0.03)', mark: HAS ? '●' : '—', label: '' } })),
        /* §M · The legend explained a colour code for market effect. There is no market
           effect on this screen any more, so the legend has nothing to explain. */
        semLegend: [],
        current: [], outlook: [], forces: [], hasForces: false, spark: null, hasSpark: false,
        outlookNote: mkIT ? 'Nessuna fonte previsionale è ingerita. Questo portale non pubblica una previsione di mercato.' : 'No forward-looking source is ingested. This portal publishes no market forecast.',
        weather: { state: mkNotIngested, note: mkIT ? 'Nessuna osservazione di condizione colturale o di rischio produttivo è ingerita in questo pacchetto.' : 'No crop-condition or production-risk observation is ingested in this package.' },
        traj: { past: '—', pastNote: mkIT ? 'nessuna serie storica ingerita' : 'no historical series ingested',
          now: String(N), next: '—', nextNote: mkIT ? 'nessuna fonte previsionale ingerita' : 'no forward-looking source ingested',
          nowArrow: HAS ? '●' : '—', nowLine: coverLine },
        trajNowColor: tok.color,

        hasPrice: !!ref,
        priceState: ref ? (mkIT ? 'UNA PIAZZA · UNA DEFINIZIONE DI PRODOTTO' : 'ONE MARKET · ONE PRODUCT DEFINITION') : (mkIT ? 'NESSUNA QUOTAZIONE CORRENTE' : 'NO CURRENT QUOTE'),
        priceStateColor: '#B1A9A7', priceSem: tok,
        price: ref
          ? { headline: ref.priceRaw || mkNum(ref.price), unit: ref.unit, product: ref.product + ' · ' + ref.market, geo: ref.market, period: mkSpan(ref), cadence: srcFreq }
          : { headline: '—', unit: '', product: (mkIT ? 'nessuna quotazione corrente ingerita per questa coltura' : 'no current quote ingested for this crop'), geo: '—', period: '—', cadence: srcFreq },
        priceChanges: priceChanges,
        chart: chart, hasChart: !!chart,

        /* §M · Production, trade, stocks, farmer confidence and input costs have no ingested
           record at all — the fixture supplied every figure those four cards showed, including
           a Baltic Dry Index value flagged state:'OBSERVED' that a reader could not tell apart
           from a real observation. They are emptied here; the markup that frames them should
           be deleted (see report). */
        prodSem: MK_TOK.off, prodState: mkNotIngested, prodStateColor: '#8F8886',
        prodHead: { k: mkIT ? 'Produzione' : 'Production', v: mkNotIngested, d: '', period: '—', geo: '—',
          src: mkIT ? 'nessuna serie di produzione, superficie, resa o scorte è ingerita' : 'no production, area, yield or stock series is ingested' },
        production: [],
        tradeSem: MK_TOK.off,
        trade: { state: mkNotIngested, note: mkIT ? 'Nessuna osservazione di import, export, scorte o bilancio di approvvigionamento è ingerita in questo pacchetto.' : 'No import, export, stock or supply-balance observation is ingested in this package.' },
        flow: [],
        confSem: MK_TOK.off, confColor: '#8F8886',
        confidence: { overall: '—', scale: '', current: mkNotIngested, expectations: mkNotIngested, change: mkNotIngested,
          caution: mkIT ? 'Nessuna serie di fiducia degli agricoltori è ingerita.' : 'No farmer-confidence series is ingested.',
          period: '—', cadence: '—', geo: '—', source: '—', splits: [] },
        confSplits: [],
        inputSem: MK_TOK.off, inputs: [],

        hasRegionRows: regionRows.length > 0, regionRows: regionRows,
        regional: {
          state: HAS ? (B.piazzaCount + (mkIT ? ' PIAZZE' : ' MARKETS')) : mkNotIngested,
          note: HAS
            ? (mkIT ? 'Ogni riga è una singola osservazione settimanale, l’ultima disponibile per quella piazza. Non c’è media e non c’è indice. ' + B.stoppedCount + ' righe su ' + N + ' stanno su serie ferme e la loro ultima quotazione non è un prezzo attuale.' : 'Each row is a single weekly observation, the latest available for that market. There is no average and no index. ' + B.stoppedCount + ' of ' + N + ' rows sit on stopped series and their last quote is not a current price.')
            : (mkIT ? 'Nessuna piazza quotata per questa coltura in questo pacchetto.' : 'No quoted market for this crop in this package.'),
          source: srcName,
        },

        adamaDays: nextW ? (wDays(nextW) === null ? '—' : wDays(nextW)) : '—',
        adamaDaysLabel: nextW
          ? (wDays(nextW) === null ? (mkIT ? 'data non definita a monte' : 'date not established upstream')
            : nextW.canonicalStatus === 'WINDOW_OPEN' ? (T.wDaysRemaining || 'days remaining') : (T.wDaysToOpen || 'days to open'))
          : (mkIT ? 'nessuna finestra mappata' : 'no window mapped'),
        adamaStance: nextW ? wst(nextW.canonicalStatus) : (mkIT ? 'NESSUNA FINESTRA MAPPATA' : 'NO WINDOW MAPPED'),
        adamaWhy: why.join(' '),
        wins: mWins, noWins: mWins.length === 0,
        products: mProducts, noProducts: mProducts.length === 0, productCount: PL ? PL.productCount : 0,
        /* §M · The old signal join could never match: real futureSignals crops read 'MAIS' and
           'TRANSVERSAL' against tab crops 'Maize' and 'Durum Wheat', and status is null on all
           3 records. It rendered nothing then and is declared empty now. */
        signals: [], noSignals: true,
        caseCount: mCases.length, goCases: () => this.radarWith({ fCrop: mc.crop }),
        changed: [], hasChanged: false,
        commentary: { text: '', src: '' },
        gaps: gaps,
        contextIt: [],
        fresh: fresh,
        goWindowsAll: () => this.go({ view: 'windows' }),
      };

      /* §M · The market-context strip on the opportunity-case screen printed the fixture
         temperature under a hardcoded "interpretation" caption. There is no verdict to put
         there, so the strip is switched off through its existing hasCsMarket guard. */
      csMarket = null;
    }

    /* §M · Industry tab. The 9 Agrofarma-Federchimica sector figures are gone: no industry
       record exists and no Agrofarma source is registered. The feasibility audit is rebuilt
       from what is actually connected — 1 route of 11 — and the source map is the registered
       MARKET sources, measured: exactly one, IT-SRC-AGRIFOOD. MK.INTERNAL (SELL-IN, SELL-OUT,
       CRM/PIPELINE, ORDERS, DISTRIBUTOR INVENTORY, WAREHOUSE STOCK...) is not passed on. */
    const cpMarketObj = (() => {
      const yes = mkIT ? 'SÌ' : 'YES', part = mkIT ? 'PARZIALE' : 'PARTIAL', no = 'NO', dash = '—';
      const none = mkIT ? 'nessuna serie ingerita' : 'no series ingested';
      const n = MK_OBS.length;
      const withPrev = MK_OBS.filter((x) => x.changeVsPrev !== null && x.changeVsPrev !== undefined).length;
      const stopped = MK_OBS.filter((x) => !x.isCurrentSeries).length;
      const src0 = MK_SRC.length ? MK_SRC[0] : null;
      const srcN = src0 ? src0.name : dash, srcF = mkFreq(src0 ? src0.frequency : null);
      const table = [
        [mkIT ? 'PREZZO PER PIAZZA' : 'PRICE BY MARKET', yes, srcN, srcF, mkIT ? 'Italia · piazza' : 'Italy · market',
          mkIT ? n + ' righe ingerite, ' + stopped + ' su serie ferme; le piazze non sono intercambiabili' : n + ' rows ingested, ' + stopped + ' on stopped series; markets are not interchangeable'],
        [mkIT ? 'MOMENTUM DI PREZZO' : 'PRICE MOMENTUM', part, srcN, srcF, mkIT ? 'piazza' : 'market',
          mkIT ? 'valido solo dentro una serie; variazione presente su ' + withPrev + ' righe su ' + n : 'valid only inside one series; change present on ' + withPrev + ' of ' + n + ' rows'],
        [mkIT ? 'SERIE STORICA' : 'PRICE HISTORY', no, dash, dash, dash,
          mkIT ? 'di ogni serie è ingerita solo l’ultima riga' : 'only the latest row of each series is ingested'],
        [mkIT ? 'PRODUZIONE / SUPERFICIE / RESA' : 'PRODUCTION / AREA / YIELD', no, dash, dash, dash, none],
        [mkIT ? 'IMPORT / EXPORT' : 'IMPORT / EXPORT', no, dash, dash, dash, none],
        [mkIT ? 'SCORTE' : 'STOCKS', no, dash, dash, dash, none],
        [mkIT ? 'BILANCIO DI APPROVVIGIONAMENTO' : 'SUPPLY BALANCE', no, dash, dash, dash, none],
        [mkIT ? 'COSTO DEGLI INPUT' : 'INPUT COST', no, dash, dash, dash, none],
        [mkIT ? 'FIDUCIA DEGLI AGRICOLTORI' : 'FARMER CONFIDENCE', no, dash, dash, dash, none],
        [mkIT ? 'PREVISIONE DI MERCATO' : 'MARKET OUTLOOK', no, dash, dash, dash,
          mkIT ? 'nessuna fonte previsionale ingerita' : 'no forward-looking source ingested'],
        [mkIT ? 'DIMENSIONE DEL MERCATO AGROFARMACI' : 'CROP PROTECTION MARKET SIZE', no, dash, dash, dash,
          mkIT ? 'nessuna fonte di settore è registrata' : 'no sector source is registered'],
      ];
      return {
        intro: mkIT
          ? 'Questo livello descrive il settore agrofarmaci italiano. Non descrive ADAMA e non può produrre quota di mercato, domanda di prodotto, vendite regionali o scorte del canale.'
          : 'This layer describes the Italian crop-protection industry. It does not describe ADAMA and it cannot produce market share, product demand, regional sales or channel stock.',
        caution: mkIT ? [
          'Nessuna cifra di settore è ingerita, quindi nessuna è mostrata.',
          'Un movimento di settore non direbbe nulla su una singola azienda, su un singolo prodotto o su una singola regione.',
          'Nulla di osservabile da fonti pubbliche sostiene un’affermazione sugli acquisti del canale.',
        ] : [
          'No sector figure is ingested, so none is displayed.',
          'A sector-level movement would say nothing about any single company, product or region.',
          'Nothing observable from public sources supports a statement about channel purchasing.',
        ],
        metrics: [],
        feasibility: table.map((p) => ({ field: p[0], status: p[1], statusColor: p[1] === yes ? '#00B152' : p[1] === part ? '#F89E18' : '#8F8886', source: p[2], cadence: p[3], geo: p[4], limit: p[5] })),
        sources: MK_SRC.map((x) => ({ name: x.name, cadence: mkFreq(x.frequency), geo: x.geography || x.country || '—',
          role: mkIT ? n + ' osservazioni di prezzo ingerite · ultima osservazione dichiarata dalla fonte ' + (x.latestObservation || '—') : n + ' price observations ingested · source-declared latest observation ' + (x.latestObservation || '—') })),
      };
    })();
