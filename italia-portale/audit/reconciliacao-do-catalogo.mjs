#!/usr/bin/env node
/* SINTONIA ITALIA · A RECONCILIACAO DO CATALOGO — 711 OCORRENCIAS, 213 PARES
   ---------------------------------------------------------------------------
   node audit/reconciliacao-do-catalogo.mjs           tabela humana
   node audit/reconciliacao-do-catalogo.mjs --json    para maquina

   POR QUE ESTE FICHEIRO EXISTE
   -----------------------------
   A missao da Opportunity mediu 711 -> 213 em scripts descartaveis. A conta
   ficou na mensagem do commit 5880b80, e uma conta que so existe numa mensagem
   nao se volta a fazer.

       UM NUMERO QUE VIVE NUMA MENSAGEM DE COMMIT NAO E UM MEDIDOR.
       E UMA LEMBRANCA DE QUE ALGUEM MEDIU.

   AS TRES UNIDADES QUE NAO SE SOMAM
   ----------------------------------
   O erro facil e tratar 711, 213 e 611 como a mesma coisa. Nao sao:

     711  OCORRENCIAS (produto, termo textual) no censo publico do catalogo.
          Um termo repetido em dois produtos conta duas vezes.
     213  PARES normalizados (produto, CROP_ID) no pacote. O par e a unidade
          que o portal consegue cruzar.
     611  JUSTIFICACOES (CARTAO, PRODUTO) sobre 43 cartoes — outra unidade
          ainda, e de outra coleccao. NAO reconcilia 711 -> 213.

   Este medidor so fala das duas primeiras, e diz onde para.

   O QUE ELE PROVA, E O QUE RECUSA PROVAR
   ---------------------------------------
   Prova por ARITMETICA DE CONJUNTOS sobre campos que o proprio pacote declara:
   nao reimplementa a normalizacao. Duas implementacoes da mesma regra divergem,
   e a divergencia aparece quando ja custou. O dono da normalizacao e
   `scripts/v21_ingest.py`, na linhagem claude/opportunity-commercial-priority-v1.

   Por isso a pergunta «quantos dos pares vieram SO da pagina de cultura» fica
   NAO MEDIDA aqui, com o motivo escrito: mapear termo -> CROP_ID exigiria uma
   segunda normalizacao. A origem declara 2. Este ficheiro regista a alegacao e
   diz que nao a verificou.

       CHAMAR FALHA AO QUE NAO SE PODE MEDIR E MENTIR PARA BAIXO.
       CHAMAR SUCESSO E MENTIR PARA CIMA.

   E OS 436 NAO SAO 436 PRODUTOS EM FALTA
   ---------------------------------------
   Sao 436 OCORRENCIAS cujo termo nao normalizou, sobre 114 termos distintos.
   Ficam declaradas em CROPS_NOT_RECOGNISED, verbatim. Resolve-las por
   semelhanca de texto para fechar uma conta seria inventar cobertura.
   A cobertura global continua PARCIAL, e o medidor di-lo em vez de a arredondar.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { statoDelPacchetto } from './lib/pacote.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(HERE, '..', '..');
const JSONOUT = process.argv.includes('--json');
const CENSO = path.join(RAIZ, 'data', 'samples', 'IT-CATALOGO', 'IT-ADAMA-CATALOG-CENSUS-2026-09-02.json');

const pac = statoDelPacchetto();
const falhas = [];
const naoMedidos = [];

if (!fs.existsSync(CENSO)) {
  console.error('censo ausente: ' + path.relative(RAIZ, CENSO));
  process.exit(1);
}
const PCPATH = path.join(pac.dir, 'PRODUCTS-COMMERCIAL.json');
if (!fs.existsSync(PCPATH)) {
  const linha = 'NAO MEDIDO: nao ha PRODUCTS-COMMERCIAL.json no disco. O pacote gera-se, nao se guarda.';
  if (JSONOUT) console.log(JSON.stringify({ naoMedidos: [linha] }, null, 2));
  else console.log('\n  ' + linha + '\n');
  process.exit(0);
}

const censo = JSON.parse(fs.readFileSync(CENSO, 'utf8'));
const pc = JSON.parse(fs.readFileSync(PCPATH, 'utf8'));
const A = (v) => (Array.isArray(v) ? v : []);

/* -- 1 . o lado do censo: a origem dos termos ------------------------------ */
const censoProdutos = A(censo.PRODUCTS);
let ocorrenciasCenso = 0;
const termosCenso = new Map();
for (const p of censoProdutos) {
  for (const t of A(p.CROPS_DECLARED_ON_PAGE)) {
    ocorrenciasCenso++;
    termosCenso.set(t, (termosCenso.get(t) || 0) + 1);
  }
}

