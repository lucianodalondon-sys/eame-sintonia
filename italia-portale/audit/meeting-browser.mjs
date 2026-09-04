/* SINTONIA · IL PERCORSO DELLA RIUNIONE NEL BROWSER
   ===========================================================================
   `meeting-gate.mjs` prova che il motore arriva al modello della schermata.
   Questo prova che arriva all'OCCHIO: apre la superficie in un browser vero,
   a 1440 e a 390, in IT e in EN, e percorre i SEI CASI della demo.

       UNA SCHERMATA CHE NESSUNO HA APERTO NON E UNA SCHERMATA PROVATA.

   Per ogni caso confronta cio che si LEGGE nel DOM con cio che lo snapshot
   DICHIARA, passando per il dizionario: se il motore dice ACT_NOW, sullo
   schermo deve esserci «AGIRE ORA» in italiano e «ACT NOW» in inglese — non
   un gettone, non una parola diversa, non niente.

   Preme VEDI TUTTI davvero, perche due dei sei casi stanno oltre i primi
   dodici: e il gesto che fara chi presenta.
   =========================================================================== */
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const SNAP = JSON.parse(fs.readFileSync(path.join(CLIENT, 'meeting-intelligence-snapshot.json'), 'utf8'));

/* il dizionario, caricato come lo carica la pagina: il file si dichiara su
   `window`, quindi gli si da un `window` e si legge da li. */
const win = {};
globalThis.window = win;
new Function(fs.readFileSync(path.join(CLIENT, 'meeting-labels.js'), 'utf8'))();
const ML = win.MEETING_LABELS;
if (!ML) { console.error('meeting-labels.js non si e dichiarato'); process.exit(1); }

/* I sei casi che la riunione apre, con cio che ciascuno deve dimostrare. */
const DEMO = [
  ['A', 'OPP_5F31A63F844D', 'botrite · vite · Emilia-Romagna — ACT_NOW, finestra aperta'],
  ['B', 'OPP_F8106D5E1767', 'botrite · vite · Toscana — ACT_NOW sostenuto'],
  ['C', 'OPP_169BD86DB324', 'tignoletta · vite · Umbria — la fonte non chiede di agire'],
  ['D', 'OPP_75C37DED9160', 'carpocapsa · melo · Veneto — stadio concluso E azione viva'],
  ['E', 'OPP_75C37DED9160', 'lo stesso caso — RULE_DELEGATED_TO_FARM in parole'],
  ['F', 'OPP_D11664591168', 'scafoideo · vite · Toscana — obbligo amministrativo'],
];

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.png': 'image/png', '.svg': 'image/svg+xml', '.ttf': 'font/ttf', '.otf': 'font/otf' };
const PORT = 8931;
const srv = http.createServer((req, res) => {
  let rel = decodeURIComponent((req.url || '/').split('?')[0]);
  if (rel === '/') rel = '/portale.html';
  if (!path.extname(rel)) rel += '.html';
  const f = path.join(CLIENT, rel);
  fs.readFile(f, (e, b) => {
    if (e) { res.writeHead(404).end('404'); return; }
    res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' }).end(b);
  });
}).listen(PORT);

const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });

/* Un segnaposto di template dentro un attributo SVG e il template che fa il
   template, non un errore. Esiste identico in BASELINE/portale.html, e
   audit/browser.mjs applica la stessa regola. Si conta a parte, non si
   nasconde. */
const TEMPLATE_ATTR = /attribute (d|viewBox|points|transform|cx|cy|r|x|y|width|height):/;
let consoleErrors = 0, templateNoise = 0;
const problems = [];
const rows = [];

