/* SINTONIA · CTA_DEAD_BUTTON_GATE + NAVIGATION_GATE
   ---------------------------------------------------------------------------
   node italia-portale/audit/cta-navigation.mjs [--json out.json] [--screens N] [--max N]

   Un bottone che il cursore promette e che non fa niente e peggio di un bottone
   assente: chi legge crede di aver premuto, aspetta, e conclude che il portale
   e rotto. Questo controllo non cerca stringhe nel sorgente — apre un Chromium,
   percorre ogni schermata della barra laterale, PREME ogni affordance e chiede
   al DOM se e successo qualcosa.

       IL CURSORE E UNA PROMESSA. UNA PROMESSA CHE NON SI MUOVE E UN DIFETTO.

   Prova di vita accettata, in ordine di forza: l'impronta della schermata
   cambia · un pannello/drawer compare · il DOM muta (una sola mutazione basta —
   il rumore a riposo, misurato a ogni esecuzione, e zero) · si apre una scheda
   nuova o un download · si apre un dialog nativo.

   Tre cose NON sono difetti, e il portone le riconosce da solo:
     · la voce di menu della schermata in cui gia ti trovi (premere «Concorrenza»
       stando su Concorrenza deve essere un no-op);
     · i controlli di modulo (<select>) — la loro semantica e `change`, non
       `click`, e giudicarli col click produrrebbe accuse false;
     · un filtro GIA attivo — «TUTTI I CONCORRENTI» quando tutti sono gia
       mostrati non cambia niente perche non deve. Per questo ogni sospetto ha
       una SECONDA PROVA: si preme prima un fratello dello stesso gruppo (un
       altro chip, l'altra lingua) e poi di nuovo il sospetto. Se allora si
       muove, era idempotente, non morto.

   La prima versione di questo portone contava 139 morti su 156 in una sola
   schermata perche indicizzava la lista di partenza e cliccava per indice su un
   DOM che nel frattempo era cambiato: l'indice 153 non era piu «MONITORAGGIO
   EVENTI →». Si preme per FIRMA (tag|title|testo|w|h) e ordinale, e si ripristina
   la schermata prima di ogni pressione che ha spostato qualcosa.

       UN PORTONE CHE GRIDA AL LUPO INSEGNA A IGNORARLO.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import { serve, open, nav, clickables, clickTitle, C, line } from './lib/drive.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const JSON_OUT = arg('json', null);
const MAX_SCREENS = Number(arg('screens', 99));
const MAX_CLICKS = Number(arg('max', 9999));
const PORT = 8951;
const PORTAL = `http://localhost:${PORT}/portale.html`;
const SETTLE = 200;

/* ── l'enumerazione, identica a quella di drive.clickables() ───────────────
   Deve essere IDENTICA, altrimenti l'indice della descrizione e l'elemento che
   si preme non sono lo stesso oggetto. Il portone lo verifica a ogni schermata
   (assert su lunghezza) invece di sperarci. */
const ENUM = `() => { const out = [];
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (!(cs.cursor === 'pointer' || el.onclick || el.tagName === 'BUTTON' || el.tagName === 'A')) continue;
    let p = el.parentElement, nested = false;
    while (p) { const pc = getComputedStyle(p); if (pc.cursor === 'pointer' || p.tagName === 'A' || p.tagName === 'BUTTON') { nested = true; break; } p = p.parentElement; }
    if (nested) continue;
    out.push(el);
  } return out; }`;

const SIG = `(el) => { const r = el.getBoundingClientRect();
  return [el.tagName.toLowerCase(), el.getAttribute('title') || '', (el.textContent || '').trim().slice(0, 70),
    Math.round(r.width), Math.round(r.height)].join('|'); }`;

const sigOf = (c) => [c.tag, c.title, c.text, c.w, c.h].join('|');

/* ── l'impronta dello stato ────────────────────────────────────────────────
   Non basta il testo: un chip che si accende cambia la classe e non il testo.
   Si prende l'hash del testo LETTO, l'hash dell'HTML, il conto degli elementi,
   gli strati sovrapposti (il drawer), l'URL e la posizione di scorrimento —
   perche un salto ad ancora e un effetto vero quanto un pannello. */
