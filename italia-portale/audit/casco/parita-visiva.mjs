/* FASE 11 · PARITA VISIVA CON IL CLIENT-DEMO, SCHERMATA PER SCHERMATA
   ---------------------------------------------------------------------------
   Il confronto non e sul testo — il testo DEVE cambiare, perche i dati sono
   diversi. Il confronto e sulla FORMA: il tag e i suoi attributi di stile, con
   i binding e il contenuto tolti. Cosi «una scheda con questo bordo, questo
   raggio, questo fondo» resta confrontabile anche se dentro ci va un'altra
   coltura.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';

const CASCO = process.argv[2] || '/home/user/canonical/italia-portale/client/portale.html';
const VIVO = process.argv[3] || '/home/user/eame-sintonia/italia-portale/client/portale.html';

const markup = (file) => {
  const s = fs.readFileSync(file, 'utf8');
  const a = s.indexOf('<template id="__bundler_thumbnail"');
  const b = s.indexOf('<script type="text/x-dc"');
  return s.slice(a, b);
};

/* segmenta per schermata: ogni blocco `sc-if value="{{ isX }}"` di primo livello */
const segmenta = (m) => {
  const righe = m.split('\n');
  const out = {}; let corrente = '__shell';
  out[corrente] = [];
  for (const r of righe) {
    const mm = r.match(/^\s{4}<sc-if value="\{\{ (is[A-Z][A-Za-z]*) \}\}"/);
    if (mm) { corrente = mm[1]; out[corrente] = out[corrente] || []; continue; }
    out[corrente].push(r);
  }
  return out;
};

/* IL PAVIMENTO TIPOGRAFICO E UNA SOLA DECISIONE, NON SEICENTO.
   Il casco dichiara 674 corpi di testo sotto i dieci pixel; il portale ne
   dichiara undici. Ogni tag toccato da quella regola diventa, per un confronto
   di stringhe, una forma diversa — e il conto della parita crolla senza che
   una sola scelta di disegno sia cambiata.

       ALZARE TUTTO IL TESTO DI UN PIXEL NON E RIDISEGNARE: E LEGGERE.

   Percio si misura DUE VOLTE: la parita letterale, e quella con il pavimento
   normalizzato a dieci. La differenza fra le due E la regola. */
const PAVIMENTO = (t) => t.replace(/font-size:([0-9.]+)px/g,
  (m, n) => 'font-size:' + (parseFloat(n) < 10 ? 10 : n) + 'px');

/* la FORMA visiva: tag + attributi, senza binding, testo, gestori, titoli */
const forme = (righe, pavimento) => {
  const testo = righe.join('\n')
    .replace(/\{\{[^}]*\}\}/g, '·')
    .replace(/>[^<]*</g, '><');
  const out = new Set();
  for (const t of (testo.match(/<[a-zA-Z-]+[^>]*>/g) || [])) {
    const g = pavimento ? PAVIMENTO(t) : t;
    out.add(g
      .replace(/ on[A-Z][a-zA-Z]*="[^"]*"/g, '')
      .replace(/ (title|aria-label|alt|href|role)="[^"]*"/g, '')
      .replace(/ hint-[a-z-]*="[^"]*"/g, '')
      .replace(/ data-[a-z-]*="[^"]*"/g, '')
      .replace(/ class="sn-[a-z]*"/g, '')
      .replace(/\s+/g, ' '));
  }
  return out;
};

const C = segmenta(markup(CASCO)), V = segmenta(markup(VIVO));
const schermate = Object.keys(C);
/* Una forma puo essere SPOSTATA invece che tolta: se non e piu su questa
   schermata ma esiste altrove nel portale, il disegno non e andato perduto,
   e cambiato di posto. Le due cose non si contano insieme. */
const OVUNQUE_VIVO = forme(Object.keys(V).reduce((a, k) => a.concat(V[k]), []));

