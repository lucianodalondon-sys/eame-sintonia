// CONTABILIDADE DAS FONTES ITALIANAS — calculada, nunca digitada a mao.
//
// LEI DESTA MISSAO:  ACCESS_CLASSIFICATION != ANALYTIC_VERDICT
//   Uma fonte pode ter ACCESS_STATE = LOGIN_REQUIRED / WAF_CHALLENGE / PUBLIC_CAPABILITY
//   sem NUNCA receber veredito analitico. Estado de porta nao e julgamento de fonte.
//
// Uso:  node scripts/italy_accounting.mjs          (imprime)
//       import { contabilidade } from ...          (usado pelos guardas)

import { readFileSync, readdirSync, existsSync } from "node:fs";

const DIR = "data/samples/IT-SOURCE-SAMPLES";
const AVULSOS = { "IT-T3-005": "data/samples/ITALY-T3-005-MONITORAGGIO" };

// conjunto classificado NA BASE, antes da rodada browser. Congelado por SOURCE_ID.
export const BASE_CLASSIFIED_SET = ["IT-T1-001", "IT-T2-001", "IT-T3-002", "IT-T3-005", "IT-T4-001", "IT-T5-003", "IT-T10-002"];

const classe = v => {
  const s = String(v || "").toUpperCase();
  if (s.startsWith("GREEN")) return "GREEN";
  if (s.startsWith("YELLOW")) return "YELLOW";
  if (s.startsWith("RED")) return "RED";
  if (/NAO SEI|NÃO SEI/.test(s)) return "NAO_SEI";
  return "SEM_VEREDITO";
};

export function contabilidade() {
  const manifestos = [];
  for (const id of existsSync(DIR) ? readdirSync(DIR) : []) {
    manifestos.push([id, JSON.parse(readFileSync(`${DIR}/${id}/MANIFEST.json`, "utf8"))]);
  }
  for (const [id, p] of Object.entries(AVULSOS)) {
    manifestos.push([id, JSON.parse(readFileSync(`${p}/MANIFEST.json`, "utf8"))]);
  }

  const porFonte = manifestos.map(([id, m]) => ({
    SOURCE_ID: id,
    VERDICT: classe(m.VERDICT),
    VERDICT_TEXTO: String(m.VERDICT || ""),
    RAW_EVIDENCE_STATE: m.RAW_EVIDENCE_STATE,
    NOVA_NESTA_RODADA: !BASE_CLASSIFIED_SET.includes(id)
  })).sort((a, b) => a.SOURCE_ID.localeCompare(b.SOURCE_ID));

  const conta = set => {
    const c = { GREEN: 0, YELLOW: 0, RED: 0, NAO_SEI: 0, SEM_VEREDITO: 0 };
    set.forEach(f => c[f.VERDICT]++);
    return c;
  };

  const atual = conta(porFonte);
  const base = conta(porFonte.filter(f => !f.NOVA_NESTA_RODADA));
  const novas = porFonte.filter(f => f.NOVA_NESTA_RODADA);
  const delta = conta(novas);

  const raw = porFonte.filter(f => f.RAW_EVIDENCE_STATE === "PRESERVED").length;
  const extrato = porFonte.filter(f => f.RAW_EVIDENCE_STATE === "BROWSER_RENDERED_EXTRACT").length;

  return {
    LEI: "ACCESS_CLASSIFICATION != ANALYTIC_VERDICT — estado de porta nunca entra neste placar",
    ROTAS_NO_CATALOGO: JSON.parse(readFileSync("data/samples/ITALY-SOURCE-MASTER-V1.json", "utf8")).sources.length,
    ANALYTICALLY_CLASSIFIED: porFonte.length,
    SAMPLE_CAPTURED: porFonte.length,
    RAW_PRESERVED: raw,
    BROWSER_RENDERED_EXTRACT: extrato,
    VEREDITOS_ATUAIS: atual,
    VEREDITOS_BASE: base,
    ROUND_BROWSER_DELTA: {
      novas_por_source_id: novas.map(f => `${f.SOURCE_ID}=${f.VERDICT}`),
      quantas: novas.length,
      por_veredito: delta
    },
    por_fonte: porFonte
  };
}

// as fontes que so tem ESTADO DE PORTA — nunca entram no placar de veredito
export const ACCESS_ONLY = {
  "IT-T3-003": { nome: "SIMFITO (Campania)", ACCESS_STATE: "LOGIN_REQUIRED", classificacao: "PUBLIC_CAPABILITY", ANALYTIC_VERDICT: null },
  "IT-T7-012": { nome: "PICA (CAVIT)", ACCESS_STATE: "LOGIN_REQUIRED", classificacao: "PUBLIC_CAPABILITY", ANALYTIC_VERDICT: null },
  "IT-T9-003": { nome: "Syngenta Italia", ACCESS_STATE: "WAF_CHALLENGE", classificacao: null, ANALYTIC_VERDICT: null },
  "IT-T10-001": { nome: "ISMEA Mercati", ACCESS_STATE: "ROUTE_FOUND_PANEL_NOT_RENDERED", classificacao: null, ANALYTIC_VERDICT: null }
};

if (process.argv[1] && import.meta.url === `file:///${process.argv[1].replace(/\\/g, "/")}`) {
  const c = contabilidade();
  console.log("ROTAS_NO_CATALOGO        ", c.ROTAS_NO_CATALOGO);
  console.log("ANALYTICALLY_CLASSIFIED  ", c.ANALYTICALLY_CLASSIFIED);
  console.log("RAW_PRESERVED            ", c.RAW_PRESERVED);
  console.log("BROWSER_RENDERED_EXTRACT ", c.BROWSER_RENDERED_EXTRACT);
  console.log("\nVEREDITOS ATUAIS ", JSON.stringify(c.VEREDITOS_ATUAIS));
  console.log("VEREDITOS BASE   ", JSON.stringify(c.VEREDITOS_BASE));
  console.log("DELTA DA RODADA  ", JSON.stringify(c.ROUND_BROWSER_DELTA.por_veredito), "· novas:", c.ROUND_BROWSER_DELTA.quantas);
  console.log("\nnovas por SOURCE_ID:");
  c.ROUND_BROWSER_DELTA.novas_por_source_id.forEach(x => console.log("  " + x));
  const s = c.VEREDITOS_ATUAIS;
  const soma = s.GREEN + s.YELLOW + s.RED + s.NAO_SEI;
  console.log(`\nFECHA?  ${soma} == ${c.ANALYTICALLY_CLASSIFIED}  ->  ${soma === c.ANALYTICALLY_CLASSIFIED ? "SIM" : "NAO"}`);
  console.log("\nSO ESTADO DE PORTA (fora do placar):");
  Object.entries(ACCESS_ONLY).forEach(([k, v]) => console.log(`  ${k} ${v.nome} · ${v.ACCESS_STATE} · veredito analitico: ${v.ANALYTIC_VERDICT ?? "NENHUM (correto)"}`));
}
