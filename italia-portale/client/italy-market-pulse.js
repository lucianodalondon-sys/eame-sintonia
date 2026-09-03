/* Sintonia · MARKET — PRESENTATION VOCABULARY ONLY. No facts live in this file.
   ---------------------------------------------------------------------------------------
   WHAT THIS FILE USED TO BE, AND WHY IT WAS EMPTIED (measured 2026-09-02)

   window.ITALY_MARKET was never ingested data. It was a hand-authored editorial fixture:
   8 crop objects with no record id, no SOURCE_ID and no PROVENANCE on any of them. It
   attributed numbers to ISMEA, CUN Grano Duro, BMTI/Unioncamere, ICQRF, Agrofarma-
   Federchimica, Baltic Exchange, JRC MARS and Veneto Agricoltura — NONE of which appear
   among the 31 registered sources in ITALY_INGEST.SOURCES. 20 of its 23 chart values do
   not exist anywhere in the real market data. It rendered a market-temperature verdict,
   a Sintonia "reading", drivers, a PAST/TODAY/OUTLOOK trajectory, ISMEA farmer confidence
   (-1.4), a Baltic Dry Index value of 2,843 explicitly flagged state:'OBSERVED', and
   production / stocks / trade / industry figures. Under product law a fixture may never
   supply a fact, so every one of those was deleted rather than repaired — there are no
   real numbers behind them to repair them with.

   THE REAL BACKING, MEASURED against APP.collections.marketObservations:
     77 raw rows in ITALY_INGEST, all from ONE registered source (IT-SRC-AGRIFOOD,
        European Commission Agri-food Data Portal weekly prices). 76 accepted;
        IT-MKT-077 rejected for having no product.
     Per crop tab:  Wheat 13 · Maize 11 · Durum Wheat 8 · Olive 36
                    Grapevine 0 usable (its single row is the rejected one)
                    Tomato 0 · Sugar Beet 0 · Apple 0
     Quality:  12 of 77 rows sit on series that STOPPED quoting (the last quote is not a
               current price) · STAGE missing on 37 of 77 · no publication date on
               37 of 77. All of the missing STAGE / PUBLICATION_DATE rows are olive oil.
     Also ingested but with no crop tab to show it: Barley, 8 rows.

   WHAT SURVIVES HERE: crop keys, display labels, colours, icon paths, freshness and
   semantic colour maps, the capability table of what public sources CAN and CANNOT yield,
   and a coverage-gap list regenerated from the measurement above. Every number in this
   file is a count of our own data coverage, never a market fact.

   ONE CLOCK: there is no LAST_REVIEW here. The screen reads AM.referenceDate.

   The object is deliberately left in place, and window.ITALY_MARKET is deliberately not
   renamed, because portale.html reads it in 17 places and that migration is owned by
   another agent. A present-but-fact-free shape is what lets that migration land. */
