/* SINTONIA ITALIA · DOVE FINISCONO LE OPPORTUNITA
   ---------------------------------------------------------------------------
   node audit/opportunity-trace.mjs [--json] [--no-browser] [--port N]

   Misura la STESSA popolazione a cinque frontiere e confronta gli ID, non i
   totali. Due insiemi possono avere la stessa cardinalita e non contenere gli
   stessi casi: per questo un conteggio uguale non e una prova.

       DUE INSIEMI DELLA STESSA DIMENSIONE NON SONO LO STESSO INSIEME.

     A · pacchetto canonico   build/…/DESIGN-INGEST/OPPORTUNITIES.json
     B · handoff imbarcato    client/italy-handoff-v21.js
     C · ITALY_APP_MODEL      collections.opportunities
     D · proiezione a schermo cio che la schermata Opportunity riceve
     E · DOM                  cio che il browser ha davvero disegnato

   PERCHE ESISTE
   -------------
   Le prime quattro frontiere portavano gia gli stessi trentasette ID. Il caso
   si perdeva alla quinta, e per una ragione che nessun conteggio poteva
   mostrare: l'ORDINE. Le nove convergenze verificate finivano ai posti 2, 5,
   15, 17, 18, 19, 23, 29 e 35 di una lista che ne mostra dodici. Chi apriva il
   portale ne vedeva due.

       PUBBLICATO E DIETRO UN PULSANTE NON E PUBBLICATO.

   COSA FA FALLIRE QUESTO CONTROLLO
   --------------------------------
   Non solo la divergenza fra insiemi. Anche ognuno dei modi in cui un test del
   genere finge di aver guardato:
     · zero casi disegnati mentre il canonico ne autorizza
     · il controllo di paginazione non trovato — e il test che tira dritto
     · solo le prime schede esaminate invece di tutte
     · un dettaglio che non si apre
     · un ID a schermo che il canonico non contiene
   --------------------------------------------------------------------------- */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadData, mount } from './lib/harness.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const PKG = path.resolve(HERE, '..', '..', 'build', 'ITALY-REALITY-HANDOFF-V2.1',
  'DESIGN-INGEST', 'OPPORTUNITIES.json');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const PORT = Number(arg('port', 8931));
/* Con --base la tappa E interroga un URL GIA PUBBLICATO invece della
   cartella locale: e l'unico modo di provare che il DEPLOY — non il
   disco — mostra gli stessi casi. Senza --base resta il server locale. */
const BASE = arg('base', null);
const WITH_BROWSER = !argv.includes('--no-browser');

const set = (a) => new Set(a);
const sorted = (s) => [...s].sort();
const minus = (a, b) => sorted([...a].filter((x) => !b.has(x)));

/* ── A · il pacchetto canonico ─────────────────────────────────────────── */
const pkg = JSON.parse(fs.readFileSync(PKG, 'utf8'));
const A_all = pkg.RECORDS.map((r) => r.ID);
const A_pub = pkg.RECORDS.filter((r) => r.RENDERABLE_WITH_METHOD === true).map((r) => r.ID);

/* ── B · cio che l'ingest ha imbarcato ─────────────────────────────────── */
const ctx = loadData();
const B_rows = (ctx.ITALY_HANDOFF_V21 || {}).opportunities || [];
const B_all = B_rows.map((r) => r.ID);
const B_pub = B_rows.filter((r) => r.RENDERABLE_WITH_METHOD === true).map((r) => r.ID);

/* ── C · il modello ────────────────────────────────────────────────────── */
const AM = ctx.ITALY_APP_MODEL;
const C_coll = AM.collections.opportunities;
const C_all = C_coll.records.map((r) => r.id);
const C_pub = C_coll.records.filter((r) => r.convergence === 'VERIFIED_CONVERGENCE').map((r) => r.id);

/* ── D · la proiezione che la schermata riceve ─────────────────────────── */
const D = {};
for (const lang of ['it', 'en']) {
  const first = mount().vals({ view: 'radar', lang });
  const all = mount().vals({ view: 'radar', lang, showAll: true });
  D[lang] = {
    firstPage: (first.visibleCases || []).map((c) => c.id),
    filteredCount: first.filteredCount,
    all: (all.visibleCases || []).map((c) => c.id),
    pub: (all.visibleCases || []).filter((c) => c.convergence === 'VERIFIED_CONVERGENCE').map((c) => c.id),
    summary: first.convSummary,
  };
}

