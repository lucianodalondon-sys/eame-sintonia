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
import vm from 'node:vm';
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { PT_MARKERS } from './lang.mjs';
/* UM DETECTOR, E UMA SO VEZ. A regra de negacao — e a propriedade de que
   a negacao da frase ANTERIOR nao absolve a afirmacao seguinte — vive em
   audit/do-not-show.mjs, partilhada com lote-completo.mjs. Duas copias da
   mesma lei divergem, e a que divergir para o lado permissivo passa a dar
   PASS sem nunca ter disparado. */
import { medir, controloNegativo, QA } from './do-not-show.mjs';

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

/* O artefacto que o browser carrega, lido como o browser o le: executando-o. */
const embarcadoV21 = () => {
  const g = { window: {} };
  vm.createContext(g);
  vm.runInContext(fs.readFileSync(path.join(CLIENTE, 'italy-handoff-v21.js'), 'utf8'), g);
  return g.window.ITALY_HANDOFF_V21 || {};
};
const HS = J('IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json');

const R = [];
const check = (id, fn) => { try { R.push({ id, ...fn() }); }
  catch (e) { R.push({ id, pass: false, detail: [`LANCOU: ${e.message}`] }); } };

const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const pg = await b.newPage({ viewport: { width: 1280, height: 1000 } });
const erros = [];
pg.on('pageerror', (e) => erros.push(e.message));
pg.on('console', (m) => { if (m.type() === 'error') erros.push(m.text()); });
/* A LINGUA E UM ESTADO DA SUPERFICIE, NAO UM FICHEIRO A PARTE.
   A casa desenha-se em italiano e em ingles a partir do MESMO pacote. Medir
   so o italiano deixaria metade do ecra por medir — e e a metade em que um
   codigo sem frase inglesa apareceria primeiro.

       UMA SUPERFICIE BILINGUE MEDIDA NUMA LINGUA E UMA SUPERFICIE MEDIDA A METADE. */
const abrirTudo = async () => {
  /* Uma dobra pode conter outra: abre-se ate nao aparecerem mais. */
  for (let i = 0; i < 6; i++) {
    const n = await pg.evaluate(() => {
      const d = [...document.querySelectorAll('details')].filter((x) => !x.open);
      d.forEach((x) => { x.open = true; });
      return d.length;
    });
    if (!n) break;
    await pg.waitForTimeout(120);
  }
};
const trocarLingua = async (lg) => {
  await pg.evaluate((l) => {
    const b = document.querySelector(`[data-lang="${l}"]`);
    if (!b) throw new Error(`sem botao de lingua ${l}`);
    b.click();
  }, lg);
  await pg.waitForTimeout(250);
};

await pg.addInitScript(() => { try { localStorage.removeItem('sintonia.casa.lang'); } catch (e) {} });
await pg.goto('file://' + path.join(CLIENTE, 'casa.html'), { waitUntil: 'load' });
await pg.waitForTimeout(300);
/* fechada e aberta: o cliente ve as duas */
const fechada = await pg.evaluate(() => document.body.innerText);
await abrirTudo();
const aberta = await pg.evaluate(() => document.body.innerText);
const CASA = await pg.evaluate(() => window.ITALY_CASA);
/* Contagens medidas NO DOM, nao no dado: um cartao que o dado traz e o ecra
   nao desenha continua a nao existir para quem le. */
const lerDom = () => pg.evaluate(() => {
  const casos = [...document.querySelectorAll('[data-caso]')];
  const txt = document.body.innerText;
  return {
    casos: casos.length,
    estados: casos.map((e) => e.getAttribute('data-stato')),
    /* Cada caso tem de ter as sete seccoes do L2 e uma dobra de L3 dentro. */
    seccoes: casos.map((e) => e.querySelectorAll(':scope > .dd > .sec').length),
    comL3: casos.filter((e) => e.querySelector(':scope > .dd > details')).length,
    /* O registo dos 44, medido no DOM e nao no dado. */
    ledger: [...document.querySelectorAll('table tbody tr')]
      .map((r) => (r.cells[0] ? r.cells[0].innerText.trim() : ''))
      .filter((v) => /^ITFC-\d+/.test(v)).map((v) => v.slice(0, 8)),
    /* Buracos de etiqueta: `tt()` desenha [codigo] quando o par falta. */
    buracos: (txt.match(/\[[A-Za-z][A-Za-z0-9_]{3,}\]/g) || []),
    objetos: (txt.match(/\[object Object\]/g) || []).length,
    htmlLang: document.documentElement.lang,
    texto: txt,
  };
});
const domIT = await lerDom();
await trocarLingua('en');
await abrirTudo();
const abertaEN = await pg.evaluate(() => document.body.innerText);
const domEN = await lerDom();
/* Larguras reais. O scroll horizontal a 390px nao se ve num viewport de 1280. */
const larguras = {};
for (const [nome, w] of [['desktop1440', 1440], ['mobile390', 390]]) {
  await pg.setViewportSize({ width: w, height: 900 });
  await pg.waitForTimeout(150);
  larguras[nome] = await pg.evaluate(() => ({
    scrollW: document.documentElement.scrollWidth,
    clientW: document.documentElement.clientWidth,
  }));
}
await pg.setViewportSize({ width: 1280, height: 1000 });
await trocarLingua('it');
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
    /* O limite viaja em PAR: uma metade em falta e meia cautela, e meia
       cautela numa lingua e nenhuma cautela para quem le nessa lingua. */
    for (const lg of ['it', 'en']) {
      if (!o.LIMITE || !o.LIMITE[lg] || !String(o.LIMITE[lg]).trim()) bad.push(`${k} sem limite declarado em ${lg}`);
    }
  }
  for (const lg of ['it', 'en']) {
    if (!CASA.FONTES.RESPONDE || !CASA.FONTES.RESPONDE[lg]) bad.push(`FONTES sem o que a cobertura RESPONDE em ${lg}`);
    else if (CASA.FONTES.RESPONDE[lg] === CASA.FONTES.LIMITE[lg]) bad.push(`FONTES (${lg}): responde e limite sao a mesma frase`);
  }
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
  /* NAS DUAS LINGUAS. A prosa de investigacao e portuguesa, e a superficie
     inglesa e tao capaz de a deixar passar como a italiana — mais, ate: quem
     revê o italiano olha para cada frase, quem revê o inglês tende a assumir
     que ja foi vista uma vez. */
  const bad = [];
  for (const [lg, txt] of [['it', aberta], ['en', abertaEN]]) {
    for (const m of PT_MARKERS) {
      const re = new RegExp('(?<!\\p{L})' + m.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?!\\p{L})', 'giu');
      const h = txt.match(re);
      if (h) bad.push(`${lg}: ${m} ×${h.length}`);
    }
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : ['zero marcadores em italiano e em ingles, com todas as dobras abertas'] };
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

