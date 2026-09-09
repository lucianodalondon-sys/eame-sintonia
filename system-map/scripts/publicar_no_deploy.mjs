#!/usr/bin/env node
/* SINTONIA SYSTEM MAP — O QUE A BUILD SABE E O FICHEIRO NAO PODE ADIVINHAR
   ---------------------------------------------------------------------------
   O DEFEITO QUE ISTO FECHA, com nome e numero.

   O mapa era gerado, o ficheiro era commitado, e o commit mudava o HEAD. Logo o
   ficheiro nascia SEMPRE a apontar para o commit ANTERIOR:

       commit 8e1947d2  ->  state.PROVENANCE.HEAD = c293be65
       commit c293be65  ->  state.PROVENANCE.HEAD = 44e2de1b
       commit 44e2de1b  ->  state.PROVENANCE.HEAD = 2af57a41

   Oito commits seguidos medidos, oito vezes o mesmo desencontro. Nenhuma
   quantidade de disciplina conserta isto: e impossivel escrever dentro de um
   ficheiro o SHA do commit que ainda nao existe porque esse ficheiro ainda nao
   entrou nele.

       O COMMIT IMPLANTADO NASCE NO BUILD, NUNCA NUM FICHEIRO COMMITADO.

   Este script corre DURANTE a build, onde a resposta existe: a Vercel sabe que
   commit esta a implantar, e diz. Ele faz cinco coisas, nesta ordem:

     1. mede o que existe no contentor (Python? git? arvore?);
     2. REGENERA o mapa pela cadeia que ja existe — a mesma do CI, lida de
        `CADEIA-DO-MAPA.json`, nunca uma segunda copia dela;
     3. corre o validador que ja existe, e guarda o veredito;
     4. copia/publica (o gerador ja faz isso, em `construir()`);
     5. escreve `deployment.generated.json` com o commit REALMENTE implantado.

   O QUE ELE NAO FAZ, DE PROPOSITO
   -------------------------------
   · NAO reimplementa nenhum scanner. Duas implementacoes do mesmo scanner sao
     proibidas: seriam duas arquiteturas com o mesmo nome.
   · NAO derruba a build quando o mapa falha. O portal inteiro nao pode cair por
     causa da tela de auditoria; em vez disso o artefato diz FAIL, e a tela pinta
     SYSTEM MAP INVALID a vermelho. Reprovar e o trabalho do CI.
   · NAO escreve segredo nenhum. So um conjunto FECHADO de variaveis publicas e
     lido, uma a uma pelo nome. Nao ha `process.env` inteiro a ser serializado, e
     por isso nenhum token pode viajar aqui por distraccao.

       O ARTEFATO E PUBLICO. TUDO O QUE ENTRA NELE E PUBLICO.
   --------------------------------------------------------------------------- */
'use strict';

import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = resolve(AQUI, '..', '..');
const CADEIA = JSON.parse(readFileSync(join(AQUI, 'CADEIA-DO-MAPA.json'), 'utf8'));
const SERVIDO = join(RAIZ, 'italia-portale', 'client', 'system-map');
const ESTADO = join(SERVIDO, 'state.generated.json');
const ARTEFATO = join(SERVIDO, CADEIA.ARTEFATO_DE_DEPLOY);

const SHA40 = /^[0-9a-f]{40}$/;

/* AS VARIAVEIS LIDAS, UMA A UMA, PELO NOME.
   Nada aqui e secreto: o SHA, o ref e o ID da build aparecem no proprio commit
   publico e no URL do deployment. `VERCEL_URL` e o hostname que o browser ja
   conhece — ele esta na barra de endereco de quem esta a ler.
   ⚠️ Nenhum nome com TOKEN, KEY, SECRET, PASSWORD ou TOKEN_ID pode entrar nesta
   lista, e o teste `test_system_map.py` reprova se entrar. */
