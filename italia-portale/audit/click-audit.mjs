/* SINTONIA · FUNCTIONAL_CLICK_AUDIT — mille e venticinque, uno per uno
   ---------------------------------------------------------------------------
   node italia-portale/audit/click-audit.mjs --screen "Fonti" [--state f.json]
   node italia-portale/audit/click-audit.mjs --report --state f.json

   La passata precedente moriva per timeout a meta strada e chiamava
   «sospetti» centocinque controlli.

       «SOSPETTO» NON E UN VERDETTO. E UN LAVORO NON FINITO.

   Questo portone lavora a LOTTI — una schermata per volta — e PERSISTE il
   risultato su disco fra un lotto e l'altro, cosi nessuna morte per timeout
   perde cio che era gia stato giudicato.

   Sei classi, e ognuna esige una prova diversa:
     LIVE               il clic cambia rotta, stato, DOM o produce un file
     DISABLED_BY_RULE   non cambia nulla E la pagina dice perche
     DUPLICATE_CONTROL  porta esattamente dove porta un altro controllo vivo
     PLACEBO            non cambia nulla e nessuna regola lo spiega
     BROKEN             il clic lancia un errore o rompe la schermata
     UNREACHABLE        esiste nel DOM ma nessun clic puo raggiungerlo
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import { serve, open, clickTitle, nav, clickables, clickKey, keyOf, C, line } from './lib/drive.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const STATE = arg('state', '/tmp/sintonia-click-state.json');
const ONLY = arg('screen', null);
const REPORT = argv.includes('--report');
const PORT = Number(arg('port', 8974));

const load = () => { try { return JSON.parse(fs.readFileSync(STATE, 'utf8')); } catch { return { screens: {} }; } };
const save = (s) => fs.writeFileSync(STATE, JSON.stringify(s, null, 1));

/* ── il verdetto ──────────────────────────────────────────────────────────── */
if (REPORT) {
  const st = load();
  const all = Object.values(st.screens).flatMap((s) => s.controls || []);
  const t = {};
  all.forEach((c) => { t[c.verdict] = (t[c.verdict] || 0) + 1; });
  const order = ['LIVE', 'DISABLED_BY_RULE', 'DUPLICATE_CONTROL', 'PLACEBO', 'BROKEN', 'UNREACHABLE'];
  console.log('\n  SINTONIA · FUNCTIONAL_CLICK_AUDIT');
  console.log('  ' + '─'.repeat(96));
  console.log('  ' + 'SCHERMATA'.padEnd(30) + 'CONTROLLI'.padStart(10) + 'GIUDICATI'.padStart(11) + '  ' + order.map((o) => o.slice(0, 4)).join('  '));
  let tot = 0, judged = 0;
  for (const [name, s] of Object.entries(st.screens)) {
    const cs = s.controls || [];
    const per = order.map((o) => String(cs.filter((c) => c.verdict === o).length).padStart(4));
    tot += s.found || cs.length; judged += cs.length;
    console.log('  ' + name.slice(0, 29).padEnd(30) + String(s.found || cs.length).padStart(10) + String(cs.length).padStart(11) + '  ' + per.join('  '));
  }
  console.log('  ' + '─'.repeat(96));
  console.log(`  CLICKABLE = ${tot} · JUDGED = ${judged}`);
  for (const o of order) console.log(`  ${o.padEnd(20)} = ${t[o] || 0}`);
  const bad = all.filter((c) => ['PLACEBO', 'BROKEN', 'UNREACHABLE'].includes(c.verdict));
  console.log('\n  ' + (bad.length ? C.r('DA CHIUDERE: ' + bad.length) : C.g('nessun controllo morto, finto o irraggiungibile')));
  for (const b of bad.slice(0, 40)) console.log(`   ${C.r(b.verdict.padEnd(18))} ${b.screen} · <${b.tag}> "${(b.text || '').slice(0, 52)}"`);
  console.log('');
  console.log(line(judged === tot, 'FC1', 'Every clickable is judged', tot, judged));
  console.log(line(!(t.BROKEN || 0), 'FC2', 'No broken control', 0, t.BROKEN || 0));
  console.log(line(!(t.PLACEBO || 0), 'FC3', 'No placebo control', 0, t.PLACEBO || 0));
  console.log(line(!(t.UNREACHABLE || 0), 'FC4', 'No unreachable control', 0, t.UNREACHABLE || 0));
  process.exit((judged === tot && !(t.BROKEN || 0) && !(t.PLACEBO || 0) && !(t.UNREACHABLE || 0)) ? 0 : 1);
}

