/* SINTONIA ITALIA · LA PAGINA NON PUO ESSERE PIU LARGA DELLO SCHERMO
   ---------------------------------------------------------------------------
   node audit/responsive.mjs [--base http://host]

   Il guscio del portale e una riga flex con una barra laterale di 228px fissi
   e una barra superiore che non va a capo, e in tutto il file non esisteva una
   sola @media. A 390px la larghezza minima del contenuto restava sopra i
   960px: si vedeva la barra laterale e una fetta di pagina, e il resto stava
   571px piu a destra — su ogni schermata, in entrambe le lingue. Sulla
   schermata Fonti il testo arrivava a sovrapporsi.

       IL DESIGN NON CAMBIA. CAMBIA CHE SI PUO LEGGERE.

   Il controllo misura una cosa sola e la misura in due larghezze: nessuna
   schermata puo costringere la pagina a scorrere in orizzontale. A 1440px
   deve continuare a essere vero — se una regola pensata per il telefono
   toccasse il desktop, si vedrebbe qui.
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
const PORT = Number(arg('port', 8997));

const NAV = {
  it: ['Radar delle Opportunità', 'Radar Futuro', 'Finestre Colturali', 'Polso di Mercato',
    'Portafoglio', 'Voci dal Campo', 'Concorrenza', 'Intelligence Scientifica', 'Archivio', 'Fonti'],
  en: ['Opportunity Radar', 'Future Radar', 'Crop Windows', 'Market Pulse',
    'Portfolio', 'Field Voices', 'Competitor Watch', 'Scientific Intelligence', 'Archive', 'Sources'],
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

const bad = [];
let measured = 0;
for (const vp of [{ w: 1440, h: 1200, n: 'desktop' }, { w: 390, h: 844, n: 'mobile' }]) {
  for (const lang of ['it', 'en']) {
    const page = await browser.newPage({ viewport: { width: vp.w, height: vp.h }, hasTouch: vp.w < 500, isMobile: vp.w < 500 });
    await page.goto(`${ORIGIN}/portale.html`, { waitUntil: 'networkidle', timeout: 120000 });
    await page.waitForTimeout(1100);
    if (lang === 'en') {
      await page.evaluate(() => { const e = [...document.querySelectorAll('span,div')].find((x) => x.textContent.trim() === 'EN');
        let n = e; for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer') { n.click(); return; } n = n.parentElement; } });
      await page.waitForTimeout(800);
    }
    for (const label of NAV[lang]) {
      const went = await page.evaluate((t) => { const h = document.querySelector(`[title="${t}"]`); if (!h) return false;
        let n = h; for (let i = 0; i < 4 && n; i++) { if (getComputedStyle(n).cursor === 'pointer') { n.click(); return true; } n = n.parentElement; } h.click(); return true; }, label);
      if (!went) { bad.push(`${vp.n}·${lang}·${label}: could not be reached`); continue; }
      await page.waitForTimeout(500);
      measured++;
      const over = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      if (over > 0) bad.push(`${vp.n}·${lang}·${label}: ${over}px of horizontal overflow`);
    }
    await page.close();
  }
}
await browser.close();
if (server) server.close();

/* NON-VACUITA · quaranta schermate, o non ha misurato niente. */
const EXPECTED = 2 * 2 * NAV.it.length;
if (measured < EXPECTED) bad.push(`only ${measured} of ${EXPECTED} screens were measured`);

const G = '\x1b[32m', R = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log(`\n  SINTONIA ITALY · RESPONSIVE   (${measured} screens at 1440 and 390)`);
console.log('  ' + '-'.repeat(90));
if (bad.length) { bad.slice(0, 12).forEach((x) => console.log(`  ${R}FAIL${X} ${x}`)); }
else console.log(`  ${G}PASS · no screen forces the page to scroll sideways, at either width${X}`);
console.log('  ' + '-'.repeat(90) + '\n');
process.exit(bad.length === 0 ? 0 : 1);
