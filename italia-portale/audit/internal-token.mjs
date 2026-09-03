/* SINTONIA · INTERNAL_TOKEN_AUDIT
   ---------------------------------------------------------------------------
   node italia-portale/audit/internal-token.mjs [--json out.json] [--cases 8]

   Il motore parla in maiuscole con il trattino basso: VERIFIED_LABEL_MATCH,
   FUTURE_PREPARATION, RFF_FOLPET, IT-CAN-43822F56F7. È il suo diritto — è la
   sua lingua. Ma quella lingua non è italiana e non è inglese, e chi legge il
   portale non l'ha mai imparata.

       IL VOCABOLARIO DEL MOTORE NON È UNA TRADUZIONE MANCANTE.
       È UNA PAROLA CHE NON ESISTE IN NESSUNA DELLE DUE LINGUE.

   Questo portone non cerca stringhe nel sorgente: apre un Chromium, percorre
   ogni schermata della barra laterale NELLE DUE LINGUE, scende nelle
   sotto-schermate premendo la prima riga del corpo, e apre almeno otto schede
   di opportunità con un clic vero — poi legge i NODI DI TESTO che sono rimasti
   sullo schermo.

   ── LE DUE CLASSI, CHE NON SI GIUDICANO ALLO STESSO MODO ───────────────────
   Un id NON è sempre un difetto. «Amaranto comune · soybean · Amaranthaceae ·
   first case — · IT-RES-004» mostra un id COME id, in coda al nome umano che
   lo spiega: è una citazione, ed è legittima. «Scadenza normativa ·
   RFF_FOLPET · Apri» mostra l'id AL POSTO del nome: nella stessa lista, dodici
   righe più su, la stessa colonna scrive «FOLPAN GOLD». Lo stesso pixel, la
   stessa colonna, e in un caso c'è un prodotto e nell'altro un codice interno.

   Come si distingue, misurando invece di indovinare: il runtime marca ogni
   elemento con `data-dc-tpl`, l'identità del NODO DI TEMPLATE che l'ha
   generato. Tutte le righe di una lista `sc-for` condividono lo stesso tpl per
   la stessa colonna. Quindi si chiede allo slot chi sono i suoi PARI:

     · se accanto al codice, dentro il suo stesso slot, resta già un nome umano
       → BESIDE, citazione legittima                            → si riporta
     · se il codice è solo nello slot e almeno un PARI dello stesso slot porta
       testo umano → STANDS_IN, sta al posto dell'etichetta      → REPROVA
     · se il codice è solo nello slot e OGNI pari è a sua volta un codice
       → ALONE, è una colonna di codici mostrata come tale       → si riporta
     · se lo slot è unico e non ha pari, decide la riga intorno. NEL DUBBIO NON
       SI ACCUSA: UN PORTONE CHE GRIDA AL LUPO INSEGNA A IGNORARLO.

   ── LA TRAPPOLA DEL text-transform ─────────────────────────────────────────
   innerText restituisce il testo TRASFORMATO: «finestre aperte» con
   text-transform:uppercase torna «FINESTRE APERTE», e una regola sulle
   maiuscole accuserebbe italiano corretto. Per questo si esige il TRATTINO
   BASSO, oppure una forma di id che il MODELLO stesso dichiara — mai la sola
   maiuscola. La prosa normale non contiene trattini bassi. Quante volte la
   maiuscola era dipinta dal CSS invece che scritta si conta e si stampa: se un
   giorno non fosse più zero, chi legge il verdetto lo saprebbe.

   ── LE FORME DI ID NON SI INDOVINANO: SI LEGGONO DAL MODELLO ───────────────
   L'harness costruisce ITALY_APP_MODEL e questo portone ne estrae gli id reali
   e i loro prefissi (IT-PRD-, IT-WIN-, IT-RES-, IT-CAN-, IT-MKT-, OPP_, SRC_,
   RFF_, AI_, XCR_ …). Un token è un id perché il modello dice che lo è, non
   perché somiglia a uno — e così «METALAXYL-M», «TAU-FLUVALINATE», «NUTS-2»,
   «FT-NIR» restano quello che sono: chimica, statistica, metodo analitico.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import net from 'node:net';
import { serve, open, nav, clickTitle, openCase, caseIds, fingerprint, C, line } from './lib/drive.mjs';
import { loadData } from './lib/harness.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const JSON_OUT = arg('json', null);
const WANT_CASES = Number(arg('cases', 8));

/* La porta si tasta prima di consegnarla a serve(): serve() non rifiuta la
   promessa quando è occupata — emette 'error' e uccide il processo — e un
   portone che muore con EADDRINUSE non ha misurato niente, ha solo stampato
   uno stack trace al posto di un verdetto. */
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