let totC = 0, totTenute = 0, totPerse = 0;
const righeReport = [];
for (const s of schermate) {
  const fc = forme(C[s]), fv = forme(V[s] || []);
  const tenute = [...fc].filter(f => fv.has(f)).length;
  const perse = [...fc].filter(f => !fv.has(f));
  const nuove = [...fv].filter(f => !fc.has(f)).length;
  totC += fc.size; totTenute += tenute; totPerse += perse.length;
  const spostate = perse.filter(f => OVUNQUE_VIVO.has(f)).length;
  righeReport.push({ s, casco: fc.size, tenute, spostate, perse: perse.length - spostate, nuove,
    parita: fc.size ? Math.round(((tenute + spostate) / fc.size) * 1000) / 10 : 100 });
}
righeReport.sort((a, b) => a.parita - b.parita);

console.log('SCHERMATA'.padEnd(16), 'CASCO'.padStart(6), 'TENUTE'.padStart(7), 'SPOSTATE'.padStart(9), 'PERSE'.padStart(6), 'NUOVE'.padStart(6), 'PARITA'.padStart(7));
for (const r of righeReport) {
  console.log(r.s.padEnd(16), String(r.casco).padStart(6), String(r.tenute).padStart(7),
    String(r.spostate).padStart(9), String(r.perse).padStart(6), String(r.nuove).padStart(6), (r.parita + '%').padStart(7));
}
console.log('');
const totSpost = righeReport.reduce((a, r) => a + r.spostate, 0);
const totPerseVere = righeReport.reduce((a, r) => a + r.perse, 0);
console.log('FORME DEL CASCO', totC, '· TENUTE', totTenute, '· SPOSTATE', totSpost, '· PERSE', totPerseVere,
  '· PARITA LETTERALE', Math.round(((totTenute + totSpost) / totC) * 1000) / 10 + '%');

/* la seconda misura: la stessa, con il pavimento normalizzato */
const tuttoCasco = forme(Object.keys(C).reduce((a, k) => a.concat(C[k]), []), true);
const tuttoVivo = forme(Object.keys(V).reduce((a, k) => a.concat(V[k]), []), true);
const tenutePav = [...tuttoCasco].filter((f) => tuttoVivo.has(f)).length;
console.log('CON IL PAVIMENTO A 10px  ', tuttoCasco.size, '· tenute', tenutePav,
  '· PARITA', Math.round((tenutePav / tuttoCasco.size) * 1000) / 10 + '%');
const sotto = (file) => (fs.readFileSync(file, 'utf8').match(/font-size:([0-9.]+)px/g) || [])
  .filter((m) => parseFloat(m.slice(10)) < 10).length;
console.log('corpi sotto i 10px       ', 'casco', sotto(CASCO), '· portale', sotto(VIVO));

if (process.env.SCRIVI) {
  const dir = process.env.SCRIVI;
  for (const r of righeReport) {
    const fc = forme(C[r.s]), fv = forme(V[r.s] || []);
    const perse = [...fc].filter(x => !fv.has(x) && !OVUNQUE_VIVO.has(x));
    if (!perse.length) continue;
    fs.writeFileSync(dir + '/' + r.s + '.txt',
      'SCHERMATA ' + r.s + '\nFORME DEL CASCO ' + r.casco + ' · TENUTE ' + r.tenute +
      ' · SPOSTATE ' + r.spostate + ' · PERSE ' + r.perse + ' · PARITA ' + r.parita + '%\n\n' +
      perse.join('\n') + '\n');
  }
  console.log('scritti', righeReport.filter(r => r.perse).length, 'file in', dir);
}
if (process.env.DETTAGLIO) {
  for (const r of righeReport) {
    if (!r.perse) continue;
    console.log('\n── ' + r.s + ' · ' + r.perse + ' forme perse ──');
    const fc = forme(C[r.s]), fv = forme(V[r.s] || []);
    for (const f of [...fc].filter(x => !fv.has(x))) console.log('   ' + f.slice(0, 200));
  }
}
