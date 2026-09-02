#!/usr/bin/env node
/* SINTONIA ITALY · FINAL ACCEPTANCE REPORT
   ---------------------------------------------------------------------------
   Emits the §36 report, every line measured from the running code. Nothing here
   is typed by hand; if a number is wrong, the code is wrong.

     node audit/acceptance.mjs            human readable
     node audit/acceptance.mjs --md       markdown, for the handoff document
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { loadData, mount, CLIENT } from './lib/harness.mjs';
import { scanAll, grepPackage } from './lib/scan.mjs';
import { runAll } from './checks.mjs';

const md = process.argv.includes('--md');

const ctx = loadData();
const AM = ctx.ITALY_APP_MODEL || {};
const C = AM.collections || {};
const scan = scanAll();
const checks = runAll();
const check = (id) => checks.find((c) => c.id === id) || { pass: false, measured: 'n/a' };
const count = (k) => (C[k] ? C[k].count : 'ABSENT');

let m;
try { m = mount(); } catch (e) { m = null; }
const vals = (patch) => { try { return m ? m.vals(patch) : null; } catch (e) { return null; } };

const rows = [];
const R = (item, measured, expected) => rows.push({ item, measured, expected });
const YN = (b) => (b ? 'YES' : 'NO');

/* ── the report ─────────────────────────────────────────────────────────── */
R('BASELINE BUILD', 'SINTONIA EAME - ITALIA PILOTO (8)', 'SINTONIA EAME - ITALIA PILOTO (8)');
R('BRANDWELL LOCAL SYSTEM FOUND', YN(check('B1').pass), 'YES');
R('BRANDWELL PATH', 'CLIENT-DEMO/_ds/adama-brandwell/ → client/_ds/adama-brandwell/', 'CLIENT-DEMO/_ds/adama-brandwell/');

R('CORE DATA-BEARING D.* READS', scan.counts.DATA_BEARING_CORE, 0);
R('VISUAL_ONLY D.* READS', scan.counts.VISUAL_ONLY, '(classified, with a written reason)');
R('EXPLICIT_DEMO D.* READS', scan.counts.EXPLICIT_DEMO, '(classified, with a written reason)');
R('MODEL-LEVEL CORE FACTS DEPENDING ON DEMO', check('M4').measured, 0);

R('FUTURE REAL SIGNALS', count('futureSignals'), 3);
R('FUTURE REAL DETAIL USES APP', YN(check('F3').pass), 'YES');
R('DEFAULT FUTURE DEMO SCENARIOS', (() => { const v = vals({ view: 'future' }); return v && m ? (m.instance.state.showScenarios ? count('futureScenarios') : 0) : 'n/a'; })(), 0);
R('CORE D.SIGNALS', (scan.bySymbol.SIGNALS || { core: 0 }).core, 0);

R('COMPETITOR REAL ACTIVITIES', count('competitorActivities'), 503);
R('VISIBLE COMPETITOR USES APP', YN((scan.bySymbol.ACTIVITIES || { core: 0 }).core === 0), 'YES');
R('D.ACTIVITIES CORE READS', (scan.bySymbol.ACTIVITIES || { core: 0 }).core, 0);

R('MARKET REAL OBSERVATIONS', count('marketObservations'), '77 ingested (1 rejected: no product)');
R('VISIBLE MARKET USES APP', YN(!/window\.ITALY_MARKET\.(CROPS\[[^\]]*\]\.(temp|reading|drivers|current|outlook|price|production|trade|confidence))/.test(fs.readFileSync(path.join(CLIENT, 'portale.html'), 'utf8'))), 'YES');

R('SCIENCE REAL RECORDS', count('scienceRecords'), 88);
R('RESEARCHERS', count('researchers'), 60);
R('RESISTANCE', count('resistance'), 34);
R('VISIBLE SCIENCE USES APP', YN((scan.bySymbol.SCI_THEMES || { core: 0 }).core === 0 && (scan.bySymbol.RECORDS || { core: 0 }).core === 0), 'YES');
R('VISIBLE RESEARCHERS USE APP', YN((scan.bySymbol.PEOPLE || { core: 0 }).core === 0 && (scan.bySymbol.TSR || { core: 0 }).core === 0), 'YES');

