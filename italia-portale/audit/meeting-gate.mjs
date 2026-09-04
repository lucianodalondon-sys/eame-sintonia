#!/usr/bin/env node
/* SINTONIA · IL PORTONE DELLA RIUNIONE
   ---------------------------------------------------------------------------
       node audit/meeting-gate.mjs           tabella umana
       node audit/meeting-gate.mjs --json    macchina

   Venti testimoni sopra una domanda sola: LO SCHERMO PRESENTA CIO CHE IL
   MOTORE HA DECISO, O DECIDE PER CONTO SUO?

   Nove di questi portoni sono scritti per REPROVARE LA VERSIONE PRECEDENTE.
   Un test che non rompe il bug che dice di sorvegliare non e un testimone: e
   una firma. Ognuno di quei nove porta accanto la riga `# REPROVA:` con il
   comportamento esatto che deve far fallire.

       UN PORTONE CHE NON SA QUALE VERSIONE DEVE BOCCIARE
       NON STA SORVEGLIANDO NIENTE.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { serve, open, openCase, screenText, clickTitle, C, line } from './lib/drive.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const R = (f) => fs.readFileSync(path.join(CLIENT, f), 'utf8');

const JSONOUT = process.argv.includes('--json');
const PORT = 8951;

/* Il commit dell'intelligenza canonica che questa riunione mostra. Non e una
   preferenza: e la procedenza che lo snapshot dichiara, e se cambia senza che
   qualcuno lo scriva qui, il portone lo dice. */
const EXPECTED_SOURCE_HEAD = 'b3935bd';
const EXPECTED_BUILD_ID = 'V21-358954754db5ea2f';
const EXPECTED_TOTAL = 43;

const SNAP = JSON.parse(R('meeting-intelligence-snapshot.json'));
const PORTALE = R('portale.html');
const MODEL = R('italy-app-model.js');

const results = [];
const check = (id, title, fn) => {
  let r;
  try { r = fn(); } catch (e) { r = { pass: false, expected: 'check runs', measured: 'THREW', detail: [String(e && e.message)] }; }
  results.push(Object.assign({ id, title }, r));
};
const zero = (bad, exp) => ({ pass: bad.length === 0, expected: exp === undefined ? 0 : exp, measured: bad.length, detail: bad.slice(0, 10) });

/* ─────────────────────────── IL CONTRATTO ─────────────────────────────── */

check('MG1', 'MEETING_SNAPSHOT_CONTRACT · header whole and identified', () => {
  const bad = [];
  for (const k of ['COLLECTION', 'LAW', 'SOURCE_HEAD', 'BUILD_ID', 'ENGINE_VERSION',
    'RULE_VERSION', 'GENERATED_AT', 'MEETING_CUTOFF', 'TOTAL_CASES', 'CASES']) {
    if (SNAP[k] === undefined) bad.push(`${k} absent`);
  }
  if (SNAP.TOTAL_CASES !== (SNAP.CASES || []).length) bad.push('TOTAL_CASES disagrees with CASES');
  return zero(bad);
});

check('MG2', 'SNAPSHOT_SOURCE_HEAD_VALID · declares the canonical intelligence', () => {
  const bad = [];
  if (SNAP.SOURCE_HEAD !== EXPECTED_SOURCE_HEAD) bad.push(`SOURCE_HEAD ${SNAP.SOURCE_HEAD}, expected ${EXPECTED_SOURCE_HEAD}`);
  if (SNAP.BUILD_ID !== EXPECTED_BUILD_ID) bad.push(`BUILD_ID ${SNAP.BUILD_ID}, expected ${EXPECTED_BUILD_ID}`);
  /* Il pacchetto del sito e lo snapshot devono venire dallo stesso build: due
     build diversi sulla stessa schermata sono due popolazioni. */
  const site = R('italy-handoff-v21.js').slice(0, 4000);
  if (!site.includes(EXPECTED_BUILD_ID)) bad.push('italy-handoff-v21.js was built from another BUILD_ID');
  return zero(bad);
});

check('MG3', 'NO_PARTIAL_INPUT · nothing crossed the meeting cutoff', () => {
  const bad = [];
  const cut = Date.parse(SNAP.MEETING_CUTOFF);
  if (!cut) bad.push('MEETING_CUTOFF unparseable');
  for (const c of SNAP.CASES) {
    const d = c.REFERENCE_DATE ? Date.parse(c.REFERENCE_DATE) : null;
    if (d && d > cut) bad.push(`${c.ID} REFERENCE_DATE ${c.REFERENCE_DATE} is after the cutoff`);
  }
  return zero(bad);
});

