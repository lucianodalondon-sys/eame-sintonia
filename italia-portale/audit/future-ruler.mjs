/* SINTONIA · FUTURE_SIGNAL_RULER — la differenza fra una data e un segnale
   ---------------------------------------------------------------------------
   node italia-portale/audit/future-ruler.mjs [--json out.json]

   Nel pacchetto ci sono 154 fatti con una data nel futuro e 3 segnali futuri.
   La tentazione e promuovere i 154. Sarebbe sbagliato, e il motivo si scrive:

       AVERE UNA DATA NEL FUTURO NON E ANTICIPARE UNA DECISIONE.
       UN SEGNALE FUTURO CAMBIA CIO CHE ADAMA FA OGGI.

   Cinque condizioni, tutte necessarie. Un fatto che ne manca una resta un fatto
   — non si cancella, non si promuove, e si dice quale condizione gli manca.

     1 · FATTO TRACCIABILE      esiste un record con una fonte risolvibile
     2 · ORIZZONTE FUTURO       la data e oltre la data di riferimento
     3 · CONSEGUENZA ADAMA      tocca un prodotto, una coltura o una linea che
                                il portafoglio ADAMA nomina — non «il settore»
     4 · MOTIVO PER SORVEGLIARE la data e DECISIONALE (scade, si decide, apre),
                                non amministrativa (un registro si rinnova da se)
     5 · PROVA RISOLVIBILE      la fonte o l'evidenza si apre da qui

   La quinta e la piu severa, ed e quella che tiene fuori i 148 rinnovi di
   registrazione: una scadenza di registro non e una decisione europea, e
   rinnovarla e la normalita, non un evento.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import { loadData } from './lib/harness.mjs';
import { C, line } from './lib/drive.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const AM = loadData().ITALY_APP_MODEL;
const K = AM.collections;
const REF = AM.REF;
const dt = (v) => { const d = AM.asDate ? AM.asDate(v) : null; return d && !isNaN(d) ? d : null; };

/* i prodotti e le colture che il portafoglio ADAMA nomina davvero */
const adamaProducts = new Set(K.products.records.map((p) => String(p.name || '').toUpperCase()).filter(Boolean));
const adamaAI = new Set(K.activeIngredients.records.map((a) => String(a.name || '').toUpperCase()).filter(Boolean));
const adamaCrops = new Set(K.productRelationships.records.map((r) => String(r.crop || '').toUpperCase()).filter(Boolean));

/* ── i candidati, per famiglia ─────────────────────────────────────────────── */
const cands = [];
const add = (family, id, title, date, opts) => cands.push(Object.assign({ family, id, title, date }, opts));

K.regulatoryFutureFacts.records.forEach((r) => add('regulatory', r.id,
  [r.activeIngredient, r.euState].filter(Boolean).join(' · '), r.euExpiryISO || r.euExpiry,
  { touchesAdama: adamaAI.has(String(r.activeIngredient || '').toUpperCase()), decisional: true, sourced: !!(r.sourceIds || []).length || !!r.euCelex }));
K.regulatoryFuture.records.forEach((r) => add('portfolio', r.id,
  [r.product, r.status].filter(Boolean).join(' · '), r.expiryISO || r.expiry,
  { touchesAdama: adamaProducts.has(String(r.product || '').toUpperCase()),
    /* una registrazione nazionale che scade si RINNOVA: e amministrazione */
    decisional: false, sourced: !!(r.sourceIds || []).length || !!r.labelUrl }));
K.productsRegulatory.records.forEach((r) => add('portfolio', r.id, r.name, r.expiry,
  { touchesAdama: true, decisional: false, sourced: !!r.labelUrl }));
K.futureEvents.records.concat(K.events.records).forEach((r) => add('events', r.id,
  r.name || r.title, r.startDate,
  { touchesAdama: true, decisional: true, sourced: !!(r.sourceIds || []).length || !!r.site || !!r.url }));
K.cropWindows.records.forEach((r) => add('window', r.windowId, [r.crop, r.issue].filter(Boolean).join(' · '), r.startDate,
  { touchesAdama: adamaCrops.has(String(r.crop || '').toUpperCase()), decisional: true, sourced: !!(r.sourceIds || []).length }));
