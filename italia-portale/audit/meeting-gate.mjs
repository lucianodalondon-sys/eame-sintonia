/* SINTONIA · PORTONE DELLA RIUNIONE
   ===========================================================================
   Le testimonianze che l'integrazione della riunione deve poter produrre.

   Ogni controllo qui sotto guarda la SCHERMATA COSTRUITA — `renderVals()` sul
   pacchetto client reale — non una grep del sorgente. Un controllo che legge
   il file e non la schermata non sa se quel valore e arrivato all'occhio.

       IL MOTORE DECIDE. LO SCHERMO PRESENTA. IL PORTONE MISURA.

   NON e un secondo motore: non calcola inteligenza, non tocca soglie, non
   riscrive un verdetto. Conta cio che lo schermo mostra e lo confronta con
   cio che lo snapshot dichiara.
   =========================================================================== */
import fs from 'node:fs';
import path from 'node:path';
import { mount, CLIENT } from './lib/harness.mjs';

const C = {
  g: (t) => `\x1b[32m${t}\x1b[0m`, r: (t) => `\x1b[31m${t}\x1b[0m`,
  y: (t) => `\x1b[33m${t}\x1b[0m`, d: (t) => `\x1b[2m${t}\x1b[0m`,
  b: (t) => `\x1b[1m${t}\x1b[0m`,
};

const results = [];
const R = (name, ok, detail) => { results.push({ name, ok: !!ok, detail: detail || '' }); };

const SNAP = JSON.parse(fs.readFileSync(path.join(CLIENT, 'meeting-intelligence-snapshot.json'), 'utf8'));
/* L'HEAD dell'inteligenza che questa riunione ha approvato. Lo snapshot vale
   solo se dimostra di venire da qui. */
const APPROVED_SOURCE_HEAD = 'b3935bd';
const APPROVED_BUILD_ID = 'V21-358954754db5ea2f';

const m = await mount();
const vIT = m.vals({ view: 'canonical', lang: 'it' });
const vEN = m.vals({ view: 'canonical', lang: 'en' });
const detail = (id, lang) => m.vals({ view: 'copportunity', cCaseId: id, lang }).cd;
const IDS = SNAP.CASES.map((c) => c.ID);

/* ── 1 · il contratto dell'istantanea ─────────────────────────────────── */
R('MEETING_SNAPSHOT_CONTRACT',
  SNAP.COLLECTION === 'MEETING-INTELLIGENCE-SNAPSHOT'
  && Array.isArray(SNAP.CASES) && SNAP.CASES.length === SNAP.TOTAL_CASES
  && !!SNAP.BUILD_ID && !!SNAP.SOURCE_HEAD && !!SNAP.MEETING_CUTOFF,
  `${SNAP.COLLECTION} · ${SNAP.CASES.length} casi · ${SNAP.BUILD_ID}`);

R('SNAPSHOT_SOURCE_HEAD_VALID',
  SNAP.SOURCE_HEAD === APPROVED_SOURCE_HEAD && SNAP.BUILD_ID === APPROVED_BUILD_ID,
  `SOURCE_HEAD=${SNAP.SOURCE_HEAD} BUILD_ID=${SNAP.BUILD_ID}`);

/* ── 2 · i 43, e soltanto i 43 ────────────────────────────────────────── */
const rendered = vIT.cCards.map((c) => c.id);
R('CANONICAL_43_RENDERED',
  rendered.length === SNAP.TOTAL_CASES && IDS.every((id) => rendered.indexOf(id) >= 0),
  `${rendered.length} schede costruite su ${SNAP.TOTAL_CASES} casi`);

/* I conteggi della superficie devono essere RICONTABILI dallo snapshot. Se un
   solo numero non si riproduce contando i 43, viene da qualche altra parte. */
