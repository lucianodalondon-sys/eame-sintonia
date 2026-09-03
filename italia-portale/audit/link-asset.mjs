/* SINTONIA · LINK_AND_ASSET_GATE + CONSOLE_ERROR_GATE
   ---------------------------------------------------------------------------
   node audit/link-asset.mjs [--json out.json] [--port 8963] [--client <pasta>]

   Um icone que nao carrega nao da erro: da um quadrado vazio. O leitor nao ve
   um 404, ve uma ficha sem simbolo e conclui que o portal esta incompleto. E o
   contrario tambem acontece: o ficheiro existe na pasta, o markup aponta para
   ele, e ninguem o pede porque o caminho tem uma letra a mais.

       O QUE A PAGINA PEDE TEM DE CHEGAR. O QUE ELA APONTA TEM DE EXISTIR.

   Por isso este portao mede as duas pontas, e nenhuma delas por leitura de
   codigo-fonte de comportamento:

     rede   — abre um Chromium, recarrega a pagina com o ouvido ligado e
              percorre TODAS as telas da barra lateral, guardando o status de
              cada resposta. 4xx/5xx reprova.
     disco  — le as referencias declaradas no markup (url(...), src=, href= e
              os <meta ext-resource-dependency>) e os caminhos que o MODELO
              publica em iconAsset/aShape — porque esses o markup nunca os
              escreve, o runtime e que os preenche — e exige o ficheiro.
     link   — valida a forma de cada href externo. NAO chama o host: um portao
              que depende da internet reprova quando a internet e que falhou.
     olho   — qualquer <img> que renderizou com naturalWidth === 0 e uma imagem
              partida que o leitor VE. Essa e a unica prova que interessa.

   E por cima de tudo isso, o silencio: zero pageerror e zero console.error na
   varredura inteira. A unica excecao e o marcador de template dentro de um
   atributo SVG — d="{{ p }}" existe no HTML antes de o runtime o substituir, e
   o browser queixa-se ao ANALISAR, nao ao executar. O drive.mjs ja separa essas
   queixas no balde `noise`; aqui conta-se o balde para que uma mudanca no
   numero seja visivel em vez de silenciosa.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { serve, open, clickTitle, openCase, caseIds, nav, CLIENT as DEFAULT_CLIENT, C, line } from './lib/drive.mjs';
import { loadData } from './lib/harness.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const JSON_OUT = arg('json', null);
const PORT = Number(arg('port', 8963));
/* `--client <pasta>` serve e mede uma COPIA do pacote em vez do original. Existe
   por duas razoes, e nenhuma delas e conveniencia: valida um candidato sem tocar
   no ficheiro que os outros agentes estao a ler, e — sobretudo — permite provar
   que este portao sabe reprovar. Um portao que nunca se viu falhar nao e um
   portao, e um carimbo. */
const CLIENT = path.resolve(arg('client', DEFAULT_CLIENT));
/* Quantos marcadores de template dentro de atributos SVG o markup pode ter sem
   que isso conte como novidade. Hoje o Chromium queixa-se de UM (d="{{ p }}",
   o <path> do sparkline dentro do sc-for). O tecto fica no valor herdado da
   especificacao — 5 — para que o portao acuse quem acrescentar o sexto. */
const NOISE_MAX = Number(arg('noise-max', 5));
/* E quantos ele TEM hoje, medidos e nao supostos. O tecto acima e o contrato; a
   linha de base e a verdade. Quando as duas divergem o resumo di-lo em voz alta,
   porque um numero que muda dentro da folga e uma mudanca que ninguem viu. */
const NOISE_BASELINE = 1;

/* ── 1. o que o MODELO publica como caminho de asset ───────────────────────
   O markup escreve `background-image:url({{ a.chIcon }})`. Grep nenhum
   encontra «assets/icons/rain-white.png» ali, porque essa string nao esta no
   markup — esta no modelo. Quem quiser verificar o ficheiro tem de perguntar
   ao modelo qual e o caminho que ele vai publicar. */
