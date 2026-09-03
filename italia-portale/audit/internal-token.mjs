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
   ogni schermata della barra laterale NELLE DUE LINGUE, scende in cinque
   sotto-schermate e apre almeno otto schede di opportunità con un clic vero,
   poi legge i NODI DI TESTO che sono rimasti sullo schermo.

   ── LE DUE CLASSI, CHE NON SI GIUDICANO ALLO STESSO MODO ───────────────────
   Un id NON è sempre un difetto. «Alisma plantago-aquatica · rice · IT-RES-001»
   mostra un id COME id, accanto al nome umano che lo spiega: è una citazione,
   ed è legittima. «Scadenza normativa · RFF_FOLPET · Apri» mostra l'id AL POSTO
   del nome: la stessa riga, due voci più su, scrive «FOLPAN GOLD». Lo stesso
   pixel, la stessa colonna, e in un caso c'è un prodotto e nell'altro un
   codice interno.

   Come si distingue, misurando invece di indovinare: il runtime marca ogni
   elemento con `data-dc-tpl`, l'identità del NODO DI TEMPLATE che l'ha
   generato. Tutte le righe di una lista `sc-for` condividono lo stesso tpl per
   la stessa colonna. Quindi si chiede allo slot chi sono i suoi PARI:

     · se almeno un pari dello stesso slot porta testo umano  → il token STA
       AL POSTO di un'etichetta                                 → REPROVA
     · se ogni pari dello stesso slot è a sua volta un codice → è una COLONNA
       di id, mostrata come tale                                → si riporta
     · se lo slot è unico e non ha pari, si guarda la riga: se accanto c'è già
       un nome umano non si accusa nessuno. UN PORTONE CHE GRIDA AL LUPO
       INSEGNA A IGNORARLO.

   ── LA TRAPPOLA DEL text-transform ─────────────────────────────────────────
   innerText restituisce il testo TRASFORMATO: «finestre aperte» con
   text-transform:uppercase torna «FINESTRE APERTE», e una regola sulle
   maiuscole accuserebbe italiano corretto. Per questo si esige il TRATTINO
   BASSO, oppure una forma di id che il MODELLO stesso dichiara — mai la sola
   maiuscola. La prosa normale non contiene trattini bassi.

   ── LE FORME DI ID NON SI INDOVINANO: SI LEGGONO DAL MODELLO ───────────────
   L'harness costruisce ITALY_APP_MODEL e questo portone ne estrae gli 8.577 id
   reali e i loro prefissi (IT-PRD-, IT-WIN-, IT-RES-, IT-CAN-, OPP_, SRC_,
   RFF_, AI_, XCR_ …). Un token è un id perché il modello dice che lo è, non
   perché somiglia a uno.
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
   promessa quando è occupata, emette 'error' e uccide il processo — e un
   portone che muore con EADDRINUSE non ha misurato niente. */
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
   8.577 id reali e i prefissi che li generano. `FIELD_` esce dalla tavola dei
   prefissi di proposito: è anche il prefisso di FIELD_SIGNAL, che è
   VOCABOLARIO e non un id, e un prefisso ambiguo declasserebbe un difetto a
   nota. Per quella famiglia decide l'appartenenza esatta all'insieme. */
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

