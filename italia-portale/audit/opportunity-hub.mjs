/* SINTONIA · OPPORTUNITY_DETAIL_COMPLETENESS_GATE + OPPORTUNITY_RELATIONSHIP_GATE
   ---------------------------------------------------------------------------
   node audit/opportunity-hub.mjs [--cases 12] [--json out.json]

   A ficha tinha a informacao e o detalhe nao a projetava. Este portao nao le o
   codigo: abre o radar num Chromium, CLICA em cada oportunidade, e compara o
   que o MODELO carrega com o que o LEITOR ve.

       SE O MODELO TEM E A TELA NAO MOSTRA, REPROVA.
       SE A TELA MOSTRA UM VINCULO QUE O MODELO NAO TEM, REPROVA MAIS.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import { serve, open, openCase, caseIds, screenText, clickTitle, C, line } from './lib/drive.mjs';
import { loadData } from './lib/harness.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const WANT = Number(arg('cases', 12));
const JSON_OUT = arg('json', null);
const PORT = 8946;

/* ── o que o modelo sabe ──────────────────────────────────────────────────── */
const AM = loadData().ITALY_APP_MODEL;
const OPP = AM.collections.opportunities.records;
const byId = {}; OPP.forEach((o) => { byId[o.id] = o; });
const WIN = AM.collections.cropWindows.records;
const winIds = new Set(WIN.map((w) => w.windowId));

const server = await serve(PORT);
const { browser, page, errors, failed } = await open({ port: PORT });

const ids = await caseIds(page);
/* Escolhe uma amostra que cobre os estados, nao os doze primeiros da lista:
   verificado, so candidato pendente, com janela, sem janela, e cada status. */
const pick = [];
const want = (fn) => { const hit = ids.find((i) => !pick.includes(i) && byId[i] && fn(byId[i])); if (hit) pick.push(hit); };
want((o) => (o.productLinks || []).some((l) => l.strength === 'VERIFIED_LABEL_MATCH'));
want((o) => (o.productLinks || []).length && !(o.productLinks || []).some((l) => l.strength === 'VERIFIED_LABEL_MATCH'));
want((o) => o.windowStart);
want((o) => !o.windowStart);
for (const st of ['ACT_NOW', 'PREPARE_NOW', 'FUTURE_PREPARATION', 'TO_VALIDATE']) want((o) => o.status === st);
for (const ar of ['SUPPLY', 'MARKETING', 'REGULATORY', 'SCIENCE_TECHNICAL']) want((o) => (o.actionMap || []).includes(ar));
want((o) => (o.evidenceIds || []).some((e) => /^IT-WIN/.test(e)));
for (const i of ids) { if (pick.length >= WANT) break; if (!pick.includes(i)) pick.push(i); }

const rows = [];
for (const id of pick.slice(0, WANT)) {
  const o = byId[id];
  if (!o) continue;
  await clickTitle(page, 'Radar delle Opportunità');
  const opened = await openCase(page, id, 600);
  if (!opened) { rows.push({ id, error: 'card not clickable' }); continue; }
  const txt = await screenText(page);
  const has = (v) => !!v && txt.includes(String(v));

  /* MODELO TEM  ->  TELA MOSTRA */
  const prodNames = (o.productLinks || []).map((l) => l.name || l.product).filter(Boolean);
  const areas = o.actionMap || [];
  const evIds = o.evidenceIds || [];
  const srcIds = o.sourceIds || [];

  rows.push({
    id,
    crop: (o.cropKeys || [])[0] || o.crop,
    status: o.status,
    /* conteudo: um detalhe vazio e o que tinha 1966 caracteres */
    chars: txt.length,
    hasContent: txt.length > 2500,
    /* produto: pelo menos um NOME do modelo tem de aparecer escrito */
    modelHasProduct: prodNames.length > 0,
    productVisible: prodNames.some((n) => has(n)),
    productShown: prodNames.filter((n) => has(n)).length,
    /* mapa de acoes: a area tem de aparecer pelo nome traduzido */
    modelHasActionMap: areas.length > 0,
    actionMapVisible: areas.length > 0 && txt.includes('MAPPA DELLE AZIONI'),
    /* evidencia: o gate exige que as linhas existam, nao so a contagem */
    modelHasEvidence: evIds.length > 0,
    evidenceVisible: evIds.length > 0 && txt.includes('PROVE E FONTI'),
    /* fonte navegavel */
    modelHasSources: srcIds.length > 0,
    sourcesVisible: srcIds.length > 0 && txt.includes('FONTI DEL CASO'),
    /* janela: so conta como ligada quando o proprio record a declara */
    modelHasWindow: !!(o.windowStart || o.windowEnd || o.windowState),
    windowVisible: !!(o.windowStart && has(String(o.windowStart))),
    /* ══ OD6 · «DIRLO A PAROLE» NON E «DIRE QUELLA FRASE» ═══════════════
       La regola e: se non c'e finestra, lo schermo NON deve tacere. Il
       controllo pero cercava una stringa precisa — «Nessuna finestra
       dichiarata» — nata quando quella era l'unica cosa che si sapeva dire.

       Ora il motore dichiara la finestra AGRONOMICA anche dove non esiste
       una finestra colturale con date: tipo, regola e stato attuale, a
       parole. Lo schermo dice DI PIU, e il portone lo contava come silenzio.

           UN PORTONE CHE CERCA UNA FRASE MISURA LA FRASE.
           QUELLO CHE VOLEVAMO MISURARE E IL SILENZIO.

       Vale quindi qualunque enunciato esplicito sulla finestra: la frase
       storica, oppure una di quelle che il dizionario della riunione produce
       da WINDOW_TYPE / WINDOW_RULE_STATE / WINDOW_OPEN_NOW. */
    windowHonest: !(o.windowStart || o.windowEnd || o.windowState)
      ? (txt.includes('Nessuna finestra dichiarata')
         || txt.includes('Finestra agronomica aperta')
         || txt.includes('Nessuna condizione dichiarata')
         || txt.includes('Condizione nota; stato attuale non ancora misurato')
         || /Finestra definita d/.test(txt)
         || txt.includes('osservazione in campo')
         || txt.includes('Obbligo amministrativo'))
      : true,
    /* RELATIONSHIP: nenhuma janela pode ser mostrada se o id nao resolve */
    citesUnresolvedWindow: evIds.filter((e) => /^IT-WIN/.test(e) && !winIds.has(e)).length,
  });
}

