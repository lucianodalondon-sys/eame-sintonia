#!/usr/bin/env node
/* SINTONIA EAME · A FRONTEIRA ACERVO -> PACOTE, COM MEDIDOR
   ---------------------------------------------------------------------------
   node italia-portale/audit/fronteira-acervo-pacote.mjs           tabela humana
   node italia-portale/audit/fronteira-acervo-pacote.mjs --json    para maquina
   node italia-portale/audit/fronteira-acervo-pacote.mjs --build   grava o artefacto

   POR QUE ESTE FICHEIRO EXISTE
   -----------------------------
   O CHECKPOINT desta linhagem declara PRINCIPAL_LOSS_POINT = O ACERVO NAO
   ATRAVESSA A INGESTAO, e mede-o em tres familias: 5.033.374 caracteres de
   transcricao -> 0, 763 materiais de ciencia -> 88 com 93.933 ch de abstract
   -> 0, e 414 datas de verificacao de anuncio -> 0.

   Esses numeros vivem numa TABELA DE MARKDOWN. A linhagem ja aprendeu o que
   isso vale (audit/reconciliacao-do-catalogo.mjs, sobre 711 -> 213):

       UM NUMERO QUE VIVE NUM DOCUMENTO NAO E UM MEDIDOR.
       E UMA LEMBRANCA DE QUE ALGUEM MEDIU.

   Este ficheiro da medidor ao lado que DAQUI se pode medir, e recusa-se a
   inventar o outro.

   OS DOIS LADOS DA FRONTEIRA, E SO UM E MEDIVEL DAQUI
   ----------------------------------------------------
     PARTIU   o que o acervo tem. O acervo NAO ESTA NESTE REPOSITORIO: vive na
              linhagem geradora e no Postgres. Daqui nao se conta. Cada numero
              do lado PARTIU entra como ALEGACAO com dono e origem escritos,
              e o campo MEDIDO_DAQUI diz NAO.
     CHEGOU   o que atravessou ate ao artefacto que o portal carrega —
              italia-portale/client/italy-handoff-v21.js, versionado, gerado
              por scripts/site_v21_ingest.py. Este lado mede-se, e mede-se
              aqui, contando campos declarados no proprio artefacto.

   A LEI QUE ESTE FICHEIRO OBEDECE
   --------------------------------
   Da seccao I do RELATORIO-PORTAO-DE-ENTRADA-DA-COLETA, onde a linhagem
   publicou ZERO no lugar de NAO MEDIDO DAQUI e teve de se corrigir:

       SOURCE FAILURE != ZERO.
       NAO MEDIDO DAQUI NAO E ZERO, E ZERO MEDIDO NAO E NAO MEDIDO.

   Por isso um CHEGOU = 0 medido aqui NAO fecha a conta sozinho: prova que
   nada chegou, nao prova quanto partiu. A perda so e QUANTIFICAVEL quando os
   dois lados forem medidos pelo mesmo medidor. Enquanto um lado for alegacao,
   o estado da familia e ABERTA_MEDIDA_DE_UM_LADO — nem fechada, nem inventada.

   O QUE ESTE FICHEIRO NAO FAZ
   ----------------------------
   Nao corrige nenhuma das perdas. Todas as quatro sao INTEGRATION_DEPENDENCY
   da linhagem claude/opportunity-commercial-priority-v1: o campo que falta
   falta no PACOTE, e o pacote nao se escreve deste lado. Este medidor existe
   para que a divida deixe de depender de alguem se lembrar dela.
*/
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..', '..');
const HANDOFF = path.join(RAIZ, 'italia-portale', 'client', 'italy-handoff-v21.js');
const SAIDA = path.join(RAIZ, 'data', 'samples', 'FRONTEIRA-ACERVO-PACOTE.json');

/* A data da missao, fixa. Nao e a data de hoje de proposito: um artefacto
   derivado tem de sair byte-identico quando as entradas nao mudam, e um
   carimbo de relogio faria cada regeracao parecer um facto novo. A identidade
   da safra medida esta no BUILD_ID, que vem do proprio artefacto medido. */
const DATA_DA_MISSAO = '2026-09-08';

