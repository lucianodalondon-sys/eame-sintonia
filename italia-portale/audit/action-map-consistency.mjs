/* SINTONIA · ACTION_MAP_CONSISTENCY_GATE
   ---------------------------------------------------------------------------
   node audit/action-map-consistency.mjs [--cases 14] [--lang it] [--json out.json]

   Un caso vive in due posti: la SCHEDA sul radar e il DETTAGLIO dietro il clic.
   Sono la stessa cosa scritta due volte — e due scritture della stessa cosa
   divergono da sole, senza che nessuno lo decida.

       LA SCHEDA E IL DETTAGLIO NON POSSONO DIRE DUE COSE DELLO STESSO CASO.

   Questo portao non legge il sorgente. Apre il radar in un Chromium vero, LEGGE
   la scheda (coltura, regione, stato, prodotto nello slot `data-product`, riga
   dello stato del legame), CLICCA dentro, e rilegge le stesse affermazioni nel
   dettaglio. Poi confronta la MAPPA DELLE AZIONI stampata con l'`actionMap` del
   record: nessuna area inventata, nessuna area lasciata cadere.

       CIO CHE SI MISURA E IL PIXEL, NON LA STRINGA NEL FILE.

   Perche non si selezionano gli stili: il runtime compila `style=""` in classi
   generate, quindi un selettore per attributo di stile trova zero elementi
   senza dire che ne ha trovati zero. Si legge il valore COMPUTATO — e si usano
   gli appigli che il markup dichiara apposta: `data-case`, `data-product`, e lo
   `<span class="sc-interp">` in cui il renderer avvolge OGNI interpolazione.
   Ogni affermazione della schermata e uno di quegli span; il resto e cornice.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import { serve, open, openCase, clickTitle, C, line } from './lib/drive.mjs';
import { loadData } from './lib/harness.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const WANT = Number(arg('cases', 14));
const LANG = String(arg('lang', 'it')).toLowerCase() === 'en' ? 'en' : 'it';
const JSON_OUT = arg('json', null);
const PORT = 8949;

/* ── il modello, prima del browser ─────────────────────────────────────────
   Le sette aree che il motore pubblica. Non sono un'opinione: sono la lista
   chiusa che il record puo instradare, e le etichette vivono in V21. */
/* ══ LA MAPPA CANONICA E QUELLA DELLA RIUNIONE ════════════════════════════
   Questo portone leggeva la mappa a sette aree della scheda vecchia, e
   continuava a leggerla dopo che la decisione di prodotto l'aveva ritirata:
   apriva un cartello della riunione e poi cercava il markup di una schermata
   che non c'e piu, riportando dodici aree cadute che nessuno aveva perso.

       UN PORTONE PUNTATO A UNA SUPERFICIE RITIRATA MISURA UN ALTRO PRODOTTO.

   Le aree sono ora le CINQUE canoniche, prese dal modello, e la superficie e
   quella che il lettore apre davvero. */
const AREAS = (loadData().ITALY_APP_MODEL.AREE_CANONICHE || []).slice();
const STATUSES = ['ACT_NOW', 'PREPARE_NOW', 'FUTURE_PREPARATION', 'TO_VALIDATE'];
/* Gli stati che una riga della mappa canonica puo dichiarare. */
const STATI_AZIONE = ['ACTION_STATE_ACT', 'ACTION_STATE_PREPARE', 'ACTION_STATE_VALIDATE',
  'ACTION_STATE_WATCH', 'ACTION_STATE_NO_ACTION'];

const DATA = loadData();
const AM = DATA.ITALY_APP_MODEL;
const OPP = AM.collections.opportunities.records;
const byId = {}; OPP.forEach((o) => { byId[o.id] = o; });

