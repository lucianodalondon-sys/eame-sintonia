#!/usr/bin/env node
/* SINTONIA · D97 · O QUE O CASCO DESENHA VEIO DA INTELLIGENCE?
   ---------------------------------------------------------------------------
   A pergunta do dono (27/09): «tudo esta passando pelo processo correto?
   coleta, inteligencia e casco? nao tem nada se cruzando e indo pro casco so
   pra encher ele?»

   A lei D97: o casco mostra SO o que a Intelligence produziu (o pote). Este
   portao mede tres coisas, no sandbox que os testes do portal usam, com o pote
   publicado da rodada 7 carregado como a Vercel o serve:

     1 · OBJETOS — todo objeto do pote R7 diz ESPECIE_DITA_POR = INTELLIGENCE,
         e a PROVA dele tem ITEM_ID, RAW_OBSERVATION_ID, SOURCE_ID, DOCUMENT_ID,
         CORRIDA_UPSTREAM e URL navegavel, da MESMA corrida?
     2 · CRUZAMENTOS — dos cruzamentos que o Portafoglio desenha (ANALISE-R7),
         quantos sao OBJETO do pote e quantos o pote RECUSOU ou nem conhece?
         Um cruzamento desenhado que o pote recusou por PROVA_INCOMPLETA e um
         cruzamento no casco sem a prova que o proprio pote exige.
     3 · ROTAS — com o pote carregado, que rotas continuam a desenhar o legado
         (V2.1, demo, snapshot de 07/09) em vez do pote?

   Nao conserta nada: mede e lista, com ficheiro:linha. Sai 1 enquanto houver
   rota de legado alcancavel com o pote, porque isso E uma violacao da D97 —
   dizer PASS por omissao seria o verde falso que esta casa nao pode dar.

   AJUSTE DECLARADO (missao CASCO-HOJE-MINIMO-HONESTO, item 9: «0 objetos fora
   do pote e 0 cruzamentos sem prova NA TELA»). A medida 2 contava os 86 da
   ANALISE-R7 como «desenhados» porque a tela os desenhava todos. Agora mede o
   que a tela PRINCIPAL do Portafoglio desenha (potePub.cruz.principais, do
   proprio casco montado); os 84 da aba «rifiutati» continuam contados e
   listados, a parte, com o motivo — nao sumiram, so deixaram de ser resultado.
   A medida 3 passa a reconhecer as duas leituras que NAO sao legado: a busca
   nos objetos do pote (buscaNoPote) e a Label Intelligence como PRODUTO DE
   FERRAMENTA registado pelo publicador (temLabelFerramenta). A medida 4 e nova:
   pote esperado e ausente -> nenhuma rota desenha legado nem demo.

       node italia-portale/audit/casco/d97-auditoria.mjs [--json]            */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { mount, CLIENT } from '../lib/harness.mjs';

const RAIZ = path.resolve(CLIENT, '..', '..');
const POTE_F = 'docs/casco/r7/POTE-R7.json';
const ANALISE_F = 'docs/casco/r7/ANALISE-R7.json';
const PORTAL_F = 'italia-portale/client/portale.html';
const ler = (p) => fs.readFileSync(path.join(RAIZ, p), 'utf8');
const linhaDe = (texto, agulha) => { const i = texto.split('\n').findIndex((l) => l.includes(agulha)); return i < 0 ? null : i + 1; };

