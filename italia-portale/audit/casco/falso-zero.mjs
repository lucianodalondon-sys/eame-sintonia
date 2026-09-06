/* GATE · FALSE_ZERO — uno zero che significa «non collegato» letto come «niente» */
import { mount } from '../lib/harness.mjs';
const M = mount({});
const AM = M.AM;

/* ── Registro delle fonti: quante righe dichiarano 0 elementi ─────────────── */
const v = M.vals({ view: 'sources' });
const chiavi = Object.keys(v).filter(k => Array.isArray(v[k]) && v[k].length > 20);
console.log('elenchi lunghi nella vista Fonti:', chiavi.map(k => k + '=' + v[k].length).join(' '));
for (const k of chiavi) {
  const righe = v[k];
  const campiNum = Object.keys(righe[0] || {}).filter(c => typeof righe[0][c] === 'number' || /^\d+$/.test(String(righe[0][c])));
  for (const c of campiNum) {
    const zeri = righe.filter(r => Number(r[c]) === 0).length;
    if (zeri) console.log('  ', k + '.' + c, '· zero su', zeri + '/' + righe.length);
  }
  const campiTesto = Object.keys(righe[0] || {}).filter(c => typeof righe[0][c] === 'string');
  for (const c of campiTesto) {
    const zeri = righe.filter(r => /^0\b|·\s*0\s|\b0\s+(elementi|items|record)/i.test(String(r[c]))).length;
    if (zeri > righe.length * 0.3) console.log('  ', k + '.' + c, '· testo con zero su', zeri + '/' + righe.length, '· es:', JSON.stringify(righe.find(r => /0/.test(String(r[c])))[c]).slice(0, 70));
  }
}

/* ── Portafoglio ──────────────────────────────────────────────────────────── */
const p = M.vals({ view: 'portfolio' });
const pk = Object.keys(p).filter(k => Array.isArray(p[k]) && p[k].length > 10);
console.log('\nelenchi lunghi nella vista Portafoglio:', pk.map(k => k + '=' + p[k].length).join(' '));
for (const k of pk) {
  const righe = p[k];
  for (const c of Object.keys(righe[0] || {})) {
    const zeri = righe.filter(r => Number(r[c]) === 0).length;
    if (zeri > righe.length * 0.3) console.log('  ', k + '.' + c, '· zero su', zeri + '/' + righe.length);
    if (typeof righe[0][c] === 'string') {
      const z = righe.filter(r => /(^|\s)0(\s|$)/.test(String(r[c]))).length;
      if (z > righe.length * 0.3) console.log('  ', k + '.' + c, '· testo con zero su', z + '/' + righe.length, '· es:', JSON.stringify(righe.find(r => /(^|\s)0(\s|$)/.test(String(r[c])))[c]).slice(0, 70));
    }
  }
}