/* ── 1 · IL VOCABOLARIO DEGLI ID, LETTO DAL MODELLO ─────────────────────────
   Gli id reali del pacchetto e i prefissi che li generano. `FIELD_` esce dalla
   tavola di proposito: è anche il prefisso di FIELD_SIGNAL, che è VOCABOLARIO
   e non un id, e un prefisso ambiguo declasserebbe un difetto a nota. Per
   quella famiglia decide l'appartenenza esatta all'insieme. */
const AM = loadData().ITALY_APP_MODEL;
const MODEL_IDS = new Set();
const PREFIX = {};
for (const col of Object.values(AM.collections || {})) {
  for (const r of (col && col.records) || []) {
    for (const f of ['id', 'windowId', 'sourceId', 'recordId', 'caseId', 'productId']) {
      const v = r && r[f];
      if (typeof v !== 'string' || !/^[A-Z][A-Z0-9]*[-_]/.test(v)) continue;
      MODEL_IDS.add(v);
      const m = v.match(/^([A-Z]{2,6}-[A-Z]{2,5}-|[A-Z]{1,7}[_-])/);
      if (m) PREFIX[m[1]] = (PREFIX[m[1]] || 0) + 1;
    }
  }
}
delete PREFIX.FIELD_;
const ID_PREFIXES = Object.keys(PREFIX).sort((a, b) => b.length - a.length);
const isIdShaped = (t) => MODEL_IDS.has(t) || ID_PREFIXES.some((p) => t.startsWith(p) && t.length > p.length);

/* Candidati: una corsa di 2+ parole maiuscole unite da trattino basso, oppure
   la stessa forma unita da trattino — che però vale SOLO se il modello la
   riconosce come id, perché «KLARTAN 20 EW» e «METALAXYL-M» sono nomi, non
   codici. */
const CAND = '\\b[A-Z][A-Z0-9]*(?:[_-][A-Z0-9]+)+\\b';

/* ── 2 · IL LETTORE DI SCHERMO ──────────────────────────────────────────────
   Si cammina sui NODI DI TESTO, non sull'innerText della pagina: solo così si
   sa in QUALE elemento vive il token, e quindi quali sono i suoi pari. Il testo
   si legge come lo legge chi guarda — con text-transform applicato — ma si
   conserva anche il grezzo, per poter dire se la maiuscola era scritta
   dall'autore o dipinta dal CSS. */
const SCAN = `(CAND) => {
  const RE = new RegExp(CAND, 'g');
  const seen = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const raw = n.nodeValue || '';
    if (!raw.trim()) continue;
    const el = n.parentElement;
    if (!el || el.tagName === 'SCRIPT' || el.tagName === 'STYLE' || el.tagName === 'TITLE') continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;          /* nel DOM ma non sullo schermo */
    const shown = cs.textTransform === 'uppercase' ? raw.toUpperCase() : raw;
    const ms = shown.match(RE);
    if (!ms) continue;

    /* lo SLOT: il nodo di template che ha generato questo pezzo di schermo */
    let slot = el, hops = 0;
    while (slot && !slot.hasAttribute('data-dc-tpl') && hops < 8) { slot = slot.parentElement; hops++; }
    if (!slot) slot = el;
    const tpl = slot.getAttribute ? (slot.getAttribute('data-dc-tpl') || '') : '';
    const slotText = (slot.innerText || slot.textContent || '').trim().replace(/\\s+/g, ' ');

    /* i PARI: ogni altro elemento nato dallo stesso nodo di template */
    let peers = [];
    if (tpl) {
      peers = [...document.querySelectorAll('[data-dc-tpl="' + tpl + '"]')]
        .map((p) => (p.innerText || '').trim().replace(/\\s+/g, ' '))
        .filter((t) => t.length);
    }

    /* la RIGA: il primo antenato che porta compagnia al token */
    let row = el, rh = 0;
    while (row.parentElement && rh < 6
      && (row.innerText || '').trim().replace(/\\s+/g, ' ').length < shown.trim().length + 14) { row = row.parentElement; rh++; }
    const rowText = (row.innerText || '').trim().replace(/\\s+/g, ' ');

    const flat = shown.replace(/\\s+/g, ' ');
    for (const tok of [...new Set(ms)]) {
      /* La citazione si ritaglia INTORNO al token, non dall'inizio del nodo:
         una nota metodologica lunga metteva a referto il titolo della
         schermata al posto della frase che contiene la parola accusata, e una
         prova che non mostra il fatto non è una prova. */
      const at = flat.indexOf(tok);
      seen.push({
        token: tok,
        viaTransform: !raw.includes(tok),          /* maiuscola dipinta dal CSS, non scritta */
        quote: flat.slice(Math.max(0, at - 66), at + tok.length + 66).trim(),
        tpl,
        slotText: slotText.slice(0, 200),
        peers: peers.slice(0, 40),
        peerCount: peers.length,
        row: rowText.slice(0, 240),
      });
    }
  }
  return seen;
}`;

