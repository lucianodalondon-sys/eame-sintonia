#!/usr/bin/env node
/* SINTONIA · MEETING BROWSER — la superficie canonica in un browser vero
   ---------------------------------------------------------------------------
   Le due contraddizioni non sono state viste in un test: sono state viste su
   uno SCHERMO. Quindi si chiudono su uno schermo.

   Questo portone apre Chromium, percorre
       HOME → RADAR CANONICO → OPPORTUNITA → PRODOTTI → PERCHE COMMERCIALE
       → PERCHE ORA → FINESTRA → MAPPA AZIONI → EVIDENZE → FONTI
   in italiano e in inglese, a 1440 e a 390, sui casi che la riunione deve
   poter mostrare, e confronta cio che il lettore LEGGE con cio che il motore
   ha scritto.

       UN CAMPO CHE PASSA NEI PROPS E UN CAMPO CHE PASSA NEI PROPS.
       LA CONTRADDIZIONE SI VEDE NEL DOM.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import { navName } from './lib/nav-names.mjs';
import path from 'node:path';
import { serve, open, clickTitle, clickSelector, screenText, clickables, CLIENT } from './lib/drive.mjs';

/* --dir <path> serve OUTRA pasta em vez de client/. Existe para uma coisa so:
   correr estas mesmas testemunhas sobre os BYTES DESCARREGADOS DO URL PUBLICO,
   quando o Chromium deste contentor nao consegue atravessar o proxy ate ao
   dominio. O que se mede continua a ser o que o publico recebe. */
const DIR = (() => { const i = process.argv.indexOf('--dir'); return i >= 0 ? process.argv[i + 1] : null; })();
const SERVE_DIR = DIR || CLIENT;

const SNAP = JSON.parse(fs.readFileSync(path.join(CLIENT, 'meeting-intelligence-snapshot.json'), 'utf8'));
const byId = (id) => SNAP.CASES.find((c) => c.ID === id) || {};

/* I casi che il briefing nomina, e cosa ciascuno deve poter dimostrare. */
const CASES = [
  { id: 'OPP_5F31A63F844D', what: 'botrite × vite × Emilia-Romagna · ACT_NOW · finestra aperta' },
  { id: 'OPP_75C37DED9160', what: 'carpocapsa × melo × Veneto · volo concluso E azione raccomandata' },
  { id: 'OPP_169BD86DB324', what: 'tignoletta × vite × Umbria · la fonte raffredda il caso' },
  { id: 'OPP_D11664591168', what: 'scafoideo × vite × Toscana · obbligo amministrativo' },
];

const findings = [];
const fail = (id, msg) => findings.push({ id, msg });
const visited = [];

/* IL NOME DELLA VOCE NON SI SCRIVE QUI.
   Questa riga diceva «Radar Canonico» / «Canonical Radar»: il nome che la voce
   di menu portava quando esistevano DUE radar. Da quando ne esiste uno solo la
   voce si chiama «Radar delle Opportunita», e questo portone ha continuato a
   cercare il nome vecchio — quattro volte, due larghezze per due lingue —
   dichiarando irraggiungibile una schermata che si apre al primo clic.

       UN PORTONE CHE CERCA UN NOME RITIRATO NON MISURA IL PORTALE:
       MISURA LA PROPRIA MEMORIA.

   Il nome viene ora dal dizionario, dove il portale lo tiene. */
const NAV_LABEL = { it: navName('it', 'navMeeting'), en: navName('en', 'navMeeting') };

const setLang = async (page, code) => {
  const ok = await page.evaluate((want) => {
    const e = [...document.querySelectorAll('span')].find((x) => (x.textContent || '').trim() === want && !x.children.length);
    if (!e) return false;
    let n = e;
    for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer' || n.onclick) { n.click(); return true; } n = n.parentElement; }
    e.click(); return true;
  }, code.toUpperCase());
  await page.waitForTimeout(700);
  return ok && (await page.evaluate(() => document.documentElement.lang)) === code;
};

/* Il click sulla scheda canonica: `data-meeting-case` e l'identita resa
   leggibile al DOM, come `data-case` lo e per il radar dimostrativo. */
const openMeetingCase = async (page, id) => {
  const ok = await page.evaluate((wanted) => {
    const card = document.querySelector(`[data-meeting-case="${wanted}"]`);
    if (!card) return false;
    let n = card;
    for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer' || n.onclick) { n.click(); return true; } n = n.parentElement; }
    card.click(); return true;
  }, id);
  await page.waitForTimeout(600);
  return ok;
};

