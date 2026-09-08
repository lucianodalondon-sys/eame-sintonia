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
   Nao corrige nenhuma perda. As que restam sao INTEGRATION_DEPENDENCY da
   linhagem claude/opportunity-commercial-priority-v1: o campo que falta falta
   no PACOTE, e o pacote nao se escreve deste lado. Este medidor existe para
   que a divida deixe de depender de alguem se lembrar dela.

   O QUE MUDOU DESDE A PRIMEIRA CORRIDA, E POR QUE ISSO E O PONTO
   ---------------------------------------------------------------
   Na safra V21-044e4924854d5f0a as quatro familias mediam zero. Na safra
   seguinte, V21-06c6421d001ea52a, a familia `transcripts` passou a atravessar:
   184 registos com a escada inteira, o SHA do texto e a contagem da origem —
   e o TEXTO continua a nao atravessar, DE PROPOSITO e com a razao escrita em
   scripts/site_v21_ingest.py.

   Este medidor nao foi editado para acompanhar. Ele mediu.

       UM MEDIDOR QUE PRECISA DE SER REESCRITO QUANDO O MUNDO MUDA
       NAO ESTAVA A MEDIR O MUNDO.

   Precisou de UMA correccao, e essa esta registada onde doi: contava rotulos
   de estado como se fossem fala. Ver o bloco das duas listas, abaixo.
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

/* ── contadores sobre campos DECLARADOS, nunca sobre heuristica de conteudo ──

   CUIDADO QUE ESTE FICHEIRO JA PAGOU UMA VEZ
   -------------------------------------------
   A primeira versao contava como «fala transcrita» os caracteres de QUALQUER
   campo cujo nome casasse /transcript/. Quando a familia `transcripts` chegou
   ao artefacto, ela devolveu 809 caracteres de texto que nao e fala nenhuma:
   eram os rotulos de estado — «true», «false», «INCLUDED» — dos campos
   TRANSCRIPT_EXISTS, TRANSCRIPT_USABLE e irmaos.

       CONTAR O ROTULO DO ESTADO COMO SE FOSSE O TEXTO E EXACTAMENTE
       A CONFUSAO QUE A LEI DESTE REPOSITORIO PROIBE:
       VIDEO_EXISTS != TRANSCRIPT_EXISTS != TRANSCRIPT_USABLE !=
       TRANSCRIPT_USED_AS_EVIDENCE.

   Por isso ha DUAS listas, e nunca uma so: a dos campos que CARREGAM texto e
   a dos campos que DECLARAM estado sobre esse texto. Um campo de estado nunca
   entra na conta de caracteres.                                             */