/* ── 3 · LA PASSEGGIATA ─────────────────────────────────────────────────── */
const { server, port } = await bind(8952);
const { browser, page, errors } = await open({ port });

const findings = [];
const visited = [];
const scan = async (screen, lang) => {
  const hits = await page.evaluate(eval('(' + SCAN + ')'), CAND);
  const fp = await fingerprint(page);
  visited.push({ screen, lang, chars: fp.chars, hits: hits.length });
  for (const h of hits) findings.push({ screen, lang, ...h });
};

/* Il commutatore di lingua è una coppia di <span> con scritto IT / EN. Il testo
   vive nello span, il gestore sull'antenato: si sale finché il browser dice che
   lì il cursore è una promessa. E non ci si fida del clic: si CONTROLLA
   <html lang>, perché una lingua che non è cambiata farebbe leggere due volte
   la stessa schermata e chiamarlo doppio. */
const setLang = async (code) => {
  const ok = await page.evaluate((want) => {
    const e = [...document.querySelectorAll('span')].find((x) => (x.textContent || '').trim() === want && !x.children.length);
    if (!e) return false;
    let n = e;
    for (let i = 0; i < 5 && n; i++) { if (getComputedStyle(n).cursor === 'pointer' || n.onclick) { n.click(); return true; } n = n.parentElement; }
    e.click(); return true;
  }, code.toUpperCase());
  await page.waitForTimeout(700);
  return ok && (await page.evaluate(() => document.documentElement.lang)) === code;
};

/* Le sotto-schermate non stanno nella barra: ci si arriva premendo la prima
   riga larga del corpo (a destra della barra, sotto l'intestazione). */
const DRILL = [0, 3, 5, 6, 7, 9];       /* Radar · Polso · Concorrenza · Scienza · Portafoglio · Fonti */
const drillFirstRow = async () => page.evaluate(() => {
  const cand = [...document.querySelectorAll('*')].filter((e) => {
    const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const r = e.getBoundingClientRect();
    return cs.cursor === 'pointer' && r.width > 200 && r.height > 24 && r.top > 200 && r.left > 240;
  });
  if (!cand.length) return null;
  cand[0].click();
  return (cand[0].textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60);
});

let langsProven = 0;
for (const lang of ['it', 'en']) {
  if (lang === 'it' || await setLang('en')) langsProven++;

  const titles = (await nav(page)).slice(0, 11);
  for (let i = 0; i < titles.length; i++) {
    await clickTitle(page, titles[i], 620);
    await scan(titles[i], lang);
    if (!DRILL.includes(i)) continue;
    const label = await drillFirstRow();
    await page.waitForTimeout(620);
    if (label) await scan(titles[i] + ' → ' + label.slice(0, 28), lang);
  }

  /* Le schede: si aprono con un clic vero sulla carta del radar, una per una,
     tornando al radar prima di ognuna perché il DOM cambia sotto i piedi. */
  await clickTitle(page, titles[0], 620);
  const ids = await caseIds(page);
  for (const id of ids.slice(0, WANT_CASES)) {
    await clickTitle(page, titles[0], 520);
    if (!(await openCase(page, id, 640))) continue;
    await scan('case ' + id, lang);
  }
}

await browser.close(); server.close();

