/* SINTONIA · DRIVE — o navegador de verdade, uma vez, para todos os portoes
   ---------------------------------------------------------------------------
   Cada portao anterior abria o seu proprio Chromium, servia a sua propria copia
   da pasta e reescrevia o mesmo `clickNav`. Tres coisas iguais escritas em
   quatro lugares divergem: um portao aprendia a clicar num elemento que o outro
   nao encontrava, e a diferenca passava por resultado.

       UM SO CLIQUE, UM SO SERVIDOR, UM SO LUGAR ONDE ELES VIVEM.

   Este modulo NAO julga nada. Ele abre, serve, clica, le o DOM e devolve o que
   viu. O juizo e de quem chama — e por isso pode ser medido.
   --------------------------------------------------------------------------- */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const CLIENT = path.resolve(HERE, '..', '..', 'client');

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.css': 'text/css', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.ttf': 'font/ttf', '.otf': 'font/otf',
  '.woff': 'font/woff', '.woff2': 'font/woff2', '.pdf': 'application/pdf',
};

/** Serve a pasta client exactly as Vercel serves it (cleanUrls included). */
export function serve(port = 8899, dir = CLIENT) {
  const server = http.createServer((req, res) => {
    const url = decodeURIComponent((req.url || '/').split('?')[0]);
    /* O browser pede /favicon.ico sozinho. Em producao quem responde e o CDN;
       contar esse 404 seria reprovar o site pelo servidor de teste. */
    if (url === '/favicon.ico') { res.writeHead(204).end(); return; }
    let rel = url === '/' ? '/portale.html' : url;
    let file = path.join(dir, rel);
    /* cleanUrls: /portale resolve para /portale.html, como na Vercel. */
    if (!fs.existsSync(file) && !path.extname(file) && fs.existsSync(file + '.html')) file += '.html';
    if (!file.startsWith(dir)) { res.writeHead(403).end('no'); return; }
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(404, { 'content-type': 'text/plain' }).end('404 ' + rel); return; }
      res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' }).end(buf);
    });
  });
  return new Promise((r) => server.listen(port, () => r(server)));
}

const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));

/* Cinco atributos SVG do template carregam o seu proprio marcador — d="{{ … }}"
   — quando o browser analisa o HTML, antes de o renderer os substituir. E o
   template a ser template, nao um erro de JavaScript. Conta-se a parte: se o
   numero muda, alguem acrescentou um marcador dentro de um atributo. */
const TEMPLATE_ATTR = /attribute (d|cx|cy|x|y|r|points|width|height|transform|viewBox):.*\{\{/;

export async function open({ port = 8899, width = 1440, height = 1000, page: url = '/portale.html' } = {}) {
  const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ viewport: { width, height }, acceptDownloads: true });
  const page = await ctx.newPage();
  const errors = [], noise = [], failed = [], logs = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (m) => {
    const t = m.text().slice(0, 260);
    logs.push(m.type() + ': ' + t);
    if (m.type() !== 'error') return;
    (TEMPLATE_ATTR.test(t) ? noise : errors).push('console: ' + t);
  });
  page.on('requestfailed', (r) => failed.push(r.url().slice(0, 160) + ' :: ' + ((r.failure() || {}).errorText || '')));
  page.on('response', (r) => { if (r.status() >= 400) failed.push(r.status() + ' ' + r.url().slice(0, 160)); });
  await page.goto(`http://localhost:${port}${url}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(700);
  return { browser, ctx, page, errors, noise, failed, logs };
}

/* ── CLIQUE ────────────────────────────────────────────────────────────────
   O renderer compila style="" numa classe gerada, portanto um seletor por
   atributo de estilo encontra zero elementos sem dizer que encontrou zero. E o
   texto vive num <span> que nao carrega o handler: o clique tem de subir ate o
   antecessor que o browser considera clicavel — onde o leitor realmente premo. */
const CLICKABLE = `(n) => { for (let i = 0; i < 5 && n; i++) { const cs = getComputedStyle(n);
  if (cs.cursor === 'pointer' || n.onclick || n.tagName === 'BUTTON' || n.tagName === 'A') return n; n = n.parentElement; } return null; }`;

export async function clickTitle(page, label, wait = 420) {
  const ok = await page.evaluate(([t, up]) => {
    const hit = document.querySelector(`[title="${t.replace(/"/g, '\\"')}"]`);
    if (!hit) return false;
    const target = eval(up)(hit) || hit; target.click(); return true;
  }, [label, CLICKABLE]);
  if (ok) await page.waitForTimeout(wait);
  return ok;
}

