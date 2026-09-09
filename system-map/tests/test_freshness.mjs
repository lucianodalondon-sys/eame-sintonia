#!/usr/bin/env node
/* AS PROVAS DA LEI DA FRESCURA
   ---------------------------------------------------------------------------
   Estas provas existem por uma razao muito concreta: o mapa esteve a servir
   `105602f6` com `624/1321` no ecra, enquanto a cabeca da linha canonica ja ia
   em `8e1947d2`. Nada na tela estava errado — e nada na tela avisava.

   A prova mais importante deste ficheiro e a que ninguem pensa em escrever:

       COVERAGE  !=  FRESHNESS

   `decidir()` NAO RECEBE COBERTURA. `cobertura_nao_entra_na_decisao` prova isso
   pela unica via que nao se pode contornar: 1/1000 com as cabecas iguais da
   verde, e 1000/1000 com o servido velho da vermelho.

   E a segunda mais importante:

       AUSENCIA DE PROVA DE STALENESS  !=  PROVA DE CURRENT

   Nenhum caminho onde falte uma medicao pode devolver CURRENT. Isso e provado
   por forca bruta, sobre todas as combinacoes possiveis das medicoes.
   --------------------------------------------------------------------------- */
'use strict';

import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createContext, runInContext } from 'node:vm';

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = resolve(AQUI, '..', '..');

/* A LEI E CARREGADA DO FICHEIRO QUE O BROWSER CARREGA. Nao ha copia do teste,
   nao ha reimplementacao: se este teste passar, e a lei servida que passou. */
const ctx = createContext({});
runInContext(readFileSync(join(RAIZ, 'system-map', 'app', 'freshness.js'), 'utf8'), ctx);
const { decidir, ESTADOS } = ctx.SM_FRESHNESS;

const A = 'a'.repeat(40);
const B = 'b'.repeat(40);
const REPO = 'lucianodalondon-sys/eame-sintonia';
const RAMO = 'claude/collection-foundation-integration-v1';
const SCHEMA = 'sintonia.system-map.state/1';

/* Uma medicao COMPLETA e SA: os quatro factos presentes e a bater. Cada teste
   parte daqui e estraga UMA coisa — assim o que falha e sempre nomeavel. */
const sa = (extra) => ({
  repository: REPO, state_repository: REPO,
  source_branch: RAMO, state_branch: RAMO,
  generated_from: A, deployed_commit: A, latest_canonical_head: A,
  latest_head_error: null, system_map_check: 'PASS', behind_by: null,
  deployment_present: true, schema_do_estado: SCHEMA, schema_declarado: SCHEMA,
  map_belongs_to_deployed_tree: true,
  ...extra,
});

