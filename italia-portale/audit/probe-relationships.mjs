/* One-off measurement: what does the REAL evidence support for product
   relationships, compared with what the demo fixture currently asserts? */
import { loadData } from './lib/harness.mjs';

const w = loadData();
const { ITALY_LABEL_VERDICTS: LV, ITALY_DEMO: D, ITALY_INGEST: IG } = w;
const U = (s) => String(s || '').trim().toUpperCase();

console.log('IG.LINKS crops     :', [...new Set(IG.LINKS.map((l) => l.crop))].join(' · '));
console.log('IG.LINKS cropTerm  :', [...new Set(IG.LINKS.map((l) => l.cropTerm))].join(' · '));
console.log('DEMO case crops    :', [...new Set(D.CASES.map((c) => c.crop))].join(' · '));

const V = new Set(LV.VERIFIED.map((x) => [U(x[0]), U(x[1]), U(x[2])].join('|')));
const NF = new Set(LV.NOT_FOUND.map((x) => [U(x[0]), U(x[1]), U(x[2])].join('|')));
const linkPair = new Set(IG.LINKS.map((l) => U(l.crop) + '|' + U(l.product)));
const linkProd = new Set(IG.LINKS.map((l) => U(l.product)));

let unaudited = 0, corrobCrop = 0, corrobProd = 0, none = 0;
const orphans = [];
for (const c of D.CASES) {
  for (const l of c.productLinks || []) {
    const k = U(c.crop) + '|' + U(c.issue) + '|' + U(l.name);
    if (V.has(k) || NF.has(k)) continue;
    unaudited++;
    const cropKeys = [U(c.crop), U(c.crop).replace(/\s+/g, '')];
    if (cropKeys.some((ck) => linkPair.has(ck + '|' + U(l.name)))) corrobCrop++;
    else if (linkProd.has(U(l.name))) corrobProd++;
    else { none++; orphans.push(`${c.crop} · ${c.issue} · ${l.name}`); }
  }
}
console.log('\nunaudited demo links            :', unaudited);
console.log('  corroborated crop+product     :', corrobCrop);
console.log('  product in registry, other crop:', corrobProd);
console.log('  product absent from registry   :', none);
console.log('  sample orphans:', orphans.slice(0, 8).join(' | '));

const pt = /NAO SEI|NÃO SEI|nao foi extraida|não foi|coluna de|epoca do rotulo|rótulo|dados|leitura/i;
const ptRows = IG.LINKS.filter((l) => pt.test(String(l.timing)));
console.log('\nIG.LINKS timing that is a Portuguese research note:', ptRows.length, '/', IG.LINKS.length);
console.log('distinct timing values:');
[...new Set(IG.LINKS.map((l) => String(l.timing)))].slice(0, 8).forEach((t) => console.log('   ', t.slice(0, 110)));
console.log('distinct evidence values:');
[...new Set(IG.LINKS.map((l) => String(l.evidence)))].slice(0, 8).forEach((t) => console.log('   ', t.slice(0, 110)));

/* Portuguese leakage across every collection that reaches a screen. */
console.log('\n--- Portuguese research prose reaching client-facing fields ---');
const PT = /\b(nao|não|foi|pelo|pela|está|esta\b|dados|leitura|rotulo|rótulo|nenhum|apenas|porque|sobre a|entao|então|encontrad|revogad|verificad)\b/i;
const scan = (name, arr, fields) => {
  let n = 0; const ex = [];
  for (const r of arr || []) for (const f of fields) {
    const v = r[f];
    if (typeof v === 'string' && PT.test(v) && v.length > 25) { n++; if (ex.length < 2) ex.push(`${f}: ${v.slice(0, 100)}`); }
  }
  if (n) console.log(`  ${name}: ${n} field values`, ex.map((e) => '\n      ' + e).join(''));
};
scan('IG.LINKS', IG.LINKS, ['timing', 'evidence']);
scan('IG.VOICES', IG.VOICES, ['WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE', 'DATE_NOTE', 'ROLE']);
scan('IG.NEWS', IG.NEWS, ['SINTONIA_SUMMARY', 'CAVEAT', 'CONTENT_KIND_MEANING']);
scan('IG.EVENTS', IG.EVENTS, ['NOTE', 'PARTICIPATION_LAW', 'EXHIBITOR_LIST_STATE', 'TIME_STATE']);
scan('IG.SOURCES', IG.SOURCES, ['LIMITATIONS', 'ACCESS_STATUS', 'ROLE']);
scan('IG.OPPORTUNITIES', IG.OPPORTUNITIES, ['WHAT_IS_HAPPENING', 'WHY_IT_MATTERS', 'CURRENT_EVIDENCE', 'WHAT_WE_KNOW', 'WHAT_WE_DO_NOT_KNOW', 'INTERPRETATIONS', 'MARKET_CONTEXT', 'COMPETITOR_CONTEXT', 'SCIENCE_CONTEXT', 'FIELD_VOICES']);
scan('IG.FUTURE_SIGNALS', IG.FUTURE_SIGNALS, ['WHY_WATCH', 'HOW_SINTONIA_GOT_HERE', 'OBSERVED_FACTS', 'SINTONIA_INTERPRETATION', 'UNKNOWN', 'NEXT_WINDOW', 'PORTFOLIO_CONNECTION', 'WHAT_WOULD_MAKE_IT_AN_OPPORTUNITY', 'WHO_IS_TALKING', 'WHAT_CHANGED']);
scan('IG.CROP_WINDOWS', IG.CROP_WINDOWS, ['EXPECTED_CYCLE', 'OBSERVED_STAGE', 'FIELD_REPORTED_STAGE', 'REGULATORY_WINDOW', 'ADAMA_PRODUCTS_NOTE', 'COVERAGE_STATE', 'NEXT_IMPORTANT_WINDOW', 'PREPARATION_WINDOW']);
scan('IG.RESISTANCE', IG.RESISTANCE, ['MECHANISM', 'CITATION', 'AUTHORITY']);
scan('CANONICAL.windows', w.ITALY_CANONICAL.windows, ['STATUS_REASON', 'CROP_STAGE', 'ISSUE_STAGE', 'LABEL_TRIGGER', 'REGULATORY_TIMING']);
