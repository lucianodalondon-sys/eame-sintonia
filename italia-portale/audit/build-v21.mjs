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

   2 · CARRIES THE CORPUS AS A STUB.
       CLIENT_SAFE_RULE: only CLIENT_SAFE=true may sustain a client-visible
       claim. A CLIENT_SAFE=false record still has to be COUNTED — the
       transparency panel must be able to say how large the corpus is — but its
       unreviewed prose has no business on a public URL. So a non-safe record
       travels as its identity and its QA state, and nothing else.

   Measured on this package: 15.7 MB raw -> 7.3 MB transported -> 0.46 MB over
   the wire once the host gzips it, which is less than the file it replaces.

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

/* the identity every record carries, kept even for the corpus so it can be counted */
const STUB_FIELDS = ['ID', 'ENTITY_TYPE', 'QA_STATUS', 'CLIENT_SAFE', 'PROVENANCE', 'ORIGIN_LAYER', 'CLAIM_DOMAIN'];

const stripResearch = (r) => {
  const o = {};
  for (const k of Object.keys(r)) {
    if (k === 'RESEARCH') continue;
    if (k.endsWith('_ORIGINAL_RESEARCH_TEXT')) continue;
    o[k] = r[k];
  }
  return o;
};
const stub = (r) => {
  const o = {};
  for (const k of STUB_FIELDS) if (r[k] !== undefined) o[k] = r[k];
  return o;
};

const collections = {};
const report = { BUILD_ID: M.BUILD_ID, SCHEMA_VERSION: M.SCHEMA_VERSION, BUILT_AT: M.BUILT_AT, families: [] };

for (const c of M.COLLECTIONS) {
  let R;
  try { R = records(read(c.FILE)); } catch (e) { console.error('  UNREADABLE', c.FILE); continue; }
  const safe = R.filter((r) => r && r.CLIENT_SAFE === true);
  const transported = R.map((r) => (r.CLIENT_SAFE === true ? stripResearch(r) : stub(r)));
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
    'A CLIENT_SAFE=false record travels as identity + QA state only, so it can be counted without putting unreviewed prose on a public URL.',
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
