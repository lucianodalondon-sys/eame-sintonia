#!/usr/bin/env node
/* SINTONIA · PORTAO DA CASA — a primeira dobra, medida onde ela e lida
   ---------------------------------------------------------------------------
   Uma HOME so mente de duas maneiras: mostrando um numero que nao e uma
   decisao, ou mostrando como certo aquilo que ainda nao aguenta peso. As duas
   sao invisiveis no codigo e obvias na tela.

       LER O FICHEIRO NAO E VER A PAGINA.

   Por isso este portao abre casa.html num browser de verdade, ABRE TODAS AS
   DOBRAS — portugues escondido atras de um <details> continua a chegar ao
   cliente, basta um clique — e mede o texto que fica visivel.

   O que ele nao deixa passar:
     · numero de acervo vendido como decisao (9.574, 624, 607, 560);
     · o Radar Futuro contado pelos 624 do inventario em vez dos 45 julgados;
     · AGIR_AGORA diferente de zero;
     · a populacao ITF- misturada com os ITFC-;
     · o derrubado renderizado;
     · a camada de evidencia com grelha propria;
     · um numero COM METODO sem o seu limite ao lado;
     · um sensor derrubado a aparecer como sensor;
     · prosa de investigacao portuguesa na tela italiana.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { PT_MARKERS } from './lang.mjs';

const require_ = createRequire(import.meta.url);
const { chromium } = require_('/opt/node22/lib/node_modules/playwright/index.js');

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..', '..');
const CLIENTE = path.join(RAIZ, 'italia-portale', 'client');
const UP = path.join(CLIENTE, 'upstream');
const J = (f) => JSON.parse(fs.readFileSync(path.join(UP, f), 'utf8'));

const RF = J('IT-FUTURO-HANDOFF-LINHA-B-V1.json');
const SC = J('IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json');
const FI = J('IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json');
const T3 = J('IT-TOP3-SENSORES-V1.json');
const HS = J('IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json');

const R = [];
const check = (id, fn) => { try { R.push({ id, ...fn() }); }
  catch (e) { R.push({ id, pass: false, detail: [`LANCOU: ${e.message}`] }); } };

const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const pg = await b.newPage({ viewport: { width: 1280, height: 1000 } });
const erros = [];
pg.on('pageerror', (e) => erros.push(e.message));
pg.on('console', (m) => { if (m.type() === 'error') erros.push(m.text()); });
await pg.goto('file://' + path.join(CLIENTE, 'casa.html'), { waitUntil: 'load' });
await pg.waitForTimeout(300);
/* fechada e aberta: o cliente ve as duas */
const fechada = await pg.evaluate(() => document.body.innerText);
await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => { d.open = true; }));
await pg.waitForTimeout(200);
const aberta = await pg.evaluate(() => document.body.innerText);
const CASA = await pg.evaluate(() => window.ITALY_CASA);
await b.close();

const temNum = (t, n) => new RegExp('(?<![\\d.,])' + n.toLocaleString('it-IT').replace('.', '[.\\s]?')
  + '(?![\\d.,])').test(t) || new RegExp('(?<![\\d.,])' + n + '(?![\\d.,])').test(t);

check('PAGINA_CARREGA_SEM_ERRO', () => ({
  pass: erros.length === 0, detail: erros.length ? erros : ['zero erros de JS'] }));

check('RADAR_ACT_NOW_ZERO', () => {
  const bad = [];
  if (RF.ACT_NOW !== 0) bad.push(`handoff diz ACT_NOW=${RF.ACT_NOW}`);
  if (CASA.RADAR_FUTURO.AGIR_AGORA !== 0) bad.push(`a casa diz ${CASA.RADAR_FUTURO.AGIR_AGORA}`);
  if (!/AGIRE ORA/i.test(fechada)) bad.push('a primeira dobra nao nomeia AGIRE ORA');
  return { pass: !bad.length, detail: bad.length ? bad : ['zero, e dito como decisao da regua'] };
});

check('RADAR_45_NOT_624', () => {
  const bad = [];
  if (RF.TOTAL !== 45) bad.push(`handoff TOTAL=${RF.TOTAL}`);
  if (temNum(aberta, 624) || temNum(aberta, 622)) bad.push('a tela mostra a contagem de acervo do Radar (624/622)');
  if (CASA.RADAR_FUTURO.PREPARAR + CASA.RADAR_FUTURO.MONITORAR !== RF.RENDERABLE)
    bad.push('preparar + monitorar nao fecha com os renderizaveis');
  return { pass: !bad.length, detail: bad.length ? bad
    : [`45 julgados, ${RF.RENDERABLE} renderizaveis = ${CASA.RADAR_FUTURO.PREPARAR}+${CASA.RADAR_FUTURO.MONITORAR}`] };
});

