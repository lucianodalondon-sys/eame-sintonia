#!/usr/bin/env node
/* SINTONIA · MEETING PUBLIC — o smoke test no URL REALMENTE SERVIDO
   ---------------------------------------------------------------------------
   node audit/meeting-public.mjs --base https://…

   Um deploy que devolve «success» nao e um portal que abre. Este portao nao
   serve pasta nenhuma: ele abre o dominio publico com um Chromium de verdade,
   percorre o fluxo da reuniao em IT e EN, a 1440 e a 390, e conta no DOM
   publico o que o motor diz.

       «DEPLOYMENT SUCCEEDED» NAO E UMA TESTEMUNHA. O DOM E.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';
import { CLIENT } from './lib/drive.mjs';

const argv = process.argv.slice(2);
const BASE = (() => { const i = argv.indexOf('--base'); return i >= 0 ? argv[i + 1].replace(/\/$/, '') : null; })();
if (!BASE) { console.error('--base <url> obrigatorio'); process.exit(2); }

const SNAP = JSON.parse(fs.readFileSync(path.join(CLIENT, 'meeting-intelligence-snapshot.json'), 'utf8'));
const byId = (id) => SNAP.CASES.find((c) => c.ID === id) || {};
const CASES = [
  { id: 'OPP_5F31A63F844D', what: 'botrite × vite × Emilia-Romagna' },
  { id: 'OPP_169BD86DB324', what: 'tignoletta × vite × Umbria — la fonte raffredda' },
  { id: 'OPP_75C37DED9160', what: 'carpocapsa × melo × Veneto — RULE_DELEGATED_TO_FARM' },
  { id: 'OPP_D11664591168', what: 'scafoideo × vite × Toscana — obbligo amministrativo' },
];
const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome', '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const NAV = { it: 'Radar Canonico', en: 'Canonical Radar' };
const INTERNAL = /\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g;

const bad = [];
const fail = (k, m) => bad.push(`${k} · ${m}`);
let consoleErrors = [], failedReqs = [], journeys = [];
const measured = {};

const CLICK = `(n)=>{for(let i=0;i<5&&n;i++){const c=getComputedStyle(n);if(c.cursor==='pointer'||n.onclick||n.tagName==='BUTTON'||n.tagName==='A')return n;n=n.parentElement;}return null;}`;
const clickTitle = async (page, t) => page.evaluate(([t, up]) => {
  const e = document.querySelector(`[title="${t}"]`); if (!e) return false;
  (eval(up)(e) || e).click(); return true;
}, [t, CLICK]).then(async (r) => { await page.waitForTimeout(800); return r; });
const clickSel = async (page, s) => page.evaluate(([s, up]) => {
  const e = document.querySelector(s); if (!e) return false;
  (eval(up)(e) || e).click(); return true;
}, [s, CLICK]).then(async (r) => { await page.waitForTimeout(500); return r; });
const setLang = async (page, code) => {
  await page.evaluate((w) => {
    const e = [...document.querySelectorAll('span')].find((x) => (x.textContent || '').trim() === w && !x.children.length);
    if (!e) return; let n = e;
    for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer' || n.onclick) { n.click(); return; } n = n.parentElement; }
    e.click();
  }, code.toUpperCase());
  await page.waitForTimeout(900);
  return (await page.evaluate(() => document.documentElement.lang)) === code;
};

for (const width of [1440, 390]) {
  /* O Chromium nao herda HTTPS_PROXY do ambiente como o curl herda: sem esta
     linha o dominio publico devolve ERR_CONNECTION_RESET e pareceria um deploy
     morto. A CA do proxy ja esta na loja NSS do browser. */
  /* O proxy so aceita CONNECT: mandar-lhe um localhost em HTTP simples devolve
     405, e o portal parecia partido quando o partido era o teste. Por isso o
     proxy so entra quando o alvo e mesmo externo. */
  const isLocal = /^https?:\/\/(localhost|127\.0\.0\.1)/.test(BASE);
  const PROXY = isLocal ? null : (process.env.HTTPS_PROXY || process.env.https_proxy || null);
  const browser = await chromium.launch({
    executablePath: EXEC,
    args: ['--no-sandbox', '--disable-background-networking', '--no-first-run'],
    ...(PROXY ? { proxy: { server: PROXY, bypass: 'localhost,127.0.0.1' } } : {}),
  });
  const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => consoleErrors.push(`${width} pageerror: ${e.message}`));
  page.on('console', (m) => { if (m.type() === 'error' && !/attribute (d|cx|cy|x|y|r|points|width|height|transform|viewBox):.*\{\{/.test(m.text())) consoleErrors.push(`${width} console: ${m.text().slice(0, 160)}`); });
  page.on('requestfailed', (r) => failedReqs.push(`${width} ${r.url().slice(0, 120)}`));
  page.on('response', (r) => { if (r.status() >= 400) failedReqs.push(`${width} ${r.status()} ${r.url().slice(0, 120)}`); });

  await page.goto(`${BASE}/portale`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(900);

  for (const lang of ['it', 'en']) {
    if (lang === 'en' && !(await setLang(page, 'en'))) { fail('LANG', `${width}px · EN switch failed`); continue; }
    if (!(await clickTitle(page, NAV[lang]))) { fail('NAV', `${width}px ${lang} · canonical radar unreachable`); continue; }
    await clickSel(page, '[data-meeting-filter="MEETING_FILTER_ALL"]');
    for (let i = 0; i < 3; i++) { if (!(await clickSel(page, '[data-meeting-more]'))) break; }

    const radar = await page.evaluate(() => ({
      cards: [...document.querySelectorAll('[data-meeting-case]')].map((e) => e.getAttribute('data-meeting-case')),
      text: (document.body.innerText || '').replace(/ /g, ' '),
    }));
    journeys.push(`${width} ${lang} radar(${radar.cards.length})`);
    if (lang === 'it' && width === 1440) {
      measured.PUBLIC_CANONICAL_CASES = radar.cards.length;
      /* D.CASES nao podem entrar: os ids da demo sao IT-OPP-* */
      measured.PUBLIC_DEMO_IDS_ON_CANONICAL = radar.cards.filter((c) => /^IT-OPP-/.test(c)).length;
    }
    if (radar.cards.length !== 43) fail('COUNT', `${width}px ${lang} · ${radar.cards.length} canonical cards, expected 43`);

    for (const { id, what } of CASES) {
      await clickTitle(page, NAV[lang]);
      await clickSel(page, '[data-meeting-filter="MEETING_FILTER_ALL"]');
      for (let i = 0; i < 3; i++) {
        if (await page.evaluate((w) => !!document.querySelector(`[data-meeting-case="${w}"]`), id)) break;
        if (!(await clickSel(page, '[data-meeting-more]'))) break;
      }
      const opened = await page.evaluate(([w, up]) => {
        const c = document.querySelector(`[data-meeting-case="${w}"]`); if (!c) return false;
        (eval(up)(c) || c).click(); return true;
      }, [id, CLICK]);
      await page.waitForTimeout(700);
      if (!opened) { fail('OPEN', `${width}px ${lang} · ${id} (${what}) will not open`); continue; }
      journeys.push(`${width} ${lang} ${id}`);

      const d = await page.evaluate(() => {
        const one = (s, a) => { const e = document.querySelector(s); return e ? (a ? e.getAttribute(a) : e.textContent.trim()) : null; };
        const all = (s, a) => [...document.querySelectorAll(s)].map((e) => (a ? e.getAttribute(a) : e.textContent.trim()));
        return {
          heroPrimary: one('[data-hero-primary]', 'data-hero-primary'),
          hasPrimary: one('[data-meeting-products]', 'data-has-primary'),
          products: all('[data-product]', 'data-product'),
          windowOwner: one('[data-meeting-window]', 'data-window-owner'),
          windowDefined: one('[data-meeting-window]', 'data-window-defined'),
          windowOpen: one('[data-meeting-window]', 'data-window-open'),
          windowRule: one('[data-window-rule]'), windowState: one('[data-window-state]'),
          pestStage: one('[data-pest-stage]', 'data-pest-stage'),
          actionRec: one('[data-action-rec]', 'data-action-rec'),
          whyCommercial: !!document.querySelector('[data-meeting-why-commercial]'),
          whyNow: !!document.querySelector('[data-meeting-why-now]'),
          actionMap: !!document.querySelector('[data-meeting-action-map]'),
          depts: all('[data-action-dept]', 'data-action-dept'),
          evidence: all('[data-evidence-role]', 'data-evidence-role').length,
          cooling: all('[data-cooling]', 'data-cooling'),
          sources: all('[data-source-id]', 'data-source-id').length,
          text: (document.body.innerText || '').replace(/ /g, ' '),
        };
      });
      const raw = byId(id);

      /* PRIMARY — um so dono, no DOM publico */
      const pid = raw.PRIMARY_MATCH || null;
      const pname = pid ? ((raw.PORTFOLIO_MATCHES || []).find((m) => m.PRODUCT_ID === pid) || {}).PRODUCT_NAME || null : null;
      if ((d.heroPrimary || null) !== (pname || null)) fail('PRIMARY', `${width}px ${lang} ${id} · hero "${d.heroPrimary}" vs engine "${pname}"`);
      if (!pid && d.hasPrimary === 'true') fail('PRIMARY', `${width}px ${lang} ${id} · invented a primary`);
      for (const p of (raw.PORTFOLIO_MATCHES || []).map((m) => m.PRODUCT_NAME)) if (!d.products.includes(p)) fail('PRODUCTS', `${width}px ${lang} ${id} · ${p} missing`);
      if (/\+\s*\d+\s+(more|altri|altre)\b/i.test(d.text)) fail('PRODUCTS', `${width}px ${lang} ${id} · "+N more" summary`);

      /* WINDOW — um so dono */
      if (d.windowOwner !== 'MEETING_INTELLIGENCE') fail('WINDOW', `${width}px ${lang} ${id} · owner ${d.windowOwner}`);
      if (d.windowDefined !== (raw.WINDOW_DEFINED || null)) fail('WINDOW', `${width}px ${lang} ${id} · DEFINED ${d.windowDefined}`);
      if (d.windowOpen !== 'WINDOW_OPEN_NOW_' + (raw.WINDOW_OPEN_NOW || 'UNKNOWN')) fail('WINDOW', `${width}px ${lang} ${id} · OPEN_NOW ${d.windowOpen}`);
      if (d.windowRule && d.windowRule === d.windowState) fail('WINDOW', `${width}px ${lang} ${id} · one sentence for both questions`);
      if (/nessuna finestra canonica collegata|no canonical window linked/i.test(d.text)) fail('WINDOW', `${width}px ${lang} ${id} · legacy calendar sentence`);

      /* stadio e raccomandazione: due padroni */
      if (raw.PEST_STAGE_STATE && raw.PEST_STAGE_STATE !== 'STAGE_NOT_DECLARED' && d.pestStage !== raw.PEST_STAGE_STATE) fail('STAGE', `${width}px ${lang} ${id} · stage ${d.pestStage}`);

      if (!d.whyCommercial) fail('SECTION', `${width}px ${lang} ${id} · WHY COMMERCIAL missing`);
      if (!d.whyNow) fail('SECTION', `${width}px ${lang} ${id} · WHY NOW missing`);
      if (!d.actionMap) fail('SECTION', `${width}px ${lang} ${id} · ACTION MAP missing`);
      for (const dep of Object.keys(raw.ACTION_BY_DEPARTMENT || {})) if (!d.depts.includes(dep)) fail('ACTION', `${width}px ${lang} ${id} · ${dep} missing`);
      if (d.evidence !== (raw.EVIDENCE_ROLES || []).length) fail('EVIDENCE', `${width}px ${lang} ${id} · ${d.evidence} of ${(raw.EVIDENCE_ROLES || []).length}`);
      if (!d.sources) fail('SOURCE', `${width}px ${lang} ${id} · no source named`);

      /* nenhum token interno pintado */
      const toks = [...new Set(d.text.match(INTERNAL) || [])]
        .filter((t) => !/^(IT|OPP|CATPRD|AI|GEO|REGION|FRAC|HRAC|IRAC|V21|NUTS)[-_]/.test(t))
        .filter((t) => !/^[A-Z]{2,4}_\d+$/.test(t));
      for (const t of toks) fail('TOKEN', `${width}px ${lang} ${id} · ${t}`);

      /* Umbria: a testemunha que esfria, e a soglia que nao e da Emilia */
      if (id === 'OPP_169BD86DB324') {
        if (/\b5\s*%/.test(d.text)) fail('UMBRIA', `${width}px ${lang} · the Emilia-Romagna 5% appears on Umbria`);
        if (!d.cooling.length) fail('UMBRIA', `${width}px ${lang} · the cooling reading is not shown`);
        if (lang === 'it' && !/non sono necessari interventi/i.test(d.text)) fail('UMBRIA', `${width}px it · the source sentence is not on screen`);
      }
      if (id === 'OPP_75C37DED9160' && lang === 'it' && !/osservazione in campo/i.test(d.text)) fail('FARM', `${width}px it · RULE_DELEGATED_TO_FARM not readable`);
    }
  }
  await browser.close();
}

/* ── contagens publicas ── */
const eng = {
  ACT_NOW: SNAP.CASES.filter((c) => c.STATUS === 'ACT_NOW').length,
  WINDOW_DEFINED: SNAP.CASES.filter((c) => c.WINDOW_DEFINED === 'YES').length,
  PUBLISHABLE: SNAP.CASES.filter((c) => c.PUBLICATION_STATE === 'PUBLISHABLE').length,
  VALIDATION_REQUIRED: SNAP.CASES.filter((c) => c.PUBLICATION_STATE === 'VALIDATION_REQUIRED').length,
  PRIMARY_NULL: SNAP.CASES.filter((c) => !c.PRIMARY_MATCH).length,
};

const G = '\x1b[32m', R = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
const groups = {};
for (const b of bad) { const k = b.split(' · ')[0]; (groups[k] = groups[k] || []).push(b); }
console.log(`\n  SINTONIA · MEETING PUBLIC · ${BASE}`);
console.log('  ' + '─'.repeat(100));
const rows = [
  ['PUBLIC_CANONICAL_CASES', measured.PUBLIC_CANONICAL_CASES === 43 ? 0 : 1, `${measured.PUBLIC_CANONICAL_CASES} (expected 43)`],
  ['PUBLIC_D_CASES_AS_CANONICAL', measured.PUBLIC_DEMO_IDS_ON_CANONICAL || 0, String(measured.PUBLIC_DEMO_IDS_ON_CANONICAL || 0)],
  ['PUBLIC_PRIMARY_INVENTED', (groups.PRIMARY || []).length, String((groups.PRIMARY || []).length)],
  ['PUBLIC_ALL_PRODUCTS', (groups.PRODUCTS || []).length, String((groups.PRODUCTS || []).length)],
  ['PUBLIC_WINDOW_ONE_OWNER', (groups.WINDOW || []).length, String((groups.WINDOW || []).length)],
  ['PUBLIC_STAGE_VS_RECOMMENDATION', (groups.STAGE || []).length, String((groups.STAGE || []).length)],
  ['PUBLIC_SECTIONS', (groups.SECTION || []).length + (groups.ACTION || []).length + (groups.EVIDENCE || []).length + (groups.SOURCE || []).length, ''],
  ['PUBLIC_UMBRIA_WITNESS', (groups.UMBRIA || []).length, ''],
  ['PUBLIC_RULE_DELEGATED_TO_FARM', (groups.FARM || []).length, ''],
  ['PUBLIC_INTERNAL_TOKENS', (groups.TOKEN || []).length, String((groups.TOKEN || []).length)],
  ['PUBLIC_REACHABLE_IT_EN_1440_390', (groups.NAV || []).length + (groups.LANG || []).length + (groups.OPEN || []).length + (groups.COUNT || []).length, ''],
  ['PUBLIC_CONSOLE_ERRORS', consoleErrors.length, String(consoleErrors.length)],
  ['PUBLIC_FAILED_REQUESTS', failedReqs.length, String(failedReqs.length)],
];
for (const [id, n, extra] of rows) console.log(`  ${n === 0 ? G + 'PASS' + X : R + 'FAIL' + X}  ${id.padEnd(34)} ${D}got${X} ${n}${extra ? D + '  · ' + extra + X : ''}`);
for (const v of Object.values(groups)) for (const m of v.slice(0, 5)) console.log(`        ${D}${m.slice(0, 140)}${X}`);
for (const e of consoleErrors.slice(0, 5)) console.log(`        ${D}${e.slice(0, 140)}${X}`);
for (const e of failedReqs.slice(0, 5)) console.log(`        ${D}${e.slice(0, 140)}${X}`);
console.log('  ' + '─'.repeat(100));
console.log(`  ENGINE: ACT_NOW ${eng.ACT_NOW} · WINDOW_DEFINED ${eng.WINDOW_DEFINED} · PUBLISHABLE ${eng.PUBLISHABLE} · VALIDATION_REQUIRED ${eng.VALIDATION_REQUIRED} · PRIMARY_MATCH null ${eng.PRIMARY_NULL}`);
console.log(`  percorsi: ${journeys.length} · ${D}${journeys.slice(0, 3).join(' | ')}${X}`);
const total = rows.reduce((a, [, n]) => a + n, 0);
console.log(`  ${total === 0 ? G + 'PUBLIC BUILD VERIFIED' + X : R + total + ' rilievi' + X}\n`);
process.exit(total === 0 ? 0 : 1);
