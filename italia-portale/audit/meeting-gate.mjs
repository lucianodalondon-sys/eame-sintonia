#!/usr/bin/env node
/* SINTONIA · MEETING GATE — le testimonianze del build della riunione
   ---------------------------------------------------------------------------
   Un test che passava anche PRIMA non prova il difetto.

   Le due contraddizioni viste a schermo erano errori di PROPRIETA: due blocchi
   della stessa pagina leggevano due fonti diverse per lo stesso fatto. Per
   dimostrare che i portoni le prendono, ognuno dei quattro testimoni centrali
   viene eseguito DUE volte:

     · sulla superficie vera        → deve PASSARE
     · su una superficie LEGACY     → deve FALLIRE

   La superficie legacy non e inventata per l'occasione: riproduce esattamente
   i due meccanismi misurati nel repository —

       portale.html:2758   const primary = c.primary || (verified[0] ? ... )
       italy-canonical-windows.js   29 finestre di calendario per LEGACY_CASE_ID

   Se un testimone passa anche sulla legacy, non sta misurando niente e lo dice.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { mount, loadData, CLIENT, readPortal, extractMarkup } from './lib/harness.mjs';

const results = [];
const check = (id, title, fn) => {
  try { const r = fn(); results.push({ id, title, ...r }); }
  catch (e) { results.push({ id, title, pass: false, expected: 'runs', measured: 'THREW', detail: [e.message, (e.stack || '').split('\n')[1] || ''] }); }
};

const m = mount();
const ctx = m.ctx;
const SNAP = ctx.MEETING_INTELLIGENCE;
const SURF = ctx.MEETING_SURFACE;
const markup = extractMarkup(readPortal());
const MODEL = { it: SURF.build('it'), en: SURF.build('en') };

/* ── il modello LEGACY · i due difetti, riprodotti ───────────────────────── */
function legacyModel(lang) {
  const base = SURF.build(lang);
  const CANON = (ctx.ITALY_CANONICAL && ctx.ITALY_CANONICAL.windows) || [];
  return {
    ...base,
    cases: base.cases.map((c, i) => {
      const matches = c.products.matches;
      /* IL DIFETTO 1 · il primo elemento dell'array come ripiego */
      const primary = c.products.primary || matches[0] || null;
      /* IL DIFETTO 2 · la finestra dal calendario legacy, per posizione */
      const lw = CANON[i % CANON.length] || {};
      const legacyOpen = lw.CURRENT_STATUS === 'WINDOW_OPEN';
      return {
        ...c,
        products: {
          ...c.products, primary, hasPrimary: !!primary,
          primaryId: primary ? primary.PRODUCT_ID : null,
          /* e il riassunto che nasconde cio che si conosce gia */
          moreLabel: primary && matches.length > 1 ? `+ ${matches.length - 1} more` : '',
          shown: primary ? [primary] : [],
        },
        window: {
          ...c.window,
          OWNER: 'ITALY_CANONICAL',
          DEFINED: lw.START_DATE ? 'YES' : 'NO',
          OPEN_NOW: legacyOpen ? 'WINDOW_OPEN_NOW_YES' : 'WINDOW_OPEN_NOW_NO',
          /* IL DIFETTO 3 · una frase sola per due domande */
          ruleSentence: legacyOpen ? 'Finestra aperta' : 'Nessuna finestra canonica collegata',
          stateSentence: legacyOpen ? 'Finestra aperta' : 'Nessuna finestra canonica collegata',
        },
      };
    }),
  };
}
const LEGACY = legacyModel('it');

/* Ogni testimone centrale e una funzione pura del modello, cosi puo essere
   puntata sulla superficie vera e su quella legacy senza riscriverla. */
