/* SINTONIA ITALIA · DOVE FINISCONO LE ATTIVITA DEI CONCORRENTI
   ---------------------------------------------------------------------------
   node audit/competitor-population.mjs [--base http://host]

   Il pacchetto canonico porta 577 record. La schermata ne mostrava 561, e
   sedici sparivano senza che nessuna riga lo dicesse — otto dei quali
   CLIENT_SAFE con QA approvato. Non erano duplicati: erano una SECONDA FORMA
   della stessa famiglia. 561 sono ANNUNCI osservati; 16 sono NOTE DI
   OSSERVAZIONE, che non hanno inserzionista ne piattaforma e portano invece
   una coppia gia tradotta di «cosa prova» e «cosa non prova». La lista dei
   campi ammessi conosceva solo la prima forma, e il validatore chiedeva a
   tutti un inserzionista.

   I due numeri sono entrambi veri e non sono lo stesso numero:

       577  il CORPUS       — tutto cio che il pacchetto porta
       569  il PUBBLICABILE — cio che puo sostenere un'affermazione
         8  QA_UNREVIEWED   — vive nel corpus, non chiude una risposta

   Questo controllo pretende che il PUBBLICABILE arrivi intero fino al DOM, e
   che gli otto trattenuti non ci arrivino. Se non riesce a leggere il DOM,
   fallisce: un controllo che non ha guardato non ha assolto.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadData, mount } from './lib/harness.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const PKG = path.resolve(HERE, '..', '..', 'build', 'ITALY-REALITY-HANDOFF-V2.1',
  'DESIGN-INGEST', 'COMPETITOR-ACTIVITIES.json');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = arg('base', null);
const PORT = Number(arg('port', 8981));

const set = (a) => new Set(a);
const diff = (a, b) => [...a].filter((x) => !b.has(x));
const failures = [];

/* ── A · il pacchetto canonico ─────────────────────────────────────────── */
const pkg = JSON.parse(fs.readFileSync(PKG, 'utf8'));
const A_all = pkg.RECORDS.map((r) => r.ID);
const A_pub = pkg.RECORDS.filter((r) => r.CLIENT_SAFE === true).map((r) => r.ID);
const A_held = pkg.RECORDS.filter((r) => r.CLIENT_SAFE !== true).map((r) => r.ID);

/* ── B · il payload spedito ────────────────────────────────────────────── */
const D = loadData();
const B_all = (D.ITALY_HANDOFF_V21.competitorActivities || []).map((r) => r.ID);

/* ── C · il modello ────────────────────────────────────────────────────── */
const recs = D.ITALY_APP_MODEL.collections.competitorActivities.records;
const C_all = recs.map((r) => r.id);
const C_pub = recs.filter((r) => r.publishable).map((r) => r.id);

/* ── D · la proiezione di schermo ──────────────────────────────────────── */
const m = mount();
const dScreen = {};
for (const lang of ['it', 'en']) {
  const r = m.tryVals({ view: 'competitors', lang, compShown: 2000 });
  if (!r.ok) { failures.push(`D · ${lang}: the screen did not render — ${r.error}`); continue; }
  const cards = [].concat.apply([], (r.vals.feedGroups || []).map((g) => g.items || []));
  dScreen[lang] = cards.map((c) => c.id).filter(Boolean);
}

