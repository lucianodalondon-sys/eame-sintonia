#!/usr/bin/env node
/* D126 · PORTAL-PUBLICA-SOZINHO — A FOTO E A CONTAGEM de cada tela, num navegador de verdade.

       node portoes/fotografar_portal.mjs --base <URL> --saida <pasta> [--telas meeting,market,...]

   Abre o portal que esta EM <URL> (o que esta no ar, um preview, ou a copia montada servida
   localmente), vai a cada tela do casco e grava:

       <saida>/<tela>.png        a foto
       <saida>/CONTAGENS.json    por tela: objetos do pote desenhados, compartimento, vazio/recusado,
                                  a marca, e QUANTO DO LEGADO continua visivel (D122)

   ESTE FICHEIRO NAO JULGA NADA. Ele abre, conta e fotografa. Quem compara a contagem com o pote, e
   decide PASS ou FAIL, e o publicador (portoes/publicar_portal_sozinho.py) — e por isso a decisao se
   pode medir sem navegador nenhum.

   O LEGADO QUE A D122 MANDA ESCONDER e lido da propria pagina, nao escrito aqui: os 43 casos de hoje
   (ITALY_CASA.OPPORTUNITA_ATTUALI.CASI[].ID) e os 44 do radar futuro antigo
   (ITALY_CASA.RADAR_FUTURO.REGISTRO[].ID). Uma lista escrita a mao envelhecia com o pacote.
   Procura-se o id no HTML desenhado (atributos incluidos, <script> excluido) e nos cartoes de legado
   (`[data-meeting-case]`, `[data-case]`, `[data-itfc]`).

   Sai 0 se conseguiu abrir e medir todas as telas; 1 se o navegador nao abriu ou uma tela nao carregou
   (NAO CONSEGUI MEDIR != MEDI E ESTA MAU — mas nao medir tambem nao autoriza). */
import fs from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = (arg('base', '') || '').replace(/\/+$/, '');
const SAIDA = arg('saida', '');
/* As telas que um compartimento le (sintonia-pote-casco.js → FERRAMENTAS). `accesso` e a porta. */
const TELAS = (arg('telas', 'inicio,meeting,radarfuturo,future,archive,windows,market,voices,competitors,science,portfolio,etichette,sources,field,accesso,casa')).split(',').filter(Boolean);
const LANG = arg('lang', 'it');
/* Telas que sao PAGINAS e nao rotas do casco: a porta, a casa, e o portal sem rota (o que abre primeiro). */
const PAGINAS = { accesso: '/accesso', casa: '/casa', inicio: '/portale' };
if (!BASE || !SAIDA) {
  console.error('uso: node portoes/fotografar_portal.mjs --base <URL> --saida <pasta> [--telas a,b]');
  process.exit(2);
}

/* O navegador: o mesmo pacote que os portoes do portal usam (playwright-core). Se nao estiver
   instalado, diz-se QUAL falta — nao se contorna. */
let chromium;
try { ({ chromium } = await import('playwright-core')); }
catch (e) {
  console.error('DEPENDENCIA AUSENTE: playwright-core (npm install --no-save playwright-core, como no portao do release)');
  process.exit(1);
}
const EXEC = [process.env.SINTONIA_CHROMIUM, '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => p && fs.existsSync(p));

fs.mkdirSync(SAIDA, { recursive: true });
const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });
const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
await ctx.addInitScript((l) => { try { localStorage.setItem('sintonia_lang', l); } catch (e) {} }, LANG);
const page = await ctx.newPage();
const erros = [];
page.on('pageerror', (e) => erros.push(String(e.message || e).slice(0, 200)));