/* ── 2 · IL LETTORE DI SCHERMO ──────────────────────────────────────────────
   Si cammina sui NODI DI TESTO, non su innerText della pagina: solo così si sa
   in QUALE elemento vive il token, e quindi quali sono i suoi pari.
   Il testo si legge come lo legge chi guarda — con text-transform applicato —
   ma si conserva anche il grezzo, per poter dire se la maiuscola era scritta
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

    for (const tok of [...new Set(ms)]) {
      seen.push({
        token: tok,
        viaTransform: !raw.includes(tok),          /* maiuscola dipinta dal CSS, non scritta */
        own: raw.trim().replace(/\\s+/g, ' ').slice(0, 160),
        tpl,
        slotText: slotText.slice(0, 160),
        standalone: slotText === tok,
        peers: peers.slice(0, 40),
        peerCount: peers.length,
        row: rowText.slice(0, 240),
        font: Math.round(parseFloat(cs.fontSize) || 0),
      });
    }
  }
  return seen;
}`;

/* Candidati: una corsa di 2+ parole maiuscole unite da trattino basso, oppure
   la stessa forma unita da trattino (che vale SOLO se il modello la riconosce
   come id — «METALAXYL-M» è una sostanza attiva, non un codice). */
const CAND = '\\b[A-Z][A-Z0-9]*(?:[_-][A-Z0-9]+)+\\b';

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
   lì il cursore è una promessa. */
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
   riga larga del corpo. Si registra il nome della schermata di partenza perché
   il titolo cambia con la lingua e il confronto dev'essere fra le stesse due. */
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
  if (lang === 'en' && await setLang('en')) langsProven++;
  else if (lang === 'it') langsProven++;

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
   Prima si scartano i candidati che non sono vocabolario: una forma con
   trattino sopravvive solo se il modello la riconosce. Poi si separa CHE COSA
   è il token (id o parola del motore) da DOVE sta (al posto di un'etichetta,
   in una colonna di id, dentro la prosa). */
const isHuman = (t) => t.length > 1 && t.length < 220
  && /[A-Za-zÀ-ÿ]{3}/.test(t)
  && !new RegExp('^' + CAND + '$').test(t.trim());

const kept = [];
for (const f of findings) {
  const hasUnderscore = f.token.includes('_');
  if (!hasUnderscore && !isIdShaped(f.token)) continue;   /* METALAXYL-M e simili: non è un codice */
  f.kind = isIdShaped(f.token) ? 'ID' : 'VOCAB';
  f.known = MODEL_IDS.has(f.token);

  const humanPeers = (f.peers || []).filter((p) => p !== f.token && isHuman(p));
  if (!f.standalone) f.place = 'PROSE';                    /* citato dentro una frase */
  else if (humanPeers.length) { f.place = 'STANDS_IN'; f.proof = humanPeers.slice(0, 3); }
  else if (f.peerCount >= 2) f.place = 'ID_COLUMN';        /* ogni pari è un codice: è una colonna di id */
  else {
    /* Slot senza pari: non c'è prova strutturale. Si accusa solo se nella riga
       non c'è NESSUN altro nome umano — cioè se il codice è l'unica cosa che
       nomina la voce. Nel dubbio, non si accusa. */
    const rest = (f.row || '').split(f.token).join(' ').trim();
    f.place = isHuman(rest) ? 'WITH_LABEL' : 'STANDS_IN';
    if (f.place === 'STANDS_IN') f.proof = ['slot unico, riga senza nome umano'];
  }
  kept.push(f);
}

/* Si raggruppa per token+schermata: lo stesso RFF_FOLPET su it e en è lo stesso
   difetto visto due volte, ma le due lingue si contano perché una traduzione
   può ripararne una sola. */
const key = (f) => [f.kind, f.place, f.token, f.screen, f.lang].join('|');
const uniq = [...new Map(kept.map((f) => [key(f), f])).values()];

const vocabStand = uniq.filter((f) => f.kind === 'VOCAB' && f.place === 'STANDS_IN');
const vocabProse = uniq.filter((f) => f.kind === 'VOCAB' && f.place === 'PROSE');
const vocabOther = uniq.filter((f) => f.kind === 'VOCAB' && f.place !== 'STANDS_IN' && f.place !== 'PROSE');
const idStand = uniq.filter((f) => f.kind === 'ID' && f.place === 'STANDS_IN');
const idProse = uniq.filter((f) => f.kind === 'ID' && f.place === 'PROSE');
const idShown = uniq.filter((f) => f.kind === 'ID' && (f.place === 'ID_COLUMN' || f.place === 'WITH_LABEL'));
const painted = uniq.filter((f) => f.viaTransform);

const tokensOf = (a) => [...new Set(a.map((f) => f.token))];
const langsSeen = [...new Set(visited.map((v) => v.lang))];

console.log('\n  SINTONIA · INTERNAL_TOKEN_AUDIT');
console.log('  ' + '─'.repeat(100));
console.log(line(langsProven === 2 && langsSeen.length === 2, 'IT0', 'Both languages actually rendered (IT + EN)', 2, langsSeen.length));
console.log(line(vocabStand.length === 0, 'IT1', 'No engine word standing in for a human label', 0, vocabStand.length));
console.log(line(vocabProse.length === 0, 'IT2', 'No engine word inside the human prose', 0, vocabProse.length));
console.log(line(vocabOther.length === 0, 'IT3', 'No engine word anywhere else on screen', 0, vocabOther.length));
console.log(line(idStand.length === 0, 'IT4', 'No internal id standing in for a human label', 0, idStand.length));
console.log(line(idProse.length === 0, 'IT5', 'No internal id dropped inside a sentence', 0, idProse.length));
console.log(line(true, 'IT6', 'Ids shown AS ids (legitimate — reported only)', '–', idShown.length));
console.log(line(errors.length === 0, 'IT7', 'No console error during the whole sweep', 0, errors.length));
console.log('  ' + '─'.repeat(100));
console.log(`  SCHERMATE LETTE = ${visited.length} (${visited.filter((v) => v.lang === 'it').length} it · ${visited.filter((v) => v.lang === 'en').length} en) · CARATTERI = ${visited.reduce((a, v) => a + v.chars, 0)}`);
console.log(`  ID DEL MODELLO CONFRONTATI = ${MODEL_IDS.size} · PREFISSI = ${ID_PREFIXES.length}`);
console.log(`  OCCORRENZE GREZZE = ${findings.length} · TOKEN VERI = ${kept.length} · CASI DISTINTI = ${uniq.length}`);
console.log(`  MAIUSCOLE DIPINTE DAL CSS (non accusate come parola) = ${painted.length}`);

const show = (title, rows) => {
  if (!rows.length) return;
  console.log('\n  ' + title);
  for (const f of rows.sort((a, b) => a.token.localeCompare(b.token))) {
    console.log('   ' + C.r('•') + ' ' + f.token.padEnd(24) + C.d(f.lang) + '  ' + f.screen);
    console.log('     ' + C.d('slot ' + (f.tpl || '—') + ' · ' + f.place + (f.known ? ' · id reale del modello' : '')));
    console.log('     ' + C.d('riga: ') + f.row.slice(0, 150));
    if (f.proof) console.log('     ' + C.d('pari umani nello stesso slot: ') + f.proof.map((p) => '«' + p.slice(0, 46) + '»').join(' '));
  }
};
show('PAROLE DEL MOTORE AL POSTO DI UN\'ETICHETTA', vocabStand);
show('PAROLE DEL MOTORE NELLA PROSA', vocabProse);
show('PAROLE DEL MOTORE, ALTRO', vocabOther);
show('ID AL POSTO DI UN NOME (difetto)', idStand);
show('ID DENTRO UNA FRASE (difetto)', idProse);

if (idShown.length) {
  console.log('\n  ' + C.y('ID MOSTRATI COME ID — legittimi, solo riportati'));
  const g = {};
  for (const f of idShown) { const k = f.screen + ' · ' + f.place; (g[k] = g[k] || []).push(f.token); }
  for (const k of Object.keys(g).sort()) console.log('   ' + C.d('·') + ' ' + k.padEnd(46) + tokensOf(g[k].map((t) => ({ token: t }))).slice(0, 6).join(' '));
}

if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({
  visited, modelIds: MODEL_IDS.size, prefixes: ID_PREFIXES,
  vocabStand, vocabProse, vocabOther, idStand, idProse, idShown, painted, errors,
}, null, 1));

const FAIL = (langsProven !== 2) || vocabStand.length || vocabProse.length || vocabOther.length
  || idStand.length || idProse.length || errors.length;
process.exit(FAIL ? 1 : 0);