const AMBIENTE_PUBLICO = [
  'VERCEL_GIT_COMMIT_SHA', 'VERCEL_GIT_COMMIT_REF', 'VERCEL_GIT_REPO_OWNER',
  'VERCEL_GIT_REPO_SLUG', 'VERCEL_DEPLOYMENT_ID', 'VERCEL_URL', 'VERCEL_ENV',
  'VERCEL_TARGET_ENV', 'VERCEL_REGION', 'CI', 'GITHUB_SHA', 'GITHUB_REF_NAME',
  'GITHUB_REPOSITORY', 'GITHUB_RUN_ID',
];

const amb = {};
for (const nome of AMBIENTE_PUBLICO) {
  if (typeof process.env[nome] === 'string' && process.env[nome] !== '') {
    amb[nome] = process.env[nome];
  }
}

const diario = [];
const nota = (t) => { diario.push(t); console.log(`  · ${t}`); };

/* ── 1 · o que existe neste contentor ──────────────────────────────────────── */
function comando(bin, args) {
  const r = spawnSync(bin, args, { cwd: RAIZ, encoding: 'utf8' });
  return r.status === 0 ? String(r.stdout).trim() : null;
}

const python = ['python3', 'python'].find(b => comando(b, ['--version']) !== null) || null;
const versaoPython = python ? comando(python, ['--version']) : null;
const temGit = comando('git', ['rev-parse', '--git-dir']) !== null;
const shaDoGit = temGit ? comando('git', ['rev-parse', 'HEAD']) : null;
const refDoGit = temGit ? comando('git', ['rev-parse', '--abbrev-ref', 'HEAD']) : null;

console.log('SYSTEM MAP · metadata do deploy');
nota(`python=${versaoPython || 'AUSENTE'} · git=${temGit ? 'SIM' : 'AUSENTE'}`);
nota(`ambiente publico lido: ${Object.keys(amb).join(' ') || '(nenhuma)'}`);

/* ── 2 e 3 · regenerar pela cadeia que ja existe, e validar ────────────────── */
/* ⚠️ A ARVORE DA BUILD PODE NAO SER A ARVORE DO REPOSITORIO — E NA VERCEL NAO E.
   Medido nesta missao, no log de uma build real:

       Found .vercelignore
       Removed 1125 ignored files defined in .vercelignore

   O `.vercelignore` existe por uma razao seria: impedir que /build /data /docs
   /handoff /research /supabase /tests /.github sejam sequer ENVIADOS para um
   contentor cujo output e publico. Duas fechaduras, e a segunda e essa.

   Consequencia: dentro da build o repositorio tem 311 ficheiros em vez de 1338.
   Regenerar ali produz um mapa REAL de uma arvore MUTILADA — 11 pecas partidas,
   25 em NAO SEI, cobertura 297/311 — e publica-lo por cima do mapa commitado
   seria substituir um mapa correcto por um mapa errado que PARECE fresco.

       UM MAPA DA ARVORE ERRADA E PIOR DO QUE UM MAPA DA ARVORE ANTIGA.

   Por isso a completude e MEDIDA antes de a cadeia correr, e a cadeia so corre
   se a arvore estiver inteira. Quando nao esta, nada e regerado, o mapa
   commitado continua a ser servido, e o artefato diz UNKNOWN com o numero exacto
   ao lado — a tela nao fica verde, e diz porque.

   Levantar esta trava e uma decisao de quem e dono do `.vercelignore`, e nao
   deste script: significa enviar o repositorio inteiro para o contentor. */
let regenerou = false;
let check = 'UNKNOWN';
let porqueNaoRegenerou = null;

/* ⚠️ CONTAR O INDICE NAO MEDE O DISCO — E A PRIMEIRA VERSAO DISTO ERRAVA AQUI.
   A guarda comparava `git ls-files` com o `files_tracked` do mapa commitado, e
   deu ARVORE INTEIRA no contentor da Vercel: `git ls-files` lista o INDICE, e o
   indice continua com os 1503 caminhos mesmo depois de o `.vercelignore` ter
   apagado 1125 FICHEIROS DO DISCO. A guarda media a lista de nomes, e a lista
   de nomes nao tinha sido tocada.

       ESTAR NO INDICE  !=  ESTAR NO DISCO.

   `scan_repo.py` mede o CONTEUDO EM DISCO e salta em silencio o que nao
   encontra (`except OSError: continue`) — foi assim que 1503 caminhos deram 311
   ficheiros medidos. A pergunta certa e portanto a que `git ls-files --deleted`
   responde: que ficheiros o git conhece e o disco nao tem? Zero e a unica
   resposta que autoriza regerar. */
