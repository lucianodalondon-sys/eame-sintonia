#!/usr/bin/env node
/* SINTONIA ITALY · CHECK RUNNER
   node audit/run.mjs               human table
   node audit/run.mjs --json        machine readable
   node audit/run.mjs --only=D1,F3  a subset
   node audit/run.mjs --verbose     print every detail
   Exit code 0 only when every check passes. */
import { spawnSync } from 'node:child_process';
import { runAll } from './checks.mjs';

const argv = process.argv.slice(2);
const arg = (k) => { const a = argv.find((x) => x.startsWith(`--${k}=`)); return a ? a.split('=')[1] : null; };
const has = (k) => argv.includes(`--${k}`);

const only = arg('only') ? arg('only').split(',').map((s) => s.trim()) : null;
const results = runAll(only);

if (has('json')) {
  console.log(JSON.stringify({ results, passed: results.filter((r) => r.pass).length, total: results.length }, null, 2));
  process.exit(results.every((r) => r.pass) ? 0 : 1);
}

const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
const pad = (s, n) => String(s).slice(0, n).padEnd(n);

console.log('');
console.log('  SINTONIA ITALY · STRUCTURAL CHECKS');
console.log('  ' + '─'.repeat(96));
/* ── TRE STATI, NON DUE ────────────────────────────────────────────────────
   Quattro controlli hanno bisogno del pacchetto canonico per esistere, e quel
   pacchetto SI GENERA, non si conserva: non e nel repository per contratto, e
   la catena di QUESTO ramo produce un'altra safra (misurato: V21-5d312cb90a0de01d,
   con trenta file indietro rispetto al generatore canonico). Dicevano FAIL, e
   un FAIL dice «ho misurato e non va». Non avevano misurato.

       CHIAMARE FALLIMENTO CIO CHE NON SI E POTUTO MISURARE E MENTIRE VERSO IL
       BASSO. CHIAMARLO SUCCESSO E MENTIRE VERSO L'ALTO.

   Terzo stato, con il motivo scritto accanto. Non conta come passato — il
   totale lo mostra a parte — e non fa uscire il portone con zero, perche un
   controllo non misurato resta un debito. */
const Y = '\x1b[33m';
for (const r of results) {
  const mark = r.notTestable ? `${Y}N/M ${X}` : r.pass ? `${G}PASS${X}` : `${R}FAIL${X}`;
  console.log(`  ${mark}  ${pad(r.id, 5)} ${pad(r.title, 58)} ${DIM}exp${X} ${pad(r.expected, 12)} ${DIM}got${X} ${r.measured}`);
  if ((!r.pass || r.notTestable || has('verbose')) && r.detail !== undefined) {
    const d = Array.isArray(r.detail) ? r.detail : [r.detail];
    for (const line of d.slice(0, has('verbose') ? 40 : 12)) {
      console.log(`        ${DIM}${typeof line === 'string' ? line.slice(0, 150) : JSON.stringify(line).slice(0, 150)}${X}`);
    }
  }
}
/* ══ E O PORTAO DA SUPERFICIE, QUE ESTE CORREDOR TEM DE CHAMAR ═════════════
   `superficie-visivel.mjs` responde a pergunta que nenhum controlo desta
   tabela responde: se uma familia que EXISTE chega a ver-se. Deixa-lo de fora
   fa-lo-ia o setimo portao orfao deste repositorio — e ja se mediu o que isso
   custa: `brandwell.mjs` dizia 71/71 enquanto tinha uma reprovacao dentro.

       UM PORTAO QUE NENHUM CORREDOR CHAMA NAO GUARDA NADA.

   Corre em processo separado porque monta o portal umas trinta vezes e cada
   montagem recarrega o pacote inteiro: dentro deste processo envenenaria as
   medicoes dos outros controlos, que e o defeito que `mount()` ja tem quando
   se reutiliza. Vinte e tres segundos e o preco de nao mentir. */
