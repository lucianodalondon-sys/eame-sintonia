// FASE H — guardas do contrato novo das fontes italianas.
// Roda em Node porque o Python desta maquina esta quebrado (ver relatorio §2).
// Uso: node scripts/italy_contract_test.mjs

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";

let falhas = 0, ok = 0;
const T = (nome, cond, detalhe = "") => {
  if (cond) { ok++; console.log("  ok  " + nome); }
  else { falhas++; console.log("FALHA " + nome + (detalhe ? " — " + detalhe : "")); }
};

const master = JSON.parse(readFileSync("data/samples/ITALY-SOURCE-MASTER-V1.json", "utf8"));
const DIR = "data/samples/IT-SOURCE-SAMPLES";
const ids = existsSync(DIR) ? readdirSync(DIR) : [];
const manifests = ids.map(id => [id, JSON.parse(readFileSync(`${DIR}/${id}/MANIFEST.json`, "utf8"))]);
const extras = [["IT-T3-005", JSON.parse(readFileSync("data/samples/ITALY-T3-005-MONITORAGGIO/MANIFEST.json", "utf8"))]];
const todos = [...manifests, ...extras];

console.log("\n1 · nenhuma fonte vira GREEN sem amostra preservada");
for (const [id, m] of todos) {
  if (m.VERDICT === "GREEN") T(`${id} GREEN tem RAW_EVIDENCE_STATE=PRESERVED`, m.RAW_EVIDENCE_STATE === "PRESERVED", m.RAW_EVIDENCE_STATE);
}

console.log("\n2 · toda amostra preservada tem MIME, BYTES e SHA256 de verdade");
for (const [id, m] of todos) {
  if (m.RAW_EVIDENCE_STATE !== "PRESERVED") continue;
  for (const f of m.FILES || []) {
    T(`${id}/${f.RAW_FILE || f.path} tem SHA256 de 64 hex`, /^[0-9a-f]{64}$/.test(f.SHA256 || ""), f.SHA256);
    T(`${id}/${f.RAW_FILE || f.path} tem BYTES > 0`, Number(f.BYTES) > 0, String(f.BYTES));
  }
}

console.log("\n3 · o hash bate com o arquivo no disco (evidencia re-verificavel)");
for (const [id, m] of manifests) {
  for (const f of m.FILES || []) {
    const p = `${DIR}/${id}/${f.RAW_FILE}`;
    if (!existsSync(p)) { T(`${id}/${f.RAW_FILE} existe`, false); continue; }
    const real = createHash("sha256").update(readFileSync(p)).digest("hex");
    T(`${id}/${f.RAW_FILE} hash confere`, real === f.SHA256, `disco=${real.slice(0, 12)} manifesto=${String(f.SHA256).slice(0, 12)}`);
  }
}

console.log("\n4 · ACCESS FAILURE nunca virou RED nem virou zero");
const probe = JSON.parse(readFileSync("data/samples/IT-PROBE/probe-fase-c.json", "utf8"));
const falhos = probe.RESULTADOS.filter(r => ["BLOCKED_PARA_CURL", "NETWORK_ERROR", "SERVER_ERROR", "WAF_CHALLENGE"].includes(r.RESULTADO));
T("ha falhas de acesso registradas (nao foram silenciadas)", falhos.length > 0, `${falhos.length}`);
T("nenhuma falha de acesso foi contada como BYTES validos", falhos.every(r => !(r.BYTES > 0 && r.RESULTADO === "NETWORK_ERROR")));
T("nenhum veredito RED foi emitido nesta missao", todos.every(([, m]) => m.VERDICT !== "RED"));

console.log("\n5 · SOURCE_LOCATION e FACT_LOCATION existem e nao sao o mesmo campo");
for (const [id, m] of todos) {
  if (m.RAW_EVIDENCE_STATE !== "PRESERVED") continue;
  T(`${id} declara SOURCE_LOCATION`, !!m.SOURCE_LOCATION);
  T(`${id} declara FACT_LOCATION`, !!m.FACT_LOCATION);
}

console.log("\n6 · OWNER_KIND nunca e um territorio");
const TERRS = new Set(["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12", "T13"]);
const KINDS = new Set(["OFFICIAL_NATIONAL_AGENCY", "OFFICIAL_REGIONAL_AGENCY", "RESEARCH_INSTITUTION", "COOPERATIVE",
  "PRODUCER_ORG", "AOP", "CONSORTIUM", "TECHNICAL_NETWORK", "TRADE_ASSOCIATION", "TECHNICAL_MEDIA",
  "COMPANY", "UNIVERSITY", "FOUNDATION", "OTHER"]);
for (const o of master.owners || []) T(`owner ${o.OWNER_ID} tem OWNER_KIND valido e nao-territorio`, KINDS.has(o.OWNER_KIND) && !TERRS.has(o.OWNER_KIND), o.OWNER_KIND);
for (const [id, m] of todos) if (m.OWNER_KIND) T(`${id} OWNER_KIND nao e territorio`, !TERRS.has(m.OWNER_KIND), m.OWNER_KIND);

console.log("\n7 · uma organizacao pode ter varios canais (owner reaproveitado)");
const porOwner = {};
for (const s of master.sources || []) porOwner[s.OWNER_ID] = (porOwner[s.OWNER_ID] || 0) + 1;
const multi = Object.entries(porOwner).filter(([, n]) => n > 1);
T("existe pelo menos um owner com mais de uma fonte", multi.length > 0, multi.slice(0, 3).map(x => x.join("=")).join(" "));
T("nenhum SOURCE_ID esta duplicado", new Set((master.sources || []).map(s => s.SOURCE_ID)).size === (master.sources || []).length);

console.log("\n8 · nao se criou T13 novo");
T("todo TERRITORY de fonte esta entre T1 e T12", (master.sources || []).every(s => /^T([1-9]|1[0-2])$/.test(s.TERRITORY)),
  [...new Set((master.sources || []).map(s => s.TERRITORY))].join(","));
T("T13 aparece so como divida declarada (taxonomy_debt)", !!master.taxonomy_debt?.T13);

console.log("\n9 · toda amostra preservada diz o que NAO prova");
for (const [id, m] of todos) {
  if (m.RAW_EVIDENCE_STATE !== "PRESERVED") continue;
  T(`${id} declara WHAT_IT_DOES_NOT_PROVE`, !!m.WHAT_IT_DOES_NOT_PROVE);
}

console.log(`\n===== ${ok} passaram, ${falhas} falharam =====`);
process.exit(falhas ? 1 : 0);
