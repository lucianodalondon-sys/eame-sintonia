/* Per ogni fonte: quanti record la citano nel modello, e quanti l'indice sa aprire. */
import { mount } from '../lib/harness.mjs';
const M = mount({});
const AM = M.AM, C = AM.collections;
const nelModello = new Map();
for (const nome of Object.keys(C)) {
  if (nome === 'archive' || nome === 'sources') continue;
  for (const r of ((C[nome] && C[nome].records) || [])) {
    for (const campo of ['sourceId', 'SOURCE_ID', 'sourceIds', 'SOURCE_IDS']) {
      const v = r && r[campo]; if (!v) continue;
      for (const id of (Array.isArray(v) ? v : [v])) {
        const k = String(id).trim(); if (!k) continue;
        nelModello.set(k, (nelModello.get(k) || 0) + 1);
      }
    }
  }
}
const nellIndice = new Map();
for (const a of C.archive.records) if (a.sourceId) nellIndice.set(String(a.sourceId), (nellIndice.get(String(a.sourceId)) || 0) + 1);

const fonti = C.sources.records;
let zeroIndice = 0, zeroEntrambi = 0, divario = 0;
const esempi = [];
for (const f of fonti) {
  const id = String(f.id);
  const m = nelModello.get(id) || 0, i = nellIndice.get(id) || 0;
  if (i === 0) zeroIndice++;
  if (i === 0 && m === 0) zeroEntrambi++;
  if (i === 0 && m > 0) { divario++; if (esempi.length < 12) esempi.push({ id, nome: f.name, modello: m }); }
}
console.log('fonti', fonti.length);
console.log('mostrano 0 sullo schermo (indice)        ', zeroIndice);
console.log('  di cui davvero senza record            ', zeroEntrambi);
console.log('  di cui FALSO ZERO (record nel modello) ', divario);
console.log('');
console.log('esempi di falso zero:');
for (const e of esempi) console.log('  ', e.id.padEnd(24), String(e.modello).padStart(5), 'record nel modello ·', String(e.nome || '').slice(0, 50));
const somma = [...nelModello.values()].reduce((a, b) => a + b, 0);
console.log('');
console.log('riferimenti a fonte nel modello', somma, '· nell\'indice', [...nellIndice.values()].reduce((a, b) => a + b, 0));
