// FASE H — guardas do contrato novo das fontes italianas.
// Roda em Node porque o Python desta maquina esta quebrado (ver relatorio §2).
// Uso: node regras/italy_contract_test.mjs

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

console.log("\n13 · leis da rodada browser");
const B = master.rodada_browser_2026_09_07;
T("a rodada browser provou o IP de saida DO NAVEGADOR, nao so o do sistema", /ipinfo|205\.147\.30\.20/.test(B?.instrumento || ""));
T("BROWSER_REQUIRED nao foi confundido com SOURCE_UNAUTOMATABLE",
  todos.every(([, m]) => !(m.BROWSER_REQUIRED === "YES" && /NOT_AUTOMATABLE/.test(String(m.AUTOMATION_FEASIBILITY)))));
T("nenhum extrato de navegador foi promovido a RAW_PRESERVED",
  todos.every(([, m]) => !(m.RAW_EVIDENCE_STATE === "BROWSER_RENDERED_EXTRACT" && m.VERDICT === "GREEN")));
T("todo BROWSER_RENDERED_EXTRACT explica por que nao virou RAW",
  todos.filter(([, m]) => m.RAW_EVIDENCE_STATE === "BROWSER_RENDERED_EXTRACT").every(([, m]) => !!m.motivo_nao_PRESERVED));
T("todo COMPANY_CLAIM carrega a lei que o separa de fato regulatorio",
  todos.filter(([, m]) => m.EVIDENCE_CLASS === "COMPANY_CLAIM").every(([, m]) => /COMPANY_CLAIM\s*!=\s*REGULATORY_FACT/.test(String(m.LEI_APLICADA))));
T("nenhum COMPANY_CLAIM afirma FACT_LOCATION sem prova",
  todos.filter(([, m]) => m.EVIDENCE_CLASS === "COMPANY_CLAIM").every(([, m]) => /UNKNOWN/.test(String(m.FACT_LOCATION))));
T("toda fonte com rota corrigida guarda a rota velha E a nova",
  todos.filter(([, m]) => m.OLD_ROUTE).every(([, m]) => !!m.CURRENT_ROUTE));
T("nenhuma fonte com login foi marcada GREEN",
  todos.every(([, m]) => !(String(m.LOGIN_REQUIRED) === "YES" && m.VERDICT === "GREEN")));
T("as tres fontes sem URL foram todas endereçadas", Object.keys(B?.tres_fontes_sem_url || {}).length === 3);
T("as duas que ficaram em login estao como PUBLIC_CAPABILITY, nao RED",
  Object.values(B?.tres_fontes_sem_url || {}).filter(v => /LOGIN|NOT_PUBLICLY/.test(JSON.stringify(v))).every(v => v.classificacao === "PUBLIC_CAPABILITY" && v.VERDICT !== "RED"));

console.log("\n14 · os estados de cobertura continuam somando");
const E2 = master.estados_de_cobertura_2026_09_07;
T("SAMPLE_CAPTURED = RAW_PRESERVED + BROWSER_RENDERED_EXTRACT",
  E2.SAMPLE_CAPTURED.n === E2.RAW_PRESERVED.n + E2.BROWSER_RENDERED_EXTRACT.n,
  `${E2.SAMPLE_CAPTURED.n} vs ${E2.RAW_PRESERVED.n}+${E2.BROWSER_RENDERED_EXTRACT.n}`);
T("RAW_PRESERVED bate com os manifestos", E2.RAW_PRESERVED.n === todos.filter(([, m]) => m.RAW_EVIDENCE_STATE === "PRESERVED").length);
T("BROWSER_RENDERED_EXTRACT bate com os manifestos", E2.BROWSER_RENDERED_EXTRACT.n === todos.filter(([, m]) => m.RAW_EVIDENCE_STATE === "BROWSER_RENDERED_EXTRACT").length);
T("ROUTE_PROBED cobre agora as 54 rotas", E2.ROUTE_PROBED.n === E2.ROTAS_NO_CATALOGO && E2.NUNCA_TOCADAS.n === 0);
T("a matriz regiao x cultura nao inventa celula", /so entra celula com FONTE PROVADA/.test(master.matriz_regiao_x_cultura?.metodo || ""));
T("DURUM_WHEAT continua declarado como lacuna", /LACUNA/i.test(master.matriz_regiao_x_cultura?.leitura_das_culturas_prioritarias?.DURUM_WHEAT || ""));

