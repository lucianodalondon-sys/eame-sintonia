/* Executa um adapter de portal contra o snapshot real e despeja o modelo client
   em JSON, para que audit_adapter_boundary.py possa medi-lo.
   Uso: SP=<dir com snap.js labels.js surface.js> node scripts/adapter_dump.mjs */
import fs from 'node:fs';
import vm from 'node:vm';
const SP = process.env.SP;
const win = {};
const ctx = vm.createContext({ window: win, globalThis: win, console });
for (const f of ['snap.js', 'labels.js', 'surface.js']) {
  vm.runInContext(fs.readFileSync(`${SP}/${f}`, 'utf8'), ctx, { filename: f });
}
const S = win.MEETING_SURFACE;
if (!S) { console.error('MEETING_SURFACE ausente'); process.exit(2); }
console.error('snapshot carregado:', win.MEETING_INTELLIGENCE?.TOTAL_CASES, 'casos · labels:', !!win.MEETING_LABELS);
for (const lang of ['it', 'en']) {
  const m = S.build(lang);
  fs.writeFileSync(`${SP}/client_${lang}.json`, JSON.stringify(m));
  console.error(`build(${lang}): ${m.cases.length} casos · counts.ACT_NOW=${JSON.stringify(m.counts.BY_STATUS?.ACT_NOW)} · WINDOW_DEFINED=${m.counts.WINDOW_DEFINED}`);
}