/* ── 4 · IL GIUDIZIO ────────────────────────────────────────────────────────
   Prima si scarta ciò che non è vocabolario del motore: una forma con TRATTINO
   sopravvive solo se il modello la dichiara id.

   Poi si separano DUE domande che non vanno mai confuse:
     CHE COSA è il token   → ID (il modello lo dichiara) o VOCAB (parola del motore)
     DOVE sta il token     → BESIDE / STANDS_IN / ALONE (vedi il capo di questo file)

   La prima versione di questo blocco chiedeva `slotText === token`, e con quella
   domanda «Amaranto comune · soybean · Amaranthaceae · first case — · IT-RES-004»
   diventava un difetto: l'id era in coda a una riga che lo spiega tutta, e
   veniva accusato come prosa. Misurava la punteggiatura, non la sostanza.

       LA DOMANDA NON È SE IL TOKEN È SOLO NEL SUO NODO.
       È SE, TOLTO IL TOKEN, RESTA UN NOME UMANO ACCANTO.

   Tolto il token (e ogni altro codice, e i separatori, e le cifre), se resta
   una parola vera allora il codice è CITATO accanto alla sua etichetta e non si
   accusa nessuno. Se non resta niente, il codice È l'etichetta, e allora
   decidono i pari dello slot. */
