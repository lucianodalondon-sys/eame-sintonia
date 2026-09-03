/* SINTONIA ITALIA · IL GIRO DI PATRICIA
   ---------------------------------------------------------------------------
   node audit/browser-deep.mjs [--base http://host] [--shots dir]

   `browser.mjs` prova che ogni schermata si apre. Questo prova un'altra cosa:
   che una persona possa PRESENTARLE. Patricia apre il portale davanti a Max,
   clicca una scheda, e deve poter dire cosa sta guardando e perche esiste.

       UNA SCHERMATA CHE SI APRE NON E UNA SCHERMATA CHE SI PUO MOSTRARE.

   Percio il giro non conta gli errori: legge le schede una per una — tre
   convergenze verificate e tre da validare, di archetipi diversi — e chiede a
   ognuna se dice il proprio titolo, la coltura, il bersaglio, la geografia, la
   data del segnale, la finestra, l'archetipo, lo stato, quante prove la
   reggono e chi dovrebbe guardarla. Un campo assente NON e un errore: molti
   casi non hanno bersaglio agronomico, e dirlo e corretto. Un campo che mente,
   si.

   Le quattro cose che il navigatore aveva gia trovato una volta, e che nessun
   controllo headless vedeva, sono verificate per nome:

     1 · `issueKey` inglese («Scab», «Downy mildew») dentro l'interfaccia italiana
     2 · scheda senza titolo comprensibile
     3 · «IN ATTESA DI LOCALIZZAZIONE» su casi che un bersaglio non lo avranno mai
     4 · forza dell'evidenza a zero su un caso che ne cita sei
   --------------------------------------------------------------------------- */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { PT_MARKERS } from './lang.mjs';
import { loadData } from './lib/harness.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const SHOTS = arg('shots', null);
const BASE = arg('base', null);
const PORT = Number(arg('port', 8901));

let server = null;
let origin = BASE;
if (!BASE) {
  const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json', '.css': 'text/css', '.png': 'image/png', '.svg': 'image/svg+xml',
    '.ttf': 'font/ttf', '.otf': 'font/otf' };
  server = http.createServer((req, res) => {
    const url = decodeURIComponent((req.url || '/').split('?')[0]);
    if (url === '/favicon.ico') { res.writeHead(204).end(); return; }
    const file = path.join(CLIENT, url === '/' ? '/accesso.html' : url);
    if (!file.startsWith(CLIENT)) { res.writeHead(403).end('no'); return; }
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(404).end('404'); return; }
      res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' }).end(buf);
    });
  });
  await new Promise((r) => server.listen(PORT, r));
  origin = `http://localhost:${PORT}`;
}

const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