/* ─── NO_RAW_BYPASS · la prosa di ricerca non attraversa, a nessuna profondita ── */

/* REPROVA: la versione precedente copiava i contenitori interi */
check('MG4', 'DEEP_NESTED_INTERNAL_TOKEN_FILTER · no research prose below depth 1', () => {
  const CODE = /^[A-Z0-9][A-Z0-9_\-./: ]*$/;
  /* I nomi propri attraversano: un prodotto si chiama «Lamdex® Extra» e una
     sostanza «PARAFFIN OIL/(CAS 97862-82-3)». Sono fatti del registro, non
     prosa — e sono nominati qui uno per uno invece di essere esclusi da una
     regola che domani lascerebbe passare una frase. */
  const NAMES = new Set(['PORTFOLIO_MATCHES[].PRODUCT_NAME',
    'MATCHED_COMMERCIAL_PRODUCT_NAMES[]', 'ACTIVE_INGREDIENT_NAMES[]']);
  const bad = [];
  const prose = (v) => typeof v === 'string' && v.length >= 12 && v.includes(' ')
    && !CODE.test(v) && !/^\d{4}-\d{2}-\d{2}/.test(v) && !v.startsWith('http');
  const walk = (o, p, depth) => {
    if (o && typeof o === 'object') {
      if (Array.isArray(o)) o.forEach((v) => walk(v, p + '[]', depth + 1));
      else Object.keys(o).forEach((k) => walk(o[k], p ? p + '.' + k : k, depth + 1));
    } else if (depth >= 2 && prose(o) && !NAMES.has(p)) {
      bad.push(`${p} carries prose: ${String(o).slice(0, 60)}`);
    }
  };
  SNAP.CASES.forEach((c) => walk(c, '', 0));
  /* La testimonianza a profondita 4: dict -> dict -> list -> dict -> foglia. */
  let deepest = 0;
  const depthOf = (o, d) => {
    if (o && typeof o === 'object') {
      (Array.isArray(o) ? o : Object.values(o)).forEach((v) => depthOf(v, d + 1));
    } else if (d > deepest) deepest = d;
  };
  SNAP.CASES.forEach((c) => depthOf(c, 0));
  if (deepest < 4) bad.push(`snapshot never nests deeper than ${deepest}; the deep witness is vacuous`);
  const uniq = [...new Set(bad)];
  return { pass: uniq.length === 0, expected: 0, measured: uniq.length, detail: uniq.slice(0, 8) };
});

/* REPROVA: NEXT_TRIGGER era prosa portoghese su 215 blocchi su 215 */
check('MG5', 'NO_RAW_BYPASS · the four forbidden bookkeeping words never ship', () => {
  const raw = fs.readFileSync(path.join(CLIENT, 'meeting-intelligence-snapshot.js'), 'utf8');
  const bad = [];
  for (const w of ['NEXT_TRIGGER', 'RED_TEAM_FINDINGS', 'BLOCKING_GATES',
    'WHY_NOT_CLIENT_SAFE', 'BRIEF_TEMPLATES', 'ORIGINAL_RESEARCH_TEXT']) {
    if (raw.includes('"' + w + '"')) bad.push(`${w} crossed the boundary`);
  }
  /* La prosa che NON attraversa deve comunque essere DICHIARATA, altrimenti la
     schermata non puo dire «esiste, ed e nel documento X». */
  const declared = SNAP.CASES.filter((c) => c.WINDOW_CONDITION__PT_ONLY === true).length;
  if (declared === 0) bad.push('no case declares WINDOW_CONDITION__PT_ONLY; the declaration was dropped instead of the prose');
  return zero(bad);
});

/* ─────────────────── I DUE PROPRIETARI, NEL CODICE ────────────────────── */

/* REPROVA: `const primary = c.primary || (verified[0] ? ...)` incoronava il primo
   VERIFIED in ordine di array — e `primaryLabel: ... : csProductRows[0]` ripiegava
   sul primo prodotto QUALUNQUE. Nessuna delle tre forme sopravvive senza guardia. */