const I18N = (DATA.SINTONIA_I18N || {})[LANG] || {};
const V21 = I18N.V21 || {};
const PSTATE = I18N.PSTATE || {};
const AREAMODE = I18N.AREAMODE || {};
const areaLabel = (a) => V21[a] || String(a).replace(/_/g, ' ');
const statusLabel = (s) => V21[s] || String(s).replace(/_/g, ' ');
const STATUS_LABELS = STATUSES.map(statusLabel);
const PSTATE_LABELS = Object.values(PSTATE);
/* L'etichetta di area e la CHIAVE al contrario: il portao deve poter risalire
   dal testo sullo schermo all'area del modello, altrimenti «PORTAFOGLIO» sullo
   schermo e `PORTFOLIO` nel record sarebbero due mondi che non si toccano. */
const AREA_BY_LABEL = {}; AREAS.forEach((a) => { AREA_BY_LABEL[a] = a; });
/* Il modo che lo STATO DEL CASO implica. Il template lo deriva dallo stato
   della finestra canonica — che e nullo su 37 record su 37 — quindi qui si
   scrive l'unica lettura che il lettore puo fare: uno schermo che grida AGIRE
   ORA non puo etichettare le sue aree «da monitorare». */
/* Quattro stati, quattro modi. Il quarto — VALIDATE — e nato quando la mappa
   ha smesso di dire «da monitorare» a un caso DA VALIDARE: chi lo legge deve
   sapere che il suo compito e validare, non guardare. */
const modeForStatus = (s) => AREAMODE[s === 'ACT_NOW' ? 'LOOK' : s === 'PREPARE_NOW' ? 'PREPARE'
  : s === 'TO_VALIDATE' ? 'VALIDATE' : 'MONITOR'] || '';

/* ── campione: ogni stato, e le due situazioni di prodotto ──────────────────
   «Almeno un legame VERIFIED_LABEL_MATCH» contro «solo LABEL_CHECK_NEEDED» non
   e un dettaglio del catalogo: e la differenza fra una scheda che promette e
   una che aspetta. Misurato in questo pacchetto: 12 record verificati, 25 in
   attesa di lettura — e nessuno dei due gruppi copre tutti e quattro gli stati,
   quindi la copertura si costruisce a coppie, non per stato. */
const verifiedOf = (o) => (o.productLinks || []).some((l) => l.strength === 'VERIFIED_LABEL_MATCH');
const pick = [];
const take = (fn) => { const hit = OPP.find((o) => !pick.includes(o.id) && fn(o)); if (hit) pick.push(hit.id); };
for (const st of STATUSES) { take((o) => o.status === st && verifiedOf(o)); take((o) => o.status === st && !verifiedOf(o)); }
for (const st of STATUSES) take((o) => o.status === st);
/* le sette aree devono essere state guardate almeno una volta, non solo le tre
   che quasi ogni record porta */
for (const ar of AREAS) take((o) => (o.actionMap || []).includes(ar));
for (const o of OPP) { if (pick.length >= WANT) break; if (!pick.includes(o.id)) pick.push(o.id); }
const SAMPLE = pick.slice(0, Math.max(WANT, 12));

/* ── il browser ────────────────────────────────────────────────────────────
   Il radar apre 12 schede su 37 e tiene le altre dietro un interruttore. Un
   portao che legge solo le prime 12 misura la finestra, non il pacchetto. */
const server = await serve(PORT);
const { browser, page, errors } = await open({ port: PORT });

/* La lingua e un interruttore nell'intestazione, non un parametro dell'URL. Il
   testo «EN» vive in uno <span> che NON porta il gestore: il gestore sta sopra,
   e il clic deve salire fino a dove il browser mostra il cursore — la stessa
   regola che `drive.mjs` applica a ogni clic di questo pacchetto. */
if (LANG === 'en') {
  const swapped = await page.evaluate(() => {
    const hit = [...document.querySelectorAll('span')].find((e) => (e.textContent || '').trim() === 'EN');
    if (!hit) return false;
    let n = hit;
    for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer' || n.onclick) { n.click(); return true; } n = n.parentElement; }
    hit.click(); return true;
  });
  await page.waitForTimeout(700);
  if (!swapped) { console.log('  ' + C.r('lingua EN non raggiunta — il portao si ferma invece di misurare la lingua sbagliata')); process.exit(1); }
}