/* ── o artefacto que o portal carrega, lido pelo proprio carregador ──────────
   O ficheiro usa uma tabela de strings internadas. Reimplementar a
   desinternacao aqui seria uma segunda implementacao da mesma regra — o erro
   que reconciliacao-do-catalogo.mjs recusa cometer. Executa-se o proprio
   ficheiro, que e o unico dono do formato.                                  */
function carregaHandoff() {
  const src = fs.readFileSync(HANDOFF, 'utf8');
  const win = {};
  new Function('window', src)(win);
  const H = win.ITALY_HANDOFF_V21;
  if (!H) throw new Error('ITALY_HANDOFF_V21 ausente: o artefacto mudou de forma');
  return H;
}

/* ── contadores sobre campos DECLARADOS, nunca sobre heuristica de conteudo ── */
const RE_TRANSCRICAO = /transcript|transcricao|transcrizione|trascrizione|SPEECH_TEXT/i;
const RE_TEXTO_CIENTIFICO = /^(ABSTRACT|SUMMARY|RESUMO|FULL_TEXT|BODY_TEXT|PAPER_TEXT)/i;
const RE_DATA_DE_OBSERVACAO = /^(LAST_OBSERVED|FIRST_OBSERVED|OBSERVED_AT|VERIFIED_AT|CHECKED_AT|LAST_SEEN)/i;

function familias(H) {
  return Object.keys(H).filter((k) => Array.isArray(H[k]));
}

function camposDe(linhas) {
  const s = new Set();
  for (const o of linhas) {
    if (o && typeof o === 'object') for (const k of Object.keys(o)) s.add(k);
  }
  return [...s].sort();
}

function charsDe(linhas, casaCampo) {
  let chars = 0;
  let registos = 0;
  for (const o of linhas) {
    if (!o || typeof o !== 'object') continue;
    let tocou = false;
    for (const [k, v] of Object.entries(o)) {
      if (!casaCampo(k)) continue;
      if (typeof v === 'string') { chars += v.length; tocou = true; }
      else if (Array.isArray(v)) {
        for (const x of v) if (typeof x === 'string') { chars += x.length; tocou = true; }
      }
    }
    if (tocou) registos += 1;
  }
  return { chars, registos };
}

/* ── as quatro familias da fronteira ────────────────────────────────────────
   Cada uma declara: o que se alega do lado do acervo (com dono e onde esta
   escrito), o que se mede do lado que chegou, e a accao minima.             */