/* -- 2 . o lado do pacote: o que a normalizacao devolveu ------------------- */
const recs = A(pc.RECORDS);
let declaradas = 0, naoReconhecidas = 0, naoReconhecidasCampo = 0, viaPagina = 0;
const pares = new Set();
const termosNaoReconhecidos = new Map();
for (const r of recs) {
  declaradas += A(r.CROPS_DECLARED_BY_PRODUCT).length;
  const nr = A(r.CROPS_NOT_RECOGNISED);
  naoReconhecidas += nr.length;
  naoReconhecidasCampo += (typeof r.CROPS_NOT_RECOGNISED_COUNT === 'number' ? r.CROPS_NOT_RECOGNISED_COUNT : 0);
  for (const t of nr) termosNaoReconhecidos.set(t, (termosNaoReconhecidos.get(t) || 0) + 1);
  viaPagina += A(r.CROPS_DISCOVERED_VIA_CROP_PAGE).length;
  for (const c of A(r.CROP_IDS)) pares.add(r.ID + ' ' + c);
}
const reconhecidas = declaradas - naoReconhecidas;
const redundancia = reconhecidas - pares.size;

/* -- 3 . as perguntas ----------------------------------------------------- */
/* T1 . nada se perde ANTES da normalizacao: o pacote recebeu todas as
        ocorrencias que o censo publicou. Se o pacote declarar ZERO, o campo
        nao existe nesta safra — e isso e NAO MEDIDO, nao uma perda de 711. */
if (declaradas === 0) {
  naoMedidos.push({ t: 'T1', porque:
    'esta safra do pacote nao publica CROPS_DECLARED_BY_PRODUCT: a reconciliacao '
    + 'termo-a-termo nao existe nela. O censo continua a declarar ' + ocorrenciasCenso
    + ' ocorrencias, e o pacote so mostra o resultado (' + pares.size + ' pares). '
    + 'Sem os termos declarados nao se sabe QUAIS ocorrencias colapsaram nem quais '
    + 'nao normalizaram. Traga a safra que os publica.' });
} else if (declaradas !== ocorrenciasCenso) {
  falhas.push({ t: 'T1', porque: 'o censo publica ' + ocorrenciasCenso
    + ' ocorrencias e o pacote declara ' + declaradas });
}
/* T2 . a reparticao explica tudo, e o contador do registo bate com a lista. */
if (declaradas > 0 && naoReconhecidas !== naoReconhecidasCampo) {
  falhas.push({ t: 'T2', porque: 'CROPS_NOT_RECOGNISED soma ' + naoReconhecidas
    + ' mas CROPS_NOT_RECOGNISED_COUNT soma ' + naoReconhecidasCampo });
}
if (reconhecidas < 0) falhas.push({ t: 'T2', porque: 'mais nao reconhecidas do que declaradas' });
/* T3 . nenhum par sem origem: os pares tem de caber nas ocorrencias
        reconhecidas mais as descobertas por pagina de cultura. */
if (declaradas > 0 && pares.size > reconhecidas + viaPagina) {
  falhas.push({ t: 'T3', porque: pares.size + ' pares nao cabem em ' + reconhecidas
    + ' ocorrencias reconhecidas + ' + viaPagina + ' da pagina de cultura — ha par sem origem' });
}
/* T4 . os termos nao reconhecidos ficam PRESERVADOS, verbatim. Um termo que
        desaparece sem entrar em CROPS_NOT_RECOGNISED e perda muda. */
if (naoReconhecidas > 0 && termosNaoReconhecidos.size === 0) {
  falhas.push({ t: 'T4', porque: 'ha ocorrencias nao reconhecidas e nenhum termo preservado' });
}
/* T5 . a cobertura declara-se, nunca se arredonda. */
const cobertura = declaradas ? (reconhecidas / declaradas) : null;

naoMedidos.push({
  t: 'ORIGEM_DOS_PARES_DE_PAGINA_DE_CULTURA',
  porque: 'mapear termo -> CROP_ID exigiria uma SEGUNDA normalizacao, e o dono e '
    + 'scripts/v21_ingest.py na linhagem claude/opportunity-commercial-priority-v1. '
    + 'Medido aqui: ' + viaPagina + ' ocorrencias via pagina de cultura. Quantos PARES vem SO '
    + 'dai nao se mede sem reimplementar a regra. A origem declara 2; alegacao NAO verificada.',
});

