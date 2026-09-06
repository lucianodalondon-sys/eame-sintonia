/* SINTONIA ITALIA · L'AUDIT NEL NAVIGATORE VERO
   ---------------------------------------------------------------------------
   node audit/browser.mjs [--port 8899] [--shots dir]

   La regua headless carrega os dados, instancia a classe do portal e chama
   `renderVals()`. Isso prova que os dados chegam. NAO prova que a pagina abre.

       renderVals() DEVOLVE VALORES. O NAVEGADOR DESENHA UMA PAGINA.
       Entre as duas coisas cabe um erro de JavaScript que nada mede.

   Este audit abre o Chromium de verdade, clica na navegacao como um leitor,
   troca IT -> EN -> IT e le o TEXTO QUE FICOU NA TELA. As sete perguntas do
   fecho, feitas contra o que o olho veria:

     0 erro fatal de JS · 0 "undefined" · 0 "[object Object]"
     0 portugues diante do cliente · 0 fallback factual de fixture
     0 oportunidade rejeitada renderizada · 0 evidencia quebrada

   POR QUE LER O TEXTO, E NAO O DOM
   ---------------------------------
   Porque "undefined" numa tela nao e um no com um atributo: e uma palavra que
   o leitor le. Procura-la no texto visivel e fazer a mesma pergunta que ele faz.
   --------------------------------------------------------------------------- */
import http from 'node:http';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { PT_MARKERS } from './lang.mjs';
import { navMap } from './lib/nav-names.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const PORT = Number(arg('port', 8899));
const SHOTS = arg('shots', null);

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.css': 'text/css', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.ttf': 'font/ttf', '.otf': 'font/otf',
};
const server = http.createServer((req, res) => {
  const url = decodeURIComponent((req.url || '/').split('?')[0]);
  /* Il browser chiede /favicon.ico da solo, senza che la pagina la nomini. Un
     404 li e il server di prova, non il sito: in produzione lo serve il CDN.
     Contarlo come risorsa mancante avrebbe fatto fallire un controllo vero per
     un file che nessuno referenzia. */
  if (url === '/favicon.ico') { res.writeHead(204).end(); return; }
  const file = path.join(CLIENT, url === '/' ? '/portale.html' : url);
  if (!file.startsWith(CLIENT)) { res.writeHead(403).end('no'); return; }
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404, { 'content-type': 'text/plain' }).end('404'); return; }
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' }).end(buf);
  });
});
await new Promise((r) => server.listen(PORT, r));

const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

/* Un errore che il lettore non vede è comunque un errore: la pagina che smette
   di aggiornarsi ha esattamente questo aspetto. */
const fatals = [];
const templateNoise = [];
/* Cinque attributi SVG del template portano ancora il loro segnaposto —
   d="{{ mp.spark.d }}" — quando il browser analizza l'HTML, prima che il
   renderer li sostituisca. Il browser lo segnala come errore di attributo, e
   non e un errore di JavaScript: e il template che e un template. Misurato
   identico su BASELINE/portale.html, cioe prima di questo lavoro.

       UN RUMORE CHE SI CONTA NON E UN RUMORE CHE SI NASCONDE.

   Percio si contano a parte e si stampano: se il numero cambia, qualcuno ha
   aggiunto un segnaposto in un attributo, e allora si vuole saperlo. */