function mede() {
  const H = carregaHandoff();
  const todas = familias(H);
  const todosOsCampos = new Map(todas.map((f) => [f, camposDe(H[f])]));

  /* 1 · TRANSCRICOES — procura-se em TODAS as familias, nao so numa.
     A pergunta nao e «a familia de transcricoes esta vazia», e sim «existe
     em algum sitio do artefacto um campo que carregue fala transcrita». */
  const camposDeTranscricao = [];
  for (const [fam, cs] of todosOsCampos) {
    for (const c of cs) if (RE_TRANSCRICAO.test(c)) camposDeTranscricao.push(fam + '.' + c);
  }
  let charsTranscricao = 0;
  for (const fam of todas) {
    charsTranscricao += charsDe(H[fam], (k) => RE_TRANSCRICAO.test(k)).chars;
  }

  /* 2 · TEXTO CIENTIFICO */
  const ciencia = H.scienceRecords || [];
  const camposCiencia = todosOsCampos.get('scienceRecords') || [];
  const textoCiencia = charsDe(ciencia, (k) => RE_TEXTO_CIENTIFICO.test(k));
  const comDOI = ciencia.filter((o) => o && o.DOI).length;
  const comURL = ciencia.filter((o) => o && (o.SOURCE_URL || (o.SOURCE_URLS || []).length)).length;

  /* 3 · DATA DE VERIFICACAO DOS ANUNCIOS */
  const comp = H.competitorActivities || [];
  const camposComp = todosOsCampos.get('competitorActivities') || [];
  const camposDeObservacao = camposComp.filter((c) => RE_DATA_DE_OBSERVACAO.test(c));
  const comDataDeObservacao = comp.filter(
    (o) => o && camposDeObservacao.some((c) => o[c])).length;
  const declaramActivo = comp.filter(
    (o) => o && /^ACTIVE$/i.test(String(o.ACTIVE_STATUS || ''))).length;

  /* 4 · VIDEO ORGANICO — os 147 cartoes, e a terceira fronteira nao atravessada */
  const organico = comp.filter(
    (o) => o && /ORGANIC/i.test(String(o.ACTIVITY_TYPE || o.MEDIA_TYPE || '')));
  const organicoCompleto = organico.filter(
    (o) => o.TITLE && (o.URL || o.AD_URL) && o.PUBLISHED_AT).length;
  const organicoSemPais = organico.filter((o) => !o.COUNTRY_REACHED).length;

  const FAMILIAS = [
    {
      FAMILIA: 'TRANSCRICOES',
      PERGUNTA: 'a fala transcrita do acervo atravessa ate ao artefacto do portal?',
      PARTIU: {
        VALOR: 5033374,
        UNIDADE: 'caracteres de fala transcrita',
        OBJETOS: 143,
        OBJETOS_UNIDADE: 'transcricoes utilizaveis',
        MEDIDO_DAQUI: 'NAO',
        PORQUE_NAO: 'o acervo de transcricoes nao esta neste repositorio',
        ORIGEM_DA_ALEGACAO: 'italia-portale/CHECKPOINT-INTEGRACAO-ACERVO-PORTAL.md, seccao 5',
        DONO_DA_MEDICAO: 'claude/opportunity-commercial-priority-v1',
      },
      CHEGOU: {
        VALOR: charsTranscricao,
        UNIDADE: 'caracteres',
        CAMPOS_ENCONTRADOS: camposDeTranscricao,
        MEDIDO_DAQUI: 'SIM',
        COMO: 'varredura de nomes de campo nas ' + todas.length
          + ' familias do artefacto versionado',
      },
      ACAO_MINIMA: 'familia de transcricoes no pacote, com id de video e texto',
      DONO_DA_ACAO: 'claude/opportunity-commercial-priority-v1',
    },
    {
      FAMILIA: 'CIENCIA_TEXTO',
      PERGUNTA: 'o texto dos materiais cientificos atravessa, ou so a ficha?',
      PARTIU: {
        VALOR: 93933,
        UNIDADE: 'caracteres de abstract',
        OBJETOS: 763,
        OBJETOS_UNIDADE: 'materiais no acervo',
        MEDIDO_DAQUI: 'NAO',
        PORQUE_NAO: 'o acervo cientifico nao esta neste repositorio',
        ORIGEM_DA_ALEGACAO: 'italia-portale/CHECKPOINT-INTEGRACAO-ACERVO-PORTAL.md, seccao 3',
        DONO_DA_MEDICAO: 'claude/opportunity-commercial-priority-v1',
      },
      CHEGOU: {
        VALOR: textoCiencia.chars,
        UNIDADE: 'caracteres',
        REGISTOS_COM_TEXTO: textoCiencia.registos,
        REGISTOS: ciencia.length,
        REGISTOS_COM_DOI: comDOI,
        REGISTOS_COM_URL: comURL,
        CAMPOS_DECLARADOS: camposCiencia,
        MEDIDO_DAQUI: 'SIM',
        COMO: 'campos de scienceRecords que casem ABSTRACT|SUMMARY|RESUMO|FULL_TEXT|BODY_TEXT|PAPER_TEXT',
      },
      NAO_CONFUNDIR:
        'FICHA_CHEGOU nao e TEXTO_CHEGOU. Os 88 registos chegam, e chegam com '
        + 'ligacao para o paper. O que nao chega e o texto que permitiria cruzar '
        + 'o que o paper PROVA com o caso — hoje CROP e ISSUE sao o termo da busca.',
      ACAO_MINIMA: 'campo de texto cientifico em SCIENCE.json',
      DONO_DA_ACAO: 'claude/opportunity-commercial-priority-v1',
    },
    {
      FAMILIA: 'ANUNCIOS_DATA_DE_VERIFICACAO',
      PERGUNTA: 'o selo ATTIVO chega com a data que o provaria?',
      PARTIU: {
        VALOR: 414,
        UNIDADE: 'anuncios com last_observed e first_observed no acervo',
        MEDIDO_DAQUI: 'NAO',
        PORQUE_NAO: 'o acervo de anuncios nao esta neste repositorio',
        ORIGEM_DA_ALEGACAO: 'italia-portale/CHECKPOINT-INTEGRACAO-ACERVO-PORTAL.md, seccao 6',
        DONO_DA_MEDICAO: 'claude/opportunity-commercial-priority-v1',
      },
      CHEGOU: {
        VALOR: comDataDeObservacao,
        UNIDADE: 'anuncios com data de observacao',
        REGISTOS: comp.length,
        DECLARAM_ACTIVE: declaramActivo,
        CAMPOS_DE_OBSERVACAO_ENCONTRADOS: camposDeObservacao,
        MEDIDO_DAQUI: 'SIM',
        COMO: 'campos de competitorActivities que casem LAST_OBSERVED|FIRST_OBSERVED|'
          + 'OBSERVED_AT|VERIFIED_AT|CHECKED_AT|LAST_SEEN',
      },
      PORQUE_IMPORTA:
        'ACTIVE e uma afirmacao sobre o PRESENTE. Sem data de verificacao, o selo '
        + 'afirma hoje o que se observou num dia que ninguem consegue nomear.',
      ACAO_MINIMA: 'transportar last_observed para COMPETITOR-ACTIVITIES.json',
      DONO_DA_ACAO: 'claude/opportunity-commercial-priority-v1',
    },
    {
      FAMILIA: 'VIDEO_ORGANICO',
      PERGUNTA: 'os cartoes de video organico chegam com titulo, ligacao e data?',
      PARTIU: {
        VALOR: 1467,
        UNIDADE: 'objetos de video distintos no acervo',
        MEDIDO_DAQUI: 'NAO',
        PORQUE_NAO: 'o acervo de video nao esta neste repositorio',
        ORIGEM_DA_ALEGACAO: 'italia-portale/CHECKPOINT-INTEGRACAO-ACERVO-PORTAL.md, seccao 5',
        DONO_DA_MEDICAO: 'claude/opportunity-commercial-priority-v1',
      },
      CHEGOU: {
        VALOR: organico.length,
        UNIDADE: 'cartoes de video organico no artefacto',
        COM_TITULO_LIGACAO_E_DATA: organicoCompleto,
        SEM_COUNTRY_REACHED: organicoSemPais,
        MEDIDO_DAQUI: 'SIM',
        COMO: 'competitorActivities com ACTIVITY_TYPE ou MEDIA_TYPE contendo ORGANIC',
      },
      TERCEIRA_FRONTEIRA:
        'os campos chegam ao motor; nenhuma tela os renderiza ainda. A razao esta '
        + 'no CHECKPOINT, seccao 5: COUNTRY_REACHED e nulo, e ligar titulo e '
        + 'ligacao poria cartoes ES e FR numa tela italiana. A decisao e do dono '
        + 'do pacote.',
      ACAO_MINIMA: 'COUNTRY_REACHED por cartao, para que a tela possa filtrar',
      DONO_DA_ACAO: 'claude/opportunity-commercial-priority-v1',
    },
  ];

  /* ── o estado de cada familia, DERIVADO, nunca escrito a mao ──────────────
     Tres estados, e a distincao entre eles e o assunto deste ficheiro:

       FECHADA                   chegou o que se esperava, e os dois lados
                                 foram medidos pelo mesmo medidor
       ABERTA_MEDIDA_DE_UM_LADO  o lado que chegou foi medido daqui e e
                                 insuficiente; o lado que partiu e alegacao
       NAO_MEDIDA                nem um lado nem outro                        */
  for (const f of FAMILIAS) {
    const chegouMedido = f.CHEGOU.MEDIDO_DAQUI === 'SIM';
    const partiuMedido = f.PARTIU.MEDIDO_DAQUI === 'SIM';
    const chegouAlgo = Number(f.CHEGOU.VALOR) > 0;
    if (!chegouMedido) f.ESTADO = 'NAO_MEDIDA';
    else if (partiuMedido && chegouAlgo) f.ESTADO = 'FECHADA';
    else f.ESTADO = 'ABERTA_MEDIDA_DE_UM_LADO';
    f.PERDA_QUANTIFICAVEL = (chegouMedido && partiuMedido) ? 'SIM' : 'NAO';
    f.PORQUE_A_PERDA_NAO_E_QUANTIFICAVEL = f.PERDA_QUANTIFICAVEL === 'SIM' ? null
      : 'um dos dois lados e alegacao, nao medicao. Subtrair uma medicao de uma '
        + 'alegacao produz um numero com cara de facto.';
  }

  const abertas = FAMILIAS.filter((f) => f.ESTADO !== 'FECHADA');
  return {
    SOURCE_ID: 'FRONTEIRA-ACERVO-PACOTE',
    VERSION: 1,
    captured_at: DATA_DA_MISSAO,
    SOURCE_LOCATION: 'interno',
    FACT_LOCATION: 'EAME',
    ORIGINAL_LANGUAGE: 'pt',
    DERIVADO_DE: [
      'italia-portale/client/italy-handoff-v21.js',
      'italia-portale/CHECKPOINT-INTEGRACAO-ACERVO-PORTAL.md',
    ],
    O_QUE_ISTO_E:
      'a medicao do lado que CHEGOU da fronteira ACERVO -> PACOTE, contra o '
      + 'artefacto versionado que o portal carrega.',
    O_QUE_ISTO_NAO_E:
      'nao e a medicao do acervo. O acervo nao esta neste repositorio, e nenhum '
      + 'numero do lado PARTIU foi verificado daqui.',
    ARTEFACTO_MEDIDO: 'italia-portale/client/italy-handoff-v21.js',
    BUILD_ID: H.buildId || 'UNKNOWN',
    REFERENCE_DATE: H.referenceDate || 'UNKNOWN',
    FAMILIAS_DO_ARTEFACTO: todas.length,
    FAMILIAS,
    FRONTEIRA_ATRAVESSADA: abertas.length === 0 ? 'SIM' : 'NAO',
    FAMILIAS_ABERTAS: abertas.map((f) => f.FAMILIA),
    DONO_DA_FRONTEIRA: 'claude/opportunity-commercial-priority-v1',
    REGRA:
      'SOURCE FAILURE nao e ZERO. Um lado medido e outro alegado nao produzem '
      + 'uma perda quantificada — produzem uma fronteira aberta com dono.',
  };
}