const openRadar = async () => {
  await clickTitle(page, I18N.navRadar || 'Radar delle Opportunità');
  /* «VEDI TUTTE 37 OPPORTUNITÀ» — il testo lo costruisce il dizionario, non
     questo file: se l'etichetta cambia, il portao la segue. */
  await page.evaluate((prefix) => {
    const all = [...document.querySelectorAll('span,div')];
    const hit = all.filter((e) => {
      const t = (e.textContent || '').trim();
      return t.length < 60 && t.indexOf(prefix) === 0 && /\d/.test(t);
    });
    if (hit.length) hit[hit.length - 1].click();
  }, I18N.lblViewAllShort || 'VEDI TUTTE');
  await page.waitForTimeout(420);
};

/* ── ciò che la schermata AFFERMA ──────────────────────────────────────────
   Una sola funzione per la scheda e per il dettaglio: le due superfici devono
   essere lette con lo STESSO metro, o la differenza misurata sarebbe la
   differenza fra due lettori. */
const READ = `(root, V) => {
  const txt = (e) => ((e && e.textContent) || '').replace(/\\u00a0/g, ' ').trim();
  /* alpha === 1 separa la pillola dello STATO (fondo pieno, testo bianco) dalla
     pillola della CONVERGENZA (fondo allo 0.14, testo colorato). Le due possono
     portare le stesse due parole — «DA VALIDARE» — e senza questa misura il
     portao confonderebbe l'una con l'altra. */
  const opaque = (bg) => { const m = /rgba?\\(([^)]+)\\)/.exec(bg || ''); if (!m) return false;
    const p = m[1].split(',').map((s) => parseFloat(s)); return p.length < 4 || p[3] === 1; };
  const interps = [...root.querySelectorAll('.sc-interp')];
  /* ⚠️ «PASTIGLIA PIENA» NON E LA DEFINIZIONE DI STATO.
     Questa riga cercava lo stato fra le etichette che stanno su un fondo
     OPACO — un modo per trovare la pastiglia, non un requisito. Quando AGIRE
     ORA e diventato l'unico stato PIENO (e gli altri contorni, apposta, perche
     uno solo dei quattro chiama all'azione), la scheda ha smesso di dichiarare
     lo stato a questo portone su nove casi su quattordici. Nessuno di quei nove
     era un difetto: la parola era li, scritta, in tutti e due i posti.

         LO SLOT SI DICHIARA. IL PORTONE NON INDOVINA DAL RIEMPIMENTO. */
  const status = [...root.querySelectorAll('[data-status]')]
    .map((e) => (e.getAttribute('data-status') || '').trim()).filter(Boolean);
  const linkState = [];
  for (const s of interps) {
    const t = txt(s);
    if (V.pstateLabels.indexOf(t) >= 0) linkState.push(t);
  }
  /* COLTURA · REGIONE vive in una riga che si riconosce da sola: due span con
     un PUNTO in mezzo. Il punto non porta testo, e tondo, e misura pochi pixel.
     Questa e la stessa forma sulla scheda (3px) e nel dettaglio (4px), quindi
     una sola regola legge tutte e due. */
  const dots = [...root.querySelectorAll('div')].filter((d) => {
    if (d.children.length !== 3) return false;
    if (txt(d.children[1])) return false;
    const cs = getComputedStyle(d.children[1]);
    return cs.borderTopLeftRadius === '50%' && parseFloat(cs.width) > 0 && parseFloat(cs.width) <= 6;
  });
  const crop = dots.length ? txt(dots[0].children[0]) : '';
  const region = dots.length ? txt(dots[0].children[2]) : '';
  /* Lo slot del prodotto lo dichiara il markup: data-product. Cercare il nome
     nel testo della pagina casa «FORZA» dentro «FORZA DELL'EVIDENZA». */
  const products = [...root.querySelectorAll('[data-product]')]
    .map((e) => (e.getAttribute('data-product') || '').trim()).filter(Boolean);
  /* LA MAPPA DELLE AZIONI · si trova per la sua intestazione RESA, non per una
     stringa nel sorgente: il blocco e il padre del titolo, la griglia e il suo
     ultimo figlio, e ogni riquadro porta l'area e il modo. */
  /* ⚠️ LO SLOT SI DICHIARA, NON SI CONTA.
     Questa lettura andava a POSIZIONE — children[0] il nome, children[1] il
     modo — e il giorno in cui il riquadro ha guadagnato un ordinale accanto al
     nome ha cominciato a leggere «COMMERCIALE 2» come nome d'area: quarantadue
     aree inventate, quarantadue cadute, quarantadue fuori vocabolario, e non
     una sola era un difetto della schermata.

         UN PORTONE CHE LEGGE PER POSIZIONE MISURA IL LAYOUT, NON IL FATTO.

     Ora il markup dichiara data-area, data-area-name e data-area-mode, e
     questa funzione legge quelli. Se domani il riquadro cambia di nuovo forma,
     la misura resta la stessa. */
  let areas = [], modes = [], mapFound = false;
  const boxes = [...root.querySelectorAll('[data-action-dept]')];
  if (boxes.length) {
    mapFound = true;
    areas = boxes.map((c) => (c.getAttribute('data-action-dept') || '').trim());
    modes = boxes.map((c) => (c.getAttribute('data-action-state') || '').trim());
  }
  return { crop, region, dotRows: dots.length, status, linkState, products, areas, modes, mapFound,
    chars: (root.innerText || '').length };
}`;