export async function clickText(page, txt, wait = 380) {
  const ok = await page.evaluate(([t, up]) => {
    const all = [...document.querySelectorAll('span,div,a,button')];
    const hit = all.find((e) => (e.textContent || '').trim() === t)
      || all.find((e) => (e.textContent || '').trim().includes(t) && (e.textContent || '').trim().length < t.length + 40);
    if (!hit) return false;
    const target = eval(up)(hit) || hit; target.click(); return true;
  }, [txt, CLICKABLE]);
  if (ok) await page.waitForTimeout(wait);
  return ok;
}

export async function clickSelector(page, sel, wait = 380) {
  const ok = await page.evaluate(([s, up]) => {
    const hit = document.querySelector(s);
    if (!hit) return false;
    const target = eval(up)(hit) || hit; target.click(); return true;
  }, [sel, CLICKABLE]);
  if (ok) await page.waitForTimeout(wait);
  return ok;
}

/** Abre a primeira ficha de oportunidade do radar (ou a de um id concreto). */
export async function openCase(page, id = null, wait = 480) {
  const ok = await page.evaluate(([wanted, up]) => {
    const cards = [...document.querySelectorAll('[data-case]')].filter((c) => c.getAttribute('data-case'));
    const hit = wanted ? cards.find((c) => c.getAttribute('data-case') === wanted) : cards[0];
    if (!hit) return false;
    const target = eval(up)(hit) || hit; target.click(); return true;
  }, [id, CLICKABLE]);
  if (ok) await page.waitForTimeout(wait);
  return ok;
}

/** Todos os ids de ficha visiveis agora. */
export const caseIds = (page) => page.evaluate(() =>
  [...document.querySelectorAll('[data-case]')].map((c) => c.getAttribute('data-case')).filter(Boolean));

/** O texto que ficou no ecra — o que o leitor le, nao o que o DOM guarda. */
export const screenText = (page) => page.evaluate(() => (document.body.innerText || '').replace(/ /g, ' '));

/** Todo elemento que o browser considera clicavel, com o que o leitor le nele. */
export const clickables = (page) => page.evaluate(() => {
  const seen = [];
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const isClick = cs.cursor === 'pointer' || !!el.onclick || el.tagName === 'BUTTON' || el.tagName === 'A';
    if (!isClick) continue;
    /* Um filho clicavel dentro de um pai clicavel e o MESMO botao para o leitor.
       Conta-se o mais externo — senao uma ficha com seis <span> vale seis botoes.
       O `onclick` do ANTECESSOR nao serve de prova: o runtime do design system
       pendura um handler delegado na raiz do host, que e antecessor de tudo. A
       primeira versao desta regra contava 1 clicavel numa tela com 12 fichas,
       porque essa raiz excluia o resto. Vale o que o leitor ve: o cursor. */
    let p = el.parentElement, nested = false;
    while (p) { const pc = getComputedStyle(p); if (pc.cursor === 'pointer' || p.tagName === 'A' || p.tagName === 'BUTTON') { nested = true; break; } p = p.parentElement; }
    if (nested) continue;
    const r = el.getBoundingClientRect();
    seen.push({
      tag: el.tagName.toLowerCase(),
      /* Il testo si NORMALIZZA qui, una volta: chi indicizza e chi clicca devono
         confrontare la stessa stringa. Salvandolo grezzo e collassandolo solo
         dopo, «SINTONIA\n ADAMA ITALIA» tagliato a 70 caratteri grezzi non
         coincide piu con lo stesso testo collassato, e diciassette controlli
         sempre presenti risultavano introvabili.

             DUE NORMALIZZAZIONI DELLA STESSA STRINGA SONO DUE STRINGHE. */
      text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 70),
      title: el.getAttribute('title') || '',
      href: el.getAttribute('href') || '',
      /* `onclick` proprio, ou o cursor que o autor pos de proposito. Um <span>
         com cursor:pointer e sem handler proprio pode ainda assim funcionar,
         porque o handler esta no elemento que o envolve — por isso quem julga
         botao morto tem de CLICAR, nao ler esta linha. */
      hasHandler: !!el.onclick,
      pointer: getComputedStyle(el).cursor === 'pointer',
      w: Math.round(r.width), h: Math.round(r.height),
      visible: r.width > 0 && r.height > 0,
    });
  }
  return seen;
});

