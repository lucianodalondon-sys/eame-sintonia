/* Le 189 fonti: quante sono davvero senza record collegato, e perche. */
import { mount } from '../lib/harness.mjs';
const M = mount({});
const AM = M.AM, C = AM.collections;
const fonti = C.sources.records;
console.log('fonti nel registro:', fonti.length);

/* chi, nel modello, dichiara di venire da una fonte */
const citate = new Map();
let colonneCitanti = 0;
for (const nome of Object.keys(C)) {
  const rec = (C[nome] && C[nome].records) || [];
  let n = 0;
  for (const r of rec) {
    for (const campo of ['sourceId', 'SOURCE_ID', 'source', 'sourceIds', 'SOURCE_IDS']) {
      const v = r && r[campo];
      if (!v) continue;
      for (const id of (Array.isArray(v) ? v : [v])) {
        const k = String(id).trim(); if (!k) continue;
        if (!citate.has(k)) citate.set(k, new Set());
        citate.get(k).add(nome); n++;
      }
    }
  }
  if (n) { colonneCitanti++; console.log('  cita fonti:', nome, n); }
}
console.log('collezioni che citano una fonte:', colonneCitanti);
console.log('identificativi di fonte citati:', citate.size);

const idFonti = new Set(fonti.map(f => String(f.id)));
const citatiNonNelRegistro = [...citate.keys()].filter(k => !idFonti.has(k));
const nelRegistroMaiCitati = fonti.filter(f => !citate.has(String(f.id)));
console.log('citati che NON stanno nel registro:', citatiNonNelRegistro.length, citatiNonNelRegistro.slice(0, 8).join(' '));
console.log('nel registro e MAI citati:', nelRegistroMaiCitati.length, '/', fonti.length);
console.log('');
console.log('per tipo, le fonti mai citate:');
const perTipo = {};
for (const f of nelRegistroMaiCitati) { const t = f.type || f.TYPE || f.group || '?'; perTipo[t] = (perTipo[t] || 0) + 1; }
const perTipoTot = {};
for (const f of fonti) { const t = f.type || f.TYPE || f.group || '?'; perTipoTot[t] = (perTipoTot[t] || 0) + 1; }
for (const t of Object.keys(perTipoTot).sort()) console.log('  ', t, (perTipo[t] || 0) + '/' + perTipoTot[t], 'senza record');
