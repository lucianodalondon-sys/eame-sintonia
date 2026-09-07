// SAUDE DAS FONTES ITALIANAS — roda o contrato contra o RAW ja preservado.
//
// LEI:  SOURCE_VERDICT != SOURCE_HEALTH
//   veredito  = quanto a fonte vale        (GREEN / YELLOW / RED / NÃO SEI)
//   saude     = como ela se comportou AGORA (HEALTHY / DEGRADED / FAILED / UNKNOWN)
//   Uma fonte GREEN pode estar FAILED. Uma YELLOW pode estar HEALTHY.
//
// LEI:  HTTP_200 != HEALTHY_SOURCE — aqui nem se olha status; olha-se os BYTES.
//
// Uso:  node scripts/italy_source_health.mjs [--negativos]

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { CONTRACTS } from "./italy_contracts.mjs";

const DIR = "data/samples/IT-SOURCE-SAMPLES";
const AVULSOS = { "IT-T3-005": "data/samples/ITALY-T3-005-MONITORAGGIO" };
const pastaDe = id => AVULSOS[id] || `${DIR}/${id}`;

function assinatura(buf) {
  const h = buf.subarray(0, 8).toString("latin1");
  if (h.startsWith("%PDF")) return "PDF";
  if (h.startsWith("PK")) return "ZIP";
  const t = buf.subarray(0, 400).toString("latin1").trimStart();
  if (t.startsWith("<")) return "HTML";
  if (t.startsWith("{") || t.startsWith("[")) return "JSON";
  return "TEXTO";
}

function textoDoPdf(caminho) {
  try { return execFileSync("pdftotext", ["-layout", "-enc", "UTF-8", caminho, "-"], { maxBuffer: 64e6, encoding: "utf8" }); }
  catch { return ""; }
}

function texto(caminho, tipo) {
  if (tipo === "PDF") return textoDoPdf(caminho);
  const b = readFileSync(caminho);
  if (tipo === "ZIP") { try { return execFileSync("node", ["scripts/ods_peek.mjs", caminho, "4000"], { encoding: "utf8" }); } catch { return ""; } }
  return b.toString("utf8");
}

export function medir(id, { mutacao = null } = {}) {
  const c = CONTRACTS[id];
  if (!c) return { SOURCE_ID: id, HEALTH: "UNKNOWN", motivo: "sem contrato" };
  const pasta = pastaDe(id);
  const mp = `${pasta}/MANIFEST.json`;
  if (!existsSync(mp)) return { SOURCE_ID: id, HEALTH: "UNKNOWN", motivo: "sem manifesto" };
  const m = JSON.parse(readFileSync(mp, "utf8"));

  const falhas = [], degradacoes = [];

  // BROWSER_RENDERED_EXTRACT tem contrato proprio: identidade, nao bytes de servidor
  if (c.OUTPUT_TYPE === "BROWSER_RENDERED_EXTRACT") {
    const f = m.FILES[0];
    let e = {};
    try { e = JSON.parse(readFileSync(`${pasta}/${f.RAW_FILE}`, "utf8")); } catch { falhas.push("extrato ilegivel"); }
    if (mutacao === "sem_identidade") delete e.SOURCE_DATE;
    if (!e.CANONICAL_URL) falhas.push("sem CANONICAL_URL — sem identidade");
    if (!e.SOURCE_DATE) falhas.push("sem SOURCE_DATE — sem identidade");
    if (m.RAW_EVIDENCE_STATE !== "BROWSER_RENDERED_EXTRACT") falhas.push("estado de evidencia nao bate com o contrato");
    return resultado(id, c, m, falhas, degradacoes);
  }

  // arquivo principal = o primeiro que casa com a assinatura esperada
  const alvo = (m.FILES || []).find(f => !/headers|meta\.txt/.test(f.RAW_FILE || f.path || ""));
  const nome = alvo?.RAW_FILE || alvo?.path;
  const caminho = `${pasta}/${nome}`;
  if (!existsSync(caminho)) { falhas.push(`arquivo ausente: ${nome}`); return resultado(id, c, m, falhas, degradacoes); }

  let buf = readFileSync(caminho);

  // --- CONTROLES NEGATIVOS: mutam os bytes em memoria, nunca no disco ---
  if (mutacao === "pdf_virou_html") buf = Buffer.from("<html><body>Access denied</body></html>");
  if (mutacao === "vazio") buf = Buffer.alloc(0);
  if (mutacao === "sem_marcadores") buf = Buffer.from(buf.subarray(0, 8)); // so a assinatura, sem conteudo
  if (mutacao === "truncado") buf = buf.subarray(0, Math.floor(buf.length / 20));

  const sig = assinatura(buf);
  if (c.EXPECTED_SIGNATURE === "%PDF" && sig !== "PDF") falhas.push(`esperava PDF, os bytes sao ${sig} — HTTP 200 nao salva isto`);
  if (c.EXPECTED_SIGNATURE === "PK" && sig !== "ZIP") falhas.push(`esperava planilha (ZIP), os bytes sao ${sig}`);
  if (c.EXPECTED_SIGNATURE === "<" && sig !== "HTML") falhas.push(`esperava HTML, os bytes sao ${sig}`);
  if (typeof c.EXPECTED_SIGNATURE === "string" && c.EXPECTED_SIGNATURE.includes(";") && !buf.subarray(0, 400).toString("utf8").includes(c.EXPECTED_SIGNATURE)) falhas.push("cabecalho de CSV esperado ausente");
  if (c.EXPECTED_SIGNATURE === "DATAFLOW,FREQ,REF_AREA" && !buf.subarray(0, 400).toString("utf8").includes(c.EXPECTED_SIGNATURE)) falhas.push("cabecalho SDMX esperado ausente");

  if (buf.length === 0) falhas.push("corpo vazio — EMPTY != ZERO, isto e FAILED");
  else if (c.MIN_BYTES && buf.length < c.MIN_BYTES) degradacoes.push(`${buf.length} bytes, abaixo do minimo ${c.MIN_BYTES}`);

  // marcadores de conteudo — so quando a assinatura ja passou
  if (falhas.length === 0 && c.EXPECTED_CONTENT_MARKERS) {
    let t = "";
    if (mutacao === "sem_marcadores") t = "";
    else {
      const tmp = `${pasta}/${nome}`;
      t = sig === "PDF" ? textoDoPdf(tmp) : buf.toString("utf8");
      if (mutacao === "truncado") t = t.slice(0, Math.floor(t.length / 20));
    }
    const faltando = c.EXPECTED_CONTENT_MARKERS.filter(k => !t.includes(k));
    if (faltando.length === c.EXPECTED_CONTENT_MARKERS.length) falhas.push(`nenhum marcador de conteudo encontrado: ${faltando.join(", ")}`);
    else if (faltando.length) degradacoes.push(`marcadores ausentes: ${faltando.join(", ")}`);
  }

  // colunas obrigatorias
  if (falhas.length === 0 && c.EXPECTED_COLUMNS) {
    let cab = "";
    if (sig === "ZIP") cab = texto(caminho, "ZIP");
    else cab = buf.subarray(0, 3000).toString("utf8");
    if (mutacao === "coluna_removida" && c.EXPECTED_COLUMNS[0]) cab = cab.split(c.EXPECTED_COLUMNS[0]).join("__REMOVIDA__");
    const faltando = c.EXPECTED_COLUMNS.filter(k => !cab.includes(k));
    if (faltando.length) falhas.push(`coluna obrigatoria ausente: ${faltando.join(", ")}`);
  }

  // identidade semantica presente?
  if (!c.DOCUMENT_ID_RULE) falhas.push("contrato sem regra de DOCUMENT_ID");

  return resultado(id, c, m, falhas, degradacoes);
}