/* ── E · il DOM ────────────────────────────────────────────────────────── */
const E = {};
const failures = [];
if (WITH_BROWSER) {
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
  const jsErrors = [];
  page.on('pageerror', (e) => jsErrors.push(e.message));

  const ids = () => page.evaluate(() => [...document.querySelectorAll('[data-case]')]
    .map((e) => ({ id: e.getAttribute('data-case'), conv: e.getAttribute('data-convergence') })));

  for (const lang of ['it', 'en']) {
    await page.goto(`${ORIGIN}/portale.html`, { waitUntil: 'networkidle', timeout: 120000 });
    await page.waitForTimeout(900);
    if (lang === 'en') {
      await page.evaluate(() => {
        const e = [...document.querySelectorAll('span,div')].find((x) => x.textContent.trim() === 'EN');
        let n = e; for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer') { n.click(); return; } n = n.parentElement; }
      });
      await page.waitForTimeout(800);
    }
    const firstPage = await ids();
    /* Il DOM deve poter dire QUALI casi mostra. Senza `data-case` questo
       controllo conterebbe rettangoli. */
    if (!firstPage.length) failures.push(`${lang} · E: the DOM exposes no case identity — 0 [data-case] nodes`);

    /* Il controllo di paginazione DEVE esistere finche ci sono piu casi della
       prima pagina. Non trovarlo non e «salta»: e un fallimento. */
    const expanded = await page.evaluate(() => {
      const c = [...document.querySelectorAll('span,div')]
        .filter((e) => /VEDI TUTTE|VIEW ALL/i.test((e.textContent || '').trim()) && (e.textContent || '').length < 60);
      const hit = c.reverse().find((e) => getComputedStyle(e).cursor === 'pointer');
      if (!hit) return false;
      hit.click(); return true;
    });
    await page.waitForTimeout(900);
    if (!expanded && A_all.length > firstPage.length) {
      failures.push(`${lang} · E: the pagination control was not found, yet ${A_all.length} cases exist and only ${firstPage.length} are drawn`);
    }
    const allPage = await ids();
    if (allPage.length <= firstPage.length && A_all.length > firstPage.length) {
      failures.push(`${lang} · E: expanding changed nothing (${firstPage.length} -> ${allPage.length})`);
    }

    /* Ogni caso pubblicabile deve APRIRSI. Un dettaglio che non si apre e un
       caso che non esiste, per chi legge. */
    const detailFailures = [];
    for (const id of A_pub) {
      const opened = await page.evaluate((cid) => {
        const el = document.querySelector(`[data-case="${cid}"]`);
        if (!el) return 'absent';
        el.click(); return 'clicked';
      }, id);
      if (opened === 'absent') { detailFailures.push(`${id}: not on screen`); continue; }
      await page.waitForTimeout(420);
      const title = await page.evaluate(() => {
        let best = '', size = 0;
        for (const e of document.querySelectorAll('div,span,h1,h2')) {
          const t = (e.textContent || '').trim();
          if (!t || t.length > 90 || e.children.length > 1) continue;
          if ((t.match(/\p{L}/gu) || []).length < 3) continue;
          const px = parseFloat(getComputedStyle(e).fontSize) || 0;
          if (px > size) { size = px; best = t; }
        }
        return best;
      });
      if (!title) detailFailures.push(`${id}: detail opened with no title`);
      /* torna indietro e riapre la lista intera */
      await page.evaluate((back) => {
        const el = document.querySelector(`[title="${back}"]`);
        if (!el) return;
        let n = el; for (let i = 0; i < 4 && n; i++) { if (getComputedStyle(n).cursor === 'pointer') { n.click(); return; } n = n.parentElement; }
      }, lang === 'it' ? 'Indietro' : 'Back');
      await page.waitForTimeout(360);
      await page.evaluate(() => {
        const c = [...document.querySelectorAll('span,div')]
          .filter((e) => /VEDI TUTTE|VIEW ALL/i.test((e.textContent || '').trim()) && (e.textContent || '').length < 60);
        const hit = c.reverse().find((e) => getComputedStyle(e).cursor === 'pointer');
        if (hit) hit.click();
      });
      await page.waitForTimeout(380);
    }
    for (const f of detailFailures) failures.push(`${lang} · E detail: ${f}`);

    E[lang] = {
      firstPage: firstPage.map((x) => x.id),
      firstPagePub: firstPage.filter((x) => x.conv === 'VERIFIED_CONVERGENCE').map((x) => x.id),
      all: allPage.map((x) => x.id),
      pub: allPage.filter((x) => x.conv === 'VERIFIED_CONVERGENCE').map((x) => x.id),
    };
    if (jsErrors.length) failures.push(`${lang} · E: ${jsErrors.length} fatal JS error(s): ${jsErrors[0]}`);
  }
  await browser.close();
  if (server) server.close();
}

