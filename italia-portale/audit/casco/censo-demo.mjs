/* FASE 4 · INVENTARIO DELLE COLLEZIONI DEL CLIENT-DEMO
   Per ogni collezione che il pacchetto dimostrativo porta: quanti record ha,
   se il modello reale espone un equivalente, e con quale precedenza. */
import { loadData } from '../lib/harness.mjs';

const win = await loadData();
const D = win.ITALY_DEMO || {};
const M = win.ITALY_APP_MODEL || {};

const size = (v) => Array.isArray(v) ? v.length : (v && typeof v === 'object' ? Object.keys(v).length : (v === undefined ? -1 : 1));
const kind = (v) => Array.isArray(v) ? 'array' : (v && typeof v === 'object' ? 'object' : typeof v);

console.log('=== ITALY_DEMO · collezioni ===');
const dk = Object.keys(D).sort();
for (const k of dk) console.log([k, kind(D[k]), size(D[k])].join('\t'));
console.log('TOTALE_COLLEZIONI\t' + dk.length);

console.log('\n=== ITALY_APP_MODEL · chiavi di primo livello ===');
const mk = Object.keys(M).sort();
for (const k of mk) {
  const v = M[k];
  let extra = '';
  if (v && typeof v === 'object' && !Array.isArray(v)) {
    if (Array.isArray(v.items)) extra = 'items=' + v.items.length + ' prec=' + (v.precedence || '?') + ' src=' + (v.source || '?');
    else extra = 'keys=' + Object.keys(v).length;
  }
  console.log([k, kind(v), size(v), extra].join('\t'));
}
console.log('TOTALE_CHIAVI\t' + mk.length);
