#!/usr/bin/env node
/* SINTONIA · UPSTREAM INGESTION — o lote recebido, medido contra o que declara
   ---------------------------------------------------------------------------
   Quatro familias chegaram como handoff determinístico: Radar Futuro, Sinais de
   Campo, Fontes e o Fitossanitário como camada de evidência. Copiar ficheiros é
   fácil; o que este portão faz é impedir que a cópia vire outra coisa a caminho
   da tela.

       UM LOTE QUE CHEGA SEM PORTÃO NÃO FOI INGERIDO: FOI DEPOSITADO.

   Ele NÃO desenha nada e NÃO decide nada. As regras de superfície vêm todas do
   upstream — CARTÃO, COM_MÉTODO, EVIDENCE_ONLY, DROPPED, avisos, limites — e
   aqui só se verifica que continuam a valer do lado de cá.

   O que ele guarda, um a um:
     · os quatro carimbos de origem estão na mesma história, um contendo os outros;
     · a contagem de cada família bate com o handoff;
     · nenhum ID renderizável se perdeu;
     · nenhum DROPPED atravessou;
     · EVIDENCE_ONLY não tem grelha própria;
     · nenhum PARCIAL foi promovido;
     · AGIR_AGORA do Radar Futuro continua 0;
     · nenhum ITF- misturado com ITFC-;
     · nenhuma contagem global usa 7.456;
     · nenhuma tela chama 622 de «sinais futuros» nem 560 de «alertas».
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { CLIENT, readPortal } from './lib/harness.mjs';
import { antepassadoNaTestemunha } from './lineage-witness.mjs';

const results = [];
const check = (id, title, fn) => {
  try { const r = fn(); results.push({ id, title, ...r }); }
  catch (e) { results.push({ id, title, pass: false, expected: 'runs', measured: 'THREW', detail: [e.message] }); }
};

let detalheDaLinhagem = '';
const UP = path.join(CLIENT, 'upstream');
const J = (f) => JSON.parse(fs.readFileSync(path.join(UP, f), 'utf8'));

const RF = J('IT-FUTURO-HANDOFF-LINHA-B-V1.json');
const SC_ = J('IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json');
const FO = J('IT-HANDOFF-LINHA-B-FONTES-V1.json');
const FI = J('IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json');

/* O critério aprovado. Não sai dos handoffs: se saísse, provaria só que eles
   concordam consigo mesmos. */
const CRIT = {
  RADAR: { TOTAL: 45, RENDERABLE: 44, DROPPED: 1, ACT_NOW: 0, PREPARE: 23, WATCH: 21, LIMITED: 8 },
  CAMPO: { TOTAL: 640, CARD: 28, METHOD: 19, EVIDENCE: 421, DROPPED: 172 },
  FONTES: { TOTAL: 317, CARD: 0, METHOD: 91, EVIDENCE: 39, DROPPED: 187 },
  FITO: { TOTAL: 560, CARD: 0, METHOD: 0, EVIDENCE: 560, DROPPED: 0 },
};

