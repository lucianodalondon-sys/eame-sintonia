#!/usr/bin/env node
/* SINTONIA ITALY · V2.1 TRANSPORT
   ---------------------------------------------------------------------------
   Turns the canonical DESIGN-INGEST package into the single file the portal
   loads:  client/italy-v21.js  ->  window.ITALY_HANDOFF_V21

   It is a TRANSPORT, not an interpretation. It renames nothing, derives nothing
   and drops no record. What it decides is only WHICH WORDS may travel.

   THE GATE IS APPROVAL, NOT CLIENT_SAFE.
   -------------------------------------
   The first version of this file gated prose on CLIENT_SAFE: a record with
   CLIENT_SAFE=false kept its scalar facts and lost every localized sentence.
   The Opportunity Engine broke that rule's back. All 37 opportunities carry
   CLIENT_SAFE=false — deliberately, because the package's own law says an
   opportunity is OUR READING of third-party facts and the client-safe rule
   governs what WE produce. Under the old gate the entire engine — every
   WHY_NOW, every ADAMA_RELEVANCE, every WHAT_IT_PROVES, the labels, the action
   map — would have been stripped on the way to the browser, and the screen
   would have shown 37 empty cards with nothing failing.

   So the rule is now the one the package actually states:

     RESEARCH and *_ORIGINAL_RESEARCH_TEXT never travel.  They are the
     researcher's Portuguese notes and APP-MANIFEST says the Design never
     reads them.

     An APPROVED TRANSLATION always travels.  Approval is what makes a sentence
     showable. CLIENT_SAFE still governs what may be ASSERTED, and the model
     enforces that; it was never a language rule.

     An UNTRANSLATED sentence travels only when nothing translated it, and the
     model's narrative gate then refuses to display it.

   THE TRANSLATION MEMORY
   ----------------------
   The package ships approved *_IT / *_EN for some fields and not others, but
   the branch also ships a 1055-entry PT->IT/EN translation memory whose own law
   is "frase igual tem traducao igual, em todo arquivo, por construcao". Joining
   it resolves 21 309 of the package's 101 817 long strings — including all six
   distinct WHY_NOW sentences and all six ADAMA_RELEVANCE sentences, which §5 of
   the brief requires on screen. Using it is not translating: it is reading the
   translation the package already approved, keyed by the exact sentence.

     node audit/build-v21.mjs [packageDir]
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { CLIENT } from './lib/harness.mjs';

const PKG = process.argv[2] || 'C:/eame-sintonia/build/V21-INGEST-2';
const DI = (() => {
  const direct = path.join(PKG, 'DESIGN-INGEST');
  if (fs.existsSync(direct)) return direct;
  /* the zip unpacks one level deeper */
  for (const e of fs.readdirSync(PKG, { withFileTypes: true })) {
    if (!e.isDirectory()) continue;
    const p = path.join(PKG, e.name, 'DESIGN-INGEST');
    if (fs.existsSync(p)) return p;
  }
  throw new Error('no DESIGN-INGEST under ' + PKG);
})();
const OUT = path.join(CLIENT, 'italy-v21.js');

const read = (f) => JSON.parse(fs.readFileSync(path.join(DI, f), 'utf8'));
const readIf = (f) => { try { return read(f); } catch { return null; } };
const records = (j) => {
  if (Array.isArray(j)) return j;
  for (const k of ['RECORDS', 'records', 'ITEMS', 'items', 'DATA', 'data', 'ROWS', 'rows', 'REJEICOES']) {
    if (Array.isArray(j[k])) return j[k];
  }
  return Object.values(j).find((v) => Array.isArray(v) && v.length && typeof v[0] === 'object') || [];
};

const M = read('APP-MANIFEST.json');

/* ── the translation memory ─────────────────────────────────────────────── */
const DICT = (() => {
  const j = readIf('_TRADUCOES.json');
  const m = new Map();
  if (!j) return m;
  for (const e of (j.TRADUCOES || [])) {
    const pt = String(e.PT || '').trim();
    if (pt) m.set(pt, { it: e.IT || null, en: e.EN || null });
  }
  return m;
})();

/* Prose, not a token. A code, an id, an enum or a short label is never sent to
   the translation memory and never dropped in favour of one. */
