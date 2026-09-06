/* GATE · BRANDWELL_PARITY — la tavolozza del portale contro quella del CLIENT-DEMO */
import fs from 'node:fs';
const CASCO = '/home/user/canonical/italia-portale/client/portale.html';
const VIVO = '/home/user/eame-sintonia/italia-portale/client/portale.html';
const colori = (f) => {
  const s = fs.readFileSync(f, 'utf8');
  const out = new Map();
  for (const m of s.matchAll(/#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b/g)) {
    const c = m[0].toUpperCase(); out.set(c, (out.get(c) || 0) + 1);
  }
  return out;
};
const C = colori(CASCO), V = colori(VIVO);
const soloVivo = [...V.keys()].filter(c => !C.has(c)).sort();
const soloCasco = [...C.keys()].filter(c => !V.has(c)).sort();
console.log('colori nel CLIENT-DEMO', C.size, '· nel portale', V.size, '· condivisi', [...V.keys()].filter(c => C.has(c)).length);
console.log('');
console.log('FUORI TAVOLOZZA (nel portale, mai nel CLIENT-DEMO) =', soloVivo.length);
for (const c of soloVivo) console.log('   ', c, '·', V.get(c), 'occorrenze');
console.log('');
console.log('PERSI (nel CLIENT-DEMO, mai nel portale) =', soloCasco.length);
for (const c of soloCasco) console.log('   ', c, '·', C.get(c), 'occorrenze nel demo');