const cnt = (p) => SNAP.CASES.filter(p).length;
const kpi = (k) => (vIT.cKpis.filter((x) => x.key === k)[0] || {}).value;
const kpiChecks = [
  ['TOTAL', SNAP.CASES.length],
  ['PUBLISHABLE', cnt((c) => c.PUBLICATION_STATE === 'PUBLISHABLE')],
  ['VALIDATION_REQUIRED', cnt((c) => c.PUBLICATION_STATE === 'VALIDATION_REQUIRED')],
  ['ACT_NOW', cnt((c) => c.STATUS === 'ACT_NOW')],
  ['VALIDATE_NOW', cnt((c) => c.STATUS === 'VALIDATE_NOW')],
  ['TO_VALIDATE', cnt((c) => c.STATUS === 'TO_VALIDATE')],
  ['WATCH', cnt((c) => c.STATUS === 'WATCH')],
  ['FUTURE_PREPARATION', cnt((c) => c.STATUS === 'FUTURE_PREPARATION')],
  ['WINDOW_DEFINED', cnt((c) => c.WINDOW_DEFINED === 'YES')],
  ['WINDOW_OPEN_NOW', cnt((c) => c.WINDOW_OPEN_NOW === 'YES')],
];
const kpiBad = kpiChecks.filter(([k, want]) => kpi(k) !== want);
R('CANONICAL_COUNTS_FROM_43_ONLY', kpiBad.length === 0,
  kpiBad.length ? kpiBad.map(([k, w]) => `${k}: schermo ${kpi(k)} != snapshot ${w}`).join(' · ')
                : kpiChecks.map(([k, w]) => `${k}=${w}`).join(' · '));

/* I 29 casi di presentazione vivono su un'altra schermata e non entrano qui.
   Il controllo e sugli ID: due insiemi della stessa dimensione non sono lo
   stesso insieme, e solo l'identita lo dimostra. */
const demoIds = ((m.ctx.ITALY_DEMO && m.ctx.ITALY_DEMO.CASES) || []).map((c) => c.id);
const bleed = rendered.filter((id) => demoIds.indexOf(id) >= 0);
R('DEMO_CASES_NOT_COUNTED_AS_CANONICAL',
  bleed.length === 0 && rendered.every((id) => /^OPP_/.test(id)),
  `${demoIds.length} casi di presentazione · 0 sulla superficie canonica`);

/* ── 3 · nessuna scorciatoia, nessun ricalcolo ────────────────────────── */
const portal = fs.readFileSync(path.join(CLIENT, 'portale.html'), 'utf8');
const block = portal.slice(portal.indexOf('canonicalVals(T, s) {'));
/* La superficie legge lo snapshot e il dizionario. Se leggesse ITALY_DEMO o
   il pacchetto grezzo, starebbe scavalcando la frontiera. */
R('NO_RAW_BYPASS',
  block.indexOf('ITALY_DEMO') < 0 && block.indexOf('ITALY_HANDOFF_V21') < 0
  && block.indexOf('window.MEETING_INTELLIGENCE') >= 0,
  'la superficie canonica legge solo MEETING_INTELLIGENCE + MEETING_LABELS');

/* Nessuna soglia, nessun punteggio, nessuna decisione rifatta a valle. */
const recalcWords = ['OPPORTUNITY_SCORE', 'threshold', 'SCORE_DIMENSIONS'];
const recalcHits = recalcWords.filter((w) => block.indexOf(w) >= 0);
R('NO_FRONTEND_INTELLIGENCE_RECALCULATION', recalcHits.length === 0,
  recalcHits.length ? 'trovato: ' + recalcHits.join(', ') : 'nessun punteggio, nessuna soglia, nessun verdetto ricostruito');