const isProse = (v) => typeof v === 'string' && v.trim().length >= 25 && /\s/.test(v) && !/^[A-Z0-9_·\-\s]+$/.test(v);

/* A NAME IS NOT PROSE, AND MUST SURVIVE ITS OWN TRANSLATION.
   The first version of this rule dropped any original that had an approved _IT
   sibling and looked long enough to be a sentence. It therefore deleted every
   Latin binomial in RESISTANCE: "Alisma plantago-aquatica L." is 27 characters
   with a space, so it scored as prose, and because SPECIES_IT exists ("Mesolaccia
   comune, piantaggine acquatica…") the transport threw the taxonomy away on all
   34 records. The brief forbids exactly that — Latin names and taxonomic
   authorities are preserved, never translated. A translation of a name is an
   ADDITIONAL name, never a replacement.
   So a field whose job is to hold a name never loses its original, however long
   it is; and for everything else the original is only dropped when it is long
   enough to be unmistakably a sentence rather than a label. */
const NAME_FIELD = /(^|_)(SPECIES|NAME|TITLE|PRODUCT|COMPANY|CHANNEL|HANDLE|AUTHOR|AUTHORITY|CITATION|ORGANIZATION|ORGANISATION|INSTITUTION|VENUE|JOURNAL|LABEL|CROP|TARGET|ISSUE|REGION|GEOGRAPHY|HOLDER)(_|$)/;
const mayDropOriginal = (k, v) => !NAME_FIELD.test(k) && String(v).trim().length >= 60;

const NEVER_TRAVELS = (k) => k === 'RESEARCH' || k.endsWith('_ORIGINAL_RESEARCH_TEXT');

/**
 * One record, transported.
 *  · research notes dropped
 *  · approved *_IT / *_EN kept as they are
 *  · a prose field with no approved sibling looked up in the translation memory;
 *    on a hit it gains <FIELD>_IT / <FIELD>_EN and the Portuguese original is
 *    dropped, because a translated sentence has no reason to ship twice
 *  · everything else kept untouched, for the model's narrative gate to judge
 */
function transport(r, stats) {
  const out = {};
  const has = (k) => r[k] !== undefined && r[k] !== null && r[k] !== '';
  for (const k of Object.keys(r)) {
    if (NEVER_TRAVELS(k)) { stats.researchDropped++; continue; }
    const v = r[k];
    if (k.endsWith('_IT') || k.endsWith('_EN')) { out[k] = v; stats.approvedKept++; continue; }
    /* the package already approved this one: drop the untranslated original */
    if (has(k + '_IT') && isProse(v) && mayDropOriginal(k, v)) { stats.originalDropped++; continue; }
    if (isProse(v)) {
      const hit = DICT.get(String(v).trim());
      if (hit && hit.it) {
        /* the memory resolved it, but a NAME still keeps its original */
        if (!mayDropOriginal(k, v)) out[k] = v;
        out[k + '_IT'] = hit.it;
        if (hit.en) out[k + '_EN'] = hit.en;
        stats.memoryResolved++;
        continue;
      }
      stats.untranslatedKept++;
    }
    out[k] = v;
  }
  return out;
}

const collections = {};
const report = { BUILD_ID: M.BUILD_ID, SCHEMA_VERSION: M.SCHEMA_VERSION, BUILT_AT: M.BUILT_AT, families: [] };
const stats = { researchDropped: 0, approvedKept: 0, originalDropped: 0, memoryResolved: 0, untranslatedKept: 0 };

for (const c of M.COLLECTIONS) {
  let R;
  try { R = records(read(c.FILE)); } catch { console.error('  UNREADABLE', c.FILE); continue; }
  const safe = R.filter((r) => r && r.CLIENT_SAFE === true);
  const key = String(c.APP_KEY).replace(/^APP\./, '');
  collections[key] = R.map((r) => transport(r, stats));
  report.families.push({
    family: key, file: c.FILE, total: R.length, clientSafe: safe.length,
    declaredTotal: c.COUNT_TOTAL, declaredSafe: c.COUNT_CLIENT_SAFE,
    primaryKey: c.PRIMARY_KEY || null, law: c.LAW || null,
    sourceOfTruth: c.SOURCE_OF_TRUTH || null, replaces: c.REPLACES_OLD_FILES || [],
  });
}

