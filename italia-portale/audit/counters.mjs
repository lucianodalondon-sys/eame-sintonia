/* SINTONIA ITALIA · LA RICONCILIAZIONE DEI CONTATORI
   ---------------------------------------------------------------------------
   node audit/counters.mjs

   Legge i numeri DUE volte — una dal modello, una dallo SCHERMO — e li mette
   uno accanto all'altro. Non si fida di nessuna costante, comprese le proprie:
   ogni riga qui sotto e misurata, e la colonna «=» dice se le due letture
   parlano dello stesso universo.

       UN NUMERO CHE COMPARE IN UN RAPPORTO E UN NUMERO CHE QUALCUNO
       HA COPIATO. UN NUMERO CHE COMPARE DUE VOLTE E STATO MISURATO.

   E la ragione per cui esiste: le due letture possono divergere legittimamente.
   La navigazione conta l'ARCHIVIO come indice (958 righe che rileggono record
   gia contati altrove), mentre il modello conta le famiglie. Dire «958 record»
   accanto a «6.876 record» sarebbe sommare due volte la stessa verita. Dove le
   due letture misurano cose diverse, la riga lo dichiara invece di allinearle.
   --------------------------------------------------------------------------- */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { loadData } from './lib/harness.mjs';
import { navName } from './lib/nav-names.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = arg('base', null);
const PORT = Number(arg('port', 8913));

let server = null;
let origin = BASE;
if (!BASE) {
  const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json', '.css': 'text/css', '.png': 'image/png', '.ttf': 'font/ttf', '.otf': 'font/otf' };
  server = http.createServer((req, res) => {
    const url = decodeURIComponent((req.url || '/').split('?')[0]);
    if (url === '/favicon.ico') { res.writeHead(204).end(); return; }
    fs.readFile(path.join(CLIENT, url === '/' ? '/portale.html' : url), (e, b) => {
      if (e) { res.writeHead(404).end('404'); return; }
      res.writeHead(200, { 'content-type': TYPES[path.extname(url)] || 'application/octet-stream' }).end(b);
    });
  });
  await new Promise((r) => server.listen(PORT, r));
  origin = `http://localhost:${PORT}`;
}

const ctx = loadData();
const AM = ctx.ITALY_APP_MODEL;
const C = AM.collections;
const opp = C.opportunities.records;

const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
await page.goto(`${origin}/portale.html`, { waitUntil: 'networkidle' });
await page.waitForTimeout(900);

/* La navigazione porta il proprio conteggio accanto al nome: e il numero che
   il cliente legge, non quello che il modello pensa. */
const nav = await page.evaluate(() => {
  const out = {};
  for (const e of document.querySelectorAll('[title]')) {
    const row = e.parentElement;
    if (!row) continue;
    const t = (row.innerText || '').trim().split('\n').map((x) => x.trim()).filter(Boolean);
    if (t.length >= 2 && /^\d+$/.test(t[t.length - 1])) out[e.getAttribute('title')] = Number(t[t.length - 1]);
  }
  return out;
});
const screenText = await page.evaluate(() => document.body.innerText || '');
const num = (re) => { const m = screenText.match(re); return m ? Number(m[1]) : null; };

const rows = [];
const R = (label, model, screen, note) => rows.push({ label, model, screen, note: note || '' });

/* ══ LE 43 SI DIVIDONO IN TRE, E IL TOTALE NON SPARISCE ═══════════════════
   Questo blocco confrontava le 43 del pacchetto con la pastiglia del radar, e
   la pastiglia ne dice 13. Non e una divergenza: e la LEGGE DI RILEVANZA
   ADAMA (scripts/adama_relevance.py), che chiama «opportunita» solo cio che si
   lega a un prodotto ADAMA e manda il resto a radar e a segnali. La riga
   `TO VALIDATE` peggiorava l'errore: la sua regex prendeva il «21» di
   «21 RADAR · DA VALIDARE» e lo confrontava con le 10 TO_VALIDATE del modello.

       DUE NUMERI DIVERSI NON SONO UNA CONTRADDIZIONE SE CONTANO DUE COSE.
       MA CHI LI CONFRONTA DEVE DIRE QUALI DUE COSE SONO.

   Adesso si riconcilia popolazione per popolazione, con i nomi che lo schermo
   usa, e in piu si prova che le tre piu l'errore FANNO 43: cosi la legge non
   puo perdere un caso per strada senza che questo conto lo veda. */