const readCard = (id) => page.evaluate(([i, R, V]) => {
  const card = document.querySelector('[data-case="' + i + '"]');
  if (!card) return null;
  return Object.assign({ id: card.getAttribute('data-case') }, eval(R)(card, V));
}, [id, READ, { statusLabels: STATUS_LABELS, pstateLabels: PSTATE_LABELS, actionMapLabel: I18N.lblActionMap }]);

const readDetail = () => page.evaluate(([R, V]) => {
  /* Quando il dettaglio e aperto NESSUNA scheda resta nel DOM (misurato: 0),
     quindi la radice del dettaglio e il documento. Lo si verifica qui, invece
     di darlo per scontato: se un giorno le schede restassero, questa lettura
     mescolerebbe le due superfici e il portao lo direbbe. */
  const stillCards = document.querySelectorAll('[data-case]').length;
  const h1 = document.querySelector('h1');
  return Object.assign({ stillCards, headline: ((h1 && h1.textContent) || '').trim() },
    eval(R)(document.body, V));
}, [READ, { statusLabels: STATUS_LABELS, pstateLabels: PSTATE_LABELS, actionMapLabel: I18N.lblActionMap }]);

/* ── la passeggiata ───────────────────────────────────────────────────────── */
const rows = [];
for (const id of SAMPLE) {
  const o = byId[id];
  await openRadar();
  const card = await readCard(id);
  if (!card) { rows.push({ id, error: 'card not on the radar' }); continue; }
  const opened = await openCase(page, id, 620);
  if (!opened) { rows.push({ id, error: 'card did not open' }); continue; }
  const det = await readDetail();

  /* La mappa canonica instrada TUTTE le cinque aree su TUTTE le opportunita:
     mostrare un'area non significa inventarle un'azione — significa dire, con
     una parola, che quell'area non ha nulla di provato da fare adesso. */
  const modelAreas = AREAS.slice();
  const wantAreas = modelAreas.slice();
  const gotAreas = det.areas.slice();
  const setEq = (a, b) => a.length === b.length && a.slice().sort().join('|') === b.slice().sort().join('|');
  const invented = gotAreas.filter((x) => wantAreas.indexOf(x) < 0);
  const dropped = wantAreas.filter((x) => gotAreas.indexOf(x) < 0);
  /* Un'area sullo schermo che NON e una delle sette che il modello pubblica e
     una terza categoria: non e «inventata rispetto a questo record», e fuori
     dal vocabolario. Si conta a parte perche dice una cosa diversa. */
  const offVocab = gotAreas.filter((x) => !(x in AREA_BY_LABEL));
  const cardProduct = card.products[0] || '';
  const wantMode = modeForStatus(o.status);

  rows.push({
    id, status: o.status, verified: verifiedOf(o),
    card: { crop: card.crop, region: card.region, status: card.status, product: cardProduct, linkState: card.linkState, dotRows: card.dotRows },
    detail: { crop: det.crop, region: det.region, status: det.status, products: det.products, linkState: det.linkState, dotRows: det.dotRows, chars: det.chars },
    /* AC1 · il dettaglio aperto e il caso che la scheda diceva di essere — e la
       riga COLTURA · REGIONE e UNA sola su ciascuna superficie. Se fossero due,
       il portao non saprebbe quale ha letto, e una lettura ambigua non e una
       misura: e un'opinione con un numero davanti. */
    openedRight: det.stillCards === 0 && det.chars > 2500 && card.dotRows === 1 && det.dotRows === 1,
    /* AC2 · la coltura */
    cropCard: card.crop, cropDetail: det.crop,
    cropAgrees: !!card.crop && !!det.crop && card.crop === det.crop,
    /* AC3 · lo stato, nelle stesse parole, e le parole del modello */
    statusAgrees: card.status.length > 0 && det.status.length > 0
      && new Set(card.status).size === 1 && new Set(det.status).size === 1
      && card.status[0] === det.status[0],
    statusIsModel: card.status[0] === statusLabel(o.status) && det.status[0] === statusLabel(o.status),
    /* AC4 · il prodotto della scheda e nominato nel dettaglio */
    productNamed: !!cardProduct && det.products.indexOf(cardProduct) >= 0,
    /* AC5/6/7/8 · la mappa delle azioni */
    mapFound: det.mapFound, modelAreas, wantAreas, gotAreas,
    mapExact: det.mapFound && setEq(wantAreas, gotAreas),
    invented, dropped, offVocab,
    /* AC9 · lo stato del legame */
    linkAgrees: card.linkState.length === 0 ? null : det.linkState.indexOf(card.linkState[0]) >= 0,
    /* AC10 · la regione, dove entrambe parlano */
    regionAgrees: (!card.region || !det.region) ? null : card.region === det.region,
    /* AC11 · La scheda tace e il dettaglio parla. Trenta record su 37 non
       nominano una regione ma DICHIARANO fino a dove arriva il fatto
       (NATIONAL / EUROPEAN): il dettaglio ripiega sull'ampiezza e scrive
       «NAZIONALE», la scheda no — e disegna comunque il punto separatore,
       lasciando «Mais ·» sospeso su niente.

           TACERE DOVE L'ALTRA SUPERFICIE PARLA E ANCORA DISACCORDO. */
    regionSilent: !card.region && !!det.region,
    /* AC12 · il modo delle aree contro lo stato che LA STESSA schermata stampa */
    /* Ogni riquadro porta il PROPRIO stato — non quello del caso: cinque aree
       sullo stesso caso possono stare in cinque stati diversi, ed e questo che
       le rende una mappa invece di un'etichetta ripetuta. Si verifica che ogni
       stato sia uno di quelli pubblicati. */
    wantMode, gotModes: [...new Set(det.modes)],
    modeAgrees: det.mapFound ? det.modes.every((m) => STATI_AZIONE.indexOf(m) >= 0) : null,
  });
}

