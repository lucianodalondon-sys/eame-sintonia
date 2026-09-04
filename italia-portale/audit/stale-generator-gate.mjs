#!/usr/bin/env node
/* SINTONIA · O PORTAO CONTRA A SAFRA VELHA — provado, nao declarado
   ---------------------------------------------------------------------------
   A Linha B guarda uma cadeia que ainda sabe gerar, e o que ela gera e a doenca
   que ja foi curada: V21-5d312cb90a0de01d, sem MEETING_SURFACE_RULE, com
   PREPARE_NOW de volta em onze casos.

   O detalhe que obriga este ficheiro a existir: AS DUAS SAFRAS TEM 43 CASOS.
   Um portao que contasse casos diria que esta tudo bem.

       O CONTROLO NEGATIVO NAO E UM LUXO DO TESTE. E O TESTE.

   Aqui nao se descreve o comportamento do portao: corre-se a build de verdade,
   com o artefacto envenenado no lugar do bom, e exige-se que ela falhe. Um
   portao que nunca viu o caso mau nao foi verificado — foi acreditado.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { recusas, CONTRATO } from './ingestion-provenance.mjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..', '..');
const EMBARCADO = path.join(RAIZ, 'italia-portale', 'client', 'italy-handoff-v21.js');
const STALE = JSON.parse(fs.readFileSync(path.join(AQUI, 'STALE-GENERATOR-CONTROL.json'), 'utf8'));

const R = [];
const teste = (id, fn) => {
  try { const r = fn(); R.push({ id, ...r }); }
  catch (e) { R.push({ id, pass: false, detail: [`LANCOU: ${e.message}`] }); }
};

/* Corre `npm run build` e devolve o codigo de saida. Nao mascara nada. */
function build() {
  try {
    execFileSync('npm', ['run', 'build'], { cwd: RAIZ, stdio: 'pipe', encoding: 'utf8' });
    return 0;
  } catch (e) { return e.status ?? 1; }
}

/* Troca o artefacto servido por um envenenado, corre a build, e repoe SEMPRE —
   inclusive se algo explodir no meio. Um teste que deixa o repositorio pior do
   que o encontrou nao e um teste: e um acidente com relatorio. */
function comArtefactoEnvenenado(mut, fn) {
  const original = fs.readFileSync(EMBARCADO, 'utf8');
  try {
    fs.writeFileSync(EMBARCADO, mut(original), 'utf8');
    return fn();
  } finally {
    fs.writeFileSync(EMBARCADO, original, 'utf8');
  }
}

/* ── 1 · a saida real do gerador atrasado e recusada ─────────────────────── */
teste('STALE_LINE_B_GENERATOR_OUTPUT_REJECTED', () => {
  const r = recusas({
    buildId: STALE.BUILD_ID,
    cases: STALE.CASES,
    surfaceRule: STALE.MEETING_SURFACE_RULE_PRESENTE ? {} : null,
    states: STALE.STATES,
  });
  return {
    pass: r.length > 0,
    detail: [`medido no pacote real da cadeia local: ${r.join(' · ')}`,
             `nota: ${STALE.CASES} casos, os mesmos do canonico — contar casos nao chegava`],
  };
});

/* ── 2 · o pacote canonico continua a passar ─────────────────────────────── */
teste('CANONICAL_55C2674_OUTPUT_ACCEPTED', () => {
  const r = recusas({
    buildId: CONTRATO.EXPECTED_BUILD_ID,
    cases: CONTRATO.EXPECTED_CASES,
    surfaceRule: Object.fromEntries(CONTRATO.SURFACE_RULE_FIELDS.map((f) => [f, true])),
    states: CONTRATO.CANONICAL_STATES,
  });
  return { pass: r.length === 0, detail: r.length ? r : ['zero recusas — o portao nao e apenas restritivo'] };
});

/* ── 3 · cada sinal sozinho basta para recusar ───────────────────────────── */
const canonico = () => ({
  buildId: CONTRATO.EXPECTED_BUILD_ID,
  cases: CONTRATO.EXPECTED_CASES,
  surfaceRule: Object.fromEntries(CONTRATO.SURFACE_RULE_FIELDS.map((f) => [f, true])),
  states: { ...CONTRATO.CANONICAL_STATES },
});

teste('PREPARE_NOW_REJECTED', () => {
  const p = canonico();
  p.states.PREPARE_NOW = 11;
  const r = recusas(p);
  return { pass: r.some((x) => x.includes('PREPARE_NOW')), detail: r };
});

teste('MEETING_SURFACE_RULE_REQUIRED', () => {
  const p = canonico(); p.surfaceRule = null;
  const r = recusas(p);
  return { pass: r.some((x) => x.includes('MEETING_SURFACE_RULE')), detail: r };
});