/* ── OS OITO LITERAIS, NAS DUAS LINGUAS ───────────────────────────────────────
   O teste abaixo compara a frase `NAO_DIZER` — escrita em PORTUGUES — contra uma
   pagina em ITALIANO. Isso passa quase sempre, e nao por a regra ser respeitada:
   por a frase nunca poder estar la. Medido em 2026-09-04 contra este HEAD:
   injetei «copertura BUONA in 72 celle. C'e un problema in questa regione.
   Spazio libero: 0 sottotitoli.» na casa, e o portao deu 14/14.

       UM PORTAO QUE SO SABE A LINGUA EM QUE A REGRA FOI ESCRITA
       NAO GUARDA A LINGUA EM QUE O ECRA FALA.

   O equivalente italiano e adaptacao QA DESTA linha — nao sai do handoff — e por
   isso vive num ficheiro declarado, `DO-NOT-SHOW-QA.json`, com a razao escrita.

   E ha um cuidado que o controlo NAO pode atropelar: a casa DIZ as frases
   proibidas para as NEGAR — «si dice 72 con l'espansione dichiarata, mai
   copertura BUONA in 72 celle» e «la mappa risponde ... Non risponde ...».
   Proibir isso seria exigir que a tela escondesse a propria regra.

       A FRASE PROIBIDA, NEGADA, E A REGRA A ENSINAR-SE.
       PROIBI-LA SERIA APAGAR A LICAO PARA SALVAR O GREP. */
check('LITERAL_PT_CONTROL', () => {
  const bad = [];
  if (QA.LITERAIS.length !== 8) bad.push(`a adaptacao QA declara ${QA.LITERAIS.length} literais, nao 8`);
  bad.push(...medir(aberta, 'PT'));
  bad.push(...controloNegativo());
  return { pass: !bad.length, detail: bad.length ? bad : ['8/8 em portugues, e a negacao pedagogica nao conta como afirmacao'] };
});

