#!/usr/bin/env node
/* SINTONIA · O QUE O ECRA MOSTRA QUANDO O SNAPSHOT FALHA
   ---------------------------------------------------------------------------
   O snapshot canonico e enxertado sobre o pacote embarcado. A pergunta que
   ninguem tinha feito e a unica que importa numa reuniao:

       E SE O ENXERTO NAO ACONTECER?

   Antes desta ingestao a resposta era: o ecra caia para a safra velha e mostrava
   dezasseis AGIR AGORA que o dono canonico chama WATCH, e onze PREPARE_NOW de um
   vocabulario revogado. Silenciosamente, porque um fallback nao avisa.

   Depois desta ingestao o artefacto embarcado E o canonico. Nao ha safra velha
   para onde cair. Este ficheiro prova isso nos quatro cenarios, em vez de o
   afirmar.

       CAIR PARA DADO ANTIGO E PIOR QUE NAO ABRIR:
       O ECRA QUE NAO ABRE VE-SE. O QUE MENTE, NAO.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { CLIENT, DATA_FILES } from './lib/harness.mjs';
import { EXPECTED_BUILD_ID, REVOKED_STATES } from './ingestion-provenance.mjs';

/* Carrega os ficheiros do cliente com o snapshot adulterado de N maneiras. */
function carregar(mutar) {
  const g = { window: {}, console: { log() {}, warn() {}, error() {} },
              setTimeout, clearTimeout, setInterval, clearInterval };
  g.window.window = g.window; g.globalThis = g;
  vm.createContext(g);
  for (const f of DATA_FILES) {
    let src = fs.readFileSync(path.join(CLIENT, f), 'utf8');
    if (f === 'meeting-intelligence-snapshot.js') src = mutar(src);
    try { vm.runInContext(src, g); } catch (e) { g.__erro = `${f}: ${e.message}`; }
  }
  return g.window;
}

const conta = (rows, f) => rows.reduce((a, o) => { const v = o[f]; if (v) a[v] = (a[v] || 0) + 1; return a; }, {});

/* O que o cliente veria: a faixa da superficie, se existir, e o estado do
   pacote, que e o que qualquer vista le quando a superficie nao responde. */
function oQueOClienteVe(win) {
  const H = win.ITALY_HANDOFF_V21 || {};
  const estados = conta(H.opportunities || [], 'STATUS');
  let faixas = null, superficie = 'AUSENTE';
  try {
    if (win.MEETING_SURFACE && win.MEETING_SURFACE.build) {
      const m = win.MEETING_SURFACE.build('it');
      superficie = m ? 'RESPONDE' : 'DEVOLVE_NULO';
      if (m && m.counts) faixas = m.counts;
    }
  } catch (e) { superficie = 'LANCA: ' + e.message.slice(0, 60); }
  return { estados, superficie, faixas, buildId: H.buildId };
}

const CENARIOS = {
  SNAPSHOT_PRESENT: (s) => s,
  SNAPSHOT_MISSING: () => '/* snapshot ausente */',
  SNAPSHOT_INVALID: (s) => s.slice(0, Math.floor(s.length / 2)) + '\n/* truncado */',
  BUILD_MISMATCH: (s) => s.replace(EXPECTED_BUILD_ID, 'V21-000000000000dead'),
};

const out = [];
for (const [nome, mutar] of Object.entries(CENARIOS)) {
  const v = oQueOClienteVe(carregar(mutar));
  const revogado = REVOKED_STATES.filter((r) => v.estados[r]).map((r) => `${r}=${v.estados[r]}`);
  const actNow = v.estados.ACT_NOW || 0;
  out.push({ nome, ...v, revogado, actNow });
}

console.log('== FALHA DO SNAPSHOT: O QUE O CLIENTE VE ==\n');
let falhas = 0;
for (const r of out) {
  /* A lei: em NENHUM cenario pode aparecer estado revogado, e em nenhum pode
     aparecer um ACT_NOW que o canonico nao tenha (o canonico tem 2). */
  const ok = r.revogado.length === 0 && r.actNow <= 2;
  if (!ok) falhas++;
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${r.nome.padEnd(18)} superficie=${String(r.superficie).padEnd(14)} ACT_NOW=${r.actNow}  revogado=${r.revogado.join(',') || 'nenhum'}`);
  console.log(`        estados: ${JSON.stringify(r.estados)}`);
  if (r.faixas) console.log(`        faixas : ${JSON.stringify(r.faixas)}`);
}
console.log(`\n  ${falhas ? 'FAIL' : 'PASS'} — ${out.length - falhas}/${out.length} cenarios sem safra velha`);
process.exit(falhas ? 1 : 0);