const RE_TEXTO_DE_FALA = /^(TRANSCRIPT_TEXT|SPEECH_TEXT|CAPTIONS?|SUBTITLES?|TEXT)$/i;
const RE_ESTADO_DE_TRANSCRICAO = /^(VIDEO_EXISTS|TRANSCRIPT_EXISTS|TRANSCRIPT_USABLE|TRANSCRIPT_INCLUDED_IN_PACKAGE|TRANSCRIPT_USED_AS_EVIDENCE)$/i;
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

  /* 1 · TRANSCRICOES — a ESCADA inteira, degrau a degrau.
     Procura-se texto de fala em TODAS as familias, nao so numa: a pergunta nao
     e «а familia de transcricoes esta vazia», e sim «existe em algum sitio do
     artefacto um campo que carregue fala transcrita». */
  const camposDeTexto = [];
  for (const [fam, cs] of todosOsCampos) {
    for (const c of cs) if (RE_TEXTO_DE_FALA.test(c)) camposDeTexto.push(fam + '.' + c);
  }
  let charsTranscricao = 0;
  for (const fam of todas) {
    charsTranscricao += charsDe(H[fam], (k) => RE_TEXTO_DE_FALA.test(k)).chars;
  }

  const trx = H.transcripts || [];
  const conta = (campo, valor) => trx.filter(
    (o) => o && String(o[campo]).toLowerCase() === valor).length;
  const escada = {
    REGISTOS: trx.length,
    VIDEO_EXISTS: conta('VIDEO_EXISTS', 'true'),
    TRANSCRIPT_EXISTS: conta('TRANSCRIPT_EXISTS', 'true'),
    TRANSCRIPT_USABLE: conta('TRANSCRIPT_USABLE', 'true'),
    TRANSCRIPT_INCLUDED_IN_PACKAGE: conta('TRANSCRIPT_INCLUDED_IN_PACKAGE', 'true'),
    TRANSCRIPT_USED_AS_EVIDENCE: conta('TRANSCRIPT_USED_AS_EVIDENCE', 'true'),
    COM_TEXT_SHA256: trx.filter((o) => o && o.TEXT_SHA256).length,
    CAMPOS_DE_ESTADO_ENCONTRADOS: (todosOsCampos.get('transcripts') || [])
      .filter((c) => RE_ESTADO_DE_TRANSCRICAO.test(c)),
  };
  /* CHARS e a contagem que a origem declara por registo. Viaja DENTRO do
     artefacto versionado — logo e reproduzivel daqui —, mas continua a ser
     DECLARACAO DA ORIGEM sobre um texto que o artefacto nao carrega. Contar
     caracteres nao e le-los, e transportar a contagem nao e transportar o
     texto: por isso tem campo proprio e nunca entra em CHEGOU. */
  const charsDeclarados = trx.reduce((a, o) => a + (Number(o && o.CHARS) || 0), 0);

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
      PERGUNTA: 'a fala transcrita do acervo atravessa, e ate que degrau?',
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
        UNIDADE: 'caracteres de fala',
        CAMPOS_DE_TEXTO_ENCONTRADOS: camposDeTexto,
        ESCADA: escada,
        CHARS_DECLARADOS_PELA_ORIGEM: charsDeclarados,
        MEDIDO_DAQUI: 'SIM',
        COMO: 'campos que casem TRANSCRIPT_TEXT|SPEECH_TEXT|CAPTIONS|SUBTITLES|TEXT '
          + 'nas ' + todas.length + ' familias; os campos de ESTADO sao contados '
          + 'a parte e nunca entram na conta de caracteres',
      },
      O_TEXTO_NAO_ATRAVESSA_POR_DECISAO:
        'scripts/site_v21_ingest.py declara, com a razao escrita, que TEXT nao '
        + 'embarca: cinco milhoes de caracteres de fala no payload de cada '
        + 'navegador, para um ecra que hoje nao renderiza uma linha. Atravessam '
        + 'a identidade, a escada inteira, a contagem e o SHA. Isto NAO e perda '
        + 'silenciosa — e fronteira declarada. O que este medidor guarda e que a '
        + 'declaracao continue verdadeira e que a escada continue visivel.',
      O_DEGRAU_QUE_FALTA:
        'TRANSCRIPT_USED_AS_EVIDENCE e false em ' + escada.REGISTOS + '/'
        + escada.REGISTOS + '. Fala existe, e utilizavel, esta no pacote — e '
        + 'nenhum cartao apoia afirmacao nela. O degrau nao e do pacote: e do '
        + 'motor, e so vira true quando uma afirmacao se apoiar nesses bytes.',
      ACAO_MINIMA: 'um cartao que apoie afirmacao em fala, virando o ultimo degrau',
      DONO_DA_ACAO: 'o motor do portal, nesta linhagem',
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
     Quatro estados, e a distincao entre eles e o assunto deste ficheiro:

       FECHADA                        chegou o que se esperava, e os dois lados
                                      foram medidos pelo mesmo medidor
       FECHADA_COM_FRONTEIRA_DECLARADA
                                      o conteudo pesado NAO atravessa DE
                                      PROPOSITO, e o que atravessa em vez dele
                                      — identidade, escada de estado, contagem
                                      e SHA — chegou e mede-se aqui
       ABERTA_MEDIDA_DE_UM_LADO       o lado que chegou foi medido daqui e e
                                      insuficiente; o lado que partiu e alegacao
       NAO_MEDIDA                     nem um lado nem outro

     O terceiro estado e o perigoso: seria uma porta para fechar familia por
     escrever uma frase. Nao e, porque nao se deriva da frase. Deriva-se da
     ASSINATURA MECANICA de uma fronteira deliberada, medida no artefacto:
     registos presentes, os cinco degraus da escada declarados, SHA do texto
     por registo e a contagem de caracteres da origem. Sem os quatro, a familia
     volta a ABERTA por muito bem escrita que esteja a razao.

         UMA FRONTEIRA DELIBERADA DEIXA VESTIGIO MEDIVEL.
         UM ESQUECIMENTO DEIXA SO SILENCIO.                                  */
  for (const f of FAMILIAS) {
    const chegouMedido = f.CHEGOU.MEDIDO_DAQUI === 'SIM';
    const partiuMedido = f.PARTIU.MEDIDO_DAQUI === 'SIM';
    const chegouAlgo = Number(f.CHEGOU.VALOR) > 0;
    const e = f.CHEGOU.ESCADA;
    const fronteiraDeclarada = Boolean(
      f.O_TEXTO_NAO_ATRAVESSA_POR_DECISAO && e
      && e.REGISTOS > 0
      && (e.CAMPOS_DE_ESTADO_ENCONTRADOS || []).length === 5
      && e.COM_TEXT_SHA256 > 0
      && Number(f.CHEGOU.CHARS_DECLARADOS_PELA_ORIGEM) > 0);
    if (!chegouMedido) f.ESTADO = 'NAO_MEDIDA';
    else if (partiuMedido && chegouAlgo) f.ESTADO = 'FECHADA';
    else if (fronteiraDeclarada) f.ESTADO = 'FECHADA_COM_FRONTEIRA_DECLARADA';
    else f.ESTADO = 'ABERTA_MEDIDA_DE_UM_LADO';
    f.PERDA_QUANTIFICAVEL = (chegouMedido && partiuMedido) ? 'SIM' : 'NAO';
    f.PORQUE_A_PERDA_NAO_E_QUANTIFICAVEL = f.PERDA_QUANTIFICAVEL === 'SIM' ? null
      : 'um dos dois lados e alegacao, nao medicao. Subtrair uma medicao de uma '
        + 'alegacao produz um numero com cara de facto.';
  }

  const FECHADAS = new Set(['FECHADA', 'FECHADA_COM_FRONTEIRA_DECLARADA']);
  const abertas = FAMILIAS.filter((f) => !FECHADAS.has(f.ESTADO));
  const degrausAbertos = FAMILIAS.filter((f) => f.O_DEGRAU_QUE_FALTA)
    .map((f) => ({ FAMILIA: f.FAMILIA, DEGRAU: f.O_DEGRAU_QUE_FALTA,
                   DONO: f.DONO_DA_ACAO }));
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
    DEGRAUS_ABERTOS: degrausAbertos,
    O_QUE_DEGRAU_ABERTO_NAO_E:
      'um degrau aberto NAO bloqueia a fronteira. A fronteira pergunta se o que '
      + 'se coletou chega; o degrau pergunta se o que chegou e usado. Sao duas '
      + 'perguntas, e colapsa-las faria a coleta refem do motor.',
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
  console.log('  ' + '-'.repeat(103));
  console.log('  ' + 'FAMILIA'.padEnd(30) + 'PARTIU'.padStart(15) + 'CHEGOU'.padStart(12)
    + '  ' + 'ESTADO'.padEnd(34) + 'PERDA?');
  console.log('  ' + '-'.repeat(103));
  for (const f of d.FAMILIAS) {
    const partiu = String(f.PARTIU.VALOR) + (f.PARTIU.MEDIDO_DAQUI === 'NAO' ? ' (aleg.)' : '');
    console.log('  ' + f.FAMILIA.padEnd(30) + partiu.padStart(15)
      + String(f.CHEGOU.VALOR).padStart(12) + '  ' + f.ESTADO.padEnd(34)
      + f.PERDA_QUANTIFICAVEL);
  }
  console.log('  ' + '-'.repeat(103));
  console.log('  FRONTEIRA_ATRAVESSADA = ' + d.FRONTEIRA_ATRAVESSADA
    + (d.FAMILIAS_ABERTAS.length ? '   abertas: ' + d.FAMILIAS_ABERTAS.join(' · ') : ''));
  console.log('  DONO = ' + d.DONO_DA_FRONTEIRA);
  for (const g of d.DEGRAUS_ABERTOS) {
    console.log('  degrau aberto em ' + g.FAMILIA + ' — dono: ' + g.DONO);
  }
  console.log('');
  console.log('  Nenhum numero do lado PARTIU foi medido daqui. NAO MEDIDO DAQUI nao e ZERO.');
  console.log('');
}
