/* SINTONIA · BRANDWELL_COLOR_AUDIT + TYPOGRAPHY_AUDIT
   ---------------------------------------------------------------------------
   node audit/brandwell.mjs [--base http://host] [--json file]

   NAO le o CSS. Le o DOM CALCULADO, ecra por ecra, e faz tres perguntas que um
   ser humano faria com o manual na mao:

     1  esta cor esta na paleta oficial da ADAMA?
     2  este texto e legivel sobre o fundo que lhe ficou por baixo?
     3  este titulo esta em CAIXA ALTA, que o manual proibe para titulos?

   A primeira e a unica que um grep tambem responderia — e responderia mal, porque
   uma cor pode entrar por um componente do design system, por um `filter`, ou por
   um valor calculado que nao esta escrito em lado nenhum. As outras duas nao tem
   versao em grep: dependem do que ficou por baixo e de que tamanho ficou.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import { serve, open, clickTitle, openCase, nav, C, line } from './lib/drive.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = arg('base', null);
const JSONOUT = arg('json', null);
const PORT = Number(arg("port", 8977));

/* ── A PALETA OFICIAL ─────────────────────────────────────────────────────────
   Copiada de _ds/adama-brandwell/tokens/colors.css, que por sua vez vem do
   BrandWell com CMYK e Pantone ao lado. Nada aqui foi escolhido: os unicos
   valores acrescentados sao TINTOS DE ADAMA EARTH, e o manual diz textualmente
   «Any tint of ADAMA Earth is permitted; tints of Primary, Secondary or Utility
   are not». */
const PALETTE = {
  '#009845': 'ADAMA Green', '#00783F': 'Secondary Corporate Green', '#978B87': 'ADAMA Earth',
  '#F89E18': 'Crop Enhancement', '#7DB41E': 'Weed Control', '#00A0DF': 'Disease Control', '#9D1D96': 'Pest Control',
  '#F5B317': 'Secondary Yellow', '#93CC23': 'Secondary Green', '#00698F': 'Secondary Blue', '#752157': 'Secondary Purple',
  '#5F504D': 'Text Grey', '#FFFFFF': 'White', '#000000': 'Black',
  '#F4F2F2': 'Earth 10%', '#E5E1E0': 'Earth 20%', '#CBC5C3': 'Earth 40%', '#B1A9A7': 'Earth 60%', '#A39D9A': 'Earth 80%',
};
/* Uma justificacao por excecao, escrita, ou nao e uma excecao — e um descuido.
   As tres primeiras vem do pacote do design system e nao deste portal. */
const ALLOWED_EXTRA = {
  '#EFEFEF': 'plano de fundo do Button do proprio pacote _ds/adama-brandwell (componente oficial)',
  '#EAE8E7': 'a-corporate-2.png · recorte oficial do shape «A» ADAMA, tinto de Earth',
  '#9A8D88': 'container-earth.png · shape de container oficial ADAMA',
  '#EAE8E6': 'anti-aliasing do shape «A» sobre branco',
};

const hex = (c) => {
  const m = /rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([0-9.]+))?\)/.exec(c || '');
  if (!m) return null;
  const a = m[4] === undefined ? 1 : parseFloat(m[4]);
  if (a === 0) return null;                       /* transparente nao pinta nada */
  return { hex: '#' + [1, 2, 3].map((i) => Number(m[i]).toString(16).padStart(2, '0').toUpperCase()).join(''), a,
    rgb: [1, 2, 3].map((i) => Number(m[i])) };
};

/* Tinto de Earth = Earth misturado com branco. Aceita-se qualquer proporcao,
   com 2/255 de tolerancia para o arredondamento do navegador. */
const EARTH = [151, 139, 135];
const isEarthTint = ([r, g, b]) => {
  for (let t = 0; t <= 100; t++) {
    const k = t / 100;
    if (Math.abs(r - (EARTH[0] + (255 - EARTH[0]) * k)) <= 2
      && Math.abs(g - (EARTH[1] + (255 - EARTH[1]) * k)) <= 2
      && Math.abs(b - (EARTH[2] + (255 - EARTH[2]) * k)) <= 2) return true;
  }
  return false;
};
const official = (h, rgb) => !!PALETTE[h] || !!ALLOWED_EXTRA[h] || isEarthTint(rgb);

const server = BASE ? null : await serve(PORT);
const { browser, page, errors } = await open(BASE ? { port: 0, page: '/' } : { port: PORT });
if (BASE) { await page.goto(BASE + '/portale', { waitUntil: 'networkidle' }); await page.waitForTimeout(900); }

