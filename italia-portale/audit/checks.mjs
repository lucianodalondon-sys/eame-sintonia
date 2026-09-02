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
import { scanAll, grepPackage, walkPackage } from './lib/scan.mjs';
import { isPortuguese, isEnglish, collectStrings, cropKeyOf } from './lang.mjs';

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
  return { pass: st.view === 'product' && st.productId === name, expected: `view=product productId=${name}`,
    measured: `view=${st.view} productId=${st.productId}` };
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
  const byKey = Object.fromEntries(nav.map((n) => [n.key || n.view || n.id, n.count]));
  const expect = {
    future: AM.collections.futureSignals.count,
    windows: AM.collections.windows.count,
    voices: AM.collections.voices.count,
  };
  const bad = Object.entries(expect).filter(([k, want]) => byKey[k] !== undefined && byKey[k] !== want)
    .map(([k, want]) => `${k}: shows ${byKey[k]}, model says ${want}`);
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: { nav: byKey, bad } };
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
  { view: 'theme', label: 'Science theme', pick: (AM) => ({ themeId: (AM.collections.scienceRecords.records[0] || {}).id }) },
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

check('H1', 'Handoff V2.1 has NOT been ingested', () => {
  const files = fs.readdirSync(CLIENT);
  const forbidden = files.filter((f) => /NEW-REAL-DATA|handoff-v2|HANDOFF-V2/i.test(f));
  return { pass: forbidden.length === 0, expected: 0, measured: forbidden.length, detail: forbidden };
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