/* ── un lotto ─────────────────────────────────────────────────────────────── */
const server = await serve(PORT);
const { browser, page, errors } = await open({ port: PORT });
const labels = [...new Set(await nav(page))].filter((l) => !/^(Valle|Trentino|Friuli|Piemonte|Lombardia|Veneto|Liguria|Emilia|Toscana|Marche|Umbria|Lazio|Abruzzo|Molise|Campania|Puglia|Basilicata|Calabria|Sicilia|Sardegna)/.test(l));
const targets = ONLY ? labels.filter((l) => l === ONLY) : labels;
if (!targets.length) { console.log('nessuna schermata: ' + ONLY + '\ndisponibili: ' + labels.join(' | ')); await browser.close(); server.close(); process.exit(2); }

/* Come si descrive un controllo in modo che sopravviva a un re-render: il
   renderer rigenera i nodi, quindi un handle non vale. Vale la POSIZIONE nella
   lista dei clicabili piu il testo. */
/* O indice vem de drive.mjs, e o clique tambem: um criterio so. */
const snapshot = async () => {
  /* l'ordinale fra omonimi completa l'identita: due «ESPLORA SEGNALE →» sono
     due controlli diversi, e vanno giudicati separatamente */
  const list = await clickables(page);
  const seen = {};
  return list.map((c) => {
    const base = [c.tag, c.title || '', (c.text || '').replace(/\s+/g, ' ').trim().slice(0, 70)].join('\u00a7');
    const nth = seen[base] = (seen[base] === undefined ? 0 : seen[base] + 1);
    return Object.assign({}, c, { nth });
  });
};
const fingerprint = () => page.evaluate(() => ({
  url: location.href, chars: (document.body.innerText || '').length,
  head: (document.body.innerText || '').slice(0, 120).replace(/\s+/g, ' '),
  nodes: document.querySelectorAll('*').length,
  cases: document.querySelectorAll('[data-case]').length,
}));
const same = (a, b) => a.url === b.url && a.chars === b.chars && a.head === b.head && a.nodes === b.nodes && a.cases === b.cases;

const st = load();
/* ── TORNARE ALLA SCHERMATA, DAVVERO ──────────────────────────────────────
   Un clic vivo puo lasciarci dove la barra laterale non esiste — un dettaglio,
   un pannello. Allora `clickTitle` non trova il titolo, ritorna false in
   silenzio, e il portone continua a giudicare i controlli restanti su una
   schermata che non e quella: «indice fuori intervallo (3 controlli)»,
   quindici volte.

       UN RITORNO CHE FALLISCE IN SILENZIO SPOSTA TUTTO CIO CHE VIENE DOPO.

   Si verifica il ritorno, e se non riesce si ricarica la pagina. */
const backTo = async (label, hard) => {
  /* UN CLIC VIVO LASCIA UNO STATO, E LO STATO RESTA.
     Tornare alla schermata con un clic sulla barra laterale non annulla un
     commutatore acceso ne un filtro scelto: quattordici controlli risultavano
     «non presenti adesso» perche il portone stesso aveva cambiato la schermata
     che stava giudicando.

         CHI MISURA NON PUO LASCIARE IMPRONTE SU CIO CHE MISURA.

     Dopo ogni clic vivo si ricarica: e piu lento, ed e l'unico modo perche il
     controllo numero trenta sia giudicato sulla stessa schermata del primo. */
  for (let attempt = 0; attempt < 3; attempt++) {
    if (hard || attempt) {
      await page.reload({ waitUntil: 'networkidle' });
      await page.waitForTimeout(800);
    }
    if (await clickTitle(page, label, 800)) {
      if ((await clickables(page)).length > 3) return true;
    }
  }
  return false;
};