/* ── a leitura, feita no navegador ─────────────────────────────────────────── */
const SURVEY = `() => {
  const out = { colors: [], text: [], caps: [], fonts: {}, radii: {}, pills: [] };
  const solid = (el) => {
    /* O fundo efetivo de um texto e o primeiro antecessor que pinta algo. Sem
       isto o contraste mede-se contra 'transparent' e da sempre otimo. */
    let n = el;
    while (n && n !== document.documentElement) {
      const c = getComputedStyle(n).backgroundColor;
      const m = /rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([0-9.]+))?\\)/.exec(c);
      if (m && (m[4] === undefined || parseFloat(m[4]) > 0.55)) return c;
      n = n.parentElement;
    }
    return 'rgb(255, 255, 255)';
  };
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.06) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const tag = el.tagName.toLowerCase();
    if (tag === 'x-dc' || tag === 'helmet' || tag === 'template') continue;
    for (const prop of ['backgroundColor', 'borderTopColor', 'borderBottomColor', 'borderLeftColor', 'borderRightColor']) {
      const v = cs[prop];
      if (v && v !== 'rgba(0, 0, 0, 0)') {
        /* uma borda de largura 0 nao pinta */
        if (prop !== 'backgroundColor' && parseFloat(cs[prop.replace('Color', 'Width')]) === 0) continue;
        out.colors.push({ v, prop, tag, text: (el.textContent || '').trim().slice(0, 40) });
      }
    }
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!own) continue;
    const s = (el.textContent || '').trim();
    out.colors.push({ v: cs.color, prop: 'color', tag, text: s.slice(0, 40) });
    out.text.push({ fg: cs.color, bg: solid(el), size: parseFloat(cs.fontSize), weight: cs.fontWeight,
      text: s.slice(0, 62), tag });
    const fam = (cs.fontFamily || '').split(',')[0].replace(/["']/g, '');
    out.fonts[fam] = (out.fonts[fam] || 0) + 1;
    const size = parseFloat(cs.fontSize) || 0;
    const upper = cs.textTransform === 'uppercase' || (s === s.toUpperCase() && /[A-Z]{2}/.test(s));
    /* TITULO = 16px ou mais. Um rotulo de 8px em caixa alta e o tratamento de
       aba/etiqueta que o manual usa; um titulo de 19px em caixa alta e o que
       ele proibe. A regua e o tamanho, porque e o tamanho que faz um titulo. */
    if (size >= 16 && upper && s.length > 3 && s.length < 160) /* L'UNICA ECCEZIONE, E CON IL MOTIVO SCRITTO ACCANTO: «ADAMA sempre in
         maiuscolo» e una REGOLA DI MARCA, e SINTONIA e il nome del prodotto nel
         logotipo. Una allowlist senza motivo e un portone spento. */
      if (!/^(SINTONIA|ADAMA)$/.test(s.trim())) out.caps.push({ text: s.slice(0, 80), size, tag });
    if (parseFloat(cs.borderTopLeftRadius) > 0) {
      const k = cs.borderTopLeftRadius;
      out.radii[k] = (out.radii[k] || 0) + 1;
    }
  }
  return out;
}`;

