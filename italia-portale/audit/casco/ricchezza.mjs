/* FASE 12 · IL REALE E PIU RICCO DEL DIMOSTRATIVO — misurato, non affermato.
   Da una parte il CLIENT-DEMO come e; dall'altra il portale di oggi. */
import fs from 'node:fs';
import { loadData, CLIENT } from '../lib/harness.mjs';

const DEMO_DIR = '/home/user/canonical/italia-portale/client';
const FILE_DEMO = ['italy-canonical-windows.js', 'italy-label-verdicts.js', 'italy-real-intelligence.js',
  'italy-demo-data.js', 'italy-briefs.js', 'italy-market-pulse.js', 'italy-science-business.js',
  'italy-i18n.js', 'italy-catalog.js', 'italy-ingested.js', 'italy-app-model.js'];

const demo = loadData({ dir: DEMO_DIR, files: FILE_DEMO });
const vero = loadData({ dir: CLIENT });

const S = (x) => new Set([].concat(x).filter(v => v !== null && v !== undefined && String(v).trim() !== ''));
const dai = (recs, campi) => {
  const out = new Set();
  for (const r of recs || []) for (const c of campi) {
    const v = r && r[c]; if (!v) continue;
    for (const x of (Array.isArray(v) ? v : [v])) if (x && String(x).trim()) out.add(String(x).trim().toUpperCase());
  }
  return out;
};

const misura = (win, etichetta) => {
  const M = win.ITALY_APP_MODEL, C = M.collections;
  const rec = (n) => (C[n] && C[n].records) || [];
  const tutte = Object.keys(C);
  const oggetti = tutte.filter(n => n !== 'archive').reduce((a, n) => a + rec(n).length, 0);
  const famiglie = new Set();
  for (const l of (M.provenanceSummary || [])) if (!l.demo && l.source) famiglie.add(String(l.source).trim());
  const regioni = new Set(), colture = new Set(), avversita = new Set(), prove = new Set();
  for (const n of tutte) {
    const r = rec(n);
    for (const x of dai(r, ['region', 'regionKeys', 'regionIds', 'REGION'])) regioni.add(x);
    for (const x of dai(r, ['crop', 'cropKeys', 'cropIds', 'CROP'])) colture.add(x);
    for (const x of dai(r, ['issue', 'issueIds', 'issueKeys', 'ISSUE', 'target'])) avversita.add(x);
    for (const x of dai(r, ['sourceUrls', 'url', 'labelUrl', 'sourceUrl'])) if (/^https?:/i.test(x)) prove.add(x);
  }
  const incroci = rec('clientSafeCrossings').length + rec('relationships').length + rec('competitorWindowMoments').length;
  return {
    etichetta,
    REAL_SOURCE_FAMILIES: famiglie.size,
    REAL_INTELLIGENCE_OBJECTS: oggetti,
    REAL_CROSSINGS: incroci,
    REAL_REGIONS: regioni.size,
    REAL_CROPS: colture.size,
    REAL_ISSUES: avversita.size,
    REAL_EVIDENCE_LINKS: prove.size,
    RECORD_DEMO: (M.provenanceTotals || {}).demo || (M.provenanceSummary || []).reduce((a, l) => a + (l.demo || 0), 0),
    RECORD_REALI: (M.provenanceTotals ? M.provenanceTotals.real + M.provenanceTotals.derived
      : (M.provenanceSummary || []).reduce((a, l) => a + (l.real || 0) + (l.derived || 0), 0)),
  };
};

/* Quante volte lo SCHERMO legge il pacchetto dimostrativo, commenti esclusi. */
const letturaDemo = (file) => {
  const src = fs.readFileSync(file, 'utf8');
  const i = src.indexOf('<script type="text/x-dc"');
  const codice = src.slice(i).replace(/\/\*[\s\S]*?\*\//g, '');
  const hit = codice.match(/\bD\.[A-Z_0-9]+/g) || [];
  return { letture: hit.length, collezioni: new Set(hit).size };
};
const ld = letturaDemo(DEMO_DIR + '/portale.html'), lv = letturaDemo(CLIENT + '/portale.html');

const a = misura(demo, 'CLIENT-DEMO'), b = misura(vero, 'PORTALE');
a.LETTURE_DEMO_SULLO_SCHERMO = ld.letture; b.LETTURE_DEMO_SULLO_SCHERMO = lv.letture;
a.COLLEZIONI_DEMO_LETTE = ld.collezioni; b.COLLEZIONI_DEMO_LETTE = lv.collezioni;
const chiavi = Object.keys(a).filter(k => k !== 'etichetta');
console.log('MISURA'.padEnd(28), 'CLIENT-DEMO'.padStart(13), 'PORTALE'.padStart(13), 'FATTORE'.padStart(9));
for (const k of chiavi) {
  const f = a[k] ? (Math.round((b[k] / a[k]) * 10) / 10) + '×' : (b[k] ? 'nuovo' : '—');
  console.log(k.padEnd(28), String(a[k]).padStart(13), String(b[k]).padStart(13), String(f).padStart(9));
}