await browser.close(); server.close();

/* ── juizo ────────────────────────────────────────────────────────────────── */
const ok = rows.filter((r) => !r.error);
const broken = rows.filter((r) => r.error).length;
const stCovered = new Set(ok.map((r) => r.status));
const bothProducts = new Set(ok.map((r) => r.verified)).size;
const coverage = stCovered.size === 4 && bothProducts === 2;
const notOpened = ok.filter((r) => !r.openedRight).length;
const cropBad = ok.filter((r) => !r.cropAgrees).length;
const statusBad = ok.filter((r) => !r.statusAgrees || !r.statusIsModel).length;
const prodBad = ok.filter((r) => !r.productNamed).length;
const mapBad = ok.filter((r) => !r.mapExact).length;
const inventedN = ok.reduce((a, r) => a + r.invented.length, 0);
const droppedN = ok.reduce((a, r) => a + r.dropped.length, 0);
const offVocabN = ok.reduce((a, r) => a + r.offVocab.length, 0);
const linkBad = ok.filter((r) => r.linkAgrees === false).length;
const regionBad = ok.filter((r) => r.regionAgrees === false).length;
const regionMute = ok.filter((r) => r.regionSilent).length;
const modeBad = ok.filter((r) => r.modeAgrees === false).length;

console.log('\n  SINTONIA · ACTION_MAP_CONSISTENCY_GATE   ·   lang=' + LANG + '   ·   ' + ok.length + ' casi aperti su ' + OPP.length);
console.log('  ' + '─'.repeat(104));
console.log(line(coverage && broken === 0, 'AC0', 'Sample covers 4 statuses x both product situations', '4+2', stCovered.size + '+' + bothProducts + (broken ? ' (' + broken + ' unreadable)' : '')));
console.log(line(notOpened === 0, 'AC1', 'Every card opens its own, non-empty detail', 0, notOpened));
console.log(line(cropBad === 0, 'AC2', 'Card crop === detail crop', 0, cropBad));
console.log(line(statusBad === 0, 'AC3', 'Card status === detail status === model status', 0, statusBad));
console.log(line(prodBad === 0, 'AC4', 'Card product is named on the detail', 0, prodBad));
console.log(line(mapBad === 0, 'AC5', 'Action map === model actionMap, translated', 0, mapBad));
console.log(line(inventedN === 0, 'AC6', 'No area claimed that the record does not route to', 0, inventedN));
console.log(line(droppedN === 0, 'AC7', 'No area of the record dropped from the screen', 0, droppedN));
console.log(line(offVocabN === 0, 'AC8', 'Every area printed is one of the 5 canonical areas', 0, offVocabN));
console.log(line(linkBad === 0, 'AC9', 'Card link-state is a link-state the detail names', 0, linkBad));
console.log(line(regionBad === 0, 'AC10', 'Card region === detail region (where both speak)', 0, regionBad));
console.log(line(regionMute === 0, 'AC11', 'Card is not mute on geography while the detail names it', 0, regionMute));
console.log(line(modeBad === 0, 'AC12', 'Area mode agrees with the status the detail prints', 0, modeBad));
console.log(line(errors.length === 0, 'AC13', 'No console error during the sweep', 0, errors.length));
console.log('  ' + '─'.repeat(104));

