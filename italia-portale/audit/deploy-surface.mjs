/* SINTONIA ITALIA · LA SUPERFICIE PUBBLICA DEL DEPLOY
   ---------------------------------------------------------------------------
   node audit/deploy-surface.mjs [--base https://…]

   Un deploy statico serve QUELLO CHE GLI VIENE DATO. L'integrazione Git parte
   dalla RADICE del repository, e la radice di questo repository contiene
   l'archivio di ricerca, i pacchetti canonici e il codice di audit. Senza una
   regola esplicita tutto questo diventa scaricabile da chiunque abbia l'URL.

       IL SITO E UNA CARTELLA. IL REPOSITORY E UN ARCHIVIO.
       PUBBLICARE IL SECONDO PER RAGGIUNGERE IL PRIMO NON E UN DETTAGLIO
       DI CONFIGURAZIONE: E UNA FUGA DI DOCUMENTI.

   Senza --base controlla il CONTRATTO (vercel.json + .vercelignore).
   Con --base controlla la REALTA: interroga l'URL vero e pretende che le vie
   interne non rispondano 200 e che il portale risponda.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = arg('base', null);

const OUT_DIR = 'italia-portale/client';
/* Vie che non devono MAI rispondere 200 su un URL pubblico. */
const FORBIDDEN = [
  '/italia-portale/audit/checks.mjs',
  '/italia-portale/audit/lang.mjs',
  '/italia-portale/audit/opportunity-trace.mjs',
  '/build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip',
  '/build/ITALY-REALITY-HANDOFF-V2/MANIFEST.json',
  '/build/ITALY-REALITY-HANDOFF-V2/PREVIOUS-HANDOFF/02-RESEARCH-ARCHIVE/ITALY-OPPORTUNITY-CANDIDATES-REAL.md',
  '/scripts/site_v21_ingest.py',
  '/scripts/v21_cadeia.sh',
  '/research', '/data', '/docs', '/handoff', '/supabase', '/tests',
  '/README.md',
  '/italia-portale/ACCETTAZIONE.md',
  '/italia-portale/RICEVITORE-V2.1.md',
  '/italia-portale/client/LEGGIMI.md',
  '/.env', '/.env.local', '/.vercel/project.json', '/.gitignore',
  /* e le stesse vie come se la cartella client fosse la radice servita */
  '/audit/checks.mjs', '/LEGGIMI.md',
  /* configurazione di hosting che viaggiava dentro la cartella client */
  '/vercel.json', '/.vercelignore',
  '/_ds/adama-brandwell/_adherence.oxlintrc.json',
];
/* Vie che DEVONO rispondere: se queste cadono, la protezione ha spento il sito. */
const REQUIRED = ['/portale.html', '/italy-handoff-v21.js', '/italy-app-model.js', '/index.html'];

const fail = [];
const pass = [];

/* ---- 1. IL CONTRATTO ---------------------------------------------------- */
const vjPath = path.join(ROOT, 'vercel.json');
if (!fs.existsSync(vjPath)) fail.push('vercel.json assente dalla radice: il deploy servirebbe tutto il repository');
else {
  const vj = JSON.parse(fs.readFileSync(vjPath, 'utf8'));
  if (vj.outputDirectory !== OUT_DIR) {
    fail.push(`vercel.json outputDirectory = ${JSON.stringify(vj.outputDirectory)} · atteso ${JSON.stringify(OUT_DIR)}`);
  } else pass.push(`vercel.json serve solo ${OUT_DIR}`);
}
const viPath = path.join(ROOT, '.vercelignore');
if (!fs.existsSync(viPath)) fail.push('.vercelignore assente dalla radice');
else {
  const vi = fs.readFileSync(viPath, 'utf8');
  const must = ['/build', '/research', '/data', '/scripts', '/italia-portale/audit', '.env', '.vercel', '*.md',
    '/italia-portale/client/vercel.json', '/italia-portale/client/.vercelignore'];
  const miss = must.filter((m) => !vi.split('\n').some((l) => l.trim() === m));
  if (miss.length) fail.push(`.vercelignore non esclude: ${miss.join(' ')}`);
  else pass.push('.vercelignore esclude archivio, pacchetti, script, audit e segreti');
}

/* ---- 2. LA REALTA ------------------------------------------------------- */
if (BASE) {
  const code = (u) => {
    try {
      return Number(execFileSync('curl', ['-sS', '-o', '/dev/null', '-w', '%{http_code}',
        '--max-time', '45', '-L', u], { encoding: 'utf8' }).trim());
    } catch { return 0; }
  };
  for (const p of FORBIDDEN) {
    const c = code(BASE + p);
    if (c === 200) fail.push(`ESPOSTO pubblicamente (HTTP 200): ${p}`);
  }
  pass.push(`${FORBIDDEN.length} vie interne interrogate su ${BASE}`);
  let reachable = 0;
  for (const p of REQUIRED) {
    const c = code(BASE + p);
    if (c !== 200) fail.push(`il sito non risponde dove deve (HTTP ${c}): ${p}`);
    else reachable++;
  }
  /* Non-vacuita: se NESSUNA via richiesta risponde, il controllo sopra sarebbe
     "verde" solo perche non ha trovato nulla da controllare. */
  if (reachable === 0) fail.push('nessuna via del sito ha risposto: il controllo non ha misurato niente');
  else pass.push(`${reachable}/${REQUIRED.length} vie del portale raggiungibili`);
} else {
  pass.push('nessun --base: verificato solo il contratto, non l\'URL pubblicato');
}

const G = '\x1b[32m', R = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';
console.log('\n  SINTONIA ITALY · DEPLOY PUBLIC SURFACE' + (BASE ? `   (${BASE})` : '   (contratto)'));
console.log('  ' + '-'.repeat(94));
for (const p of pass) console.log(`  ${G}OK${X}   ${p}`);
for (const f of fail) console.log(`  ${R}FAIL${X} ${f}`);
console.log('  ' + '-'.repeat(94));
console.log(`  ${fail.length} problema/i di superficie pubblica\n`);
process.exit(fail.length === 0 ? 0 : 1);