/* ── il verdetto ───────────────────────────────────────────────────────── */
const cmp = (from, to, a, b, what) => {
  const lost = minus(a, b), gained = minus(b, a);
  if (lost.length) failures.push(`${from}→${to} LOSES ${lost.length} ${what}: ${lost.join(', ')}`);
  if (gained.length) failures.push(`${from}→${to} INVENTS ${gained.length} ${what}: ${gained.join(', ')}`);
};
cmp('A', 'B', set(A_all), set(B_all), 'opportunities');
cmp('B', 'C', set(B_all), set(C_all), 'opportunities');
cmp('C', 'D', set(C_all), set(D.it.all), 'opportunities');
cmp('A', 'B', set(A_pub), set(B_pub), 'publishable');
cmp('B', 'C', set(A_pub), set(C_pub), 'publishable');
cmp('C', 'D', set(C_pub), set(D.it.pub), 'publishable');
if (WITH_BROWSER) {
  for (const lang of ['it', 'en']) {
    cmp('D', `E(${lang})`, set(D[lang].all), set(E[lang].all), 'opportunities');
    cmp('A', `E(${lang})`, set(A_pub), set(E[lang].pub), 'publishable');
    /* IL PUNTO DI TUTTA QUESTA MISSIONE: pubblicabile significa VISIBILE
       APRENDO, non raggiungibile dopo un clic su «vedi tutte». */
    const buried = minus(set(A_pub), set(E[lang].firstPagePub));
    if (buried.length) {
      failures.push(`${lang} · ${buried.length} of ${A_pub.length} publishable cases are NOT on the first screen: ${buried.join(', ')}`);
    }
    /* niente che il canonico non contenga */
    const alien = minus(set(E[lang].all), set(A_all));
    if (alien.length) failures.push(`${lang} · E shows ${alien.length} case(s) absent from the canonical package: ${alien.join(', ')}`);
    if (A_pub.length && !E[lang].pub.length) failures.push(`${lang} · E draws 0 publishable cases while the canonical package authorises ${A_pub.length}`);
  }
}

const G = '\x1b[32m', RD = '\x1b[31m', D_ = '\x1b[2m', X = '\x1b[0m';
const row = (id, label, recv, pub, note) =>
  console.log(`  ${id.padEnd(6)} ${label.padEnd(32)} ${String(recv).padStart(8)} ${String(pub).padStart(11)}   ${D_}${note || ''}${X}`);

if (argv.includes('--json')) {
  console.log(JSON.stringify({ buildId: pkg.BUILD_ID, A_all, A_pub, B_all, B_pub, C_all, C_pub, D, E, failures }, null, 1));
} else {
  console.log('');
  console.log(`  SINTONIA ITALY · OPPORTUNITY POPULATION TRACE   (${pkg.BUILD_ID})`);
  console.log('  ' + '─'.repeat(98));
  console.log(`  ${''.padEnd(6)} ${'boundary'.padEnd(32)} ${'received'.padStart(8)} ${'publishable'.padStart(11)}`);
  console.log('  ' + '─'.repeat(98));
  row('A', 'canonical package', A_all.length, A_pub.length, `${A_all.length - A_pub.length} candidates`);
  row('B', 'shipped handoff', B_all.length, B_pub.length, '');
  row('C', 'ITALY_APP_MODEL', C_all.length, C_pub.length, `source: ${C_coll.source}`);
  for (const lang of ['it', 'en']) {
    row('D', `screen projection (${lang})`, D[lang].all.length, D[lang].pub.length,
      `first page ${D[lang].firstPage.length} of ${D[lang].filteredCount}`);
  }
  if (WITH_BROWSER) {
    for (const lang of ['it', 'en']) {
      row('E', `DOM (${lang})`, E[lang].all.length, E[lang].pub.length,
        `first screen draws ${E[lang].firstPagePub.length} of ${A_pub.length} publishable`);
    }
  }
  console.log('  ' + '─'.repeat(98));
  if (!failures.length) {
    console.log(`  ${G}PASS · the same ids reach every boundary, and every publishable case is on the first screen${X}`);
  } else {
    for (const f of failures) console.log(`  ${RD}FAIL${X} ${f}`);
  }
  console.log('');
  console.log(`  publishable (${A_pub.length}): ${sorted(set(A_pub)).join(' ')}`);
  if (WITH_BROWSER) console.log(`  drawn first  : ${sorted(set(E.it.firstPagePub)).join(' ')}`);
  console.log('');
}
process.exit(failures.length === 0 ? 0 : 1);
