/* SINTONIA · CTA_DEAD_BUTTON_GATE + NAVIGATION_GATE
   ---------------------------------------------------------------------------
   node italia-portale/audit/cta-navigation.mjs
        [--json out.json] [--screens N] [--max N] [--port 8951]

   Un bottone che il cursore promette e che non fa niente e peggio di un bottone
   assente: chi legge crede di aver premuto, aspetta, e conclude che il portale
   e rotto. Questo controllo non cerca stringhe nel sorgente — apre un Chromium,
   percorre ogni schermata della barra laterale, PREME ogni affordance e chiede
   al DOM se e successo qualcosa.

       IL CURSORE E UNA PROMESSA. UNA PROMESSA CHE NON SI MUOVE E UN DIFETTO.

   Prova di vita accettata, in ordine di forza: l'impronta della schermata
   cambia · un pannello/drawer compare · il DOM muta (una sola mutazione basta —
   il rumore a riposo, misurato a ogni esecuzione, e zero) · si apre una scheda
   nuova o un download · si apre un dialog nativo · per un <a>, una destinazione
   vera nell'href (vedi il blocco «i collegamenti» piu sotto).

   Tre cose NON sono difetti, e il portone le riconosce da solo:
     · la voce di menu della schermata in cui gia ti trovi (premere «Concorrenza»
       stando su Concorrenza deve essere un no-op);
     · i controlli di modulo (<select>) — la loro semantica e `change`, non
       `click`, e giudicarli col click produrrebbe accuse false;
     · un comando GIA soddisfatto — il segmento «12M» quando l'orizzonte e gia
       dodici mesi, il chip «TUTTI I CONCORRENTI» quando sono gia tutti, il
       marchio che porta a casa quando sei gia a casa. Nessuno di questi e
       morto. Per questo chi non si muove al primo colpo non viene accusato:
       passa al passaggio 2, che lo ripreme dopo un FRATELLO VIVO del suo
       gruppo e poi su un'ALTRA schermata, dove ha ancora lavoro da fare.

   La prima versione di questo portone contava 139 morti su 156 in una sola
   schermata perche indicizzava la lista di partenza e cliccava per indice su un
   DOM che nel frattempo era cambiato: l'indice 153 non era piu «MONITORAGGIO
   EVENTI →». Si preme per FIRMA (tag|title|testo|w|h) e ordinale, e si ripristina
   la schermata prima di ogni pressione che ha spostato qualcosa.

       UN PORTONE CHE GRIDA AL LUPO INSEGNA A IGNORARLO.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import net from 'node:net';
import { serve, open, nav, clickables, clickTitle, C, line } from './lib/drive.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const JSON_OUT = arg('json', null);
const MAX_SCREENS = Number(arg('screens', 99));
const MAX_CLICKS = Number(arg('max', 9999));
const PROVE_LINKS = Number(arg('prove-links', 3));   /* quanti <a> esterni per schermata si aprono davvero */
const SETTLE = 190;

/* La porta si cerca, non si dichiara. Un portone che muore con EADDRINUSE
   perche l'esecuzione precedente ha lasciato un socket a raffreddare non ha
   misurato niente: chi lo lancia legge uno stack trace al posto di un verdetto.
   serve() non rifiuta la promessa quando la porta e occupata — emette 'error'
   e uccide il processo — quindi la porta si tasta prima, con un socket usa e
   getta, e solo dopo si consegna a serve(). */
const canBind = (p) => new Promise((r) => {
  const probe = net.createServer();
  probe.once('error', () => r(false));
  probe.once('listening', () => probe.close(() => r(true)));
  probe.listen(p, '0.0.0.0');
});
async function bind(first) {
  for (let p = first; p < first + 20; p++) if (await canBind(p)) return { server: await serve(p), port: p };
  throw new Error('nessuna porta libera fra ' + first + ' e ' + (first + 19));
}

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

const { server, port: PORT } = await bind(Number(arg('port', 8951)));
const PORTAL = `http://localhost:${PORT}/portale.html`;
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