/** Uma impressao digital do estado: que ecra, quantas fichas, que titulo. */
export const fingerprint = (page) => page.evaluate(() => {
  const t = (document.body.innerText || '');
  return { chars: t.length, cases: document.querySelectorAll('[data-case]').length, head: t.slice(0, 90).replace(/\s+/g, ' ') };
});

export const shot = async (page, dir, name) => {
  if (!dir) return null;
  fs.mkdirSync(dir, { recursive: true });
  const f = path.join(dir, name.replace(/[^a-z0-9_.-]/gi, '_') + '.png');
  await page.screenshot({ path: f, fullPage: false });
  return f;
};

/* ── impressao ─────────────────────────────────────────────────────────────
   O nome das cores e das fontes tal como o browser as calculou. Ler o CSS-fonte
   nao prova nada: o que decide e o valor computado no elemento. */
export const computedSurvey = (page) => page.evaluate(() => {
  const out = { bg: {}, color: {}, font: {}, radius: {}, caps: [] };
  const bump = (o, k) => { o[k] = (o[k] || 0) + 1; };
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    if (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)') bump(out.bg, cs.backgroundColor);
    const txt = (el.childNodes.length && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) ;
    if (txt) {
      bump(out.color, cs.color);
      bump(out.font, (cs.fontFamily || '').split(',')[0].replace(/["']/g, ''));
      const s = (el.textContent || '').trim();
      /* ALL CAPS num titulo: tamanho grande, letras todas maiusculas, mais de
         uma palavra. text-transform conta como caps porque o leitor le caps. */
      const fs2 = parseFloat(cs.fontSize) || 0;
      const upper = cs.textTransform === 'uppercase' || (s === s.toUpperCase() && /[A-Z]{2}/.test(s));
      if (fs2 >= 16 && upper && s.length > 3 && s.length < 120) out.caps.push({ text: s.slice(0, 70), size: fs2 });
    }
    if (parseFloat(cs.borderTopLeftRadius) > 0) bump(out.radius, cs.borderTopLeftRadius);
  }
  return out;
});

/** Overflow horizontal: o que o leitor tem de arrastar para ler. */
export const overflow = (page) => page.evaluate(() => {
  const de = document.documentElement;
  const wide = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.right > de.clientWidth + 2 && r.width > 4 && r.height > 4) {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      /* Uma faixa que rola por dentro (overflow-x:auto) e uma decisao, nao um
         defeito: o leitor rola a faixa, nao a pagina. */
      let p = el.parentElement, inScroller = false;
      while (p) { const pc = getComputedStyle(p); if (pc.overflowX === 'auto' || pc.overflowX === 'scroll') { inScroller = true; break; } p = p.parentElement; }
      if (inScroller) continue;
      wide.push({ tag: el.tagName.toLowerCase(), right: Math.round(r.right), text: (el.textContent || '').trim().slice(0, 50) });
    }
  }
  return { docWidth: de.clientWidth, scrollWidth: de.scrollWidth, bodyScroll: document.body.scrollWidth, offenders: wide.slice(0, 12) };
});

export const nav = (page) => page.evaluate(() =>
  [...document.querySelectorAll('[title]')].map((e) => e.getAttribute('title')).filter(Boolean));


/* ── O MESMO CRITERIO, PARA CONTAR E PARA CLICAR ───────────────────────────
   `clickables` aprendeu que o `onclick` do ANTECESSOR nao serve de prova — o
   runtime pendura um handler delegado na raiz. Quem escreve um segundo portao
   reescreve o criterio de memoria e volta a cair no mesmo buraco: contei 1
   clicavel numa tela com 33.

       UM CRITERIO DUPLICADO E DOIS CRITERIOS QUE VAO DIVERGIR.

   Portanto o indice e o clique saem daqui, do mesmo lugar. */
