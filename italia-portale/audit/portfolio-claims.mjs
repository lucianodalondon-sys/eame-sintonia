/* SINTONIA ITALIA · CIO CHE IL PORTAFOGLIO PUO AFFERMARE
   ---------------------------------------------------------------------------
   node audit/portfolio-claims.mjs

   Due frasi del portafoglio dicevano piu di quanto il dato sostenga.

   La prima: una REGISTRAZIONE SCADUTA veniva mostrata in verde come
   «Registrato in Italia». Presenza nel registro e validita formale sono due
   cose diverse — quindici prodotti hanno una data di scadenza gia passata
   rispetto alla data di riferimento del pacchetto.

   La seconda: RELATED_PORTFOLIO — che significa «l'etichetta dichiara
   SEPARATAMENTE che il prodotto agisce su questo bersaglio e che si impiega su
   questa coltura» — veniva stampato come «riga d'uso autorizzata nel registro
   nazionale», cioe una affermazione piu forte di quella riservata alla
   corrispondenza verificata.

       UNA RELAZIONE DI PORTAFOGLIO NON E UNA AUTORIZZAZIONE DI ETICHETTA.
       UNA REGISTRAZIONE SCADUTA NON E UNA REGISTRAZIONE VIVA.

   Il controllo apre ogni prodotto interessato nelle due lingue. Se non riesce
   ad aprirne nessuno, fallisce: non avrebbe misurato niente.
   --------------------------------------------------------------------------- */
import { mount, loadData } from './lib/harness.mjs';

const AM = loadData().ITALY_APP_MODEL;
const R = AM.collections.products.records;
const m = mount();

const isPast = (p) => p.expiresInDays !== undefined && p.expiresInDays !== null && p.expiresInDays < 0;
const expired = R.filter(isPast);
const live = R.filter((p) => p.inRegulatory && !isPast(p));

const pd = (p, lang) => {
  const e = AM.findProduct(p.name);
  const r = m.tryVals({ view: 'product', productId: e ? e.key : null, lang });
  return (r.ok && r.vals && r.vals.pd) ? r.vals.pd : null;
};

const LIVE_LABEL = { it: 'Registrato in Italia', en: 'Registered in Italy' };
/* La vecchia frase, quella che rivendicava una autorizzazione dello Stato. */
const OLD_AUTH_CLAIM = /riga d'uso autorizzata nel registro nazionale|authorised use row in the national registry/i;

const bad = { expiredGreen: [], liveLost: [], authClaim: [], render: [] };
let opened = 0;

for (const lang of ['it', 'en']) {
  for (const p of expired) {
    const v = pd(p, lang);
    if (!v) { bad.render.push(`${lang}·${p.name}`); continue; }
    opened++;
    if (String(v.regulatoryL || '') === LIVE_LABEL[lang]) bad.expiredGreen.push(`${lang}·${p.name}·${p.expiry}`);
  }
  /* Non-vacuita al contrario: la correzione non deve aver spento anche i vivi. */
  for (const p of live.slice(0, 25)) {
    const v = pd(p, lang);
    if (!v) { bad.render.push(`${lang}·${p.name}`); continue; }
    opened++;
    if (String(v.regulatoryL || '') !== LIVE_LABEL[lang]) bad.liveLost.push(`${lang}·${p.name}·${v.regulatoryL}`);
  }
  /* Nessuna riga di relazione puo rivendicare una riga d'uso autorizzata. */
  for (const p of R.slice(0, 60)) {
    const v = pd(p, lang);
    if (!v) continue;
    for (const row of [].concat(v.related || [], v.verified || [])) {
      if (OLD_AUTH_CLAIM.test(String(row.evidence || ''))) bad.authClaim.push(`${lang}·${p.name}`);
    }
  }
}

if (opened === 0) bad.render.push('nessun prodotto aperto: il controllo non ha misurato niente');

const rows = [
  ['R1', 'an expired registration is never shown as live', bad.expiredGreen],
  ['R2', 'a live registration is still shown as registered', bad.liveLost],
  ['R3', 'a portfolio relationship never claims an authorised use row', bad.authClaim],
  ['R4', 'every product under test actually opened', bad.render],
];
const G = '\x1b[32m', RD = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log(`\n  SINTONIA ITALY · PORTFOLIO CLAIMS   (${expired.length} expired · ${live.length} live)`);
console.log('  ' + '-'.repeat(96));
let fails = 0;
for (const [id, title, list] of rows) {
  const ok = list.length === 0;
  if (!ok) fails++;
  console.log(`  ${ok ? G + 'PASS' + X : RD + 'FAIL' + X}  ${id}  ${title.padEnd(58)} ${D}exp${X} 0  ${D}got${X} ${list.length}`);
  if (!ok) console.log(`        ${D}${list.slice(0, 5).join('  ')}${X}`);
}
console.log('  ' + '-'.repeat(96));
console.log(`  ${opened} product screens opened\n`);
process.exit(fails === 0 ? 0 : 1);
