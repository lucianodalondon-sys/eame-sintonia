// AS GUARDAS DA CADENCIA DA REFERENCIA (D117, dono, 27/09)
//
//     CADENCIA NAO E ADMISSAO. DEVIDA HOJE NAO E ELEGIVEL.
//
// Calendario usado (2026): 21/09 SEG · 22 TER · 23 QUA · 24 QUI · 25 SEX · 28 SEG · 29 TER.
import { readFileSync } from "node:fs";
import { devidaHoje, planoDaRotacao, filtrarPorCadencia, conferirCadencia, CadenciaInvalida }
  from "./cadencia_da_referencia.mjs";
import { CONTRACTS } from "./italy_contracts.mjs";

let ok = 0, falhas = 0;
const t = (nome, cond, det = "") => {
  if (cond) { ok++; console.log(`  ✓ ${nome}`); }
  else { falhas++; console.log(`  ✗ ${nome}${det ? " — " + det : ""}`); }
};

const SEM = CONTRACTS["IT-T4-001"].CADENCIA;

console.log("\n1 · O CONTRATO DE IT-T4-001 DECLARA A CADENCIA DA D117");
t("SEMANAL na TERCA, retentar QUARTA e QUINTA",
  SEM && SEM.TIPO === "SEMANAL" && SEM.DIA === "TER" && JSON.stringify(SEM.RETENTAR) === '["QUA","QUI"]');
t("a cadencia do contrato passa na conferencia", (() => { try { conferirCadencia("IT-T4-001", SEM); return true; } catch { return false; } })());
t("as bulas: rotacao de ate 3 por dia, disparadas primeiro",
  CONTRACTS["IT-T4-001"].ENDPOINTS_DE_REFERENCIA.ETICHETTE.CADENCIA.MAX_POR_DIA === 3
  && CONTRACTS["IT-T4-001"].ENDPOINTS_DE_REFERENCIA.ETICHETTE.CADENCIA.PRIORIDADE === "DISPARADAS_PELO_DIFF");
t("o portfolio: mensal + extraordinaria, NO ENDPOINT (nunca no topo de IT-T9-008)",
  CONTRACTS["IT-T9-008"].ENDPOINTS_DE_REFERENCIA.CATALOGO.CADENCIA.TIPO === "MENSAL"
  && !!CONTRACTS["IT-T9-008"].ENDPOINTS_DE_REFERENCIA.CATALOGO.CADENCIA.EXTRAORDINARIA
  && CONTRACTS["IT-T9-008"].CADENCIA === undefined);
t("robots e teto declarados nos dois endpoints",
  ["IT-T4-001:ETICHETTE", "IT-T9-008:CATALOGO"].every((k) => {
    const [s, e] = k.split(":"); const x = CONTRACTS[s].ENDPOINTS_DE_REFERENCIA[e];
    return /OBRIGATORIO/.test(x.ROBOTS) && /5 pedidos/.test(x.TETO); }));
t("tipo fora do vocabulario reprova", (() => { try { conferirCadencia("X", { TIPO: "QUINZENAL" }); return false; } catch (e) { return e instanceof CadenciaInvalida; } })());

console.log("\n2 · SEMANAL: TERCA, RETENTA QUARTA E QUINTA, ALERTA CONTINUA");
const d = (hoje, ult) => devidaHoje(SEM, hoje, ult);
let r = d("2026-09-22", "2026-09-18T17:20:53Z");
t("terca, ultima ok na semana anterior -> devida PRIMARIA, sem alerta",
  r.DEVIDA && r.TENTATIVA === "PRIMARIA" && r.ALERTA === null, JSON.stringify(r));
r = d("2026-09-22", "2026-09-22T19:00:00Z");
t("terca ja checada -> nao devida", !r.DEVIDA);
r = d("2026-09-23", "2026-09-22T19:00:00Z");
t("quarta com terca ok -> nao devida e sem alerta", !r.DEVIDA && r.ALERTA === null);
r = d("2026-09-23", "2026-09-18");
t("quarta sem checagem ok desde terca -> RETENTATIVA com alerta",
  r.DEVIDA && r.TENTATIVA === "RETENTATIVA" && /NAO_CONFIRMADA/.test(r.ALERTA), JSON.stringify(r));
r = d("2026-09-24", "2026-09-18");
t("quinta idem -> RETENTATIVA", r.DEVIDA && r.TENTATIVA === "RETENTATIVA");
r = d("2026-09-25", "2026-09-18");
t("sexta -> nao devida, mas o ALERTA CONTINUA", !r.DEVIDA && !!r.ALERTA, JSON.stringify(r));
r = d("2026-09-28", "2026-09-18");
t("segunda -> nao devida, alerta continua", !r.DEVIDA && !!r.ALERTA);
r = d("2026-09-29", "2026-09-18");
t("terca seguinte -> devida PRIMARIA e o alerta vem de tras",
  r.DEVIDA && r.TENTATIVA === "PRIMARIA" && /SEM_CHECAGEM_OK_DESDE_2026-09-18/.test(r.ALERTA), JSON.stringify(r));
r = d("2026-09-21", "2026-09-14");
t("segunda nunca e dia de coleta", !r.DEVIDA);
r = d("2026-09-22", null);
t("sem nenhuma checagem ok -> devida na terca, alerta NUNCA", r.DEVIDA && r.ALERTA === "NUNCA_CHECADA_COM_SUCESSO");
r = d("2026-09-25", null);
t("sem nenhuma checagem ok, sexta -> nao devida, alerta continua", !r.DEVIDA && r.ALERTA === "NUNCA_CHECADA_COM_SUCESSO");

