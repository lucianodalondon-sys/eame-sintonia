#!/usr/bin/env node
/* SINTONIA · I PORTONI DELLA RIUNIONE — audit/meeting-gate.mjs
   ===========================================================================
       node audit/meeting-gate.mjs           tabella leggibile
       node audit/meeting-gate.mjs --json    per una macchina

   Le quattordici testimonianze del §23, ognuna misurata sul portale montato —
   mai su un rapporto scritto, mai sul file sorgente quando la domanda riguarda
   cio che finisce sullo schermo.

   PERCHE QUESTI PORTONI, E NON ALTRI
   -----------------------------------
   Ogni riga qui sotto esiste perche un difetto REALE l'ha resa necessaria.
   Non sono controlli di stile: sono la memoria di cio che e gia andato storto.

       SNAPSHOT_FROM_CANONICAL_HEAD   il pacchetto puo essere ricostruito da un
                                      HEAD diverso e nessuno se ne accorge
       SNAPSHOT_43_CASES              un caso che sparisce non fa rumore
       NO_RAW_BYPASS                  il portale deduceva `status` dal grezzo:
                                      16 AGIRE ORA contro i 2 del motore
       ACTION_MAP_FROM_ENGINE         la mappa leggeva lo stato del CASO, e
                                      tutte e cinque le aree dicevano lo stesso
       ALL_PORTFOLIO_MATCHES_RENDERED «primario + altri N» quando lo snapshot
                                      li conosce tutti
       NO_INTERNAL_CODES              «VALIDATE NOW» stampato in italiano dalla
                                      fine di una catena di ripiego
       VALIDATION_STATE_NOT_HIDDEN    38 casi DA VALIDARE con addosso la sola
                                      parola «verificata»

   LA REGOLA DI QUESTO FILE
   ------------------------
   Un portone che non puo fallire non e un portone. Ognuno qui dichiara che
   cosa ha CONTATO, cosi un domani si vede se ha smesso di separare qualcosa —
   che e esattamente come `O1` era invecchiato senza dirlo.
   =========================================================================== */
import fs from 'node:fs';
import path from 'node:path';
import { mount, loadData, CLIENT, readPortal } from './lib/harness.mjs';

const CHECKS = [];
const check = (id, title, fn) => CHECKS.push({ id, title, fn });

const SNAP_JSON = path.join(CLIENT, 'meeting-intelligence-snapshot.json');
const PKG = path.join(CLIENT, '..', '..', 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                      'DESIGN-INGEST', 'OPPORTUNITIES.json');

const snap = JSON.parse(fs.readFileSync(SNAP_JSON, 'utf8'));
const CASES = snap.CASES || [];

/* Le viste che la riunione percorre. Un portone che misura una sola schermata
   prova una sola schermata. */
const CASE_IDS_FOR_SCREEN = [
  'OPP_5F31A63F844D', /* A · botrite × vite × Emilia-Romagna — ACT_NOW */
  'OPP_F8106D5E1767', /* B · botrite × vite × Toscana — ACT_NOW */
  'OPP_169BD86DB324', /* C · tignoletta × vite × Umbria — WATCH, fonte che raffredda */
  'OPP_75C37DED9160', /* D+E · carpocapsa × melo × Veneto — stadio finito, protezione no */
  'OPP_D11664591168', /* F · scafoide × vite × Toscana — obbligo amministrativo */
];

/* Il dettaglio espone i suoi campi sotto `cs`, non alla radice: leggerli alla
   radice restituisce `undefined` per tutto, e un portone che confronta
   `undefined` con un numero fallisce raccontando un difetto che non esiste. */
const caseVals = (id, lang = 'it') =>
  (mount().vals({ view: 'case', caseId: id, lang }) || {}).cs || {};

const radarVals = (lang = 'it') => mount().vals({ view: 'radar', lang, showAll: true });

/* ── 1 · PROVENIENZA ─────────────────────────────────────────────────────── */

