/* SINTONIA ITALIA · LO SPECCHIO DEL DEPLOY
   ---------------------------------------------------------------------------
   node audit/mirror.mjs --base https://…  [--out dir]

   Il Chromium di questa sandbox non attraversa il proxy di uscita: la stessa
   pagina che curl scarica gli restituisce ERR_CONNECTION_RESET. Aprire allora
   la CARTELLA LOCALE e chiamarla «produzione» sarebbe la peggiore delle prove,
   perche e esattamente cio che il deploy potrebbe non star servendo.

       NON SI PROVA IL FILE CHE HO SCRITTO. SI PROVA IL BYTE PUBBLICATO.

   Quindi questo script SCARICA con curl ogni file che la cartella pubblicata
   contiene, dall'indirizzo vero, e li mette in una copia. Poi confronta byte a
   byte con il disco: se un file manca, e diverso o risponde con un codice
   sbagliato, lo dice per nome. Chi apre lo specchio nel browser apre i byte
   che il cliente riceve, non i propri.

   Uscita 0 solo se OGNI file pubblicato e identico a quello in repo.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', 'client');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = String(arg('base', '') || '').replace(/\/$/, '');
const OUT = arg('out', path.join('/tmp', 'sintonia-specchio'));
if (!BASE) { console.error('  serve --base https://…'); process.exit(2); }

const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const walk = (dir, base = '') => fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
  const rel = base ? `${base}/${e.name}` : e.name;
  return e.isDirectory() ? walk(path.join(dir, e.name), rel) : [rel];
});

/* Cio che .vercelignore toglie NON deve rispondere 200: e il contratto della
   superficie pubblica (audit/deploy-surface.mjs lo prova dall'altro lato).
   Qui si legge lo stesso file, cosi le due prove non possono divergere. */
const IGNORE = fs.readFileSync(path.resolve(HERE, '..', '..', '.vercelignore'), 'utf8')
  .split('\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('#') && !l.startsWith('!'))
  .filter((l) => l.startsWith('/italia-portale/client/'))
  .map((l) => l.slice('/italia-portale/client/'.length));
/* .vercelignore esclude anche per estensione, con le righe «*.md». Si legge
   anche quello, invece di scoprire un 404 e chiamarlo differenza. */
const IGNORE_EXT = fs.readFileSync(path.resolve(HERE, '..', '..', '.vercelignore'), 'utf8')
  .split('\n').map((l) => l.trim())
  .filter((l) => /^(\*\*\/)?\*\.[A-Za-z0-9]+$/.test(l))
  .map((l) => l.slice(l.lastIndexOf('.')));
const ESCLUSO = (rel) => IGNORE.includes(rel) || rel === '.gitignore'
  || IGNORE_EXT.includes(path.extname(rel));

/* La Vercel inietta la propria barra di commento nelle ANTEPRIME — un tag
   <script> verso vercel.live che non esiste in produzione e non e nostro.
   Si nomina, non si ignora in silenzio. */
const INIEZIONE_ANTEPRIMA = /<script async data-explicit-opt-in="true" data-deployment-id="[^"]*" src="https:\/\/vercel\.live\/[^"]*"><\/script>\s*$/;

const files = walk(CLIENT).sort();
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const bad = [], esclusi = [], iniettati = [];
let same = 0;
for (const rel of files) {
  const local = fs.readFileSync(path.join(CLIENT, rel));
  const dest = path.join(OUT, rel);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (ESCLUSO(rel)) { esclusi.push(rel); continue; }
  let code = '000';
  try {
    /* --compressed perche la Vercel serve gzip: senza, i byte confrontati
       sarebbero quelli compressi e ogni file risulterebbe diverso. */
    const out = execFileSync('curl', ['-sS', '--compressed', '-L', '-o', dest,
      '-w', '%{http_code}', `${BASE}/${rel}`], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
    code = out.trim();
  } catch (e) { bad.push(`${rel}: curl ha fallito — ${String(e.message).slice(0, 80)}`); continue; }
  if (code !== '200') { bad.push(`${rel}: HTTP ${code}`); continue; }
  const got = fs.readFileSync(dest);
  if (sha(got) === sha(local)) { same += 1; continue; }
  /* Se l'unica differenza e la barra dell'anteprima, il byte nostro e identico. */
  const ripulito = got.toString('utf8').replace(INIEZIONE_ANTEPRIMA, '').replace(/\s*$/, '');
  if (sha(Buffer.from(ripulito, 'utf8')) === sha(Buffer.from(local.toString('utf8').replace(/\s*$/, ''), 'utf8'))) {
    same += 1; iniettati.push(rel); continue;
  }
  bad.push(`${rel}: ${local.length} B in repo, ${got.length} B pubblicati — sha diverso`);
}

const G = '\x1b[32m', R = '\x1b[31m', X = '\x1b[0m';
console.log('');
console.log(`  SINTONIA · SPECCHIO DEL DEPLOY   (${BASE})`);
console.log('  ' + '-'.repeat(94));
console.log(`  ${bad.length ? R + 'DIFFERENZE' + X : G + 'IDENTICO' + X}   ${same}/${files.length - esclusi.length} file serviti sono byte per byte quelli del repo`);
for (const b of bad.slice(0, 20)) console.log(`        ${b}`);
if (esclusi.length) console.log(`        ${esclusi.length} file NON serviti per contratto (.vercelignore): ${esclusi.join(', ')}`);
if (iniettati.length) console.log(`        ${iniettati.length} con la barra di commento che la Vercel inietta nelle anteprime: ${iniettati.join(', ')}`);
console.log(`  copia in ${OUT}`);
console.log('  ' + '-'.repeat(94));
console.log('');
process.exit(bad.length ? 1 : 0);
