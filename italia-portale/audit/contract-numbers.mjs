/* SINTONIA ITALIA · I NUMERI DEL CONTRATTO, LETTI DAL DOCUMENTO
   ---------------------------------------------------------------------------
   node audit/contract-numbers.mjs

   RICEVITORE-V2.1.md non e prosa: e la tabella che dice ad ADAMA quanto e
   grande ogni famiglia. Finche quel numero viveva solo nel markdown, il
   sistema poteva cambiare e il documento restare fermo — e chi legge il
   documento non ha modo di accorgersene.

   Questo controllo NON scrive i numeri: li LEGGE dalla tabella pubblicata e
   pretende che il pacchetto spedito li confermi uno per uno. Se il documento
   dice 561 e il pacchetto ne porta 577, fallisce — e fallisce dalla parte
   giusta, perche il documento e la promessa.

   Due numeri hanno una lettura dichiarata, non un conteggio grezzo:
     sources        189 righe spedite = 187 fonti reali + 2 SOURCE_SENTINEL
     competitor     577 nel corpus, 569 pubblicabili (competitor-population)
   Entrambe le letture devono comparire nel documento, altrimenti il numero
   sarebbe vero e la frase falsa.

   Un controllo che non trova la tabella fallisce: non aver guardato non e
   un'assoluzione.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadData } from './lib/harness.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DOC = path.resolve(HERE, '..', 'RICEVITORE-V2.1.md');
const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';

export function contractRows() {
const md = fs.readFileSync(DOC, 'utf8');
const w = loadData();
const H = w.ITALY_HANDOFF_V21;
const M = w.ITALY_APP_MODEL;

/* ── 1 · la tabella, letta ─────────────────────────────────────────────── */
/* Il documento porta DUE censimenti: quello di oggi (| famiglia | agora |
   antes |) e quello storico di com'era prima. Solo il primo e una promessa;
   il secondo e memoria, e deve restare com'e. */
const num = (s) => Number(String(s).replace(/[.\s]/g, ''));
const lines = md.split('\n');
const head = lines.findIndex((l) => /^\|\s*fam[ií]lia\s*\|\s*agora\s*\|/i.test(l));
const claimed = new Map();
if (head >= 0) {
  for (let i = head + 2; i < lines.length && lines[i].startsWith('|'); i++) {
    const m = lines[i].match(/^\|\s*`([A-Za-z]+)`[^|]*\|\s*\**([\d.]+)\**\s*\|/);
    if (m) claimed.set(m[1], num(m[2]));
  }
}
/* le due misure che il documento enuncia in prosa, non in tabella */
const prose = (re) => { const m = md.match(re); return m ? num(m[1]) : null; };
const claimedCrops = prose(/\*\*CULTURAS\s*=\s*(\d+)\*\*/i);
const claimedTargets = prose(/\*\*ALVOS\s*=\s*(\d+)\*\*/i);
const claimedWeight = prose(/`cropEconomicWeight`\s*\((\d+)\s+culturas\)/i);

/* ── 2 · il pacchetto, misurato ────────────────────────────────────────── */
const len = (k) => (Array.isArray(H[k]) ? H[k].length : null);
const measured = new Map();
for (const k of claimed.keys()) {
  if (k === 'cropWindows') measured.set(k, M.collections.cropWindows.records.length);
  else measured.set(k, len(k));
}
/* CULTURAS e ALVOS sono ricontati dalle 2.030 duplicate, non digitati */
const rel = H.productRelationships || [];
/* il vocabolario e quello SCRITTO IN ETICHETTA, non la chiave canonica: sono
   due misure diverse e il documento parla della prima. */
const distinct = (k) => new Set(rel.map((r) => r[k]).filter(Boolean)).size;
const measuredCrops = distinct('CROP_ON_LABEL');
const measuredTargets = distinct('TARGET_ON_LABEL');
const measuredWeight = M.collections.cropEconomicWeight.count;

/* ── 3 · le due letture dichiarate ─────────────────────────────────────── */
const srcRows = len('sources');
const srcReal = M.collections.sources.count;
const srcSentinel = srcRows - srcReal;
const compCorpus = len('competitorActivities');