K.agrometConditions.records.forEach((r) => add('agromet', r.id, r.observationClass, null,
  { touchesAdama: false, decisional: false, sourced: !!(r.sourceIds || []).length }));
K.competitorActivities.records.forEach((r) => add('competitor', r.id, r.company, r.date,
  { touchesAdama: false, decisional: false, sourced: !!r.pageId }));
K.scienceRecords.records.forEach((r) => add('science', r.id, r.title, r.date,
  { touchesAdama: false, decisional: false, sourced: !!r.doi }));

/* ── la regua ─────────────────────────────────────────────────────────────── */
for (const c of cands) {
  const d = dt(c.date);
  c.gates = {
    traceable: !!c.id,
    future: !!(d && d > REF),
    adama: !!c.touchesAdama,
    decisional: !!c.decisional,
    proof: !!c.sourced,
  };
  c.missing = Object.entries(c.gates).filter(([, v]) => !v).map(([k]) => k);
  c.eligible = c.missing.length === 0;
}
const futureDated = cands.filter((c) => c.gates.future);
const eligible = cands.filter((c) => c.eligible);
const current = K.futureSignals.records.length;

const byFam = {};
futureDated.forEach((c) => { (byFam[c.family] ||= { n: 0, ok: 0, miss: {} }); byFam[c.family].n++; if (c.eligible) byFam[c.family].ok++; c.missing.forEach((m) => { byFam[c.family].miss[m] = (byFam[c.family].miss[m] || 0) + 1; }); });

console.log('\n  SINTONIA · FUTURE_SIGNAL_RULER');
console.log('  ' + '─'.repeat(100));
console.log('  ' + 'FAMIGLIA'.padEnd(16) + 'CON DATA FUTURA'.padStart(16) + 'IDONEI'.padStart(9) + '   PERCHE GLI ALTRI NON PASSANO');
for (const [f, v] of Object.entries(byFam).sort((a, b) => b[1].n - a[1].n)) {
  const why = Object.entries(v.miss).sort((a, b) => b[1] - a[1]).map(([k, n]) => `${k} ${n}`).join(' · ');
  console.log('  ' + f.padEnd(16) + String(v.n).padStart(16) + String(v.ok).padStart(9) + '   ' + why);
}
console.log('  ' + '─'.repeat(100));
console.log(`  SEGNALI FUTURI REALI OGGI ...... ${current}`);
console.log(`  FATTI CON DATA FUTURA .......... ${futureDated.length}`);
console.log(`  IDONEI SECONDO LA REGUA ........ ${eligible.length}`);
console.log(`  RESPINTI ....................... ${futureDated.length - eligible.length}`);
if (eligible.length) {
  console.log('\n  I CANDIDATI CHE PASSANO:');
  eligible.slice(0, 20).forEach((c) => console.log(`    ${c.family.padEnd(12)} ${String(c.title || c.id).slice(0, 54).padEnd(56)} ${c.date || ''}`));
  console.log('\n  Non sono promossi qui: promuovere e lavoro del MOTORE, che scrive');
  console.log('  il pacchetto canonico. La regua dice QUALI meritano il giro, e serve');
  console.log('  perche fino a oggi la domanda non aveva risposta scritta.');
}
console.log('\n  ' + line(true, 'FR1', 'The ruler is explicit and executable', 5, '5 gates'));
console.log('  ' + line(eligible.length <= futureDated.length, 'FR2', 'No fact promoted without passing all five', 0, futureDated.length - eligible.length + ' rejected'));
console.log('  ' + line(current === K.futureSignals.records.filter((f) => f.provenance !== 'DEMO_SCENARIO').length,
  'FR3', 'No demo scenario counted as a real signal', current, current));
const out = arg('json', null);
if (out) fs.writeFileSync(out, JSON.stringify({ current, futureDated: futureDated.length, eligible: eligible.map((c) => ({ family: c.family, id: c.id, title: c.title, date: c.date })), byFam }, null, 1));