teste('BUILD_ID_REQUIRED', () => {
  const semId = recusas({ ...canonico(), buildId: undefined });
  const outroId = recusas({ ...canonico(), buildId: STALE.BUILD_ID });
  return {
    pass: semId.some((x) => x.includes('BUILD_ID')) && outroId.some((x) => x.includes('BUILD_ID')),
    detail: [`ausente: ${semId.join(' · ')}`, `errado: ${outroId.join(' · ')}`],
  };
});

/* ── 4 · o portao esta NO CAMINHO, e fecha ───────────────────────────────── */
teste('PROVENANCE_GATE_RUNS_ON_STANDARD_BUILD', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(RAIZ, 'package.json'), 'utf8'));
  const pre = pkg.scripts?.prebuild || '';
  const declarado = pre.includes('build-gate.mjs');
  /* Declarar nao chega: envenena-se o artefacto e exige-se que a build recuse.

     O primeiro veneno desta suite era falso e o portao apanhou-o: `replace` com
     texto troca so a PRIMEIRA ocorrencia, e a primeira ocorrencia do BUILD_ID
     neste ficheiro esta no comentario do cabecalho. O artefacto continuava
     canonico, a build passava, e o teste dizia FAIL do portao — quando o errado
     era o teste. Por isso agora envenena-se o CAMPO, com ancora, e confirma-se
     que o veneno pegou antes de julgar o portao.

         UM TESTE QUE NAO VERIFICA O PROPRIO VENENO MEDE-SE A SI MESMO. */
  const venenos = [
    ['BUILD_ID de safra velha', (s) => s.replace(`"buildId":"${CONTRATO.EXPECTED_BUILD_ID}"`, `"buildId":"${STALE.BUILD_ID}"`)],
    ['estado revogado PREPARE_NOW', (s) => s.replace('"STATUS":"WATCH"', '"STATUS":"PREPARE_NOW"')],
  ];
  const linhas = [`prebuild declara o portao: ${declarado}`];
  let todosFecharam = true;
  for (const [nome, mut] of venenos) {
    const r = comArtefactoEnvenenado((s) => {
      const out = mut(s);
      if (out === s) throw new Error(`o veneno "${nome}" nao pegou — ancora nao encontrada no artefacto`);
      return out;
    }, () => build());
    if (r === 0) todosFecharam = false;
    linhas.push(`build com ${nome}: exit ${r} (tem de ser != 0)`);
  }
  const limpa = build();
  if (limpa !== 0) todosFecharam = false;
  linhas.push(`build com o artefacto reposto: exit ${limpa} (tem de ser 0)`);
  return { pass: declarado && todosFecharam, detail: linhas };
});

teste('PROVENANCE_GATE_RUNS_BEFORE_PREVIEW', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(RAIZ, 'package.json'), 'utf8'));
  const vercel = JSON.parse(fs.readFileSync(path.join(RAIZ, 'vercel.json'), 'utf8'));
  const mau = [];
  /* A Vercel corre `npm run build` no preview e na producao; o npm corre
     `prebuild` antes. O que quebraria isto e um buildCommand proprio que
     saltasse o npm — por isso o que se verifica e a AUSENCIA desse desvio. */
  if (vercel.buildCommand && !/npm run build/.test(vercel.buildCommand)) {
    mau.push(`vercel.json desvia a build: ${vercel.buildCommand}`);
  }
  const prev = pkg.scripts?.preview;
  if (prev && !/npm run build|build-gate/.test(prev)) mau.push(`script preview nao passa pelo portao: ${prev}`);
  if (!pkg.scripts?.prebuild?.includes('build-gate.mjs')) mau.push('prebuild nao invoca o portao');
  return {
    pass: mau.length === 0,
    detail: mau.length ? mau : ['preview e producao partilham `npm run build`, e o npm corre `prebuild` antes de ambas'],
  };
});

/* ── 5 · o ENXERTO chama mesmo o portao ──────────────────────────────────── */
/* Os quatro testes acima provam que a REGRA recusa. Nenhum deles prova que
   alguem a CHAMA. Medido em 2026-09-04 contra este mesmo HEAD: apaguei a linha
   da chamada em `site_v21_ingest.py`, deixando definicao, imports e o resto
   intactos, e os cinco portoes desta casa ficaram verdes.

       UMA LEI QUE NINGUEM INVOCA E UM COMENTARIO COM SINTAXE.

   E o detector NAO pode ser `indexOf('recusas_de_proveniencia(')`: essa sequencia
   esta dentro da propria DEFINICAO, `def recusas_de_proveniencia(...)`. Um teste
   escrito assim mede que a funcao existe, nao que ela corre — e foi exatamente
   nessa pedra que a primeira versao desta prova tropecou.

       CASAR A DEFINICAO EM VEZ DA CHAMADA E CONFERIR A CHAVE
       CONTRA A FOTOGRAFIA DA CHAVE.

   A chamada e uma ATRIBUICAO: `<alvos> = recusas_de_proveniencia(...)`. `def`
   nunca satisfaz isso, porque `def` nao tem `=` antes do nome. */
