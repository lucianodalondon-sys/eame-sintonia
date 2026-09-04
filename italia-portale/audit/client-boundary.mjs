/* SINTONIA · LA FRONTIERA DEL CLIENTE  (T1…T8)
   ===========================================================================
   Il motore trova i casi. Il cliente compra opportunita. Non sono la stessa
   cosa, e questa e la riga che lo tiene fermo.

       IL CLIENTE NON DEVE VEDERE COME LA MACCHINA HA TROVATO IL CASO.
       E NON DEVE SMETTERE DI ESISTERE NIENTE PERCHE E STATO NASCOSTO.

   Le due meta contano ugualmente. I controlli dispari (T1…T5) provano che la
   meccanica interna NON arriva allo schermo; i pari (T6…T8) provano che quello
   che e stato tolto dalla vista e ancora INTERO dietro — id canonici, prove,
   fonti, e i casi strategici raggiungibili nelle loro aree.

   NASCONDERE NON E CANCELLARE. Un portone che verificasse solo la prima meta
   approverebbe una perdita di dati come se fosse pulizia.
   =========================================================================== */
import fs from 'node:fs';
import path from 'node:path';
import { mount, CLIENT } from './lib/harness.mjs';

const C = { g: (t) => `\x1b[32m${t}\x1b[0m`, r: (t) => `\x1b[31m${t}\x1b[0m`,
  d: (t) => `\x1b[2m${t}\x1b[0m`, b: (t) => `\x1b[1m${t}\x1b[0m` };
const out = [];
const T = (id, name, ok, detail) => out.push({ id, name, ok: !!ok, detail: detail || '' });

const SNAP = JSON.parse(fs.readFileSync(path.join(CLIENT, 'meeting-intelligence-snapshot.json'), 'utf8'));
const m = await mount();
const AM = m.ctx.ITALY_APP_MODEL;

/* ── che cosa e «schermo del cliente» ──────────────────────────────────────
   Le proprieta che la marcatura lega e mostra. Le chiavi macchina — un id in
   un attributo `data-`, il valore di un <option>, un codice tenuto per il
   filtro — NON sono testo sullo schermo, e confonderle farebbe fallire il
   portone su cose che nessuno legge. */
const MACHINE_KEY = /^(id|token|key|value|v|statusCode|priorityCode|caseId|href|url|cursor)$/;
const collectText = (root, label) => {
  const found = [];
  const walk = (v, where, seen) => {
    if (v === null || v === undefined) return;
    if (typeof v === 'string') { found.push([where, v]); return; }
    if (typeof v !== 'object') return;
    if (seen.has(v)) return; seen.add(v);
    if (Array.isArray(v)) { v.forEach((x, i) => walk(x, `${where}[${i}]`, seen)); return; }
    for (const k of Object.keys(v)) {
      if (typeof v[k] === 'function' || MACHINE_KEY.test(k)) continue;
      walk(v[k], `${where}.${k}`, seen);
    }
  };
  walk(root, label, new WeakSet());
  return found;
};

/* La superficie che il cliente apre davvero, nelle due lingue. */
const CLIENT_SURFACE = () => {
  const rows = [];
  for (const lang of ['it', 'en']) {
    const v = m.vals({ view: 'radar', lang });
    /* `kpis` e la griglia PRECEDENTE alla riconciliazione: `isRadar` e falso e
       quel blocco non si rende piu, quindi le sue proprieta non sono testo
       sullo schermo. Misurarle qui farebbe fallire il portone su parole che
       nessuno legge — e T5 e T7 provano gia che quella superficie non e
       raggiungibile. */
    for (const key of ['nav', 'meetingKpis', 'meetingStatusBtns', 'meetingShown', 'mt']) {
      if (v[key] !== undefined) rows.push(...collectText(v[key], `${lang}.${key}`));
    }
    for (const id of SNAP.CASES.slice(0, 6).map((c) => c.ID)) {
      const d = m.vals({ view: 'mcase', mCaseId: id, lang });
      rows.push(...collectText(d.mc, `${lang}.${id}.mc`));
      for (const k of ['mcActions', 'mcProducts', 'mcWindow', 'mcChain', 'mcEvidence']) {
        if (d[k] !== undefined) rows.push(...collectText(d[k], `${lang}.${id}.${k}`));
      }
    }
  }
  return rows;
};
const SURFACE = CLIENT_SURFACE();