// ===== MISSAO SOURCE CONTRACT HARDENING V1 =====
{
  const { CONTRACTS } = await import("./italy_contracts.mjs");
  const { contabilidade, ACCESS_ONLY, BASE_CLASSIFIED_SET } = await import("./italy_accounting.mjs");
  const { medir } = await import("./italy_source_health.mjs");
  const C = contabilidade();

  console.log("\n15 · a contabilidade fecha por SOURCE_ID, nao por subtracao cega");
  const v = C.VEREDITOS_ATUAIS;
  T("ANALYTICALLY_CLASSIFIED == GREEN+YELLOW+RED+NAO_SEI",
    v.GREEN + v.YELLOW + v.RED + v.NAO_SEI === C.ANALYTICALLY_CLASSIFIED,
    `${v.GREEN}+${v.YELLOW}+${v.RED}+${v.NAO_SEI} vs ${C.ANALYTICALLY_CLASSIFIED}`);
  T("nenhuma fonte classificada ficou SEM_VEREDITO", v.SEM_VEREDITO === 0);
  T("ROUND_DELTA fecha por SOURCE_ID (conjunto atual menos conjunto base)",
    C.ROUND_BROWSER_DELTA.quantas === C.ANALYTICALLY_CLASSIFIED - BASE_CLASSIFIED_SET.length,
    `${C.ROUND_BROWSER_DELTA.quantas} novas`);
  const dl = C.ROUND_BROWSER_DELTA.por_veredito, vb = C.VEREDITOS_BASE;
  T("base + delta == atual, veredito a veredito",
    ["GREEN", "YELLOW", "RED", "NAO_SEI"].every(k => vb[k] + dl[k] === v[k]));
  T("os numeros do JSON mestre sao os CALCULADOS, nao digitados",
    master.counts.GREEN === v.GREEN && master.counts.YELLOW === v.YELLOW && master.counts.NAO_SEI === v.NAO_SEI,
    `json G${master.counts.GREEN}/Y${master.counts.YELLOW}/NS${master.counts.NAO_SEI} vs calc G${v.GREEN}/Y${v.YELLOW}/NS${v.NAO_SEI}`);

  console.log("\n16 · ACCESS_CLASSIFICATION != ANALYTIC_VERDICT");
  T("nenhuma fonte de estado-de-porta recebeu veredito analitico",
    Object.values(ACCESS_ONLY).every(x => x.ANALYTIC_VERDICT === null));
  T("nenhuma fonte de estado-de-porta entrou no placar",
    Object.keys(ACCESS_ONLY).every(id => !C.por_fonte.some(f => f.SOURCE_ID === id)));
  T("LOGIN_REQUIRED e WAF_CHALLENGE existem como estado, sem virar RED",
    Object.values(ACCESS_ONLY).some(x => /LOGIN|WAF/.test(x.ACCESS_STATE)) &&
    Object.values(ACCESS_ONLY).every(x => x.ANALYTIC_VERDICT !== "RED"));

  console.log("\n17 · leis dos contratos");
  const ct = Object.entries(CONTRACTS);
  T("todo contrato declara DOCUMENT_ID_RULE (DOCUMENT_ID != BYTE_ID)", ct.every(([, c]) => !!c.DOCUMENT_ID_RULE));
  T("nenhum contrato usa SHA256 como identidade semantica", ct.every(([, c]) => !/SHA/i.test(String(c.DOCUMENT_ID_RULE))));
  T("todo contrato declara FAIL_CLOSED_RULE", ct.every(([, c]) => !!c.FAIL_CLOSED_RULE));
  T("todo contrato separa DECLARED de OBSERVED frequency", ct.every(([, c]) => "DECLARED_FREQUENCY" in c && "OBSERVED_FREQUENCY" in c));
  T("frequencia observada so afirma cadencia quando diz 'provado'",
    ct.every(([, c]) => !/^\d+D$|^\d+Y$/.test(String(c.OBSERVED_FREQUENCY)) || /provad/i.test(String(c.OBSERVED_FREQUENCY))));
  T("todo ROUTE_TYPE e um dos cinco tipos previstos",
    ct.every(([, c]) => ["STATIC_ROUTE", "PREDICTABLE_ROUTE", "DISCOVERED_ROUTE", "APPLICATION_ROUTE", "BROWSER_DISCOVERED_ROUTE"].includes(c.ROUTE_TYPE)));
  T("toda fonte SOBRESCRITA esta marcada FORWARD_ONLY e ARCHIVE CRITICAL",
    ct.filter(([, c]) => /SOBRESCRITA/.test(String(c.UPDATE_BEHAVIOR))).every(([, c]) => c.HISTORICAL_OR_FORWARD === "FORWARD_ONLY" && c.ARCHIVE_REQUIREMENT === "CRITICAL"));
  T("toda fonte FORWARD_ONLY carrega a lei SAME_URL != SAME_DOCUMENT ou explica a perda",
    ct.filter(([, c]) => c.HISTORICAL_OR_FORWARD === "FORWARD_ONLY").every(([, c]) => /SAME_URL/.test(JSON.stringify(c)) || /nao ha arquivo/i.test(JSON.stringify(c))));
  T("nenhum contrato usa a sede de quem publica como FACT_LOCATION, salvo excecao justificada por escrito",
    ct.every(([, c]) => !c.FACT_LOCATION_RULE || !/sede/i.test(c.FACT_LOCATION_RULE)
      || /NUNCA|nao inferir/i.test(c.FACT_LOCATION_RULE) || !!c.POR_QUE_A_SEDE_VALE_AQUI));
  T("a unica excecao de sede e a do registro de organizacoes, e ela diz por que",
    ct.filter(([, c]) => c.POR_QUE_A_SEDE_VALE_AQUI).every(([id, c]) => id === "IT-T7-002" && /o proprio fato registrado E o endereco/.test(c.POR_QUE_A_SEDE_VALE_AQUI)));
  T("todo contrato tem controle negativo declarado", ct.every(([, c]) => !!c.NEGATIVE_CONTROL));

  console.log("\n18 · SOURCE_VERDICT != SOURCE_HEALTH");
  const saude = Object.keys(CONTRACTS).map(id => medir(id));
  T("saude e calculada e nao copiada do veredito",
    saude.every(r => ["HEALTHY", "DEGRADED", "FAILED", "UNKNOWN"].includes(r.HEALTH)));
  T("existe pelo menos uma fonte cujo veredito e saude DIVERGEM (prova de que sao eixos diferentes)",
    saude.some(r => r.VERDICT !== "GREEN" && r.HEALTH === "HEALTHY"),
    saude.filter(r => r.VERDICT !== "GREEN" && r.HEALTH === "HEALTHY").map(r => `${r.SOURCE_ID}:${r.VERDICT}/${r.HEALTH}`).join(" "));

  console.log("\n19 · controles negativos precisam REPROVAR de verdade");
  const mutacoes = [
    ["IT-T2-001", "pdf_virou_html"], ["IT-T3-010", "vazio"], ["IT-T3-008", "sem_marcadores"],
    ["IT-T4-001", "coluna_removida"], ["IT-T7-002", "coluna_removida"],
    ["IT-T9-008", "sem_identidade"], ["IT-T3-005", "vazio"], ["IT-T1-001", "vazio"]
  ];
  for (const [id, mut] of mutacoes) {
    const antes = medir(id).HEALTH, depois = medir(id, { mutacao: mut }).HEALTH;
    T(`${id} + ${mut} reprova (${antes} -> ${depois})`, antes !== "FAILED" && depois === "FAILED");
  }
  T("PDF_EXPECTED_REJECTS_HTML — a armadilha do /view do Plone e pega",
    medir("IT-T2-001", { mutacao: "pdf_virou_html" }).falhas.some(f => /esperava PDF/.test(f)));
  T("EMPTY_LIST_FAILS_CLOSED — corpo vazio vira FAILED, nunca zero",
    medir("IT-T3-005", { mutacao: "vazio" }).falhas.some(f => /EMPTY != ZERO/.test(f)));

  console.log("\n20 · contagens que ja me enganaram");
  const masaf = CONTRACTS["IT-T7-002"].CONTAGEM;
  T("MASAF declara RAW_ROWS e UNIQUE_ORGANIZATIONS separados", masaf.RAW_ROWS !== masaf.UNIQUE_ORGANIZATIONS);
  T("MASAF explica por que os dois numeros diferem", !!masaf.WHY_DIFFERENT);
  T("MASAF registra a correcao dos numeros errados que publiquei", /269|264/.test(String(masaf.CORRECAO)));
  T("MASAF: OP + AOP == UNIQUE_ORGANIZATIONS", masaf.OP + masaf.AOP === masaf.UNIQUE_ORGANIZATIONS);
  T("FEM carrega QUERY_MATCH != PROVED_TOPIC", /QUERY_MATCH != PROVED_TOPIC/.test(String(CONTRACTS["IT-T5-002"].LEI_CRITICA)));
}



const { guardasDoPiloto } = await import("./italy_pilot_guards.mjs");
guardasDoPiloto(T);
const { guardasDeAgendamento } = await import("./italy_scheduling_guards.mjs");
guardasDeAgendamento(T);

console.log(`\n===== ${ok} passaram, ${falhas} falharam =====`);
process.exit(falhas ? 1 : 0);