const AM = loadData({ dir: CLIENT }).ITALY_APP_MODEL;
const ASSETISH = /^(?:\.\/)?[\w./-]+\.(png|jpe?g|svg|webp|gif|avif)$/i;
const modelAssets = new Map();   // caminho -> onde foi encontrado
const modelEmptySlots = [];      // slots de icone declarados VAZIOS
{
  const seen = new WeakSet();
  const walk = (o, at, depth) => {
    if (!o || typeof o !== 'object' || depth > 8 || seen.has(o)) return;
    seen.add(o);
    for (const k of Object.keys(o)) {
      const v = o[k];
      if (typeof v === 'string') {
        if (ASSETISH.test(v) && !/^https?:/i.test(v)) { if (!modelAssets.has(v)) modelAssets.set(v, `${at}.${k}`); }
        else if (v === '' && /^(iconAsset|aShape)$/.test(k)) modelEmptySlots.push(`${at}.${k}`);
      } else if (v && typeof v === 'object') walk(v, `${at}.${k}`, depth + 1);
    }
  };
  walk(AM, 'AM', 0);
}

/* ── 2. o que o MARKUP declara ─────────────────────────────────────────────
   Ler o ficheiro aqui nao e julgar comportamento por grep: e recolher a LISTA
   de referencias para depois a confrontar com o disco. O juizo continua a ser
   uma medida — existe ou nao existe. */
const HTML = fs.readFileSync(path.join(CLIENT, 'portale.html'), 'utf8');

/* Um valor so e um caminho local quando nao tem esquema, nao tem marcador de
   template e nao tem sinais de concatenacao em JavaScript. As tres exclusoes
   nasceram de casos reais neste ficheiro: `url(...)` e `url("")` vivem dentro
   de COMENTARIOS que explicam o proprio mecanismo, e `href="{{ v.url }}"` e o
   runtime a ser runtime. */
