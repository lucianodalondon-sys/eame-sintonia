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
const SETTLE = 190;

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
   Premere «EN» traduce l'intera applicazione: clickTitle('Concorrenza') non
   trova piu niente, e la scelta SOPRAVVIVE alla ricarica perche vive in
   localStorage['sintonia_lang']. La prima versione di questo portone ricaricava
   e ricadeva in inglese: da li in poi ogni firma mancava il bersaglio, 105
   pressioni finivano nel vuoto e due voci di menu sembravano gemelle. Non era
   un difetto del portale — era il portone che misurava uno stato che si era
   portato addosso.

       PRIMA DI MISURARE, RIPORTA IL MONDO DOV'ERA. ANCHE LA MEMORIA.

   Il ripristino sale di livello finche l'impronta del testo torna quella di
   partenza: rientro dal menu · memoria svuotata + ricarica + rientro · resa. */
const wipe = () => page.evaluate(() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) { /* origine opaca */ } }).catch(() => {});

async function reboot() {
  await wipe();
  await page.goto(PORTAL, { waitUntil: 'networkidle' }).catch(() => {});
  await wipe();
  await page.reload({ waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(600);
}

let rebase = 0;
const freshSnap = async (label) => {
  await reboot();
  const ok = await clickTitle(page, label, 460).catch(() => false);
  return ok ? snap(page).catch(() => null) : null;
};

/* `sc` e la scheda della schermata, non un numero: quando l'impronta congelata
   all'inizio non torna nemmeno dopo due riavvii, la si RIMISURA da pulito due
   volte. Se le due misure coincidono, quella E la schermata — l'impronta di
   partenza era di un istante transitorio — e la scheda la riadotta. Accusare
   una deriva che non esiste costa piu che ammettere di aver misurato presto. */
async function restore(label, sc) {
  for (let k = 0; k < 3; k++) {
    if (k > 0) await reboot();
    const ok = await clickTitle(page, label, 340).catch(() => false);
    if (!ok) continue;
    const s = await snap(page).catch(() => null);
    if (s && s.th === sc.th) return s;
  }
  const a = await freshSnap(label);
  const b = await freshSnap(label);
  if (a && b && a.th === b.th) { sc.th = a.th; sc.chars = a.chars; sc.rebased = true; rebase++; return b; }
  return null;
}

/* ═══════════════ passaggio 1 · lo spazzamento ═══════════════════════════ */
const screens = [];
const suspects = [];
const blew = [];   /* pressioni che hanno fatto urlare la console */
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

    const t0 = tabs, d0 = downloads, g0 = dialogs, e0 = errors.length;
    const hit = await clickSig(page, sigs[i], ord[i]);
    if (!hit) { sc.skipped++; drift++; await harvest(page); const r = await restore(label, sc); cur = r || cur; continue; }
    await page.waitForTimeout(SETTLE);
    const mut = await harvest(page);
    const post = await snap(page).catch(() => null);
    /* Un errore di console va ATTRIBUITO alla pressione che lo ha prodotto,
       altrimenti il portone dice «sei errori» e nessuno sa dove premere. */
    if (errors.length > e0) blew.push({ screen: label, tag: c.tag, text: (c.text || c.title || '').replace(/\s+/g, ' ').slice(0, 46), msg: errors[e0] });
    const moved = differs(cur, post) || mut > NOISE || tabs > t0 || downloads > d0 || dialogs > g0;

    sc.judged++; judged++;
    if (moved) { alive++; sc.alive++; const r = await restore(label, sc); if (r) cur = r; else { drift++; cur = await snap(page).catch(() => cur); } }
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
const dead = [], idempotent = [];
for (const s of suspects) {
  const sc = screens.find((x) => x.label === s.label);
  let r = await restore(s.label, sc);
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
  /* L'impronta si prende SEMPRE prima di premere. La prima riscrittura di
     questo blocco la prendeva dopo il click e confrontava il dopo col dopo:
     tutto risultava fermo. Lo si e visto perche il portone accusava comandi
     che a mano si muovevano. */
  const press = async (sig, ordinal) => {
    const pre = await snap(page).catch(() => null);
    const t0 = tabs, d0 = downloads, g0 = dialogs;
    const ok = await clickSig(page, sig, ordinal);
    if (!ok) { await harvest(page); return null; }
    await page.waitForTimeout(SETTLE);
    const mut = await harvest(page);
    const post = await snap(page).catch(() => null);
    return differs(pre, post) || mut > NOISE || tabs > t0 || downloads > d0 || dialogs > g0;
  };

  let moved = await press(s.sig, s.ord);
  if (moved === null) {
    /* il fratello ha portato via il sospetto: si ritenta senza contesto */
    const rr = await restore(s.label, sc);
    if (!rr) { drift++; continue; }
    mode = 'solo';
    moved = await press(s.sig, s.ord);
    if (moved === null) { drift++; continue; }
  }
  if (moved) { alive++; sc.alive++; continue; }

  /* ── terza prova · lo STESSO comando su un'ALTRA schermata ───────────────
     Il blocco del marchio «SINTONIA / ADAMA ITALIA · INTELLIGENCE» porta a
     casa. Sulla schermata di casa non muove niente — perche sei gia a casa —
     e il portone lo accusava di essere morto: un'accusa falsa contro un
     comando che funziona. Lo stesso vale per la voce di menu della schermata
     corrente, che qui pero e gia esclusa per nome.

         PRIMA DI DICHIARARE MORTO UN COMANDO, PROVALO DOVE HA QUALCOSA DA FARE.

     Si cerca la stessa firma su un'altra schermata della barra e la si preme
     li. Se li si muove, era idempotente, non morto. */
  let revived = null;
  for (const other of SIDEBAR.slice(0, MAX_SCREENS)) {
    if (other === s.label) continue;
    const osc = screens.find((x) => x.label === other);
    if (!osc) continue;
    const or = await restore(other, osc);
    if (!or) continue;
    const ocl = await clickables(page);
    const osigs = ocl.map(sigOf);
    if (!osigs.includes(s.sig)) continue;
    const oord = osigs.filter((x, ix) => x === s.sig && ix < osigs.indexOf(s.sig)).length;
    if (await press(s.sig, oord)) { revived = other; break; }
  }
  if (revived) { alive++; sc.alive++; idempotent.push({ ...s, revived }); continue; }
  dead.push({ ...s, mode }); sc.dead.push(s.c);
}

/* ═══════════════ NAVIGATION_GATE ════════════════════════════════════════ */
/* Si riparte da zero: la navigazione si giudica su un portale appena aperto,
   non su quello che lo spazzamento ha lasciato dietro di se. */
await reboot();
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
   Non si cerca la parola «Indietro»: si scende in un dettaglio e si prova ogni
   comando della testata finche uno riporta ESATTAMENTE all'elenco da cui si e
   partiti. Se nessuno lo fa, l'indietro non esiste — e non importa come si
   chiama.

   Si comincia da una schermata che NON e quella di casa. Il blocco del marchio
   riporta a casa da ovunque: provando l'indietro su casa, il marchio passava
   l'esame al posto suo e il portone dichiarava funzionante un ritorno che non
   aveva mai misurato.

       UN RITORNO SI PROVA DOVE TORNARE INDIETRO E DIVERSO DA TORNARE A CASA.

   Non si prova un <a href>: quello lascia l'applicazione, non ci rientra. */
let backOk = false, backLabel = null, backScreen = null, backTried = 0, detailOpened = false;
{
  const navThSet = new Set(navRows.map((r) => r.th));
  const order = SIDEBAR.slice(1, MAX_SCREENS).concat(SIDEBAR.slice(0, 1));
  for (const label of order.slice(0, 4)) {
    if (backOk) break;
    await reboot();
    if (!await clickTitle(page, label, 520)) continue;
    const listSnap = await snap(page);
    const geo = await page.evaluate((E) => eval(E)().map((e) => { const r = e.getBoundingClientRect(); return { top: Math.round(r.top), left: Math.round(r.left), w: Math.round(r.width), h: Math.round(r.height) }; }), ENUM);
    const cl = await clickables(page);
    const sigs = cl.map(sigOf); const ord = []; const seen = {};
    for (const g of sigs) { seen[g] = (seen[g] || 0); ord.push(seen[g]); seen[g]++; }
    /* una riga di contenuto: sotto la testata, fuori dalla colonna del menu */
    const rows = cl.map((c, ix) => ({ c, ix })).filter(({ c, ix }) => c.visible && !FORM.has(c.tag) && !c.href
      && geo[ix] && geo[ix].top >= 120 && geo[ix].left >= 240 && geo[ix].w >= 80 && geo[ix].h >= 24);

    let openedIx = -1;
    for (const { ix } of rows.slice(0, 8)) {
      const ok = await clickSig(page, sigs[ix], ord[ix]); await harvest(page);
      if (!ok) continue;
      await page.waitForTimeout(520);
      const d = await snap(page).catch(() => null);
      /* un dettaglio e uno stato che la barra laterale non sa raggiungere */
      if (d && d.th !== listSnap.th && !navThSet.has(d.th)) { openedIx = ix; break; }
      await reboot(); await clickTitle(page, label, 460);
    }
    if (openedIx < 0) continue;
    detailOpened = true;

    const reopen = async () => {
      await reboot();
      if (!await clickTitle(page, label, 460)) return false;
      const ok = await clickSig(page, sigs[openedIx], ord[openedIx]); await harvest(page);
      if (ok) await page.waitForTimeout(520);
      return ok;
    };

    const dgeo = await page.evaluate((E) => eval(E)().map((e) => Math.round(e.getBoundingClientRect().top)), ENUM);
    const dcl = await clickables(page);
    const dsigs = dcl.map(sigOf);
    const cands = dcl.map((c, ix) => ({ c, ix })).filter(({ c, ix }) => c.visible && !FORM.has(c.tag)
      && c.tag !== 'a' && !c.href && dgeo[ix] !== undefined && dgeo[ix] < 80 && !sidebarSet.has(c.title));
    for (const { c, ix } of cands) {
      backTried++;
      const g = sigOf(c);
      const o = dsigs.slice(0, ix).filter((x) => x === g).length;
      const ok = await clickSig(page, g, o); await harvest(page);
      if (ok) {
        await page.waitForTimeout(600);
        const back = await snap(page).catch(() => null);
        if (back && back.th === listSnap.th) {
          backOk = true; backScreen = label;
          backLabel = (c.title || c.text || c.tag).replace(/\s+/g, ' ').slice(0, 28);
          break;
        }
      }
      if (!await reopen()) break;   /* si riparte pulito per il candidato dopo */
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
console.log(line(backOk, 'NV3', 'In-app back returns from a detail to its list', 'yes', backOk ? `yes «${backLabel}» su ${backScreen}` : (detailOpened ? 'NO (' + backTried + ' topbar controls tried)' : 'no drill-down found')));
console.log(line(reloadOk, 'NV4', 'A page reload does not break the portal', 'yes', reloadOk ? `yes (${afterReload.chars} char, ${reloadClicks} clic)` : 'NO'));
console.log(line(emptyScreens.length === 0, 'NV5', 'No navigation leaves the screen empty', 0, emptyScreens.length));
console.log(line(errors.length === 0, 'NV6', 'No console error during the whole sweep', 0, errors.length));
console.log(line(failed.length === 0, 'NV7', 'No failed request during the whole sweep', 0, failed.length));
console.log('  ' + '─'.repeat(100));
console.log(`  SCHERMATE = ${screens.length} di ${SIDEBAR.length} nella barra (${NAV_ALL.length} [title] in pagina, il resto e testata e mappa)`);
console.log(`  CLICCABILI TROVATI = ${totalClickables} · PREMUTI E GIUDICATI = ${judged} · VIVI = ${alive} · MORTI = ${dead.length}`);
console.log(`  non giudicati: ${formCtl} controlli di modulo (semantica change) · ${selfNav} voce della schermata corrente · ${notJudged} senza cursore proprio (host delegato, celle inerti della mappa)`);
console.log(`  rumore del DOM a riposo = ${NOISE} mutazioni/600ms — con zero, UNA mutazione dopo il click e prova di vita`);
console.log(`  impronte rimisurate da pulito = ${rebase} · schermate non ripristinabili = ${drift}`);
console.log(`  idempotenti (fermi qui, vivi altrove) = ${idempotent.length} — un comando gia soddisfatto non e un comando morto`);
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
if (blew.length) {
  console.log('\n  ' + C.r('PRESSIONI CHE HANNO FATTO URLARE LA CONSOLE') + ':');
  for (const b of blew.slice(0, 12)) console.log(`    ${b.screen.padEnd(26)} <${b.tag}> «${b.text}»`.padEnd(84) + C.d(b.msg.slice(0, 70)));
}
if (errors.length) { console.log('\n  ' + C.r('CONSOLE') + ':'); for (const e of errors.slice(0, 10)) console.log('    ' + e); }
if (failed.length) { console.log('\n  ' + C.r('RICHIESTE') + ':'); for (const f of failed.slice(0, 10)) console.log('    ' + f); }
console.log('');

if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({
  sidebar: SIDEBAR, noise: NOISE, screens, dead, idempotent, noHandler, blew, navRows, collisions, unreached, emptyScreens,
  back: { ok: backOk, label: backLabel, screen: backScreen, tried: backTried, detailOpened },
  reload: { ok: reloadOk, chars: afterReload.chars, clickables: reloadClicks },
  totals: { screens: screens.length, clickables: totalClickables, judged, alive, dead: dead.length, formCtl, selfNav, notJudged, drift, rebase, tabs, downloads, dialogs },
  errors, failed,
}, null, 1));

const FAIL = dead.length || noHandler.length || drift || enumSkew || unreached.length || collisions.length
  || !backOk || !reloadOk || emptyScreens.length || errors.length || failed.length;
process.exit(FAIL ? 1 : 0);