check('FIELD_VISIBLE_47', () => {
  const esperado = SC.RENDERABLE_CARD + SC.RENDERABLE_WITH_METHOD;
  const bad = [];
  if (esperado !== 47) bad.push(`o handoff da ${esperado}, nao 47`);
  if (CASA.SINAIS_DE_CAMPO.VISIVEIS !== esperado) bad.push('a casa discorda do handoff');
  if (temNum(aberta, SC.TOTAL)) bad.push(`a tela mostra o universo ${SC.TOTAL} como se fosse o visivel`);
  return { pass: !bad.length, detail: bad.length ? bad : [`${esperado} visiveis = 28 cartao + 19 com metodo`] };
});

check('PHYTOSANITARY_GRID_ZERO', () => {
  const bad = [];
  if (FI.RENDERABLE_CARD !== 0 || FI.RENDERABLE_WITH_METHOD !== 0)
    bad.push('a familia de evidencia traz cartoes');
  if (FI.EVIDENCE_ONLY !== 560) bad.push(`EVIDENCE_ONLY=${FI.EVIDENCE_ONLY}`);
  /* 560 pode aparecer — mas so dito como camada de evidencia, nunca como alerta */
  if (/560[^.]{0,40}(alert|avvis|segnal)/i.test(aberta)) bad.push('560 apresentado como alerta ou sinal');
  return { pass: !bad.length, detail: bad.length ? bad : ['560 so como camada de evidencia, zero grelha'] };
});

check('DROPPED_NOT_RENDERED', () => {
  const caidos = (RF.EXCLUIDOS || []).map((e) => e.ID);
  const bad = caidos.filter((id) => aberta.includes(id));
  return { pass: !bad.length, detail: bad.length ? [`derrubado na tela: ${bad}`]
    : [`${caidos.length} derrubado (${caidos}) fora da tela`] };
});

check('ITF_NOT_MIXED', () => {
  const itfc = (aberta.match(/ITFC-\d+/g) || []);
  const itf = (aberta.match(/(?<!ITFC-)\bITF-\d+/g) || []);
  return { pass: itf.length === 0, detail: itf.length ? [`populacao ITF- na tela: ${itf}`]
    : [`${new Set(itfc).size} ids, todos ITFC-`] };
});

check('EVIDENCE_ONLY_NOT_PROMOTED', () => {
  const bad = [];
  const proibidos = [[9574, 'acervo inteiro'], [607, 'oportunidades'], [6249, 'rotulos']];
  for (const [n, o] of proibidos) if (temNum(aberta, n)) bad.push(`${n} (${o}) na tela`);
  if (!/evidenza/i.test(aberta)) bad.push('a camada de evidencia nao e nomeada como evidencia');
  return { pass: !bad.length, detail: bad.length ? bad : ['nenhum numero de acervo vendido como decisao'] };
});

check('PORTAL_WITH_METHOD_HAS_LIMIT', () => {
  const bad = [];
  /* Cada bloco COM METODO tem de trazer o seu limite no MESMO artefacto.
     A primeira versao disto media o COMPRIMENTO do limite e reprovou FONTES,
     cujo limite — «qui c'e un problema» — tem dezanove caracteres e e o mais
     afiado dos cinco. Medir prosa por regua nao mede nada: o que se exige e
     que o campo exista, e que FONTES traga o PAR, porque o valor dela esta na
     diferenca entre o que a mapa responde e o que nunca responde. */
  for (const [k, o] of Object.entries({
    SINAIS_DE_CAMPO: CASA.SINAIS_DE_CAMPO, FONTES: CASA.FONTES,
    AUTORIZACOES: CASA.AUTORIZACOES, REVOGADO_X_SCADUTO: CASA.REVOGADO_X_SCADUTO,
    RADAR_FUTURO: CASA.RADAR_FUTURO })) {
    if (!o.LIMITE || !String(o.LIMITE).trim()) bad.push(`${k} sem limite declarado`);
  }
  if (!CASA.FONTES.RESPONDE) bad.push('FONTES sem o que a cobertura RESPONDE');
  if (CASA.FONTES.RESPONDE === CASA.FONTES.LIMITE) bad.push('FONTES: responde e limite sao a mesma frase');
  if (!/Non risponde mai/i.test(aberta)) bad.push('a cobertura nao diz o que NAO responde');
  if (!/Non è quota di mercato|non e quota di mercato/i.test(aberta))
    bad.push('a contagem de autorizacoes nao nega quota de mercado');
  return { pass: !bad.length, detail: bad.length ? bad : ['cada numero com metodo traz o seu limite'] };
});

