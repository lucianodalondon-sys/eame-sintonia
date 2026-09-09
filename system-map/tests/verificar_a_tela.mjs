#!/usr/bin/env node
/* A TELA DA FRESCURA, NUM BROWSER A SERIO — SETE CENARIOS
   ---------------------------------------------------------------------------
   ISTO NAO E UM PORTAO, E DIZE-LO E PARTE DO TRABALHO.

   `test_freshness.mjs` prova a LEI (49 provas, no CI, sem browser). Isto prova
   a TELA: que o `map.js` liga a lei aos factos certos e pinta o que decidiu. Ele
   precisa de um browser de verdade, e o CI deste repositorio nao tem nenhum — a
   cadeia do mapa nao carrega dependencia de terceiro, de proposito.

       UM PORTAO QUE NUNCA CORRE NAO E UM PORTAO. Este nao se disfarca de um.

   Corre-se a mao, com o playwright instalado FORA do repositorio:

       npm i playwright   (num directorio a parte)
       node system-map/tests/verificar_a_tela.mjs <raiz-servida> <commit>

   COMO SE PREPARA A RAIZ SERVIDA, E PORQUE ASSIM
   ----------------------------------------------
   Nao se escreve o `deployment.generated.json` a mao. Clona-se o repositorio,
   APAGA-SE DO DISCO o que o `.vercelignore` nao envia, e corre-se o publicador
   real com as variaveis da Vercel. O que a tela le e o que a build produz — se
   fosse escrito a mao, isto provaria a minha imaginacao.

       git clone . /tmp/vercel && cd /tmp/vercel
       rm -rf build data docs handoff research prototype supabase scripts tests \
              .github italia-portale/BASELINE
       find . -name '*.md' -not -path './.git/*' -delete
       VERCEL_GIT_COMMIT_SHA=$(git rev-parse HEAD) ... \
         node system-map/scripts/publicar_no_deploy.mjs

   So as respostas do GitHub sao interceptadas — para cada cenario ser
   DETERMINISTICO, e nao para as tornar convenientes. Cinco dos sete cenarios
   exigem que a tela NAO fique verde; se a interceptacao fosse complacente, eram
   esses cinco que reprovavam.
   --------------------------------------------------------------------------- */
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';

const RAIZ = process.argv[2];
const COMMIT = process.argv[3];
const TIPOS = { '.html':'text/html', '.js':'text/javascript', '.css':'text/css',
                '.json':'application/json', '.svg':'image/svg+xml', '.woff2':'font/woff2' };

const servidor = createServer(async (req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p.endsWith('/')) p += 'index.html';
  try {
    const corpo = await readFile(join(RAIZ, normalize(p)));
    res.writeHead(200, { 'Content-Type': TIPOS[extname(p)] || 'application/octet-stream' });
    res.end(corpo);
  } catch { res.writeHead(404).end('nao existe'); }
});
await new Promise(r => servidor.listen(0, r));
const PORTA = servidor.address().port;

const CENARIOS = [
  { nome: 'CURRENT · tudo alinhado',
    head: COMMIT, portao: { status:'completed', conclusion:'success' },
    espera: 'CURRENT' },
  { nome: 'STALE · a cabeca remota andou',
    head: 'a'.repeat(40), portao: { status:'completed', conclusion:'success' },
    espera: 'STALE' },
  { nome: 'UNKNOWN · o GitHub nao responde',
    head: null, portao: null, espera: 'UNKNOWN' },
  { nome: 'BROKEN · o portao do mapa reprovou este commit',
    head: COMMIT, portao: { status:'completed', conclusion:'failure' },
    espera: 'BROKEN' },
  { nome: 'UNKNOWN · o portao ainda esta a correr (corrida com o deploy)',
    head: COMMIT, portao: { status:'in_progress', conclusion:null },
    espera: 'UNKNOWN' },
  { nome: 'STALE · o mapa e de OUTRA arvore (impressao diferente)',
    head: COMMIT, portao: { status:'completed', conclusion:'success' },
    impressaoErrada: true, espera: 'STALE' },
  { nome: 'UNKNOWN · o portao correu mas com outro nome',
    head: COMMIT, portao: { status:'completed', conclusion:'success', nome:'outro-portao' },
    espera: 'UNKNOWN' },
];

const navegador = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
let falhas = 0, erros = [];
for (const c of CENARIOS) {
  const pagina = await navegador.newPage();
  pagina.on('pageerror', e => erros.push(`${c.nome}: ${e.message}`));
  await pagina.route('**/api.github.com/**', async (rota) => {
    const url = rota.request().url();
    if (c.head === null) return rota.abort('failed');
    if (url.includes('/check-runs')) {
      const p = c.portao;
      if (!p) return rota.abort('failed');
      return rota.fulfill({ status:200, contentType:'application/json',
        body: JSON.stringify({ total_count:1, check_runs:[
          { name: p.nome || 'SYSTEM MAP CHECK', status:p.status, conclusion:p.conclusion }]}) });
    }
    if (url.includes('/compare/')) {
      return rota.fulfill({ status:200, contentType:'application/json',
        body: JSON.stringify({ status:'ahead', ahead_by:7 }) });
    }
    return rota.fulfill({ status:200, contentType:'application/json',
      body: JSON.stringify({ sha: c.head }) });
  });
  if (c.impressaoErrada) {
    await pagina.route('**/deployment.generated.json', async (rota) => {
      const r = await rota.fetch(); const d = await r.json();
      d.MAP_SOURCE_TREE_FINGERPRINT = 'f'.repeat(64);
      d.MAP_BELONGS_TO_DEPLOYED_TREE = false;
      return rota.fulfill({ status:200, contentType:'application/json',
        body: JSON.stringify(d) });
    });
  }
  await pagina.goto(`http://127.0.0.1:${PORTA}/system-map/`, { waitUntil:'networkidle' });
  await pagina.waitForFunction(() => {
    const b = document.getElementById('syncBadge');
    return b && b.className.includes('sync-') && b.textContent.trim().length > 2;
  }, { timeout: 15000 }).catch(()=>{});
  const badge = await pagina.textContent('#syncBadge');
  const classe = await pagina.getAttribute('#syncBadge', 'class');
  const pecas = await pagina.evaluate(() => document.querySelectorAll('.node, .component, [data-id]').length);
  const barra = await pagina.evaluate(() => {
    const b = document.getElementById('staleBar'); return b && !b.hidden; });
  const ok = classe.includes(`sync-${c.espera.toLowerCase()}`);
  if (!ok) falhas++;
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${c.nome}`);
  console.log(`        badge=${JSON.stringify((badge||'').trim())} · classe=${classe} · barra_vermelha=${barra} · nos=${pecas}`);
  await pagina.close();
}
await navegador.close(); servidor.close();
if (erros.length) { console.log('\nERROS DE JS:'); erros.forEach(e=>console.log('  '+e)); }
console.log(`\nBROWSER=${falhas || erros.length ? 'FAIL' : 'PASS'} · ${CENARIOS.length - falhas}/${CENARIOS.length} cenarios · ${erros.length} erro(s) de JS`);
process.exit(falhas || erros.length ? 1 : 0);
