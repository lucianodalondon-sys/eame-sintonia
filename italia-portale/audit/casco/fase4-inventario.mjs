/* FASE 4 · INVENTARIO DELLA SOSTITUZIONE
   Per ogni collezione che le SCHERMATE del CLIENT-DEMO leggono davvero:
   quanti record dimostrativi portava, se esiste l'equivalente reale, da quale
   fonte, con quanti record, e in che stato e la sostituzione. */
import fs from 'node:fs';
import { loadData, CLIENT } from '../lib/harness.mjs';

const DEMO_DIR = '/home/user/canonical/italia-portale/client';
const demo = loadData({ dir: DEMO_DIR, files: ['italy-canonical-windows.js', 'italy-label-verdicts.js',
  'italy-real-intelligence.js', 'italy-demo-data.js', 'italy-briefs.js', 'italy-market-pulse.js',
  'italy-science-business.js', 'italy-i18n.js', 'italy-catalog.js', 'italy-ingested.js', 'italy-app-model.js'] });
const vero = loadData({ dir: CLIENT });
const D = demo.ITALY_DEMO, AM = vero.ITALY_APP_MODEL, C = AM.collections;

/* le collezioni che il markup + la logica del casco leggono, commenti esclusi */
const lette = (file) => {
  const s = fs.readFileSync(file, 'utf8');
  const i = s.indexOf('<script type="text/x-dc"');
  const codice = s.slice(i).replace(/\/\*[\s\S]*?\*\//g, '');
  const out = {};
  for (const m of (codice.match(/\bD\.[A-Z_0-9]+/g) || [])) { const k = m.slice(2); out[k] = (out[k] || 0) + 1; }
  return out;
};
const usoCasco = lette(DEMO_DIR + '/portale.html');
const usoVivo = lette(CLIENT + '/portale.html');

/* dove e finita ciascuna: la collezione reale che ne ha preso il posto */
const EREDE = {
  WINDOWS: 'cropWindows', CASES: 'opportunities', SIGNALS: 'futureSignals', ARCHIVE: 'archive',
  SOURCES: 'sources', NEWS: 'news', PEOPLE: 'people', ACTIVITIES: 'competitorActivities',
  COMPANIES: 'competitorCompanies', CPRODUCTS: 'competitorProducts', SCI_THEMES: 'scienceThemes',
  RECORDS: 'scienceRecords', PRODUCTS: 'products', PRODUCT_LIST: 'products', INSTITUTIONS: 'scienceInstitutions',
  EVENTS: 'futureEvents', BULLETINS: 'fieldBulletins', OBSERVED: 'currentFieldSignals',
  MATRIX: 'competitorMatrix', ISSUE_ROWS: 'competitorIssueDensity', REGION_STATS: 'windowsByRegion',
  CROP_CAL: 'windowCalendarRows', CAL: 'windowCalendarRows', WINDOW_KPI: 'cropWindows',
  KPI: null, TSR: null, FIELD_MESSAGES: null, FIELD_KPI: null, LADDER: null, DEPT: null,
  NOTIFICATIONS: null, WHAT_CHANGED: null, PREP_LEAD: null, STATUS: null, CAT: null,
  TSR_KPI: null, REALITY: 'clientSafeCrossings', REAL_STATS: null, TODAY: null,
  GROUP_COLOR: null, F_COLOR: null, ATYPE_COLOR: null, CROP_COLS: null,
};

const dim = (v) => Array.isArray(v) ? v.length : (v && typeof v === 'object' ? Object.keys(v).length : (v === undefined ? 0 : 1));
const righe = [];
for (const k of Object.keys(usoCasco).sort()) {
  const erede = EREDE[k];
  const reale = erede && C[erede] ? ((C[erede].records || []).length) : 0;
  const fonte = erede && C[erede] ? (C[erede].source || C[erede].precedence || '—') : '—';
  let stato;
  if (usoVivo[k]) stato = 'ANCORA_LETTA';
  else if (erede && reale) stato = 'REPLACED_WITH_REAL';
  else if (erede) stato = 'REAL_PARTIAL';
  else stato = 'NO_REAL_EQUIVALENT';
  righe.push({ k, letture: usoCasco[k], demo: dim(D[k]), erede: erede || '—', reale, fonte, stato });
}
righe.sort((a, b) => b.letture - a.letture);

console.log('COLLEZIONE'.padEnd(16), 'LETT'.padStart(5), 'DEMO'.padStart(6), 'EREDE REALE'.padEnd(24), 'REALE'.padStart(6), 'STATO');
for (const r of righe) console.log(r.k.padEnd(16), String(r.letture).padStart(5), String(r.demo).padStart(6),
  r.erede.padEnd(24), String(r.reale).padStart(6), r.stato);
const per = {};
for (const r of righe) per[r.stato] = (per[r.stato] || 0) + 1;
console.log('');
console.log('collezioni lette dal CLIENT-DEMO:', righe.length, '·', JSON.stringify(per));
console.log('record dimostrativi che quelle collezioni portavano:', righe.reduce((a, r) => a + r.demo, 0));
console.log('record reali negli eredi:', [...new Set(righe.map(r => r.erede))].filter(e => e !== '—')
  .reduce((a, e) => a + ((C[e] && C[e].records) || []).length, 0));
