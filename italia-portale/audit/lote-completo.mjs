#!/usr/bin/env node
/* SINTONIA · LOTE COMPLETO — as quatro bases e os dois enriquecimentos
   ---------------------------------------------------------------------------
   Um enriquecimento não pode redefinir a base que enriquece. É a regra que
   torna o lote seguro: se o TOP_3 ou os Human Sensors falharem, rejeita-se o
   enriquecimento e os quatro insumos-base ficam de pé.

       UM ENRIQUECIMENTO QUE PODE MUDAR O JULGAMENTO NÃO ENRIQUECE:
       SUBSTITUI, E SEM DIZER QUE SUBSTITUIU.

   Os números aqui são o critério aprovado, não saem dos handoffs. Se saíssem
   de lá, provariam apenas que cada pacote concorda consigo mesmo.

   Sobre os DO_NOT_SHOW: a divisão entre LITERAL e SEMÂNTICO **não vem do
   handoff** — ele traz 14 entradas sem classe. A divisão é declarada aqui, com
   a regra à vista: LITERAL é frase ou número que um grep encontra no ecrã;
   SEMÂNTICO é uma FORMA de afirmação, com variável ou relação, que nenhuma
   busca de texto apanha. Oito e seis.

       DIZER QUE SE TESTOU CATORZE PORQUE SE GREPARAM OITO
       É COBERTURA DECLARADA, NÃO COBERTURA MEDIDA.

   Sobre os IT-OPP-00x: medido nesta corrida, portale.html cita-os 44 vezes e
   TODAS em comentário. O portal legado carrega os três registos reais e o
   fixture de 29 nos seus próprios ficheiros de dados — camada antiga, anterior
   a este lote, que não alimenta a superfície da reunião. O portão por isso não
   proíbe a string: proíbe a TRAVESSIA (id no snapshot, id em handoff, id em
   código, meeting-surface a ler o fixture).
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { CLIENT, readPortal } from './lib/harness.mjs';

const results = [];
const check = (id, title, fn) => {
  try { const r = fn(); results.push({ id, title, ...r }); }
  catch (e) { results.push({ id, title, pass: false, expected: 'runs', measured: 'THREW', detail: [e.message] }); }
};

const UP = path.join(CLIENT, 'upstream');
const J = (f) => JSON.parse(fs.readFileSync(path.join(UP, f), 'utf8'));
const RF = J('IT-FUTURO-HANDOFF-LINHA-B-V1.json');
const SC_ = J('IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json');
const FO = J('IT-HANDOFF-LINHA-B-FONTES-V1.json');
const FI = J('IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json');
const T3 = J('IT-TOP3-SENSORES-V1.json');
const HS = J('IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json');
const PINS = J('UPSTREAM-PINS.json');

/* Os oito literais: frase ou número que um grep encontra. */
/* As oito literais e as seis semânticas moram num ficheiro declarado, e não aqui:
   `casa-gate.mjs` precisa exatamente da mesma divisão para medir a primeira dobra,
   e duas cópias da mesma lista divergem na terceira vez que alguém mexe numa.

       DUAS LISTAS DA MESMA LEI SÃO DUAS LEIS À ESPERA DE DISCORDAR.

   O ficheiro traz também o equivalente ITALIANO de cada literal — necessário
   porque as regras estão escritas em português e o ecrã fala italiano. */
const QA_DNS = JSON.parse(fs.readFileSync(new URL('./DO-NOT-SHOW-QA.json', import.meta.url), 'utf8'));
const DO_NOT_SHOW_LITERAIS = QA_DNS.LITERAIS.map((x) => x.PT);
const DO_NOT_SHOW_SEMANTICOS = QA_DNS.SEMANTICOS;

