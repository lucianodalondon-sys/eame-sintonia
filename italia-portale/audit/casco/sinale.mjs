/* GATE · SEM_SINAL_ATUAL — la riga non puo negare un segnale che il record dichiara */
import { mount } from '../lib/harness.mjs';
const M = mount({});
const src = (M.ctx.MEETING_INTELLIGENCE.cases || M.ctx.MEETING_INTELLIGENCE.CASES || []);
const B = M.ctx.MEETING_SURFACE.build('it');
const visti = new Set(); const casi = [];
for (const k of Object.keys(B)) if (Array.isArray(B[k])) for (const c of B[k]) if (c && c.id && !visti.has(c.id)) { visti.add(c.id); casi.push(c); }

const SENZA_AZIONE = ['NO_ACTION_RECOMMENDED', 'WINDOW_CONCLUDED', 'ACTION_SUSPENDED', 'TREATMENT_PROHIBITED', 'NEUTRAL_MENTION'];
const AGIBILE = ['POSITIVE_PRESSURE'];

const classe = (r) => {
  if (r.SIGNAL_CURRENCY !== 'CURRENT') return 'NO_CURRENT_SIGNAL';
  if (SENZA_AZIONE.indexOf(r.NEED_DIRECTION) >= 0) return 'CURRENT_SIGNAL_NO_ACTION';
  if (AGIBILE.indexOf(r.NEED_DIRECTION) >= 0) return 'CURRENT_SIGNAL_ACTIONABLE';
  return 'UNKNOWN';
};

const conta = {}; let righe = 0, falsi = 0;
const dettaglio = [];
for (const lang of ['it', 'en']) for (const c of casi) {
  const v = M.vals({ view: 'mcase', mCaseId: c.id, lang });
  const r = src.find(x => (x.ID || x.id) === c.id) || {};
  for (const a of (v.mcActions || [])) {
    if (a.whyToken !== 'SEM_SINAL_ATUAL' && a.whyToken !== 'SINAL_ATUAL') continue;
    righe++;
    const k = classe(r);
    conta[k] = (conta[k] || 0) + 1;
    const nega = /Nessun segnale di campo corrente|No current field signal/.test(String(a.why));
    if (nega && r.SIGNAL_CURRENCY === 'CURRENT') { falsi++; if (dettaglio.length < 8) dettaglio.push(lang + ' ' + c.id + ' :: ' + a.why); }
  }
}
console.log('righe che parlano del segnale di campo (due lingue):', righe);
console.log('classificate:');
for (const k of ['NO_CURRENT_SIGNAL', 'CURRENT_SIGNAL_NO_ACTION', 'CURRENT_SIGNAL_ACTIONABLE', 'UNKNOWN'])
  console.log('   ' + k.padEnd(28), (conta[k] || 0) / 2, '(per lingua)');
console.log('');
console.log('SEM_SINAL_ATUAL_FALSE_STATEMENTS =', falsi);
for (const d of dettaglio) console.log('   ', d);
process.exitCode = falsi === 0 ? 0 : 1;