/* ── the Opportunity Engine's own supporting files ──────────────────────────
   Not in the manifest's COLLECTIONS, but the portal cannot honestly present
   the engine without them: the rejection list is the only way to PROVE that no
   red-team-rejected case reached a client card, and the rules file is where the
   archetypes, gates and states are defined rather than guessed. */
const rejectionsRaw = readIf('OPPORTUNITY-REJECTIONS.json');
const rulesRaw = readIf('OPPORTUNITY-RULES.json');
const evidenceRaw = readIf('OPPORTUNITY-EVIDENCE.json');

const engine = {
  REJECTIONS: rejectionsRaw ? records(rejectionsRaw).map((r) => transport(r, stats)) : [],
  REJECTION_LAW: rejectionsRaw ? rejectionsRaw.LEI || null : null,
  REJECTION_TOTAL: rejectionsRaw ? rejectionsRaw.TOTAL ?? null : null,
  RULES: rulesRaw || null,
  EVIDENCE_BY_OPPORTUNITY: evidenceRaw ? evidenceRaw.POR_OPORTUNIDADE || {} : {},
  EVIDENCE_LAW: evidenceRaw ? evidenceRaw.LEI || null : null,
};

const payload = {
  BUILD_ID: M.BUILD_ID,
  SCHEMA_VERSION: M.SCHEMA_VERSION,
  BUILT_AT: M.BUILT_AT,
  REFERENCE_DATE: '2026-09-02',
  CLIENT_SAFE_RULE: M.CLIENT_SAFE_RULE,
  LANGUAGE_RULE: M.LANGUAGE_RULE,
  DOUBLE_COUNT_WARNING: M.DOUBLE_COUNT_WARNING,
  TRANSPORT_LAW:
    'RESEARCH and *_ORIGINAL_RESEARCH_TEXT are not transported: the package says the Design never reads them. ' +
    'Everything else travels. The gate on PROSE is APPROVAL, not CLIENT_SAFE: an approved *_IT/*_EN travels, an ' +
    'untranslated sentence resolved by the package translation memory travels as *_IT/*_EN and its Portuguese ' +
    'original is dropped, and a sentence nobody translated travels untouched for the model narrative gate to refuse. ' +
    'CLIENT_SAFE still governs what may be ASSERTED and is enforced in the model, not here.',
  TRANSPORT_STATS: stats,
  MANIFEST: report.families,
  ENGINE: engine,
  collections,
};

const body =
  '/* SINTONIA ITALY · CANONICAL INTELLIGENCE V2.1 — GENERATED, DO NOT EDIT BY HAND.\n' +
  '   Rebuild with: node audit/build-v21.mjs\n' +
  '   Source package: ITALY-REALITY-HANDOFF-V2.1 · BUILD_ID ' + M.BUILD_ID + '\n' +
  '   ' + payload.TRANSPORT_LAW.replace(/\. /g, '.\n   ') + ' */\n' +
  'window.ITALY_HANDOFF_V21 = ' + JSON.stringify(payload) + ';\n';

fs.writeFileSync(OUT, body);

const gz = zlib.gzipSync(Buffer.from(body)).length;
console.log('BUILD_ID :', M.BUILD_ID);
console.log('written  :', OUT);
console.log('size     :', (body.length / 1048576).toFixed(2), 'MB raw ·', (gz / 1048576).toFixed(2), 'MB gzipped');
console.log('families :', report.families.length);
console.log('words    :', JSON.stringify(stats));
console.log('engine   :', engine.REJECTIONS.length, 'rejections ·', Object.keys(engine.EVIDENCE_BY_OPPORTUNITY).length, 'evidence maps ·', engine.RULES ? 'rules present' : 'NO RULES');
const bad = report.families.filter((f) => f.total !== f.declaredTotal);
console.log(bad.length ? `  ${bad.length} family total(s) disagree with the manifest` : '  every family total reproduces the manifest');
const safeDiff = report.families.filter((f) => f.clientSafe !== f.declaredSafe);
if (safeDiff.length) {
  console.log('  client-safe counts where the files are more conservative than the manifest:');
  safeDiff.forEach((f) => console.log(`    ${f.family}: manifest ${f.declaredSafe}, files ${f.clientSafe}`));
}
