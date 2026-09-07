#!/usr/bin/env node
/* SINTONIA ITALIA · A CADEIA, FAMILIA POR FAMILIA
   ---------------------------------------------------------------------------
   node audit/cadeia-de-familias.mjs           tabela humana
   node audit/cadeia-de-familias.mjs --json    para maquina

   Mede a mesma familia em QUATRO fronteiras e poe os numeros lado a lado:

       PACOTE    build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/*.json  (.RECORDS)
       PORTAL    window.ITALY_HANDOFF_V21.<familia>      o que embarca no site
       MOTOR     AM.ingest.report.families               o que o modelo aceita
       COLECAO   AM.collections.<nome>                   o que as telas podem ler

   POR QUE ESTE FICHEIRO EXISTE
   -----------------------------
   `counters.mjs` reconcilia MODELO x ECRA. `checks.mjs` prova invariantes por
   ecra. Faltava a pergunta mais simples de todas, e a mais facil de perder:

       UMA FAMILIA INTEIRA PODE DESAPARECER SEM QUE NENHUM NUMERO FIQUE VERMELHO.

   Foi o que aconteceu com `events`. O pacote publica 40; o modelo expoe uma
   colecao chamada `events` que e um ALIAS de `futureEvents`; a colecao tem 2, o
   ecra mostra 2, e nada em lado nenhum ficou por explicar — porque ninguem
   estava a comparar o nome da colecao com a familia que ela diz ler.

       UM ALIAS E UMA PERDA QUE SE APRESENTA COMO UM NUMERO CERTO.

   AS CINCO PERGUNTAS
   -------------------
   T1  toda familia que o pacote publica no portal e LIDA por alguma colecao?
   T2  a aritmetica do motor fecha em cada familia (entrada = aceites + rejeitados)?
   T3  a contagem PACOTE -> PORTAL e identica em cada familia?
   T4  alguma colecao tem nome de uma familia e le outra? (o alias)
   T5  o pacote no disco e a safra que o portal serve? Se nao for, T3 NAO MEDE.

   TRES ESTADOS, NAO DOIS. Onde a safra do disco nao e a servida, T3 diz NAO
   MEDIDO e nomeia o gerador canonico — nao inventa um PASS nem acusa um FAIL.
   Chamar falha ao que nao se pode medir e mentir para baixo; chamar sucesso e
   mentir para cima.

   A PROVA DE QUE O PACOTE CANONICO SE OBTEM (medida em 2026-09-06)
   ----------------------------------------------------------------
       git worktree add --detach /tmp/wt 55c2674
       cd /tmp/wt && bash scripts/v21_cadeia.sh          # exit 0, ~20s
       cp -r /tmp/wt/build/ITALY-REALITY-HANDOFF-V2.1 build/
   Resultado: 32/32 ficheiros com o SHA256 de INGESTION-REPRODUCTION.json e
   BUILD_ID V21-69bf448ac934a6d9 — o mesmo que o portal serve. O pacote nao se
   guarda, gera-se; e agora esta escrito que gerar funciona.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { loadData } from './lib/harness.mjs';
import { statoDelPacchetto, perchePuoiNonMisurare } from './lib/pacote.mjs';

const JSONOUT = process.argv.includes('--json');

/* O nome do ficheiro do pacote para cada familia publicada. Escrito por extenso:
   derivar por transformacao de texto e como o alias entrou. */