/* ── a tabela por caso ────────────────────────────────────────────────────── */
console.log('\n  ' + 'CASE'.padEnd(20) + 'STATUS'.padEnd(20) + 'CROP  STAT  PROD  MAPA  LINK  REGI  MODO   AREE (schermo / modello)');
for (const r of rows) {
  if (r.error) { console.log('  ' + r.id.padEnd(20) + C.r(r.error)); continue; }
  const m = (b) => (b === null ? C.d(' n.a.') : b ? C.g('  yes') : C.r('   NO'));
  console.log('  ' + r.id.padEnd(20) + (r.status + (r.verified ? ' ·V' : ' ·C')).padEnd(20)
    + m(r.cropAgrees) + m(r.statusAgrees && r.statusIsModel) + m(r.productNamed) + m(r.mapExact)
    + m(r.linkAgrees) + m(r.regionSilent ? false : r.regionAgrees) + m(r.modeAgrees)
    + '   ' + r.gotAreas.length + '/' + r.wantAreas.length);
}

/* ── as discordâncias, escritas por extenso ───────────────────────────────── */
const say = [];
for (const r of ok) {
  if (!r.cropAgrees) say.push(`${r.id} · COLTURA: scheda «${r.cropCard}» · dettaglio «${r.cropDetail}»`);
  if (!r.statusAgrees) say.push(`${r.id} · STATO: scheda ${JSON.stringify(r.card.status)} · dettaglio ${JSON.stringify(r.detail.status)}`);
  else if (!r.statusIsModel) say.push(`${r.id} · STATO: schermo «${r.card.status[0]}» · modello «${statusLabel(r.status)}»`);
  if (!r.productNamed) say.push(`${r.id} · PRODOTTO: scheda «${r.card.product}» non compare fra ${JSON.stringify(r.detail.products)}`);
  if (r.invented.length) say.push(`${r.id} · AREA INVENTATA: ${JSON.stringify(r.invented)} · il record instrada ${JSON.stringify(r.modelAreas)}`);
  if (r.dropped.length) say.push(`${r.id} · AREA CADUTA: ${JSON.stringify(r.dropped)} · lo schermo mostra ${JSON.stringify(r.gotAreas)}`);
  if (r.linkAgrees === false) say.push(`${r.id} · LEGAME: scheda «${r.card.linkState[0]}» · dettaglio ${JSON.stringify([...new Set(r.detail.linkState)])}`);
  if (r.regionAgrees === false) say.push(`${r.id} · REGIONE: scheda «${r.card.region}» · dettaglio «${r.detail.region}»`);
  if (r.regionSilent) say.push(`${r.id} · REGIONE: la scheda non nomina nulla dopo «${r.card.crop} ·» · il dettaglio dice «${r.detail.region}»`);
  if (r.modeAgrees === false) say.push(`${r.id} · MODO: lo schermo stampa «${r.card.status[0]}» e etichetta le aree ${JSON.stringify(r.gotModes)} — atteso «${r.wantMode}»`);
}
if (say.length) {
  console.log('\n  ' + C.r('DISCORDANZE MISURATE') + ' (' + say.length + ')');
  for (const s of say) console.log('    · ' + s);
}

