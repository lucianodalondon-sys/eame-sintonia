/* SINTONIA · APPLICATION DATA MODEL — v2
   ---------------------------------------------------------------------------
   THE DATA CONTRACT for every core screen.

   Precedence, highest first:
     1 CANONICAL       upstream-audited truth (windows, label verdicts)
     2 REAL_SOURCE     real ingested records from an external source
     3 REAL_DERIVED    computed from real records, never invented
     4 SYNTHETIC_DEMO  explicit demonstration fixtures, always labelled
     5 DEMO_SCENARIO   presentation scenario, never counted as real

   NORMALIZATION HAPPENS HERE, not in the views. Every screen consumes
   normalized records with stable lowercase field names, so the next
   intelligence package replaces DATA behind these contracts instead of
   requiring a portal rewrite.

   PRODUCT RULE: Sintonia core is EXTERNAL intelligence. Nothing here depends on
   CRM, orders, sell-in, sell-out, stock or private pipeline. What the external
   world cannot reveal resolves to NOT_EXTERNALLY_OBSERVABLE — never a
   placeholder inviting private data.
   --------------------------------------------------------------------------- */
(function () {
  const D = window.ITALY_DEMO || {};
  const IG = window.ITALY_INGEST || {};
  const CANON = window.ITALY_CANONICAL || {};
  const CAT = window.ITALY_CATALOG || {};
  const REAL = window.ITALY_REAL || {};
  const MKT = window.ITALY_MARKET || {};

  const P = {
    CANONICAL: 'CANONICAL', REAL_SOURCE: 'REAL_SOURCE', REAL_DERIVED: 'REAL_DERIVED',
    SYNTHETIC_DEMO: 'SYNTHETIC_DEMO', DEMO_SCENARIO: 'DEMO_SCENARIO',
    NOT_OBSERVABLE: 'NOT_EXTERNALLY_OBSERVABLE'
  };
  const DEMO_CLASSES = { SYNTHETIC_DEMO: 1, DEMO_SCENARIO: 1, DEMO: 1 };

  /* §19 · ONE reference date for the whole application. Comes from the canonical
     contract, never from a per-file clock. */
  const REFERENCE_DATE = (CANON.meta && CANON.meta.referenceDate) || CANON.referenceDate || '2026-09-02';
  const REF = new Date(REFERENCE_DATE + 'T00:00:00');
  const daysFrom = (iso) => { if (!iso) return null; const d = new Date(String(iso).slice(0, 10) + 'T00:00:00'); return isNaN(d) ? null : Math.round((d - REF) / 864e5); };

  /* §22 · ONE provenance classifier. Explicit provenance is primary truth; a
     record is never called real because a property name happened to be absent. */
  const provOf = (r, fallback) => {
    if (!r) return fallback;
    const p = String(r.provenance || r.PROVENANCE || r.prov || '').toUpperCase();
    if (p) { for (const k in DEMO_CLASSES) if (p.indexOf(k) >= 0) return P.SYNTHETIC_DEMO; return p; }
    if (r.isDemo === true || r.demo === true) return P.SYNTHETIC_DEMO;
    return fallback;
  };
  const isDemo = (r, fallback) => !!DEMO_CLASSES[provOf(r, fallback)];

  const coll = (records, provenance, note) => {
    const rec = records || [];
    return {
      records: rec, provenance, note: note || '', count: rec.length,
      demo: rec.filter(r => isDemo(r, provenance)).length,
      real: rec.filter(r => !isDemo(r, provenance)).length
    };
  };

  const S = (v) => (v === null || v === undefined || v === '') ? null : String(v).trim();
  const N = (v) => (v === null || v === undefined || v === '') ? null : (isNaN(Number(v)) ? null : Number(v));

  // ================= WINDOWS =================
  const uiOf = (r) => r ? { icon: r.category && r.category.icon, color: r.category && r.category.color, order: r.n } : {};
  const dwByCase = {};
  (D.WINDOWS || []).forEach(w => { dwByCase[w.caseId || w.id] = w; });
  const windows = coll((CANON.windows || []).map(w => ({
    ui: uiOf(dwByCase[w.LEGACY_CASE_ID]),
    windowId: w.WINDOW_ID, legacyCaseId: w.LEGACY_CASE_ID,
    id: (dwByCase[w.LEGACY_CASE_ID] || {}).id || w.WINDOW_ID,
    crop: S(w.CROP_NAME), issue: S(w.ISSUE_NAME), region: S(w.REGION),
    windowType: w.WINDOW_TYPE, startDate: w.START_DATE, endDate: w.END_DATE,
    dateState: w.DATE_STATE, dateConfidence: w.DATE_CONFIDENCE,
    cropStage: w.CROP_STAGE, cropStageClass: w.CROP_STAGE_CLASS,
    issueStage: w.ISSUE_STAGE, issueStageClass: w.ISSUE_STAGE_CLASS,
    status: w.CURRENT_STATUS, statusReason: w.STATUS_REASON,
    daysToStart: daysFrom(w.START_DATE), daysToEnd: daysFrom(w.END_DATE),
    sourceIds: w.SOURCE_IDS || [], provenance: P.CANONICAL, raw: w
  })), P.CANONICAL, 'canonical audited crop windows');

  // ================= PRODUCTS =================
  const norm = (s) => String(s || '').trim().toUpperCase();
  const byName = {};
  const addProduct = (name, patch) => {
    const k = norm(name); if (!k) return;
    byName[k] = Object.assign({ name: String(name).trim(), regulatory: null, commercial: null, links: [] }, byName[k], patch);
  };
  (IG.PRODUCTS || []).forEach(p => addProduct(p.name || p.PRODUCT, {
    regulatory: p, line: p.line, ai: p.ai || p.ACTIVE_INGREDIENTS,
    targets: p.targets || [], crops: p.crops || [], provenance: P.REAL_SOURCE
  }));
  ((CAT.ITEMS || CAT.PRODUCTS) || []).forEach(p => addProduct(p.name || p.PRODUCT, {
    commercial: p, category: p.category || p.CATALOG_CATEGORY, catalogUrl: p.url || p.CATALOG_URL, provenance: P.REAL_SOURCE
  }));
  Object.keys(D.PRODUCTS || {}).forEach(k => { if (!byName[norm(k)]) addProduct(k, { ai: (D.PRODUCTS[k] || {}).ai, provenance: P.SYNTHETIC_DEMO }); });

  /* §8 · ONE product-relationship truth. Strength classes come from the upstream
     label audit; no screen may invent or promote a relationship. */
  (D.CASES || []).forEach(c => (c.productLinks || []).forEach(l => {
    const e = byName[norm(l.name)];
    if (e) e.links.push({ crop: c.crop, issue: c.issue, region: c.region, caseId: c.id, strength: l.strength });
  }));
  const CATEGORY_OF = (e) => {
    const c = norm(e.category); if (c) return c;
    const line = norm(e.line);
    return line === 'HERBICIDA' ? 'ERBICIDI' : line === 'FUNGICIDA' ? 'FUNGICIDI'
      : (line === 'INSETICIDA' || line === 'INSETTICIDA') ? 'INSETTICIDI'
      : (line === 'OUTRA' || line === 'SPECIALE') ? 'SPECIALI' : '';
  };
  const products = Object.keys(byName).sort().map(k => {
    const e = byName[k];
    return Object.assign(e, {
      key: k, categoryLabel: CATEGORY_OF(e), inRegulatory: !!e.regulatory, inCommercial: !!e.commercial,
      verifiedLinks: e.links.filter(l => l.strength === 'VERIFIED_LABEL_MATCH'),
      checkNeededLinks: e.links.filter(l => l.strength === 'LABEL_CHECK_NEEDED'),
      relatedLinks: e.links.filter(l => l.strength === 'RELATED_PORTFOLIO'),
      rejectedLinks: e.links.filter(l => l.strength === 'NO_CONFIRMED_MATCH_CURRENT_READING'),
      commercialPerformance: P.NOT_OBSERVABLE
    });
  });
  const productByKey = {}; products.forEach(p => { productByKey[p.key] = p; });
  const strengthFor = (name, crop, issue) => {
    const e = productByKey[norm(name)]; if (!e) return 'NO_CONFIRMED_MATCH_CURRENT_READING';
    const hit = e.links.find(l => l.crop === crop && l.issue === issue);
    return hit ? hit.strength : 'NO_CONFIRMED_MATCH_CURRENT_READING';
  };

  // ================= COMPETITOR · §4 the key was wrong, 503 records were unused =================
  const competitorActivities = coll((IG.COMP_ACTIVITIES || []).map(a => {
    const paid = String(a.type || '').toUpperCase() === 'PAID';
    const sem = String(a.countrySem || '').toUpperCase();
    /* Italy reach is an observation, never a targeting claim. Organic multi-country
       or country-null records are NOT called observed in Italy. */
    const italyReach = paid && (sem.indexOf('IT') >= 0 || String(a.country || '').toUpperCase().indexOf('IT') >= 0);
    return {
      id: a.id, type: a.type, platform: S(a.platform), company: S(a.company), companyRaw: S(a.companyRaw),
      page: S(a.page), pageId: S(a.pageId),
      country: S(a.country), countrySem: S(a.countrySem),
      geoClass: italyReach ? 'REACHED_IN_ITALY' : (paid ? 'REACH_NOT_RESOLVED' : 'MULTI_COUNTRY_OR_UNRESOLVED'),
      italyReach, startDate: a.start, endDate: a.end, active: a.active,
      media: a.media, products: a.products || [], crops: a.crops || [], issues: a.issues || [],
      text: S(a.text), url: S(a.url),
      daysFromRef: daysFrom(a.start), provenance: provOf(a, P.REAL_SOURCE), raw: a
    };
  }), P.REAL_SOURCE, 'real observed competitor activity; Italy reach only where evidence supports it');

  // ================= MARKET · §13 =================
  const marketObservations = coll((IG.MARKET || []).map(m => ({
    id: m.ID, group: S(m.GROUP), product: S(m.PRODUCT), market: S(m.MARKET),
    priceRaw: S(m.PRICE_RAW), price: N(m.PRICE_NUM), unit: S(m.UNIT), stage: S(m.STAGE),
    referencePeriod: S(m.REFERENCE_PERIOD), publicationDate: S(m.PUBLICATION_DATE),
    geography: S(m.GEOGRAPHY), prevPrice: N(m.PREV_PRICE_NUM), changeVsPrev: N(m.CHANGE_VS_PREV_PCT),
    yearAgoPrice: N(m.YEAR_AGO_PRICE_NUM), changeVsYearAgo: N(m.CHANGE_VS_YEAR_AGO_PCT),
    seriesState: S(m.SERIES_STATE), seriesWarning: S(m.SERIES_WARNING),
    observations: N(m.OBSERVATIONS_IN_SERIES), sourceId: S(m.SOURCE_ID),
    provenance: provOf(m, P.REAL_SOURCE), raw: m
  })), P.REAL_SOURCE, 'real market observations with their own series state');

  // ================= VOICES · §11 the schema is uppercase; normalize once =================
  const voices = coll((IG.VOICES || []).map(v => ({
    id: v.ID, kind: S(v.KIND),
    person: S(v.PERSON), identityState: S(v.PERSON_IDENTITY_STATE),
    role: S(v.ROLE), organization: S(v.ORGANIZATION),
    platform: S(v.PLATFORM), channel: S(v.CHANNEL), title: S(v.CONTENT_TITLE),
    date: S(v.DATE), dateRelative: S(v.DATE_RELATIVE),
    crop: S(v.CROP), issue: S(v.ISSUE), caseId: S(v.CASE_ID),
    region: S(v.REGION), countryOfFact: S(v.COUNTRY_OF_FACT),
    /* The original quote is never translated and never parsed for facts. */
    textOriginal: S(v.TEXT_ORIGINAL),
    proves: S(v.WHAT_IT_PROVES), notProves: S(v.WHAT_IT_DOES_NOT_PROVE),
    sourceUrl: S(v.SOURCE_URL), sourceId: S(v.SOURCE_ID),
    provenance: provOf(v, P.REAL_SOURCE), raw: v
  })), P.REAL_SOURCE, 'real public field voices; identity never upgraded');

  // ================= SCIENCE · RESEARCHERS · §15 =================
  const scienceRecords = coll((IG.SCIENCE || []).map(r => ({
    id: r.ID || r.id, title: S(r.TITLE || r.title), institution: S(r.INSTITUTION || r.institution),
    date: S(r.DATE || r.date), year: S(r.YEAR || r.year),
    crop: S(r.CROP || r.crop), issue: S(r.ISSUE || r.issue),
    studyArea: S(r.STUDY_AREA || r.studyArea), affiliation: S(r.AFFILIATION || r.affiliation),
    url: S(r.SOURCE_URL || r.url), sourceId: S(r.SOURCE_ID || r.sourceId),
    provenance: provOf(r, P.REAL_SOURCE), raw: r
  })), P.REAL_SOURCE, 'real scientific records');

  const researchers = coll((IG.RESEARCHERS || []).map(r => ({
    id: r.ID || r.id, name: S(r.NAME || r.name || r.PERSON), org: S(r.ORGANIZATION || r.org || r.INSTITUTION),
    role: S(r.ROLE || r.role), crops: r.CROPS || r.crops || [], issues: r.ISSUES || r.issues || [],
    url: S(r.SOURCE_URL || r.url), provenance: provOf(r, P.REAL_SOURCE), raw: r
  })), P.REAL_SOURCE, 'real researcher identities');

  const resistance = coll((IG.RESISTANCE || []).map(r => ({
    id: r.ID, species: S(r.SPECIES), speciesIt: S(r.SPECIES_IT),
    mechanism: S(r.MECHANISM), crop: S(r.CROP_DECLARED),
    firstCaseYear: S(r.FIRST_CASE_YEAR), regions: r.REGIONS || [],
    multiple: !!r.MULTIPLE_RESISTANCE, provenance: provOf(r, P.REAL_SOURCE), raw: r
  })), P.REAL_SOURCE, 'GIRE confirmed Italian resistance cases');

  // ================= SOURCES · CHANNELS · EVENTS · NEWS =================
  /* cov / topics are FACTUAL scope fields — never inherited from a fixture. */
  const dsByName = {}; (D.SOURCES || []).forEach(x => { dsByName[String(x.name || '').toUpperCase()] = x; });
  const sources = coll((IG.SOURCES || []).map(s => ({
    ui: uiOf(dsByName[String(s.NAME || s.name || '').toUpperCase()]),
    id: (dsByName[String(s.NAME || s.name || '').toUpperCase()] || {}).id || s.ID || s.id, sourceId: s.ID || s.id, name: S(s.NAME || s.name), type: S(s.TYPE || s.type),
    group: S(s.GROUP || s.group), url: S(s.URL || s.url),
    geography: S(s.GEOGRAPHY || s.geography), provenance: provOf(s, P.REAL_SOURCE), raw: s
  })), P.REAL_SOURCE, 'real source registry');
  const channels = coll((IG.CHANNELS || []).map(c => ({
    id: c.ID || c.id, name: S(c.NAME || c.name || c.CHANNEL), platform: S(c.PLATFORM || c.platform),
    url: S(c.URL || c.url), provenance: provOf(c, P.REAL_SOURCE), raw: c
  })), P.REAL_SOURCE, 'real Italian public channels');
  const deByName = {}; (D.EVENTS || []).forEach(x => { deByName[String(x.name || '').toUpperCase()] = x; });
  const events = coll((IG.EVENTS || []).map(e => ({
    ui: uiOf(deByName[String(e.NAME || e.name || '').toUpperCase()]),
    id: (deByName[String(e.NAME || e.name || '').toUpperCase()] || {}).id || e.ID || e.id, name: S(e.NAME || e.name), date: S(e.DATE || e.date),
    location: S(e.LOCATION || e.location), url: S(e.URL || e.url),
    daysFromRef: daysFrom(e.DATE || e.date), provenance: provOf(e, P.REAL_SOURCE), raw: e
  })), P.REAL_SOURCE, 'real events');
  const news = coll((IG.NEWS || []).map(n => ({
    id: n.ID || n.id, title: S(n.TITLE || n.title), date: S(n.DATE || n.date),
    outlet: S(n.OUTLET || n.outlet || n.SOURCE), url: S(n.URL || n.url),
    crop: S(n.CROP || n.crop), issue: S(n.ISSUE || n.issue),
    provenance: provOf(n, P.REAL_SOURCE), raw: n
  })), P.REAL_SOURCE, 'real news records');

  /* §5 §6 · FUTURE SIGNALS come from upstream only. The old generated feed
     manufactured source descriptions and then counted them as independent
     convergence — that is removed. Upstream currently supplies few; that is the
     honest number, and the next load expands it. */
  const futureSignals = coll((IG.FUTURE_SIGNALS || []).map(f => ({
    id: f.SIGNAL_ID || f.ID || f.id, crop: S(f.CROP || f.crop), issue: S(f.ISSUE || f.issue),
    region: S(f.REGION || f.region), status: S(f.STATUS || f.status),
    whyNow: S(f.WHY_NOW || f.WHY_WATCH || f.whyNow),
    sourceIds: f.SOURCE_IDS || [], evidenceIds: f.EVIDENCE_RECORD_IDS || [],
    proves: S(f.WHAT_IT_PROVES), notProves: S(f.WHAT_IT_DOES_NOT_PROVE),
    confidence: S(f.CONFIDENCE), provenance: provOf(f, P.REAL_SOURCE), raw: f
  })), P.REAL_SOURCE, 'upstream future signals with traceable evidence links');

  /* §7 · Generated presentation scenarios live OUTSIDE the real feed. They are never
     counted in real signal totals, source convergence or emerging-topic metrics. */
  const futureScenarios = coll((D.SIGNALS || []).map(x => Object.assign({}, x, { provenance: P.DEMO_SCENARIO })), P.DEMO_SCENARIO, 'presentation scenarios; not evidence, not counted as real');

  const upstreamOpportunities = coll((IG.OPPORTUNITIES || []).map(o => ({
    id: o.ID || o.id, crop: S(o.CROP || o.crop), issue: S(o.ISSUE || o.issue),
    region: S(o.REGION || o.region), provenance: provOf(o, P.REAL_SOURCE), raw: o
  })), P.REAL_SOURCE, 'upstream opportunity candidates');

  /* §23 · Opportunity cases keep PER-RECORD provenance. A case is REAL_DERIVED only
     when its window is canonical and it carries a traceable external source. */
  const upstreamOppIds = {};
  (IG.OPPORTUNITIES || []).forEach(o => { upstreamOppIds[String(o.ID || o.id || '').toUpperCase()] = o; });
  const opportunities = coll((D.CASES || []).map(c => {
    const w = windows.records.find(x => x.legacyCaseId === c.id) || null;
    const upstream = upstreamOppIds[String(c.id).toUpperCase()] || null;
    /* Precedence: upstream real > REAL_DERIVED only with upstream evidence IDs >
       DEMO_SCENARIO. A traceable window is not evidence for the whole case. */
    const prov = upstream ? P.REAL_SOURCE : P.DEMO_SCENARIO;
    return Object.assign({}, c, {
      windowId: w ? w.windowId : null, canonicalWindow: w, upstream,
      provenance: prov, isUpstreamReal: !!upstream
    });
  }), P.DEMO_SCENARIO, 'presentation cases over canonical windows; upstream-real ones flagged');

  /* §17 · Archive is an INDEX over normalized intelligence, not a manufactured list. */
  const arch = [];
  const push = (kind, id, title, date, source, url, crop, issue, prov) => arch.push({ kind, id, title, date, source, url, crop, issue, provenance: prov });
  scienceRecords.records.forEach(r => push('SCIENCE', r.id, r.title, r.date || r.year, r.institution, r.url, r.crop, r.issue, r.provenance));
  marketObservations.records.forEach(m => push('MARKET', m.id, (m.product || '') + ' · ' + (m.market || ''), m.publicationDate, m.sourceId, null, m.product, null, m.provenance));
  competitorActivities.records.forEach(a => push('COMPETITOR', a.id, (a.company || '') + ' · ' + (a.type || ''), a.startDate, a.platform, a.url, (a.crops || [])[0], (a.issues || [])[0], a.provenance));
  voices.records.forEach(v => push('VOICE', v.id, v.title || v.person, v.date, v.platform, v.sourceUrl, v.crop, v.issue, v.provenance));
  events.records.forEach(e => push('EVENT', e.id, e.name, e.date, e.location, e.url, null, null, e.provenance));
  news.records.forEach(n => push('NEWS', n.id, n.title, n.date, n.outlet, n.url, n.crop, n.issue, n.provenance));
  windows.records.forEach(w => push('WINDOW', w.id, (w.issue || '') + ' · ' + (w.region || ''), w.startDate, 'CANONICAL', null, w.crop, w.issue, w.provenance));
  const archive = coll(arch, P.REAL_DERIVED, 'index over normalized intelligence records; no manufactured rows');

  /* OPTIONAL INTEGRATION DEMO — outside the external-intelligence core.
     §9 · These records must never mutate a core object. */
  const fieldMessages = coll((D.FIELD_MESSAGES || []).map(m => Object.assign({}, m, { provenance: P.SYNTHETIC_DEMO })), P.SYNTHETIC_DEMO, 'optional integration demonstration; never affects core intelligence');

  const collections = {
    windows, opportunities, upstreamOpportunities, futureSignals, futureScenarios,
    products: coll(products, P.REAL_SOURCE, 'regulatory registry joined to the public commercial catalog'),
    regulatory: coll(IG.PRODUCTS, P.REAL_SOURCE, 'official Italian registration records'),
    commercial: coll(CAT.ITEMS || CAT.PRODUCTS, P.REAL_SOURCE, 'reconstructed public commercial catalog'),
    competitorActivities, marketObservations, scienceRecords, researchers, resistance,
    voices, channels, sources, events, news, archive, fieldMessages
  };

  const provenanceSummary = Object.keys(collections).map(k => ({
    layer: k, provenance: collections[k].provenance,
    total: collections[k].count, real: collections[k].real, demo: collections[k].demo, note: collections[k].note
  }));

  /* §18 · Search indexes the normalized model in both languages. */
  const searchIndex = [];
  const idx = (kind, id, label, terms, route) => searchIndex.push({ kind, id, label, route: route || kind, terms: terms.filter(Boolean).map(t => String(t).toLowerCase()) });
  products.forEach(p => idx('product', p.name, p.name, [p.name, p.ai, p.categoryLabel, p.line], 'product'));
  opportunities.records.forEach(c => idx('case', c.id, c.issue + ' · ' + c.region, [c.issue, c.crop, c.region, c.latin, c.id], 'case'));
  voices.records.forEach(v => idx('voice', v.id, v.person || v.channel, [v.person, v.channel, v.crop, v.issue, v.title], 'voice'));
  futureSignals.records.forEach(f => idx('signal', f.id, f.issue + ' · ' + f.region, [f.issue, f.crop, f.region], 'signal'));
  researchers.records.forEach(r => idx('researcher', r.id, r.name, [r.name, r.org], 'person'));
  resistance.records.forEach(r => idx('resistance', r.id, r.species, [r.species, r.speciesIt, r.crop], 'science'));

  window.ITALY_APP_MODEL = {
    version: '2.0', compiled: '2026-09-02',
    PROVENANCE: P, referenceDate: REFERENCE_DATE, REF, daysFrom, provOf, isDemo,
    productDefinition: 'EXTERNAL_INTELLIGENCE_CORE', coreRequiresPrivateData: false,
    collections, provenanceSummary, searchIndex,
    products, productByKey, strengthFor,
    findProduct: (name) => productByKey[norm(name)] || null,
    counts: Object.keys(collections).reduce((a, k) => { a[k] = collections[k].count; return a; }, {})
  };
})();
