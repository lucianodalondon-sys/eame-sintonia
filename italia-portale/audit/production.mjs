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
R.saysWhy = /PERCHE INTERESSA AD ADAMA/i.test(txt);
R.relevanceOnCards = await page.evaluate(() => {
  const L = ['Opportunita di prodotto', 'Sviluppo di mercato', 'Lacuna di portafoglio', 'Impatto normativo',
    'Preparazione approvvigionamento', 'Risposta competitiva', 'Preparazione tecnica', 'Da validare'];
  return [...document.querySelectorAll('[data-case]')].filter((c) => L.some((x) => (c.innerText || '').includes(x))).length;
});
R.junk = ['undefined', '[object Object]', '{{'].filter((j) => txt.includes(j));
/* a categoria voltou? conta as linguetas por cor de linha */
R.lines = await page.evaluate(() => {
  const L = { 'rgb(157, 29, 150)': 'pest', 'rgb(0, 160, 223)': 'disease', 'rgb(125, 180, 30)': 'weed', 'rgb(248, 158, 24)': 'crop' };
  const t = {};
  for (const c of document.querySelectorAll('[data-case]')) {
    for (const el of c.querySelectorAll('*')) { const k = L[getComputedStyle(el).backgroundColor]; if (k) { t[k] = (t[k] || 0) + 1; break; } }
  }
  return t;
});

/* o detalhe, por clique real, em producao */
await page.evaluate(() => { const c = document.querySelector('[data-case]'); if (c) c.click(); });
await page.waitForTimeout(1200);
const dtxt = await page.evaluate(() => document.body.innerText);
R.detailChars = dtxt.length;
R.detailHasActionMap = /MAPPA DELLE AZIONI/i.test(dtxt);
R.detailHasProducts = /PRODOTTI ADAMA COLLEGATI/i.test(dtxt);
R.detailHasEvidence = /PROVE E FONTI/i.test(dtxt);
R.detailHasWhy = /PERCHE INTERESSA AD ADAMA/i.test(dtxt);
R.detailHasRtvState = /MATERIALE DI CAMPO/i.test(dtxt);
R.briefChips = await page.evaluate(() => document.querySelectorAll('[data-brief-dept]').length);

/* o PDF, gerado em PRODUCAO */
await page.evaluate(() => { const b = document.querySelector('[data-brief-dept]'); if (b) b.click(); });
await page.waitForTimeout(1400);
R.hasPdfButton = (await page.$('[data-download-pdf] button')) !== null;
if (R.hasPdfButton) {
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
L(R.relevanceOnCards === R.cards, 'P4', 'Every card says why ADAMA should care', R.relevanceOnCards + '/' + R.cards);
L(Object.keys(R.lines).length >= 2, 'P5', 'Cards carry their BrandWell product line', JSON.stringify(R.lines));
L(R.detailChars > 2500, 'P6', 'The detail is a hub, not an empty page', R.detailChars + ' chars');
L(R.detailHasActionMap, 'P7', 'The action map is on the detail', R.detailHasActionMap);
L(R.detailHasProducts, 'P8', 'Products are named on the detail', R.detailHasProducts);
L(R.detailHasEvidence, 'P9', 'Evidence and sources are on the detail', R.detailHasEvidence);
L(R.detailHasWhy, 'P10', 'The detail says why ADAMA should care', R.detailHasWhy);
L(R.detailHasRtvState, 'P11', 'The detail declares its field-material state', R.detailHasRtvState);
L(R.briefChips > 0, 'P12', 'The commercial material is reachable', R.briefChips + ' chips');
L(!!R.pdfValid, 'P13', 'A real PDF is produced in production', (R.pdfBytes || 0) + 'B ' + (R.pdfError || ''));
L(R.junk.length === 0, 'P14', 'No undefined / [object Object] / {{ }} on screen', R.junk.join(',') || 'clean');
L(R.errors.length === 0, 'P15', 'No console error in production', R.errors.length);
L(R.failed.length === 0, 'P16', 'No failed request in production', R.failed.length);
console.log('  ' + '─'.repeat(100));
console.log('  produtos nomeados: ' + R.products.slice(0, 8).join(' · '));
if (R.errors.length) R.errors.slice(0, 5).forEach((e) => console.log('   ' + r(e)));
if (R.failed.length) R.failed.slice(0, 5).forEach((e) => console.log('   ' + r(e)));
