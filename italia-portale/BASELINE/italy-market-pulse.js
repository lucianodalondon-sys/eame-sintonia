/* Sintonia · MARKET PULSE — real Italian market conditions & outlook
   Every metric carries SOURCE / REFERENCE PERIOD / PUBLICATION or OBSERVATION DATE /
   GEOGRAPHY / UNIT / PRODUCT DEFINITION. Where a real observation was not retrieved,
   the field is marked NOT AVAILABLE or ROUTE MAPPED — never filled with a synthetic value.
   Market temperature labels are SINTONIA INTERPRETATION, not observed facts. */
(function () {
  const TEMP = {
    'SUPPORTIVE': '#00B152', 'BALANCED': '#B1A9A7', 'PRESSURED': '#F89E18',
    'COOLING': '#00A0DF', 'TIGHTENING': '#00A0DF', 'VOLATILE': '#9D1D96', 'MIXED SIGNALS': '#978B87'
  };

  // ---------- shared context (Italy-level, not crop-specific) ----------
  const CONFIDENCE_IT = {
    indicator: 'Indice del Clima di Fiducia (ICF) · Agricoltura',
    sector: 'AGRICULTURE · ALL SECTORS (no crop-level breakdown published)',
    scale: 'index, min −100 / max +100',
    overall: '−1.4',
    splits: [
      { k: 'Under-40 holdings', v: '+2.7' },
      { k: 'Over-40 holdings', v: '−2.2' }
    ],
    current: 'NOT SEPARATELY INGESTED', expectations: 'NOT SEPARATELY INGESTED',
    change: 'PRIOR-QUARTER DELTA NOT INGESTED',
    period: 'Q1 2025', cadence: 'QUARTERLY', geo: 'Italy', source: 'ISMEA · Indice del clima di fiducia',
    caution: 'ISMEA publishes agriculture-level and broad-sector confidence. It does NOT publish crop-specific sentiment. Do not read this as durum-wheat, maize or olive grower sentiment.'
  };

  const CONTEXT_IT = [
    { k: 'Agricultural value added', v: '+0.6%', note: 'Q4 2025 vs Q4 2024', src: 'ISMEA AgriMercati', geo: 'Italy' },
    { k: 'Agri-food exports', v: '+3%', note: 'Q4 2025, y/y', src: 'ISMEA AgriMercati', geo: 'Italy' },
    { k: 'Agri-food imports', v: '+6.6%', note: 'Q4 2025, y/y — imports growing faster than exports', src: 'ISMEA AgriMercati', geo: 'Italy' },
    { k: 'Consumer confidence', v: '92.6', note: 'March 2026, lowest since Oct 2023 — consumer, NOT farmer sentiment', src: 'ISTAT', geo: 'Italy' }
  ];

  const INPUT_ROUTES = [
    { k: 'FERTILIZER PRICE PRESSURE', state: 'ROUTE MAPPED · NOT INGESTED', route: 'Eurostat agricultural input price index (apri_pi_in_pm) · ISMEA indice dei costi di produzione', cadence: 'QUARTERLY / MONTHLY', geo: 'Italy · EU' },
    { k: 'ENERGY & AGRICULTURAL DIESEL', state: 'ROUTE MAPPED · NOT INGESTED', route: 'ISMEA weekly input-price monitoring (agricultural diesel surveyed every 15 days)', cadence: 'FORTNIGHTLY', geo: 'Italy' },
    { k: 'FREIGHT / LOGISTICS COST', state: 'OBSERVED', value: '2,843 points', delta: '+4.1% w/w · highest since 15 July', note: 'Baltic Dry Index, 3 August 2026 (2,696 on 27 July). Affects imported grain and imported input landed cost, not farm-gate cost directly.', src: 'Baltic Exchange, via AgroNotizie', cadence: 'DAILY', geo: 'Global' },
    { k: 'FARM PRODUCTION COST INDEX', state: 'ROUTE MAPPED · NOT INGESTED', route: 'ISMEA · Indice dei costi di produzione agricola', cadence: 'QUARTERLY', geo: 'Italy' }
  ];

  const NA = { state: 'NOT AVAILABLE' };

  // ---------- crops ----------
  const CROPS = [
    {
      key: 'maize', label: 'Maize', it: 'Mais', crop: 'Maize', color: '#F89E18',
      temp: 'MIXED SIGNALS',
      reading: 'Producer prices firmer year-on-year and a materially larger 2025 domestic crop. Sintonia reads the environment as workable but not strong: the price gain is measured against a weak base, and no ingested 2026 price observation confirms the trend has held.',
      drivers: [
        { d: '↑', t: 'Producer price vs year earlier', v: '+6.1% · €238.56/t Sep-2025 vs €224.88/t Sep-2024', tone: 'up' },
        { d: '↑', t: 'Domestic production', v: '5.5 Mt, +11.9% on 2024', tone: 'up' },
        { d: '↑', t: 'Sown area', v: '~541,000 ha, +9.2%', tone: 'up' },
        { d: '↑', t: 'Yield', v: '10.2 t/ha, +2.5%', tone: 'up' },
        { d: '↑', t: 'Freight cost', v: 'Baltic Dry 2,843 (+4.1% w/w, 3 Aug 2026)', tone: 'down' },
        { d: '○', t: 'Current-season 2026 price', v: 'NOT INGESTED — weekly ISMEA piazza series available but not connected', tone: 'flat' }
      ],
      current: [
        { k: 'PRICE MOMENTUM', v: 'FIRM vs LAST YEAR', tone: 'up', meta: 'last ingested observation Sep 2025' },
        { k: 'PRODUCTION', v: 'EXPANDED', tone: 'up', meta: '2025 campaign' },
        { k: 'SUPPLY', v: 'NOT AVAILABLE', tone: 'na', meta: 'ISMEA supply balance not ingested' },
        { k: 'FARMER CONFIDENCE', v: 'SECTOR-LEVEL ONLY', tone: 'na', meta: 'ICF Agriculture −1.4, Q1 2025' }
      ],
      outlook: [
        { k: 'PRODUCTION OUTLOOK', v: 'ROUTE MAPPED', tone: 'na', meta: 'EU Short-Term Outlook · JRC MARS maize yield bulletin' },
        { k: 'INPUT PRESSURE', v: 'LOGISTICS RISING', tone: 'down', meta: 'freight only; fertilizer/energy not ingested' },
        { k: 'EU OUTLOOK', v: 'NOT INGESTED', tone: 'na', meta: 'European Commission cereals balance sheet' }
      ],
      outlookNote: 'Sintonia does not forecast. The next 3–6 months line reads only from published forward-looking sources; where none has been ingested the field stays empty.',
      price: {
        headline: '€238.56', unit: '€/t', product: 'Maize, national — ISMEA origin price',
        geo: 'ITALY', period: 'September 2025', published: 'ISMEA AgriMercati, published 22 January 2026', cadence: 'MONTHLY', timeSeries: true,
        changes: [{ k: 'YEAR-ON-YEAR', v: '+6.1%', tone: 'up' }, { k: 'WEEK-ON-WEEK', v: 'NOT INGESTED', tone: 'na' }, { k: 'MONTH-ON-MONTH', v: 'NOT INGESTED', tone: 'na' }],
        points: [
          { label: 'Sep 2024', v: 224.88, s: 0 },
          { label: 'Sep 2025', v: 238.56, s: 0 }
        ],
        series: [{ name: 'ISMEA origin · maize national, €/t', color: '#F89E18' }],
        chartNote: 'Two observations only. A 12-month curve is available at source (ISMEA weekly prices by piazza) but has not been ingested for this demonstration — no interpolated line is drawn.'
      },
      regional: { state: 'ROUTE MAPPED', note: 'ISMEA publishes maize origin prices by piazza (Milano, Padova, Udine, Cremona and others) on a weekly cadence. Values are not ingested here, so no regional comparison is displayed. Piazze differ in sale condition (f.co magazzino arrivo for maize) — they are not interchangeable.', source: 'ISMEA Mercati · prezzi per piazza · origine · mais' },
      production: [
        { k: 'Production', v: '5.5 Mt', d: '+11.9%', period: '2025 campaign', src: 'ISMEA', geo: 'Italy' },
        { k: 'Area', v: '~541,000 ha', d: '+9.2%', period: '2025', src: 'ISMEA', geo: 'Italy' },
        { k: 'Yield', v: '10.2 t/ha', d: '+2.5%', period: '2025', src: 'ISMEA', geo: 'Italy' }
      ],
      trade: { state: 'NOT AVAILABLE', note: 'Italy is a structural maize importer, but no current import/export volume has been ingested. ISMEA BD commercio estero is the mapped route. An increase in imports would NOT by itself indicate rising demand — it can equally reflect a production shortfall, stock rebuilding, price arbitrage or processing displacement.' },
      confidence: CONFIDENCE_IT,
      weather: { state: 'ROUTE MAPPED', note: 'JRC MARS Bulletin publishes maize crop-condition and yield forecasts monthly during the season. Use for production risk only — never as a price forecast.', src: 'JRC MARS' },
      commentary: { text: 'The 2025 Italian maize campaign expanded on all three axes — area, yield and total output — while the producer price still gained on the year. Both cannot be read as one signal: the price comparison is against a low 2024 base.', src: 'Sintonia reading of ISMEA AgriMercati, 22 Jan 2026' },
      changed: [
        { when: '22 Jan 2026', t: 'ISMEA AgriMercati confirmed the 2025 maize balance: area +9.2%, yield +2.5%, output +11.9%.', src: 'ISMEA' },
        { when: '03 Aug 2026', t: 'Baltic Dry Index jumped 4.1% in a week to 2,843 — highest since mid-July. Raises landed cost of imported grain.', src: 'Baltic Exchange via AgroNotizie' }
      ],
      gaps: ['Current-season 2026 weekly piazza prices', 'Import / export volumes and self-sufficiency', 'Fertilizer and energy cost index values', 'EU maize balance-sheet outlook']
    },

    {
      key: 'durum', label: 'Durum Wheat', it: 'Frumento duro', crop: 'Durum Wheat', color: '#00A0DF',
      temp: 'PRESSURED',
      reading: 'A full year of ingested observations shows the national durum price stepping down from ~€291/t (Jul-2025) to a CUN range of €231–236/t in late May 2026, then flattening. Imported durum is the only quotation rising. Sintonia reads grower economics as pressured, and reads the August flatness as a pause, not a recovery.',
      drivers: [
        { d: '↓', t: 'National producer price over 12 months', v: '€290.92/t Jul-2025 → €231–236/t CUN late-May 2026', tone: 'down' },
        { d: '↓', t: 'CUN cumulative movement since 30 March 2026', v: 'down to −€17/t across quality classes', tone: 'down' },
        { d: '↔', t: 'Origin prices, most recent reading', v: 'all 11 ISMEA piazze stable, 3 Aug 2026', tone: 'flat' },
        { d: '↑', t: 'Imported durum quotations', v: 'Milano and Altamura +€10/t in two weeks (Aug 2026)', tone: 'down' },
        { d: '↑', t: 'Domestic production', v: '~3.6 Mt in 2025, +3.4% on better yields', tone: 'flat' },
        { d: '↑', t: 'Freight cost', v: 'Baltic Dry 2,843, +4.1% w/w (3 Aug 2026)', tone: 'down' }
      ],
      current: [
        { k: 'PRICE MOMENTUM', v: 'WEAK · FLAT AT A LOW LEVEL', tone: 'down', meta: 'CUN + ISMEA origin, Aug 2026' },
        { k: 'PRODUCTION', v: 'ABOVE PRIOR YEAR', tone: 'up', meta: '2025, +3.4%' },
        { k: 'IMPORT COMPETITION', v: 'STRENGTHENING', tone: 'down', meta: 'foreign durum the only rising quotation' },
        { k: 'FARMER CONFIDENCE', v: 'SECTOR-LEVEL ONLY', tone: 'na', meta: 'ICF Agriculture −1.4, Q1 2025' }
      ],
      outlook: [
        { k: 'PRODUCTION OUTLOOK', v: 'NORTH-AMERICA DEPENDENT', tone: 'na', meta: 'analysts: an abundant western-Canada crop would hold markets steady into early autumn' },
        { k: 'INPUT PRESSURE', v: 'LOGISTICS RISING', tone: 'down', meta: 'freight; farm input indices not ingested' },
        { k: 'EU OUTLOOK', v: 'NOT INGESTED', tone: 'na', meta: 'EC cereals short-term outlook' }
      ],
      outlookNote: 'The North-America dependency line is a market-analyst statement reported in June 2026, not a Sintonia forecast and not a price prediction.',
      price: {
        headline: '€231–236', unit: '€/t', product: 'Durum wheat fino, national — CUN Grano Duro orientation price (min–max)',
        geo: 'ITALY', period: 'week of 25 May 2026', published: 'CUN Grano Duro session, reported 1 June 2026', cadence: 'WEEKLY (Monday CUN session)', timeSeries: true,
        changes: [{ k: 'vs PRIOR SESSION', v: 'stable (−€4/t the week before)', tone: 'flat' }, { k: 'vs 30 MARCH 2026', v: 'down to −€17/t', tone: 'down' }, { k: 'vs JULY 2025', v: '≈ −20%', tone: 'down' }],
        points: [
          { label: 'Jul 2025', v: 290.92, s: 0 },
          { label: 'Sep 2025', v: 271.50, s: 0 },
          { label: 'Dec 2025', v: 274.90, s: 0 },
          { label: '29 Jan 2026', v: 274.50, s: 1 },
          { label: '28 Jan 2026', v: 245.00, s: 2 },
          { label: '02 Feb 2026', v: 254.00, s: 3 },
          { label: '25 May 2026', v: 233.50, s: 4 }
        ],
        series: [
          { name: 'ISMEA origin · durum fino, national monthly avg', color: '#00A0DF' },
          { name: 'ISMEA origin · Bologna piazza', color: '#00B152' },
          { name: 'CWAD #1 FOB Toronto (import reference)', color: '#978B87' },
          { name: 'FOB Great Lakes (import reference)', color: '#B1A9A7' },
          { name: 'CUN Grano Duro · national orientation, mid of €231–236 range', color: '#F89E18' }
        ],
        chartNote: 'Five different price series. They are deliberately NOT connected into one line: they differ in sale condition, quality class, origin and market. Comparing across series is not methodologically valid; read each series against itself.'
      },
      regional: {
        state: 'PARTIAL',
        rows: [
          { p: 'Bologna', v: '€274.50/t', d: '−1.8% w/w', note: 'ISMEA origin, durum fino from producer · 29 Jan 2026' },
          { p: 'Grosseto', v: 'DECLINING', d: '↓', note: 'ISMEA origin, loss recorded week 27 Jan – 2 Feb 2026' },
          { p: 'Ferrara', v: 'DECLINING', d: '↓', note: 'ISMEA origin, loss recorded week 27 Jan – 2 Feb 2026' },
          { p: 'Milano', v: 'DECLINING (national) / RISING (imported)', d: '↓ / ↑', note: 'second consecutive negative reading on national, 4 May 2026; imported durum +€10/t over two weeks, Aug 2026' },
          { p: 'Catania', v: 'DECLINING', d: '↓', note: 'ISMEA origin, second consecutive negative reading · 4 May 2026' },
          { p: 'Palermo', v: 'DECLINING', d: '↓', note: 'ISMEA origin, second consecutive negative reading · 4 May 2026' },
          { p: 'Altamura', v: 'RISING (imported only)', d: '↑', note: 'imported durum +€10/t over two weeks · Aug 2026; Canadian 2nd quality +€10/t in July' }
        ],
        note: '11 ISMEA origin piazze are surveyed for durum fino; 7 are shown because only these carry an ingested dated observation. On 3 August 2026 all 11 were reported stable. Since the Ministry decree of 16 January 2026 establishing the CUN Grano Duro, borsa merci quotations for national durum are suspended — only imported durum is still quoted there. Piazza values are not interchangeable.',
        source: 'ISMEA Mercati · prezzi per piazza · origine · frumento duro; CUN Grano Duro; via AgroNotizie weekly monitoring'
      },
      production: [
        { k: 'Production', v: '~3.6 Mt', d: '+3.4%', period: '2025 campaign', src: 'ISMEA', geo: 'Italy' },
        { k: 'Yields', v: 'ABOVE PRIOR YEAR', d: '↑', period: '2025', src: 'ISMEA — "more favourable weather, overall good quality profile"', geo: 'Italy' },
        { k: 'Yield forecast 2026', v: 'NOT INGESTED', d: '', period: '—', src: 'JRC MARS route mapped', geo: 'EU / Italy' }
      ],
      trade: { state: 'PARTIAL', note: 'No ingested Italian import/export tonnage. What IS observed is competitive pressure through price: imported durum is the only quotation rising in Italy while national quotations fall, and Canadian CWAD FOB Toronto stood at €245/t on 28 January 2026, +€1/t on the week. Rising imported-durum prices do not mean Italian demand is rising — currency, freight and North-American crop conditions all move that quotation.' },
      confidence: Object.assign({}, CONFIDENCE_IT, { caution: 'ISMEA publishes ICF for agriculture overall. There is no published DURUM WHEAT grower confidence. Even a cereals-level confidence figure would not equal durum-wheat sentiment.' }),
      weather: { state: 'PARTIAL', note: 'Drought in central-southern Saskatchewan and western North Dakota was under market attention in June 2026 — a supply-side risk to the import reference, not to the Italian crop.', src: 'market analysis via AgroNotizie, June 2026' },
      commentary: { text: 'Two structural changes matter as much as the price level. First, the CUN Grano Duro (decree 16 Jan 2026) replaced borsa merci quotations for national durum, so the national price reference itself changed mid-year. Second, the widening gap between falling national and rising imported quotations is the clearest current market fact.', src: 'Sintonia reading of CUN / ISMEA / AgroNotizie, Jan–Aug 2026' },
      changed: [
        { when: '16 Jan 2026', t: 'Ministry decree established the CUN Grano Duro; borsa merci quotations for national durum suspended. The reference series changed — historical comparisons must be handled carefully.', src: 'MASAF decree' },
        { when: '04 May 2026', t: 'Sixth CUN session confirmed a downward trend, cumulative falls to €17/t since 30 March across quality classes.', src: 'CUN Grano Duro' },
        { when: '03 Aug 2026', t: 'All 11 ISMEA origin piazze stable; imported durum at Milano and Altamura +€10/t in two weeks.', src: 'ISMEA via AgroNotizie' }
      ],
      gaps: ['Italian durum import and export tonnage', 'Supply balance and stock change', 'Cereals-sector farmer confidence at sector granularity', 'Production-cost index values for durum systems']
    },

    {
      key: 'soft', label: 'Soft Wheat', it: 'Frumento tenero', crop: 'Wheat', color: '#7DB41E',
      temp: 'BALANCED',
      reading: 'The flattest of the ingested markets. Prices moved inside a €245–248/t band across the second half of 2025 and production eased slightly. Sintonia reads it as balanced — with the honest caveat that no 2026 observation has been ingested, so "balanced" describes the last confirmed state, not today.',
      drivers: [
        { d: '↔', t: 'Producer price band, Jul–Dec 2025', v: '€247.61 → €245.42 → €246.79 /t', tone: 'flat' },
        { d: '↓', t: 'Domestic production', v: '~2.5 Mt in 2025, slightly below 2024', tone: 'flat' },
        { d: '○', t: '2026 price observations', v: 'NOT INGESTED', tone: 'flat' }
      ],
      current: [
        { k: 'PRICE MOMENTUM', v: 'FLAT', tone: 'flat', meta: 'last ingested observation Dec 2025' },
        { k: 'PRODUCTION', v: 'SLIGHTLY BELOW PRIOR YEAR', tone: 'flat', meta: '2025' },
        { k: 'SUPPLY', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'FARMER CONFIDENCE', v: 'SECTOR-LEVEL ONLY', tone: 'na', meta: 'ICF Agriculture −1.4, Q1 2025' }
      ],
      outlook: [
        { k: 'PRODUCTION OUTLOOK', v: 'ROUTE MAPPED', tone: 'na', meta: 'JRC MARS · EC cereals balance sheet' },
        { k: 'INPUT PRESSURE', v: 'LOGISTICS RISING', tone: 'down', meta: 'freight only' },
        { k: 'EU OUTLOOK', v: 'NOT INGESTED', tone: 'na', meta: '' }
      ],
      outlookNote: 'No forward-looking soft-wheat source has been ingested. The outlook column stays deliberately thin rather than being filled by inference from durum.',
      price: {
        headline: '€246.79', unit: '€/t', product: 'Soft wheat, national — ISMEA origin price',
        geo: 'ITALY', period: 'December 2025', published: 'ISMEA AgriMercati, published 22 January 2026', cadence: 'MONTHLY', timeSeries: true,
        changes: [{ k: 'vs OCT 2025', v: '+0.6%', tone: 'flat' }, { k: 'vs JUL 2025', v: '−0.3%', tone: 'flat' }, { k: '2026 CHANGE', v: 'NOT INGESTED', tone: 'na' }],
        points: [{ label: 'Jul 2025', v: 247.61, s: 0 }, { label: 'Oct 2025', v: 245.42, s: 0 }, { label: 'Dec 2025', v: 246.79, s: 0 }],
        series: [{ name: 'ISMEA origin · soft wheat national, €/t', color: '#7DB41E' }],
        chartNote: 'Three monthly observations from one consistent series. Intermediate months exist at source but were not ingested.'
      },
      regional: { state: 'ROUTE MAPPED', note: 'ISMEA surveys soft-wheat origin prices by piazza weekly; the Bologna exchange is the national reference for central-northern cereals and distinguishes national from imported product. Not ingested here.', source: 'ISMEA Mercati · Borsa Merci Bologna' },
      production: [{ k: 'Production', v: '~2.5 Mt', d: 'slightly below 2024', period: '2025 campaign', src: 'ISMEA', geo: 'Italy' }],
      trade: NA,
      confidence: CONFIDENCE_IT,
      weather: { state: 'ROUTE MAPPED', note: 'JRC MARS soft-wheat yield forecast, monthly in season.', src: 'JRC MARS' },
      commentary: { text: 'Nothing in the ingested record moves soft wheat. That is itself a finding: a flat market gives commercial conversations no price-driven urgency in either direction.', src: 'Sintonia reading of ISMEA AgriMercati' },
      changed: [{ when: '22 Jan 2026', t: 'ISMEA confirmed 2025 soft-wheat output ~2.5 Mt, marginally below 2024, with the price band essentially unchanged.', src: 'ISMEA' }],
      gaps: ['2026 price observations', 'Trade and supply balance', 'Regional piazza spread']
    },

    {
      key: 'olive', label: 'Olive / Olive Oil', it: 'Olivo / Olio d\'oliva', crop: 'Olive', color: '#009845',
      temp: 'PRESSURED',
      reading: 'Origin quotations fell hard through autumn 2025 and have since gone flat at a level growers and their organisations publicly describe as insufficient. Stocks are up a third and import pressure is real. Sintonia reads the market as pressured with a sharply segmented structure: PDO/PGI lines hold value, conventional bulk does not.',
      drivers: [
        { d: '↓', t: 'Origin price, conventional extra virgin', v: 'from €7.00–8.00/kg high-quality at Bari (Dec 2025) to a flat, low market by mid-2026', tone: 'down' },
        { d: '↑', t: 'Stocks', v: '~153,000 t extra virgin at 30 Nov 2025, +33% y/y', tone: 'down' },
        { d: '↑', t: 'Import pressure', v: 'marked rise in foreign arrivals, notably from Greece', tone: 'down' },
        { d: '↔', t: 'Most recent weekly quotations', v: 'Bari flat at 0.0%, Trapani −2.8% (week 24–30 Aug 2026)', tone: 'flat' },
        { d: '↑', t: 'Denominations hold value', v: 'PGI Toscano €12.00/kg, DOP Garda ~€15.50/kg, Chianti Classico ~€16/kg, Brisighella >€23/kg', tone: 'up' },
        { d: '↑', t: 'Production cost estimate', v: '€8.87–10.31/kg to produce quality extra virgin (sector reconstruction) vs a €4.55/kg Bari quotation', tone: 'down' }
      ],
      current: [
        { k: 'PRICE MOMENTUM', v: 'FLAT AT A LOW LEVEL', tone: 'down', meta: 'week 24–30 Aug 2026' },
        { k: 'STOCKS', v: 'HIGH', tone: 'down', meta: '+33% y/y at 30 Nov 2025' },
        { k: 'IMPORT PRESSURE', v: 'ELEVATED', tone: 'down', meta: 'Spanish EVOO €4.25–4.26/kg, week of 16 Jan 2026' },
        { k: 'GROWER ECONOMICS', v: 'BELOW STATED COST OF PRODUCTION', tone: 'down', meta: 'conventional bulk segment' }
      ],
      outlook: [
        { k: 'MARKET STRUCTURE', v: 'SEGMENTED', tone: 'na', meta: 'certified lines defend value; volume does not follow' },
        { k: 'SUPPLY MANAGEMENT', v: 'UNDER DISCUSSION', tone: 'na', meta: 'temporary market withdrawal raised under Reg. (EU) 1308/2013 art. 167 bis' },
        { k: 'EU OUTLOOK', v: 'ROUTE MAPPED', tone: 'na', meta: 'EC olive-oil dashboard: prices, production, trade, balance sheets' }
      ],
      outlookNote: 'The withdrawal discussion is a reported industry position, not an adopted measure and not a Sintonia prediction.',
      price: {
        headline: '€4.55', unit: '€/kg', product: 'Extra virgin olive oil, unspecified origin — ISMEA origin quotation, Bari',
        geo: 'BARI (PUGLIA)', period: 'survey week 24–30 August 2026', published: 'ISMEA Mercati weekly price survey', cadence: 'WEEKLY',
        changes: [{ k: 'WEEK-ON-WEEK', v: '0.0%', tone: 'flat' }, { k: 'MONTH-ON-MONTH', v: 'NOT INGESTED', tone: 'na' }, { k: 'YEAR-ON-YEAR', v: 'NOT INGESTED', tone: 'na' }],
        points: [
          { label: '16 Dec 2025', v: 7.50, s: 1 },
          { label: '~16 Jan 2026', v: 7.50, s: 2 },
          { label: '~16 Jan 2026 ', v: 4.255, s: 3 },
          { label: '24–30 Aug 2026', v: 4.55, s: 0 },
          { label: '24–30 Aug 2026 ', v: 6.90, s: 4 }
        ],
        series: [
          { name: 'ISMEA origin · EVOO ns, Bari (€/kg)', color: '#009845' },
          { name: 'Borsa Merci Bari · high-quality EVO <0.40% acidity, mid of €7–8 range', color: '#00B152' },
          { name: 'ISMEA · quality Italian extra virgin, "above €7.5/kg"', color: '#F89E18' },
          { name: 'ISMEA international · Spain EVOO (€4.25–4.26/kg)', color: '#978B87' },
          { name: 'ISMEA origin · EVOO ns, Trapani (€/kg)', color: '#9D1D96' }
        ],
        chartNote: 'Five different product definitions — generic vs high-quality vs national-quality vs Spanish import reference vs a second Italian piazza. They are shown as separate observations, never as one price history. The gap between them IS the story.'
      },
      regional: {
        state: 'OBSERVED',
        rows: [
          { p: 'Bari · EVOO ns', v: '€4.55/kg', d: '0.0%', note: 'ISMEA origin, week 24–30 Aug 2026' },
          { p: 'Bari · Olio DOP Terra di Bari', v: '€4.55/kg', d: '0.0%', note: 'ISMEA origin, week 24–30 Aug 2026' },
          { p: 'Trapani · EVOO ns', v: '€6.90/kg', d: '−2.8%', note: 'ISMEA origin, week 24–30 Aug 2026' },
          { p: 'Siena · Olio IGP Toscano', v: '€12.00/kg', d: '0.0%', note: 'ISMEA origin, week 24–30 Aug 2026' },
          { p: 'Brindisi · lampante ns', v: '€3.00/kg', d: '—', note: 'ISMEA origin, week 24–30 Aug 2026 — lampante is not a comparable grade' }
        ],
        note: 'These are five different products in five different places in one week — not a price range for one product. Lampante in particular is a refining-grade oil and must never be averaged with extra virgin.',
        source: 'ISMEA Mercati · olio d\'oliva · prezzi per piazza'
      },
      production: [
        { k: 'Stocks, extra virgin', v: '~153,000 t', d: '+33% y/y', period: 'at 30 November 2025', src: 'ICQRF Frantoio Italia report, relayed by Coldiretti / Unaprol', geo: 'Italy' },
        { k: 'Production 2026/27', v: 'NOT INGESTED', d: '', period: '—', src: 'ISMEA production estimate route mapped', geo: 'Italy' },
        { k: 'Estimated production cost', v: '€8.87–10.31/kg', d: '', period: 'sector estimate, 2026', src: 'industry cost reconstruction (not an official statistic)', geo: 'Italy' }
      ],
      trade: { state: 'PARTIAL', note: 'Foreign arrivals rose markedly in the early months of the campaign, Greece prominent among them. Volumes have not been ingested. The Spanish EVOO reference at €4.25–4.26/kg (week of 16 Jan 2026) is the clearest observable measure of import pressure — a landed alternative below the Italian quality price.' },
      confidence: Object.assign({}, CONFIDENCE_IT, { caution: 'ISMEA publishes agriculture-level ICF. Producer-organisation statements (Coldiretti, Unaprol, Italia Olivicola) are advocacy positions, valuable as evidence of sentiment but not a measured confidence index. Sintonia keeps them separate.' }),
      weather: { state: 'PARTIAL', note: 'Adverse climatic events and plant disease reduced yields in the main olive districts in recent campaigns, per ISMEA-based sector analysis. Current-season crop condition is not ingested.', src: 'sector analysis of ISMEA data, 2026' },
      commentary: { text: 'The 2026 opening was described as an apparent truce after the autumn collapse: quotations stopped falling but settled at a level most producers judge insufficient. Stabilisation of the list price is not the same thing as economic recovery in the chain — and that distinction is the whole reading.', src: 'ICQRF / ISMEA analysis, January 2026' },
      changed: [
        { when: '16 Dec 2025', t: 'Bari Borsa Merci olive-oil commission cut high-quality EVO by €0.20/kg to €7.00–8.00/kg in the last session of 2025.', src: 'Borsa Merci Bari' },
        { when: 'Jan 2026', t: 'ICQRF Frantoio Italia report 1/2026 certified abundant availability; ISMEA international prices put Spanish EVOO at €4.25–4.26/kg.', src: 'ICQRF · ISMEA' },
        { when: '24–30 Aug 2026', t: 'Weekly ISMEA survey: Bari flat, Trapani −2.8%, Siena IGP Toscano unchanged at €12.00/kg.', src: 'ISMEA' }
      ],
      gaps: ['Current-campaign production estimate', 'Import volumes by origin', 'EC olive-oil balance sheet values', 'Regional crop condition']
    },

    {
      key: 'wine', label: 'Grapevine / Wine', it: 'Vite / Vino', crop: 'Grapevine', color: '#9D1D96',
      temp: 'PRESSURED',
      reading: 'A third consecutive year of falling grape prices across most Italian denominations, with double-digit falls on major DOCG names, against volume that barely moved. Sintonia reads the market as pressured — with real, named exceptions that must not be flattened into a national verdict.',
      drivers: [
        { d: '↓', t: 'Grape prices, most regions', v: 'widespread annual declines, several double-digit — vendemmia 2025', tone: 'down' },
        { d: '↓', t: 'Third consecutive year of decline', v: 'many denominations down for the third year running', tone: 'down' },
        { d: '↔', t: 'Wine production', v: '~44 M hl, +1% on 2024', tone: 'flat' },
        { d: '↔', t: 'Wine-grape volume', v: '~66 M quintals, −0.4%', tone: 'flat' },
        { d: '↓', t: 'Commercial outlets', v: 'lower domestic consumption and reduced export cited as driving a red-wine surplus', tone: 'down' },
        { d: '↑', t: 'Named exceptions', v: 'Puglia Primitivo ~+40%, Bolgheri Rosso ~+21%, Glera Conegliano-Valdobbiadene stable', tone: 'up' }
      ],
      current: [
        { k: 'PRICE MOMENTUM', v: 'DOWN · THIRD YEAR', tone: 'down', meta: 'vendemmia 2025 list prices' },
        { k: 'PRODUCTION', v: 'ESSENTIALLY FLAT', tone: 'flat', meta: '+1% wine, −0.4% grapes' },
        { k: 'DEMAND SIGNAL', v: 'WEAKER OUTLETS REPORTED', tone: 'down', meta: 'trade-association statements, not a measured index' },
        { k: 'FARMER CONFIDENCE', v: 'SECTOR-LEVEL ONLY', tone: 'na', meta: 'ICF Agriculture −1.4, Q1 2025' }
      ],
      outlook: [
        { k: 'PRICE OUTLOOK', v: 'REBALANCING PHASE', tone: 'na', meta: 'analysis to 28 Feb 2026 describes progressive rebalancing after the 2022 peak' },
        { k: 'ASSET VALUES', v: 'FOLLOWING GRAPES DOWN', tone: 'down', meta: 'vineyard and estate valuations reported to be adjusting' },
        { k: 'EU OUTLOOK', v: 'ROUTE MAPPED', tone: 'na', meta: 'EC wine dashboard and balance sheets' }
      ],
      outlookNote: 'US tariffs and unpredictable weather are cited in the sector reporting as pressures on the Veneto chain. Sintonia records them as reported context, not as quantified drivers.',
      price: {
        headline: 'DECLINING', unit: '€/quintal, by denomination', product: 'Wine grapes — Chamber of Commerce list prices, elaborated by BMTI',
        geo: 'ITALY · BY DENOMINATION AND PIAZZA', period: 'vendemmia 2025', published: 'Unioncamere / BMTI report, May 2026', cadence: 'ANNUAL (per harvest)',
        changes: [{ k: 'YEAR-ON-YEAR', v: 'widespread declines, several double-digit', tone: 'down' }, { k: 'MULTI-YEAR', v: 'third consecutive year of decline for many denominations', tone: 'down' }],
        points: [
          { label: 'Brunello di Montalcino DOCG', v: 250, s: 0 },
          { label: 'Chianti Classico DOCG', v: 170, s: 0 },
          { label: 'Nobile di Montepulciano DOCG', v: 130, s: 0 },
          { label: 'Sagrantino DOCG', v: 120, s: 0 },
          { label: 'Morellino di Scansano DOCG', v: 80, s: 0 },
          { label: 'Montepulciano d\'Abruzzo DOC', v: 50, s: 0 }
        ],
        series: [{ name: 'Chamber of Commerce list price, vendemmia 2025 (€/quintal)', color: '#9D1D96' }],
        chartNote: 'These are six DIFFERENT denominations at one harvest, not a time series. Each carries its own year-on-year change: Brunello over −40%, Nobile −15%, Sagrantino ~−15%, Morellino −26%, Montepulciano d\'Abruzzo −20%, Chianti Classico −5%.'
      },
      regional: {
        state: 'OBSERVED',
        rows: [
          { p: 'Veneto · average, all grapes', v: '€0.66/kg', d: '−0.5%', note: 'Veneto Agricoltura observatory, vendemmia 2025' },
          { p: 'Treviso', v: '€0.72/kg', d: '+4.1%', note: 'led by Refosco DOC +37.5% and strong IGT gains' },
          { p: 'Verona', v: '€0.72/kg', d: '−4.9%', note: 'Amarone / Recioto DOC zone −14%' },
          { p: 'Padova', v: '€0.52/kg', d: '+0.6%', note: 'Cabernet ~+12%, Merlot −6.7%' },
          { p: 'Toscana · Montalcino', v: '€250/q', d: 'over −40%', note: 'sangiovese for Brunello DOCG' },
          { p: 'Umbria · Perugia', v: 'MINIMA −30%', d: '−30% / −33.3%', note: 'Borsa Merci list of 14 Oct 2025; prices actually paid to producers, franco delivery' },
          { p: 'Puglia · Primitivo', v: 'RISING', d: '~+40%', note: 'principal national exception' }
        ],
        note: 'Two different units coexist in this market: €/kg in the Veneto observatory and €/quintal in the Chamber of Commerce denomination lists. They are not converted here. Perugia is noted separately because it publishes prices actually paid to producers rather than inter-trade prices.',
        source: 'BMTI / Unioncamere · Veneto Agricoltura · Camera di Commercio dell\'Umbria'
      },
      production: [
        { k: 'Wine production', v: '~44 M hl', d: '+1%', period: '2025', src: 'OIV, via BMTI', geo: 'Italy' },
        { k: 'Wine-grape production', v: '~66 M quintals', d: '−0.4%', period: '2025', src: 'ISTAT, via BMTI', geo: 'Italy' },
        { k: 'Veneto output', v: '~12 M hl', d: '+2%', period: '2025 estimate', src: 'Veneto Agricoltura', geo: 'Veneto — first producing region' }
      ],
      trade: { state: 'PARTIAL', note: 'Reduced export and lower domestic consumption are cited by trade associations as producing a surplus, particularly in reds. No ingested export volume or value. US tariffs are reported as a pressure on the Veneto chain. Treat all of this as reported context, not measured trade data.' },
      confidence: Object.assign({}, CONFIDENCE_IT, { caution: 'No published wine-sector confidence index has been ingested. Grower-organisation statements are recorded as sentiment evidence, not as an index.' }),
      weather: { state: 'PARTIAL', note: 'Unpredictable climatic conditions cited in regional reporting; 2025 quality was generally judged good. No ingested crop-condition series.', src: 'regional sector reporting' },
      commentary: { text: 'The most instructive detail in the BMTI analysis is causal, not numerical: early-vendemmia estimates pointed to +8% output, final figures came in far lower, but the initial estimate had already anchored price negotiation. A forecast, not a harvest, moved the market.', src: 'BMTI / CIA statements, vendemmia 2025 report' },
      changed: [
        { when: '14 Oct 2025', t: 'Perugia Borsa Merci list showed Umbrian grape prices down to −30% on minima and −33.3% on maxima against 2024.', src: 'Camera di Commercio dell\'Umbria' },
        { when: 'May 2026', t: 'Unioncamere / BMTI published the vendemmia 2025 grape-price report: widespread declines, exceptions in Puglia and Bolgheri.', src: 'BMTI' },
        { when: '28 Feb 2026', t: 'Updated BMTI-based analysis reported vineyard and estate valuations beginning to follow grape prices down.', src: 'Unioncamere / BMTI' }
      ],
      gaps: ['Current 2026 harvest price formation', 'Export volumes and values', 'Wine-sector confidence index', 'Stock levels in cellar']
    },

    {
      key: 'tomato', label: 'Tomato', it: 'Pomodoro', crop: 'Tomato', color: '#F89E18',
      temp: 'MIXED SIGNALS',
      reading: 'Not enough ingested observation to give this market a defensible reading. Sintonia shows the mapped routes and refuses the label rather than manufacturing one.',
      thin: true,
      drivers: [{ d: '○', t: 'No ingested price, production or trade observation', v: 'processing-tomato contract prices, OI Pomodoro agreements and ISMEA fruit-and-vegetable series are the mapped routes', tone: 'flat' }],
      current: [
        { k: 'PRICE MOMENTUM', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'PRODUCTION', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'SUPPLY', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'FARMER CONFIDENCE', v: 'SECTOR-LEVEL ONLY', tone: 'na', meta: 'ICF Agriculture −1.4, Q1 2025' }
      ],
      outlook: [{ k: 'OUTLOOK', v: 'NOT AVAILABLE', tone: 'na', meta: 'no forward-looking source ingested' }],
      outlookNote: 'A crop with an active Opportunity Radar case can still have no usable market layer. That combination is legitimate and is shown as-is.',
      price: null,
      regional: { state: 'ROUTE MAPPED', note: 'ISMEA surveys wholesale and origin prices for fresh tomato by piazza; processing tomato is priced through inter-branch organisation agreements (OI Pomodoro Nord Italia / Centro-Sud), a contract price rather than a market quotation.', source: 'ISMEA Mercati · OI Pomodoro' },
      production: [{ k: 'Production', v: 'NOT INGESTED', d: '', period: '—', src: 'ISTAT / ISMEA route mapped', geo: 'Italy' }],
      trade: NA,
      confidence: CONFIDENCE_IT,
      weather: { state: 'ROUTE MAPPED', note: 'JRC MARS does not publish a dedicated Italian processing-tomato yield forecast at this granularity.', src: '—' },
      commentary: { text: 'The honest output for tomato is an empty market layer with named routes. Filling it would be the single easiest way to make this tool untrustworthy.', src: 'Sintonia' },
      changed: [],
      gaps: ['Processing-tomato contract price', 'Area and production', 'Fresh-tomato wholesale price series', 'Trade flows']
    },

    {
      key: 'sugarbeet', label: 'Sugar Beet', it: 'Barbabietola da zucchero', crop: 'Sugar Beet', color: '#00A0DF',
      temp: 'MIXED SIGNALS',
      reading: 'No ingested Italian sugar-beet market observation. The crop is priced largely through contracts with the processing industry rather than an open quotation, which is itself the reason a price-first market layer fits it badly.',
      thin: true,
      drivers: [{ d: '○', t: 'No ingested price, production or trade observation', v: 'EC sugar market observatory and ISMEA sector sheet are the mapped routes', tone: 'flat' }],
      current: [
        { k: 'PRICE MOMENTUM', v: 'NOT AVAILABLE', tone: 'na', meta: 'contract-priced crop' },
        { k: 'PRODUCTION', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'SUPPLY', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'FARMER CONFIDENCE', v: 'SECTOR-LEVEL ONLY', tone: 'na', meta: 'ICF Agriculture −1.4, Q1 2025' }
      ],
      outlook: [{ k: 'EU OUTLOOK', v: 'ROUTE MAPPED', tone: 'na', meta: 'European Commission sugar dashboard and balance sheet' }],
      outlookNote: '',
      price: null,
      regional: { state: 'ROUTE MAPPED', note: 'Beet is contracted with the sugar industry; there is no representative Italian spot quotation to compare across piazze.', source: 'EC sugar market observatory' },
      production: [{ k: 'Production', v: 'NOT INGESTED', d: '', period: '—', src: 'ISTAT route mapped', geo: 'Italy' }],
      trade: NA,
      confidence: CONFIDENCE_IT,
      weather: { state: 'ROUTE MAPPED', note: 'JRC MARS publishes sugar-beet yield forecasts within the EU bulletin.', src: 'JRC MARS' },
      commentary: { text: 'A contract-priced crop needs a different market layer than a quoted commodity. Building it on price momentum would misrepresent how the value is actually set.', src: 'Sintonia' },
      changed: [],
      gaps: ['Contract price and beet payment terms', 'Area and production', 'EU sugar balance']
    },

    {
      key: 'apple', label: 'Apple', it: 'Melo', crop: 'Apple', color: '#7DB41E',
      temp: 'MIXED SIGNALS',
      reading: 'No ingested Italian apple market observation, though the routes are unusually good: ISMEA surveys apple prices weekly (franco magazzino) and the EC fruit-and-vegetable dashboard covers the EU balance.',
      thin: true,
      drivers: [{ d: '○', t: 'No ingested price observation', v: 'ISMEA weekly apple price survey is franco magazzino, not f.co azienda — a different sale condition from most crops', tone: 'flat' }],
      current: [
        { k: 'PRICE MOMENTUM', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'PRODUCTION', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'SUPPLY', v: 'NOT AVAILABLE', tone: 'na', meta: '' },
        { k: 'FARMER CONFIDENCE', v: 'SECTOR-LEVEL ONLY', tone: 'na', meta: 'ICF Agriculture −1.4, Q1 2025' }
      ],
      outlook: [{ k: 'EU OUTLOOK', v: 'ROUTE MAPPED', tone: 'na', meta: 'EC fruit and vegetable dashboard' }],
      outlookNote: '',
      price: null,
      regional: { state: 'ROUTE MAPPED', note: 'ISMEA weekly apple prices by piazza; Trentino-Alto Adige and the producer organisations are the reference for the Italian crop.', source: 'ISMEA Mercati · ortofrutta' },
      production: [{ k: 'Production', v: 'NOT INGESTED', d: '', period: '—', src: 'ISTAT route mapped', geo: 'Italy' }],
      trade: NA,
      confidence: CONFIDENCE_IT,
      weather: { state: 'ROUTE MAPPED', note: '—', src: '—' },
      commentary: { text: 'Apple has an active Opportunity Radar case and a well-mapped price route. It is the strongest candidate for the next crop to be connected.', src: 'Sintonia' },
      changed: [],
      gaps: ['Weekly price by piazza', 'Production and stocks', 'Export flows']
    }
  ];

  // ---------- crop protection industry layer ----------
  const CP_MARKET = {
    intro: 'This layer describes the Italian crop-protection INDUSTRY. It does not describe ADAMA. It cannot produce market share, product-level demand, regional sales or dealer inventory.',
    metrics: [
      { k: 'Sector turnover', v: '≈ €1 billion', period: '2025', src: 'Agrofarma–Federchimica', geo: 'Italy', note: 'the 30 Agrofarma member companies represent ~95% of Italian sector turnover' },
      { k: 'Market movement', v: '+2% value · +1% volume', period: 'end 2025 vs 2024', src: 'Federchimica, L\'evoluzione dei settori chimici, March 2026', geo: 'Italy', note: 'growth reported as spread across all segments' },
      { k: 'Share of Italian chemical turnover', v: '≈ 1.7%', period: '2025', src: 'Agrofarma–Federchimica', geo: 'Italy', note: '' },
      { k: 'Member companies', v: '30–35', period: '2025–2026', src: 'Agrofarma–Federchimica', geo: 'Italy', note: 'company count is stated differently in different Agrofarma publications; both figures are shown rather than picking one' },
      { k: 'R&D investment', v: '> €30 million/yr, ≈3% of turnover', period: 'annual', src: 'Agrofarma–Federchimica', geo: 'Italy', note: 'about one third directed to natural-origin products; twice the ISTAT industrial average of ~1.5%' },
      { k: 'Employment', v: '≈ 2,000', period: 'current', src: 'Agrofarma–Federchimica', geo: 'Italy', note: '~12% engaged in R&D; collaboration with 300+ Italian research institutes' },
      { k: 'European ranking', v: '3rd largest market in Europe', period: 'structural', src: 'Federchimica', geo: 'Italy', note: 'behind France and Spain' },
      { k: 'Volume trend', v: 'DECLINING SINCE 2011', period: '2011 →', src: 'Agrofarma–Federchimica', geo: 'Italy', note: 'near-continuous reduction in volume sold; value and volume have decoupled' },
      { k: 'Illegal product market', v: '≈ 10% of the legal market', period: 'estimate', src: 'Agrofarma / CropLife Europe', geo: 'Europe', note: 'thefts, counterfeits and illegal parallel imports' }
    ],
    caution: [
      'Sector turnover is not ADAMA revenue.',
      'A +2% sector value movement says nothing about any single company, product or region.',
      'Volume decline is a long-run structural trend, not a demand forecast.',
      'None of this supports a statement about distributor orders, dealer inventory or share.'
    ]
  };

  const INTERNAL = [
    { k: 'SELL-IN', why: 'would turn market conditions into an actual demand read' },
    { k: 'SELL-OUT', why: 'would show whether market pressure reaches the grower purchase' },
    { k: 'CRM / PIPELINE', why: 'would connect market timing to real commercial conversations' },
    { k: 'ORDERS', why: 'would test whether a supportive market precedes ordering' },
    { k: 'DISTRIBUTOR INVENTORY', why: 'would separate channel stock from grower demand' },
    { k: 'WAREHOUSE STOCK', why: 'would make supply readiness a real answer, not a request' },
    { k: 'PRICE REALIZATION', why: 'would relate crop economics to ADAMA positioning' },
    { k: 'SALES BY REGION', why: 'would let market context be read at the territory a TSR works' }
  ];

  const FEASIBILITY = [
    ['FARM_GATE_PRICE', 'YES', 'ISMEA origin price survey', 'Weekly / monthly', 'Italy + piazza', 'Sale condition differs by product (f.co azienda vs magazzino)'],
    ['WHOLESALE_PRICE', 'YES', 'ISMEA wholesale · BMTI · Chambers of Commerce', 'Weekly', 'Piazza', 'Different stage of the chain from farm gate'],
    ['PRICE MOMENTUM', 'YES', 'derived from the above', 'Follows source cadence', 'As source', 'Only valid within one series'],
    ['REGIONAL_PRICE', 'YES', 'ISMEA prezzi per piazza', 'Weekly', 'Piazza', 'Piazze are not interchangeable; quality classes differ'],
    ['PRODUCTION', 'YES', 'ISTAT · ISMEA', 'Annual / campaign', 'Italy + region', 'Published with a lag'],
    ['YIELD', 'YES', 'ISTAT · ISMEA', 'Annual', 'Italy + region', 'Lag'],
    ['YIELD_FORECAST', 'PARTIAL', 'JRC MARS', 'Monthly in season', 'EU + member state', 'Not a price forecast; national resolution only'],
    ['IMPORT', 'PARTIAL', 'ISMEA BD commercio estero · Eurostat Comext', 'Monthly / cumulative', 'Italy', 'Not ingested in this demo'],
    ['EXPORT', 'PARTIAL', 'ISMEA · ISTAT · Eurostat', 'Monthly / cumulative', 'Italy', 'Not ingested in this demo'],
    ['STOCK', 'PARTIAL', 'ICQRF Frantoio Italia (olive oil) · sector balances', 'Periodic', 'Italy', 'Available for some sectors only'],
    ['SUPPLY_BALANCE', 'PARTIAL', 'ISMEA supply balances · EC balance sheets', 'Periodic / campaign', 'Italy · EU', 'Cadence varies by sector'],
    ['SELF_SUFFICIENCY', 'PARTIAL', 'derived from ISMEA balance', 'Periodic', 'Italy', 'Derivable only where a full balance exists'],
    ['FARMER_CONFIDENCE', 'PARTIAL', 'ISMEA Indice del Clima di Fiducia', 'Quarterly', 'Italy', 'Agriculture-level; NO crop-level breakdown published'],
    ['INPUT_COST', 'PARTIAL', 'ISMEA indice dei costi · Eurostat input price index', 'Quarterly', 'Italy · EU', 'Route mapped, values not ingested'],
    ['FERTILIZER_COST', 'PARTIAL', 'Eurostat apri_pi_in_pm', 'Quarterly', 'Italy · EU', 'Route mapped, values not ingested'],
    ['ENERGY_COST', 'PARTIAL', 'ISMEA weekly input monitoring (diesel every 15 days)', 'Fortnightly', 'Italy', 'Route mapped, values not ingested'],
    ['EU_MARKET_OUTLOOK', 'PARTIAL', 'EC Short-Term Agricultural Outlook · sector dashboards', 'Periodic', 'EU', 'EU level only — never downscale to a region'],
    ['ITALY_SECTOR_OUTLOOK', 'PARTIAL', 'ISMEA sector sheets and Tendenze reports', 'Periodic / annual', 'Italy', 'Publication dates vary widely by sector'],
    ['CROP_PROTECTION_SECTOR_SIZE', 'YES', 'Agrofarma–Federchimica', 'Annual / semi-annual', 'Italy', 'Industry aggregate; ~95% coverage, not 100%'],
    ['ADAMA_PRODUCT_DEMAND', 'NOT_MEASURED', '—', '—', '—', 'No public source can produce this'],
    ['ADAMA_SALES', 'NOT_MEASURED', '—', '—', '—', 'Internal data only'],
    ['DISTRIBUTOR_STOCK', 'NOT_MEASURED', '—', '—', '—', 'Internal / channel data only']
  ];

  const SOURCES = [
    { name: 'ISMEA Mercati', role: 'Origin and wholesale prices by piazza, price and cost indices, supply balances, foreign trade, confidence index, sector sheets', cadence: 'Weekly · monthly · quarterly · annual', geo: 'Italy · piazza' },
    { name: 'CUN Grano Duro', role: 'National orientation prices for durum wheat since the MASAF decree of 16 Jan 2026', cadence: 'Weekly (Monday)', geo: 'Italy, by macro-area and quality class' },
    { name: 'BMTI · Unioncamere', role: 'Chamber of Commerce price elaboration, wine-grape analysis, grain and rice market commentary', cadence: 'Weekly commentary · annual harvest reports', geo: 'Italy · province' },
    { name: 'ISTAT', role: 'Production, area, yield, agricultural economic accounts, business and consumer confidence', cadence: 'Monthly · annual', geo: 'Italy · region' },
    { name: 'Eurostat', role: 'Agricultural output and input price indices, fertilizer and energy inputs, trade', cadence: 'Quarterly', geo: 'EU · member state' },
    { name: 'European Commission · DG AGRI', role: 'Short-Term Outlook, balance sheets, sector dashboards (cereals, wine, olive oil, sugar, fruit & vegetables)', cadence: 'Periodic', geo: 'EU' },
    { name: 'JRC MARS', role: 'Crop condition, yield forecasts, weather-driven production risk', cadence: 'Monthly in season', geo: 'EU · member state' },
    { name: 'ICQRF · Frantoio Italia', role: 'Olive-oil stock declarations', cadence: 'Periodic', geo: 'Italy' },
    { name: 'Agrofarma–Federchimica', role: 'Crop-protection industry structure, turnover, R&D, volume trend', cadence: 'Annual / semi-annual', geo: 'Italy' },
    { name: 'Veneto Agricoltura', role: 'Regional wine-grape price observatory', cadence: 'Annual', geo: 'Veneto · province' }
  ];

  /* Icon paths — thin-stroke line icons, 24×24 viewBox, ADAMA icon language */
  const ICON = {
    price: 'M4 17l5-6 4 4 7-8',
    production: 'M12 21V9m0 12c-4-1-6-4-6-8 3 0 6 2 6 5m0 3c4-1 6-4 6-8-3 0-6 2-6 5',
    trade: 'M3 8h13m-3-3 3 3-3 3M21 16H8m3 3-3-3 3-3',
    cost: 'M15 8a4 4 0 1 0 0 8M4 10h7M4 14h7',
    logistics: 'M3 16V8h11v8M14 11h4l3 3v2h-7M6.5 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3m11 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3',
    weather: 'M7 17a4 4 0 0 1 0-8 5 5 0 0 1 9.6 1.4A3.5 3.5 0 0 1 17 17z',
    stocks: 'M4 8h16v12H4zM4 8l2-4h12l2 4M12 4v16',
    demand: 'M6 6h15l-2 8H8zM8 14 6 4H3m5 17a1 1 0 1 0 0-2 1 1 0 0 0 0 2m9 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2',
    structure: 'M12 3v18M4 8h16M6 8v10M18 8v10',
    gap: 'M12 4v9m0 4v.5M4.5 20h15L12 4z'
  };

  const F = (k, period, state) => ({ k, period, state });

  const EXTRA = {
    maize: {
      fresh: [F('PRICE', 'Sep 2025', 'AGING'), F('PRODUCTION', '2025 campaign', 'AGING'), F('CONFIDENCE', 'Q1 2025', 'HISTORICAL'), F('INPUT · FREIGHT', '3 Aug 2026', 'CURRENT'), F('TRADE', '—', 'NOT INGESTED'), F('EU OUTLOOK', '—', 'NOT INGESTED')],
      forces: [
        { i: 'production', t: 'PRODUCTION', d: '↑', tone: 'up', x: 'The 2025 campaign expanded on all three axes — area, yield and total output.', s: 'ISMEA, 2025 campaign' },
        { i: 'price', t: 'PRICE', d: '↑', tone: 'up', x: 'Producer price gained 6.1% on the year, but measured against a weak September 2024 base.', s: 'ISMEA, Sep 2025' },
        { i: 'logistics', t: 'LOGISTICS', d: '↑', tone: 'down', x: 'Baltic Dry at 2,843, up 4.1% in a week — imported grain lands dearer.', s: 'Baltic Exchange, 3 Aug 2026' },
        { i: 'gap', t: 'DATA GAP', d: '○', tone: 'na', x: 'No 2026 price observation ingested, so the current direction is unconfirmed.', s: 'Sintonia coverage note' }
      ],
      traj: { past: 'WEAKER BASE', pastNote: 'Sep 2024', now: 'MIXED SIGNALS', next: 'UNCERTAIN', nextNote: 'no forward-looking maize source ingested' },
      adamaWhy: 'Market economics create neither a strong tailwind nor a headwind on the ingested record. Production scale is the commercially relevant fact, not the price.'
    },
    durum: {
      fresh: [F('PRICE', '3 Aug 2026', 'CURRENT'), F('PRODUCTION', '2025 campaign', 'AGING'), F('CONFIDENCE', 'Q1 2025', 'HISTORICAL'), F('INPUT · FREIGHT', '3 Aug 2026', 'CURRENT'), F('OUTLOOK STATEMENT', 'Jun 2026', 'RECENT'), F('TRADE VOLUMES', '—', 'NOT INGESTED')],
      forces: [
        { i: 'price', t: 'PRICE', d: '↓', tone: 'down', x: 'National quotations stepped down roughly a fifth from July 2025 to the May 2026 CUN range, then flattened.', s: 'ISMEA / CUN Grano Duro' },
        { i: 'trade', t: 'IMPORT COMPETITION', d: '↑', tone: 'down', x: 'Imported durum is the only rising quotation — Milano and Altamura up €10/t in two weeks.', s: 'ISMEA via AgroNotizie, Aug 2026' },
        { i: 'weather', t: 'NORTH-AMERICAN CROP', d: '↔', tone: 'flat', x: 'Analysts hold that an abundant western-Canada crop would keep markets steady into early autumn.', s: 'market analysis, Jun 2026' },
        { i: 'logistics', t: 'LOGISTICS', d: '↑', tone: 'down', x: 'Baltic Dry at 2,843, up 4.1% on the week, its highest since mid-July.', s: 'Baltic Exchange, 3 Aug 2026' },
        { i: 'structure', t: 'MARKET STRUCTURE', d: '◇', tone: 'na', x: 'The CUN replaced borsa merci quotations in January 2026 — the national reference itself changed mid-year.', s: 'MASAF decree, 16 Jan 2026' }
      ],
      traj: { past: 'FALLING', pastNote: 'Jul 2025 → May 2026', now: 'PRESSURED', next: 'MIXED / UNCERTAIN', nextNote: 'flat is a pause, not a confirmed recovery' },
      adamaWhy: 'Grower economics are pressured while the fungicide windows sit in the next campaign. Value proposition and economic justification deserve stronger emphasis — this is not evidence that growers will reduce protection.'
    },
    soft: {
      fresh: [F('PRICE', 'Dec 2025', 'AGING'), F('PRODUCTION', '2025 campaign', 'AGING'), F('CONFIDENCE', 'Q1 2025', 'HISTORICAL'), F('INPUT · FREIGHT', '3 Aug 2026', 'CURRENT'), F('TRADE', '—', 'NOT INGESTED'), F('EU OUTLOOK', '—', 'NOT INGESTED')],
      forces: [
        { i: 'price', t: 'PRICE', d: '↔', tone: 'flat', x: 'Three monthly observations inside a €245–248/t band across the second half of 2025.', s: 'ISMEA, Jul–Dec 2025' },
        { i: 'production', t: 'PRODUCTION', d: '↓', tone: 'flat', x: 'About 2.5 Mt in 2025, marginally below the previous campaign.', s: 'ISMEA, 2025' },
        { i: 'gap', t: 'DATA GAP', d: '○', tone: 'na', x: 'No 2026 observation ingested — "balanced" describes the last confirmed state, not today.', s: 'Sintonia coverage note' }
      ],
      traj: { past: 'BALANCED', pastNote: 'Jul 2025', now: 'BALANCED', next: 'UNCERTAIN', nextNote: 'no forward-looking soft-wheat source ingested' },
      adamaWhy: 'A flat market gives commercial conversations no price-driven urgency in either direction. Timing arguments must come from the crop window, not the market.'
    },
    olive: {
      fresh: [F('PRICE', '24–30 Aug 2026', 'CURRENT'), F('STOCKS', '30 Nov 2025', 'AGING'), F('IMPORT REFERENCE', 'Jan 2026', 'RECENT'), F('CONFIDENCE', 'Q1 2025', 'HISTORICAL'), F('INPUT · FREIGHT', '3 Aug 2026', 'CURRENT'), F('PRODUCTION 2026/27', '—', 'NOT INGESTED')],
      forces: [
        { i: 'stocks', t: 'STOCKS', d: '↑', tone: 'down', x: 'About 153,000 t of extra virgin at 30 November 2025, a third more than a year earlier.', s: 'ICQRF Frantoio Italia' },
        { i: 'trade', t: 'IMPORT PRESSURE', d: '↑', tone: 'down', x: 'Spanish extra virgin at €4.25–4.26/kg is a landed alternative below the Italian quality price.', s: 'ISMEA international, Jan 2026' },
        { i: 'cost', t: 'COST OF PRODUCTION', d: '↑', tone: 'down', x: 'Sector reconstructions put quality extra virgin at €8.87–10.31/kg to produce, against a €4.55/kg Bari quotation.', s: 'industry cost estimate, 2026' },
        { i: 'price', t: 'PRICE', d: '↔', tone: 'flat', x: 'Bari unchanged and Trapani −2.8% in the latest survey week: flat, at a level producers call insufficient.', s: 'ISMEA, 24–30 Aug 2026' },
        { i: 'structure', t: 'SEGMENTATION', d: '◇', tone: 'na', x: 'Denominations defend value where volume cannot — IGP Toscano at €12.00/kg against €4.55/kg generic.', s: 'ISMEA, Aug 2026' }
      ],
      traj: { past: 'COLLAPSING', pastNote: 'autumn 2025', now: 'PRESSURED', next: 'MIXED / UNCERTAIN', nextNote: 'stabilisation of the list price is not recovery in the chain' },
      adamaWhy: 'Fruit-fly windows are open in the southern districts while grower economics are at their weakest. Programme cost and justification will be scrutinised harder than in a normal year.'
    },
    wine: {
      fresh: [F('GRAPE PRICES', 'vendemmia 2025', 'RECENT'), F('PRODUCTION', '2025', 'AGING'), F('ASSET VALUES', '28 Feb 2026', 'RECENT'), F('CONFIDENCE', 'Q1 2025', 'HISTORICAL'), F('2026 HARVEST', '—', 'NOT INGESTED'), F('EXPORT VOLUMES', '—', 'NOT INGESTED')],
      forces: [
        { i: 'price', t: 'GRAPE PRICE', d: '↓', tone: 'down', x: 'Widespread annual declines, several double-digit, for a third consecutive year on many denominations.', s: 'Unioncamere / BMTI, May 2026' },
        { i: 'demand', t: 'COMMERCIAL OUTLETS', d: '↓', tone: 'down', x: 'Lower domestic consumption and reduced export are cited as producing a surplus, particularly in reds.', s: 'trade-association statements' },
        { i: 'production', t: 'VOLUME', d: '↔', tone: 'flat', x: 'Wine output ~44 M hl (+1%) and grapes ~66 M quintals (−0.4%) — volume barely moved.', s: 'OIV / ISTAT via BMTI' },
        { i: 'structure', t: 'ESTIMATE ANCHORING', d: '◇', tone: 'na', x: 'Early-vendemmia estimates of +8% anchored negotiation before final figures came in far lower. A forecast moved the market, not a harvest.', s: 'BMTI / CIA, 2025' },
        { i: 'trade', t: 'TARIFFS', d: '↓', tone: 'down', x: 'US tariffs are reported as a pressure on the Veneto chain. Reported context, not measured trade data.', s: 'regional sector reporting' }
      ],
      traj: { past: 'FALLING', pastNote: 'third year', now: 'PRESSURED', next: 'REBALANCING · UNCERTAIN', nextNote: 'described as progressive rebalancing after the 2022 peak' },
      adamaWhy: 'Vineyard economics are weak in most denominations but not all — Primitivo and Bolgheri moved the other way. Regional argument beats a national one on this crop.'
    },
    tomato: { fresh: [F('ALL COMPONENTS', '—', 'NOT INGESTED')], forces: [], traj: { past: '—', pastNote: '', now: 'NOT ENOUGH DATA', next: '—', nextNote: 'no market layer for this crop' }, adamaWhy: 'No market layer. The agronomic case stands on its own evidence and is not weakened by the absence.' },
    sugarbeet: { fresh: [F('ALL COMPONENTS', '—', 'NOT INGESTED')], forces: [], traj: { past: '—', pastNote: '', now: 'NOT ENOUGH DATA', next: '—', nextNote: 'contract-priced crop; no representative spot quotation' }, adamaWhy: 'Beet value is set by contract with the processing industry, so a price-first market layer would misrepresent it.' },
    apple: { fresh: [F('ALL COMPONENTS', '—', 'NOT INGESTED')], forces: [], traj: { past: '—', pastNote: '', now: 'NOT ENOUGH DATA', next: '—', nextNote: 'routes mapped, values not connected' }, adamaWhy: 'Best-mapped of the unconnected crops — the strongest candidate for the next ingestion.' }
  };

  const SEM = {
    POSITIVE: { key: 'POSITIVE', color: '#00B152', line: '#009845', tint: 'rgba(0,152,69,0.10)', border: 'rgba(0,152,69,0.42)', mark: '\u25cf', label: 'POSITIVE' },
    NEGATIVE: { key: 'NEGATIVE', color: '#F89E18', line: '#F89E18', tint: 'rgba(248,158,24,0.10)', border: 'rgba(248,158,24,0.42)', mark: '\u25bc', label: 'NEGATIVE' },
    NEUTRAL: { key: 'NEUTRAL', color: '#F5B317', line: '#F5B317', tint: 'rgba(245,179,23,0.055)', border: 'rgba(245,179,23,0.38)', mark: '\u25cb', label: 'WATCH' },
    UNKNOWN: { key: 'UNKNOWN', color: '#B1A9A7', line: '#978B87', tint: 'transparent', border: 'rgba(151,139,135,0.28)', mark: '\u2014', label: 'NO DATA' }
  };
  const TONE_SEM = { up: 'POSITIVE', down: 'NEGATIVE', flat: 'NEUTRAL', na: 'UNKNOWN' };
  const TEMP_SEM = { 'SUPPORTIVE': 'POSITIVE', 'TIGHTENING': 'NEUTRAL', 'BALANCED': 'NEUTRAL', 'MIXED SIGNALS': 'NEUTRAL', 'PRESSURED': 'NEGATIVE', 'COOLING': 'NEGATIVE', 'VOLATILE': 'NEUTRAL' };

  const FRESH_COLOR = { 'CURRENT': '#00B152', 'RECENT': '#7DB41E', 'AGING': '#F89E18', 'HISTORICAL': '#978B87', 'NOT INGESTED': '#8F8886' };

  window.ITALY_MARKET = { TEMP, CROPS, CP_MARKET, INTERNAL, FEASIBILITY, SOURCES, CONTEXT_IT, INPUT_ROUTES, ICON, EXTRA, FRESH_COLOR, SEM, TONE_SEM, TEMP_SEM, LAST_REVIEW: '1 September 2026' };
})();
