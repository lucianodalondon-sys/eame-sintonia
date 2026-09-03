/* Sintonia · Italy demonstration dataset (local fixtures, no backend). Internal provenance in ITALY-DEMO-PROVENANCE-MATRIX.md */
(function () {
  const REAL = window.ITALY_REAL || { RESEARCHERS: [], SCIENCE: [], NEWS: [], BULLETINS: [], COMPETITOR_REAL: [], EVENT_EXTRA: {}, EVENTS_EXTRA: [], SOURCES_EXTRA: [], MEDIA_RECLASS: {}, REALITY: [] };
  /* §19 · One reference date, from the canonical intelligence contract. */
  const REF_ISO = (window.ITALY_CANONICAL && ((window.ITALY_CANONICAL.meta && window.ITALY_CANONICAL.meta.referenceDate) || window.ITALY_CANONICAL.referenceDate)) || '2026-09-02';
  const TODAY = new Date(REF_ISO + 'T00:00:00');
  const seed = (n) => { let x = Math.sin(n * 9301 + 49297) * 233280; return x - Math.floor(x); };
  const pick = (arr, n) => arr[Math.floor(seed(n) * arr.length) % arr.length];
  const MON_EN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const MON_IT = ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'];
  /* The interface language is read at load time, before any date string is built, so dates
     baked into the demo arrays follow the language too. setMonths() handles later switches. */
  const startLang = (() => { try { return localStorage.getItem('sintonia_lang') === 'en' ? 'en' : 'it'; } catch (e) { return 'it'; } })();
  const MON = (startLang === 'en' ? MON_EN : MON_IT).slice();
  const setMonths = (arr) => { if (Array.isArray(arr) && arr.length === 12) arr.forEach((v, i) => { MON[i] = v.charAt(0) + v.slice(1).toLowerCase(); }); };
  /* Null-safe: a window without a defensible calendar range has no date string.
     The UI must render DATE_TO_CONFIRM, never a fabricated date. */
  const fmt = (d) => d ? (String(d.getDate()).padStart(2, '0') + ' ' + MON[d.getMonth()]) : null;
  const addDays = (d, n) => new Date(d.getTime() + n * 864e5);
  const ago = (n) => n === 0 ? 'today' : n === 1 ? '1d ago' : n < 30 ? n + 'd ago' : Math.round(n / 30) + 'mo ago';

  const CAT = {
    pest: { key: 'pest', label: 'Pest Control', color: '#9D1D96', dark: '#FFFFFF', surface: '#FFFFFF', soft: '#752157', ink: '#fff', body: '#5F504D', muted: '#978B87', icon: 'assets/icons/pest-control-white.png',  aShape: 'assets/a-pest-2.png' },
    disease: { key: 'disease', label: 'Disease Control', color: '#00A0DF', dark: '#FFFFFF', surface: '#FFFFFF', soft: '#00698F', ink: '#fff', body: '#5F504D', muted: '#978B87', icon: 'assets/icons/disease-control-white.png',  aShape: 'assets/a-disease-2.png' },
    weed: { key: 'weed', label: 'Weed Control', color: '#7DB41E', dark: '#FFFFFF', surface: '#FFFFFF', soft: '#00698F', ink: '#5F504D', body: '#5F504D', muted: '#978B87', icon: 'assets/icons/weed-control-white.png',  aShape: '' }
  };
  /* One ink rule for every brand fill: dark ink on light fills, white only on the dark ones.
     Text colour must be derived from the surface, never authored per call-site. */
  const INK = { '#F89E18': '#5F504D', '#00A0DF': '#FFFFFF', '#978B87': '#FFFFFF', '#7DB41E': '#5F504D', '#F5B317': '#5F504D', '#93CC23': '#5F504D', '#CBC5C3': '#5F504D', '#E5E1E0': '#5F504D', '#F4F2F2': '#5F504D', '#fff': '#5F504D', '#FFFFFF': '#5F504D',
    '#009845': '#fff', '#00783F': '#fff', '#752157': '#fff', '#9D1D96': '#fff', '#00698F': '#fff', '#5F504D': '#fff' };
  const inkOn = (fill) => INK[String(fill || '').trim()] || '#5F504D';

  const STATUS = {
    'ACT NOW': { color: '#00783F', text: '#00783F', rank: 0 },
    'ACTION WINDOW OPENING': { color: '#00783F', text: '#00783F', rank: 1 },
    'PREPARE': { color: '#00783F', text: '#00783F', rank: 2 },
    'WATCH': { color: '#978B87', text: '#978B87', rank: 3 },
    'VALIDATE': { color: '#978B87', text: '#978B87', rank: 4 },
    'NEXT CYCLE': { color: '#CBC5C3', text: '#978B87', rank: 5 },
    /* Canonical codes from the intelligence contract. ACT_NOW is absent on purpose:
       the presentation layer must never derive it. */
    'WINDOW_OPEN': { color: '#00783F', text: '#00783F', rank: 1 },
    'WINDOW_CLOSED': { color: '#CBC5C3', text: '#978B87', rank: 6 },
    'NEXT_CYCLE': { color: '#CBC5C3', text: '#978B87', rank: 5 },
    'DATE_UNKNOWN': { color: '#978B87', text: '#978B87', rank: 4 },
    'ACT_NOW': { color: '#00783F', text: '#00783F', rank: 0 }
  };
  const DEPT = {
    'MARKET DEVELOPMENT': { color: '#978B87', soft: '#978B87' },
    'SALES / RTV': { color: '#978B87', soft: '#978B87' },
    'MARKETING': { color: '#978B87', soft: '#978B87' },
    'TECHNICAL / SCIENCE': { color: '#978B87', soft: '#978B87' },
    'REGULATORY / PORTFOLIO': { color: '#978B87', soft: '#978B87' },
    'SUPPLY': { color: '#978B87', soft: '#978B87' }
  };

  const REGIONS = [
    ['Valle d\'Aosta', 0, 0], ['Trentino-Alto Adige', 2, 0], ['Friuli-Venezia Giulia', 3, 0],
    ['Piemonte', 0, 1], ['Lombardia', 1, 1], ['Veneto', 2, 1],
    ['Liguria', 0, 2], ['Emilia-Romagna', 1, 2],
    ['Toscana', 1, 3], ['Marche', 2, 3],
    ['Umbria', 1, 4], ['Abruzzo', 2, 4],
    ['Lazio', 1, 5], ['Molise', 2, 5], ['Sardegna', 0, 5],
    ['Campania', 2, 6], ['Puglia', 3, 6],
    ['Basilicata', 2, 7], ['Calabria', 2, 8], ['Sicilia', 1, 9]
  ].map(r => ({ name: r[0], col: r[1], row: r[2] }));

  // ADAMA Italy portfolio — names restricted to the Italy evidence pack. AI shown only where confirmed.
  const PRODUCTS = {
    'SULCOTREK': { ai: 'Terbuthylazine + sulcotrione', cat: 'weed', crops: ['Maize'], targets: ['Broadleaf weeds', 'Annual grasses'], use: 'Post-emergence · crop 2–6 leaves', moa: 'HRAC 5 (C1) + 27 (F2)' },
    'PYXIDES WG': { ai: 'Dicamba + nicosulfuron + mesotrione', cat: 'weed', crops: ['Maize'], targets: ['Sorghum halepense', 'Broadleaf weeds'], use: 'Post-emergence', moa: 'HRAC 2 (B) + 4 (O) + 27 (F2)' },
    'NICOGAN V.O.': { ai: 'Nicosulfuron', cat: 'weed', crops: ['Maize'], targets: ['Sorghum halepense', 'Echinochloa', 'Setaria'], use: 'Post-emergence', moa: 'HRAC 2 (B)' },
    'ACTIVUS 40 SC': { ai: 'Pendimethalin', cat: 'weed', crops: ['Maize', 'Soybean', 'Grapevine'], targets: ['Annual grasses', 'Broadleaf weeds'], use: 'Pre-emergence', moa: 'HRAC 3 (K1)' },
    'TOPIK 80 EC': { ai: 'Clodinafop + cloquintocet-mexyl', cat: 'weed', crops: ['Durum Wheat', 'Wheat'], targets: ['Lolium', 'Avena', 'Phalaris', 'Alopecurus'], use: 'Post-emergence · tillering', moa: 'HRAC 1 (A)' },
    'CELIO 80 EC': { ai: 'Clodinafop + cloquintocet-mexyl', cat: 'weed', crops: ['Durum Wheat', 'Wheat'], targets: ['Lolium', 'Avena', 'Phalaris'], use: 'Post-emergence', moa: 'HRAC 1 (A)' },
    'EDAPTIS': { ai: 'Mesosulfuron-methyl + pinoxaden + mefenpyr-diethyl', cat: 'weed', crops: ['Durum Wheat', 'Wheat'], targets: ['Lolium', 'Alopecurus', 'Avena', 'Broadleaf weeds'], use: 'Post-emergence · tillering', moa: 'HRAC 1 + 2' },
    'DICURAN PLUS': { ai: 'Chlorotoluron + diflufenican', cat: 'weed', crops: ['Durum Wheat', 'Wheat'], targets: ['Papaver rhoeas', 'Stellaria media', 'Annual grasses'], use: 'Pre- or early post-emergence', moa: 'HRAC 5 + 12' },
    'GOLTIX': { ai: 'Metamitron', cat: 'weed', crops: ['Sugar Beet'], targets: ['Chenopodium album', 'Amaranthus retroflexus', 'Polygonum'], use: 'Pre- and post-emergence programme', moa: 'HRAC 5 (C1)' },
    'CONTATTO 320': { ai: 'Phenmedipham', cat: 'weed', crops: ['Sugar Beet'], targets: ['Chenopodium album', 'Amaranthus retroflexus', 'Stellaria media'], use: 'Post-emergence · repeated low dose', moa: 'HRAC 5 (C1)' },
    'LEOPARD 5 EC': { ai: 'Quizalofop-P-ethyl', cat: 'weed', crops: ['Sugar Beet', 'Soybean'], targets: ['Sorghum halepense', 'Echinochloa', 'Setaria'], use: 'Post-emergence graminicide', moa: 'HRAC 1 (A)' },
    'AGIL': { ai: 'Propaquizafop', cat: 'weed', crops: ['Soybean'], targets: ['Sorghum halepense', 'Annual grasses'], use: 'Post-emergence graminicide', moa: 'HRAC 1 (A)' },
    'DAVAI': { ai: 'Imazamox', cat: 'weed', crops: ['Soybean', 'Rice'], targets: ['Amaranthus', 'Echinochloa', 'Broadleaf weeds'], use: 'Post-emergence', moa: 'HRAC 2 (B)' },
    'EARLEX': { ai: 'Imazamox', cat: 'weed', crops: ['Soybean', 'Rice'], targets: ['Amaranthus', 'Echinochloa'], use: 'Post-emergence', moa: 'HRAC 2 (B)' },
    'GLIPHOGAN TOP CL': { ai: 'Glyphosate', cat: 'weed', crops: ['Grapevine', 'Olive'], targets: ['Sorghum halepense', 'Conyza', 'Perennial weeds'], use: 'Inter-row directed application', moa: 'HRAC 9 (G)' },
    'EVURE PRO': { ai: 'Tau-fluvalinate', cat: 'pest', crops: ['Grapevine'], targets: ['Scaphoideus titanus', 'Grapevine leafhoppers'], use: 'Foliar · adults and nymphs', moa: 'IRAC 3A' },
    'MAVRIK SMART': { ai: 'Tau-fluvalinate', cat: 'pest', crops: ['Grapevine', 'Olive', 'Wheat'], targets: ['Scaphoideus titanus', 'Aphids', 'Olive fruit fly'], use: 'Foliar', moa: 'IRAC 3A' },
    'MAVRIK EW': { ai: 'Tau-fluvalinate', cat: 'pest', crops: ['Wheat', 'Durum Wheat', 'Grapevine'], targets: ['Cereal aphids', 'Scaphoideus titanus'], use: 'Foliar', moa: 'IRAC 3A' },
    'KLARTAN SMART': { ai: 'Tau-fluvalinate', cat: 'pest', crops: ['Grapevine', 'Olive'], targets: ['Scaphoideus titanus', 'Olive fruit fly'], use: 'Foliar', moa: 'IRAC 3A' },
    'KLARTAN 20 EW': { ai: 'Tau-fluvalinate', cat: 'pest', crops: ['Grapevine', 'Olive'], targets: ['Scaphoideus titanus', 'Olive fruit fly'], use: 'Foliar', moa: 'IRAC 3A' },
    'TAU AL 240 EW': { ai: 'Tau-fluvalinate', cat: 'pest', crops: ['Grapevine'], targets: ['Scaphoideus titanus'], use: 'Foliar', moa: 'IRAC 3A' },
    'COSAYR 200 SC': { ai: 'Chlorantraniliprole', cat: 'pest', crops: ['Maize', 'Grapevine', 'Tomato', 'Apple'], targets: ['European corn borer', 'Lobesia botrana', 'Tuta absoluta', 'Codling moth'], use: 'Foliar · egg-laying / early larvae', moa: 'IRAC 28' },
    'FORZA': { ai: 'Lambda-cyhalothrin', cat: 'pest', crops: ['Maize'], targets: ['European corn borer', 'Diabrotica adults'], use: 'Foliar · adults', moa: 'IRAC 3A' },
    'NINJA': { ai: 'See label record', cat: 'pest', crops: ['Maize'], targets: ['European corn borer', 'Diabrotica adults'], use: 'Foliar', moa: 'IRAC 3A' },
    'DURAVIS': { ai: 'See label record', cat: 'pest', crops: ['Maize'], targets: ['Soil and foliar pests'], use: 'See label', moa: '—' },
    'ELTIRA': { ai: 'See label record', cat: 'pest', crops: ['Maize'], targets: ['Lepidoptera'], use: 'Foliar', moa: '—' },
    'LEBRON 0.5 G': { ai: 'See label record', cat: 'pest', crops: ['Maize'], targets: ['Diabrotica larvae', 'Soil pests'], use: 'Soil granular at sowing', moa: '—' },
    'SCHERMO 0.5 G': { ai: 'See label record', cat: 'pest', crops: ['Maize'], targets: ['Diabrotica larvae', 'Soil pests'], use: 'Soil granular at sowing', moa: '—' },
    'MAXENTIS': { ai: 'Azoxystrobin + Prothioconazole', cat: 'disease', crops: ['Durum Wheat', 'Wheat', 'Barley'], targets: ['Fusarium head blight', 'Septoria', 'Rusts'], use: 'Foliar · flowering / flag leaf', moa: 'FRAC 11 + 3' },
    'KOJAMI': { ai: 'See label record', cat: 'disease', crops: ['Durum Wheat', 'Wheat'], targets: ['Fusarium head blight', 'Septoria'], use: 'Foliar', moa: '—' },
    'MIRADOR TURBO': { ai: 'See label record', cat: 'disease', crops: ['Durum Wheat', 'Wheat', 'Sugar Beet', 'Grapevine'], targets: ['Fusarium head blight', 'Cercospora', 'Downy mildew', 'Rusts'], use: 'Foliar', moa: 'FRAC 11 (+)' },
    'BLAISE ULTRA': { ai: 'See label record', cat: 'disease', crops: ['Durum Wheat', 'Wheat'], targets: ['Fusarium head blight', 'Rusts'], use: 'Foliar', moa: '—' },
    'CUSTODIA ULTRA': { ai: 'See label record', cat: 'disease', crops: ['Durum Wheat', 'Wheat', 'Sugar Beet'], targets: ['Rusts', 'Septoria', 'Cercospora'], use: 'Foliar', moa: 'FRAC 11 + 3' }
  };
  Object.keys(PRODUCTS).forEach(k => { PRODUCTS[k].name = k; });

  const COMPANIES = ['BASF', 'Bayer', 'Corteva', 'FMC', 'Syngenta', 'UPL'];

  const ACTIONS = {
    weed: [
      ['MARKET DEVELOPMENT', 'Validate the weed complex and resistance context for {crop} in this territory.', 'Weed programmes are decided before the window, not during it.', 'NOW'],
      ['TECHNICAL / SCIENCE', 'Read the authorised use rows for {product} and confirm crop stage, weed stage and dose.', 'The label use rows have not been extracted for any herbicide in the corpus.', 'NOW'],
      ['REGULATORY / PORTFOLIO', 'Confirm HRAC classification and authorisation validity across the herbicide range.', 'Mode of action is undeclared for part of the range and 13 authorisations expire before 2027.', 'CHECK NOW'],
      ['MARKETING', 'Prepare a resistance-management argument rather than a single-product claim.', 'Rotation is the defensible message where GIRE documents resistance.', 'THIS MONTH'],
      ['FIELD SALES', 'Open the programme conversation with dealers and cooperatives before sowing decisions close.', 'The channel decides the whole sequence in one conversation.', 'THIS MONTH'],
      ['SUPPLY', 'Review availability against the pre-emergence window, not the spray date.', 'Herbicide demand concentrates in a short pre-season period.', 'PLAN']
    ],
    pest: [
      ['MARKET DEVELOPMENT', 'Validate whether the movement extends into adjacent {crop} areas.', 'Regional signal is fresh and the window is defined.', 'NOW'],
      ['SALES / RTV', 'Prepare field conversations around the current treatment window.', 'Growers decide within the window, not after it.', 'ACT NOW'],
      ['MARKETING', 'Review competitor communication and prepare regional support material.', 'Competitor content on {crop} was observed this month.', 'PREPARE'],
      ['TECHNICAL / SCIENCE', 'Validate pressure and confirm timing with the next regional update.', 'Timing accuracy drives label-compliant positioning.', '48H'],
      ['REGULATORY / PORTFOLIO', 'Confirm current authorization and label positioning for {product}.', 'Label position must be current before any field message.', 'CHECK NOW'],
      ['SUPPLY', 'Review internal readiness for the expected regional demand window.', 'Demand concentrates inside a short window.', 'PREPARE']
    ],
    disease: [
      ['MARKET DEVELOPMENT', 'Map {crop} area where the disease pressure pattern repeats.', 'Regional scale makes this a programme, not a spot.', 'NOW'],
      ['SALES / RTV', 'Build the treatment-programme conversation for the coming window.', 'Programmes are decided before the season.', 'PREPARE'],
      ['MARKETING', 'Prepare regional technical material on timing and resistance management.', 'Competitor fungicide messaging is active in the region.', 'PREPARE'],
      ['TECHNICAL / SCIENCE', 'Validate pressure model against the regional bulletin and field reports.', 'Disease timing depends on phenology and weather.', 'VALIDATE'],
      ['REGULATORY / PORTFOLIO', 'Confirm current authorization and label positioning for {product}.', 'Authorisations on cereals and beet change frequently.', 'CHECK NOW']
    ]
  };

  // ---- 24 Opportunity cases -------------------------------------------------
  const C = (o) => o;
  const CASES = [
    C({ id: 'IT-OPP-001', issue: 'Flavescenza Dorata', latin: 'Grapevine phytoplasma · vector Scaphoideus titanus', crop: 'Grapevine', region: 'Veneto', cat: 'pest', status: 'ACT NOW', ws: -10, we: 20, updated: 1, primary: 'EVURE PRO', products: ['EVURE PRO', 'MAVRIK SMART', 'KLARTAN SMART', 'KLARTAN 20 EW', 'TAU AL 240 EW', 'MAVRIK EW'], hero: true, source: 'Regional phytosanitary bulletin · compulsory control decree', origin: 41,
      happening: 'Symptom expression is at seasonal peak in the regional vineyards and the compulsory-control framework requires survey and removal of infected vines. Late Scaphoideus titanus adults are still being captured in the monitoring network.',
      why: 'Veneto is the largest Italian wine-grape region and flavescenza dorata control is mandatory. Registered ADAMA tau-fluvalinate products address the vector, and the 2027 treatment programme is being decided now.',
      stage: 'BBCH 85–89 · ripening / harvest', signal: 'Symptom peak · late adult captures', label: 'Vector control per regional decree calendar',
      know: ['Compulsory control decree in force', 'Regional trap network reporting weekly', 'Six registered ADAMA responses on the vector'], watch: ['Regional symptom-survey results', 'Uprooting compliance notices', '2027 treatment calendar publication', 'Competitor vector-control messaging'],
      timeline: [['12 Jun', 'Regional decree · first treatment window'], ['08 Jul', 'Second treatment window'], ['14 Aug', 'Symptom survey starts'], ['27 Aug', 'Late adult captures reported'], ['31 Aug', 'Opportunity updated']],
      adjacent: ['Friuli-Venezia Giulia', 'Trentino-Alto Adige', 'Lombardia'], evidence: { field: 4, science: 6, official: 3, people: 3, market: 2 } }),
    C({ id: 'IT-OPP-002', issue: 'European Corn Borer', latin: 'Ostrinia nubilalis · Diabrotica virgifera also under monitoring', crop: 'Maize', region: 'Friuli-Venezia Giulia', cat: 'pest', status: 'ACTION WINDOW OPENING', ws: -4, we: 14, updated: 2, primary: 'COSAYR 200 SC', products: ['COSAYR 200 SC', 'FORZA', 'NINJA', 'ELTIRA', 'DURAVIS'], hero: true, source: 'Regional maize bulletin (ERSA) · trap network', origin: 18,
      happening: 'Adult flight and oviposition activity are being observed in the regional monitoring network. The crop is entering a stage where timing becomes commercially relevant.',
      why: 'The signal coincides with a major maize production area and with registered ADAMA solutions targeting the observed pests.',
      stage: 'BBCH 65–75 · flowering to grain fill', signal: 'Oviposition increasing', label: 'Intervene during oviposition / early larvae',
      know: ['Regional pest signal observed', 'Crop stage available', 'Registered ADAMA response exists'], watch: ['Next field update', 'Movement into adjacent regions', 'Competitor communication', 'Change in application timing'],
      timeline: [['12 Aug', 'Regional bulletin'], ['18 Aug', 'Adult flight increases'], ['24 Aug', 'Oviposition signal'], ['28 Aug', 'Application window opens'], ['30 Aug', 'Opportunity updated']],
      adjacent: ['Veneto', 'Lombardia', 'Emilia-Romagna'], evidence: { field: 3, science: 4, official: 2, people: 2, market: 3 } }),
    C({ id: 'IT-OPP-003', issue: 'Fusarium Head Blight', latin: 'Fusarium spp. · mycotoxin risk', crop: 'Durum Wheat', region: 'Toscana', sub: 'Grosseto', cat: 'disease', status: 'PREPARE', ws: 250, we: 268, updated: 3, primary: 'MAXENTIS', products: ['MAXENTIS', 'KOJAMI', 'MIRADOR TURBO', 'BLAISE ULTRA', 'CUSTODIA ULTRA'], hero: true, source: 'Field symptoms observed · LaMMA agro-meteorology · ISTAT area', origin: 120,
      happening: 'Field symptoms were observed at flowering in the last campaign in the Grosseto durum area. Sowing plans for the next campaign are being set and the flowering-stage fungicide window will return in May.',
      why: 'Grosseto is one of the main durum wheat districts in central Italy. ADAMA has five registered fungicide responses with a Fusarium label window, so the treatment programme conversation must happen before sowing.',
      stage: 'Pre-sowing · next flowering May 2027', signal: 'Symptom history · mycotoxin attention', label: 'Apply at flowering (BBCH 61–65)',
      know: ['Symptoms observed at flowering last campaign', 'Regional durum area confirmed (ISTAT)', 'Five registered ADAMA fungicides with Fusarium label'], watch: ['Sowing progress and variety choice', 'Spring weather at flowering', 'Mycotoxin regulatory attention', 'Competitor fungicide programmes'],
      timeline: [['22 May', 'Flowering symptoms observed'], ['30 Jun', 'Harvest quality reports'], ['20 Jul', 'Mycotoxin attention in technical media'], ['25 Aug', 'Sowing-plan conversations begin'], ['29 Aug', 'Opportunity updated']],
      adjacent: ['Lazio', 'Umbria', 'Marche'], evidence: { field: 3, science: 7, official: 2, people: 4, market: 3 } }),
    C({ id: 'IT-OPP-004', issue: 'Diabrotica Adults', latin: 'Diabrotica virgifera virgifera · adult feeding on silks', crop: 'Maize', region: 'Lombardia', cat: 'pest', status: 'ACT NOW', ws: -12, we: 9, updated: 1, primary: 'FORZA', products: ['FORZA', 'NINJA', 'COSAYR 200 SC'], source: 'Regional phytosanitary service · yellow-trap network', origin: 26, stage: 'BBCH 67–73', signal: 'Adult captures above threshold', label: 'Foliar treatment on adults at silking', adjacent: ['Piemonte', 'Veneto', 'Emilia-Romagna'], evidence: { field: 4, science: 3, official: 2, people: 2, market: 2 } }),
    C({ id: 'IT-OPP-005', issue: 'Diabrotica Larvae', latin: 'Diabrotica virgifera · soil stage at next sowing', crop: 'Maize', region: 'Piemonte', cat: 'pest', status: 'PREPARE', ws: 215, we: 245, updated: 6, primary: 'LEBRON 0.5 G', products: ['LEBRON 0.5 G', 'SCHERMO 0.5 G'], source: 'Regional phytosanitary service · adult counts predict larval risk', origin: 60, stage: 'Post-harvest · sowing April 2027', signal: 'High adult counts in continuous maize', label: 'Granular at sowing in furrow', adjacent: ['Lombardia'], evidence: { field: 3, science: 3, official: 2, people: 1, market: 2 } }),
    C({ id: 'IT-OPP-006', issue: 'Olive Fruit Fly', latin: 'Bactrocera oleae', crop: 'Olive', region: 'Puglia', cat: 'pest', status: 'ACT NOW', ws: -6, we: 28, updated: 2, primary: 'KLARTAN 20 EW', products: ['KLARTAN 20 EW', 'KLARTAN SMART', 'MAVRIK SMART'], source: 'Producer organisation monitoring (Assoproli) · regional bulletin', origin: 22, stage: 'Fruit hardening to veraison', signal: 'Infestation above intervention threshold', label: 'Adulticide treatment on threshold', adjacent: ['Basilicata', 'Calabria'], evidence: { field: 5, science: 5, official: 2, people: 3, market: 2 } }),
    C({ id: 'IT-OPP-007', issue: 'Cercospora Leaf Spot', latin: 'Cercospora beticola', crop: 'Sugar Beet', region: 'Veneto', cat: 'disease', status: 'WATCH', ws: -22, we: 19, updated: 5, primary: 'MIRADOR TURBO', products: ['MIRADOR TURBO', 'CUSTODIA ULTRA'], source: 'Co.Pro.B. Cercospora DSS referenced by regional bulletin', origin: 55, stage: 'Late canopy · pre-harvest', signal: 'DSS risk moderate', label: 'Fungicide on DSS alert', adjacent: ['Emilia-Romagna'], evidence: { field: 2, science: 3, official: 2, people: 1, market: 1 } }),
    C({ id: 'IT-OPP-008', issue: 'Cercospora Leaf Spot', latin: 'Cercospora beticola', crop: 'Sugar Beet', region: 'Emilia-Romagna', cat: 'disease', status: 'WATCH', ws: -22, we: 16, updated: 4, primary: 'MIRADOR TURBO', products: ['MIRADOR TURBO', 'CUSTODIA ULTRA'], source: 'Co.Pro.B. DSS · regional technical network', origin: 55, stage: 'Late canopy', signal: 'DSS risk moderate', label: 'Fungicide on DSS alert', adjacent: ['Veneto', 'Lombardia'], evidence: { field: 3, science: 3, official: 2, people: 2, market: 1 } }),
    C({ id: 'IT-OPP-009', issue: 'Flavescenza Dorata', latin: 'Scaphoideus titanus · late adults', crop: 'Grapevine', region: 'Piemonte', cat: 'pest', status: 'WATCH', ws: -20, we: 12, updated: 4, primary: 'MAVRIK SMART', products: ['MAVRIK SMART', 'EVURE PRO', 'KLARTAN SMART', 'TAU AL 240 EW'], source: 'Regional phytosanitary service · compulsory control area', origin: 70, stage: 'Harvest', signal: 'Late adults · symptom survey', label: 'Per regional decree calendar', adjacent: ['Lombardia', 'Liguria'], evidence: { field: 3, science: 5, official: 3, people: 2, market: 1 } }),
    C({ id: 'IT-OPP-010', issue: 'Olive Fruit Fly', latin: 'Bactrocera oleae', crop: 'Olive', region: 'Sicilia', cat: 'pest', status: 'ACT NOW', ws: -8, we: 30, updated: 1, primary: 'KLARTAN SMART', products: ['KLARTAN SMART', 'KLARTAN 20 EW', 'MAVRIK SMART'], source: 'Regional phytosanitary bulletin · producer organisations', origin: 30, stage: 'Fruit hardening', signal: 'Second-generation flight rising', label: 'Adulticide treatment on threshold', adjacent: ['Calabria'], evidence: { field: 4, science: 4, official: 2, people: 2, market: 2 } }),
    C({ id: 'IT-OPP-011', issue: 'European Corn Borer', latin: 'Ostrinia nubilalis · second generation', crop: 'Maize', region: 'Veneto', cat: 'pest', status: 'ACT NOW', ws: -9, we: 8, updated: 1, primary: 'COSAYR 200 SC', products: ['COSAYR 200 SC', 'FORZA', 'NINJA', 'ELTIRA'], source: 'Regional phytosanitary bulletin · trap network', origin: 24, stage: 'BBCH 71–75', signal: 'Egg masses found in fields', label: 'Intervene at egg hatch', adjacent: ['Friuli-Venezia Giulia', 'Lombardia'], evidence: { field: 4, science: 4, official: 2, people: 2, market: 3 } }),
    C({ id: 'IT-OPP-012', issue: 'Olive Fruit Fly', latin: 'Bactrocera oleae', crop: 'Olive', region: 'Toscana', cat: 'pest', status: 'WATCH', ws: -2, we: 32, updated: 5, primary: 'MAVRIK SMART', products: ['MAVRIK SMART', 'KLARTAN 20 EW'], source: 'Consorzio Olio Toscano IGP via agricultural media · 27 Aug 2026 · LaMMA weather', origin: 19, stage: 'Fruit hardening', signal: 'Pressure reported very low · weather could turn favourable', label: 'Adulticide treatment on threshold', adjacent: ['Umbria', 'Lazio'], evidence: { field: 3, science: 3, official: 2, people: 2, market: 1 } }),
    C({ id: 'IT-OPP-013', issue: 'Grapevine Moth', latin: 'Lobesia botrana · third generation', crop: 'Grapevine', region: 'Sicilia', cat: 'pest', status: 'ACTION WINDOW OPENING', ws: -3, we: 13, updated: 3, primary: 'COSAYR 200 SC', products: ['COSAYR 200 SC'], source: 'Regional phytosanitary bulletin · table-grape districts', origin: 15, stage: 'Veraison to harvest (table grape)', signal: 'Third-generation flight', label: 'Ovicidal-larvicidal timing at egg-laying', adjacent: ['Puglia'], evidence: { field: 2, science: 3, official: 2, people: 1, market: 2 } }),
    C({ id: 'IT-OPP-014', issue: 'Codling Moth', latin: 'Cydia pomonella · late generation', crop: 'Apple', region: 'Trentino-Alto Adige', cat: 'pest', status: 'ACTION WINDOW OPENING', ws: -5, we: 11, updated: 2, primary: 'COSAYR 200 SC', products: ['COSAYR 200 SC'], source: 'Provincial advisory service bulletin', origin: 21, stage: 'Pre-harvest', signal: 'Late flight · pre-harvest interval attention', label: 'Respect pre-harvest interval', adjacent: ['Veneto'], evidence: { field: 3, science: 3, official: 2, people: 2, market: 2 } }),
    C({ id: 'IT-OPP-015', issue: 'Septoria Leaf Blotch', latin: 'Zymoseptoria tritici', crop: 'Wheat', region: 'Emilia-Romagna', cat: 'disease', status: 'PREPARE', ws: 200, we: 235, updated: 7, primary: 'MAXENTIS', products: ['MAXENTIS', 'KOJAMI', 'CUSTODIA ULTRA', 'MIRADOR TURBO'], source: 'Regional technical network (Piacenza) · bulletin archive', origin: 90, stage: 'Pre-sowing · T1/T2 window spring 2027', signal: 'High-pressure history in the plain', label: 'Flag leaf application', adjacent: ['Lombardia', 'Veneto'], evidence: { field: 2, science: 4, official: 2, people: 2, market: 3 } }),
    C({ id: 'IT-OPP-016', issue: 'Fusarium Head Blight', latin: 'Fusarium spp.', crop: 'Durum Wheat', region: 'Puglia', cat: 'disease', status: 'PREPARE', ws: 235, we: 255, updated: 6, primary: 'KOJAMI', products: ['KOJAMI', 'MAXENTIS', 'MIRADOR TURBO', 'BLAISE ULTRA'], source: 'ISTAT durum area · regional technical media', origin: 100, stage: 'Pre-sowing · flowering April–May 2027', signal: 'Largest durum area in Italy · programme decisions', label: 'Apply at flowering', adjacent: ['Basilicata', 'Molise'], evidence: { field: 1, science: 6, official: 2, people: 3, market: 3 } }),
    C({ id: 'IT-OPP-017', issue: 'Cereal Aphids · BYDV Risk', latin: 'Rhopalosiphum padi · virus vector', crop: 'Wheat', region: 'Puglia', cat: 'pest', status: 'PREPARE', ws: 55, we: 90, updated: 8, primary: 'MAVRIK EW', products: ['MAVRIK EW', 'MAVRIK SMART'], source: 'Regional bulletin · autumn sowing calendar', origin: 45, stage: 'Sowing Oct–Nov', signal: 'Mild-autumn forecasts raise vector activity', label: 'Autumn foliar on aphid presence', adjacent: ['Basilicata'], evidence: { field: 1, science: 2, official: 1, people: 2, market: 1 } }),
    C({ id: 'IT-OPP-018', issue: 'Wheat Rusts', latin: 'Puccinia spp.', crop: 'Durum Wheat', region: 'Sicilia', cat: 'disease', status: 'PREPARE', ws: 190, we: 230, updated: 9, primary: 'CUSTODIA ULTRA', products: ['CUSTODIA ULTRA', 'MAXENTIS', 'BLAISE ULTRA', 'MIRADOR TURBO'], source: 'ISTAT durum area · technical media', origin: 110, stage: 'Pre-sowing', signal: 'Early-rust seasons recur in the island', label: 'Foliar at first pustules', adjacent: ['Calabria'], evidence: { field: 1, science: 3, official: 2, people: 2, market: 2 } }),
    C({ id: 'IT-OPP-019', issue: 'Diabrotica Larvae', latin: 'Diabrotica virgifera · soil stage', crop: 'Maize', region: 'Veneto', cat: 'pest', status: 'PREPARE', ws: 215, we: 245, updated: 6, primary: 'SCHERMO 0.5 G', products: ['SCHERMO 0.5 G', 'LEBRON 0.5 G'], source: 'Regional phytosanitary service · adult counts', origin: 60, stage: 'Sowing April 2027', signal: 'Continuous-maize risk areas mapped', label: 'Granular at sowing', adjacent: ['Friuli-Venezia Giulia'], evidence: { field: 3, science: 3, official: 2, people: 1, market: 1 } }),
    C({ id: 'IT-OPP-020', issue: 'Tomato Leafminer', latin: 'Tuta absoluta', crop: 'Tomato', region: 'Puglia', cat: 'pest', status: 'WATCH', ws: -30, we: 10, updated: 5, primary: 'COSAYR 200 SC', products: ['COSAYR 200 SC'], source: 'Producer organisation · processing-tomato district', origin: 40, stage: 'Late harvest', signal: 'Population stable · harvest closing', label: 'Larvicidal on threshold · PHI', adjacent: ['Campania', 'Emilia-Romagna'], evidence: { field: 2, science: 3, official: 1, people: 2, market: 2 } }),
    C({ id: 'IT-OPP-021', issue: 'Downy Mildew', latin: 'Plasmopara viticola', crop: 'Grapevine', region: 'Veneto', cat: 'disease', status: 'WATCH', ws: -60, we: 5, updated: 6, primary: 'MIRADOR TURBO', products: ['MIRADOR TURBO'], source: 'Regional phytosanitary bulletin · season review', origin: 80, stage: 'Harvest · season closing', signal: 'Late-season attacks on laterals', label: 'Season programme · 2027 planning', adjacent: ['Friuli-Venezia Giulia', 'Trentino-Alto Adige'], evidence: { field: 3, science: 4, official: 2, people: 2, market: 4 } }),
    C({ id: 'IT-OPP-022', issue: 'Mycotoxin Risk', latin: 'Fusarium / Aspergillus · aflatoxin attention', crop: 'Maize', region: 'Lombardia', cat: 'disease', status: 'VALIDATE', ws: 0, we: 40, updated: 3, primary: null, products: [], source: 'Regional technical media · research signal', origin: 12, stage: 'Grain fill · pre-harvest', signal: 'Hot-season aflatoxin attention rising', label: 'Portfolio check needed', adjacent: ['Piemonte', 'Veneto'], evidence: { field: 1, science: 5, official: 1, people: 3, market: 1 } }),
    C({ id: 'IT-OPP-023', issue: 'European Corn Borer', latin: 'Ostrinia nubilalis · late flight', crop: 'Maize', region: 'Emilia-Romagna', cat: 'pest', status: 'VALIDATE', ws: -6, we: 9, updated: 4, primary: 'COSAYR 200 SC', products: ['COSAYR 200 SC', 'FORZA'], source: 'Regional technical network · needs field confirmation', origin: 9, stage: 'BBCH 75–79', signal: 'Late flight reported · not yet confirmed', label: 'Intervene at egg hatch if confirmed', adjacent: ['Veneto', 'Lombardia'], evidence: { field: 1, science: 2, official: 1, people: 1, market: 2 } }),
    C({ id: 'IT-OPP-024', issue: 'Powdery Mildew', latin: 'Erysiphe necator', crop: 'Grapevine', region: 'Puglia', cat: 'disease', status: 'VALIDATE', ws: -40, we: 6, updated: 7, primary: null, products: [], source: 'Technical media · producer voices', origin: 14, stage: 'Harvest (table grape)', signal: 'Late attacks reported in technical media', label: 'Portfolio check needed', adjacent: ['Sicilia', 'Basilicata'], evidence: { field: 1, science: 2, official: 1, people: 3, market: 1 } }),
    C({ id: 'IT-OPP-025', issue: 'Grass weed complex', latin: 'Sorghum halepense · Echinochloa spp. · Setaria spp.', crop: 'Maize', region: 'Lombardia', cat: 'weed', status: 'PREPARE', ws: 212, we: 282, updated: 3, primary: 'SULCOTREK', products: ['SULCOTREK', 'PYXIDES WG', 'NICOGAN V.O.', 'ACTIVUS 40 SC'], source: 'ADAMA Italy label corpus · GIRE resistance database', origin: 0,
      happening: 'The 2027 maize weed programme is being decided now, before winter. Ten registered ADAMA herbicides carry MAIZE on the label, across four HRAC groups, and GIRE documents ALS- and triazine-resistant populations in the northern maize belt.',
      why: 'Lombardia is the largest Italian maize area. Weed control is a planned, programme-based decision — it does not need an outbreak to be commercially relevant, and the decision is made months before the spray.',
      stage: 'Post-harvest · programme decisions for 2027', signal: 'Pre-season commercial preparation', label: 'Pre-emergence from sowing; post-emergence at crop 2–6 leaves',
      know: ['Ten registered ADAMA herbicides with MAIZE on the label', 'Four HRAC groups available for rotation', 'GIRE documents resistant populations in northern maize', 'Two distinct windows — pre- and post-emergence'], watch: ['Authorised use rows still unread for all 91 herbicides', 'Regional weed pressure for 2027', 'Competitor pre-emergence communication', 'Sowing area decisions'],
      timeline: [['02 Sep', 'Herbicide layer promoted into the radar'], ['01 Apr', 'Expected pre-emergence window opens'], ['05 May', 'Expected post-emergence window opens']],
      adjacent: ['Veneto', 'Piemonte', 'Friuli-Venezia Giulia', 'Emilia-Romagna'], evidence: { field: 2, science: 4, official: 10, people: 0, market: 1 } }),
    C({ id: 'IT-OPP-026', issue: 'Resistant grass weeds', latin: 'Lolium spp. · Avena spp. · Phalaris spp. · Alopecurus myosuroides', crop: 'Durum Wheat', region: 'Puglia', cat: 'weed', status: 'PREPARE', ws: 61, we: 105, updated: 2, primary: 'TOPIK 80 EC', products: ['TOPIK 80 EC', 'CELIO 80 EC', 'EDAPTIS', 'DICURAN PLUS'], source: 'ADAMA Italy label corpus · GIRE resistance database', origin: 0,
      happening: 'Autumn sowing decisions are being made in the main durum districts. Thirteen registered ADAMA herbicides carry DURUM_WHEAT on the label, and GIRE records ACCase- and ALS-resistant grass weeds in Italian cereals.',
      why: 'Puglia is the largest durum area in Italy. The autumn window follows sowing within weeks, so the commercial conversation has to happen before the drill moves — and Market Pulse reads durum as pressured, which makes the value argument harder and more necessary.',
      stage: 'Pre-sowing · soil preparation reported by the field network', signal: 'Autumn window approaching · 61 days',
      label: 'Pre- or early post-emergence after sowing; post-emergence at tillering',
      know: ['Thirteen registered ADAMA herbicides with DURUM_WHEAT on the label', 'HRAC 1 and HRAC 2 both available', 'GIRE records resistant Lolium and Avena in Italian cereals', 'Field network reports soil preparation under way near Foggia'], watch: ['Authorised use rows unread', 'Whether resistance is present in these specific fields', 'Sowing intentions for 2027', 'Competitor cereal herbicide communication'],
      timeline: [['02 Sep', 'Herbicide layer promoted into the radar'], ['01 Nov', 'Expected autumn window opens'], ['01 Feb', 'Expected tillering window opens']],
      adjacent: ['Sicilia', 'Basilicata', 'Toscana'], evidence: { field: 1, science: 5, official: 13, people: 0, market: 3 } }),
    C({ id: 'IT-OPP-027', issue: 'Beet weed programme', latin: 'Chenopodium album · Amaranthus retroflexus · Polygonum spp.', crop: 'Sugar Beet', region: 'Emilia-Romagna', cat: 'weed', status: 'PREPARE', ws: 190, we: 242, updated: 4, primary: 'GOLTIX', products: ['GOLTIX', 'CONTATTO 320', 'LEOPARD 5 EC'], source: 'ADAMA Italy label corpus · cooperative channel enquiry', origin: 0,
      happening: 'A cooperative has asked which ADAMA options are available for the 2027 beet weed programme, ahead of its technical meeting. SUGARBEET is the second-largest crop term in the herbicide portfolio with 32 registered products.',
      why: 'Beet weed control is a repeated low-dose programme rather than a single spray, which makes it a genuinely different commercial rhythm — the channel decides the whole sequence in one conversation, months ahead.',
      stage: 'Post-harvest · 2027 programme design', signal: 'Channel question reported · cooperative',
      label: 'Pre-emergence after sowing, then repeated low-dose post-emergence',
      know: ['32 registered ADAMA herbicides with SUGARBEET on the label', 'Metamitron, phenmedipham and graminicide routes all present', 'A cooperative enquiry is on record in the field channel', 'The programme is decided in a single channel conversation'], watch: ['Authorised use rows unread', 'Beet contract area for 2027', 'Whether the cooperative enquiry repeats', 'Cercospora programme timing on the same crop'],
      timeline: [['02 Sep', 'Herbicide layer promoted into the radar'], ['10 Mar', 'Expected pre-emergence window opens'], ['05 Apr', 'Expected post-emergence programme starts']],
      adjacent: ['Veneto', 'Lombardia'], evidence: { field: 1, science: 1, official: 32, people: 0, market: 0 } }),
    C({ id: 'IT-OPP-028', issue: 'Herbicide resistance · rice', latin: 'Echinochloa spp. · Alisma plantago-aquatica · Cyperus spp.', crop: 'Rice', region: 'Piemonte', cat: 'weed', status: 'VALIDATE', ws: 226, we: 292, updated: 1, primary: 'DAVAI', products: ['DAVAI', 'EARLEX'], source: 'GIRE resistance database · ADAMA Italy label corpus', origin: 0,
      happening: 'Rice carries the heaviest documented herbicide-resistance load of any Italian crop in the GIRE record — ALS, ACCase, propanil and Clearfield-variety cases. A grower has reported that his usual programme is not holding on Echinochloa, from a single farm and with no measurement.',
      why: 'Fifteen registered ADAMA herbicides carry RICE on the label. Any rice weed conversation in Italy is a resistance-management conversation first, and that is a technical argument rather than a price one.',
      stage: 'Harvest · next-programme decisions', signal: 'Local concern reported · validation needed',
      label: 'Pre-emergence before flooding; post-emergence in water',
      know: ['Rice has the highest GIRE case count of any Italian crop', 'Fifteen registered ADAMA herbicides with RICE on the label', 'ALS, ACCase, propanil and Clearfield cases all documented', 'One field report of a programme not holding'], watch: ['The single-farm report is unvalidated — it is not regional resistance', 'Which ADAMA rice uses are authorised against which species', 'Whether the report repeats in other territories', 'GIRE updates for the Piemonte rice belt'],
      timeline: [['02 Sep', 'Herbicide layer promoted into the radar'], ['20 Apr', 'Expected pre-emergence window opens'], ['15 May', 'Expected post-emergence window opens']],
      adjacent: ['Lombardia'], evidence: { field: 1, science: 8, official: 15, people: 0, market: 0 } }),
    C({ id: 'IT-OPP-029', issue: 'Soybean grass weeds', latin: 'Sorghum halepense · Amaranthus spp. · Echinochloa spp.', crop: 'Soybean', region: 'Veneto', cat: 'weed', status: 'WATCH', ws: 261, we: 297, updated: 5, primary: 'AGIL', products: ['AGIL', 'LEOPARD 5 EC', 'DAVAI', 'ACTIVUS 40 SC'], source: 'ADAMA Italy label corpus · GIRE resistance database', origin: 0,
      happening: 'A dealer has asked twice in one week which graminicide options exist for soybean, after two customers had Sorghum halepense problems. Twenty-one registered ADAMA herbicides carry SOYBEAN on the label, and GIRE documents ALS-resistant Amaranthus in Italian soybean.',
      why: 'Soybean has substantial ADAMA herbicide presence and no representation anywhere else in the pilot. The graminicide route (HRAC 1) and the ALS route (HRAC 2) are commercially different arguments to the same customer.',
      stage: 'Harvest approaching · 2027 planning', signal: 'Product interest reported · dealer',
      label: 'Pre-emergence after sowing; post-emergence at weed 2–4 leaves',
      know: ['21 registered ADAMA herbicides with SOYBEAN on the label', 'HRAC 1 and HRAC 2 routes both available', 'GIRE documents ALS-resistant Amaranthus in soybean', 'A dealer enquiry is on record in the field channel'], watch: ['Authorised use rows unread', 'Soybean area intentions for 2027', 'Whether the dealer enquiry becomes a pattern', 'Competitor soybean herbicide communication'],
      timeline: [['02 Sep', 'Herbicide layer promoted into the radar'], ['20 Apr', 'Expected pre-emergence window opens'], ['20 May', 'Expected post-emergence window opens']],
      adjacent: ['Friuli-Venezia Giulia', 'Emilia-Romagna', 'Piemonte'], evidence: { field: 1, science: 4, official: 21, people: 0, market: 0 } })
  ];
  const genText = (c) => {
    const p = c.primary ? PRODUCTS[c.primary] : null;
    if (!c.happening) c.happening = c.cat === 'pest'
      ? `${c.signal} in the ${c.region} monitoring network for ${c.crop.toLowerCase()}. Crop stage: ${c.stage.toLowerCase()}.`
      : `${c.signal} for ${c.crop.toLowerCase()} in ${c.region}. Crop stage: ${c.stage.toLowerCase()}.`;
    if (!c.why) c.why = p
      ? `${c.region} is a relevant ${c.crop.toLowerCase()} area and ${c.primary} carries a registered ${c.crop} · ${c.issue.toLowerCase()} position${c.products.length > 1 ? ', with ' + (c.products.length - 1) + ' further ADAMA matches' : ''}.`
      : `${c.region} is a relevant ${c.crop.toLowerCase()} area. No confirmed ADAMA label position has been matched yet — Regulatory / Portfolio should confirm before this becomes a commercial case.`;
    if (!c.know) c.know = [`${c.cat === 'pest' ? 'Regional pest' : 'Regional disease'} signal observed`, 'Crop stage available', p ? 'Registered ADAMA response exists' : 'Portfolio position to be confirmed'];
    if (!c.watch) c.watch = ['Next regional update', 'Movement into ' + c.adjacent[0], 'Competitor communication', 'Change in application timing'];
    if (!c.timeline) {
      const b = addDays(TODAY, -Math.max(20, c.origin));
      c.timeline = [[fmt(b), 'Entered Future Radar'], [fmt(addDays(b, 8)), 'Regional bulletin'], [fmt(addDays(b, Math.max(12, c.origin - 6))), c.signal.split(' ·')[0]], [fmt(addDays(TODAY, -c.updated)), 'Opportunity updated']];
    }
  };

  const REAL_OBS = { 'IT-OPP-001': ['Regione Veneto: 20 grapevine bulletins published in 2026 through 27 Aug', 'Regione Veneto — Servizio Fitosanitario'], 'IT-OPP-002': ['ERSA FVG maize integrated-defence bulletin series · latest measured 12 Aug 2026', 'ERSA Friuli-Venezia Giulia'], 'IT-OPP-009': ['Official 2026 Flavescenza survey · field period 14 Jul → 30 Sep 2026', 'Regione Piemonte — Settore Fitosanitario'], 'IT-OPP-012': ['Olive fruit fly pressure reported extremely low in Tuscany (week to 27 Aug); cooler humid conditions could favour the pest', 'Consorzio Olio Toscano IGP via agricultural media'], 'IT-OPP-014': ['Golden harvest starting 1 Sep on the valley floor, hill zones ~6–7 days later (Italiafruit, 1 Sep)', 'Italiafruit News'], 'IT-OPP-015': ['National soft-wheat varietal trial results published 27 Aug for 2026 sowing decisions', "L'Informatore Agrario"], 'IT-OPP-006': ['Puglia: +50% subsidised fuel for additional phytosanitary treatments (26 Aug) — management-intensity signal only', 'Regione Puglia via regional press'], 'IT-OPP-022': ['2026 research activity on seasonal aflatoxin forecasting and predictive models (Università Cattolica Piacenza · CNR-ISPA) — science signal, not incidence', 'Università Cattolica · CNR-ISPA'], 'IT-OPP-003': ['Durum-wheat research ecosystem (CNR-ISPA Fusarium metabolism, fumonisins) active in 2026 — science signal', 'CNR-ISPA'] };
  CASES.forEach((c, i) => {
    genText(c);
    if (REAL_OBS[c.id]) { c.realObs = { text: REAL_OBS[c.id][0], source: REAL_OBS[c.id][1], provenance: 'REAL_FACT' }; c.know.unshift('Real observation · ' + REAL_OBS[c.id][0]); c.evidence.official += 1; }
    c.n = i;
    c.category = CAT[c.cat];
    c.st = STATUS[c.status];
    /* CANONICAL WINDOW CONSUMPTION — the presentation layer reads, it does not compute.
       The former transform (addDays(TODAY, ws/we)) produced a window that slid with the
       clock and could never be stale. It is deleted. See WINDOW-TRUTH-AUDIT.md § 2.5. */
    const CW = (window.ITALY_CANONICAL && window.ITALY_CANONICAL.windows) || [];
    const cw = CW.find(w => w.LEGACY_CASE_ID === c.id) || null;
    c.canonical = cw;
    c.windowId = cw ? cw.WINDOW_ID : null;
    c.dateState = cw ? cw.DATE_STATE : 'DATE_TO_CONFIRM';
    c.dateConfidence = cw ? cw.DATE_CONFIDENCE : 'NONE';
    c.provenance = cw ? cw.PROVENANCE : 'NOT_ESTABLISHED';
    c.statusReason = cw ? cw.STATUS_REASON : 'No canonical window object for this case';
    c.lastValidated = cw ? cw.LAST_VALIDATED : null;
    c.cropStageClass = cw ? cw.CROP_STAGE_CLASS : 'UNKNOWN';
    c.issueStageClass = cw ? cw.ISSUE_STAGE_CLASS : 'UNKNOWN';
    c.hasDates = !!(cw && cw.START_DATE && cw.END_DATE);
    c.windowStart = c.hasDates ? new Date(cw.START_DATE + 'T00:00:00') : null;
    c.windowEnd = c.hasDates ? new Date(cw.END_DATE + 'T00:00:00') : null;
    c.wsLabel = c.hasDates ? fmt(c.windowStart) : null;
    c.weLabel = c.hasDates ? fmt(c.windowEnd) : null;
    // status is supplied upstream, never derived
    c.status = cw ? cw.CURRENT_STATUS : 'DATE_UNKNOWN';
    c.st = STATUS[c.status] || STATUS['DATE_UNKNOWN'];
    c.windowOpen = c.status === 'WINDOW_OPEN' || c.status === 'ACT_NOW';
    c.daysLeft = c.hasDates ? Math.round((c.windowEnd - TODAY) / 864e5) : null;
    c.daysToOpen = c.hasDates ? Math.round((c.windowStart - TODAY) / 864e5) : null;
    // presentation-only derivations, permitted by the contract
    c.progress = (c.windowOpen && c.hasDates) ? Math.max(0, Math.min(100, Math.round((TODAY - c.windowStart) / (c.windowEnd - c.windowStart) * 100))) : 0;
    c.windowLine = !c.hasDates ? 'DATE_TO_CONFIRM'
      : c.windowOpen ? c.daysLeft + '|daysRemaining'
      : c.daysToOpen > 0 ? c.daysToOpen + '|daysToOpen'
      : 'WINDOW_CLOSED';
    // expected must never read as observed
    c.stage = (cw && cw.CROP_STAGE) ? cw.CROP_STAGE : 'NOT_OBSERVED';
    c.signal = (cw && cw.ISSUE_STAGE) ? cw.ISSUE_STAGE : 'NOT_OBSERVED';
    c.updatedLabel = ago(c.updated);
    /* UPSTREAM LABEL VERDICTS. Every product relationship carries an explicit strength
       class supplied by the label audit. The presentation layer never promotes a weaker
       relationship, and a NOT_FOUND verdict is never rendered as "ADAMA has no product". */
    const LV = window.ITALY_LABEL_VERDICTS;
    const vd = (p) => LV ? LV.verdict(c.crop, c.issue, p) : 'LABEL_CHECK_NEEDED';
    c.productLinks = c.products.map(k => ({ name: k, obj: PRODUCTS[k], strength: vd(k) }));
    c.verifiedLinks = c.productLinks.filter(l => l.strength === 'VERIFIED_LABEL_MATCH');
    c.hasVerifiedMatch = c.verifiedLinks.length > 0;
    /* The label audit controls CLAIM STRENGTH, not visibility. A candidate whose label
       has not been verified stays on the card with an honest amber class — hiding it turned
       LABEL_CHECK_NEEDED into "no portfolio", which was destructive and wrong. Only a
       relationship the audit explicitly REJECTED is refused the primary slot. */
    const RANK = { VERIFIED_LABEL_MATCH: 0, RELATED_PORTFOLIO: 1, LABEL_CHECK_NEEDED: 2, NO_CONFIRMED_MATCH_CURRENT_READING: 3 };
    c.verifiedCount = c.productLinks.filter(l => l.strength === 'VERIFIED_LABEL_MATCH').length;
    c.relatedCount = c.productLinks.filter(l => l.strength === 'RELATED_PORTFOLIO').length;
    c.checkNeededCount = c.productLinks.filter(l => l.strength === 'LABEL_CHECK_NEEDED').length;
    c.notConfirmedCount = c.productLinks.filter(l => l.strength === 'NO_CONFIRMED_MATCH_CURRENT_READING').length;
    // best showable candidate: anything the audit did not reject, strongest first
    const showable = c.productLinks.filter(l => l.strength !== 'NO_CONFIRMED_MATCH_CURRENT_READING')
      .sort((x, y) => RANK[x.strength] - RANK[y.strength]);
    const primaryVerdict = c.primary ? vd(c.primary) : null;
    c.primaryRejected = !!(c.primary && primaryVerdict === 'NO_CONFIRMED_MATCH_CURRENT_READING');
    if (c.primaryRejected) {
      c.primaryWas = c.primary;
      c.primary = showable.length ? showable[0].name : null;
    }
    c.primaryVerdict = c.primary ? vd(c.primary) : null;
    c.primaryDowngraded = c.primaryVerdict !== null && c.primaryVerdict !== 'VERIFIED_LABEL_MATCH';
    c.matchCount = showable.length;
    c.moreMatches = Math.max(0, showable.length - 1);
    c.primaryAi = c.primary ? PRODUCTS[c.primary].ai : 'AI_NOT_APPLICABLE';
    c.productObjs = c.products.map(k => PRODUCTS[k]);
    c.alternatives = c.productObjs.slice(1);
    c.primaryObj = c.primary ? PRODUCTS[c.primary] : null;
    c.portfolioState = c.primaryVerdict || 'NO_CONFIRMED_MATCH_CURRENT_READING';
    const acts = ACTIONS[c.cat].filter(a => a[0] !== 'SUPPLY' || c.st.rank <= 1);
    c.actions = acts.map(a => ({ dept: a[0], what: a[1].replace('{crop}', c.crop.toLowerCase()).replace('{product}', c.primary || 'the candidate portfolio'), why: a[2].replace('{crop}', c.crop.toLowerCase()), when: a[3], color: ['NOW', 'ACT NOW', 'CHECK NOW', '48H'].includes(a[3]) ? '#009845' : '#978B87', soft: '#978B87' }));
    c.departments = c.actions.filter(a => ['NOW', 'ACT NOW', 'CHECK NOW', '48H'].includes(a.when)).map(a => a.dept);
    c.evidenceTotal = Object.values(c.evidence).reduce((s, v) => s + v, 0);
    c.evidenceLabel = c.evidenceTotal >= 16 ? 'Strong' : c.evidenceTotal >= 11 ? 'Good' : 'Building';
    c.originLabel = `Originated from Future Radar · ${c.origin} days ago`;
    c.competitors = [0, 1, 2].map(k => { const co = COMPANIES[(i + k * 3) % COMPANIES.length]; const items = 1 + Math.floor(seed(i * 7 + k) * 4); return { company: co, items, topic: `${c.crop} ${c.cat === 'pest' ? 'pest' : 'disease'}-control communication`, days: 1 + Math.floor(seed(i * 11 + k) * 12), type: pick(['Paid creative observed', 'Organic post observed', 'Technical video observed', 'People mention observed'], i * 13 + k) }; });
    c.sub = c.sub || null;
    c.regionLabel = c.sub ? `${c.region} · ${c.sub}` : c.region;
    c.tl = c.timeline.map((t, k) => ({ date: t[0], label: t[1], last: k === c.timeline.length - 1, color: k === c.timeline.length - 1 ? '#009845' : '#6E6663' }));
  });

  // ---- Future Radar (56 signals) -------------------------------------------
  const THEMES = [
    { issue: 'Flavescenza Dorata', crop: 'Grapevine', cat: 'pest', regions: ['Lombardia', 'Friuli-Venezia Giulia', 'Trentino-Alto Adige', 'Emilia-Romagna', 'Toscana'], product: 'EVURE PRO', science: 'grapevine-phytoplasma' },
    { issue: 'European Corn Borer', crop: 'Maize', cat: 'pest', regions: ['Lombardia', 'Piemonte'], product: 'COSAYR 200 SC', science: 'maize-borer' },
    { issue: 'Diabrotica', crop: 'Maize', cat: 'pest', regions: ['Friuli-Venezia Giulia', 'Emilia-Romagna'], product: 'FORZA', science: 'maize-borer' },
    { issue: 'Fusarium Head Blight', crop: 'Durum Wheat', cat: 'disease', regions: ['Marche', 'Sicilia', 'Basilicata', 'Lazio'], product: 'MAXENTIS', science: 'durum-fusarium' },
    { issue: 'Septoria', crop: 'Wheat', cat: 'disease', regions: ['Lombardia', 'Veneto', 'Piemonte'], product: 'MAXENTIS', science: 'durum-fusarium' },
    { issue: 'Cercospora', crop: 'Sugar Beet', cat: 'disease', regions: ['Lombardia', 'Marche'], product: 'MIRADOR TURBO', science: null },
    { issue: 'Olive Fruit Fly', crop: 'Olive', cat: 'pest', regions: ['Calabria', 'Lazio', 'Umbria', 'Liguria', 'Campania'], product: 'KLARTAN 20 EW', science: 'olive-bactrocera' },
    { issue: 'Downy Mildew', crop: 'Grapevine', cat: 'disease', regions: ['Piemonte', 'Toscana', 'Friuli-Venezia Giulia', 'Emilia-Romagna'], product: 'MIRADOR TURBO', science: null },
    { issue: 'Powdery Mildew', crop: 'Grapevine', cat: 'disease', regions: ['Sicilia', 'Veneto', 'Toscana'], product: null, science: null },
    { issue: 'Mycotoxin Risk', crop: 'Maize', cat: 'disease', regions: ['Veneto', 'Piemonte', 'Friuli-Venezia Giulia', 'Emilia-Romagna'], product: null, science: 'maize-mycotoxins' },
    { issue: 'Grapevine Moth', crop: 'Grapevine', cat: 'pest', regions: ['Puglia', 'Veneto', 'Toscana', 'Piemonte'], product: 'COSAYR 200 SC', science: null },
    { issue: 'Tomato Leafminer', crop: 'Tomato', cat: 'pest', regions: ['Emilia-Romagna', 'Campania', 'Sicilia'], product: 'COSAYR 200 SC', science: null },
    { issue: 'Codling Moth', crop: 'Apple', cat: 'pest', regions: ['Veneto', 'Emilia-Romagna', 'Piemonte'], product: 'COSAYR 200 SC', science: null },
    { issue: 'Cereal Aphids · BYDV', crop: 'Wheat', cat: 'pest', regions: ['Emilia-Romagna', 'Toscana', 'Sicilia', 'Marche'], product: 'MAVRIK EW', science: null },
    { issue: 'Xylella fastidiosa', crop: 'Olive', cat: 'disease', regions: ['Puglia', 'Basilicata'], product: null, science: 'xylella' },
    { issue: 'Brown Marmorated Stink Bug', crop: 'Apple', cat: 'pest', regions: ['Emilia-Romagna', 'Veneto', 'Piemonte', 'Trentino-Alto Adige'], product: null, science: null },
    { issue: 'Popillia japonica', crop: 'Maize', cat: 'pest', regions: ['Piemonte', 'Lombardia'], product: null, science: null },
    { issue: 'Scaphoideus titanus resistance', crop: 'Grapevine', cat: 'pest', regions: ['Veneto', 'Piemonte'], product: 'EVURE PRO', science: 'scaphoideus' }
  ];
  const F_SOURCES = ['Science', 'Researchers', 'Field network', 'Regulatory', 'Technical media', 'Producer organizations', 'Competitor movement'];
  const F_STATUS = ['NEW SIGNAL', 'GAINING ATTENTION', 'MULTIPLE SIGNALS', 'WATCH CLOSELY', 'NEEDS VALIDATION', 'TIMING APPROACHING', 'PREPARE'];
  const F_COLOR = { 'NEW SIGNAL': '#B1A9A7', 'GAINING ATTENTION': '#B1A9A7', 'MULTIPLE SIGNALS': '#B1A9A7', 'WATCH CLOSELY': '#B1A9A7', 'NEEDS VALIDATION': '#B1A9A7', 'TIMING APPROACHING': '#009845', 'PREPARE': '#009845' };
  const SIGNALS = [];
  let sn = 0;
  for (let round = 0; SIGNALS.length < 56; round++) {
    THEMES.forEach((t, ti) => {
      if (SIGNALS.length >= 56 || round >= t.regions.length) return;
      const region = t.regions[round];
      const status = F_STATUS[(ti + round * 2) % 7];
      const spark = Array.from({ length: 8 }, (_, k) => 20 + Math.round(seed(sn * 31 + k) * 80));
      SIGNALS.push({
        provenance: 'DEMO_SCENARIO',
        id: 'IT-SIG-' + String(++sn).padStart(3, '0'), issue: t.issue, crop: t.crop, region, cat: t.cat, category: CAT[t.cat],
        status, color: F_COLOR[status], sourceType: F_SOURCES[(ti * 3 + round) % F_SOURCES.length],
        lastObserved: ago(1 + Math.floor(seed(sn * 5) * 20)), lastDays: 1 + Math.floor(seed(sn * 5) * 20),
        movement: pick(['Publication activity rising', 'New regional mention', 'Field reports increasing', 'Regulatory reference published', 'Technical article series', 'Producer bulletin update', 'Competitor content observed'], sn * 3),
        why: `${t.crop} is relevant in ${region}; ${t.issue.toLowerCase()} pressure here would ${t.product ? 'connect to a registered ADAMA position' : 'require a portfolio check'}.`,
        product: t.product, portfolio: t.product ? 'Potential portfolio link · ' + t.product : 'Portfolio check needed',
        spark, science: t.science, sparkMax: 100
      });
    });
  }

  // ---- Science --------------------------------------------------------------
  const INSTITUTIONS = ['CREA – Difesa e Certificazione', 'CNR – IPSP', 'CNR-ISPA', 'Università Cattolica del Sacro Cuore · Piacenza', 'Università di Verona', 'Università di Torino · DISAFA', 'Università di Padova', 'Università di Bologna', 'Università di Firenze', 'Università di Udine', 'Università di Bari Aldo Moro', 'Università Cattolica – Piacenza', 'Fondazione Edmund Mach', 'Università di Torino', 'Università di Palermo', 'Università di Milano'];
  const SCI_THEMES = [
    { id: 'grapevine-phytoplasma', title: 'Grapevine phytoplasma', crop: 'Grapevine', issue: 'Flavescenza Dorata', works: 135, trend: 'Rising', cat: 'pest', note: 'Topic-linked works indexed in the Italy science layer', cases: ['IT-OPP-001', 'IT-OPP-009'] },
    { id: 'scaphoideus', title: 'Scaphoideus titanus', crop: 'Grapevine', issue: 'Flavescenza Dorata vector', works: 66, trend: 'Rising', cat: 'pest', note: 'Vector biology, dispersal and control timing', cases: ['IT-OPP-001', 'IT-OPP-009'] },
    { id: 'maize-borer', title: 'Maize borer / Diabrotica', crop: 'Maize', issue: 'European Corn Borer · Diabrotica', works: 30, trend: 'Stable', cat: 'pest', note: 'Flight models, larval damage, mycotoxin interaction', cases: ['IT-OPP-002', 'IT-OPP-004', 'IT-OPP-011', 'IT-OPP-022'] },
    { id: 'olive-bactrocera', title: 'Olive Bactrocera', crop: 'Olive', issue: 'Olive Fruit Fly', works: 70, trend: 'Rising', cat: 'pest', note: 'Population dynamics, thresholds, climate effect', cases: ['IT-OPP-006', 'IT-OPP-010', 'IT-OPP-012'] },
    { id: 'durum-fusarium', title: 'Durum wheat Fusarium', crop: 'Durum Wheat', issue: 'Fusarium Head Blight', works: 78, trend: 'Rising', cat: 'disease', note: 'Mycotoxin risk, flowering timing, fungicide efficacy', cases: ['IT-OPP-003', 'IT-OPP-016'] },
    { id: 'cercospora-dss', title: 'Cercospora decision support', crop: 'Sugar Beet', issue: 'Cercospora', works: 18, trend: 'Stable', cat: 'disease', note: 'DSS models and regional alert systems', cases: ['IT-OPP-007', 'IT-OPP-008'] },
    { id: 'maize-mycotoxins', title: 'Maize mycotoxins', crop: 'Maize', issue: 'Mycotoxin Risk · Fusarium · Aspergillus', works: 41, trend: 'Rising', cat: 'disease', note: 'Aflatoxin / fumonisin prediction, climate, seasonal forecasting (UCSC Piacenza · CNR-ISPA)', cases: ['IT-OPP-022', 'IT-OPP-003'] },
    { id: 'xylella', title: 'Xylella fastidiosa', crop: 'Olive', issue: 'Xylella fastidiosa', works: 52, trend: 'Rising', cat: 'disease', note: 'Early diagnosis, resistant varieties, vector control (CREA projects · CNR-IPSP Bari · 5th European Conference, Mola di Bari)', cases: ['IT-OPP-006'] },
    { id: 'ipm', title: 'Integrated pest management', crop: 'All crops', issue: 'Low / zero-pesticide protection', works: 19, trend: 'Emerging', cat: 'disease', note: 'CREA SUPPORT project (Aug 2026) · policy and adoption · no ADAMA product connection asserted', cases: [] },
    { id: 'resistance', title: 'Insecticide resistance monitoring', crop: 'Grapevine · Maize', issue: 'Pyrethroid / diamide sensitivity', works: 24, trend: 'Emerging', cat: 'pest', note: 'Resistance management informs label positioning', cases: ['IT-OPP-001', 'IT-OPP-011'] }
  ].map(t => ({ ...t, category: CAT[t.cat], caseObjs: t.cases.map(id => CASES.find(c => c.id === id)), trendColor: t.trend === 'Rising' ? '#009845' : '#B1A9A7' }));
  const STUDY = ['Field trial', 'Population model', 'Review', 'Regional survey', 'Laboratory study', 'Decision-support evaluation'];
  const REAL_RECORDS = REAL.SCIENCE.map(r => { const t = SCI_THEMES.find(x => x.id === r.themeId) || SCI_THEMES[0]; const cs = t.caseObjs[0] || CASES[5]; return { id: r.id, theme: t, themeId: t.id, year: r.date, institution: r.org, study: r.kind, crop: r.crop, issue: r.issue, category: t.category, descriptor: r.title, why: r.what, related: cs, location: r.region, note: r.provenance === 'REAL_FACT' ? 'Real record · ' + r.kind : 'Real theme · titles retrieved from source at production', real: true, provenance: r.provenance }; });
  const RECORDS = REAL_RECORDS.concat(Array.from({ length: 24 }, (_, i) => {
    const t = SCI_THEMES[i % SCI_THEMES.length]; const year = 2022 + (i % 5);
    return { id: 'IT-SCI-' + String(i + 1).padStart(3, '0'), theme: t, themeId: t.id, year, institution: INSTITUTIONS[(i * 5) % INSTITUTIONS.length], study: STUDY[i % STUDY.length], crop: t.crop, issue: t.issue, category: t.category,
      descriptor: `${STUDY[i % STUDY.length]} · ${t.title} · ${year}`, why: `Connected because it informs ${t.issue.toLowerCase()} timing or pressure for ${t.crop.toLowerCase()} in Italy.`, related: t.caseObjs[i % Math.max(1, t.caseObjs.length)] || CASES[0], location: seed(i * 9) > 0.55 && t.caseObjs.length ? t.caseObjs[i % t.caseObjs.length].region : 'Study location not stated', note: 'Anonymised topic record · title and authors in source record', real: false, provenance: 'REAL_DERIVED · aggregate' };
  }));
  SCI_THEMES.forEach(t => { t.records = RECORDS.filter(r => r.themeId === t.id); t.institutions = [...new Set(t.records.map(r => r.institution))]; });
  const INST_OBJS = INSTITUTIONS.slice(0, 12).map((name, k) => ({ name, records: RECORDS.filter(r => r.institution === name).length, themes: [...new Set(RECORDS.filter(r => r.institution === name).map(r => r.theme.title))], type: name.startsWith('CREA') || name.startsWith('CNR') ? 'National research body' : name.startsWith('Fondazione') ? 'Research foundation' : 'University' }));

  // ---- People (source directory) -------------------------------------------
  const ROLES = ['Researcher', 'Agronomist', 'Technical advisor', 'Influencer / creator', 'Field expert', 'Producer voice', 'Institutional expert'];
  const ROLE_CAT = { 'Researcher': 'RESEARCHERS', 'Agronomist': 'AGRONOMISTS / ENGINEERS', 'Technical advisor': 'TECHNICAL ADVISORS', 'Influencer / creator': 'INFLUENCERS / CREATORS', 'Field expert': 'FIELD EXPERTS', 'Producer voice': 'PRODUCER / FARM VOICES', 'Institutional expert': 'INSTITUTIONAL EXPERTS' };
  const ORGS_BY_ROLE = { 'Researcher': INSTITUTIONS, 'Agronomist': ['Independent · Veneto', 'Cooperative technical service', 'Consorzio Agrario', 'Independent · Puglia'], 'Technical advisor': ['Regional technical network', 'Distributor technical team', 'Consorzio Fitosanitario Piacenza'], 'Influencer / creator': ['YouTube · farm channel', 'Instagram · agronomy', 'LinkedIn · agri-tech', 'Podcast · agricoltura'], 'Field expert': ['ERSA FVG', 'LaMMA', 'Regione Veneto · U.O. Fitosanitario', 'Servizio Fitosanitario Lombardia'], 'Producer voice': ['Co.Pro.B.', 'Assoproli', 'Coldiretti Puglia', 'Confagricoltura Veneto'], 'Institutional expert': ['CREA', 'Regione Emilia-Romagna', 'Provincia Autonoma di Trento', 'Regione Sicilia'] };
  const PLATFORMS = { 'Researcher': 'Publications · OpenAlex', 'Agronomist': 'LinkedIn · field notes', 'Technical advisor': 'Technical bulletins', 'Influencer / creator': 'YouTube · Instagram', 'Field expert': 'Regional bulletin', 'Producer voice': 'Association communication', 'Institutional expert': 'Official communication' };
  const REAL_PEOPLE = REAL.RESEARCHERS.map((r, i) => { const theme = SCI_THEMES.find(t => t.id === r.themeId) || SCI_THEMES[0]; return { id: r.id, initials: r.name.split(' ').map(w => w[0]).join('').slice(0, 2), role: 'Researcher', roleCat: 'RESEARCHERS', org: r.org, platform: 'Publications · institutional repository / OpenAlex', region: 'Affiliation · not a field location', crops: [r.crop], issues: [r.issue], recentTopic: r.focus, lastDays: 20 + i * 3, last: ago(20 + i * 3), related: CASES.filter(x => x.crop === r.crop).slice(0, 3), signals: SIGNALS.filter(s => s.crop === r.crop).slice(0, 3), theme, contentCount: null, label: r.name, real: true, provenance: 'REAL_FACT', color: '#978B87', note: r.note }; });
  const PEOPLE = REAL_PEOPLE.concat(Array.from({ length: 18 }, (_, i0) => { const i = i0 + 12;
    const role = ROLES[1 + (i % 6)]; const c = CASES[(i * 7) % 24]; const theme = SCI_THEMES[i % SCI_THEMES.length];
    const orgs = ORGS_BY_ROLE[role]; const org = orgs[i % orgs.length];
    const related = CASES.filter(x => x.crop === c.crop).slice(0, 3);
    return { id: 'P-' + String(i + 1).padStart(2, '0'), initials: role[0] + (i + 1), role, roleCat: ROLE_CAT[role], org, platform: PLATFORMS[role], region: role === 'Researcher' ? 'Affiliation · field location varies' : c.region, crops: role === 'Researcher' ? [theme.crop] : [c.crop], issues: role === 'Researcher' ? [theme.issue] : [c.issue], recentTopic: role === 'Researcher' ? theme.title + ' · ' + theme.note.toLowerCase() : `${c.issue} in ${c.region} · ${c.signal.toLowerCase()}`, lastDays: 1 + Math.floor(seed(i * 13) * 25), last: ago(1 + Math.floor(seed(i * 13) * 25)), related, signals: SIGNALS.filter(s => s.crop === (role === 'Researcher' ? theme.crop : c.crop)).slice(0, 3), theme: role === 'Researcher' ? theme : null, contentCount: 3 + Math.floor(seed(i * 29) * 14), label: `Demo profile · ${role}`, real: false, provenance: 'SYNTHETIC_DEMO', color: '#978B87' };
  }));

  // ---- Competitor Watch · market activity universe (72 items) ----------------
  // Companies are real; products named are real competitor brands; platform routes are realistically observable; events are real.
  // Participation in future real events is never shown as confirmed unless an official catalogue supports it.
  const CO_META = {
    'BASF': { label: 'BASF Agricultural Solutions Italia', color: '#978B87', products: ['Belanty', 'Cabrio Top', 'Revysol'], crops: ['Grapevine', 'Maize', 'Wheat', 'Durum Wheat'], themes: ['Maize protection', 'Disease control', 'Grapevine protection', 'Weed management'], confidence: 'Confirmed in Italy Meta source work' },
    'Bayer': { label: 'Bayer Crop Science Italia', color: '#978B87', products: ['Luna Experience', 'Movento'], crops: ['Grapevine', 'Maize', 'Olive', 'Apple'], themes: ['Regenerative viticulture', 'Sustainability', 'Fruit protection'], confidence: 'Confirmed in Italy Meta source work' },
    'Corteva': { label: 'Corteva Agriscience Italia', color: '#978B87', products: ['Pioneer', 'Zorvec'], crops: ['Maize', 'Grapevine', 'Wheat'], themes: ['Maize seed & protection', 'Downy mildew', 'Agronomy services'], confidence: 'Confirmed in Italy Meta source work' },
    'FMC': { label: 'FMC Italia', color: '#978B87', products: ['Exirel', 'Coragen', 'ARC farm intelligence'], crops: ['Grapevine', 'Olive', 'Maize', 'Tomato'], themes: ['Precision agriculture', 'Insect control', 'Real-time field monitoring', 'Crop quality'], confidence: 'Confirmed in Italy Meta source work' },
    'Syngenta': { label: 'Syngenta Italia', color: '#978B87', products: ['Ampligo', 'Amistar', 'Elatus Era'], crops: ['Grapevine', 'Maize', 'Wheat', 'Durum Wheat'], themes: ['Vine protection', 'Cereal fungicides', 'Technical agronomy video'], confidence: 'Confirmed in Italy Meta source work' },
    'UPL': { label: 'UPL Italia', color: '#978B87', products: ['Kocide 2000'], crops: ['Grapevine', 'Olive', 'Tomato'], themes: ['Copper & biosolutions', 'Viticulture', 'Olive protection'], confidence: 'Confirmed in Italy Meta source work' }
  };
  // COMPANIES declared above (same six).
  const EVENTS = [
    { id: 'EV-1', name: 'EIMA International 2026', city: 'Bologna', region: 'Emilia-Romagna', dates: '10–14 Nov 2026', startDays: 70, sector: 'Agricultural machinery & technology', crops: ['Maize', 'Precision agriculture', 'Crop technology'], exhibitorStatus: 'Official exhibitor catalogue published · 1,500+ exhibitors listed', participation: { BASF: 'MONITORING', Bayer: 'MONITORING', Corteva: 'NOT YET CONFIRMED', FMC: 'MONITORING', Syngenta: 'NOT YET CONFIRMED', UPL: 'MONITORING' }, real: true, program: 'Programme published on official site · technical sessions on precision agriculture', site: 'eima.it' },
    { id: 'EV-2', name: 'Fieragricola 2026', city: 'Verona', region: 'Veneto', dates: '2026 edition completed · next edition 2028', startDays: -200, sector: 'Agriculture & technology', crops: ['All crops'], exhibitorStatus: '2026 official material available', participation: { Corteva: 'HISTORICAL PARTICIPANT · 2026', Syngenta: 'HISTORICAL PARTICIPANT · 2026', BASF: 'NOT YET KNOWN · 2028', Bayer: 'NOT YET KNOWN · 2028', FMC: 'NOT YET KNOWN · 2028', UPL: 'NOT YET KNOWN · 2028' }, real: true, program: 'Historical programme · useful for pattern analysis only', site: 'fieragricola.it' },
    { id: 'EV-3', name: 'Enovitis in Campo 2026', city: 'Greve in Chianti', region: 'Toscana', dates: '17–18 Jun 2026 · completed', startDays: -76, sector: 'Viticulture & olive technology', crops: ['Grapevine', 'Olive'], exhibitorStatus: 'Official 2026 exhibitor catalogue · 130+ exhibitors', participation: { Syngenta: 'CONFIRMED EXHIBITOR · 2026 catalogue', UPL: 'CONFIRMED EXHIBITOR · 2026 catalogue', BASF: 'NOT LISTED', Bayer: 'NOT LISTED', Corteva: 'NOT LISTED', FMC: 'NOT LISTED' }, real: true, program: 'Field demonstrations in vineyard · technical talks', site: 'enovitisincampo.it' },
    { id: 'EV-4', name: 'Macfrut 2027', city: 'Rimini', region: 'Emilia-Romagna', dates: '20–22 Apr 2027', startDays: 231, sector: 'Fruit & vegetable professional show', crops: ['Tomato', 'Apple', 'Grapevine (table)'], exhibitorStatus: 'EXHIBITOR LIST NOT YET PUBLISHED', participation: { BASF: 'NOT YET KNOWN', Bayer: 'NOT YET KNOWN', Corteva: 'NOT YET KNOWN', FMC: 'NOT YET KNOWN', Syngenta: 'NOT YET KNOWN', UPL: 'NOT YET KNOWN' }, real: true, program: 'Not yet published', site: 'macfrut.com' },
    { id: 'EV-5', name: 'Agrilevante 2027', city: 'Bari', region: 'Puglia', dates: '7–10 Oct 2027', startDays: 401, sector: 'Agricultural technology · southern Italy', crops: ['Olive', 'Durum Wheat', 'Grapevine'], exhibitorStatus: 'EXHIBITOR LIST NOT YET PUBLISHED', participation: { BASF: 'NOT YET KNOWN', Bayer: 'NOT YET KNOWN', Corteva: 'NOT YET KNOWN', FMC: 'NOT YET KNOWN', Syngenta: 'NOT YET KNOWN', UPL: 'NOT YET KNOWN' }, real: true, program: 'Not yet published', site: 'agrilevante.eu' }
  ];
  Object.entries(REAL.EVENT_EXTRA).forEach(([id, x]) => { const e = EVENTS.find(v => v.id === id); if (e) Object.assign(e, x); });
  REAL.EVENTS_EXTRA.forEach(e => EVENTS.push(e));
  EVENTS.forEach(e => { e.countdown = e.startDays > 0 ? e.startDays + ' days' : 'Completed'; e.bucket = e.startDays < 0 ? 'COMPLETED' : e.startDays <= 30 ? '30 DAYS' : e.startDays <= 90 ? '90 DAYS' : e.startDays <= 180 ? '6 MONTHS' : 'NEXT YEAR'; e.confirmed = Object.entries(e.participation).filter(([k, v]) => v.startsWith('CONFIRMED')).map(([k]) => k); e.historical = Object.entries(e.participation).filter(([k, v]) => v.startsWith('HISTORICAL')).map(([k]) => k); e.partRows = Object.entries(e.participation).map(([k, v]) => ({ company: k, state: v, color: v.startsWith('CONFIRMED') ? '#009845' : v.startsWith('HISTORICAL') ? '#B1A9A7' : v.startsWith('MONITORING') ? '#B1A9A7' : '#6E6663' })); });
  const ATYPES = ['PAID', 'ORGANIC', 'VIDEO', 'PEOPLE', 'EVENT', 'PRODUCT / PORTFOLIO'];
  const ATYPE_COLOR = { 'PAID': '#B1A9A7', 'ORGANIC': '#B1A9A7', 'VIDEO': '#B1A9A7', 'PEOPLE': '#B1A9A7', 'EVENT': '#B1A9A7', 'PRODUCT / PORTFOLIO': '#B1A9A7' };
  const PLATFORM_OF = { 'PAID': ['Meta · Facebook', 'Meta · Instagram'], 'ORGANIC': ['Instagram', 'Facebook', 'LinkedIn', 'Company website'], 'VIDEO': ['YouTube'], 'PEOPLE': ['Instagram', 'YouTube', 'LinkedIn'], 'EVENT': ['Official event site', 'Exhibitor catalogue', 'LinkedIn'], 'PRODUCT / PORTFOLIO': ['Company website', 'Banca Dati Fitosanitari'] };
  const CREATIVE_PALETTE = ['#1E3A2F', '#2B2A45', '#3B2D1F', '#1F3346', '#402431', '#2F3A1F'];
  const DIST = [].concat(Array(13).fill('PAID'), Array(11).fill('ORGANIC'), Array(10).fill('VIDEO'), Array(8).fill('PEOPLE'), Array(5).fill('EVENT'), Array(6).fill('PRODUCT / PORTFOLIO'));
  const REAL_ACTS = REAL.COMPETITOR_REAL.map((r, i) => { const m = CO_META[r.company]; const cs = CASES.filter(c => c.crop === r.crop); const c = cs[i % Math.max(1, cs.length)] || CASES[0]; const ev = r.eventId ? EVENTS.find(e => e.id === r.eventId) : null; const days = ev ? Math.max(1, -ev.startDays) : 2 + (i * 5) % 40; return { id: 'IT-REAL-' + String(i + 1).padStart(3, '0'), company: r.company, companyLabel: m.label, companyColor: m.color, type: r.kind, kind: r.kind, color: ATYPE_COLOR[r.kind], platform: r.platform, channel: r.platform, product: r.product, crop: r.crop, issue: r.issue,
      region: 'Italy', country: 'REACHED_IN_ITALY', isDemo: false, provenance: 'REAL_OBSERVATION', days, when: ago(days), date: fmt(addDays(TODAY, -days)), dayLabel: days < 7 ? days + ' DAYS AGO' : days < 30 ? Math.round(days / 7) + ' WEEK' + (days >= 14 ? 'S' : '') + ' AGO' : 'OLDER', headline: r.headline, observed: r.headline, duration: null, topics: [], transcript: false, active: r.kind === 'PAID' ? 'OBSERVED' : null, person: null, personId: null, personRole: null, relationship: null, event: ev ? ev.name : null, eventId: r.eventId || null, participation: r.participation || null, creativeBg: CREATIVE_PALETTE[i % 6], provenance: r.provenance, newly: days <= 7 ? 'NEWLY OBSERVED' : null, caseId: c.id, caseTitle: `${c.issue} · ${c.crop} · ${c.region}`, brand: r.product ? 'Brand captured' : 'Brand not identified', real: true }; });
  /* §11/§12 · Provenance is a first-class field. A synthetic record may never say
     OBSERVED, ACTIVE, NEWLY OBSERVED, or offer VIEW AD. Real records carry their
     country semantics; synthetic ones carry a visible demonstration badge. */
  const ACTIVITIES = REAL_ACTS.concat(DIST.map((type, i) => {
    const co = COMPANIES[(i * 5) % 6]; const m = CO_META[co];
    const crop = m.crops[(i * 3) % m.crops.length];
    const cs = CASES.filter(c => c.crop === crop); const c = cs[(i * 7) % Math.max(1, cs.length)] || CASES[(i * 5) % 24];
    const product = m.products[(i * 2) % m.products.length];
    const platform = PLATFORM_OF[type][(i * 3) % PLATFORM_OF[type].length];
    let days = 1 + Math.floor(seed(i * 17 + 5) * 58); if (i % 9 === 0) days = i % 18 === 0 ? 0 : 1;
    const ev = type === 'EVENT' ? EVENTS[[0, 2, 1, 0, 3, 2, 4, 0][i % 8]] : null;
    const person = type === 'PEOPLE' ? PEOPLE.filter(p => p.role !== 'Researcher')[(i * 5) % 18] : null;
    const headline = type === 'PAID' ? `${product} — ${c.issue.toLowerCase()} protection in ${crop.toLowerCase()}` : type === 'ORGANIC' ? [`${crop} season update · ${c.issue.toLowerCase()}`, `Regenerative ${crop.toLowerCase()} · technical story`, `Field day recap · ${crop.toLowerCase()}`, `Product spotlight · ${product}`][i % 4] : type === 'VIDEO' ? [`Precision in ${crop.toLowerCase()} protection`, `Technical video · ${c.issue.toLowerCase()} timing`, `Field trial walkthrough · ${crop.toLowerCase()}`, `Agronomist Q&A · ${crop.toLowerCase()} season`][i % 4] : type === 'PEOPLE' ? `Mentioned ${product} in a ${crop.toLowerCase()} ${c.cat === 'pest' ? 'pest' : 'disease'}-control discussion` : type === 'EVENT' ? (ev.startDays < 0 ? `${ev.name} · participation recorded in official material` : `${ev.name} · exhibitor list monitored`) : [`Product page update · ${product} · ${crop.toLowerCase()} use`, `Authorisation reference observed · ${product}`, `Label communication · ${product}`][i % 3];
    const duration = type === 'VIDEO' ? `${4 + (i % 9)}:${String(10 + (i * 7) % 50).padStart(2, '0')}` : null;
    const topics = type === 'VIDEO' ? ['precision', 'treatment timing', 'real-time monitoring', 'resistance management', 'crop quality'].filter((_, k) => (i + k) % 2 === 0) : [];
    const partState = ev ? ev.participation[co] : null;
    return { id: 'IT-ACT-' + String(i + 1).padStart(3, '0'), company: co, companyLabel: m.label, companyColor: m.color, type, kind: type, color: ATYPE_COLOR[type], platform, channel: platform, product: type === 'EVENT' ? null : product, crop, issue: type === 'EVENT' ? ev.sector : c.issue,
      /* §11 · A generated record never claims an observation nor an Italy reach. */
      region: 'DEMO', country: 'DEMO_RECORD', isDemo: true, provenance: 'SYNTHETIC_DEMO', days, when: days === 0 ? 'today' : ago(days), date: fmt(addDays(TODAY, -days)), dayLabel: days === 0 ? 'TODAY' : days === 1 ? 'YESTERDAY' : days < 7 ? days + ' DAYS AGO' : days < 30 ? Math.round(days / 7) + ' WEEK' + (days >= 14 ? 'S' : '') + ' AGO' : 'OLDER',
      headline, observed: headline, duration, topics, transcript: type === 'VIDEO' ? (i % 3 !== 0) : false, active: null, canViewAd: false,
      person: person ? person.label : null, personId: person ? person.id : null, personRole: person ? person.role : null, relationship: type === 'PEOPLE' ? 'UNKNOWN RELATIONSHIP' : null,
      event: ev ? ev.name : null, eventId: ev ? ev.id : null, participation: partState,
      creativeBg: CREATIVE_PALETTE[i % 6], provenance: type === 'PAID' && i % 4 === 0 ? 'REAL · Meta EAME dataset pattern' : 'SYNTHETIC_DEMO_BASED_ON_REAL_COMPETITOR_PATTERN', newly: days <= 7 ? (i % 3 === 0 ? 'NEWLY OBSERVED' : 'NEWLY PUBLISHED') : null,
      caseId: c.id, caseTitle: `${c.issue} · ${c.crop} · ${c.region}`, brand: 'Brand captured', real: false };
  })).sort((a, b) => a.days - b.days);
  const COMPANY_OBJS = COMPANIES.map((name, k) => {
    const m = CO_META[name]; const acts = ACTIVITIES.filter(a => a.company === name).sort((a, b) => a.days - b.days);
    const uniq = (arr) => [...new Set(arr)]; const byType = (t) => acts.filter(a => a.type === t).length;
    return { name, label: m.label, color: m.color, id: 'CO-' + (k + 1), count: acts.length, crops: uniq(acts.map(a => a.crop)), issues: uniq(acts.filter(a => a.type !== 'EVENT').map(a => a.issue)), products: m.products, themes: m.themes, lastDays: acts[0] ? acts[0].days : 0, last: acts[0] ? acts[0].when : '—', recent30: acts.filter(a => a.days <= 30).length, recent7: acts.filter(a => a.days <= 7).length, activities: acts, cases: uniq(acts.map(a => a.caseId)).map(id => CASES.find(c => c.id === id)), brands: m.products.length, confidence: m.confidence, counts: { paid: byType('PAID'), organic: byType('ORGANIC'), video: byType('VIDEO'), people: byType('PEOPLE'), events: byType('EVENT'), product: byType('PRODUCT / PORTFOLIO') } };
  });
  const CPRODUCTS = [];
  COMPANIES.forEach(co => CO_META[co].products.forEach(p => { const acts = ACTIVITIES.filter(a => a.product === p); CPRODUCTS.push({ name: p, company: co, color: CO_META[co].color, count: acts.length, activities: acts, crops: [...new Set(acts.map(a => a.crop))], issues: [...new Set(acts.map(a => a.issue))], first: acts.length ? acts[acts.length - 1].date : '—', last: acts.length ? acts[0].when : '—', people: acts.filter(a => a.type === 'PEOPLE').length, paid: acts.filter(a => a.type === 'PAID').length, cases: [...new Set(acts.map(a => a.caseId))].map(id => CASES.find(c => c.id === id)).slice(0, 4) }); }));
  const CROP_COLS = ['Grapevine', 'Maize', 'Wheat', 'Olive', 'Tomato', 'Apple'];
  const MATRIX = COMPANIES.map(co => ({ company: co, color: CO_META[co].color, cells: CROP_COLS.map(cr => ({ crop: cr, n: ACTIVITIES.filter(a => a.company === co && (a.crop === cr || (cr === 'Wheat' && a.crop === 'Durum Wheat'))).length })) }));
  const ISSUE_ROWS = [...new Set(CASES.map(c => c.issue))].map(issue => { const acts = ACTIVITIES.filter(a => a.issue === issue); const cs = CASES.filter(c => c.issue === issue); return { issue, count: acts.length, paid: acts.filter(a => a.type === 'PAID').length, companies: [...new Set(acts.map(a => a.company))], adama: [...new Set(cs.flatMap(c => c.products))].slice(0, 3), caseId: cs[0] ? cs[0].id : null }; }).filter(r => r.count > 0).sort((a, b) => b.count - a.count);
  const WHAT_CHANGED = ATYPES.map(t => ({ type: t, color: ATYPE_COLOR[t], n: ACTIVITIES.filter(a => a.type === t && a.days <= 7).length, label: { 'PAID': 'new paid creatives observed', 'ORGANIC': 'organic posts observed', 'VIDEO': 'new videos observed', 'PEOPLE': 'people mentions observed', 'EVENT': 'event records updated', 'PRODUCT / PORTFOLIO': 'product / portfolio movements' }[t] }));

  // ---- Sources (organizations) ---------------------------------------------
  const S = (name, group, type, what, freq, cov, topics, health) => ({ name, group, type, what, freq, cov, topics, health });
  const SOURCES = [
    S('Regione Veneto · U.O. Fitosanitario', 'GOVERNMENT & OFFICIAL', 'Regional phytosanitary service', 'Bulletins, compulsory-control decrees, trap network', 'Weekly in season', 'Veneto', ['Grapevine', 'Maize', 'Sugar Beet'], 'Available'),
    S('ERSA Friuli-Venezia Giulia', 'GOVERNMENT & OFFICIAL', 'Regional agency', 'Maize bulletin, flight and oviposition monitoring', 'Weekly in season', 'Friuli-Venezia Giulia', ['Maize', 'Grapevine'], 'Available'),
    S('Servizio Fitosanitario Lombardia', 'GOVERNMENT & OFFICIAL', 'Regional phytosanitary service', 'Bulletins, Diabrotica and Popillia monitoring', 'Weekly in season', 'Lombardia', ['Maize', 'Grapevine'], 'Available'),
    S('Servizio Fitosanitario Emilia-Romagna', 'GOVERNMENT & OFFICIAL', 'Regional phytosanitary service', 'Provincial bulletins, DSS references', 'Weekly in season', 'Emilia-Romagna', ['Wheat', 'Sugar Beet', 'Tomato'], 'Available'),
    S('Servizio Fitosanitario Piemonte', 'GOVERNMENT & OFFICIAL', 'Regional phytosanitary service', 'Flavescenza compulsory-control area, bulletins', 'Weekly in season', 'Piemonte', ['Grapevine', 'Maize'], 'Intermittent'),
    S('Regione Toscana · Servizio Fitosanitario', 'GOVERNMENT & OFFICIAL', 'Regional phytosanitary service', 'Olive and cereal bulletins', 'Bi-weekly', 'Toscana', ['Olive', 'Durum Wheat'], 'Available'),
    S('Osservatorio Fitosanitario Puglia', 'GOVERNMENT & OFFICIAL', 'Regional phytosanitary service', 'Olive, cereal and Xylella communication', 'Bi-weekly', 'Puglia', ['Olive', 'Durum Wheat', 'Grapevine'], 'Intermittent'),
    S('Servizio Fitosanitario Sicilia', 'GOVERNMENT & OFFICIAL', 'Regional phytosanitary service', 'Regional bulletins', 'Bi-weekly', 'Sicilia', ['Olive', 'Grapevine', 'Durum Wheat'], 'Alternative route needed'),
    S('Consorzio LaMMA', 'GOVERNMENT & OFFICIAL', 'Agro-meteorological consortium', 'Weather and agro-climatic context', 'Daily', 'Toscana', ['All crops'], 'Available'),
    S('Ministero della Salute · Banca Dati Fitosanitari', 'GOVERNMENT & OFFICIAL', 'Regulatory authority', 'Product authorisations, labels, status changes', 'Event-driven', 'Italy', ['All crops'], 'Available'),
    S('ISTAT', 'GOVERNMENT & OFFICIAL', 'National statistics', 'Regional crop area and production', 'Annual', 'Italy', ['All crops'], 'Available'),
    S('Eurostat', 'GOVERNMENT & OFFICIAL', 'European statistics', 'Crop statistics, cross-check', 'Annual', 'EU', ['All crops'], 'Available'),
    S('CREA', 'RESEARCH & SCIENCE', 'National research body', 'Research outputs, plant protection science', 'Monthly', 'Italy', ['Grapevine', 'Wheat', 'Olive'], 'Available'),
    S('CNR – IPSP', 'RESEARCH & SCIENCE', 'National research institute', 'Plant protection research', 'Monthly', 'Italy', ['Grapevine', 'Olive'], 'Available'),
    S('OpenAlex', 'RESEARCH & SCIENCE', 'Scientific database', 'Topic-linked publications and author discovery', 'Continuous', 'Global · Italy filter', ['All topics'], 'Available'),
    S('Fondazione Edmund Mach', 'RESEARCH & SCIENCE', 'Research foundation', 'Apple and grapevine research, advisory', 'Monthly', 'Trentino-Alto Adige', ['Apple', 'Grapevine'], 'Available'),
    S('Italian universities (agri faculties)', 'RESEARCH & SCIENCE', 'University network', 'Research outputs across 9 institutions', 'Monthly', 'Italy', ['All crops'], 'Available'),
    S('Co.Pro.B.', 'FIELD & PRODUCER ORGANIZATIONS', 'Producer cooperative', 'Cercospora DSS, beet campaign updates', 'Weekly in season', 'Veneto · Emilia-Romagna', ['Sugar Beet'], 'Available'),
    S('Assoproli', 'FIELD & PRODUCER ORGANIZATIONS', 'Producer organisation', 'Olive fruit fly monitoring, grower updates', 'Weekly in season', 'Puglia', ['Olive'], 'Available'),
    S('Consorzio Fitosanitario Piacenza', 'FIELD & PRODUCER ORGANIZATIONS', 'Technical network', 'Cereal and tomato technical bulletins', 'Weekly in season', 'Emilia-Romagna', ['Wheat', 'Tomato'], 'Available'),
    S('Confagricoltura', 'FIELD & PRODUCER ORGANIZATIONS', 'Farmer association', 'Positions, campaign communication', 'Weekly', 'Italy', ['All crops'], 'Available'),
    S('Coldiretti', 'FIELD & PRODUCER ORGANIZATIONS', 'Farmer association', 'Positions, regional campaign news', 'Weekly', 'Italy', ['All crops'], 'Available'),
    S('AgroNotizie', 'NEWS & TRADE MEDIA', 'Technical media', 'Technical articles, product news, competitor content', 'Daily', 'Italy', ['All crops'], 'Available'),
    S('Terra e Vita', 'NEWS & TRADE MEDIA', 'Technical media', 'Agronomic articles, seasonal analysis', 'Daily', 'Italy', ['All crops'], 'Available'),
    S("L'Informatore Agrario", 'NEWS & TRADE MEDIA', 'Technical media', 'Technical dossiers, trials', 'Weekly', 'Italy', ['All crops'], 'Intermittent'),
    S('Competitor technical sites', 'COMPANIES & MARKET', 'Company channels', 'Technical and product communication of 8 companies', 'Continuous', 'Italy', ['All crops'], 'Available'),
    S('Public ad library', 'COMPANIES & MARKET', 'Advertising repository', 'Paid creative observed by advertiser', 'Continuous', 'Italy', ['All crops'], 'Intermittent'),
    S('Company social channels', 'COMPANIES & MARKET', 'Company channels', 'Public content and campaign timing', 'Continuous', 'Italy', ['All crops'], 'Available'),
    S('YouTube · company & creator channels', 'COMPANIES & MARKET', 'Video platform', 'New videos, titles, descriptions, dates, transcripts where available', 'Continuous', 'Italy', ['All crops'], 'Available'),
    S('EIMA International', 'EVENTS & TRADE FAIRS', 'Trade fair · Bologna', 'Exhibitor catalogue, programme, speakers, event social activity', 'Per edition · Nov 2026', 'Emilia-Romagna', ['Maize', 'Precision agriculture'], 'Available'),
    S('Fieragricola', 'EVENTS & TRADE FAIRS', 'Trade fair · Verona', 'Historical exhibitor material · next edition 2028', 'Per edition', 'Veneto', ['All crops'], 'Available'),
    S('Enovitis in Campo', 'EVENTS & TRADE FAIRS', 'Field event · Greve in Chianti', '2026 exhibitor catalogue, field demonstrations', 'Per edition · Jun', 'Toscana', ['Grapevine', 'Olive'], 'Available'),
    S('Macfrut', 'EVENTS & TRADE FAIRS', 'Trade fair · Rimini', 'Exhibitor catalogue when published · Apr 2027', 'Per edition', 'Emilia-Romagna', ['Tomato', 'Apple', 'Grapevine'], 'Intermittent'),
    S('Agrilevante', 'EVENTS & TRADE FAIRS', 'Trade fair · Bari', 'Exhibitor catalogue when published · Oct 2027', 'Per edition', 'Puglia', ['Olive', 'Durum Wheat'], 'Intermittent')
  ].concat(REAL.SOURCES_EXTRA.map(a => S(...a))).map((s, k) => {
    if (REAL.MEDIA_RECLASS[s.name]) s.group = REAL.MEDIA_RECLASS[s.name];
    s.id = 'SRC-' + String(k + 1).padStart(2, '0');
    s.lastDays = 1 + Math.floor(seed(k * 19) * 12); s.last = ago(s.lastDays);
    s.related = CASES.filter(c => (s.cov === 'Italy' || s.cov === 'EU' || s.cov.includes(c.region)) && (s.topics.includes('All crops') || s.topics.includes(c.crop))).length;
    s.healthColor = s.health === 'Available' ? '#009845' : '#B1A9A7';
    s.real = true; s.provenance = 'REAL_SOURCE';
    s.groupColor = { 'GOVERNMENT & OFFICIAL': '#B1A9A7', 'RESEARCH & SCIENCE': '#B1A9A7', 'FIELD & PRODUCER ORGANIZATIONS': '#009845', 'NEWS & TRADE MEDIA': '#B1A9A7', 'COMPANIES & MARKET': '#B1A9A7', 'EVENTS & TRADE FAIRS': '#B1A9A7' }[s.group];
    return s;
  });

  // ---- Archive (420 items) --------------------------------------------------
  const ATYPE_LIST = ['Field bulletin', 'Regulatory record', 'Label', 'Scientific paper', 'Researcher signal', 'Technical article', 'Competitor activity', 'Producer-organization update', 'Monitoring observation'];
  const ARCHIVE = Array.from({ length: 420 }, (_, i) => {
    const type = ATYPE_LIST[(i * 7) % ATYPE_LIST.length]; const c = CASES[(i * 11) % 24]; const sig = SIGNALS[(i * 13) % 56]; const useSig = i % 5 === 4;
    const ent = useSig ? sig : c; const days = (i * 37) % 240; const date = addDays(TODAY, -days);
    const srcPool = type === 'Scientific paper' || type === 'Researcher signal' ? SOURCES.filter(s => s.group === 'RESEARCH & SCIENCE') : type === 'Competitor activity' ? SOURCES.filter(s => s.group === 'COMPANIES & MARKET') : type === 'Technical article' ? SOURCES.filter(s => s.group === 'NEWS & TRADE MEDIA') : type === 'Producer-organization update' ? SOURCES.filter(s => s.group === 'FIELD & PRODUCER ORGANIZATIONS') : type === 'Regulatory record' || type === 'Label' ? [SOURCES[9]] : SOURCES.filter(s => s.group === 'GOVERNMENT & OFFICIAL' && s.cov.includes(ent.region));
    const src = srcPool[i % Math.max(1, srcPool.length)] || SOURCES[0];
    const company = type === 'Competitor activity' ? COMPANIES[i % 8] : null;
    const product = !useSig && c.primary && (type === 'Label' || type === 'Regulatory record' || i % 3 === 0) ? c.primary : null;
    const title = type === 'Label' ? `Label record · ${product || c.primary || 'portfolio candidate'} · ${ent.crop}` : type === 'Regulatory record' ? `Authorisation status · ${product || c.primary || 'portfolio candidate'}` : type === 'Competitor activity' ? `${company} · ${ent.crop} ${ent.issue.toLowerCase()} communication` : type === 'Scientific paper' ? `Research record · ${ent.issue} · ${ent.crop}` : type === 'Researcher signal' ? `Researcher activity · ${ent.issue}` : `${type} · ${ent.issue} · ${ent.region}`;
    /* §13 · A generated record is never attributed to a real institution as if that
       institution published it. The source becomes the record TYPE it demonstrates, and the
       real organisation is kept only as the route the real equivalent would come from. */
    return { id: 'IT-ARC-' + String(i + 1).padStart(4, '0'), type, title, date: fmt(date), dateFull: date.toLocaleDateString('it-IT', { day: '2-digit', month: 'short', year: 'numeric' }), days, crop: ent.crop, issue: ent.issue, region: ent.region, category: ent.category,
      isDemo: true, provenance: 'SYNTHETIC_DEMO',
      source: 'DEMO_RECORD', sourceRoute: src.name, sourceId: src.id, company, product, caseObj: useSig ? null : c, signal: useSig ? sig : null,
      summary: type === 'Field bulletin' ? `Regional bulletin item reporting ${ent.issue.toLowerCase()} situation on ${ent.crop.toLowerCase()} in ${ent.region}, with crop stage and monitoring guidance.` : type === 'Label' ? `Label extract for ${product || 'the candidate product'}: crop ${ent.crop}, target ${ent.issue}, application timing and interval as authorised.` : type === 'Regulatory record' ? `National database record confirming current authorisation status for ${product || 'the candidate product'} on ${ent.crop.toLowerCase()}.` : type === 'Scientific paper' ? `Topic-linked scientific work on ${ent.issue.toLowerCase()} in ${ent.crop.toLowerCase()}; connected to the Italy science layer. Title and authors in source record.` : type === 'Researcher signal' ? `Researcher activity on ${ent.issue.toLowerCase()} detected through publication and institutional channels.` : type === 'Technical article' ? `Technical article discussing ${ent.issue.toLowerCase()} pressure and timing for ${ent.crop.toLowerCase()} in ${ent.region}.` : type === 'Competitor activity' ? `${company} communication observed on ${ent.crop.toLowerCase()} ${ent.issue.toLowerCase()} topic. Activity only — no strategy inferred.` : type === 'Producer-organization update' ? `Producer organisation update on ${ent.crop.toLowerCase()} campaign and ${ent.issue.toLowerCase()} monitoring in ${ent.region}.` : `Monitoring observation: ${ent.issue.toLowerCase()} indicator recorded for ${ent.crop.toLowerCase()} in ${ent.region}.`,
      typeColor: '#B1A9A7' };
  }).sort((a, b) => a.days - b.days);
  const REAL_ARCHIVE = [].concat(
    REAL.NEWS.map(n => ({ id: n.id, type: 'News article', title: n.title, date: n.date, dateFull: n.date + ' 2026', days: n.days, crop: n.crop, issue: n.issue, region: n.region, category: CAT.disease, source: n.source, sourceId: (SOURCES.find(s => s.name === n.source) || SOURCES[0]).id, company: null, product: null, caseObj: (n.use.find(u => u.startsWith('case:')) ? CASES.find(c => c.id === n.use.find(u => u.startsWith('case:')).slice(5)) : null), signal: null, summary: n.summary + ' Originating source: ' + n.originating + '. Editorial type: ' + n.editorial + '.', typeColor: '#B1A9A7', real: true, provenance: n.provenance, originating: n.originating, editorial: n.editorial })),
    REAL.BULLETINS.map(b => ({ id: b.id, type: 'Field bulletin', title: b.what, date: b.through, dateFull: b.through + ' 2026', days: 5, crop: b.crop, issue: 'Regional monitoring', region: b.region, category: CAT.pest, source: b.source, sourceId: (SOURCES.find(s => s.name === b.source) || SOURCES[0]).id, company: null, product: null, caseObj: b.caseId ? CASES.find(c => c.id === b.caseId) : null, signal: null, summary: b.what + '. Official regional bulletin route — recurring real signal.', typeColor: '#B1A9A7', real: true, provenance: b.provenance })),
    REAL.SCIENCE.map(r => ({ id: r.id, type: 'Scientific paper', title: r.kind + ' · ' + r.title, date: r.date, dateFull: r.date, days: 30, crop: r.crop, issue: r.issue, region: r.region, category: CAT.disease, source: r.org, sourceId: (SOURCES.find(s => r.org.indexOf(s.name.split(' ')[0]) === 0) || SOURCES[12]).id, company: null, product: null, caseObj: ((SCI_THEMES.find(t => t.id === r.themeId) || { caseObjs: [] }).caseObjs[0]) || null, signal: null, summary: r.what, typeColor: '#B1A9A7', real: true, provenance: r.provenance }))
  );
  ARCHIVE.forEach(a => { a.real = false; a.provenance = 'SYNTHETIC_DEMO'; });
  const ARCHIVE_ALL = REAL_ARCHIVE.concat(ARCHIVE).sort((a, b) => a.days - b.days);

  // ---- Field Sales Channel (10 demo messages) --------------------------------
  /* Fictional field representatives. Never a real ADAMA employee — provenance SYNTHETIC_DEMO.
     They are the inbound human sensor network: they send into Sintonia, Sintonia does not message them. */
  /* §15 · Role-based demonstration identities. A realistic invented employee name
     reads as a real ADAMA person, so the identity is the role and the territory. */
  const TSR_DEF = [
    ['RTV DEMO · VENETO', 'Veneto', 'Technical Sales Representative'],
    ['FIELD SALES DEMO · TOSCANA', 'Toscana', 'Field Sales Representative'],
    ['RTV DEMO · FRIULI-VENEZIA GIULIA', 'Friuli-Venezia Giulia', 'Technical Sales Representative'],
    ['FIELD SALES DEMO · PUGLIA', 'Puglia', 'Field Sales Representative'],
    ['RTV DEMO · EMILIA-ROMAGNA', 'Emilia-Romagna', 'Technical Sales Representative'],
    ['Marco R.', 'Lombardia', 'Field Sales Representative'],
    ['Luca F.', 'Piemonte', 'Technical Sales Representative']
  ];
  const TSR = TSR_DEF.map((t, i) => ({ id: 'TSR-' + (i + 1), region: t[1], name: t[0], label: t[0], initials: 'D', org: 'ADAMA Italy · Field Sales network · DEMO', role: t[2], roleCat: 'TECHNICAL SALES REPRESENTATIVES', platform: 'WhatsApp · inbound field channel', color: '#009845', demo: true, provenance: 'SYNTHETIC_DEMO' }));
  const tsrFor = (r) => TSR.find(t => t.region === r);
  const FM = (o) => o;
  const FIELD_MESSAGES = [
    FM({ id: 'FM-01', region: 'Veneto', sub: 'Treviso', crop: 'Grapevine', issue: 'Flavescenza Dorata', caseId: 'IT-OPP-001', state: 'CONNECTED', mins: 38, text: 'Several growers asking again about Scaphoideus control after the latest regional update. Dealers want clarity on the treatment window before they speak to customers this week.', signal: 'Customer questions observed', timing: 'Late season · symptom survey', product: 'EVURE PRO' }),
    FM({ id: 'FM-02', region: 'Toscana', sub: 'Grosseto', crop: 'Durum Wheat', issue: 'Fusarium Head Blight', caseId: 'IT-OPP-003', state: 'CONNECTED', mins: 95, text: 'Fusarium coming up in conversations again. Growers here are planning sowing and two customers asked what ADAMA has for the flowering window next spring. Want to be ready.', signal: 'Product interest reported', timing: 'Pre-sowing · programme decisions', product: 'MAXENTIS' }),
    FM({ id: 'FM-03', region: 'Friuli-Venezia Giulia', sub: 'Udine', crop: 'Maize', issue: 'European Corn Borer', caseId: 'IT-OPP-002', state: 'CONNECTED', mins: 2, text: 'Two maize customers asked today about timing for corn borer. They are watching the ERSA flight info and want to know when the conversation should start.', signal: 'Customer questions observed', timing: 'Oviposition · window open', product: 'COSAYR 200 SC' }),
    FM({ id: 'FM-04', region: 'Friuli-Venezia Giulia', sub: 'Pordenone', crop: 'Maize', issue: 'Diabrotica', caseId: null, signalMatch: { issue: 'Diabrotica', region: 'Friuli-Venezia Giulia' }, state: 'NEW SIGNAL', mins: 260, text: 'Diabrotica being discussed more by dealers this week. One customer specifically asked about the options ADAMA has available for next year.', signal: 'Local concern reported', timing: 'Adults · next-sowing planning', product: 'FORZA' }),
    FM({ id: 'FM-05', region: 'Veneto', sub: 'Rovigo', crop: 'Sugar Beet', issue: 'Cercospora Leaf Spot', caseId: 'IT-OPP-007', state: 'CONNECTED', mins: 1440, text: 'Growers watching Cercospora very closely. Co.Pro.B. updates being discussed at the dealer and there is interest in understanding when protection becomes more urgent.', signal: 'Local concern reported', timing: 'Late canopy · DSS alert', product: 'MIRADOR TURBO' }),
    FM({ id: 'FM-06', region: 'Puglia', sub: 'Bari', crop: 'Olive', issue: 'Olive Fruit Fly', caseId: 'IT-OPP-006', state: 'CONNECTED', mins: 1800, text: 'Olive fruit fly back in customer conversations. Two growers asked whether we expect pressure to become important before the next treatment decision.', signal: 'Customer questions observed', timing: 'Fruit hardening · threshold', product: 'KLARTAN 20 EW' }),
    FM({ id: 'FM-07', region: 'Veneto', sub: 'Verona', crop: 'Grapevine', issue: 'Downy Mildew', caseId: 'IT-OPP-021', state: 'CONNECTED', mins: 2900, text: 'After the recent weather several vineyards are asking about protection strategy for next season. Dealers want support material they can use quickly.', signal: 'Product interest reported', timing: 'Season closing · 2027 programme', product: 'MIRADOR TURBO' }),
    FM({ id: 'FM-08', region: 'Emilia-Romagna', sub: 'Piacenza', crop: 'Wheat', issue: 'Septoria Leaf Blotch', caseId: null, relatedCase: 'IT-OPP-015', signalMatch: { issue: 'Septoria', region: 'Lombardia' }, state: 'NEW SIGNAL', mins: 3300, text: 'Septoria coming up again in technical conversations here. 3 customers already asking what products should be considered for the next timing.', signal: 'Customer questions observed · 3', timing: 'Pre-sowing · T1/T2 spring', product: 'MAXENTIS' }),
    FM({ id: 'FM-09', region: 'Lombardia', sub: 'Cremona', crop: 'Maize', issue: 'Competitor mention', caseId: 'IT-OPP-004', state: 'NEEDS VALIDATION', mins: 4200, text: 'One distributor says competitor technical activity around maize protection has increased. Customers mentioned Bayer and Syngenta more than usual this week.', signal: 'Competitor mention observed', timing: 'Silking · adults', product: null, competitors: ['Bayer', 'Syngenta'] }),
    FM({ id: 'FM-10', region: 'Piemonte', sub: 'Asti', crop: 'Grapevine', issue: 'Flavescenza Dorata', caseId: 'IT-OPP-009', state: 'CONNECTED', mins: 5600, text: 'Symptom survey started in the compulsory-control area. Growers asking what the 2027 obligations will look like and whether we can support a dealer meeting before winter.', signal: 'Customer questions observed', timing: 'Harvest · symptom survey', product: 'MAVRIK SMART' }),
    FM({ id: 'FM-11', region: 'Lombardia', sub: 'Cremona', crop: 'Maize', issue: 'Weed control', caseId: null, state: 'NEW SIGNAL', mins: 12, mtype: 'CUSTOMER QUESTION', channel: 'GROWER', text: 'Several maize growers are already asking how to plan pre-emergence weed control for the next cycle. They want to decide the programme before winter, not in April.', signal: 'Customer questions observed', timing: 'Pre-season · programme planning', product: null, weed: true }),
    FM({ id: 'FM-12', region: 'Emilia-Romagna', sub: 'Bologna', crop: 'Sugar Beet', issue: 'Weed control', caseId: null, state: 'CLASSIFIED', mins: 180, mtype: 'DEALER / COOPERATIVE SIGNAL', channel: 'COOPERATIVE', text: 'A cooperative asked which ADAMA options are available for the beet weed programme next spring. They run repeated low-dose applications and want the range explained before their technical meeting.', signal: 'Channel question reported', timing: 'Pre-season · channel preparation', product: null, weed: true }),
    FM({ id: 'FM-13', region: 'Piemonte', sub: 'Vercelli', crop: 'Rice', issue: 'Herbicide resistance', caseId: null, state: 'NEEDS VALIDATION', mins: 420, mtype: 'WEED OBSERVATION', channel: 'GROWER', text: 'A grower says his usual rice weed programme is not holding on Echinochloa the way it used to. One farm only, and he has no trial data — but he is asking what to change.', signal: 'Local concern reported', timing: 'Post-harvest · next programme', product: null, weed: true, validation: 'Single farm, no measurement. Cannot be read as regional resistance — GIRE is the reference for confirmed cases.' }),
    FM({ id: 'FM-14', region: 'Veneto', sub: 'Verona', crop: 'Grapevine', issue: 'Crop stage', caseId: null, state: 'CLASSIFIED', mins: 300, mtype: 'CROP STAGE', channel: 'GROWER', text: 'Vineyards in the plots I visited around Verona have finished harvest this week.', signal: 'Field-reported crop stage', timing: 'Harvest complete · local', product: null, validation: 'Adequately scoped to the visited plots. Valid as a local field-reported stage, not as a regional stage.' }),
    FM({ id: 'FM-15', region: 'Puglia', sub: 'Foggia', crop: 'Durum Wheat', issue: 'Crop stage', caseId: null, state: 'CLASSIFIED', mins: 1100, mtype: 'CROP STAGE', channel: 'GROWER', text: 'Soil preparation has started on the farms I follow near Foggia. Sowing decisions are being made now.', signal: 'Field-reported crop stage', timing: 'Pre-sowing', product: null, validation: 'Scoped to the farms followed by this representative.' }),
    FM({ id: 'FM-16', region: 'Emilia-Romagna', sub: 'Ferrara', crop: 'Soybean', issue: 'Weed control', caseId: null, state: 'NEW SIGNAL', mins: 2200, mtype: 'PRODUCT INTEREST', channel: 'DEALER', text: 'A dealer asked twice this week which graminicide options we have for soybean. Two of his customers had Sorghum halepense problems last season.', signal: 'Product interest reported', timing: 'Pre-season', product: null, weed: true }),
    FM({ id: 'FM-17', region: 'Lombardia', sub: 'Pavia', crop: 'Maize', issue: 'Competitor mention', caseId: null, state: 'NEEDS VALIDATION', mins: 3000, mtype: 'COMPETITOR MENTION', channel: 'DEALER', text: 'The dealer here is showing customers a competitor pre-emergence programme for maize. He mentioned it twice while I was there.', signal: 'Competitor mention observed', timing: 'Pre-season', product: null, competitors: ['Syngenta'], weed: true, validation: 'One dealer, one visit. Not evidence of a competitor campaign.' }),
    FM({ id: 'FM-18', region: 'Toscana', sub: 'Siena', crop: 'Olive', issue: 'Application timing', caseId: 'IT-OPP-006', state: 'CONNECTED', mins: 5000, mtype: 'APPLICATION TIMING QUESTION', channel: 'TECHNICAL ADVISOR', text: 'A technical advisor asked how to position the treatment relative to the trap thresholds this year. He is preparing advice for a group of growers.', signal: 'Application timing question', timing: 'Fruit fly window open', product: 'KLARTAN 20 EW' })
  ];
  const FM_COLOR = { 'CONNECTED': '#009845', 'NEW SIGNAL': '#978B87', 'NEEDS VALIDATION': '#978B87', 'WATCH': '#978B87' };
  const MTYPE_BY_SIGNAL = {
    'Customer questions observed': 'CUSTOMER QUESTION', 'Product interest reported': 'PRODUCT INTEREST',
    'Local concern reported': 'FIELD OBSERVATION', 'Competitor mention observed': 'COMPETITOR MENTION',
    'Field-reported crop stage': 'CROP STAGE', 'Channel question reported': 'DEALER / COOPERATIVE SIGNAL',
    'Application timing question': 'APPLICATION TIMING QUESTION'
  };
  const MTYPE_COLOR = {
    'CUSTOMER QUESTION': '#00A0DF', 'PRODUCT INTEREST': '#009845', 'FIELD OBSERVATION': '#F5B317',
    'COMPETITOR MENTION': '#F89E18', 'CROP STAGE': '#7DB41E', 'DEALER / COOPERATIVE SIGNAL': '#9D1D96',
    'APPLICATION TIMING QUESTION': '#00698F', 'WEED OBSERVATION': '#7DB41E'
  };
  const MTYPE_TEXT = { 'DEALER / COOPERATIVE SIGNAL': '#C77BC3', 'APPLICATION TIMING QUESTION': '#5CC3EE' };
  const CHANNEL_BY_SIGNAL = { 'Customer questions observed': 'GROWER', 'Product interest reported': 'GROWER', 'Competitor mention observed': 'DEALER', 'Channel question reported': 'COOPERATIVE', 'Local concern reported': 'GROWER' };
  FIELD_MESSAGES.forEach(m => {
    m.tsr = tsrFor(m.region); m.person = m.tsr.name; m.personRole = m.tsr.role; m.color = FM_COLOR[m.state];
    m.mtype = m.mtype || MTYPE_BY_SIGNAL[m.signal] || 'FIELD OBSERVATION';
    m.mtypeColor = MTYPE_COLOR[m.mtype] || '#978B87';
    m.mtypeText = MTYPE_TEXT[m.mtype] || m.mtypeColor;
    m.channel = m.channel || CHANNEL_BY_SIGNAL[m.signal] || 'UNKNOWN';
    m.isWeed = !!m.weed;
    m.demo = true; m.provenance = 'SYNTHETIC_DEMO';
    m.proves = 'This representative reported this. Nothing more.';
    m.when = m.mins < 60 ? m.mins + ' min ago' : m.mins < 1440 ? Math.round(m.mins / 60) + 'h ago' : Math.round(m.mins / 1440) + 'd ago';
    m.caseObj = m.caseId ? CASES.find(c => c.id === m.caseId) : (m.relatedCase ? CASES.find(c => c.id === m.relatedCase) : null);
    m.signalObj = m.signalMatch ? SIGNALS.find(x => x.issue === m.signalMatch.issue && x.region === m.signalMatch.region) || SIGNALS.find(x => x.issue === m.signalMatch.issue) : null;
    m.confidence = 'Field voice observed'; m.needsValidation = true; m.category = CAT[m.caseObj ? m.caseObj.cat : 'pest'];
  });
  /* §9 · The optional Field Sales integration is a DEMONSTRATION. Its synthetic messages
     may be shown as "this message would connect to X", but they must never mutate core
     intelligence: no evidence total, no score, no status, no source convergence. */
  CASES.forEach(c => {
    c.fieldMessages = FIELD_MESSAGES.filter(m => m.caseId === c.id);
    c.fieldCount = c.fieldMessages.length;
    c.evidenceTotal = Object.values(c.evidence).reduce((s, v) => s + v, 0);
  });
  TSR.forEach(t => { t.messages = FIELD_MESSAGES.filter(m => m.region === t.region); t.related = t.messages.map(m => m.caseObj).filter(Boolean); t.signals = t.messages.map(m => m.signalObj).filter(Boolean); t.crops = [...new Set(t.messages.map(m => m.crop))]; t.issues = [...new Set(t.messages.map(m => m.issue))]; t.recentTopic = t.messages[0] ? t.messages[0].issue + ' · ' + t.messages[0].signal.toLowerCase() : 'No message yet'; t.lastDays = t.messages[0] ? Math.max(0, Math.round(t.messages[0].mins / 1440)) : 0; t.last = t.messages[0] ? t.messages[0].when : '—'; t.contentCount = t.messages.length; t.region = t.region; t.label = t.label; });
  const NOTIFICATIONS = [
    { kind: 'NEW FIELD MESSAGE', text: 'Friuli-Venezia Giulia · Maize · European Corn Borer', when: '2 min ago', color: '#009845', target: 'field' },
    { kind: 'FIELD SIGNAL CONNECTED', text: 'Flavescenza Dorata · Veneto · dealer questions added context', when: '38 min ago', color: '#009845', target: 'IT-OPP-001' },
    { kind: 'ACTION BRIEF GENERATED', text: 'Field Sales · Fusarium · Durum Wheat · Toscana', when: '1h ago', color: '#E5E1E0', target: 'IT-OPP-003' },
    { kind: 'WINDOW UPDATE', text: 'European Corn Borer · FVG · 14 days remaining', when: '2h ago', color: '#009845', target: 'IT-OPP-002' },
    { kind: 'COMPETITOR MOVEMENT', text: 'BASF · technical communication · maize', when: '1d ago', color: '#E5E1E0', target: 'competitors' },
    { kind: 'NEW FUTURE SIGNAL', text: 'Diabrotica · Maize · FVG · from field channel', when: '4h ago', color: '#E5E1E0', target: 'future' }
  ];
  const FIELD_KPI = { messages: FIELD_MESSAGES.length, connected: FIELD_MESSAGES.filter(m => m.state === 'CONNECTED').length, newSignals: FIELD_MESSAGES.filter(m => m.state === 'NEW SIGNAL').length, regions: [...new Set(FIELD_MESSAGES.map(m => m.region))].length, products: [...new Set(FIELD_MESSAGES.map(m => m.product).filter(Boolean))].length, validation: FIELD_MESSAGES.filter(m => m.state === 'NEEDS VALIDATION').length };

  // ---- Crop Windows · anticipation layer -------------------------------------
  const CAL = { 'Flavescenza Dorata': [[6, 10], [7, 20], 'Vector treatments · mid-June → late July'], 'European Corn Borer': [[7, 10], [8, 20], 'Second-generation flight · July → August'], 'Diabrotica Adults': [[7, 1], [8, 15], 'Adult feeding at silking · July → mid-August'], 'Diabrotica Larvae': [[3, 20], [4, 30], 'Granular at sowing · late March → April'], 'Fusarium Head Blight': [[5, 1], [5, 25], 'Flowering · May'], 'Olive Fruit Fly': [[7, 15], [10, 15], 'Fruit hardening → harvest · mid-July → mid-October'], 'Cercospora Leaf Spot': [[6, 15], [9, 15], 'Canopy · mid-June → mid-September'], 'Septoria Leaf Blotch': [[4, 1], [5, 15], 'T1–T2 · April → mid-May'], 'Wheat Rusts': [[3, 15], [5, 10], 'First pustules · mid-March → May'], 'Cereal Aphids · BYDV Risk': [[10, 20], [11, 30], 'Autumn emergence · late October → November'], 'Grapevine Moth': [[7, 1], [8, 30], 'Second/third generation · July → August'], 'Codling Moth': [[5, 1], [8, 31], 'Generations · May → August'], 'Tomato Leafminer': [[6, 1], [8, 31], 'Fruit set → harvest · June → August'], 'Downy Mildew': [[4, 15], [7, 15], 'Shoot growth → bunch closure · mid-April → mid-July'], 'Powdery Mildew': [[5, 1], [7, 15], 'Flowering → bunch closure · May → mid-July'], 'Mycotoxin Risk': [[7, 15], [9, 15], 'Grain fill · mid-July → mid-September'] };
  const PREP_RULES = [[180, 'TOO EARLY', '#978B87'], [90, 'PLAN', '#009845'], [45, 'PREPARE', '#009845'], [14, 'ACTIVATE', '#009845'], [-1, 'ACT NOW', '#009845']];
  const LADDER = [[90, 'MARKET DEVELOPMENT', 'Start regional validation'], [60, 'MARKETING', 'Prepare communication assets'], [45, 'SALES / RTV', 'Prepare customer conversations'], [30, 'SUPPLY', 'Review internal readiness'], [14, 'SALES / RTV', 'Activate field execution']];
  // Next relevant moment for cases whose summer window is closing: autumn sowing / soil treatments / spring programmes (days from today).
  const WINDOW_SHIFT = { 'IT-OPP-007': [22, 40, 'Post-harvest review → 2027 DSS programme · late September'], 'IT-OPP-008': [26, 44, 'Post-harvest review → 2027 DSS programme · late September'], 'IT-OPP-009': [35, 70, 'Autumn uprooting obligation · compulsory-control decree · October'], 'IT-OPP-021': [48, 75, '2027 programme decisions with dealers · October → November'], 'IT-OPP-024': [55, 80, 'Post-harvest technical review · table grape · October → November'], 'IT-OPP-020': [230, 260, 'Transplanting → fruit set · processing tomato · April → May'], 'IT-OPP-022': [40, 60, 'Harvest mycotoxin sampling · October'], 'IT-OPP-017': [50, 90, 'Autumn emergence · late October → November'], 'IT-OPP-005': [200, 240, 'Granular at sowing · late March → April'], 'IT-OPP-019': [200, 240, 'Granular at sowing · late March → April'], 'IT-OPP-003': [88, 110, 'Sowing → early tillering · late November → December (programme decisions)'], 'IT-OPP-016': [80, 100, 'Sowing → early tillering · November'], 'IT-OPP-018': [95, 130, 'Sowing → tillering · December → January'], 'IT-OPP-015': [110, 150, 'Winter tillering → T0 · December → January'], 'IT-OPP-023': [14, 24, 'Pre-harvest larval damage check · September'] };
  const nextWindow = (issue) => { const c = CAL[issue]; if (!c) return null; const y = TODAY.getFullYear(); let st = new Date(y, c[0][0] - 1, c[0][1]), en = new Date(y, c[1][0] - 1, c[1][1]); if (en < TODAY) { st = new Date(y + 1, c[0][0] - 1, c[0][1]); en = new Date(y + 1, c[1][0] - 1, c[1][1]); } return { st, en, label: c[2] }; };
  const WINDOWS = CASES.map(c => {
    // Demo: some cases point at an autumn/winter/spring window (next relevant moment), not the closing summer one.
    /* ONE SEMANTIC WINDOW, ONE CANONICAL OBJECT. The former WINDOW_SHIFT /
       nextWindow(CAL) pair was a second window source and produced the 11 cross-screen
       conflicts found by the audit. Both are removed from the window path. */
    const cw = c.canonical;
    const open = c.windowOpen;
    const st = c.windowStart, en = c.windowEnd;
    const days = c.hasDates ? (open ? 0 : Math.max(0, c.daysToOpen)) : null;
    const remaining = open && c.hasDates ? c.daysLeft : null;
    // current-year evidence requires an upstream observation class, never a status literal
    const currentEvidence = !!(cw && (cw.CROP_STAGE_CLASS === 'OFFICIAL_OBSERVED_CURRENT' || cw.CROP_STAGE_CLASS === 'FIELD_REPORTED_CURRENT' || cw.ISSUE_STAGE_CLASS === 'OFFICIAL_OBSERVED_CURRENT' || cw.ISSUE_STAGE_CLASS === 'FIELD_REPORTED_CURRENT'));
    const nw = null;
    const confirmed = currentEvidence && open;
    const rule = open ? (currentEvidence ? PREP_RULES[4] : [0, c.status === 'WATCH' ? 'MONITOR' : 'VALIDATE', '#978B87']) : (PREP_RULES.find(r => days > r[0]) || PREP_RULES[PREP_RULES.length - 1]);
    const bucket = open ? 'OPEN NOW' : days <= 30 ? 'NEXT 30 DAYS' : days <= 60 ? '31–60 DAYS' : days <= 90 ? '61–90 DAYS' : days <= 180 ? '3–6 MONTHS' : 'NEXT CYCLE';
    const fm = FIELD_MESSAGES.filter(m => m.caseId === c.id || (m.relatedCase === c.id));
    const comp = ACTIVITIES.filter(a => a.crop === c.crop && a.issue === c.issue && a.region === c.region && a.days <= 30);
    const sig = SIGNALS.filter(x => x.crop === c.crop && x.region === c.region);
    const early = fm.length ? { state: 'FIELD REPORTED', color: '#009845', text: `${fm.length} field message${fm.length > 1 ? 's' : ''} · ${fm[0].signal.toLowerCase()}` } : comp.length ? { state: 'MARKET ATTENTION', color: '#E5E1E0', text: `${comp.length} competitor communication${comp.length > 1 ? 's' : ''} on ${c.crop.toLowerCase()} · 30d` } : { state: 'NOT OBSERVED', color: '#E5E1E0', text: 'No early commercial signal observed in monitored sources' };
    const scale = ['Puglia', 'Veneto', 'Lombardia', 'Emilia-Romagna', 'Piemonte', 'Friuli-Venezia Giulia', 'Sicilia'].includes(c.region) ? 'HIGH' : 'MEDIUM';
    const why = [
      { ok: true, t: open ? `Window open · ${remaining} days remaining (${confirmed ? 'confirmed by current-year signal' : 'seasonal · pressure not confirmed'})` : `Window in ${days} days (expected from annual cycle)` },
      { ok: true, t: `${scale === 'HIGH' ? 'High' : 'Medium'} ${c.crop.toLowerCase()} relevance in ${c.region}` },
      { ok: !!c.primary, t: c.primary ? `ADAMA portfolio match exists · ${c.primary}` : 'No confirmed portfolio match — check needed' },
      { ok: true, t: 'Annual monitoring expected for this issue' },
      { ok: fm.length > 0, t: fm.length ? `${fm.length} early field question${fm.length > 1 ? 's' : ''} reported` : 'No early field question yet' },
      { ok: confirmed, warn: !confirmed, t: confirmed ? 'Current-year pressure signal present' : 'Current-year pressure not yet confirmed' }
    ];
    const p = c.primaryObj;
    const readiness = p ? [['Target fit', 'CONFIRMED', '#009845'], ['Italy authorization', 'CONFIRMED · demo pack', '#009845'], ['Label window', 'CONFIRMED', '#009845'], ['Current crop timing', confirmed ? 'CURRENT' : 'EXPECTED', confirmed ? '#009845' : '#B1A9A7'], ['Field signal', fm.length ? 'REPORTED' : 'WAITING', fm.length ? '#009845' : '#978B87'], ['Internal stock', 'NOT CONNECTED', '#6E6663'], ['Marketing material', 'INTERNAL DATA REQUIRED', '#6E6663'], ['Sales readiness', 'INTERNAL DATA REQUIRED', '#6E6663']] : [['Target fit', 'TO CONFIRM', '#B1A9A7'], ['Italy authorization', 'PORTFOLIO CHECK NEEDED', '#B1A9A7'], ['Internal stock', 'NOT CONNECTED', '#6E6663']];
    return { id: 'WIN-' + c.id.slice(-3), caseId: c.id, c, crop: c.crop, region: c.region, issue: c.issue, category: c.category, days, remaining, open, confirmed, kind: confirmed ? 'CONFIRMED WINDOW' : open ? 'SEASONAL WINDOW · UNCONFIRMED' : 'EXPECTED WINDOW', windowLabel: `${fmt(st)} → ${fmt(en)}`, calLabel: nw ? nw.label : c.label, prep: rule[1], prepColor: rule[2], bucket, early, fieldMessages: fm, compCount: comp.length, signals: sig, scale, why, readiness: readiness.map(r => ({ k: r[0], v: r[1], color: r[2] })), ladder: LADDER.map(l => ({ days: l[0], dept: l[1], text: l[2], reached: days <= l[0], color: DEPT[l[1]].color, soft: DEPT[l[1]].soft })), nowRelevant: c.st.rank <= 1 };
  }).sort((a, b) => a.days - b.days);
  const WINDOW_KPI = { total: WINDOWS.length, open: WINDOWS.filter(w => w.open).length, d30: WINDOWS.filter(w => !w.open && w.days <= 30).length, d60: WINDOWS.filter(w => w.days > 30 && w.days <= 60).length, d90: WINDOWS.filter(w => w.days > 60 && w.days <= 90).length, d180: WINDOWS.filter(w => w.days > 90 && w.days <= 180).length, cycle: WINDOWS.filter(w => w.days > 180).length, plan: WINDOWS.filter(w => ['PLAN', 'PREPARE', 'ACTIVATE'].includes(w.prep)).length, early: WINDOWS.filter(w => w.early.state !== 'NOT OBSERVED').length };

  // ---- Future Radar · explainable layer ------------------------------------
  const GROUP_OF = { 'GOVERNMENT & OFFICIAL': 'OFFICIAL', 'RESEARCH & SCIENCE': 'SCIENCE', 'FIELD & PRODUCER ORGANIZATIONS': 'FIELD', 'NEWS & TRADE MEDIA': 'TECHNICAL MEDIA', 'COMPANIES & MARKET': 'MARKET', 'EVENTS & TRADE FAIRS': 'EVENTS' };
  const GROUP_COLOR = { 'NEWS & MEDIA': '#B1A9A7', EVENTS: '#B1A9A7', OFFICIAL: '#B1A9A7', FIELD: '#009845', SCIENCE: '#B1A9A7', RESEARCHERS: '#B1A9A7', 'TECHNICAL MEDIA': '#B1A9A7', MARKET: '#B1A9A7', COMPETITORS: '#B1A9A7', 'FIELD SALES': '#009845', PEOPLE: '#B1A9A7' };
  SIGNALS.forEach((x, i) => {
    const d = (n) => fmt(addDays(TODAY, -n));
    const off = SOURCES.filter(s => s.group === 'GOVERNMENT & OFFICIAL' && s.cov.includes(x.region) && (s.topics.includes('All crops') || s.topics.includes(x.crop))).slice(0, 1);
    const field = SOURCES.filter(s => s.group === 'FIELD & PRODUCER ORGANIZATIONS' && (s.topics.includes(x.crop) || (s.topics.includes('All crops') && i % 3 === 0))).slice(0, 1);
    const media = SOURCES.filter(s => s.group === 'NEWS & TRADE MEDIA').slice(i % 3, i % 3 + 1);
    const theme = SCI_THEMES.find(t => t.id === x.science);
    const recs = theme ? theme.records.slice(0, 2) : [];
    const researchers = theme ? PEOPLE.filter(p => p.theme && p.theme.id === theme.id && !p.real).slice(0, 1) : [];
    const comp = ACTIVITIES.filter(a => a.crop === x.crop && a.days <= 45).slice(0, 2);
    const fms = FIELD_MESSAGES.filter(m => m.signalObj && m.signalObj.id === x.id || (m.crop === x.crop && m.issue.split(' ')[0] === x.issue.split(' ')[0] && m.region === x.region));
    const src = [];
    off.forEach(s => src.push({ group: 'OFFICIAL', name: s.name, role: s.type, date: d(x.lastDays), observed: `${x.crop} bulletin item referencing ${x.issue.toLowerCase()}`, srcLoc: x.region, factLoc: x.region, id: s.id, kind: 'source' }));
    field.forEach(s => src.push({ group: 'FIELD', name: s.name, role: s.type, date: d(x.lastDays + 3), observed: `${x.crop} campaign update mentioning ${x.issue.toLowerCase()}`, srcLoc: s.cov, factLoc: s.cov.includes(x.region) ? x.region : 'Not yet established', id: s.id, kind: 'source' }));
    recs.forEach(r => src.push({ group: 'SCIENCE', name: r.institution, role: 'Research record · ' + r.study, date: String(r.year), observed: `${r.descriptor} — topic-linked work (title/authors in source record)`, srcLoc: 'Author affiliation', factLoc: r.location.startsWith('Study') ? 'Not yet established' : r.location, id: r.id, kind: 'record' }));
    researchers.forEach(p => src.push({ group: 'RESEARCHERS', name: p.label, role: p.org, date: d(p.lastDays), observed: `Recent activity on ${theme.title.toLowerCase()} · ${p.contentCount} works in monitored scope`, srcLoc: 'Affiliation · not a field location', factLoc: 'Not yet established', id: p.id, kind: 'person' }));
    media.forEach(s => src.push({ group: 'TECHNICAL MEDIA', name: s.name, role: s.type, date: d(x.lastDays + 5), observed: `Technical article on ${x.issue.toLowerCase()} in ${x.crop.toLowerCase()} (repeats regional bulletin content)`, srcLoc: 'Italy', factLoc: x.region, id: s.id, kind: 'source', derived: off.length > 0 }));
    comp.forEach(a => src.push({ group: 'COMPETITORS', name: a.company, role: a.type.toLowerCase(), date: a.date, observed: `${a.observed} — publication exists; no campaign intent inferred`, srcLoc: a.region, factLoc: 'Not applicable', id: a.company, kind: 'company' }));
    REAL.NEWS.filter(n => (n.crop === x.crop || n.crop.startsWith('Multiple')) && (n.region.includes(x.region) || n.region.startsWith('Italy'))).slice(0, 2).forEach(n => src.push({ group: 'NEWS & MEDIA', name: n.source, role: 'Media observation · originating: ' + n.originating, date: n.date, observed: n.title, srcLoc: 'Italy', factLoc: n.region, id: n.id, kind: 'news', real: true, derived: n.editorial.startsWith('REPUBLICATION') }));
    REAL.BULLETINS.filter(b => b.crop === x.crop && b.region === x.region).forEach(b => src.push({ group: 'OFFICIAL', name: b.source, role: 'Regional phytosanitary service', date: b.through, observed: b.what, srcLoc: b.region, factLoc: b.region, id: (SOURCES.find(s => s.name === b.source) || {}).id, kind: 'source', real: true }));
    REAL.RESEARCHERS.filter(r => r.themeId === (theme ? theme.id : null)).slice(0, 3).forEach(r => src.push({ group: 'RESEARCHERS', name: r.name, role: r.org, date: '2026', observed: r.focus, srcLoc: 'Affiliation · not a field location', factLoc: 'Not yet established', id: r.id, kind: 'person', real: true }));
    fms.forEach(m => src.push({ group: 'FIELD SALES', name: m.person, role: 'Technical Sales Representative', date: m.when, observed: `Field report: ${m.signal.toLowerCase()} — “${m.text.slice(0, 90)}…”`, srcLoc: m.region + ' · ' + m.sub, factLoc: m.region + ' (customer conversations, unverified)', id: m.id, kind: 'field' }));
    x.sources = src;
    const groups = [...new Set(src.map(s => s.group))];
    x.who = groups.map(g => ({ group: g, count: src.filter(s => s.group === g).length, color: GROUP_COLOR[g] }));
    x.independent = src.filter(s => !s.derived).length; x.observations = src.length;
    x.independenceNote = x.observations > x.independent ? `${x.observations} observations from ${x.independent} originating facts — media repeats of the bulletin are not counted as independent confirmation.` : `${x.observations} observations · each from a distinct originating source.`;
    const hasOfficial = off.length > 0, hasField = fms.length > 0 || field.length > 0, hasPortfolio = !!x.product, hasScience = recs.length > 0;
    const w = WINDOWS.find(y => y.crop === x.crop && y.region === x.region && y.issue.toLowerCase().includes(x.issue.toLowerCase().split(' ')[0])) || WINDOWS.find(y => y.crop === x.crop && y.issue.toLowerCase().includes(x.issue.toLowerCase().split(' ')[0]));
    x.window = w || null; x.windowLine = w ? (w.open ? `Current window · ${w.remaining} days remaining` : `~${w.days} days`) : 'Not yet established';
    x.timingKind = w ? (w.confirmed ? 'CURRENT WINDOW · supported by current observation' : w.open ? 'SEASONAL WINDOW · current-year timing not yet observed' : 'EXPECTED WINDOW · based on technical calendar') : 'TO BE CONFIRMED · no window record';
    x.whyWatch = [{ ok: true, t: `${groups.length} source type${groups.length > 1 ? 's' : ''} discussing the same crop × issue` }, { ok: hasOfficial, t: hasOfficial ? 'Official regional source references the issue' : 'No official regional reference yet' }, { ok: !!w, t: w ? 'Crop timing is relevant (' + x.windowLine + ')' : 'Timing not yet established' }, { ok: hasPortfolio, t: hasPortfolio ? 'ADAMA portfolio match exists · ' + x.product : 'No confirmed ADAMA label position' }, { warn: true, t: `Only ${x.region} has a current source — geographic relevance beyond it not established` }];
    x.whyShort = groups.length >= 3 ? `${groups.length} independent source types are discussing the same crop × issue.` : groups.length === 2 ? 'Two source types now reference this crop × issue.' : 'A first monitored source references this crop × issue.';
    x.whyRadar = `Attention is forming within monitored sources around ${x.crop.toLowerCase()} × ${x.issue.toLowerCase()} in ${x.region}. ${hasOfficial ? 'An official regional source references the issue' : 'No official regional source references it yet'}${hasPortfolio ? ', and ADAMA has a confirmed portfolio relationship (' + x.product + ')' : ''}. This does not yet prove a broader regional opportunity — field validation is still missing.`;
    x.observed = src.filter(s => s.group !== 'RESEARCHERS').slice(0, 4).map(s => `${s.name}: ${s.observed}`);
    if (hasPortfolio) x.observed.push(`${x.product} label names ${x.crop} · target family for ${x.issue.toLowerCase()}`);
    x.interpretation = [`The alignment of ${hasOfficial ? 'an official reference, ' : ''}${hasScience ? 'science attention, ' : ''}and crop timing makes this issue worth monitoring for portfolio relevance.`, 'Sintonia does not infer incidence, demand or market movement from these observations.'];
    x.unknown = ['Whether a current field signal exists beyond ' + x.region, 'Whether customer demand is changing', 'Whether distributors are preparing orders', 'ADAMA stock availability'];
    x.waiting = ['Next regional bulletin', fms.length ? 'Field confirmation of the reported questions' : 'A first field-sales report', hasPortfolio ? 'Regulatory confirmation of label position' : 'Portfolio check'];
    const step = (n, h, who, when, text, srcIdx) => ({ n, h, who, when, text, ev: srcIdx != null ? src[srcIdx] : null, hasEv: srcIdx != null && !!src[srcIdx] });
    x.trail = [
      step(1, hasOfficial ? 'OFFICIAL SIGNAL DETECTED' : 'SOURCE SIGNAL DETECTED', src[0] ? src[0].name : '—', src[0] ? src[0].date : '', src[0] ? src[0].observed : 'First monitored mention', 0),
      step(2, 'CROP CONTEXT CHECKED', x.crop + ' · ' + x.region, '', w ? 'Case record stage: ' + w.c.stage : 'Crop stage not yet observed for this region', null),
      step(3, 'TIMING CHECKED', 'Crop Windows', '', x.timingKind, null),
      step(4, 'PORTFOLIO CHECKED', x.product || 'No match', '', hasPortfolio ? 'Crop × target relationship confirmed in Italy portfolio evidence' : 'No confirmed ADAMA label position — Regulatory check requested', null),
      step(5, 'REGIONAL SCALE CHECKED', x.region, '', `${x.crop} relevance in ${x.region} confirmed at regional scale (ISTAT); adjacent regions not yet observed`, null),
      step(6, 'SINTONIA CONCLUSION', x.status, d(x.lastDays), 'Worth monitoring. The signal is relevant but geographic and field validation are needed before treating it as a commercial opportunity.', null)
    ];
    x.changes = src.slice(0, 5).map(s => ({ date: s.date, text: `${s.group === 'FIELD SALES' ? 'Field Sales question reported' : s.group === 'COMPETITORS' ? 'Competitor communication observed' : s.group === 'SCIENCE' ? 'Research record detected' : s.group === 'TECHNICAL MEDIA' ? 'New technical article' : 'Source item published'} · ${s.name}` })).concat([{ date: d(x.lastDays), text: 'Future Radar signal updated' }]);
    const before = 2 + (i % 4), after = before + 1 + (i % 5);
    x.trend = i % 4 === 0 ? { label: 'NOT COMPARABLE', text: 'Monitored source set changed in the period — no trend claimed.', color: '#978B87' } : { label: `${before} → ${after}`, text: `Mentions within the same monitored source set · last 30 days vs previous 30 days.`, color: '#fff' };
    const matchCase = CASES.find(c => c.crop === x.crop && c.region === x.region && c.issue.toLowerCase().includes(x.issue.toLowerCase().split(' ')[0]));
    x.promotion = [{ ok: fms.length > 0 || (matchCase && matchCase.windowOpen), t: 'Current regional field signal' }, { ok: true, t: 'Meaningful crop scale' }, { ok: hasPortfolio, t: 'ADAMA portfolio match' }, { ok: !!(w && w.open), t: 'Current crop stage observed' }, { ok: hasPortfolio, t: 'Label window known' }, { ok: !!(w && w.open), t: 'Timing overlap' }, { ok: false, t: 'Sufficient geographic relevance' }];
    x.promoted = !!(matchCase && matchCase.st.rank <= 1); x.matchCase = matchCase || null;
    x.promotionStatus = x.promoted ? 'PROMOTED · OPPORTUNITY EXISTS' : 'NOT YET';
    x.earlyMarket = fms.length ? `${fms.length} field-sales question${fms.length > 1 ? 's' : ''} reported — customer interest observed, not demand.` : comp.length ? `${comp.length} competitor communication${comp.length > 1 ? 's' : ''} observed — publication exists, no intent inferred.` : 'No early market signal observed in monitored sources.';
    x.scienceLine = theme ? `${theme.works} topic-linked works in monitored ${theme.title} scope · ${researchers.length} researcher profiles recently active · science signal, not field signal.` : 'No scientific theme linked yet.';
    x.updated = d(x.lastDays);
  });

  // ---- Crop calendar (bar matrix) --------------------------------------------
  // Expected cycles = agronomic norms for Italy (approximate, month/day). Regional hectares = ISTAT order of magnitude (approx). Observed markers only from REAL records.
  const M = (m, d) => [m, d];
  const CROP_CAL = {
    'Durum Wheat': { regions: [['Puglia', 350, -10], ['Sicilia', 280, -12], ['Basilicata', 110, -8], ['Marche', 120, 0], ['Toscana', 60, 0], ['Emilia-Romagna', 80, 5]], stages: [['Sowing', M(11, 1), M(12, 15)], ['Tillering', M(12, 15), M(3, 1)], ['Stem elongation', M(3, 1), M(4, 15)], ['Flowering', M(4, 20), M(5, 25)], ['Grain fill', M(5, 20), M(6, 20)], ['Harvest', M(6, 15), M(7, 15)]], issue: 'Fusarium Head Blight', issueWin: [M(4, 20), M(5, 25)], monitor: [M(3, 15), M(6, 1)], mandatory: null, weed: [['Post-emergence weed control', M(2, 1), M(3, 20)]] },
    'Wheat': { regions: [['Emilia-Romagna', 130, 0], ['Veneto', 90, 0], ['Piemonte', 90, 3], ['Lombardia', 80, 2], ['Toscana', 50, -3], ['Umbria', 45, -3]], stages: [['Sowing', M(10, 20), M(12, 10)], ['Tillering', M(12, 10), M(3, 1)], ['Stem elongation', M(3, 1), M(4, 20)], ['Flowering', M(4, 25), M(5, 30)], ['Grain fill', M(5, 25), M(6, 25)], ['Harvest', M(6, 20), M(7, 20)]], issue: 'Septoria Leaf Blotch', issueWin: [M(4, 1), M(5, 15)], monitor: [M(3, 1), M(6, 1)], mandatory: null, weed: [['Post-emergence weed control', M(2, 5), M(3, 25)]] },
    'Maize': { regions: [['Lombardia', 200, 0], ['Veneto', 150, 0], ['Piemonte', 140, 3], ['Friuli-Venezia Giulia', 70, 0], ['Emilia-Romagna', 70, -2]], stages: [['Sowing', M(3, 20), M(4, 30)], ['Vegetative', M(5, 1), M(6, 30)], ['Flowering', M(7, 1), M(7, 25)], ['Grain fill', M(7, 25), M(9, 10)], ['Maturation', M(9, 10), M(9, 30)], ['Harvest', M(9, 20), M(10, 31)]], issue: 'European Corn Borer', issueWin: [M(7, 10), M(8, 20)], monitor: [M(5, 15), M(9, 15)], mandatory: null, weed: [['Pre-emergence weed control', M(4, 1), M(5, 5)], ['Post-emergence weed control', M(5, 5), M(6, 10)]] },
    'Grapevine': { regions: [['Veneto', 95, 0], ['Puglia', 90, -10], ['Sicilia', 95, -14], ['Toscana', 60, -3], ['Piemonte', 43, 2], ['Trentino-Alto Adige', 15, 7], ['Lombardia', 28, 0]], stages: [['Bud break', M(4, 1), M(4, 20)], ['Shoot growth', M(4, 20), M(5, 31)], ['Flowering', M(6, 1), M(6, 20)], ['Fruit set', M(6, 20), M(7, 10)], ['Veraison', M(7, 25), M(8, 20)], ['Maturation', M(8, 20), M(9, 20)], ['Harvest', M(9, 1), M(10, 15)]], issue: 'Flavescenza Dorata', issueWin: [M(6, 10), M(7, 20)], monitor: [M(5, 15), M(9, 30)], mandatory: [M(6, 10), M(7, 20)], weed: [['Inter-row weed control', M(3, 1), M(5, 15)]] },
    'Olive': { regions: [['Puglia', 370, -7], ['Calabria', 180, -7], ['Sicilia', 160, -10], ['Toscana', 90, 5], ['Lazio', 80, 0], ['Liguria', 13, 5]], stages: [['Flowering', M(5, 15), M(6, 10)], ['Fruit set', M(6, 10), M(7, 10)], ['Fruit hardening', M(7, 10), M(8, 31)], ['Veraison', M(9, 15), M(10, 31)], ['Harvest', M(10, 15), M(12, 15)]], issue: 'Olive Fruit Fly', issueWin: [M(7, 15), M(10, 15)], monitor: [M(7, 1), M(10, 31)], mandatory: null, weed: [['Inter-row weed control', M(3, 1), M(5, 15)]] },
    'Sugar Beet': { regions: [['Emilia-Romagna', 12, 0], ['Veneto', 10, 0], ['Lombardia', 4, 0]], stages: [['Sowing', M(3, 1), M(3, 31)], ['Canopy development', M(4, 1), M(6, 15)], ['Closed canopy', M(6, 15), M(8, 31)], ['Harvest', M(8, 20), M(10, 31)]], issue: 'Cercospora Leaf Spot', issueWin: [M(6, 15), M(9, 15)], monitor: [M(6, 1), M(9, 15)], mandatory: null, weed: [['Post-emergence weed control', M(4, 1), M(5, 31)]] },
    'Apple': { regions: [['Trentino-Alto Adige', 28, 0], ['Veneto', 6, -5], ['Piemonte', 5, -3], ['Emilia-Romagna', 4, -5]], stages: [['Flowering', M(4, 5), M(4, 30)], ['Fruit growth', M(5, 1), M(7, 31)], ['Ripening', M(8, 1), M(8, 31)], ['Harvest', M(8, 20), M(10, 20)]], issue: 'Codling Moth', issueWin: [M(5, 1), M(8, 31)], monitor: [M(4, 15), M(9, 15)], mandatory: null, weed: [['Inter-row weed control', M(3, 15), M(5, 20)]] },
    'Tomato': { regions: [['Emilia-Romagna', 25, 0], ['Puglia', 20, -7], ['Lombardia', 8, 0]], stages: [['Transplant', M(4, 15), M(5, 31)], ['Flowering · fruit set', M(6, 1), M(6, 30)], ['Fruit development', M(7, 1), M(7, 31)], ['Harvest', M(8, 1), M(9, 15)]], issue: 'Tomato Leafminer', issueWin: [M(6, 1), M(8, 31)], monitor: [M(5, 15), M(9, 1)], mandatory: null, weed: [['Pre-transplant weed control', M(4, 1), M(5, 15)]] }
  };
  const OBSERVED = [
    { crop: 'Grapevine', region: 'Toscana', stage: 'Harvest start expected 7 Sep', date: M(9, 7), obsDate: '01 Sep', source: 'Consorzio Brunello di Montalcino (Agricultura.it)', provenance: 'REAL_FACT' },
    { crop: 'Grapevine', region: 'Veneto', stage: 'Bulletin series active · 20 issues to 27 Aug', date: M(8, 27), obsDate: '27 Aug', source: 'Regione Veneto — Servizio Fitosanitario', provenance: 'REAL_FACT' },
    { crop: 'Grapevine', region: 'Piemonte', stage: 'Flavescenza survey · field period to 30 Sep', date: M(9, 1), obsDate: '14 Jul → 30 Sep', source: 'Regione Piemonte — Settore Fitosanitario', provenance: 'REAL_FACT' },
    { crop: 'Apple', region: 'Trentino-Alto Adige', stage: 'Golden harvest starting (valley floor) · hills +6–7 d', date: M(9, 1), obsDate: '01 Sep', source: 'Italiafruit News', provenance: 'REAL_FACT' },
    { crop: 'Maize', region: 'Friuli-Venezia Giulia', stage: 'ERSA maize bulletin · flight / oviposition · BBCH 65–75', date: M(8, 12), obsDate: '12 Aug', source: 'ERSA Friuli-Venezia Giulia', provenance: 'REAL_FACT' },
    { crop: 'Olive', region: 'Toscana', stage: 'Fruit fly pressure reported very low', date: M(8, 27), obsDate: '27 Aug', source: 'Consorzio Olio Toscano IGP via media', provenance: 'REAL_FACT' },
    { crop: 'Olive', region: 'Veneto', stage: 'Olive bulletin series · 28 issues to 26 Aug', date: M(8, 26), obsDate: '26 Aug', source: 'Regione Veneto — Servizio Fitosanitario', provenance: 'REAL_FACT' },
    { crop: 'Olive', region: 'Liguria', stage: 'Heat / water stress · unusual fly dynamics', date: M(8, 20), obsDate: 'Aug', source: 'CeRSAA via Teatro Naturale', provenance: 'REAL_FACT' },
    { crop: 'Wheat', region: 'Umbria', stage: 'Cereal bulletins · 6 issues to 15 May', date: M(5, 15), obsDate: '15 May', source: 'Regione Umbria — Servizio Fitosanitario', provenance: 'REAL_FACT' },
    { crop: 'Grapevine', region: 'Umbria', stage: 'Grapevine bulletins · 20 issues to 21 Aug', date: M(8, 21), obsDate: '21 Aug', source: 'Regione Umbria — Servizio Fitosanitario', provenance: 'REAL_FACT' }
  ];
  const PREP_LEAD = 90;

  // ---- KPIs (computed) ------------------------------------------------------
  const count = (st) => CASES.filter(c => c.status === st).length;
  const KPI = {
    /* Buckets follow the canonical status codes. The legacy names no longer exist on any
       case, so counting them produced four permanently-zero, permanently-unmatched filters. */
    total: CASES.length,
    windowOpen: count('WINDOW_OPEN'), windowClosed: count('WINDOW_CLOSED'),
    nextCycle: count('NEXT_CYCLE'), dateUnknown: count('DATE_UNKNOWN'),
    windows: CASES.filter(c => c.windowOpen).length,
    /* Verified label matches, not raw links: 80 links resolve to 13 verified positions. */
    links: CASES.reduce((s, c) => s + (c.productLinks || []).length, 0),
    matches: CASES.reduce((s, c) => s + (c.verifiedLinks || []).length, 0),
    withMatch: CASES.filter(c => c.primary).length,
    movements: ACTIVITIES.filter(a => a.days <= 30).length, signals: SIGNALS.length, regions: [...new Set(CASES.map(c => c.region))].length,
    orgs: SOURCES.length, people: PEOPLE.length, official: SOURCES.filter(s => s.group === 'GOVERNMENT & OFFICIAL').length, research: SOURCES.filter(s => s.group === 'RESEARCH & SCIENCE').length, field: SOURCES.filter(s => s.group === 'FIELD & PRODUCER ORGANIZATIONS').length, media: SOURCES.filter(s => s.group === 'NEWS & TRADE MEDIA').length, market: SOURCES.filter(s => s.group === 'COMPANIES & MARKET').length, events: SOURCES.filter(s => s.group === 'EVENTS & TRADE FAIRS').length,
    archive: ARCHIVE_ALL.length, records: RECORDS.length, researchers: PEOPLE.filter(p => p.role === 'Researcher').length, companies: COMPANIES.length, activities: ACTIVITIES.length
  };
  const REGION_STATS = REGIONS.map(r => { const cs = CASES.filter(c => c.region === r.name); const sg = SIGNALS.filter(s => s.region === r.name); const top = cs.slice().sort((a, b) => a.st.rank - b.st.rank)[0]; return { ...r, cases: cs.length, signals: sg.length, color: cs.length ? top.st.color : sg.length ? 'rgba(151,139,135,0.204)' : 'rgba(151,139,135,0.085)', border: cs.length ? top.st.color : 'rgba(151,139,135,0.17)', textColor: cs.length ? '#fff' : sg.length ? '#C9C3C1' : '#B1A9A7', short: r.name.split(/[\s-]/).map(w => w[0]).join('').slice(0, 3).toUpperCase(), active: cs.length > 0 || sg.length > 0 }; });

  KPI.people += TSR.length;
  const cnt = (arr, f) => arr.filter(f).length;
  const REAL_STATS = (() => { const groups = [['Sources', SOURCES.length, SOURCES.length], ['News items', REAL.NEWS.length, REAL.NEWS.length], ['Official bulletin routes', REAL.BULLETINS.length, REAL.BULLETINS.length], ['Researchers', cnt(PEOPLE, p => p.real), cnt(PEOPLE, p => p.role === 'Researcher')], ['People (all)', cnt(PEOPLE, p => p.real), PEOPLE.length], ['Science records', cnt(RECORDS, r => r.real), RECORDS.length], ['Events', EVENTS.length, EVENTS.length], ['Event participations (official)', EVENTS.reduce((s, e) => s + e.confirmed.length + e.historical.length, 0), EVENTS.reduce((s, e) => s + e.confirmed.length + e.historical.length, 0)], ['Competitor activity', cnt(ACTIVITIES, a => a.real), ACTIVITIES.length], ['Opportunity cases with real observation', cnt(CASES, c => c.realObs), CASES.length], ['Crop windows with observed timing', cnt(WINDOWS, w => w.c.realObs), WINDOWS.length], ['Future signals', cnt(SIGNALS, x => x.sources.some(s => s.real)), SIGNALS.length], ['Archive', cnt(ARCHIVE_ALL, a => a.real), ARCHIVE_ALL.length], ['Field messages', 0, FIELD_MESSAGES.length]]; const real = groups.reduce((s, g) => s + g[1], 0), total = groups.reduce((s, g) => s + g[2], 0); return { groups: groups.map(g => ({ label: g[0], real: g[1], total: g[2] })), real, total, pct: Math.round(real / total * 100) }; })();
  window.ITALY_DEMO = { inkOn, setMonths, TODAY, CAT, STATUS, DEPT, REGIONS, REGION_STATS, PRODUCTS, PRODUCT_LIST: Object.values(PRODUCTS), CASES, SIGNALS, COMPANIES: COMPANY_OBJS, CO_META, ACTIVITIES, EVENTS, CPRODUCTS, MATRIX, CROP_COLS, ISSUE_ROWS, WHAT_CHANGED, ATYPE_COLOR, SCI_THEMES, RECORDS, INSTITUTIONS: INST_OBJS, PEOPLE: PEOPLE.concat(TSR), TSR, FIELD_MESSAGES, FIELD_KPI, NOTIFICATIONS, WINDOWS, WINDOW_KPI, LADDER, F_COLOR, GROUP_COLOR, SOURCES, ARCHIVE: ARCHIVE_ALL, NEWS: REAL.NEWS, BULLETINS: REAL.BULLETINS, REALITY: REAL.REALITY, KPI, ago, fmt, REAL_STATS, CROP_CAL, OBSERVED, PREP_LEAD, CAL };
})();