check('RAW_OPPORTUNITIES_FAMILY_CANNOT_REPLACE_CANONICAL_43',
      'the raw OPORTUNIDADES family never stands in for the canonical 43', () => {
  const bad = [];
  /* Os 43 sao GERADOS pela cadeia (build/.../DESIGN-INGEST/OPPORTUNITIES.json) e
     nunca procurados como artefacto commitado. A familia crua data/ ->
     OPORTUNIDADES tem TRES registos — IT-OPP-001/002/003 — e o portal legado
     carrega-os desde sempre, no seu proprio fixture de 3 reais + 29 demo. O
     perigo nao e o id existir: e o id ATRAVESSAR para a superficie canonica.

         PROIBIR A PALAVRA NAO PROTEGE NADA SE ELA SO VIVE EM COMENTARIO.
         O QUE SE PROIBE E A TRAVESSIA. */
  const snap = path.join(CLIENT, 'meeting-intelligence-snapshot.json');
  if (!fs.existsSync(snap)) return { pass: false, expected: 0, measured: 1, detail: ['snapshot canonico ausente'] };
  const s = JSON.parse(fs.readFileSync(snap, 'utf8'));
  const ids = (s.CASES || []).map((c) => c.ID || '');
  if (s.TOTAL_CASES !== 43 || ids.length !== 43) bad.push(`o snapshot traz ${s.TOTAL_CASES}/${ids.length} casos, nao 43`);
  for (const i of ids) if (!/^OPP_/.test(i)) bad.push(`id canonico sem prefixo OPP_: ${i}`);
  for (const i of ids) if (/IT-OPP-/.test(i)) bad.push(`id da familia crua no snapshot: ${i}`);
  if (s.SOURCE_HEAD !== '55c2674') bad.push(`SOURCE_HEAD ${s.SOURCE_HEAD}`);
  if (!/^V21-/.test(s.BUILD_ID || '')) bad.push('o snapshot nao declara BUILD_ID da cadeia');
  /* Nenhum handoff deste lote pode trazer um id da familia crua. */
  for (const f of fs.readdirSync(UP)) {
    if (/IT-OPP-\d/.test(fs.readFileSync(path.join(UP, f), 'utf8'))) bad.push(`${f} carrega um id IT-OPP-`);
  }
  /* No portal, os ids legados so podem viver em comentario. Fora dele, zero. */
  const html = readPortal();
  const semComentario = html.replace(/\/\*[\s\S]*?\*\//g, '')
    .split('\n').map((l) => l.replace(/(^|\s)\/\/.*$/, '')).join('\n');
  const emCodigo = semComentario.match(/IT-OPP-\d/g) || [];
  const emComentario = (html.match(/IT-OPP-\d/g) || []).length - emCodigo.length;
  if (emCodigo.length) bad.push(`${emCodigo.length} id(s) IT-OPP- fora de comentario em portale.html`);
  /* E a superficie da reuniao le o snapshot, nao o fixture legado. */
  const surf = fs.readFileSync(path.join(CLIENT, 'meeting-surface.js'), 'utf8');
  if (/ITALY_REAL_INTELLIGENCE|ITALY_DEMO_DATA/.test(surf)) bad.push('meeting-surface le o fixture legado');
  if (!/window\.MEETING_INTELLIGENCE/.test(surf)) bad.push('meeting-surface nao le MEETING_INTELLIGENCE');
  return { pass: !bad.length, expected: 0, measured: `43 OPP_ · 0 IT-OPP- em codigo · ${emComentario} em comentario`, detail: bad };
});

check('RADAR_45_NOT_624', 'the radar surface counts signals, never structural records', () => {
  const bad = [];
  if (RF.TOTAL !== 45) bad.push(`TOTAL ${RF.TOTAL}`);
  if ((RF.RENDERIZAVEIS || []).length !== 44) bad.push(`renderizáveis ${(RF.RENDERIZAVEIS || []).length}`);
  const html = readPortal();
  for (const n of ['624', '625', '622']) {
    const rx = new RegExp(`${n}\\s*(segnali|sinais|signals|schede|cards)`, 'i');
    if (rx.test(html)) bad.push(`${n} apresentado como sinais — são registos estruturais`);
  }
  return { pass: !bad.length, expected: 0, measured: `${RF.TOTAL} canónicos · ${(RF.RENDERIZAVEIS || []).length} visíveis`, detail: bad };
});

check('RADAR_ACT_NOW_ZERO', 'nothing in the radar arrives as act-now', () => {
  const bad = [];
  if (RF.ACT_NOW !== 0) bad.push(`ACT_NOW ${RF.ACT_NOW}`);
  const acoes = new Set(Object.values(RF.LIMITACOES_POR_SINAL || {}).map((v) => v.ACAO));
  if (acoes.has('AGIR_AGORA')) bad.push('um sinal chegou como AGIR_AGORA');
  return { pass: !bad.length, expected: 0, measured: [...acoes].join(' · '), detail: bad };
});

check('ITF_CANNOT_MIX_WITH_ITFC', 'the ten ITF- stay out of the ITFC- grid', () => {
  const bad = [];
  for (const i of RF.RENDERIZAVEIS || []) if (!/^ITFC-/.test(i)) bad.push(`${i} não é ITFC-`);
  const p = RF.POPULACAO_QUE_NAO_ENTRA || {};
  if (p.PREFIXO !== 'ITF' || p.N !== 10) bad.push('a população separada não está declarada como ITF- · 10');
  return { pass: !bad.length, expected: 0, measured: `${(RF.RENDERIZAVEIS || []).length} ITFC- · ${p.N} ITF- fora`, detail: bad };
});

check('FIELD_SIGNALS_VISIBLE_47', 'field signals put 28 + 19 on screen, never 640', () => {
  const bad = [];
  if (SC_.RENDERABLE_CARD !== 28) bad.push(`cartão ${SC_.RENDERABLE_CARD}`);
  if (SC_.RENDERABLE_WITH_METHOD !== 19) bad.push(`método ${SC_.RENDERABLE_WITH_METHOD}`);
  const n = (SC_.ENTRADAS_AUTORIZADAS || []).length;
  if (n !== 47) bad.push(`${n} entradas autorizadas, critério 47`);
  return { pass: !bad.length, expected: 0, measured: `${SC_.RENDERABLE_CARD} + ${SC_.RENDERABLE_WITH_METHOD} = ${n}`, detail: bad };
});

check('PHYTOSANITARY_HAS_NO_STANDALONE_GRID', '560 documents ship zero cards', () => {
  const bad = [];
  if (FI.RENDERABLE_CARD || FI.RENDERABLE_WITH_METHOD) bad.push('o fitossanitário emitiu cartão');
  if ((FI.ENTRADAS_AUTORIZADAS || []).length) bad.push(`${FI.ENTRADAS_AUTORIZADAS.length} entradas — são documentos, não cartões`);
  if (FI.EVIDENCE_ONLY !== 560) bad.push(`evidence ${FI.EVIDENCE_ONLY}`);
  return { pass: !bad.length, expected: 0, measured: `${FI.EVIDENCE_ONLY} evidence · 0 cartões`, detail: bad };
});

check('EVIDENCE_ONLY_NOT_PROMOTED_TO_SIGNAL', 'evidence never crosses as an authorised entry', () => {
  const bad = [];
  for (const [n, d] of [['CAMPO', SC_], ['FONTES', FO], ['FITO', FI]]) {
    for (const e of d.ENTRADAS_AUTORIZADAS || []) {
      if (e.DESTINO === 'EVIDENCE_ONLY') bad.push(`${n}: ${e.ID} é evidência e está autorizado como entrada`);
    }
  }
  return { pass: !bad.length, expected: 0, measured: bad.length, detail: bad.slice(0, 5) };
});

check('DROPPED_CANNOT_RENDER', 'no dropped record can reach the screen', () => {
  const bad = [];
  if ((RF.RENDERIZAVEIS || []).includes('ITFC-027')) bad.push('ITFC-027 renderizável');
  for (const [n, d] of [['CAMPO', SC_], ['FONTES', FO]]) {
    for (const e of d.ENTRADAS_AUTORIZADAS || []) if (e.DESTINO === 'DROPPED') bad.push(`${n}: ${e.ID}`);
  }
  const total = SC_.DROPPED + FO.DROPPED + FI.DROPPED + RF.DROPPED;
  return { pass: !bad.length, expected: 0, measured: `${total} dropped, nenhum autorizado`, detail: bad };
});

/* Uma restricao declarada e uma chave que NEGA ou PROIBE. Um campo que apenas
   explica nao limita: explicar e convidar a publicar. */
const RESTRITIVA = /LIMIT|PROIBID|NUNCA|(^|_)NAO(_|$)|RESSALVA/;
const declaraLimite = (a) => Object.keys(a || {}).some((k) => {
  if (!RESTRITIVA.test(k)) return false;
  const v = a[k];
  return v !== null && v !== undefined && v !== '' && !(Array.isArray(v) && !v.length);
});

check('PORTAL_WITH_METHOD_REQUIRES_LIMIT', 'nothing ships with method and no declared limit', () => {
  const bad = [];
  for (const [n, d] of [['CAMPO', SC_], ['FONTES', FO]]) {
    const avisos = d.AVISOS_OBRIGATORIOS || {};
    const comMetodo = (d.LIMITES || []).filter((l) => (d.CAMPOS_OBRIGATORIOS || {})[l.SUBCONJUNTO]);
    for (const l of comMetodo) {
      if (!l.NAO_SEI || !l.NAO_SEI.COMO_RENDERIZAR) bad.push(`${n}/${l.SUBCONJUNTO} sem regra de NAO SEI`);
    }
    if (d.RENDERABLE_WITH_METHOD > 0 && !Object.keys(avisos).length) bad.push(`${n} rende com metodo e nao declara aviso`);
  }
  const ACH = HS.ACHADOS || {};
  for (const p of (HS.PORTAL_WITH_METHOD || [])) {
    if (!(p in ACH)) { bad.push(`human sensors: ${p} autorizado e inexistente`); continue; }
    if (!declaraLimite(ACH[p])) bad.push(`human sensors: ${p} sem restricao declarada`);
  }
  /* Cada achado pertence a exactamente um balde. Um achado em dois baldes e
     publicavel pelo mais permissivo; um achado em nenhum e publicavel por
     omissao. Sao a mesma falha vista de dois lados. */
  const baldes = ['PORTAL_NOW', 'PORTAL_WITH_METHOD', 'METHOD_ONLY', 'CODE_FIX_HANDOFF', 'OWNER_DECISION'];
  const conta = {};
  for (const b of baldes) for (const k of (HS[b] || [])) conta[k] = (conta[k] || 0) + 1;
  for (const k of Object.keys(ACH)) {
    if (!conta[k]) bad.push(`${k} nao esta em nenhum balde de autorizacao`);
    else if (conta[k] > 1) bad.push(`${k} esta em ${conta[k]} baldes`);
  }
  for (const k of Object.keys(conta)) if (!(k in ACH)) bad.push(`um balde cita ${k}, que nao e achado`);
  /* Controlo negativo: um achado so descritivo tem de ser recusado pela mesma
     funcao. Um portao que nunca reprovou e decoracao. */
  if (declaraLimite({ CLASSE: 'X', FATO: 'y', NUMERO: 3 })) bad.push('CONTROLO NEGATIVO FALHOU: achado sem restricao foi aceite');
  return { pass: !bad.length, expected: 0, measured: `${(HS.PORTAL_WITH_METHOD || []).length} com metodo · ${Object.keys(ACH).length} achados em ${baldes.length} baldes`, detail: bad.slice(0, 6) };
});

check('DO_NOT_SHOW_LITERAL_8_OF_8', 'the eight greppable forbidden strings are absent from the screen', () => {
  const bad = [];
  const html = readPortal();
  if (DO_NOT_SHOW_LITERAIS.length !== 8) bad.push(`a lista literal tem ${DO_NOT_SHOW_LITERAIS.length}, não 8`);
  for (const s of DO_NOT_SHOW_LITERAIS) if (html.includes(s)) bad.push(`o ecrã diz «${s}»`);
  if ((HS.DO_NOT_SHOW || []).length !== 14) bad.push(`o handoff traz ${(HS.DO_NOT_SHOW || []).length} DO_NOT_SHOW, não 14`);
  return { pass: !bad.length, expected: 0, measured: `${DO_NOT_SHOW_LITERAIS.length}/8 testados por grep`, detail: bad };
});

check('DO_NOT_SHOW_SEMANTIC_6_OF_6_REVIEWED', 'the six semantic ones are named, and NOT claimed as automated', () => {
  const bad = [];
  if (DO_NOT_SHOW_SEMANTICOS.length !== 6) bad.push(`a lista semântica tem ${DO_NOT_SHOW_SEMANTICOS.length}, não 6`);
  if (DO_NOT_SHOW_LITERAIS.length + DO_NOT_SHOW_SEMANTICOS.length !== (HS.DO_NOT_SHOW || []).length) {
    bad.push('literais + semânticos não somam os DO_NOT_SHOW do handoff');
  }
  /* Este teste NÃO prova ausência: prova que os seis estão nomeados e que a
     revisão humana é exigida. Um grep que fingisse cobri-los seria pior que
     não os ter. */
  return { pass: !bad.length, expected: 0, measured: `${DO_NOT_SHOW_SEMANTICOS.length} nomeados · revisão humana exigida, NÃO automatizada`, detail: bad };
});

check('TOP3_CANNOT_CHANGE_JUDGMENT', 'the enrichment adds watch fields and touches no verdict', () => {
  const bad = [];
  const PERMITIDO = ['VARIABLE_TO_WATCH', 'SOURCE_TO_WATCH', 'WATCH_CADENCE', 'TRIGGER_CONDITION',
                     'INVALIDATION_TRIGGER_LITERAL_ATUAL', 'EXECUTABILITY'];
  const PROIBIDO = ['ESTADO', 'ACAO', 'VEREDITO', 'COMMERCIAL_PRIORITY', 'PRIORIDADE',
                    'TOP_3', 'PORTFOLIO', 'ADAMA_PAIR_EXISTS', 'DROPPED', 'RENDERIZAVEIS'];
  const rows = T3.ROWS || [];
  if (rows.length !== 3) bad.push(`o enriquecimento traz ${rows.length} linhas, nao 3`);
  const t3 = RF.TOP_3 || [];
  if ((T3.TOP_3 || []).join('|') !== t3.join('|')) bad.push('o TOP_3 do enriquecimento difere do congelado');
  const lim = RF.LIMITACOES_POR_SINAL || {};
  for (const r of rows) {
    const id = r.SIGNAL_ID;
    if (!t3.includes(id)) { bad.push(`${id} nao esta no TOP_3 congelado`); continue; }
    for (const k of PROIBIDO) if (k in r) bad.push(`${id} traz ${k} — enriquecimento nao decide julgamento`);
    if (!PERMITIDO.some((k) => k in r)) bad.push(`${id} nao traz nenhum campo de vigilancia`);
    /* O enriquecimento pode ECOAR o estado-base; nao pode contradize-lo. */
    const base = lim[id] || {};
    const eco = String(r.CURRENT_STATE || '').toUpperCase();
    if (base.ESTADO && !eco.includes(base.ESTADO)) bad.push(`${id}: o eco nao confirma ESTADO ${base.ESTADO}`);
    if (base.ACAO && !eco.includes(base.ACAO)) bad.push(`${id}: o eco nao confirma ACAO ${base.ACAO}`);
    /* Um alvo de transicao declarado NAO e uma transicao. */
    if ((T3.TRANSICAO_AUTORIZADA_PELA_REGUA || {})[id] !== 'NAO') bad.push(`${id}: o enriquecimento autoriza transicao de estado`);
  }
  if (RF.TOTAL !== 45) bad.push('o enriquecimento mexeu no universo-base');
  if (RF.ACT_NOW !== 0) bad.push('um sinal passou a AGIR_AGORA');
  return { pass: !bad.length, expected: 0, measured: `${rows.length} instrumentados · 0 transicoes autorizadas · TOP_3 intacto`, detail: bad.slice(0, 6) };
});

check('HUMAN_SENSORS_HASH_MATCH', 'the human sensors handoff is the pinned one, by SHA and by hash', () => {
  const bad = [];
  const f = 'IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json';
  const pin = (PINS.PINS || {})[f];
  if (!pin) bad.push('sem pin declarado');
  else {
    if (pin.SHA_QUE_CONTEM_OS_BYTES !== '7501255') bad.push(`SHA ${pin.SHA_QUE_CONTEM_OS_BYTES}`);
    if (!/^sha256:[0-9a-f]{64}$/.test(pin.HASH)) bad.push('hash mal formado');
  }
  if (HS.DETERMINISTICO !== 'SIM — sem relógio, sem aleatório, chaves ordenadas') bad.push('o handoff não se declara determinístico');
  if (!HS.SOURCE_HEAD) bad.push('sem SOURCE_HEAD');
  if ((HS.PORTAL_NOW || []).length !== 1) bad.push(`PORTAL_NOW ${(HS.PORTAL_NOW || []).length}`);
  const az = (HS.ACHADOS || {})['01_AZOXISTROBINA_PROTIOCONAZOL'] || {};
  if (!/quatro registros/.test(az.FATO || '')) bad.push('o caso azoxi/protio não declara os quatro registos');
  if (!/31\/05\/2027/.test(az.FATO || '') || !/31\/03\/2028/.test(az.FATO || '')) bad.push('as duas datas não estão no facto');
  return { pass: !bad.length, expected: 0, measured: `pin 7501255 · SOURCE_HEAD ${String(HS.SOURCE_HEAD).slice(0, 7)}`, detail: bad };
});

check('ENRIQUECIMENTO_NAO_REDEFINE_BASE', 'neither enrichment moves a base universe', () => {
  const bad = [];
  const base = { RADAR: RF.TOTAL, CAMPO: SC_.TOTAL, FONTES: FO.TOTAL, FITO: FI.TOTAL };
  const crit = { RADAR: 45, CAMPO: 640, FONTES: 317, FITO: 560 };
  for (const k of Object.keys(crit)) if (base[k] !== crit[k]) bad.push(`${k} ${base[k]} != ${crit[k]}`);
  for (const f of ['IT-TOP3-SENSORES-V1.json', 'IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json']) {
    if (((PINS.PINS || {})[f] || {}).CLASSE !== 'ENRIQUECIMENTO') bad.push(`${f} não está classificado como enriquecimento`);
  }
  return { pass: !bad.length, expected: 0, measured: JSON.stringify(base), detail: bad };
});

check('UPSTREAM_PINS_SELF_VERIFY', 'every pinned artefact hashes to the hash it was pinned by', () => {
  const bad = [];
  /* O SHA que CONTEM os bytes nao e o SOURCE_HEAD que o artefacto DECLARA.
     MEDIDO neste lote: os quatro handoffs-base declaram 8c082f7 e vivem em
     032ebd1 — em 8c082f7 os mesmos nomes trazem ainda os carimbos antigos
     (5c2d47f, 1eda9b6) e outro hash. O primeiro pin que escrevi trocava um
     pelo outro.

         PINAR PELO QUE O FICHEIRO DIZ DE SI E PEDIR UMA COISA
         E DESCARREGAR OUTRA. O QUE SE PINA E O QUE SE PODE PROVAR. */
  const sha = (b) => 'sha256:' + crypto.createHash('sha256').update(b).digest('hex');
  const P = PINS.PINS || {};
  const nosDisco = fs.readdirSync(UP).filter((f) => f !== 'UPSTREAM-PINS.json');
  for (const f of nosDisco) if (!P[f]) bad.push(`${f} esta na pasta e nao esta pinado`);
  for (const [f, pin] of Object.entries(P)) {
    const abs = path.join(UP, f);
    if (!fs.existsSync(abs)) { bad.push(`${f} esta pinado e nao esta na pasta`); continue; }
    const real = sha(fs.readFileSync(abs));
    if (real !== pin.HASH) bad.push(`${f}: hash real ${real.slice(7, 23)} != pinado ${String(pin.HASH).slice(7, 23)}`);
    if (!/^[0-9a-f]{7,40}$/.test(pin.SHA_QUE_CONTEM_OS_BYTES || '')) bad.push(`${f} sem commit que contenha os bytes`);
    if (!pin.CAMINHO_NESSE_COMMIT) bad.push(`${f} sem caminho nesse commit`);
    if (!['BASE', 'ENRIQUECIMENTO'].includes(pin.CLASSE)) bad.push(`${f} sem classe`);
  }
  /* Controlo negativo: um byte a mais e o hash tem de deixar de bater. */
  const alvo = fs.readFileSync(path.join(UP, 'IT-TOP3-SENSORES-V1.json'));
  if (sha(Buffer.concat([alvo, Buffer.from(' ')])) === (P['IT-TOP3-SENSORES-V1.json'] || {}).HASH) {
    bad.push('CONTROLO NEGATIVO FALHOU: um byte a mais nao mudou o hash');
  }
  return { pass: !bad.length, expected: 0, measured: `${Object.keys(P).length} pinados · ${nosDisco.length} em disco · hashes refeitos`, detail: bad };
});

/* ── report ──────────────────────────────────────────────────────────────── */
const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
const pad = (s, n) => String(s).slice(0, n).padEnd(n);
console.log('\n  SINTONIA · LOTE COMPLETO · quatro bases + dois enriquecimentos');
console.log('  ' + '─'.repeat(118));
for (const r of results) {
  console.log(`  ${r.pass ? G + 'PASS' + X : R + 'FAIL' + X}  ${pad(r.id, 46)} ${pad(r.title, 46)} ${DIM}got${X} ${r.measured}`);
  if (!r.pass) for (const d of (Array.isArray(r.detail) ? r.detail : [r.detail]).slice(0, 6)) console.log(`        ${DIM}${String(d).slice(0, 150)}${X}`);
}
const ok = results.filter((r) => r.pass).length;
console.log('  ' + '─'.repeat(118));
console.log(`  ${ok}/${results.length} passing\n`);
process.exit(ok === results.length ? 0 : 1);
