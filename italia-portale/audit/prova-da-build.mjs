/* SINTONIA · A BUILD, CORRIDA NUMA COPIA QUE SO TEM O QUE SOBE
   ---------------------------------------------------------------------------
   node audit/prova-da-build.mjs

   O `.vercelignore` decide o que chega ao contentor. Correr `npm run prebuild`
   NESTE repositorio prova que o portao passa com TODOS os ficheiros presentes —
   e nao e essa a pergunta. A pergunta e se passa com os que sobem.

       CORRER O PORTAO ONDE ESTA TUDO NAO PROVA A BUILD.
       PROVA QUE O DISCO ESTA COMPLETO.

   Medido a 06-09-2026: um import novo em `ingestion-provenance.mjs` apontava
   para `lib/pacote.mjs`, que o `.vercelignore` nao libertava. Aqui passava;
   na Vercel morria em MODULE_NOT_FOUND, tres deploys seguidos em ERROR.

   Este script monta uma copia com o conjunto MINIMO que a build precisa —
   package.json, vercel.json, a pasta publicada e a fechadura de audit/ que o
   `.vercelignore` liberta — e corre `npm run prebuild` la dentro.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const VI = fs.readFileSync(path.join(ROOT, '.vercelignore'), 'utf8')
  .split('\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('#'));
/* o que o .vercelignore LIBERTA de audit/ — nada mais de audit/ viaja */
const LIBERTOS = VI.filter((l) => l.startsWith('!/italia-portale/audit/'))
  .map((l) => l.slice('!/italia-portale/audit/'.length))
  .filter((f) => !f.endsWith('/'));

const OUT = fs.mkdtempSync(path.join(os.tmpdir(), 'sintonia-build-'));
const copia = (rel) => {
  const src = path.join(ROOT, rel);
  if (!fs.existsSync(src)) return false;
  const dst = path.join(OUT, rel);
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.cpSync(src, dst, { recursive: true });
  return true;
};

const faltam = [];
for (const rel of ['package.json', 'vercel.json', 'italia-portale/client']) {
  if (!copia(rel)) faltam.push(rel);
}
for (const f of LIBERTOS) {
  if (!copia(path.join('italia-portale', 'audit', f))) faltam.push(`audit/${f}`);
}

const G = '\x1b[32m', R = '\x1b[31m', X = '\x1b[0m';
console.log('');
console.log('  SINTONIA · A BUILD NUMA COPIA COM SO O QUE SOBE');
console.log('  ' + '-'.repeat(94));
console.log(`  copia em ${OUT}`);
console.log(`  de audit/ subiram ${LIBERTOS.length}: ${LIBERTOS.join(' ')}`);
if (faltam.length) {
  console.log(`  ${R}FALTAM NO DISCO${X}  ${faltam.join(' ')}`);
  process.exit(1);
}
let ok = true, saida = '';
try {
  saida = execFileSync('npm', ['run', 'prebuild'], { cwd: OUT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
} catch (e) {
  ok = false;
  saida = String(e.stdout || '') + String(e.stderr || '');
}
for (const l of saida.split('\n').filter(Boolean).slice(-14)) console.log('        ' + l);
console.log('  ' + '-'.repeat(94));
console.log(`  ${ok ? G + 'A BUILD PASSA' + X : R + 'A BUILD MORRE' + X} com o conjunto que a Vercel recebe`);
console.log('');
fs.rmSync(OUT, { recursive: true, force: true });
process.exit(ok ? 0 : 1);