check('LITERAL_IT_AND_EN_CONTROL', () => {
  /* A LINGUA REAL DA SUPERFICIE — as duas, e cada uma medida com as SUAS
     frases. Medir a pagina inglesa com as frases italianas passaria sempre,
     e nao por a regra ser respeitada: por a frase nunca poder estar la. */
  const bad = [];
  const nIT = QA.LITERAIS.reduce((a, L) => a + (L.IT || []).length, 0);
  const nEN = QA.LITERAIS.reduce((a, L) => a + (L.EN || []).length, 0);
  bad.push(...medir(aberta, 'IT').map((m) => `IT · ${m}`));
  bad.push(...medir(abertaEN, 'EN').map((m) => `EN · ${m}`));
  bad.push(...controloNegativo());
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${nIT} equivalentes italianos e ${nEN} ingleses para os 8 literais, cada lingua medida com os seus — isto e grep, NAO revisao semantica`] };
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

/* ── um nome de superficie, uma populacao ────────────────────────────────── */
/* O menu chamava «Radar Futuro» a tres registos IT-FUT- do pacote V21, e a casa
   chama «Radar Futuro» aos 45 ITFC. Chamava «Fonti» a 189 linhas SRC_ do mesmo
   pacote — sem AUTHORITY_CLASS e sem COLLECTABILITY, que sao precisamente os dois
   campos que definem as 91 «fonti con metodo». Interseccao de IDs: ZERO nos dois
   casos. Dois universos disjuntos com o mesmo nome, a um clique da primeira dobra.

       O CLIENTE NAO PODE CLICAR NUM NOME E CAIR NOUTRO UNIVERSO.

   Este portao NAO procura a ausencia de uma string: liga o ROTULO ao DONO DA
   POPULACAO. Para cada nome de superficie pergunta-se de que colecao ele conta,
   e exige-se que o nome canonico so possa pertencer ao universo canonico.
   Um portao por ausencia de texto passaria com o rotulo certo aplicado a
   populacao errada — que e exactamente o defeito. */
const NOMES_CANONICOS = {
  RADAR: ['radar futuro', 'future radar'],
  FONTES: ['fonti con metodo', 'sources with method'],
};

check('ONE_SURFACE_NAME_ONE_POPULATION', () => {
  const i18n = fs.readFileSync(path.join(CLIENTE, 'italy-i18n.js'), 'utf8');
  const rot = (chave) => [...i18n.matchAll(new RegExp(`${chave}:\\s*'((?:[^'\\\\]|\\\\.)*)'`, 'g'))].map((m) => m[1]);
  const bad = [];

  /* de que colecao conta cada entrada de menu — lido do portal, nao adivinhado */
  const portale = fs.readFileSync(path.join(CLIENTE, 'portale.html'), 'utf8');
  const contaDe = (chave) => {
    const m = portale.match(new RegExp(`\\[\\s*'[a-z]+'\\s*,\\s*T\\.${chave}\\s*,\\s*navN\\('([a-zA-Z]+)'\\)`));
    return m ? m[1] : null;
  };
  const donoFuture = contaDe('navFuture');
  const donoSources = contaDe('navSources');
  if (donoFuture !== 'futureSignals') bad.push(`navFuture conta '${donoFuture}', esperado futureSignals`);
  if (donoSources !== 'sources') bad.push(`navSources conta '${donoSources}', esperado sources`);

  /* a populacao que cada dono entrega, medida no artefacto embarcado */
  const emb = embarcadoV21();
  const idsFuture = (emb.futureSignals || []).map((x) => x.ID || x.id || '');
  const idsSources = (emb.sources || []).map((x) => x.ID || x.id || '');
  const canonicos = new Set((RF.RENDERIZAVEIS || []).map((x) => (typeof x === 'string' ? x : x && (x.ID || x.id))));

  /* ZERO em comum: se um dia se cruzarem, deixa de haver dois universos e este
     portao tem de ser reescrito em vez de silenciado. */
  const cruz = idsFuture.filter((id) => canonicos.has(id));
  if (cruz.length) bad.push(`IT-FUT e ITFC deixaram de ser disjuntos: ${cruz.join(',')}`);
  if (!idsFuture.length || !idsFuture.every((id) => /^IT-FUT-/.test(id)))
    bad.push(`a populacao de navFuture nao e IT-FUT-*: ${idsFuture.slice(0, 3).join(',')}`);
  if (!idsSources.every((id) => /^SRC_/.test(id)))
    bad.push('a populacao de navSources nao e SRC_*');

  /* A LEI: o nome canonico nao pode rotular a populacao legada. */
  for (const r of rot('navFuture'))
    if (NOMES_CANONICOS.RADAR.includes(r.trim().toLowerCase()))
      bad.push(`«${r}» rotula ${idsFuture.length} registos IT-FUT-, mas e o nome dos ${canonicos.size} ITFC`);
  for (const r of rot('navSources'))
    if (NOMES_CANONICOS.FONTES.includes(r.trim().toLowerCase()) || /^(fonti|sources)$/i.test(r.trim()))
      bad.push(`«${r}» rotula ${idsSources.length} linhas SRC_, ao lado das 91 fonti con metodo`);

  /* CONTROLO NEGATIVO — um portao que nunca reprovou e decoracao. Da-se o nome
     canonico a populacao legada e exige-se que a mesma regra o apanhe. */
  const regra = (rotulos, canon) => rotulos.some((r) => canon.includes(r.trim().toLowerCase()));
  if (!regra(['Radar Futuro'], NOMES_CANONICOS.RADAR)) bad.push('CONTROLO NEGATIVO FALHOU: «Radar Futuro» na populacao IT-FUT nao foi apanhado');
  if (!regra(['Fonti con metodo'], NOMES_CANONICOS.FONTES)) bad.push('CONTROLO NEGATIVO FALHOU: «Fonti con metodo» na coleccao legada nao foi apanhado');

  return { pass: !bad.length, detail: bad.length ? bad : [
    `navFuture «${rot('navFuture').join(' / ')}» -> ${donoFuture} · ${idsFuture.length} IT-FUT-`,
    `navSources «${rot('navSources').join(' / ')}» -> ${donoSources} · ${idsSources.length} SRC_`,
    `«Radar Futuro» fica reservado aos ${canonicos.size} ITFC · interseccao IT-FUT x ITFC = 0`,
    'controlo negativo: os dois nomes canonicos aplicados ao legado SAO apanhados',
  ] };
});

/* ══ AS 43 OPORTUNIDADES ATUAIS ═════════════════════════════════════════════
   O numero maior da primeira dobra e o que mais facilmente se escreve a mao. E
   um 43 escrito a mao nao e um erro que se veja: e um numero certo hoje que
   deixa de mudar quando o motor mudar.

       UM NUMERO DERIVADO E UMA MEDIDA. UM NUMERO ESCRITO E UMA LEMBRANCA.

   Por isso este portao nao pergunta "esta 43 no ecra?" — pergunta "de onde
   veio o 43 que esta no ecra?", e refaz a conta a partir do dono. */
const MI = JSON.parse(fs.readFileSync(path.join(CLIENTE, 'meeting-intelligence-snapshot.json'), 'utf8'));

