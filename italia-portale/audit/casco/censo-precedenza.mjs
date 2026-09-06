import { loadData } from '../lib/harness.mjs';
const win = await loadData();
const M = win.ITALY_APP_MODEL;
console.log('=== provenanceTotals ==='); console.log(JSON.stringify(M.provenanceTotals, null, 1));
console.log('\n=== provenanceSummary (collezione / record / precedenza / fonte) ===');
for (const r of M.provenanceSummary) console.log(JSON.stringify(r));
console.log('\n=== counts ==='); console.log(JSON.stringify(M.counts, null, 1));
