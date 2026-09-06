/* SINTONIA ITALY · STRUCTURAL CHECK SUITE
   ---------------------------------------------------------------------------
   The mandatory §32 checks, each one measured against the running pipeline or
   the source, never against a written report.

   Run:  node audit/run.mjs            (all checks, human table)
         node audit/run.mjs --json     (machine readable)
         node audit/run.mjs --only=D1  (one check)
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { mount, loadData, CLIENT, readPortal, extractLogic, extractMarkup, nullRate } from './lib/harness.mjs';
import { EXPECTED_BUILD_ID } from './ingestion-provenance.mjs';
import { scanAll, grepPackage, walkPackage } from './lib/scan.mjs';
import { isPortuguese, isEnglish, looksEnglish, collectStrings, cropKeyOf } from './lang.mjs';

const REFERENCE_DATE = '2026-09-02';

/* A check returns { pass, expected, measured, detail? }. */
export const CHECKS = [];
const check = (id, title, fn) => CHECKS.push({ id, title, fn });

/* ── 1 · the fixture is no longer a source of fact ────────────────────────── */

check('D1', 'CORE DATA-BEARING D.* READS = 0', () => {
  const r = scanAll();
  return {
    pass: r.counts.DATA_BEARING_CORE === 0,
    expected: 0,
    measured: r.counts.DATA_BEARING_CORE,
    detail: {
      total: r.counts.total,
      VISUAL_ONLY: r.counts.VISUAL_ONLY,
      EXPLICIT_DEMO: r.counts.EXPLICIT_DEMO,
      helpers: r.counts.helpers,
      aliases: r.aliases,
      worst: Object.entries(r.bySymbol)
        .filter(([, v]) => v.core)
        .sort((a, b) => b[1].core - a[1].core)
        .slice(0, 12)
        .map(([k, v]) => `${k}:${v.core}`),
      sample: r.dataBearing.slice(0, 8).map((x) => `${x.file}:${x.line} ${x.alias}.${x.symbol}`),
    },
  };
});

check('D2', 'Every downgraded D.* read carries a written reason', () => {
  const r = scanAll();
  const bare = r.reads.filter((x) => x.klass !== 'DATA_BEARING_CORE' && !x.isHelper && (!x.reason || x.reason.length < 8));
  return { pass: bare.length === 0, expected: 0, measured: bare.length,
    detail: bare.slice(0, 10).map((x) => `${x.file}:${x.line} ${x.symbol}`) };
});

check('D3', 'No second identifier is bound to the legacy fixture', () => {
  const r = scanAll();
  const extra = r.aliases.filter((a) => a !== 'D');
  return { pass: extra.length === 0, expected: '[D]', measured: JSON.stringify(r.aliases), detail: extra };
});

/* ── 2 · the model contract ───────────────────────────────────────────────── */

check('M1', 'ITALY_APP_MODEL builds with no load error', () => {
  const ctx = loadData();
  const errs = ctx.__loadErrors || [];
  return { pass: errs.length === 0 && !!ctx.ITALY_APP_MODEL, expected: 0, measured: errs.length, detail: errs };
});