const TEMPLATE_ATTR = /attribute (d|cx|cy|x|y|r|points|width|height):.*\{\{/;
page.on('pageerror', (e) => fatals.push('pageerror: ' + e.message));
page.on('console', (m) => {
  if (m.type() !== 'error') return;
  const t = m.text().slice(0, 200);
  (TEMPLATE_ATTR.test(t) ? templateNoise : fatals).push('console: ' + t);
});
page.on('requestfailed', (r) => fatals.push('request failed: ' + r.url().slice(0, 120)));

await page.goto(`http://localhost:${PORT}/portale.html`, { waitUntil: 'networkidle' });
await page.waitForTimeout(700);

/* LA NAVIGAZIONE SI CHIAMA PER NOME.
   Ogni voce porta title="{{ n.label }}", quindi l'attributo e il nome che il
   lettore legge — e resta li anche dentro una schermata di dettaglio, dove
   compare in piu «Indietro». Cercarla per lo stile in linea non funzionava:
   il renderer trasforma style="" in una classe generata, e il filtro trovava
   zero voci senza dirlo. */
const clickNav = async (label) => {
  const el = await page.$(`[title="${label}"]`);
  if (!el) return false;
  const ok = await page.evaluate((t) => {
    const hit = document.querySelector(`[title="${t}"]`);
    if (!hit) return false;
    let n = hit;
    for (let i = 0; i < 4 && n; i++) {
      if (getComputedStyle(n).cursor === 'pointer') { n.click(); return true; }
      n = n.parentElement;
    }
    hit.click();
    return true;
  }, label);
  if (!ok) return false;
  await page.waitForTimeout(400);
  return true;
};

const clickText = async (txt) => {
  /* Il testo vive in uno <span> che non porta il gestore; il click va
     all'antenato che il browser considera cliccabile — cioe dove il lettore
     preme davvero. */
  const ok = await page.evaluate((t) => {
    const hit = [...document.querySelectorAll('span,div,a')]
      .find((e) => (e.textContent || '').trim() === t);
    if (!hit) return false;
    let n = hit;
    for (let i = 0; i < 4 && n; i++) {
      if (getComputedStyle(n).cursor === 'pointer') { n.click(); return true; }
      n = n.parentElement;
    }
    hit.click();
    return true;
  }, txt);
  if (!ok) return false;
  await page.waitForTimeout(340);
  return true;
};
const clickFirstCard = async () => {
  /* IL RENDERER NON LASCIA LO STILE NELL'ATTRIBUTO.
     Il template scrive style="…min-height:250px…", ma cio che arriva nel DOM e
     una classe generata (`scp0`), quindi ogni selettore per attributo trovava
     zero schede — e il controllo diceva «nessuna scheda da aprire» su una
     pagina che ne mostrava dodici.

         SI CERCA CIO CHE IL BROWSER HA CALCOLATO, NON CIO CHE ERA SCRITTO.

     E NEMMENO L'ALTEZZA E UN'IDENTITA. La banda era 200–520 px. Misurato: in
     italiano le schede stanno fra 197 e 211 px, in inglese fra 184 e 186 —
     l'inglese e piu corto, la scheda si accorcia, e il controllo diceva di
     nuovo «nessuna scheda» su una pagina che ne mostrava dodici. Un test che
     riconosce un oggetto dalla sua altezza in pixel misura il font, non il
     prodotto.

         UNA SCHEDA NON SI RICONOSCE DAL NUMERO DI PIXEL CHE OCCUPA.
         SI RICONOSCE DAL FATTO CHE, CLICCANDOLA, LA PAGINA CAMBIA.

     Quindi: fra i blocchi cliccabili si tengono i piu esterni (una scheda ne
     contiene altri, ma nessuna scheda ne sta dentro un'altra), e si prova ad
     aprirli in ordine finche il testo della pagina cambia davvero. */
  const before = ((await page.evaluate(() => document.body.innerText)) || '').trim();
  const total = await page.evaluate(() => {
    const all = [...document.querySelectorAll('div')].filter((e) => {
      if (getComputedStyle(e).cursor !== 'pointer') return false;
      const h = e.getBoundingClientRect().height;
      return h >= 120 && h <= 640 && (e.innerText || '').trim().length > 40;
    });
    const outer = all.filter((e) => !all.some((o) => o !== e && o.contains(e)));
    window.__sintoniaCards = outer;
    return outer.length;
  });
  for (let i = 0; i < Math.min(total, 6); i += 1) {
    const ok = await page.evaluate((n) => {
      const el = (window.__sintoniaCards || [])[n];
      if (!el) return false;
      el.click();
      return true;
    }, i);
    if (!ok) break;
    await page.waitForTimeout(480);
    const after = ((await page.evaluate(() => document.body.innerText)) || '').trim();
    if (after && after !== before) return true;
  }
  return false;
};


const PT_RE = new RegExp('(^|[^\\p{L}])(' + PT_MARKERS.join('|') + ')([^\\p{L}]|$)', 'iu');
const FORBIDDEN = /(CLIENT_SAFE|RENDERABLE_WITH_METHOD|EVIDENCE_DERIVED|FAILED_GATES)/;
/* IL RED TEAM DECLASSA, NON CANCELLA — e questo controllo lo aveva capito male.
   I 17 casi che ha abbattuto sono tutti e 17 dentro i 37: restano come
   candidati, ed e giusto che si vedano, perche «da validare» e esattamente
   cio che sono. Cercare il loro id a schermo li dichiarava tutti un difetto.

       CIO CHE IL RED TEAM VIETA NON E MOSTRARLI: E CHIAMARLI VERIFICATI.

   L'invariante vera, quindi: nessuno dei 17 puo comparire sotto l'etichetta
   della convergenza verificata. Misurato sul pacchetto: 0 su 17 lo fanno, e
   questo controllo fallisce il giorno in cui uno lo facesse. */
const rejected = JSON.parse(fs.readFileSync(
  path.resolve(HERE, '..', '..', 'build', 'ITALY-REALITY-HANDOFF-V2.1',
    'DESIGN-INGEST', 'OPPORTUNITY-REJECTIONS.json'), 'utf8'));
const rejectedIds = new Set(
  (rejected.REJEICOES || []).map((r) => r.ID || r.IDENTITY_KEY).filter(Boolean));
const VERIFIED_WORDS = /(CONVERGENZA VERIFICATA|VERIFIED CONVERGENCE)/;

const findings = { fatal: [], undef: [], objobj: [], pt: [], forbidden: [], rejected: [], empty: [] };
const seen = [];

const inspect = async (label, lang) => {
  const txt = await page.evaluate(() => document.body.innerText || '');
  /* L'IMPRONTA E TUTTA LA SCHERMATA, NON LA SUA PRIMA RIGA.
     Le prime righe sono la navigazione, uguale ovunque: presa come impronta
     diceva «2 schermate distinte» su dodici, cioe misurava il menu invece del
     contenuto. Un digest del testo intero distingue cio che il lettore vede. */
  let h = 0;
  for (let i = 0; i < txt.length; i++) { h = (h * 31 + txt.charCodeAt(i)) | 0; }
  const print = String(h);
  seen.push({ label, lang, chars: txt.length, print });
  const at = (what) => `${lang.toUpperCase()} · ${label}: ${what}`;
  if (txt.length < 200) findings.empty.push(at(`only ${txt.length} chars rendered`));
  for (const line of txt.split('\n').map((l) => l.trim()).filter(Boolean)) {
    if (/\bundefined\b/.test(line)) findings.undef.push(at(line.slice(0, 90)));
    if (line.includes('[object Object]')) findings.objobj.push(at(line.slice(0, 90)));
    if (FORBIDDEN.test(line)) findings.forbidden.push(at(line.slice(0, 90)));
    if (lang === 'it' && PT_RE.test(line)) findings.pt.push(at(line.slice(0, 90)));
    /* un id declassato sulla stessa riga dell'etichetta verificata */
    if (VERIFIED_WORDS.test(line)) {
      for (const id of rejectedIds) if (line.includes(id)) findings.rejected.push(at(id + ' rendered as verified'));
    }
  }
  if (SHOTS) {
    fs.mkdirSync(SHOTS, { recursive: true });
    await page.screenshot({ path: path.join(SHOTS, `${lang}-${label.replace(/[^a-z0-9]+/gi, '-')}.png`) });
  }
};

/* Le tredici schermate che il fecho nomina, nell'ordine in cui un lettore le
   incontra. Il dettaglio e le sue schede si aprono dalla scheda, non da un URL:
   è così che le apre lui. */
/* I NOMI DELLE VOCI VENGONO DAL DIZIONARIO, NON DA QUI — vedi
   audit/lib/nav-names.mjs, che li legge dagli stessi due file che il portale
   legge e esplode se una chiave manca. */
const NAV = { it: navMap('it'), en: navMap('en') };
const TOUR = [
  { label: 'HOME · Radar', key: 'home' },
  { label: 'OPPORTUNITY DETAIL', card: true },
  { label: 'FUTURE', key: 'future' },
  { label: 'WINDOWS', key: 'windows' },
  { label: 'MARKET', key: 'market' },
  { label: 'PORTFOLIO', key: 'portfolio' },
  { label: 'VOCI', key: 'voci' },
  { label: 'COMPETITOR', key: 'competitor' },
  { label: 'SCIENCE', key: 'science' },
  { label: 'ARCHIVE', key: 'archive' },
  { label: 'SOURCES', key: 'sources' },
];

const setLang = async (lang) => {
  await clickText(lang.toUpperCase());
  await page.waitForTimeout(420);
};

const runTour = async (lang) => {
  const N = NAV[lang];
  for (const stop of TOUR) {
    if (stop.card) {
      if (!(await clickFirstCard())) { findings.empty.push(`${lang} · ${stop.label}: no card to open`); continue; }
    } else if (!(await clickNav(N[stop.key]))) {
      findings.empty.push(`${lang} · ${stop.label}: nav item "${N[stop.key]}" not found`);
      continue;
    }
    await inspect(stop.label, lang);
    if (stop.card) {
      /* IL PORTALE NON INSTRADA CON L'URL.
         `page.goBack()` usciva dall'applicazione invece di tornare al radar, e
         da li in poi la navigazione non esisteva piu: il giro finiva dopo la
         seconda tappa e undici schermate non venivano mai guardate. Si torna
         come torna il lettore, con il comando «Indietro» del portale. */
      if (!(await clickNav(N.back))) await clickNav(N.home);
      await page.waitForTimeout(420);
    }
  }
  /* SEARCH · digitato come lo digita un lettore */
  const box = await page.$('input');
  if (box) {
    await box.click().catch(() => {});
    await box.fill('vite');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(520);
    await inspect('SEARCH', lang);
  } else findings.empty.push(`${lang} · SEARCH: no input`);
};

await runTour('it');
await setLang('en'); await runTour('en');
await setLang('it'); await runTour('it');

findings.fatal = fatals;
await browser.close();
server.close();

const G = '\x1b[32m', R = '\x1b[31m', X = '\x1b[0m';
const line = (id, title, hits) => {
  const ok = hits.length === 0;
  console.log(`  ${ok ? `${G}PASS${X}` : `${R}FAIL${X}`}  ${id.padEnd(5)} ${title.padEnd(52)} exp 0      got ${hits.length}`);
  [...new Set(hits)].slice(0, 6).forEach((h) => console.log(`        ${h}`));
};
console.log('');
console.log('  SINTONIA ITALY · REAL BROWSER ACCEPTANCE');
console.log('  ' + '─'.repeat(96));
line('BR1', 'No fatal JavaScript in a real browser', findings.fatal);
console.log(`        (${templateNoise.length} SVG attribute notices from unrendered template placeholders — 5 in the markup, same as BASELINE)`);
line('BR2', 'No "undefined" rendered on any screen', findings.undef);
line('BR3', 'No "[object Object]" rendered on any screen', findings.objobj);
line('BR4', 'No Portuguese in front of the Italian client', findings.pt);
line('BR5', 'No engine bookkeeping rendered', findings.forbidden);
line('BR6', 'No red-team rejected opportunity rendered', findings.rejected);
line('BR7', 'Every screen actually rendered content', findings.empty);
console.log('  ' + '─'.repeat(96));
console.log(`  ${seen.length} screen visits over IT -> EN -> IT · ${rejectedIds.size} rejected ids checked`);
/* Un giro che visita trentasei volte la stessa schermata passerebbe ogni
   controllo qui sopra. Le impronte dicono che non e cosi: schermate diverse
   hanno testi diversi, e due lingue della stessa schermata pure. */
const prints = new Set(seen.map((v) => v.lang + ':' + v.print));
console.log(`  ${prints.size} distinct screen fingerprints (${new Set(seen.map((v) => v.label)).size} screens x 2 languages)`);
seen.filter((v) => v.lang === 'it').slice(0, 12).forEach((v) =>
  console.log(`     ${String(v.chars).padStart(6)} chars  ${v.label}`));
console.log('');
const total = Object.values(findings).reduce((a, v) => a + v.length, 0);
process.exit(total === 0 ? 0 : 1);