const snap = (page) => page.evaluate(() => {
  const H = (s) => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h * 33) ^ s.charCodeAt(i)) | 0; return h; };
  const t = document.body.innerText || '';
  let overlays = 0;
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' && cs.position !== 'absolute') continue;
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
    if (!(parseInt(cs.zIndex, 10) >= 10)) continue;
    const r = el.getBoundingClientRect();
    if (r.width * r.height > 40000) overlays++;   /* un pannello, non un badge */
  }
  return { chars: t.length, th: H(t), hh: H(document.body.innerHTML),
    els: document.querySelectorAll('*').length, overlays,
    url: location.href, sy: Math.round(window.scrollY),
    head: t.slice(0, 90).replace(/\s+/g, ' ') };
});

const differs = (a, b) => !a || !b || a.th !== b.th || a.hh !== b.hh || a.els !== b.els
  || a.overlays !== b.overlays || a.url !== b.url || a.sy !== b.sy;

/* Rumore a riposo: quante mutazioni il DOM produce da solo in mezzo secondo.
   Se e zero, UNA mutazione dopo un click e prova di vita. Se un giorno non
   fosse piu zero, il portone lo stampa e la soglia si rialza da sola. */
const idleNoise = (page, ms = 600) => page.evaluate(async (t) => {
  let n = 0; const o = new MutationObserver((ms2) => { n += ms2.length; });
  o.observe(document.documentElement, { subtree: true, childList: true, attributes: true, characterData: true });
  await new Promise((r) => setTimeout(r, t)); o.disconnect(); return n;
}, ms);

const server = await serve(PORT);
const { browser, ctx, page, errors, failed } = await open({ port: PORT });

/* effetti che vivono FUORI dal documento: scheda nuova, download, dialog */
let tabs = 0, downloads = 0, dialogs = 0;
ctx.on('page', (p) => { tabs++; p.close().catch(() => {}); });
page.on('download', (d) => { downloads++; d.cancel().catch(() => {}); });
page.on('dialog', (d) => { dialogs++; d.dismiss().catch(() => {}); });

const NOISE = await idleNoise(page);

/* ── chi e la barra laterale ───────────────────────────────────────────────
   nav() restituisce OGNI [title] della pagina: le undici voci, le tre icone di
   testata e le venti regioni della mappa. La barra si riconosce dalla geometria
   misurata — la colonna a sinistra, etichette larghe — non da un elenco scritto
   a mano che invecchia al primo rinominare. */
const SIDEBAR = await page.evaluate(() => [...document.querySelectorAll('[title]')]
  .map((e) => ({ t: e.getAttribute('title'), r: e.getBoundingClientRect(), cur: getComputedStyle(e).cursor }))
  .filter((o) => o.t && o.r.left < 260 && o.r.width >= 100 && o.cur === 'pointer')
  .map((o) => o.t));
const NAV_ALL = await nav(page);
const sidebarSet = new Set(SIDEBAR);

const FORM = new Set(['select', 'input', 'textarea', 'option', 'label']);

/* enumera descrizioni + gruppo (stesso genitore) + a quale voce di menu punta */
const enrich = (p) => p.evaluate((E) => {
  const els = eval(E)(); const par = [];
  return els.map((e) => {
    const pa = e.parentElement; let g = par.indexOf(pa); if (g < 0) { par.push(pa); g = par.length - 1; }
    const nt = e.getAttribute('title') || (e.querySelector('[title]') ? e.querySelector('[title]').getAttribute('title') : '') || '';
    return { g, nt };
  });
}, ENUM);

const clickSig = (p, sig, ord) => p.evaluate(([E, S, s, o]) => {
  window.__m = 0; if (window.__mo) window.__mo.disconnect();
  window.__mo = new MutationObserver((ms) => { window.__m += ms.length; });
  window.__mo.observe(document.documentElement, { subtree: true, childList: true, attributes: true, characterData: true });
  const els = eval(E)(); const sg = eval(S);
  const hit = els.filter((e) => sg(e) === s)[o];
  if (!hit) { window.__mo.disconnect(); window.__mo = null; return false; }
  hit.click(); return true;
}, [ENUM, SIG, sig, ord]).catch(() => false);

const harvest = (p) => p.evaluate(() => { const n = window.__m || 0; if (window.__mo) window.__mo.disconnect(); window.__mo = null; return n; })
  .catch(() => 0);