const REL = (ctx.MEETING_SURFACE && ctx.MEETING_SURFACE.build('it') || {}).relevance || {};
R('OPPORTUNITIES · package total', opp.length, num(/OPPORTUNITÀ ATTUALI\s*\n\s*(\d+)\s*\n\s*·/i),
  'la legge di rilevanza le divide in tre — nessuna sparisce');
R('  OPPORTUNITÀ (linked to an ADAMA product)', REL.OPPORTUNITA ?? null, num(/·\s*(\d+)\s+OPPORTUNITÀ/i));
R('  RADAR · da validare', REL.RADAR ?? null, num(/·\s*(\d+)\s+RADAR/i));
R('  SEGNALI grezzi', REL.SEGNALI ?? null, num(/·\s*(\d+)\s+SEGNALI/i));
R('  the three plus error = the package total',
  (REL.OPPORTUNITA ?? 0) + (REL.RADAR ?? 0) + (REL.SEGNALI ?? 0) + (REL.ERRORE ?? 0), opp.length,
  'se questa riga si spezza, la legge ha perso un caso');
R('  VERIFIED CONVERGENCE (model)', opp.filter((o) => o.convergence === 'VERIFIED_CONVERGENCE').length,
  num(/(\d+)\s+convergenze verificate/i));

R('CANONICAL CROP WINDOWS', C.cropWindows.count, nav['Finestre Colturali']);
R('FIELD READINGS (not windows)', C.currentFieldSignals.count, null,
  'separate universe · IT-WIN-001..007');
R('FIELD BULLETINS', C.fieldBulletins.count, null, 'regional bulletins as read');

R('COMMERCIAL PRODUCTS', C.productsCommercial.count, null);
R('REGULATORY PRODUCTS', C.productsRegulatory.count, null);
R('  portfolio nav (both, deduplicated)', C.products.count, nav['Portafoglio']);
R('LABEL USE PAIRS', C.productRelationships.count, num(/(\d+)\s*$/m) === null ? null : null,
  'shown as the portfolio-links KPI');
R('ACTIVE SUBSTANCES', C.activeIngredients.count, null);

R('MARKET', C.marketObservations.count, nav[navName('it', 'navMarket')]);
R('SCIENCE', C.scienceRecords.count, nav[navName('it', 'navScience')]);
R('RESISTANCE', C.resistance.count, null, 'inside Scientific Intelligence');
R('COMPETITOR', C.competitorActivities.count, nav[navName('it', 'navCompetitors')]);
R('VOICES', C.publicVoices.count, nav[navName('it', 'navVoices')]);
R('FUTURE', C.futureSignals.count, nav[navName('it', 'navFuture')]);
R('SOURCES', C.sources.count, nav[navName('it', 'navSources')]);
R('ARCHIVE (index over the model)', C.archive.count, nav[navName('it', 'navArchive')],
  'an index, never summed with the families');

/* Il KPI dei collegamenti di portafoglio e l'unico posto dove le 2.030 duplas
   compaiono come numero grande sulla schermata. */
const kpiLinks = await page.evaluate(() => {
  const t = document.body.innerText || '';
  const m = t.match(/(\d[\d.]*)\s*\n?\s*Collegamenti di portafoglio/i);
  return m ? Number(String(m[1]).replace(/\./g, '')) : null;
});
const lp = rows.find((r) => r.label === 'LABEL USE PAIRS');
if (lp) lp.screen = kpiLinks;

await browser.close();
if (server) server.close();

const G = '\x1b[32m', R_ = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log('');
console.log(`  SINTONIA ITALY · COUNTER RECONCILIATION   (${origin})`);
console.log('  ' + '─'.repeat(96));
console.log(`  ${'measure'.padEnd(38)} ${'model'.padStart(7)} ${'screen'.padStart(7)}  =`);
console.log('  ' + '─'.repeat(96));
let mismatches = 0;
for (const r of rows) {
  const same = r.screen === null || r.screen === undefined ? null : r.model === r.screen;
  if (same === false) mismatches++;
  const mark = same === null ? `${D}—${X}` : same ? `${G}✓${X}` : `${R_}✗${X}`;
  console.log(`  ${r.label.padEnd(38)} ${String(r.model).padStart(7)} ${String(r.screen ?? '—').padStart(7)}  ${mark}   ${D}${r.note}${X}`);
}
console.log('  ' + '─'.repeat(96));
console.log(`  ${mismatches} mismatch(es) between what the model holds and what the screen shows`);
console.log('');
process.exit(mismatches === 0 ? 0 : 1);
