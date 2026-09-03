/* SINTONIA ITALIA · CIO CHE STA NEL MODELLO SI DEVE POTER APRIRE
   ---------------------------------------------------------------------------
   node audit/reachability.mjs

   Centoventidue bollettini di campo vivevano in ITALY_APP_MODEL, contavano nel
   pannello di stato, e nessuna schermata li apriva: nessuna vista, nessuna
   riga d'archivio, nessuna voce nell'indice di ricerca. Informazione
   canonica — con regione, data e fonte — impossibile da raggiungere.

       UN DATO CHE STA NEL MODELLO E NON SI PUO APRIRE
       NON E STATO CONSEGNATO.

   Il controllo non chiede una schermata per famiglia: chiede che ogni famiglia
   canonica sia raggiungibile da ALMENO una superficie — una vista, l'archivio
   o la ricerca. L'archivio e per definizione l'indice sopra il modello, quindi
   e la casa naturale di chi non ha una vista propria.
   --------------------------------------------------------------------------- */
import { loadData } from './lib/harness.mjs';

const AM = loadData().ITALY_APP_MODEL;
const C = AM.collections;

/* Le famiglie che portano intelligence al cliente. Le collezioni derivate
   (indici, proiezioni) e la demo di integrazione non sono qui: non sono
   informazione canonica da aprire. */
const FAMILIES = [
  'opportunities', 'cropWindows', 'currentFieldSignals', 'fieldBulletins',
  'marketObservations', 'scienceRecords', 'resistance', 'researchers',
  'competitorActivities', 'publicVoices', 'futureSignals', 'sources',
  'productsCommercial', 'productsRegulatory', 'activeIngredients',
  'productRelationships',
];

const archive = (C.archive || { records: [] }).records;
const archIds = new Set(archive.map((r) => String(r.recordId)));
const idxIds = new Set((AM.searchIndex || []).map((e) => String(e.id)));

/* come ciascuna famiglia di prodotto si apre davvero */
const prodNames = new Set((AM.searchIndex || []).filter((e) => e.kind === 'product').map((e) => String(e.id)));
const aiInProducts = new Set();
(AM.products || []).forEach((p) => (p.aiList || []).forEach((a) => aiInProducts.add(String(a).toUpperCase())));
const PRODUCT_FAMILIES = {
  productsCommercial: (recs) => recs.filter((r) => { const e = AM.findProduct(r.name); return e && prodNames.has(e.name); }).length,
  productsRegulatory: (recs) => recs.filter((r) => { const e = AM.findProduct(r.name); return e && prodNames.has(e.name); }).length,
  activeIngredients: (recs) => recs.filter((r) => aiInProducts.has(String(r.name || r.id).toUpperCase())).length,
  productRelationships: (recs) => recs.filter((r) => !!AM.findProduct(r.product)).length,
};

const bad = { unreachable: [], empty: [] };
const table = [];

for (const f of FAMILIES) {
  const col = C[f];
  if (!col) { bad.empty.push(`${f}: collection absent`); continue; }
  const recs = col.records || [];
  if (!recs.length) { bad.empty.push(`${f}: no records to inspect`); continue; }
  const inArchive = recs.filter((r) => archIds.has(String(r.id || r.windowId || r.voiceId))).length;
  const inSearch = recs.filter((r) => idxIds.has(String(r.id || r.name || r.windowId || r.voiceId))).length;
  /* LE FAMIGLIE DI PRODOTTO SI APRONO PER NOME, NON PER ID.
     Catalogo, registro, sostanze attive e righe d'uso non hanno una voce
     propria nell'indice: si raggiungono attraverso l'ENTITA UNITA, che porta
     il nome commerciale. Una prima versione di questo controllo cercava i loro
     id e le dichiarava tutte irraggiungibili — cinquantuno prodotti che la
     schermata Portafoglio disegna uno per uno. Un controllo che grida al lupo
     e peggio di nessun controllo, perche insegna a ignorarlo. */
  const viaProduct = PRODUCT_FAMILIES[f] ? PRODUCT_FAMILIES[f](recs) : 0;
  const reach = Math.max(inArchive, inSearch, viaProduct);
  table.push({ f, n: recs.length, inArchive, inSearch, viaProduct });
  /* Una famiglia intera irraggiungibile e il difetto. Una copertura parziale
     e legittima — non tutti i record hanno un titolo da indicizzare — ma zero
     su tutti significa che nessuna superficie la conosce. */
  if (reach === 0) bad.unreachable.push(`${f}: ${recs.length} records, reachable from nothing`);
}

const G = '\x1b[32m', R = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log('\n  SINTONIA ITALY · REACHABILITY');
console.log('  ' + '-'.repeat(88));
console.log(`  ${'family'.padEnd(26)} ${'records'.padStart(8)} ${'archive'.padStart(9)} ${'search'.padStart(8)} ${'product'.padStart(9)}`);
console.log('  ' + '-'.repeat(88));
for (const r of table) {
  const ok = Math.max(r.inArchive, r.inSearch, r.viaProduct) > 0;
  console.log(`  ${(ok ? G + '✓' + X : R + '✗' + X)} ${r.f.padEnd(24)} ${String(r.n).padStart(8)} ${String(r.inArchive).padStart(9)} ${String(r.inSearch).padStart(8)} ${String(r.viaProduct || '—').padStart(9)}`);
}
console.log('  ' + '-'.repeat(88));
const fails = bad.unreachable.length + bad.empty.length;
for (const b of bad.unreachable.concat(bad.empty)) console.log(`  ${R}FAIL${X} ${b}`);
if (!fails) console.log(`  ${G}PASS · every canonical family can be opened from at least one surface${X}`);
console.log('');
process.exit(fails === 0 ? 0 : 1);
