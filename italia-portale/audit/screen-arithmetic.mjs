/* SINTONIA ITALIA · UNA SCHERMATA NON PUO SMENTIRSI DA SOLA
   ---------------------------------------------------------------------------
   node audit/screen-arithmetic.mjs [--base http://host]

   Sul Radar il contatore diceva «5 · DATA DA CONFERMARE» e sotto, sulla stessa
   schermata, dodici schede portavano scritto DATA DA CONFERMARE. Nessuno dei
   due numeri era sbagliato: cinque sono le FINESTRE canoniche senza data,
   dodici erano i CASI senza finestra dichiarata. Due popolazioni diverse che
   avevano preso in prestito la stessa frase.

       CHI LEGGE NON HA MODO DI SAPERE CHE SONO DUE COSE.
       CONTA, TROVA DODICI, LEGGE CINQUE, E SMETTE DI FIDARSI.

   Il controllo cerca, su ogni schermata, ogni cifra che porta accanto una
   parola, e conta quante ALTRE volte quella stessa parola compare come
   etichetta di un elemento. Se le due misure non coincidono e il contatore non
   dichiara di che popolazione parla, e un'ambiguita e fallisce.

   Si guarda in UNA SOLA DIREZIONE, e per una ragione. Un contatore piu ALTO di
   cio che si vede e normale: la lista e paginata o filtrata, e ventinove
   finestre non stanno in cinque righe. Un contatore piu BASSO non ha scuse:
   non si possono disegnare dodici membri di un insieme che ne dichiara cinque.
   Quella e la direzione in cui un lettore attento trova l'errore, ed e la sola
   che qui fallisce — un controllo che grida al lupo insegna a non ascoltarlo.

   Un contatore puo comunque difendersi dicendo il denominatore: «su 29 finestre
   canoniche» chiude la questione, perche il lettore sa contro cosa contare.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = arg('base', null);
const PORT = Number(arg('port', 8993));

const NAV = {
  it: ['Radar delle Opportunità', 'Radar Futuro', 'Finestre Colturali', 'Polso di Mercato',
    'Portafoglio', 'Voci dal Campo', 'Concorrenza', 'Intelligence Scientifica', 'Fonti'],
  en: ['Opportunity Radar', 'Future Radar', 'Crop Windows', 'Market Pulse',
    'Portfolio', 'Field Voices', 'Competitor Watch', 'Scientific Intelligence', 'Sources'],
};

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.css': 'text/css', '.png': 'image/png', '.ttf': 'font/ttf', '.otf': 'font/otf' };
const server = BASE ? null : http.createServer((q, r) => {
  const u = decodeURIComponent((q.url || '/').split('?')[0]);
  if (u === '/favicon.ico') { r.writeHead(204).end(); return; }
  fs.readFile(path.join(CLIENT, u === '/' ? '/portale.html' : u), (e, b) => {
    if (e) { r.writeHead(404).end('404'); return; }
    r.writeHead(200, { 'content-type': TYPES[path.extname(u)] || 'application/octet-stream' }).end(b);
  });
});
if (server) await new Promise((r) => server.listen(PORT, r));
const ORIGIN = BASE || `http://localhost:${PORT}`;
const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });

/* Il rilievo vive nel browser: legge le coppie (cifra, etichetta) e poi conta
   quante volte quella etichetta compare da sola altrove sulla stessa schermata. */