check('MG1', 'SNAPSHOT_FROM_CANONICAL_HEAD · lo snapshot dichiara l’HEAD e il build che lo hanno prodotto', () => {
  const bad = [];
  if (!snap.SOURCE_HEAD) bad.push('SOURCE_HEAD assente');
  if (!snap.BUILD_ID) bad.push('BUILD_ID assente');
  if (!snap.MEETING_CUTOFF) bad.push('MEETING_CUTOFF assente');
  if (!snap.ENGINE_VERSION) bad.push('ENGINE_VERSION assente');
  if (!snap.RULE_VERSION) bad.push('RULE_VERSION assente');
  if (!snap.GENERATED_AT) bad.push('GENERATED_AT assente');
  /* Il BUILD_ID dello snapshot deve essere quello del pacchetto che lo ha
     generato: due build diversi con lo stesso nome sono il modo piu rapido di
     mostrare in riunione i numeri di ieri. */
  if (fs.existsSync(PKG)) {
    const pkg = JSON.parse(fs.readFileSync(PKG, 'utf8'));
    if (pkg.BUILD_ID !== snap.BUILD_ID) {
      bad.push(`BUILD_ID diverge: pacchetto ${pkg.BUILD_ID} vs snapshot ${snap.BUILD_ID}`);
    }
  } else {
    bad.push('pacchetto canonico assente — ricostruire con scripts/v21_cadeia.sh');
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad : [`${snap.SOURCE_HEAD} · ${snap.BUILD_ID} · cutoff ${snap.MEETING_CUTOFF}`] };
});

check('MG2', 'SNAPSHOT_43_CASES · il numero di casi e quello del pacchetto, contato non dichiarato', () => {
  const bad = [];
  if (CASES.length !== snap.TOTAL_CASES) {
    bad.push(`TOTAL_CASES dichiara ${snap.TOTAL_CASES}, il corpo ne ha ${CASES.length}`);
  }
  if (fs.existsSync(PKG)) {
    const pkg = JSON.parse(fs.readFileSync(PKG, 'utf8'));
    const a = new Set(pkg.RECORDS.map((r) => r.ID));
    const b = new Set(CASES.map((c) => c.ID));
    const lost = [...a].filter((x) => !b.has(x));
    const gained = [...b].filter((x) => !a.has(x));
    if (lost.length) bad.push(`lo snapshot perde ${lost.length}: ${lost.slice(0, 5).join(', ')}`);
    if (gained.length) bad.push(`lo snapshot inventa ${gained.length}: ${gained.slice(0, 5).join(', ')}`);
  }
  const dup = CASES.map((c) => c.ID).filter((x, i, a) => a.indexOf(x) !== i);
  if (dup.length) bad.push(`ID duplicati: ${dup.slice(0, 5).join(', ')}`);
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad : [`${CASES.length} casi, insieme identico al pacchetto`] };
});

check('MG3', 'MEETING_SNAPSHOT_CONTRACT · ogni caso porta i campi su cui la riunione si appoggia', () => {
  const REQUIRED = ['ID', 'STATUS', 'COMMERCIAL_PRIORITY', 'PUBLICATION_STATE',
                    'TRAIL_STATE', 'WINDOW_DEFINED', 'WINDOW_OPEN_NOW',
                    'WHY_NOW_CODES', 'WHY_COMMERCIAL_CODES', 'WHAT_IS_MISSING',
                    'PORTFOLIO_MATCHES', 'ACTION_BY_DEPARTMENT', 'EVIDENCE_ROLES'];
  const bad = [];
  for (const c of CASES) {
    for (const f of REQUIRED) {
      if (c[f] === undefined) bad.push(`${c.ID} manca ${f}`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10) : [`${REQUIRED.length} campi presenti su ${CASES.length} casi`] };
});

check('MG4', 'SNAPSHOT_ONLY_CLOSED_INPUTS · nessun ingresso parziale, temporaneo o in scrittura', () => {
  /* Un input aperto non si riconosce dal contenuto: si riconosce dal NOME e
     dal fatto che la cadeia lo abbia chiuso. Lo snapshot nasce da un solo
     file, e quel file e l'uscita dichiarata della cadeia canonica. */
  const bad = [];
  const raw = fs.readFileSync(SNAP_JSON, 'utf8');
  for (const m of ['TODO', 'PARTIAL', 'TEMP_', '_TMP', 'IN_PROGRESS', 'WRITING', 'DRAFT_']) {
    if (raw.includes('"' + m) || raw.includes(m + '"')) bad.push(`marca di lavoro aperto: ${m}`);
  }
  if (!fs.existsSync(PKG)) bad.push('il pacchetto sorgente non esiste');
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad : ['un solo ingresso: OPPORTUNITIES.json della cadeia canonica'] };
});

