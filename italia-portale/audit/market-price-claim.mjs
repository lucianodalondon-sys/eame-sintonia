/* SINTONIA ITALIA · UN RECORD DI MERCATO NON E UN PREZZO
   ---------------------------------------------------------------------------
   node audit/market-price-claim.mjs

   Ottanta record su 157 non portano prezzo, ne unita, ne periodo, ne stato di
   serie. La schermata li contava insieme agli altri e chiamava il totale
   «righe di prezzo settimanali ingerite»: per il pomodoro annunciava dodici
   righe di prezzo dove i prezzi sono zero.

   E faceva un secondo passo sbagliato: «stato di serie assente» cadeva su
   «serie non corrente», cioe dichiarava FERMA una serie di cui non sa nulla,
   e stampava «serie ferma dal null» perche nemmeno l'anno esisteva.

       NON SAPERE SE UNA SERIE E CORRENTE NON E SAPERE CHE E FERMA.
       E UN RECORD SENZA PREZZO NON E UN PREZZO.

   Nessun record viene buttato: restano tutti nel corpus. Cio che cambia e che
   il contatore dice quale universo sta misurando.
   --------------------------------------------------------------------------- */
import { mount, loadData } from './lib/harness.mjs';
import { collectStrings } from './lang.mjs';

const AM = loadData().ITALY_APP_MODEL;
const R = AM.collections.marketObservations.records;
const m = mount();

const total = R.length;
const priced = R.filter((r) => r.hasPrice).length;
const stopped = R.filter((r) => r.isStoppedSeries).length;
const undeclared = R.filter((r) => r.seriesState === 'NOT_DECLARED').length;

const bad = { model: [], claim: [], nulls: [], render: [] };

/* 1 · il modello deve distinguere i tre stati */
if (priced === total) bad.model.push('every record claims a price: hasPrice is not discriminating');
if (stopped + undeclared + R.filter((r) => r.isCurrentSeries).length !== total) {
  bad.model.push(`the three series states do not add up to ${total}`);
}
if (R.some((r) => typeof r.hasPrice !== 'boolean')) bad.model.push('some records carry no hasPrice flag');

/* 2 · nessuna schermata puo chiamare «prezzi» il totale dei record */
let screens = 0;
for (const lang of ['it', 'en']) {
  for (const crop of ['tomato', 'apple', 'maize', 'olive']) {
    const r = m.tryVals({ view: 'market', lang, mCrop: crop });
    if (!r.ok) { bad.render.push(`${lang}·${crop}: ${r.error}`); continue; }
    screens++;
    for (const { value } of collectStrings(r.vals)) {
      const v = String(value);
      /* «serie ferma dal null», «(  )» e ogni null letterale */
      if (/\bnull\b/.test(v)) bad.nulls.push(`${lang}·${crop}: ${v.slice(0, 70)}`);
      /* il totale dei record annunciato come righe di prezzo */
      const mt = /(\d+)\s+(?:righe di prezzo settimanali ingerite|weekly price rows ingested)/.exec(v);
      if (mt) {
        const n = Number(mt[1]);
        const row = (AM.marketByCrop || []).find((x) => String(x.cropKey || '').toLowerCase().includes(crop.slice(0, 5)));
        if (row && n > row.priceCount) bad.claim.push(`${lang}·${crop}: claims ${n} price rows, the data has ${row.priceCount}`);
      }
    }
  }
}
if (screens < 8) bad.render.push(`only ${screens} of 8 market screens rendered`);

const rows = [
  ['M1', 'the model separates a market record from a price observation', bad.model],
  ['M2', 'no screen calls the record total a count of prices', bad.claim],
  ['M3', 'no literal null reaches a market screen', bad.nulls],
  ['M4', 'every market screen under test rendered', bad.render],
];
const G = '\x1b[32m', Rd = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log(`\n  SINTONIA ITALY · MARKET PRICE CLAIM   (${total} records · ${priced} with a price)`);
console.log('  ' + '-'.repeat(96));
let fails = 0;
for (const [id, title, list] of rows) {
  const ok = list.length === 0;
  if (!ok) fails++;
  console.log(`  ${ok ? G + 'PASS' + X : Rd + 'FAIL' + X}  ${id}  ${title.padEnd(56)} ${D}exp${X} 0  ${D}got${X} ${list.length}`);
  if (!ok) list.slice(0, 5).forEach((x) => console.log(`        ${D}${x}${X}`));
}
console.log('  ' + '-'.repeat(96));
console.log(`  ${D}series: ${R.filter((r) => r.isCurrentSeries).length} current · ${stopped} declared stopped · ${undeclared} not declared${X}\n`);
process.exit(fails === 0 ? 0 : 1);
