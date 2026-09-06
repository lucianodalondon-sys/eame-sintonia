/* SINTONIA ITALIA · RELEASE GATE — quindici domande, una risposta ciascuna
   ---------------------------------------------------------------------------
   Corto e deterministico. Non apre un'auditoria: chiede se la demo di domani
   puo essere mostrata. Ogni riga porta il numero che l'ha decisa.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import { serve, open, screenText, C } from '../lib/drive.mjs';
import { mount } from '../lib/harness.mjs';

const R = {}; const dettagli = [];
const nota = (t) => dettagli.push(t);

/* ── parte A · quello che si misura senza browser ──────────────────────────── */
const M = mount({});
const AM = M.AM, ctx = M.ctx;
const CANON = AM.AREE_CANONICHE || [];
const B = ctx.MEETING_SURFACE.build('it');
const visti = new Set(); const casi = [];
for (const k of Object.keys(B)) if (Array.isArray(B[k])) for (const c of B[k]) if (c && c.id && !visti.has(c.id)) { visti.add(c.id); casi.push(c); }
const grezzi = (ctx.MEETING_INTELLIGENCE.cases || ctx.MEETING_INTELLIGENCE.CASES || []);
const grezzo = (id) => grezzi.find((x) => (x.ID || x.id) === id) || {};

/* 3 · cinque aree su tutte le opportunita, due lingue */
let complete = 0, righe = 0;
let semSinalFalsi = 0, prepararaDuplicato = 0, vendita = 0;
for (const lang of ['it', 'en']) for (const c of casi) {
  const v = M.vals({ view: 'mcase', mCaseId: c.id, lang });
  const a = v.mcActions || [];
  const cod = a.map((x) => x.DEPARTMENT);
  if (CANON.every((k) => cod.indexOf(k) >= 0) && cod.length === CANON.length) complete++;
  const r = grezzo(c.id);
  for (const x of a) {
    righe++;
    if (/Nessun segnale di campo corrente|No current field signal/.test(String(x.why)) && r.SIGNAL_CURRENCY === 'CURRENT') semSinalFalsi++;
    const by = (r.ACTION_BY_DEPARTMENT || {})[x.DEPARTMENT] || {};
    if (by.ACTION && by.ACTION_STATE && by.ACTION === by.ACTION_STATE && x.actionDistinct !== false) prepararaDuplicato++;
  }
}
R.MAPA_5_AREAS = CANON.length + ' aree · ' + (complete / 2) + '/' + casi.length + ' opportunita, due lingue · ' + righe + ' righe';
R.SEM_SINAL_ATUAL_FALSE = semSinalFalsi;
R.PREPARARE_DUPLICADO = prepararaDuplicato;

/* 5 · la legge della rilevanza */
const V = ctx.ADAMA_RELEVANCE.VERDETTI || {};
let contraddizioni = 0;
for (const o of AM.collections.opportunities.records) {
  const cls = AM.adamaRelevance(o) || [];
  const v = V[o.id];
  if (cls.indexOf('PRODUCT_OPPORTUNITY') >= 0 && v && v.PROVA === null) contraddizioni++;
}
R.ADAMA_RELEVANCE_CONTRADICTIONS = contraddizioni;

/* 4 · mappa vecchia: struttura, non parole — schermo E sorgente dei documenti */
const SRC = fs.readFileSync(new URL('../../client/portale.html', import.meta.url), 'utf8');
const SENZA = SRC.slice(SRC.indexOf('<script type="text/x-dc"')).replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
const residui = [];
for (const t of ['data-area=', 'data-area-name=', 'cs.actionMapRows', 'cs.hasActionMap']) if (SRC.indexOf(t) >= 0) residui.push('markup:' + t);
if (/actionAreas[\s\S]{0,200}?actionMap/.test(SENZA)) residui.push('PDF: actionAreas da actionMap');
if (/V21\s*&&\s*T\.V21\[a\]/.test(SENZA)) residui.push('etichette V21 di area');
const fuori = new Set();
const cerca = (v, d = 0) => {
  if (d > 7 || v == null || typeof v !== 'object') return;
  if (Array.isArray(v)) { for (const x of v) cerca(x, d + 1); return; }
  const cod = v.DEPARTMENT || v.area || v.dept;
  if (cod && typeof cod === 'string' && /^[A-Z][A-Z_]{3,}$/.test(cod) && CANON.indexOf(cod) < 0) fuori.add(cod);
  for (const k in v) { if (k === 'raw') continue; try { cerca(v[k], d + 1); } catch (e) {} }
};
const VISTE = ['meeting', 'future', 'windows', 'market', 'voices', 'competitors', 'science', 'portfolio', 'archive', 'sources'];
for (const lang of ['it', 'en']) {
  for (const view of VISTE) { const r = M.tryVals({ view, lang }); if (r.ok) cerca(r.vals); }
  for (const c of casi) { const r = M.tryVals({ view: 'mcase', mCaseId: c.id, lang }); if (r.ok) cerca(r.vals); }
  for (const o of AM.collections.opportunities.records) { const r = M.tryVals({ view: 'case', caseId: o.id, lang }); if (r.ok) cerca(r.vals); }
  for (const w of AM.collections.cropWindows.records) { const r = M.tryVals({ view: 'window', windowId: w.id, lang }); if (r.ok) cerca(r.vals); }
}
for (const f of fuori) residui.push('codice di reparto reso: ' + f);
R.MAPA_ANTIGO_VISIBLE = residui.length ? 'SIM · ' + residui.join(' · ') : 'NAO';

