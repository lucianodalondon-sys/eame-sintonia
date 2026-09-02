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
import { isPortuguese, isEnglish, looksEnglish, collectStrings, cropKeyOf } from './lang.mjs';
import { assertFrozen, blocks, markupBlocks } from './blocks.mjs';
import { scan as exposureScan } from './exposure.mjs';

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
  /* Checking three badges let a real one through: the opportunity badge showed
     29 — the canonical WINDOW count — standing in for a feed of 3. Every badge
     is checked by position now, because a badge nobody checks is one that
     drifts back to whatever number looks fuller. */
  const expect = [
    AM.collections.opportunities.count,
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

/* Identifiers the markup actually binds. A prop the template never reads is
   not on the client's screen. It is a trap for the first view that binds it —
   a real risk, but a different one, and mixing the two makes the headline
   number useless: measured when this split was made, 1178 "hits on a rendered
   screen" collapsed to a handful the client could actually see, the rest being
   props that nothing renders. */
export function markupBound() {
  const mk = extractMarkup(readPortal());
  const out = new Set();
  for (const m of mk.matchAll(/\{\{([^}]*)\}\}/g)) {
    for (const t of m[1].matchAll(/[A-Za-z_$][\w$]*/g)) out.add(t[0]);
  }
  for (const m of mk.matchAll(/\bas="([A-Za-z_][\w]*)"/g)) out.add(m[1]);
  return out;
}
const leafOf = (p) => String(p).split('.').pop().replace(/\[\d+\]$/, '');
/* A *Raw field is the published source text kept beside the resolved value so
   nothing becomes untraceable. Provenance, not display; PT3 proves no markup
   binds one. */
