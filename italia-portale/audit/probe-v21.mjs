/* Independent recount of the V2.1 package, from the files themselves.
   The brief's numbers, the manifest's declared numbers and the files must all
   agree; where they do not, the files win and the difference is named. */
import fs from 'node:fs';
import path from 'node:path';

const PKG = process.argv[2] || 'C:/eame-sintonia/build/V21-INGEST';
const DI = path.join(PKG, 'DESIGN-INGEST');

const read = (f) => JSON.parse(fs.readFileSync(path.join(DI, f), 'utf8'));
/* every collection file is either an array or wraps one; find it */
export const records = (j) => {
  if (Array.isArray(j)) return j;
  for (const k of ['RECORDS', 'records', 'ITEMS', 'items', 'DATA', 'data', 'ROWS', 'rows']) {
    if (Array.isArray(j[k])) return j[k];
  }
  const arr = Object.values(j).find((v) => Array.isArray(v) && v.length && typeof v[0] === 'object');
  return arr || [];
};

const M = read('APP-MANIFEST.json');
console.log('BUILD_ID :', M.BUILD_ID);
console.log('SCHEMA   :', M.SCHEMA_VERSION, '· built', M.BUILT_AT);
console.log('');
console.log('APP_KEY'.padEnd(34), 'FILE'.padEnd(32), 'declared'.padStart(12), 'measured'.padStart(12), ' safe decl/meas');
console.log('-'.repeat(112));

let bad = 0;
for (const c of M.COLLECTIONS) {
  let n = 'MISSING', s = '-';
  try {
    const recs = records(read(c.FILE));
    n = recs.length;
    s = recs.filter((r) => r && (r.CLIENT_SAFE === true || r.CLIENT_SAFE === 'true')).length;
  } catch (e) { n = 'UNREADABLE'; }
  const okN = String(n) === String(c.COUNT_TOTAL);
  const okS = String(s) === String(c.COUNT_CLIENT_SAFE);
  if (!okN || !okS) bad++;
  console.log(
    String(c.APP_KEY).padEnd(34),
    String(c.FILE).padEnd(32),
    String(c.COUNT_TOTAL).padStart(12),
    String(n).padStart(12) + (okN ? ' ' : '!'),
    String(c.COUNT_CLIENT_SAFE).padStart(6) + '/' + String(s).padStart(6) + (okS ? '' : ' !')
  );
}
console.log('-'.repeat(112));
console.log(bad === 0 ? 'every declared count reproduces from the files' : `${bad} collection(s) disagree with the manifest`);

/* the figures the brief names that are not a plain row count */
console.log('\n--- the derived figures the brief names ---');
const PR = records(read('PRODUCT-RELATIONSHIPS.json'));
const keysOf = (r) => Object.keys(r || {});
console.log('PRODUCT-RELATIONSHIPS record keys:', keysOf(PR[0]).join(', '));
const pick = (r, ...names) => { for (const n of names) if (r && r[n] !== undefined && r[n] !== null && r[n] !== '') return r[n]; return null; };
const crops = new Set(), targets = new Set(), euRel = [];
for (const r of PR) {
  const c = pick(r, 'CROP', 'CROP_ID', 'CROP_NAME', 'CROP_IDS');
  const t = pick(r, 'TARGET', 'TARGET_ID', 'TARGET_NAME', 'ISSUE', 'ISSUE_IDS');
  [].concat(c || []).forEach((x) => x && crops.add(String(x)));
  [].concat(t || []).forEach((x) => x && targets.add(String(x)));
  if (/\bEU\b|EUROPE/i.test(JSON.stringify(r))) euRel.push(r);
}
console.log('LABEL CROPS      brief 35   measured', crops.size);
console.log('LABEL TARGETS    brief 78   measured', targets.size);
console.log('EU RELATIONSHIPS brief 183  measured', euRel.length);
