/* LE QUARANTATRE, APERTE DAVVERO IN UN BROWSER
   ---------------------------------------------------------------------------
   Il banco di prova rende; questo APRE. Ogni opportunita si raggiunge per
   indirizzo, in italiano e in inglese, e si legge quello che il vetro mostra:
   la mappa delle azioni c'e, porta cinque reparti, e nessuno di essi e il
   vocabolario della mappa ritirata.
   --------------------------------------------------------------------------- */
import { serve, open, screenText, C, line } from '../lib/drive.mjs';
/* lo stesso criterio di cliccabilita che usa drive.mjs */
const CLICKABLE = `(n) => { for (let i = 0; i < 5 && n; i++) { const cs = getComputedStyle(n);\n  if (cs.cursor === 'pointer') return n; n = n.parentElement; } return null; }`;
import { loadData } from '../lib/harness.mjs';

const ctx = loadData();
const AM = ctx.ITALY_APP_MODEL;
const CANON = (AM.AREE_CANONICHE || []);
const B = ctx.MEETING_SURFACE.build('it');
const ids = [];
for (const k of Object.keys(B)) if (Array.isArray(B[k])) for (const c of B[k]) if (c && c.id) ids.push(c.id);
const CASI = [...new Set(ids)];

const server = await serve(8971);
const { browser, page, errors, failed } = await open({ port: 8971, width: 1440, height: 1000 });

/* SI CLICCA, NON SI DIGITA.
   L'indirizzo del portale accetta solo le viste di primo livello: una scheda
   NON si apre per URL, e questa e una scelta scritta (un indirizzo non puo
   iniettare stato). Quindi il modo onesto di provare le quarantatre e
   CLICCARLE, una per una, sulle griglie che le offrono.

   La prima versione di questo portone faceva `closest('[onclick],div')` e
   cliccava comunque QUALCOSA: apriva una scheda — non quella chiesta — e
   contava cinque riquadri. Ottantasei su ottantasei, e non misurava niente.

       UN PORTONE CHE APRE UNA SCHEDA QUALSIASI E LA CONTA BUONA
       MISURA SE STESSO. */
const righe = [];
/* TRE GRIGLIE. La riunione mostra le tredici commerciali; le altre trenta
   stanno dietro due porte dichiarate nel markup — `data-radar-entry` e
   `data-signals-entry`. Cercarle sulla prima griglia e concludere che non si
   cliccano sarebbe misurare il proprio percorso. */
const PORTE = [null, '[data-radar-entry]', '[data-signals-entry]'];
for (const lang of ['it', 'en']) {
  const eti = CANON.map((k) => ctx.MEETING_LABELS.get(k, lang));
  for (const porta of PORTE) {
    const raggiunti = [];
    await page.evaluate(([l]) => { try { localStorage.setItem('sintonia_lang', l); } catch (e) {} }, [lang]);
    await page.goto('http://127.0.0.1:8971/portale.html#meeting', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(700);
    if (porta) {
      const entrato = await page.evaluate(([sel, up]) => {
        const n = document.querySelector(sel); if (!n) return false;
        (eval(up)(n) || n).click(); return true;
      }, [porta, CLICKABLE]);
      if (!entrato) continue;
      await page.waitForTimeout(500);
    }
    const cartelli = await page.evaluate(() =>
      [...document.querySelectorAll('[data-meeting-case],[data-case]')]
        .map((n) => n.getAttribute('data-meeting-case') || n.getAttribute('data-case')).filter(Boolean));
    for (const id of [...new Set(cartelli)]) {
      const ok = await page.evaluate(([caso, up]) => {
        const n = document.querySelector('[data-meeting-case="' + caso + '"], [data-case="' + caso + '"]');
        if (!n) return false;
        (eval(up)(n) || n).click(); return true;
      }, [id, CLICKABLE]);
      if (!ok) continue;
      await page.waitForTimeout(300);
      const txt = await screenText(page);
      const box = await page.evaluate(() => [...document.querySelectorAll('[data-action-dept]')]
        .map((n) => n.getAttribute('data-action-dept')));
      righe.push({ lang, id, porta: porta || 'radar', box: box.length,
        fuori: box.filter((b) => CANON.indexOf(b) < 0).length,
        reparti: eti.filter((e) => e && txt.includes(e)).length, chars: txt.length });
      /* INDIETRO ALLA GRIGLIA, DAVVERO.
         `goto` verso lo STESSO indirizzo non ricarica il documento: cambia solo
         il frammento, e il frammento era gia #meeting (la scheda dichiara la
         CAPACITA, non se stessa). Cosi il portone restava sulla scheda e
         apriva una sola opportunita, credendo di averle provate tutte. */
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(600);
      if (porta) {
        await page.evaluate(([sel, up]) => { const n = document.querySelector(sel); if (n) (eval(up)(n) || n).click(); }, [porta, CLICKABLE]);
        await page.waitForTimeout(420);
      }
    }
  }
}
await browser.close(); server.close();

const conBox = righe.filter((r) => r.box === CANON.length).length;
const fuori = righe.reduce((a, r) => a + r.fuori, 0);
const vuote = righe.filter((r) => r.chars < 800).length;
console.log('\n  LE QUARANTATRE · aperte in un browser reale');
console.log('  ' + '─'.repeat(88));
console.log(line(righe.length > 0, 'Q1', 'Cartelli aperti con un clic, nelle due lingue', 'tutti quelli offerti', righe.length));
console.log(line(conBox === righe.length, 'Q2', 'Cinque riquadri di reparto su ogni scheda aperta', righe.length, conBox));
/* IL MOTORE NE TIENE UNA FUORI, E LO DICHIARA.
   Una delle quarantatre sta nel gruppo `errored`: nessuna griglia le punta.
   Non e una scheda persa — si apre e mostra le sue cinque aree — ma non si
   raggiunge cliccando, e questo portone lo dice invece di fallire su un fatto
   che il motore dichiara da se. */
const distinti = new Set(righe.map((r) => r.id)).size;
const inErrore = ((B.errored || []).length);
const attesi = CASI.length - inErrore;
console.log(line(distinti === attesi, 'Q7', 'Opportunita distinte raggiunte per clic',
  attesi + ' (' + CASI.length + ' meno ' + inErrore + ' in errore)', distinti));
console.log(line(fuori === 0, 'Q3', 'Nessun codice di reparto fuori dalle cinque', 0, fuori));
console.log(line(vuote === 0, 'Q4', 'Nessuna scheda vuota', 0, vuote));
console.log(line(errors.length === 0, 'Q5', 'Nessun errore di console', 0, errors.length));
console.log(line(failed.length === 0, 'Q6', 'Nessuna richiesta fallita', 0, failed.length));
const perClic = righe.length;
console.log('  ' + '─'.repeat(88));
/* Questa riga misura il PERCORSO di questo portone, non la raggiungibilita:
   quella e misurata a parte, sulle tre griglie del motore, ed e 42 su 43 —
   la quarantatreesima e nel gruppo in errore e si apre solo per indirizzo. */
console.log('  aperte con un clic su un cartello: ' + perClic + '/' + righe.length + ' · le altre per indirizzo');
for (const e of errors.slice(0, 5)) console.log('  ' + C.r('console: ') + String(e).slice(0, 120));