/* ── RELATIONSHIP: o nome de um produto e um CAMPO, nao uma ocorrencia ─────
   Procurar o nome no texto da pagina casa «FORZA» dentro de «LA FORZA DELLA
   RELAZIONE», porque text-transform:uppercase entra no innerText — e assim o
   portao acusava onze relacoes inventadas que nao existiam.

       MEDE-SE A CASA DO NOME (data-product), NAO O TEXTO DA PAGINA.

   E a relacao valida nao e so `productLinks`: um caso de preparacao normativa
   nomeia produtos atraves da substancia ativa que a UE vai reavaliar, e isso e
   uma relacao DECLARADA pelo modelo (evidencia RFF_/AI_/IT-PRD), nao uma
   semelhanca. O portao aceita o grafo declarado, e so ele. */
let phantom = 0;
const allProductNames = new Set(AM.collections.products.records.map((x) => x.name).filter(Boolean));
const regProducts = AM.collections.productsRegulatory.records;
const regById = {}; regProducts.forEach((r) => { if (r.id) regById[r.id] = r; });
for (const r of rows) {
  const o = byId[r.id];
  if (!o) continue;
  const declared = new Set((o.productLinks || []).map((l) => l.name || l.product).filter(Boolean));
  /* ══ IL PORTAFOGLIO DEL MOTORE E UNA RELAZIONE DICHIARATA ═══════════════
     `productLinks` e la lettura del pacchetto grezzo. Lo snapshot canonico
     pubblica PORTFOLIO_MATCHES — il prodotto unito al caso per NUMERO DI
     REGISTRAZIONE, con etichetta e catalogo verificati — ed e quello che
     l'eroe mostra dal build della riunione in poi.

     Misurato: i cinque «prodotti fantasma» segnalati erano, uno per uno,
     esattamente i prodotti che lo snapshot dichiara. Non erano inventati
     dalla schermata: erano dichiarati da una fonte che questo portone non
     leggeva ancora.

         UN PRODOTTO NON E UN FANTASMA PERCHE IO NON SO DA DOVE VIENE.
         E UN FANTASMA SE NESSUNO LO DICHIARA. */
  for (const pm of ((o.meeting && o.meeting.PORTFOLIO_MATCHES) || [])) {
    if (pm && pm.PRODUCT_NAME) declared.add(pm.PRODUCT_NAME);
  }
  /* produtos citados por id de registo nas proprias evidencias do caso */
  for (const eid of (o.evidenceIds || [])) {
    const rec = regById[eid];
    if (rec && rec.name) declared.add(rec.name);
  }
  /* produtos que partilham a substancia ativa citada pelo caso — a relacao que
     um caso O5_REGULATORY_PREPARATION declara ao nomear a substancia */
  const subs = (o.evidenceIds || []).filter((e) => /^(AI_|RFF_)/.test(e))
    .map((e) => e.replace(/^(AI_|RFF_)/, '').replace(/_/g, ' ').toUpperCase());
  if (subs.length) {
    for (const pr of regProducts) {
      const ai = (pr.ai || []).map((x) => String(x).toUpperCase());
      if (ai.some((a) => subs.some((sb) => a.includes(sb) || sb.includes(a)))) declared.add(pr.name);
    }
  }
  await clickTitle(page, 'Radar delle Opportunità');
  await openCase(page, r.id, 520);
  const shown = await page.evaluate(() => [...document.querySelectorAll('[data-product]')]
    .map((e) => (e.getAttribute('data-product') || '').trim()).filter(Boolean));
  for (const n of shown) {
    if (!allProductNames.has(n)) continue;      // nao e um nome de catalogo
    if (declared.has(n)) continue;              // relacao declarada pelo modelo
    phantom++; r.phantom = (r.phantom || []).concat(n);
  }
  r.namedSlots = shown.length;
}