check('CURRENT_OPPORTUNITIES_OWNER_DERIVED', () => {
  const bad = [];
  const OA = CASA.OPPORTUNITA_ATTUALI || {};
  /* A regra prioridade -> estado do cliente e de meeting-surface.js. Le-se de
     la; copia-la para aqui daria a este portao um terceiro dono da mesma lei. */
  const surf = fs.readFileSync(path.join(CLIENTE, 'meeting-surface.js'), 'utf8');
  const bloco = surf.match(/const CLIENT_STATE = \{([\s\S]*?)\n  \};/);
  if (!bloco) return { pass: false, detail: ['meeting-surface.js: CLIENT_STATE nao encontrado'] };
  const mapa = Object.fromEntries([...bloco[1].matchAll(/([A-Z_]+):\s*'([A-Z_]+)'/g)].map((m) => [m[1], m[2]]));
  if (Object.keys(mapa).length !== 3) bad.push(`CLIENT_STATE tem ${Object.keys(mapa).length} entradas, esperadas 3`);

  const casos = MI.CASES || [];
  const comercial = casos.filter((c) => mapa[c.COMMERCIAL_PRIORITY]).length;
  const validar = casos.length - comercial;
  if (MI.TOTAL_CASES !== casos.length) bad.push(`o snapshot diz ${MI.TOTAL_CASES} e traz ${casos.length}`);
  if (OA.TOTALE !== casos.length) bad.push(`a casa diz ${OA.TOTALE}, o dono traz ${casos.length}`);
  if (OA.PRIORITA_COMMERCIALE !== comercial) bad.push(`prioridade comercial: casa ${OA.PRIORITA_COMMERCIALE}, dono ${comercial}`);
  if (OA.DA_VALIDARE !== validar) bad.push(`da validare: casa ${OA.DA_VALIDARE}, dono ${validar}`);
  if (OA.PRIORITA_COMMERCIALE + OA.DA_VALIDARE !== OA.TOTALE) bad.push('as duas partes nao fecham no total');
  if ((OA.CASI || []).length !== casos.length) bad.push(`o pacote leva ${(OA.CASI || []).length} casos, nao ${casos.length}`);
  if (OA.SOURCE_HEAD !== MI.SOURCE_HEAD || OA.BUILD_ID !== MI.BUILD_ID) bad.push('a casa declara outra proveniencia que o dono');
  /* ── A DECOMPOSICAO QUE O ECRA MOSTRA E A DA LEI DE RELEVANCIA ──────────
     Ate a lei existir, a primeira dobra dizia 26 + 17 = 43: a divisao do
     motor entre prioridade comercial e por validar. A lei rimediu, e a
     divisao que o cliente le passou a ser outra — quantas se conseguem ligar
     a um produto ADAMA. O total nao muda, porque nenhum caso desapareceu.

         O QUE MUDOU NAO FOI O NUMERO. FOI A PERGUNTA QUE ELE RESPONDE. */
  const partes = [OA.OPPORTUNITA, OA.RADAR, OA.SEGNALI, OA.ERRORE].filter((n) => n > 0);
  if (partes.reduce((a, b) => a + b, 0) !== OA.TOTALE) {
    bad.push(`as superficies somam ${partes.reduce((a, b) => a + b, 0)}, nao ${OA.TOTALE}`);
  }
  /* E o ecra tem de o dizer, nas duas linguas e sem o esconder atras de uma dobra. */
  for (const [lg, txt] of [['it', fechada], ['en', abertaEN]]) {
    if (!temNum(txt, OA.TOTALE)) bad.push(`${lg}: o ecra nao mostra ${OA.TOTALE}`);
    for (const n of partes) if (!temNum(txt, n)) bad.push(`${lg}: o ecra nao mostra ${n}`);
  }
  /* A aritmetica dita, nao deixada ao leitor. */
  const soma = new RegExp(partes.join('\\s*\\+\\s*') + `\\s*=\\s*${OA.TOTALE}`);
  if (!soma.test(aberta)) bad.push(`a primeira dobra nao explica ${partes.join(' + ')} = ${OA.TOTALE}`);
  if (!soma.test(abertaEN)) bad.push('a superficie inglesa nao explica a mesma soma');
  /* A LEI TEM UM DONO, E O ECRA CONTA O QUE ELE DECIDIU. */
  if (OA.RILEVANZA_PER_CLASSE.A !== OA.OPPORTUNITA) bad.push('classe A e superficie OPPORTUNITA divergem');
  for (const k of ['B', 'C', 'D', 'E']) {
    if (OA.RILEVANZA_PER_CLASSE[k] === undefined) bad.push(`a lei nao conta a classe ${k}`);
  }
  return { pass: !bad.length, detail: bad.length ? bad : [
    `${OA.TOTALE} = ${OA.OPPORTUNITA} opportunita + ${OA.RADAR} radar + ${OA.SEGNALI} segnali + ${OA.ERRORE} errore, refeitos a partir do snapshot ${MI.BUILD_ID}`,
    `a lei de relevancia vive em scripts/adama_relevance.py · A=${OA.RILEVANZA_PER_CLASSE.A} B=${OA.RILEVANZA_PER_CLASSE.B} C=${OA.RILEVANZA_PER_CLASSE.C} D=${OA.RILEVANZA_PER_CLASSE.D} E=${OA.RILEVANZA_PER_CLASSE.E}`,
    `a regra prioridade->estado lida de meeting-surface.js: ${Object.entries(mapa).map(([a, b]) => `${a}->${b}`).join(' · ')}`,
  ] };
});