/* ── 2 · IL PORTALE NON DEDUCE PIU ───────────────────────────────────────── */

check('MG5', 'NO_RAW_BYPASS · lo stato sullo schermo e quello del motore, non quello dedotto', () => {
  const AM = loadData().ITALY_APP_MODEL;
  const recs = AM.collections.opportunities.records;
  const byId = {}; CASES.forEach((c) => { byId[c.ID] = c; });
  const bad = [];
  for (const r of recs) {
    const c = byId[r.id];
    if (!c) { bad.push(`${r.id} non e nello snapshot`); continue; }
    if (r.status !== c.STATUS) bad.push(`${r.id}: schermo ${r.status} ≠ motore ${c.STATUS}`);
    if (r.publicationState !== c.PUBLICATION_STATE) {
      bad.push(`${r.id}: pubblicazione ${r.publicationState} ≠ ${c.PUBLICATION_STATE}`);
    }
  }
  /* E il conteggio, che e la ragione per cui il portone esiste. */
  const n = (s) => recs.filter((r) => r.status === s).length;
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10)
      : [`ACT_NOW ${n('ACT_NOW')} · VALIDATE_NOW ${n('VALIDATE_NOW')} · WATCH ${n('WATCH')} — dal motore`] };
});

check('MG6', 'NO_PARTIAL_INPUT_USED · l’adattatore si innesta senza difetti e senza ID orfani', () => {
  const w = loadData();
  const A = w.MEETING_ADAPTER;
  const bad = [];
  if (!A) return { pass: false, expected: 0, measured: 1, detail: ['MEETING_ADAPTER non caricato'] };
  if (!A.OK) bad.push('adattatore non OK');
  (A.FAULTS || []).forEach((f) => bad.push('difetto: ' + f));
  if (A.SOURCE_HEAD !== snap.SOURCE_HEAD) bad.push('SOURCE_HEAD diverge');
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad : [`innestato da ${A.SOURCE_HEAD} · build ${A.BUILD_ID}`] };
});