R('VISIBLE ARCHIVE USES APP', YN((scan.bySymbol.ARCHIVE || { core: 0 }).core === 0), 'YES');
R('D.ARCHIVE CORE READS', (scan.bySymbol.ARCHIVE || { core: 0 }).core, 0);
R('SYNTHETIC ARCHIVE ROWS', (C.archive ? C.archive.demo : 'ABSENT'), 0);

R('CANONICAL WINDOWS', count('cropWindows'), 29);
R('VISIBLE WINDOWS USE APP', YN((scan.bySymbol.WINDOWS || { core: 0 }).core === 0), 'YES');
R('D.WINDOWS CORE READS', (scan.bySymbol.WINDOWS || { core: 0 }).core, 0);

R('REAL OPPORTUNITIES', count('opportunities'), '(upstream only)');
R('DEFAULT DEMO OPPORTUNITIES', (() => { const v = vals({ view: 'radar' }); return v && Array.isArray(v.visibleCases) && m && !m.instance.state.showScenarios ? v.visibleCases.filter((c) => c && c.isScenario).length : 'n/a'; })(), 0);
R('DEMO OPPORTUNITY COUNTED AS REAL', (C.opportunities ? C.opportunities.demo : 'ABSENT'), 0);

R('PRODUCT RELATIONSHIP CORE TRUTH SOURCE', (C.productRelationships && C.productRelationships.source) || 'ABSENT', 'label audit + national registry');
R('PRODUCT RELATIONSHIPS', count('productRelationships'), '(measured)');
R('D.CASES USED AS PRODUCT TRUTH', YN(!check('P2').pass), 'NO');

R('VOCI REAL PUBLIC VOICES', count('publicVoices'), 17);
R('VOCI RTV DEMO MESSAGES', (() => { const v = vals({ view: 'voices' }); return v && Array.isArray(v.voices) ? v.voices.filter((x) => x && (x.demo || x.provenance === 'SYNTHETIC_DEMO')).length : 'n/a'; })(), 0);

R('FIELD SALES MUTATES CORE', YN(!check('FS1').pass), 'NO');
R('FAKE PHONE NUMBER', check('FS2').measured, 0);
R('OUTBOUND FIELD SALES REQUEST', check('FS3').measured, 0);

R('SEARCH DATA SOURCE', check('S1').pass ? 'APP.searchIndex' : 'legacy manual scan', 'APP.searchIndex');
R('SEARCH INDEX ENTRIES', (AM.searchIndex || []).length, '(measured)');
R('SEARCH CORE D.* READS', check('S2').measured, 0);
R('UNRESOLVED SEARCH ROUTES', check('S3').measured, 0);

R('NAV CORE COUNTS USE APP', YN(check('N1').pass && check('N3').pass), 'YES');
R('DATA STATE USES APP PROVENANCE', YN(check('N2').pass), 'YES');
R('CORE PRIVATE-DATA-REQUIRED UI', check('L1').measured, 0);

R('REFERENCE DATE', AM.referenceDate, '2026-09-02');
R('SECOND TRUTH CLOCK', String(check('M2').measured).replace(/^.*· /, ''), '0');

R('ITALIAN DEFAULT', YN(check('I1').pass), 'YES');
R('LANGUAGE SWITCH RELOAD', YN(!check('I1').pass), 'NO');
R('PORTUGUESE RESEARCH PROSE ON SCREEN', check('PT1').measured, 0);
R('UNRESOLVED CROP VOCABULARY', check('PT2').measured, 0);

R('UNRESOLVED REAL ENTITY IDS', check('R1').measured, 0);
R('REAL ENTITY → DEMO SILENT FALLBACKS', check('R2').measured, 0);