check('HARDCODE_43_CANNOT_PASS', () => {
  /* O portao acima refaz a conta — mas refazer a conta nao impede que alguem
     escreva o numero na vista e deixe o dado a apodrecer ao lado. Aqui exige-se
     que o 43, o 26 e o 17 nao existam como literais no codigo que os desenha.

         SE O NUMERO ESTA NO CODIGO, DEIXOU DE SER MEDIDO. */
  const OA = CASA.OPPORTUNITA_ATTUALI;
  const html = fs.readFileSync(path.join(CLIENTE, 'casa.html'), 'utf8');
  const gerador = fs.readFileSync(path.resolve(AQUI, '..', '..', 'scripts', 'it_casa_dados.py'), 'utf8');
  const bad = [];
  /* So o CODIGO, nunca o comentario: um numero citado numa nota nao desenha
     nada, e proibi-lo obrigaria a escrever notas que nao podem explicar-se. */
  const TRIPLA = String.fromCharCode(34, 34, 34);
  const semComentarios = (src, tipo) => (tipo === 'js'
    ? src.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|\s)\/\/[^\n]*/g, ' ')
    : src.replace(new RegExp(TRIPLA + '[\\s\\S]*?' + TRIPLA, 'g'), ' ').replace(/#[^\n]*/g, ' '));
  const alvos = [OA.TOTALE, OA.OPPORTUNITA, OA.RADAR, OA.SEGNALI];
  /* UM LITERAL, NAO UM PEDACO DE OUTRA COISA.
     Enquanto a populacao se dizia 43/26/17, um numero nu era inconfundivel.
     A lei de relevancia trouxe numeros pequenos — 13, 21, 8 — e a busca crua
     passou a acusar o `8` de «utf-8» e o `13` de «13.216». Um portao que
     acusa o que nao e defeito ensina a ignora-lo.

         AFINAR O DETECTOR NAO E AFROUXAR A REGRA.

     Continua a proibir-se o literal escrito a mao — inclusive dentro de um
     array, que e como uma populacao inteira se hardcodeia — e passa a
     excluir-se so o digito que faz parte de outro token: precedido de hifen
     colado a letra (utf-8) ou seguido de virgula-e-digito (13.216 / 13,216). */
  const literal = (n) => new RegExp(`(?<![\\w.])(?<![A-Za-z]-)${n}(?![\\w.])(?![,.]\\d)`);
  for (const [nome, src, tipo] of [['casa.html', html, 'js'], ['it_casa_dados.py', gerador, 'py']]) {
    const corpo = semComentarios(src, tipo);
    for (const n of alvos) if (literal(n).test(corpo)) bad.push(`${nome} escreve ${n} no codigo`);
  }
  /* CONTROLO NEGATIVO — um portao que nunca reprovou e decoracao. Cinco
     sondas: tres que TEM de apanhar, duas que nao pode acusar. */
  const ve = (txt, n, tipo) => literal(n).test(semComentarios(txt, tipo || 'js'));
  if (!ve(`var totale = ${OA.TOTALE};`, OA.TOTALE)) bad.push('CONTROLO NEGATIVO FALHOU: nao ve o numero escrito a mao');
  if (!ve(`const pop = [${OA.OPPORTUNITA}, ${OA.RADAR}, ${OA.SEGNALI}];`, OA.OPPORTUNITA)) {
    bad.push('CONTROLO NEGATIVO FALHOU: nao ve a populacao hardcodeada num array');
  }
  if (!ve(`if (n === ${OA.RADAR}) {}`, OA.RADAR)) bad.push('CONTROLO NEGATIVO FALHOU: nao ve o numero numa comparacao');
  if (ve(`/* sono ${OA.TOTALE} */`, OA.TOTALE)) bad.push('CONTROLO NEGATIVO FALHOU: acusa o numero citado num comentario');
  if (ve(`decode('utf-${OA.SEGNALI}')`, OA.SEGNALI)) bad.push('CONTROLO NEGATIVO FALHOU: acusa um digito dentro de outro token');
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${alvos.join(', ')} nao existem como literais na vista nem no gerador — todos derivados`,
       'controlo negativo: um numero escrito a mao SERIA apanhado; o mesmo numero num comentario nao'] };
});

check('RADAR_NEVER_SUMMED_WITH_CURRENT', () => {
  /* 43 atuais e 44 de radar sao dois HORIZONTES. Somados dariam 87 de nada:
     o primeiro e a mesa de hoje, o segundo a campanha seguinte. */
  const bad = [];
  const OA = CASA.OPPORTUNITA_ATTUALI, R = CASA.RADAR_FUTURO;
  if (OA.ORIZZONTE === R.ORIZZONTE) bad.push('as duas superficies declaram o mesmo horizonte');
  for (const [lg, txt] of [['it', aberta], ['en', abertaEN]]) {
    if (temNum(txt, OA.TOTALE + R.RENDERIZAVEIS)) bad.push(`${lg}: a soma proibida ${OA.TOTALE + R.RENDERIZAVEIS} esta no ecra`);
    if (temNum(txt, OA.TOTALE + R.TOTAL)) bad.push(`${lg}: a soma proibida ${OA.TOTALE + R.TOTAL} esta no ecra`);
  }
  if (!/non si somma/i.test(aberta)) bad.push('a casa nao diz que os dois nao se somam');
  if (!/not added|does not add/i.test(abertaEN)) bad.push('a superficie inglesa nao diz que os dois nao se somam');
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${OA.ORIZZONTE} e ${R.ORIZZONTE} sao dois horizontes; ${OA.TOTALE + R.RENDERIZAVEIS} nao aparece em lingua nenhuma`] };
});

