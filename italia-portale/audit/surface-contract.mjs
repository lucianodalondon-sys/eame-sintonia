#!/usr/bin/env node
/* SINTONIA · SURFACE CONTRACT — la superficie misurata CONTRO il manifesto
   ---------------------------------------------------------------------------
   Il manifesto dell'intelligenza (`APP-MANIFEST.json`) ha smesso di ammettere
   due letture: dichiara `MEETING_SURFACE_RULE`, dice chi possiede la corsia e
   dice, campo per campo, che CLIENT_SAFE, RENDERABLE_WITH_METHOD e
   PUBLICATION_STATE NON filtrano lo schermo.

   Il portale, pero, arriva alla stessa risposta per una strada sua:

       COMMERCIAL_PRIORITY → CLIENT_STATE (meeting-surface.js)
                           → etichetta    (meeting-labels.js)  → «AGIRE ORA»

   Due strade che oggi coincidono. Domani una delle due cambia e nessuno se ne
   accorge finche non e in riunione davanti al cliente.

       DUE FONTI CHE OGGI CONCORDANO NON SONO UN CONTRATTO:
       SONO UNA COINCIDENZA CHE NESSUNO STA MISURANDO.

   Questo portone non riscrive la strada del portale — la CONFRONTA con il
   manifesto, caso per caso. Il manifesto e l'autorita; se divergono, fallisce
   qui invece che a schermo.

   I numeri attesi NON escono dal manifesto: sono il criterio approvato per
   questa ingestione. Se uscissero di la, proverebbero solo che il manifesto e
   d'accordo con se stesso.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { mount, CLIENT } from './lib/harness.mjs';

const results = [];
const check = (id, title, fn) => {
  try { const r = fn(); results.push({ id, title, ...r }); }
  catch (e) { results.push({ id, title, pass: false, expected: 'runs', measured: 'THREW', detail: [e.message, (e.stack || '').split('\n')[1] || ''] }); }
};

const ING = path.resolve(CLIENT, '..', '..', 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST');
const readJson = (f) => JSON.parse(fs.readFileSync(path.join(ING, f), 'utf8'));

const MAN = readJson('APP-MANIFEST.json');
const PKG = readJson('OPPORTUNITIES.json');
const RAW = new Map((PKG.RECORDS || []).map((r) => [r.ID, r]));

const m = mount();
const SNAP = m.ctx.MEETING_INTELLIGENCE;
const SURF = m.ctx.MEETING_SURFACE;
const MODEL = SURF.build('it');

/* Il criterio approvato per questa ingestione. */
const TOTAL = 43, COMMERCIAL = 26, SEGNALI = 17;
const LANES = { 'AGIRE ORA': 5, 'PREPARARE ORA': 8, 'DA MONITORARE': 13 };
const WITNESSES = ['OPP_169BD86DB324', 'OPP_D11664591168'];