/* 13 · il documento: si costruisce, e con la mappa canonica */
/* La sorgente delle aree del documento: deve venire dalla mappa della riunione,
   mai da `actionMap`. Si legge la costruzione del payload, non una parola. */
const bloccoAree = SENZA.slice(SENZA.indexOf('actionAreas'), SENZA.indexOf('actionAreas') + 700);
const areeDaRiunione = /mc\.actions/.test(bloccoAree) && !/actionMap/.test(bloccoAree);
R.PDF_SORGENTE = areeDaRiunione ? 'mappa canonica (mc.actions)' : 'DA VERIFICARE';
/* Il documento si misura dove il portale lo apre davvero: la vista `brief`. */
const primo = AM.collections.opportunities.records[0];
const vb = M.vals({ view: 'brief', caseId: primo.id, briefDept: 'MARKETING' });
R.PDF_DOC = vb.isBrief
  ? 'apre · ' + String((vb.br || {}).doc || '').slice(0, 40) + ' · ' + (((vb.br || {}).sections) || []).length + ' sezioni'
  : 'NON APRE';
/* Da DOVE si raggiunge: i pulsanti stanno sulla scheda legacy, non sulla
   scheda della riunione che la demo mostra. Si dichiara, non si nasconde. */
const conBottoni = (M.vals({ view: 'case', caseId: primo.id }).cs.briefRows || []).length;
const suRiunione = SRC.slice(SRC.indexOf('{{ isMcase }}'), SRC.indexOf('{{ isCase }}')).indexOf('data-brief-dept') >= 0;
R.PDF_RAGGIUNGIBILE = 'scheda legacy: ' + conBottoni + ' pulsanti · scheda della riunione: ' + (suRiunione ? 'si' : 'NO');

/* ── parte B · quello che serve il vetro ───────────────────────────────────── */
const CLICK = "(n)=>{for(let i=0;i<5&&n;i++){const cs=getComputedStyle(n); if(cs.cursor==='pointer') return n; n=n.parentElement;} return null;}";
const server = await serve(8811);
let erroriTot = 0, richiesteRotte = 0;
const apriPortale = async (width, lang) => {
  const s = await open({ port: 8811, width, height: width < 500 ? 844 : 1000 });
  await s.page.evaluate(([l]) => { try { localStorage.setItem('sintonia_lang', l); } catch (e) {} }, [lang]);
  await s.page.reload({ waitUntil: 'domcontentloaded' });
  await s.page.waitForTimeout(900);
  return s;
};

/* 1 · console · 2 · frammento · 9 · italiano · 12 · desktop */
{
  const s = await apriPortale(1440, 'it');
  const FRAG = ['portfolio', 'sources', 'windows', 'market', 'future', 'meeting'];
  const titoli = [];
  for (const f of FRAG) {
    await s.page.evaluate(([x]) => { window.location.hash = x; }, [f]);
    await s.page.waitForTimeout(420);
    titoli.push(await s.page.evaluate(() => ((document.querySelector('h1') || {}).innerText || '').slice(0, 26)));
  }
  const distinti = new Set(titoli).size;
  R.HASH = distinti + '/' + FRAG.length + ' frammenti danno una schermata diversa';
  nota('frammenti: ' + titoli.join(' | '));

  /* italiano: token del motore o inglese a schermo */
  const TOKEN = /\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b/;
  const brutti = [];
  for (const f of FRAG) {
    await s.page.evaluate(([x]) => { window.location.hash = x; }, [f]);
    await s.page.waitForTimeout(400);
    const t = await screenText(s.page);
    for (const riga of t.split('\n').map((x) => x.trim()).filter(Boolean)) {
      if (TOKEN.test(riga)) brutti.push(f + ' :: ' + riga.slice(0, 70));
    }
  }
  R.ITALIAN_UI_ERRORS = brutti.length;
  brutti.slice(0, 4).forEach((b) => nota('token: ' + b));
  const t1440 = await screenText(s.page);
  R.DESKTOP = t1440.length > 800 ? 'OK · ' + t1440.length + ' caratteri' : 'VUOTO';
  erroriTot += s.errors.length; richiesteRotte += s.failed.length;
  await s.browser.close();
}

/* 6 · vocabolario commerciale, due lingue */
{
  for (const lang of ['it', 'en']) {
    const s = await apriPortale(1440, lang);
    const t = await screenText(s.page);
    vendita += (t.split('PRONTO PER LA VENDITA').length - 1) + (t.split('SALES READY').length - 1);
    erroriTot += s.errors.length; richiesteRotte += s.failed.length;
    await s.browser.close();
  }
  R.PRONTO_PER_LA_VENDITA = vendita;
}

