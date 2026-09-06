/* GATE · DUPLICATE_CAPABILITIES — due mappe delle azioni sulle stesse 43 opportunita */
import { mount } from '../lib/harness.mjs';
const M = mount({});
const AM = M.AM;
const ids = AM.collections.opportunities.records.map(r => r.id);

const legacy = new Map();
let righeLegacy = 0;
for (const id of ids) {
  const v = M.vals({ view: 'case', caseId: id });
  for (const r of ((v.cs && v.cs.actionMapRows) || [])) {
    righeLegacy++;
    legacy.set(String(r.area), (legacy.get(String(r.area)) || 0) + 1);
  }
}

const B = M.ctx.MEETING_SURFACE.build('it');
const mIds = [];
for (const k of Object.keys(B)) if (Array.isArray(B[k])) for (const c of B[k]) if (c && c.id) mIds.push(c.id);
const unici = [...new Set(mIds)];
const riunione = new Map();
let righeRiunione = 0;
const etichette = { legacy: new Map(), riunione: new Map() };
for (const id of unici) {
  const v = M.vals({ view: 'mcase', mCaseId: id });
  for (const a of (v.mc.actions || [])) {
    righeRiunione++;
    const k = String(a.DEPARTMENT || a.dept);
    riunione.set(k, (riunione.get(k) || 0) + 1);
    if (a.deptLabel) etichette.riunione.set(k, a.deptLabel);
  }
}
for (const id of ids.slice(0, 10)) {
  const v = M.vals({ view: 'case', caseId: id });
  for (const r of ((v.cs && v.cs.actionMapRows) || [])) if (r.areaL) etichette.legacy.set(String(r.area), r.areaL);
}

console.log('SCHEDA LEGACY  · casi', ids.length, '· righe', righeLegacy, '· aree', legacy.size);
console.log('SCHEDA RIUNIONE· casi', unici.length, '· righe', righeRiunione, '· reparti', riunione.size);
console.log('');
console.log('REPARTO'.padEnd(24), 'LEGACY'.padStart(8), 'RIUNIONE'.padStart(9), '  ETICHETTA LEGACY / ETICHETTA RIUNIONE');
const tutti = [...new Set([...legacy.keys(), ...riunione.keys()])].sort();
let nomiDiversi = 0, soloUna = 0;
for (const k of tutti) {
  const a = legacy.get(k) || 0, b = riunione.get(k) || 0;
  const la = etichette.legacy.get(k) || '—', lb = etichette.riunione.get(k) || '—';
  if (la !== '—' && lb !== '—' && la !== lb) nomiDiversi++;
  if (!a || !b) soloUna++;
  console.log(k.padEnd(24), String(a).padStart(8), String(b).padStart(9), '  ' + la + '  /  ' + lb);
}
console.log('');
console.log('REPARTI CHE ESISTONO SU UNA SOLA SUPERFICIE =', soloUna);
console.log('REPARTI CON DUE NOMI DIVERSI               =', nomiDiversi);
console.log('DUPLICATE_CAPABILITIES =', (legacy.size && riunione.size) ? 1 : 0,
  '· due mappe delle azioni sulle stesse opportunita');
