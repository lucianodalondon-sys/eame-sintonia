/* SINTONIA ITALIA · CHI PUO ESSERE CHIAMATO PRODOTTO ADAMA
   ---------------------------------------------------------------------------
   node audit/adama-product-claim.mjs

   Sei prodotti del catalogo hanno per titolare dell'autorizzazione SYNGENTA,
   ALBAUGH o MICROCIDE, e il portale li presentava sotto la fascetta «Prodotto
   ADAMA» — nello stesso sito che elenca SYNGENTA fra i concorrenti.

   Il pacchetto e esplicito, e vale citarlo per intero:

       «il titolare dell'autorizzazione NON e il venditore. La presenza nel
        catalogo non rivela il contratto, e il contratto non si deduce.»

   COMMERCIAL_CONTRACT e NOT_ESTABLISHED su tutti e 51. Quindi il solo fatto
   osservabile e la PUBBLICAZIONE sul catalogo pubblico di ADAMA Italia, e la
   regola che questo controllo tiene e una sola:

       DISPLAY_AS_ADAMA_PRODUCT  <=  prova di catalogo compatibile con ADAMA.
       UN TITOLARE ESTERNO, DA SOLO, NON PUO DIVENTARE UN PRODOTTO ADAMA.

   HOLDER_IS_ADAMA non e utilizzabile come prova: e `undefined` esattamente sui
   sei con titolare esterno e `false` su otto che non hanno titolare affatto.
   Il controllo legge la stringa del titolare, che e il fatto.
   --------------------------------------------------------------------------- */
import { mount, loadData } from './lib/harness.mjs';

const AM = loadData().ITALY_APP_MODEL;
const P = AM.collections.products.records;
const m = mount();

const isAdama = (h) => /\bADAMA\b/i.test(String(h || ''));
const external = P.filter((p) => p.holder && !isAdama(p.holder));
const claimed = P.filter((p) => p.displayAsAdamaProduct);

const bad = { claim: [], lost: [], unnamed: [], render: [], flag: [] };

/* 1 · La regola, sul modello. */
for (const p of external) {
  if (p.displayAsAdamaProduct) bad.claim.push(`${p.name} · ${p.holder}`);
}
/* 2 · Non deve aver spento i legittimi: i 45 restano prodotti ADAMA. */
const legit = P.filter((p) => p.inCommercial && !(p.holder && !isAdama(p.holder)));
for (const p of legit) {
  if (!p.displayAsAdamaProduct) bad.lost.push(p.name);
}
/* 3 · Non nascondere: i sei restano nel catalogo e il titolare si vede. */
let opened = 0;
for (const lang of ['it', 'en']) {
  for (const p of external) {
    const e = AM.findProduct(p.name);
    const r = m.tryVals({ view: 'product', productId: e ? e.key : null, lang });
    if (!r.ok || !r.vals || !r.vals.pd) { bad.render.push(`${lang}·${p.name}`); continue; }
    opened++;
    const pd = r.vals.pd;
    if (/prodotto adama|adama product/i.test(String(pd.kindL || ''))) {
      bad.claim.push(`${lang}·${p.name}: fascetta "${pd.kindL}"`);
    }
    if (!pd.hasExternalHolder || !String(pd.holderL || '').trim()) {
      bad.unnamed.push(`${lang}·${p.name}: il titolare non compare`);
    }
  }
  /* e un legittimo deve continuare a dirsi ADAMA, altrimenti la correzione
     avrebbe semplicemente spento l'etichetta per tutti */
  const someLegit = legit.slice(0, 8);
  for (const p of someLegit) {
    const e = AM.findProduct(p.name);
    const r = m.tryVals({ view: 'product', productId: e ? e.key : null, lang });
    if (!r.ok || !r.vals || !r.vals.pd) { bad.render.push(`${lang}·${p.name}`); continue; }
    opened++;
    if (!/prodotto adama|adama product/i.test(String(r.vals.pd.kindL || ''))) {
      bad.lost.push(`${lang}·${p.name}: fascetta "${r.vals.pd.kindL}"`);
    }
  }
}
/* 4 · Il flag del pacchetto non deve tornare a essere la prova. */
const flagWrong = external.filter((p) => p.commercial && p.commercial.holderIsAdama !== false);
if (flagWrong.length === external.length && external.length) {
  /* atteso: il flag NON distingue. Se un giorno lo facesse, si puo usarlo —
     ma finche non lo fa, chi lo usasse passerebbe tutti e sei. */
}
if (opened === 0) bad.render.push('nessun prodotto aperto: il controllo non ha misurato niente');
if (external.length === 0) bad.render.push('nessun titolare esterno trovato: il controllo non ha nulla da tenere');

const rows = [
  ['H1', 'no externally held product is presented as an ADAMA product', bad.claim],
  ['H2', 'the products that are ADAMA still say so', bad.lost],
  ['H3', 'an externally held product still names its holder', bad.unnamed],
  ['H4', 'every product under test actually opened', bad.render],
];
const G = '\x1b[32m', R = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log(`\n  SINTONIA ITALY · ADAMA PRODUCT CLAIM   (${external.length} externally held · ${claimed.length} claimed)`);
console.log('  ' + '-'.repeat(96));
let fails = 0;
for (const [id, title, list] of rows) {
  const ok = list.length === 0;
  if (!ok) fails++;
  console.log(`  ${ok ? G + 'PASS' + X : R + 'FAIL' + X}  ${id}  ${title.padEnd(56)} ${D}exp${X} 0  ${D}got${X} ${list.length}`);
  if (!ok) console.log(`        ${D}${list.slice(0, 6).join('  ')}${X}`);
}
console.log('  ' + '-'.repeat(96));
for (const p of external) console.log(`  ${D}held externally:${X} ${p.name.padEnd(16)} ${D}->${X} ${p.holder}`);
console.log(`\n  ${opened} product screens opened\n`);
process.exit(fails === 0 ? 0 : 1);