/* 14 · i cinque casi commerciali · 15 · tre casi che NON affermano · 10 · comandi */
{
  const s = await apriPortale(1440, 'it');
  const forti = (B.commercial || []).slice(0, 5).map((c) => c.id);
  const negativi = [].concat((B.signals || []).slice(0, 2).map((c) => c.id), (B.radar || []).slice(0, 1).map((c) => c.id));
  /* I casi che NON affermano non stanno sul radar: vivono dietro le due porte
     dichiarate nel markup. Cercarli sulla prima griglia e concludere che non si
     aprono sarebbe misurare il proprio percorso. */
  const entra = async (sel) => {
    const ok = await s.page.evaluate(([q, up]) => {
      const n = document.querySelector(q); if (!n) return false; (eval(up)(n) || n).click(); return true;
    }, [sel, CLICK]);
    if (ok) await s.page.waitForTimeout(520);
    return ok;
  };
  const leggi = async (id) => {
    const ok = await s.page.evaluate(([caso, up]) => {
      const n = document.querySelector('[data-meeting-case="' + caso + '"]');
      if (!n) return false; (eval(up)(n) || n).click(); return true;
    }, [id, CLICK]);
    if (!ok) { await s.page.reload({ waitUntil: 'domcontentloaded' }); await s.page.waitForTimeout(700); return null; }
    await s.page.waitForTimeout(420);
    const t = await screenText(s.page);
    const aree = await s.page.evaluate(() => [...document.querySelectorAll('[data-action-dept]')].map((n) => n.getAttribute('data-action-dept')));
    const cliccabili = await s.page.evaluate(() => [...document.querySelectorAll('*')].filter((n) => getComputedStyle(n).cursor === 'pointer').length);
    await s.page.reload({ waitUntil: 'domcontentloaded' }); await s.page.waitForTimeout(700);
    return { chars: t.length, aree: aree.length, fuori: aree.filter((a) => CANON.indexOf(a) < 0).length, cliccabili, testo: t };
  };
  const F = []; for (const id of forti) { const r = await leggi(id); if (r) F.push({ id, ...r }); }
  const N = [];
  for (const [porta, ids] of [['[data-signals-entry]', (B.signals || []).slice(0, 2).map((c) => c.id)],
                              ['[data-radar-entry]', (B.radar || []).slice(0, 1).map((c) => c.id)]]) {
    for (const id of ids) {
      await s.page.reload({ waitUntil: 'domcontentloaded' }); await s.page.waitForTimeout(700);
      if (!(await entra(porta))) continue;
      const r = await leggi(id); if (r) N.push({ id, ...r });
    }
  }
  R.TOP_CASES_TESTED = F.length + '/5 · aree ' + F.map((x) => x.aree).join(',') + ' · fuori ' + F.reduce((a, x) => a + x.fuori, 0);
  const PAROLE_NEGATIVE = /Non dichiarato|Nessun|non risulta|Not stated|No |non e dichiarat/i;
  const sanno = N.filter((x) => PAROLE_NEGATIVE.test(x.testo)).length;
  R.NEGATIVE_CASES_TESTED = N.length + ' aperti · ' + sanno + ' dichiarano cio che non sanno';
  R.COMANDI = F.concat(N).length ? 'schede con comandi: ' + F.concat(N).map((x) => x.cliccabili).join(',') : 'nessuna';
  erroriTot += s.errors.length; richiesteRotte += s.failed.length;
  await s.browser.close();
}

/* 11 · mobile 390 */
{
  const s = await apriPortale(390, 'it');
  const largo = await s.page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 2);
  const t = await screenText(s.page);
  R.MOBILE = (largo ? 'SCORRE DI LATO' : 'OK') + ' · ' + t.length + ' caratteri a 390px';
  erroriTot += s.errors.length; richiesteRotte += s.failed.length;
  await s.browser.close();
}
server.close();

R.BROWSER_ERRORS = erroriTot;
R.BROKEN_LINKS = richiesteRotte;

console.log('');
console.log('  SINTONIA ITALIA · RELEASE GATE');
console.log('  ' + '─'.repeat(92));
for (const k of ['BROWSER_ERRORS', 'BROKEN_LINKS', 'HASH', 'MAPA_5_AREAS', 'MAPA_ANTIGO_VISIBLE',
  'ADAMA_RELEVANCE_CONTRADICTIONS', 'PRONTO_PER_LA_VENDITA', 'SEM_SINAL_ATUAL_FALSE',
  'PREPARARE_DUPLICADO', 'ITALIAN_UI_ERRORS', 'MOBILE', 'DESKTOP', 'PDF_SORGENTE', 'PDF_DOC', 'PDF_RAGGIUNGIBILE', 'COMANDI',
  'TOP_CASES_TESTED', 'NEGATIVE_CASES_TESTED']) {
  console.log('  ' + k.padEnd(32) + ' = ' + R[k]);
}
console.log('  ' + '─'.repeat(92));
for (const d of dettagli.slice(0, 8)) console.log('  ' + C.d(d));