const FICHEIRO = {
  activeIngredients: 'ACTIVE-INGREDIENTS.json',
  agrometConditions: 'AGROMET-CONDITIONS.json',
  clientSafeCrossings: 'CLIENT-SAFE-CROSSINGS.json',
  competitorActivities: 'COMPETITOR-ACTIVITIES.json',
  cropEconomics: 'CROP-ECONOMIC-WEIGHT.json',
  currentFieldSignals: 'CROP-WINDOWS.json',
  events: 'EVENTS.json',
  fieldBulletins: 'CURRENT-FIELD-SIGNALS.json',
  futureEvents: 'FUTURE-EVENTS.json',
  futureSignals: 'FUTURE-SIGNALS.json',
  marketObservations: 'MARKET-OBSERVATIONS.json',
  news: 'NEWS.json',
  opportunities: 'OPPORTUNITIES.json',
  productActiveIngredients: 'PRODUCT-ACTIVE-INGREDIENTS.json',
  productRelationships: 'PRODUCT-RELATIONSHIPS.json',
  productsCommercial: 'PRODUCTS-COMMERCIAL.json',
  productsRegulatory: 'PRODUCTS-REGULATORY.json',
  publicChannels: 'PUBLIC-CHANNELS.json',
  publicVoices: 'PUBLIC-VOICES.json',
  regulatoryFuture: 'REGULATORY-FUTURE.json',
  regulatoryFutureFacts: 'REGULATORY-FUTURE-FACTS.json',
  relationships: 'RELATIONSHIPS.json',
  researchers: 'RESEARCHERS.json',
  resistance: 'RESISTANCE.json',
  scienceRecords: 'SCIENCE.json',
  sources: 'SOURCES.json',
  /* A safra V21-06c6421d001ea52a trouxe duas familias novas. Escritas por
     extenso, como as outras: derivar por transformacao de texto e como o alias
     de `events` entrou. */
  transcripts: 'TRANSCRIPTS.json',
  scienceCorpus: 'SCIENCE-CORPUS.json',
};

const ctx = loadData();
const H = ctx.ITALY_HANDOFF_V21 || {};
const AM = ctx.ITALY_APP_MODEL;
const COLS = AM.collections;
const FAM = (AM.ingest && AM.ingest.report && AM.ingest.report.families) || [];
const pac = statoDelPacchetto();
const medivel = pac.stato === 'CANONICO';

const contaPacote = (fam) => {
  const f = FICHEIRO[fam];
  if (!f || !medivel) return null;
  const p = path.join(pac.dir, f);
  if (!fs.existsSync(p)) return null;
  const j = JSON.parse(fs.readFileSync(p, 'utf8'));
  return Array.isArray(j.RECORDS) ? j.RECORDS.length : null;
};

/* Que colecoes declaram ler cada familia do pacote, pelo campo `source` que o
   proprio modelo publica. E o unico sitio onde o alias se ve. */
const leemFamilia = {};
for (const [nome, c] of Object.entries(COLS)) {
  const s = String((c && c.source) || '');
  const m = s.match(/^HANDOFF_V21 · ([A-Za-z0-9_]+)/);
  if (m) (leemFamilia[m[1]] = leemFamilia[m[1]] || []).push(nome);
}

const linhas = [];
for (const fam of Object.keys(H)) {
  if (!Array.isArray(H[fam])) continue;
  const portal = H[fam].length;
  const pacote = contaPacote(fam);
  const constr = FAM.find((f) => f.family === fam);
  const tent = constr && (constr.tried || []).find((t) => t.source === constr.chosen);
  const leitores = leemFamilia[fam] || [];
  linhas.push({
    familia: fam,
    pacote,
    portal,
    motorEntrada: tent ? tent.in : null,
    motorAceite: constr ? constr.accepted : null,
    motorRejeitado: constr ? (constr.rejected || 0) : null,
    colecao: constr ? (COLS[fam] ? COLS[fam].count : null) : null,
    leitores,
  });
}
linhas.sort((a, b) => b.portal - a.portal);

/* ── as cinco perguntas ──────────────────────────────────────────────────── */
const falhas = [];
const naoMedidos = [];