/* ── ripristino ────────────────────────────────────────────────────────────
   Premere «EN» traduce l'intera applicazione e clickTitle('Concorrenza') non
   trova piu niente. Il ripristino sale di livello finche l'impronta torna
   quella di partenza: rientro dal menu · ricarica + rientro · resa. */
async function restore(label, wantTh) {
  for (let k = 0; k < 3; k++) {
    if (k > 0) { await page.goto(PORTAL, { waitUntil: 'networkidle' }).catch(() => {}); await page.waitForTimeout(500); }
    const ok = await clickTitle(page, label, 340).catch(() => false);
    if (!ok) continue;
    const s = await snap(page).catch(() => null);
    if (s && s.th === wantTh) return s;
  }
  return null;
}

/* ═══════════════ passaggio 1 · lo spazzamento ═══════════════════════════ */
const screens = [];
const suspects = [];
let judged = 0, alive = 0, formCtl = 0, selfNav = 0, notJudged = 0, drift = 0, enumSkew = 0;

for (const label of SIDEBAR.slice(0, MAX_SCREENS)) {
  const reached = await clickTitle(page, label, 520);
  const base = await snap(page);
  const cl = await clickables(page);
  const meta = await enrich(page);
  if (cl.length !== meta.length) enumSkew++;
  const sigs = cl.map(sigOf);
  const ord = []; const seen = {};
  for (const s of sigs) { seen[s] = (seen[s] || 0); ord.push(seen[s]); seen[s]++; }

  const sc = { label, reached, chars: base.chars, th: base.th, hh: base.hh, els: base.els,
    clickables: cl.length, judged: 0, alive: 0, dead: [], forms: 0, selfNav: 0, skipped: 0 };

  let cur = base;
  for (let i = 0; i < cl.length && sc.judged < MAX_CLICKS; i++) {
    const c = cl[i];
    /* Vale quello che il lettore vede: il cursore, o un <a>/<button> veri. Il
       div ospite del runtime porta un handler delegato ed e antenato di tutto —
       premerlo non e premere un bottone. */
    if (!c.visible || !(c.pointer || c.tag === 'a' || c.tag === 'button')) { notJudged++; continue; }
    if (FORM.has(c.tag)) { formCtl++; sc.forms++; continue; }
    if ((meta[i] || {}).nt === label) { selfNav++; sc.selfNav++; continue; }

    const t0 = tabs, d0 = downloads, g0 = dialogs;
    const hit = await clickSig(page, sigs[i], ord[i]);
    if (!hit) { sc.skipped++; drift++; await harvest(page); const r = await restore(label, base.th); cur = r || cur; continue; }
    await page.waitForTimeout(SETTLE);
    const mut = await harvest(page);
    const post = await snap(page).catch(() => null);
    const moved = differs(cur, post) || mut > NOISE || tabs > t0 || downloads > d0 || dialogs > g0;

    sc.judged++; judged++;
    if (moved) { alive++; sc.alive++; const r = await restore(label, base.th); if (r) cur = r; else { drift++; cur = await snap(page).catch(() => cur); } }
    else { cur = post || cur; suspects.push({ label, i, sig: sigs[i], ord: ord[i], g: (meta[i] || {}).g, c }); }
  }
  screens.push(sc);
  process.stderr.write(`  · ${label.padEnd(28)} clickables ${String(cl.length).padStart(4)}  giudicati ${String(sc.judged).padStart(4)}  vivi ${String(sc.alive).padStart(4)}  sospetti ${sc.judged - sc.alive}\n`);
}

/* ═══════════════ passaggio 2 · la seconda prova ═════════════════════════
   Un filtro gia attivo non si muove perche non deve. Si preme un FRATELLO
   dello stesso gruppo — l'altro chip, l'altra lingua — e poi di nuovo il
   sospetto. Chi si muove alla seconda era idempotente. Chi non si muove mai,
   con o senza contesto, e morto. */
