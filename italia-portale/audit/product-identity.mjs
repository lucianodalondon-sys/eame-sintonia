/* SINTONIA ITALIA · IL NOME SI MOSTRA, LA CHIAVE SI UNISCE
   ---------------------------------------------------------------------------
   node audit/product-identity.mjs

   Il registro scrive NIMROD 250 EW. Il catalogo, per lo stesso prodotto,
   scrive NIMRODR 250 EW: il simbolo ® e arrivato a monte trasformato in una
   lettera. Altrove il catalogo tiene il simbolo vero (Folpan® Energy), o un
   punto in piu (NICOGAN V.O. contro NICOGAN VO), o due spazi (TAIFUN  MK), o
   uno zero appeso (GOLTIXR TOP 0). La chiave di unione era «trim e maiuscole»,
   quindi quindici prodotti del catalogo non trovavano il proprio numero di
   registrazione e la schermata diceva loro:

       «Non presente in questa lettura del registro»

   che e un'assenza FABBRICATA — il registro li contiene, con un'altra
   ortografia. Quattro di loro mostravano anche il nome storpiato al cliente:
   COSAYRR, GOLTIXR, NIMRODR, APYZAR.

   Il controllo tiene tre cose: che i quindici restino uniti, che nessun nome
   mostri la R al posto del simbolo, e che l'unione non abbia FUSO prodotti
   diversi — perche una chiave troppo generosa e peggio del difetto che cura.
   --------------------------------------------------------------------------- */
import { loadData } from './lib/harness.mjs';

const AM = loadData().ITALY_APP_MODEL;
const P = AM.collections.products.records;

/* I quindici che il catalogo scriveva diversamente dal registro. */
const REJOINED = [
  'Avastel', 'Diode', 'Folpan® Energy', 'Highcard', 'Lamdex® Extra', 'Maganic',
  'NICOGAN V.O.', 'Schermo® 0.5 G', 'Sonavio', 'Stavento', 'TAIFUN MK CL PFNPE',
  'APYZA® WG', 'COSAYR® 200 SC', 'GOLTIX® TOP', 'NIMROD® 250 EW',
];

const bad = { lost: [], corrupt: [], merged: [], missing: [] };

/* NON BASTA CHE findProduct TROVI QUALCOSA.
   findProduct conosce le stesse varianti dell'unione, quindi cercando
   «NIMROD® 250 EW» trova comunque la scheda del REGISTRO — anche se le due
   fonti NON si sono unite. Una prima versione di questo controllo passava
   proprio cosi, e passava anche col difetto rimesso dentro. Cio che va
   preteso e che la stessa entita porti ENTRAMBI i lati: la voce di catalogo
   e la riga di registro. */
for (const n of REJOINED) {
  const e = AM.findProduct(n);
  if (!e) { bad.missing.push(n); continue; }
  if (!e.inRegulatory || !e.reg) bad.lost.push(`${e.name} · no registration`);
  else if (!e.inCommercial) bad.lost.push(`${e.name} · registry and catalogue did not join`);
}

/* Il segno diventato lettera: <MARCHIO>R dove <MARCHIO> esiste da solo. */
const keys = new Set(P.map((p) => String(p.name || '').toUpperCase().replace(/[^A-Z0-9]/g, '')));
for (const p of P) {
  const m = /^([A-Za-z]{4,})R(\s|$)/.exec(String(p.name || '').trim());
  if (m && keys.has(m[1].toUpperCase())) bad.corrupt.push(`${p.name} · '${m[1]}' exists on its own`);
}

/* Una chiave troppo generosa fonde due prodotti veri. Ogni entita unita deve
   avere al massimo UN record di registro e UNO di catalogo. */
for (const p of P) {
  if (Array.isArray(p.regulatory) || Array.isArray(p.commercial)) bad.merged.push(p.name);
}
/* e due numeri di registrazione diversi non possono vivere sotto lo stesso nome */
const byReg = {};
for (const p of P) if (p.reg) (byReg[p.reg] = byReg[p.reg] || []).push(p.name);
for (const reg of Object.keys(byReg)) {
  if (byReg[reg].length > 1) bad.merged.push(`registration ${reg} on ${byReg[reg].length} entities: ${byReg[reg].join(', ')}`);
}

/* NON-VACUITA · se non trova i prodotti, non ha misurato niente. */
if (!P.length) bad.missing.push('no products at all');

const rows = [
  ['I1', 'the fifteen differently spelled products carry their registration', bad.lost],
  ['I2', 'no product name shows an R where the trademark sign belongs', bad.corrupt],
  ['I3', 'the join did not merge two different products', bad.merged],
  ['I4', 'every product under test was found', bad.missing],
];
const G = '\x1b[32m', R = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log(`\n  SINTONIA ITALY · PRODUCT IDENTITY   (${P.length} joined entities)`);
console.log('  ' + '-'.repeat(96));
let fails = 0;
for (const [id, title, list] of rows) {
  const ok = list.length === 0;
  if (!ok) fails++;
  console.log(`  ${ok ? G + 'PASS' + X : R + 'FAIL' + X}  ${id}  ${title.padEnd(58)} ${D}exp${X} 0  ${D}got${X} ${list.length}`);
  if (!ok) console.log(`        ${D}${list.slice(0, 6).join('  ')}${X}`);
}
console.log('  ' + '-'.repeat(96));
for (const n of ['COSAYR® 200 SC', 'GOLTIX® TOP', 'NIMROD® 250 EW', 'APYZA® WG']) {
  const e = AM.findProduct(n);
  console.log(`  ${D}repaired:${X} ${String(e ? e.name : n).padEnd(20)} ${D}registration${X} ${e && e.reg ? e.reg : '—'}`);
}
console.log('');
process.exit(fails === 0 ? 0 : 1);