const dom = (page) => page.evaluate(() => {
  const one = (s, a) => { const e = document.querySelector(s); return e ? (a ? e.getAttribute(a) : e.textContent.trim()) : null; };
  const all = (s, a) => [...document.querySelectorAll(s)].map((e) => (a ? e.getAttribute(a) : e.textContent.trim()));
  return {
    heroPrimary: one('[data-hero-primary]', 'data-hero-primary'),
    heroId: one('[data-meeting-hero]', 'data-meeting-hero'),
    hasPrimary: one('[data-meeting-products]', 'data-has-primary'),
    productCountAttr: one('[data-meeting-products]', 'data-meeting-products'),
    products: all('[data-product]', 'data-product'),
    noPrimaryShown: !!document.querySelector('[data-no-primary]'),
    windowOwner: one('[data-meeting-window]', 'data-window-owner'),
    windowDefined: one('[data-meeting-window]', 'data-window-defined'),
    windowOpen: one('[data-meeting-window]', 'data-window-open'),
    windowRule: one('[data-window-rule]'),
    windowState: one('[data-window-state]'),
    pestStage: one('[data-pest-stage]', 'data-pest-stage'),
    actionRec: one('[data-action-rec]', 'data-action-rec'),
    whyCommercial: !!document.querySelector('[data-meeting-why-commercial]'),
    whyNow: !!document.querySelector('[data-meeting-why-now]'),
    chain: all('[data-chain-link]', 'data-chain-link'),
    actionMap: !!document.querySelector('[data-meeting-action-map]'),
    actionDepts: all('[data-action-dept]', 'data-action-dept'),
    evidence: all('[data-evidence-role]', 'data-evidence-role'),
    cooling: all('[data-cooling]', 'data-cooling'),
    text: (document.body.innerText || '').replace(/ /g, ' '),
  };
});

/* Un token interno e una parola tutta maiuscola con un underscore. Nessuna
   lingua umana la scrive; se e a schermo, e una chiave che e sfuggita. */
const INTERNAL = /\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g;
/* Prosa di ricerca in portoghese: le parole che il portoghese ha e l'italiano no. */
const PT_WORDS = /\b(nao|entao|declarada|necessidade|estadio|limiar|boletim|evidencia|condicao|satisfeita|atual|acao|janela|comercial|proximo)\b/i;

const server = await serve(8899, SERVE_DIR);
let consoleErrors = [], failedReqs = [], deadControls = [];