const ausentes = temGit ? comando('git', ['ls-files', '--deleted']) : null;
const rastreados = temGit ? comando('git', ['ls-files']) : null;
const nLinhas = (s) => (s === null ? null : s.split('\n').filter(Boolean).length);
const emFalta = nLinhas(ausentes);
const noIndice = nLinhas(rastreados);
const arvoreInteira = emFalta === 0;
nota(`arvore da build: ${noIndice === null ? 'nao medida' : noIndice} ficheiro(s) no`
  + ` indice · ${emFalta === null ? 'nao medido' : emFalta} ausente(s) do disco`);

if (!python) {
  porqueNaoRegenerou = 'Python nao existe neste contentor de build';
} else if (!temGit) {
  /* `scan_repo.py` mede a arvore com `git ls-files` e o SHA de cada blob. Sem
     `.git` ele nao mede — e um mapa montado sobre uma medicao que falhou seria
     pior do que o mapa velho, porque pareceria novo. */
  porqueNaoRegenerou = 'a arvore de build nao tem .git; o scanner mede a arvore pelo indice do git';
} else if (!arvoreInteira) {
  porqueNaoRegenerou = `a arvore desta build esta incompleta: ${emFalta} dos `
    + `${noIndice} ficheiros rastreados nao chegaram ao disco (o .vercelignore nao `
    + 'envia /build /data /docs /handoff /research /supabase /tests /.github para o '
    + 'contentor). Regenerar aqui daria o mapa de uma arvore mutilada. O mapa '
    + 'commitado continua a ser servido, e a frescura fica UNKNOWN em vez de verde.';
} else {
  nota(`a regerar pela cadeia de ${CADEIA.REGERAR.length} passos (a mesma do CI)`);
  try {
    for (const passo of CADEIA.REGERAR) {
      execFileSync(python, [passo], { cwd: RAIZ, stdio: 'inherit' });
    }
    regenerou = true;
    nota('mapa regerado a partir da arvore que esta a ser implantada');
  } catch (e) {
    porqueNaoRegenerou = `a cadeia falhou: ${e && e.message ? e.message : e}`;
    nota(`FALHA na cadeia: ${porqueNaoRegenerou}`);
  }

  if (regenerou) {
    /* O VALIDADOR NAO E OPCIONAL, mas tambem nao derruba o portal. Ele corre, e
       o veredito vai para o artefato — a tela pinta BROKEN se ele reprovar. */
    for (const passo of CADEIA.VALIDAR) {
      const r = spawnSync(python, [passo], { cwd: RAIZ, stdio: 'inherit' });
      check = r.status === 0 ? 'PASS' : 'FAIL';
      if (check === 'FAIL') break;
    }
    nota(`SYSTEM_MAP_CHECK=${check}`);
  }
}
if (porqueNaoRegenerou) nota(`NAO REGEROU: ${porqueNaoRegenerou}`);

/* ── 4 · o que ficou publicado ─────────────────────────────────────────────── */
const faltam = CADEIA.PUBLICADO.filter(f => !existsSync(join(SERVIDO, f)));
if (faltam.length) nota(`FALTA no que e servido: ${faltam.join(' ')}`);

let estado = null;
try {
  estado = JSON.parse(readFileSync(ESTADO, 'utf8'));
} catch (e) {
  nota('nao consegui ler o estado servido; a proveniencia da arquitetura fica nula');
}
const prov = (estado && estado.PROVENANCE) || null;

