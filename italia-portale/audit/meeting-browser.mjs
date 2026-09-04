/* SINTONIA · IL PERCORSO DELLA RIUNIONE NEL BROWSER
   ===========================================================================
   I controlli statici dicono che i dati arrivano. Questo dice che si VEDONO.

   Percorre la superficie canonica in un browser vero: 1440 e 390, IT e EN,
   dalla HOME alla scheda, e apre i SEI CASI della demo uno per uno —
   contando sullo schermo i prodotti, i reparti, le prove e cio che manca.

       UNA SCHERMATA CHE NESSUNO HA APERTO NON E UNA SCHERMATA PROVATA.

   Il pulsante VEDI TUTTI viene premuto davvero, perche due dei sei casi della
   demo stanno oltre i primi dodici: e il gesto che fara chi presenta.
   =========================================================================== */
/* Percorso reale nel browser: 1440 e 390, IT e EN, i sei casi della demo. */
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const TYPES = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.json':'application/json', '.css':'text/css', '.png':'image/png', '.svg':'image/svg+xml', '.ttf':'font/ttf', '.otf':'font/otf' };
const PORT = 8931;
const srv = http.createServer((req,res)=>{
  let rel = decodeURIComponent((req.url||'/').split('?')[0]);
  if (rel === '/') rel = '/portale.html';
  if (!path.extname(rel)) rel += '.html';
  const f = path.join(CLIENT, rel);
  fs.readFile(f,(e,b)=>{ if(e){res.writeHead(404).end('404');return;} res.writeHead(200,{'content-type':TYPES[path.extname(f)]||'application/octet-stream'}).end(b); });
}).listen(PORT);

const DEMO = [
  ['A','OPP_5F31A63F844D','Botrytis x Grapevine x Emilia-Romagna'],
  ['B','OPP_F8106D5E1767','Botrytis x Grapevine x Toscana'],
  ['C','OPP_169BD86DB324','Grape moth x Umbria'],
  ['D/E','OPP_75C37DED9160','Codling moth x Veneto (stage vs action + delegated to farm)'],
  ['F','OPP_D11664591168','Scaphoideus x Toscana (administrative only)'],
];

const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });
const report = [];
let consoleErrors = 0, templateNoise = 0;
/* La stessa regola che audit/browser.mjs applica: un segnaposto di template
   dentro un attributo SVG e il template che fa il template, non un errore di
   JavaScript. Esiste identico in BASELINE/portale.html — misurato — e non
   viene da questo lavoro. Si conta a parte, non si nasconde. */
const TEMPLATE_ATTR = /attribute (d|viewBox|points|transform|cx|cy|r|x|y|width|height):/;