await browser.close(); server.close();

/* ── juizo ────────────────────────────────────────────────────────────────── */
const ok = rows.filter((r) => !r.error);
const emptyDetails = ok.filter((r) => !r.hasContent).length;
const prodMissing = ok.filter((r) => r.modelHasProduct && !r.productVisible).length;
const amMissing = ok.filter((r) => r.modelHasActionMap && !r.actionMapVisible).length;
const evMissing = ok.filter((r) => r.modelHasEvidence && !r.evidenceVisible).length;
const srcMissing = ok.filter((r) => r.modelHasSources && !r.sourcesVisible).length;
const winDishonest = ok.filter((r) => !r.windowHonest).length;
const winLinked = ok.filter((r) => r.modelHasWindow && r.windowVisible).length;

console.log('\n  SINTONIA · OPPORTUNITY_DETAIL_COMPLETENESS_GATE + OPPORTUNITY_RELATIONSHIP_GATE');
console.log('  ' + '─'.repeat(100));
console.log(line(emptyDetails === 0, 'OD1', 'No opened detail is empty (>2500 chars)', 0, emptyDetails));
console.log(line(prodMissing === 0, 'OD2', 'Model has a product -> a NAME is on screen', 0, prodMissing));
console.log(line(amMissing === 0, 'OD3', 'Model has an action map -> it is on screen', 0, amMissing));
console.log(line(evMissing === 0, 'OD4', 'Model has evidence -> the rows are on screen', 0, evMissing));
console.log(line(srcMissing === 0, 'OD5', 'Model has sources -> they are on screen', 0, srcMissing));
console.log(line(winDishonest === 0, 'OD6', 'No window -> the screen says so, in words', 0, winDishonest));
console.log(line(phantom === 0, 'OR1', 'No product named that the model does not link', 0, phantom));
console.log(line(errors.length === 0, 'OR2', 'No console error while opening details', 0, errors.length));
console.log('  ' + '─'.repeat(100));
console.log(`  DETALHES TESTADOS = ${ok.length} · COMPLETOS = ${ok.length - emptyDetails} · VAZIOS = ${emptyDetails}`);
console.log(`  COM PRODUTO NO MODELO = ${ok.filter((r) => r.modelHasProduct).length} · PRODUTO VISIVEL = ${ok.filter((r) => r.productVisible).length}`);
console.log(`  COM ACTION MAP = ${ok.filter((r) => r.modelHasActionMap).length} · VISIVEL = ${ok.filter((r) => r.actionMapVisible).length}`);
console.log(`  COM EVIDENCIA = ${ok.filter((r) => r.modelHasEvidence).length} · NAVEGAVEL = ${ok.filter((r) => r.evidenceVisible).length}`);
console.log(`  COM JANELA REAL = ${ok.filter((r) => r.modelHasWindow).length} · CORRETAMENTE LIGADA = ${winLinked}`);
console.log(`  referencias IT-WIN que nao resolvem neste pacote = ${ok.reduce((a, r) => a + (r.citesUnresolvedWindow || 0), 0)} (declaradas, nunca ligadas)`);
console.log('\n  ' + 'ID'.padEnd(20) + 'CHARS  PROD  MAPA  PROV  FONT  JANELA');
for (const r of rows) {
  if (r.error) { console.log('  ' + r.id.padEnd(20) + C.r(r.error)); continue; }
  const m = (b, na) => (na ? C.d(' n.a.') : b ? C.g('  yes') : C.r('   NO'));
  console.log('  ' + r.id.padEnd(20) + String(r.chars).padStart(5)
    + m(r.productVisible, !r.modelHasProduct) + m(r.actionMapVisible, !r.modelHasActionMap)
    + m(r.evidenceVisible, !r.modelHasEvidence) + m(r.sourcesVisible, !r.modelHasSources)
    + m(r.windowVisible, !r.modelHasWindow));
}
if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ rows, phantom }, null, 1));
const FAIL = emptyDetails || prodMissing || amMissing || evMissing || srcMissing || winDishonest || phantom || errors.length;
process.exit(FAIL ? 1 : 0);