const fatals = [];
const templateNoise = [];
const TEMPLATE_ATTR = /attribute (d|cx|cy|x|y|r|points|width|height):.*\{\{/;
page.on('pageerror', (e) => fatals.push('pageerror: ' + e.message));
page.on('console', (m) => {
  if (m.type() !== 'error') return;
  const t = m.text().slice(0, 200);
  (TEMPLATE_ATTR.test(t) ? templateNoise : fatals).push(t);
});
page.on('requestfailed', (r) => fatals.push('request failed: ' + r.url().slice(0, 140)));

const PT_RE = new RegExp('(^|[^\\p{L}])(' + PT_MARKERS.join('|') + ')([^\\p{L}]|$)', 'iu');
const INTERNAL = /(CLIENT_SAFE|RENDERABLE_WITH_METHOD|EVIDENCE_DERIVED|FAILED_GATES|QA_PASS|QA_UNREVIEWED|EVIDENCE_DOCUMENTED|EVIDENCE_SOURCED|ORIGIN_LAYER|PROVENANCE_STATE)/;
/* Nome inglese canonico che NON deve comparire come etichetta in italiano.
   Un binomio latino (Echinochloa, Amaranthus) e corretto in entrambe le lingue
   e non entra in questa lista: e il nome scientifico, non una traduzione. */
const EN_ISSUE_LEAK = /\b(Scab|Downy mildew|Powdery mildew|Codling moth|European corn borer|Grape moth|Olive fruit fly|Brown marmorated stink bug|Rice blast|Fusarium head blight|Water stress|Weeds|Aphids|Rust)\b/;

/* UN TITOLO DI PAPER NON E UNA FUGA DI LINGUA.
   «Identification of QTLs for Resistance to Leaf Rust…» e il titolo pubblicato
   di uno studio: si cita come e stato pubblicato, e tradurlo sarebbe inventare
   una fonte che non esiste. Il primo giro lo ha segnalato come inglese in
   interfaccia italiana, il che avrebbe insegnato a ignorare il controllo.

       IL DETECTOR CHE ACCUSA UNA CITAZIONE CORRETTA
       ADDESTRA CHI LEGGE A NON CREDERGLI.

   L'esenzione non e euristica: sono i titoli che il modello contiene davvero,
   letti dal modello. Una parola inglese fuori da questo insieme resta un
   difetto. */
const CITAZIONI = (() => {
  const AM = loadData().ITALY_APP_MODEL;
  const out = new Set();
  const add = (v) => { const t = String(v || '').trim(); if (t.length > 12) out.add(t); };
  (AM.collections.scienceRecords.records || []).forEach((r) => add(r.title));
  (AM.collections.resistance.records || []).forEach((r) => { add(r.citation); add(r.species); });
  (AM.collections.publicVoices.records || []).forEach((r) => { add(r.title); add(r.textOriginal); });
  (AM.collections.news.records || []).forEach((r) => add(r.title));
  return [...out];
})();
const eCitazione = (line) => CITAZIONI.some((t) => line.includes(t) || t.includes(line));

const findings = {
  fatal: [], undef: [], objobj: [], pt: [], internal: [],
  enLeak: [], noTitle: [], falseAwaiting: [], zeroEvidence: [], empty: [],
};
const shots = [];
const snap = async (name) => {
  if (!SHOTS) return;
  fs.mkdirSync(SHOTS, { recursive: true });
  const f = path.join(SHOTS, name.replace(/[^a-z0-9]+/gi, '-') + '.png');
  await page.screenshot({ path: f });
  shots.push(f);
};

const text = () => page.evaluate(() => document.body.innerText || '');

const scan = async (label, lang) => {
  const txt = await text();
  const at = (w) => `${lang.toUpperCase()} · ${label}: ${w}`;
  if (txt.length < 200) findings.empty.push(at(`only ${txt.length} chars`));
  for (const line of txt.split('\n').map((l) => l.trim()).filter(Boolean)) {
    if (/\bundefined\b/.test(line)) findings.undef.push(at(line.slice(0, 100)));
    if (line.includes('[object Object]')) findings.objobj.push(at(line.slice(0, 100)));
    if (INTERNAL.test(line)) findings.internal.push(at(line.slice(0, 100)));
    if (lang === 'it' && PT_RE.test(line)) findings.pt.push(at(line.slice(0, 100)));
    if (lang === 'it' && EN_ISSUE_LEAK.test(line) && !eCitazione(line)) {
      findings.enLeak.push(at(line.slice(0, 100)));
    }
  }
  return txt;
};

const clickNav = async (label) => {
  const ok = await page.evaluate((t) => {
    const hit = document.querySelector(`[title="${t}"]`);
    if (!hit) return false;
    let n = hit;
    for (let i = 0; i < 4 && n; i++) {
      if (getComputedStyle(n).cursor === 'pointer') { n.click(); return true; }
      n = n.parentElement;
    }
    hit.click(); return true;
  }, label);
  if (ok) await page.waitForTimeout(420);
  return ok;
};
const clickText = async (t) => {
  const ok = await page.evaluate((s) => {
    const hit = [...document.querySelectorAll('span,div,a,button')]
      .find((e) => (e.textContent || '').trim() === s);
    if (!hit) return false;
    let n = hit;
    for (let i = 0; i < 5 && n; i++) {
      if (getComputedStyle(n).cursor === 'pointer') { n.click(); return true; }
      n = n.parentElement;
    }
    hit.click(); return true;
  }, t);
  if (ok) await page.waitForTimeout(400);
  return ok;
};

/* Le schede del radar, lette come le legge l'occhio: un blocco cliccabile alto
   quanto una scheda, con il proprio testo dentro. */
const cards = () => page.evaluate(() => [...document.querySelectorAll('div')]
  .filter((e) => {
    const cs = getComputedStyle(e);
    if (cs.cursor !== 'pointer') return false;
    const h = e.getBoundingClientRect().height;
    return h >= 200 && h <= 520 && (e.innerText || '').trim().length > 40;
  })
  .map((e, i) => ({ i, text: (e.innerText || '').trim() })));

const openCard = async (i) => {
  const ok = await page.evaluate((idx) => {
    const els = [...document.querySelectorAll('div')].filter((e) => {
      const cs = getComputedStyle(e);
      if (cs.cursor !== 'pointer') return false;
      const h = e.getBoundingClientRect().height;
      return h >= 200 && h <= 520 && (e.innerText || '').trim().length > 40;
    });
    if (!els[idx]) return false;
    els[idx].click(); return true;
  }, i);
  if (ok) await page.waitForTimeout(520);
  return ok;
};

const NAV = {
  it: { home: 'Radar delle Opportunità', future: 'Radar Futuro', windows: 'Finestre Colturali',
    market: 'Polso di Mercato', portfolio: 'Portafoglio', voci: 'Voci dal Campo',
    competitor: 'Concorrenza', science: 'Intelligence Scientifica', archive: 'Archivio',
    sources: 'Fonti', back: 'Indietro' },
  en: { home: 'Opportunity Radar', future: 'Future Radar', windows: 'Crop Windows',
    market: 'Market Pulse', portfolio: 'Portfolio', voci: 'Field Voices',
    competitor: 'Competitor Watch', science: 'Scientific Intelligence', archive: 'Archive',
    sources: 'Sources', back: 'Back' },
};
const VERIFIED = { it: 'CONVERGENZA VERIFICATA', en: 'VERIFIED CONVERGENCE' };
const TOVALID = { it: 'DA VALIDARE', en: 'TO VALIDATE' };
const AWAITING = { it: 'IN ATTESA DI LOCALIZZAZIONE', en: 'AWAITING LOCALIZATION' };

/* Che cosa una scheda di dettaglio deve poter dire di se. Assente non e
   sbagliato — molti casi non hanno bersaglio — ma si registra, perche una
   scheda che non dice NULLA di questo non e presentabile. */
const FIELD_PROBES = [
  ['archetype', /(PRESSIONE IN CAMPO|MOMENTO DI MERCATO|RESISTENZA|APERTURA COMPETITIVA|PREPARAZIONE NORMATIVA|DALLA SCIENZA AL CAMPO|FIELD PRESSURE|MARKET MOMENT|RESISTANCE|COMPETITIVE OPENING|REGULATORY PREPARATION|SCIENCE TO FIELD)/i],
  ['convergence', /(CONVERGENZA VERIFICATA|DA VALIDARE|VERIFIED CONVERGENCE|TO VALIDATE)/i],
  ['portfolio', /(PORTAFOGLIO|PORTFOLIO|ETICHETTA|LABEL)/i],
  ['evidence', /(FORZA DELL.EVIDENZA|EVIDENCE STRENGTH)/i],
  ['sources', /(FONTI DIETRO QUESTO CASO|SOURCES BEHIND THIS CASE)/i],
  ['window', /(FINESTRA DI APPLICAZIONE|APPLICATION WINDOW)/i],
];

const caseReports = [];

const inspectCase = async (lang, idx, expectKind) => {
  if (!(await openCard(idx))) return null;
  const txt = await scan(`CASE#${idx} (${expectKind})`, lang);
  /* IL TITOLO SI TROVA CON GLI OCCHI, NON CONTANDO LE RIGHE.
     Cercarlo come «la prima riga sostanziale» restituiva «INTEGRAZIONI · DEMO»
     — una voce della barra laterale — su tutti e dieci i casi, e quindi il
     controllo «nessuna scheda senza titolo» passava senza guardare nulla.

         UN CONTROLLO CHE MISURA LA COSA SBAGLIATA PASSA SEMPRE.

     Il titolo e il testo piu grande della pagina, che e esattamente come lo
     riconosce chi guarda. */
  const title = await page.evaluate(() => {
    let best = null, size = 0;
    for (const e of document.querySelectorAll('div,span,h1,h2')) {
      const t = (e.textContent || '').trim();
      if (!t || t.length > 90 || e.children.length > 1) continue;
      /* Il segnaposto della finestra sconosciuta e un trattino lungo, disegnato
         grande: senza questa riga «—» vinceva per dimensione e il controllo
         dichiarava senza titolo ogni scheda che un titolo ce l'aveva.
         Un titolo ha delle lettere. */
      if ((t.match(/\p{L}/gu) || []).length < 3) continue;
      const px = parseFloat(getComputedStyle(e).fontSize) || 0;
      if (px > size) { size = px; best = t; }
    }
    return best || '';
  });

  const present = {};
  for (const [k, re] of FIELD_PROBES) present[k] = re.test(txt);

  /* Defect 2 · una scheda senza titolo comprensibile */
  if (!title || title.length < 3) findings.noTitle.push(`${lang} case#${idx}: no readable title`);

  /* Defect 3 · «in attesa di localizzazione» su un caso il cui archetipo non
     avra mai un bersaglio agronomico */
  if (txt.includes(AWAITING[lang])) {
    findings.falseAwaiting.push(`${lang} case#${idx}: «${AWAITING[lang]}» — title "${title.slice(0, 50)}"`);
  }

  /* Defect 4 · l'evidenza citata contro l'evidenza mostrata */
  const m = txt.match(/(\d+)\s+(elementi di evidenza registrati|recorded evidence statements)/i);
  const shown = m ? Number(m[1]) : null;
  if (shown === 0) findings.zeroEvidence.push(`${lang} case#${idx}: shows 0 evidence on "${title.slice(0, 40)}"`);

  caseReports.push({ lang, idx, kind: expectKind, title: title.slice(0, 48), evidence: shown, present });
  await snap(`${lang}-case-${idx}-${expectKind}`);
  if (!(await clickNav(NAV[lang].back))) await clickNav(NAV[lang].home);
  await page.waitForTimeout(380);
  return { title, shown };
};

/* ── ACCESSO ─────────────────────────────────────────────────────────────── */
await page.goto(`${origin}/accesso.html`, { waitUntil: 'networkidle' }).catch(() => {});
await page.waitForTimeout(600);
await scan('ACCESSO', 'it');
await snap('it-ACCESSO');

await page.goto(`${origin}/portale.html`, { waitUntil: 'networkidle' });
await page.waitForTimeout(800);

const tour = async (lang) => {
  const N = NAV[lang];
  await clickNav(N.home);
  await scan('HOME · Radar', lang);
  await snap(`${lang}-HOME`);

  /* pagination — «vedi tutte le 37» deve mostrarne piu di dodici */
  const before = (await cards()).length;
  const all = await page.evaluate(() => {
    /* IL CONTROLLO E IL FIGLIO, NON IL PADRE.
       Il primo elemento che contiene «VEDI TUTTE 37 OPPORTUNITÀ» e il DIV che
       lo centra, e quel div non e cliccabile: lo e lo SPAN dentro di lui.
       Risalire la gerarchia — che funziona per le voci di navigazione — qui
       andava nella direzione sbagliata e tornava «non trovato» su un pulsante
       presente sette volte nel DOM.

           SI CLICCA DOVE IL CURSORE DIVENTA UNA MANO,
           E QUEL PUNTO PUO STARE SOTTO, NON SOPRA.

       Quindi: fra tutti i candidati, il piu profondo che sia davvero
       cliccabile. */
    const cands = [...document.querySelectorAll('span,div')]
      .filter((e) => /VEDI TUTTE|VIEW ALL|MOSTRA TUTT/i.test((e.textContent || '').trim())
        && (e.textContent || '').length < 60);
    const hit = cands.reverse().find((e) => getComputedStyle(e).cursor === 'pointer');
    if (!hit) return false;
    hit.click();
    return true;
  });
  await page.waitForTimeout(700);
  const after = (await cards()).length;
  /* IL CONTROLLO CHE SI SALTA DA SOLO NON E UN CONTROLLO.
     Prima: «se il pulsante esiste E non ha cambiato nulla, segnala». Se il
     pulsante non si trovava, non si segnalava niente — e il giro restava sulle
     dodici schede della prima pagina senza dirlo, trovando solo due
     convergenze verificate delle nove. Il salto era invisibile esattamente
     come il difetto che avrebbe dovuto trovare. */
  if (!all) findings.empty.push(`${lang} pagination: the "view all" control was not found`);
  else if (!(after > before)) findings.empty.push(`${lang} pagination: "view all" changed nothing (${before} -> ${after})`);

  const list = await cards();
  const verifiedIdx = list.filter((c) => c.text.includes(VERIFIED[lang])).map((c) => c.i);
  const validateIdx = list.filter((c) => c.text.includes(TOVALID[lang]) && !c.text.includes(VERIFIED[lang])).map((c) => c.i);

  /* Tre e tre, e di archetipi diversi dove il pacchetto ne offre di diversi:
     leggere tre volte lo stesso archetipo non e leggere tre casi. */
  if (verifiedIdx.length < 3) findings.empty.push(`${lang} radar: only ${verifiedIdx.length} verified convergence cards reachable, wanted 3`);
  if (validateIdx.length < 3) findings.empty.push(`${lang} radar: only ${validateIdx.length} to-validate cards reachable, wanted 3`);
  const spread = (idxs) => {
    const seen = new Set(), out = [];
    for (const i of idxs) {
      const c = list.find((x) => x.i === i);
      const arch = (String(c && c.text).match(/(PRESSIONE IN CAMPO|MOMENTO DI MERCATO|RESISTENZA[^\n]*|APERTURA COMPETITIVA|PREPARAZIONE NORMATIVA|DALLA SCIENZA AL CAMPO|FIELD PRESSURE|MARKET MOMENT|RESISTANCE[^\n]*|COMPETITIVE OPENING|REGULATORY PREPARATION|SCIENCE TO FIELD)/) || [''])[0];
      if (out.length < 3 && !seen.has(arch)) { seen.add(arch); out.push(i); }
    }
    for (const i of idxs) { if (out.length >= 3) break; if (!out.includes(i)) out.push(i); }
    return out.slice(0, 3);
  };
  for (const i of spread(verifiedIdx)) await inspectCase(lang, i, 'verified');
  for (const i of spread(validateIdx)) await inspectCase(lang, i, 'to-validate');

  for (const [label, key] of [['FUTURE', 'future'], ['WINDOWS', 'windows'], ['MARKET', 'market'],
    ['PORTFOLIO', 'portfolio'], ['VOCI', 'voci'], ['COMPETITOR', 'competitor'],
    ['SCIENCE', 'science'], ['ARCHIVE', 'archive'], ['SOURCES', 'sources']]) {
    if (!(await clickNav(N[key]))) { findings.empty.push(`${lang} · ${label}: nav "${N[key]}" not found`); continue; }
    await scan(label, lang);
    await snap(`${lang}-${label}`);
  }

  /* RESISTENZA vive dentro l'intelligence scientifica */
  await clickNav(N.science);
  await clickText(lang === 'it' ? 'RESISTENZA' : 'RESISTANCE');
  await scan('RESISTANCE', lang);
  await snap(`${lang}-RESISTANCE`);

  const box = await page.$('input');
  if (box) {
    await box.click().catch(() => {});
    await box.fill('vite');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(650);
    await scan('SEARCH', lang);
    await snap(`${lang}-SEARCH`);
  } else findings.empty.push(`${lang} · SEARCH: no input`);
  await clickNav(N.home);
};

await tour('it');
await clickText('EN'); await page.waitForTimeout(600);
await tour('en');
await clickText('IT'); await page.waitForTimeout(600);
await scan('HOME after IT→EN→IT', 'it');
await snap('it-HOME-return');

findings.fatal = fatals;
await browser.close();
if (server) server.close();

const G = '\x1b[32m', R = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
const line = (id, title, hits) => {
  console.log(`  ${hits.length === 0 ? `${G}PASS${X}` : `${R}FAIL${X}`}  ${id.padEnd(5)} ${title.padEnd(56)} exp 0      got ${hits.length}`);
  [...new Set(hits)].slice(0, 6).forEach((h) => console.log(`        ${h}`));
};
console.log('');
console.log(`  SINTONIA ITALY · PATRICIA'S WALKTHROUGH   (${origin})`);
console.log('  ' + '─'.repeat(96));
line('D1', 'No fatal JavaScript', findings.fatal);
console.log(`        ${D}(${templateNoise.length} SVG attribute notices from unrendered template placeholders)${X}`);
line('D2', 'No "undefined" on any screen', findings.undef);
line('D3', 'No "[object Object]" on any screen', findings.objobj);
line('D4', 'No Portuguese in the Italian interface', findings.pt);
line('D5', 'No internal QA / provenance enum on screen', findings.internal);
line('D6', 'No English issue label inside the Italian interface', findings.enLeak);
line('D7', 'No opportunity card without a readable title', findings.noTitle);
line('D8', 'No "awaiting localization" on a case that will never have a target', findings.falseAwaiting);
line('D9', 'No case showing zero evidence', findings.zeroEvidence);
line('D10', 'Every screen rendered, pagination and filters respond', findings.empty);
console.log('  ' + '─'.repeat(96));
console.log(`  ${caseReports.length} opportunity cases opened and read`);
for (const c of caseReports) {
  const miss = Object.entries(c.present).filter(([, v]) => !v).map(([k]) => k);
  console.log(`     ${c.lang} ${String(c.kind).padEnd(11)} ev=${String(c.evidence ?? '-').padStart(4)}  ${c.title.padEnd(46)} ${miss.length ? D + 'absent: ' + miss.join(',') + X : G + 'all panels present' + X}`);
}
if (SHOTS) console.log(`  ${shots.length} screenshots in ${SHOTS}`);
console.log('');
const total = Object.values(findings).reduce((a, v) => a + v.length, 0);
process.exit(total === 0 ? 0 : 1);