check('LOTE_COMPLETO_E_DE_UMA_SO_HISTORIA', 'the four handoffs arrive and their checkpoints share one history', () => {
  const bad = [];
  /* A regra era «um so checkpoint». Deixou de servir quando uma familia foi
     corrigida a montante sozinha — FITOSSANITARIO, cuja LEI ainda declarava o
     universo antigo de 438 registos. Refazer as outras tres so para as alinhar
     seria regerar o que ninguem pediu e nao mudou.

     Mas «checkpoints diferentes» tambem nao pode virar «checkpoint qualquer».
     A pergunta certa nao e se sao iguais: e se sao COMPARAVEIS. Um lote so e um
     lote se os seus carimbos estiverem na mesma historia, um contendo os outros.

         DUAS DATAS NA MESMA LINHA SAO UMA CORRECCAO.
         DUAS DATAS EM LINHAS DIFERENTES SAO DUAS VERDADES.

     Verifica-se pela ancestralidade real no repositorio, nao pela palavra do
     artefacto. Sem git alcancavel, isto RECUSA: nao saber nao e passar. */
  const heads = [...new Set([RF, SC_, FO, FI].map((d) => d.UPSTREAM_CHECKPOINT))];
  if (heads.some((h) => !h)) bad.push('ha familia sem UPSTREAM_CHECKPOINT');
  else if (heads.length > 1) {
    const raiz = path.resolve(CLIENT, '..', '..');
    /* Duas fontes, nesta ordem. O Git quando tem os objectos — e a autoridade.
       A testemunha versionada quando nao tem, porque um clone `--single-branch`
       desta linha nao possui commits de outra linhagem que o handoff so nomeia.

           NAO SABER CONTINUA A SER FALHAR. A testemunha nao afrouxa a regra:
           substitui «nao consigo perguntar» por «aqui esta a conta, refaz».

       O que nao se faz e ir buscar a rede a meio de um portao. */
    const temObjecto = (s) =>
      spawnSync('git', ['cat-file', '-e', `${s}^{commit}`], { cwd: raiz }).status === 0;
    const porqueTestemunha = [];
    const antepassado = (a, b) => {
      if (temObjecto(a) && temObjecto(b)) {
        const r = spawnSync('git', ['merge-base', '--is-ancestor', a, b], { cwd: raiz });
        if (r.error || r.status === null) throw new Error(`git inalcancavel: nao da para provar a linhagem de ${a}`);
        return r.status === 0;
      }
      const v = antepassadoNaTestemunha(a, b);
      if (v.resposta === null) throw new Error(`linhagem por provar: ${v.porque.join('; ')}`);
      if (!porqueTestemunha.length) porqueTestemunha.push('por testemunha versionada');
      return v.resposta;
    };
    /* o mais novo tem de conter todos os outros */
    const maisNovo = heads.find((h) => heads.every((o) => o === h || antepassado(o, h)));
    if (!maisNovo) bad.push(`checkpoints sem historia comum: ${heads.join(', ')} — isto sao safras diferentes, nao uma correccao`);
    else {
      const atras = heads.filter((h) => h !== maisNovo);
      detalheDaLinhagem = `${maisNovo} contem ${atras.join(', ')}${porqueTestemunha.length ? ' · ' + porqueTestemunha[0] : ''}`;
    }
  }
  for (const [n, d] of [['RADAR', RF], ['CAMPO', SC_], ['FONTES', FO], ['FITO', FI]]) {
    if (!d.CONTRACT_VERSION) bad.push(`${n} sem CONTRACT_VERSION`);
    if (!Object.keys(d.PROVENIENCIA?.SOURCE_ARTIFACT_HASHES || d.HASHES_DOS_ARTEFACTOS_CONSUMIDOS || {}).length) bad.push(`${n} sem hashes de origem`);
  }
  return { pass: !bad.length, expected: 0, measured: detalheDaLinhagem || heads[0] || 'ABSENT', detail: bad };
});