const falhas = [];
let total = 0;
function prova(nome, ok, detalhe) {
  total += 1;
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${nome}`);
  if (!ok) {
    falhas.push(nome);
    if (detalhe) console.log(`        ${detalhe}`);
  }
}
const eq = (nome, m, esperado) => {
  const v = decidir(m);
  prova(nome, v.state === esperado, `esperado ${esperado}, veio ${v.state}: ${v.razoes.join(' ')}`);
  return v;
};

console.log('\n── SMF · a lei da frescura ──────────────────────────────────────');

/* SMF-01 · SOURCE BRANCH e MEDIDO, e a divergencia com a branch onde o mapa foi
   gerado e DITA — mas nao e um veredito. Medido em producao: o checkout da Vercel
   responde `master` a `git rev-parse --abbrev-ref HEAD`, e um alias de branch
   servia legitimamente um mapa gerado noutra. Reprovar por isto seria gritar por
   uma diferenca que nao prova nada sobre frescura. */
{
  const v = decidir(sa({ source_branch: 'outra/branch' }));
  prova('SMF-01_branch_divergente_e_dita_e_nao_e_veredito',
    v.state === ESTADOS.CURRENT && v.razoes.join(' ').includes('outra/branch'),
    `${v.state}: ${v.razoes.join(' ')}`);
}

/* SMF-02 · DEPLOYED COMMIT e medido no build: sem artefato nao existe. */
eq('SMF-02_sem_artefato_de_build_nao_existe_deployed_commit',
  sa({ deployment_present: false, deployed_commit: null }), ESTADOS.UNKNOWN);

/* SMF-03 · LATEST HEAD nao e inventado: nulo continua nulo. */
{
  const v = decidir(sa({ latest_canonical_head: null, latest_head_error: 'GitHub respondeu 404' }));
  prova('SMF-03_latest_head_nao_e_inventado',
    v.state === ESTADOS.UNKNOWN && v.razoes.join(' ').includes('404'),
    `veio ${v.state}`);
}

/* SMF-04 · DEPLOYED != LATEST -> STALE. */
eq('SMF-04_deployed_diferente_de_latest_da_stale',
  sa({ deployed_commit: A, latest_canonical_head: B }), ESTADOS.STALE);

/* SMF-05 · DEPLOYED == LATEST + CHECK PASS + mapa daquela arvore -> CURRENT. */
eq('SMF-05_iguais_com_check_pass_da_current', sa({}), ESTADOS.CURRENT);

/* SMF-06 · LATEST indisponivel -> UNKNOWN, nunca CURRENT. */
for (const mau of [null, undefined, '', 'HEAD', 'zzzz', A.slice(0, 39)]) {
  eq(`SMF-06_latest_indisponivel_nunca_da_verde[${String(mau).slice(0, 6)}]`,
    sa({ latest_canonical_head: mau }), ESTADOS.UNKNOWN);
}

/* SMF-07 · SYSTEM_MAP_CHECK FAIL -> BROKEN, mesmo com tudo igual. */
eq('SMF-07_check_fail_da_broken', sa({ system_map_check: 'FAIL' }), ESTADOS.BROKEN);
eq('SMF-07b_check_ausente_nao_da_verde',
  sa({ system_map_check: 'UNKNOWN' }), ESTADOS.UNKNOWN);
eq('SMF-07c_check_com_valor_desconhecido_nao_da_verde',
  sa({ system_map_check: 'MAYBE' }), ESTADOS.UNKNOWN);

/* SMF-08 · COVERAGE nao participa da decisao. Provado de duas maneiras:
   pela ASSINATURA (nenhum campo de cobertura e lido) e pelo COMPORTAMENTO. */
{
  const fonte = readFileSync(join(RAIZ, 'system-map', 'app', 'freshness.js'), 'utf8');
  const corpo = fonte.slice(fonte.indexOf('function decidir'), fonte.indexOf('function veredito'));
  const proibidos = ['files_covered', 'files_tracked', 'coverage', 'cobertura']
    .filter(k => corpo.includes(k));
  prova('SMF-08_cobertura_nao_e_sequer_lida_por_decidir', proibidos.length === 0,
    `encontrado dentro de decidir(): ${proibidos.join(', ')}`);
}

/* SMF-09 · a cobertura continua a ser verdade quando o mapa esta stale: a
   decisao muda, o inventario nao. Provado por o veredito ser identico com e sem
   qualquer numero de cobertura empurrado para dentro da medicao. */
{
  const magro = decidir(sa({ latest_canonical_head: B }));
  const gordo = decidir(sa({ latest_canonical_head: B, files_covered: 1332, files_tracked: 1332 }));
  prova('SMF-09_cobertura_cheia_nao_salva_um_mapa_stale',
    magro.state === ESTADOS.STALE && gordo.state === magro.state,
    `${magro.state} vs ${gordo.state}`);
}

/* SMF-10 · STALE grita. SMF-11 · UNKNOWN nao e verde e nao grita como partido. */
{
  const s = decidir(sa({ latest_canonical_head: B }));
  prova('SMF-10_stale_grita_e_diz_para_nao_usar',
    s.grita === true && s.emoji === '🔴' && /NAO USE/i.test(s.frase), JSON.stringify(s));
  const u = decidir(sa({ latest_canonical_head: null }));
  prova('SMF-11_unknown_nunca_se_disfarca_de_verde',
    u.grita === false && u.emoji === '⚪' && u.state !== ESTADOS.CURRENT
      && /nao e prova/i.test(u.frase), JSON.stringify(u));
  const b = decidir(sa({ system_map_check: 'FAIL' }));
  prova('SMF-07d_broken_grita', b.grita === true && b.emoji === '🔴');
  const c = decidir(sa({}));
  prova('SMF-05b_current_nao_grita', c.grita === false && c.emoji === '🟢');
}

/* O DEFEITO ORIGINAL, NOMEADO: o mapa gerado de OUTRO commit que aquele que
   esta implantado. Era isto que o commit-que-se-autoreferencia produzia, e a
   tela dizia «BRANCH x @ 105602f» como se fosse a posicao da branch. */
eq('SMF-04b_mapa_provadamente_de_outra_arvore_da_stale',
  sa({ map_belongs_to_deployed_tree: false, generated_from: B }), ESTADOS.STALE);
{
  const v = decidir(sa({ map_belongs_to_deployed_tree: false, generated_from: B }));
  prova('SMF-04c_stale_por_outra_arvore_diz_porque',
    v.atraso === 'MAP OF ANOTHER TREE', v.atraso);
}
/* PERTENCA NAO PROVADA NAO E PERTENCA REFUTADA. `null` cai em UNKNOWN, nunca em
   verde e nunca em vermelho: e o caso real da build da Vercel, onde o
   `.vercelignore` deixa a arvore incompleta e a cadeia nao pode correr. */
eq('SMF-04g_pertenca_nao_provada_da_unknown',
  sa({ map_belongs_to_deployed_tree: null }), ESTADOS.UNKNOWN);
{
  const v = decidir(sa({ map_belongs_to_deployed_tree: null, system_map_check: 'UNKNOWN',
    check_reason: 'a arvore desta build esta incompleta: 311 de 1338 ficheiros' }));
  prova('SMF-04h_unknown_diz_o_motivo_medido',
    v.state === ESTADOS.UNKNOWN && v.razoes.join(' ').includes('311 de 1338'),
    v.razoes.join(' '));
}
/* A PROVA QUE MAIS IMPORTA DESTA REVISAO: staleness prova-se sozinha. Com o
   validador em UNKNOWN e a pertenca por provar, um commit servido diferente da
   cabeca remota continua a ser STALE — e nao vira UNKNOWN. Po-lo depois do
   portao do validador seria a unica maneira de esta lei mentir para o lado
   confortavel. */
eq('SMF-04i_stale_prova_se_sozinha_mesmo_sem_validador',
  sa({ latest_canonical_head: B, system_map_check: 'UNKNOWN',
    map_belongs_to_deployed_tree: null }), ESTADOS.STALE);

/* «N COMMITS BEHIND» so quando N e realmente calculavel. */
{
  const com = decidir(sa({ latest_canonical_head: B, behind_by: 4 }));
  prova('SMF-04d_diz_n_commits_behind_quando_e_calculavel',
    com.atraso === 'MAP IS 4 COMMITS BEHIND', com.atraso);
  const um = decidir(sa({ latest_canonical_head: B, behind_by: 1 }));
  prova('SMF-04e_singular_quando_e_um_commit', um.atraso === 'MAP IS 1 COMMIT BEHIND', um.atraso);
  for (const n of [null, undefined, 0, -3, 2.5, '4', NaN]) {
    const s = decidir(sa({ latest_canonical_head: B, behind_by: n }));
    prova(`SMF-04f_sem_n_calculavel_diz_head_mismatch[${String(n)}]`,
      s.atraso === 'HEAD MISMATCH', s.atraso);
  }
}

/* Metadata invalida ou contraditoria -> BROKEN, nunca verde por descuido. */
eq('SMF-07e_deployed_commit_que_nao_e_sha_da_broken',
  sa({ deployed_commit: 'HEAD' }), ESTADOS.BROKEN);
eq('SMF-07f_generated_from_que_nao_e_sha_da_broken',
  sa({ generated_from: 'main' }), ESTADOS.BROKEN);
eq('SMF-07g_repo_contraditorio_da_broken',
  sa({ state_repository: 'outro/repo' }), ESTADOS.BROKEN);
eq('SMF-07h_schema_contraditorio_da_broken',
  sa({ schema_declarado: 'sintonia.system-map.state/9' }), ESTADOS.BROKEN);

console.log('\n── RED TEAM · os seis cenarios pedidos ──────────────────────────');
eq('RED_A_latest_BBBB_deployed_AAAA__stale',
  sa({ deployed_commit: A, generated_from: A, latest_canonical_head: B }), ESTADOS.STALE);
eq('RED_B_latest_unknown_deployed_AAAA__unknown',
  sa({ latest_canonical_head: null }), ESTADOS.UNKNOWN);
eq('RED_C_iguais_mas_check_fail__broken',
  sa({ system_map_check: 'FAIL' }), ESTADOS.BROKEN);
eq('RED_D_iguais_e_check_pass__current', sa({}), ESTADOS.CURRENT);
eq('RED_E_cobertura_1_de_1000_com_cabecas_iguais__current',
  sa({ files_covered: 1, files_tracked: 1000 }), ESTADOS.CURRENT);
eq('RED_F_cobertura_1000_de_1000_com_deployed_antigo__stale',
  sa({ files_covered: 1000, files_tracked: 1000, latest_canonical_head: B }), ESTADOS.STALE);

console.log('\n── FORCA BRUTA · verde exige as quatro provas ───────────────────');
{
  /* Todas as combinacoes das medicoes que importam. CURRENT so pode aparecer no
     unico ramo onde as quatro condicoes da lei estao satisfeitas. */
  let verdes = 0, errados = [];
  for (const presente of [true, false]) {
    for (const dep of [A, B, null, 'HEAD']) {
      for (const rem of [A, B, null]) {
        for (const chk of ['PASS', 'FAIL', 'UNKNOWN']) {
          for (const pert of [true, false, null]) {
            const m = sa({ deployment_present: presente, deployed_commit: dep,
              latest_canonical_head: rem, system_map_check: chk,
              map_belongs_to_deployed_tree: pert });
            const v = decidir(m);
            if (v.state !== ESTADOS.CURRENT) continue;
            verdes += 1;
            const legitimo = presente && dep === rem && pert === true
              && typeof dep === 'string' && dep.length === 40 && chk === 'PASS';
            if (!legitimo) errados.push(JSON.stringify({ presente, dep, rem, chk, pert }));
          }
        }
      }
    }
  }
  prova('verde_so_aparece_com_as_quatro_provas', errados.length === 0, errados.slice(0, 4).join(' '));
  prova('e_o_verde_aparece_de_facto_quando_deve', verdes > 0, `verdes=${verdes}`);
}

/* A medicao vazia — o pior caso possivel — nunca pode ser verde. */
for (const vazio of [undefined, null, {}]) {
  const v = decidir(vazio);
  prova(`medicao_vazia_nunca_da_verde[${String(vazio)}]`,
    v.state !== ESTADOS.CURRENT && v.state === ESTADOS.UNKNOWN, v.state);
}

console.log();
if (falhas.length) {
  console.log(`TESTES_FRESCURA=FAIL · ${falhas.length} de ${total} reprovada(s): ${falhas.join(', ')}`);
  process.exit(1);
}
console.log(`TESTES_FRESCURA=PASS · ${total} provas`);