/* ── o resumo medido ──────────────────────────────────────────────────────── */
const areaShown = {}; ok.forEach((r) => r.gotAreas.forEach((a) => { areaShown[a] = (areaShown[a] || 0) + 1; }));
console.log('\n  CASI LETTI = ' + ok.length + ' · STATI COPERTI = ' + [...stCovered].join(', '));
console.log('  CON LEGAME VERIFICATO = ' + ok.filter((r) => r.verified).length + ' · SOLO DA VALIDARE = ' + ok.filter((r) => !r.verified).length);
console.log('  AREE SULLO SCHERMO = ' + ok.reduce((a, r) => a + r.gotAreas.length, 0) + ' · AREE NEL MODELLO = ' + ok.reduce((a, r) => a + r.wantAreas.length, 0)
  + ' · INVENTATE = ' + inventedN + ' · CADUTE = ' + droppedN + ' · FUORI VOCABOLARIO = ' + offVocabN);
console.log('  AREE VISTE ALMENO UNA VOLTA = ' + Object.keys(areaShown).length + '/' + AREAS.length + ' · ' + Object.keys(areaShown).sort().join(' · '));
console.log('  MODI STAMPATI = ' + JSON.stringify([...new Set([].concat(...ok.map((r) => r.gotModes)))]));

if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ lang: LANG, sample: SAMPLE, rows, disagreements: say }, null, 1));

const FAIL = !coverage || broken || notOpened || cropBad || statusBad || prodBad || mapBad
  || inventedN || droppedN || offVocabN || linkBad || regionBad || regionMute || modeBad || errors.length;
process.exit(FAIL ? 1 : 0);