check('CONTAGENS_BATEM_COM_O_HANDOFF', 'every family count equals the approved criterion', () => {
  const bad = [];
  const c = CRIT.RADAR;
  if (RF.TOTAL !== c.TOTAL) bad.push(`radar TOTAL ${RF.TOTAL}`);
  if (RF.RENDERABLE !== c.RENDERABLE) bad.push(`radar RENDERABLE ${RF.RENDERABLE}`);
  if (RF.DROPPED !== c.DROPPED) bad.push(`radar DROPPED ${RF.DROPPED}`);
  if (RF.PORTFOLIO_LIMITED !== c.LIMITED) bad.push(`radar PORTFOLIO_LIMITED ${RF.PORTFOLIO_LIMITED}`);
  for (const [n, d, k] of [['CAMPO', SC_, CRIT.CAMPO], ['FONTES', FO, CRIT.FONTES], ['FITO', FI, CRIT.FITO]]) {
    if (d.TOTAL !== k.TOTAL) bad.push(`${n} TOTAL ${d.TOTAL} != ${k.TOTAL}`);
    if (d.RENDERABLE_CARD !== k.CARD) bad.push(`${n} CARD ${d.RENDERABLE_CARD} != ${k.CARD}`);
    if (d.RENDERABLE_WITH_METHOD !== k.METHOD) bad.push(`${n} METHOD ${d.RENDERABLE_WITH_METHOD} != ${k.METHOD}`);
    if (d.EVIDENCE_ONLY !== k.EVIDENCE) bad.push(`${n} EVIDENCE ${d.EVIDENCE_ONLY} != ${k.EVIDENCE}`);
    if (d.DROPPED !== k.DROPPED) bad.push(`${n} DROPPED ${d.DROPPED} != ${k.DROPPED}`);
  }
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

check('SOMA_DOS_DESTINOS_FECHA', 'card + method + evidence + dropped = total, in every family', () => {
  const bad = [];
  for (const [n, d] of [['CAMPO', SC_], ['FONTES', FO], ['FITO', FI]]) {
    const s = d.RENDERABLE_CARD + d.RENDERABLE_WITH_METHOD + d.EVIDENCE_ONLY + d.DROPPED;
    if (s !== d.TOTAL) bad.push(`${n}: ${s} != ${d.TOTAL} — um registo desapareceu sem destino`);
  }
  if (RF.RENDERABLE + RF.DROPPED !== RF.TOTAL) bad.push(`RADAR: ${RF.RENDERABLE}+${RF.DROPPED} != ${RF.TOTAL}`);
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

check('NENHUM_ID_RENDERIZAVEL_PERDIDO', 'every authorised entry survives the crossing', () => {
  const bad = [];
  if ((RF.RENDERIZAVEIS || []).length !== RF.RENDERABLE) bad.push(`radar: ${(RF.RENDERIZAVEIS || []).length} ids para ${RF.RENDERABLE}`);
  for (const [n, d, k] of [['CAMPO', SC_, CRIT.CAMPO], ['FONTES', FO, CRIT.FONTES]]) {
    const n_ent = (d.ENTRADAS_AUTORIZADAS || []).length;
    if (n_ent !== k.CARD + k.METHOD) bad.push(`${n}: ${n_ent} entradas para ${k.CARD + k.METHOD}`);
  }
  return { pass: !bad.length, expected: 0, measured: `${(RF.RENDERIZAVEIS || []).length} + ${(SC_.ENTRADAS_AUTORIZADAS || []).length} + ${(FO.ENTRADAS_AUTORIZADAS || []).length}`, detail: bad };
});

check('NENHUM_DROPPED_ATRAVESSOU', 'no dropped record appears among the authorised entries', () => {
  const bad = [];
  if ((RF.RENDERIZAVEIS || []).includes('ITFC-027')) bad.push('ITFC-027 entrou na superficie');
  for (const [n, d] of [['CAMPO', SC_], ['FONTES', FO]]) {
    for (const e of d.ENTRADAS_AUTORIZADAS || []) {
      if (e.DESTINO === 'DROPPED' || e.DESTINO === 'EVIDENCE_ONLY') bad.push(`${n}: ${e.ID} tem destino ${e.DESTINO} e esta entre as autorizadas`);
    }
  }
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 5) };
});

check('EVIDENCE_ONLY_SEM_GRELHA_PROPRIA', 'the evidence layer ships zero cards', () => {
  const bad = [];
  if (FI.RENDERABLE_CARD !== 0 || FI.RENDERABLE_WITH_METHOD !== 0) bad.push('fitossanitario emitiu cartao');
  if ((FI.ENTRADAS_AUTORIZADAS || []).length !== 0) bad.push(`fitossanitario trouxe ${(FI.ENTRADAS_AUTORIZADAS || []).length} entradas — sao 560 documentos, nao 560 cartoes`);
  return { pass: !bad.length, expected: 0, measured: `${FI.EVIDENCE_ONLY} evidence · ${(FI.ENTRADAS_AUTORIZADAS || []).length} cartoes`, detail: bad };
});

check('NENHUM_PARCIAL_PROMOVIDO', 'the 40 PARCIAL stay PARCIAL, with their warning', () => {
  const bad = [];
  const lim = RF.LIMITACOES_POR_SINAL || {};
  const parc = Object.entries(lim).filter(([, v]) => v.ESTADO === 'PARCIAL');
  if (parc.length !== 40) bad.push(`${parc.length} PARCIAL, criterio 40`);
  for (const [id, v] of parc) {
    if (v.AVISO_OBRIGATORIO !== 'LETTURA_PARZIALE') bad.push(`${id} sem aviso`);
    if (!v.LACUNAS) bad.push(`${id} sem lacunas visiveis`);
  }
  return { pass: !bad.length, expected: 0, measured: `${parc.length} PARCIAL`, detail: bad.slice(0, 5) };
});

check('RADAR_ACT_NOW_CONTINUA_ZERO', 'AGIR_AGORA stays 0 and the tone rules travel', () => {
  const bad = [];
  if (RF.ACT_NOW !== 0) bad.push(`ACT_NOW ${RF.ACT_NOW}`);
  for (const k of ['PREPARAR', 'MONITORAR', 'AGIR_AGORA']) if (!(RF.REGRAS_DE_TOM || {})[k]) bad.push(`sem regra de tom para ${k}`);
  const lim = RF.LIMITACOES_POR_SINAL || {};
  const acoes = new Set(Object.values(lim).map((v) => v.ACAO));
  if (acoes.has('AGIR_AGORA')) bad.push('um sinal chegou como AGIR_AGORA');
  return { pass: !bad.length, expected: 0, measured: [...acoes].join(' · '), detail: bad };
});

check('PORTFOLIO_LIMITED_PRESERVA_LIMITACAO', 'the 8 keep their limitation and the live route stays shut', () => {
  const bad = [];
  const lim = RF.LIMITACOES_POR_SINAL || {};
  const lt = Object.entries(lim).filter(([, v]) => v.PORTFOLIO && v.PORTFOLIO.ROTA_VIVA_PERMITIDA === false);
  if (lt.length !== 8) bad.push(`${lt.length} limitados, criterio 8`);
  for (const [id, v] of lt) if (!v.PORTFOLIO.O_CARTAO_PODE) bad.push(`${id} sem regra do que o cartao pode`);
  for (const id of RF.PORTFOLIO_LIMITED_IDS || []) if (!lim[id]) bad.push(`${id} listado e sem limitacao`);
  return { pass: !bad.length, expected: 0, measured: `${lt.length} com rota viva fechada`, detail: bad };
});

check('NENHUM_ITF_MISTURADO_COM_ITFC', 'the other population never enters the grid', () => {
  const bad = [];
  const ids = RF.RENDERIZAVEIS || [];
  for (const i of ids) if (!/^ITFC-/.test(i)) bad.push(`${i} nao e ITFC-`);
  const p = RF.POPULACAO_QUE_NAO_ENTRA || {};
  if (p.PREFIXO !== 'ITF' || !p.CLASSIFICACAO) bad.push('a populacao que nao entra nao esta declarada');
  const flat = JSON.stringify(RF.RENDERIZAVEIS);
  if (/"ITF-\d/.test(flat)) bad.push('um ITF- entrou na lista renderizavel');
  return { pass: !bad.length, expected: 0, measured: `${ids.length} ids, todos ITFC-`, detail: bad };
});

check('NENHUMA_CONTAGEM_MORTA_NA_TELA', 'the portal shows no 7.456, no "622 sinais", no "560 alertas"', () => {
  const bad = [];
  const html = readPortal();
  if (/7[.,]456/.test(html)) bad.push('7.456 aparece no portal — total revogado');
  if (/622\s*(sinali|segnali|sinais|signals)/i.test(html)) bad.push('622 apresentado como sinais');
  if (/560\s*(alert|avvisi|alerta)/i.test(html)) bad.push('560 apresentado como alertas');
  if (/9[.,]4\d\d\s*(cart|card|schede)/i.test(html)) bad.push('o total do acervo apresentado como cartoes');
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

check('NENHUMA_REGRA_DE_SUPERFICIE_NASCE_AQUI', 'the portal adds no rule of its own to the batch', () => {
  const bad = [];
  for (const [n, d] of [['CAMPO', SC_], ['FONTES', FO], ['FITO', FI]]) {
    if (!d.CAMPOS_OBRIGATORIOS) bad.push(`${n} sem campos obrigatorios do upstream`);
    if (!d.RAZAO_DE_EXCLUSAO || !d.RAZAO_DE_EXCLUSAO.length) bad.push(`${n} sem razao de exclusao`);
    if (!d.LEI_DA_FAMILIA) bad.push(`${n} sem a lei da familia`);
  }
  if (!RF.CAMPOS_OBRIGATORIOS_DO_CARTAO) bad.push('RADAR sem campos obrigatorios');
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad };
});

/* ── report ──────────────────────────────────────────────────────────────── */
const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
const pad = (s, n) => String(s).slice(0, n).padEnd(n);
console.log('\n  SINTONIA · UPSTREAM INGESTION · o lote das quatro familias');
console.log('  ' + '─'.repeat(112));
for (const r of results) {
  console.log(`  ${r.pass ? G + 'PASS' + X : R + 'FAIL' + X}  ${pad(r.id, 40)} ${pad(r.title, 48)} ${DIM}got${X} ${r.measured}`);
  if (!r.pass) for (const d of (Array.isArray(r.detail) ? r.detail : [r.detail]).slice(0, 6)) console.log(`        ${DIM}${String(d).slice(0, 150)}${X}`);
}
const ok = results.filter((r) => r.pass).length;
console.log('  ' + '─'.repeat(112));
console.log(`  ${ok}/${results.length} passing\n`);
process.exit(ok === results.length ? 0 : 1);