const saida = {
  pacote: pac.stato, buildId: pac.buildId,
  censo: {
    ficheiro: path.relative(RAIZ, CENSO), produtos: censoProdutos.length,
    ocorrencias: ocorrenciasCenso, termosDistintos: termosCenso.size,
  },
  pacoteMedido: {
    produtos: recs.length, declaradas, reconhecidas, naoReconhecidas,
    termosNaoReconhecidosDistintos: termosNaoReconhecidos.size,
    paresDistintos: pares.size, redundanciaPorColapso: redundancia,
    ocorrenciasViaPaginaDeCultura: viaPagina,
    coberturaDasOcorrencias: cobertura === null ? null : Number((cobertura * 100).toFixed(1)),
  },
  falhas, naoMedidos,
};

if (JSONOUT) {
  console.log(JSON.stringify(saida, null, 2));
  process.exit(falhas.length ? 1 : 0);
}

const ESC = String.fromCharCode(27);
const G = ESC + '[32m', R = ESC + '[31m', Y = ESC + '[33m', D = ESC + '[2m', X = ESC + '[0m';
const l = (k, v, n) => console.log('  ' + k.padEnd(46) + String(v).padStart(9) + '  ' + D + (n || '') + X);
console.log('');
console.log('  SINTONIA ITALIA . A RECONCILIACAO DO CATALOGO');
console.log('  pacote: ' + (pac.stato === 'CANONICO' ? G + pac.stato + X : Y + pac.stato + X)
  + ' ' + D + (pac.buildId || '') + X);
console.log('  ' + '-'.repeat(86));
l('censo . produtos', censoProdutos.length, path.relative(RAIZ, CENSO));
l('censo . OCORRENCIAS (produto, termo)', ocorrenciasCenso, 'a unidade de entrada');
l('censo . termos distintos', termosCenso.size);
console.log('  ' + '-'.repeat(86));
l('pacote . produtos', recs.length);
l('pacote . CROPS_DECLARED_BY_PRODUCT', declaradas,
  declaradas === 0 ? Y + 'ausente nesta safra' + X
    : (declaradas === ocorrenciasCenso ? 'igual ao censo' : R + 'DIFERE DO CENSO' + X));
l('pacote . ocorrencias RECONHECIDAS', reconhecidas, 'normalizaram para CROP_ID');
l('pacote . ocorrencias NAO reconhecidas', naoReconhecidas,
  termosNaoReconhecidos.size + ' termos distintos, preservados verbatim');
l('pacote . PARES distintos (produto, CROP_ID)', pares.size, 'a unidade que o portal cruza');
l('pacote . redundancia por colapso', declaradas ? redundancia : 'NAO MEDIDA',
  declaradas ? 'ocorrencias que caem no mesmo par' : 'sem os termos declarados nao ha colapso a medir');
l('pacote . ocorrencias via pagina de cultura', viaPagina, 'segunda origem, lida a parte');
l('COBERTURA DAS OCORRENCIAS', cobertura === null ? 'NAO MEDIDA' : (cobertura * 100).toFixed(1) + '%',
  cobertura === null ? '' : 'PARCIAL — e diz-se parcial');
console.log('  ' + '-'.repeat(86));
if (declaradas > 0) {
  console.log('  ' + D + 'a conta: ' + ocorrenciasCenso + ' = ' + reconhecidas
    + ' reconhecidas + ' + naoReconhecidas + ' nao reconhecidas' + X);
  console.log('  ' + D + '         ' + reconhecidas + ' reconhecidas colapsam em '
    + (pares.size - viaPagina >= 0 ? pares.size : pares.size) + ' pares (redundancia '
    + redundancia + ')' + X);
  console.log('  ' + D + naoReconhecidas + ' nao sao ' + naoReconhecidas
    + ' produtos em falta nem ' + naoReconhecidas + ' culturas: sao ocorrencias de '
    + termosNaoReconhecidos.size + ' termos.' + X);
}
for (const f of falhas) console.log('  ' + R + 'FALHA' + X + ' ' + f.t + '  ' + f.porque);
for (const u of naoMedidos) console.log('  ' + Y + 'N/M  ' + X + ' ' + u.t + '\n        ' + D + u.porque + X);
if (!falhas.length) console.log('  ' + G + 'a aritmetica fecha' + X);
console.log('');
process.exit(falhas.length ? 1 : 0);
