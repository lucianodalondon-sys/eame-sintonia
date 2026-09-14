/* PROVA VISUAL DO SYSTEM MAP — corre fora do repositorio, com o browser do
   ambiente. Nao e um portao: e a fotografia que a missao exige como prova. */
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { mkdirSync } from 'node:fs';

const RAIZ = process.argv[2];
const SAIDA = process.argv[3];
const TAG = process.argv[4] || 'x';
mkdirSync(SAIDA, { recursive: true });

const MIME = { '.html':'text/html', '.js':'text/javascript', '.css':'text/css',
               '.json':'application/json', '.svg':'image/svg+xml',
               '.woff2':'font/woff2', '.woff':'font/woff', '.png':'image/png' };

const srv = createServer(async (req, res) => {
  let p = normalize(decodeURIComponent(req.url.split('?')[0]));
  if (p.endsWith('/')) p += 'index.html';
  try {
    const buf = await readFile(join(RAIZ, p));
    res.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
    res.end(buf);
  } catch { res.writeHead(404); res.end('nao ha'); }
});
await new Promise(r => srv.listen(0, r));
const base = `http://127.0.0.1:${srv.address().port}`;

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
// O GITHUB NAO E CHAMADO: a frescura nao e o objecto desta prova, e uma rede
// lenta tornaria a fotografia nao-determinista.
await page.route('**api.github.com/**', r => r.abort());
page.on('pageerror', e => console.log('ERRO NA PAGINA:', e.message));

const tirar = async (nome, antes) => {
  if (antes) await antes();
  await page.waitForTimeout(700);
  await page.screenshot({ path: join(SAIDA, `${TAG}-${nome}.png`) });
  console.log('  ·', `${TAG}-${nome}.png`);
};

await page.goto(base + '/system-map/', { waitUntil: 'load' });
await page.waitForFunction(() => document.querySelectorAll('.node').length > 100, { timeout: 20000 });
await page.waitForTimeout(1200);

await tirar('01-geral');
// centra a camera na peca, ao zoom em que o cartao se le
const olhar = async (id) => page.evaluate((i) => {
  const el = document.getElementById('node-' + i);
  const vp = document.getElementById('viewport');
  if (!el) return;
  el.click();
  const w = document.getElementById('world');
  const m = /scale\(([\d.]+)\)/.exec(w.style.transform);
  const r = vp.getBoundingClientRect();
  const x = parseFloat(el.style.left), y = parseFloat(el.style.top);
  const s = 0.62;
  w.style.transform = `translate(${r.width / 2 - x * s - 140}px,${
    r.height / 2 - y * s - 56}px) scale(${s})`;
}, id);

await tirar('02-coleta', async () => {
  await page.evaluate(() => {
    const b = document.querySelector('.famBtn[data-fam="F-COLETA"]');
    if (b) b.click();
  });
});
await tirar('03-selecao', async () => {
  await page.evaluate(() => {
    const b = document.querySelector('.famBtn[data-fam="F-COLETA"]');
    if (b) b.click();
  });
  await olhar('C-ADMISSAO');
});
await tirar('04-unknown', async () => { await olhar('C-READY'); });
await tirar('05-busca', async () => {
  await page.evaluate(() => {
    const s = document.getElementById('search');
    s.value = 'admissao'; s.dispatchEvent(new Event('input', { bubbles: true }));
  });
});
await tirar('06-portal', async () => {
  await page.evaluate(() => {
    const s = document.getElementById('search'); s.value = '';
    s.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await olhar('C-PORTAL-DADOS');
});
await tirar('07-controlo', async () => { await olhar('C-MAPA-GERADOR'); });
await tirar('08-caminho', async () => {
  await page.evaluate(() => {
    const b = document.getElementById('pathBtn'); if (b) b.click();
  });
});

await browser.close();
srv.close();
console.log('FOTOGRAFIAS=OK');