const dead = [];
for (const s of suspects) {
  const sc = screens.find((x) => x.label === s.label);
  const base = { th: sc.th };
  let r = await restore(s.label, sc.th);
  if (!r) { drift++; continue; }
  const cl = await clickables(page);
  const meta = await enrich(page);
  const sigs = cl.map(sigOf); const ord = []; const seen = {};
  for (const g of sigs) { seen[g] = (seen[g] || 0); ord.push(seen[g]); seen[g]++; }

  /* il fratello: stesso genitore, firma diversa, e visibile */
  let sib = -1;
  for (let j = 0; j < cl.length; j++) {
    if (sigs[j] === s.sig) continue;
    if ((meta[j] || {}).g !== s.g) continue;
    if (!cl[j].visible || FORM.has(cl[j].tag)) continue;
    if ((meta[j] || {}).nt === s.label) continue;
    sib = j; break;
  }
  let mode = 'solo';
  if (sib >= 0) {
    const ok = await clickSig(page, sigs[sib], ord[sib]);
    await harvest(page);
    if (ok) { await page.waitForTimeout(SETTLE); mode = 'con fratello «' + (cl[sib].text || cl[sib].title || cl[sib].tag).replace(/\s+/g, ' ').slice(0, 24) + '»'; }
  }
  const pre = await snap(page).catch(() => null);
  const t0 = tabs, d0 = downloads, g0 = dialogs;
  const hit = await clickSig(page, s.sig, s.ord);
  if (!hit) {
    /* il fratello ha portato via il sospetto: si ritenta senza contesto */
    await harvest(page);
    const rr = await restore(s.label, base.th);
    if (!rr) { drift++; continue; }
    const p2 = await snap(page);
    const h2 = await clickSig(page, s.sig, s.ord);
    if (!h2) { drift++; await harvest(page); continue; }
    await page.waitForTimeout(SETTLE);
    const m2 = await harvest(page);
    const q2 = await snap(page).catch(() => null);
    if (differs(p2, q2) || m2 > NOISE || tabs > t0 || downloads > d0 || dialogs > g0) { alive++; sc.alive++; continue; }
    dead.push({ ...s, mode: 'solo' }); sc.dead.push(s.c); continue;
  }
  await page.waitForTimeout(SETTLE);
  const mut = await harvest(page);
  const post = await snap(page).catch(() => null);
  if (differs(pre, post) || mut > NOISE || tabs > t0 || downloads > d0 || dialogs > g0) { alive++; sc.alive++; continue; }
  dead.push({ ...s, mode }); sc.dead.push(s.c);
}

/* ═══════════════ NAVIGATION_GATE ════════════════════════════════════════ */
const navRows = [];
for (const label of SIDEBAR.slice(0, MAX_SCREENS)) {
  const reached = await clickTitle(page, label, 520);
  const s = await snap(page);
  const cl = await clickables(page);
  navRows.push({ label, reached, chars: s.chars, th: s.th, hh: s.hh, clickables: cl.length });
}
/* due voci che atterrano sullo stesso testo sono la stessa schermata con due
   nomi: il lettore preme due cose e ne riceve una sola. */
const collisions = [];
for (let i = 0; i < navRows.length; i++) {
  for (let j = i + 1; j < navRows.length; j++) if (navRows[i].th === navRows[j].th) collisions.push([navRows[i].label, navRows[j].label]);
}
const unreached = navRows.filter((r) => !r.reached).map((r) => r.label);
const EMPTY = 400;
const emptyScreens = navRows.filter((r) => r.chars < EMPTY || r.clickables === 0).map((r) => `${r.label} (${r.chars} char, ${r.clickables} clic)`);

/* ── l'indietro ───────────────────────────────────────────────────────────
   Non si cerca la parola «Indietro»: si apre una ficha, si guarda QUALE
   affordance e comparsa nella testata che prima non c'era, e la si preme. Se
   una di quelle riporta all'elenco, l'indietro esiste e funziona. */