check('LEDGER_44_NAVIGABLE', () => {
  /* O TOP_3 e enriquecimento, nao universo. Levar tres para o browser fazia do
     destaque a coleccao inteira, e quem abrisse o Radar via 3 de 44 nao tinha
     como saber que faltavam 41. */
  const bad = [];
  const R = CASA.RADAR_FUTURO;
  const reg = R.REGISTRO || [];
  const idDe = (x) => (typeof x === 'string' ? x : (x && (x.ID || x.id)) || null);
  const rend = new Set((RF.RENDERIZAVEIS || []).map(idDe).filter(Boolean));
  const excl = new Set((RF.EXCLUIDOS || []).map(idDe).filter(Boolean));
  if (reg.length !== RF.RENDERABLE) bad.push(`o registo tem ${reg.length} linhas, o handoff diz ${RF.RENDERABLE}`);
  for (const r of reg) {
    if (excl.has(r.ID)) bad.push(`${r.ID} esta entre os EXCLUIDOS e esta no registo`);
    else if (!rend.has(r.ID)) bad.push(`${r.ID} nao esta entre os RENDERIZAVEIS`);
  }
  const prep = reg.filter((r) => r.ACAO === 'PREPARAR').length;
  const moni = reg.filter((r) => r.ACAO === 'MONITORAR').length;
  if (prep !== RF.PREPARE) bad.push(`PREPARAR: registo ${prep}, handoff ${RF.PREPARE}`);
  if (moni !== RF.WATCH) bad.push(`MONITORAR: registo ${moni}, handoff ${RF.WATCH}`);
  if (R.TOTAL !== RF.TOTAL || R.RENDERIZAVEIS !== RF.RENDERABLE || R.DERRUBADOS !== RF.DROPPED) {
    bad.push(`45/44/1 partiu-se: ${R.TOTAL}/${R.RENDERIZAVEIS}/${R.DERRUBADOS}`);
  }
  if (R.AGIR_AGORA !== 0) bad.push(`AGIR_AGORA=${R.AGIR_AGORA}`);
  /* E NAVEGAVEIS quer dizer no DOM, nao no dado. */
  for (const [lg, dom] of [['it', domIT], ['en', domEN]]) {
    const vistos = new Set(dom.ledger);
    if (vistos.size !== RF.RENDERABLE) bad.push(`${lg}: o ecra desenha ${vistos.size} linhas de registo, nao ${RF.RENDERABLE}`);
    for (const id of excl) if (vistos.has(id)) bad.push(`${lg}: o derrubado ${id} esta desenhado`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${reg.length} ITFC no pacote e ${new Set(domIT.ledger).size} desenhados · ${prep} preparar + ${moni} monitorar + ${R.AGIR_AGORA} agir agora`,
       `TOP_3 continua enriquecimento: ${reg.filter((r) => r.SENSOR).length} linhas trazem veredito de sensor, ${reg.length} trazem a linha`] };
});

check('LEVELS_1_2_3_ON_THE_SURFACE', () => {
  /* Progressive disclosure medida onde ela existe: no DOM. Um nivel que o
     pacote traz e o ecra nao desenha nao e um nivel. */
  const bad = [];
  const OA = CASA.OPPORTUNITA_ATTUALI;
  for (const [lg, dom] of [['it', domIT], ['en', domEN]]) {
    if (dom.casos !== OA.TOTALE) bad.push(`${lg}: ${dom.casos} casos no DOM, ${OA.TOTALE} no pacote`);
    if (dom.comL3 !== dom.casos) bad.push(`${lg}: ${dom.casos - dom.comL3} casos sem dobra de evidencia (L3)`);
    const magro = dom.seccoes.filter((n) => n < 7).length;
    if (magro) bad.push(`${lg}: ${magro} casos com menos de 7 seccoes de gestao (L2)`);
    if (dom.htmlLang !== lg) bad.push(`${lg}: <html lang> diz ${dom.htmlLang}`);
  }
  for (const m of ['L1', 'L2', 'L3']) if (!aberta.includes(`${m} ·`)) bad.push(`o nivel ${m} nao esta nomeado`);
  return { pass: !bad.length, detail: bad.length ? bad
    : [`L1 primeira dobra · L2 ${domIT.casos} casos com ${Math.min(...domIT.seccoes)}-${Math.max(...domIT.seccoes)} seccoes · L3 ${domIT.comL3} dobras de evidencia`,
       'medido nas duas linguas'] };
});

check('LABEL_FAIL_CLOSED_IT_AND_EN', () => {
  /* `null` em meeting-labels.js PODE fazer desaparecer uma linha: em
     meeting-surface.js, `labList` filtra as etiquetas nulas e a linha some sem
     que ninguem veja o buraco. E um defeito real, e fecha-se aqui em vez de
     se documentar.

         UMA LINHA QUE SOME EM SILENCIO E PIOR DO QUE UM TOKEN A VISTA:
         O TOKEN VE-SE.

     Fecha-se em tres sitios: o gerador FALHA se um codigo nao tiver par; a
     vista desenha [codigo] em vez de nada; e este portao reprova se algum
     [codigo] aparecer no ecra, em qualquer das duas linguas. */
  const bad = [];
  const L = CASA.LABELS || {};
  const n = Object.keys(L).length;
  if (!n) bad.push('o pacote nao leva dicionario nenhum');
  for (const [k, v] of Object.entries(L)) {
    if (!v || !v.it || !v.en) bad.push(`${k} sem par IT+EN no pacote`);
  }
  for (const [lg, dom] of [['it', domIT], ['en', domEN]]) {
    if (dom.buracos.length) bad.push(`${lg}: ${dom.buracos.length} etiqueta(s) em falta no ecra: ${[...new Set(dom.buracos)].slice(0, 6).join(', ')}`);
    if (dom.objetos) bad.push(`${lg}: ${dom.objetos} par(es) impressos como objecto`);
  }
  /* CONTROLO NEGATIVO — o detector de buracos tem de VER um buraco. */
  if (!/\[[A-Za-z][A-Za-z0-9_]{3,}\]/.test('[codigoInventado]')) {
    bad.push('CONTROLO NEGATIVO FALHOU: o detector nao ve o marcador de buraco');
  }
  if (/\[[A-Za-z][A-Za-z0-9_]{3,}\]/.test('[ab] 43 [X]')) {
    bad.push('CONTROLO NEGATIVO FALHOU: o detector acusa parenteses que nao sao codigo');
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${n} codigos no pacote, todos com par IT+EN`,
       'zero buracos desenhados em italiano e em ingles',
       'dono unico das frases: client/meeting-labels.js — o pacote transporta, nao escreve'] };
});