const ENXERTO = path.join(RAIZ, 'scripts', 'site_v21_ingest.py');

/* Uma linha executavel que ATRIBUI o resultado da funcao. Nao casa `def`. */
const RE_CHAMADA = /^[ \t]*[A-Za-z_][\w, ]*=\s*recusas_de_proveniencia\s*\(/m;
const RE_DEFINICAO = /^[ \t]*def\s+recusas_de_proveniencia\s*\(/m;
/* Escapes que transformariam o portao em sugestao. */
const RE_ESCAPE = /(SKIP|FORCE|IGNORE|BYPASS|DISABLE)[A-Z_]*_?(PROVEN|INGEST|GATE|CHECK)|(PROVEN|INGEST|GATE)[A-Z_]*_?(SKIP|FORCE|IGNORE|BYPASS|DISABLE)/;

function diagnostico(src) {
  const mChamada = RE_CHAMADA.exec(src);
  const iEscrita = src.indexOf('io.open(OUT');
  const mau = [];
  if (!RE_DEFINICAO.test(src)) mau.push('a funcao de proveniencia nem esta definida');
  if (!mChamada) mau.push('o portao NAO e chamado em nenhuma linha executavel (so definido)');
  else if (iEscrita >= 0 && mChamada.index > iEscrita) mau.push('o portao e chamado DEPOIS de escrever o artefacto');
  return mau;
}

teste('GRAFT_CALLS_PROVENANCE_GATE', () => {
  const src = fs.readFileSync(ENXERTO, 'utf8');
  const intacta = diagnostico(src);

  /* CONTROLE NEGATIVO, em memoria: tira-se SO a linha da chamada. Se o detector
     continuar a dizer que esta tudo bem, o detector e que nao serve. O ficheiro
     no disco nao e tocado — um teste que deixa o repositorio pior que o
     encontrou nao e um teste, e um acidente com relatorio. */
  const mutada = src.replace(RE_CHAMADA, '    _recusas, _C = ([], {})  # ');
  const venenoPegou = !RE_CHAMADA.test(mutada) && RE_DEFINICAO.test(mutada);
  const detectouMutacao = diagnostico(mutada).length > 0;

  const mau = [...intacta];
  if (!venenoPegou) mau.push('CONTROLE NEGATIVO INVALIDO: a mutacao nao removeu a chamada (ou removeu a definicao junto)');
  else if (!detectouMutacao) mau.push('CONTROLE NEGATIVO FALHOU: com a chamada removida o detector continuou verde');
  return {
    pass: mau.length === 0,
    detail: mau.length ? mau : [
      `chamada encontrada como atribuicao, antes de escrever o artefacto`,
      `controle negativo: remover so a chamada torna este teste vermelho`,
      `a definicao sobrevive a mutacao — nao e ela que esta a ser medida`,
    ],
  };
});

teste('PROVENANCE_CANNOT_BE_SKIPPED_BY_ENV', () => {
  const src = fs.readFileSync(ENXERTO, 'utf8');
  const mau = [];

  /* 1 · nenhuma variavel de escape existe HOJE. Nao se inventa bypass que o
     codigo nao tem: procura-se o padrao, e ele nao pode aparecer. */
  const achado = RE_ESCAPE.exec(src);
  if (achado) mau.push(`ha um escape por ambiente no enxerto: ${achado[0]}`);

  /* 2 · e se alguem introduzir um, isto fica vermelho. */
  const comEscape = src.replace(RE_CHAMADA, (m) => `    if os.environ.get('SKIP_PROVENANCE'): return 0\n${m}`);
  const venenoPegou = RE_ESCAPE.test(comEscape);
  if (!venenoPegou) mau.push('CONTROLE NEGATIVO INVALIDO: o escape injetado nao foi reconhecido pelo padrao');

  return {
    pass: mau.length === 0,
    detail: mau.length ? mau : [
      'nenhuma variavel de ambiente salta o portao no codigo de hoje',
      'controle negativo: introduzir SKIP_PROVENANCE torna este teste vermelho',
    ],
  };
});

/* ── relatorio ───────────────────────────────────────────────────────────── */
const mau = R.filter((r) => !r.pass);
console.log('\n  SINTONIA · PORTAO CONTRA A SAFRA VELHA');
console.log('  ' + '─'.repeat(88));
for (const r of R) {
  console.log(`  ${r.pass ? 'PASS' : 'FAIL'}  ${r.id}`);
  for (const d of r.detail || []) console.log(`        ${d}`);
}
console.log('  ' + '─'.repeat(88));
console.log(`  ${mau.length ? 'FAIL' : 'PASS'} — ${R.length - mau.length}/${R.length}\n`);
process.exit(mau.length ? 1 : 0);