const MEDIR = (conhecidos) => {
  const W = window;
  const C = W.ITALY_CASA || {};
  let ids43 = (((C.OPPORTUNITA_ATTUALI || {}).CASI) || []).map((c) => c && c.ID).filter(Boolean);
  let ids44 = (((C.RADAR_FUTURO || {}).REGISTRO) || []).map((c) => c && c.ID).filter(Boolean);
  /* Uma pagina que nao carrega o pacote (a porta) procura os ids que o portal ja deu — senao o detector
     seria vazio e o zero nao provaria nada. */
  if (!ids43.length && conhecidos) ids43 = conhecidos.ids43 || [];
  if (!ids44.length && conhecidos) ids44 = conhecidos.ids44 || [];
  const corpo = document.body ? document.body.cloneNode(true) : null;
  if (corpo) corpo.querySelectorAll('script,template').forEach((n) => n.remove());
  const html = corpo ? corpo.outerHTML : '';
  const vistos = (ids) => ids.filter((id) => html.indexOf(id) >= 0);
  /* D152 · o que fica FORA do SNAPSHOT: o mesmo corpo sem os [data-snapshot]. */
  const fora = document.body ? document.body.cloneNode(true) : null;
  if (fora) fora.querySelectorAll('script,template,[data-snapshot]').forEach((n) => n.remove());
  const htmlFora = fora ? fora.outerHTML : '';
  const vistosFora = (ids) => ids.filter((id) => htmlFora.indexOf(id) >= 0);
  const liveN = document.querySelector('[data-live-n]');
  const comp = document.querySelector('[data-pote-compartimento]');
  const PUB = W.SINTONIA_POTE_PUBLICADO;
  return {
    POTE_NA_TELA: !!document.querySelector('[data-view="pote"]'),
    COMPARTIMENTO: comp ? comp.getAttribute('data-pote-compartimento') : null,
    POTE_OBJETOS: document.querySelectorAll('[data-pote-objeto]').length,
    POTE_IDS: [...document.querySelectorAll('[data-pote-objeto]')].map((n) => n.getAttribute('data-pote-objeto')),
    ENTREGA_RECUSADA_NA_TELA: !!document.querySelector('[data-entrega-recusada]'),
    LIVE_DEMO: (document.querySelector('[data-live-demo]') || { getAttribute: () => null }).getAttribute('data-live-demo'),
    POTE_VAZIO: !!document.querySelector('[data-pote-vazio]'),
    POTE_RECUSADO: !!document.querySelector('[data-pote-recusado]'),
    MARCA: !!document.querySelector('[data-view="pote"] [data-marca]'),
    LEGADO_CARTOES: document.querySelectorAll('[data-meeting-case],[data-case],[data-itfc]').length,
    /* a caixa «oggi» da barra (as janelas do pacote de 02/09) */
    OGGI_LEGADO: !!document.querySelector('[data-oggi-legado]'),
    /* o contador de cada voz da barra, pela rota que ela abre (data-nav-view) */
    NAV: [...document.querySelectorAll('[data-nav-view]')].reduce((a, n) => {
      const v = n.getAttribute('data-nav-view'); const spans = n.querySelectorAll('span');
      if (v) a[v] = spans.length ? spans[spans.length - 1].textContent.trim() : null; return a;
    }, {}),
    LEGADO_43_UNIVERSO: ids43.length,
    LEGADO_43_VISIVEIS: vistos(ids43).length,
    LEGADO_44_UNIVERSO: ids44.length,
    LEGADO_44_VISIVEIS: vistos(ids44).length,
    LEGADO_43_FORA: vistosFora(ids43).length,
    LEGADO_44_FORA: vistosFora(ids44).length,
    LEGADO_CARTOES_FORA: fora ? fora.querySelectorAll('[data-meeting-case],[data-case],[data-itfc]').length : null,
    LIVE_N: liveN ? liveN.getAttribute('data-live-n') : null,
    SNAPSHOT_TITULO: !!document.querySelector('[data-snapshot-titulo]'),
    IDS: { ids43, ids44 },
    HASH: location.hash,
    ENVELOPE: PUB && typeof PUB === 'object'
      ? { CONTRATO: PUB.CONTRATO || null, POTE_SHA256: PUB.POTE_SHA256 || null, RUN: PUB.INTELLIGENCE_RUN_ID || null,
          TEM_POTE: !!PUB.POTE, ENTREGA_ESTADO: (PUB.ENTREGA && PUB.ENTREGA.ESTADO) || null }
      : null,
  };
};

const res = { BASE, LANG, MEDIDO_EM: new Date().toISOString(), TELAS: {} };
let conhecidos = null;
let falhou = false;
/* D156 · as requisicoes que falharam, por tentativa. Medido 29/09 12:36 (tarefa agendada, maquina carregada):
   #future abriu com «portale.renderVals(): Cannot read properties of null (reading 'CATEGORY_UI')» — o modelo nao
   existia na primeira pintura — e nao se reproduziu em 6 tentativas depois. Sem esta lista a causa ficou NAO SEI. */