/* ── E · il DOM ────────────────────────────────────────────────────────── */
const eDom = {};
{
  const { chromium } = await import('playwright-core');
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
  const page = await browser.newPage({ viewport: { width: 1440, height: 1400 } });
  for (const lang of ['it', 'en']) {
    await page.goto(`${ORIGIN}/portale.html`, { waitUntil: 'networkidle', timeout: 120000 });
    await page.waitForTimeout(1100);
    if (lang === 'en') {
      await page.evaluate(() => { const e = [...document.querySelectorAll('span,div')].find((x) => x.textContent.trim() === 'EN');
        let n = e; for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer') { n.click(); return; } n = n.parentElement; } });
      await page.waitForTimeout(800);
    }
    const navLabel = lang === 'it' ? 'Concorrenza' : 'Competitor Watch';
    const went = await page.evaluate((t) => { const h = document.querySelector(`[title="${t}"]`); if (!h) return false;
      let n = h; for (let i = 0; i < 4 && n; i++) { if (getComputedStyle(n).cursor === 'pointer') { n.click(); return true; } n = n.parentElement; } h.click(); return true; }, navLabel);
    if (!went) { failures.push(`E · ${lang}: the Competitor screen could not be reached`); continue; }
    await page.waitForTimeout(900);
    /* esaurire la paginazione: se il controllo non c'e mentre restano record,
       e un fallimento, non un salto. */
    for (let i = 0; i < 80; i++) {
      const before = await page.evaluate(() => document.querySelectorAll('[data-act]').length);
      const clicked = await page.evaluate(() => {
        const c = [...document.querySelectorAll('span,div')].filter((e) => /LOAD MORE|MOSTRA ALTR|VEDI ALTR/i.test((e.textContent || '').trim()) && (e.textContent || '').length < 60);
        const hit = c.reverse().find((e) => getComputedStyle(e).cursor === 'pointer');
        if (!hit) return false; hit.click(); return true;
      });
      if (!clicked) break;
      await page.waitForTimeout(180);
      const after = await page.evaluate(() => document.querySelectorAll('[data-act]').length);
      if (after <= before) break;
    }
    eDom[lang] = await page.evaluate(() => [...document.querySelectorAll('[data-act]')].map((e) => e.getAttribute('data-act')));
  }
  await browser.close();
  if (server) server.close();
}

/* ── i confronti ───────────────────────────────────────────────────────── */
const Apub = set(A_pub), Aheld = set(A_held);
if (diff(Apub, set(C_pub)).length) failures.push(`C: ${diff(Apub, set(C_pub)).length} publishable ids never reach the model — ${diff(Apub, set(C_pub)).slice(0, 6).join(' ')}`);
if (diff(set(C_pub), Apub).length) failures.push(`C: the model publishes ${diff(set(C_pub), Apub).length} ids the package does not mark publishable`);
if (A_all.length !== B_all.length) failures.push(`B: the payload carries ${B_all.length} of ${A_all.length} canonical records`);

for (const lang of ['it', 'en']) {
  const d = set(dScreen[lang] || []);
  const e = set(eDom[lang] || []);
  if (!d.size) { failures.push(`D · ${lang}: the screen projected no card at all`); continue; }
  if (!e.size) { failures.push(`E · ${lang}: the DOM exposed no [data-act] node — nothing was measured`); continue; }
  const missing = diff(Apub, e);
  if (missing.length) failures.push(`E · ${lang}: ${missing.length} publishable ids never reach the DOM — ${missing.slice(0, 5).join(' ')}`);
  const leaked = [...e].filter((id) => Aheld.has(id));
  if (leaked.length) failures.push(`E · ${lang}: ${leaked.length} withheld ids DID reach the DOM — ${leaked.slice(0, 5).join(' ')}`);
  const alien = [...e].filter((id) => !Apub.has(id) && !Aheld.has(id));
  if (alien.length) failures.push(`E · ${lang}: ${alien.length} ids on screen exist in no canonical record`);
}

const G = '\x1b[32m', R = '\x1b[31m', Dm = '\x1b[2m', X = '\x1b[0m';
console.log('\n  SINTONIA ITALY · COMPETITOR POPULATION');
console.log('  ' + '-'.repeat(96));
console.log(`  ${'boundary'.padEnd(30)} ${'corpus'.padStart(8)} ${'publishable'.padStart(12)}`);
console.log('  ' + '-'.repeat(96));
console.log(`  ${'A  canonical package'.padEnd(30)} ${String(A_all.length).padStart(8)} ${String(A_pub.length).padStart(12)}   ${Dm}${A_held.length} withheld, QA_UNREVIEWED${X}`);
console.log(`  ${'B  shipped payload'.padEnd(30)} ${String(B_all.length).padStart(8)} ${String('—').padStart(12)}`);
console.log(`  ${'C  ITALY_APP_MODEL'.padEnd(30)} ${String(C_all.length).padStart(8)} ${String(C_pub.length).padStart(12)}`);
for (const lang of ['it', 'en']) {
  console.log(`  ${('D  screen projection (' + lang + ')').padEnd(30)} ${String('—').padStart(8)} ${String((dScreen[lang] || []).length).padStart(12)}`);
  console.log(`  ${('E  DOM (' + lang + ')').padEnd(30)} ${String('—').padStart(8)} ${String((eDom[lang] || []).length).padStart(12)}`);
}
console.log('  ' + '-'.repeat(96));
if (failures.length) { failures.forEach((f) => console.log(`  ${R}FAIL${X} ${f}`)); console.log(''); process.exit(1); }
console.log(`  ${G}PASS · every publishable competitor record reaches the DOM, and the ${A_held.length} withheld do not${X}`);
console.log(`  ${Dm}the denominator is stated, not chosen: ${A_all.length} in the corpus, ${A_pub.length} publishable${X}\n`);
process.exit(0);
