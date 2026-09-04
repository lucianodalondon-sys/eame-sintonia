#!/usr/bin/env node
/* SINTONIA · PORTAO DE PROVENIENCIA DA INGESTAO
   ---------------------------------------------------------------------------
   O portal carregava TRES safras da mesma inteligencia e nenhuma delas sabia
   das outras:

     italy-handoff-v21.js embarcado  ACT_NOW 16 · PREPARE_NOW 11   (mais velho)
     o zip commitado em 55c2674      37 casos · sem MEETING_SURFACE_RULE
     a cadeia corrida em 55c2674     43 casos · V21-69bf448ac934a6d9   (canonico)

   `PREPARE_NOW` nao existe no vocabulario canonico atual. Estava embarcado, em
   onze casos, num artefacto de 5,6 MB cujo diff textual diz «2 insertions» —
   porque o ficheiro tem quatro linhas. Ninguem o veria a olho.

       UMA SAFRA VELHA NAO GRITA. ELA ESPERA QUE O ENXERTO FALHE.

   Este portao nao e dono de dado nenhum. Ele verifica o CONTRATO DE QUEM
   PRODUZ: o pacote que atravessa a fronteira do site tem de se identificar, tem
   de trazer a lei da superficie, e nao pode carregar estado revogado.

   O zip antigo serve de CONTROLE NEGATIVO: se este portao o aceitasse, nao
   estaria a medir nada.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { CLIENT } from './lib/harness.mjs';

const ING = path.resolve(CLIENT, '..', '..', 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST');

/* O que o contrato exige de QUALQUER pacote que atravesse a fronteira.
   A regra deixou de viver aqui quando o Python passou a precisar dela: uma
   regra escrita em duas linguas diverge na terceira vez que alguem a muda.
   Vive em CANONICAL-PACKAGE-CONTRACT.json, e este ficheiro le-a como todos. */
export const CONTRATO = JSON.parse(
  fs.readFileSync(new URL('./CANONICAL-PACKAGE-CONTRACT.json', import.meta.url), 'utf8'),
);
export const EXPECTED_BUILD_ID = CONTRATO.EXPECTED_BUILD_ID;
export const EXPECTED_CASES = CONTRATO.EXPECTED_CASES;
export const REVOKED_STATES = CONTRATO.REVOKED_STATES;
export const CANONICAL_STATES = CONTRATO.CANONICAL_STATES;
export const SURFACE_RULE_FIELDS = CONTRATO.SURFACE_RULE_FIELDS;

/* Le o artefacto embarcado como o browser o le: executando-o. */
export function embarcado(file = path.join(CLIENT, 'italy-handoff-v21.js')) {
  const g = { window: {} };
  vm.createContext(g);
  vm.runInContext(fs.readFileSync(file, 'utf8'), g);
  return g.window.ITALY_HANDOFF_V21;
}

/* A regra, aplicavel tanto ao pacote de origem como ao artefacto embarcado.
   Devolve a lista de razoes de RECUSA. Vazia = aceite. */
export function recusas({ buildId, cases, surfaceRule, states }) {
  const r = [];
  if (buildId !== EXPECTED_BUILD_ID) r.push(`BUILD_ID ${buildId || '(ausente)'} != ${EXPECTED_BUILD_ID}`);
  if (cases !== EXPECTED_CASES) r.push(`CASOS ${cases} != ${EXPECTED_CASES}`);
  if (!surfaceRule) r.push('MEETING_SURFACE_RULE ausente — a superficie teria de adivinhar a faixa');
  else {
    for (const f of SURFACE_RULE_FIELDS) {
      if (!(f in surfaceRule)) r.push(`MEETING_SURFACE_RULE sem ${f}`);
    }
  }
  for (const s of REVOKED_STATES) {
    if (states && states[s]) r.push(`ESTADO REVOGADO ${s} em ${states[s]} casos`);
  }
  return r;
}

const conta = (rows, f) => rows.reduce((a, o) => { const v = o[f]; if (v) a[v] = (a[v] || 0) + 1; return a; }, {});

/* Este ficheiro e portao E biblioteca: `snapshot-failure.mjs` importa a regra
   para nao a escrever duas vezes. Sem esta guarda, importar seria correr — e o
   segundo portao imprimia o primeiro no meio do seu proprio relatorio.

       QUEM E IMPORTADO NAO DEVE EXECUTAR. */
const E_O_PROGRAMA = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

const results = [];
const check = (id, title, fn) => {
  if (!E_O_PROGRAMA) return;
  try { results.push({ id, title, ...fn() }); }
  catch (e) { results.push({ id, title, pass: false, detail: [e.message] }); }
};