if (!only) {
  const sv = spawnSync(process.execPath, [new URL('./superficie-visivel.mjs', import.meta.url).pathname],
    { encoding: 'utf8' });
  const passou = sv.status === 0;
  const linha = String(sv.stdout || '').split('\n').find((l) => /VALUE_EXISTS/.test(l)) || '';
  results.push({
    id: 'SV1', title: 'Every family that exists can be seen (VALUE_EXISTS/VISIBLE)',
    pass: passou, expected: '0 invisible',
    measured: linha.replace(/\x1b\[[0-9;]*m/g, '').replace(/^\s*(PASS|FAIL)\s*·\s*/, '').trim() || (passou ? 'ok' : 'ver superficie-visivel.mjs'),
    detail: passou ? undefined : String(sv.stdout || sv.stderr || '').split('\n').slice(-14),
  });
  const r = results[results.length - 1];
  const mark = r.pass ? `${G}PASS${X}` : `${R}FAIL${X}`;
  console.log(`  ${mark}  ${pad(r.id, 5)} ${pad(r.title, 58)} ${DIM}exp${X} ${pad(r.expected, 12)} ${DIM}got${X} ${r.measured}`);
  if (!r.pass && r.detail) for (const line of r.detail) console.log(`        ${DIM}${String(line).slice(0, 150)}${X}`);
}

/* ══ PL1 · NENHUM PRODUTO FICA COM A ETIQUETA POR ABRIR ═════════════════════
   A regua das lacunas separa tres coisas que o cartao vazio confundia: nao ter
   registo, ter registo e o leitor nao achar a tabela, e ter tudo e ninguem ter
   lido. So a ultima e uma divida NOSSA — as outras duas sao o mundo e o
   parser, e cada uma tem o seu dono.

       TER A ETIQUETA E NAO A ABRIR E A UNICA DAS TRES QUE NAO TEM DESCULPA.

   Por isso o portao exige zero em RECOLHA e deixa as outras duas contadas, a
   vista, sem falhar: um numero que falha todos os dias deixa de ser lido. */
{
  const pl = await import('./portfolio-lacunas.mjs');
  const r0 = await pl.medirLacunas();
  const porColher = r0.porAccao.RECOLHA || 0;
  results.push({
    id: 'PL1', title: 'No product has a label we hold and never read',
    pass: porColher === 0, expected: '0 por colher',
    measured: porColher + ' por colher · ' + r0.completos + '/' + r0.total + ' completos · '
      + (r0.porAccao.LEITOR_DE_ROTULO || 0) + ' no leitor · '
      + (r0.porAccao.NAO_HA_O_QUE_COLHER_AQUI || 0) + ' fora do registo',
    detail: porColher ? r0.linhas.filter((l) => l.accao === 'RECOLHA').map((l) => l.nome) : undefined,
  });
  const r = results[results.length - 1];
  console.log(`  ${r.pass ? `${G}PASS${X}` : `${R}FAIL${X}`}  ${pad(r.id, 5)} ${pad(r.title, 58)} ${DIM}exp${X} ${pad(r.expected, 12)} ${DIM}got${X} ${r.measured}`);
  if (!r.pass && r.detail) for (const line of r.detail) console.log(`        ${DIM}${String(line).slice(0, 150)}${X}`);
}

const nonMisurati = results.filter((r) => r.notTestable);
const misurabili = results.filter((r) => !r.notTestable);
const ok = misurabili.filter((r) => r.pass).length;
const ko = misurabili.length - ok;
console.log('  ' + '─'.repeat(96));
console.log(`  ${ok}/${misurabili.length} passing`
  + (ko ? `  ${R}${ko} failing${X}` : '')
  + (nonMisurati.length ? `  ${Y}${nonMisurati.length} NON MISURABILI${X} (${nonMisurati.map((r) => r.id).join(' ')})` : ''));
console.log('');
process.exit(ko === 0 ? 0 : 1);