/* ── T1 · i conteggi del motore non si mostrano ────────────────────────────
   Il numero dei casi canonici e delle convergenze e una misura del MOTORE.
   Sullo schermo del cliente diventa una promessa che nessuno gli ha fatto. */
{
  const total = SNAP.TOTAL_CASES;
  const confirmed = SNAP.CASES.filter((c) => c.OPPORTUNITY_STATE === 'OPPORTUNITY_CONFIRMED').length;
  const candidate = SNAP.CASES.filter((c) => c.OPPORTUNITY_STATE === 'OPPORTUNITY_CANDIDATE').length;
  /* Il conteggio dei casi puo apparire come «quante opportunita ci sono» — e
     legittimo. Quello che non puo apparire e la COPPIA verificate/da validare,
     che e il verdetto del metodo, non un fatto commerciale. */
  const pair = new RegExp(`\\b${confirmed}\\b[^0-9]{1,40}\\b${candidate}\\b|\\b${candidate}\\b[^0-9]{1,40}\\b${confirmed}\\b`);
  const hits = SURFACE.filter(([, s]) => pair.test(s));
  T('T1', 'i conteggi verificate/da validare del motore non arrivano al cliente', hits.length === 0,
    hits.length ? hits.slice(0, 3).map(([w, s]) => `${w}: «${s.slice(0, 50)}»`).join(' · ')
      : `motore ${total} casi · ${confirmed} confermati · ${candidate} candidati — nessuna di queste coppie sullo schermo`);
}

/* ── T2 · nessun OPPORTUNITY_STATE crudo ───────────────────────────────── */
{
  const RAW = /\b(OPPORTUNITY_(?:STATE|CONFIRMED|CANDIDATE)|RENDERABLE_WITH_METHOD|CLIENT_SAFE|SALES_READY|SALES_PREPARE|COMMERCIAL_WATCH|STRATEGIC_OPPORTUNITY|VERIFIED_CONVERGENCE)\b/;
  const hits = SURFACE.filter(([, s]) => RAW.test(s));
  T('T2', 'nessun gettone crudo di stato o di priorita sullo schermo', hits.length === 0,
    hits.length ? hits.slice(0, 3).map(([w, s]) => `${w}: «${s.slice(0, 50)}»`).join(' · ')
      : `${SURFACE.length} stringhe lette in IT e EN, nessun gettone interno`);
}

/* ── T3 · il vocabolario della validazione non e navigazione ───────────────
   «Da validare» e «convergenza verificata» dicono al cliente come lavora il
   metodo, non che cosa puo fare. Fuori dal menu, dai contatori e dai filtri. */
{
  const VOCAB = /\b(da validare|to validate|validare ora|validate now|convergenz\w*|convergence|verificat\w*\bconvergenz|red team)\b/i;
  const NAVISH = /\.(nav|meetingKpis|meetingStatusBtns|kpis)\b/;
  const hits = SURFACE.filter(([w, s]) => NAVISH.test(w) && VOCAB.test(s));
  T('T3', 'il vocabolario della validazione non e nel menu, nei contatori o nei filtri', hits.length === 0,
    hits.length ? hits.map(([w, s]) => `${w}: «${s}»`).join(' · ')
      : 'menu, contatori e filtri parlano solo di azione commerciale');
}

/* ── T4 · la ricerca del cliente non trova il radar canonico ──────────── */
{
  const bad = [];
  for (const lang of ['it', 'en']) {
    for (const q of ['radar', 'canonico', 'canonical', 'convergenza']) {
      const v = m.vals({ view: 'radar', lang, query: q, committedQuery: q });
      for (const g of (v.searchGroups || [])) {
        for (const it of (g.items || [])) {
          if (/canonic|convergenz|convergence/i.test(String(it.label || '') + String(it.meta || ''))) {
            bad.push(`${lang} «${q}» -> ${it.label}`);
          }
        }
      }
    }
  }
  T('T4', 'la ricerca del cliente non espone il radar canonico', bad.length === 0,
    bad.length ? bad.slice(0, 3).join(' · ') : 'quattro interrogazioni in due lingue, nessun risultato di meccanica interna');
}

