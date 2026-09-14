#!/usr/bin/env node
/* SINTONIA ITALY · OPPORTUNITY ENGINE · EVERY CASE, NOT A SAMPLE
   ---------------------------------------------------------------------------
   Audits all 37 opportunity objects straight off the transported package,
   independently of the model and of the portal, so a defect introduced by
   either cannot hide the defect underneath.

   The questions are the brief's, in the brief's order:
     · does every evidence id resolve to a real record?
     · is any red-team-rejected case renderable?
     · does a case wear an urgency status it has no right to?
     · do two cards describe one underlying situation?
     · does a case claim more than the method it declares?
     · does an UNKNOWN window become a date?

     node audit/opp-audit.mjs
   --------------------------------------------------------------------------- */
import { loadData } from './lib/harness.mjs';

const ctx = loadData({ files: ['italy-v21.js'] });
const V = ctx.ITALY_HANDOFF_V21;
if (!V) { console.error('italy-v21.js did not load'); process.exit(2); }

const O = V.collections.opportunities || [];
const ENG = V.ENGINE || {};
const REJ = new Map((ENG.REJECTIONS || []).map((r) => [r.ID, r]));

/* Every id the package publishes anywhere, so an evidence id can be resolved
   without guessing which family it belongs to. */
const universe = new Map();
for (const [fam, rows] of Object.entries(V.collections || {})) {
  for (const r of rows || []) {
    for (const k of ['ID', 'REGISTRATION_NUMBER', 'SOURCE_ID', 'ID_ANTERIOR']) {
      const v = r && r[k];
      if (typeof v === 'string' && v) if (!universe.has(v)) universe.set(v, fam);
    }
    const aliases = r && r.ID_ALIASES;
    if (Array.isArray(aliases)) for (const a of aliases) if (typeof a === 'string' && !universe.has(a)) universe.set(a, fam);
  }
}

const renderable = O.filter((o) => o.RENDERABLE_WITH_METHOD === true);
const candidates = O.filter((o) => o.RENDERABLE_WITH_METHOD !== true);

const findings = [];
const F = (sev, id, what) => findings.push({ sev, id, what });

/* ── 1 · red team ─────────────────────────────────────────────────────────── */
const rejRenderable = renderable.filter((o) => REJ.has(o.ID));
if (rejRenderable.length) rejRenderable.forEach((o) => F('P0', o.ID, 'red-team-rejected case is RENDERABLE_WITH_METHOD'));

/* ── 2 · urgency on a knocked-down case ───────────────────────────────────── */
const URGENT = new Set(['ACT_NOW']);
for (const o of O) {
  const gated = (o.BLOCKING_GATES || []).length > 0 || REJ.has(o.ID);
  if (gated && URGENT.has(o.STATUS)) {
    F('P1', o.ID, `status ${o.STATUS} on a case the red team knocked down (${(o.RED_TEAM_FINDINGS || [])[0] || 'gated'})`);
  }
}

/* ── 3 · evidence resolution ──────────────────────────────────────────────── */
let evTotal = 0;
const unresolved = [];
for (const o of O) {
  for (const e of (o.EVIDENCE_IDS || [])) {
    evTotal++;
    if (!universe.has(e)) unresolved.push({ id: o.ID, ev: e, renderable: o.RENDERABLE_WITH_METHOD === true });
  }
}
unresolved.filter((u) => u.renderable).forEach((u) => F('P1', u.id, `evidence id ${u.ev} resolves to nothing, on a RENDERED case`));

/* ── 4 · one situation, two cards ─────────────────────────────────────────── */
const byIdentity = new Map();
for (const o of renderable) {
  const k = o.IDENTITY_KEY || [o.ARCHETYPE, o.CROP, o.TARGET, o.GEOGRAPHY].join('|');
  if (!byIdentity.has(k)) byIdentity.set(k, []);
  byIdentity.get(k).push(o.ID);
}
[...byIdentity.entries()].filter(([, v]) => v.length > 1)
  .forEach(([k, v]) => F('P1', v.join(' + '), `two rendered cards share identity ${k}`));

/* ── 5 · the window ───────────────────────────────────────────────────────── */
for (const o of O) {
  if (o.WINDOW_STATE === 'UNKNOWN' && (o.WINDOW_START || o.WINDOW_END)) {
    F('P0', o.ID, 'WINDOW_STATE=UNKNOWN but a window date is present');
  }
  if (o.WINDOW_STATE !== 'UNKNOWN' && !o.WINDOW_START && !o.WINDOW_END) {
    F('P2', o.ID, `WINDOW_STATE=${o.WINDOW_STATE} with no dates to back it`);
  }
}

/* ── 6 · does the case declare the method it used? ────────────────────────── */
for (const o of renderable) {
  if (!o.WHAT_IT_DOES_NOT_PROVE_IT) F('P1', o.ID, 'rendered case with no WHAT_IT_DOES_NOT_PROVE in Italian');
  if (!o.WHY_NOW_IT) F('P1', o.ID, 'rendered case with no WHY_NOW in Italian');
  if (!o.ADAMA_RELEVANCE_IT) F('P1', o.ID, 'rendered case with no ADAMA_RELEVANCE in Italian');
  if (!(o.EVIDENCE_IDS || []).length) F('P0', o.ID, 'rendered case with no evidence at all');
}

/* ── 7 · the semantic traps the brief lists ───────────────────────────────── */
const TRAP = [
  [/quota di mercato|market share|participacao de mercado/i, 'competitor communication read as market share'],
  [/incidenza nazionale|national incidence|incidencia nacional/i, 'a field signal read as national incidence'],
  [/sell-in|sell-out|pipeline|magazzino|stock del cliente/i, 'an internal commercial fact claimed from external evidence'],
];
for (const o of O) {
  const text = [o.WHY_NOW_IT, o.ADAMA_RELEVANCE_IT, o.WHAT_IT_PROVES_IT].filter(Boolean).join(' ');
  for (const [re, why] of TRAP) if (re.test(text)) F('P0', o.ID, why);
}

/* ── report ───────────────────────────────────────────────────────────────── */
const by = (k) => O.reduce((a, o) => { const v = Array.isArray(o[k]) ? o[k].join('|') : String(o[k]); a[v] = (a[v] || 0) + 1; return a; }, {});
console.log('BUILD_ID :', V.BUILD_ID);
console.log('audited  :', O.length, 'opportunity objects — all of them, no sample');
console.log('  renderable with method :', renderable.length);
console.log('  candidates             :', candidates.length);
console.log('  red-team rejections    :', REJ.size, '· of which renderable:', rejRenderable.length);
console.log('  archetypes             :', JSON.stringify(by('ARCHETYPE')));
console.log('  statuses               :', JSON.stringify(by('STATUS')));
console.log('  evidence links         :', evTotal, '· unresolved:', unresolved.length,
  '(on rendered cases:', unresolved.filter((u) => u.renderable).length + ')');
console.log('  window UNKNOWN         :', O.filter((o) => o.WINDOW_STATE === 'UNKNOWN').length);
console.log('');
const sev = (s) => findings.filter((f) => f.sev === s);
for (const s of ['P0', 'P1', 'P2']) {
  const list = sev(s);
  console.log(`${s}: ${list.length}`);
  list.slice(0, 12).forEach((f) => console.log(`   ${f.id}  ${f.what}`));
}
if (unresolved.length) {
  console.log('\nunresolved evidence ids (first 12):');
  unresolved.slice(0, 12).forEach((u) => console.log(`   ${u.id} -> ${u.ev}${u.renderable ? '   [RENDERED]' : ''}`));
}
process.exit(sev('P0').length ? 1 : 0);