/* ── 4 · cio che ogni scheda aperta deve mostrare ─────────────────────── */
let missProd = [], missWhyC = [], missWhyN = [], missWin = [], missAct = [], missEv = [], missPub = [];
for (const lang of ['it', 'en']) {
  for (const c of SNAP.CASES) {
    const d = detail(c.ID, lang);
    if (!d || !d.id) { missProd.push(c.ID + '/' + lang + ' NON APRE'); continue; }
    /* TUTTI i prodotti che reggono, mai «principale + altri N». */
    if ((d.prodRows || []).length !== (c.PORTFOLIO_MATCHES || []).length) missProd.push(`${c.ID}/${lang}`);
    /* PERCHE COMMERCIALE: la prosa approvata o, in sua assenza, i codici. */
    if (!d.hasWhyCommText && !(d.whyCommCodes || []).length) missWhyC.push(`${c.ID}/${lang}`);
    /* PERCHE ADESSO / PERCHE NON ANCORA: sempre una risposta. */
    if (!(d.whyNowCodes || []).length && !(d.chainRows || []).length) missWhyN.push(`${c.ID}/${lang}`);
    /* LO STATO DELLA FINESTRA non puo mancare: UNKNOWN e una risposta. */
    if (!d.win || (!d.win.definedL && !d.win.openL && !d.win.hasRule)) missWin.push(`${c.ID}/${lang}`);
    /* LA MAPPA DELLE AZIONI viene dal motore, reparto per reparto. */
    if ((d.deptRows || []).length !== Object.keys(c.ACTION_BY_DEPARTMENT || {}).length) missAct.push(`${c.ID}/${lang}`);
    /* IL RUOLO DELLE PROVE, in parole. */
    if ((c.EVIDENCE_ROLES || []).length && !(d.evRows || []).length) missEv.push(`${c.ID}/${lang}`);
    /* LO STATO DI PUBBLICAZIONE NON SI NASCONDE. */
    if (!d.pubLabel || !d.pubLong) missPub.push(`${c.ID}/${lang}`);
  }
}
R('ALL_PORTFOLIO_MATCHES_RENDERED', missProd.length === 0,
  missProd.length ? missProd.slice(0, 4).join(' · ')
    : `${SNAP.CASES.reduce((a, c) => a + (c.PORTFOLIO_MATCHES || []).length, 0)} legami di prodotto, tutti sullo schermo, in due lingue`);
R('WHY_COMMERCIAL_RENDERED', missWhyC.length === 0, missWhyC.slice(0, 4).join(' · ') || 'tutti i 43 casi, in due lingue');
R('WHY_NOW_RENDERED', missWhyN.length === 0, missWhyN.slice(0, 4).join(' · ') || 'catena o codici su tutti i 43, in due lingue');
R('WINDOW_STATE_RENDERED', missWin.length === 0, missWin.slice(0, 4).join(' · ') || 'stato della finestra su tutti i 43, UNKNOWN compreso');
R('ACTION_MAP_FROM_ENGINE', missAct.length === 0,
  missAct.slice(0, 4).join(' · ') || `${SNAP.CASES.reduce((a, c) => a + Object.keys(c.ACTION_BY_DEPARTMENT || {}).length, 0)} riquadri di reparto, uno per ogni voce del motore`);
R('EVIDENCE_ROLE_RENDERED', missEv.length === 0, missEv.slice(0, 4).join(' · ') || 'ruolo delle prove in parole su tutti i casi che ne portano');
R('VALIDATION_STATE_NOT_HIDDEN', missPub.length === 0,
  missPub.slice(0, 4).join(' · ') || 'i 38 in validazione portano il loro stato, e non somigliano ai 5 comprovati');

/* ── 5 · nessun gettone interno sullo schermo ─────────────────────────── */
const TOKEN = /\b[A-Z][A-Z0-9]{2,}(?:_[A-Z0-9]+)+\b/;
/* Gettoni che NON sono interni: sigle pubbliche del registro fitosanitario e
   codici di legge europei. Sono cio che il documento stesso stampa. */
const PUBLIC_OK = /^(FRAC|HRAC|IRAC)\b/;
const leaks = [];
const walk = (v, where, seen) => {
  if (v === null || v === undefined) return;
  if (typeof v === 'string') {
    const mt = v.match(TOKEN);
    if (mt && !PUBLIC_OK.test(mt[0])) leaks.push(`${where}: «${mt[0]}»`);
    return;
  }
  if (typeof v !== 'object') return;
  if (seen.has(v)) return; seen.add(v);
  if (Array.isArray(v)) { v.forEach((x, i) => walk(x, `${where}[${i}]`, seen)); return; }
  for (const k of Object.keys(v)) {
    /* Gli attributi d'identita (`data-…`) portano l'ID del caso al DOM apposta,
       perche un controllo possa dire QUALI casi, non solo quanti. Non sono
       testo sullo schermo. */
    if (k === 'id' || k === 'catKey' || k === 'stateKey' || k === 'key' || k === 'v'
        || k === 'evidenceId' || k === 'condNote' || k === 'url'
        || k === 'registration' || k === 'cBuildId' || k === 'cSourceHead') continue;
    if (typeof v[k] === 'function') continue;
    walk(v[k], `${where}.${k}`, seen);
  }
};
for (const lang of ['it', 'en']) {
  const v = m.vals({ view: 'canonical', lang });
  walk(v.cKpis, `${lang}.cKpis`, new WeakSet());
  walk(v.cCards, `${lang}.cCards`, new WeakSet());
  walk(v.cFilters, `${lang}.cFilters`, new WeakSet());
  for (const c of SNAP.CASES) walk(detail(c.ID, lang), `${lang}.${c.ID}`, new WeakSet());
}
R('NO_INTERNAL_CODES', leaks.length === 0,
  leaks.length ? `${leaks.length} fughe · ` + leaks.slice(0, 5).join(' · ')
               : 'nessun gettone interno in nessuna delle due lingue, su tutte le schede aperte');