/* -- i collegamenti -------------------------------------------------------
   «APRI LA FONTE ->» sono 79 <a target="_blank"> con un https vero. Premendoli
   il DOM non si muove di un carattere — la scheda nuova arriva circa un secondo
   dopo, molto oltre la finestra di 190 ms in cui il portone guarda — e la prima
   versione li accusava tutti: settantotto bugie in una schermata sola, contro
   collegamenti perfettamente funzionanti.

       UN <a> CON UNA DESTINAZIONE E GIA CABLATO: LA PROVA E L'INDIRIZZO.
       UN <a> CON «#» O «javascript:» PROMETTE E NON PORTA DA NESSUNA PARTE.

   Quindi: un href vero non si preme uno per uno (aprirebbe la rete pubblica,
   una scheda per riga, e renderebbe il portone lento e dipendente da internet);
   un href vuoto, «#» o «javascript:» si preme come qualunque altro comando.
   Perche la regola resti una MISURA e non una fiducia, ogni schermata ne APRE
   DAVVERO qualcuno (--prove-links, 3 di default) con una finestra di 1,6 s. */
const liveHref = (h) => !!h && h !== '#' && h !== '#!' && !/^javascript:/i.test(h);

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
  /* Si svuota la memoria PRIMA di riaprire: stessa origine, quindi il wipe vale
     per il caricamento successivo. Una sola apertura basta — la seconda che
     questo blocco faceva raddoppiava il costo del ripristino senza ripulire
     niente in piu. */
  await wipe();
  await page.goto(PORTAL, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(550);
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
    const ok = await clickTitle(page, label, 420).catch(() => false);
    if (!ok) continue;
    let s = await snap(page).catch(() => null);
    if (s && s.th === sc.th) return s;
    /* un respiro in piu prima di pagare un riavvio: buona parte dei ripristini
       «falliti» era solo misurata mentre la schermata finiva di disegnarsi */
    await page.waitForTimeout(360);
    s = await snap(page).catch(() => null);
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
let linked = 0, linkProved = 0;
const linkProofFailed = [];

for (const label of SIDEBAR.slice(0, MAX_SCREENS)) {
  const reached = await clickTitle(page, label, 520);
  const base = await snap(page);
  const cl = await clickables(page);
  const meta = await enrich(page);
  if (cl.length !== meta.length) enumSkew++;
  const sigs = cl.map(sigOf);
  const ord = []; const seen = {};
  for (const s of sigs) { seen[s] = (seen[s] || 0); ord.push(seen[s]); seen[s]++; }

  /* L'enumerazione resta nella scheda: la seconda prova ne ha bisogno per
     scegliere un fratello, e ri-enumerare da capo darebbe indici diversi. */
  const sc = { label, reached, chars: base.chars, th: base.th, hh: base.hh, els: base.els,
    clickables: cl.length, judged: 0, alive: 0, dead: [], forms: 0, selfNav: 0, skipped: 0,
    sigs, ord, meta, aliveIdx: [] };

  let cur = base;
  for (let i = 0; i < cl.length && sc.judged < MAX_CLICKS; i++) {
    const c = cl[i];
    /* Vale quello che il lettore vede: il cursore, o un <a>/<button> veri. Il
       div ospite del runtime porta un handler delegato ed e antenato di tutto —
       premerlo non e premere un bottone. */
    if (!c.visible || !(c.pointer || c.tag === 'a' || c.tag === 'button')) { notJudged++; continue; }
    if (FORM.has(c.tag)) { formCtl++; sc.forms++; continue; }
    if ((meta[i] || {}).nt === label) { selfNav++; sc.selfNav++; continue; }

    if (c.tag === 'a' && liveHref(c.href)) {
      linked++; sc.linked = (sc.linked || 0) + 1;
      if ((sc.proved || 0) >= PROVE_LINKS) continue;      /* cablato: l'indirizzo e la prova */
      sc.proved = (sc.proved || 0) + 1;
      const t0 = tabs, u0 = page.url();
      const hit = await clickSig(page, sigs[i], ord[i]);
      await harvest(page);
      if (!hit) { sc.skipped++; continue; }
      /* la finestra larga che una scheda nuova richiede davvero */
      for (let w = 0; w < 18 && tabs === t0 && page.url() === u0; w++) await page.waitForTimeout(200);
      if (tabs > t0 || page.url() !== u0) linkProved++;
      else linkProofFailed.push({ screen: label, text: (c.text || '').replace(/\s+/g, ' ').slice(0, 40), href: c.href });
      const r = await restore(label, sc);
      if (r) cur = r; else { drift++; cur = await snap(page).catch(() => cur); }
      continue;
    }

    /* Una pressione misurata: impronta prima · click · respiro · impronta dopo.
       `pre` e sempre lo stato REALE del momento, mai quello di partenza — ed e
       per questo che il ritorno fra un click e l'altro puo essere leggero. */
    const attempt = async (pre) => {
      const e0 = errors.length;
      const hit = await clickSig(page, sigs[i], ord[i]);
      if (!hit) { await harvest(page); return null; }
      await page.waitForTimeout(SETTLE);
      const mut = await harvest(page);
      const post = await snap(page).catch(() => null);
      /* Un errore di console va ATTRIBUITO alla pressione che lo ha prodotto,
         altrimenti il portone dice «sei errori» e nessuno sa dove premere. */
      if (errors.length > e0) blew.push({ screen: label, tag: c.tag, text: (c.text || c.title || '').replace(/\s+/g, ' ').slice(0, 46), msg: errors[e0] });
      /* QUI NON SI CONTANO SCHEDE NUOVE, DOWNLOAD NE DIALOG.
         «VEDI L'INTELLIGENCE →» apre una scheda con window.open, e la scheda
         arriva un secondo abbondante dopo il click: fuori dalla finestra di
         190 ms di questo passaggio, e dentro quella della pressione SUCCESSIVA,
         che si vedrebbe attribuire una vita non sua. Un effetto che arriva
         tardi non si giudica di fretta: chi non si muove qui diventa sospetto e
         il passaggio 2 lo riprova con la pazienza necessaria. */
      return { moved: differs(pre, post) || mut > NOISE, post };
    };

    let out = await attempt(cur);
    if (!out) {
      /* la firma non risponde: lo stato e scivolato sotto i piedi. Qui si paga
         il ripristino pesante — con riavvio, se serve — e si ritenta UNA volta. */
      const r = await restore(label, sc);
      if (!r) { sc.skipped++; drift++; continue; }
      cur = r;
      out = await attempt(cur);
      /* dopo un ripristino vero la firma ancora non c'e: quell'elemento non si
         presenta piu su questa schermata. Non e un bottone morto, e un elemento
         che non e tornato — si conta, non si accusa. */
      if (!out) { sc.skipped++; continue; }
    }

    sc.judged++; judged++;
    if (out.moved) {
      alive++; sc.alive++; sc.aliveIdx.push(i);
      /* RITORNO LEGGERO: basta essere di nuovo sulla schermata; non serve
         essere tornati all'istante esatto, perche il confronto successivo usa
         l'impronta appena misurata. Il riavvio si paga solo quando serve. */
      const back = await clickTitle(page, label, 400).catch(() => false);
      cur = back ? await snap(page).catch(() => null) : null;
      if (!cur) { const r = await restore(label, sc); if (r) cur = r; else { drift++; cur = await snap(page).catch(() => null); } }
    } else { cur = out.post || cur; suspects.push({ label, i, sig: sigs[i], ord: ord[i], g: (meta[i] || {}).g, c }); }
  }
  screens.push(sc);
  process.stderr.write(`  · ${label.padEnd(28)} clickables ${String(cl.length).padStart(4)}  giudicati ${String(sc.judged).padStart(4)}  vivi ${String(sc.alive).padStart(4)}  sospetti ${sc.judged - sc.alive}\n`);
}

/* ═══════════════ passaggio 2 · la seconda prova ═════════════════════════
   Un comando GIA soddisfatto non si muove perche non deve: il segmento «12M»
   quando l'orizzonte e gia dodici mesi, il chip «TUTTI I CONCORRENTI» quando
   sono gia tutti, la voce di casa quando sei gia a casa. Nessuno di questi e
   morto, e accusarli sarebbe una bugia con l'aria di un risultato.

   Il sospetto viene ripremuto in contesti che gli danno qualcosa da fare, dal
   piu economico al piu costoso:
     1. da solo, sulla schermata pulita (spesso basta: il primo tentativo puo
        essere caduto su uno stato sporco);
     2. dopo un FRATELLO VIVO dello stesso gruppo — vivo secondo il passaggio 1,
        non secondo la speranza. La prima versione prendeva il primo fratello in
        ordine di DOM: per «12M» era «← OGGI», che non muove niente nemmeno lui,
        e il portone accusava un segmento perfettamente funzionante. Si ordinano
        per VICINANZA: il vicino di un segmento e l'altro segmento;
     3. su un'ALTRA schermata, dove la stessa firma ha ancora lavoro da fare.

       CHI NON SI MUOVE MAI, IN NESSUN CONTESTO, E MORTO. GLI ALTRI NO.
   ─────────────────────────────────────────────────────────────────────────── */
const dead = [], idempotent = [];

/* Preme una firma e dice se il mondo si e mosso. null = la firma non esiste
   piu su questa schermata (lo stato e cambiato sotto i piedi). */
const PATIENCE = Number(arg('patience', 10));   /* × 250 ms = 2,5 s di attesa */

const press = async (sig, ordinal) => {
  const pre = await snap(page).catch(() => null);
  const t0 = tabs, d0 = downloads, g0 = dialogs;
  const ok = await clickSig(page, sig, ordinal);
  if (!ok) { await harvest(page); return null; }
  await page.waitForTimeout(SETTLE);
  const mut = await harvest(page);
  let post = await snap(page).catch(() => null);
  let moved = differs(pre, post) || mut > NOISE || tabs > t0 || downloads > d0 || dialogs > g0;
  /* LA PAZIENZA SI PAGA SOLO A CHI SEMBRA MORTO.
     Una scheda aperta con window.open, un download, un pannello che si disegna
     dopo una animazione: arrivano dopo. Qui i sospetti sono pochi e aspettare
     costa poco; nel passaggio 1, con 889 pressioni, costerebbe mezz'ora. */
  for (let w = 0; !moved && w < PATIENCE; w++) {
    await page.waitForTimeout(250);
    post = await snap(page).catch(() => null);
    moved = differs(pre, post) || tabs > t0 || downloads > d0 || dialogs > g0;
  }
  return moved;
};

for (const s of suspects) {
  const sc = screens.find((x) => x.label === s.label);

  /* i fratelli vivi dello stesso gruppo, dal piu vicino al piu lontano */
  const sibs = sc.aliveIdx
    .filter((j) => j !== s.i && (sc.meta[j] || {}).g === s.g && sc.sigs[j] !== s.sig)
    .sort((a, b) => Math.abs(a - s.i) - Math.abs(b - s.i))
    .slice(0, 4);

  let verdict = false, mode = 'solo', unresolved = false;
  for (const sib of [null].concat(sibs)) {
    const r = await restore(s.label, sc);
    if (!r) { unresolved = true; break; }
    if (sib !== null) {
      const got = await press(sc.sigs[sib], sc.ord[sib]);
      if (got === null) continue;                 /* il fratello e sparito */
      mode = 'dopo «' + (sc.sigs[sib].split('|')[2] || sc.sigs[sib].split('|')[1] || sc.sigs[sib].split('|')[0]).replace(/\s+/g, ' ').slice(0, 22) + '»';
    } else mode = 'solo';
    const moved = await press(s.sig, s.ord);
    if (moved === null) continue;                 /* il sospetto e sparito */
    if (moved) { verdict = true; break; }
  }
  if (unresolved) { drift++; continue; }
  if (verdict) { alive++; sc.alive++; if (mode !== 'solo') idempotent.push({ ...s, mode }); continue; }

  /* terza prova: la stessa firma dove ha ancora qualcosa da fare */
  let revived = null;
  for (const other of SIDEBAR.slice(0, MAX_SCREENS)) {
    if (other === s.label) continue;
    const osc = screens.find((x) => x.label === other);
    if (!osc || !osc.sigs.includes(s.sig)) continue;
    if (!await restore(other, osc)) continue;
    const ix = osc.sigs.indexOf(s.sig);
    if (await press(s.sig, osc.ord[ix])) { revived = other; break; }
  }
  if (revived) { alive++; sc.alive++; idempotent.push({ ...s, mode: 'vivo su ' + revived, revived }); continue; }
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
   Non si cerca la parola «Indietro»: si costruisce una situazione in cui solo
   un vero ritorno puo passare, e si prova ogni comando della testata finche uno
   la risolve. Se nessuno la risolve, il ritorno non funziona — e non importa
   come si chiama il bottone.

   Due scenari, perche uno solo si lascia ingannare:

     A · STORIA   casa → B → C, poi indietro DEVE dare B.
         Con due passi soltanto (casa → B, indietro) passerebbe anche il blocco
         del marchio, che porta a casa da ovunque: casa era la precedente per
         caso. Con tre passi il marchio finisce a casa e fallisce; solo chi
         torna davvero atterra su B.

     B · DETTAGLIO   B → casa → apri una ficha, poi indietro DEVE dare l'ELENCO
         di casa, non B. Se aprire una ficha non lascia traccia nella storia,
         l'indietro salta l'elenco e riporta a B — che e esattamente il difetto
         che questo scenario esiste per vedere.

   Una prima versione cercava invece «uno stato che la barra non sa raggiungere»
   e ci finiva dentro una fisarmonica che si apre: espandere una riga non e
   navigare, l'indietro giustamente tornava alla schermata precedente, e il
   portone lo chiamava difetto. Quattro schermate accusate, ventisette comandi
   provati, zero difetti veri.

       PRIMA DI GIUDICARE UN RITORNO, COSTRUISCI UN POSTO DA CUI TORNARE.

   Un <a href> non e candidato: quello esce dall'applicazione, non ci rientra. */
let backHistory = false, backDetail = false, backLabel = null, backTried = 0, caseScreen = null;
{
  const home = SIDEBAR[0];
  const B = SIDEBAR[1], Cs = SIDEBAR[2];

  /* i comandi della testata, misurati una volta su una schermata qualunque */
  await reboot();
  await clickTitle(page, B, 480);
  const topGeo = await page.evaluate((E) => eval(E)().map((e) => Math.round(e.getBoundingClientRect().top)), ENUM);
  const topCl = await clickables(page);
  const topSigs = topCl.map(sigOf);
  const cands = topCl.map((c, ix) => ({ c, ix })).filter(({ c, ix }) => c.visible && !FORM.has(c.tag)
    && c.tag !== 'a' && !c.href && topGeo[ix] !== undefined && topGeo[ix] < 80 && !sidebarSet.has(c.title))
    .map(({ c, ix }) => ({ c, sig: sigOf(c), ord: topSigs.slice(0, ix).filter((x) => x === sigOf(c)).length }));

  /* quale schermata porta fiche apribili (data-case): si misura, non si sa */
  for (const l of SIDEBAR) {
    await clickTitle(page, l, 460);
    if (await page.evaluate(() => document.querySelectorAll('[data-case]').length) > 0) { caseScreen = l; break; }
  }
  const openCaseHere = () => page.evaluate(() => {
    const c = [...document.querySelectorAll('[data-case]')].filter((x) => x.getAttribute('data-case'))[0];
    if (!c) return false;
    let n = c;
    for (let i = 0; i < 5 && n; i++) { const cs = getComputedStyle(n); if (cs.cursor === 'pointer' || n.onclick || n.tagName === 'BUTTON' || n.tagName === 'A') break; n = n.parentElement; }
    (n || c).click(); return true;
  }).catch(() => false);

  /* SCENARIO A · la storia */
  for (const k of cands) {
    if (backHistory) break;
    backTried++;
    await reboot();
    await clickTitle(page, home, 460);
    await clickTitle(page, B, 460);
    const atB = await snap(page);
    await clickTitle(page, Cs, 460);
    const atC = await snap(page);
    if (atC.th === atB.th) continue;                       /* B e C non distinti: scenario inutile */
    const ok = await clickSig(page, k.sig, k.ord); await harvest(page);
    if (!ok) continue;
    await page.waitForTimeout(700);
    const back = await snap(page).catch(() => null);
    if (back && back.th === atB.th) { backHistory = true; backLabel = (k.c.title || k.c.text || k.c.tag).replace(/\s+/g, ' ').slice(0, 28); }
  }

  /* SCENARIO B · il dettaglio */
  if (caseScreen) {
    const other = SIDEBAR.find((l) => l !== caseScreen) || B;
    for (const k of cands) {
      if (backDetail) break;
      backTried++;
      await reboot();
      await clickTitle(page, other, 460);
      await clickTitle(page, caseScreen, 520);
      const atList = await snap(page);
      if (!await openCaseHere()) break;
      await page.waitForTimeout(650);
      const det = await snap(page).catch(() => null);
      if (!det || det.th === atList.th) break;             /* la ficha non si apre: altro difetto, altro portone */
      const ok = await clickSig(page, k.sig, k.ord); await harvest(page);
      if (!ok) continue;
      await page.waitForTimeout(700);
      const back = await snap(page).catch(() => null);
      if (back && back.th === atList.th) { backDetail = true; if (!backLabel) backLabel = (k.c.title || k.c.text || k.c.tag).replace(/\s+/g, ' ').slice(0, 28); }
    }
  }
}
const backOk = backHistory && backDetail;

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
console.log(line(linkProofFailed.length === 0, 'CT5', 'Sampled <a href> links really open a tab', 0, linkProofFailed.length));
console.log(line(unreached.length === 0, 'NV1', 'Every sidebar item reaches a screen', 0, unreached.length || 'all ' + navRows.length));
console.log(line(collisions.length === 0, 'NV2', 'No two sidebar items land on the same screen', 0, collisions.length));
console.log(line(backHistory, 'NV3', 'In-app back returns to the previous screen', 'yes', backHistory ? `yes «${backLabel}»` : `NO (${backTried} topbar controls tried)`));
console.log(line(backDetail, 'NV3b', 'In-app back returns from a case detail to its list', 'yes', backDetail ? `yes, su ${caseScreen}` : 'NO'));
console.log(line(reloadOk, 'NV4', 'A page reload does not break the portal', 'yes', reloadOk ? `yes (${afterReload.chars} char, ${reloadClicks} clic)` : 'NO'));
console.log(line(emptyScreens.length === 0, 'NV5', 'No navigation leaves the screen empty', 0, emptyScreens.length));
console.log(line(errors.length === 0, 'NV6', 'No console error during the whole sweep', 0, errors.length));
console.log(line(failed.length === 0, 'NV7', 'No failed request during the whole sweep', 0, failed.length));
console.log('  ' + '─'.repeat(100));
console.log(`  SCHERMATE = ${screens.length} di ${SIDEBAR.length} nella barra (${NAV_ALL.length} [title] in pagina, il resto e testata e mappa)`);
console.log(`  CLICCABILI TROVATI = ${totalClickables} · PREMUTI E GIUDICATI = ${judged} · VIVI = ${alive} · MORTI = ${dead.length}`);
console.log(`  non giudicati: ${formCtl} controlli di modulo (semantica change) · ${selfNav} voce della schermata corrente · ${notJudged} senza cursore proprio (host delegato, celle inerti della mappa)`);
console.log(`  collegamenti con destinazione vera = ${linked} (cablati per costruzione) · aperti davvero per prova = ${linkProved}/${linkProved + linkProofFailed.length}`);
console.log(`  rumore del DOM a riposo = ${NOISE} mutazioni/600ms — con zero, UNA mutazione dopo il click e prova di vita`);
console.log(`  impronte rimisurate da pulito = ${rebase} · schermate non ripristinabili = ${drift} · firme non ripresentatesi = ${screens.reduce((a, x) => a + x.skipped, 0)}`);
console.log(`  idempotenti (fermi qui, vivi altrove) = ${idempotent.length} — un comando gia soddisfatto non e un comando morto`);
console.log(`  schede nuove = ${tabs} · download = ${downloads} · dialog nativi = ${dialogs}`);
console.log(`  console error = ${errors.length} · richieste fallite = ${failed.length}`);

console.log('\n  ' + 'SCHERMATA'.padEnd(28) + 'CHAR'.padStart(7) + 'CLIC'.padStart(6) + 'GIUD'.padStart(6) + 'VIVI'.padStart(6) + 'MORTI'.padStart(7));
for (const s of screens) {
  const d = s.dead.filter((c) => deadKeys.has(s.label + ' :: ' + sigOf(c))).length;
  console.log('  ' + s.label.padEnd(28) + String(s.chars).padStart(7) + String(s.clickables).padStart(6)
    + String(s.judged).padStart(6) + String(s.alive).padStart(6) + (d ? C.r(String(d).padStart(7)) : C.g('      0')));
}
/* Lo stesso comando della testata ripetuto su undici schermate e UN difetto
   visto undici volte, non undici difetti. Si raggruppa per firma e si dice
   dove e stato provato — il numero grezzo resta in CT1, per non ammorbidire
   il conteggio. */
const byControl = new Map();
for (const d of dead) {
  const k = d.sig;
  if (!byControl.has(k)) byControl.set(k, { c: d.c, screens: [], hits: 0, mode: d.mode });
  const g = byControl.get(k);
  g.hits++;
  if (!g.screens.includes(d.label)) g.screens.push(d.label);
}
if (dead.length) {
  console.log('\n  ' + C.r('BOTTONI MORTI') + ` — premuti in ogni contesto, e non e successo niente (${byControl.size} comandi distinti, ${dead.length} occorrenze):`);
  for (const [, g] of byControl) {
    const t = (g.c.text || g.c.title || '(senza testo)').replace(/\s+/g, ' ').slice(0, 40);
    const dove = (g.screens.length > 3 ? `${g.screens.length} schermate` : g.screens.join(' · '))
      + (g.hits > g.screens.length ? ` (${g.hits} occorrenze)` : '');
    console.log(`    <${g.c.tag}> «${t}»`.padEnd(56) + C.d(`${g.c.w}×${g.c.h} handler=${g.c.hasHandler ? 'si' : 'NO'} href=${g.c.href || 'NO'}`).padEnd(70) + '  ' + dove.slice(0, 60));
  }
}
if (collisions.length) { console.log('\n  ' + C.r('SCHERMATE GEMELLE') + ':'); for (const [a, b] of collisions) console.log(`    ${a}  ≡  ${b}`); }
if (emptyScreens.length) { console.log('\n  ' + C.r('SCHERMATE VUOTE') + ':'); for (const e of emptyScreens) console.log('    ' + e); }
if (linkProofFailed.length) {
  console.log('\n  ' + C.r('COLLEGAMENTI CHE NON SI SONO APERTI') + ':');
  for (const l of linkProofFailed.slice(0, 10)) console.log(`    ${l.screen.padEnd(26)} «${l.text}» -> ${l.href.slice(0, 60)}`);
}
if (blew.length) {
  console.log('\n  ' + C.r('PRESSIONI CHE HANNO FATTO URLARE LA CONSOLE') + ':');
  for (const b of blew.slice(0, 12)) console.log(`    ${b.screen.padEnd(26)} <${b.tag}> «${b.text}»`.padEnd(84) + C.d(b.msg.slice(0, 70)));
}
if (errors.length) { console.log('\n  ' + C.r('CONSOLE') + ':'); for (const e of errors.slice(0, 10)) console.log('    ' + e); }
if (failed.length) { console.log('\n  ' + C.r('RICHIESTE') + ':'); for (const f of failed.slice(0, 10)) console.log('    ' + f); }
console.log('');

if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({
  sidebar: SIDEBAR, noise: NOISE,
  screens: screens.map(({ sigs, ord, meta, aliveIdx, ...rest }) => rest),
  dead: dead.map((d) => ({ screen: d.label, sig: d.sig, mode: d.mode, ...d.c })),
  idempotent: idempotent.map((d) => ({ screen: d.label, sig: d.sig, mode: d.mode })),
  noHandler, blew, navRows, collisions, unreached, emptyScreens, linkProofFailed,
  back: { history: backHistory, detail: backDetail, label: backLabel, tried: backTried, caseScreen },
  reload: { ok: reloadOk, chars: afterReload.chars, clickables: reloadClicks },
  totals: { screens: screens.length, clickables: totalClickables, judged, alive, dead: dead.length, deadControls: byControl.size, idempotent: idempotent.length, formCtl, selfNav, notJudged, linked, linkProved, drift, rebase, skipped: screens.reduce((a, x) => a + x.skipped, 0), tabs, downloads, dialogs },
  errors, failed,
}, null, 1));

const FAIL = dead.length || noHandler.length || drift || enumSkew || linkProofFailed.length || unreached.length || collisions.length
  || !backOk || !reloadOk || emptyScreens.length || errors.length || failed.length;
process.exit(FAIL ? 1 : 0);
