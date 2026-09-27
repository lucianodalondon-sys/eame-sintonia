// UM EXECUTOR da prova do contador de 24 h (D90): uma corrida REAL do transporte
// (`executarRodada`, curl de verdade) contra o servidor local, num processo proprio.
//
//     node provas/contador_24h_executor.mjs <host> <porta> <run_id> <n_materias>
//
// Nao sabe nada do outro executor: partilha com ele SO o livro de 24 h
// (SINTONIA_TETO_24H), como duas linhas de rede diferentes partilhariam.
// Escreve numa linha JSON o que a corrida disse (pedidos por host, recusas).
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [host, porta, runId, nMat] = process.argv.slice(2);
process.env.ITALY_OPS_ROOT = mkdtempSync(join(tmpdir(), "contador24h-ops-"));   // ledger proprio e vazio
for (const k of ["SINTONIA_TETO_ONDA", "SINTONIA_TETO_POR_HOST"]) delete process.env[k];
process.env.SINTONIA_PAUSA_POR_HOST_S = "0";

const M = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
CONTRACTS[FONTE].ACQUISITION = { ...CONTRACTS[FONTE].ACQUISITION, INDEX_URL: `http://${host}:${porta}/news/`, MAX_TARGETS: 30,
  LINK_PATTERN: String.raw`^http://(?:www\.)?[a-z]+\.test:\d+/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$` };
CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `http://${host}:${porta}/news/`;
CONTRACTS[FONTE].RECOLLECTION = undefined;
let resumo = null, erro = null;
try {
  ({ resumo } = await M.executarRodada({ runId, apenas: [FONTE], pularParse: true, nota: `contador 24h ${runId} (${nMat})` }));
} catch (e) { erro = String(e.message || e).slice(0, 300); }
const c = resumo?.CORTESIA || {};
console.log(JSON.stringify({ RUN_ID: runId, ERRO: erro, PEDIDOS_POR_HOST: c.PEDIDOS_POR_HOST || null,
  RECUSAS: (c.RECUSAS || []).map(r => r.MOTIVO || r.motivo || r.RECUSADO || r).slice(0, 20) }));
