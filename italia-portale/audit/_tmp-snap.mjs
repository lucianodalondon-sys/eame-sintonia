import * as H from './lib/harness.mjs';
const m = H.mount(); const AM = m.AM;
const out = {};
const C = AM.collections;
const pick = (r, fs) => fs.map((f) => JSON.stringify(r[f])).join('|');
out.counts = Object.keys(C).sort().map((k) => k + '=' + C[k].records.length);
out.totals = JSON.stringify(AM.totals);
out.windows = C.cropWindows.records.map((w) => pick(w, ['windowId', 'crop', 'issue', 'issueEn', 'labelVerdictState', 'verifiedProducts', 'notFoundProducts']) + '|reg=' + (w.regulatory ? w.regulatory.id : null));
out.opps = C.opportunities.records.map((o) => pick(o, ['id', 'crop', 'cropKeys', 'cropScope', 'issue', 'issueEn', 'issueKey', 'verifiedProductCount', 'productLinks']));
out.fieldSignals = C.currentFieldSignals.records.map((r) => pick(r, ['id', 'crop', 'cropCanonical', 'issue', 'issueEn', 'region']));
out.resistance = C.resistance.records.map((r) => pick(r, ['id', 'crop', 'cropKey', 'cropKeys', 'cropScope']));
out.future = C.futureSignals ? C.futureSignals.records.map((r) => pick(r, ['id', 'crop', 'cropKey', 'cropKeys', 'cropScope', 'issue'])) : [];
out.rels = AM.productRelationships.records.map((r) => pick(r, ['id', 'crop', 'issue', 'product', 'strength', 'windowId', 'anchor']));
out.verdicts = AM.labelVerdicts.records.map((r) => pick(r, ['id', 'crop', 'issue', 'product', 'strength']));
out.market = C.marketObservations.records.map((r) => pick(r, ['id', 'cropKey', 'seriesKey']));
out.people = C.people.records.map((p) => pick(p, ['id', 'name', 'isResearcher', 'roleCat', 'theme', 'alsoIds']));
out.searchIndexSize = AM.searchIndex.length;
out.searchTerms = AM.searchIndex.map((e) => e.id + '::' + (e.terms || []).slice().sort().join(','));
const langs = ['it', 'en'];
const SC = [['radar'], ['case', { caseId: 'IT-OPP-001' }], ['case', { caseId: 'IT-OPP-002' }], ['case', { caseId: 'IT-OPP-003' }],
  ['windows'], ['window', { windowId: 'IT-WIN-0001' }], ['window', { windowId: 'IT-WIN-0005' }],
  ['market'], ['competitors'], ['science'], ['sources'], ['person', { personId: 'IT-PER-001' }],
  ['person', { personId: 'IT-PER-013' }], ['gire'], ['news'], ['voices'], ['future'], ['archive'], ['field'], ['product', { productName: 'MAVRIK SMART' }]];
out.screens = [];
for (const l of langs) for (const [v, extra] of SC) {
  let s;
  try { s = JSON.stringify(m.vals(Object.assign({ view: v, lang: l }, extra || {})), (k, val) => (typeof val === 'function' ? '[fn]' : k === 'raw' ? undefined : val)); } catch (e) { s = 'ERR ' + e.message; }
  out.screens.push(l + '/' + v + (extra ? JSON.stringify(extra) : '') + ' :: ' + s);
}
console.log(JSON.stringify(out, null, 1));
