/* SINTONIA · RTV_ELIGIBILITY_GATE + ADAMA_RELEVANCE_GATE
   ---------------------------------------------------------------------------
   node italia-portale/audit/rtv-gate.mjs [--json out.json]

   Due domande diverse, con due prove diverse:

       UNA SCHEDA CHE NON DICE PERCHE IMPORTA NON E UN'OPPORTUNITA.
       UN CASO CHE SERVE DENTRO NON E, PER QUESTO, UN MATERIALE DI CAMPO.

   Il portone apre il Chromium, legge la rilevanza su OGNI scheda, entra nei
   dettagli, e — sui casi idonei — CLICCA e scarica la scheda di campo, la apre
   con pdf.js e verifica che non porti in campo niente di interno. Sui casi non
   idonei verifica il contrario: che il pulsante NON esista e che la schermata
   dica perche.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { serve, open, openCase, caseIds, clickTitle, clickSelector, screenText, C, line } from './lib/drive.mjs';
import { loadData } from './lib/harness.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUT = arg('out', '/tmp/sintonia-rtv');
const JSON_OUT = arg('json', null);
const PORT = 8967;
fs.mkdirSync(OUT, { recursive: true });

const AM = loadData().ITALY_APP_MODEL;
const OPP = AM.collections.opportunities.records;
const byId = {}; OPP.forEach((o) => { byId[o.id] = o; });
const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
const readPdf = async (f) => {
  const d = await pdfjs.getDocument({ data: new Uint8Array(fs.readFileSync(f)), useSystemFonts: false }).promise;
  const pages = [];
  for (let i = 1; i <= d.numPages; i++) pages.push((await (await d.getPage(i)).getTextContent()).items.map((x) => x.str).join(' '));
  return { text: pages.join('\f'), pages: d.numPages };
};

const server = await serve(PORT);
const { browser, page, errors } = await open({ port: PORT });

/* ── 1 · OGNI SCHEDA DICE PERCHE IMPORTA ─────────────────────────────────── */
const cards = await page.evaluate(() => [...document.querySelectorAll('[data-case]')].map((c) => ({
  id: c.getAttribute('data-case'), text: (c.innerText || '').replace(/ /g, ' '),
})));
const relMissing = [];
for (const c of cards) {
  const o = byId[c.id];
  if (!o) continue;
  const ks = AM.adamaRelevance(o);
  const labels = ks.map((k) => (AM.RELEVANCE_LABEL[k] || [])[0]).filter(Boolean);
  if (!labels.some((l) => c.text.includes(l))) relMissing.push({ id: c.id, expected: labels });
}

/* ── 2 · IL CANCELLO RTV, DAI DUE LATI ───────────────────────────────────── */
const ids = await caseIds(page);
const readyIds = ids.filter((i) => byId[i] && AM.rtvEligibility(byId[i]).ready);
const blockedIds = ids.filter((i) => byId[i] && !AM.rtvEligibility(byId[i]).ready);
/* prova almeno un idoneo e tre bloccati, e se non c'e un idoneo sul radar lo
   si raggiunge per id: la prova non puo dipendere dall'ordinamento */
const probeReady = readyIds.slice(0, 1).length ? readyIds.slice(0, 1)
  : OPP.filter((o) => AM.rtvEligibility(o).ready).slice(0, 1).map((o) => o.id);
const probeBlocked = blockedIds.slice(0, 3);

const rows = [];
/* IL RADAR MOSTRA DODICI SCHEDE, E I TRE CASI IDONEI NON SONO FRA QUELLE.
   Il portone cercava la scheda fra le visibili e non la trovava: RT1, RT2 e
   tutte le RV passavano su un insieme VUOTO.

       UN PORTONE CHE PASSA SU ZERO CASI NON HA PROVATO NIENTE.

   Prima di cercare si apre l'elenco intero. */
const showAll = async () => {
  await page.evaluate(() => {
    /* Il pulsante e l'unico onClick={{ toggleAll }} della schermata, e il suo
       testo cambia con la lingua e con il numero. Si cerca la FORMA — una
       pastiglia cliccabile che nomina un totale — non una parola fissa. */
    /* La FOGLIA, non l'antenato. `textContent` di <body> contiene anche il
       testo del pulsante, quindi una ricerca per contenuto trova per prima la
       radice — e cliccare la radice non commuta niente.

           SI CERCA IL NODO CHE PORTA IL TESTO, NON UNO CHE LO CONTIENE. */
    const el = [...document.querySelectorAll('span,div,button')].filter((e) => {
      if (e.querySelector('span,div,button')) return false;         // solo foglie
      const t = (e.textContent || '').trim();
      return t.length > 4 && t.length < 60 && /\d{2}/.test(t) && /opportunit/i.test(t);
    })[0];
    if (el) {
      el.scrollIntoView({ block: 'center' });
      let n = el;
      for (let i = 0; i < 4 && n; i++) { if (getComputedStyle(n).cursor === 'pointer' || n.onclick) { n.click(); return; } n = n.parentElement; }
      el.click();
    }
  });
  await page.waitForTimeout(500);
};
const openBrief = async (id) => {
  await clickTitle(page, 'Radar delle Opportunità');
  await showAll();
  if (!await openCase(page, id, 600)) return false;
  return await clickSelector(page, '[data-brief-dept]', 700);
};