check('ACTION_MAP_IS_THE_ENGINE_MAP', () => {
  /* O mapa de accao mostra os reparos que o MOTOR nomeia — nunca um inventado —
     e a JANELA so onde o motor a declara. ACT, PREPARE e WATCH tem janela;
     VALIDATE e NO_ACTION nao tem, e forca-los para dentro de uma das tres
     seria decidir no lugar do motor. */
  const bad = [];
  const OA = CASA.OPPORTUNITA_ATTUALI;
  const JANELA = { ACT: 'WINDOW_ACT_NOW', PREPARE: 'WINDOW_PREPARE', WATCH: 'WINDOW_MONITOR' };
  const doMotor = new Set();
  for (const c of MI.CASES) for (const d of Object.keys(c.ACTION_BY_DEPARTMENT || {})) doMotor.add(d);
  const noPacote = new Set();
  let comJanela = 0; let semJanela = 0;
  for (const c of OA.CASI) {
    if (!c.AZIONI.length) bad.push(`${c.ID} sem mapa de accao`);
    if (c.AZIONI.length && c.AZIONI[0].REPARTO !== 'MARKET_DEVELOPMENT') {
      bad.push(`${c.ID}: Desenvolvimento de Mercado nao e o primeiro destinatario`);
    }
    for (const a of c.AZIONI) {
      noPacote.add(a.REPARTO);
      const esperada = JANELA[a.STATO] || null;
      if ((a.FINESTRA || null) !== esperada) bad.push(`${c.ID}/${a.REPARTO}: janela ${a.FINESTRA} para estado ${a.STATO}`);
      if (esperada) comJanela++; else semJanela++;
    }
  }
  for (const d of noPacote) if (!doMotor.has(d)) bad.push(`o pacote inventa o reparto ${d}`);
  for (const d of doMotor) if (!noPacote.has(d)) bad.push(`o reparto ${d} do motor nao chega ao pacote`);
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${doMotor.size} repartos, exactamente os do motor; Sviluppo Mercato primeiro em ${OA.CASI.length} casos`,
       `${comJanela} accoes com janela declarada · ${semJanela} sem, e ditas sem`] };
});

check('DEPOINTER_ONE_RULE_TWO_IMPLEMENTATIONS', () => {
  /* O gerador leva a mesma regra de ponteiro que meeting-surface.js. Duas
     implementacoes de uma lei divergem — a nao ser que alguem as compare. */
  const g = { window: {} };
  vm.createContext(g);
  vm.runInContext(fs.readFileSync(path.join(CLIENTE, 'meeting-surface.js'), 'utf8'), g);
  const dp = g.window.MEETING_SURFACE && g.window.MEETING_SURFACE.dePointer;
  if (typeof dp !== 'function') return { pass: false, detail: ['meeting-surface.js nao expoe dePointer'] };
  const porId = Object.fromEntries(CASA.OPPORTUNITA_ATTUALI.CASI.map((c) => [c.ID, c]));
  const bad = [];
  let n = 0; let cortados = 0;
  for (const c of MI.CASES) {
    for (const [lg, campo] of [['it', 'WHY_COMMERCIAL_IT'], ['en', 'WHY_COMMERCIAL_EN']]) {
      const esperado = dp(c[campo] || '');
      const obtido = (porId[c.ID] || {}).PERCHE || {};
      n++;
      if (esperado.pointerRemoved) cortados++;
      if (esperado.text !== (obtido[lg] || '')) bad.push(`${c.ID}/${lg}: o gerador e a superficie discordam`);
    }
  }
  /* CONTROLO NEGATIVO: a regra tem mesmo de cortar alguma coisa. Se cortasse
     zero, esta comparacao provaria apenas que ambas nao fazem nada. */
  if (!cortados) bad.push('CONTROLO NEGATIVO FALHOU: a regra do ponteiro nao cortou nenhuma frase');
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${n} frases comparadas, ${cortados} com ponteiro cortado — as duas implementacoes concordam em todas`] };
});

check('VIEW_READS_ONLY_ITALY_CASA', () => {
  /* Uma cadeia para o browser. A vista nao pode ir buscar dado a outro sitio:
     se for, ha dois donos de apresentacao e a proxima divergencia e invisivel. */
  const html = fs.readFileSync(path.join(CLIENTE, 'casa.html'), 'utf8');
  const scripts = [...html.matchAll(/<script[^>]*src="([^"]+)"/g)].map((m) => m[1]);
  const globais = [...new Set(html.match(/window\.[A-Z][A-Z0-9_]+/g) || [])];
  const bad = [];
  if (scripts.length !== 1 || scripts[0] !== 'italy-casa.js') bad.push(`a vista carrega ${scripts.join(', ') || '(nenhum)'}`);
  for (const gl of globais) if (gl !== 'window.ITALY_CASA') bad.push(`a vista le ${gl}`);
  return { pass: !bad.length, detail: bad.length ? bad
    : [`um so pacote (${scripts[0]}) e um so global (${globais.join(', ')})`] };
});

