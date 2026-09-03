/* SINTONIA · PDF_GENERATION_GATE + PDF_CONTENT_TRUTH_GATE
   + CARD_ACTION_PDF_CONSISTENCY_GATE
   ---------------------------------------------------------------------------
   node audit/pdf-gate.mjs [--out dir] [--cases 4]

   Nao se declara um PDF olhando para o codigo que o gera. Este portao abre o
   portal, CLICA na oportunidade, CLICA no brief, CLICA em «Download PDF»,
   apanha o ficheiro que o browser escreveu, ABRE-O, e le TODAS as paginas.

       O FICHEIRO OU EXISTE E ABRE-SE, OU O PORTAO REPROVA.

   Depois compara o que a ficha diz, o que o detalhe diz e o que o PDF diz. Se
   as tres superficies contam verdades diferentes sobre o mesmo caso, reprova —
   e essa e a unica razao de este portao existir.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { serve, open, openCase, caseIds, clickTitle, clickSelector, screenText, C, line } from './lib/drive.mjs';
import { loadData } from './lib/harness.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUT = arg('out', '/tmp/sintonia-pdf');
const WANT = Number(arg('cases', 4));
const PORT = 8957;
fs.mkdirSync(OUT, { recursive: true });

const AM = loadData().ITALY_APP_MODEL;
const byId = {}; AM.collections.opportunities.records.forEach((o) => { byId[o.id] = o; });

const server = await serve(PORT);
const { browser, ctx, page, errors } = await open({ port: PORT });

const ids = (await caseIds(page)).slice(0, 40);
/* uma amostra que cobre os dois estados do vinculo */
const pick = [];
const want = (fn) => { const h = ids.find((i) => !pick.includes(i) && byId[i] && fn(byId[i])); if (h) pick.push(h); };
want((o) => (o.productLinks || []).some((l) => l.strength === 'VERIFIED_LABEL_MATCH'));
want((o) => (o.productLinks || []).length && !(o.productLinks || []).some((l) => l.strength === 'VERIFIED_LABEL_MATCH'));
want((o) => o.status === 'ACT_NOW');
want((o) => !o.windowStart);
for (const i of ids) { if (pick.length >= WANT) break; if (!pick.includes(i)) pick.push(i); }

/* pdf.js le o ficheiro como um leitor o leria: pagina a pagina. */
const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
async function readPdf(file) {
  const doc = await pdfjs.getDocument({ data: new Uint8Array(fs.readFileSync(file)), useSystemFonts: false }).promise;
  const pages = [];
  for (let i = 1; i <= doc.numPages; i++) {
    const pg = await doc.getPage(i);
    const c = await pg.getTextContent();
    pages.push(c.items.map((x) => x.str).join(' '));
  }
  return pages.join('\f');
}