check('MG7', 'MEETING_COUNTS_FROM_SNAPSHOT · nessun conteggio della schermata e una costante', () => {
  const w = loadData();
  const c = w.MEETING_ADAPTER.counts();
  const bad = [];
  const expect = {
    total: CASES.length,
    actNow: CASES.filter((x) => x.STATUS === 'ACT_NOW').length,
    validateNow: CASES.filter((x) => x.STATUS === 'VALIDATE_NOW').length,
    watch: CASES.filter((x) => x.STATUS === 'WATCH').length,
    publishable: CASES.filter((x) => x.PUBLICATION_STATE === 'PUBLISHABLE').length,
    validationRequired: CASES.filter((x) => x.PUBLICATION_STATE === 'VALIDATION_REQUIRED').length,
    windowDefined: CASES.filter((x) => x.WINDOW_DEFINED === 'YES').length,
    windowOpenNow: CASES.filter((x) => x.WINDOW_OPEN_NOW === 'YES').length,
  };
  for (const k of Object.keys(expect)) {
    if (c[k] !== expect[k]) bad.push(`${k}: contato ${c[k]} ≠ snapshot ${expect[k]}`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad : [JSON.stringify(expect)] };
});

/* ── 3 · CIO CHE LA SCHERMATA DEVE MOSTRARE ──────────────────────────────── */

check('MG8', 'ALL_PORTFOLIO_MATCHES_RENDERED · l’eroe mostra TUTTI i prodotti, mai «primario + N»', () => {
  const bad = [];
  for (const id of CASE_IDS_FOR_SCREEN) {
    const c = CASES.find((x) => x.ID === id);
    const v = caseVals(id);
    const expect = (c.PORTFOLIO_MATCHES || []).length;
    if (!expect) continue;
    if (v.mPortfolioCount !== expect) bad.push(`${id}: la schermata dichiara ${v.mPortfolioCount} di ${expect}`);
    if ((v.mPortfolio || []).length !== expect) bad.push(`${id}: rese ${(v.mPortfolio || []).length} schede di ${expect}`);
    /* ogni nome del motore deve comparire, non solo il primo */
    const names = new Set((v.mPortfolio || []).map((p) => p.name));
    for (const p of c.PORTFOLIO_MATCHES) {
      if (!names.has(p.PRODUCT_NAME)) bad.push(`${id}: manca ${p.PRODUCT_NAME}`);
    }
    /* e un principale si mostra solo con una regola difendibile */
    if (c.PRIMARY_MATCH_REASON === 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER' && v.mHasPrimary) {
      bad.push(`${id}: elegge un principale senza regola difendibile`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10) : [`${CASE_IDS_FOR_SCREEN.length} casi · tutti i prodotti resi`] };
});

check('MG9', 'WHY_COMMERCIAL_RENDERED + WHY_NOW_RENDERED · le due domande della riunione hanno risposta', () => {
  const bad = [];
  for (const id of CASE_IDS_FOR_SCREEN) {
    for (const lang of ['it', 'en']) {
      const v = caseVals(id, lang);
      if (!v.mHasWhyCommercial) bad.push(`${id}/${lang}: nessun PERCHE COMMERCIALE`);
      if (!v.mHasChain) bad.push(`${id}/${lang}: nessuna catena del PERCHE ORA`);
      const c = CASES.find((x) => x.ID === id);
      if ((c.WHY_NOW_CHAIN ? Object.keys(c.WHY_NOW_CHAIN).length : 0) !== (v.mChain || []).length) {
        bad.push(`${id}/${lang}: anelli resi ${(v.mChain || []).length}`);
      }
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10) : ['perche commerciale e catena resi in IT e EN'] };
});

check('MG10', 'WINDOW_STATE_RENDERED · la finestra e leggibile e UNKNOWN non sparisce', () => {
  const bad = [];
  for (const id of CASE_IDS_FOR_SCREEN) {
    const c = CASES.find((x) => x.ID === id);
    for (const lang of ['it', 'en']) {
      const v = caseVals(id, lang);
      if (!v.mHasWindow) { bad.push(`${id}/${lang}: nessuno stato di finestra`); continue; }
      /* Uno stato non misurato deve DIRSI. Se la finestra e UNKNOWN e la
         schermata non lo dichiara, l'ignoto e sparito dietro la copy. */
      if (c.WINDOW_OPEN_NOW === 'UNKNOWN' && !v.mWinUnknown && !v.mWinOpenL) {
        bad.push(`${id}/${lang}: UNKNOWN non dichiarato`);
      }
      if (c.WINDOW_OPEN_NOW === 'YES' && !v.mWinIsOpen) bad.push(`${id}/${lang}: finestra aperta non annunciata`);
      /* un obbligo amministrativo non e una finestra agronomica */
      if (c.WINDOW_RULE_STATE === 'RULE_ADMINISTRATIVE_ONLY' && !v.mWinAdministrative) {
        bad.push(`${id}/${lang}: obbligo amministrativo presentato come finestra`);
      }
      if (c.WINDOW_RULE_STATE === 'RULE_DELEGATED_TO_FARM' && !v.mWinDelegated) {
        bad.push(`${id}/${lang}: regola delegata al campo non dichiarata`);
      }
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10) : ['tipo, regola e stato attuale resi; UNKNOWN visibile'] };
});

check('MG11', 'ACTION_MAP_FROM_ENGINE · ogni reparto porta il proprio stato, non quello del caso', () => {
  const bad = [];
  for (const id of CASE_IDS_FOR_SCREEN) {
    const c = CASES.find((x) => x.ID === id);
    const v = caseVals(id);
    const engine = c.ACTION_BY_DEPARTMENT || {};
    const n = Object.keys(engine).length;
    if ((v.mDepts || []).length !== n) bad.push(`${id}: aree rese ${(v.mDepts || []).length} di ${n}`);
    for (const d of (v.mDepts || [])) {
      const e = engine[d.department];
      if (!e) { bad.push(`${id}: area inventata ${d.department}`); continue; }
      if (d.actionState !== e.ACTION_STATE) bad.push(`${id}/${d.department}: stato ${d.actionState} ≠ ${e.ACTION_STATE}`);
      if (d.action !== e.ACTION) bad.push(`${id}/${d.department}: azione ${d.action} ≠ ${e.ACTION}`);
      if (!d.actionStateL) bad.push(`${id}/${d.department}: stato senza etichetta`);
      if (!d.actionL) bad.push(`${id}/${d.department}: azione senza etichetta`);
    }
    /* IL DIFETTO ORIGINALE: tutte le aree con lo stesso modo, perche il modo
       veniva dallo stato del CASO. Se il motore ne dichiara piu d'uno e lo
       schermo ne mostra uno solo, la mappa e tornata a leggere il titolo. */
    const engStates = new Set(Object.values(engine).map((x) => x.ACTION_STATE));
    const uiStates = new Set((v.mDepts || []).map((x) => x.actionState));
    if (engStates.size > 1 && uiStates.size === 1) {
      bad.push(`${id}: il motore dichiara ${engStates.size} modi, lo schermo ne mostra 1`);
    }
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10) : ['stato, azione, perche e innesco per ogni reparto'] };
});

check('MG12', 'EVIDENCE_ROLE_RENDERED · ogni prova porta il suo ruolo, e l’intelligenza negativa resta', () => {
  const bad = [];
  for (const id of CASE_IDS_FOR_SCREEN) {
    const c = CASES.find((x) => x.ID === id);
    const v = caseVals(id);
    const n = (c.EVIDENCE_ROLES || []).length;
    if (!n) continue;
    if ((v.mEvidence || []).length !== n) bad.push(`${id}: prove rese ${(v.mEvidence || []).length} di ${n}`);
    for (const e of (v.mEvidence || [])) {
      if (!e.roleL) bad.push(`${id}/${e.id}: ruolo senza etichetta`);
    }
    /* §15 · WEAKENS / CONTRADICTS / CLOSES non si tolgono e non si spostano.
       In questo snapshot non compaiono; se un giorno compariranno, questo
       portone si accorgera che sono stati persi per strada. */
    const negEngine = (c.EVIDENCE_ROLES || []).filter((e) => ['WEAKENS', 'CONTRADICTS', 'CLOSES'].includes(e.ROLE)).length;
    if (negEngine !== v.mEvNegCount) bad.push(`${id}: prove negative ${v.mEvNegCount} ≠ ${negEngine}`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10) : ['ruolo reso per ogni prova; nessuna prova negativa persa'] };
});

check('MG13', 'VALIDATION_STATE_NOT_HIDDEN · un caso DA VALIDARE non puo sembrare validato', () => {
  const bad = [];
  const r = radarVals();
  const byId = {}; CASES.forEach((c) => { byId[c.ID] = c; });
  for (const card of (r.visibleCases || [])) {
    const c = byId[card.id];
    if (!c) continue;
    if (!card.mPubL) { bad.push(`${card.id}: nessuno stato di pubblicazione sulla scheda`); continue; }
    if (c.PUBLICATION_STATE === 'PUBLISHABLE' && !card.mPubOk) bad.push(`${card.id}: pubblicabile non segnalato`);
    if (c.PUBLICATION_STATE === 'VALIDATION_REQUIRED' && card.mPubOk) {
      bad.push(`${card.id}: DA VALIDARE presentato come verificato`);
    }
  }
  for (const id of CASE_IDS_FOR_SCREEN) {
    const v = caseVals(id);
    if (!v.mPubShortL) bad.push(`${id}: il dettaglio non dichiara lo stato di pubblicazione`);
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 10)
      : [`${(r.visibleCases || []).length} schede · stato di pubblicazione sempre visibile`] };
});