const PROBE = () => {
  const txt = (el) => (el.textContent || '').trim();
  const leaves = [...document.querySelectorAll('span,div,p,strong,b,em,li,td,th')]
    .filter((el) => el.children.length === 0 && txt(el) && txt(el).length <= 60);
  /* una coppia contatore = un numero puro con, accanto, una parola in un blocco
     che contiene solo quei due (piu un eventuale sottotitolo) */
  const counters = [];
  for (const el of leaves) {
    const t = txt(el);
    if (!/^\d{1,5}$/.test(t)) continue;
    /* la cifra sta quasi sempre in un involucro stretto: si sale finche il
       blocco non porta anche la parola, non oltre. */
    let box = el.parentElement, lines = [];
    for (let i = 0; i < 4 && box; i++) {
      lines = (box.innerText || '').split('\n').map((x) => x.trim()).filter(Boolean);
      if (lines.length >= 2) break;
      box = box.parentElement;
    }
    if (lines.length < 2 || lines.length > 3 || lines[0] !== t) continue;
    counters.push({ n: Number(t), label: lines[1], sub: lines[2] || '' });
  }
  const labelCount = {};
  for (const el of leaves) {
    const t = txt(el);
    labelCount[t] = (labelCount[t] || 0) + 1;
  }
  return { counters, labelCount };
};

const bad = [];
let measured = 0;
/* «su 29 finestre canoniche», «of 29 canonical windows», «di 37», «esclusi» ...
   una sottolinea che dichiara una popolazione o un'esclusione mette il lettore
   in condizione di contare, ed e esattamente cio che chiediamo. */
const DECLARES = /\b(su|of|sulle|delle|dei|out of|esclus|excluded|canonich|canonical|su \d)\b/i;

for (const lang of ['it', 'en']) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1400 } });
  await page.goto(`${ORIGIN}/portale.html`, { waitUntil: 'networkidle', timeout: 180000 });
  await page.waitForTimeout(1200);
  if (lang === 'en') {
    await page.evaluate(() => { const e = [...document.querySelectorAll('span,div')].find((x) => x.textContent.trim() === 'EN');
      let n = e; for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer') { n.click(); return; } n = n.parentElement; } });
    await page.waitForTimeout(900);
  }
  for (const label of NAV[lang]) {
    const went = await page.evaluate((t) => { const h = document.querySelector(`[title="${t}"]`); if (!h) return false;
      let n = h; for (let i = 0; i < 4 && n; i++) { if (getComputedStyle(n).cursor === 'pointer') { n.click(); return true; } n = n.parentElement; } h.click(); return true; }, label);
    if (!went) { bad.push(`${lang}·${label}: schermata irraggiungibile`); continue; }
    await page.waitForTimeout(700);
    measured++;
    const { counters, labelCount } = await page.evaluate(PROBE);
    for (const c of counters) {
      /* una parola, non un glifo: un pallino ripetuto non e un'etichetta */
      if (!/\p{L}{3}/u.test(c.label)) continue;
      /* quante volte quella parola compare come etichetta a se stante, tolta
         l'occorrenza del contatore stesso */
      const seen = (labelCount[c.label] || 1) - 1;
      if (seen <= c.n) continue;
      if (DECLARES.test(c.sub)) continue;
      bad.push(`${lang}·${label}: «${c.n} ${c.label}» ma «${c.label}» e disegnato ${seen} volte sulla stessa schermata — piu di quanti il contatore ne dichiari`);
    }
  }
  await page.close();
}
await browser.close();
if (server) server.close();

/* NON-VACUITA · diciotto schermate, o non ha guardato niente. */
const EXPECTED = NAV.it.length + NAV.en.length;
if (measured < EXPECTED) bad.push(`solo ${measured} schermate su ${EXPECTED} sono state lette`);

const G = '\x1b[32m', R = '\x1b[31m', X = '\x1b[0m';
console.log(`\n  SINTONIA ITALIA · ARITMETICA DELLO SCHERMO   (${measured} schermate)`);
console.log('  ' + '-'.repeat(96));
if (bad.length) bad.slice(0, 14).forEach((x) => console.log(`  ${R}FAIL${X} ${x}`));
else console.log(`  ${G}PASS · nessun contatore e contraddetto da cio che si conta accanto a lui${X}`);
console.log('  ' + '-'.repeat(96) + '\n');
process.exit(bad.length === 0 ? 0 : 1);