/* ── 1 · il manifesto risponde, o il portale deve indovinare ─────────────── */
check('MANIFEST_DECLARES_THE_SURFACE', 'MEETING_SURFACE_RULE exists and names its owner', () => {
  const bad = [];
  const r = MAN.MEETING_SURFACE_RULE;
  if (!r) return { pass: false, expected: 0, measured: 1, detail: ['MEETING_SURFACE_RULE absent — the portal would have to guess'] };
  if (r.SOURCE_COLLECTION !== 'OPPORTUNITIES') bad.push(`SOURCE_COLLECTION=${r.SOURCE_COLLECTION}`);
  if (r.INCLUDE_ALL_CURRENT_CASES !== true) bad.push(`INCLUDE_ALL_CURRENT_CASES=${r.INCLUDE_ALL_CURRENT_CASES}`);
  if (r.LANE_OWNER !== 'COMMERCIAL_PRIORITY') bad.push(`LANE_OWNER=${r.LANE_OWNER}`);
  if (r.EXPECTED_TOTAL !== SNAP.TOTAL_CASES) bad.push(`EXPECTED_TOTAL=${r.EXPECTED_TOTAL} vs snapshot ${SNAP.TOTAL_CASES}`);
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

/* ── 2 · i tre campi che sembravano cancelli, e non lo sono ──────────────── */
check('NO_FIELD_IS_A_VISIBILITY_GATE', 'CLIENT_SAFE · RENDERABLE_WITH_METHOD · PUBLICATION_STATE declared non-filtering', () => {
  const bad = [];
  const r = MAN.MEETING_SURFACE_RULE || {};
  for (const f of ['CLIENT_SAFE', 'RENDERABLE_WITH_METHOD', 'PUBLICATION_STATE']) {
    if (r[`${f}_IS_VISIBILITY_GATE`] !== false) bad.push(`${f}_IS_VISIBILITY_GATE=${r[`${f}_IS_VISIBILITY_GATE`]} — absent is not declared`);
  }
  if (r.PUBLICATION_STATE_CONTROLS_EXTERNAL_DISTRIBUTION !== true) bad.push('PUBLICATION_STATE not declared as the external-distribution gate');
  if (MAN.CLIENT_SAFE_RULE && /RESEARCH_LEADS/.test(MAN.CLIENT_SAFE_RULE.LEI || '')) bad.push('the CLIENT_SAFE law sends false back to RESEARCH_LEADS');
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

/* ── 3 · nessuno sparisce, e nessuno appare due volte ────────────────────── */
check('EVERY_CASE_REACHES_THE_SURFACE', 'commercial + signals = the manifest total, with no duplicate', () => {
  const bad = [];
  const ids = [...MODEL.commercial, ...MODEL.signals].map((c) => c.id || c.ID);
  const dup = ids.filter((v, i) => ids.indexOf(v) !== i);
  if (MODEL.commercial.length !== COMMERCIAL) bad.push(`commercial ${MODEL.commercial.length}`);
  if (MODEL.signals.length !== SEGNALI) bad.push(`signals ${MODEL.signals.length}`);
  if (ids.length !== TOTAL) bad.push(`total ${ids.length}`);
  if (dup.length) bad.push(`duplicates ${dup.length}: ${dup.slice(0, 3)}`);
  for (const r of PKG.RECORDS) if (!ids.includes(r.ID)) bad.push(`case absent from the surface: ${r.ID}`);
  return { pass: !bad.length, expected: 0, measured: `${MODEL.commercial.length} + ${MODEL.signals.length} = ${ids.length} · duplicates ${dup.length}`, detail: bad.slice(0, 6) };
});

/* ── 4 · la corsia del portale e quella del manifesto, caso per caso ─────── */
check('LANE_AGREES_WITH_MANIFEST', 'the portal lane equals MEETING_SURFACE_RULE.LANES for every case', () => {
  const bad = [];
  const lanes = (MAN.MEETING_SURFACE_RULE || {}).LANES || {};
  const LB = m.ctx.MEETING_LABELS;
  const label = (code) => LB.get(code, 'it');
  const counted = {};
  for (const c of MODEL.commercial) {
    const wanted = lanes[c.priorityCode];
    const got = label(c.clientState);
    if (!wanted) { bad.push(`${c.id}: COMMERCIAL_PRIORITY=${c.priorityCode} has no lane in the manifest`); continue; }
    if (got !== wanted) bad.push(`${c.id}: portal says «${got}», manifest says «${wanted}»`);
    counted[wanted] = (counted[wanted] || 0) + 1;
  }
  /* I 17 restano fuori dalle corsie commerciali PER DECISIONE, e il manifesto
     lo dice: la loro corsia e SEGNALI. */
  for (const c of MODEL.signals) {
    const wanted = lanes[c.priorityCode];
    if (wanted !== 'SEGNALI') bad.push(`${c.id}: signal whose manifest lane is «${wanted}»`);
  }
  for (const [lane, n] of Object.entries(LANES)) if ((counted[lane] || 0) !== n) bad.push(`${lane}: ${counted[lane] || 0}, criterion ${n}`);
  return { pass: !bad.length, expected: 0, measured: JSON.stringify(counted), detail: bad.slice(0, 6) };
});

/* ── 5 · i tre campi non hanno nascosto nessuno. MISURATO, non dedotto ───── */
check('NOTHING_HIDDEN_BY_THE_THREE_FIELDS', 'no case is missing because of CLIENT_SAFE, RENDERABLE or PUBLICATION_STATE', () => {
  const bad = [];
  const onScreen = new Set([...MODEL.commercial, ...MODEL.signals].map((c) => c.id || c.ID));
  const count = { clientSafeFalse: 0, renderableFalseHidden: 0, validationRequiredHidden: 0, clientSafeFalseVisible: 0 };
  for (const r of PKG.RECORDS) {
    if (r.CLIENT_SAFE === false) {
      count.clientSafeFalse += 1;
      if (onScreen.has(r.ID)) count.clientSafeFalseVisible += 1;
      else bad.push(`${r.ID} hidden and CLIENT_SAFE=false`);
    }
    if (r.RENDERABLE_WITH_METHOD === false && !onScreen.has(r.ID)) { count.renderableFalseHidden += 1; bad.push(`${r.ID} hidden and RENDERABLE_WITH_METHOD=false`); }
    if (r.PUBLICATION_STATE === 'VALIDATION_REQUIRED' && !onScreen.has(r.ID)) { count.validationRequiredHidden += 1; bad.push(`${r.ID} hidden and VALIDATION_REQUIRED`); }
  }
  if (count.clientSafeFalseVisible !== count.clientSafeFalse) bad.push('a CLIENT_SAFE=false case did not reach the surface');
  return { pass: !bad.length, expected: 0, measured: `CLIENT_SAFE=false visible ${count.clientSafeFalseVisible}/${count.clientSafeFalse} · RENDERABLE=false hidden ${count.renderableFalseHidden} · VALIDATION_REQUIRED hidden ${count.validationRequiredHidden}`, detail: bad.slice(0, 6) };
});

/* ── 6 · RENDER != EXPORT ────────────────────────────────────────────────── */
check('RENDER_IS_NOT_EXPORT', 'the blocked-for-export cases are on the surface, and the counts hold', () => {
  const bad = [];
  const exp = MAN.EXTERNAL_EXPORT_ALLOWED || {};
  if (!Object.keys(exp).length) bad.push('EXTERNAL_EXPORT_ALLOWED absent from the manifest');
  const onScreen = new Set([...MODEL.commercial, ...MODEL.signals].map((c) => c.id || c.ID));
  let allowed = 0, blocked = 0, blockedOnScreen = 0;
  for (const r of PKG.RECORDS) {
    const rule = exp[r.PUBLICATION_STATE];
    if (rule === undefined) { bad.push(`PUBLICATION_STATE=${r.PUBLICATION_STATE} has no export rule`); continue; }
    if (/permitido/i.test(rule)) allowed += 1;
    else { blocked += 1; if (onScreen.has(r.ID)) blockedOnScreen += 1; }
  }
  if (allowed !== 5) bad.push(`export-allowed ${allowed}, criterion 5`);
  if (blocked !== 38) bad.push(`export-blocked ${blocked}, criterion 38`);
  if (blockedOnScreen !== blocked) bad.push(`${blocked - blockedOnScreen} blocked cases fell off the surface — blocking export must not empty the screen`);
  return { pass: !bad.length, expected: 0, measured: `allowed ${allowed} · blocked ${blocked} · blocked still on screen ${blockedOnScreen}`, detail: bad.slice(0, 6) };
});

/* ── 7 · i due testimoni della riunione ──────────────────────────────────── */
check('MEETING_WITNESSES_REACHABLE', 'the two witnesses stay reachable among the 17 signals', () => {
  const bad = [];
  const sig = new Set(MODEL.signals.map((c) => c.id || c.ID));
  for (const w of WITNESSES) {
    if (!RAW.has(w)) { bad.push(`${w} absent from the package`); continue; }
    if (!sig.has(w)) bad.push(`${w} is not among the ${MODEL.signals.length} signals`);
  }
  return { pass: !bad.length, expected: 0, measured: `${WITNESSES.filter((w) => sig.has(w)).length}/${WITNESSES.length} reachable`, detail: bad };
});

/* ── 8 · il pacchetto consumato e quello autorizzato ─────────────────────── */
check('INGESTION_CHECKPOINT_IS_THE_AUTHORISED_ONE', 'snapshot, package and manifest name one single build', () => {
  const bad = [];
  const ids = new Set([SNAP.BUILD_ID, PKG.BUILD_ID, MAN.BUILD_ID]);
  if (ids.size !== 1) bad.push(`build drift: snapshot ${SNAP.BUILD_ID} · package ${PKG.BUILD_ID} · manifest ${MAN.BUILD_ID}`);
  if (SNAP.SOURCE_HEAD !== '55c2674') bad.push(`SOURCE_HEAD=${SNAP.SOURCE_HEAD}, authorised 55c2674`);
  if (SNAP.BUILD_ID !== 'V21-69bf448ac934a6d9') bad.push(`BUILD_ID=${SNAP.BUILD_ID}, authorised V21-69bf448ac934a6d9`);
  return { pass: !bad.length, expected: 0, measured: `${SNAP.SOURCE_HEAD} · ${SNAP.BUILD_ID}`, detail: bad };
});

/* ── report ──────────────────────────────────────────────────────────────── */
const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
const pad = (s, n) => String(s).slice(0, n).padEnd(n);
console.log('\n  SINTONIA · SURFACE CONTRACT · la superficie misurata contro il manifesto');
console.log('  ' + '─'.repeat(112));
for (const r of results) {
  console.log(`  ${r.pass ? G + 'PASS' + X : R + 'FAIL' + X}  ${pad(r.id, 42)} ${pad(r.title, 46)} ${DIM}got${X} ${r.measured}`);
  if (!r.pass) for (const d of (Array.isArray(r.detail) ? r.detail : [r.detail]).slice(0, 8)) console.log(`        ${DIM}${String(d).slice(0, 150)}${X}`);
}
const ok = results.filter((r) => r.pass).length;
console.log('  ' + '─'.repeat(112));
console.log(`  ${ok}/${results.length} passing${ok === results.length ? '' : `  ${R}${results.length - ok} failing${X}`}\n`);
if (process.argv.includes('--json')) console.log(JSON.stringify(results, null, 2));
process.exit(ok === results.length ? 0 : 1);