/* ── saida ─────────────────────────────────────────────────────────────────── */
const args = process.argv.slice(2);
const d = mede();

if (args.includes('--json')) {
  console.log(JSON.stringify(d, null, 2));
} else if (args.includes('--build')) {
  fs.writeFileSync(SAIDA, JSON.stringify(d, null, 2) + '\n');
  console.log('gravado: ' + path.relative(RAIZ, SAIDA));
} else {
  console.log('');
  console.log('  A FRONTEIRA ACERVO -> PACOTE · ' + d.BUILD_ID);
  console.log('  ' + '-'.repeat(94));
  console.log('  ' + 'FAMILIA'.padEnd(30) + 'PARTIU'.padStart(14) + 'CHEGOU'.padStart(12)
    + '  ' + 'ESTADO'.padEnd(26) + 'PERDA?');
  console.log('  ' + '-'.repeat(94));
  for (const f of d.FAMILIAS) {
    const partiu = String(f.PARTIU.VALOR) + (f.PARTIU.MEDIDO_DAQUI === 'NAO' ? ' (aleg.)' : '');
    console.log('  ' + f.FAMILIA.padEnd(30) + partiu.padStart(14)
      + String(f.CHEGOU.VALOR).padStart(12) + '  ' + f.ESTADO.padEnd(26)
      + f.PERDA_QUANTIFICAVEL);
  }
  console.log('  ' + '-'.repeat(94));
  console.log('  FRONTEIRA_ATRAVESSADA = ' + d.FRONTEIRA_ATRAVESSADA
    + (d.FAMILIAS_ABERTAS.length ? '   abertas: ' + d.FAMILIAS_ABERTAS.join(' · ') : ''));
  console.log('  DONO = ' + d.DONO_DA_FRONTEIRA);
  console.log('');
  console.log('  Nenhum numero do lado PARTIU foi medido daqui. NAO MEDIDO DAQUI nao e ZERO.');
  console.log('');
}