check('M2', 'ONE canonical reference date (2026-09-02)', () => {
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL;
  /* A second clock is any Date built from a literal, or a bare new Date(), in
     application code. Deriving a Date from AM.REF / referenceDate is fine. */
  const hits = grepPackage(/new Date\(\s*(?:\)|\d|['"]\d)/, { codeOnly: true, files: ['portale.html', 'italy-app-model.js', 'italy-briefs.js', 'italy-demo-data.js'].map((f) => path.join(CLIENT, f)) })
    .filter((h) => !/REFERENCE_DATE|referenceDate|AM\.REF|M\(\)\.REF|\.REF\b/.test(h.text));
  return {
    pass: AM && AM.referenceDate === REFERENCE_DATE && hits.length === 0,
    expected: `${REFERENCE_DATE} · 0 second clocks`,
    measured: `${AM && AM.referenceDate} · ${hits.length} second clocks`,
    detail: hits.slice(0, 10).map((h) => `${h.file}:${h.line} ${h.text.slice(0, 120)}`),
  };
});

check('M3', 'Model exposes every V2.1 collection slot (empty is valid)', () => {
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const required = [
    'productsRegulatory', 'productsCommercial', 'productRelationships',
    'cropWindows', 'currentFieldSignals', 'cropEconomicWeight',
    'marketObservations', 'competitorActivities',
    'scienceRecords', 'researchers', 'resistance',
    'publicVoices', 'publicChannels',
    'regulatoryFuture', 'agrometConditions', 'futureEvents',
    'opportunities', 'futureSignals',
    'sources', 'events', 'news',
    'relationships', 'clientSafeCrossings',
  ];
  const have = AM.collections ? Object.keys(AM.collections) : [];
  const missing = required.filter((k) => !have.includes(k));
  return { pass: missing.length === 0, expected: `${required.length} slots`, measured: `${required.length - missing.length} present`, detail: missing };
});

check('M4', 'No core fact originates only in the fixture (model level)', () => {
  const r = scanAll(CLIENT, ['italy-app-model.js']);
  const core = r.reads.filter((x) => x.klass === 'DATA_BEARING_CORE' && !x.isHelper);
  return { pass: core.length === 0, expected: 0, measured: core.length,
    detail: core.map((x) => `line ${x.line}: D.${x.symbol}`) };
});

/* ── 3 · Future radar ─────────────────────────────────────────────────────── */

check('F1', 'Future demo scenarios are OFF by default', () => {
  const m = mount();
  const v = m.vals({ view: 'future' });
  const on = m.instance.state.showScenarios;
  return { pass: on === false, expected: 'false', measured: String(on),
    detail: { visibleSignalCount: (v.visibleSignals || []).length, futureTotal: v.futureTotal } };
});

check('F2', 'Real Future feed = APP.futureSignals, demo scenarios not counted', () => {
  const m = mount();
  const AM = m.AM;
  const v = m.vals({ view: 'future', showScenarios: false });
  const real = AM.collections.futureSignals.count;
  const shown = (v.sigAll || v.visibleSignals || []).length;
  return { pass: shown === real, expected: real, measured: shown,
    detail: { demoScenariosAvailable: AM.collections.futureScenarios.count } };
});

check('F3', 'A real Future card opens a real Future detail (no demo fallback)', () => {
  const m = mount();
  const AM = m.AM;
  const ids = AM.collections.futureSignals.records.map((r) => r.id);
  const bad = [];
  for (const id of ids) {
    const r = m.tryVals({ view: 'signal', signalId: id, showScenarios: false });
    if (!r.ok) { bad.push(`${id}: ${r.error}`); continue; }
    const v = r.vals;
    if (v.sgMissing) bad.push(`${id}: resolved to missing`);
    if (v.sg && v.sg.id && v.sg.id !== id) bad.push(`${id}: opened ${v.sg.id}`);
  }
  /* an unknown id must resolve to "missing", never to another record */
  const ghost = m.tryVals({ view: 'signal', signalId: 'NO-SUCH-SIGNAL', showScenarios: false });
  if (ghost.ok && ghost.vals.sgMissing !== true) bad.push('unknown id did not report missing');
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad };
});

check('F4', 'No core read of the demo signal fixture', () => {
  const r = scanAll();
  const core = r.reads.filter((x) => x.symbol === 'SIGNALS' && x.klass === 'DATA_BEARING_CORE');
  return { pass: core.length === 0, expected: 0, measured: core.length,
    detail: core.map((x) => `${x.file}:${x.line}`) };
});

/* ── 4 · Field Sales is inbound-only and inert ────────────────────────────── */

const snapshot = (AM) => JSON.stringify(AM.provenanceSummary) + '|' + JSON.stringify(AM.counts);

check('FS1', 'Field Sales demo mutates 0 core records', () => {
  const m = mount();
  const before = snapshot(m.AM);
  const v = m.vals({ view: 'field' });
  if (typeof v.simulateInbound === 'function') { v.simulateInbound(); v.simulateInbound(); }
  const v2 = m.vals({ view: 'field' });
  if (typeof v2.sendComposer === 'function') { m.instance.state.composerText = 'ruggine gialla su frumento in Veneto'; try { v2.sendComposer(); } catch (e) { /* inert */ } }
  const after = snapshot(m.AM);
  return { pass: before === after, expected: 'core unchanged', measured: before === after ? 'unchanged' : 'MUTATED', detail: before === after ? [] : ['provenance or counts changed after Field Sales demo actions'] };
});

check('FS2', 'Fake phone number occurrences = 0 (whole package)', () => {
  const hits = grepPackage(/\+39\s*00\s*000\s*0000|\+39 00 000 0000/);
  return { pass: hits.length === 0, expected: 0, measured: hits.length, detail: hits.slice(0, 5) };
});

check('FS3', 'Outbound Field Sales request = 0', () => {
  const hits = grepPackage(/Send your observations back|SEND FIELD INTELLIGENCE|Invia le tue osservazioni|send observations|Reply prompts/i, { codeOnly: true });
  return { pass: hits.length === 0, expected: 0, measured: hits.length, detail: hits.slice(0, 5) };
});

/* ── 5 · product as an entity ─────────────────────────────────────────────── */

check('P1', 'Product entity click opens Product Intelligence, not a radar filter', () => {
  const m = mount();
  const AM = m.AM;
  const name = AM.products[0] && AM.products[0].name;
  m.instance.openProduct(name);
  const st = m.instance.state;
  /* L'identita del prodotto non e la sua ortografia. La chiave di unione ora
     ignora ®, punti e spazi — perche il registro scrive NIMROD 250 EW dove il
     catalogo scrive NIMRODR 250 EW — quindi confrontare productId con il nome
     lettera per lettera misurava il formato della chiave, non la navigazione.
     Cio che questo controllo deve tenere e che il clic apra la scheda DI QUEL
     prodotto: si verifica risolvendola all'indietro. */
  const back = AM.findProduct(st.productId);
  const same = !!back && back.key === (AM.findProduct(name) || {}).key;
  return { pass: st.view === 'product' && same,
    expected: `view=product resolving back to ${name}`,
    measured: `view=${st.view} productId=${st.productId} resolves=${back ? back.name : 'NOTHING'}` };
});

check('P2', 'Product relationships do not come from the demo case fixture', () => {
  const r = scanAll(CLIENT, ['italy-app-model.js']);
  const fromCases = r.reads.filter((x) => x.symbol === 'CASES' && x.klass === 'DATA_BEARING_CORE');
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const rel = AM.collections && AM.collections.productRelationships;
  const usesVerdicts = fs.readFileSync(path.join(CLIENT, 'italy-app-model.js'), 'utf8').includes('ITALY_LABEL_VERDICTS');
  return {
    pass: fromCases.length === 0 && !!rel && usesVerdicts,
    expected: 'relationships from label audit, 0 demo-case reads',
    measured: `demoCaseReads=${fromCases.length} productRelationships=${rel ? rel.count : 'ABSENT'} readsLabelVerdicts=${usesVerdicts}`,
  };
});

check('P3', 'Absence is never rendered as "ADAMA has no product"', () => {
  /* The claim is forbidden as an ASSERTION. A sentence that forbids it — the
     absence rule itself — is the opposite of the defect and must survive. */
  const hits = grepPackage(/ADAMA (has |non )?(no|nessun) (product|prodotto)/i)
    .filter((h) => !/\b(not|never|non è|nao|NOT_FOUND|is not evidence|mai)\b/i.test(h.text));
  return { pass: hits.length === 0, expected: 0, measured: hits.length, detail: hits.slice(0, 5) };
});

/* ── 6 · search ───────────────────────────────────────────────────────────── */

check('S1', 'Search consumes APP.searchIndex', () => {
  const src = readPortal();
  const { code } = extractLogic(src);
  const uses = /searchIndex/.test(code);
  return { pass: uses, expected: 'searchIndex referenced in the logic', measured: uses ? 'yes' : 'no' };
});

check('S2', 'Search performs no manual scan of the fixture', () => {
  const m = mount();
  const v = m.vals({ view: 'radar', query: 'grano', committedQuery: 'grano' });
  const groups = v.searchGroups || v.sgroups || [];
  const r = scanAll();
  /* every fixture read inside the search region of the logic must be gone */
  const src = readPortal();
  const { startLine } = extractLogic(src);
  const searchCore = r.dataBearing.filter((x) => x.file === 'portale.html' && /sgp\(|searchGroups|committedQuery/.test(x.snippet));
  return { pass: searchCore.length === 0, expected: 0, measured: searchCore.length,
    detail: { groups: groups.length, offenders: searchCore.map((x) => `${x.line}: D.${x.symbol}`) } };
});

check('LG1', 'No screen states a general legal rule the package does not prove', () => {
  /* WHY_WATCH di IT-FUT-003 chiudeva con «una registrazione nazionale non
     sopravvive a un'approvazione UE scaduta»: una legge dichiarata universale
     che il pacchetto non prova e che non vale in generale — il Reg. 1107/2009
     prevede la proroga durante il rinnovo pendente e periodi di smaltimento
     alla revoca.

         SCADENZA UE != MANCATO RINNOVO
                     != INVALIDITA DELLA REGISTRAZIONE NAZIONALE
                     != RISCHIO COMMERCIALE

     L'osservazione resta; l'inferenza no, e dove il tema compare deve comparire
     anche la cautela. */
  const m = mount();
  const OVERCLAIM = /(non sopravvive a un'approvazione ue|does not survive an expired eu approval|registrazione nazionale non sopravvive|national registration does not survive)/i;
  const bad = [];
  let cards = 0, caveats = 0;
  for (const lang of ['it', 'en']) {
    const r = m.tryVals({ view: 'future', lang });
    if (!r.ok) { bad.push(`${lang}: future did not render`); continue; }
    for (const sgc of (r.vals.visibleSignals || [])) {
      cards++;
      if (OVERCLAIM.test(String(sgc.whyShort || ''))) bad.push(`${lang}·${sgc.id}: states the rule as universal`);
      if (sgc.hasEuCaveat) { caveats++; if (!String(sgc.euCaveat || '').trim()) bad.push(`${lang}·${sgc.id}: flags the caveat but shows nothing`); }
    }
  }
  /* NON-VACUITA · se non ha letto nessuna scheda, o se la cautela non compare
     mai, questo controllo non ha misurato niente. */
  if (!cards) bad.push('no signal cards were read');
  if (!caveats) bad.push('the EU-expiry caveat never appears — nothing was gated');
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 6) };
});

check('S3', 'Every search entry routes to a real entity that resolves', () => {
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL;
  const C = AM.collections;
  const resolvers = {
    product: (id) => !!AM.findProduct(id),
    case: (id) => C.opportunities.records.some((r) => r.id === id) || C.upstreamOpportunities.records.some((r) => r.id === id),
    voice: (id) => C.voices.records.some((r) => r.id === id),
    signal: (id) => C.futureSignals.records.some((r) => r.id === id) || C.futureScenarios.records.some((r) => r.id === id),
    researcher: (id) => C.researchers.records.some((r) => r.id === id),
    resistance: (id) => C.resistance.records.some((r) => r.id === id),
    window: (id) => C.windows.records.some((r) => r.id === id || r.windowId === id),
    source: (id) => C.sources.records.some((r) => r.id === id || r.sourceId === id),
    event: (id) => C.events.records.some((r) => r.id === id),
    news: (id) => C.news.records.some((r) => r.id === id),
    science: (id) => C.scienceRecords.records.some((r) => r.id === id),
    competitor: (id) => C.competitorActivities.records.some((r) => r.id === id),
    /* le due famiglie che prima non erano raggiungibili da nessuna
       superficie: si aprono attraverso l'archivio, con il proprio id. */
    bulletin: (id) => C.fieldBulletins.records.some((r) => r.id === id),
    fieldSignal: (id) => C.currentFieldSignals.records.some((r) => r.id === id),
    company: () => true,
    market: (id) => C.marketObservations.records.some((r) => r.id === id),
    archive: (id) => C.archive.records.some((r) => r.id === id),
    channel: (id) => C.channels.records.some((r) => r.id === id),
  };
  const bad = [];
  for (const e of AM.searchIndex) {
    const f = resolvers[e.kind];
    if (!f) { bad.push(`unknown kind ${e.kind}`); continue; }
    if (!f(e.id)) bad.push(`${e.kind}:${e.id} does not resolve`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { indexed: AM.searchIndex.length, kinds: [...new Set(AM.searchIndex.map((e) => e.kind))], bad: bad.slice(0, 10) } };
});

/* ── 7 · counts and provenance ────────────────────────────────────────────── */

check('N1', 'Nav counts match the active normalized collections', () => {
  const m = mount();
  const AM = m.AM;
  const v = m.vals({ view: 'radar' });
  const nav = v.nav || [];
  /* Checking three badges let a real one through: the opportunity badge showed
     29 — the canonical WINDOW count — standing in for a feed of 3. Every badge
     is checked by position now, because a badge nobody checks is one that
     drifts back to whatever number looks fuller. */
  const expect = [
    /* LA VOCE DELLA CASA. `casa.html` e una PAGINA, e la sua voce di menu
       stampa un numero solo quando le due catene — `italy-casa.js` e
       `meeting-surface` — concordano su BUILD_ID e sulle tre popolazioni.
       Il numero e quello delle OPPORTUNITA, non il totale dei 43. Quando non
       concordano la voce deve TACERE, e questo controllo lo vedrebbe come
       0 !== 13. */
    (() => { const CASA = m.ctx.ITALY_CASA && m.ctx.ITALY_CASA.OPPORTUNITA_ATTUALI;
             return CASA ? CASA.OPPORTUNITA : 0; })(),
    /* UN SOLO RADAR, E IL SUO NUMERO HA UNA SOLA FONTE LEGITTIMA:
       l'istantanea della riunione. La voce storica — servita dal pacchetto
       PRIMA della riconciliazione — non e piu nel menu, quindi qui sparisce
       anche il suo badge. Contare il radar da una collezione del modello
       sarebbe di nuovo un numero che sta al posto di un altro, che e
       esattamente il difetto per cui questo controllo esiste. */
    (() => { const s2 = m.ctx.MEETING_SURFACE && m.ctx.MEETING_SURFACE.build('it');
             return s2 ? s2.commercial.length : (m.ctx.MEETING_INTELLIGENCE || {}).TOTAL_CASES; })(),
    /* I SEGNALI NON HANNO PIU UN BADGE: non sono uno strumento, e la voce di
       primo livello e stata tolta. Restano raggiungibili da una riga in fondo
       al radar, e il loro numero non e un contatore di menu. */
    AM.collections.futureSignals.count,
    AM.collections.cropWindows.count,
    AM.collections.marketObservations.count,
    AM.collections.publicVoices.count,
    AM.collections.competitorActivities.count,
    AM.collections.scienceRecords.count,
    AM.collections.products.count,
    AM.collections.archive.count,
    AM.collections.sources.count,
  ];
  const bad = [];
  if (nav.length !== expect.length) bad.push(`nav has ${nav.length} entries, expected ${expect.length}`);
  nav.forEach((n, i) => {
    if (expect[i] !== undefined && n.count !== expect[i]) bad.push(`${n.label || i}: shows ${n.count}, model says ${expect[i]}`);
  });
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { nav: nav.map((n) => `${n.label}=${n.count}`), bad } };
});

check('N2', 'Data State panel reports APP provenance, not the fixture', () => {
  const m = mount();
  const AM = m.AM;
  const v = m.vals({ view: 'radar', showDataState: true });
  const rows = v.dataStateRows || v.dsRows || v.dataState || [];
  const r = scanAll();
  const offenders = r.dataBearing.filter((x) => /dataState|dsRows|dsCompetitor|dsArchive|dsField|layer:/.test(x.snippet));
  return {
    pass: offenders.length === 0 && Array.isArray(rows) && rows.length >= AM.provenanceSummary.length,
    expected: `>= ${AM.provenanceSummary.length} model layers, 0 fixture reads`,
    measured: `${Array.isArray(rows) ? rows.length : 'n/a'} rows, ${offenders.length} fixture reads`,
    detail: offenders.map((x) => `${x.line}: D.${x.symbol}`),
  };
});

check('N3', 'No manually maintained factual counter (D.KPI family)', () => {
  const r = scanAll();
  const kpi = r.dataBearing.filter((x) => /^(KPI|WINDOW_KPI|FIELD_KPI|REAL_STATS|WHAT_CHANGED)$/.test(x.symbol));
  return { pass: kpi.length === 0, expected: 0, measured: kpi.length,
    detail: kpi.map((x) => `${x.file}:${x.line} D.${x.symbol}`) };
});

/* ── 8 · referential integrity ────────────────────────────────────────────── */

check('R1', 'All normalized cross-linked IDs resolve', () => {
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL;
  const C = AM.collections;
  const sourceIds = new Set(C.sources.records.flatMap((s) => [s.id, s.sourceId]).filter(Boolean).map(String));
  const bad = [];
  const checkSources = (label, records, field) => {
    for (const r of records) {
      const ids = Array.isArray(r[field]) ? r[field] : r[field] ? [r[field]] : [];
      for (const id of ids) if (!sourceIds.has(String(id))) bad.push(`${label} ${r.id} -> source ${id}`);
    }
  };
  checkSources('window', C.windows.records, 'sourceIds');
  checkSources('voice', C.voices.records, 'sourceId');
  checkSources('science', C.scienceRecords.records, 'sourceId');
  checkSources('market', C.marketObservations.records, 'sourceId');
  checkSources('futureSignal', C.futureSignals.records, 'sourceIds');
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { knownSourceIds: sourceIds.size, sample: bad.slice(0, 12) } };
});

check('R2', 'A real entity never silently falls back to another entity', () => {
  const src = readPortal();
  const { code, startLine } = extractLogic(src);
  /* `.find(...) || SOMETHING[0]` is the silent-fallback shape: a lookup that
     misses opens a different record without telling anyone. */
  const bad = [];
  code.split('\n').forEach((line, i) => {
    const re = /\.find\([^)]*\)\s*\|\|\s*([A-Za-z_$][\w$.]*)\s*\[\s*0\s*\]/g;
    let m;
    while ((m = re.exec(line))) bad.push({ line: startLine + i, expr: m[0].slice(0, 120) });
  });
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 12) };
});

/* ── 9 · product law in the interface ─────────────────────────────────────── */

check('L1', 'No core UI requires private ADAMA data', () => {
  const hits = grepPackage(/sell-in|sell-out|sell in\b|CRM\b|internal stock|scorte interne|Customer purchase timing|order book|portafoglio ordini|INTERNAL ADAMA DATA|dati interni ADAMA/i, {
    codeOnly: true,
    files: ['portale.html', 'italy-briefs.js', 'italy-i18n.js', 'accesso.html', 'italy-market-pulse.js'].map((f) => path.join(CLIENT, f)),
  });
  return { pass: hits.length === 0, expected: 0, measured: hits.length,
    detail: hits.slice(0, 10).map((h) => `${h.file}:${h.line} ${h.match} — ${h.text.slice(0, 110)}`) };
});

check('L2', 'Italy reach is never promoted to Italy targeting', () => {
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL;
  const acts = AM.collections.competitorActivities.records;
  const reached = acts.filter((a) => a.geoClass === 'REACHED_IN_ITALY').length;
  const unresolved = acts.filter((a) => a.geoClass !== 'REACHED_IN_ITALY').length;
  const wrong = acts.filter((a) => a.italyReach && String(a.type).toUpperCase() !== 'PAID').length;
  return { pass: wrong === 0, expected: 0, measured: wrong,
    detail: { total: acts.length, REACHED_IN_ITALY: reached, notResolved: unresolved } };
});