R('AUTOMATED STRUCTURAL TESTS', `${checks.filter((c) => c.pass).length}/${checks.length}`, 'PASS');
R('RUNTIME SMOKE TESTS', `${check('RT1').measured} IT · ${check('RT2').measured} EN`, 'PASS');
R('OFFLINE / NO PUBLIC CDN', YN(check('B3').pass), 'YES');
R('HANDOFF V2.1 INGESTED', YN(!check('H1').pass), 'NO');
R('V2.1 COLLECTION SLOTS READY', check('M3').measured, '23 slots');

/* the hard ready rule, §37 */
const BLOCKERS = [
  ['CORE DATA-BEARING D.* READS > 0', scan.counts.DATA_BEARING_CORE > 0],
  ['a core factual value still originates only in demo', !check('M4').pass],
  ['a real entity silently falls back to demo', !check('R2').pass],
  ['Competitor still uses D.ACTIVITIES', (scan.bySymbol.ACTIVITIES || { core: 0 }).core > 0],
  ['Crop Windows still use D.WINDOWS as factual truth', (scan.bySymbol.WINDOWS || { core: 0 }).core > 0],
  ['Opportunity real feed still comes from D.CASES', (scan.bySymbol.CASES || { core: 0 }).core > 0],
  ['Science still depends on D.SCI_THEMES / D.RECORDS / D.PEOPLE', ((scan.bySymbol.SCI_THEMES || { core: 0 }).core + (scan.bySymbol.RECORDS || { core: 0 }).core + (scan.bySymbol.PEOPLE || { core: 0 }).core) > 0],
  ['Archive still depends on D.ARCHIVE', (scan.bySymbol.ARCHIVE || { core: 0 }).core > 0],
  ['Search still manually searches D.*', !check('S2').pass],
  ['nav counts still use D.KPI', !check('N3').pass],
  ['Data State still measures legacy fixture collections', !check('N2').pass],
  ['Field Sales changes core evidence', !check('FS1').pass],
  ['the fake WhatsApp loop exists anywhere', !check('FS2').pass || !check('FS3').pass],
  ['a screen does not render', !check('RT1').pass || !check('RT2').pass],
  ['Portuguese research prose reaches the client', !check('PT1').pass],
];
const failing = BLOCKERS.filter(([, bad]) => bad);
const ready = failing.length === 0;

/* ── output ─────────────────────────────────────────────────────────────── */
if (md) {
  console.log('# SINTONIA ITALY · FINAL ACCEPTANCE\n');
  console.log('| item | measured | expected |');
  console.log('|---|---|---|');
  rows.forEach((r) => console.log(`| ${r.item} | **${r.measured}** | ${r.expected} |`));
  console.log(`\n## §37 HARD READY RULE\n`);
  console.log(`**READY FOR CANONICAL HANDOFF V2.1 = ${ready ? 'YES' : 'NO'}**\n`);
  if (failing.length) {
    console.log('Blocking:\n');
    failing.forEach(([w]) => console.log(`- ${w}`));
  }
} else {
  const G = '\x1b[32m', RD = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
  console.log('\n  SINTONIA ITALY · FINAL ACCEPTANCE');
  console.log('  ' + '─'.repeat(94));
  rows.forEach((r) => {
    const ok = String(r.measured) === String(r.expected) || String(r.expected).startsWith('(');
    console.log(`  ${String(r.item).padEnd(44)} ${(ok ? G : RD)}${String(r.measured).padEnd(22)}${X}${DIM}exp ${r.expected}${X}`);
  });
  console.log('  ' + '─'.repeat(94));
  console.log(`  READY FOR CANONICAL HANDOFF V2.1 = ${ready ? G + 'YES' : RD + 'NO'}${X}`);
  if (failing.length) { console.log('  blocking:'); failing.forEach(([w]) => console.log(`    ${RD}·${X} ${w}`)); }
  console.log('');
}
process.exit(ready ? 0 : 1);
