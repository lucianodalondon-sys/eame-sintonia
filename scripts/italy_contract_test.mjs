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

console.log("\n10 · as quatro correcoes semanticas do fechamento continuam de pe");
const min = JSON.parse(readFileSync(`${DIR}/IT-T4-001/MANIFEST.json`, "utf8"));
T("Ministero e T4 REGULATORY", min.TERRITORY === "T4", min.TERRITORY);
T("Ministero e OFFICIAL_NATIONAL_AGENCY", min.OWNER_KIND === "OFFICIAL_NATIONAL_AGENCY", min.OWNER_KIND);
T("Ministero e REGULATORY_PRIMARY, nao so descoberta", min.SOURCE_ROLE === "REGULATORY_PRIMARY", min.SOURCE_ROLE);

const gio = JSON.parse(readFileSync(`${DIR}/IT-T5-003/MANIFEST.json`, "utf8"));
T("Giornate alimenta T5, T6 e T11", ["T5", "T6", "T11"].every(t => gio.TERRITORIOS_ALIMENTADOS?.[t]));
T("Giornate e AIPP seguem como dois owners separados", Object.keys(gio.OWNERS_SEPARADOS || {}).filter(k => k.startsWith("IT-OWN-")).length === 2);

const arp = JSON.parse(readFileSync(`${DIR}/IT-T2-001/MANIFEST.json`, "utf8"));
T("ARPAE e T2", arp.TERRITORY === "T2", arp.TERRITORY);
T("ARPAE e AGROCLIMATIC_SIGNAL, nao sinal de campo de praga", arp.EVIDENCE_CLASS === "AGROCLIMATIC_SIGNAL", arp.EVIDENCE_CLASS);
T("ARPAE carrega a lei AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE", /AGROCLIMATIC_SIGNAL\s*!=\s*PEST_OCCURRENCE/.test(arp.LEI_DE_NAO_PROMOCAO?.regra || ""));
T("nenhuma amostra classifica clima como ocorrencia de praga",
  todos.every(([, m]) => !(String(m.EVIDENCE_CLASS || "").includes("AGROCLIMATIC") && /PEST_OCCURRENCE/.test(String(m.EVIDENCE_CLASS)))));

console.log("\n11 · os quatro estados de cobertura fecham a conta");
const E = master.estados_de_cobertura_2026_09_07;
T("os quatro estados estao declarados", !!E && !!E.ROUTE_PROBED && !!E.SAMPLE_CAPTURED && !!E.RAW_PRESERVED && !!E.ANALYTICALLY_CLASSIFIED);
T("ROUTE_PROBED + NUNCA_TOCADAS = rotas do catalogo",
  E.ROUTE_PROBED.n + E.NUNCA_TOCADAS.n === E.ROTAS_NO_CATALOGO, `${E.ROUTE_PROBED.n}+${E.NUNCA_TOCADAS.n} vs ${E.ROTAS_NO_CATALOGO}`);
T("ROTAS_NO_CATALOGO bate com o numero real de sources", E.ROTAS_NO_CATALOGO === master.sources.length, `${E.ROTAS_NO_CATALOGO} vs ${master.sources.length}`);
T("RAW_PRESERVED bate com os manifestos que dizem PRESERVED",
  E.RAW_PRESERVED.n === todos.filter(([, m]) => m.RAW_EVIDENCE_STATE === "PRESERVED").length);
T("SAMPLE_CAPTURED nunca e maior que ROUTE_PROBED", E.SAMPLE_CAPTURED.n <= E.ROUTE_PROBED.n);
T("PROBADAS_SEM_AMOSTRA = ROUTE_PROBED - SAMPLE_CAPTURED",
  E.PROBADAS_SEM_AMOSTRA.n === E.ROUTE_PROBED.n - E.SAMPLE_CAPTURED.n);

console.log("\n12 · a lei permanente esta no contrato");
const L = master.leis_permanentes?.ROUTE_NOT_FOUND_NAO_E_SOURCE_BLOCKED;
T("ROUTE_NOT_FOUND != SOURCE_BLOCKED esta registrada", /ROUTE_NOT_FOUND\s*!=\s*SOURCE_BLOCKED/.test(L?.lei || ""));
T("OLD_URL_FAILURE != CURRENT_SOURCE_FAILURE esta registrada", /OLD_URL_FAILURE\s*!=\s*CURRENT_SOURCE_FAILURE/.test(L?.lei_irma || ""));
T("os 5 passos obrigatorios antes de BLOCKED estao escritos", (L?.antes_de_escrever_BLOCKED_e_obrigatorio || []).length === 5);
T("nenhuma fonte foi marcada BLOCKED sem passar pela lei",
  probe.RESULTADOS.every(r => r.RESULTADO !== "BLOCKED"), "so existe BLOCKED_PARA_CURL, que e inconclusivo por contrato");

console.log(`\n===== ${ok} passaram, ${falhas} falharam =====`);
process.exit(falhas ? 1 : 0);