const rows = [];
for (const id of pick.slice(0, WANT)) {
  const o = byId[id];
  const row = { id, crop: (o.cropKeys || [])[0] || o.crop };

  await clickTitle(page, 'Radar delle Opportunità');
  await openCase(page, id, 600);
  const detailTxt = await screenText(page);
  row.detailProducts = (o.productLinks || []).map((l) => l.name || l.product).filter((n) => detailTxt.includes(n));

  /* O MATERIAL COMERCIAL SO CONTA SE UM CLIQUE LA CHEGA.
     As pastilhas do detalhe declaram o seu departamento em data-brief-dept, e o
     portao carrega NESSA pastilha — nao numa palavra que por acaso esta na
     pagina. Um portao que adivinha onde clicar mede a sua propria sorte. */
  row.briefChips = await page.evaluate(() =>
    [...document.querySelectorAll('[data-brief-dept]')].map((e) => e.getAttribute('data-brief-dept')));
  await clickSelector(page, '[data-brief-dept]', 700);
  const briefTxt = await screenText(page);
  row.onBrief = (await page.$('[data-download-pdf] button')) !== null;

  if (!row.onBrief) { row.error = 'brief screen not reachable by click from the detail'; rows.push(row); continue; }

  /* ── O CLIQUE QUE TEM DE PRODUZIR UM FICHEIRO ───────────────────────────── */
  let dl = null;
  try {
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 15000 }),
      clickSelector(page, '[data-download-pdf] button', 200),
    ]);
    dl = download;
  } catch (e) { row.error = 'no download event: ' + String(e.message).slice(0, 80); }

  if (dl) {
    const file = path.join(OUT, id + '.pdf');
    await dl.saveAs(file);
    row.file = file;
    const buf = fs.readFileSync(file);
    row.bytes = buf.length;
    /* um PDF verdadeiro comeca por %PDF- e termina com %%EOF */
    row.validHeader = buf.slice(0, 5).toString() === '%PDF-';
    row.validTrailer = buf.slice(-1024).toString('latin1').includes('%%EOF');
    row.pages = (buf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
    /* ── ABRIR E LER TODAS AS PAGINAS ───────────────────────────────────────
       O visualizador do Chromium nao expoe o texto ao DOM em modo headless:
       pedir-lhe innerText devolve zero caracteres, e um portao que aceitasse
       zero teria dado PASS a um PDF que nunca leu.

           UM FICHEIRO QUE NAO SE CONSEGUE LER NAO ESTA VERIFICADO.

       pdf.js analisa o ficheiro a serio, pagina a pagina, e devolve o texto
       que la esta — incluindo o que sai da fonte LL Brown incorporada. */
    const text = await readPdf(file);
    row.text = text;
    row.pagesRead = text.split('\f').length;
    row.textLen = text.length;
    /* PDF_CONTENT_TRUTH · O QUE NUNCA PODE APARECER
       Com fronteira de palavra. Sem ela, «null» casa dentro de «non si afferma
       nulla» — italiano correcto — e o portao acusava tres documentos limpos.

           UM PORTAO QUE ACUSA O INOCENTE ENSINA A IGNORA-LO. */
    row.junk = [/\bundefined\b/, /\bnull\b/, /\bNaN\b/, /\[object Object\]/, /\{\{/, /\}\}/]
      .filter((re) => re.test(text)).map((re) => String(re));
    /* Um codigo entre parenteses DEPOIS da sua traducao — «non osservate
       (NOT_OBSERVED)» — e rastreabilidade declarada, nao um token a substituir
       uma palavra. Conta-se a parte; o que reprova e o token que fala sozinho. */
    const allTok = (text.match(/\b[A-Z][A-Z0-9]*(_[A-Z0-9]+)+\b/g) || []).filter((t, i, a) => a.indexOf(t) === i);
    row.traceCodes = allTok.filter((t) => new RegExp('\\(\\s*' + t + '\\s*\\)').test(text));
    row.rawTokens = allTok.filter((t) => !row.traceCodes.includes(t));
    /* UM PRODUTO SO SE DIZ VERIFICADO SE A REGUA O DISSER.
       Procurar /VERIFIC/ casava com «da verificare» — «por verificar», que diz
       exactamente o contrario. Mede-se a AFIRMACAO, na forma em que o gerador
       a escreve. */
    const verified = (o.productLinks || []).filter((l) => l.strength === 'VERIFIED_LABEL_MATCH').map((l) => l.name || l.product);
    /* Um veredito citado DEPOIS de a frase declarar que pertence a outras
       culturas nao e uma afirmacao sobre este caso: e o registo do produto,
       circunscrito em voz alta. O portao mede a afirmacao NAO circunscrita. */
    const unscoped = text
      .replace(/per ALTRE colture × problemi, non per questo caso[^]*?(?=(\n|$|CHE COSA|PRODOTTI|MOMENTO|MAPPA))/gi, ' ')
      .replace(/for OTHER crops × issues, not for this case[^]*?(?=(\n|$|WHAT|LINKED|TIMING|ACTION))/gi, ' ');
    const claimsVerified = /CORRISPONDENZA VERIFICATA SU ETICHETTA|VERIFIED LABEL MATCH/i.test(unscoped);
    row.verifiedInModel = verified.length;
    row.verifiedClaimUnsupported = claimsVerified && verified.length === 0;
    /* CARD -> DETALHE -> PDF: o nome do produto tem de sobreviver as tres */
    const named = (o.productLinks || []).map((l) => l.name || l.product);
    row.productsInPdf = named.filter((n) => text.includes(n));
    row.cropInPdf = !!row.crop && text.includes(row.crop);
    row.pdfHasActionMap = /MAPPA DELLE AZIONI|ACTION MAP/i.test(text);
    row.pdfHasTiming = /MOMENTO|TIMING/i.test(text);
    row.pdfSaysNoWindow = /Nessuna finestra dichiarata|No window is declared|finestra non stabilita|WINDOW NOT ESTABLISHED/i.test(text);
    row.windowHonest = (o.windowStart || o.windowEnd || o.windowState) ? true : row.pdfSaysNoWindow;
  }
  rows.push(row);
}

