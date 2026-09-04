#!/usr/bin/env node
/* SINTONIA · CONTROLO DO ENXERTO — o portao esta CHAMADO, nao so escrito
   ---------------------------------------------------------------------------
   Um portao pode existir, importar-se, compilar e nao correr. `prebuild` a
   apontar para o ficheiro certo prova que alguem escreveu a linha; nao prova
   que a linha e executada, nem que executa-la muda alguma coisa.

       PROCURAR O NOME DO PORTAO ENCONTRA A DEFINICAO, NAO A CHAMADA.

   Por isso aqui nao se faz busca de texto. Faz-se cirurgia: remove-se do
   package.json APENAS o gancho que dispara o portao — o ficheiro fica, os
   imports ficam, o codigo fica — e exige-se que a build, que antes recusava um
   artefacto envenenado, passe a aceita-lo. Se aceitar, o portao era decorativo.

   E procura-se a porta das traseiras: uma variavel de ambiente que desligue o
   portao. Se existir, tem de falhar na mesma.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { CONTRATO } from './ingestion-provenance.mjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..', '..');
const PKG = path.join(RAIZ, 'package.json');
const EMBARCADO = path.join(RAIZ, 'italia-portale', 'client', 'italy-handoff-v21.js');
const STALE = JSON.parse(fs.readFileSync(path.join(AQUI, 'STALE-GENERATOR-CONTROL.json'), 'utf8'));

const R = [];
const teste = (id, fn) => { try { R.push({ id, ...fn() }); }
  catch (e) { R.push({ id, pass: false, detail: [`LANCOU: ${e.message}`] }); } };

function build(env) {
  try { execFileSync('npm', ['run', 'build'], { cwd: RAIZ, stdio: 'pipe', encoding: 'utf8',
    env: { ...process.env, ...(env || {}) } }); return 0; }
  catch (e) { return e.status ?? 1; }
}

/* Envenena o artefacto servido, corre fn, e repoe SEMPRE — inclusive se rebentar. */
function envenenado(fn) {
  const original = fs.readFileSync(EMBARCADO, 'utf8');
  const alvo = `"buildId":"${CONTRATO.EXPECTED_BUILD_ID}"`;
  if (!original.includes(alvo)) throw new Error('ancora do veneno ausente no artefacto');
  try {
    fs.writeFileSync(EMBARCADO, original.replace(alvo, `"buildId":"${STALE.BUILD_ID}"`), 'utf8');
    return fn();
  } finally { fs.writeFileSync(EMBARCADO, original, 'utf8'); }
}

/* Remove SO o gancho, mantendo ficheiro, imports e definicao. Repoe sempre. */
function semGancho(fn) {
  const original = fs.readFileSync(PKG, 'utf8');
  const j = JSON.parse(original);
  if (!j.scripts || !j.scripts.prebuild) throw new Error('nao ha gancho prebuild para remover');
  delete j.scripts.prebuild;
  try {
    fs.writeFileSync(PKG, JSON.stringify(j, null, 2) + '\n', 'utf8');
    return fn();
  } finally { fs.writeFileSync(PKG, original, 'utf8'); }
}

teste('GRAFT_ORIGINAL_REJECTS', () => {
  const r = envenenado(() => build());
  return { pass: r !== 0, detail: [`com o gancho no lugar, a build recusa o artefacto envenenado: exit ${r}`] };
});

teste('GRAFT_CALLS_PROVENANCE_GATE', () => {
  /* O ficheiro do portao continua no disco e continua importavel: o que se
     removeu foi a CHAMADA. Se a build passar a aceitar o veneno, entao era a
     chamada que segurava — e o portao esta mesmo no caminho. */
  const semChamada = semGancho(() => envenenado(() => build()));
  const ficheiroLa = fs.existsSync(path.join(AQUI, 'build-gate.mjs'));
  const comChamada = envenenado(() => build());
  return {
    pass: ficheiroLa && semChamada === 0 && comChamada !== 0,
    detail: [`portao no disco durante o teste: ${ficheiroLa}`,
             `SEM a chamada, veneno aceite: exit ${semChamada} (tem de ser 0)`,
             `COM a chamada, veneno recusado: exit ${comChamada} (tem de ser != 0)`],
  };
});

teste('ENV_BYPASS_STATUS', () => {
  /* Se alguma variavel desligar o portao, o veneno passa. Testam-se as que
     existem no codigo e os nomes que alguem tentaria por habito. */
  const suspeitas = ['SINTONIA_CADEIA_HISTORICA', 'SINTONIA_STALE_DIR', 'SKIP_GATES',
    'SKIP_PREBUILD', 'CI', 'NODE_ENV', 'VERCEL', 'VERBOSE'];
  const passaram = [];
  for (const v of suspeitas) {
    const r = envenenado(() => build({ [v]: v === 'NODE_ENV' ? 'production' : '1' }));
    if (r === 0) passaram.push(v);
  }
  return { pass: passaram.length === 0,
    detail: passaram.length ? [`estas variaveis desligam o portao: ${passaram.join(', ')}`]
      : [`${suspeitas.length} variaveis tentadas, nenhuma abre a porta`] };
});

const mau = R.filter((r) => !r.pass);
console.log('\n  SINTONIA · CONTROLO DO ENXERTO');
console.log('  ' + '─'.repeat(88));
for (const r of R) { console.log(`  ${r.pass ? 'PASS' : 'FAIL'}  ${r.id}`);
  for (const d of r.detail || []) console.log(`        ${d}`); }
console.log('  ' + '─'.repeat(88));
console.log(`  ${mau.length ? 'FAIL' : 'PASS'} — ${R.length - mau.length}/${R.length}\n`);
process.exit(mau.length ? 1 : 0);
