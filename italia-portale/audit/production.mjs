/* A PROVA CONTA ONDE O CLIENTE ABRE. Local e o meu servidor; producao e a
   Vercel, com o seu CDN, os seus cabecalhos e o seu build. */
import fs from 'node:fs';
import { chromium } from 'playwright-core';
import { loadData } from './lib/harness.mjs';
import { serve } from './lib/drive.mjs';
/* ── DOVE SI PROVA LA PRODUZIONE ────────────────────────────────────────────
   Il Chromium di questa sandbox non attraversa il proxy di uscita: la stessa
   pagina che curl scarica gli restituisce ERR_CONNECTION_RESET. Fingere di
   averla aperta sarebbe la peggiore delle prove.

       SI PROVA IL BYTE PUBBLICATO, NON UNA SUA COPIA LOCALE.

   Quindi si specchiano con curl i 61 file che la Vercel serve — HTML, tutti i
   moduli, il pacchetto del design system, i caratteri, le icone — e si apre
   QUELLO. Cio che questa prova non copre lo dice a voce: le intestazioni e il
   CDN, che si verificano a parte con curl. */
const MIRROR = process.env.SINTONIA_MIRROR || '';
/* L'INDIRIZZO PUBBLICO NON E SEMPRE QUELLO DELL'APICE. Una anteprima di ramo
   e un deploy vero, con lo stesso CDN e le stesse intestazioni, e va provata
   PRIMA di promuoverla. `--base https://…` la indirizza; senza argomento resta
   l'indirizzo che il cliente apre. */
const ARGV = process.argv.slice(2);
const BASE = (() => { const i = ARGV.indexOf('--base'); return i >= 0 ? String(ARGV[i + 1] || '').replace(/\/$/, '') : 'https://sintonia-eame-preview.vercel.app'; })();
const URL = MIRROR ? ('http://localhost:8971/portale.html') : (BASE + '/portale');
const AM = loadData().ITALY_APP_MODEL;
const OPP = AM.collections.opportunities.records;
const byId = {}; OPP.forEach((o) => { byId[o.id] = o; });

const server = MIRROR ? await serve(8971, MIRROR) : null;
const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome', '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
/* IL CHROMIUM DELLA SANDBOX NON ESCE DA SOLO.
   curl passa dal proxy perche legge le variabili d'ambiente; il browser no, e
   restituiva ERR_CONNECTION_RESET su un sito che era in piedi. Si passa lo
   stesso proxy e la stessa CA che tutto il resto della sandbox usa — non si
   disattiva la verifica, si dice al browser DOVE guardare. */