for (const label of targets) {
  await backTo(label);
  const base = await fingerprint();
  const list = await snapshot();
  const rec = { found: list.length, controls: [] };
  /* ── NON SI TORNA INDIETRO PRIMA DI OGNI CLIC ────────────────────────────
     La prima versione ri-navigava prima di ogni controllo e aspettava 320 ms:
     l'indice veniva ri-derivato su una schermata non ancora disegnata, e
     quindici controlli veri — «ESPLORA SEGNALE», «MOSTRA SCENARI», la campana —
     risultavano irraggiungibili.

         NON ERA LA PAGINA A NON RISPONDERE: ERO IO A NON ASPETTARLA.

     Si torna indietro SOLO quando il clic ha davvero cambiato qualcosa. */
  /* ── OGNI CONTROLLO SI GIUDICA DA UNA PAGINA PULITA ──────────────────────
     Ho provato a tornare indietro con un clic, poi con un ricaricamento, e
     quattordici controlli continuavano a risultare assenti: un clic vivo lascia
     uno stato — un commutatore acceso, un filtro scelto, un pannello aperto — e
     lo stato sopravvive a tutto tranne a una pagina nuova.

         CHI MISURA NON PUO LASCIARE IMPRONTE SU CIO CHE MISURA.

     Quindi: pagina nuova, navigazione alla schermata, un solo clic, confronto.
     E piu lento di ogni altra strada, ed e l'unica in cui il controllo numero
     trenta viene giudicato nelle stesse condizioni del primo. */
  let needsFresh = true;
  for (let i = 0; i < list.length; i++) {
    const c = list[i];
    /* SI RICARICA SOLO DOPO UN CLIC CHE HA CAMBIATO QUALCOSA.
       Ricaricare prima di ognuno dei 1025 controlli e corretto e costa un'ora e
       mezza: il pacchetto pesa sei megabyte e va analizzato ogni volta. Un clic
       che NON ha cambiato niente non ha lasciato niente da annullare.

           SI PAGA IL RICARICAMENTO DOVE C'E QUALCOSA DA ANNULLARE.

       E `networkidle` dice che la rete tace, non che l'applicazione e in piedi:
       si aspetta la voce di navigazione, non un numero di millisecondi. */
    if (needsFresh) {
      await page.reload({ waitUntil: 'networkidle' });
      try { await page.waitForSelector(`[title="${label.replace(/"/g, '\\"')}"]`, { timeout: 25000 }); }
      catch { /* il verdetto lo dara il clic qui sotto */ }
      needsFresh = false;
    }
    if (!await clickTitle(page, label, 800)) { rec.controls.push({ screen: label, i, tag: c.tag, text: c.text, title: c.title, verdict: 'UNREACHABLE', note: 'screen not reachable' }); continue; }
    const before = await fingerprint();
    let threw = null, clicked = false, why = '', hitText = '';
    try {
      const r = await clickKey(page, keyOf(c));
      clicked = r.clicked; why = r.reason || ''; hitText = r.what || '';
      if (!clicked && /threw/.test(why)) threw = why;
    } catch (e) { threw = String(e.message).slice(0, 90); }
    await page.waitForTimeout(650);
    const after = await fingerprint();
    let verdict;
    if (threw) verdict = 'BROKEN';
    else if (!clicked) verdict = 'UNREACHABLE';
    else if (!same(before, after)) { verdict = 'LIVE'; needsFresh = true; }
    else {
      const ctx = await page.evaluate((t) => {
        const txt = document.body.innerText || '';
        const norm = (x) => String(x || '').replace(/\s+/g, ' ').trim();
        const wanted = norm(t);
        const sel = [...document.querySelectorAll('select')]
          .some((s2) => norm((s2.options[s2.selectedIndex] || {}).text) === wanted);
        const activeNav = [...document.querySelectorAll('[title]')].some((e) => {
          if (norm(e.getAttribute('title')) !== wanted) return false;
          let n = e;
          for (let k = 0; k < 4 && n; k++) {
            if (/rgba?\(0, 1[0-9][0-9], (69|82|63)/.test(getComputedStyle(n).backgroundColor)) return true;
            n = n.parentElement;
          }
          return false;
        });
        return { sel, activeNav, onePage: /1 \/ 1|di 1\b|of 1\b/.test(txt) };
      }, c.title || c.text);
      if (ctx.sel || ctx.activeNav) verdict = 'DISABLED_BY_RULE';
      else if (ctx.onePage && /^(‹|›|<|>|«|»|\d+)$/.test((c.text || '').trim())) verdict = 'DISABLED_BY_RULE';
      else if (list.filter((x) => x.text && x.text === c.text).length > 1) verdict = 'DUPLICATE_CONTROL';
      else verdict = 'PLACEBO';
    }
    rec.controls.push({ screen: label, i, tag: c.tag, text: c.text, title: c.title, href: c.href, verdict, note: why, hit: hitText });
    /* si scrive dopo OGNI controllo: una morte per timeout non deve portarsi via
       cio che era gia stato giudicato */
    st.screens[label] = rec; save(st);
  }
  st.screens[label] = rec;
  save(st);
  const t = {}; rec.controls.forEach((x) => { t[x.verdict] = (t[x.verdict] || 0) + 1; });
  console.log(`  ${label.padEnd(30)} ${String(rec.found).padStart(4)} controlli · ` + Object.entries(t).map(([k, v]) => `${k} ${v}`).join(' · '));
}
st.errors = (st.errors || []).concat(errors);
save(st);
await browser.close(); server.close();