check('MG14', 'NO_INTERNAL_CODES · nessun codice del motore raggiunge lo schermo, in IT o in EN', () => {
  /* Un codice si riconosce dalla FORMA: MAIUSCOLE_CON_UNDERSCORE. Cercarne una
     lista sarebbe cercare quelli che gia conosciamo; la forma trova anche
     quelli che nasceranno domani. */
  const SHAPE = /\b[A-Z][A-Z0-9]{2,}(?:_[A-Z0-9]+){1,}\b/g;
  /* Sigle che sono FATTI pubblici, non codici interni: stanno in etichetta. */
  const ALLOWED = new Set(['FRAC_M', 'IRAC_3', 'NUTS_2']);
  const bad = [];
  const seen = new Set();
  const scan = (where, val) => {
    if (typeof val === 'string') {
      const m = val.match(SHAPE);
      if (m) for (const t of m) {
        if (ALLOWED.has(t) || seen.has(where + t)) continue;
        seen.add(where + t);
        bad.push(`${where}: ${t}`);
      }
    } else if (Array.isArray(val)) {
      val.forEach((x) => scan(where, x));
    } else if (val && typeof val === 'object') {
      for (const k of Object.keys(val)) {
        /* i campi tecnici non vanno a schermo: si misura cio che si rende */
        if (/^(id|department|actionState|action|whyCode|role|entityType|status|publicationState|windowType|windowRuleState|windowOpenNow|windowDefined|link|code|productId|evidenceId|matchReason|validationState|cropFit|targetFit|regulatoryFit|windowFit|regionalFit|archetype|commercialPriority|needDirection|pestStage|actionRecommendation|threshold|magnitude|signalCurrency|opportunityState|trailState|primaryMatch|primaryMatchReason|externalMaterialReady|fact|mv|m|meeting|rawDerived|whatIsMissing|whyNowCodes|whyCommercialCodes|evidence|restrictions|actives|moa|sourceUrls|url|go|raw)$/.test(k)) continue;
        scan(where, val[k]);
      }
    }
  };
  for (const lang of ['it', 'en']) {
    for (const id of CASE_IDS_FOR_SCREEN) {
      const v = caseVals(id, lang);
      /* solo i campi che la markup rende come TESTO */
      for (const k of ['mStatusL', 'mStatusWhyL', 'mPubL', 'mPubShortL', 'mWhyCommercial',
                       'mWinTypeL', 'mWinRuleL', 'mWinOpenL', 'mWinMethodL', 'mPestStageL',
                       'mActionRecL', 'mStageNote', 'mThresholdL', 'mNeedDirectionL',
                       'mExternalReadyL', 'mArchetypeL', 'mScopeL', 'mNoPrimaryReasonL',
                       'heroWinMain', 'heroWinSub', 'bandCountL']) {
        scan(`${id}/${lang}/${k}`, v[k]);
      }
      for (const arr of ['mWhyCommercialCodes', 'mWhyNow', 'mMissing', 'mBrief', 'gapRowsM']) {
        (v[arr] || []).forEach((x) => scan(`${id}/${lang}/${arr}`, x && x.text));
      }
      (v.mDepts || []).forEach((d) => {
        scan(`${id}/${lang}/dept`, d.departmentL); scan(`${id}/${lang}/dept`, d.actionStateL);
        scan(`${id}/${lang}/dept`, d.actionL); scan(`${id}/${lang}/dept`, d.whyL);
        scan(`${id}/${lang}/dept`, d.dependencyL); scan(`${id}/${lang}/dept`, d.nextTriggerL);
      });
      (v.mPortfolio || []).forEach((p) => {
        for (const k of ['cropFitL', 'targetFitL', 'regulatoryFitL', 'windowFitL',
                         'regionalFitL', 'validationStateL', 'matchReasonL']) scan(`${id}/${lang}/prod`, p[k]);
        (p.restrictions || []).forEach((x) => scan(`${id}/${lang}/prod`, x.text));
      });
      (v.mEvidence || []).forEach((e) => { scan(`${id}/${lang}/ev`, e.roleL); scan(`${id}/${lang}/ev`, e.whyL); scan(`${id}/${lang}/ev`, e.familyL); });
      (v.mChain || []).forEach((l) => { scan(`${id}/${lang}/chain`, l.linkL); scan(`${id}/${lang}/chain`, l.factL); });
    }
    const r = radarVals(lang);
    (r.visibleCases || []).forEach((c) => {
      for (const k of ['mWindowL', 'mWhyNowL', 'mWhyCommercialL', 'mPubL', 'mFirstActorL', 'statusLabel', 'linkStateL']) {
        scan(`radar/${lang}/${k}`, c[k]);
      }
    });
  }
  return { pass: bad.length === 0, expected: 0, measured: bad.length,
    detail: bad.length ? bad.slice(0, 12) : ['nessun MAIUSCOLO_CON_UNDERSCORE nel testo reso, IT ed EN'] };
});