await browser.close(); server.close();

/* ── juizo ────────────────────────────────────────────────────────────────── */
const ok = rows.filter((r) => !r.error);
const generated = ok.filter((r) => r.file).length;
const invalid = ok.filter((r) => r.file && !(r.validHeader && r.validTrailer && r.pages > 0)).length;
const unreadable = ok.filter((r) => r.file && r.textLen < 200).length;
const junky = ok.filter((r) => (r.junk || []).length).length;
const tokenLeak = ok.filter((r) => (r.rawTokens || []).length).length;
const unsupported = ok.filter((r) => r.verifiedClaimUnsupported).length;
const prodLost = ok.filter((r) => r.detailProducts.length && !r.productsInPdf.length).length;
const winDishonest = ok.filter((r) => r.file && !r.windowHonest).length;

console.log('\n  SINTONIA · PDF_GENERATION + PDF_CONTENT_TRUTH + CARD_ACTION_PDF_CONSISTENCY');
console.log('  ' + '─'.repeat(100));
console.log(line(rows.every((r) => r.onBrief), 'PG1', 'The brief is reachable by real click from the detail', rows.length, rows.filter((r) => r.onBrief).length));
console.log(line(generated === ok.length && generated > 0, 'PG2', 'The click produces a real downloaded file', ok.length, generated));
console.log(line(invalid === 0, 'PG3', 'Every file is a valid PDF (header, trailer, pages)', 0, invalid));
console.log(line(unreadable === 0, 'PG4', 'Every PDF opens and yields readable text', 0, unreadable));
console.log(line(junky === 0, 'PT1', 'No undefined / null / NaN / JSON in any PDF', 0, junky));
console.log(line(tokenLeak === 0, 'PT2', 'No raw engine token printed in any PDF', 0, tokenLeak));
console.log(line(unsupported === 0, 'PT3', 'No VERIFIED claim the ruler does not support', 0, unsupported));
console.log(line(winDishonest === 0, 'PT4', 'No window -> the PDF says so, in words', 0, winDishonest));
console.log(line(prodLost === 0, 'CP1', 'A product named on the detail survives into the PDF', 0, prodLost));
console.log('  ' + '─'.repeat(100));
console.log(`  PDF REAL GERADO = ${generated > 0 ? 'YES' : 'NO'} · ficheiros = ${generated} · abertos e lidos por pdf.js`);
for (const r of rows) {
  if (r.error) { console.log(`  ${r.id.padEnd(20)} ${C.r(r.error)}`); continue; }
  console.log(`  ${r.id.padEnd(20)} ${String(r.bytes || 0).padStart(7)}B  ${String(r.pages || 0)}p  ${String(r.textLen || 0).padStart(5)} chars  `
    + `prod ${r.productsInPdf.length}/${r.detailProducts.length}  `
    + (r.pdfHasActionMap ? C.g('mapa') : C.r('SEM MAPA')) + '  '
    + (r.junk.length ? C.r('LIXO: ' + r.junk.join(' ')) : C.g('limpo'))
    + ((r.rawTokens || []).length ? C.r(' TOKEN: ' + r.rawTokens.slice(0, 3).join(',')) : ''));
}
if (errors.length) { console.log('\n  ERROS DE CONSOLA:'); errors.slice(0, 8).forEach((e) => console.log('   ' + C.r(e))); }
const traced = [...new Set(ok.flatMap((r) => r.traceCodes || []))];
if (traced.length) console.log(`\n  codigos de rastreio entre parenteses (declarados, nao contam como fuga): ${traced.join(', ')}`);
console.log(`\n  ficheiros em ${OUT}`);
const FAIL = rows.some((r) => r.error) || generated !== ok.length || invalid || unreadable || junky || tokenLeak || unsupported || prodLost || winDishonest;
process.exit(FAIL ? 1 : 0);