export const clickAt = (page, index) => page.evaluate((idx) => {
  const els = [];
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const isClick = cs.cursor === 'pointer' || !!el.onclick || el.tagName === 'BUTTON' || el.tagName === 'A';
    if (!isClick) continue;
    let p = el.parentElement, nested = false;
    while (p) { const pc = getComputedStyle(p); if (pc.cursor === 'pointer' || p.tagName === 'A' || p.tagName === 'BUTTON') { nested = true; break; } p = p.parentElement; }
    if (nested) continue;
    els.push(el);
  }
  const el = els[idx];
  if (!el) return { clicked: false, reason: 'index out of range (' + els.length + ' controls)' };
  const r = el.getBoundingClientRect();
  if (r.width < 1 || r.height < 1) return { clicked: false, reason: 'zero box' };
  el.scrollIntoView({ block: 'center' });
  /* Chi giudica deve poter verificare CHE COSA ha cliccato: un verdetto
     attribuito al controllo sbagliato e peggio di nessun verdetto. */
  const what = (el.getAttribute('title') || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60);
  try { el.click(); } catch (e) { return { clicked: false, reason: 'threw: ' + e.message, what }; }
  return { clicked: true, what };
}, index);

/* ── UN CONTROLLO SI CHIAMA, NON SI CONTA ──────────────────────────────────
   Indirizzare per POSIZIONE sembrava ragionevole: si elencano i clicabili e si
   clicca il numero i. Ma il renderer ridisegna, un pannello si apre, un menu si
   chiude, e la lista non e piu quella: il portone registrava «Notifications» e
   cliccava «Help», registrava «MOSTRA SCENARI» e cliccava una tendina.

       UN VERDETTO ATTRIBUITO AL CONTROLLO SBAGLIATO E PEGGIO DI NESSUN VERDETTO.

   La chiave e cio che il controllo E: tag, titolo, testo, e l'ordinale fra i
   suoi omonimi. Sopravvive a un re-render perche non dipende da chi gli sta
   accanto. */
export const keyOf = (c) => [c.tag, c.title || '', (c.text || '').replace(/\s+/g, ' ').trim().slice(0, 70), c.nth || 0].join('§');

export const clickKey = (page, key) => page.evaluate((k) => {
  const parts = k.split('\u00a7');
  const [tag, title, text, nthS] = [parts[0], parts[1], parts[2], parts[3]];
  const nth = Number(nthS) || 0;
  const els = [];
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const isClick = cs.cursor === 'pointer' || !!el.onclick || el.tagName === 'BUTTON' || el.tagName === 'A';
    if (!isClick) continue;
    let p = el.parentElement, nested = false;
    while (p) { const pc = getComputedStyle(p); if (pc.cursor === 'pointer' || p.tagName === 'A' || p.tagName === 'BUTTON') { nested = true; break; } p = p.parentElement; }
    if (nested) continue;
    els.push(el);
  }
  const match = els.filter((el) => el.tagName.toLowerCase() === tag
    && (el.getAttribute('title') || '') === title
    && (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 70) === text);
  const el = match[nth];
  if (!el) return { clicked: false, reason: 'not present now (' + match.length + ' of this identity)' };
  const r = el.getBoundingClientRect();
  if (r.width < 1 || r.height < 1) return { clicked: false, reason: 'zero box' };
  el.scrollIntoView({ block: 'center' });
  const what = (el.getAttribute('title') || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60);
  try { el.click(); } catch (e) { return { clicked: false, reason: 'threw: ' + e.message, what }; }
  return { clicked: true, what };
}, key);

export const C = { g: (s) => `\x1b[32m${s}\x1b[0m`, r: (s) => `\x1b[31m${s}\x1b[0m`, y: (s) => `\x1b[33m${s}\x1b[0m`, d: (s) => `\x1b[2m${s}\x1b[0m` };
export const line = (ok, id, name, exp, got) =>
  `  ${ok ? C.g('PASS') : C.r('FAIL')}  ${String(id).padEnd(5)} ${String(name).padEnd(52)} exp ${String(exp).padEnd(6)} got ${got}`;