for (const [w, h, size] of [[1440, 900, 'desktop 1440'], [390, 844, 'mobile 390']]) {
  for (const lang of ['it', 'en']) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h } });
    const page = await ctx.newPage();
    page.on('console', (m) => {
      if (m.type() !== 'error') return;
      const t = m.text();
      if (TEMPLATE_ATTR.test(t)) { templateNoise++; return; }
      consoleErrors++; problems.push(`${size}/${lang} console: ${t.slice(0, 140)}`);
    });
    page.on('pageerror', (e) => { consoleErrors++; problems.push(`${size}/${lang} pageerror: ${String(e).slice(0, 140)}`); });

    await page.goto(`http://localhost:${PORT}/portale.html`, { waitUntil: 'networkidle' });
    await page.evaluate((l) => localStorage.setItem('sintonia_lang', l), lang);
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(700);

    const openAll = async () => page.evaluate(() => {
      const t = [...document.querySelectorAll('*')].filter((e) => e.children.length === 0 && /VEDI TUTTE|VEDI TUTTI|VIEW ALL/i.test(e.textContent || ''));
      if (!t.length) return false;
      let el = t[0]; for (let i = 0; i < 6 && el; i++) { if (el.onclick || el.getAttribute('onclick')) break; el = el.parentElement; }
      (el || t[0]).click(); return true;
    });
    await openAll();
    await page.waitForTimeout(500);

    const radar = await page.evaluate(() => ({
      cards: document.querySelectorAll('[data-case]').length,
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    }));
    if (radar.cards !== SNAP.TOTAL_CASES) problems.push(`${size}/${lang} radar: ${radar.cards} schede, lo snapshot ne dichiara ${SNAP.TOTAL_CASES}`);
    if (radar.overflow) problems.push(`${size}/${lang} radar: la pagina scorre in orizzontale (${radar.scrollW} > ${radar.clientW})`);

    for (const [tag, id, what] of DEMO) {
      const snap = SNAP.CASES.find((c) => c.ID === id);
      const opened = await page.evaluate((cid) => {
        const el = document.querySelector(`[data-case="${cid}"]`);
        if (!el) return false; el.click(); return true;
      }, id);
      await page.waitForTimeout(500);

      const seen = await page.evaluate(() => ({
        status: [...document.querySelectorAll('[data-status]')].map((e) => e.getAttribute('data-status')),
        areas: [...document.querySelectorAll('[data-area]')].map((e) => e.getAttribute('data-area')),
        products: [...document.querySelectorAll('[data-product]')].map((e) => e.getAttribute('data-product')),
        text: (document.body.innerText || '').replace(/\s+/g, ' '),
        overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      }));

      /* CIO CHE IL MOTORE DICE DEVE ESSERE CIO CHE SI LEGGE. */
      const want = {
        status: ML.label(lang, 'STATUS', snap.STATUS),
        publication: ML.label(lang, 'PUBLICATION_STATE', snap.PUBLICATION_STATE),
        windowRule: ML.label(lang, 'WINDOW_RULE_STATE', snap.WINDOW_RULE_STATE),
      };
      const miss = [];
      if (!opened) miss.push('la scheda non si apre');
      if (want.status && seen.status.indexOf(want.status) < 0) miss.push(`stato «${want.status}» non sullo schermo (letto: ${seen.status.join('/') || 'niente'})`);
      if (want.publication && seen.text.indexOf(want.publication) < 0) miss.push(`pubblicazione «${want.publication}» non sullo schermo`);
      if (want.windowRule && seen.text.indexOf(want.windowRule) < 0) miss.push(`regola della finestra «${want.windowRule}» non sullo schermo`);
      const wantDepts = Object.keys(snap.ACTION_BY_DEPARTMENT || {}).length;
      if (wantDepts && seen.areas.length < wantDepts) miss.push(`mappa delle azioni: ${seen.areas.length} riquadri, il motore ne dichiara ${wantDepts}`);
      if (seen.overflow) miss.push('la scheda scorre in orizzontale');
      /* Nessun gettone interno puo essere leggibile sulla pagina. */
      const tok = seen.text.match(/\b[A-Z][A-Z0-9]{2,}(?:_[A-Z0-9]+)+\b/);
      if (tok) miss.push(`gettone interno a schermo: «${tok[0]}»`);

      rows.push({ size, lang, tag, id, what, ok: miss.length === 0, miss, seenStatus: seen.status[0] || '', areas: seen.areas.length });
      if (miss.length) problems.push(`${size}/${lang} ${tag} ${id}: ` + miss.join(' · '));

      await page.evaluate(() => {
        const b = [...document.querySelectorAll('span,div,a,button')].filter((e) => /INDIETRO|BACK|^←/.test((e.textContent || '').trim()));
        const el0 = b[b.length - 1];
        if (!el0) return;
        let el = el0; for (let i = 0; i < 6 && el; i++) { if (el.onclick || el.getAttribute('onclick')) break; el = el.parentElement; }
        (el || el0).click();
      });
      await page.waitForTimeout(450);
      if (!(await page.evaluate(() => document.querySelectorAll('[data-case]').length > 0))) {
        await page.goto(`http://localhost:${PORT}/portale.html`, { waitUntil: 'networkidle' });
        await page.waitForTimeout(600);
      }
      await openAll();
      await page.waitForTimeout(350);
    }
    await ctx.close();
  }
}
await browser.close(); srv.close();

const C = { g: (t) => `\x1b[32m${t}\x1b[0m`, r: (t) => `\x1b[31m${t}\x1b[0m`, d: (t) => `\x1b[2m${t}\x1b[0m`, b: (t) => `\x1b[1m${t}\x1b[0m` };
console.log('');
console.log(C.b(`  IL PERCORSO DELLA RIUNIONE · ${SNAP.BUILD_ID} · ${SNAP.TOTAL_CASES} casi`));
let last = '';
for (const r of rows) {
  const head = `${r.size} · ${r.lang.toUpperCase()}`;
  if (head !== last) { console.log(''); console.log(C.b('  ' + head)); last = head; }
  console.log('  ' + (r.ok ? C.g('OK  ') : C.r('FAIL')) + ` ${r.tag}  ${r.id}  ${C.d(r.what)}`);
  if (!r.ok) r.miss.forEach((x) => console.log('        ' + C.r(x)));
}
console.log('');
console.log(`  errori reali di console/pagina : ${consoleErrors}`);
console.log(C.d(`  segnaposto SVG del template   : ${templateNoise} (presenti anche in BASELINE, non fatali)`));
console.log('');
console.log('  ' + (problems.length === 0 && consoleErrors === 0
  ? C.g(`${rows.length}/${rows.length} percorsi verdi · 1440 e 390 · IT e EN`)
  : C.r(`${problems.length} problemi`)));
console.log('');
process.exit(problems.length === 0 && consoleErrors === 0 ? 0 : 1);