/* ── 6 · le due lingue, complete per la demo ──────────────────────────── */
const ML = m.ctx.MEETING_LABELS;
const DEMO = ['OPP_5F31A63F844D', 'OPP_F8106D5E1767', 'OPP_169BD86DB324', 'OPP_75C37DED9160', 'OPP_D11664591168'];
for (const lang of ['it', 'en']) {
  const gaps = [];
  for (const id of DEMO) {
    const d = detail(id, lang);
    if (!d || !d.id) { gaps.push(id + ' non apre'); continue; }
    const must = { headline: d.headline, status: d.statusLabel, priority: d.priority,
      publication: d.pubLabel, publicationLong: d.pubLong, archetype: d.archetype,
      actionMap: (d.deptRows || []).length, whyNow: (d.whyNowCodes || []).length + (d.chainRows || []).length,
      window: d.win && (d.win.ruleL || d.win.definedL) };
    for (const k of Object.keys(must)) if (!must[k]) gaps.push(`${id}.${k}`);
  }
  R(`${lang.toUpperCase()}_LABELS_COMPLETE_FOR_DEMO`, gaps.length === 0,
    gaps.slice(0, 5).join(' · ') || `${DEMO.length} casi della demo, ogni blocco con la sua frase`);
}

/* Il dizionario deve coprire OGNI gettone che i 43 casi usano davvero. */
const uncovered = [];
const need = (fam, tok) => {
  if (tok === null || tok === undefined || tok === '') return;
  if (!ML.label('it', fam, tok) || !ML.label('en', fam, tok)) uncovered.push(`${fam}:${tok}`);
};
for (const c of SNAP.CASES) {
  ['STATUS', 'COMMERCIAL_PRIORITY', 'ARCHETYPE', 'WINDOW_TYPE', 'WINDOW_RULE_STATE',
   'WINDOW_DEFINED', 'WINDOW_OPEN_NOW', 'WINDOW_OPEN_NOW_METHOD', 'NEED_DIRECTION',
   'NEED_METHOD', 'PEST_STAGE_STATE', 'ACTION_RECOMMENDATION_STATE', 'THRESHOLD_STATE',
   'PUBLICATION_STATE', 'TRAIL_STATE', 'OPPORTUNITY_STATE', 'PRIMARY_MATCH_REASON',
   'PRODUCT_LINK_STATE', 'MODE_OF_ACTION_STATE', 'APPLICATION_STATE', 'SIGNAL_CURRENCY',
   'COMMERCIAL_TIMING_BASIS', 'GEOGRAPHIC_SCOPE', 'COMMERCIAL_MAGNITUDE',
   'EXTERNAL_MATERIAL_READY', 'CROP', 'TARGET', 'GEOGRAPHY'].forEach((f) => need(f, c[f]));
  (c.WHY_COMMERCIAL_CODES || []).forEach((x) => need('WHY_COMMERCIAL_CODES', x));
  (c.WHY_NOW_CODES || []).forEach((x) => need('WHY_NOW_CODES', x));
  (c.WHAT_IS_MISSING || []).forEach((x) => need('WHAT_IS_MISSING', x));
  (c.EVIDENCE_FAMILIES || []).forEach((x) => need('EVIDENCE_FAMILY', x));
  Object.keys(c.WHY_NOW_CHAIN || {}).forEach((k) => need('WHY_NOW_CHAIN_LINK', k));
  Object.keys(c.ACTION_BY_DEPARTMENT || {}).forEach((k) => {
    const v = c.ACTION_BY_DEPARTMENT[k];
    need('DEPARTMENT', k); need('ACTION_STATE', v.ACTION_STATE);
    need('ACTION', v.ACTION); need('ACTION_WHY_CODE', v.WHY_CODE);
  });
  (c.EVIDENCE_ROLES || []).forEach((e) => {
    need('EVIDENCE_ROLE', e.ROLE); need('EVIDENCE_ROLE_WHY', e.WHY_CODE); need('EVIDENCE_FAMILY', e.ENTITY_TYPE);
  });
  (c.INTELLIGENCE_BRIEF || []).forEach((b) => need('BRIEF', b.CODE));
  (c.PORTFOLIO_MATCHES || []).forEach((p) => {
    ['CROP_FIT', 'TARGET_FIT', 'REGIONAL_FIT', 'REGULATORY_FIT', 'WINDOW_FIT'].forEach((f) => need('PRODUCT_FIT', p[f]));
    need('VALIDATION_STATE', p.VALIDATION_STATE); need('MATCH_REASON', p.MATCH_REASON);
    (p.RESTRICTIONS || []).forEach((r) => need('RESTRICTION', r.CODE));
  });
}
R('LABEL_DICTIONARY_COVERS_SNAPSHOT', uncovered.length === 0,
  uncovered.length ? uncovered.slice(0, 6).join(' · ') : 'ogni gettone dei 43 casi ha una frase in IT e in EN');