check('HUMAN_SENSORS_HASH_MATCH', () => {
  const decl = CASA.HASHES_CONSUMIDOS['IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json'];
  const AUT = 'sha256:1283b4f7a292798f19a964421966316603e7c25aaa9d5b52aa7764bba74ec560';
  return { pass: decl === AUT,
    detail: [decl === AUT ? `pin 7501255 · ${AUT.slice(0, 24)}…` : `declarado ${decl}, autorizado ${AUT}`] };
});

check('TOP3_ONLY_SURVIVORS_RENDERED', () => {
  const vivos = T3.ROWS.filter((r) => r.EXECUTABILITY === 'EXECUTAVEL_COM_ADAPTADOR').map((r) => r.SIGNAL_ID);
  const mortos = T3.ROWS.filter((r) => r.EXECUTABILITY !== 'EXECUTAVEL_COM_ADAPTADOR').map((r) => r.SIGNAL_ID);
  const bad = [];
  if (CASA.SENSORES.SOBREVIVERAM.length !== vivos.length) bad.push('contagem de sobreviventes diverge');
  for (const id of mortos) {
    /* o derrubado PODE aparecer — mas so etiquetado como nao executavel */
    const i = aberta.indexOf(id);
    if (i < 0) continue;
    const volta = aberta.slice(Math.max(0, i - 120), i + 40);
    if (!/NON ESEGUIBILE/i.test(volta)) bad.push(`${id} aparece sem a etiqueta de nao executavel`);
  }
  for (const s of CASA.SENSORES.SOBREVIVERAM) {
    for (const f of ['VARIAVEL', 'FONTE', 'CADENZA', 'SCATTA', 'INVALIDA'])
      if (!s[f]) bad.push(`${s.ID} sem ${f}`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${vivos.length} sobrevivente (${vivos}) como sensor; ${mortos.length} derrubados (${mortos}) etiquetados`] };
});

check('NENHUMA_PROSA_PORTUGUESA_NA_TELA', () => {
  const bad = [];
  for (const m of PT_MARKERS) {
    const re = new RegExp('(?<!\\p{L})' + m.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?!\\p{L})', 'giu');
    const h = aberta.match(re);
    if (h) bad.push(`${m} ×${h.length}`);
  }
  return { pass: !bad.length, detail: bad.length ? bad : ['zero marcadores, com todas as dobras abertas'] };
});

check('NAO_SEI_NAO_VIRA_AFIRMACAO', () => {
  const bad = [];
  /* o sensor NAO_EXECUTAVEL de ITFC-018 nasce de um NAO SEI de acesso; se a tela
     o disser como "nao existe", promoveu ausencia de leitura a facto */
  if (/non esiste/i.test(aberta) && !/NON SO/i.test(aberta))
    bad.push('«non esiste» sem o NON SO ao lado');
  if (CASA.SENSORES.DERRUBADOS.some((s) => !s.CAIU_PORQUE)) bad.push('derrubado sem o porque');
  return { pass: !bad.length, detail: bad.length ? bad : ['ausencia de leitura dita como NON SO, nao como ausencia no mundo'] };
});

check('DO_NOT_SHOW_NAO_DIZER_AUSENTE_DA_CASA', () => {
  /* A verificacao literal do lote corre sobre portale.html — readPortal() le so
     esse ficheiro. A casa e uma superficie NOVA, e a mais vista de todas: sem
     isto, as frases proibidas ficavam testadas na tela antiga e livres na
     primeira dobra.

     A lista nao e copiada de lado nenhum: le-se do proprio handoff, que e o
     dono. Copia-la para aqui faria dela duas listas, e duas listas divergem. */
  const regras = HS.DO_NOT_SHOW || [];
  const bad = [];
  if (regras.length !== 14) bad.push(`o handoff traz ${regras.length} regras, nao 14`);
  for (const r of regras) {
    if (r.NAO_DIZER && aberta.toLowerCase().includes(String(r.NAO_DIZER).toLowerCase()))
      bad.push(`a casa diz «${r.NAO_DIZER}» (${r.ACHADO})`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${regras.length} formulacoes proibidas, nenhuma presente com todas as dobras abertas`] };
});

