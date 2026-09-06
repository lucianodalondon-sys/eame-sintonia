/* GATE · SYNTHETIC_DEMO_VISIBLE
   ---------------------------------------------------------------------------
   Non si misura leggendo i commenti: si misura RENDENDO ogni schermata che un
   lettore puo raggiungere e cercando dentro cio che verrebbe disegnato le
   stringhe che ESISTONO SOLO nel pacchetto dimostrativo.

   Le impronte si calcolano, non si scrivono a mano: una stringa conta come
   dimostrativa solo se compare nelle collezioni demo e in NESSUNA collezione
   reale. Cosi un nome di coltura o di regione — che il demo condivide con il
   vero — non produce un falso allarme.
   --------------------------------------------------------------------------- */
import { mount } from '../lib/harness.mjs';

const M = mount({});
const { ctx, AM } = M;
const D = ctx.ITALY_DEMO || {};

/* ── 1 · le viste che un lettore puo davvero aprire ───────────────────────── */
const AMMESSE = (() => {
  const src = String(ctx.__Component.VIEW_FROM_HASH.toString());
  const m = src.match(/AMMESSE\s*=\s*\[([^\]]*)\]/s);
  return m ? m[1].split(',').map(s => s.trim().replace(/^'|'$/g, '')).filter(Boolean) : [];
})();

/* ── 2 · raccolta delle stringhe ──────────────────────────────────────────── */
const strings = (v, out, depth = 0) => {
  if (depth > 6 || v == null) return out;
  if (typeof v === 'string') { if (v.length >= 12) out.add(v); return out; }
  if (typeof v !== 'object') return out;
  if (Array.isArray(v)) { for (const x of v) strings(x, out, depth + 1); return out; }
  for (const k in v) { if (k === 'raw') continue; try { strings(v[k], out, depth + 1); } catch (e) {} }
  return out;
};

const DEMO_SRC = new Set();
strings(D, DEMO_SRC);

/* Il pacchetto dimostrativo NON e un'isola: la sua prima riga legge
   window.ITALY_REAL e ricopia record veri dentro i propri elenchi. Percio il
   confronto va fatto contro TUTTE le altre sorgenti caricate, non contro le
   sole collezioni del modello: una stringa che vive anche in una qualsiasi di
   esse e vocabolario condiviso, non un'impronta della dimostrazione.

       CALIBRARE SU META DEL VERO PRODUCE UN ALLARME PER OGNI COLTURA. */
const REAL_SRC = new Set();
const GLOBALI_REALI = Object.keys(ctx).filter(k =>
  /^(ITALY_|SINTONIA_|MEETING_|ADAMA_)/.test(k) && k !== 'ITALY_DEMO');
for (const g of GLOBALI_REALI) { try { strings(ctx[g], REAL_SRC, -6); } catch (e) {} }
console.log('sorgenti reali confrontate ', GLOBALI_REALI.length, '·', GLOBALI_REALI.join(' '));

/* Un colore non e un dato. `rgba(255,255,255,0.05)` vive nel pacchetto
   dimostrativo perche il demo porta anche i propri token di stile, e vive nelle
   schermate vere perche e il grigio di fondo di mezzo portale: la coincidenza
   non dice che una schermata mostra la dimostrazione, dice che due file
   scrivono lo stesso bianco al 5%.

       UN'IMPRONTA CHE PUNTA A UN COLORE NON ACCUSA UN CONTENUTO.

   L'esclusione e stretta di proposito: solo forme che un foglio di stile
   riconosce — colori, sfumature, ritagli. Nessuna parola, nessun nome, nessuna
   frase esce da qui. */