(function () {

  /* ---------------------------------------------------------------------------
     CROPS — tab strip vocabulary only. key, label, it, crop, color. Nothing else.
     No temperature, no reading, no drivers, no prices, no verdict of any kind.
     --------------------------------------------------------------------------- */
  const CROPS = [
    { key: 'maize',     label: 'Maize',            it: 'Mais',                       crop: 'Maize',      color: '#F89E18' },
    { key: 'durum',     label: 'Durum Wheat',      it: 'Frumento duro',              crop: 'Durum Wheat', color: '#00A0DF' },
    { key: 'soft',      label: 'Soft Wheat',       it: 'Frumento tenero',            crop: 'Wheat',      color: '#7DB41E' },
    { key: 'olive',     label: 'Olive / Olive Oil', it: 'Olivo / Olio d\'oliva',     crop: 'Olive',      color: '#009845' },
    { key: 'wine',      label: 'Grapevine / Wine', it: 'Vite / Vino',                crop: 'Grapevine',  color: '#9D1D96' },
    { key: 'tomato',    label: 'Tomato',           it: 'Pomodoro',                   crop: 'Tomato',     color: '#F89E18' },
    { key: 'sugarbeet', label: 'Sugar Beet',       it: 'Barbabietola da zucchero',   crop: 'Sugar Beet', color: '#00A0DF' },
    { key: 'apple',     label: 'Apple',            it: 'Melo',                       crop: 'Apple',      color: '#7DB41E' }
  ];

  /* ---------------------------------------------------------------------------
     COVERAGE — counts of OUR OWN data, measured, not market facts.
     --------------------------------------------------------------------------- */
  const COVERAGE = {
    measuredOn: 'APP.collections.marketObservations',
    rowsRaw: 77,
    rowsAccepted: 76,
    rowsRejected: 1,
    rejectedWhy: 'IT-MKT-077 (Grapevine) carries no product and is not loaded',
    sourceCount: 1,
    sourceId: 'IT-SRC-AGRIFOOD',
    sourceName: 'European Commission · Agri-food Data Portal, weekly prices',
    byCropTab: [
      { key: 'soft', rows: 13 }, { key: 'maize', rows: 11 }, { key: 'durum', rows: 8 },
      { key: 'olive', rows: 36 }, { key: 'wine', rows: 0 }, { key: 'tomato', rows: 0 },
      { key: 'sugarbeet', rows: 0 }, { key: 'apple', rows: 0 }
    ],
    ingestedWithNoCropTab: [{ name: 'Barley', rows: 8 }],
    stoppedSeries: { n: 12, of: 77 },
    missingStage: { n: 37, of: 77 },
    missingPublicationDate: { n: 37, of: 77 }
  };

  /* ---------------------------------------------------------------------------
     GAPS — regenerated from the measurement above, per crop tab.
     These describe what we do NOT have. They assert nothing about any market.
     --------------------------------------------------------------------------- */
  const GAPS = {
    maize: [
      '11 weekly price rows ingested, all from one source; STAGE and PUBLICATION_DATE complete on all 11',
      'No production, area or yield observation',
      'No import, export, stock or supply-balance observation',
      'No input-cost, fertilizer, energy or freight observation',
      'No forward-looking or outlook source ingested'
    ],
    durum: [
      '8 weekly price rows ingested, all from one source',
      '1 of the 8 sits on a series that stopped quoting — its last quote is not a current price',
      'No production, area or yield observation',
      'No import, export, stock or supply-balance observation',
      'No forward-looking or outlook source ingested'
    ],
    soft: [
      '13 weekly price rows ingested, the widest coverage of any crop tab; all on current series',
      'No production, area or yield observation',
      'No import, export, stock or supply-balance observation',
      'No forward-looking or outlook source ingested'
    ],
    olive: [
      '36 price rows across 6 different oil grades — the grades are not comparable and must never be averaged into one price',
      '10 of the 36 sit on series that stopped quoting — those last quotes are not current prices',
      'STAGE missing on all 36 rows: the point in the chain each price refers to is unknown',
      'no publication date on all 36 rows: only the reference period is known',
      'No production, stock, trade or supply-balance observation'
    ],
    wine: [
      'Zero usable observations. The single ingested grapevine row (IT-MKT-077) was rejected for carrying no product',
      'That row also sat on a series that stopped quoting in 2025, so even loaded it would not be a current price',
      'No production, trade or stock observation'
    ],
    tomato: [
      'Zero market observations ingested for this crop',
      'Processing tomato is priced through inter-branch agreements rather than an open quotation, so a price-first market layer fits it badly',
      'No production, area, trade or price observation'
    ],
    sugarbeet: [
      'Zero market observations ingested for this crop',
      'Beet is contracted with the processing industry; there is no representative Italian spot quotation',
      'No production, area, trade or price observation'
    ],
    apple: [
      'Zero market observations ingested for this crop',
      'No production, stock, trade or price observation'
    ]
  };

  /* ---------------------------------------------------------------------------
     NOT_OBSERVABLE — replaces the former INTERNAL[] list.
     That list named eight private ADAMA systems and argued what Sintonia could do
     with each. It presented ADAMA's private data as a missing piece of Sintonia,
     which product law forbids. One honest statement replaces all eight.
     Keyed to the existing i18n entry `cannotProveList`; the it/en pair below is a
     fallback so this file never depends on an edit to italy-i18n.js.
     --------------------------------------------------------------------------- */
  const NOT_OBSERVABLE = {
    i18nKey: 'cannotProveList',
    it: 'Il comportamento d\'acquisto del canale non è osservabile da fonti pubbliche. Sintonia lavora soltanto su ciò che il mondo esterno rende visibile: prezzi pubblici, statistiche pubblicate, documenti ufficiali e comunicazione pubblica.',
    en: 'The purchasing behaviour of the channel is not observable from public sources. Sintonia works only on what the external world makes visible: public prices, published statistics, official documents and public communication.'
  };

  /* ---------------------------------------------------------------------------
     CP_MARKET — the crop-protection industry layer. Its `metrics` array is gone:
     nine figures (turnover, +2% value / +1% volume, R&D spend, employment, European
     ranking, illegal-market share) attributed to Agrofarma-Federchimica, which is
     not a registered source and has no record behind it.
     --------------------------------------------------------------------------- */
  const CP_MARKET = {
    intro: 'This layer describes the Italian crop-protection INDUSTRY. It does not describe ADAMA. It cannot produce market share, product-level demand, regional sales or dealer inventory.',
    caution: [
      'No industry figure is ingested; none is displayed.',
      'A sector-level movement would say nothing about any single company, product or region.',
      'Nothing observable from public sources supports a statement about channel purchasing.'
    ]
  };

  /* ---------------------------------------------------------------------------
     FEASIBILITY — what public sources CAN and CANNOT yield. A capability table,
     not a data table: it contains no values, no dates and no verdicts about any
     market. NOT_MEASURED rows are the honest form of
     "NON OSSERVABILE DA FONTI ESTERNE".
     --------------------------------------------------------------------------- */
  const FEASIBILITY = [
    ['FARM_GATE_PRICE', 'YES', 'ISMEA origin price survey', 'Weekly / monthly', 'Italy + piazza', 'Sale condition differs by product (f.co azienda vs magazzino)'],
    ['WHOLESALE_PRICE', 'YES', 'ISMEA wholesale · BMTI · Chambers of Commerce', 'Weekly', 'Piazza', 'Different stage of the chain from farm gate'],
    ['PRICE MOMENTUM', 'YES', 'derived from the above', 'Follows source cadence', 'As source', 'Only valid within one series'],
    ['REGIONAL_PRICE', 'YES', 'ISMEA prezzi per piazza', 'Weekly', 'Piazza', 'Piazze are not interchangeable; quality classes differ'],
    ['PRODUCTION', 'YES', 'ISTAT · ISMEA', 'Annual / campaign', 'Italy + region', 'Published with a lag'],
    ['YIELD', 'YES', 'ISTAT · ISMEA', 'Annual', 'Italy + region', 'Lag'],
    ['YIELD_FORECAST', 'PARTIAL', 'JRC MARS', 'Monthly in season', 'EU + member state', 'Not a price forecast; national resolution only'],
    ['IMPORT', 'PARTIAL', 'ISMEA BD commercio estero · Eurostat Comext', 'Monthly / cumulative', 'Italy', 'Route only — nothing ingested'],
    ['EXPORT', 'PARTIAL', 'ISMEA · ISTAT · Eurostat', 'Monthly / cumulative', 'Italy', 'Route only — nothing ingested'],
    ['STOCK', 'PARTIAL', 'ICQRF Frantoio Italia (olive oil) · sector balances', 'Periodic', 'Italy', 'Route only — nothing ingested'],
    ['SUPPLY_BALANCE', 'PARTIAL', 'ISMEA supply balances · EC balance sheets', 'Periodic / campaign', 'Italy · EU', 'Route only — nothing ingested'],
    ['SELF_SUFFICIENCY', 'PARTIAL', 'derived from ISMEA balance', 'Periodic', 'Italy', 'Derivable only where a full balance exists'],
    ['FARMER_CONFIDENCE', 'PARTIAL', 'ISMEA Indice del Clima di Fiducia', 'Quarterly', 'Italy', 'Agriculture-level; NO crop-level breakdown published; nothing ingested'],
    ['INPUT_COST', 'PARTIAL', 'ISMEA indice dei costi · Eurostat input price index', 'Quarterly', 'Italy · EU', 'Route only — nothing ingested'],
    ['FERTILIZER_COST', 'PARTIAL', 'Eurostat apri_pi_in_pm', 'Quarterly', 'Italy · EU', 'Route only — nothing ingested'],
    ['ENERGY_COST', 'PARTIAL', 'ISMEA weekly input monitoring (diesel every 15 days)', 'Fortnightly', 'Italy', 'Route only — nothing ingested'],
    ['EU_MARKET_OUTLOOK', 'PARTIAL', 'EC Short-Term Agricultural Outlook · sector dashboards', 'Periodic', 'EU', 'EU level only — never downscale to a region'],
    ['ITALY_SECTOR_OUTLOOK', 'PARTIAL', 'ISMEA sector sheets and Tendenze reports', 'Periodic / annual', 'Italy', 'Publication dates vary widely by sector'],
    ['CROP_PROTECTION_SECTOR_SIZE', 'PARTIAL', 'Agrofarma–Federchimica', 'Annual / semi-annual', 'Italy', 'Industry aggregate; not a registered source here and nothing ingested'],
    ['ADAMA_PRODUCT_DEMAND', 'NOT_MEASURED', '—', '—', '—', 'No public source can produce this'],
    ['ADAMA_SALES', 'NOT_MEASURED', '—', '—', '—', 'Not observable from external sources'],
    ['DISTRIBUTOR_STOCK', 'NOT_MEASURED', '—', '—', '—', 'Not observable from external sources']
  ];

  /* Icon paths — thin-stroke line icons, 24×24 viewBox, ADAMA icon language. */
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

  /* Colour semantics. Vocabulary only — nothing here decides what state anything is in. */
  const SEM = {
    POSITIVE: { key: 'POSITIVE', color: '#00B152', line: '#009845', tint: 'rgba(0,152,69,0.10)', border: 'rgba(0,152,69,0.42)', mark: '●', label: 'POSITIVE' },
    NEGATIVE: { key: 'NEGATIVE', color: '#F89E18', line: '#F89E18', tint: 'rgba(248,158,24,0.10)', border: 'rgba(248,158,24,0.42)', mark: '▼', label: 'NEGATIVE' },
    NEUTRAL: { key: 'NEUTRAL', color: '#F5B317', line: '#F5B317', tint: 'rgba(245,179,23,0.055)', border: 'rgba(245,179,23,0.38)', mark: '○', label: 'WATCH' },
    UNKNOWN: { key: 'UNKNOWN', color: '#B1A9A7', line: '#978B87', tint: 'transparent', border: 'rgba(151,139,135,0.28)', mark: '—', label: 'NO DATA' }
  };
  const TONE_SEM = { up: 'POSITIVE', down: 'NEGATIVE', flat: 'NEUTRAL', na: 'UNKNOWN' };

  /* Freshness colours. The STATE is supplied by whatever renders a dated record —
     this map only says which colour each state wears. */
  const FRESH_COLOR = { 'CURRENT': '#00B152', 'RECENT': '#7DB41E', 'AGING': '#F89E18', 'HISTORICAL': '#978B87', 'NOT INGESTED': '#8F8886' };

  /* TEMP and TEMP_SEM are deliberately absent: they existed only to colour the
     market-temperature verdicts (SUPPORTIVE / PRESSURED / MIXED SIGNALS …) that
     this file is no longer allowed to assert.
     SOURCES[] is deliberately absent: it listed ten organisations as if they fed
     this package. One source feeds it, IT-SRC-AGRIFOOD, and it is registered in
     ITALY_INGEST.SOURCES where it belongs. */
  window.ITALY_MARKET = { CROPS, GAPS, COVERAGE, NOT_OBSERVABLE, CP_MARKET, FEASIBILITY, ICON, SEM, TONE_SEM, FRESH_COLOR };
})();