for (const [w,h,size] of [[1440,900,'desktop 1440'],[390,844,'mobile 390']]) {
  for (const lang of ['it','en']) {
    const ctx = await browser.newContext({ viewport:{width:w,height:h} });
    const page = await ctx.newPage();
    page.on('console', m => { if (m.type()!=='error') return;
      const t = m.text();
      if (TEMPLATE_ATTR.test(t)) { templateNoise++; return; }
      consoleErrors++; console.log('  CONSOLE ERROR:', t.slice(0,400)); });
    page.on('pageerror', e => { consoleErrors++; console.log('  PAGE ERROR:', String(e).slice(0,160)); });
    await page.goto(`http://localhost:${PORT}/portale.html`, { waitUntil:'networkidle' });
    await page.evaluate(l => localStorage.setItem('sintonia_lang', l), lang);
    await page.reload({ waitUntil:'networkidle' });
    await page.waitForTimeout(700);

    // HOME -> superficie canonica, via la voce di navigazione (un click reale)
    const navHit = await page.evaluate(() => {
      const t = [...document.querySelectorAll('*')].filter(e =>
        e.children.length===0 && /Radar Canonico|Canonical Radar/.test(e.textContent||''));
      if (!t.length) return false;
      let el = t[0]; for (let i=0;i<6 && el;i++){ if (el.onclick||el.getAttribute('onclick')) break; el = el.parentElement; }
      (el||t[0]).click(); return true;
    });
    await page.waitForTimeout(600);

    // VEDI TUTTI: la schermata ne mostra 12 e tiene gli altri dietro un
    // pulsante. Per percorrere i sei casi della demo si apre la lista intera,
    // che e esattamente cio che fara chi presenta.
    const showedAll = await page.evaluate(() => {
      const t=[...document.querySelectorAll('*')].filter(e=>e.children.length===0 && /VEDI TUTTI|VIEW ALL/i.test(e.textContent||''));
      if(!t.length) return false;
      let el=t[0]; for(let i=0;i<6&&el;i++){ if(el.onclick||el.getAttribute('onclick')) break; el=el.parentElement; }
      (el||t[0]).click(); return true;
    });
    await page.waitForTimeout(500);

    const radar = await page.evaluate(() => ({
      cards: document.querySelectorAll('[data-canonical-case]').length,
      kpis: [...document.querySelectorAll('[data-ckpi]')].map(e=>e.getAttribute('data-ckpi')+'='+(e.querySelector('span')||{}).textContent),
      hOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    }));
    radar.showedAll = showedAll;

    const cases = [];
    for (const [tag,id,desc] of DEMO) {
      const opened = await page.evaluate((cid) => {
        const el = document.querySelector(`[data-canonical-case="${cid}"]`);
        if (!el) return false; el.click(); return true;
      }, id);
      await page.waitForTimeout(450);
      const d = await page.evaluate(() => {
        const q = s => document.querySelector(s);
        const txt = s => { const e=q(s); return e? (e.textContent||'').trim() : null; };
        return {
          detail: !!q('[data-canonical-detail]'),
          detailId: q('[data-canonical-detail]') ? q('[data-canonical-detail]').getAttribute('data-canonical-detail') : null,
          status: q('[data-cstatus]') ? q('[data-cstatus]').getAttribute('data-cstatus') : null,
          pub: q('[data-cpub]') ? q('[data-cpub]').getAttribute('data-cpub') : null,
          whyComm: !!q('[data-why-commercial]'),
          whyNow: document.querySelectorAll('[data-why-now]').length,
          window: !!q('[data-window-state]') || !!q('[data-window-rule]'),
          windowRule: txt('[data-window-rule]'),
          products: document.querySelectorAll('[data-canonical-product]').length,
          depts: document.querySelectorAll('[data-action-dept]').length,
          evidence: document.querySelectorAll('[data-evidence-role]').length,
          missing: document.querySelectorAll('[data-what-missing]').length,
          divergent: !!q('[data-stage-divergent]'),
          sources: document.querySelectorAll('a[href^="http"]').length,
          hOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        };
      });
      cases.push({ tag, id, desc, opened, ...d, back: '' });
      // torna al radar canonico: prima il pulsante INDIETRO della schermata,
      // e si verifica che abbia funzionato davvero; altrimenti la voce di nav.
      const backWorked = await page.evaluate(() => {
        const cand=[...document.querySelectorAll('span,div,a,button')].filter(e=>/^\u2190/.test((e.textContent||'').trim()));
        if(!cand.length) return 'no-button';
        const b=cand[cand.length-1];
        let el=b; for(let i=0;i<6&&el;i++){ if(el.onclick||el.getAttribute('onclick')) break; el=el.parentElement; }
        (el||b).click(); return 'clicked';
      });
      await page.waitForTimeout(450);
      let backOk = await page.evaluate(() => document.querySelectorAll('[data-canonical-case]').length > 0);
      if (!backOk) {
        await page.evaluate(() => {
          const t=[...document.querySelectorAll('*')].filter(e=>e.children.length===0 && /Radar Canonico|Canonical Radar/.test(e.textContent||''));
          if(t.length){ let el=t[0]; for(let i=0;i<6&&el;i++){ if(el.onclick||el.getAttribute('onclick')) break; el=el.parentElement; } (el||t[0]).click(); }
        });
        await page.waitForTimeout(450);
      }
      cases[cases.length-1].back = backWorked + (backOk ? '/ok' : '/RECOVERED-VIA-NAV');
      await page.evaluate(() => {
        const t=[...document.querySelectorAll('*')].filter(e=>e.children.length===0 && /VEDI TUTTI|VIEW ALL/i.test(e.textContent||''));
        if(t.length){ let el=t[0]; for(let i=0;i<6&&el;i++){ if(el.onclick||el.getAttribute('onclick')) break; el=el.parentElement; } (el||t[0]).click(); }
      });
      await page.waitForTimeout(400);
    }
    report.push({ size, lang, navHit, radar, cases });
    await ctx.close();
  }
}
await browser.close(); srv.close();

let fail = 0;
for (const r of report) {
  console.log(`\n══ ${r.size} · ${r.lang.toUpperCase()} ══  nav=${r.navHit?'ok':'MISS'}  cards=${r.radar.cards} showAll=${r.radar.showedAll?'ok':'MISS'}  overflow=${r.radar.hOverflow?'YES ('+r.radar.scrollW+'>'+r.radar.clientW+')':'no'}`);
  console.log('   kpis:', r.radar.kpis.join(' '));
  if (!r.navHit || r.radar.cards === 0 || r.radar.hOverflow) fail++;
  for (const c of r.cases) {
    const ok = c.opened && c.detail && c.detailId === c.id && c.whyComm && c.whyNow>0 && c.window && c.depts>0 && !c.hOverflow;
    if (!ok) fail++;
    console.log(`   ${ok?'OK ':'XX '} ${c.tag.padEnd(3)} ${c.id} status=${c.status} pub=${c.pub} why=${c.whyComm?1:0} whyNow=${c.whyNow} win=${c.window?1:0} prod=${c.products} dept=${c.depts} ev=${c.evidence} miss=${c.missing} div=${c.divergent?'Y':'n'} src=${c.sources} ovf=${c.hOverflow?'YES':'no'} back=${c.back}`);
    if (c.windowRule) console.log(`         rule: ${c.windowRule}`);
  }
}
console.log(`\nerrori reali di console/pagina: ${consoleErrors}`);
console.log(`segnaposto SVG del template (presenti anche in BASELINE, non fatali): ${templateNoise}`);
console.log(fail === 0 && consoleErrors === 0 ? '\nBROWSER WALK = PASS' : `\nBROWSER WALK = FAIL (${fail} problems)`);
process.exit(fail===0 && consoleErrors===0 ? 0 : 1);