check('MG6', 'PRIMARY_MATCH_SINGLE_OWNER · no array-order winner survives', () => {
  const bad = [];
  /* Le tre righe che incoronavano per ordine, alla loro indentazione originale
     (4 spazi = non guardate). Le versioni di ripiego per i record che il motore
     non conosce vivono ora dentro un ramo `else`, piu rientrate. */
  if (/\n    const primary = c\.primary \|\| \(verified\[0\]/.test(PORTALE)) bad.push('the card still crowns verified[0] unconditionally');
  if (/\n    const csPrimary = csProds\.find\(/.test(PORTALE)) bad.push('the detail still crowns the first verified of its own list');
  if (/\n      primaryLabel: csPrimary \? csPrimary\.name\n        : \(csProductRows\[0\]/.test(PORTALE)) bad.push('the detail still falls back to any first product');
  if (!/ENG\.primary \? ENG\.primary\.name : null/.test(PORTALE)) bad.push('the card does not read PRIMARY_MATCH');
  if (!/CSENG\.primary \? \(csEngProds\.filter\(p => p\.isPrimary\)\[0\]/.test(PORTALE)) bad.push('the detail does not read PRIMARY_MATCH');
  return zero(bad);
});

/* REPROVA: `hasWindow: !!(csWinRec || csRecWinStart || csRecWinEnd)` chiedeva la
   finestra a due date nulle su 43 casi su 43, e `csGaps.push(lblNoWindowHonest)`
   scriveva «nessuna finestra» nell'eroe sopra un dome che diceva il contrario. */
check('MG7', 'WINDOW_SINGLE_OWNER · no parallel window rule survives', () => {
  const bad = [];
  if (/\n      hasWindow: !!\(csWinRec \|\| csRecWinStart \|\| csRecWinEnd\),/.test(PORTALE)) bad.push('the dome still derives the window from dates');
  if (/\n    if \(!\(csWinRec \|\| csRecWinStart \|\| csRecWinEnd\)\) csGaps\.push/.test(PORTALE)) bad.push('the hero still writes «no window» from dates');
  if (/\n      windowLine: \(csRec && csRec\.windowApplication\)/.test(PORTALE)) bad.push('the window line still restates a legacy enum unconditionally');
  if (!/CSENG\.window\.defined === 'YES'/.test(PORTALE)) bad.push('the dome does not read WINDOW_DEFINED');
  if (!/CSML\(CSENG\.window\.openNow, 'WINDOW_OPEN_NOW'\)/.test(PORTALE)) bad.push('the screen does not read WINDOW_OPEN_NOW');
  if (!/if \(CSENG\) \{\n      CSMLIST\(CSENG\.whatIsMissing/.test(PORTALE)) bad.push('the hero gaps do not read WHAT_IS_MISSING');
  return zero(bad);
});

check('MG8', 'NO_FRONTEND_INTELLIGENCE_RECALCULATION · the action map is not deduced from status', () => {
  const bad = [];
  /* REPROVA: `const modeKey = st === 'ACT_NOW' ? 'LOOK' : ...` era il portale che
     decideva che cosa fa il Commerciale, e lo decideva da un campo che parla del
     CASO. Alla sua indentazione originale (6 spazi) non deve piu esistere. */
  if (/\n      const modeKey = st === 'ACT_NOW'/.test(PORTALE)) {
    bad.push('the action map still derives its mode from the case status alone');
  }
  if (!/CSENG\.actionByDepartment/.test(PORTALE)) bad.push('the action map does not read ACTION_BY_DEPARTMENT');
  /* Il modello COPIA: non decide. Nessun campo canonico puo essere calcolato. */
  if (!/o\.engine = \{/.test(MODEL)) bad.push('the model does not publish the engine sub-object');
  return zero(bad);
});

/* ───────────────────── LE CONTAGGI, DAI 43 E SOLO DAI 43 ──────────────── */

check('MG9', 'CANONICAL_COUNTS_FROM_43_ONLY · nothing is hardcoded, nothing comes from D.CASES', () => {
  const bad = [];
  if (SNAP.TOTAL_CASES !== EXPECTED_TOTAL) bad.push(`TOTAL_CASES ${SNAP.TOTAL_CASES}, expected ${EXPECTED_TOTAL}`);
  const t = (k) => SNAP.CASES.reduce((a, c) => (a[String(c[k])] = (a[String(c[k])] || 0) + 1, a), {});
  const pub = t('PUBLICATION_STATE');
  if (pub.PUBLISHABLE !== 5) bad.push(`PUBLISHABLE ${pub.PUBLISHABLE}, expected 5`);
  if (pub.VALIDATION_REQUIRED !== 38) bad.push(`VALIDATION_REQUIRED ${pub.VALIDATION_REQUIRED}, expected 38`);
  /* Il modello deve CONTARE, non dichiarare: un numero scritto a mano nel
     portale sopravviverebbe a un motore che cambia. */
  if (!/const tally = \(fn\) => \{/.test(MODEL)) bad.push('the model declares counts instead of counting them');
  if (/D\.CASES/.test(R('meeting-labels.js'))) bad.push('the canonical dictionary reaches into the presentation cases');
  return zero(bad);
});

/* ───────────────────────── E ORA, NEL BROWSER ─────────────────────────── */

const srv = serve(PORT);
const { browser, page, errors, failed } = await open({ port: PORT });

/* Il radar apre su dodici schede e offre «VEDI TUTTE N». Sono i 43 che questa
   riunione mostra, e un portone che ne guarda solo dodici direbbe PASS su un
   portale che ne ha perso trentuno. */
const showAll = async () => {
  const n = await page.evaluate(() => {
    const hit = [...document.querySelectorAll('span')]
      .find((e) => /VEDI TUTTE|VIEW ALL/i.test(e.textContent || '') && e.children.length === 0);
    if (!hit) return 0;
    hit.click(); return 1;
  });
  if (n) await page.waitForTimeout(650);
  return n;
};
const toRadar = async () => { await clickTitle(page, 'Radar delle Opportunità'); await showAll(); };
await toRadar();

const radarIds = await page.evaluate(() =>
  [...document.querySelectorAll('[data-case]')].map((c) => c.getAttribute('data-case')).filter(Boolean));

const model = await page.evaluate(() => {
  const AM = window.ITALY_APP_MODEL;
  const recs = AM.collections.opportunities.records;
  return {
    meeting: AM.MEETING,
    total: recs.length,
    withEngine: recs.filter((o) => o.engine).length,
    labels: !!window.MEETING_LABELS,
    /* CIO CHE LA SCHEDA SCRIVE, contro CIO CHE IL MOTORE DICE — per tutti. */
    cards: recs.map((o) => ({
      id: o.id,
      enginePrimary: o.engine && o.engine.primary ? o.engine.primary.name : null,
      engineReason: o.engine ? o.engine.primaryReason : null,
      matches: o.engine ? o.engine.portfolioMatches.map((m) => m.PRODUCT_NAME) : [],
      windowDefined: o.engine ? o.engine.window.defined : null,
      windowOpenNow: o.engine ? o.engine.window.openNow : null,
    })),
  };
});

check('MG10', 'CANONICAL_43_RENDERED · every canonical case reaches the model', () => {
  const bad = [];
  if (model.total !== EXPECTED_TOTAL) bad.push(`model carries ${model.total} opportunities, expected ${EXPECTED_TOTAL}`);
  if (model.withEngine !== EXPECTED_TOTAL) bad.push(`${model.withEngine} of ${model.total} carry the engine payload`);
  if (!model.labels) bad.push('meeting-labels.js did not load');
  if (!model.meeting) bad.push('AM.MEETING absent');
  else {
    if (model.meeting.total !== EXPECTED_TOTAL) bad.push(`AM.MEETING.total ${model.meeting.total}`);
    if (model.meeting.sourceHead !== EXPECTED_SOURCE_HEAD) bad.push(`AM.MEETING.sourceHead ${model.meeting.sourceHead}`);
  }
  const ids = new Set(SNAP.CASES.map((c) => c.ID));
  model.cards.forEach((c) => { if (!ids.has(c.id)) bad.push(`${c.id} is on screen and not in the snapshot`); });
  if (radarIds.length !== EXPECTED_TOTAL) bad.push(`the expanded radar draws ${radarIds.length} cards, expected ${EXPECTED_TOTAL}`);
  radarIds.forEach((id) => { if (!ids.has(id)) bad.push(`${id} is drawn and is not canonical`); });
  ids.forEach((id) => { if (!radarIds.includes(id)) bad.push(`${id} is canonical and is not drawn`); });
  return zero(bad);
});

/* REPROVA: 26 casi su 43 avrebbero mostrato un principale scelto dall'ordine */
check('MG11', 'NO_PRIMARY_WHEN_UNKNOWN · no crown without a defensible rule', () => {
  const bad = [];
  let unknown = 0;
  for (const c of model.cards) {
    if (c.engineReason === 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER') {
      unknown += 1;
      if (c.enginePrimary) bad.push(`${c.id} shows a primary the engine refused to elect`);
    }
  }
  if (unknown === 0) bad.push('no case has an unknown primary; the witness is vacuous');
  return zero(bad);
});

const T = {};
const PROD = {};
for (const [key, id] of Object.entries({
  botrytis: 'OPP_5F31A63F844D', carpocapsa: 'OPP_75C37DED9160',
  umbria: 'OPP_169BD86DB324', scaphoideus: 'OPP_D11664591168',
})) {
  await toRadar();
  const ok = await openCase(page, id, 700);
  T[key] = ok ? await screenText(page) : null;
  /* I nomi che la schermata presenta COME PORTAFOGLIO portano `data-product`.
     Le prove che citano un'etichetta non lo portano: una relazione d'uso
     nominata fra le evidenze non e un prodotto incoronato, ed e giusto che
     resti leggibile. Il confronto e su quei nomi, non sul testo intero. */
  PROD[key] = ok ? await page.evaluate(() => [...new Set([...document.querySelectorAll('[data-product]')]
    .map((e) => e.getAttribute('data-product')).filter(Boolean))]) : null;
}

const caseOf = (id) => SNAP.CASES.find((c) => c.ID === id);
const L = JSON.parse(JSON.stringify(
  (() => { const w = {}; new Function('window', R('meeting-labels.js'))(w); return w.MEETING_LABELS.families; })()
));
const say = (fam, code) => (L[fam] && L[fam][code] ? L[fam][code][0] : null);

check('MG12', 'HERO_AND_DETAIL_AGREE_ON_PRIMARY · botrytis, the witness case', () => {
  const bad = [];
  const t = T.botrytis;
  if (!t) return { pass: false, expected: 'screen opens', measured: 'not opened' };
  const c = caseOf('OPP_5F31A63F844D');
  const primaryName = (c.PORTFOLIO_MATCHES.find((m) => m.PRODUCT_ID === c.PRIMARY_MATCH) || {}).PRODUCT_NAME;
  if (!t.includes(primaryName)) bad.push(`the engine's primary ${primaryName} is not on the screen`);
  if (!t.includes(say('UI', 'PRIMARY'))) bad.push('the primary is not marked as primary');
  /* REPROVA: la banda mostrava AGHARTA, BANJO ed EMBRACE — i legami di etichetta
     che il portale DEDUCE — dove PORTFOLIO_MATCHES ne dichiara uno solo. */
  for (const [k, id] of Object.entries({ botrytis: 'OPP_5F31A63F844D', carpocapsa: 'OPP_75C37DED9160', umbria: 'OPP_169BD86DB324', scaphoideus: 'OPP_D11664591168' })) {
    const shown = PROD[k]; const cc = caseOf(id);
    if (!shown) { bad.push(`${k}: screen did not open`); continue; }
    const engine = [...new Set((cc.PORTFOLIO_MATCHES || []).map((m) => m.PRODUCT_NAME))];
    shown.forEach((n) => { if (!engine.includes(n)) bad.push(`${k}: «${n}» is presented as portfolio and is not in PORTFOLIO_MATCHES`); });
    engine.forEach((n) => { if (!shown.includes(n)) bad.push(`${k}: «${n}» is in PORTFOLIO_MATCHES and is not presented`); });
  }
  return zero(bad);
});

/* REPROVA: la schermata scriveva «Nessuna finestra dichiarata per questo caso» */
check('MG13', 'WINDOW_UI_EQUALS_ENGINE · no screen contradicts the engine on the window', () => {
  const bad = [];
  const NOWIN = 'Nessuna finestra dichiarata per questo caso';
  const NOCANON = 'nessuna finestra canonica collegata';
  for (const [k, id] of Object.entries({ botrytis: 'OPP_5F31A63F844D', carpocapsa: 'OPP_75C37DED9160', scaphoideus: 'OPP_D11664591168' })) {
    const t = T[k]; const c = caseOf(id);
    if (!t) { bad.push(`${k}: screen did not open`); continue; }
    if (c.WINDOW_DEFINED === 'YES') {
      if (t.includes(NOWIN)) bad.push(`${k}: the hero says «no window» while WINDOW_DEFINED=YES`);
      if (t.toLowerCase().includes(NOCANON)) bad.push(`${k}: the dome says «no canonical window» while WINDOW_DEFINED=YES`);
      const type = say('WINDOW_TYPE', c.WINDOW_TYPE);
      if (type && !t.includes(type)) bad.push(`${k}: the window type «${type}» is not on the screen`);
    }
    const openL = say('WINDOW_OPEN_NOW', c.WINDOW_OPEN_NOW);
    if (openL && !t.includes(openL)) bad.push(`${k}: the current state «${openL}» is not on the screen`);
  }
  return zero(bad);
});

check('MG14', 'WINDOW_DEFINED_OPEN_SEPARATED · a known rule is never announced as an open window', () => {
  const bad = [];
  const openPhrase = say('WINDOW_OPEN_NOW', 'YES');
  const unknownPhrase = say('WINDOW_OPEN_NOW', 'UNKNOWN');
  for (const [k, id] of Object.entries({ carpocapsa: 'OPP_75C37DED9160', scaphoideus: 'OPP_D11664591168' })) {
    const t = T[k]; const c = caseOf(id);
    if (!t) continue;
    if (c.WINDOW_OPEN_NOW !== 'YES' && t.includes(openPhrase)) bad.push(`${k}: «${openPhrase}» on a case whose OPEN_NOW is ${c.WINDOW_OPEN_NOW}`);
    if (c.WINDOW_OPEN_NOW === 'UNKNOWN' && !t.includes(unknownPhrase)) bad.push(`${k}: OPEN_NOW=UNKNOWN is not stated on the screen`);
    if (c.WINDOW_RULE_STATE === 'RULE_ADMINISTRATIVE_ONLY') {
      const p = say('WINDOW_RULE_STATE', 'RULE_ADMINISTRATIVE_ONLY');
      if (!t.includes(p)) bad.push(`${k}: an administrative obligation is not named as one`);
    }
  }
  return zero(bad);
});

check('MG15', 'PEST_STAGE_AND_ACTION_ARE_TWO_FACTS · the end of the flight is not the end of the action', () => {
  const bad = [];
  const t = T.carpocapsa; const c = caseOf('OPP_75C37DED9160');
  if (!t) return { pass: false, expected: 'screen opens', measured: 'not opened' };
  if (c.PEST_STAGE_STATE !== 'STAGE_ENDED') bad.push(`the witness case no longer carries STAGE_ENDED (${c.PEST_STAGE_STATE})`);
  if (c.ACTION_RECOMMENDATION_STATE !== 'CONTINUE_RECOMMENDED') bad.push(`the witness case no longer carries CONTINUE_RECOMMENDED (${c.ACTION_RECOMMENDATION_STATE})`);
  const stage = say('PEST_STAGE_STATE', 'STAGE_ENDED');
  const act = say('ACTION_RECOMMENDATION_STATE', 'CONTINUE_RECOMMENDED');
  if (!t.includes(stage)) bad.push('the ended flight is not on the screen');
  if (!t.includes(act)) bad.push('the standing recommendation is not on the screen');
  return zero(bad);
});

check('MG16', 'WHY_COMMERCIAL_RENDERED · the sentence comes from the payload', () => {
  const bad = [];
  const t = T.botrytis; const c = caseOf('OPP_5F31A63F844D');
  if (!t) return { pass: false, expected: 'screen opens', measured: 'not opened' };
  if (!c.WHY_COMMERCIAL_IT) bad.push('the case carries no Italian why-commercial');
  else if (!t.includes(c.WHY_COMMERCIAL_IT.slice(0, 48))) bad.push('the payload sentence is not on the screen');
  for (const code of c.WHY_COMMERCIAL_CODES || []) {
    const p = say('WHY_COMMERCIAL_CODES', code);
    if (p && !t.includes(p)) bad.push(`the code ${code} is not shown in words`);
  }
  return zero(bad);
});

check('MG17', 'WHY_NOW_RENDERED · every link of the chain, including the ones that fail', () => {
  const bad = [];
  const t = T.umbria; const c = caseOf('OPP_169BD86DB324');
  if (!t) return { pass: false, expected: 'screen opens', measured: 'not opened' };
  const links = Object.keys(c.WHY_NOW_CHAIN || {});
  if (!links.length) bad.push('the witness case carries no chain');
  for (const k of links) {
    const p = say('CHAIN_LINK', k);
    if (p && !t.includes(p)) bad.push(`the chain link ${k} is not on the screen`);
  }
  const broken = links.filter((k) => c.WHY_NOW_CHAIN[k].OK !== true);
  if (!broken.length) bad.push('the witness case has no failing link; the witness is vacuous');
  return zero(bad);
});

check('MG18', 'ACTION_MAP_FROM_ENGINE · every department the engine convened, with its action', () => {
  const bad = [];
  const t = T.botrytis; const c = caseOf('OPP_5F31A63F844D');
  if (!t) return { pass: false, expected: 'screen opens', measured: 'not opened' };
  const deps = Object.entries(c.ACTION_BY_DEPARTMENT || {});
  if (deps.length !== 5) bad.push(`the engine convenes ${deps.length} departments, expected 5`);
  for (const [d, v] of deps) {
    const dl = say('DEPARTMENT', d);
    if (dl && !t.includes(dl)) bad.push(`${d} is not on the screen`);
    const al = say('ACTION', v.ACTION);
    if (al && !t.includes(al)) bad.push(`${d}: the action ${v.ACTION} is not on the screen`);
  }
  return zero(bad);
});

check('MG19', 'EVIDENCE_ROLE_RENDERED · evidence that decides nothing says so', () => {
  const bad = [];
  let shown = 0;
  for (const [k, id] of Object.entries({ botrytis: 'OPP_5F31A63F844D', umbria: 'OPP_169BD86DB324', carpocapsa: 'OPP_75C37DED9160' })) {
    const t = T[k]; const c = caseOf(id);
    if (!t) continue;
    const roles = [...new Set((c.EVIDENCE_ROLES || []).map((e) => e.ROLE))];
    for (const r of roles) {
      const p = say('EVIDENCE_ROLE', r);
      if (p && !t.includes(p)) bad.push(`${k}: the role ${r} is not on the screen`);
      if (p && t.includes(p)) shown += 1;
    }
    /* Il ruolo che NON sostiene deve essere visibile come gli altri: mostrarne
       solo i sostegni sarebbe una selezione, e una selezione non e una prova. */
    if (roles.includes('BACKGROUND_ONLY') && !t.includes(say('EVIDENCE_ROLE', 'BACKGROUND_ONLY'))) {
      bad.push(`${k}: BACKGROUND_ONLY is filtered out of the screen`);
    }
  }
  if (shown === 0) bad.push('no evidence role reached any screen');
  return zero(bad);
});

check('MG20', 'VALIDATION_STATE_NOT_HIDDEN · the 38 are shown, and shown as unvalidated', () => {
  const bad = [];
  for (const [k, id] of Object.entries({ umbria: 'OPP_169BD86DB324', carpocapsa: 'OPP_75C37DED9160', botrytis: 'OPP_5F31A63F844D' })) {
    const t = T[k]; const c = caseOf(id);
    if (!t) continue;
    const p = say('PUBLICATION_STATE', c.PUBLICATION_STATE);
    if (p && !t.includes(p)) bad.push(`${k}: PUBLICATION_STATE ${c.PUBLICATION_STATE} is not on the screen`);
  }
  return zero(bad);
});

check('MG21', 'IT_LABELS_COMPLETE + EN_LABELS_COMPLETE · no internal code can reach a screen', () => {
  const w = {}; new Function('window', R('meeting-labels.js'))(w);
  const ML = w.MEETING_LABELS;
  const need = [];
  const add = (f, v) => { if (v === null || v === undefined || v === '') return; (Array.isArray(v) ? v : [v]).forEach((x) => need.push([f, String(x)])); };
  for (const c of SNAP.CASES) {
    add('STATUS', c.STATUS); add('OPPORTUNITY_STATE', c.OPPORTUNITY_STATE);
    add('COMMERCIAL_PRIORITY', c.COMMERCIAL_PRIORITY); add('ARCHETYPE', c.ARCHETYPE);
    add('WHY_COMMERCIAL_CODES', c.WHY_COMMERCIAL_CODES);
    add('EXTERNAL_MATERIAL_READY', c.EXTERNAL_MATERIAL_READY);
    add('EXTERNAL_BLOCKER_CODES', c.EXTERNAL_BLOCKER_CODES);
    add('WHY_NOW_CODES', c.WHY_NOW_CODES);
    add('CHAIN_LINK', Object.keys(c.WHY_NOW_CHAIN || {}));
    add('SIGNAL_CURRENCY', c.SIGNAL_CURRENCY); add('COMMERCIAL_TIMING_BASIS', c.COMMERCIAL_TIMING_BASIS);
    add('WINDOW_TYPE', c.WINDOW_TYPE); add('WINDOW_DEFINED', c.WINDOW_DEFINED);
    add('WINDOW_OPEN_NOW', c.WINDOW_OPEN_NOW); add('WINDOW_OPEN_NOW_METHOD', c.WINDOW_OPEN_NOW_METHOD);
    add('WINDOW_RULE_STATE', c.WINDOW_RULE_STATE); add('WINDOW_STATE', c.WINDOW_STATE);
    add('PEST_STAGE_STATE', c.PEST_STAGE_STATE);
    add('ACTION_RECOMMENDATION_STATE', c.ACTION_RECOMMENDATION_STATE);
    add('THRESHOLD_STATE', c.THRESHOLD_STATE); add('NEED_DIRECTION', c.NEED_DIRECTION);
    add('NEED_METHOD', c.NEED_METHOD); add('PRIMARY_MATCH_REASON', c.PRIMARY_MATCH_REASON);
    add('PRODUCT_LINK_STATE', c.PRODUCT_LINK_STATE); add('MODE_OF_ACTION_STATE', c.MODE_OF_ACTION_STATE);
    add('APPLICATION_STATE', c.APPLICATION_STATE); add('WHAT_IS_MISSING', c.WHAT_IS_MISSING);
    add('PUBLICATION_STATE', c.PUBLICATION_STATE); add('TRAIL_STATE', c.TRAIL_STATE);
    add('COMMERCIAL_MAGNITUDE', c.COMMERCIAL_MAGNITUDE);
    add('CONFIDENCE', [c.CONFIDENCE, c.SIGNAL_CONFIDENCE, c.WINDOW_CONFIDENCE, c.PRODUCT_MATCH_CONFIDENCE]);
    add('GEOGRAPHIC_SCOPE', c.GEOGRAPHIC_SCOPE); add('CROP', c.CROP); add('TARGET', c.TARGET);
    add('GEOGRAPHY', [c.GEOGRAPHY, c.CLAIM_GEOGRAPHY]);
    (c.EVIDENCE_ROLES || []).forEach((e) => { add('EVIDENCE_ROLE', e.ROLE); add('EVIDENCE_WHY_CODE', e.WHY_CODE); add('EVIDENCE_ENTITY_TYPE', e.ENTITY_TYPE); });
    add('EVIDENCE_ENTITY_TYPE', c.EVIDENCE_FAMILIES);
    Object.entries(c.ACTION_BY_DEPARTMENT || {}).forEach(([d, v]) => {
      add('DEPARTMENT', d); add('ACTION_STATE', v.ACTION_STATE); add('ACTION', v.ACTION);
      add('ACTION_WHY_CODE', v.WHY_CODE); add('CHAIN_LINK', v.DEPENDENCY); add('CHAIN_LINK', v.MISSING_LINKS);
    });
    (c.INTELLIGENCE_BRIEF || []).forEach((b) => add('BRIEF_CODE', b.CODE));
    (c.PORTFOLIO_MATCHES || []).forEach((m) => {
      ['CROP_FIT', 'TARGET_FIT', 'REGIONAL_FIT', 'REGULATORY_FIT', 'WINDOW_FIT'].forEach((k) => add('FIT', m[k]));
      add('VALIDATION_STATE', m.VALIDATION_STATE); add('MATCH_REASON', m.MATCH_REASON);
      (m.RESTRICTIONS || []).forEach((r) => add('RESTRICTION', r.CODE));
    });
    (c.PRODUCT_RESTRICTIONS || []).forEach((r) => add('RESTRICTION', r.CODE));
    add('MAGNITUDE_DIM', Object.keys(c.COMMERCIAL_MAGNITUDE_DIMENSIONS || {}));
  }
  const uniq = [...new Set(need.map((x) => x.join('|')))].map((s) => s.split('|'));
  const bad = [];
  uniq.forEach(([f, c]) => {
    if (!ML.t(f, c, 'it')) bad.push(`IT missing: ${f}/${c}`);
    if (!ML.t(f, c, 'en')) bad.push(`EN missing: ${f}/${c}`);
  });
  return { pass: bad.length === 0, expected: `0 of ${uniq.length} codes untranslated`, measured: bad.length, detail: bad.slice(0, 12) };
});

check('MG22', 'NO_CONSOLE_ERROR_ON_THE_CANONICAL_JOURNEY', () => {
  const bad = errors.slice();
  (failed || []).forEach((f) => bad.push('failed request: ' + f));
  return zero(bad);
});

await browser.close();
if (srv && srv.close) srv.close();

if (JSONOUT) {
  console.log(JSON.stringify({ results, passed: results.filter((r) => r.pass).length, total: results.length }, null, 2));
} else {
  console.log('');
  console.log('  SINTONIA · MEETING INTEGRATION GATE');
  console.log('  ' + '─'.repeat(100));
  for (const r of results) console.log(line(r.pass, r.id, r.title, r.expected, r.measured));
  for (const r of results) {
    if (!r.pass && r.detail) (Array.isArray(r.detail) ? r.detail : [r.detail]).forEach((d) => console.log(`        ${C.d(String(d).slice(0, 140))}`));
  }
  const ok = results.filter((r) => r.pass).length;
  console.log('  ' + '─'.repeat(100));
  console.log(`  ${ok}/${results.length} passing` + (ok === results.length ? '' : `  ${C.r(`${results.length - ok} failing`)}`));
  console.log('');
}
process.exit(results.every((r) => r.pass) ? 0 : 1);