/* ── 1 · o pacote canonico passa ─────────────────────────────────────────── */
check('CANONICAL_PACKAGE_ACCEPTED', 'o pacote gerado por 55c2674 atravessa a fronteira', () => {
  const M = JSON.parse(fs.readFileSync(path.join(ING, 'APP-MANIFEST.json'), 'utf8'));
  const O = JSON.parse(fs.readFileSync(path.join(ING, 'OPPORTUNITIES.json'), 'utf8'));
  const rows = O.RECORDS || O;
  const r = recusas({ buildId: M.BUILD_ID, cases: rows.length, surfaceRule: M.MEETING_SURFACE_RULE, states: conta(rows, 'STATUS') });
  return { pass: r.length === 0, expected: 'zero recusas', measured: r.length, detail: r };
});

/* ── 2 · o zip antigo NAO passa. Controle negativo. ──────────────────────── */
check('STALE_PACKAGE_REJECTED', 'o zip historico e recusado, e por razoes nomeadas', () => {
  /* Reconstruido do que foi medido nele, para o portao nao depender de um zip
     que amanha pode nao estar no disco. Se o zip existir, e lido. */
  let stale = { buildId: 'V21-99226fbb90dcdbc2', cases: 37, surfaceRule: null, states: {} };
  const zipDir = process.env.SINTONIA_STALE_DIR;
  if (zipDir && fs.existsSync(path.join(zipDir, 'APP-MANIFEST.json'))) {
    const M = JSON.parse(fs.readFileSync(path.join(zipDir, 'APP-MANIFEST.json'), 'utf8'));
    const O = JSON.parse(fs.readFileSync(path.join(zipDir, 'OPPORTUNITIES.json'), 'utf8'));
    const rows = O.RECORDS || O;
    stale = { buildId: M.BUILD_ID, cases: rows.length, surfaceRule: M.MEETING_SURFACE_RULE, states: conta(rows, 'STATUS') };
  }
  const r = recusas(stale);
  return { pass: r.length > 0, expected: 'pelo menos uma recusa', measured: r.length, detail: r };
});

/* ── 3 · o artefacto embarcado ja e o canonico ───────────────────────────── */
check('BUILD_ID_MATCH', 'italy-handoff-v21.js carrega o BUILD_ID canonico', () => {
  const H = embarcado();
  return { pass: H.buildId === EXPECTED_BUILD_ID, expected: EXPECTED_BUILD_ID, measured: H.buildId, detail: [] };
});

check('NO_REVOKED_STATUS', 'nenhum estado revogado sobrevive no caminho executavel', () => {
  const H = embarcado();
  const st = conta(H.opportunities, 'STATUS');
  const bad = REVOKED_STATES.filter((s) => st[s]);
  return { pass: bad.length === 0, expected: 'zero', measured: bad.map((s) => `${s}=${st[s]}`).join(',') || 0, detail: [JSON.stringify(st)] };
});

check('43_CASE_IDS_PRESERVED', 'os 43 IDs do embarcado sao os 43 do pacote', () => {
  const H = embarcado();
  const O = JSON.parse(fs.readFileSync(path.join(ING, 'OPPORTUNITIES.json'), 'utf8'));
  const rows = O.RECORDS || O;
  const a = new Set(H.opportunities.map((o) => o.ID));
  const b = new Set(rows.map((o) => o.ID));
  const so_a = [...a].filter((x) => !b.has(x));
  const so_b = [...b].filter((x) => !a.has(x));
  return {
    pass: a.size === EXPECTED_CASES && so_a.length === 0 && so_b.length === 0,
    expected: `${EXPECTED_CASES} iguais`, measured: `${a.size} embarcados`,
    detail: [`so no embarcado: ${so_a.join(',') || '-'}`, `so no pacote: ${so_b.join(',') || '-'}`],
  };
});

check('CANONICAL_STATE_DISTRIBUTION', 'a distribuicao de estado e a declarada pelo contrato', () => {
  const H = embarcado();
  const st = conta(H.opportunities, 'STATUS');
  const bad = Object.entries(CANONICAL_STATES).filter(([k, v]) => st[k] !== v).map(([k, v]) => `${k}: esperado ${v}, medido ${st[k] || 0}`);
  return { pass: bad.length === 0, expected: JSON.stringify(CANONICAL_STATES), measured: JSON.stringify(st), detail: bad };
});

const fail = results.filter((r) => !r.pass);
if (!E_O_PROGRAMA) { /* importado como biblioteca: nao imprime, nao sai */ }
else {
console.log('== PORTAO DE PROVENIENCIA DA INGESTAO ==');
for (const r of results) {
  console.log(`  ${r.pass ? 'PASS' : 'FAIL'}  ${r.id.padEnd(30)} ${r.title}`);
  if (!r.pass || process.env.VERBOSE) (r.detail || []).forEach((d) => d && console.log(`        ${d}`));
}
console.log(`\n  ${fail.length ? 'FAIL' : 'PASS'} — ${results.length - fail.length}/${results.length}`);
process.exit(fail.length ? 1 : 0);
}