const W = {
  PRIMARY_MATCH_SINGLE_OWNER: (M) => {
    const bad = [];
    for (const c of M.cases) {
      const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
      const engine = raw.PRIMARY_MATCH || null;
      const shown = c.products.primaryId;
      if ((engine || null) !== (shown || null)) bad.push(`${c.id}: engine=${engine} shown=${shown}`);
    }
    return bad;
  },
  NO_PRIMARY_WHEN_UNKNOWN: (M) => {
    const bad = [];
    for (const c of M.cases) {
      const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
      if (!raw.PRIMARY_MATCH && c.products.hasPrimary) bad.push(`${c.id}: engine crowned nobody, screen crowned ${c.products.primaryId}`);
    }
    return bad;
  },
  WINDOW_SINGLE_OWNER: (M) => {
    const bad = [];
    for (const c of M.cases) {
      const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
      if (c.window.OWNER !== 'MEETING_INTELLIGENCE') { bad.push(`${c.id}: window owner is ${c.window.OWNER}`); continue; }
      if ((c.window.DEFINED || null) !== (raw.WINDOW_DEFINED || null)) bad.push(`${c.id}: DEFINED ${c.window.DEFINED} != engine ${raw.WINDOW_DEFINED}`);
      const expect = 'WINDOW_OPEN_NOW_' + (raw.WINDOW_OPEN_NOW || 'UNKNOWN');
      if (c.window.OPEN_NOW !== expect) bad.push(`${c.id}: OPEN_NOW ${c.window.OPEN_NOW} != engine ${expect}`);
    }
    return bad;
  },
  WINDOW_DEFINED_OPEN_SEPARATED: (M) => {
    const bad = [];
    for (const c of M.cases) {
      /* La regola e lo stato sono DUE domande: due frasi diverse, sempre. */
      if (c.window.ruleSentence && c.window.ruleSentence === c.window.stateSentence) bad.push(`${c.id}: one sentence answers both questions`);
      /* E il caso che il briefing nomina: regola nota, stato non misurato, non
         puo mai leggersi come "finestra aperta". */
      const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
      if (raw.WINDOW_DEFINED === 'YES' && raw.WINDOW_OPEN_NOW === 'UNKNOWN') {
        if (/aperta|open\b/i.test(c.window.stateSentence || '')) bad.push(`${c.id}: UNKNOWN reads as open — "${c.window.stateSentence}"`);
      }
    }
    return bad;
  },
};