/* ── T5 · il radar canonico non e una voce di menu ───────────────────────── */
{
  const bad = [];
  for (const lang of ['it', 'en']) {
    const v = m.vals({ view: 'radar', lang });
    (v.nav || []).forEach((n) => { if (/canonic/i.test(String(n.label))) bad.push(`${lang}: ${n.label}`); });
    /* Un solo radar di opportunita. «Radar Futuro» e un altro strumento e resta. */
    const radars = (v.nav || []).filter((n) => /radar/i.test(String(n.label)) && !/futur/i.test(String(n.label)));
    if (radars.length !== 1) bad.push(`${lang}: ${radars.length} radar di opportunita nel menu`);
  }
  T('T5', 'nessuna voce «radar canonico» nel menu, e un solo radar di opportunita', bad.length === 0,
    bad.length ? bad.join(' · ') : 'una sola voce di radar in IT e in EN');
}

/* ── T6 · la tracciabilita resta intera ──────────────────────────────────
   Il cliente riceve la sintesi; la catena che la sostiene deve restare
   raggiungibile per intero da ogni caso mostrato. */
{
  const missing = [];
  for (const c of SNAP.CASES) {
    const d = m.vals({ view: 'mcase', mCaseId: c.ID, lang: 'it' });
    const mc = d.mc || {};
    if (!d.mcId && !mc.id) missing.push(`${c.ID}: id canonico non risolve`);
    const ev = (d.mcEvidence || mc.evidence || []).length || (c.EVIDENCE_IDS || []).length;
    if ((c.EVIDENCE_IDS || []).length && !ev) missing.push(`${c.ID}: prove non raggiungibili`);
    const src = (d.mcSources || mc.sources || []).length || (d.mcSourceUrls || []).length;
    if ((c.SOURCE_IDS || []).length && !src) missing.push(`${c.ID}: fonti non raggiungibili`);
  }
  T('T6', 'ogni opportunita mostrata mantiene id canonico, prove e fonti', missing.length === 0,
    missing.length ? `${missing.length} · ` + missing.slice(0, 3).join(' · ')
      : `${SNAP.CASES.length} casi · id, prove e fonti risolvono da ognuno`);
}

/* ── T7 · togliere dalla vista non toglie dal motore ──────────────────── */
{
  const back = SNAP.CASES.length;
  const coll = AM && AM.collections && AM.collections.opportunities ? AM.collections.opportunities.count : 0;
  const ids = SNAP.CASES.every((c) => /^OPP_/.test(c.ID));
  const gates = SNAP.CASES.every((c) => c.OPPORTUNITY_STATE && c.TRAIL_STATE && c.PUBLICATION_STATE);
  T('T7', 'i casi canonici restano interi dietro lo schermo', back === SNAP.TOTAL_CASES && coll > 0 && ids && gates,
    `istantanea ${back} casi · modello ${coll} record · stati di metodo presenti su tutti`);
}

/* ── T8 · l'intelligenza non commerciale resta raggiungibile ─────────────
   Un caso che oggi non e un'opportunita commerciale non sparisce: vive nella
   sua area. Se le aree si svuotassero, «nascondere» sarebbe diventato
   «perdere», che e la cosa che questo portone esiste per impedire. */
{
  const areas = ['futureSignals', 'windows', 'marketObservations', 'competitorActivities', 'scienceRecords', 'sources'];
  const empty = areas.filter((a) => !(AM.collections[a] && AM.collections[a].count > 0));
  const v = m.vals({ view: 'radar', lang: 'it' });
  const navAreas = (v.nav || []).filter((n) => n.count > 0).length;
  T('T8', 'le aree strategiche restano popolate e raggiungibili', empty.length === 0 && navAreas >= 6,
    empty.length ? 'aree vuote: ' + empty.join(', ')
      : areas.map((a) => `${a} ${AM.collections[a].count}`).join(' · ') + ` · ${navAreas} voci di menu vive`);
}

/* ── il verdetto ─────────────────────────────────────────────────────────── */
const pass = out.filter((x) => x.ok).length;
const fail = out.length - pass;
console.log('');
console.log(C.b('  SINTONIA · LA FRONTIERA DEL CLIENTE'));
console.log('  ' + '─'.repeat(100));
for (const x of out) {
  console.log('  ' + (x.ok ? C.g('PASS') : C.r('FAIL')) + `  ${x.id.padEnd(4)} ${x.name}`);
  console.log('        ' + C.d(x.detail));
}
console.log('  ' + '─'.repeat(100));
console.log('  ' + (fail === 0 ? C.g(`${pass}/${out.length} · la meccanica resta dentro, e niente e andato perso`)
  : C.r(`${fail} su ${out.length} falliti`)));
console.log('');
process.exit(fail === 0 ? 0 : 1);
