/* I sette rappresentanti dimostrativi sono entrati nell'elenco reale delle persone? */
import { loadData } from '../lib/harness.mjs';
const win = await loadData();
const M = win.ITALY_APP_MODEL, D = win.ITALY_DEMO;
const tsrNames = new Set((D.TSR || []).map(t => String(t.name || t.label || '').toUpperCase().trim()).filter(Boolean));
console.log('TSR dimostrativi:', [...tsrNames].join(' | '));
const people = (M.people && M.people.records) || [];
console.log('persone nel modello:', people.length);
const cats = {};
for (const p of people) { const c = String(p.category || p.cat || p.role || '?'); cats[c] = (cats[c] || 0) + 1; }
console.log('categorie:', JSON.stringify(cats, null, 1));
const leak = people.filter(p => tsrNames.has(String(p.name || '').toUpperCase().trim()));
console.log('FUGA_TSR_IN_PERSONE =', leak.length);
if (leak.length) console.log(JSON.stringify(leak, null, 1));
const tsrCat = people.filter(p => /TECHNICAL SALES/i.test(String(p.category || p.cat || p.role || '')));
console.log('persone in categoria TECHNICAL SALES REPRESENTATIVES =', tsrCat.length);
