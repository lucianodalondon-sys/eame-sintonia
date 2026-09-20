// SINTONIA EAME — A PROCEDÊNCIA DO CONTRATO
//
// O DEFEITO QUE ISTO FECHA, MEDIDO
// ---------------------------------
// `SOURCE_CONTRACT_VERSION` era um literal digitado dentro do coletor:
//
//     coleta/italy_pilot_collect.mjs:599
//     SOURCE_CONTRACT_VERSION: "italy-contracts-v1"
//
// Medido no ledger: **41 corridas**, todas carimbadas `v1`, sobre **12
// GIT_HEAD diferentes** — e `regras/italy_contracts.mjs` mudou em 6 commits
// nesse intervalo, incluindo mudanças de conteúdo. O literal mudou uma vez:
// quando nasceu.
//
//     UM CAMPO QUE NUNCA MUDA NÃO VERSIONA NADA. É UM CARIMBO.
//
// E quem o digitava era o consumidor, não o dono do contrato:
//
//     QUEM ESCREVE A PRÓPRIA VERSÃO NÃO A DECLARA — AFIRMA-A.
//
// QUATRO PERGUNTAS, QUATRO CAMPOS
// --------------------------------
// A confusão era ter um campo só para quatro perguntas distintas. Decisão do
// dono, fechada:
//
//     SOURCE_CONTRACT_VERSION  que FORMATO o runtime entende
//     SOURCE_CONTRACT_HASH     que contrato EXECUTÁVEL correu, naquela fonte
//     CONFIG_HASH              que CONFIGURAÇÃO efetiva a corrida teve
//     CONTRATO_MOTOR_VERSAO    que MOTOR interpretou o contrato
//     GIT_HEAD                 que árvore de código inteira estava lá
//
// Nenhum substitui o outro. Acrescentar uma fonte NÃO move a versão do
// schema — move o hash. Acrescentar `ACQUISITION` ao formato MOVE a versão.

import { createHash } from "node:crypto";

// ── O DONO ÚNICO DA VERSÃO DO SCHEMA ───────────────────────────────────────
// Sobe para `v2` porque o formato mudou de maneira material: `ACQUISITION` e
// `IDENTITY` entraram, e um runtime que só entenda `v1` não sabe executá-los.
//
// ⚠️ AS 41 CORRIDAS ANTIGAS FICAM `v1`, E ISSO NÃO SE CORRIGE.
// Elas dizem a verdade sobre o formato que existia quando correram. Reescrevê-las
// seria fazer o passado declarar um contrato que ainda não tinha sido escrito.
//
//     A HISTÓRIA NÃO SE ACTUALIZA. ELA DATA-SE.
export const SOURCE_CONTRACT_VERSION = "italy-contracts-v2";

// ── OS CAMPOS QUE O RUNTIME REALMENTE LÊ ───────────────────────────────────
// ⚠️ A LISTA É DE LEITURA, NÃO DE VONTADE.
// Só entra no hash o que muda execução. `DISCOVERY_METHOD`, `aviso_de_idioma`
// e `DOCUMENT_ID_RULE` são prosa para gente — corrigir uma vírgula neles não
// pode invalidar a procedência de uma coleta que correu igual.
//
//     UM HASH QUE MUDA COM UM COMENTÁRIO MEDE O FICHEIRO, NÃO O CONTRATO.
//
// E o contrário é pior: deixar de fora um campo que o runtime lê faria dois
// contratos diferentes carimbarem o mesmo hash. Por isso esta lista espelha
// exactamente os campos que `motor_de_rota.mjs` consome.
const CAMPOS_EXECUTAVEIS = Object.freeze([
  "ACQUISITION", "IDENTITY",
  // consumidos pela validação do que foi buscado
  "EXPECTED_MIME", "EXPECTED_SIGNATURE", "MIN_BYTES", "MIN_ROWS",
  "OUTPUT_TYPE", "EXPECTED_COLUMNS", "EXPECTED_CONTENT_MARKERS",
  // consumidos pelo roteamento
  "ROUTE_TYPE", "ACCESS_INSTRUMENT", "AUTH_REQUIRED",
  "BROWSER_REQUIRED", "JS_REQUIRED",
]);

// ── SERIALIZAÇÃO CANÓNICA ──────────────────────────────────────────────────
// `JSON.stringify` cru não serve, e a razão é concreta: os contratos guardam
// `EXPECTED_MIME` como RegExp, e `JSON.stringify(/^application\/pdf/)` devolve
// `{}` — o padrão desaparece e dois contratos com MIME diferente ficariam com
// o mesmo hash.
//
//     UMA SERIALIZAÇÃO QUE PERDE INFORMAÇÃO PRODUZ UM HASH QUE MENTE.
//
// As chaves saem ordenadas para que a ordem acidental de escrita não mude o
// resultado: o hash é da SEMÂNTICA, não da digitação.
function canonico(v) {
  if (v === null || v === undefined) return null;
  if (v instanceof RegExp) return { REGEX_SOURCE: v.source, REGEX_FLAGS: v.flags };
  if (Array.isArray(v)) return v.map(canonico);
  if (typeof v === "object") {
    const fora = {};
    for (const k of Object.keys(v).sort()) fora[k] = canonico(v[k]);
    return fora;
  }
  if (typeof v === "function") {
    // Um contrato não carrega código. Se aparecer uma função aqui, o hash não
    // a disfarça de dado — grita.
    throw new Error("contrato com função: o contrato é dado, não programa");
  }
  return v;
}

const sha = (s) => createHash("sha256").update(s).digest("hex");

export function contratoExecutavel(contrato) {
  const fora = {};
  for (const k of CAMPOS_EXECUTAVEIS) {
    if (contrato && contrato[k] !== undefined) fora[k] = canonico(contrato[k]);
  }
  return fora;
}

export function hashDoContrato(contrato) {
  return sha(JSON.stringify(contratoExecutavel(contrato)));
}

// ── A CONFIGURAÇÃO EFECTIVA DA CORRIDA ─────────────────────────────────────
// ⚠️ O QUE NÃO ENTRA É TÃO DELIBERADO QUANTO O QUE ENTRA.
// `RUN_ID`, `STARTED_AT` e `CAPTURED_AT` ficam DE FORA: duas corridas com a
// mesma configuração têm de dar o mesmo `CONFIG_HASH`. Se o relógio entrasse,
// o campo passava a medir «quando» em vez de «com quê» — e deixava de servir
// para a pergunta que existe para responder:
//
//     ESTA CORRIDA CORREU COM A MESMA CONFIGURAÇÃO DA ANTERIOR?
export function hashDaConfiguracao({
  sourceId, contractHash, contractVersion, motorVersao,
  mode = null, windowStart = null, windowEnd = null, params = null,
} = {}) {
  return sha(JSON.stringify(canonico({
    SOURCE_ID: sourceId,
    SOURCE_CONTRACT_HASH: contractHash,
    SOURCE_CONTRACT_VERSION: contractVersion,
    CONTRATO_MOTOR_VERSAO: motorVersao,
    MODE: mode,
    WINDOW_START: windowStart,
    WINDOW_END: windowEnd,
    PARAMS: params,
  })));
}

export const CAMPOS_DO_HASH = CAMPOS_EXECUTAVEIS;
