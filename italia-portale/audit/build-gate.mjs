#!/usr/bin/env node
/* SINTONIA · PORTAO DA BUILD — fail-closed, no caminho normal
   ---------------------------------------------------------------------------
   A Linha B guarda uma cadeia geradora atrasada. Corrida aqui, `v21_cadeia.sh`
   produz V21-5d312cb90a0de01d: sem MEETING_SURFACE_RULE e com PREPARE_NOW de
   volta em onze casos. O artefacto embarcado hoje e o canonico — mas nada
   impedia alguem de regenerar e servir a safra velha sem se aperceber.

       UM PORTAO QUE SE CHAMA A PARTE E DISCIPLINA. NO CAMINHO, E REGRA.

   Por isso este ficheiro corre como `prebuild`: quem faz `npm run build` —
   e a Vercel faz, tanto na producao como no preview — passa por aqui antes de
   existir candidato. Nao ha bandeira para o desligar.

   Ele verifica duas coisas, e a segunda so quando existe o que verificar:

     1. O ARTEFACTO QUE VAI SER SERVIDO. Sempre. E o unico que chega ao cliente,
        e e o que sobrevive ao .vercelignore.
     2. O PACOTE LOCAL, se estiver no disco. E aqui que a cadeia stale seria
        apanhada: um pacote regenerado com o gerador atrasado nao atravessa.

   Falhar aberto seria pior do que nao ter portao: daria a sensacao de guarda
   com a garantia de nenhuma. Qualquer erro inesperado tambem e FAIL.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { recusas, embarcado, CONTRATO } from './ingestion-provenance.mjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..', '..');
const CLIENTE = path.join(RAIZ, 'italia-portale', 'client');
const PACOTE = path.join(RAIZ, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST');

const conta = (rows, f) => rows.reduce((a, o) => { const v = o[f]; if (v) a[v] = (a[v] || 0) + 1; return a; }, {});
const linhas = [];
let falhou = false;

function porta(id, o_que, fn) {
  let r;
  try { r = fn(); }
  catch (e) { r = { pass: false, detail: [`${e.message}`] }; }
  if (!r.pass) falhou = true;
  linhas.push({ id, o_que, ...r });
}

/* ── 1 · o que vai ser servido ───────────────────────────────────────────── */
/* MEETING_SURFACE_RULE nao viaja para o artefacto embarcado: vive no manifesto
   do pacote, e `site_v21_ingest.py` so atravessa BUILD_ID e as familias. Exigi-la
   aqui seria pedir ao artefacto uma prova que ele nao pode carregar — e um portao
   que reprova por impossibilidade nao mede nada. Ela e exigida no pacote, onde
   vive. Aqui exige-se o que o embarcado PODE provar, e prova por si:
   identidade, populacao, estado revogado e distribuicao. */
porta('ARTEFACTO_SERVIDO_E_CANONICO', 'italy-handoff-v21.js prova a sua proveniencia', () => {
  const f = path.join(CLIENTE, 'italy-handoff-v21.js');
  if (!fs.existsSync(f)) return { pass: false, detail: [`ausente: ${path.relative(RAIZ, f)}`] };
  const H = embarcado(f);
  const casos = H.opportunities || [];
  const st = conta(casos, 'STATUS');
  const r = [];
  if (H.buildId !== CONTRATO.EXPECTED_BUILD_ID) r.push(`BUILD_ID ${H.buildId || '(ausente)'} != ${CONTRATO.EXPECTED_BUILD_ID}`);
  if (casos.length !== CONTRATO.EXPECTED_CASES) r.push(`CASOS ${casos.length} != ${CONTRATO.EXPECTED_CASES}`);
  for (const s of CONTRATO.REVOKED_STATES) if (st[s]) r.push(`ESTADO REVOGADO ${s} em ${st[s]} casos`);
  for (const [k, v] of Object.entries(CONTRATO.CANONICAL_STATES)) {
    if (st[k] !== v) r.push(`${k}: contrato diz ${v}, o embarcado tem ${st[k] || 0}`);
  }
  const conhecido = CONTRATO.STALE_KNOWN_BUILD_IDS[H.buildId];
  if (conhecido) r.push(`safra conhecida como velha: ${conhecido}`);
  return { pass: r.length === 0, detail: r, medido: H.buildId };
});

/* ── 2 · o pacote local, quando existe ───────────────────────────────────── */
porta('PACOTE_LOCAL_NAO_E_SAFRA_VELHA', 'o pacote no disco, se houver, e o canonico', () => {
  const man = path.join(PACOTE, 'APP-MANIFEST.json');
  const opp = path.join(PACOTE, 'OPPORTUNITIES.json');
  if (!fs.existsSync(man)) {
    return { pass: true, detail: ['nenhum pacote local — nada a ingerir, nada a recusar'], medido: 'AUSENTE' };
  }
  if (!fs.existsSync(opp)) return { pass: false, detail: ['APP-MANIFEST.json existe mas OPPORTUNITIES.json nao — pacote truncado'] };
  const M = JSON.parse(fs.readFileSync(man, 'utf8'));
  const O = JSON.parse(fs.readFileSync(opp, 'utf8'));
  const rows = O.RECORDS || O;
  const r = recusas({ buildId: M.BUILD_ID, cases: rows.length, surfaceRule: M.MEETING_SURFACE_RULE, states: conta(rows, 'STATUS') });
  const conhecido = CONTRATO.STALE_KNOWN_BUILD_IDS[M.BUILD_ID];
  if (conhecido) r.push(`safra conhecida como velha: ${conhecido}`);
  return { pass: r.length === 0, detail: r, medido: M.BUILD_ID };
});

/* ── relatorio ───────────────────────────────────────────────────────────── */
console.log('\n  SINTONIA · PORTAO DA BUILD — a proveniencia antes do candidato');
console.log('  ' + '─'.repeat(88));
for (const l of linhas) {
  console.log(`  ${l.pass ? 'PASS' : 'FAIL'}  ${l.id.padEnd(32)} ${l.o_que}${l.medido ? `  [${l.medido}]` : ''}`);
  if (!l.pass) for (const d of l.detail || []) console.log(`        ${d}`);
}
console.log('  ' + '─'.repeat(88));
if (falhou) {
  console.log(`  BUILD RECUSADA. O gerador canonico e ${CONTRATO.CANONICAL_GENERATOR.LINHAGEM} @ ${CONTRATO.CANONICAL_GENERATOR.COMMIT.slice(0, 7)}.`);
  console.log('  A cadeia local desta linhagem esta atrasada e NAO deve ser usada para regenerar.\n');
  process.exit(1);
}
console.log('  proveniencia provada — a build pode continuar\n');