/* ── 5 · o commit REALMENTE implantado ─────────────────────────────────────── */
/* A ordem e deliberada. A Vercel e a autoridade sobre o que ela implantou; o git
   da arvore e a segunda melhor prova; nunca se inventa um terceiro. Se nenhuma
   das duas responder, o campo fica NULO e a tela diz UNKNOWN — que e a verdade. */
const implantado = [amb.VERCEL_GIT_COMMIT_SHA, amb.GITHUB_SHA, shaDoGit]
  .find(s => typeof s === 'string' && SHA40.test(s)) || null;
const ramo = amb.VERCEL_GIT_COMMIT_REF || amb.GITHUB_REF_NAME
  || (refDoGit && refDoGit !== 'HEAD' ? refDoGit : null)
  || (prov ? prov.BRANCH : null);
const repositorio = (amb.VERCEL_GIT_REPO_OWNER && amb.VERCEL_GIT_REPO_SLUG)
  ? `${amb.VERCEL_GIT_REPO_OWNER}/${amb.VERCEL_GIT_REPO_SLUG}`
  : (amb.GITHUB_REPOSITORY || (prov ? prov.REPO : null));

const artefato = {
  SCHEMA: 'sintonia.system-map.deployment/1',
  NOTA: 'Gerado no BUILD. Nao editar a mao, e nao commitar: um ficheiro commitado '
    + 'nunca pode conhecer o SHA do commit que o contem.',
  REPOSITORY: repositorio,
  SOURCE_BRANCH: ramo,
  DEPLOYED_COMMIT: implantado,
  DEPLOYED_COMMIT_SOURCE: amb.VERCEL_GIT_COMMIT_SHA ? 'VERCEL_GIT_COMMIT_SHA'
    : amb.GITHUB_SHA ? 'GITHUB_SHA'
      : shaDoGit ? 'git rev-parse HEAD' : null,
  BUILD_ID: amb.VERCEL_DEPLOYMENT_ID || amb.GITHUB_RUN_ID || null,
  BUILD_TIME: new Date().toISOString(),
  DEPLOYMENT_URL: amb.VERCEL_URL ? `https://${amb.VERCEL_URL}` : null,
  ENVIRONMENT: amb.VERCEL_TARGET_ENV || amb.VERCEL_ENV || (amb.CI ? 'ci' : 'local'),
  SYSTEM_MAP_SCHEMA: estado ? estado.SCHEMA : null,
  SYSTEM_MAP_CHECK: check,
  REGENERATED_AT_BUILD: regenerou,
  NOT_REGENERATED_REASON: porqueNaoRegenerou,
  BUILD_TREE_COMPLETE: arvoreInteira,
  BUILD_TREE_TRACKED: noIndice,
  BUILD_TREE_MISSING: emFalta,
  PUBLISHED_FILES_MISSING: faltam,
  ARCHITECTURE_SOURCE_PROVENANCE: prov
    ? {
      REPO: prov.REPO, BRANCH: prov.BRANCH, HEAD: prov.HEAD,
      GENERATED_AT: prov.GENERATED_AT,
    }
    : null,
  TOOLCHAIN: { PYTHON: versaoPython, GIT: temGit, NODE: process.version },
  BUILD_LOG: diario,
};

writeFileSync(ARTEFATO, `${JSON.stringify(artefato, null, 2)}\n`, 'utf8');

const igual = implantado && prov && prov.HEAD === implantado;
console.log(`DEPLOY_METADATA=OK · DEPLOYED_COMMIT=${(implantado || 'UNKNOWN').slice(0, 10)}`
  + ` · GENERATED_FROM=${((prov && prov.HEAD) || 'UNKNOWN').slice(0, 10)}`
  + ` · MESMA_ARVORE=${igual ? 'SIM' : 'NAO'} · SYSTEM_MAP_CHECK=${check}`
  + ` · REGENERADO=${regenerou ? 'SIM' : 'NAO'}`);

/* Sair 0 sempre que o artefato ficou escrito. A honestidade do artefato e o
   produto; reprovar a mudanca e o trabalho do CI, nao do publicador. */
process.exit(0);
