/* D156 · item 6 do LAB — a tela ESCAPA o texto de ataque do pote DEMO.
   O pote sintetico traz, no PORQUE de SINT-OP-1, `<script>alert('porque')</script>`. Aqui abre-se o preview NO AR
   num navegador real, e mede-se: (1) nenhum dialogo (alert) abriu; (2) nenhum <script> da pagina contem o ataque;
   (3) o ataque aparece como TEXTO visivel. Escreve um JSON e uma captura. So le; nao publica nada.
   uso: node provas/l3/escapa_o_ataque.mjs --base <URL do preview> --saida <pasta> */
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = (arg('base', '') || '').replace(/\/+$/, '');
const SAIDA = arg('saida', '');
if (!BASE || !SAIDA) { console.error('uso: --base <URL> --saida <pasta>'); process.exit(2); }
const ATAQUE = "<script>alert('porque')</script>";
const EXEC = [process.env.SINTONIA_CHROMIUM, 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => p && fs.existsSync(p));

fs.mkdirSync(SAIDA, { recursive: true });
const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });
const telas = [];
try {
  for (const [nome, rota] of [['debug', '/portale#debug-intelligence-pot'], ['radar', '/portale#meeting'],
    ['radarfuturo', '/portale#radarfuturo']]) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const dialogos = [];
    page.on('dialog', async (d) => { dialogos.push(d.message()); await d.dismiss(); });
    await page.goto(BASE + rota, { waitUntil: 'networkidle', timeout: 90000 });
    await page.waitForTimeout(2500);
    const m = await page.evaluate((a) => ({
      TEXTO_VISIVEL: document.body.innerText.includes(a),
      SCRIPTS_COM_O_ATAQUE: [...document.querySelectorAll('script')].filter((s) => s.textContent.includes("alert('porque')")).length,
      ELEMENTOS_SCRIPT_NO_BODY: [...document.body.querySelectorAll('script')].map((s) => s.textContent.slice(0, 60)),
      BARRA: [...document.querySelectorAll('[data-nav-view="meeting"],[data-nav-view="radarfuturo"]')].map((e) => e.innerText.replace(/\s+/g, ' ')),
    }), ATAQUE);
    const cap = path.join(SAIDA, `escapa-${nome}.png`);
    /* no debug, a captura e a do proprio texto do ataque, tal como o leitor o ve */
    const alvo = page.getByText("alert('porque')", { exact: false }).first();
    if (m.TEXTO_VISIVEL && await alvo.count()) {
      await alvo.scrollIntoViewIfNeeded();
      await page.screenshot({ path: cap, fullPage: false });
    } else await page.screenshot({ path: cap, fullPage: false });
    telas.push({ TELA: nome, URL: BASE + rota, DIALOGOS_ABERTOS: dialogos, ...m, CAPTURA: path.basename(cap) });
    await page.close();
  }
} finally { await browser.close(); }
/* SCRIPTS_COM_O_ATAQUE conta tambem o <script> que CARREGA o envelope (o pote e dado JSON dentro dele) — por isso a
   prova de execucao e o dialogo, e a de escape e o texto visivel; um <script> no BODY com o ataque seria injecao. */
const injetado = telas.some((t) => t.ELEMENTOS_SCRIPT_NO_BODY.some((s) => s.includes("alert('porque')")));
const debug = telas.find((t) => t.TELA === 'debug');
const r = { BASE, QUANDO: new Date().toISOString(), ATAQUE, TELAS: telas,
  VEREDITO: telas.every((t) => t.DIALOGOS_ABERTOS.length === 0) && !injetado && debug.TEXTO_VISIVEL ? 'ESCAPA' : 'FALHA' };
fs.writeFileSync(path.join(SAIDA, 'ESCAPA-O-ATAQUE.json'), JSON.stringify(r, null, 1) + '\n');
console.log(JSON.stringify({ VEREDITO: r.VEREDITO, TELAS: telas.map((t) => [t.TELA, t.DIALOGOS_ABERTOS.length, t.TEXTO_VISIVEL, t.BARRA]) }));
process.exit(r.VEREDITO === 'ESCAPA' ? 0 : 1);