const reqFalhadas = [];
page.on('requestfailed', (q) => reqFalhadas.push(`${q.url().replace(BASE, '')} · ${(q.failure() || {}).errorText || '?'}`));
page.on('response', (q) => { if (q.status() >= 400) reqFalhadas.push(`${q.url().replace(BASE, '')} · HTTP ${q.status()}`); });

async function medirTela(tela, url) {
  const antes = erros.length, antesReq = reqFalhadas.length;
  /* Cada tela e um carregamento INTEIRO: mudar so o fragmento nao devolve resposta HTTP, e uma tela
     sem resposta medida nao prova que foi servida. */
  await page.goto('about:blank');
  const r = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  const status = r ? r.status() : null;
  if (!PAGINAS[tela]) {
    await page.waitForSelector('[data-view="pote"],[data-meeting-case],[data-case],main,body', { timeout: 15000 }).catch(() => {});
  }
  await page.waitForTimeout(900);
  /* O endereco so abre as rotas de primeiro nivel, e uma que ele nao aceite fica com o fragmento certo e
     a vista errada (medido: #field desenhava o radar). Por isso, havendo voz da barra para a tela, CLICA-SE
     nela — e o caminho do leitor. Se nem essa existir, mede-se o que abriu, e a contagem diz o resto. */
  let clicou = false;
  if (!PAGINAS[tela]) {
    clicou = await page.evaluate((t) => { const n = document.querySelector('[data-nav-view="' + t + '"]');
      if (!n) return false; n.click(); return true; }, tela);
    if (clicou) await page.waitForTimeout(900);
  }
  const medido = await page.evaluate(MEDIR, conhecidos);
  const erroDePintura = await page.evaluate(() => /renderVals\(\)/.test((document.body && document.body.innerText) || ''));
  return { status, clicou, medido, erroDePintura, erros: erros.slice(antes), falhadas: reqFalhadas.slice(antesReq) };
}

for (const tela of TELAS) {
  const url = PAGINAS[tela] ? `${BASE}${PAGINAS[tela]}` : `${BASE}/portale#${tela}`;
  try {
    let t = await medirTela(tela, url);
    /* Uma tela que abriu com o erro de pintura mede-se UMA vez mais; a primeira fica no registo, inteira.
       A medida que conta e a segunda — e se ela tambem falhar, ERRO_DE_PINTURA = true reprova (C5/C6). */
    const tentativasFalhadas = [];
    if (t.erroDePintura) {
      await page.screenshot({ path: path.join(SAIDA, `${tela}-tentativa-1.png`), fullPage: false });
      tentativasFalhadas.push({ ERRO_DE_PINTURA: true, ERROS_JS: t.erros, REQUISICOES_FALHADAS: t.falhadas });
      t = await medirTela(tela, url);
    }
    const { IDS, ...m } = t.medido;
    if (IDS && IDS.ids43.length && !conhecidos) conhecidos = IDS;
    await page.screenshot({ path: path.join(SAIDA, `${tela}.png`), fullPage: false });
    /* URL_FINAL: onde a pagina terminou depois dos redirects (a casa legada tem de acabar na porta). */
    res.TELAS[tela] = { URL: url, URL_FINAL: page.url(), HTTP: t.status, CLICOU_NA_BARRA: t.clicou, ...m,
      ERRO_DE_PINTURA: t.erroDePintura, ERROS_JS: t.erros, REQUISICOES_FALHADAS: t.falhadas,
      TENTATIVAS_FALHADAS: tentativasFalhadas };
    if (t.status !== 200) falhou = true;
  } catch (e) {
    res.TELAS[tela] = { URL: url, HTTP: null, NAO_CONSEGUI_MEDIR: String(e.message || e).slice(0, 300) };
    falhou = true;
  }
}
await browser.close();
res.MEDICAO_COMPLETA = !falhou;
fs.writeFileSync(path.join(SAIDA, 'CONTAGENS.json'), JSON.stringify(res, null, 1));
for (const [t, v] of Object.entries(res.TELAS)) {
  console.log(`  ${t.padEnd(12)} HTTP ${v.HTTP} · pote ${v.POTE_OBJETOS ?? '-'} (${v.COMPARTIMENTO ?? '-'}) · legado 43:${v.LEGADO_43_VISIVEIS ?? '-'} 44:${v.LEGADO_44_VISIVEIS ?? '-'} cartoes:${v.LEGADO_CARTOES ?? '-'}`);
}
process.exit(falhou ? 1 : 0);