check('NO_HORIZONTAL_SCROLL_1440_390', () => {
  /* Medido nos dois ecras reais, nao inferido do CSS. */
  const bad = [];
  for (const [nome, m] of Object.entries(larguras)) {
    if (m.scrollW > m.clientW) bad.push(`${nome}: scroll ${m.scrollW} > viewport ${m.clientW} (${m.scrollW - m.clientW}px)`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : Object.entries(larguras).map(([k, m]) => `${k}: ${m.scrollW}px = ${m.clientW}px`) };
});

/* ── a assinatura humana, e o que ela cobre ──────────────────────────────── */
/* As seis regras semanticas nao sao grepaveis: proibem uma FORMA de afirmacao,
   nao uma string. A maquina inspecciona e mostra a evidencia; quem assina e o
   humano. Este portao nao produz assinatura nenhuma — le a que existe, e recusa
   se ela nao existir ou se ja nao for sobre esta superficie.

       UMA ASSINATURA QUE VIAJA SOZINHA PARA A VERSAO SEGUINTE
       NAO E UMA ASSINATURA: E UM CARIMBO.

   Por isso a assinatura fica presa ao HEAD sobre o qual foi dada, e ao conteudo
   exacto das seis regras nessa altura. Mudar uma delas depois nao invalida o que
   foi lido: invalida a afirmacao de que continua lido. */
check('SEMANTIC_HUMAN_SIGNED', () => {
  const F = path.join(AQUI, 'DO-NOT-SHOW-SEMANTIC-REVIEW.json');
  if (!fs.existsSync(F)) return { pass: false, detail: ['a ficha de revisao semantica nao existe'] };
  const S = JSON.parse(fs.readFileSync(F, 'utf8'));
  const bad = [];

  if ((S.SEMANTICOS_6 || []).length !== 6) bad.push(`a ficha tem ${(S.SEMANTICOS_6 || []).length} regras, nao 6`);
  if (S.CONFIRMADO_POR_HUMANO !== true) bad.push(`CONFIRMADO_POR_HUMANO = ${JSON.stringify(S.CONFIRMADO_POR_HUMANO)} — sem assinatura humana nao ha PREVIEW`);
  if (!S.CONFIRMADO_EM) bad.push('a assinatura nao diz quando foi dada');
  if (!S.APROVACAO_LITERAL) bad.push('a assinatura nao guarda as palavras da aprovacao');

  /* O QUE FOI ASSINADO — verificavel em qualquer lado, sem repositorio.
     A primeira versao disto prendia a assinatura ao git, e reprovou na copia de
     sandbox do controlo negativo — que copia so italia-portale/ e nao leva .git.
     Prender a assinatura ao AMBIENTE fa-la-ia passar por nao se conseguir
     perguntar, que e a falha que estas seis regras existem para impedir.

         O HEAD DIZ DE QUE SUPERFICIE A ASSINATURA FALA.
         O HASH DIZ O QUE ELA ASSINOU. So o segundo se verifica em toda a parte. */
  const canon = JSON.stringify(S.SEMANTICOS_6);
  const agora = 'sha256:' + crypto.createHash('sha256').update(canon, 'utf8').digest('hex');
  if (!S.SEMANTICOS_6_SHA256) bad.push('a assinatura nao guarda o hash do que assinou');
  else if (S.SEMANTICOS_6_SHA256 !== agora)
    bad.push('as seis regras mudaram depois da aprovacao — e precisa nova assinatura humana');

  /* A LINHAGEM — verificacao adicional, so onde ha repositorio. A sua ausencia
     nao afrouxa nada: o que garante o essencial e o hash acima. */
  const cabeca = S.APROVADO_SOBRE_HEAD;
  let sobre = 'sem repositorio aqui — linhagem nao verificada, conteudo sim';
  if (!cabeca) bad.push('a assinatura nao diz sobre que HEAD foi dada');
  else {
    const raiz = path.resolve(AQUI, '..', '..');
    const eRepo = spawnSync('git', ['rev-parse', '--git-dir'], { cwd: raiz }).status === 0;
    if (eRepo) {
      const existe = spawnSync('git', ['cat-file', '-e', `${cabeca}^{commit}`], { cwd: raiz }).status === 0;
      if (!existe) bad.push(`APROVADO_SOBRE_HEAD ${cabeca.slice(0, 7)} nao existe neste repositorio`);
      else if (spawnSync('git', ['merge-base', '--is-ancestor', cabeca, 'HEAD'], { cwd: raiz }).status !== 0)
        bad.push(`a assinatura foi dada sobre ${cabeca.slice(0, 7)}, que nao esta na historia desta superficie`);
      else sobre = `${cabeca.slice(0, 7)} e antepassado desta superficie`;
    }
  }
  return { pass: !bad.length, detail: bad.length ? bad : [
    `INSPECTED 6/6 · HUMAN_SIGNED 6/6 · «${S.APROVACAO_LITERAL}» em ${S.CONFIRMADO_EM}`,
    `as seis regras batem com o hash assinado: ${agora.slice(0, 23)}…`,
    sobre,
  ] };
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
