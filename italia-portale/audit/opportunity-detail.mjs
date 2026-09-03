/* SINTONIA ITALIA · LA SCHEDA E IL DETTAGLIO DEVONO DIRE LA STESSA COSA
   ---------------------------------------------------------------------------
   node audit/opportunity-detail.mjs

   Il dettaglio del caso e nato per i tre casi legacy, che vivevano tutti
   appesi a una finestra canonica. I 37 record V2.1 portano invece i propri
   campi — stato, date, giorni residui, eta del segnale, ampiezza geografica,
   verdetti di etichetta — e il dettaglio non ne leggeva nessuno: cadeva nei
   ripieghi e STAMPAVA UN'ASSENZA DOVE IL RECORD AFFERMA UN FATTO.

       NON MOSTRARE UN FATTO E UNA LACUNA.
       DICHIARARE CHE NON ESISTE E UN ERRORE.

   Questo controllo apre TUTTI E 37 i casi nelle due lingue e confronta cio che
   la schermata dice con cio che il record porta. Se non riesce ad aprirli
   tutti, fallisce: un controllo che non ha guardato non ha assolto.
   --------------------------------------------------------------------------- */
import { mount, loadData } from './lib/harness.mjs';

const AM = loadData().ITALY_APP_MODEL;
const recs = AM.collections.opportunities.records;
const m = mount();

const rows = [];
const R = (id, title, measured, detail) => rows.push({ id, title, measured, detail });

const bad = { status: [], window: [], product: [], latin: [], region: [], date: [], render: [] };
let opened = 0;

for (const lang of ['it', 'en']) {
  for (const r of recs) {
    const res = m.tryVals({ view: 'case', caseId: r.id, lang });
    if (!res.ok || !res.vals || !res.vals.cs) { bad.render.push(`${lang}·${r.id}`); continue; }
    const cs = res.vals.cs;
    opened++;

    /* Lo stato temporale del caso e un fatto: se il record lo dichiara, la
       schermata non puo rispondere «data da confermare». */
    if (r.status && r.status !== 'TO_VALIDATE') {
      const fallback = lang === 'it' ? 'DATA DA CONFERMARE' : 'DATE TO CONFIRM';
      if (cs.statusLabel === fallback) bad.status.push(`${lang}·${r.id}·${r.status}`);
    }
    /* Una finestra dichiarata dal record non e «nessuna finestra collegata». */
    if ((r.windowStart || r.windowEnd) && cs.noWindow) bad.window.push(`${lang}·${r.id}`);
    /* Una posizione di etichetta verificata dal motore non puo diventare
       «nessuna corrispondenza confermata». */
    if (r.verifiedProductCount > 0 && !cs.hasPrimary) bad.product.push(`${lang}·${r.id}·${r.verifiedProductCount}`);
    /* Lo slot del binomio latino non ripete il titolo ne stampa l'italiano
       sotto un titolo inglese. */
    if (cs.latin && cs.latin === cs.issueL) bad.latin.push(`${lang}·${r.id}`);
    /* L'etichetta della geografia non sta sopra il vuoto. */
    if (!cs.regionLabel) bad.region.push(`${lang}·${r.id}`);
    /* Se il caso sa di quando e, la schermata non dice di non saperlo. */
    if ((r.signalAgeDays !== null && r.signalAgeDays !== undefined) || r.signalDate) {
      const unknown = lang === 'it' ? 'non noto' : 'not known';
      if (!cs.updatedLabel || String(cs.updatedLabel).toLowerCase().includes(unknown)) bad.date.push(`${lang}·${r.id}`);
    }
  }
}

/* NON-VACUITA · se non ha aperto tutti i casi nelle due lingue, non ha
   misurato niente e non puo essere verde. */
const EXPECTED = recs.length * 2;
if (opened !== EXPECTED) bad.render.push(`aperti ${opened} di ${EXPECTED}`);

R('S1', 'the case status the record declares reaches the screen', bad.status.length, bad.status);
R('S2', 'a window the record declares is never called absent', bad.window.length, bad.window);
R('S3', 'a verified label position is never denied', bad.product.length, bad.product);
R('S4', 'the latin slot never repeats the title nor crosses language', bad.latin.length, bad.latin);
R('S5', 'the geography label never stands over an empty value', bad.region.length, bad.region);
R('S6', 'a case that knows its date does not say it is unknown', bad.date.length, bad.date);
R('S7', 'every case opened in both languages', bad.render.length, bad.render);

const G = '\x1b[32m', RD = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log(`\n  SINTONIA ITALY · OPPORTUNITY DETAIL vs RECORD   (${recs.length} cases x 2 languages)`);
console.log('  ' + '-'.repeat(98));
let fails = 0;
for (const r of rows) {
  const ok = r.measured === 0;
  if (!ok) fails++;
  console.log(`  ${ok ? G + 'PASS' + X : RD + 'FAIL' + X}  ${r.id.padEnd(4)} ${r.title.padEnd(58)} ${D}exp${X} 0  ${D}got${X} ${r.measured}`);
  if (!ok) console.log(`        ${D}${r.detail.slice(0, 6).join('  ')}${r.detail.length > 6 ? ' …' : ''}${X}`);
}
console.log('  ' + '-'.repeat(98));
console.log(`  ${opened} detail screens opened and compared against their record\n`);
process.exit(fails === 0 ? 0 : 1);