/* ── os dados que chegam ao browser, e de onde eles saem ─────────────────── */
check('CASA_HASHES_6_OF_6_MATCH_PINS_AND_DISK', () => {
  /* A casa declara seis hashes consumidos e o portao verificava UM. Cinco
     declaracoes que ninguem confere sao cinco lugares onde um insumo podia ter
     sido trocado sem que nada aqui mudasse de cor.

         UM HASH DECLARADO E UMA AFIRMACAO. SO REFAZE-LO E QUE E PROVA.

     Cada um e conferido DUAS vezes, contra coisas diferentes: contra o pin
     (foi este o artefacto que autorizamos?) e contra os bytes em disco (e este
     o artefacto que esta aqui agora?). Bater so no pin provaria que copiamos a
     tabela certa; bater so no disco provaria que lemos o que la esta. */
  const PINS = J('UPSTREAM-PINS.json').PINS || {};
  const decl = CASA.HASHES_CONSUMIDOS || {};
  const bad = [];
  const nomes = Object.keys(decl).sort();
  if (nomes.length !== 6) bad.push(`a casa declara ${nomes.length} hashes, nao 6`);
  for (const n of nomes) {
    const pin = (PINS[n] || {}).HASH;
    if (!pin) { bad.push(`${n}: consumido pela casa e NAO esta pinado`); continue; }
    if (pin !== decl[n]) bad.push(`${n}: a casa diz ${decl[n].slice(0, 22)}…, o pin diz ${pin.slice(0, 22)}…`);
    const f = path.join(UP, n);
    if (!fs.existsSync(f)) { bad.push(`${n}: pinado e ausente do disco`); continue; }
    const disco = 'sha256:' + crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
    if (disco !== decl[n]) bad.push(`${n}: os bytes em disco dao ${disco.slice(0, 22)}…`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${nomes.length}/6 refeitos contra o pin E contra os bytes em disco`] };
});

check('BROWSER_DATA_ONLY_AUTHORIZED_DESTINATIONS', () => {
  /* Nao basta que a TELA nao mostre um derrubado: o ficheiro que o browser
     carrega tambem nao pode carrega-lo. Um id que viaja no dado e so nao e
     desenhado hoje continua a uma linha de CSS de ser visto.

         NAO RENDERIZADO NAO E O MESMO QUE NAO ENTREGUE.

     Os tres ITFC- que a casa carrega tem de estar todos entre os 44
     RENDERIZAVEIS do handoff do radar, e nenhum entre os EXCLUIDOS. */
  const idDe = (x) => (typeof x === 'string' ? x : (x && (x.ID || x.id)) || null);
  const rend = new Set((RF.RENDERIZAVEIS || []).map(idDe).filter(Boolean));
  const excl = new Set((RF.EXCLUIDOS || []).map(idDe).filter(Boolean));
  const noDado = [...new Set((fs.readFileSync(path.join(CLIENTE, 'italy-casa.js'), 'utf8')
    .match(/ITFC-\d+/g) || []))].sort();
  const bad = [];
  for (const id of noDado) {
    if (excl.has(id)) bad.push(`${id} esta entre os EXCLUIDOS e viaja no dado do browser`);
    else if (!rend.has(id)) bad.push(`${id} viaja no dado e nao esta entre os RENDERIZAVEIS`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${noDado.length} ids no dado (${noDado.join(', ')}), todos entre os ${rend.size} renderizaveis`] };
});

/* ── um nome, um universo ────────────────────────────────────────────────── */
/* O menu do portal chamava «Radar Futuro» a tres registos IT-FUT- do pacote V21,
   e «Fonti» a 189 SRC_ sem AUTHORITY_CLASS nem COLLECTABILITY. A casa chama
   «Radar Futuro» aos 45 ITFC e «fonti con metodo» as 91. Interseccao de IDs: ZERO
   nos dois casos — sao universos disjuntos com o mesmo nome, a um clique.

       O CLIENTE NAO PODE CLICAR NUM NOME E CAIR NOUTRO UNIVERSO.

   Isto nao renomeia dados nem apaga populacoes: exige so que dois universos
   distintos nao partilhem o nome na navegacao. */