for (const id of probeReady) {
  const o = byId[id];
  const row = { id, expect: 'READY' };
  if (!await openBrief(id)) { row.error = 'brief non raggiunto'; rows.push(row); continue; }
  row.hasRtvButton = (await page.$('[data-download-rtv] button')) !== null;
  if (row.hasRtvButton) {
    try {
      const [dl] = await Promise.all([
        page.waitForEvent('download', { timeout: 15000 }),
        clickSelector(page, '[data-download-rtv] button', 200),
      ]);
      const file = path.join(OUT, id + '-rtv.pdf');
      await dl.saveAs(file);
      const buf = fs.readFileSync(file);
      row.file = file; row.bytes = buf.length;
      row.validPdf = buf.slice(0, 5).toString() === '%PDF-' && buf.slice(-1024).toString('latin1').includes('%%EOF');
      const { text, pages } = await readPdf(file);
      row.pages = pages; row.textLen = text.length; row.text = text;
      /* ── CIO CHE NON PUO ENTRARE IN CAMPO ────────────────────────────────
         Le aree interne, i token del motore, gli id, e ogni prodotto il cui
         legame NON e verificato. Un candidato in validazione su un foglio di
         campo si legge come una raccomandazione. */
      const internalAreas = ['MARKETING', 'APPROVVIGIONAMENTO', 'SUPPLY', 'SVILUPPO DI MERCATO', 'MARKET DEVELOPMENT', 'PORTAFOGLIO'];
      row.internalLeak = internalAreas.filter((a) => text.toUpperCase().includes(a));
      row.rawTokens = (text.match(/\b[A-Z][A-Z0-9]*(_[A-Z0-9]+)+\b/g) || []).filter((t, i, a) => a.indexOf(t) === i);
      row.idLeak = (text.match(/\b(OPP_[A-F0-9]{8,}|IT-[A-Z]{2,5}-\d+|SRC_[A-Z0-9_]+|AI_[A-Z0-9_]+|RFF_[A-Z0-9_]+)\b/g) || []);
      row.junk = [/\bundefined\b/, /\bnull\b/, /\bNaN\b/, /\[object Object\]/, /\{\{/]
        .filter((re) => re.test(text)).map(String);
      const unverified = (o.productLinks || []).filter((l) => l.strength !== 'VERIFIED_LABEL_MATCH').map((l) => l.name || l.product);
      row.unverifiedNamed = unverified.filter((n) => n && n.length > 3 && text.includes(n));
      const verified = (o.productLinks || []).filter((l) => l.strength === 'VERIFIED_LABEL_MATCH').map((l) => l.name || l.product);
      row.verifiedNamed = verified.filter((n) => text.includes(n));
      /* la scheda deve rimandare all'etichetta per dose e carenza: e la riga
         che impedisce a un foglio di sembrare una prescrizione */
      row.hasLabelDisclaimer = /etichetta del prodotto|product label/i.test(text);
      row.namesCrop = !!((o.cropKeys || [])[0] || o.crop) && text.includes(String((o.cropKeys || [])[0] || o.crop));
    } catch (e) { row.error = 'download non avvenuto: ' + String(e.message).slice(0, 70); }
  }
  rows.push(row);
}

for (const id of probeBlocked) {
  const row = { id, expect: 'BLOCKED' };
  if (!await openBrief(id)) { row.error = 'brief non raggiunto'; rows.push(row); continue; }
  row.hasRtvButton = (await page.$('[data-download-rtv] button')) !== null;
  const txt = await screenText(page);
  /* Bloccato non vuol dire muto: la schermata deve dire PERCHE. */
  row.explains = /MATERIALE DI CAMPO NON DISPONIBILE|FIELD MATERIAL NOT AVAILABLE/i.test(txt);
  const bl = AM.rtvEligibility(byId[id]).blockers.map((b) => (AM.RTV_BLOCKER_LABEL[b] || [])[0]).filter(Boolean);
  row.namesBlockers = bl.filter((b) => txt.includes(b)).length;
  row.expectedBlockers = bl.length;
  rows.push(row);
}

await browser.close(); server.close();

/* ── juizo ────────────────────────────────────────────────────────────────── */
const ready = rows.filter((r) => r.expect === 'READY' && !r.error);
const blocked = rows.filter((r) => r.expect === 'BLOCKED' && !r.error);
const noBtn = ready.filter((r) => !r.hasRtvButton).length;
const badPdf = ready.filter((r) => r.file && !r.validPdf).length;
const leak = ready.reduce((a, r) => a + (r.internalLeak || []).length, 0);
const tok = ready.reduce((a, r) => a + (r.rawTokens || []).length + (r.idLeak || []).length, 0);
const junk = ready.reduce((a, r) => a + (r.junk || []).length, 0);
const unver = ready.reduce((a, r) => a + (r.unverifiedNamed || []).length, 0);
const noDisc = ready.filter((r) => r.file && !r.hasLabelDisclaimer).length;
const btnWhenBlocked = blocked.filter((r) => r.hasRtvButton).length;
const silent = blocked.filter((r) => !r.explains).length;

console.log('\n  SINTONIA · ADAMA_RELEVANCE_GATE + RTV_ELIGIBILITY_GATE + RTV_PDF_TRUTH');
console.log('  ' + '─'.repeat(100));
console.log(line(relMissing.length === 0, 'AR1', 'Every card says why ADAMA should care', 0, relMissing.length));
/* Un PASS su zero casi e un PASS che non ha misurato niente: RT1 esige che
   almeno un caso idoneo sia stato davvero aperto. */
console.log(line(ready.length > 0 && noBtn === 0, 'RT1', 'An eligible case offers the field sheet', '>=1 ok', ready.length ? (noBtn ? noBtn + ' senza pulsante' : ready.length + ' provati') : 'NESSUN CASO PROVATO'));
console.log(line(badPdf === 0, 'RT2', 'The field sheet is a valid PDF', 0, badPdf));
console.log(line(btnWhenBlocked === 0, 'RT3', 'A blocked case offers NO field sheet', 0, btnWhenBlocked));
console.log(line(silent === 0, 'RT4', 'A blocked case says WHY it is blocked', 0, silent));
console.log(line(leak === 0, 'RV1', 'No internal area printed on a field sheet', 0, leak));
console.log(line(tok === 0, 'RV2', 'No engine token or internal id in the field sheet', 0, tok));
console.log(line(junk === 0, 'RV3', 'No undefined / null / NaN in the field sheet', 0, junk));
console.log(line(unver === 0, 'RV4', 'No unverified product named on a field sheet', 0, unver));
console.log(line(noDisc === 0, 'RV5', 'The field sheet sends dose and PHI to the label', 0, noDisc));
console.log(line(errors.length === 0, 'RV6', 'No console error during the whole run', 0, errors.length));
console.log('  ' + '─'.repeat(100));
console.log(`  RTV_MATERIAL_READY no modelo = ${OPP.filter((o) => AM.rtvEligibility(o).ready).length} / ${OPP.length}`);
console.log(`  provados idoneos = ${ready.length} · provados bloqueados = ${blocked.length}`);
for (const r of rows) {
  if (r.error) { console.log(`  ${r.id.padEnd(20)} ${r.expect.padEnd(8)} ${C.r(r.error)}`); continue; }
  if (r.expect === 'READY') {
    console.log(`  ${r.id.padEnd(20)} READY    ${r.hasRtvButton ? C.g('pulsante') : C.r('SENZA PULSANTE')}  ${r.bytes || 0}B ${r.pages || 0}p ${r.textLen || 0}ch  `
      + `prod ${(r.verifiedNamed || []).length}v/${(r.unverifiedNamed || []).length}nv  `
      + ((r.internalLeak || []).length ? C.r('AREA INTERNA: ' + r.internalLeak.join(',')) : C.g('nessuna area interna')));
  } else {
    console.log(`  ${r.id.padEnd(20)} BLOCKED  ${r.hasRtvButton ? C.r('PULSANTE PRESENTE') : C.g('nessun pulsante')}  ${r.explains ? C.g('spiega') : C.r('MUTO')}  motivi ${r.namesBlockers}/${r.expectedBlockers}`);
  }
}
if (relMissing.length) { console.log('\n  SCHEDE SENZA RILEVANZA:'); relMissing.slice(0, 8).forEach((m) => console.log('   ' + C.r(m.id) + ' attesa: ' + m.expected.join(' · '))); }
if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ rows, relMissing }, null, 1));
const FAIL = relMissing.length || ready.length === 0 || noBtn || badPdf || btnWhenBlocked || silent || leak || tok || junk || unver || noDisc || errors.length;
process.exit(FAIL ? 1 : 0);