const rows = [];
const put = (id, title, exp, got, extra) =>
  rows.push({ id, title, exp, got, pass: exp !== null && exp === got, extra });

let i = 0;
for (const [k, v] of claimed) {
  const got = measured.get(k);
  /* sources: il documento pubblica le righe spedite, il modello ne conta 187 */
  if (k === 'sources') {
    put(`CN${++i}`, `${k} · righe spedite`, v, got,
      `${srcReal} fonti reali + ${srcSentinel} SOURCE_SENTINEL`);
    continue;
  }
  put(`CN${++i}`, k, v, got);
}
put(`CN${++i}`, 'CULTURAS ricontate dalle duplicate', claimedCrops, measuredCrops);
put(`CN${++i}`, 'ALVOS ricontati dalle duplicate', claimedTargets, measuredTargets);
put(`CN${++i}`, 'cropEconomicWeight ricontato, non da fixture', claimedWeight, measuredWeight);

/* Le letture devono essere SCRITTE, e scritte DOVE si parla della famiglia:
   una cifra giusta persa in un altro paragrafo non spiega niente a chi legge.
   Cerchiamo quindi il paragrafo che nomina la famiglia e pretendiamo che sia
   li che i due numeri compaiono. */
const paras = md.split(/\n\s*\n/);
const paraWith = (re) => paras.filter((p) => re.test(p));
const hasAll = (list, nums) =>
  list.some((p) => nums.every((n) => new RegExp(`\\b${n}\\b`).test(p)));

const srcParas = paraWith(/SOURCE_SENTINEL/);
const saysSentinel = hasAll(srcParas, [srcRows, srcReal, srcSentinel]);
const compParas = paraWith(/competitorActivities|concorrent|QA_UNREVIEWED/i);
const saysPublishable = hasAll(compParas, [compCorpus, 569]);
rows.push({ id: `CN${++i}`, title: 'il documento dichiara le 187 fonti reali e le 2 sentinelle',
  exp: 'dichiarato', got: saysSentinel ? 'dichiarato' : 'silenzioso', pass: saysSentinel });
rows.push({ id: `CN${++i}`, title: 'il documento dichiara corpus 577 e pubblicabili 569',
  exp: 'dichiarato', got: saysPublishable ? 'dichiarato' : 'silenzioso', pass: saysPublishable });

if (head < 0 || !claimed.size) {
  rows.length = 0;
  rows.push({ id: 'CN0', title: `nessuna riga letta da ${path.basename(DOC)}`,
    exp: 'una tabella', got: 'niente', pass: false });
}
return { rows, compCorpus, buildId: H.buildId };
}

/* ── CLI ───────────────────────────────────────────────────────────────── */
/* Importato da acceptance.mjs questo file deve solo ESPORRE la funzione: se
   stampasse e uscisse, spegnerebbe il rapporto che lo ha chiamato. */
const DIRECT = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (DIRECT) {
const { rows, compCorpus, buildId } = contractRows();

console.log('');
console.log('  SINTONIA ITALIA · I NUMERI DEL CONTRATTO');
console.log('  ' + '-'.repeat(96));
console.log(`  ${DIM}letti da ${path.relative(path.resolve(HERE, '..'), DOC)} · misurati sul pacchetto ${buildId}${X}`);
console.log('  ' + '-'.repeat(96));
const pad = (s, n) => String(s).slice(0, n).padEnd(n);
for (const r of rows) {
  console.log(`  ${r.pass ? G + 'PASS' + X : R + 'FAIL' + X}  ${pad(r.id, 5)} ${pad(r.title, 52)} ${DIM}doc${X} ${pad(r.exp, 10)} ${DIM}pacchetto${X} ${pad(r.got, 10)}${r.extra ? DIM + '  ' + r.extra + X : ''}`);
}
const ok = rows.filter((r) => r.pass).length;
console.log('  ' + '-'.repeat(96));
console.log(`  ${ok}/${rows.length} · corpus concorrenti ${compCorpus}, pubblicabili 569 (competitor-population)`);
console.log('');
process.exit(ok === rows.length ? 0 : 1);
}