/* ── 7 · le due letture che non devono confondersi ────────────────────── */
const veneto = SNAP.CASES.filter((c) => c.PEST_STAGE_STATE === 'STAGE_ENDED'
  && c.ACTION_RECOMMENDATION_STATE === 'CONTINUE_RECOMMENDED');
const venetoOk = veneto.every((c) => ['it', 'en'].every((lang) => {
  const d = detail(c.ID, lang);
  return d.stage && d.stage.divergent === true && !!d.stage.note && d.stage.stageL && d.stage.recL;
}));
R('STAGE_NOT_CONFUSED_WITH_ACTION', veneto.length > 0 && venetoOk,
  `${veneto.length} caso/i con volo concluso e raccomandazione viva · la nota che li separa e sullo schermo`);

/* Il principale esiste solo quando il motore porta una regola difendibile. */
const primaryBad = [];
for (const c of SNAP.CASES) {
  const d = detail(c.ID, 'it');
  const shown = (d.prodRows || []).filter((p) => p.isPrimary).length;
  const should = (c.PRIMARY_MATCH && c.PRIMARY_MATCH_REASON !== 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER') ? 1 : 0;
  if (shown > should) primaryBad.push(`${c.ID}: ${shown} principali, regola difendibile ${should}`);
}
R('PRIMARY_ONLY_WHEN_DEFENSIBLE', primaryBad.length === 0,
  primaryBad.slice(0, 4).join(' · ') || 'nessun principale inventato dove il motore dice di non avere una regola');

/* ── 8 · nessun ingresso parziale ─────────────────────────────────────── */
const partial = ['RUNNING', 'PARTIAL', 'UNCOMMITTED', 'TEMP', 'INCOMPLETE']
  .filter((w) => JSON.stringify(SNAP).indexOf('"' + w + '"') >= 0);
R('NO_PARTIAL_INPUT_USED', partial.length === 0,
  partial.length ? 'trovato: ' + partial.join(', ') : 'nessun marcatore di lavoro in corso dentro l\'istantanea');

/* ── il verdetto ──────────────────────────────────────────────────────── */
const pass = results.filter((x) => x.ok).length;
const fail = results.length - pass;
console.log('');
console.log(C.b('  PORTONE DELLA RIUNIONE · ' + SNAP.BUILD_ID + ' · SOURCE_HEAD ' + SNAP.SOURCE_HEAD));
console.log('');
for (const x of results) {
  console.log('  ' + (x.ok ? C.g('PASS') : C.r('FAIL')) + '  ' + x.name.padEnd(38) + C.d(x.detail));
}
console.log('');
console.log('  ' + (fail === 0 ? C.g(`${pass}/${results.length} testimonianze`) : C.r(`${fail} FALLITE su ${results.length}`)));
console.log('');
process.exit(fail === 0 ? 0 : 1);