check('CANONICAL_LABEL_COLLISION', () => {
  const i18n = fs.readFileSync(path.join(CLIENTE, 'italy-i18n.js'), 'utf8');
  const rot = (chave) => [...i18n.matchAll(new RegExp(`${chave}:\\s*'([^']+)'`, 'g'))].map((m) => m[1]);
  const bad = [];
  const nomesDaCasa = ['Radar Futuro', 'Future Radar'];
  for (const r of rot('navFuture'))
    if (nomesDaCasa.some((n) => r.toLowerCase() === n.toLowerCase()))
      bad.push(`navFuture continua a chamar-se «${r}», o nome do universo canonico dos ITFC`);
  for (const r of rot('navSources'))
    if (/^(fonti|sources)$/i.test(r.trim()))
      bad.push(`navSources continua a chamar-se «${r}» ao lado das 91 fonti con metodo`);
  return { pass: !bad.length, detail: bad.length ? bad
    : [`navFuture = ${rot('navFuture').join(' / ')}`, `navSources = ${rot('navSources').join(' / ')}`,
       'RADAR_LABEL_COLLISION = ZERO · FONTI_LABEL_COLLISION = ZERO'] };
});

/* ── os 8 literais, tambem em italiano ───────────────────────────────────── */
/* As regras DO_NOT_SHOW foram escritas em portugues, e a tela e italiana. Testar
   so a string portuguesa e testar uma frase que nunca poderia aparecer: o portao
   fica verde por construcao. Aqui declara-se, para cada regra, a AFIRMACAO
   ITALIANA equivalente — a forma que a superficie realmente usaria — e testa-se
   essa.

       UM CONTROLO QUE SO CONHECE A LINGUA ERRADA NAO E UM CONTROLO.

   Nao e revisao semantica: sao formulacoes literais, so na lingua da tela. */
const LITERAIS_IT = [
  { PT: '0 legendas', IT: ['0 sottotitoli', 'nessun sottotitolo', 'zero sottotitoli'] },
  { PT: 'ADAMA possui 155 autorizações', IT: ['ADAMA possiede 155', 'ADAMA ha 155 autorizzazioni'] },
  { PT: '114 pessoas', IT: ['114 persone'] },
  { PT: 'temos agrônomos e produtores na base', IT: ['abbiamo agronomi e produttori'] },
  { PT: 'cobertura BOA em 72 células', IT: ['copertura BUONA in 72', 'copertura buona in 72 celle'] },
  { PT: 'há problema nesta região', IT: ['c\'è un problema in questa regione', 'qui c\'è un problema in'] },
  { PT: '61 documentos relevantes', IT: ['61 documenti rilevanti'] },
  { PT: 'oportunidade / espaço livre / ativo subutilizado', IT: ['spazio libero', 'attivo sottoutilizzato'] },
];

check('LITERAL_IT_CONTROL', () => {
  const bad = [];
  if (LITERAIS_IT.length !== 8) bad.push(`a lista italiana tem ${LITERAIS_IT.length}, nao 8`);
  const baixo = aberta.toLowerCase();
  for (const r of LITERAIS_IT) {
    for (const f of r.IT) if (baixo.includes(f.toLowerCase())) bad.push(`a casa diz «${f}»`);
  }
  /* CONTROLO NEGATIVO: se injectar uma destas frases no texto medido nao fizer
     falhar, o teste nao esta a medir nada. */
  const envenenado = (aberta + '\n' + LITERAIS_IT[4].IT[0]).toLowerCase();
  const apanha = LITERAIS_IT.some((r) => r.IT.some((f) => envenenado.includes(f.toLowerCase())));
  if (!apanha) bad.push('CONTROLO NEGATIVO FALHOU: a frase injectada nao foi apanhada');
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${LITERAIS_IT.reduce((a, r) => a + r.IT.length, 0)} formulacoes italianas testadas em 8 regras`,
       'controlo negativo: a frase injectada FOI apanhada'] };
});

const mau = R.filter((r) => !r.pass);
console.log('\n  SINTONIA · PORTAO DA CASA — a primeira dobra medida no browser');
console.log('  ' + '─'.repeat(92));
for (const r of R) {
  console.log(`  ${r.pass ? 'PASS' : 'FAIL'}  ${r.id}`);
  for (const d of r.detail || []) console.log(`        ${d}`);
}
console.log('  ' + '─'.repeat(92));
console.log(`  ${mau.length ? 'FAIL' : 'PASS'} — ${R.length - mau.length}/${R.length}\n`);
process.exit(mau.length ? 1 : 0);