for (const width of [1440, 390]) {
  const { browser, page, errors, failed } = await open({ port: 8899, width, height: width === 390 ? 844 : 1000 });

  for (const lang of ['it', 'en']) {
    if (lang === 'en' && !(await setLang(page, 'en'))) { fail('LANG', `${width}px · could not switch to EN`); continue; }
    if (lang === 'it' && (await page.evaluate(() => document.documentElement.lang)) !== 'it') { fail('LANG', `${width}px · not in IT`); continue; }

    /* HOME → RADAR CANONICO */
    if (!(await clickTitle(page, NAV_LABEL[lang], 800))) { fail('NAV', `${width}px ${lang} · the canonical radar is not reachable from the nav`); continue; }
    const radar = await dom(page);
    const cardCount = await page.evaluate(() => document.querySelectorAll('[data-meeting-case]').length);
    if (cardCount < 1) fail('RADAR', `${width}px ${lang} · the canonical radar rendered no card`);
    visited.push(`${width} ${lang} radar (${cardCount} cards)`);

    /* il radar non deve mostrare il totale dei 21 di presentazione */
    if (!/\b43\b/.test(radar.text)) fail('COUNT', `${width}px ${lang} · the canonical total 43 is not on the radar`);

    for (const { id, what } of CASES) {
      await clickTitle(page, NAV_LABEL[lang], 700);
      /* la scheda puo essere oltre la prima pagina: si apre l'elenco intero */
      await clickSelector(page, '[data-meeting-filter="MEETING_FILTER_ALL"]', 400);
      /* L'elenco parte da 24 schede: un caso oltre quella soglia non e
         irraggiungibile, e solo non ancora chiesto. Si preme finche c'e. */
      for (let i = 0; i < 4; i++) {
        if (await page.evaluate((w) => !!document.querySelector(`[data-meeting-case="${w}"]`), id)) break;
        if (!(await clickSelector(page, '[data-meeting-more]', 420))) break;
      }
      if (!(await openMeetingCase(page, id))) { fail('OPEN', `${width}px ${lang} · ${id} (${what}) does not open`); continue; }
      const d = await dom(page);
      const raw = byId(id);
      visited.push(`${width} ${lang} ${id}`);

      /* ── CONTRADDIZIONE A · un solo prodotto principale ───────────────── */
      const enginePrimaryId = raw.PRIMARY_MATCH || null;
      const enginePrimaryName = enginePrimaryId
        ? ((raw.PORTFOLIO_MATCHES || []).find((m) => m.PRODUCT_ID === enginePrimaryId) || {}).PRODUCT_NAME || null
        : null;
      const heroPrimary = d.heroPrimary || null;
      if ((heroPrimary || null) !== (enginePrimaryName || null)) {
        fail('PRIMARY', `${width}px ${lang} · ${id} · hero shows "${heroPrimary}", engine says "${enginePrimaryName}"`);
      }
      if (!enginePrimaryId && d.hasPrimary === 'true') fail('PRIMARY', `${width}px ${lang} · ${id} · the screen crowned a product the engine did not`);
      if (!enginePrimaryId && !d.noPrimaryShown) fail('PRIMARY', `${width}px ${lang} · ${id} · no primary, and the screen does not say why`);
      /* e TUTTI i prodotti sono a schermo, mai un riassunto */
      const engineProducts = (raw.PORTFOLIO_MATCHES || []).map((m) => m.PRODUCT_NAME);
      for (const p of engineProducts) if (!d.products.includes(p)) fail('PRODUCTS', `${width}px ${lang} · ${id} · ${p} is not on the screen`);
      if (/\+\s*\d+\s+(more|altri|altre)\b/i.test(d.text)) fail('PRODUCTS', `${width}px ${lang} · ${id} · the screen summarises products it already knows`);

      /* ── CONTRADDIZIONE B · una sola finestra ─────────────────────────── */
      if (d.windowOwner !== 'MEETING_INTELLIGENCE') fail('WINDOW', `${width}px ${lang} · ${id} · window owner is ${d.windowOwner}`);
      if (d.windowDefined !== (raw.WINDOW_DEFINED || null)) fail('WINDOW', `${width}px ${lang} · ${id} · DEFINED ${d.windowDefined} != engine ${raw.WINDOW_DEFINED}`);
      const expectOpen = 'WINDOW_OPEN_NOW_' + (raw.WINDOW_OPEN_NOW || 'UNKNOWN');
      if (d.windowOpen !== expectOpen) fail('WINDOW', `${width}px ${lang} · ${id} · OPEN_NOW ${d.windowOpen} != engine ${expectOpen}`);
      /* la frase legacy del calendario dei 29 non puo comparire qui */
      if (/nessuna finestra canonica collegata|no canonical window linked/i.test(d.text)) {
        fail('WINDOW', `${width}px ${lang} · ${id} · the legacy calendar sentence is on the canonical detail`);
      }
      /* la regola e lo stato restano due frasi diverse */
      if (d.windowRule && d.windowRule === d.windowState) fail('WINDOW', `${width}px ${lang} · ${id} · one sentence answers both window questions`);
      if (raw.WINDOW_DEFINED === 'YES' && raw.WINDOW_OPEN_NOW === 'UNKNOWN' && /finestra .*aperta|window .*open\b/i.test(d.windowState || '')) {
        fail('WINDOW', `${width}px ${lang} · ${id} · UNKNOWN reads as an open window`);
      }

      /* ── stadio e raccomandazione: due padroni ────────────────────────── */
      if (raw.PEST_STAGE_STATE && raw.PEST_STAGE_STATE !== 'STAGE_NOT_DECLARED') {
        if (d.pestStage !== raw.PEST_STAGE_STATE) fail('STAGE', `${width}px ${lang} · ${id} · stage ${d.pestStage} != ${raw.PEST_STAGE_STATE}`);
        if (raw.ACTION_RECOMMENDATION_STATE && raw.ACTION_RECOMMENDATION_STATE !== 'RECOMMENDATION_NOT_DECLARED' && !d.actionRec) {
          fail('STAGE', `${width}px ${lang} · ${id} · the stage is shown but the recommendation is not — the reader will infer one from the other`);
        }
      }

      /* ── le sezioni che la riunione deve vedere ───────────────────────── */
      if (!d.whyCommercial) fail('SECTION', `${width}px ${lang} · ${id} · WHY COMMERCIAL is missing`);
      if (!d.whyNow) fail('SECTION', `${width}px ${lang} · ${id} · WHY NOW is missing`);
      if (!d.actionMap) fail('SECTION', `${width}px ${lang} · ${id} · ACTION MAP is missing`);
      const engineDepts = Object.keys(raw.ACTION_BY_DEPARTMENT || {});
      for (const dep of engineDepts) if (!d.actionDepts.includes(dep)) fail('ACTION', `${width}px ${lang} · ${id} · ${dep} is not on the screen`);
      if (d.evidence.length !== (raw.EVIDENCE_ROLES || []).length) {
        fail('EVIDENCE', `${width}px ${lang} · ${id} · ${d.evidence.length} evidence rows of ${(raw.EVIDENCE_ROLES || []).length}`);
      }
      if (d.chain.length !== Object.keys(raw.WHY_NOW_CHAIN || {}).length) {
        fail('WHYNOW', `${width}px ${lang} · ${id} · ${d.chain.length} chain links of ${Object.keys(raw.WHY_NOW_CHAIN || {}).length}`);
      }

      /* ── nessun token interno, nessun portoghese ──────────────────────── */
      const tokens = [...new Set((d.text.match(INTERNAL) || []))]
        /* gli ID sono identita riportata accanto a un nome, non chiavi sfuggite */
        .filter((t) => !/^(IT|OPP|CATPRD|AI|GEO|REGION|FRAC|HRAC|IRAC|V21|NUTS)[-_]/.test(t))
        .filter((t) => !/^[A-Z]{2,4}_\d+$/.test(t));
      for (const t of tokens) fail('TOKEN', `${width}px ${lang} · ${id} · internal token on screen: ${t}`);
      if (lang !== 'pt') {
        const ptHit = (d.text.split('\n').find((l) => l.length > 25 && PT_WORDS.test(l) && !/^[A-Z_]+$/.test(l)) || '').trim();
        if (ptHit && /\b(nao|declarada|necessidade|boletim|evidencia|satisfeita)\b/i.test(ptHit)) {
          fail('PT', `${width}px ${lang} · ${id} · Portuguese research prose on screen: ${ptHit.slice(0, 70)}`);
        }
      }

      /* ── §13 · la soglia dell'Umbria non e quella dell'Emilia-Romagna ─── */
      if (id === 'OPP_169BD86DB324' && /\b5\s*%/.test(d.text)) {
        fail('UMBRIA', `${width}px ${lang} · the Emilia-Romagna 5% threshold appears on the Umbria case`);
      }

      /* ── controlli vivi ───────────────────────────────────────────────── */
      const ctrl = await clickables(page);
      if (ctrl.length < 3) deadControls.push(`${width} ${lang} ${id}: only ${ctrl.length} controls`);
    }
  }
  consoleErrors = consoleErrors.concat(errors);
  failedReqs = failedReqs.concat(failed);
  await browser.close();
}
server.close();