check('L3', 'Taxonomic names reach the screen complete', () => {
  /* A grep for .split('(') cannot judge this: the parenthesis is often PART of
     the name. "Sorghum halepense (L.) Pers." carries its describing authority,
     and "Schoenoplectus (Scirpus) mucronatus" carries a synonym genus inside
     the binomial. Only a parenthetical that is prose — the upstream's own
     "(sinonimi na ficha: ...)" research note — may be dropped. So compare what
     renders against what the source published. */
  const m = mount();
  const ctx = loadData();
  const src = (ctx.ITALY_INGEST && ctx.ITALY_INGEST.RESISTANCE) || [];
  const bySpecies = {};
  src.forEach((r) => { if (r.ID) bySpecies[r.ID] = String(r.SPECIES || ''); });
  const strip = (s) => s.replace(/\s*\((?:sinonimi|sin[oó]nimos)\b[^)]*\)\s*/gi, ' ').replace(/\s+/g, ' ').trim();
  const bad = [];
  const seen = new Set();
  for (const sc of SCREENS) {
    const patch = Object.assign({ view: sc.view, lang: 'it' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
    const r = m.tryVals(patch);
    if (!r.ok) continue;
    for (const { path, value } of collectStrings(r.vals)) {
      if (!/speci|latin|scientific|gire/i.test(path)) continue;
      for (const [id, full] of Object.entries(bySpecies)) {
        if (seen.has(id + path)) continue;
        const want = strip(full);
        if (!want || want.length < 8) continue;
        /* a rendered value that is a PREFIX of the real name, cut at a
           parenthesis or an authority, is a truncation */
        if (value !== want && want.startsWith(value) && value.length >= 8 && want.length - value.length > 3) {
          seen.add(id + path);
          bad.push(`${sc.label} ${path}: "${value}" is a prefix of "${want}"`);
        }
      }
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
});

/* ── 10 · localization ────────────────────────────────────────────────────── */

check('I1', 'Italian is the default language and the switch does not reload', () => {
  const src = readPortal();
  const { code } = extractLogic(src);
  const defaultIt = /lang:\s*\(\(\)\s*=>\s*\{[^}]*'en'\s*\?\s*'en'\s*:\s*'it'/.test(code) || /=== 'en' \? 'en' : 'it'/.test(code);
  const reloads = /location\.reload|window\.location\s*=/.test(code);
  return { pass: defaultIt && !reloads, expected: 'it default, no reload', measured: `default=${defaultIt ? 'it' : 'UNKNOWN'} reload=${reloads}` };
});

check('PT1', 'No Portuguese research prose reaches any rendered screen', () => {
  const m = mount();
  const hits = [];
  let rendered = 0;
  const want = SCREENS.length * 2;
  for (const sc of SCREENS) {
    for (const lang of ['it', 'en']) {
      const patch = Object.assign({ view: sc.view, lang }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
      const r = m.tryVals(patch);
      if (!r.ok) continue;
      rendered++;
      for (const { path, value } of collectStrings(r.vals)) {
        /* A *Raw field is the published source text, kept beside the resolved
           value so nothing becomes untraceable. It is provenance, not display —
           and PT3 proves no markup binds one. */
        if (/(^|\.)[A-Za-z]*Raw(\[|$|\.)/.test(path)) continue;
        if (isPortuguese(value)) hits.push(`${sc.label}/${lang} ${path}: ${value.slice(0, 110)}`);
      }
    }
  }
  const uniqueHits = [...new Set(hits)];
  /* A language check that passes because nothing rendered is a false green —
     exactly the kind of empty pass this suite exists to prevent. */
  const vacuous = rendered < want;
  return {
    pass: uniqueHits.length === 0 && !vacuous,
    expected: `0 hits over ${want} renders`,
    measured: vacuous ? `${uniqueHits.length} hits but only ${rendered}/${want} rendered — INCONCLUSIVE` : `${uniqueHits.length} hits over ${rendered} renders`,
    detail: uniqueHits.slice(0, 14),
  };
});

check('PT4', 'No source reaches the model carrying a research note where its NAME should be', () => {
  const AM = loadData().ITALY_APP_MODEL;
  const records = ((AM.collections || {}).sources || {}).records || [];

  /* WHY THIS IS NOT COVERED BY PT1.
     PT1 walks the props a screen returns, and it reported 0 while 66 of 188
     source names were the analyst's Portuguese working notes. Two reasons, both
     measured. The Fonti screen returns ~24.800 strings and collectStrings()
     stops at 4.000, so the names were never reached; and the marker list did
     not carry this class of word, so the ones it did reach read as Italian.

         UNA REGOLA CHE MISURA L'USCITA DI UNO SCHERMO
         NON SA DIRE SE HA GUARDATO TUTTO.

     So this check does not render anything. It reads the collection itself —
     the single field that the Fonti list, the source detail title and its
     uppercased breadcrumb, the case source list, the Future-Radar cards and
     the FONTI group of the search all print — and it reads every row of it. */
  const isProse = (t) => /[.!?]\s+\p{Lu}/u.test(t) || (/[.!?]\s*$/.test(t) && t.length > 55);
  const bad = [];
  for (const r of records) {
    const n = r && r.name;
    if (typeof n !== 'string' || !n.trim()) { bad.push(`${r && r.id}: no printable name at all`); continue; }
    if (isPortuguese(n)) bad.push(`${r.id}: PORTUGUESE name "${n.slice(0, 90)}"`);
    else if (isProse(n)) bad.push(`${r.id}: RESEARCH PROSE as name "${n.slice(0, 90)}"`);
  }

  /* A CHECK THAT FINDS NOTHING TO LOOK AT HAS NOT PASSED.
     If the sources family ever comes up empty — a renamed collection, a family
     that failed to build, a harness that loaded no data — this check would
     report zero Portuguese names and be perfectly wrong. Nothing to inspect is
     itself the failure, and it says so instead of going green. */
  const vacuous = records.length === 0;
  return {
    pass: !vacuous && bad.length === 0,
    expected: '0 in >0 sources',
    measured: vacuous ? 'NO SOURCE RECORDS TO INSPECT — INCONCLUSIVE' : `${bad.length} of ${records.length} sources`,
    detail: vacuous ? ['AM.collections.sources.records is empty'] : bad.slice(0, 14),
  };
});

check('PT2', 'Every crop token that reaches a screen resolves to the canonical vocabulary', () => {
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL;
  const C = AM.collections;
  const tokens = [];
  const take = (label, recs, field) => (recs || []).forEach((r) => {
    const v = r[field];
    (Array.isArray(v) ? v : [v]).filter(Boolean).forEach((x) => tokens.push({ label, x }));
  });
  take('cropWindows', C.cropWindows.records, 'crop');
  take('opportunities', C.opportunities.records, 'crop');
  take('futureSignals', C.futureSignals.records, 'crop');
  take('publicVoices', C.publicVoices.records, 'crop');
  take('scienceRecords', C.scienceRecords.records, 'crop');
  take('news', C.news.records, 'crop');
  take('resistance', C.resistance.records, 'crop');
  take('competitorActivities', C.competitorActivities.records, 'crops');
  const bad = [];
  const scopes = {};
  for (const { label, x } of tokens) {
    const r = cropKeyOf(x);
    scopes[r.scope] = (scopes[r.scope] || 0) + 1;
    if (r.scope === 'UNMAPPED') bad.push(`${label}: ${String(x).slice(0, 70)}`);
    if (isPortuguese(x)) bad.push(`${label}: PORTUGUESE crop token "${String(x).slice(0, 70)}"`);
  }
  const uniqueBad = [...new Set(bad)];
  return { pass: uniqueBad.length === 0, expected: 0, measured: uniqueBad.length,
    detail: { scopes, bad: uniqueBad.slice(0, 12) } };
});

check('I2', 'Italian mode shows no accidental English in Future', () => {
  const m = mount();
  const v = m.vals({ view: 'future', lang: 'it' });
  const ENGLISH = /\b(days left|in \d+ days|no content|All crops|All issues|All regions|Portfolio check needed|Send|Search|Loading|Unknown|Unrecognised|real identity|demo profile|works|Recent activity|Related|Sources?|Evidence|Window open|Next cycle|Act now|Prepare|Watch)\b/;
  const walk = (v, seen = new Set(), out = [], p = '') => {
    if (out.length > 40 || v === null || v === undefined) return out;
    if (typeof v === 'string') { if (ENGLISH.test(v)) out.push(`${p}: ${v.slice(0, 90)}`); return out; }
    if (typeof v !== 'object' || seen.has(v)) return out;
    seen.add(v);
    for (const k of Object.keys(v)) { if (k === 'raw' || k === 'ui') continue; walk(v[k], seen, out, p ? `${p}.${k}` : k); }
    return out;
  };
  const hits = walk({ visibleSignals: v.visibleSignals, fStatuses: v.fStatuses, futureChips: v.futureChips, sigAll: v.sigAll });
  return { pass: hits.length === 0, expected: 0, measured: hits.length, detail: hits.slice(0, 12) };
});

/* ── 11 · the package itself ──────────────────────────────────────────────── */

check('B1', 'ADAMA Brandwell local design system is present', () => {
  const base = path.join(CLIENT, '_ds', 'adama-brandwell');
  const need = ['_ds_manifest.json', '_ds_bundle.js', 'styles.css',
    'tokens/base.css', 'tokens/colors.css', 'tokens/spacing.css', 'tokens/typography.css', 'tokens/patterns.css'];
  const missing = need.filter((f) => !fs.existsSync(path.join(base, f)));
  return { pass: missing.length === 0, expected: `${need.length} files`, measured: `${need.length - missing.length} present`, detail: missing };
});

check('B2', 'Every asset the HTML references exists on disk', () => {
  const missing = [];
  for (const p of walkPackage(CLIENT, ['.html'])) {
    const src = fs.readFileSync(p, 'utf8');
    const re = /(?:src|href)\s*=\s*["']([^"'#?]+)["']/g;
    let m;
    while ((m = re.exec(src))) {
      const ref = m[1];
      if (/^(https?:|data:|mailto:|javascript:)/.test(ref) || ref.includes('{{')) continue;
      const target = path.resolve(path.dirname(p), ref);
      if (!fs.existsSync(target)) missing.push(`${path.basename(p)} -> ${ref}`);
    }
  }
  return { pass: missing.length === 0, expected: 0, measured: missing.length, detail: missing.slice(0, 12) };
});

check('B3', 'No public CDN runtime dependency', () => {
  const hits = grepPackage(/unpkg\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare|esm\.sh/, { exts: ['.html', '.js'] });
  return { pass: hits.length === 0, expected: 0, measured: hits.length,
    detail: hits.slice(0, 10).map((h) => `${h.file}:${h.line} ${h.match}`) };
});

/* ── 12 · runtime smoke over every screen ─────────────────────────────────── */

export const SCREENS = [
  { view: 'radar', label: 'Opportunity list' },
  { view: 'case', label: 'Opportunity detail', pick: (AM) => ({ caseId: (AM.collections.upstreamOpportunities.records[0] || AM.collections.opportunities.records[0] || {}).id }) },
  { view: 'future', label: 'Future list' },
  { view: 'signal', label: 'Future detail', pick: (AM) => ({ signalId: (AM.collections.futureSignals.records[0] || {}).id }) },
  { view: 'windows', label: 'Crop Windows' },
  { view: 'window', label: 'Window detail', pick: (AM) => ({ windowId: (AM.collections.windows.records[0] || {}).id }) },
  { view: 'market', label: 'Market Pulse' },
  { view: 'voices', label: 'Voci dal Campo' },
  { view: 'competitors', label: 'Competitor feed' },
  { view: 'competitors', label: 'Competitor gallery', state: { compView: 'gallery' } },
  { view: 'competitors', label: 'Competitor events', state: { compView: 'events' } },
  { view: 'competitors', label: 'Competitor issue view', state: { compView: 'issue' } },
  { view: 'company', label: 'Competitor company', pick: (AM) => ({ companyId: (AM.collections.competitorActivities.records[0] || {}).company }) },
  { view: 'science', label: 'Scientific Intelligence' },
  { view: 'theme', label: 'Science theme', pick: (AM) => ({ themeId: (AM.collections.scienceThemes.records[0] || {}).id }) },
  { view: 'person', label: 'Researcher', pick: (AM) => ({ personId: (AM.collections.researchers.records[0] || {}).id }) },
  { view: 'portfolio', label: 'Portafoglio' },
  { view: 'product', label: 'Product Intelligence', pick: (AM) => ({ productId: (AM.products[0] || {}).name }) },
  { view: 'archive', label: 'Archive' },
  { view: 'archive', label: 'Archive detail', pick: (AM) => ({ archiveId: (AM.collections.archive.records[0] || {}).id }) },
  { view: 'sources', label: 'Sources' },
  { view: 'source', label: 'Source detail', pick: (AM) => ({ sourceId: (AM.collections.sources.records[0] || {}).id }) },
  { view: 'event', label: 'Event detail', pick: (AM) => ({ eventId: (AM.collections.events.records[0] || {}).id }) },
  { view: 'field', label: 'Field Sales demo' },
  { view: 'radar', label: 'Global search', state: { query: 'grano', committedQuery: 'grano' } },
  { view: 'brief', label: 'Action brief', pick: (AM) => ({ caseId: (AM.collections.opportunities.records[0] || {}).id, briefDept: 'MARKETING' }) },
  /* La superficie canonica della riunione entra nell'elenco degli schermi, cosi
     che OGNI controllo gia scritto — lingua, prop legate, liste, token interni —
     la misuri senza che nessuno debba ricordarsene. Un portone che non conosce
     una schermata la dichiara verde per silenzio. */
  { view: 'meeting', label: 'Canonical radar' },
  { view: 'mcase', label: 'Canonical opportunity', state: { mCaseId: 'OPP_5F31A63F844D' } },
  { view: 'mcase', label: 'Canonical opportunity · no primary', state: { mCaseId: 'OPP_75C37DED9160' } },
];

check('RT1', 'Every screen renders in Italian without crashing', () => {
  const m = mount();
  const fails = [];
  for (const sc of SCREENS) {
    const patch = Object.assign({ view: sc.view, lang: 'it' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
    const r = m.tryVals(patch);
    if (!r.ok) fails.push(`${sc.label} (${sc.view}): ${r.error}`);
  }
  return { pass: fails.length === 0, expected: `${SCREENS.length} screens`, measured: `${SCREENS.length - fails.length} ok`, detail: fails };
});

check('RT2', 'Every screen renders in English without crashing', () => {
  const m = mount();
  const fails = [];
  for (const sc of SCREENS) {
    const patch = Object.assign({ view: sc.view, lang: 'en' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
    const r = m.tryVals(patch);
    if (!r.ok) fails.push(`${sc.label} (${sc.view}): ${r.error}`);
  }
  return { pass: fails.length === 0, expected: `${SCREENS.length} screens`, measured: `${SCREENS.length - fails.length} ok`, detail: fails };
});

check('RT3', 'No screen renders the string "undefined" or "[object Object]"', () => {
  const m = mount();
  const bad = [];
  const walk = (v, seen, out, p) => {
    if (out.length > 30 || v === null || v === undefined) return;
    if (typeof v === 'string') { if (/undefined|\[object Object\]|NaN/.test(v)) out.push(`${p}: ${v.slice(0, 80)}`); return; }
    if (typeof v !== 'object' || seen.has(v)) return;
    seen.add(v);
    for (const k of Object.keys(v)) { if (k === 'raw') continue; walk(v[k], seen, out, p ? `${p}.${k}` : k); }
  };
  let rendered = 0;
  for (const sc of SCREENS) {
    const patch = Object.assign({ view: sc.view, lang: 'it' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
    const r = m.tryVals(patch);
    if (!r.ok) continue;
    rendered++;
    const out = [];
    walk(r.vals, new Set(), out, '');
    if (out.length) bad.push(`${sc.label}: ${out.slice(0, 3).join(' · ')}`);
  }
  /* A pass that comes from nothing rendering is a false green. */
  const vacuous = rendered < SCREENS.length;
  return { pass: bad.length === 0 && !vacuous, expected: `0 over ${SCREENS.length} screens`,
    measured: vacuous ? `${bad.length} but only ${rendered}/${SCREENS.length} rendered — INCONCLUSIVE` : `${bad.length} over ${rendered} screens`,
    detail: bad.slice(0, 12) };
});

check('RT4', 'Back returns to the previous portal state', () => {
  const m = mount();
  m.instance.setState({ view: 'radar' });
  m.instance.openProduct((m.AM.products[0] || {}).name);
  const fwd = m.instance.state.view;
  const canBack = typeof m.instance.back === 'function' || typeof m.instance.goBack === 'function';
  if (!canBack) return { pass: false, expected: 'a back handler exists', measured: 'none', detail: ['no back()/goBack() on the component'] };
  (m.instance.back || m.instance.goBack).call(m.instance);
  return { pass: m.instance.state.view === 'radar', expected: 'radar', measured: m.instance.state.view, detail: { forward: fwd } };
});

/* ── 13 · handoff readiness ───────────────────────────────────────────────── */

/* ── H · THE V2.1 INGEST ───────────────────────────────────────────────────
   H1 used to assert the OPPOSITE of what it asserts now: that no V2.1 file had
   been dropped into client/. It was a tripwire for a half-finished migration —
   the failure where the package lands, the model reads some of it, and nobody
   can tell which numbers are new.

   The migration happened. A tripwire against it would now fail forever and
   teach the suite to be ignored, so it is replaced by the question it was
   really protecting: IS the package ingested, whole, and identified?

       A GUARD THAT SURVIVES THE THING IT GUARDED AGAINST
       STOPS BEING A GUARD AND BECOMES NOISE. */
/* IL BUILD ATTESO NON SI SCRIVE DUE VOLTE.
   Questa costante era 'V21-99226fbb90dcdbc2' scritta a mano, e ha smesso di
   corrispondere nel momento in cui l'artefatto imbarcato e stato rigenerato dal
   pacchetto canonico di 55c2674. Un numero copiato in due file e un numero che
   prima o poi discorda con se stesso — ed e esattamente la malattia che questa
   ingestione e venuta a curare.

       CHI DICHIARA IL CONTRATTO E UNO SOLO.

   `audit/ingestion-provenance.mjs` e il portone che rifiuta il pacchetto stale:
   e li che vive l'attesa, e da li che H1 la legge. */
const V21_BUILD_ID = EXPECTED_BUILD_ID;

check('H1', 'Handoff V2.1 is ingested and identifies its build', () => {
  const ctx = loadData();
  const H = ctx.ITALY_HANDOFF_V21;
  const AM = ctx.ITALY_APP_MODEL;
  const bad = [];
  if (!H) bad.push('window.ITALY_HANDOFF_V21 absent');
  else if (H.buildId !== V21_BUILD_ID) bad.push(`BUILD_ID ${H.buildId}, expected ${V21_BUILD_ID}`);
  /* Ingested means the model CHOSE it, not merely that the file loaded. Every
     family below must report HANDOFF_V21 as the source it built from; one that
     silently kept the fixture is the exact half-migration this check exists for. */
  const mustBeV21 = [
    'productsRegulatory', 'productsCommercial', 'productRelationships',
    'activeIngredients', 'opportunities', 'sources', 'publicVoices',
    'competitorActivities', 'marketObservations', 'scienceRecords',
    'researchers', 'resistance', 'currentFieldSignals', 'news', 'futureEvents',
    'futureSignals', 'publicChannels', 'clientSafeCrossings', 'agrometConditions',
    'regulatoryFutureFacts', 'fieldBulletins', 'cropEconomics',
  ];
  for (const f of mustBeV21) {
    const c = AM && AM.collections[f];
    if (!c) { bad.push(`${f}: absent`); continue; }
    if (!/HANDOFF_V21/.test(String(c.source || ''))) bad.push(`${f}: built from ${c.source}`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 12) };
});

check('H2', 'The V2.1 universe counts are MEASURED, not declared', () => {
  /* The recovery brief quoted six reference numbers. They are asserted here
     against the MODEL, so the check fails if the ingest quietly drops rows —
     which is what the difference between 51 and 44 commercial products, or
     between 2.030 and 236 label pairs, would otherwise look like: nothing. */
  const AM = loadData().ITALY_APP_MODEL;
  const C = AM.collections;
  const bad = [];
  const eq = (label, got, want) => { if (got !== want) bad.push(`${label}: ${got}, expected ${want}`); };
  eq('commercial products', C.productsCommercial.count, 51);
  eq('regulatory products', C.productsRegulatory.count, 163);
  eq('label use pairs', C.productRelationships.count, 2030);
  eq('active substances', C.activeIngredients.count, 53);
  /* CROPS and TARGETS are the label corpus's own vocabulary, recounted from the
     pairs rather than read off a list anybody typed. */
  const crops = new Set(C.productRelationships.records.map((r) => r.cropOnLabel).filter(Boolean));
  const targets = new Set(C.productRelationships.records.map((r) => r.target).filter(Boolean));
  eq('distinct label crops', crops.size, 35);
  eq('distinct label targets', targets.size, 78);
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad };
});

check('H3', 'The opportunity engine reaches the screen without its bookkeeping', () => {
  /* 37 detected · 9 verified convergences · 28 to validate.
     And the four words the client must never read: CLIENT_SAFE,
     RENDERABLE_WITH_METHOD, EVIDENCE_DERIVED, FAILED_GATES. They are engine
     state, they decided the label, and then they were dropped — so this asserts
     they are ABSENT FROM THE OBJECT, not merely unbound by today's markup.
     A property that does not exist cannot be rendered by tomorrow's markup. */
  const AM = loadData().ITALY_APP_MODEL;
  const recs = AM.collections.opportunities.records;
  const bad = [];
  if (recs.length !== 37) bad.push(`opportunities: ${recs.length}, expected 37`);
  const verified = recs.filter((o) => o.convergence === 'VERIFIED_CONVERGENCE').length;
  const toValidate = recs.filter((o) => o.convergence === 'TO_VALIDATE').length;
  if (verified !== 9) bad.push(`verified convergences: ${verified}, expected 9`);
  if (toValidate !== 28) bad.push(`to validate: ${toValidate}, expected 28`);
  const FORBIDDEN = /^(clientSafe|renderableWithMethod|qaStatus|blockingGates|redTeamFindings|whyNotClientSafe|raw)$/;
  for (const o of recs) {
    for (const k of Object.keys(o)) if (FORBIDDEN.test(k)) bad.push(`${o.id} still carries ${k}`);
  }
  /* A rejected opportunity must not be reachable at all. The 17 the red team
     knocked out are not shipped, so this is checked as absence of the file's
     content rather than as a filter somebody could remove. */
  const H = loadData().ITALY_HANDOFF_V21;
  if (H && H.opportunityRejections) bad.push('rejected opportunities were shipped to the browser');
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
});


check('H4', 'Engine bookkeeping never reaches a rendered screen', () => {
  /* H3 asserts the four words are absent from the opportunity OBJECT. This one
     asks the harder question about every other family: the model still carries
     QA_STATUS and EVIDENCE_STATUS on 6.876 records, because the provenance
     panel is built on them and deleting them would blind it.

     So the test is not «does the value exist in the render context» — it does,
     and it should. It is «can the template put it in front of a reader».

         UN VALORE CHE NESSUN BINDING NOMINA NON È MOSTRATO.
         Un valore che un binding nomina è mostrato, sempre, un giorno.

     Two questions, both measured against the MARKUP, which is the half of the
     file that renders:
       1 · the markup must not name any of the four, nor the props that hold
           them — so no expression can resolve to one;
       2 · nothing the markup DOES bind may contain one, which catches the value
           arriving through a label, a chip or a search row instead of directly.

     And one phrasing, not a token: 37 may be shown as detected and 9 as
     verified convergences, but «37 confermate» / «37 confirmed» is forbidden —
     it would round a convergence we drew into a fact somebody else established. */
  const html = readPortal();
  const markup = extractMarkup(html);
  const NAMES = ['CLIENT_SAFE', 'RENDERABLE_WITH_METHOD', 'EVIDENCE_DERIVED', 'FAILED_GATES',
    'clientSafe', 'renderableWithMethod', 'qaStatus', 'blockingGates', 'redTeamFindings'];
  const bad = NAMES.filter((n) => markup.includes(n)).map((n) => `the markup names ${n}`);

  /* every identifier the markup binds, at any depth of an expression */
  const bound = new Set();
  let mm;
  const re = /\{\{\s*([A-Za-z_$][\w$.]*)/g;
  while ((mm = re.exec(markup))) mm[1].split('.').forEach((seg) => bound.add(seg));

  const m = mount();
  const FORBIDDEN = /(CLIENT_SAFE|RENDERABLE_WITH_METHOD|EVIDENCE_DERIVED|FAILED_GATES)/;
  let rendered = 0;
  for (const lang of ['it', 'en']) {
    for (const sc of SCREENS) {
      const patch = Object.assign({ view: sc.view, lang }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
      const r = m.tryVals(patch);
      if (!r.ok) continue;
      rendered++;
      for (const { path, value } of collectStrings(r.vals)) {
        const leaf = String(path).split('.').pop().replace(/\[\d+\]$/, '');
        if (bound.has(leaf) && FORBIDDEN.test(value)) bad.push(`${lang} ${sc.label} ${path}: ${value.slice(0, 60)}`);
        if (/\b37\s+(confermate|confirmed)\b/i.test(value)) bad.push(`${lang} ${sc.label} ${path}: presents 37 as confirmed`);
      }
    }
  }
  const uniq = [...new Set(bad)];
  return { pass: uniq.length === 0 && rendered > 0, expected: 0, measured: uniq.length,
    detail: uniq.slice(0, 10) };
});

check('W1', 'The 29 canonical crop windows are never collapsed to the 7 field readings', () => {
  /* IL PACCHETTO V2.1 HA UN FILE CHIAMATO CROP-WINDOWS.json. NON SONO LE FINESTRE.
     Sono le sette letture per coltura x avversita — gli stessi IT-WIN-001..007
     che hanno sempre alimentato currentFieldSignals — mentre le 29 finestre
     agronomiche auditate vivono nel contratto canonico, che il V2.1 non
     sostituisce e non contiene.

     Due universi, due domande diverse: «quando la coltura ha bisogno di
     protezione» non e «cosa si e letto nel campo». Un ingest che leggesse il
     nome del file al posto del contenuto scambierebbe 29 finestre per 7
     letture, e nulla si romperebbe: il portale mostrerebbe sette righe dove ne
     mostrava ventinove, tutte vere, e nessun conteggio andrebbe in rosso.

         LA PERDITA PIU CARA E QUELLA CHE LASCIA IL RESTO COERENTE.

     Peggio: i due spazi di identificatori distano UNO ZERO — IT-WIN-0001 le
     canoniche, IT-WIN-001 le letture. Una giunzione distratta li fonde senza
     sollevare nulla, quindi qui si controlla anche che non si tocchino. */
  const AM = loadData().ITALY_APP_MODEL;
  const C = AM.collections;
  const bad = [];
  const cw = C.cropWindows, fs = C.currentFieldSignals;

  if (!cw) bad.push('cropWindows absent');
  else {
    if (cw.count !== 29) bad.push(`canonical crop windows: ${cw.count}, expected 29`);
    /* La provenienza e il punto: se un giorno arrivano dal pacchetto, sono le
       letture travestite da finestre. */
    if (/HANDOFF_V21/.test(String(cw.source || ''))) {
      bad.push(`cropWindows now built from ${cw.source} — the field readings have replaced the canonical windows`);
    }
  }
  if (!fs) bad.push('currentFieldSignals absent');
  else if (fs.count !== 7) bad.push(`field readings: ${fs.count}, expected 7`);

  /* Gli id non devono incontrarsi mai. */
  if (cw && fs) {
    const idsW = new Set(cw.records.map((r) => String(r.id)));
    const shared = fs.records.filter((r) => idsW.has(String(r.id))).map((r) => r.id);
    if (shared.length) bad.push(`id spaces collided: ${shared.join(', ')}`);
  }

  /* E dove il portale RAPPRESENTA quell'universo, deve rappresentarlo intero:
     la riga di navigazione e il calendario contano 29, non 7. */
  const m = mount();
  const v = m.vals({ view: 'windows', lang: 'it' });
  const navW = (v.nav || []).find((n) => /finestre/i.test(String(n.label || '')));
  if (!navW) bad.push('the windows nav entry is gone');
  else if (navW.count !== 29) bad.push(`nav shows ${navW.count} windows, expected 29`);
  if (C.windowCalendarRows && C.windowCalendarRows.count !== 29) {
    bad.push(`window calendar rows: ${C.windowCalendarRows.count}, expected 29`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad };
});

check('W2', 'The red team downgrades; it is not a second population', () => {
  /* I 17 casi che il red team ha abbattuto sono un SOTTOINSIEME dei 28 «da
     validare», non righe nascoste in piu. Sommarli — 37 + 17 — inventerebbe 54
     oggetti dove ne esistono 37, ed e un errore facile da commettere in un
     rapporto, perche il file si chiama REJECTIONS.

         RESPINTA QUI VUOL DIRE DECLASSATA, NON CANCELLATA.

     Quindi: ogni id declassato esiste fra i 37, nessuno di essi e verificato, e
     tutti stanno dentro i 28. Se un giorno un declassato comparisse fra i nove,
     il portone lo direbbe qui invece che il cliente sullo schermo. */
  const AM = loadData().ITALY_APP_MODEL;
  const recs = AM.collections.opportunities.records;
  const rej = JSON.parse(fs.readFileSync(path.join(CLIENT, '..', '..', 'build',
    'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST', 'OPPORTUNITY-REJECTIONS.json'), 'utf8'));
  const ids = (rej.REJEICOES || []).map((r) => r.ID).filter(Boolean);
  const byId = new Map(recs.map((o) => [o.id, o]));
  const bad = [];
  if (ids.length !== 17) bad.push(`downgraded cases: ${ids.length}, expected 17`);
  const missing = ids.filter((id) => !byId.has(id));
  if (missing.length) bad.push(`${missing.length} downgraded ids are NOT among the 37 — they became a second population`);
  const verified = ids.filter((id) => byId.get(id) && byId.get(id).convergence === 'VERIFIED_CONVERGENCE');
  if (verified.length) bad.push(`downgraded but shown as verified: ${verified.join(', ')}`);
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad : [`17 downgraded ⊆ 28 to-validate ⊂ 37 total`] };
});

check('C1', 'A fallback label never becomes a factual pairing', () => {
  /* Una scheda senza bersaglio agronomico ripiega sull'ARCHETIPO per il
     titolo, ed e giusto: dice perche il caso esiste. Ma quel ripiego era
     finito dentro una frase di fatto — «nessuna posizione di etichetta ADAMA
     confermata per Vite × MOMENTO DI MERCATO» — che interroga l'audit su una
     coppia che non esiste e ne riporta l'esito negativo. Max lo legge e chiede
     che cosa sia «Vite per Momento di Mercato». Non c'e una buona risposta.

         UN RIPIEGO PUO STARE IN UN TITOLO.
         IN UNA FRASE DI FATTO DIVENTA UNA DOMANDA INVENTATA.

     Il soggetto di quella frase deve contenere solo cio che il caso ha: la
     coppia coltura × bersaglio dove il bersaglio esiste, la sola coltura dove
     non esiste. Mai un archetipo. */
  const m = mount();
  const AM = m.AM;
  const ARCH = /(PRESSIONE IN CAMPO|MOMENTO DI MERCATO|APERTURA COMPETITIVA|PREPARAZIONE NORMATIVA|DALLA SCIENZA AL CAMPO|RESISTENZA E MECCANISMO|FIELD PRESSURE|MARKET MOMENT|COMPETITIVE OPENING|REGULATORY PREPARATION|SCIENCE TO FIELD|RESISTANCE AND MODE)/i;
  const bad = [];
  for (const lang of ['it', 'en']) {
    for (const o of AM.collections.opportunities.records) {
      const r = m.tryVals({ view: 'case', caseId: o.id, lang });
      if (!r.ok) { bad.push(`${lang} ${o.id}: detail did not render`); continue; }
      const cs = r.vals.cs || {};
      const subj = String(cs.absenceSubject || '');
      if (ARCH.test(subj)) bad.push(`${lang} ${o.id}: absence subject names an archetype — "${subj}"`);
      /* e una coppia si scrive solo quando ci sono due termini */
      if (subj.includes('×') && subj.split('×').filter((x) => x.trim()).length < 2) {
        bad.push(`${lang} ${o.id}: dangling pairing — "${subj}"`);
      }
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 8) };
});

check('C2', 'Every crop and issue that reaches a screen has a label in that language', () => {
  /* «Pear» compariva nell'interfaccia italiana. Non era una fuga di prosa —
     PT1 e I6 non potevano vederla — ma il NOME CANONICO di una coltura che la
     tabella di interfaccia non conosceva, restituito da `cl()` cosi com'e.
     Kiwi cadeva giusto per caso, perche in italiano si scrive uguale.

         UNA TABELLA CHE NON CONOSCE UNA CHIAVE NON FALLISCE:
         RESTITUISCE LA CHIAVE. ED E COSI CHE L'INGLESE ARRIVA A SCHERMO.

     Le colture del V2.1 sono venti e le avversita ventiquattro: insiemi chiusi,
     quindi si puo esigere copertura totale invece di sperarla. In inglese il
     nome canonico E la parola giusta, quindi li si controlla che esista, non
     che sia tradotto. */
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL;
  const I18N = ctx.SINTONIA_I18N || {};
  const crops = new Set(), issues = new Set();
  for (const f of ['opportunities', 'productRelationships', 'cropWindows', 'resistance',
    'fieldBulletins', 'currentFieldSignals', 'news', 'publicVoices']) {
    for (const r of (AM.collections[f] || { records: [] }).records) {
      if (r.crop) crops.add(r.crop);
      (r.cropKeys || []).forEach((c) => crops.add(c));
      if (r.issue) issues.add(r.issue);
    }
  }
  const bad = [];
  const T = (I18N.it || {});
  for (const c of crops) if (!(T.CROPS || {})[c] && /^[A-Z][a-z]+( [A-Z]?[a-z]+)*$/.test(c)) {
    /* un nome canonico inglese senza riga italiana esce in inglese */
    if (!/^(Kiwi|Triticale|Diabrotica|Echinochloa|Amaranthus|Lolium|Septoria|Botrytis|Cercospora|Fusarium)$/.test(c)) {
      bad.push(`IT has no crop label for "${c}"`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10) : [`${crops.size} crops · ${issues.size} issue labels reach a screen`] };
});

check('O1', 'The same opportunity ids reach the package, the handoff, the model and the screen', () => {
  /* Confronta INSIEMI DI ID, non totali: due insiemi della stessa dimensione
     non sono lo stesso insieme, e un conteggio uguale a ogni frontiera non
     dimostra che sia passata la stessa popolazione.

     La frontiera del DOM vive in `audit/opportunity-trace.mjs`, che apre un
     browser vero; qui restano le quattro che si misurano senza. */
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL;
  const pkg = JSON.parse(fs.readFileSync(path.join(CLIENT, '..', '..', 'build',
    'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST', 'OPPORTUNITIES.json'), 'utf8'));

  const A = pkg.RECORDS.map((r) => r.ID);
  const Apub = pkg.RECORDS.filter((r) => r.RENDERABLE_WITH_METHOD === true).map((r) => r.ID);
  const B = ((ctx.ITALY_HANDOFF_V21 || {}).opportunities || []).map((r) => r.ID);
  const C = AM.collections.opportunities.records.map((r) => r.id);
  const Cpub = AM.collections.opportunities.records
    .filter((r) => r.convergence === 'VERIFIED_CONVERGENCE').map((r) => r.id);
  const m = mount();
  const D = (m.vals({ view: 'radar', lang: 'it', showAll: true }).visibleCases || []).map((c) => c.id);
  const Dpub = (m.vals({ view: 'radar', lang: 'it', showAll: true }).visibleCases || [])
    .filter((c) => c.convergence === 'VERIFIED_CONVERGENCE').map((c) => c.id);

  const bad = [];
  const same = (n1, a, n2, b) => {
    const sa = new Set(a), sb = new Set(b);
    const lost = [...sa].filter((x) => !sb.has(x));
    const gained = [...sb].filter((x) => !sa.has(x));
    if (lost.length) bad.push(`${n1}→${n2} loses ${lost.length}: ${lost.slice(0, 5).join(', ')}`);
    if (gained.length) bad.push(`${n1}→${n2} invents ${gained.length}: ${gained.slice(0, 5).join(', ')}`);
  };
  same('package', A, 'handoff', B);
  same('handoff', B, 'model', C);
  same('model', C, 'screen', D);
  same('package.publishable', Apub, 'model.publishable', Cpub);
  same('model.publishable', Cpub, 'screen.publishable', Dpub);
  if (!Apub.length) bad.push('the canonical package authorises no publishable case at all');

  /* E la ragione per cui questa missione e esistita: pubblicabile deve voler
     dire VISIBILE APRENDO, non raggiungibile dopo un clic su «vedi tutte». */
  const firstPage = (mount().vals({ view: 'radar', lang: 'it' }).visibleCases || []).map((c) => c.id);
  const buried = Apub.filter((id) => !firstPage.includes(id));
  if (buried.length) bad.push(`${buried.length} publishable case(s) are not on the first page: ${buried.slice(0, 5).join(', ')}`);

  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad : [`${A.length} ids · ${Apub.length} publishable · identical at every boundary`] };
});

/* ── 14 · the template contract ───────────────────────────────────────────
   renderVals() is only half the render. The markup binds ~1200 expressions by
   name, and the runtime degrades a missing sc-for list to an empty array with
   a console warning — so a prop that quietly disappears does not crash, it just
   stops showing. That is exactly the failure this migration could ship without
   noticing, so the binding contract is checked explicitly. */

function markupBindings() {
  const mk = extractMarkup(readPortal());
  /* every {{ ... }} expression, plus the loop variables sc-for introduces */
  const roots = new Set();
  const loopVars = new Set();
  let m;
  const asRe = /sc-for\b[^>]*\bas="([^"]+)"/g;
  while ((m = asRe.exec(mk))) loopVars.add(m[1]);
  const exprRe = /\{\{\s*([A-Za-z_$][\w$]*)/g;
  while ((m = exprRe.exec(mk))) roots.add(m[1]);
  const forRe = /sc-for\s+list="\{\{\s*([A-Za-z_$][\w$]*)\s*\}\}"/g;
  const lists = new Set();
  while ((m = forRe.exec(mk))) lists.add(m[1]);
  return { roots, loopVars, lists };
}

check('MK1', 'Every prop the markup binds is still returned by the render', () => {
  const { roots, loopVars } = markupBindings();
  const m = mount();
  const provided = new Set();
  for (const sc of SCREENS) {
    const patch = Object.assign({ view: sc.view, lang: 'it' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
    const r = m.tryVals(patch);
    if (!r.ok) continue;
    Object.keys(r.vals).forEach((k) => provided.add(k));
  }
  const LITERAL = new Set(['true', 'false', 'null', 'undefined']);
  const missing = [...roots].filter((k) => !loopVars.has(k) && !provided.has(k) && !LITERAL.has(k)).sort();
  return { pass: missing.length === 0, expected: 0, measured: missing.length,
    detail: { bound: roots.size, loopVars: loopVars.size, provided: provided.size, missing: missing.slice(0, 25) } };
});

check('MK2', 'Every sc-for list resolves to an array on the screen that owns it', () => {
  const { lists, loopVars } = markupBindings();
  const m = mount();
  const seen = {};
  for (const sc of SCREENS) {
    const patch = Object.assign({ view: sc.view, lang: 'it' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
    const r = m.tryVals(patch);
    if (!r.ok) continue;
    for (const name of lists) {
      if (loopVars.has(name)) continue;
      const v = r.vals[name];
      if (Array.isArray(v)) seen[name] = 'array';
      else if (seen[name] !== 'array') seen[name] = v === undefined ? 'undefined' : typeof v;
    }
  }
  const bad = Object.entries(seen).filter(([, t]) => t !== 'array').map(([k, t]) => `${k}: ${t}`);
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { checked: Object.keys(seen).length, bad: bad.slice(0, 25) } };
});


check('PT3', 'No *Raw traceability field is ever bound by the markup', () => {
  /* PT1 exempts *Raw props because they carry the published source text for
     traceability. That exemption is only safe while nothing renders them, so
     the exemption is itself checked. */
  const mk = extractMarkup(readPortal());
  const bad = [];
  const re = /\{\{\s*([A-Za-z_$][\w$.]*)\s*\}\}/g;
  let m;
  while ((m = re.exec(mk))) if (/Raw$/.test(m[1]) || /Raw\./.test(m[1])) bad.push(m[1]);
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: [...new Set(bad)] };
});


check('I3', 'document lang follows the interface language, including on reload', () => {
  /* A returning visitor never clicks the switch: their stored preference goes
     straight into state. The attribute has to follow the state, not the click,
     or the page is served as Italian while rendering English. */
  const m = mount();
  const doc = m.ctx.document;
  m.vals({ view: 'radar', lang: 'en' });
  const afterEn = doc.documentElement.lang;
  m.vals({ view: 'radar', lang: 'it' });
  const afterIt = doc.documentElement.lang;
  const ok = afterEn === 'en' && afterIt === 'it';
  return { pass: ok, expected: 'en then it', measured: `${afterEn} then ${afterIt}` };
});

check('I4', 'No hard-coded English left in the Italian interface chrome', () => {
  /* The markup carries literals the i18n layer never sees — a placeholder, a
     badge, a button. Measured by reading the template, not the props. */
  const mk = extractMarkup(readPortal());
  const bad = [];
  const re = /(?:placeholder|title|aria-label)="([^"{}]{3,60})"/g;
  let m2;
  while ((m2 = re.exec(mk))) if (isEnglish(m2[1]) || /^[A-Z][a-z]+ [a-z]+/.test(m2[1])) bad.push(m2[1]);
  /* bare English words sitting as element text between tags */
  const txt = /> *([A-Z][a-z]+(?: [a-z]+){1,4}) *</g;
  while ((m2 = txt.exec(mk))) if (isEnglish(m2[1])) bad.push(m2[1]);
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: [...new Set(bad)].slice(0, 15) };
});


check('I5', 'Italian interface strings are actually Italian', () => {
  /* Two failure shapes the props-level check cannot see, both measured in this
     package: an Italian value that is really English ("Intelligence
     Scientifica"), and an entry where it and en are the same string because the
     translation was never written. Codes, proper nouns and Latin names are
     legitimately identical, so those are excluded by shape. */
  const ctx = loadData();
  const I18N = ctx.SINTONIA_I18N || {};
  const it = I18N.it || {}, en = I18N.en || {};
  const flat = (o, p = '', out = {}) => {
    for (const k of Object.keys(o || {})) {
      const v = o[k];
      if (typeof v === 'string') out[p ? `${p}.${k}` : k] = v;
      else if (v && typeof v === 'object' && !Array.isArray(v)) flat(v, p ? `${p}.${k}` : k, out);
    }
    return out;
  };
  const fit = flat(it), fen = flat(en);
  const PROPER = /^[A-Z0-9 ·§+\-/&.]+$/;            /* a code or an all-caps token */
  const SHORT = (s) => s.trim().split(/\s+/).length < 2;
  const bad = [];
  for (const [k, v] of Object.entries(fit)) {
    if (!v || PROPER.test(v) || SHORT(v)) continue;
    if (isEnglish(v)) bad.push(`it.${k} reads English: "${v.slice(0, 60)}"`);
    else if (fen[k] && fen[k] === v && v.length > 12) bad.push(`it.${k} === en.${k}: "${v.slice(0, 60)}"`);
  }
  /* CROPS / ISSUES / WSTATUS and friends are translation MAPS keyed by the
     canonical English term. They exist only on the Italian side by design: in
     English the key is already the answer. */
  const MAP_NS = /^(CROPS|ISSUES|WSTATUS|DSTATE|OBSCLASS|PSTATE|ARCHTYPES|SRCTYPES|FSTATUS|EVCHIP|WSTATE|months|REGIONS)./;
  const missing = Object.keys(fen).filter((k) => !(k in fit) && !MAP_NS.test(k));
  const extra = Object.keys(fit).filter((k) => !(k in fen) && !MAP_NS.test(k));
  return {
    pass: bad.length === 0 && missing.length === 0 && extra.length === 0,
    expected: '0 English-in-Italian, 0 key gaps',
    measured: `${bad.length} suspect · ${missing.length} missing in it · ${extra.length} missing in en`,
    detail: [...bad.slice(0, 10), ...missing.slice(0, 6).map((k) => `only in en: ${k}`), ...extra.slice(0, 6).map((k) => `only in it: ${k}`)],
  };
});


check('DS1', 'Turning demo scenarios ON changes no real count', () => {
  /* §17 · The 56 future scenarios and the 29 presentation cases may be shown
     behind an explicit, default-off mode. What they may never do is move a real
     number. Measured by diffing every nav badge, every KPI and every Data State
     row with the mode off and on. */
  const m = mount();
  const snap = (on) => {
    const v = m.vals({ view: 'radar', showScenarios: on, lang: 'it' });
    return {
      nav: (v.nav || []).map((n) => n.count),
      kpi: (v.kpis || []).map((k) => k.value),
      state: (v.dataState || []).map((r) => [r.layer, r.real, r.derived]),
      counts: JSON.stringify(m.AM.counts),
      prov: JSON.stringify(m.AM.provenanceSummary.map((p) => [p.layer, p.real, p.derived])),
    };
  };
  const off = snap(false);
  const on = snap(true);
  const bad = [];
  off.nav.forEach((n, i) => { if (n !== on.nav[i]) bad.push(`nav[${i}]: ${n} -> ${on.nav[i]}`); });
  off.kpi.forEach((n, i) => { if (n !== on.kpi[i]) bad.push(`kpi[${i}]: ${n} -> ${on.kpi[i]}`); });
  if (off.counts !== on.counts) bad.push('AM.counts changed');
  if (off.prov !== on.prov) bad.push('provenance real/derived changed');
  if (JSON.stringify(off.state) !== JSON.stringify(on.state)) bad.push('Data State real/derived changed');
  /* and the mode must actually do something, or the check is vacuous */
  const vOff = m.vals({ view: 'radar', showScenarios: false });
  const vOn = m.vals({ view: 'radar', showScenarios: true });
  /* The radar paginates at 12 with a 'view all' toggle, so BOTH lists are 12
     long as soon as there are more than 12 real opportunities — which there now
     are, 37 of them. Comparing lengths therefore called a working toggle
     vacuous. What the guard actually means is that the mode must put DIFFERENT
     records on the screen, so that is what it compares. */
  const idsOff = (vOff.filtered || vOff.visibleCases || []).map((c) => c.id);
  const idsOn = (vOn.filtered || vOn.visibleCases || []).map((c) => c.id);
  const same = idsOff.length === idsOn.length && idsOff.every((x, i) => x === idsOn[i]);
  if (same) bad.push(`the toggle changes nothing (${idsOff.length} identical cases) — check is vacuous`);
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { casesOff: idsOff.length, casesOn: idsOn.length, changed: !same, bad } };
});

check('DS2', 'A demo scenario is never counted as a real record', () => {
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL;
  const C = AM.collections;
  const bad = [];
  for (const k of ['futureScenarios', 'opportunityScenarios', 'fieldMessages']) {
    const c = C[k];
    if (!c) { bad.push(`${k} missing`); continue; }
    if (c.real > 0) bad.push(`${k}: ${c.real} records counted as real`);
    if (!/DEMO/.test(String(c.provenance))) bad.push(`${k}: provenance is ${c.provenance}`);
  }
  /* and no real collection may contain a record whose provenance is a demo class */
  for (const [k, c] of Object.entries(C)) {
    if (/Scenario|fieldMessages/.test(k)) continue;
    const leaked = (c.records || []).filter((r) => AM.isDemo(r, c.provenance)).length;
    if (leaked) bad.push(`${k}: ${leaked} demo-provenance records inside a real collection`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
});


check('MK3', 'Every i18n key the markup binds resolves in both languages', () => {
  /* MK1 only proves the `t` object is returned. An agent replacing a hardcoded
     English literal with {{ t.someKey }} and forgetting to add the string
     leaves a BLANK LABEL over a populated value — worse than the English it
     replaced, because the reader has to guess what the number means. Measured
     on the real render, per language. */
  const mk = extractMarkup(readPortal());
  const keys = new Set();
  const re = /\{\{\s*t\.([A-Za-z_$][\w$]*)/g;
  let m;
  while ((m = re.exec(mk))) keys.add(m[1]);
  /* `t` is also a common sc-for alias; those are not i18n keys */
  const aliases = new Set();
  const asRe = /sc-for\b[^>]*\bas="t"/g;
  if (asRe.test(mk)) {
    const loopKeys = /\{\{\s*t\.([A-Za-z_$][\w$]*)/g;
    /* keep it simple and conservative: a key that exists in neither locale AND
       appears only inside an sc-for as="t" region is treated as a loop field */
    const regions = mk.split(/<sc-for\b[^>]*\bas="t"[^>]*>/).slice(1).map((s) => s.split('</sc-for>')[0]);
    for (const r of regions) { let mm; loopKeys.lastIndex = 0; while ((mm = loopKeys.exec(r))) aliases.add(mm[1]); }
  }
  const m2 = mount();
  const langs = ['it', 'en'];
  const resolved = {};
  for (const lang of langs) {
    const v = m2.vals({ view: 'radar', lang });
    resolved[lang] = v.t || {};
  }
  const missing = [];
  for (const k of keys) {
    if (aliases.has(k)) continue;
    const bad = langs.filter((l) => resolved[l][k] === undefined || resolved[l][k] === '');
    if (bad.length) missing.push(`t.${k} (${bad.join(',')})`);
  }
  return { pass: missing.length === 0, expected: 0, measured: missing.length,
    detail: { bound: keys.size, loopAliases: aliases.size, missing: missing.slice(0, 25) } };
});

check('MK4', 'No hardcoded English text node left in the Italian template', () => {
  /* renderVals() is the only surface the props-level checks can see. A literal
     sitting between two tags never becomes a prop, so 222 English strings sat
     in the Italian interface with every language check green. */
  const mk = extractMarkup(readPortal());
  const bad = [];
  /* text between tags, ignoring interpolations, attributes and style blocks */
  const cleaned = mk.replace(/<style[\s\S]*?<\/style>/g, '').replace(/<!--[\s\S]*?-->/g, '');
  const re = />([^<>{}]+)</g;
  let m;
  while ((m = re.exec(cleaned))) {
    const txt = m[1].replace(/\s+/g, ' ').trim();
    if (txt.length < 4 || !/[A-Za-z]{4}/.test(txt)) continue;
    if (looksEnglish(txt)) bad.push(txt.slice(0, 70));
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: [...new Set(bad)].slice(0, 20) };
});

check('R3', 'A stale id reports itself on every detail screen', () => {
  /* RT3 only walks the happy path. A link that has gone stale must say so, on
     every drill-down, not render "UNDEFINED · UNDEFINED · UNDEFINED". */
  const m = mount();
  const GHOST = 'NO-SUCH-ID-12345';
  const screens = [
    ['case', { caseId: GHOST }], ['signal', { signalId: GHOST }], ['window', { windowId: GHOST }],
    ['source', { sourceId: GHOST }], ['person', { personId: GHOST }], ['theme', { themeId: GHOST }],
    ['company', { companyId: GHOST }], ['event', { eventId: GHOST }], ['cproduct', { cproductId: GHOST }],
    ['product', { productId: GHOST }],
  ];
  const bad = [];
  for (const [view, patch] of screens) {
    const r = m.tryVals(Object.assign({ view, lang: 'it' }, patch));
    if (!r.ok) { bad.push(`${view}: threw — ${r.error}`); continue; }
    const strings = collectStrings(r.vals).map((s) => s.value);
    /* "undefined" is matched in any case, because the breadcrumb upper-cases
       it. "NaN" is matched case-SENSITIVELY, because /nan/i hits inside an
       ordinary public handle like @giulianomassignan1737 — a real identity,
       not junk. */
    const junk = strings.filter((s) => /\bundefined\b/i.test(s) || /\[object Object\]/.test(s) || /\bNaN\b/.test(s));
    if (junk.length) { bad.push(`${view}: renders "${junk[0].slice(0, 60)}"`); continue; }
    /* something must state the absence */
    /* the props graph is cyclic, so look for the flag by key rather than by
       serializing the whole thing */
    const flagged = Object.entries(r.vals).some(([k, v]) => v === true && /missing|notfound/i.test(k));
    const saysMissing = flagged || strings.some((s) => /non trovat|not found|non esiste|nessun risultato/i.test(s));
    if (!saysMissing) bad.push(`${view}: silent — no missing state and no message`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad };
});


check('X1', 'Two screens never contradict each other on the same crop × issue', () => {
  /* The Opportunity screen printed "verifica etichetta necessaria" over the
     exact pair the Window screen proved VERIFIED — because the lookup was keyed
     on the source's Portuguese wording and the record had since been resolved
     into Italian. A cross-screen comparison is the only thing that catches a
     join breaking on one side. */
  const m = mount();
  const AM = m.AM;
  const bad = [];
  for (const o of AM.collections.opportunities.records) {
    if (!o.cropKeys || !o.cropKeys.length || !o.issueKey) continue;
    const w = AM.collections.cropWindows.records.find(
      (x) => x.crop === o.cropKeys[0] && String(x.issue || '').toLowerCase().includes(String(o.issueKey).toLowerCase().split(' ')[0]));
    if (!w) continue;
    for (const l of o.productLinks || []) {
      const fromAudit = AM.strengthFor(l.name, o.cropKeys[0], o.issueKey);
      if (fromAudit === 'VERIFIED_LABEL_MATCH' && l.strength !== 'VERIFIED_LABEL_MATCH') {
        bad.push(`${o.id} ${l.name}: opportunity says ${l.strength}, the label audit says VERIFIED`);
      }
      /* THE AUDIT SAYING NOTHING IS NOT THE AUDIT DISAGREEING.
         There are now two label readings of different depth: the 163-label
         audit that produced 12 verdicts, and the V2.1 reader that produced
         2.030 use pairs. LABEL_CHECK_NEEDED is the audit's own scope note —
         'this triple was never assessed' — and the absence rule the same file
         carries says in as many words that absence in our reading is not
         absence in the world. Counting it as a contradiction would force the
         portal to downgrade 37 pairs the document itself joins, and call the
         smaller reading the more careful one.

         What IS a contradiction is the audit having LOOKED and not found it. */
      if (l.strength === 'VERIFIED_LABEL_MATCH' && fromAudit === 'NO_CONFIRMED_MATCH_CURRENT_READING') {
        bad.push(`${o.id} ${l.name}: opportunity claims VERIFIED, the audit looked and did not find it`);
      }
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
});


check('A1', 'No filter affordance leads to an empty result', () => {
  /* The Radar's region panel invited a click on seven regions and five of them
     opened an empty radar, because the tile counted canonical crop windows
     while the filter matched opportunities. A control that promises records
     must deliver at least one, or it must not be lit. */
  const m = mount();
  const bad = [];
  const v = m.vals({ view: 'radar', lang: 'it' });
  const countFor = (patch) => {
    const r = m.tryVals(Object.assign({ view: 'radar', showAll: true, lang: 'it' }, patch));
    return r.ok ? (r.vals.visibleCases || []).length : -1;
  };
  /* region tiles that show a number and offer a filter */
  for (const t of v.regionRank || []) {
    if (!t || !t.name) continue;
    const n = countFor({ fRegion: t.name, fCrop: '', fIssue: '', fStatus: '' });
    if (n === 0) bad.push(`region "${t.name}" shows ${t.cases} and filters to 0`);
  }
  /* OGNI menu, non tre su cinque. A1 provava coltura, avversita e regione e
     lasciava fuori STATO e REPARTO — ed e li che il difetto viveva: le quattro
     voci del menu di stato erano una lista letterale scritta per le finestre
     colturali (WINDOW_OPEN, NEXT_CYCLE, DATE_UNKNOWN, WINDOW_CLOSED) mentre le
     schede portano gli stati del motore. Tutte e quattro filtravano a ZERO, e
     questo controllo non le guardava.

         UN CONTROLLO CHE PROVA TRE MENU SU CINQUE
         DICE LA VERITA SU TRE MENU. */
  for (const [key, list] of [['fCrop', v.cropOptions], ['fIssue', v.issueOptions],
    ['fRegion', v.regionOptions], ['fStatus', v.statusOptions], ['fDept', v.deptOptions]]) {
    for (const o of list || []) {
      if (!o || !o.v) continue;
      /* LA CHIAVE IN PROVA SI APPLICA PER ULTIMA.
         L'oggetto era `{ [key]: o.v, fCrop:'', fIssue:'', fRegion:'', fStatus:'' }`
         e in JavaScript vince l'ultima proprieta scritta: quando `key` era
         `fStatus`, la riga di azzeramento cancellava proprio il filtro che si
         stava provando, e il controllo misurava il radar senza filtri — 37
         casi, sempre. Passava su un menu i cui quattro elementi filtravano
         tutti a zero.

             AZZERARE GLI ALTRI FILTRI E GIUSTO.
             AZZERARE ANCHE QUELLO IN PROVA E MISURARE NIENTE. */
      const n = countFor(Object.assign(
        { fCrop: '', fIssue: '', fRegion: '', fStatus: '', fDept: '', fProduct: '' },
        { [key]: o.v }));
      if (n === 0) bad.push(`${key}="${o.v}" filters to 0`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 12) };
});

check('A3', 'A cross-link never rests on a shared crop name alone', () => {
  /* Two records sharing a crop name is not a relationship (rule 13). The Field
     Sales router matched the first window with the same crop and ignored the
     issue, so a herbicide question was routed to an insect window and the label
     stated that window's issue as the message's target. */
  const m = mount();
  const AM = m.AM;
  const v = m.tryVals({ view: 'field', lang: 'it' });
  if (!v.ok) return { pass: false, expected: 'field renders', measured: v.error };
  const wins = AM.collections.cropWindows.records;
  const norm = (s) => String(s || '').toLowerCase().replace(/[^a-z]+/g, ' ').trim();
  /* The label prints the LOCALIZED issue ("Cercosporiosi"), not the canonical
     one ("Cercospora Leaf Spot"), so resolving the window by scanning the label
     needs the same translation table the view used. Falling back to the region
     instead — the first version of this check did — picks an unrelated window
     in the same region and reports a defect that is not there. */
  const ISSUES = (v.vals.t && v.vals.t.ISSUES) || {};
  const localized = (w) => ISSUES[w.issue] || w.issue;
  const bad = [];
  for (const msg of v.vals.fieldMessages || []) {
    const target = msg.targetLabel || msg.windowLabel || '';
    if (!/finestre|window/i.test(target)) continue;
    const w = wins.find((x) => target.includes(localized(x)) && (!msg.crop || x.crop === msg.crop))
      || wins.find((x) => target.includes(localized(x)));
    if (!w) { bad.push(`"${msg.issue}" routes to "${target}" — no window matches that label`); continue; }
    const mi = norm(msg.issue), wi = norm(w.issue);
    if (!mi || !wi) continue;
    const shares = mi.split(' ').some((tok) => tok.length > 4 && wi.includes(tok)) ||
      wi.split(' ').some((tok) => tok.length > 4 && mi.includes(tok)) ||
      norm(ISSUES[msg.issue] || '') === norm(localized(w));
    if (!shares) bad.push(`"${msg.issue}" routed to window "${w.issue}" — only the crop matches`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
});

check('A4', 'The person directory agrees with the researcher collection', () => {
  /* isResearcher was true on 1 of 66 while the model held 60 researchers, so
     the publications panel was suppressed on 59 people who have publications. */
  const m = mount();
  const AM = m.AM;
  const ids = new Set(AM.collections.researchers.records.map((r) => r.id));
  const v = m.tryVals({ view: 'sources', sourceGroup: 'ALL', peopleCat: 'ALL', lang: 'it' });
  if (!v.ok) return { pass: false, expected: 'sources renders', measured: v.error };
  const people = v.vals.visiblePeople || [];
  if (!people.length) return { pass: false, expected: 'a people list', measured: 'empty' };
  const flagged = people.filter((p) => p.isResearcher).length;
  const shouldBe = people.filter((p) => ids.has(p.id)).length;
  return { pass: flagged === shouldBe, expected: shouldBe, measured: flagged,
    detail: { listed: people.length, inResearcherCollection: shouldBe, flagged } };
});


check('A5', 'A permanently empty panel is guarded or gone, never a label over nothing', () => {
  /* The adversarial audit measured these props empty on 100% of the records of
     their own collection, while their section heading still rendered. Each one
     must now either disappear (the prop is gone) or be knowable as empty (a
     companion boolean the template can guard on). A heading over nothing is
     worse than showing less: the reader assumes the data is missing, not that
     it was never claimed. */
  const m = mount();
  const HOLLOW = [
    ['signal', { signalId: (AM) => (AM.collections.futureSignals.records[0] || {}).id }, 'sg', ['who', 'whyWatch', 'trail', 'promotion']],
    ['person', { personId: (AM) => (AM.collections.researchers.records[0] || {}).id }, 'pr', ['issues', 'related', 'signals', 'history', 'messages']],
    ['source', { sourceId: (AM) => (AM.collections.sources.records[0] || {}).id }, 'sr', ['topics', 'cases']],
    ['event', { eventId: (AM) => (AM.collections.futureEvents.records[0] || {}).id }, 'evd', ['program']],
    ['theme', { themeId: (AM) => (AM.collections.scienceThemes.records[0] || {}).id }, 'th', ['caseObjs']],
  ];
  const mk = extractMarkup(readPortal());
  const bad = [];
  for (const [view, pickers, root, props] of HOLLOW) {
    const patch = { view, lang: 'it' };
    for (const [k, fn] of Object.entries(pickers)) patch[k] = fn(m.AM);
    const r = m.tryVals(patch);
    if (!r.ok) { bad.push(`${view}: ${r.error}`); continue; }
    const obj = r.vals[root];
    if (!obj) continue;
    for (const p of props) {
      const v = obj[p];
      const empty = v === undefined || v === null || (Array.isArray(v) && v.length === 0) || v === '';
      if (!empty) continue;
      /* it may simply be gone from the template */
      const bound = new RegExp(`\{\{\s*${root}\.${p}\b`).test(mk);
      if (!bound) continue;
      /* otherwise the code must know it is empty */
      const cap = p.charAt(0).toUpperCase() + p.slice(1);
      const knows = obj[`has${cap}`] === false || obj[`no${cap}`] === true ||
        obj[`has${cap}`] === 0 || Object.keys(obj).some((k) => new RegExp(`^(has|no)${cap}$`, 'i').test(k));
      if (!knows) bad.push(`${view}.${root}.${p}: empty, still bound, and no has${cap}/no${cap} to guard on`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 12) };
});


check('A6', 'The Opportunity product filter offers only linked products, and says so', () => {
  /* The selector filters opportunities, so it can only offer the products the
     opportunity records are linked to. It was labelled "tutti i prodotti ADAMA"
     over a list of six, which reads as the whole portfolio being present and
     mostly irrelevant. The universe belongs to PORTAFOGLIO · CATALOGO
     COMMERCIALE (44 catalogue entries, 166 joined). This check fails both ways:
     if the label over-promises, and if the list ever grows into the universe. */
  const m = mount();
  const AM = m.AM;
  const bad = [];
  const linked = new Set();
  for (const o of AM.collections.opportunities.records.concat(AM.collections.opportunityScenarios.records)) {
    for (const l of o.productLinks || []) if (l && (l.name || l.product)) linked.add(String(l.name || l.product).toUpperCase());
    for (const p of o.adamaProducts || []) linked.add(String(p).toUpperCase());
  }
  for (const lang of ['it', 'en']) {
    const v = m.vals({ view: 'radar', lang });
    for (const [where, list] of [['productOptions', v.productOptions], ['radarFilters', ((v.radarFilters || [])[4] || {}).options]]) {
      if (!Array.isArray(list) || !list.length) { bad.push(`${where}/${lang}: absent`); continue; }
      const label = String((list[0] || {}).l || '');
      if (/tutti i prodotti|all adama products/i.test(label)) bad.push(`${where}/${lang}: label still promises the whole portfolio — "${label}"`);
      const offered = list.slice(1).map((o) => String(o.v || '').toUpperCase()).filter(Boolean);
      const stray = offered.filter((p) => !linked.has(p));
      if (stray.length) bad.push(`${where}/${lang}: offers ${stray.length} product(s) no opportunity links, e.g. ${stray[0]}`);
      if (offered.length >= AM.collections.products.count) bad.push(`${where}/${lang}: the filter has become the product universe`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 8) };
});

check('VJ1', 'No vocabulary join has silently come unhooked', () => {
  /* The failure this catches is the one nothing else catches: a lookup keyed on
     a raw source string, a resolver that rewrites that string somewhere else,
     and a join that stops matching. Nothing crashes, no count goes red, and a
     screen prints an absence over a fact the package can prove — which is
     exactly how the Opportunity screen came to deny two label matches the
     Window screen proved on the same crop and issue.

     So the joins are asserted as numbers instead of read off a render.
     AM.joinHealth is the model reporting on itself; these floors are what the
     package measured on 2026-09-02, and a drop below one of them means a
     wording changed on one side of a join and not the other. Raising a floor
     when real data arrives is correct; lowering one needs a reason on the line. */
  const AM = mount().AM;
  const J = AM.joinHealth;
  if (!J) return { pass: false, expected: 'AM.joinHealth', measured: 'absent' };
  const bad = [];
  const atLeast = (label, got, floor) => { if (!(got >= floor)) bad.push(`${label}: ${got}, floor ${floor}`); };
  atLeast('labelAudit -> window (windows with a verdict)', J.labelAuditToWindow.filled, 19);
  atLeast('labelAudit -> window (verified)', J.labelAuditToWindow.verified, 12);
  atLeast('regional act -> window', J.fieldSignalToWindow.filled, 2);
  atLeast('opportunity -> label audit', J.opportunityToLabelAudit.filled, 2);
  atLeast('crop vocabulary · news', J.cropVocabulary.news.filled, 6);
  atLeast('crop vocabulary · voices', J.cropVocabulary.voices.filled, 17);
  atLeast('crop vocabulary · field signals', J.cropVocabulary.fieldSignals.filled, 7);
  atLeast('crop vocabulary · market series', J.cropVocabulary.marketSeries.filled, 77);
  /* The enum-keyed tables must reconcile exactly OVER THE ROWS THAT CARRY THE
     KEY. sourceGroup is keyed on SOURCE.TYPE, and 158 of the 189 V2.1 sources
     do not declare a TYPE at all — the last-mile expansion added them without
     one. That is a missing field upstream, not a table that stopped matching,
     and the two failures look nothing alike: an unhooked join misses rows that
     HAVE a key. So the denominator is the rows that have one. */
  for (const [k, r] of Object.entries(J.enums)) {
    const keyed = r.keyed === undefined ? r.n : r.keyed;
    if (r.filled !== keyed) bad.push(`enum ${k}: ${r.filled} of ${keyed} keyed rows resolve`);
  }
  /* THE MANDATORY CONTROL CASE.
     It used to be IT-OPP-001, one of three hand-written cards, and it proved
     that the crop/issue resolver still reached the label audit. Those three
     cards no longer exist: the engine derives its cases and names them
     OPP_<hash>, so pinning the check to a fixture id would pin it to data the
     package deliberately deleted.

     The control it replaces is the same question asked of the new join: the
     grapevine x downy mildew case must still resolve BOTH sides and come back
     with every one of its products carrying a label pair. If the canonical id
     join comes unhooked, this count goes to zero without anything crashing. */
  const opp = AM.collections.opportunities.records.find(
    (o) => o.crop === 'Grapevine' && /downy/i.test(String(o.issueEn || '')));
  if (!opp) bad.push('the Grapevine x Downy mildew control case is absent');
  else if (opp.verifiedProductCount !== opp.adamaProducts.length || !opp.adamaProducts.length) {
    bad.push(`control case verified products: ${opp.verifiedProductCount} of ${opp.adamaProducts.length}, expected all`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
});

check('VJ2', 'isResearcher means membership, not "has a paper here"', () => {
  /* Two different facts. isResearcher answers "is this row a row of
     collections.researchers?"; hasPublications answers "does this package hold
     a paper joined to this person by ORCID?". Conflating them told the reader
     that 59 of the 60 people in the bibliometric index were not researchers,
     and suppressed the publications panel by the wrong reason. A4 checks the
     directory LIST; this checks the person DETAIL, where the flag was being
     recomputed, and it checks the model's own numbers behind it. */
  const m = mount();
  const AM = m.AM;
  const P = AM.collections.people;
  const bad = [];
  const ids = new Set(AM.collections.researchers.records.map((r) => r.id));
  const collFlagged = P.records.filter((p) => p.isResearcher).length;
  if (collFlagged !== ids.size) bad.push(`collection: isResearcher on ${collFlagged}, researchers ${ids.size}`);
  /* the join itself, so a broken ORCID normalization cannot pass quietly */
  const joined = P.records.filter((p) => p.hasPublications).length;
  if (joined < 1) bad.push('publications join returns nothing for anybody — ORCID normalization is broken');
  if (P.records.some((p) => p.hasPublications && p.publicationCount === 0)) bad.push('hasPublications true with 0 publications');
  if (P.records.some((p) => !p.hasPublications && p.publicationCount > 0)) bad.push('hasPublications false with publications');
  /* every person detail must agree with the model on both facts */
  for (const id of ['IT-PER-001', 'IT-PER-013']) {
    const rec = P.records.find((p) => p.id === id);
    if (!rec) continue;
    const v = m.tryVals({ view: 'person', personId: id, lang: 'it' });
    if (!v.ok) { bad.push(`${id}: ${v.error}`); continue; }
    const pr = v.vals.pr || {};
    if (pr.isResearcher !== undefined && pr.isResearcher !== rec.isResearcher) {
      bad.push(`${id} "${rec.name}": the person detail says isResearcher ${pr.isResearcher}, the researcher collection says ${rec.isResearcher}. `
        + 'The detail recomputes the flag from the publication join instead of reading membership. '
        + 'Fix in client/portale.html (§12 person detail): isResearcher must come from the people record '
        + '(pr0.isResearcher / AM.collections.researchers membership); the PUBLICATIONS panel must be guarded '
        + 'on pr0.hasPublications, which the model now publishes per person.');
    }
    /* the panel may only be hidden for a person who really has no publication */
    const shown = Array.isArray(pr.themeRecords) ? pr.themeRecords.length : 0;
    if (shown > rec.publicationCount) bad.push(`${id}: detail lists ${shown} publications, the ORCID join finds ${rec.publicationCount}`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
});


check('I6', 'Italian mode shows no accidental English on any screen', () => {
  /* I2 only walked the Future screen. The Market breadcrumb read
     "MAIS · CROP MARKET" for months with every language check green, because
     the tab strip was localized and the crumb above it was built separately.
     This walks every rendered prop of every screen.

     Proper nouns are exempt BY PATH, not by guesswork: a product name, a company
     name, a Latin binomial, an original public quote, a source title and a URL
     are correctly untranslated (rule 11). */
  const m = mount();
  const EXEMPT_PATH = /(^|\.)(product|products|productName|company|companyLabel|name|species|latin|title|textOriginal|quote|url|sourceUrl|labelUrl|catalogUrl|author|institution|venue|doi|orcid|channel|person|platform|raw|ui|id|sourceId|crumbId|key|state|status|kind|type|code|vocab|scope|provenance|strength)(\[|\.|$)/i;
  /* The Field Sales fixture and the presentation scenarios are English BY
     DESIGN — they are labelled demonstration payloads, not interface copy.
     Walking into them measures the fixture's language, not the portal's. */
  const DEMO_PATH = /(^|\.)(fieldMessages|extraMessages|futureScenarios|opportunityScenarios|scenarios|tsr|tsrs|allMessages|composerExamples)(\[|\.|$)/i;
  /* A narrative slot is `{ state, it, en }`, and its `.en` half is English BY
     DEFINITION — that is the whole point of an approved pair. The fixture never
     populated one, so this walk never met an `.en` that was legitimately
     English; the V2.1 package populates 10.832 of them and every screen lit up.

         THE ENGLISH HALF OF A TRANSLATION IS NOT ACCIDENTAL ENGLISH.

     The exemption is deliberately narrow: `.en` is exempt only where a sibling
     `.it` exists on the SAME object, which is what makes it a pair rather than
     a field that merely ends in those two letters. An English string anywhere
     else still fails, and a pair whose `.it` went missing fails too — which is
     the defect worth catching, because that is the one that reaches the screen. */
  const pairedEn = (vals) => {
    const out = new Set();
    /* The model graph has cycles — an opportunity points at its window and the
       window's rows point back — so the walk carries a seen set, exactly as
       collectStrings does. Without it this recursion blows the stack rather
       than reporting anything. */
    const seen = new WeakSet();
    const walk = (v, path) => {
      if (!v || typeof v !== 'object') return;
      if (seen.has(v)) return;
      seen.add(v);
      if (Array.isArray(v)) { v.forEach((x, i) => walk(x, `${path}[${i}]`)); return; }
      if (typeof v.it === 'string' && typeof v.en === 'string') out.add(`${path}.en`);
      for (const k of Object.keys(v)) walk(v[k], path ? `${path}.${k}` : k);
    };
    walk(vals, '');
    return out;
  };
  const hits = [];
  let rendered = 0;
  for (const sc of SCREENS) {
    const patch = Object.assign({ view: sc.view, lang: 'it' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
    const r = m.tryVals(patch);
    if (!r.ok) continue;
    rendered++;
    const paired = pairedEn(r.vals);
    for (const { path, value } of collectStrings(r.vals)) {
      if (EXEMPT_PATH.test(path) || DEMO_PATH.test(path)) continue;
      if (paired.has(path)) continue;
      if (isEnglish(value)) hits.push(`${sc.label} ${path}: ${value.slice(0, 70)}`);
    }
  }
  const uniq = [...new Set(hits)];
  const vacuous = rendered < SCREENS.length;
  return {
    pass: uniq.length === 0 && !vacuous,
    expected: `0 over ${SCREENS.length} screens`,
    measured: vacuous ? `${uniq.length} but only ${rendered}/${SCREENS.length} rendered — INCONCLUSIVE` : `${uniq.length} over ${rendered} screens`,
    detail: uniq.slice(0, 15),
  };
});


check('E1', 'The entry page counts, it does not assert', () => {
  /* accesso.html is the first screen the client sees and it is a static page
     outside the model. It carried three hardcoded figures — 7 regions, 8 crops
     and "72 SEGNALI OSSERVATI". The 72 was the demo fixture's activity count:
     a fabricated number, in the largest type on the page, on the one screen
     that is guaranteed to be read. */
  const src = fs.readFileSync(path.join(CLIENT, 'accesso.html'), 'utf8');
  const bad = [];
  /* a bare number in a stat slot is an assertion */
  const re = /<b[^>]*>\s*(\d[\d.,]*)\s*<\/b>/g;
  let m;
  while ((m = re.exec(src))) bad.push(`hardcoded figure <b>${m[1]}</b>`);
  if (!/italy-canonical-windows\.js/.test(src)) bad.push('the canonical contract is not loaded, so nothing can be counted');
  /* and the numbers it shows must match the contract */
  const ctx = loadData();
  const C = (ctx.ITALY_CANONICAL && ctx.ITALY_CANONICAL.windows) || [];
  const uniq = (a) => new Set(a.filter(Boolean)).size;
  const expect = { regions: uniq(C.map((w) => w.REGION)), crops: uniq(C.map((w) => w.CROP_NAME)), windows: C.length };
  for (const id of ['statRegionsN', 'statCropsN', 'statWindowsN']) {
    if (!src.includes(id)) bad.push(`${id} slot is missing`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { willShow: expect, bad } };
});

export function runAll(only) {
  const list = only ? CHECKS.filter((c) => only.includes(c.id)) : CHECKS;
  return list.map((c) => {
    try {
      const r = c.fn();
      return Object.assign({ id: c.id, title: c.title }, r);
    } catch (e) {
      return { id: c.id, title: c.title, pass: false, expected: 'check runs', measured: 'THREW', detail: [e.message, (e.stack || '').split('\n')[1]] };
    }
  });
}