let backOk = false, backLabel = null, backCandidates = 0, detailOpened = false;
{
  const home = SIDEBAR[0];
  await clickTitle(page, home, 520);
  const listSnap = await snap(page);
  const listSigs = new Set((await clickables(page)).map(sigOf));
  const opened = await page.evaluate(() => {
    const c = [...document.querySelectorAll('[data-case]')].filter((x) => x.getAttribute('data-case'))[0];
    if (!c) return false;
    let n = c; for (let i = 0; i < 5 && n; i++) { const cs = getComputedStyle(n); if (cs.cursor === 'pointer' || n.onclick || n.tagName === 'BUTTON' || n.tagName === 'A') break; n = n.parentElement; }
    (n || c).click(); return true;
  });
  await page.waitForTimeout(600);
  const detail = await snap(page);
  detailOpened = opened && detail.th !== listSnap.th;
  if (detailOpened) {
    const fresh = await clickables(page);
    const cand = [];
    for (const c of fresh) { const g = sigOf(c); if (listSigs.has(g)) continue; if (!c.visible || FORM.has(c.tag)) continue; cand.push(c); }
    /* la testata: quello che compare in alto quando si e dentro un dettaglio */
    const top = await page.evaluate((E) => eval(E)().map((e) => Math.round(e.getBoundingClientRect().top)), ENUM);
    const freshSigs = fresh.map(sigOf);
    const inTop = cand.filter((c) => { const ix = freshSigs.indexOf(sigOf(c)); return ix >= 0 && top[ix] < 80; });
    backCandidates = inTop.length;
    for (const c of inTop) {
      const ok = await clickSig(page, sigOf(c), 0); await harvest(page);
      if (!ok) continue;
      await page.waitForTimeout(600);
      const back = await snap(page);
      if (back.th === listSnap.th) { backOk = true; backLabel = (c.title || c.text || c.tag).replace(/\s+/g, ' ').slice(0, 28); break; }
      /* non era l'indietro: si riapre il dettaglio e si prova il successivo */
      await clickTitle(page, home, 420);
      await page.evaluate(() => { const c2 = [...document.querySelectorAll('[data-case]')].filter((x) => x.getAttribute('data-case'))[0]; if (c2) { let n = c2; for (let i = 0; i < 5 && n; i++) { const cs = getComputedStyle(n); if (cs.cursor === 'pointer' || n.onclick) break; n = n.parentElement; } (n || c2).click(); } });
      await page.waitForTimeout(500);
    }
  }
}

/* ── la ricarica ──────────────────────────────────────────────────────────
   F5 e il gesto piu comune di chi non si fida di quello che vede. Se dopo la
   ricarica lo schermo e vuoto o la console urla, l'applicazione e rotta per
   chiunque prema F5. */
const errBefore = errors.length, failBefore = failed.length;
await page.reload({ waitUntil: 'networkidle' });
await page.waitForTimeout(900);
const afterReload = await snap(page);
const reloadClicks = (await clickables(page)).length;
const reloadNav = (await nav(page)).length;
const reloadOk = afterReload.chars > EMPTY && reloadClicks > 0 && reloadNav > 0
  && errors.length === errBefore && failed.length === failBefore;

await browser.close(); server.close();

/* ═══════════════ giudizio ═══════════════════════════════════════════════ */
const noHandler = [];
for (const sc of screens) for (const c of sc.dead) if (c.pointer && !c.hasHandler && !c.href) noHandler.push({ screen: sc.label, ...c });
const totalClickables = screens.reduce((a, s) => a + s.clickables, 0);
const deadKeys = new Set(dead.map((d) => d.label + ' :: ' + d.sig));