const isRawPath = (p) => /(^|\.)[A-Za-z]*Raw(\[|$|\.)/.test(p);
/* The public quote and the post's own headline are the source's words. The
   brief forbids translating them, so Portuguese there is correct behaviour and
   not a defect. */
const VERBATIM_LEAVES = new Set(['quote', 'headline', 'textOriginal']);

/** Walk every screen once and label each Portuguese hit bound / unbound. */
function portugueseOnScreens() {
  const m = mount();
  const bound = markupBound();
  const hitsBound = [];
  const hitsUnbound = [];
  let rendered = 0;
  const want = SCREENS.length * 2;
  for (const sc of SCREENS) {
    for (const lang of ['it', 'en']) {
      const r = m.tryVals(Object.assign({ view: sc.view, lang }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {}));
      if (!r.ok) continue;
      rendered++;
      for (const { path, value } of collectStrings(r.vals)) {
        if (isRawPath(path)) continue;
        if (VERBATIM_LEAVES.has(leafOf(path))) continue;
        if (!isPortuguese(value)) continue;
        const line = sc.label + '/' + lang + ' ' + path + ': ' + value.slice(0, 110);
        (bound.has(leafOf(path)) ? hitsBound : hitsUnbound).push(line);
      }
    }
  }
  return { rendered, want, bound: [...new Set(hitsBound)], unbound: [...new Set(hitsUnbound)] };
}

check('PT1', 'No Portuguese prose is bound by the markup on any rendered screen', () => {
  const r = portugueseOnScreens();
  /* A language check that passes because nothing rendered is a false green —
     exactly the kind of empty pass this suite exists to prevent. */
  const vacuous = r.rendered < r.want;
  return {
    pass: r.bound.length === 0 && !vacuous,
    expected: '0 bound hits over ' + r.want + ' renders',
    measured: vacuous
      ? r.bound.length + ' bound hits but only ' + r.rendered + '/' + r.want + ' rendered — INCONCLUSIVE'
      : r.bound.length + ' bound over ' + r.rendered + ' renders (' + r.unbound.length + ' more sit unbound in props — see PT1b)',
    detail: r.bound.slice(0, 14),
  };
});

check('PT1b', 'The unbound Portuguese still sitting in the props only shrinks', () => {
  /* These strings are one binding away from the client. Demanding zero would
     mean deleting facts the package carries on purpose, so this is a ratchet:
     the number may fall, never rise. Lower CEILING when it falls. */
  const CEILING = 942;
  const r = portugueseOnScreens();
  return {
    pass: r.unbound.length <= CEILING && r.rendered === r.want,
    expected: '<= ' + CEILING + ' unbound hits',
    measured: r.rendered < r.want
      ? 'only ' + r.rendered + '/' + r.want + ' rendered — INCONCLUSIVE'
      : r.unbound.length + ' unbound hits',
    detail: r.unbound.slice(0, 8),
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
  const shownOff = (vOff.filtered || vOff.visibleCases || []).length;
  const shownOn = (vOn.filtered || vOn.visibleCases || []).length;
  if (shownOn <= shownOff) bad.push(`the toggle shows nothing extra (${shownOff} -> ${shownOn}) — check is vacuous`);
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { casesOff: shownOff, casesOn: shownOn, bad } };
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
      if (l.strength === 'VERIFIED_LABEL_MATCH' && fromAudit !== 'VERIFIED_LABEL_MATCH') {
        bad.push(`${o.id} ${l.name}: opportunity claims VERIFIED, the audit says ${fromAudit}`);
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
  /* every option the crop / issue / region dropdowns offer must match something */
  for (const [key, list] of [['fCrop', v.cropOptions], ['fIssue', v.issueOptions], ['fRegion', v.regionOptions]]) {
    for (const o of list || []) {
      if (!o || !o.v) continue;
      const n = countFor({ [key]: o.v, fCrop: '', fIssue: '', fRegion: '', fStatus: '' });
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
  /* the enum-keyed tables reconcile exactly, so any miss at all is a fault */
  for (const [k, r] of Object.entries(J.enums)) {
    if (r.filled !== r.n) bad.push(`enum ${k}: ${r.filled} of ${r.n} resolve`);
  }
  /* IT-OPP-001 is the mandatory-control case: it must keep proving its two
     verified products through the resolver, in both directions. */
  const opp = AM.collections.opportunities.records.find((o) => o.id === 'IT-OPP-001');
  if (!opp) bad.push('IT-OPP-001 absent');
  else if (opp.verifiedProductCount !== 2) bad.push(`IT-OPP-001 verified products: ${opp.verifiedProductCount}, expected 2`);
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


/* Content the source published in its own words. Translating any of it is
   forbidden by the brief, so English here is correct and not a defect: an
   institution's name, a journal, a channel handle, a video or paper title, a
   literal search query, a Latin binomial, a package code.
   Note this list is deliberately WIDER than PT1's. The two checks ask different
   questions: PT1 asks "is this untranslated Portuguese research prose", and an
   opportunity's title is exactly that, so title is IN scope there. I6 asks
   "is this accidental English", and a source's title is deliberate English,
   so title is OUT of scope here. */
const ORIGINAL_LEAVES = new Set([
  'title', 'descriptor', 'org', 'orgLabel', 'institutions', 'institution', 'name',
  'venue', 'locationShort', 'channel', 'headline', 'query', 'note', 'short',
  'latin', 'issueEn', 'series', 'quote', 'author', 'handle', 'company', 'product',
  'textOriginal',
]);

function englishOnItalianScreens() {
  const m = mount();
  const bound = markupBound();
  const leaf = (p) => String(p).split('.').pop().replace(/\[\d+\]$/, '');
  const hitsBound = [];
  const hitsUnbound = [];
  let rendered = 0;
  for (const sc of SCREENS) {
    const it = m.tryVals(Object.assign({ view: sc.view, lang: 'it' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {}));
    if (!it.ok) continue;
    const en = m.tryVals(Object.assign({ view: sc.view, lang: 'en' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {}));
    rendered++;
    const enByPath = en.ok ? new Map(collectStrings(en.vals).map((x) => [x.path, x.value])) : new Map();
    for (const { path, value } of collectStrings(it.vals)) {
      const k = leaf(path);
      if (ORIGINAL_LEAVES.has(k)) continue;
      /* an {it, en} pair always exposes an English .en — that is the pair
         working, not a leak; the markup picks the side by language */
      if (k === 'en' && enByPath.has(path.replace(/\.en$/, '.it'))) continue;
      if (!looksEnglish(value)) continue;
      /* if the string CHANGES in English mode, the i18n is wired and the
         Italian text merely looked English to the detector */
      if (en.ok && enByPath.get(path) !== value) continue;
      /* dedupe by the STRING, not by the path: one caption repeated on every
         screen is one thing to translate, not twenty-six defects. */
      (bound.has(k) ? hitsBound : hitsUnbound).push(String(value));
    }
  }
  return { rendered, want: SCREENS.length, bound: [...new Set(hitsBound)], unbound: [...new Set(hitsUnbound)] };
}

check('I6', 'Italian mode binds no accidental English on any screen', () => {
  /* 228 distinct English captions were found the day the string walk stopped
     truncating. They are generated captions this portal authors itself — a
     status reason, a law caption, a filter placeholder — never source content,
     which is exempted above. */
  const CEILING = 201;
  const r = englishOnItalianScreens();
  const vacuous = r.rendered < r.want;
  return {
    pass: r.bound.length <= CEILING && !vacuous,
    expected: '<= ' + CEILING + ' bound English captions over ' + r.want + ' screens',
    measured: vacuous
      ? r.bound.length + ' bound but only ' + r.rendered + '/' + r.want + ' rendered — INCONCLUSIVE'
      : r.bound.length + ' bound over ' + r.rendered + ' screens (' + r.unbound.length + ' unbound)',
    detail: r.bound.slice(0, 12).map((v) => v.slice(0, 88)),
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

/* ── 15 · the canonical V2.1 package ──────────────────────────────────────
   The package is not "more data". It carries a per-record CLIENT_SAFE flag and
   its own laws about what may be said out loud. These checks hold the site to
   them. */

const V21_BUILD_ID = 'V21-843baf4229d93598';

check('V1', 'The declared V2.1 build is the one that is loaded', () => {
  const ctx = loadData();
  const V = ctx.ITALY_HANDOFF_V21;
  const AM = ctx.ITALY_APP_MODEL || {};
  const got = V && V.BUILD_ID;
  return {
    pass: got === V21_BUILD_ID,
    expected: V21_BUILD_ID,
    measured: got || 'ABSENT',
    detail: {
      families: V ? Object.keys(V.collections || {}).length : 0,
      modelSeesIt: !!(AM.ingest && AM.ingest.handoffV21Present),
    },
  };
});

check('V2', 'Every family reproduces the package manifest, from the files', () => {
  const ctx = loadData();
  const V = ctx.ITALY_HANDOFF_V21;
  if (!V) return { pass: false, expected: 'package loaded', measured: 'ABSENT' };
  const bad = [];
  for (const m of V.MANIFEST || []) {
    const rows = (V.collections || {})[m.family];
    if (!rows) { bad.push(`${m.family}: not transported`); continue; }
    if (rows.length !== m.total) bad.push(`${m.family}: ${rows.length} rows, manifest says ${m.total}`);
    const safe = rows.filter((r) => r && r.CLIENT_SAFE === true).length;
    if (safe !== m.clientSafe) bad.push(`${m.family}: ${safe} client-safe, transport recorded ${m.clientSafe}`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { families: (V.MANIFEST || []).length, bad: bad.slice(0, 10) } };
});

check('V3', 'No unreviewed research prose was transported to the browser', () => {
  /* The package's own language rule: RESEARCH holds Portuguese working notes
     the Design never reads. A CLIENT_SAFE=false record travels as identity
     only, so an unreviewed reading cannot sit in a public file waiting for
     some future component to render it. */
  const ctx = loadData();
  const V = ctx.ITALY_HANDOFF_V21;
  const bad = [];
  /* Read the payload, not the file: LANGUAGE_RULE.RESEARCH is the rule TEXT
     saying research notes are not transported, and a grep over the whole file
     scores that sentence as the very thing it forbids. */
  const payload = JSON.stringify((V && V.collections) || {});
  if (/"RESEARCH":/.test(payload)) bad.push('a RESEARCH field reached a record');
  if (/_ORIGINAL_RESEARCH_TEXT":/.test(payload)) bad.push('an *_ORIGINAL_RESEARCH_TEXT field reached a record');
  /* A non-client-safe record keeps its FACTS — the gate governs what may be
     ASSERTED, not what may EXIST. Stubbing it to an id would have shrunk the
     label layer from 2030 pairs to 1512 and from 78 label targets to 51, which
     is a loss of fact dressed as caution. What it must not carry is the
     unreviewed READING: a localized *_IT / *_EN pair. */
  if (V) {
    for (const [fam, rows] of Object.entries(V.collections || {})) {
      const leaky = (rows || []).filter((r) => r && r.CLIENT_SAFE !== true &&
        Object.keys(r).some((k) => k.endsWith('_IT') || k.endsWith('_EN')));
      if (leaky.length) bad.push(`${fam}: ${leaky.length} non-client-safe record(s) carry a localized reading`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 8) };
});

check('V4', 'The three opportunity candidates are never called opportunities', () => {
  /* Measured on the package: all three are ENTITY_TYPE OPPORTUNITY_CANDIDATE,
     QA_STATUS EVIDENCE_DERIVED, CLIENT_SAFE false, and each carries a
     FORBIDDEN_LABEL that forbids the words "opportunity" and "commercial
     opportunity". So the client-safe opportunity count is 0, and nothing in the
     model or on a screen may round it up. */
  const ctx = loadData();
  const V = ctx.ITALY_HANDOFF_V21;
  const AM = ctx.ITALY_APP_MODEL || {};
  const bad = [];
  const pkg = (V && V.collections && V.collections.opportunities) || [];
  const pkgSafe = pkg.filter((o) => o.CLIENT_SAFE === true).length;
  if (pkgSafe !== 0) bad.push(`the package itself now has ${pkgSafe} client-safe opportunities — re-read it before trusting this check`);
  const coll = AM.collections && AM.collections.opportunities;
  if (!coll) bad.push('collections.opportunities is absent');
  else {
    /* null is not zero. A transparency panel cannot render "null client-safe",
       and a screen reading it as falsy would be right by accident. The count
       has to be stated. */
    if (typeof coll.clientSafe !== 'number') {
      bad.push(`the model states clientSafe as ${JSON.stringify(coll.clientSafe)}; it must be the number 0`);
    } else if (coll.clientSafe !== 0) {
      bad.push(`the model reports ${coll.clientSafe} client-safe opportunities; the package says 0`);
    }
    const fromRecords = (coll.records || []).filter((r) => r.CLIENT_SAFE === true).length;
    if (fromRecords !== 0) bad.push(`${fromRecords} record(s) carry CLIENT_SAFE=true; the package says none do`);
  }
  const m = mount();
  const v = m.tryVals({ view: 'radar', lang: 'it', showScenarios: false });
  if (v.ok) {
    const asserted = (v.vals.visibleCases || []).filter((c) => c && c.clientSafe === true);
    if (asserted.length) bad.push(`${asserted.length} radar card(s) claim to be client-safe`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { packageTotal: pkg.length, packageClientSafe: pkgSafe, bad } };
});

check('V5', 'A future regulatory fact never becomes an opportunity', () => {
  /* EU APPROVAL EXPIRY is not NON-RENEWAL, is not COMMERCIAL RISK, is not
     ITALIAN MARKETABILITY, and is not an OPPORTUNITY. 47 facts are 47 facts. */
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const C = AM.collections || {};
  const facts = C.regulatoryFutureFacts || C.regulatoryFuture;
  const bad = [];
  if (!facts) bad.push('no regulatory-future collection is exposed');
  else {
    const opp = (C.opportunities && C.opportunities.count) || 0;
    if (facts.count > 3 && opp >= facts.count) bad.push(`opportunities (${opp}) grew to the size of the fact table (${facts.count})`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { regulatoryFutureFacts: facts ? facts.count : 0, opportunities: (C.opportunities && C.opportunities.count) || 0, bad } };
});

check('V6', 'The commercial catalogue and the regulatory universe are never summed', () => {
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const C = AM.collections || {};
  const com = C.productsCommercial && C.productsCommercial.count;
  const reg = C.productsRegulatory && C.productsRegulatory.count;
  const bad = [];
  if (com !== 51) bad.push(`commercial catalogue is ${com}, the package says 51`);
  if (reg !== 163) bad.push(`regulatory universe is ${reg}, the package says 163`);
  /* 214 is the two universes added together and must appear nowhere */
  const m = mount();
  for (const view of ['portfolio', 'product', 'radar']) {
    const r = m.tryVals({ view, lang: 'it' });
    if (!r.ok) continue;
    for (const { path: p, value } of collectStrings(r.vals)) {
      if (/\b214\b/.test(value)) bad.push(`${view} ${p}: renders 214 — the two universes added together`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: { commercial: com, regulatory: reg, bad } };
});

check('V7', 'The audited window contract survives the V2.1 ingestion', () => {
  /* A trap with a very quiet failure mode. The V2.1 package ships
     CROP-WINDOWS.json under the key APP.windows — 7 rows, sourced from regional
     lotta obbligatoria decrees. The site's crop-window contract is a DIFFERENT
     table: window.ITALY_CANONICAL, 29 audited windows carrying START_DATE,
     END_DATE, CURRENT_STATUS and DATE_STATE.

     Measured: the id spaces do not overlap — IT-WIN-001..007 against
     IT-WIN-0001..0029 — and the package's REPLACES_OLD_FILES for that family
     names a previous-handoff file, not the canonical contract. So the 7 are
     field readings, not a replacement.

     If an adapter lets them win by name, the Crop Windows screen silently drops
     from 29 windows to 7 and every date, stage and agronomic status disappears
     with them. Nothing throws. This check is the only thing that would notice. */
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const C = AM.collections || {};
  const canon = (ctx.ITALY_CANONICAL && ctx.ITALY_CANONICAL.windows) || [];
  const bad = [];
  const w = C.cropWindows;
  if (!w) bad.push('collections.cropWindows is absent');
  else {
    if (w.count < canon.length) bad.push(`cropWindows is ${w.count}; the audited contract has ${canon.length}`);
    const withStatus = (w.records || []).filter((r) => r.status).length;
    const withDates = (w.records || []).filter((r) => r.startDate || r.endDate).length;
    if (withStatus < canon.length) bad.push(`only ${withStatus} of ${w.count} windows carry an agronomic status`);
    if (withDates < 20) bad.push(`only ${withDates} windows carry a date; the contract supplies 24`);
  }
  /* the 7 decree readings must still be reachable, just not as the contract */
  const V = ctx.ITALY_HANDOFF_V21;
  const decree = (V && V.collections && V.collections.windows) || [];
  const fs2 = C.currentFieldSignals;
  if (decree.length && (!fs2 || fs2.count === 0)) bad.push('the 7 decree-backed readings are not exposed anywhere');
  return {
    pass: bad.length === 0,
    expected: `>= ${canon.length} canonical windows`,
    measured: w ? `${w.count} windows` : 'ABSENT',
    detail: { canonical: canon.length, decreeReadings: decree.length, fieldSignals: fs2 ? fs2.count : 0, bad },
  };
});

check('V8', 'The label-use layer keeps every pair the package carries', () => {
  /* Mission §5 is explicit: preserve the 2030 verified ministerial label-use
     pairs, 35 crops, 78 targets, and do NOT zero this layer.

     The client-safe gate legitimately limits what may be ASSERTED — 1512 of the
     2030 are client-safe — but it does not shrink the layer. Total and
     client-safe are two different numbers and the model has to carry both, or
     the portfolio screen quietly loses a third of the evidence with nothing
     failing. Deduplicating to a distinct product x crop x target key would drop
     it to 1077; that would also be a loss, because the same triple can be
     proved by two different rows of the label. */
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const V = ctx.ITALY_HANDOFF_V21;
  const bad = [];
  const pkg = (V && V.collections && V.collections['products.relationships']) || [];
  const pkgSafe = pkg.filter((r) => r.CLIENT_SAFE === true).length;
  const crops = new Set(pkg.map((r) => r.CROP_ON_LABEL).filter(Boolean));
  const targets = new Set(pkg.map((r) => r.TARGET_ON_LABEL).filter(Boolean));

  /* Two different numbers, and the model must carry both.
     The LABEL-USE LAYER is the source table: 2030 rows, 35 crops, 78 targets.
     The RELATIONSHIP layer is the distinct view of it — the package's own law
     says the three LINK_STRENGTH values do not sum, so the same product x crop
     x target proved twice is one relationship, not two. Requiring the
     relationship layer to hold 2030 would be requiring it to double-count. */
  const C = AM.collections || {};
  const layer = Object.entries(C).find(([, c]) => c && c.count === pkg.length);
  if (!layer) bad.push(`no collection holds the ${pkg.length} label-use rows`);
  else {
    const rows = layer[1].records || [];
    const lc = new Set(rows.map((r) => r.cropOnLabel || r.CROP_ON_LABEL || r.crop).filter(Boolean));
    const lt = new Set(rows.map((r) => r.targetOnLabel || r.TARGET_ON_LABEL || r.target).filter(Boolean));
    if (lc.size < crops.size) bad.push(`the layer exposes ${lc.size} label crops; the package has ${crops.size}`);
    if (lt.size < targets.size) bad.push(`the layer exposes ${lt.size} label targets; the package has ${targets.size}`);
  }
  const rel = C.productRelationships;
  if (!rel) bad.push('collections.productRelationships is absent');
  else {
    /* Every relationship the model presents as client-safe must be able to say
       which QA state it inherits. 518 of the 2030 source rows are unreviewed;
       a relationship that rests only on those may exist, but it may not be
       asserted, and without a QA stamp nobody can tell which is which. */
    const unstamped = (rel.records || []).filter((r) => r.clientSafe === true && !r.qaStatus && !r.QA_STATUS);
    if (unstamped.length) bad.push(`${unstamped.length} relationship(s) are marked client-safe with no QA status to inherit it from`);
  }
  /* Report the two layers separately. Printing the relationship count (2013)
     against the label-use expectation (>= 2030) made a passing check read like
     a failing one — the two numbers are answers to different questions, and a
     summary line that mixes them teaches the reader to distrust the green. */
  const layerRows = layer ? layer[1].count : 0;
  return {
    pass: bad.length === 0,
    expected: `label-use >= ${pkg.length} rows · ${crops.size} crops · ${targets.size} targets, and every client-safe relationship QA-stamped`,
    measured: layer
      ? `label-use ${layerRows} in ${layer[0]} · distinct relationships ${rel ? rel.count : 0}`
      : 'label-use layer ABSENT',
    detail: { packageRows: pkg.length, packageClientSafe: pkgSafe, labelCrops: crops.size, labelTargets: targets.size, bad },
  };
});

check('V9', 'Every V2.1 family the package supplies actually reaches the model', () => {
  /* A family can be silently skipped by mapping it to the wrong key — the
     record count then reflects the old source and nothing fails. This walks the
     manifest and asks, for each family, whether the model chose the V2.1
     source and ended up with the package's row count. */
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const V = ctx.ITALY_HANDOFF_V21;
  if (!V || !AM.ingest) return { pass: false, expected: 'package and ingest report', measured: 'ABSENT' };
  const chosen = {};
  for (const f of (AM.ingest.report && AM.ingest.report.families) || []) chosen[f.family] = f;
  const bad = [];
  /* families whose package rows must be visible somewhere in the model */
  const MUST = {
    'products.regulatory': 163, 'products.commercial': 51, 'products.relationships': 2030,
    fieldSignals: 122, market: 157, competitors: 577, science: 88, researchers: 60,
    resistance: 34, voices: 79, channels: 62, sources: 189, news: 8, events: 40,
    opportunities: 3, futureSignals: 3, regulatoryFutureFacts: 47, activeIngredients: 53,
  };
  const totals = Object.values(AM.collections || {}).map((c) => c && c.count);
  for (const [fam, n] of Object.entries(MUST)) {
    const pkgRows = (V.collections[fam] || []).length;
    if (pkgRows !== n) { bad.push(`${fam}: package has ${pkgRows}, this check expects ${n} — re-read the manifest`); continue; }
    if (!totals.includes(n)) bad.push(`${fam}: ${n} rows are in the package but no collection in the model holds ${n}`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad.slice(0, 12) };
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

check('G1', 'The parallel-edit block map still describes the file it maps', () => {
  /* The map is the safety mechanism for several agents editing one file. It
     carried hand-typed line numbers (2394-3459) while portale.html grew to
     7073 lines, so every range silently pointed into the markup instead of the
     logic, and the function meant to catch that — assertFrozen — did not exist
     at all. Nothing failed; the map was simply wrong for weeks.

     Two things are asserted here. First, every block edge falls on a top-level
     statement boundary of renderVals(), which is the only place a cut is legal.
     Second, the blocks tile the function with no gap and no overlap. If either
     breaks, parallel editing is unsafe and must stop. */
  const bad = [];
  let frozen = null;
  try { frozen = assertFrozen(); } catch (e) { bad.push(e.message); }
  if (frozen) {
    const bs = blocks();
    /* a block nobody can edit is not a block; 1200 lines is where review breaks down */
    const huge = bs.filter((b) => b.b - b.a + 1 > 1200);
    for (const h of huge) bad.push(`block ${h.key} is ${h.b - h.a + 1} lines — add an anchor inside it`);
    const mk = markupBlocks();
    if (mk.length < 20) bad.push(`only ${mk.length} markup screens found; the template has more`);
    for (let i = 1; i < mk.length; i++) {
      if (mk[i].a !== mk[i - 1].b + 1) bad.push(`markup gap/overlap between ${mk[i - 1].key} and ${mk[i].key}`);
    }
  }
  return {
    pass: bad.length === 0,
    expected: 'every edge legal, no gap, no overlap',
    measured: frozen ? `${frozen.blocks} logic blocks over ${frozen.lines} lines` : 'MAP UNUSABLE',
    detail: bad,
  };
});

check('G2', 'The language guards look at the whole screen, not the first slice of it', () => {
  /* PT1 and I6 walk the props object. The walker had a 4000-string cap, which
     was invisible until V2.1 grew the radar's props to 25 111 strings: the walk
     then stopped at 16% of the screen, and PT1 reported "0 Portuguese hits"
     over a radar that was rendering CONVERGENCIA QUE MERECE INVESTIGACAO in
     Portuguese. A guard that quietly stops looking reports silence as safety.
     This asserts the walk completes on the biggest screens, so a future data
     growth spurt fails HERE, loudly, instead of turning PT1 green. */
  const m = mount();
  const bad = [];
  const sizes = [];
  for (const sc of SCREENS) {
    const r = m.tryVals(Object.assign({ view: sc.view, lang: 'it' }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {}));
    if (!r.ok) continue;
    const s = collectStrings(r.vals);
    sizes.push({ screen: sc.label, strings: s.length });
    if (s.truncated) bad.push(`${sc.label}: the string walk hit its cap at ${s.length} — PT1/I6 cannot see the rest of this screen`);
  }
  if (!sizes.length) bad.push('no screen rendered, so nothing was walked');
  sizes.sort((a, b) => b.strings - a.strings);
  return {
    pass: bad.length === 0,
    expected: '0 truncated walks',
    measured: `${bad.length} truncated over ${sizes.length} screens`,
    detail: { largest: sizes.slice(0, 3), bad },
  };
});

check('G3', 'No localized display field carries a research note instead of a name', () => {
  /* The package answers some localized fields with an honest admission rather
     than a translation: 2 of the 34 GIRE resistance records fill SPECIES_IT
     with a Portuguese note explaining that the source card has no Italian
     common name. The note is true and useful upstream; on a screen it is a
     Portuguese apology sitting where a species name belongs.

     PT1 only sees fields that a screen actually binds today, so a field nobody
     renders yet is a trap armed for the first view that binds it. This walks
     the MODEL instead: every *It / *_IT display field must look like a name —
     no unknown sentinel, no explanatory clause, no Portuguese. */
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const SENTINEL = /^\s*(NAO SEI|N[ÃA]O SEI|NOT KNOWN|UNKNOWN)\b/i;
  const bad = [];
  let checked = 0;
  for (const [fam, c] of Object.entries(AM.collections || {})) {
    for (const r of (c && c.records) || []) {
      for (const k of Object.keys(r)) {
        if (!/It$|_IT$/.test(k)) continue;
        const v = r[k];
        if (typeof v !== 'string' || !v) continue;
        checked++;
        const why = SENTINEL.test(v) ? 'opens with an unknown sentinel'
          : isPortuguese(v) ? 'is Portuguese'
            : /\s[—–]\s.{25,}/.test(v) ? 'carries an explanatory clause'
              : null;
        if (why) bad.push(`${fam}.${r.id || '?'}.${k} ${why}: ${JSON.stringify(v).slice(0, 90)}`);
      }
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: { localizedFieldsChecked: checked, bad: bad.slice(0, 10) } };
});

check('G4', 'Portuguese in the model only shrinks, and never sits in a field a screen can bind', () => {
  /* PT1 measures what a screen RENDERS. This measures what a screen COULD
     render. The V2.1 package writes its interpretation rules — the geography
     laws, the commodity-stage law, the "this is not a claim" sentence — in
     Portuguese, and supplies an approved Italian variant for some of them and
     not others. 617 string fields across 44 field paths are Portuguese today.
     Most are never bound by the markup, but "not bound" is not "safe": each is
     a trap armed for the first view that binds it, and PT1 sees only what is
     bound today. Measured when this was written, of the Portuguese reaching the
     props: 288 hits over 4 keys WERE bound by the markup and 1508 over 9 keys
     were present but unbound. The gap between those two numbers is the size of
     the trap, not the size of the safety margin.

     This is a RATCHET, not a zero. Demanding 0 would mean deleting facts the
     package deliberately carries for traceability. What it forbids is growth:
     the number may fall, never rise, and no NEW field path may appear. When a
     path is fixed — by binding the approved *_IT sibling, or by moving the
     original under the *Raw suffix that PT3 already forbids the markup from
     binding — lower CEILING and drop the path from KNOWN. */
  const CEILING = 617;
  const KNOWN_PATHS = 44;
  const ctx = loadData();
  const AM = ctx.ITALY_APP_MODEL || {};
  const seen = new Map();
  let total = 0;
  for (const [fam, c] of Object.entries(AM.collections || {})) {
    for (const r of (c && c.records) || []) {
      for (const k of Object.keys(r)) {
        const v = r[k];
        if (typeof v !== 'string' || v.length < 13) continue;
        if (/Raw$/.test(k) || k === 'raw') continue;   /* traceability slot, PT3 forbids binding it */
        if (!isPortuguese(v)) continue;
        total++;
        const p = `${fam}.${k}`;
        seen.set(p, (seen.get(p) || 0) + 1);
      }
    }
  }
  const bad = [];
  if (total > CEILING) bad.push(`Portuguese fields grew from ${CEILING} to ${total} — a new source of untranslated prose entered the model`);
  if (seen.size > KNOWN_PATHS) bad.push(`field paths carrying Portuguese grew from ${KNOWN_PATHS} to ${seen.size}`);
  /* and the ones a screen actually binds must be zero — that is PT1's job, so
     here we only assert the two are consistent */
  return {
    pass: bad.length === 0,
    expected: `<= ${CEILING} fields over <= ${KNOWN_PATHS} paths`,
    measured: `${total} fields over ${seen.size} paths`,
    detail: { worst: [...seen.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8), bad },
  };
});

check('X2', 'The public upload carries no credential and no internal document', () => {
  /* The repository and the upload set are not the same folder, and only one of
     them goes public. This scans the ACTUAL upload — what survives
     .vercelignore — because 'vercel link' once wrote a .env.local holding a
     live VERCEL_OIDC_TOKEN directly into the folder being uploaded, and nothing
     in the suite would have noticed.

     Three separate questions, because they fail differently: is a CREDENTIAL in
     the upload, is an INTERNAL DOCUMENT in the upload (handoffs, research,
     audit files, prompts, .md), and does any uploaded file CONTAIN a
     secret-shaped string. */
  const r = exposureScan();
  const bad = [
    ...r.secrets.map((f) => 'credential file: ' + f),
    ...r.privates.map((f) => 'internal document: ' + f),
    ...r.inContent.map((f) => 'secret-shaped string inside: ' + f),
  ];
  return {
    pass: bad.length === 0,
    expected: '0 findings in the upload set',
    measured: bad.length + ' findings over ' + r.uploaded.length + ' public files',
    detail: bad.slice(0, 10),
  };
});

check('E2', 'The entry-page map is sized from the element, not from a resize event', () => {
  /* The map on accesso.html raced the page layout and lost, on every load, in
     silence. draw() reads stage.clientWidth/clientHeight; the atlas JSON
     normally arrives before the flex layout has given .stage a size, so both
     were 0, d3.geoMercator().fitExtent() produced scale 0, and every country
     collapsed to "M0,0L0,0…" inside a viewBox of "0 0 0 0". Nothing threw and
     nothing was logged — the first screen a client sees was simply an empty
     black rectangle. The only redraw path was a window "resize" listener, and
     no resize event fires on its own, so it never recovered.

     Node has no layout, so this cannot be proved headlessly. What it CAN prove
     is that the page does not depend on the event that never comes: the map
     must be redrawn from an observation of the element itself. */
  const src = fs.readFileSync(path.join(CLIENT, 'accesso.html'), 'utf8');
  const bad = [];
  const drawsOnLoad = /d3\.json\([^)]*\)[\s\S]{0,200}?draw\(/.test(src);
  if (!drawsOnLoad) bad.push('the map is never drawn when the atlas loads');
  if (!/ResizeObserver/.test(src)) {
    bad.push('nothing observes .stage — the map can only be sized by a window resize event, which never fires by itself');
  }
  /* and the redraw must refuse a zero-sized stage rather than baking scale 0 */
  if (!/clientWidth[\s\S]{0,240}(if \(!w \|\| !h\)|w && h|!w \|\| !h)/.test(src)) {
    bad.push('no guard against drawing the map while the stage still measures 0 x 0');
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length, detail: bad };
});
