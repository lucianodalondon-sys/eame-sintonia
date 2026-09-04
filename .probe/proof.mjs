import { serve, open, openCase, clickTitle, caseIds } from '../italia-portale/audit/lib/drive.mjs';

const DIR = process.env.DIR;
const LANG = process.env.LANG2 || 'it';
const W = Number(process.env.W || 1440), H = Number(process.env.H || 1000);
const PORT = Number(process.env.PORT || 8992);
const LIMIT = Number(process.env.LIMIT || 0);

const srv = serve(PORT, DIR);
const { browser, page, errors, failed } = await open({ port: PORT, width: W, height: H });

if (LANG === 'en') {
  await page.evaluate(() => {
    const h = [...document.querySelectorAll('span,div,button,a')]
      .find((e) => (e.textContent || '').trim() === 'EN' && e.children.length === 0);
    let t = h; for (let i = 0; i < 4 && t; i++) { t.click(); t = t.parentElement; }
  });
  await page.waitForTimeout(700);
}
const L = LANG === 'en' ? 'en' : 'it';

/* The nav title is read from the DOM instead of typed here: an accented string
   that travels through a shell is a string that can arrive mangled, and a
   selector that never matches looks exactly like a screen that never renders. */
const navTitles = await page.evaluate(() =>
  [...new Set([...document.querySelectorAll('[title]')].map((e) => e.getAttribute('title')).filter(Boolean))]);
const RADAR = navTitles.find((n) => /radar/i.test(n) && !/futur/i.test(n))
  || navTitles.find((n) => /opportunit/i.test(n));

const showAll = async () => {
  const n = await page.evaluate(() => {
    const h = [...document.querySelectorAll('span')]
      .find((e) => /VEDI TUTTE|VIEW ALL/i.test(e.textContent || '') && e.children.length === 0);
    if (!h) return 0; h.click(); return 1;
  });
  if (n) await page.waitForTimeout(700);
};

const defaultCards = await page.evaluate(() => document.querySelectorAll('[data-case]').length);
await clickTitle(page, RADAR); await showAll();
const drawn = await caseIds(page);

const SNAP = await page.evaluate(() => window.MEETING_INTELLIGENCE);
const say = await page.evaluate((l) => {
  const d = window.MEETING_LABELS; const o = {};
  for (const fam of ['WINDOW_TYPE', 'WINDOW_OPEN_NOW', 'WINDOW_DEFINED', 'UI']) {
    o[fam] = {}; for (const k of Object.keys(d.families[fam])) o[fam][k] = d.t(fam, k, l);
  }
  return o;
}, L);

/* The sentences the old surface printed. Any of them on a case whose engine
   declares a window is the contradiction this hotfix exists to keep closed. */
const NOWIN = ['Nessuna finestra dichiarata', 'No window is declared',
  'nessuna finestra canonica collegata', 'no canonical window linked'];

let primaryBad = 0, windowBad = 0, invented = 0, opened = 0;
const notOpened = [], firstFailures = [], witnesses = {};
const cases = LIMIT ? SNAP.CASES.slice(0, LIMIT) : SNAP.CASES;

for (const c of cases) {
  await clickTitle(page, RADAR); await showAll();
  const ok = await openCase(page, c.ID, 380);
  if (!ok) { notOpened.push(c.ID); continue; }
  opened++;
  const d = await page.evaluate(() => ({
    prods: [...new Set([...document.querySelectorAll('[data-product]')]
      .map((e) => e.getAttribute('data-product')).filter(Boolean))],
    txt: (document.body.innerText || '').replace(/ /g, ' '),
  }));

  const engine = [...new Set((c.PORTFOLIO_MATCHES || []).map((m) => m.PRODUCT_NAME))];
  const extra = d.prods.filter((n) => !engine.includes(n));
  const lost = engine.filter((n) => !d.prods.includes(n));
  const crowns = d.txt.includes(say.UI.PRIMARY);
  let pbad = null;
  if (extra.length) pbad = `presents ${JSON.stringify(extra)} not in PORTFOLIO_MATCHES`;
  else if (lost.length) pbad = `omits ${JSON.stringify(lost)} from PORTFOLIO_MATCHES`;
  else if (!c.PRIMARY_MATCH && crowns) pbad = 'crowns a primary the engine refused to elect';
  if (pbad) { primaryBad++; if (firstFailures.length < 6) firstFailures.push(`${c.ID} PRIMARY: ${pbad}`); }
  if (!c.PRIMARY_MATCH && crowns) invented++;

  const wt = say.WINDOW_TYPE[c.WINDOW_TYPE] || '';
  const wo = say.WINDOW_OPEN_NOW[c.WINDOW_OPEN_NOW] || '';
  let wbad = null;
  if (c.WINDOW_DEFINED === 'YES') {
    const hit = NOWIN.find((s) => d.txt.includes(s));
    if (hit) wbad = `says "${hit}" while WINDOW_DEFINED=YES`;
    else if (wt && !d.txt.includes(wt)) wbad = `window type "${wt}" absent`;
  } else if (!d.txt.includes(say.WINDOW_DEFINED.NO)) {
    wbad = 'does not state that no rule is declared';
  }
  if (!wbad && wo && !d.txt.includes(wo)) wbad = `current state "${wo}" absent`;
  if (wbad) { windowBad++; if (firstFailures.length < 6) firstFailures.push(`${c.ID} WINDOW: ${wbad}`); }

  if (c.ID === 'OPP_5F31A63F844D' || c.ID === 'OPP_75C37DED9160') {
    witnesses[c.ID] = {
      enginePrimary: (c.PORTFOLIO_MATCHES || [])
        .filter((m) => m.PRODUCT_ID === c.PRIMARY_MATCH).map((m) => m.PRODUCT_NAME)[0] || null,
      detailProducts: d.prods, crownsSomeone: crowns,
      windowDefined: c.WINDOW_DEFINED, windowOpenNow: c.WINDOW_OPEN_NOW,
    };
  }
}

/* The card, read on the radar itself: the name the screen shows before a click. */
await clickTitle(page, RADAR); await showAll();
const cardPrimary = await page.evaluate(() => {
  const out = {};
  for (const id of ['OPP_5F31A63F844D', 'OPP_75C37DED9160']) {
    const card = [...document.querySelectorAll('[data-case]')].find((c) => c.getAttribute('data-case') === id);
    out[id] = card ? [...card.querySelectorAll('[data-product]')]
      .map((e) => e.getAttribute('data-product')).filter(Boolean) : null;
  }
  return out;
});

console.log(JSON.stringify({
  lang: L, viewport: `${W}x${H}`, radarTitle: RADAR,
  NAV_RADAR_ENTRIES: navTitles.filter((n) => /radar|opportunit/i.test(n)),
  DEFAULT_SCREEN_CARDS: defaultCards,
  CANONICAL_CASES: drawn.length, SNAPSHOT_TOTAL: SNAP.TOTAL_CASES,
  OPENED: opened, NOT_OPENED: notOpened,
  PRIMARY_CONTRADICTION: primaryBad, WINDOW_CONTRADICTION: windowBad,
  PRIMARY_NULL: SNAP.CASES.filter((c) => !c.PRIMARY_MATCH).length,
  INVENTED_PRIMARY: invented,
  CARD_PRIMARY: cardPrimary, witnesses, firstFailures,
  CONSOLE_ERRORS: errors.length, FAILED_REQUESTS: (failed || []).length,
}, null, 1));

await browser.close(); if (srv && srv.close) srv.close(); process.exit(0);