/* ── 1 · objetos ─────────────────────────────────────────────────────── */
export function objetos(pote, texto) {
  const run = pote.INTELLIGENCE_RUN_ID, out = [];
  let n = 0;
  for (const [k, e] of Object.entries(pote.COMPARTIMENTOS || {})) {
    for (const o of e.OBJETOS || []) {
      n++;
      const porque = [];
      if (o.ESPECIE_DITA_POR !== 'INTELLIGENCE') porque.push('ESPECIE_DITA_POR=' + o.ESPECIE_DITA_POR);
      if (!(o.PROVA || []).length) porque.push('sem PROVA');
      for (const q of o.PROVA || []) {
        for (const f of ['ITEM_ID', 'RAW_OBSERVATION_ID', 'SOURCE_ID', 'DOCUMENT_ID', 'CORRIDA_UPSTREAM']) {
          if (q[f] === undefined || q[f] === null || q[f] === '' || q[f] === 'NAO SEI') porque.push('PROVA.' + f + ' vazio');
        }
        if (!/^https?:\/\//.test(String(q.URL || ''))) porque.push('PROVA.URL nao navegavel');
        if (q.INTELLIGENCE_RUN_ID !== run) porque.push('PROVA de outra corrida');
      }
      if (o.CORRIDA_SINTETICA !== false) porque.push('CORRIDA_SINTETICA nao e false');
      if (porque.length) out.push({ COMPARTIMENTO: k, OBJETO_ID: o.OBJETO_ID, ONDE: `${POTE_F}:${linhaDe(texto, `"OBJETO_ID": "${o.OBJETO_ID}"`)}`, PORQUE: [...new Set(porque)] });
    }
  }
  /* n conta gavetas; o mesmo objeto em duas gavetas e UM objeto (a tela conta os distintos). */
  const distintos = new Set(Object.values(pote.COMPARTIMENTOS || {}).flatMap((e) => (e.OBJETOS || []).map((o) => o.OBJETO_ID))).size;
  return { TOTAL: n, DISTINTOS: distintos, FORA_DA_INTELLIGENCE_OU_SEM_PROVA: out };
}

/* ── 2 · cruzamentos ─────────────────────────────────────────────────── */
export function cruzamentos(pote, analise, texto, naTela) {
  const noPote = new Set(((pote.COMPARTIMENTOS.portfolio || {}).OBJETOS || []).map((o) => o.OBJETO_ID));
  const rec = new Map((pote.RECUSADOS || []).filter((r) => r.COMPARTIMENTO === 'portfolio').map((r) => [r.OBJETO_ID, r]));
  const linhas = (analise.CROSSINGS || []).map((c) => {
    const r = rec.get(c.OBJETO_ID);
    const destino = noPote.has(c.OBJETO_ID) ? 'OBJETO_DO_POTE' : r ? 'RECUSADO_PELO_POTE' : 'AUSENTE_DO_POTE';
    return { OBJETO_ID: c.OBJETO_ID, ESTADO_R7: c.ESTADO_R7, VIA: c.VIA, DESTINO_NO_POTE: destino,
      MOTIVO: r ? `${r.MOTIVO}: ${r.DETALHE}` : null, ONDE: `${ANALISE_F}:${linhaDe(texto, `"OBJETO_ID": "${c.OBJETO_ID}"`)}`,
      URL: c.URL || null, SALA_CHAVE: c.SALA_CHAVE || null };
  });
  const conta = (f) => linhas.reduce((o, x) => { o[f(x)] = (o[f(x)] || 0) + 1; return o; }, {});
  const tela = new Set(naTela || []);
  const naTelaPrincipal = linhas.filter((x) => tela.has(x.OBJETO_ID));
  return { DA_ANALISE: linhas.length, DESENHADOS: naTelaPrincipal.length, POR_DESTINO: conta((x) => x.DESTINO_NO_POTE),
    POR_MOTIVO: conta((x) => x.MOTIVO || x.DESTINO_NO_POTE),
    NA_ABA_RIFIUTATI: linhas.filter((x) => !tela.has(x.OBJETO_ID)).length,
    SEM_A_PROVA_QUE_O_POTE_EXIGE: naTelaPrincipal.filter((x) => x.DESTINO_NO_POTE !== 'OBJETO_DO_POTE'),
    /* um id na tela que a analise nem conhece tambem e cruzamento sem prova */
    NA_TELA_FORA_DA_ANALISE: [...tela].filter((id) => !linhas.some((x) => x.OBJETO_ID === id)) };
}

/* ── 3 · rotas ───────────────────────────────────────────────────────── */
const VISTAS = ['meeting', 'radar', 'msignals', 'mradar', 'mcase', 'radarfuturo', 'future', 'windows', 'window', 'market',
  'voices', 'competitors', 'company', 'cproduct', 'event', 'science', 'theme', 'person', 'portfolio', 'product', 'etichette',
  'etichetta', 'archive', 'sources', 'source', 'signal', 'case', 'brief', 'field', 'search'];
function montar() {
  const M = mount({});
  M.ctx.location = { search: '', hash: '' };
  for (const f of ['sintonia-pote-publicado.js', 'sintonia-pote-casco.js', 'sintonia-pote-publicacao.js']) {
    vm.runInContext(fs.readFileSync(path.join(CLIENT, f), 'utf8'), M.ctx, { filename: f });
  }
  return M;
}
/* O que a tela principal do Portafoglio desenha, lido do casco montado. */
export function cruzamentosNaTela() {
  const M = montar();
  const x = M.vals({ view: 'portfolio', lang: 'it' });
  return ((x.potePub || {}).cruz || {}).principais ? x.potePub.cruz.principais.map((c) => c.id) : [];
}
export function rotas() {
  const M = montar();
  const html = ler(PORTAL_F);
  const legado = [], pote = [];
  for (const v of VISTAS) {
    const x = M.vals({ view: v, lang: 'it', committedQuery: 'vite', query: 'vite' });
    /* O que e do pote nao conta como legado: a busca nos objetos do pote e a Label Intelligence registada
       como produto de ferramenta. Qualquer OUTRA bandeira acesa numa rota do pote e legado ao lado dele. */
    const permitido = (k) => k === 'isOrgs' || (k === 'isSearch' && x.buscaNoPote) ||
      ((k === 'isEtichette' || k === 'isEtichetta') && x.temLabelFerramenta);
    const flags = Object.keys(x).filter((k) => /^is[A-Z]/.test(k) && x[k] === true && !permitido(k));
    if ((x.poteVista || x.potePubVista || x.temLabelFerramenta || x.buscaNoPote) && !flags.length) { pote.push(v); continue; }
    if (!flags.length) continue; /* nada desenhado para este estado (ex.: brief sem caso) */
    const r = { ROTA: v, BANDEIRAS_DE_LEGADO_ACESAS: flags };
    if (v === 'search') {
      r.EXEMPLO = `busca «vite»: ${x.searchTotal} resultados do modelo legado (${(x.searchGroups || []).map((g) => `${g.label} ${g.count}`).join(' · ')})`;
      r.ONDE = [`${PORTAL_F}:${linhaDe(html, 'const sPool = ')}`, `${PORTAL_F}:${linhaDe(html, 'onQueryKey: (e) =>')}`];
    }
    legado.push(r);
  }
  return { ROTAS_DO_POTE: pote, ROTAS_DE_LEGADO_COM_O_POTE: legado,
    PORQUE: `${PORTAL_F}:${linhaDe(html, 'static FLAGS_DO_LEGADO')} — a lista das bandeiras que o pote desliga nao inclui a busca nem as vistas de detalhe`,
    COMO_SE_CHEGA: 'a barra de busca esta sempre visivel; cada linha do resultado abre a vista de detalhe do registo legado' };
}

/* ── 4 · pote esperado e ausente ──────────────────────────────────────── */
export function semPote() {
  const M = mount({});
  M.ctx.location = { search: '', hash: '' };
  /* a pagina pede o pote (a tag esta no documento), e ele nao chegou */
  M.ctx.document.querySelector = (q) => (/sintonia-pote-publicado\.js/.test(String(q)) ? {} : null);
  for (const f of ['sintonia-pote-casco.js', 'sintonia-pote-publicacao.js']) {
    vm.runInContext(fs.readFileSync(path.join(CLIENT, f), 'utf8'), M.ctx, { filename: f });
  }
  const legado = [];
  for (const v of VISTAS) {
    const x = M.vals({ view: v, lang: 'it', committedQuery: 'vite', query: 'vite' });
    const flags = Object.keys(x).filter((k) => /^is[A-Z]/.test(k) && x[k] === true && k !== 'isOrgs');
    if (flags.length) legado.push({ ROTA: v, BANDEIRAS_DE_LEGADO_ACESAS: flags });
  }
  return { ROTAS_DE_LEGADO_SEM_POTE: legado };
}

export function auditar() {
  const tp = ler(POTE_F), ta = ler(ANALISE_F);
  const pote = JSON.parse(tp), analise = JSON.parse(ta);
  return { SCHEMA: 'AUDITORIA_D97/v1', POTE: POTE_F, CORRIDA: pote.INTELLIGENCE_RUN_ID,
    OBJETOS: objetos(pote, tp), CRUZAMENTOS: cruzamentos(pote, analise, ta, cruzamentosNaTela()), ROTAS: rotas(), SEM_POTE: semPote() };
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  const A = auditar();
  if (process.argv.includes('--json')) { process.stdout.write(JSON.stringify(A, null, 1) + '\n'); }
  else {
    console.log(`  1 · objetos do pote ${A.CORRIDA}: ${A.OBJETOS.DISTINTOS} distintos (${A.OBJETOS.TOTAL} lugares em gavetas); fora da Intelligence ou sem prova: ${A.OBJETOS.FORA_DA_INTELLIGENCE_OU_SEM_PROVA.length}`);
    for (const o of A.OBJETOS.FORA_DA_INTELLIGENCE_OU_SEM_PROVA) console.log(`      ${o.ONDE} ${o.OBJETO_ID} · ${o.PORQUE.join(', ')}`);
    console.log(`  2 · cruzamentos na tela principal: ${A.CRUZAMENTOS.DESENHADOS}; sem a prova que o pote exige: ${A.CRUZAMENTOS.SEM_A_PROVA_QUE_O_POTE_EXIGE.length + A.CRUZAMENTOS.NA_TELA_FORA_DA_ANALISE.length} · na aba rifiutati: ${A.CRUZAMENTOS.NA_ABA_RIFIUTATI} de ${A.CRUZAMENTOS.DA_ANALISE} da analise · ${JSON.stringify(A.CRUZAMENTOS.POR_DESTINO)}`);
    for (const [k, v] of Object.entries(A.CRUZAMENTOS.POR_MOTIVO)) console.log(`      ${v} · ${k}`);
    console.log(`  3 · rotas que desenham o pote: ${A.ROTAS.ROTAS_DO_POTE.length}; rotas de LEGADO com o pote carregado: ${A.ROTAS.ROTAS_DE_LEGADO_COM_O_POTE.length}`);
    for (const r of A.ROTAS.ROTAS_DE_LEGADO_COM_O_POTE) console.log(`      ${r.ROTA} (${r.BANDEIRAS_DE_LEGADO_ACESAS.join(',')})${r.EXEMPLO ? ' · ' + r.EXEMPLO : ''}`);
    if (A.ROTAS.ROTAS_DE_LEGADO_COM_O_POTE.length) console.log(`      porque: ${A.ROTAS.PORQUE}`);
    console.log(`  4 · pote esperado e ausente: rotas que desenham legado ou demo: ${A.SEM_POTE.ROTAS_DE_LEGADO_SEM_POTE.length}`);
    for (const r of A.SEM_POTE.ROTAS_DE_LEGADO_SEM_POTE) console.log(`      ${r.ROTA} (${r.BANDEIRAS_DE_LEGADO_ACESAS.join(',')})`);
  }
  process.exit(A.ROTAS.ROTAS_DE_LEGADO_COM_O_POTE.length || A.OBJETOS.FORA_DA_INTELLIGENCE_OU_SEM_PROVA.length ||
    A.CRUZAMENTOS.SEM_A_PROVA_QUE_O_POTE_EXIGE.length || A.CRUZAMENTOS.NA_TELA_FORA_DA_ANALISE.length ||
    A.SEM_POTE.ROTAS_DE_LEGADO_SEM_POTE.length ? 1 : 0);
}