const CAND_RE = new RegExp(CAND, 'g');
const isHuman = (t) => {
  if (!t || t.length > 240) return false;
  const rest = t.replace(CAND_RE, ' ').replace(/[0-9·•|/\\_\-–—,.:;()\[\]«»"'×]+/g, ' ');
  return /[A-Za-zÀ-ÿ]{3}/.test(rest);
};

const kept = [];
const discarded = new Set();
for (const f of findings) {
  /* Il filtro si registra invece di essere silenzioso: chi legge il verdetto
     deve poter vedere che cosa è stato SCARTATO — «METALAXYL-M», «NUTS-2»,
     «FT-NIR» — e contestarlo.
     UN FILTRO CHE NON SI VEDE È UN FILTRO CHE NON SI DISCUTE. */
  if (!f.token.includes('_') && !isIdShaped(f.token)) { discarded.add(f.token); continue; }
  f.kind = isIdShaped(f.token) ? 'ID' : 'VOCAB';
  f.known = MODEL_IDS.has(f.token);

  if (isHuman(f.slotText.split(f.token).join(' '))) {
    f.place = 'BESIDE';                                    /* un nome lo accompagna già */
    f.proof = [f.slotText.split(f.token).join('␣').slice(0, 90)];
  } else {
    const humanPeers = (f.peers || []).filter((p) => p !== f.token && isHuman(p));
    if (humanPeers.length) { f.place = 'STANDS_IN'; f.proof = humanPeers.slice(0, 3); }
    else if (f.peerCount >= 2) f.place = 'ALONE';          /* ogni pari è un codice: colonna di codici */
    else {
      /* Slot unico, nessuna prova strutturale. Decide la riga intorno, e nel
         dubbio non si accusa. */
      const rest = (f.row || '').split(f.token).join(' ');
      f.place = isHuman(rest) ? 'BESIDE' : 'STANDS_IN';
      f.proof = [f.place === 'BESIDE' ? rest.trim().slice(0, 90) : 'slot unico, riga senza nome umano'];
    }
  }
  kept.push(f);
}

/* Lo stesso token, sullo stesso slot, nella stessa schermata e nella stessa
   lingua è UN caso. Le due lingue si contano separate perché una traduzione può
   ripararne una sola e lasciare l'altra rotta. */
const key = (f) => [f.kind, f.place, f.token, f.screen, f.lang].join('|');
const uniq = [...new Map(kept.map((f) => [key(f), f])).values()];

const vocabLabel = uniq.filter((f) => f.kind === 'VOCAB' && f.place !== 'BESIDE');
const vocabProse = uniq.filter((f) => f.kind === 'VOCAB' && f.place === 'BESIDE');
const idStand = uniq.filter((f) => f.kind === 'ID' && f.place === 'STANDS_IN');
const idShown = uniq.filter((f) => f.kind === 'ID' && f.place !== 'STANDS_IN');
const painted = uniq.filter((f) => f.viaTransform);

const itScreens = visited.filter((v) => v.lang === 'it').length;
const enScreens = visited.filter((v) => v.lang === 'en').length;
const itCases = visited.filter((v) => v.lang === 'it' && /^case /.test(v.screen)).length;
const enCases = visited.filter((v) => v.lang === 'en' && /^case /.test(v.screen)).length;
/* Un portone che smette di navigare misura zero e passa. La copertura è essa
   stessa un controllo: se la passeggiata si accorcia, il verdetto non vale. */
const covered = langsProven === 2 && itScreens >= 14 && enScreens >= 14
  && itCases >= WANT_CASES && enCases >= WANT_CASES;

console.log('\n  SINTONIA · INTERNAL_TOKEN_AUDIT');
console.log('  ' + '─'.repeat(100));
console.log(line(covered, 'IT0', 'Swept both languages, every screen, ' + WANT_CASES + '+ cases', 'ok', `it ${itScreens}/${itCases}c · en ${enScreens}/${enCases}c`));
console.log(line(vocabLabel.length === 0, 'IT1', 'No engine word standing in for a human label', 0, vocabLabel.length));
console.log(line(vocabProse.length === 0, 'IT2', 'No engine word inside the human prose', 0, vocabProse.length));
console.log(line(idStand.length === 0, 'IT3', 'No internal id standing in for a human label', 0, idStand.length));
console.log(line(true, 'IT4', 'Ids shown AS ids, beside a label (reported only)', '–', idShown.length));
console.log(line(errors.length === 0, 'IT5', 'No console error during the whole sweep', 0, errors.length));
console.log('  ' + '─'.repeat(100));
console.log(`  SCHERMATE LETTE = ${visited.length} (${itScreens} it · ${enScreens} en) · CARATTERI LETTI = ${visited.reduce((a, v) => a + v.chars, 0)}`);
console.log(`  ID DEL MODELLO CONFRONTATI = ${MODEL_IDS.size} · PREFISSI DERIVATI = ${ID_PREFIXES.length}`);
console.log(`  OCCORRENZE GREZZE = ${findings.length} · TOKEN VERI = ${kept.length} · CASI DISTINTI = ${uniq.length}`);
console.log(`  DI CUI: al posto di un'etichetta = ${vocabLabel.length + idStand.length} · nella prosa = ${vocabProse.length} · citati accanto a un nome = ${idShown.length}`);
console.log(`  MAIUSCOLE DIPINTE DAL text-transform (mai accusate come parola) = ${painted.length}`);
console.log(`  SCARTATI perché il modello non li dichiara codici = ${discarded.size}${discarded.size ? C.d(' · ' + [...discarded].slice(0, 8).join(' ')) : ''}`);

const show = (title, rows) => {
  if (!rows.length) return;
  console.log('\n  ' + C.r(title));
  for (const f of rows.sort((a, b) => (a.token + a.lang).localeCompare(b.token + b.lang))) {
    console.log('   ' + C.r('•') + ' ' + f.token.padEnd(24) + C.d('[' + f.lang + '] ') + f.screen);
    console.log('     ' + C.d('slot ' + (f.tpl || '—') + ' · ' + f.place + (f.known ? ' · id reale del modello' : '')));
    console.log('     ' + C.d('letto: ') + '…' + f.quote + '…');
    if (f.proof) console.log('     ' + C.d('prova: ') + f.proof.map((p) => '«' + p.slice(0, 44) + '»').join(' '));
  }
};
show('PAROLA DEL MOTORE AL POSTO DI UN\'ETICHETTA', vocabLabel);
show('PAROLA DEL MOTORE DENTRO LA PROSA', vocabProse);
show('ID AL POSTO DI UN NOME UMANO', idStand);

if (idShown.length) {
  console.log('\n  ' + C.y('ID MOSTRATI COME ID, ACCANTO A UN NOME — legittimi, solo riportati'));
  const g = {};
  for (const f of idShown) { const k = f.lang + ' · ' + f.screen; (g[k] = g[k] || []).push(f.token); }
  for (const k of Object.keys(g).sort()) {
    const toks = [...new Set(g[k])];
    console.log('   ' + C.d('·') + ' ' + k.slice(0, 50).padEnd(52) + toks.slice(0, 5).join(' ') + (toks.length > 5 ? C.d(` (+${toks.length - 5})`) : ''));
  }
}

if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({
  visited, modelIds: MODEL_IDS.size, prefixes: ID_PREFIXES, discarded: [...discarded],
  vocabLabel, vocabProse, idStand, idShown, painted, errors,
}, null, 1));

const FAIL = !covered || vocabLabel.length || vocabProse.length || idStand.length || errors.length;
process.exit(FAIL ? 1 : 0);
