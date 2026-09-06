/* GATE · EXPERIMENTAL_DISEASE_VISIBLE / EXPERIMENTAL_LABEL_VISIBLE
   Nessuna superficie sotto prova deve arrivare allo schermo. */
import { mount } from '../lib/harness.mjs';
const M = mount({});
const AM = M.AM, ctx = M.ctx;

const SEGNI_MALATTIA = [
  'DISEASE_FORECAST', 'Disease Forecast', 'Previsione malattie', 'previsione della malattia',
  'DISEASE_INTELLIGENCE', 'Disease Intelligence', 'MODELLO EPIDEMIOLOGICO', 'infection risk model',
  'rischio di infezione previsto',
];
const SEGNI_ETICHETTA = [
  'LABEL_INTELLIGENCE_V1', 'Label Intelligence', 'LABEL_EXPERIMENTAL', 'etichetta sperimentale',
  'LABEL_INTEL_EXPERIMENTAL',
];

const stringhe = (v, out, d = 0) => {
  if (d > 7 || v == null) return out;
  if (typeof v === 'string') { out.push(v); return out; }
  if (typeof v !== 'object') return out;
  if (Array.isArray(v)) { for (const x of v) stringhe(x, out, d + 1); return out; }
  for (const k in v) { if (k === 'raw') continue; try { stringhe(v[k], out, d + 1); } catch (e) {} }
  return out;
};

const AMMESSE = ['meeting', 'future', 'windows', 'market', 'voices', 'competitors',
  'science', 'portfolio', 'archive', 'sources'];
const C = AM.collections;
const idsDi = (n, c) => ((C[n] && C[n].records) || []).map(r => r[c]).filter(Boolean);
const B = ctx.MEETING_SURFACE.build('it');
const mIds = []; for (const k of Object.keys(B)) if (Array.isArray(B[k])) for (const c of B[k]) if (c && c.id) mIds.push(c.id);

const schermate = [];
for (const lang of ['it', 'en']) {
  for (const v of AMMESSE) schermate.push({ view: v, lang });
  for (const id of [...new Set(mIds)]) schermate.push({ view: 'mcase', mCaseId: id, lang });
  for (const id of idsDi('opportunities', 'id')) schermate.push({ view: 'case', caseId: id, lang });
  for (const id of idsDi('cropWindows', 'id')) schermate.push({ view: 'window', windowId: id, lang });
  for (const p of (AM.products || [])) schermate.push({ view: 'product', productId: p.key, lang });
}

let malattia = 0, etichetta = 0, rese = 0;
const trovati = [];
for (const st of schermate) {
  const r = M.tryVals(st);
  if (!r.ok) continue;
  rese++;
  const testo = stringhe(r.vals, []).join('\n');
  for (const s of SEGNI_MALATTIA) if (testo.indexOf(s) >= 0) { malattia++; trovati.push([st.view, s]); }
  for (const s of SEGNI_ETICHETTA) if (testo.indexOf(s) >= 0) { etichetta++; trovati.push([st.view, s]); }
}
console.log('schermate rese', rese, 'su', schermate.length);
console.log('EXPERIMENTAL_DISEASE_VISIBLE =', malattia);
console.log('EXPERIMENTAL_LABEL_VISIBLE   =', etichetta);
for (const t of trovati.slice(0, 12)) console.log('   ', t[0], '·', t[1]);