function resultado(id, c, m, falhas, degradacoes) {
  const HEALTH = falhas.length ? "FAILED" : degradacoes.length ? "DEGRADED" : "HEALTHY";
  return {
    SOURCE_ID: id, VALUE: c.VALUE, ROUTE_TYPE: c.ROUTE_TYPE,
    VERDICT: String(m.VERDICT || "").split(" ")[0],
    HEALTH, falhas, degradacoes,
    FORWARD_ONLY: c.HISTORICAL_OR_FORWARD === "FORWARD_ONLY",
    ARCHIVE_REQUIREMENT: c.ARCHIVE_REQUIREMENT
  };
}

if (process.argv[1] && import.meta.url === `file:///${process.argv[1].replace(/\\/g, "/")}`) {
  const negativos = process.argv.includes("--negativos");
  if (!negativos) {
    console.log("SAUDE — contrato rodado contra o RAW preservado\n");
    console.log("SOURCE_ID    VAL  VEREDITO  SAUDE      observacao");
    const res = Object.keys(CONTRACTS).map(id => medir(id));
    for (const r of res) {
      console.log(`${r.SOURCE_ID.padEnd(12)} ${String(r.VALUE).padEnd(4)} ${String(r.VERDICT).padEnd(9)} ${r.HEALTH.padEnd(10)} ${[...r.falhas, ...r.degradacoes].join(" · ").slice(0, 70)}`);
    }
    const c = {};
    res.forEach(r => c[r.HEALTH] = (c[r.HEALTH] || 0) + 1);
    console.log("\nresumo:", JSON.stringify(c));
    console.log("FORWARD_ONLY (perde se nao coletar):", res.filter(r => r.FORWARD_ONLY).map(r => r.SOURCE_ID).join(", "));
  } else {
    console.log("CONTROLES NEGATIVOS — o teste precisa REPROVAR quando o documento e corrompido\n");
    const casos = [
      ["IT-T2-001", "pdf_virou_html", "PDF esperado vira HTML de 'Access denied' (a armadilha do /view do Plone)"],
      ["IT-T3-010", "vazio", "documento vazio"],
      ["IT-T3-008", "sem_marcadores", "PDF sem nenhum marcador de conteudo"],
      ["IT-T4-001", "coluna_removida", "CSV sem a coluna obrigatoria"],
      ["IT-T7-002", "coluna_removida", "planilha sem a coluna CODICE IT"],
      ["IT-T9-008", "sem_identidade", "extrato de navegador sem data — sem identidade"],
      ["IT-T3-005", "vazio", "HTML de monitoramento vazio"],
      ["IT-T1-001", "vazio", "resposta SDMX vazia"]
    ];
    let rodados = 0, reprovaram = 0;
    for (const [id, mut, desc] of casos) {
      const antes = medir(id).HEALTH;
      const depois = medir(id, { mutacao: mut }).HEALTH;
      rodados++;
      const ok = antes !== "FAILED" && depois === "FAILED";
      if (ok) reprovaram++;
      console.log(`${ok ? "REPROVOU " : "NAO PEGOU"} ${id.padEnd(12)} ${antes} -> ${depois}   ${desc}`);
    }
    console.log(`\nrodados: ${rodados} · reprovaram como deviam: ${reprovaram}`);
    process.exit(rodados === reprovaram ? 0 : 1);
  }
}