const LUM = (rgb) => { const f = rgb.map((v) => { const c = v / 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }); return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]; };
const ratio = (a, b) => { const [x, y] = [LUM(a), LUM(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };

const screens = [];
const seen = { offPalette: new Map(), lowContrast: new Map(), caps: new Map(), fonts: {}, radii: {} };

async function survey(name) {
  const r = await page.evaluate(eval(SURVEY));
  screens.push(name);
  for (const c of r.colors) {
    const h = hex(c.v); if (!h) continue;
    if (!official(h.hex, h.rgb)) {
      const k = h.hex + '|' + c.prop;
      if (!seen.offPalette.has(k)) seen.offPalette.set(k, { hex: h.hex, prop: c.prop, n: 0, where: name, sample: c.text });
      seen.offPalette.get(k).n++;
    }
  }
  for (const t of r.text) {
    const f = hex(t.fg), b = hex(t.bg);
    if (!f || !b) continue;
    const big = t.size >= 18.66 || (t.size >= 14 && Number(t.weight) >= 700);
    const need = big ? 3.0 : 4.5;
    const got = ratio(f.rgb, b.rgb);
    if (got < need) {
      const k = f.hex + '>' + b.hex + '|' + Math.round(t.size);
      if (!seen.lowContrast.has(k)) seen.lowContrast.set(k, { fg: f.hex, bg: b.hex, size: t.size, need, got: Math.round(got * 100) / 100, n: 0, where: name, sample: t.text });
      seen.lowContrast.get(k).n++;
    }
  }
  for (const c of r.caps) { const k = c.text; if (!seen.caps.has(k)) seen.caps.set(k, { ...c, where: name }); }
  for (const [k, v] of Object.entries(r.fonts)) seen.fonts[k] = (seen.fonts[k] || 0) + v;
  for (const [k, v] of Object.entries(r.radii)) seen.radii[k] = (seen.radii[k] || 0) + v;
}

await survey('HOME');
const NAVS = (await nav(page)).filter((l, i, a) => a.indexOf(l) === i);
const SCREENS = NAVS.filter((l) => !/^(Valle|Trentino|Friuli|Piemonte|Lombardia|Veneto|Liguria|Emilia|Toscana|Marche|Umbria|Abruzzo|Lazio|Molise|Campania|Puglia|Basilicata|Calabria|Sicilia|Sardegna)/.test(l));
for (const l of SCREENS) { if (await clickTitle(page, l, 500)) await survey(l); }
await clickTitle(page, NAVS[0], 500);
if (await openCase(page)) await survey('CASE');

await browser.close(); if (server) server.close();

/* ── o veredicto ──────────────────────────────────────────────────────────── */
const off = [...seen.offPalette.values()].sort((a, b) => b.n - a.n);
const low = [...seen.lowContrast.values()].sort((a, b) => a.got - b.got);
  const caps = [...seen.caps.values()];
const badFonts = Object.keys(seen.fonts).filter((f) => f && !['BrownLL', 'Aleo', 'Arial'].includes(f));
const primaryShare = Math.round(((seen.fonts.BrownLL || 0) / Math.max(1, Object.values(seen.fonts).reduce((a, b) => a + b, 0))) * 100);
const badRadii = Object.keys(seen.radii).filter((r) => r === '0px');

const rows = [
  ['BW1', 'Every painted colour is BrandWell palette', 0, off.length],
  ['BW2', 'Every text passes WCAG AA on its own ground', 0, low.length],
  ['BW3', 'No headline (>=16px) in ALL CAPS', 0, caps.length],
  ['TY1', 'No font family outside LL Brown / Aleo / Arial', 0, badFonts.length],
  ['TY2', 'LL Brown is the primary face (share >= 80%)', '>=80', primaryShare + '%'],
];
console.log('\n  SINTONIA · BRANDWELL_COLOR_AUDIT  +  TYPOGRAPHY_AUDIT');
console.log('  ' + '─'.repeat(100));
let ok = true;
for (const [id, name, exp, got] of rows) {
  const pass = id === 'TY2' ? primaryShare >= 80 : got === 0;
  ok = ok && pass;
  console.log(line(pass, id, name, exp, got));
}
console.log('  ' + '─'.repeat(100));
console.log(`  ${screens.length} ecras lidos · ${Object.entries(seen.fonts).map(([k, v]) => k + ' ×' + v).join(' · ')}`);
console.log(`  raios usados: ${Object.entries(seen.radii).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k, v]) => k + ' ×' + v).join(' · ')}`);
if (off.length) { console.log('\n  FORA DA PALETA:'); off.slice(0, 30).forEach((o) => console.log(`   ${C.r(o.hex)} ${o.prop.padEnd(18)} ×${String(o.n).padEnd(4)} ${o.where} · "${o.sample}"`)); }
if (low.length) { console.log('\n  CONTRASTE INSUFICIENTE:'); low.slice(0, 40).forEach((o) => console.log(`   ${C.r(o.fg)} sobre ${o.bg}  ${o.got}:1 (min ${o.need}) ${String(Math.round(o.size)) + 'px'} ×${o.n} ${o.where} · "${o.sample}"`)); }
if (caps.length) { console.log('\n  TITULOS EM CAIXA ALTA:'); caps.slice(0, 30).forEach((o) => console.log(`   ${C.y(Math.round(o.size) + 'px')} ${o.where} · "${o.text}"`)); }
if (badFonts.length) console.log('\n  FONTES FORA DO MANUAL: ' + badFonts.join(', '));
if (errors.length) console.log('\n  ERROS DE CONSOLA: ' + errors.length);

if (JSONOUT) fs.writeFileSync(JSONOUT, JSON.stringify({ off, low, caps, fonts: seen.fonts, radii: seen.radii, screens }, null, 1));
process.exit(ok ? 0 : 1);