const isLocalPath = (v) => {
  const s = (v || '').trim();
  if (!s || s === '...' || s.length > 300) return false;
  if (/^(data:|blob:|https?:|\/\/|mailto:|tel:|javascript:|#)/i.test(s)) return false;
  if (/[{}$`'+\s<>]/.test(s)) return false;      // template, concatenacao ou lixo
  return /\.[a-z0-9]{2,5}$/i.test(s.split('?')[0].split('#')[0]);
};

const refs = new Map();          // caminho -> Set(origem no markup)
const addRef = (v, kind) => {
  if (!isLocalPath(v)) return;
  const clean = v.trim().split('?')[0].split('#')[0].replace(/^\.\//, '').replace(/^\//, '');
  if (!refs.has(clean)) refs.set(clean, new Set());
  refs.get(clean).add(kind);
};
/* Os comentarios do proprio ficheiro FALAM de url(): «The markup paints the row
   icon with url(...)», «background-image: url("") su 74 schermate». Contar essas
   frases como referencias seria acusar o portal de apontar para um ficheiro que
   ninguem escreveu — um falso positivo, que e pior do que nao ter portao. */
const CODE = HTML.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/<!--[\s\S]*?-->/g, ' ');
for (const m of HTML.matchAll(/<meta\s+name="ext-resource-dependency"\s+content="([^"]*)"/gi)) addRef(m[1], 'meta ext-resource-dependency');
for (const m of CODE.matchAll(/\ssrc=["']([^"']*)["']/gi)) addRef(m[1], 'src=');
for (const m of CODE.matchAll(/\shref=["']([^"']*)["']/gi)) addRef(m[1], 'href=');
for (const m of CODE.matchAll(/url\(\s*(['"]?)([^)'"]*)\1\s*\)/gi)) addRef(m[2], 'url()');
for (const [p, where] of modelAssets) {
  if (!refs.has(p)) refs.set(p, new Set());
  refs.get(p).add('model:' + where.replace(/\.records\.\d+\./, '.records[].'));
}

const missingOnDisk = [];
for (const [p, kinds] of refs) {
  if (!fs.existsSync(path.join(CLIENT, p))) missingOnDisk.push({ path: p, from: [...kinds] });
}

/* ── 3. a varredura no browser ─────────────────────────────────────────────── */
const server = await serve(PORT, CLIENT);
const { browser, page, errors, noise, failed: loadFailed } = await open({ port: PORT });

/* O `open()` ja navegou, e um ouvinte pendurado depois disso perde o carregamento
   inicial — que e exatamente onde vivem os scripts, as fontes e o CSS. Recarrega-se
   uma vez com o ouvido ja ligado para que a lista de pedidos seja COMPLETA. O que
   o `open()` ja tinha ouvido nesse primeiro carregamento nao se deita fora: entra
   no juizo pela lista `failed` que ele devolve, senao a primeira volta seria um
   ponto cego. */
const responses = new Map();     // url -> status
const netFailed = [];
page.on('response', (r) => responses.set(r.url(), r.status()));
page.on('requestfailed', (r) => netFailed.push({ url: r.url(), why: (r.failure() || {}).errorText || '?' }));
/* O `<helmet>` do design system injecta os doze ficheiros de dados DEPOIS de o
   browser dizer «networkidle», e um reload disparado nessa cauda cancela o que
   ainda vinha a caminho. A primeira versao deste portao reprovou por isso: 18
   pedidos «ERR_ABORTED», e os mesmos 18 URLs serviram 200 na mesma execucao.

       UM PEDIDO CANCELADO NAO E UM FICHEIRO EM FALTA.

   Duas defesas, porque uma so nao chegava: espera-se que a cauda assente antes
   de recarregar, e um ERR_ABORTED conta-se a parte em vez de reprovar. Quem
   falta de verdade responde 404 — e isso o `responses` apanha. */
await page.waitForLoadState('networkidle').catch(() => {});
await page.waitForTimeout(1200);
await page.reload({ waitUntil: 'networkidle' });
await page.waitForTimeout(900);

/* Quais sao as telas? Pergunta-se ao DOM, nao a uma lista escrita a mao — uma
   lista escrita a mao envelhece calada no dia em que alguem acrescenta um ecra.
   O `nav()` do drive.mjs devolve TODOS os [title] da pagina, e nesses 34 vem
   tambem os tres icones da barra de topo e os vinte nomes de regiao do mapa:
   «Toscana», «Puglia», «Sicilia». Nenhum desses e uma tela.

       A BARRA LATERAL E UM <aside>. O QUE VIVE LA DENTRO E TELA.

   A primeira versao desta linha tentou distingui-los por `closest('svg')` — os
   nomes de regiao PARECEM <path> de um mapa. Nao sao: sao <div> dentro do
   <main>, e o teste devolveu zero. Vinte regioes entraram na lista de telas e o
   resumo anunciou «13 alcancadas, 20 NAO» — uma cobertura inventada. Mede-se a
   arvore em que o elemento vive, e confirma-se com o que o ecra devolve. */
const titles = await nav(page);
const inAside = new Set(await page.evaluate(() => [...document.querySelectorAll('aside [title]')]
  .map((e) => e.getAttribute('title')).filter(Boolean)));
const SCREENS = titles.filter((t) => inAside.has(t));
if (!SCREENS.length) { console.log(C.r('  nenhuma tela dentro de <aside> — o shell nao montou')); process.exit(1); }

const imgs = new Map();          // src -> {nw, visible, screens}
const domHrefs = new Map();      // href -> Set(screen)
const bgUrls = new Map();        // url absoluta -> Set(screen)
const emptyBg = [];                // elementos que pintam url("") — icone vazio visivel

const harvest = async (tag) => {
  const d = await page.evaluate(() => {
    const out = { imgs: [], hrefs: [], bg: [], empty: 0, emptyVisible: 0 };
    for (const i of document.images) {
      const r = i.getBoundingClientRect();
      out.imgs.push({ src: i.currentSrc || i.src || '', attr: i.getAttribute('src') || '',
        nw: i.naturalWidth, complete: i.complete, visible: r.width > 0 && r.height > 0 });
    }
    for (const a of document.querySelectorAll('[href]')) out.hrefs.push(a.getAttribute('href') || '');
    for (const e of document.querySelectorAll('*')) {
      const bi = getComputedStyle(e).backgroundImage;
      if (!bi || bi === 'none') continue;
      /* `url("")` e um slot de icone declarado vazio: o browser nao pede nada e
         o leitor ve um circulo em branco. Nao aparece em nenhum 404. */
      if (/url\(\s*(["']?)\1\s*\)/.test(bi)) {
        out.empty++;
        const r = e.getBoundingClientRect();
        if (r.width > 2 && r.height > 2) out.emptyVisible++;
        continue;
      }
      for (const m of bi.matchAll(/url\((['"]?)(.*?)\1\)/g)) if (m[2]) out.bg.push(m[2]);
    }
    return out;
  });
  for (const i of d.imgs) {
    const key = i.attr || i.src;
    const prev = imgs.get(key) || { ...i, screens: new Set() };
    prev.nw = Math.max(prev.nw, i.nw); prev.visible = prev.visible || i.visible;
    prev.screens.add(tag); imgs.set(key, prev);
  }
  for (const h of d.hrefs) { if (!domHrefs.has(h)) domHrefs.set(h, new Set()); domHrefs.get(h).add(tag); }
  for (const u of d.bg) { if (!bgUrls.has(u)) bgUrls.set(u, new Set()); bgUrls.get(u).add(tag); }
  if (d.empty) emptyBg.push({ screen: tag, slots: d.empty, visible: d.emptyVisible });
};

/* Uma tela anunciada pelo DOM que o clique nao alcanca e um buraco na COBERTURA
   deste portao, nao um defeito de asset: o que ele nao visitou, nao mediu. Fica
   impressa a vermelho no resumo e vai inteira para o --json. Quem reprova por
   ecra inalcancavel e o responsive.mjs, que tem essa pergunta por objeto — aqui
   duplicar o veredicto so daria dois vermelhos para o mesmo facto. */
const walked = [];
await harvest('(load)');
for (const s of SCREENS) {
  const ok = await clickTitle(page, s, 650);
  walked.push({ screen: s, reached: ok });
  if (ok) await harvest(s);
}
/* A ficha aberta e uma tela por direito proprio: e la que os icones de produto,
   de canal e de acao aparecem. Duas chegam para exercitar os dois ramos. */
await clickTitle(page, SCREENS[0], 650);
const ids = await caseIds(page);
for (const id of ids.slice(0, 2)) {
  await clickTitle(page, SCREENS[0], 550);
  if (await openCase(page, id, 650)) { walked.push({ screen: 'case:' + id, reached: true }); await harvest('case:' + id); }
}

await browser.close();
server.close();

/* ── 4. juizo ─────────────────────────────────────────────────────────────── */

/* LA1 — REDE. O /favicon.ico e servido 204 de proposito por drive.mjs: em
   producao quem o serve e o CDN, e contar esse pedido seria reprovar o portal
   pelo servidor de teste. Qualquer outra coisa acima de 400 conta. */
const isFavicon = (u) => /\/favicon\.ico(\?|$)/.test(u);
const ABORT = /ERR_ABORTED/;
const badStatus = [...responses].filter(([u, s]) => s >= 400 && !isFavicon(u)).map(([u, s]) => ({ url: u, status: s }));
const badNet = netFailed.filter((f) => !isFavicon(f.url) && !ABORT.test(f.why));
const aborted = netFailed.filter((f) => ABORT.test(f.why));
/* O que o `open()` ouviu na primeira volta, com a mesma regra: 4xx/5xx e falhas
   de rede que nao sejam cancelamentos nem o favicon que o servidor de teste
   responde 204 de proposito. */
const badFirstLoad = (loadFailed || []).filter((f) => !isFavicon(f) && !ABORT.test(f) && !/^204 /.test(f));
/* Conta-se o RECURSO partido, nao a queixa: o mesmo /assets/x.png pedido em duas
   voltas sao dois avisos e um ficheiro. Um numero que cresce com o numero de
   telas percorridas nao mede nada. */
const brokenUrls = new Set([
  ...badStatus.map((b) => b.url), ...badNet.map((b) => b.url),
  ...badFirstLoad.map((f) => (String(f).match(/https?:\/\/\S+/) || [String(f)])[0]),
]);
const netBroken = brokenUrls.size;

/* LA3 — LINKS EXTERNOS. Valida-se a FORMA, nunca se chama o host: um portao que
   depende da rede publica reprova no dia em que a YouTube tem soluços. Contam-se
   os hrefs que o DOM realmente carregava, porque o markup escreve `{{ v.url }}`
   e so o runtime sabe o que la vai. */
const externals = new Map();     // url -> Set(screen)
for (const [h, screens] of domHrefs) if (/^https?:/i.test(h || '')) externals.set(h, screens);
for (const m of CODE.matchAll(/\shref=["'](https?:[^"']*)["']/gi)) if (!externals.has(m[1])) externals.set(m[1], new Set(['markup']));
const malformed = [];
const hosts = new Map();
let insecure = 0;
for (const [u, screens] of externals) {
  let parsed = null;
  try { parsed = new URL(u); } catch { malformed.push({ url: u, why: 'não analisável como URL', screens: [...screens][0] }); continue; }
  const why = [];
  if (!/^https?:$/.test(parsed.protocol)) why.push('esquema ' + parsed.protocol);
  if (!parsed.hostname || !parsed.hostname.includes('.')) why.push('host sem ponto');
  if (/\s/.test(u)) why.push('espaço no URL');
  if (/\{\{|\}\}/.test(u)) why.push('marcador de template por substituir');
  if (/[…]$|\.\.\.$/.test(u)) why.push('URL truncado');
  if (/^https?:\/\/(localhost|127\.|0\.0\.0\.0)/i.test(u)) why.push('aponta para a máquina de quem publica');
  if (why.length) { malformed.push({ url: u, why: why.join(' + '), screens: [...screens][0] }); continue; }
  if (parsed.protocol === 'http:') insecure++;
  hosts.set(parsed.hostname, (hosts.get(parsed.hostname) || 0) + 1);
}

/* LA4 — IMAGENS PARTIDAS. `complete && naturalWidth === 0` e a definicao que o
   browser da de «pedi, terminei, e nao ha pixeis». Um <img> sem src nenhum nao
   e uma imagem partida, e um placeholder — nao conta. */
const brokenImgs = [...imgs.entries()]
  .filter(([k, i]) => k && i.complete && i.nw === 0)
  .map(([k, i]) => ({ ref: k, screens: [...i.screens].slice(0, 3), visible: i.visible }));

/* CE2 — o balde de marcadores. Conta-se DISTINTO: o mesmo aviso repete-se a
   cada parse (o reload duplica-o) e isso nao e um marcador novo. */
const noiseDistinct = [...new Set(noise)];

const okNet = netBroken === 0;
const okDisk = missingOnDisk.length === 0;
const okLinks = malformed.length === 0;
const okImgs = brokenImgs.length === 0;
const okErrors = errors.length === 0;
const okNoise = noiseDistinct.length <= NOISE_MAX;
const unreached = walked.filter((w) => !w.reached);

console.log('\n  SINTONIA · LINK_AND_ASSET_GATE + CONSOLE_ERROR_GATE');
console.log('  ' + '─'.repeat(100));
console.log(line(okNet, 'LA1', 'Every request the page makes returns < 400', 0, netBroken));
console.log(line(okDisk, 'LA2', 'Every referenced asset exists on disk', 0, missingOnDisk.length));
console.log(line(okLinks, 'LA3', 'Every external href is well-formed', 0, malformed.length));
console.log(line(okImgs, 'LA4', 'No <img> rendered with naturalWidth === 0', 0, brokenImgs.length));
console.log(line(okErrors, 'CE1', 'Zero pageerror / console.error in the sweep', 0, errors.length));
console.log(line(okNoise, 'CE2', `Template-placeholder SVG notices <= ${NOISE_MAX}`, '<=' + NOISE_MAX, noiseDistinct.length));
console.log('  ' + '─'.repeat(100));
console.log(`  TELAS PERCORRIDAS = ${walked.length} (${walked.filter((w) => w.reached).length} alcançadas${unreached.length ? ', ' + C.r(unreached.length + ' NÃO') : ''}) · PEDIDOS OUVIDOS = ${responses.size}`);
const statusTally = {};
for (const [, s] of responses) statusTally[s] = (statusTally[s] || 0) + 1;
console.log(`  STATUS = ${Object.entries(statusTally).sort().map(([s, n]) => `${s}×${n}`).join(' · ')}`
  + ` · falhas de rede = ${badNet.length}` + C.d(` (+${aborted.length} cancelados pelo reload, todos servidos 200 na mesma volta)`)
  + ` · da 1ª volta = ${badFirstLoad.length}`);
console.log(`  REFERÊNCIAS NO MARKUP+MODELO = ${refs.size} · EM FALTA NO DISCO = ${missingOnDisk.length}`);
console.log(`  CAMINHOS QUE O MODELO PUBLICA (iconAsset/aShape/…) = ${modelAssets.size} · slots declarados VAZIOS = ${modelEmptySlots.length} (${modelEmptySlots.join(', ') || '—'})`);
console.log(`  BACKGROUNDS PINTADOS EM TEMPO DE EXECUÇÃO = ${bgUrls.size} distintos · <img> no DOM = ${imgs.size}`);
const emptyVis = emptyBg.reduce((a, e) => a + e.visible, 0);
console.log(`  slots de ícone pintados url("") = ${emptyBg.reduce((a, e) => a + e.slots, 0)} ocorrências, ${emptyVis} com área visível${emptyVis ? ' ' + C.y('← círculo vazio no ecrã') : ''}`);
console.log(`  LINKS EXTERNOS = ${externals.size} distintos · HOSTS = ${hosts.size} · em http:// simples = ${insecure} · malformados = ${malformed.length}`);
console.log(`  RUÍDO DE TEMPLATE = ${noiseDistinct.length} distinto(s) / ${noise.length} ocorrência(s)`
  + (noiseDistinct.length === NOISE_BASELINE ? C.d(` · linha de base ${NOISE_BASELINE}, sem desvio`)
    : C.y(` ← DESVIO: a linha de base era ${NOISE_BASELINE}`)));

if (missingOnDisk.length) {
  console.log('\n  ' + C.r('ASSETS REFERENCIADOS QUE NÃO EXISTEM'));
  for (const m of missingOnDisk) console.log('   ' + C.r('✗') + ' ' + m.path.padEnd(52) + C.d(m.from.join(' · ')));
}
if (badStatus.length || badNet.length || badFirstLoad.length) {
  console.log('\n  ' + C.r('PEDIDOS QUE NÃO CHEGARAM'));
  for (const b of badStatus) console.log('   ' + C.r(b.status) + ' ' + b.url.slice(0, 110));
  for (const b of badNet) console.log('   ' + C.r('net') + ' ' + b.url.slice(0, 90) + ' :: ' + b.why);
  for (const b of badFirstLoad) console.log('   ' + C.r('1ª') + ' ' + String(b).slice(0, 120));
}
if (malformed.length) {
  console.log('\n  ' + C.r('LINKS EXTERNOS MALFORMADOS'));
  for (const m of malformed) console.log('   ' + C.r('✗') + ' ' + m.url.slice(0, 96) + '  ' + C.d('— ' + m.why + ' (' + m.screens + ')'));
}
if (brokenImgs.length) {
  console.log('\n  ' + C.r('IMAGENS PARTIDAS QUE O LEITOR VÊ'));
  for (const b of brokenImgs) console.log('   ' + C.r('✗') + ' ' + String(b.ref).slice(0, 90) + C.d(' — ' + b.screens.join(', ') + (b.visible ? ' · com área' : ' · sem área')));
}
if (errors.length) {
  console.log('\n  ' + C.r('ERROS DE CONSOLA'));
  for (const e of errors.slice(0, 12)) console.log('   ' + C.r('✗') + ' ' + e.slice(0, 150));
}

console.log('\n  HOSTS EXTERNOS CITADOS');
for (const [h, n] of [...hosts].sort((a, b) => b[1] - a[1])) console.log('   ' + String(n).padStart(4) + '  ' + h);
console.log('\n  RUÍDO DE TEMPLATE ACEITE (marcador dentro de atributo SVG)');
for (const n of noiseDistinct) console.log('   ' + C.d('· ' + n.slice(0, 140)));

if (JSON_OUT) {
  fs.writeFileSync(JSON_OUT, JSON.stringify({
    walked, statusTally, responses: [...responses].map(([url, status]) => ({ url, status })),
    netFailed, aborted, badFirstLoad, brokenUrls: [...brokenUrls], missingOnDisk, refs: [...refs].map(([p, k]) => ({ path: p, from: [...k] })),
    modelAssets: [...modelAssets].map(([p, at]) => ({ path: p, at })), modelEmptySlots,
    externals: [...externals].map(([u, s]) => ({ url: u, screens: [...s] })), malformed,
    hosts: [...hosts].map(([h, n]) => ({ host: h, n })), insecure,
    imgs: [...imgs].map(([k, i]) => ({ ref: k, nw: i.nw, visible: i.visible, screens: [...i.screens] })),
    brokenImgs, emptyBg, errors, noise: noiseDistinct,
  }, null, 1));
}

const FAIL = !okNet || !okDisk || !okLinks || !okImgs || !okErrors || !okNoise;
process.exit(FAIL ? 1 : 0);