/* ── IL GIUDIZIO ─────────────────────────────────────────────────────────── */
const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
const groups = {};
for (const f of findings) (groups[f.id] = groups[f.id] || []).push(f.msg);

console.log('\n  SINTONIA · MEETING BROWSER · la superficie canonica in un browser vero');
console.log('  ' + '─'.repeat(100));
const rows = [
  ['PRIMARY_ONE_OWNER_ON_SCREEN', (groups.PRIMARY || []).length + (groups.PRODUCTS || []).length],
  ['WINDOW_ONE_OWNER_ON_SCREEN', (groups.WINDOW || []).length],
  ['STAGE_AND_RECOMMENDATION_SEPARATE', (groups.STAGE || []).length],
  ['SECTIONS_RENDERED', (groups.SECTION || []).length + (groups.ACTION || []).length + (groups.EVIDENCE || []).length + (groups.WHYNOW || []).length],
  ['NO_INTERNAL_TOKEN_ON_SCREEN', (groups.TOKEN || []).length],
  ['NO_PORTUGUESE_ON_SCREEN', (groups.PT || []).length],
  ['REGION_BOUND_TO_ITS_THRESHOLD', (groups.UMBRIA || []).length],
  ['REACHABLE_IT_EN_DESKTOP_MOBILE', (groups.NAV || []).length + (groups.LANG || []).length + (groups.OPEN || []).length + (groups.RADAR || []).length + (groups.COUNT || []).length],
  ['CONSOLE_ERRORS', consoleErrors.length],
  ['FAILED_REQUESTS', failedReqs.length],
  ['DEAD_CONTROLS', deadControls.length],
];
for (const [id, n] of rows) {
  console.log(`  ${n === 0 ? G + 'PASS' + X : R + 'FAIL' + X}  ${String(id).padEnd(38)} ${DIM}got${X} ${n}`);
}
for (const [k, v] of Object.entries(groups)) for (const msg of v.slice(0, 6)) console.log(`        ${DIM}${k} · ${msg.slice(0, 140)}${X}`);
for (const e of consoleErrors.slice(0, 5)) console.log(`        ${DIM}console · ${e.slice(0, 140)}${X}`);
for (const e of failedReqs.slice(0, 5)) console.log(`        ${DIM}request · ${e.slice(0, 140)}${X}`);
console.log('  ' + '─'.repeat(100));
console.log(`  percorsi: ${visited.length} · ${DIM}${visited.slice(0, 4).join(' | ')}${X}`);
const total = rows.reduce((a, [, n]) => a + n, 0);
console.log(`  ${total === 0 ? G + 'tutte le testimonianze verdi' + X : R + total + ' rilievi' + X}\n`);
process.exit(total === 0 ? 0 : 1);
