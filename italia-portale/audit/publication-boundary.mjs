/* SINTONIA ITALIA · CIO CHE PUO CHIUDERE UNA RISPOSTA
   ---------------------------------------------------------------------------
   node audit/publication-boundary.mjs [--base http://host]

   README-FIRST §3 del pacchetto, testuale:

       CLIENT_SAFE = true   -> puo sostenere un'affermazione visibile al cliente
       CLIENT_SAFE = false  -> vive nel corpus, compare come RESEARCH_LEADS,
                               e NON sostiene MAI un'affermazione da solo

   Due doveri, non uno. Il primo: un record non verificato non deve CHIUDERE
   una risposta — puo restare nel corpus, non puo entrare in un conteggio che
   il portale presenta come osservazione. Il secondo, opposto e altrettanto
   importante: il timbro stesso — CLIENT_SAFE, QA_UNREVIEWED — e contabilita
   interna e non deve mai comparire sullo schermo.

       IL DATO CHE NON E STATO CONFERITO PUO APRIRE UNA DOMANDA.
       NON PUO CHIUDERE UN'AFFERMAZIONE.

   Dove corpus e pubblicabile non coincidono, la schermata deve DIRE quale dei
   due sta mostrando. Un numero giusto sotto un'etichetta che ne promette un
   altro e un denominatore falso, anche se ogni cifra presa da sola e vera.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadData, mount } from './lib/harness.mjs';
import { collectStrings } from './lang.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = arg('base', null);
const PORT = Number(arg('port', 8985));

const AM = loadData().ITALY_APP_MODEL;
const bad = { token: [], split: [], silent: [], render: [] };

/* ── 1 · il timbro interno non va sullo schermo ─────────────────────────── */
const TOKENS = /\b(CLIENT_SAFE|QA_UNREVIEWED|QA_PASS|QA_CORRECTED|QA_REJECTED|EVIDENCE_DERIVED|EVIDENCE_SOURCED|EVIDENCE_DOCUMENTED|RENDERABLE_WITH_METHOD|FAILED_GATES|RESEARCH_LEADS)\b/;
const VIEWS = ['radar', 'future', 'windows', 'market', 'portfolio', 'voices',
  'competitors', 'science', 'archive', 'sources'];
const m = mount();
let screens = 0;
for (const lang of ['it', 'en']) {
  for (const view of VIEWS) {
    const r = m.tryVals({ view, lang });
    if (!r.ok) { bad.render.push(`${lang}·${view}: ${r.error}`); continue; }
    screens++;
    for (const { path: p, value } of collectStrings(r.vals)) {
      const hit = TOKENS.exec(String(value));
      if (hit) bad.token.push(`${lang}·${view}·${p}: ${hit[1]}`);
    }
  }
}
if (screens < VIEWS.length * 2) bad.render.push(`only ${screens} of ${VIEWS.length * 2} screens rendered`);

/* ── 2 · dove il corpus e il pubblicabile divergono, il modello deve saperlo ── */
const FAMILIES = ['competitorActivities', 'publicVoices', 'marketObservations', 'sources'];
for (const f of FAMILIES) {
  const recs = (AM.collections[f] || { records: [] }).records;
  if (!recs.length) { bad.render.push(`${f}: no records to inspect`); continue; }
  const pub = recs.filter((r) => r.publishable).length;
  if (pub === recs.length) continue;
  /* il campo deve esistere su OGNI record, altrimenti «publishable» sarebbe
     vero solo per distrazione */
  const missing = recs.filter((r) => typeof r.publishable !== 'boolean').length;
  if (missing) bad.split.push(`${f}: ${missing} records carry no publishable flag`);
}

/* ── 3 · le due schermate che dichiarano un denominatore ridotto ────────── */
const says = (vals, re) => collectStrings(vals).some(({ value }) => re.test(String(value)));
for (const lang of ['it', 'en']) {
  const comp = m.tryVals({ view: 'competitors', lang });
  if (comp.ok) {
    const tabs = (comp.vals.compTabs || []);
    const all = tabs[0] ? tabs[0].count : null;
    const parts = tabs.slice(1).reduce((a, t) => a + (t.count || 0), 0);
    if (all !== parts) bad.silent.push(`${lang}·competitors: the total (${all}) is not the sum of its categories (${parts})`);
  } else bad.render.push(`${lang}·competitors did not render`);
  const src = m.tryVals({ view: 'sources', lang });
  if (src.ok) {
    /* NON con collectStrings: si ferma a 4.000 stringhe e la schermata Fonti
       ne produce circa 24.800, quindi il titolo non veniva mai raggiunto e il
       controllo falliva per cecita, non per difetto. Il valore si legge dove
       sta. */
    const re = lang === 'it' ? /con accesso verificato/i : /with verified access/i;
    const kpi = (src.vals.sourceKpis || []).map((k) => String(k && k.label || '')).join(' | ');
    if (!kpi) bad.render.push(`${lang}·sources: no KPI to read`);
    else if (!re.test(kpi)) bad.silent.push(`${lang}·sources: the headline does not say how many have a measured access route — "${kpi.slice(0, 80)}"`);
  } else bad.render.push(`${lang}·sources did not render`);
}

const rows = [
  ['B1', 'no internal QA or safety stamp reaches a screen', bad.token],
  ['B2', 'every record in a split family carries the publishable flag', bad.split],
  ['B3', 'a reduced denominator is stated, not left silent', bad.silent],
  ['B4', 'every screen under test rendered', bad.render],
];
const G = '\x1b[32m', R = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log(`\n  SINTONIA ITALY · PUBLICATION BOUNDARY   (${screens} screens read)`);
console.log('  ' + '-'.repeat(96));
let fails = 0;
for (const [id, title, list] of rows) {
  const ok = list.length === 0;
  if (!ok) fails++;
  console.log(`  ${ok ? G + 'PASS' + X : R + 'FAIL' + X}  ${id}  ${title.padEnd(56)} ${D}exp${X} 0  ${D}got${X} ${list.length}`);
  if (!ok) list.slice(0, 6).forEach((x) => console.log(`        ${D}${x}${X}`));
}
console.log('  ' + '-'.repeat(96));
for (const f of FAMILIES) {
  const recs = (AM.collections[f] || { records: [] }).records;
  console.log(`  ${D}${f.padEnd(22)} corpus ${String(recs.length).padStart(4)}   publishable ${String(recs.filter((r) => r.publishable).length).padStart(4)}${X}`);
}
console.log('');
process.exit(fails === 0 ? 0 : 1);
