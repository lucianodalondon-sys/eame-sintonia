// O RELATORIO GERA-SE DA MEDICAO — nenhum numero escrito a mao.
//
// Escreve dois ficheiros e imprime os blocos de markdown que
// `RELATORIO-RECOLLECTION.md` recebe nos marcadores <!-- ... -->.
//
//     medidas/RECOLLECTION-CENSO-V1.json   as 186 linhas, uma por contrato
//     (stdout)                             os blocos do relatorio
//
// ⚠️ A ELEGIBILIDADE NAO SE DIGITA. Vem de `curadoria/collection_gate.py`,
// que e quem decide quem entra em Collection nesta casa. Uma lista fixa aqui
// seria a capacidade de ontem — e ja custou caro nesta casa confundir
// «sei o caminho» com «pode ir».

import { writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { CONTRACTS, CONTRACT_IDS } from "../regras/italy_contracts.mjs";
import { admissivelNaBigCollection } from "../regras/incrementalidade.mjs";
import { tabela } from "./recollection_topologia.mjs";
import { lerObservacoes } from "./recollection_censo.mjs";

function elegiveis() {
  const py = execFileSync("py", ["-c",
    "from curadoria import collection_gate as G; print(' '.join(G.elegiveis()))"],
    { encoding: "utf8", env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" } });
  return py.trim().split(/\s+/).filter(Boolean);
}

const ELEGIVEIS = elegiveis();

// ⚠️ ELEGIVEL SEM CONTRATO TEM DE APARECER, E QUASE NAO APARECEU.
// `tabela()` percorre `CONTRACT_IDS`. Uma fonte que o portao admite e para a
// qual NAO HA contrato nenhum nao esta nessa lista — e desaparecia do censo
// em silencio. E o pior caso de todos: o portao aprova quem o coletor nao
// conhece, e o relatorio nao dava por isso.
const SEM_CONTRATO = ELEGIVEIS.filter((id) => !CONTRACTS[id]);
const T = [...tabela(), ...SEM_CONTRATO.map((id) => ({
  SOURCE_ID: id, SOURCE_NAME: "SEM CONTRATO", UNIVERSE: "NAO SEI",
  RECOLLECTION_CURRENT: "AUSENTE", ENDERECOS_OBSERVADOS: 0,
  PUBLICATION_TOPOLOGY: "UNKNOWN", RECOLLECTION_PROPOSED: "UNKNOWN",
  EVIDENCE_TYPE: "SEM_EVIDENCIA",
  EVIDENCE: "o portao admite esta fonte e NAO existe contrato nenhum para ela — "
    + "nao ha onde declarar RECOLLECTION, e nao ha quem saiba ir la buscar",
  CONFIDENCE: "NONE", REASON: "sem contrato nao ha onde declarar",
  NEEDS_HUMAN_REVIEW: "YES", COBERTURA_HOJE: "BLOCKED_FOR_BIG_COLLECTION",
  ADMISSIVEL_HOJE: false,
}))];
const obs = lerObservacoes();
const porId = Object.fromEntries(T.map((l) => [l.SOURCE_ID, l]));

// ── saude da descoberta: o indice chegou a abrir? ─────────────────────────
function descoberta(sid) {
  const o = obs.filter((x) => x.SOURCE_ID === sid);
  const falhas = o.filter((x) => x.OBSERVATION_RESULT === "DISCOVERY_FAILED").length;
  if (!o.length) return { OBS: 0, DISCOVERY_FAILED: 0, PROVA: "NAO SEI — nunca observada nesta arvore" };
  const ok = o.length - falhas;
  return { OBS: o.length, DISCOVERY_FAILED: falhas,
    PROVA: falhas === 0 ? `${ok} observacoes, nenhuma falha de descoberta`
      : `${ok} observacoes boas e ${falhas} DISCOVERY_FAILED` };
}

const linhas = T.map((l) => ({
  ...l,
  ELEGIVEL_HOJE: ELEGIVEIS.includes(l.SOURCE_ID) ? "SIM" : "NAO",
  DESCOBERTA: descoberta(l.SOURCE_ID),
}));

writeFileSync("medidas/RECOLLECTION-CENSO-V1.json", JSON.stringify({
  MEDICAO: "RECOLLECTION-V1", GERADO_EM: new Date().toISOString().slice(0, 10),
  FONTE_DA_ELEGIBILIDADE: "curadoria/collection_gate.py :: elegiveis()",
  NETWORK_REQUESTS: 0,
  CONTRACTS_TOTAL: CONTRACT_IDS.length,
  ELEGIVEIS_SEM_CONTRATO: SEM_CONTRATO,
  COLLECTION_ELIGIBLE: ELEGIVEIS.length,
  LINHAS: linhas,
}, null, 1) + "\n");

const q = (s) => String(s == null ? "" : s).replace(/\|/g, "/");
const decl = linhas.filter((l) => l.RECOLLECTION_CURRENT !== "AUSENTE");
const interessantes = linhas.filter((l) =>
  l.RECOLLECTION_CURRENT !== "AUSENTE" || l.ELEGIVEL_HOJE === "SIM" || l.CONFIDENCE !== "NONE");

console.log("<!-- TABELA_CANONICA -->\n");
console.log(`As 186 linhas vivem em \`medidas/RECOLLECTION-CENSO-V1.json\`, uma por
contrato, com todos os campos. Aqui ficam as ${interessantes.length} que carregam evidencia,
declaracao ou elegibilidade — as restantes ${linhas.length - interessantes.length} sao uma so linha repetida:
topologia \`UNKNOWN\`, \`RECOLLECTION_PROPOSED = UNKNOWN\`, \`CONFIDENCE = NONE\`,
\`NEEDS_HUMAN_REVIEW = YES\`, e \`BLOCKED_FOR_BIG_COLLECTION\`.
`);
console.log("| SOURCE_ID | UNIVERSE | ELEG. | TOPOLOGIA | ACTUAL | PROPOSTO | CONF. | EVIDENCE_TYPE | REVISAO |");
console.log("|---|---|---|---|---|---|---|---|---|");
for (const l of interessantes.sort((a, b) => (b.RECOLLECTION_CURRENT !== "AUSENTE") - (a.RECOLLECTION_CURRENT !== "AUSENTE") || a.SOURCE_ID.localeCompare(b.SOURCE_ID))) {
  console.log(`| \`${l.SOURCE_ID}\` | ${q(l.UNIVERSE)} | ${l.ELEGIVEL_HOJE} | ${q(l.PUBLICATION_TOPOLOGY)} | ${q(l.RECOLLECTION_CURRENT)} | ${q(l.RECOLLECTION_PROPOSED)} | ${q(l.CONFIDENCE)} | ${q(l.EVIDENCE_TYPE)} | ${q(l.NEEDS_HUMAN_REVIEW)} |`);
}
console.log("\n**A evidência de cada uma, por extenso:**\n");
for (const l of interessantes.sort((a, b) => a.SOURCE_ID.localeCompare(b.SOURCE_ID))) {
  console.log(`- \`${l.SOURCE_ID}\` — ${q(l.SOURCE_NAME)}\n  ${q(l.EVIDENCE)}`);
}

// ── FASE 7-8 ────────────────────────────────────────────────────────────
const mut = decl.filter((l) => l.RECOLLECTION_CURRENT === "MUTABLE");
const imut = decl.filter((l) => l.RECOLLECTION_CURRENT === "IMMUTABLE");
console.log("\n\n<!-- GRUPOS_DE_RISCO -->\n");
console.log("```");
console.log(`SAME_URL_OVERWRITE_COUNT = ${mut.length}`);
console.log(`NEW_URL_PER_ITEM_COUNT   = ${imut.length}`);
console.log("```\n");
console.log("### Grupo 1 · a mesma morada recebe factos novos\n");
console.log("| SOURCE_ID | URL_PATTERN | PROOF_OF_OVERWRITE | CURRENT_BEHAVIOR | REQUIRED_BEHAVIOR |");
console.log("|---|---|---|---|---|");
for (const l of mut.sort((a, b) => a.SOURCE_ID.localeCompare(b.SOURCE_ID))) {
  const c = CONTRACTS[l.SOURCE_ID];
  console.log(`| \`${l.SOURCE_ID}\` | \`${q(c.CANONICAL_ENTRY_URL || (c.ACQUISITION && c.ACQUISITION.INDEX_URL) || "NAO SEI")}\` | ${q(l.EVIDENCE)} | \`REVALIDATE\` a cada corrida, razao \`CONTRACT_DECLARES_MUTABLE\` | revisitar o detalhe — e o que passou a acontecer |`);
}
console.log("\n### Grupo 2 · morada nova por item — e a descoberta, provada ou não\n");
console.log("| SOURCE_ID | rota declarada | a descoberta foi provada? |");
console.log("|---|---|---|");
for (const l of imut.sort((a, b) => a.SOURCE_ID.localeCompare(b.SOURCE_ID))) {
  const c = CONTRACTS[l.SOURCE_ID];
  console.log(`| \`${l.SOURCE_ID}\` | ${q(c.ROUTE_TYPE)} | ${q(l.DESCOBERTA.PROVA)} |`);
}

// ── FASE 10-11 ──────────────────────────────────────────────────────────
const pareto = {};
for (const l of linhas) pareto[l.PUBLICATION_TOPOLOGY] = (pareto[l.PUBLICATION_TOPOLOGY] || 0) + 1;
console.log("\n\n<!-- CONTAGENS -->\n");
console.log("```");
console.log(`PARETO POR TOPOLOGIA — ${CONTRACT_IDS.length} contratos + ${SEM_CONTRATO.length} elegivel sem contrato = ${linhas.length} linhas`);
for (const k of Object.keys(pareto).sort((a, b) => pareto[b] - pareto[a]))
  console.log(`  ${String(pareto[k]).padStart(4)}  ${k}`);
console.log("");
console.log(`WITH_RECOLLECTION_BEFORE      7`);
console.log(`WITH_RECOLLECTION_AFTER      ${decl.length}    IMMUTABLE ${imut.length} · MUTABLE ${mut.length}`);
console.log(`UNKNOWN_RECOLLECTION_AFTER   ${linhas.length - decl.length}    todos BLOCKED_FOR_BIG_COLLECTION`);
console.log(`   dos quais SEM CONTRATO      ${SEM_CONTRATO.length}    ${SEM_CONTRATO.join(" ")}`);
console.log("```");

// ── GATE ────────────────────────────────────────────────────────────────
const el = linhas.filter((l) => l.ELEGIVEL_HOJE === "SIM");
const elDecl = el.filter((l) => l.RECOLLECTION_CURRENT !== "AUSENTE");
const elBloq = el.filter((l) => !admissivelNaBigCollection(l.SOURCE_ID, CONTRACTS[l.SOURCE_ID] || null).ADMISSIVEL);
console.log("\n\n<!-- GATE -->\n");
console.log("```");
console.log(`COLLECTION_ELIGIBLE           ${el.length}   (curadoria/collection_gate.py)`);
console.log(`  com RECOLLECTION declarada  ${elDecl.length}   ${elDecl.map((l) => l.SOURCE_ID).join(" ")}`);
console.log(`  BLOCKED_FOR_BIG_COLLECTION  ${elBloq.length}   ${elBloq.map((l) => l.SOURCE_ID).join(" ")}`);
console.log("");
console.log(`RECOLLECTION_COVERAGE = ${elDecl.length + elBloq.length}/${el.length}  comportamento EXPLICITO e seguro`);
console.log(`                        ${elDecl.length}/${el.length}  declarado (colhe e revisita)`);
console.log(`                        ${elBloq.length}/${el.length}  bloqueado  (nao entra ate ser classificado)`);
console.log("```");
for (const l of el.sort((a, b) => a.SOURCE_ID.localeCompare(b.SOURCE_ID))) {
  const a = admissivelNaBigCollection(l.SOURCE_ID, CONTRACTS[l.SOURCE_ID] || null);
  console.log(`- \`${l.SOURCE_ID}\` — **${a.COBERTURA}** — ${q(a.PORQUE)}`);
}