/* ── ESECUZIONE ──────────────────────────────────────────────────────────── */

const results = CHECKS.map((c) => {
  try {
    return Object.assign({ id: c.id, title: c.title }, c.fn());
  } catch (e) {
    return { id: c.id, title: c.title, pass: false, expected: 'il portone gira',
             measured: 'HA LANCIATO', detail: [e.message, (e.stack || '').split('\n')[1]] };
  }
});

if (process.argv.includes('--json')) {
  console.log(JSON.stringify({ results, passed: results.filter((r) => r.pass).length, total: results.length }, null, 2));
  process.exit(results.every((r) => r.pass) ? 0 : 1);
}

const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
const pad = (s, n) => String(s).slice(0, n).padEnd(n);
console.log('');
console.log('  SINTONIA · I PORTONI DELLA RIUNIONE');
console.log(`  ${DIM}snapshot ${snap.SOURCE_HEAD} · build ${snap.BUILD_ID} · cutoff ${snap.MEETING_CUTOFF}${X}`);
console.log('  ' + '─'.repeat(100));
for (const r of results) {
  console.log(`  ${r.pass ? G + 'PASS' + X : R + 'FAIL' + X}  ${pad(r.id, 5)} ${pad(r.title, 74)} ${DIM}got${X} ${r.measured}`);
  if (!r.pass || process.argv.includes('--verbose')) {
    const d = Array.isArray(r.detail) ? r.detail : [r.detail];
    for (const line of d.slice(0, 12)) console.log(`        ${DIM}${String(line).slice(0, 150)}${X}`);
  }
}
const ok = results.filter((r) => r.pass).length;
console.log('  ' + '─'.repeat(100));
console.log(`  ${ok}/${results.length} passing${ok === results.length ? '' : `  ${R}${results.length - ok} failing${X}`}`);
console.log('');
process.exit(ok === results.length ? 0 : 1);
