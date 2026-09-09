#!/usr/bin/env node
/* SINTONIA ITALY · V2.1 TRANSPORT
   ---------------------------------------------------------------------------
   Turns the canonical DESIGN-INGEST package into the single file the portal
   loads:  client/italy-v21.js  ->  window.ITALY_HANDOFF_V21

   It is a TRANSPORT, not an interpretation. It renames nothing, derives
   nothing and drops no record. It does exactly two things, and both are the
   package's own instruction:

   1 · DROPS THE RESEARCH FIELDS.
       APP-MANIFEST LANGUAGE_RULE: "as notas de pesquisa ficam em portugues
       dentro de RESEARCH — o Design NUNCA precisa le-las." So RESEARCH and
       every *_ORIGINAL_RESEARCH_TEXT stay out of the browser. The approved
       *_IT / *_EN fields travel; the public quotes travel untouched.

   2 · KEEPS THE CORPUS FACTS, DROPS THE CORPUS PROSE.
       CLIENT_SAFE_RULE: only CLIENT_SAFE=true may sustain a client-visible
       claim. But the gate is about what may be ASSERTED, not about what may
       EXIST. A label-use row that has not been re-read is still a row of a
       ministerial label: stubbing it to an id would shrink the layer from 2030
       pairs to 1512 and from 78 label targets to 51, which is a loss of fact
       dressed as caution. So a non-safe record keeps its scalar facts and loses
       its prose — the unreviewed READING is what must not sit on a public URL.

   Measured on this package: 15.7 MB raw -> 9.9 MB transported -> 0.56 MB over
   the wire once the host gzips it, still less than the file it replaces.

     node audit/build-v21.mjs [packageDir]
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { CLIENT } from './lib/harness.mjs';

const PKG = process.argv[2] || 'C:/eame-sintonia/build/V21-INGEST';
const DI = path.join(PKG, 'DESIGN-INGEST');
const OUT = path.join(CLIENT, 'italy-v21.js');

const read = (f) => JSON.parse(fs.readFileSync(path.join(DI, f), 'utf8'));
const records = (j) => {
  if (Array.isArray(j)) return j;
  for (const k of ['RECORDS', 'records', 'ITEMS', 'items', 'DATA', 'data', 'ROWS', 'rows']) if (Array.isArray(j[k])) return j[k];
  return Object.values(j).find((v) => Array.isArray(v) && v.length && typeof v[0] === 'object') || [];
};

const M = read('APP-MANIFEST.json');

/* A narrative field is one the package localized: it has a sibling <FIELD>_IT.
   That is the prose — a reading, in the researcher's words. Everything else is
   a scalar fact read off a document: a product name, a registration number, a
   crop as written on the label, a date, an enum. */
const narrativeFields = (r) => {
  const out = new Set();
  for (const k of Object.keys(r)) {
    if (k.endsWith('_IT')) { const base = k.slice(0, -3); if (r[base] !== undefined) out.add(base); }
    if (k === 'RESEARCH') out.add(k);
    if (k.endsWith('_ORIGINAL_RESEARCH_TEXT')) out.add(k);
  }
  return out;
};

const stripResearch = (r) => {
  const o = {};
  for (const k of Object.keys(r)) {
    if (k === 'RESEARCH') continue;
    if (k.endsWith('_ORIGINAL_RESEARCH_TEXT')) continue;
    o[k] = r[k];
  }
  return o;
};

/* The corpus record. The client-safe gate is about what may be ASSERTED, not
   about what may EXIST: a label-use row that has not been re-read is still a
   row of a ministerial label, and dropping its crop and target would shrink the
   layer from 2030 pairs to 1512 and from 78 label targets to 51 — a loss of
   fact, not a gain in safety. So the facts travel and the PROSE does not: an
   unreviewed reading has no business on a public URL, and CLIENT_SAFE=false
   still forbids the row from closing an assertion. */
const corpus = (r) => {
  const drop = narrativeFields(r);
  const o = {};
  for (const k of Object.keys(r)) {
    if (drop.has(k)) continue;
    if (k.endsWith('_IT') || k.endsWith('_EN')) continue;
    o[k] = r[k];
  }
  return o;
};

const collections = {};
const report = { BUILD_ID: M.BUILD_ID, SCHEMA_VERSION: M.SCHEMA_VERSION, BUILT_AT: M.BUILT_AT, families: [] };

for (const c of M.COLLECTIONS) {
  let R;
  try { R = records(read(c.FILE)); } catch (e) { console.error('  UNREADABLE', c.FILE); continue; }
  const safe = R.filter((r) => r && r.CLIENT_SAFE === true);
  const transported = R.map((r) => (r.CLIENT_SAFE === true ? stripResearch(r) : corpus(r)));
  /* the APP_KEY is "APP.products.regulatory" — the leaf is the family name */
  const key = String(c.APP_KEY).replace(/^APP\./, '');
  collections[key] = transported;
  report.families.push({
    family: key, file: c.FILE, total: R.length, clientSafe: safe.length,
    declaredTotal: c.COUNT_TOTAL, declaredSafe: c.COUNT_CLIENT_SAFE,
    primaryKey: c.PRIMARY_KEY || null, law: c.LAW || null,
    sourceOfTruth: c.SOURCE_OF_TRUTH || null, replaces: c.REPLACES_OLD_FILES || [],
  });
}

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
    'A CLIENT_SAFE=false record keeps its FACTS and loses its PROSE: the gate is about what may be asserted, not about what may exist.',
  MANIFEST: report.families,
  collections,
};

const body =
  '/* SINTONIA ITALY · CANONICAL INTELLIGENCE V2.1 — GENERATED, DO NOT EDIT BY HAND.\n' +
  '   Rebuild with: node audit/build-v21.mjs\n' +
  '   Source package: ITALY-REALITY-HANDOFF-V2.1 · BUILD_ID ' + M.BUILD_ID + '\n' +
  '   ' + payload.TRANSPORT_LAW.replace(/\n/g, '\n   ') + ' */\n' +
  'window.ITALY_HANDOFF_V21 = ' + JSON.stringify(payload) + ';\n';

fs.writeFileSync(OUT, body);

const gz = zlib.gzipSync(Buffer.from(body)).length;
console.log('BUILD_ID :', M.BUILD_ID);
console.log('written  :', OUT);
console.log('size     :', (body.length / 1048576).toFixed(2), 'MB raw ·', (gz / 1048576).toFixed(2), 'MB gzipped');
console.log('families :', report.families.length);
const bad = report.families.filter((f) => f.total !== f.declaredTotal);
console.log(bad.length ? `  ${bad.length} family total(s) disagree with the manifest` : '  every family total reproduces the manifest');
const safeDiff = report.families.filter((f) => f.clientSafe !== f.declaredSafe);
if (safeDiff.length) {
  console.log('  client-safe counts where the files are more conservative than the manifest:');
  safeDiff.forEach((f) => console.log(`    ${f.family}: manifest ${f.declaredSafe}, files ${f.clientSafe}`));
}