const PROXY = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || '';
const browser = await chromium.launch({
  executablePath: EXEC,
  /* `<-loopback>` dice al Chromium di NON scavalcare il proxy per localhost —
     cioe l'esatto contrario di quel che serve quando la copia e servita in
     locale: il proxy rispondeva 405 a un indirizzo che non e suo. Quando si
     prova lo specchio non si passa nessun proxy. */
  args: ['--no-sandbox', '--disable-quic', '--disable-http2']
    .concat((PROXY && !MIRROR) ? ['--proxy-server=' + PROXY, '--ignore-certificate-errors'] : []),
  ignoreHTTPSErrors: false,
});
const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true, ignoreHTTPSErrors: true });
const page = await ctx.newPage();
const errors = [], failed = [];
page.on('pageerror', (e) => errors.push(e.message.slice(0, 120)));
page.on('console', (m) => { if (m.type() === 'error' && !/attribute (d|cx|cy|x|y|r|points|width|height):.*\{\{/.test(m.text())) errors.push(m.text().slice(0, 120)); });
page.on('response', (r) => { if (r.status() >= 400) failed.push(r.status() + ' ' + r.url().slice(0, 90)); });

await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForTimeout(1500);

const R = {};
R.bg = await page.evaluate(() => getComputedStyle(document.querySelector('.sn-shell') || document.body).backgroundColor);
R.cards = await page.evaluate(() => document.querySelectorAll('[data-case]').length);
R.products = await page.evaluate(() => [...document.querySelectorAll('[data-product]')].map((e) => e.getAttribute('data-product')).filter(Boolean));
const txt = await page.evaluate(() => document.body.innerText);
R.chars = txt.length;
R.saysWhy = /PERCHE E COMMERCIALE/i.test(txt);
/* ══ QUESTA PROVA GUARDAVA UNA SUPERFICIE CHE NON C'E PIU ═══════════════════
   Cercava «PERCHE INTERESSA AD ADAMA», «PRODOTTI ADAMA COLLEGATI», «PROVE E
   FONTI», «MATERIALE DI CAMPO» e la pastiglia [data-brief-dept]. La superficie
   della riunione ha rinominato tutto: «PERCHE E COMMERCIALE», «PORTAFOGLIO»,
   «EVIDENZE» + «FONTI», e la mappa delle azioni con [data-action-dept]. Otto
   controlli su sedici erano quindi rossi su una schermata PIENA — e lo erano
   identici anche sull'indirizzo pubblico, cioe da giorni.

       UN CONTROLLO CHE CERCA UN NOME VECCHIO NON PROVA CHE MANCA QUALCOSA.
       PROVA CHE NESSUNO L'HA RILETTO.

   Adesso si legge dagli ATTRIBUTI che il markup dichiara apposta
   (data-meeting-*, data-action-dept, data-source-id): sopravvivono a un
   cambio di parola, non a un cambio di sostanza. */
/* «LO STATO DI PUBBLICAZIONE NON SI NASCONDE MAI» — lo dice il markup della
   scheda, ed e la legge che questo controllo deve difendere. Ogni scheda porta
   DUE stati: se e pubblicabile, e quanto vale commercialmente. Le parole
   vengono da meeting-labels.js, non da qui, cosi valgono in tutte e due le
   lingue e sopravvivono a una riscrittura del testo. */
const STATI = await page.evaluate(() => {
  const L = (window.MEETING_LABELS || { get: () => null });
  const lang = (document.documentElement.lang === 'en') ? 'en' : 'it';
  const w = (k) => L.get(k, lang);
  return {
    pubblicazione: ['PUBLISHABLE', 'VALIDATION_REQUIRED'].map(w).filter(Boolean),
    priorita: ['SALES_READY', 'STRATEGIC_OPPORTUNITY', 'COMMERCIAL_WATCH', 'TO_VALIDATE'].map(w).filter(Boolean),
  };
});
R.stateWords = STATI;
R.cardsWithState = await page.evaluate((S) => [...document.querySelectorAll('[data-case]')]
  .filter((c) => { const t = c.innerText || '';
    return S.pubblicazione.some((x) => t.includes(x)) && S.priorita.some((x) => t.includes(x)); }).length, STATI);
R.cardsWithWindowLines = await page.evaluate(() => [...document.querySelectorAll('[data-case]')]
  .filter((c) => c.hasAttribute('data-window-defined') && c.hasAttribute('data-window-open')).length);
R.junk = ['undefined', '[object Object]', '{{'].filter((j) => txt.includes(j));

/* o detalhe, por clique real, em producao */
await page.evaluate(() => { const c = document.querySelector('[data-case]'); if (c) c.click(); });
await page.waitForTimeout(1200);
const dtxt = await page.evaluate(() => document.body.innerText);
R.detailChars = dtxt.length;
R.detailHasActionMap = /MAPPA DELLE AZIONI|ACTION MAP/i.test(dtxt);
R.detailHasProducts = (await page.$('[data-meeting-products]')) !== null && (await page.$('[data-product]')) !== null;
R.detailSourceIds = await page.evaluate(() => document.querySelectorAll('[data-source-id]').length);
R.detailHasEvidence = (await page.$('[data-meeting-evidence]')) !== null && R.detailSourceIds > 0;
R.detailHasWhy = (await page.$('[data-meeting-why-commercial]')) !== null;
/* LA DIREZIONE DELLA NECESSITA e cio che questa superficie dichiara al posto
   del vecchio «MATERIALE DI CAMPO»: dice se la fonte chiede di intervenire o
   no. Un'opportunita che non la dichiara sta affermando senza dirlo. */
R.detailHasNeedDirection = (await page.$('[data-need-direction]')) !== null;
R.actionDepts = await page.evaluate(() => [...new Set([...document.querySelectorAll('[data-action-dept]')]
  .map((e) => e.getAttribute('data-action-dept')).filter(Boolean))].length);

/* o PDF · IL PACCHETTO D'AZIONE NON E RAGGIUNGIBILE DA UN'OPPORTUNITA.
   [data-download-pdf] vive sulla schermata «case» legacy, che il radar non
   apre piu: il radar apre il dettaglio della riunione. Non si finge di averlo
   provato — si dice dove sta e che da qui non ci si arriva. */
R.pdfOnDetail = (await page.$('[data-download-pdf]')) !== null;
if (R.pdfOnDetail) {
  try {
    const [dl] = await Promise.all([
      page.waitForEvent('download', { timeout: 25000 }),
      page.evaluate(() => document.querySelector('[data-download-pdf] button').click()),
    ]);
    const f = '/tmp/prod-brief.pdf'; await dl.saveAs(f);
    const buf = fs.readFileSync(f);
    R.pdfBytes = buf.length;
    R.pdfValid = buf.slice(0, 5).toString() === '%PDF-' && buf.slice(-1024).toString('latin1').includes('%%EOF');
  } catch (e) { R.pdfError = String(e.message).slice(0, 80); }
}
R.errors = errors; R.failed = [...new Set(failed)];
await browser.close();
if (server) server.close();

const g = (s) => `\x1b[32m${s}\x1b[0m`, r = (s) => `\x1b[31m${s}\x1b[0m`;
const L = (ok, id, name, got) => console.log(`  ${ok ? g('PASS') : r('FAIL')}  ${id.padEnd(5)} ${name.padEnd(52)} ${got}`);
console.log('\n  SINTONIA · PROVA EM PRODUCAO · ' + URL);
console.log('  ' + '─'.repeat(100));
L(R.bg === 'rgb(17, 14, 13)', 'P1', 'The approved dark surface is live', R.bg);
L(R.cards >= 12, 'P2', 'The radar renders opportunity cards', R.cards + ' cards');
L(R.products.length >= 12, 'P3', 'Every card names its product', R.products.length + ' named');
L(R.cardsWithState === R.cards, 'P4', 'Every card declares publication AND priority', R.cardsWithState + '/' + R.cards);
L(R.cardsWithWindowLines === R.cards, 'P5', 'Every card declares rule AND state of its window', R.cardsWithWindowLines + '/' + R.cards);
L(R.detailChars > 2500, 'P6', 'The detail is a hub, not an empty page', R.detailChars + ' chars');
L(R.detailHasActionMap, 'P7', 'The action map is on the detail', R.detailHasActionMap);
L(R.detailHasProducts, 'P8', 'The detail names the linked ADAMA portfolio', String(R.detailHasProducts));
L(R.detailHasEvidence, 'P9', 'Evidence and sources are on the detail', R.detailSourceIds + ' source ids');
L(R.detailHasWhy, 'P10', 'The detail says why the case is commercial', String(R.detailHasWhy));
L(R.detailHasNeedDirection, 'P11', 'The detail declares the direction of the need', String(R.detailHasNeedDirection));
L(R.actionDepts >= 5, 'P12', 'The action map covers every audience', R.actionDepts + ' departments');
L(!!R.pdfValid, 'P13', 'A real PDF is produced in production',
  R.pdfOnDetail ? ((R.pdfBytes || 0) + 'B ' + (R.pdfError || ''))
    : 'no download control on the opportunity detail — the action package lives on the legacy case route');
L(R.junk.length === 0, 'P14', 'No undefined / [object Object] / {{ }} on screen', R.junk.join(',') || 'clean');
L(R.errors.length === 0, 'P15', 'No console error in production', R.errors.length);
L(R.failed.length === 0, 'P16', 'No failed request in production', R.failed.length);
console.log('  ' + '─'.repeat(100));
console.log('  produtos nomeados: ' + R.products.slice(0, 8).join(' · '));
if (R.errors.length) R.errors.slice(0, 5).forEach((e) => console.log('   ' + r(e)));
if (R.failed.length) R.failed.slice(0, 5).forEach((e) => console.log('   ' + r(e)));