console.log('\n  SINTONIA · CTA_DEAD_BUTTON_GATE + NAVIGATION_GATE');
console.log('  ' + '─'.repeat(100));
console.log(line(dead.length === 0, 'CT1', 'Every CTA pressed does something (dead buttons)', 0, dead.length));
console.log(line(noHandler.length === 0, 'CT2', 'No cursor:pointer without handler, href or effect', 0, noHandler.length));
console.log(line(drift === 0, 'CT3', 'No click left a screen the gate could not restore', 0, drift));
console.log(line(enumSkew === 0, 'CT4', 'Enumeration and click list are the same list', 0, enumSkew));
console.log(line(unreached.length === 0, 'NV1', 'Every sidebar item reaches a screen', 0, unreached.length || 'all ' + navRows.length));
console.log(line(collisions.length === 0, 'NV2', 'No two sidebar items land on the same screen', 0, collisions.length));
console.log(line(backOk, 'NV3', 'In-app back returns from a detail to its list', 'yes', backOk ? 'yes «' + backLabel + '»' : (detailOpened ? 'NO (' + backCandidates + ' candidates tried)' : 'no detail opened')));
console.log(line(reloadOk, 'NV4', 'A page reload does not break the portal', 'yes', reloadOk ? `yes (${afterReload.chars} char, ${reloadClicks} clic)` : 'NO'));
console.log(line(emptyScreens.length === 0, 'NV5', 'No navigation leaves the screen empty', 0, emptyScreens.length));
console.log(line(errors.length === 0, 'NV6', 'No console error during the whole sweep', 0, errors.length));
console.log(line(failed.length === 0, 'NV7', 'No failed request during the whole sweep', 0, failed.length));
console.log('  ' + '─'.repeat(100));
console.log(`  SCHERMATE = ${screens.length} di ${SIDEBAR.length} nella barra (${NAV_ALL.length} [title] in pagina, il resto e testata e mappa)`);
console.log(`  CLICCABILI TROVATI = ${totalClickables} · PREMUTI E GIUDICATI = ${judged} · VIVI = ${alive} · MORTI = ${dead.length}`);
console.log(`  non giudicati: ${formCtl} controlli di modulo (semantica change) · ${selfNav} voce della schermata corrente · ${notJudged} senza cursore proprio (host delegato, celle inerti della mappa)`);
console.log(`  rumore del DOM a riposo = ${NOISE} mutazioni/600ms — con zero, UNA mutazione dopo il click e prova di vita`);
console.log(`  schede nuove = ${tabs} · download = ${downloads} · dialog nativi = ${dialogs}`);
console.log(`  console error = ${errors.length} · richieste fallite = ${failed.length}`);

console.log('\n  ' + 'SCHERMATA'.padEnd(28) + 'CHAR'.padStart(7) + 'CLIC'.padStart(6) + 'GIUD'.padStart(6) + 'VIVI'.padStart(6) + 'MORTI'.padStart(7));
for (const s of screens) {
  const d = s.dead.filter((c) => deadKeys.has(s.label + ' :: ' + sigOf(c))).length;
  console.log('  ' + s.label.padEnd(28) + String(s.chars).padStart(7) + String(s.clickables).padStart(6)
    + String(s.judged).padStart(6) + String(s.alive).padStart(6) + (d ? C.r(String(d).padStart(7)) : C.g('      0')));
}
if (dead.length) {
  console.log('\n  ' + C.r('BOTTONI MORTI') + ' — premuti, e non e successo niente:');
  for (const d of dead) {
    const t = (d.c.text || d.c.title || '(senza testo)').replace(/\s+/g, ' ').slice(0, 46);
    console.log(`    ${d.label.padEnd(26)} <${d.c.tag}> «${t}»`.padEnd(84)
      + C.d(`${d.c.w}×${d.c.h} handler=${d.c.hasHandler ? 'si' : 'NO'} href=${d.c.href || 'NO'} · 2ª prova ${d.mode}`));
  }
}
if (collisions.length) { console.log('\n  ' + C.r('SCHERMATE GEMELLE') + ':'); for (const [a, b] of collisions) console.log(`    ${a}  ≡  ${b}`); }
if (emptyScreens.length) { console.log('\n  ' + C.r('SCHERMATE VUOTE') + ':'); for (const e of emptyScreens) console.log('    ' + e); }
if (errors.length) { console.log('\n  ' + C.r('CONSOLE') + ':'); for (const e of errors.slice(0, 10)) console.log('    ' + e); }
if (failed.length) { console.log('\n  ' + C.r('RICHIESTE') + ':'); for (const f of failed.slice(0, 10)) console.log('    ' + f); }
console.log('');

if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({
  sidebar: SIDEBAR, noise: NOISE, screens, dead, noHandler, navRows, collisions, unreached, emptyScreens,
  back: { ok: backOk, label: backLabel, candidates: backCandidates, detailOpened },
  reload: { ok: reloadOk, chars: afterReload.chars, clickables: reloadClicks },
  totals: { screens: screens.length, clickables: totalClickables, judged, alive, dead: dead.length, formCtl, selfNav, notJudged, drift, tabs, downloads, dialogs },
  errors, failed,
}, null, 1));

const FAIL = dead.length || noHandler.length || drift || enumSkew || unreached.length || collisions.length
  || !backOk || !reloadOk || emptyScreens.length || errors.length || failed.length;
process.exit(FAIL ? 1 : 0);