const SOLO_STILE = /^(rgba?\(|#[0-9a-fA-F]{3,8}$|linear-gradient\(|radial-gradient\(|polygon\(|clip-path)/;
const IMPRONTE = [...DEMO_SRC].filter(s => !REAL_SRC.has(s) && !SOLO_STILE.test(s));
console.log('viste raggiungibili        ', AMMESSE.length, '·', AMMESSE.join(' '));
console.log('stringhe solo-demo (impronte)', IMPRONTE.length);

/* ── 3 · si rende, e si cerca ─────────────────────────────────────────────── */
const trovate = [];
let renderizzate = 0, rotte = 0;
/* Le due lingue sono due superfici. Il demo porta il proprio testo in
   entrambe, e una schermata pulita in italiano puo perdere in inglese. */
const LINGUE = ['it', 'en'];
for (const lang of LINGUE) for (const view of AMMESSE) {
  const r = M.tryVals({ view, lang });
  if (!r.ok) { rotte++; console.log('  ROTTA', view, '·', r.error); continue; }
  renderizzate++;
  const viste = strings(r.vals, new Set());
  for (const imp of IMPRONTE) if (viste.has(imp)) trovate.push({ view: lang + ' · ' + view, testo: imp.slice(0, 90) });
}

/* ── 3b · le schermate di dettaglio ───────────────────────────────────────
   Una vista di primo livello si apre dal menu; una scheda si apre CLICCANDO.
   Se il gate si fermasse alle dieci del menu, misurerebbe il vestibolo e
   dichiarerebbe pulita la casa.

       DIECI PORTE CONTROLLATE NON SONO UNA CASA CONTROLLATA.

   Gli identificativi non sono inventati: si prendono dai record veri del
   modello, cosi ogni scheda si apre su qualcosa che esiste davvero. */
const C = AM.collections;
const ids = (coll, campo) => ((C[coll] && C[coll].records) || []).map(r => r[campo]).filter(Boolean);
const DETTAGLI = [
  ['mcase', 'mCaseId', (() => {
    const B = ctx.MEETING_SURFACE && ctx.MEETING_SURFACE.build ? ctx.MEETING_SURFACE.build('it') : null;
    if (!B) return [];
    const tutti = [];
    for (const k of Object.keys(B)) if (Array.isArray(B[k])) for (const c of B[k]) if (c && c.id) tutti.push(c.id);
    return [...new Set(tutti)];
  })()],
  ['case', 'caseId', ids('opportunities', 'id')],
  ['window', 'windowId', ids('cropWindows', 'id')],
  ['product', 'productId', (AM.products || []).map(p => p.key)],
  ['source', 'sourceId', ids('sources', 'id')],
  ['person', 'personId', ids('researchers', 'id').concat(ids('publicPeople', 'id'))],
  ['company', 'companyId', ids('competitorCompanies', 'name')],
  ['cproduct', 'cproductId', ids('competitorProducts', 'name')],
  ['theme', 'themeId', ids('scienceThemes', 'id')],
  ['event', 'eventId', ids('futureEvents', 'id')],
  ['signal', 'signalId', ids('futureSignals', 'id')],
  ['mradar', 'mStatus', ['']],
  ['msignals', 'mStatus', ['']],
];
let schede = 0;
for (const [view, campo, elenco] of DETTAGLI) {
  if (!elenco.length) { console.log('  NESSUN ID per', view); continue; }
  for (const id of elenco) for (const lang of LINGUE) {
    const r = M.tryVals({ view, [campo]: id, lang });
    if (!r.ok) { rotte++; if (rotte < 12) console.log('  ROTTA', view, id, '·', r.error); continue; }
    schede++;
    const viste = strings(r.vals, new Set());
    for (const imp of IMPRONTE) if (viste.has(imp)) trovate.push({ view: lang + ' · ' + view + ' · ' + id, testo: imp.slice(0, 90) });
  }
}
console.log('schede di dettaglio rese   ', schede);

console.log('viste rese                 ', renderizzate, '· rotte', rotte);
console.log('');
console.log('SYNTHETIC_DEMO_VISIBLE =', trovate.length);
for (const t of trovate.slice(0, 40)) console.log('  ', t.view, '·', t.testo);
process.exitCode = trovate.length === 0 && rotte === 0 ? 0 : 1;