console.log("\n3 · MENSAL + EXTRAORDINARIA (portfolio)");
const MEN = CONTRACTS["IT-T9-008"].ENDPOINTS_DE_REFERENCIA.CATALOGO.CADENCIA;
t("ja checada no mes -> nao devida", !devidaHoje(MEN, "2026-09-27", "2026-09-15").DEVIDA);
t("mes novo -> devida", devidaHoje(MEN, "2026-10-01", "2026-09-15").DEVIDA);
r = devidaHoje(MEN, "2026-09-27", "2026-09-15", ["019999"]);
t("diff com produto ADAMA novo -> EXTRAORDINARIA no mesmo mes", r.DEVIDA && r.TENTATIVA === "EXTRAORDINARIA");

console.log("\n4 · A ROTACAO DAS BULAS: DISPARADAS PRIMEIRO, NUNCA ACIMA DO TETO");
const ETI = CONTRACTS["IT-T4-001"].ENDPOINTS_DE_REFERENCIA.ETICHETTE.CADENCIA;
const fila = [{ ID: "000100", ULTIMA_CHECAGEM_OK: "2026-09-01" }, { ID: "000200", ULTIMA_CHECAGEM_OK: null },
              { ID: "000300", ULTIMA_CHECAGEM_OK: "2026-08-01" }, { ID: "011111", ULTIMA_CHECAGEM_OK: "2026-09-20" }];
let p = planoDaRotacao({ cad: ETI, disparados: ["011111", "019999"], fila, jaGastos: 0, teto: 5, reservaRobots: 1 });
t("disparadas vem primeiro, depois a mais antiga (nunca checada a frente)",
  JSON.stringify(p.HOJE.map((x) => x.ID)) === '["011111","019999","000200"]', JSON.stringify(p.HOJE));
t("no maximo 3 por dia", p.HOJE.length === 3);
p = planoDaRotacao({ cad: ETI, disparados: ["A", "B", "C", "D"], fila: [], jaGastos: 1, teto: 5, reservaRobots: 1 });
t("o que nao cabe fica DITO como adiado", JSON.stringify(p.ADIADAS_DISPARADAS) === '["D"]' && p.HOJE.length === 3);
p = planoDaRotacao({ cad: ETI, disparados: ["A", "B"], fila, jaGastos: 3, teto: 5, reservaRobots: 1 });
t("o CSV ja gastou o dominio: so cabe o resto do teto", p.HOJE.length === 1 && p.ORCAMENTO.CABE_HOJE === 1);
p = planoDaRotacao({ cad: ETI, disparados: ["A"], fila, jaGastos: 5, teto: 5, reservaRobots: 0 });
t("teto esgotado -> zero hoje, nunca negativo", p.HOJE.length === 0 && p.ORCAMENTO.CABE_HOJE === 0);
t("o ciclo e declarado estimativa", /ESTIMATIVA/.test(p.CICLO_E));

console.log("\n5 · O FILTRO DO CORREDOR");
const contratos = { "IT-T4-001": CONTRACTS["IT-T4-001"], "IT-T3-010": CONTRACTS["IT-T3-010"] };
let f = filtrarPorCadencia(["IT-T3-010", "IT-T4-001"], contratos, "2026-09-25", { "IT-T4-001": "2026-09-18T17:00:00Z" });
t("sem CADENCIA passa como sempre; a semanal fora do dia sai COM porque",
  JSON.stringify(f.aColher) === '["IT-T3-010"]' && !!f.foraDaCadencia["IT-T4-001"] && !!f.alertas["IT-T4-001"]);
f = filtrarPorCadencia(["IT-T3-010", "IT-T4-001"], contratos, "2026-09-22", { "IT-T4-001": "2026-09-18T17:00:00Z" });
t("na terca a semanal entra", f.aColher.includes("IT-T4-001"));
f = filtrarPorCadencia(["IT-T4-001"], contratos, "2026-09-22", null);
t("sem a leitura das checagens -> NAO SEI, nao adivinha e nao colhe",
  f.aColher.length === 0 && /NAO SEI/.test(f.foraDaCadencia["IT-T4-001"]));
f = filtrarPorCadencia(["IT-T3-010"], contratos, "2026-09-25", {});
t("a cadencia nao ACRESCENTA ninguem: so tira do dia", JSON.stringify(f.aColher) === '["IT-T3-010"]');

console.log("\n6 · O CORREDOR AGENDADO USA A CADENCIA, DEPOIS DO PORTAO");
const runner = readFileSync(new URL("../coleta/italy_recurrent_collect.mjs", import.meta.url), "utf8");
const codigo = runner.split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
t("importa filtrarPorCadencia", /import \{ filtrarPorCadencia \} from "\.\.\/regras\/cadencia_da_referencia\.mjs"/.test(codigo));
t("a cadencia corre DEPOIS do portao e ANTES do coletor",
  codigo.indexOf("collection_gate.py") < codigo.indexOf("filtrarPorCadencia(aColher")
  && codigo.indexOf("filtrarPorCadencia(aColher") < codigo.indexOf('import("./italy_pilot_collect.mjs")'));
// Medido pela mutacao K5: chamar o filtro e deitar fora o resultado passava por todas as guardas acima.
t("o resultado do filtro E a populacao a colher (nao so e calculado)",
  /const cad = filtrarPorCadencia\(aColher,[^\n]*\n\s*aColher = cad\.aColher;/.test(codigo)
  && codigo.indexOf("aColher = cad.aColher;") < codigo.indexOf("executarRodada({"));
t("a ultima checagem vem do dono (leis/frescor_da_referencia.py)", codigo.includes('"leis/frescor_da_referencia.py", "--json"'));
t("o corredor continua sem passar ids ao portao", !codigo.includes("--ids="));

console.log(`\n===== ${ok} passaram, ${falhas} falharam =====`);
process.exit(falhas ? 1 : 0);