/* ── 1 · l'istantanea ────────────────────────────────────────────────────── */
check('MEETING_SNAPSHOT_CONTRACT', 'The snapshot declares its own provenance and carries 43 cases', () => {
  const bad = [];
  for (const k of ['SOURCE_HEAD', 'BUILD_ID', 'MEETING_CUTOFF', 'TOTAL_CASES', 'CASES']) if (SNAP[k] === undefined) bad.push(`missing ${k}`);
  if (SNAP.TOTAL_CASES !== 43) bad.push(`TOTAL_CASES ${SNAP.TOTAL_CASES}`);
  if ((SNAP.CASES || []).length !== 43) bad.push(`CASES ${(SNAP.CASES || []).length}`);
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

check('SNAPSHOT_SOURCE_HEAD_VALID', 'SOURCE_HEAD names the intelligence commit, not the checkout', () => {
  const bad = [];
  if (SNAP.SOURCE_HEAD !== 'b3935bd') bad.push(`SOURCE_HEAD=${SNAP.SOURCE_HEAD}, expected the reconciled canonical head b3935bd`);
  const pkg = path.resolve(CLIENT, '..', '..', 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST', 'OPPORTUNITIES.json');
  if (fs.existsSync(pkg)) {
    const d = JSON.parse(fs.readFileSync(pkg, 'utf8'));
    if (d.BUILD_ID !== SNAP.BUILD_ID) bad.push(`BUILD_ID drift: package ${d.BUILD_ID} vs snapshot ${SNAP.BUILD_ID}`);
    if ((d.RECORDS || []).length !== 43) bad.push(`package carries ${(d.RECORDS || []).length} records`);
  } else bad.push('package not rebuilt in this tree — BUILD_ID not reconciled');
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

/* ── 2 · i 43, e nessun altro insieme ────────────────────────────────────── */
check('CANONICAL_43_RENDERED', 'All 43 canonical cases reach the canonical radar', () => {
  const v = m.vals({ view: 'meeting', lang: 'it', mShown: 999 });
  const ids = new Set(v.meetingCases.map((c) => c.id));
  const missing = SNAP.CASES.filter((c) => !ids.has(c.ID)).map((c) => c.ID);
  return { pass: !missing.length && v.meetingTotal === 43, expected: 43,
    measured: `${ids.size} rendered · total ${v.meetingTotal}`, detail: missing.slice(0, 8) };
});

check('CANONICAL_COUNTS_FROM_43_ONLY', 'Every canonical count is computed from the 43, never from D.CASES', () => {
  const bad = [];
  const c = MODEL.it.counts;
  const tally = (f) => SNAP.CASES.reduce((a, x) => { const k = f(x); if (k) a[k] = (a[k] || 0) + 1; return a; }, {});
  const st = tally((x) => x.STATUS), pub = tally((x) => x.PUBLICATION_STATE), wo = tally((x) => x.WINDOW_OPEN_NOW);
  const want = {
    TOTAL: 43, PUBLISHABLE: pub.PUBLISHABLE || 0, VALIDATION_REQUIRED: pub.VALIDATION_REQUIRED || 0,
    ACT_NOW: st.ACT_NOW || 0, VALIDATE_NOW: st.VALIDATE_NOW || 0, WATCH: st.WATCH || 0,
    TO_VALIDATE: st.TO_VALIDATE || 0, PREPARE: st.FUTURE_PREPARATION || 0,
    WINDOW_DEFINED: SNAP.CASES.filter((x) => x.WINDOW_DEFINED === 'YES').length,
    WINDOW_OPEN_NOW_YES: wo.YES || 0, WINDOW_OPEN_NOW_NO: wo.NO || 0, WINDOW_OPEN_NOW_UNKNOWN: wo.UNKNOWN || 0,
  };
  for (const k of Object.keys(want)) if (c[k] !== want[k]) bad.push(`${k}: screen ${c[k]} vs snapshot ${want[k]}`);
  /* e il numero dei 21 casi di presentazione non deve MAI comparire come totale */
  const demo = (ctx.ITALY_DEMO && ctx.ITALY_DEMO.CASES || []).length;
  if (demo && c.TOTAL === demo) bad.push(`TOTAL equals the demonstration count (${demo})`);
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

/* ── 3 · nessun bypass, nessun ricalcolo ─────────────────────────────────── */
check('NO_RAW_BYPASS', 'The canonical surface reads the snapshot and never the legacy sources', () => {
  const src = fs.readFileSync(path.join(CLIENT, 'meeting-surface.js'), 'utf8');
  const body = src.replace(/\/\*[\s\S]*?\*\//g, '');           /* i commenti spiegano, non eseguono */
  const bad = [];
  for (const forbidden of ['ITALY_CANONICAL', 'ITALY_DEMO', 'D.CASES', 'ITALY_BRIEFS']) {
    if (body.includes(forbidden)) bad.push(`meeting-surface.js reads ${forbidden}`);
  }
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

check('NO_FRONTEND_INTELLIGENCE_RECALCULATION', 'Every decided field is copied, never derived on the screen', () => {
  const bad = [];
  for (const c of MODEL.it.cases) {
    const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
    const pairs = [
      ['STATUS', c.statusCode, raw.STATUS],
      ['COMMERCIAL_PRIORITY', c.priorityCode, raw.COMMERCIAL_PRIORITY],
      ['PUBLICATION_STATE', c.publicationCode, raw.PUBLICATION_STATE],
      ['WINDOW_DEFINED', c.window.DEFINED, raw.WINDOW_DEFINED],
      ['PORTFOLIO_COUNT', c.products.count, (raw.PORTFOLIO_MATCHES || []).length],
      ['EVIDENCE_COUNT', c.evidence.count, (raw.EVIDENCE_ROLES || []).length],
      ['ACTION_COUNT', c.actions.length, Object.keys(raw.ACTION_BY_DEPARTMENT || {}).length],
    ];
    for (const [k, shown, engine] of pairs) if (shown !== engine) bad.push(`${c.id} ${k}: ${shown} != ${engine}`);
  }
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
});

/* ── 4 · i quattro testimoni centrali, con la prova che discriminano ─────── */
for (const [id, title] of [
  ['PRIMARY_MATCH_SINGLE_OWNER', 'The primary product has exactly one owner: PRIMARY_MATCH'],
  ['NO_PRIMARY_WHEN_UNKNOWN', 'No primary is invented where the engine crowned nobody'],
  ['WINDOW_SINGLE_OWNER', 'The window has exactly one owner: the canonical snapshot'],
  ['WINDOW_DEFINED_OPEN_SEPARATED', 'The rule and the state stay two questions'],
]) {
  check(id, title, () => {
    const real = W[id](MODEL.it);
    const legacy = W[id](LEGACY);
    const bad = real.slice();
    /* UN TESTIMONE CHE PASSA ANCHE SULLA LEGACY NON MISURA NIENTE. */
    if (!legacy.length) bad.push('VACUOUS: this witness also passes on the legacy implementation, so it does not prove the defect');
    return { pass: !bad.length, expected: '0 real · >0 legacy',
      measured: `real ${real.length} · legacy ${legacy.length}`, detail: bad.slice(0, 6) };
  });
}

/* ── 5 · tutto il portafoglio, e le sezioni ──────────────────────────────── */
check('ALL_PORTFOLIO_MATCHES_RENDERED', 'Every portfolio match reaches the screen — never "primary + N more"', () => {
  const bad = [];
  const v = m.vals({ view: 'mcase', lang: 'it', mCaseId: 'OPP_5F31A63F844D' });
  for (const c of MODEL.it.cases) {
    const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
    const engine = (raw.PORTFOLIO_MATCHES || []).length;
    if (c.products.matches.length !== engine) bad.push(`${c.id}: ${c.products.matches.length} of ${engine}`);
  }
  if (/\+\s*\{\{\s*\w+\.moreMatches/.test(markup) || /moreLabel/.test(markup.split('isMcase')[1] || '')) bad.push('the canonical detail binds a "+ N more" summary');
  if (v.mcProducts.length !== (SNAP.CASES.find((x) => x.ID === 'OPP_5F31A63F844D').PORTFOLIO_MATCHES || []).length) bad.push('rendered product list is shorter than the engine list');
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 8) };
});

check('WHY_COMMERCIAL_RENDERED', 'WHY COMMERCIAL comes from the engine, in the reader language', () => {
  const bad = [];
  if (!markup.includes('data-meeting-why-commercial')) bad.push('the section is not in the markup');
  for (const lang of ['it', 'en']) {
    const key = lang === 'en' ? 'WHY_COMMERCIAL_EN' : 'WHY_COMMERCIAL_IT';
    for (const c of MODEL[lang].cases) {
      const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
      const engine = (raw[key] || '').trim();
      const shown = (c.whyCommercial || '').trim();
      /* La prosa e del motore. L'unica differenza ammessa e la coda di rimando
         ai suoi campi: la frase mostrata deve essere un PREFISSO di quella del
         motore, mai una riscrittura. */
      if (!engine) { if (shown) bad.push(`${lang} ${c.id}: prose appeared where the engine wrote none`); continue; }
      const stem = shown.replace(/\.$/, '');
      if (!engine.startsWith(stem)) bad.push(`${lang} ${c.id}: the shown prose is not the engine's`);
      if (c.whyCommercialPointerRemoved && engine.length <= shown.length) bad.push(`${lang} ${c.id}: a pointer was declared removed but nothing was`);
      /* e nessuna chiave interna puo sopravvivere nella frase mostrata */
      const tok = shown.match(/\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g);
      if (tok) bad.push(`${lang} ${c.id}: internal key in rendered prose: ${tok[0]}`);
      /* cio che il rimando indicava deve restare a schermo */
      if (c.whyCommercialPointerRemoved && !c.needDirection) bad.push(`${lang} ${c.id}: the pointer was removed and its fact went with it`);
    }
  }
  /* Il motore non ha prosa su 3 dei 43. La regola non e "ci deve essere una
     frase": e "il posto non puo restare muto, e nessuno puo riempirlo".
     Dove la frase manca deve restare almeno un codice tradotto. */
  for (const c of MODEL.it.cases) {
    if (!c.whyCommercial && !c.whyCommercialCodes.length) bad.push(`${c.id}: neither prose nor a coded reason reaches the screen`);
  }
  if (!/mcWhyCommercialCodes/.test(markup)) bad.push('the coded reason has no slot in the markup');
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 6) };
});

check('WHY_NOW_RENDERED', 'WHY NOW shows the engine chain, and names the missing link', () => {
  const bad = [];
  if (!markup.includes('data-meeting-why-now')) bad.push('the section is not in the markup');
  for (const c of MODEL.it.cases) {
    const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
    const engine = Object.keys(raw.WHY_NOW_CHAIN || {}).length;
    if (c.whyNow.links.length !== engine) bad.push(`${c.id}: ${c.whyNow.links.length} links of ${engine}`);
    for (const l of c.whyNow.links) {
      const e = (raw.WHY_NOW_CHAIN || {})[l.KEY] || {};
      if (!!e.OK !== l.ok) bad.push(`${c.id} ${l.KEY}: ok ${l.ok} != engine ${!!e.OK}`);
    }
  }
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 6) };
});

check('ACTION_MAP_FROM_ENGINE', 'The action map is ACTION_BY_DEPARTMENT, not a hand-written action', () => {
  const bad = [];
  if (!markup.includes('data-meeting-action-map')) bad.push('the section is not in the markup');
  for (const c of MODEL.it.cases) {
    const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
    const by = raw.ACTION_BY_DEPARTMENT || {};
    for (const a of c.actions) {
      const e = by[a.DEPARTMENT];
      if (!e) { bad.push(`${c.id}: ${a.DEPARTMENT} is not in the engine map`); continue; }
      if (a.stateToken !== 'ACTION_STATE_' + e.ACTION_STATE) bad.push(`${c.id} ${a.DEPARTMENT}: state ${a.stateToken} != ${e.ACTION_STATE}`);
      if (a.actionToken !== 'ACTION_' + e.ACTION) bad.push(`${c.id} ${a.DEPARTMENT}: action ${a.actionToken} != ${e.ACTION}`);
    }
  }
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 6) };
});

check('EVIDENCE_ROLE_RENDERED', 'Every evidence role reaches the screen, cooling evidence included', () => {
  const bad = [];
  if (!markup.includes('data-evidence-role')) bad.push('evidence roles are not in the markup');
  if (!markup.includes('data-cooling')) bad.push('cooling intelligence has no slot in the markup');
  for (const c of MODEL.it.cases) {
    const raw = SNAP.CASES.find((x) => x.ID === c.id) || {};
    if (c.evidence.rows.length !== (raw.EVIDENCE_ROLES || []).length) bad.push(`${c.id}: ${c.evidence.rows.length} roles of ${(raw.EVIDENCE_ROLES || []).length}`);
    for (const r of c.evidence.rows) if (!r.role) bad.push(`${c.id} ${r.id}: role ${r.roleToken} has no phrase`);
  }
  const cooled = MODEL.it.cases.filter((c) => c.evidence.hasCooling);
  if (!cooled.length) bad.push('no case renders cooling intelligence — the negative reading would be invisible');
  return { pass: !bad.length, expected: 0, measured: bad.length,
    detail: bad.slice(0, 6).concat([`cases carrying cooling evidence: ${cooled.length}`]) };
});

check('VALIDATION_STATE_NOT_HIDDEN', 'VALIDATION_REQUIRED is shown, never dressed as validated', () => {
  const bad = [];
  const v = m.vals({ view: 'meeting', lang: 'it', mShown: 999 });
  const shown = v.meetingCases.filter((c) => c.publicationCode === 'VALIDATION_REQUIRED');
  if (shown.length !== 38) bad.push(`${shown.length} of 38 VALIDATION_REQUIRED cases reach the radar`);
  for (const c of shown) if (!c.publication) bad.push(`${c.id}: publication state has no phrase`);
  if (!/\{\{\s*c\.publication\s*\}\}/.test(markup)) bad.push('the card does not bind the publication state');
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 6) };
});

/* ── 6 · la frontiera, misurata in profondita ────────────────────────────── */
check('DEEP_NESTED_INTERNAL_TOKEN_FILTER', 'The boundary filters at every depth: dict → dict → list → dict → leaf', () => {
  const bad = [];
  const probe = {
    KEEP: 'visible',
    LEVEL2: {
      RAW_LEDGER: 'must not cross',
      LIST: [
        { KEEP2: 'visible', _INTERNAL: 'must not cross', DEEP: { RULE_VERSION: 'must not cross', OK: 'visible' } },
        { OPPORTUNITY_SCORE: 9.9 },
      ],
      WINDOW_CONDITION__PT_ONLY: 'prosa em portugues que nao pode atravessar',
    },
  };
  const out = SURF.clientSafe(probe, null);
  const flat = JSON.stringify(out);
  for (const f of ['RAW_LEDGER', '_INTERNAL', 'RULE_VERSION', 'OPPORTUNITY_SCORE', 'PT_ONLY', 'must not cross', 'portugues']) {
    if (flat.includes(f)) bad.push(`${f} crossed the boundary`);
  }
  if (!flat.includes('visible')) bad.push('the filter also removed legitimate content');
  /* un contenitore svuotato sparisce invece di disegnare una scatola vuota */
  if (out.LEVEL2 && out.LEVEL2.LIST && out.LEVEL2.LIST.some((x) => x && Object.keys(x).length === 0)) bad.push('an emptied container survived as an empty box');
  /* e nessun campo PT_ONLY raggiunge il modello reale */
  const real = JSON.stringify(MODEL.it.cases);
  if (real.includes('__PT_ONLY')) bad.push('a __PT_ONLY field reached the view model');
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

/* ── 7 · le lingue ───────────────────────────────────────────────────────── */
for (const lang of ['it', 'en']) {
  check(`${lang.toUpperCase()}_LABELS_COMPLETE`, `No internal code reaches the ${lang.toUpperCase()} screen without a phrase`, () => {
    const bad = [];
    const holes = new Set();
    const walk = (o) => {
      if (Array.isArray(o)) return o.forEach(walk);
      if (o && typeof o === 'object') {
        for (const k of Object.keys(o)) {
          if (/(Token|Code)$/.test(k) && o[k]) {
            const base = k.replace(/(Token|Code)$/, '');
            if (base in o && (o[base] === null || o[base] === undefined || o[base] === '')) holes.add(String(o[k]));
          }
          walk(o[k]);
        }
      }
    };
    walk(MODEL[lang].cases);
    for (const h of holes) bad.push(`no ${lang.toUpperCase()} phrase for ${h}`);
    /* i codici che il briefing nomina uno per uno */
    const MUST = ['RULE_DELEGATED_TO_FARM', 'RULE_ADMINISTRATIVE_ONLY', 'WEAKENS', 'CLOSES', 'CONTRADICTS',
      'PHENOLOGY_WINDOW', 'PREHARVEST_WINDOW', 'THRESHOLD_WINDOW', 'PEST_STAGE_WINDOW', 'WEATHER_TRIGGERED_WINDOW',
      'ACT_NOW', 'VALIDATE_NOW', 'WATCH', 'TO_VALIDATE', 'FUTURE_PREPARATION',
      'PUBLISHABLE', 'VALIDATION_REQUIRED', 'NO_ACTION', 'VALIDATE', 'PREPARE', 'ACT'];
    for (const k of MUST) if (!ctx.MEETING_LABELS.get(k, lang)) bad.push(`the brief names ${k} and ${lang.toUpperCase()} has no phrase for it`);
    return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 10) };
  });
}

/* ── 8 · le due superfici non si mescolano ───────────────────────────────── */
check('DEMO_AND_CANONICAL_SEPARATED', 'The 21 demonstration cases never enter the canonical surface', () => {
  const bad = [];
  const demoIds = new Set(((ctx.ITALY_DEMO && ctx.ITALY_DEMO.CASES) || []).map((c) => c.id));
  for (const c of MODEL.it.cases) if (demoIds.has(c.id)) bad.push(`${c.id} is a demonstration case`);
  /* e nessuna prosa dei 21 riempie un buco dei 43 */
  const flat = JSON.stringify(MODEL.it.cases);
  for (const c of ((ctx.ITALY_DEMO && ctx.ITALY_DEMO.CASES) || []).slice(0, 25)) {
    for (const f of ['happening', 'know', 'watch', 'timeline']) {
      const v = c[f];
      if (typeof v === 'string' && v.length > 30 && flat.includes(v)) bad.push(`demonstration prose (${f}) reached the canonical surface`);
    }
  }
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 6) };
});

/* ── report ──────────────────────────────────────────────────────────────── */
const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
const pad = (s, n) => String(s).slice(0, n).padEnd(n);
console.log('\n  SINTONIA · MEETING GATE · le testimonianze del build della riunione');
console.log('  ' + '─'.repeat(104));
for (const r of results) {
  console.log(`  ${r.pass ? G + 'PASS' + X : R + 'FAIL' + X}  ${pad(r.id, 38)} ${pad(r.title, 52)} ${DIM}got${X} ${r.measured}`);
  if (!r.pass) for (const d of (Array.isArray(r.detail) ? r.detail : [r.detail]).slice(0, 8)) console.log(`        ${DIM}${String(d).slice(0, 150)}${X}`);
}
const ok = results.filter((r) => r.pass).length;
console.log('  ' + '─'.repeat(104));
console.log(`  ${ok}/${results.length} passing${ok === results.length ? '' : `  ${R}${results.length - ok} failing${X}`}\n`);
if (process.argv.includes('--json')) console.log(JSON.stringify(results, null, 2));
process.exit(ok === results.length ? 0 : 1);