for (const l of linhas) {
  if (!l.leitores.length) {
    falhas.push({ t: 'T1', familia: l.familia,
      porque: `o pacote publica ${l.portal} registos e NENHUMA colecao do modelo declara ler esta familia` });
  }
}
for (const f of FAM) {
  const t = (f.tried || []).find((x) => x.source === f.chosen);
  if (!t) continue;
  if (t.in !== (f.accepted || 0) + (f.rejected || 0)) {
    falhas.push({ t: 'T2', familia: f.family,
      porque: `entrada ${t.in} != aceites ${f.accepted} + rejeitados ${f.rejected || 0}` });
  }
}
if (!medivel) {
  naoMedidos.push({ t: 'T3', porque: perchePuoiNonMisurare(pac) });
} else {
  for (const l of linhas) {
    if (l.pacote === null) continue;
    if (l.pacote !== l.portal) {
      falhas.push({ t: 'T3', familia: l.familia,
        porque: `pacote ${l.pacote} != portal ${l.portal}` });
    }
  }
}
for (const [nome, c] of Object.entries(COLS)) {
  const m = String((c && c.source) || '').match(/^HANDOFF_V21 · ([A-Za-z0-9_]+)/);
  if (!m) continue;
  const familia = m[1];
  /* Uma colecao pode chamar-se diferente da familia de proposito — mas so
     quando NAO existe uma familia do pacote com o nome dela. Se existe, a
     colecao esta a ocupar um nome que ja tem dono, e o dono fica por ler. */
  if (nome !== familia && Array.isArray(H[nome])) {
    falhas.push({ t: 'T4', familia: nome,
      porque: `a colecao '${nome}' le a familia '${familia}', e existe uma familia do pacote chamada '${nome}' com ${H[nome].length} registos que fica por ler` });
  }
}

if (JSONOUT) {
  console.log(JSON.stringify({ pacote: pac.stato, buildId: pac.buildId, linhas, falhas, naoMedidos }, null, 2));
  process.exit(falhas.length ? 1 : 0);
}

const G = '\x1b[32m', R = '\x1b[31m', Y = '\x1b[33m', D = '\x1b[2m', X = '\x1b[0m';
const n = (v) => (v === null || v === undefined ? '—' : String(v));
console.log('');
console.log('  SINTONIA ITALIA · A CADEIA, FAMILIA POR FAMILIA');
console.log(`  pacote no disco: ${pac.stato === 'CANONICO' ? G + pac.stato + X : Y + pac.stato + X}  ${D}${pac.buildId || ''}${X}`);
console.log('  ' + '─'.repeat(104));
console.log(`  ${'FAMILIA'.padEnd(26)}${'PACOTE'.padStart(8)}${'PORTAL'.padStart(8)}${'MOTOR>'.padStart(8)}${'ACEITE'.padStart(8)}${'REJ'.padStart(6)}${'COLECAO'.padStart(9)}  QUEM LE`);
console.log('  ' + '─'.repeat(104));
for (const l of linhas) {
  const sem = !l.leitores.length;
  const marca = sem ? `${R}NINGUEM LE${X}` : `${D}${l.leitores.join(', ').slice(0, 34)}${X}`;
  console.log(`  ${l.familia.padEnd(26)}${n(l.pacote).padStart(8)}${n(l.portal).padStart(8)}`
    + `${n(l.motorEntrada).padStart(8)}${n(l.motorAceite).padStart(8)}`
    + `${(l.motorRejeitado ? R + n(l.motorRejeitado) + X : n(l.motorRejeitado)).padStart(l.motorRejeitado ? 15 : 6)}`
    + `${n(l.colecao).padStart(9)}  ${marca}`);
}
console.log('  ' + '─'.repeat(104));
for (const f of falhas) console.log(`  ${R}FALHA${X} ${f.t}  ${f.familia}: ${f.porque}`);
for (const u of naoMedidos) console.log(`  ${Y}N/M  ${X} ${u.t}  ${u.porque}`);
if (!falhas.length && !naoMedidos.length) console.log(`  ${G}T1–T5 passam${X}`);
console.log(`  ${falhas.length} falha(s), ${naoMedidos.length} nao medido(s)`);
console.log('');
process.exit(falhas.length ? 1 : 0);
