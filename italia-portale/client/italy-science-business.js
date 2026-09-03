/* Sintonia · SCIENCE → BUSINESS layer
   Scientific facts stay in italy-demo-data.js / italy-real-intelligence.js.
   This file adds only the BUSINESS INTERPRETATION on top of them, always separated
   from the science and always explainable. No paper count is treated as importance.
   No scientific activity is read as field incidence or as demand. */
(function () {
  const REL = {
    'ACT NOW': { color: '#00783F', bright: '#00B152', tint: 'rgba(0,152,69,0.10)', border: 'rgba(0,152,69,0.42)', def: 'Science contributes to an already actionable commercial or agronomic situation.' },
    'PREPARE': { color: '#00A0DF', bright: '#4FC3EF', tint: 'rgba(0,160,223,0.10)', border: 'rgba(0,160,223,0.42)', def: 'Science is relevant to an approaching crop, application or commercial preparation window.' },
    'PORTFOLIO OPPORTUNITY': { color: '#00B152', bright: '#00B152', tint: 'rgba(0,177,82,0.10)', border: 'rgba(0,177,82,0.42)', def: 'Evidence strengthens the relevance of a problem for which ADAMA has verified portfolio fit.' },
    'PORTFOLIO RISK': { color: '#F89E18', bright: '#F89E18', tint: 'rgba(248,158,24,0.10)', border: 'rgba(248,158,24,0.42)', def: 'Evidence may threaten or complicate current portfolio positioning — resistance or reduced sensitivity.' },
    'PORTFOLIO GAP': { color: '#9D1D96', bright: '#C46ABE', tint: 'rgba(157,29,150,0.10)', border: 'rgba(157,29,150,0.42)', def: 'Scientifically relevant issue with no confirmed ADAMA Italy solution.' },
    'POSITIONING WATCH': { color: '#7DB41E', bright: '#93CC23', tint: 'rgba(125,180,30,0.10)', border: 'rgba(125,180,30,0.42)', def: 'Evidence may influence how an existing product or category should be positioned.' },
    'MARKET DEVELOPMENT WATCH': { color: '#F5B317', bright: '#F5B317', tint: 'rgba(245,179,23,0.08)', border: 'rgba(245,179,23,0.38)', def: 'Issue may deserve trials, validation, expert engagement or geographic investigation.' },
    'SCIENCE WATCH': { color: '#978B87', bright: '#B1A9A7', tint: 'transparent', border: 'rgba(151,139,135,0.30)', def: 'Interesting science, but no demonstrated business implication yet.' }
  };

  const ACTIVITY_NOTE = 'Activity trend is reported as NOT MEASURED: no time-window comparison has been computed over a declared monitored universe in this demonstration. The descriptor carried by the source index is shown separately. Volume is volume, not importance.';

  // business layer, keyed by the science theme id in italy-demo-data.js
  const B = {
    'durum-fusarium': {
      rel: 'PREPARE', owners: ['MARKET DEVELOPMENT', 'TECHNICAL / SCIENCE', 'MARKETING'],
      short: 'Active Fusarium and mycotoxin research on a crop with verified ADAMA portfolio relevance, ahead of the next flowering window.',
      why: [
        { ok: true, t: 'Verified ADAMA portfolio fit on the linked opportunity cases' },
        { ok: true, t: 'Next relevant agronomic window is the spring flowering stage — next cycle, not this season' },
        { ok: true, t: 'Recent science supports the technical relevance of flowering-timing and mycotoxin risk' },
        { warn: true, t: 'Market Pulse reads durum wheat as pressured — value justification will matter more than usual' },
        { warn: true, t: 'No evidence here that Fusarium pressure is currently rising in Italian fields' }
      ],
      changes: ['NEXT-CYCLE PREPARATION', 'TECHNICAL CLAIMS / EVIDENCE', 'PORTFOLIO RELEVANCE', 'MARKET DEVELOPMENT'],
      shows: 'Published work examines Fusarium head blight epidemiology, flowering-stage timing and mycotoxin accumulation in durum systems.',
      notShows: 'It does not show current-season Fusarium incidence in any Italian region, and it does not show that growers will treat.',
      actions: ['PREPARE NEXT CYCLE', 'CREATE TECHNICAL BRIEF', 'REVIEW POSITIONING'],
      limits: ['No current-year field incidence', 'No mycotoxin monitoring data ingested', 'No trial data of our own']
    },
    'maize-mycotoxins': {
      rel: 'MARKET DEVELOPMENT WATCH', owners: ['MARKET DEVELOPMENT', 'TECHNICAL / SCIENCE'],
      short: 'Aflatoxin and fumonisin prediction work at UCSC Piacenza and CNR-ISPA sits close to Italy\'s largest maize districts.',
      why: [
        { ok: true, t: 'Italian institutions with a maize-mycotoxin specialism, in the main production regions' },
        { ok: true, t: 'Connects to maize opportunity cases already on the radar' },
        { warn: true, t: 'The link from mycotoxin prediction to a crop-protection intervention is indirect' },
        { warn: true, t: 'No verified ADAMA mycotoxin-specific claim in Italy' }
      ],
      changes: ['MARKET DEVELOPMENT', 'FIELD VALIDATION NEED', 'EXPERT / KOL ENGAGEMENT'],
      shows: 'Seasonal forecasting and climate-driven prediction of aflatoxin and fumonisin risk in Italian maize.',
      notShows: 'It does not establish an ADAMA product response, and it does not measure current contamination levels.',
      actions: ['FOLLOW RESEARCH THEME', 'IDENTIFY EXPERT', 'REVIEW TRIAL NEED'],
      limits: ['No product-level connection verified', 'Prediction models are not incidence data']
    },
    'resistance': {
      rel: 'PORTFOLIO RISK', resistance: true, owners: ['TECHNICAL / SCIENCE', 'MARKET DEVELOPMENT', 'REGULATORY / PORTFOLIO'],
      short: 'Pyrethroid and diamide sensitivity work touches mechanisms present in the ADAMA Italy insecticide range.',
      moa: { groups: ['IRAC 3A · pyrethroids', 'IRAC 28 · diamides'], exposureNote: 'Exposure is listed from the registered active ingredients of products already linked to the affected cases. It is a mechanism overlap, not a report of product failure.' },
      why: [
        { ok: true, t: 'Resistance / sensitivity theme with a named mechanism' },
        { ok: true, t: 'Mechanism overlap with registered ADAMA Italy actives is verifiable from label data' },
        { ok: true, t: 'Relevant Italian crops — grapevine and maize' },
        { warn: true, t: 'No Italian field-failure evidence for any ADAMA product is present in this corpus' },
        { warn: true, t: 'Sensitivity shifts in a population are not the same as loss of efficacy in a use' }
      ],
      changes: ['PORTFOLIO RISK', 'PRODUCT POSITIONING', 'TECHNICAL CLAIMS / EVIDENCE', 'FIELD VALIDATION NEED'],
      shows: 'Studies examine sensitivity of relevant pest populations to pyrethroid and diamide mechanisms.',
      notShows: 'It does not show that any ADAMA product has failed, and it does not quantify resistance frequency in Italian commercial fields.',
      actions: ['REVIEW RESISTANCE RISK', 'REVIEW PORTFOLIO', 'PLAN FIELD VALIDATION', 'CREATE TECHNICAL BRIEF'],
      limits: ['No Italian resistance-frequency survey ingested', 'No product-level efficacy data', 'IRAC classification not verified per active in this demo']
    },
    'xylella': {
      rel: 'PORTFOLIO GAP', owners: ['MARKET DEVELOPMENT', 'REGULATORY / PORTFOLIO'],
      short: 'High strategic relevance to Italian olive production, with no confirmed direct ADAMA portfolio response.',
      why: [
        { ok: true, t: 'Major Italian olive issue with active CREA and CNR-IPSP research and a European conference' },
        { ok: true, t: 'Olive is a crop where ADAMA Italy already has registered positions on other targets' },
        { warn: true, t: 'No confirmed direct ADAMA portfolio match for the pathogen itself' },
        { warn: true, t: 'Vector control is the only adjacent route, and it is not established here' }
      ],
      changes: ['PORTFOLIO GAP', 'MARKET DEVELOPMENT', 'REGULATORY WATCH'],
      shows: 'Work on early diagnosis, resistant varieties and vector control.',
      notShows: 'It does not show outbreak movement, and it does not imply ADAMA should develop a product.',
      actions: ['ASSESS PORTFOLIO GAP', 'FOLLOW RESEARCH THEME', 'WATCH REGULATORY DEVELOPMENT'],
      limits: ['No current outbreak-movement data', 'Adjacent vector-control fit not verified']
    },
    'grapevine-phytoplasma': {
      rel: 'PORTFOLIO OPPORTUNITY', owners: ['TECHNICAL / SCIENCE', 'MARKET DEVELOPMENT'],
      short: 'The largest science body in the corpus sits on a mandatory-control issue where ADAMA has a verified vector position.',
      why: [
        { ok: true, t: 'Verified ADAMA vector position on the linked cases' },
        { ok: true, t: 'Compulsory regional control framework gives the issue a fixed annual calendar' },
        { ok: true, t: 'Largest Italian wine regions are directly concerned' },
        { warn: true, t: 'Science volume is not evidence of rising field pressure' }
      ],
      changes: ['PORTFOLIO RELEVANCE', 'TECHNICAL CLAIMS / EVIDENCE', 'NEXT-CYCLE PREPARATION'],
      shows: 'Phytoplasma biology, epidemiology and control-programme evaluation.',
      notShows: 'It does not measure current infection rates, nor demand for any treatment.',
      actions: ['PREPARE NEXT CYCLE', 'REVIEW POSITIONING', 'IDENTIFY EXPERT'],
      limits: ['Current-year infection pressure unknown', 'Regional decree dates for the next season not yet published']
    },
    'scaphoideus': {
      rel: 'POSITIONING WATCH', owners: ['TECHNICAL / SCIENCE', 'MARKETING'],
      short: 'Vector biology and dispersal work bears directly on when a vector treatment should be positioned.',
      why: [
        { ok: true, t: 'Timing evidence is exactly what a vector-control positioning argument needs' },
        { ok: true, t: 'Same verified portfolio position as the phytoplasma theme' },
        { warn: true, t: 'Control-timing findings are regional and not automatically transferable' }
      ],
      changes: ['PRODUCT POSITIONING', 'TECHNICAL CLAIMS / EVIDENCE'],
      shows: 'Vector phenology, dispersal and the effect of treatment timing on vector populations.',
      notShows: 'It does not establish efficacy of any specific commercial product.',
      actions: ['REVIEW POSITIONING', 'CREATE TECHNICAL BRIEF'],
      limits: ['Regional transferability not established']
    },
    'olive-bactrocera': {
      rel: 'ACT NOW', owners: ['TECHNICAL / SCIENCE', 'FIELD SALES', 'MARKETING'],
      short: 'Threshold and population-dynamics work on an issue whose application window is open in the southern districts right now.',
      why: [
        { ok: true, t: 'Application window is currently open on the linked Puglia and Sicilia cases' },
        { ok: true, t: 'Verified ADAMA portfolio position on the linked cases' },
        { ok: true, t: 'Threshold research supports the intervention-timing conversation' },
        { warn: true, t: 'Market Pulse reads olive as pressured — grower economics are at their weakest' }
      ],
      changes: ['PORTFOLIO RELEVANCE', 'TECHNICAL CLAIMS / EVIDENCE', 'PRODUCT POSITIONING'],
      shows: 'Population dynamics, intervention thresholds and climate effects on the olive fruit fly.',
      notShows: 'It does not report current trap captures, and it does not predict purchase.',
      actions: ['REVIEW EVIDENCE', 'CREATE TECHNICAL BRIEF', 'VALIDATE'],
      limits: ['No current trap-capture series ingested']
    },
    'maize-borer': {
      rel: 'PREPARE', owners: ['MARKET DEVELOPMENT', 'TECHNICAL / SCIENCE'],
      short: 'Flight-model and larval-damage work on maize, where the window has closed for this season and reopens next cycle.',
      why: [
        { ok: true, t: 'Verified ADAMA portfolio fit on four linked maize cases' },
        { ok: true, t: 'Flight models are directly usable in next-cycle preparation' },
        { warn: true, t: 'This season\'s application window has closed' },
        { warn: true, t: 'Mycotoxin interaction is a research finding, not an ADAMA claim' }
      ],
      changes: ['NEXT-CYCLE PREPARATION', 'PORTFOLIO RELEVANCE', 'TECHNICAL CLAIMS / EVIDENCE'],
      shows: 'Flight phenology models, larval damage assessment and the interaction with mycotoxin risk.',
      notShows: 'It does not show current-season populations, and it does not support a yield-protection claim.',
      actions: ['PREPARE NEXT CYCLE', 'REVIEW EVIDENCE'],
      limits: ['No current-season flight data', 'Model transferability across regions not established']
    },
    'cercospora-dss': {
      rel: 'POSITIONING WATCH', owners: ['TECHNICAL / SCIENCE', 'MARKET DEVELOPMENT'],
      short: 'Decision-support and regional alert systems change how a fungicide programme is justified, not whether it is needed.',
      why: [
        { ok: true, t: 'DSS adoption directly affects how treatment timing is argued in the field' },
        { ok: true, t: 'Verified ADAMA position on the linked sugar-beet cases' },
        { warn: true, t: 'Small science volume — the theme is narrow, not weak' }
      ],
      changes: ['PRODUCT POSITIONING', 'TECHNICAL CLAIMS / EVIDENCE', 'MARKET DEVELOPMENT'],
      shows: 'Evaluation of decision-support models and regional alert systems for Cercospora.',
      notShows: 'It does not evaluate any commercial product.',
      actions: ['REVIEW POSITIONING', 'FOLLOW RESEARCH THEME'],
      limits: ['Beet is contract-priced — no market layer available for economic context']
    },
    'ipm': {
      rel: 'SCIENCE WATCH', strategic: true, owners: ['MARKET DEVELOPMENT', 'REGULATORY / PORTFOLIO'],
      short: 'Low and zero-pesticide protection research. No current commercial opportunity, high strategic relevance.',
      why: [
        { ok: true, t: 'Public-funded Italian project activity (CREA SUPPORT, Aug 2026)' },
        { warn: true, t: 'No ADAMA product connection is asserted or implied' },
        { warn: true, t: 'Policy and adoption research, not an agronomic intervention signal' }
      ],
      changes: ['MARKET DEVELOPMENT', 'REGULATORY WATCH'],
      shows: 'Policy, adoption and system-level work on reduced-input protection.',
      notShows: 'It does not indicate reduced crop-protection use in Italian commercial fields.',
      actions: ['FOLLOW RESEARCH THEME', 'WATCH REGULATORY DEVELOPMENT'],
      limits: ['No adoption measurement', 'No portfolio implication established']
    }
  };

  /* Additional monitored themes that the disease-heavy corpus was missing.
     These carry NO ingested paper count — the routes are named instead of a number invented. */
  const EXTRA_THEMES = [
    {
      id: 'weed-resistance', title: 'Herbicide resistance', crop: 'Durum Wheat · Wheat · Maize', issue: 'Resistant grass and broadleaf weeds', cat: 'weed',
      note: 'Italy has a dedicated herbicide-resistance research and monitoring community (GIRE — Gruppo Italiano di Resistenza agli Erbicidi, with university and CNR partners). Case counts and publication volume have not been ingested into this demonstration.',
      works: null, sourceTrend: 'not ingested', route: 'GIRE resistance database · HRAC classification · university weed-science groups',
      rel: 'PORTFOLIO RISK', resistance: true, weed: true, owners: ['TECHNICAL / SCIENCE', 'MARKET DEVELOPMENT', 'REGULATORY / PORTFOLIO'],
      short: 'The herbicide side of resistance intelligence, currently the least covered part of the science layer.',
      moa: { groups: ['HRAC Group 1 · ACCase', 'HRAC Group 2 · ALS', 'HRAC Group 9 · EPSPS'], exposureNote: 'ADAMA Italy herbicide exposure by HRAC group has NOT been verified in this demonstration. No product is listed until the label data is connected.' },
      why: [
        { ok: true, t: 'Resistance is the single mechanism-level risk that can move a herbicide portfolio position' },
        { ok: true, t: 'Weed-control windows are now mapped in Crop Windows for all eight crops' },
        { warn: true, t: 'No Italian resistance survey data ingested — routes are mapped, values are not' },
        { warn: true, t: 'ADAMA Italy herbicide range and HRAC exposure not yet connected' }
      ],
      changes: ['PORTFOLIO RISK', 'PRODUCT POSITIONING', 'PORTFOLIO GAP'],
      shows: 'Nothing yet. The theme is declared because its absence was a real gap in the science layer.',
      notShows: 'No claim of resistance presence, frequency or product impact in Italy.',
      actions: ['REVIEW PORTFOLIO', 'REVIEW RESISTANCE RISK', 'FOLLOW RESEARCH THEME'],
      limits: ['No publication volume ingested', 'No HRAC exposure mapping for the ADAMA Italy range', 'No Italian resistance-frequency data']
    },
    {
      id: 'weed-management', title: 'Weed management in cereals and maize', crop: 'Maize · Wheat · Durum Wheat', issue: 'Pre- and post-emergence programmes', cat: 'weed',
      note: 'Pre-emergence and post-emergence programme design, rotation effects and integrated weed management. Publication volume not ingested.',
      works: null, sourceTrend: 'not ingested', route: 'University weed-science groups · regional technical bulletins',
      rel: 'MARKET DEVELOPMENT WATCH', weed: true, owners: ['MARKET DEVELOPMENT', 'TECHNICAL / SCIENCE'],
      short: 'The commercial counterpart to the new weed windows in Crop Windows.',
      why: [
        { ok: true, t: 'Weed-control windows now exist for every crop in Crop Windows, with a 90-day preparation lead' },
        { warn: true, t: 'No ADAMA Italy herbicide portfolio connected in this demonstration' },
        { warn: true, t: 'No publication volume or trend measured' }
      ],
      changes: ['MARKET DEVELOPMENT', 'NEXT-CYCLE PREPARATION', 'PORTFOLIO GAP'],
      shows: 'Nothing ingested yet.',
      notShows: 'No claim about weed pressure or herbicide demand.',
      actions: ['FOLLOW RESEARCH THEME', 'REVIEW PORTFOLIO', 'PREPARE NEXT CYCLE'],
      limits: ['No records ingested', 'No portfolio connection']
    },
    {
      id: 'biocontrol', title: 'Biological control and low-residue systems', crop: 'All crops', issue: 'Biologicals · residue management', cat: 'disease',
      note: 'Strategic theme. Biological products are a declared investment area for the Italian crop-protection industry — roughly a third of sector R&D is directed to natural-origin products (Agrofarma).',
      works: null, sourceTrend: 'not ingested', route: 'Agrofarma R&D reporting · CREA and university programmes',
      rel: 'SCIENCE WATCH', strategic: true, owners: ['MARKET DEVELOPMENT', 'REGULATORY / PORTFOLIO'],
      short: 'No current commercial opportunity. Real strategic relevance to where the sector is investing.',
      why: [
        { ok: true, t: 'Sector R&D direction is documented: about one third of Italian crop-protection R&D goes to natural-origin products' },
        { warn: true, t: 'No ADAMA Italy biological position established in this demonstration' },
        { warn: true, t: 'No specific Italian research records ingested for this theme' }
      ],
      changes: ['MARKET DEVELOPMENT', 'REGULATORY WATCH', 'PORTFOLIO GAP'],
      shows: 'Industry-level investment direction only.',
      notShows: 'No product, efficacy or adoption claim.',
      actions: ['FOLLOW RESEARCH THEME', 'ASSESS PORTFOLIO GAP'],
      limits: ['No research records ingested', 'Industry aggregate is not an ADAMA position']
    }
  ];

  const RECORD_REL = {
    'grapevine-phytoplasma': 'MARKET DEVELOPMENT WATCH', 'scaphoideus': 'POSITIONING WATCH',
    'durum-fusarium': 'PREPARE', 'maize-borer': 'PREPARE', 'olive-bactrocera': 'ACT NOW',
    'maize-mycotoxins': 'MARKET DEVELOPMENT WATCH', 'xylella': 'PORTFOLIO GAP',
    'cercospora-dss': 'POSITIONING WATCH', 'ipm': 'SCIENCE WATCH', 'resistance': 'PORTFOLIO RISK'
  };

  const PERSON_USE = {
    'Researcher': 'Technical watch · potential expert to engage',
    'default': 'Monitored voice · context only'
  };

  window.ITALY_SCIENCE = { REL, B, EXTRA_THEMES, RECORD_REL, ACTIVITY_NOTE, PERSON_USE };
})();
