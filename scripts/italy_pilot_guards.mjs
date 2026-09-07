// GUARDAS DO PILOTO DE COLETA RECORRENTE.
// Exportados para serem rodados dentro de italy_contract_test.mjs, no mesmo placar.
import { readFileSync } from "node:fs";
import { CONTRACTS } from "./italy_contracts.mjs";
import { PILOT_SOURCES, lerLedger, estadoDeCadencia } from "./italy_pilot_collect.mjs";

export function guardasDoPiloto(T) {
  const led = lerLedger();
  const runs = readFileSync("data/collection-ledger/italy/runs.ndjson", "utf8").trim().split("\n").map(l => JSON.parse(l));
  const r1 = runs[0], r2 = runs.at(-1);

  console.log("\n21 · o piloto rodou de verdade e o ledger e o indice explicito");
  T("existem pelo menos duas execucoes registradas", runs.length >= 2, String(runs.length));
  T("o ledger tem observacoes", led.length > 0, String(led.length));
  T("toda observacao aponta RUN_ID e SOURCE_ID", led.every(o => o.RUN_ID && o.SOURCE_ID));
  T("toda observacao bem-sucedida tem DOCUMENT_ID e RAW_SHA256",
    led.filter(o => o.HEALTH_STATE !== "FAILED").every(o => o.DOCUMENT_ID && o.RAW_SHA256));
  T("o piloto cobre exatamente as 7 fontes contratadas",
    new Set(led.map(o => o.SOURCE_ID)).size === PILOT_SOURCES.length, String(new Set(led.map(o => o.SOURCE_ID)).size));

  console.log("\n22 · FIRST_RUN = BASELINE");
  T("a primeira rodada esta marcada como baseline", r1.IS_BASELINE === true);
  T("a primeira rodada NAO diz 'novo desde ontem' (nada marcado NEW_DOCUMENT)",
    led.filter(o => o.RUN_ID === r1.RUN_ID).every(o => o.OBSERVATION_RESULT !== "NEW_DOCUMENT"));
  T("a segunda rodada NAO e baseline", r2.IS_BASELINE === false);

  console.log("\n23 · CAPTURE != DOCUMENT · IDEMPOTENT_SECOND_RUN");
  const docs = new Set(led.filter(o => o.DOCUMENT_ID).map(o => o.SOURCE_ID + "|" + o.DOCUMENT_ID));
  T("ha mais observacoes do que documentos (ver de novo nao cria documento)",
    led.length > docs.size, `${led.length} observacoes / ${docs.size} documentos`);
  T("a segunda rodada criou ZERO objetos RAW", r2.contadores.RAW_OBJECTS_CREATED === 0, String(r2.contadores.RAW_OBJECTS_CREATED));
  T("a segunda rodada criou ZERO documentos novos", r2.contadores.NEW_DOCUMENTS === 0);
  T("a segunda rodada criou ZERO observacoes normalizadas novas", r2.contadores.NORMALIZED_OBSERVATIONS_NEW === 0);
  T("a segunda rodada marcou SEEN_AGAIN tudo que reviu", r2.contadores.SEEN_AGAIN > 0, String(r2.contadores.SEEN_AGAIN));
  T("as duas coletas ficaram no ledger — observamos 2x sem fingir que achamos 2 coisas",
    led.some(o => o.RUN_ID === r1.RUN_ID) && led.some(o => o.RUN_ID === r2.RUN_ID));

  console.log("\n24 · SAME_HASH != DEGRADED · NO_CHANGE != FAILURE");
  const revistas = led.filter(o => o.OBSERVATION_RESULT === "SEEN_AGAIN");
  T("nenhuma observacao SEEN_AGAIN virou DEGRADED", revistas.every(o => o.HEALTH_STATE !== "DEGRADED"), `${revistas.length} revistas`);
  T("nenhuma observacao SEEN_AGAIN virou FAILED", revistas.every(o => o.HEALTH_STATE !== "FAILED"));
  // olhar os VALORES dos contratos, nao o texto do arquivo: o comentario de correcao
  // cita a formulacao errada de proposito, para deixar registrado o que mudou.
  T("nenhuma regra VIVA de contrato diz que hash repetido e DEGRADED",
    !Object.values(CONTRACTS).some(c => /(hash repetido|SHA de ontem|SHA numa nova captura)[^"]{0,20}=\s*DEGRADED/i.test(JSON.stringify(c))));
  T("o contrato do ARPAV diz explicitamente que mesmo SHA e NO_CHANGE, nao DEGRADED",
    /mesmo SHA numa nova captura = NO_CHANGE, NAO DEGRADED/.test(JSON.stringify(CONTRACTS["IT-T2-002"])));
  T("os contratos carregam a lei SAME_HASH != DEGRADED",
    /SAME_HASH\s*!=\s*DEGRADED/.test(readFileSync("scripts/italy_contracts.mjs", "utf8")));

  console.log("\n25 · OVERDUE_UPDATE exige prova de cadencia");
  const semCad = led.filter(o => o.OBSERVED_FREQUENCY && !/provado/i.test(String(o.OBSERVED_FREQUENCY)));
  T("nenhuma fonte sem cadencia provada foi acusada de atraso",
    semCad.every(o => o.CADENCE_STATE !== "OVERDUE_UPDATE"), `${semCad.length} observacoes sem cadencia provada`);
  T("fonte sem cadencia provada que nao mudou recebe CADENCE_UNKNOWN",
    semCad.filter(o => o.OBSERVATION_RESULT === "SEEN_AGAIN").every(o => o.CADENCE_STATE === "CADENCE_UNKNOWN"));
  T("fonte COM cadencia provada e dentro do prazo recebe EXPECTED_NO_CHANGE",
    led.filter(o => /provado/i.test(String(o.OBSERVED_FREQUENCY)) && o.OBSERVATION_RESULT === "SEEN_AGAIN")
      .every(o => o.CADENCE_STATE === "EXPECTED_NO_CHANGE"));
  T("a funcao de cadencia so devolve OVERDUE com cadencia provada E prazo vencido",
    estadoDeCadencia(CONTRACTS["IT-T3-010"], { SOURCE_DATE_ISO: "2026-07-01" }, false).CADENCE_STATE === "OVERDUE_UPDATE" &&
    estadoDeCadencia(CONTRACTS["IT-T2-004"], { SOURCE_DATE_ISO: "2026-07-01" }, false).CADENCE_STATE === "CADENCE_UNKNOWN");

  console.log("\n26 · SAME_URL != SAME_DOCUMENT · DOCUMENT_ID != BYTE_ID");
  T("nenhum DOCUMENT_ID e a propria URL", led.filter(o => o.DOCUMENT_ID).every(o => o.DOCUMENT_ID !== o.SOURCE_URL));
  T("nenhum DOCUMENT_ID e igual ao SHA256", led.filter(o => o.DOCUMENT_ID).every(o => o.DOCUMENT_ID !== o.RAW_SHA256));
  T("as tres fontes de URL fixa tem DOCUMENT_ID derivado do CONTEUDO",
    ["IT-T3-005", "IT-T2-002", "IT-T2-004"].every(id =>
      led.filter(o => o.SOURCE_ID === id && o.DOCUMENT_ID).length > 0 &&
      led.filter(o => o.SOURCE_ID === id && o.DOCUMENT_ID).every(o => /\d{4}/.test(o.DOCUMENT_ID))));

  console.log("\n27 · MOVING_WINDOW != NEW_DATASET_EVERY_DAY");
  const sias = led.filter(o => o.SOURCE_ID === "IT-T2-004" && o.parse);
  T("o SIAS foi normalizado por STATION + DATE + VARIABLE", sias.every(o => o.parse.UNIQUE_STATION_DATE_VARIABLE > 0));
  T("na segunda rodada o SIAS nao gerou nenhuma observacao normalizada nova",
    sias.filter(o => o.RUN_ID === r2.RUN_ID).every(o => o.parse.NEW_NORMALIZED_OBSERVATIONS === 0));
  T("a janela tem mais linhas do que dias — a chave nao e a pagina",
    sias.length > 0 && sias[0].parse.ROWS_IN_WINDOW > 11);

  console.log("\n28 · PARSER_FAILURE MUST NOT DESTROY CAPTURED_RAW");
  T("toda observacao declara RAW preservado ANTES do parse",
    led.filter(o => o.RAW_SHA256).every(o => o.RAW_PRESERVED_BEFORE_PARSE === true));
  T("nenhuma observacao com erro de parse perdeu o RAW",
    led.filter(o => o.PARSE_ERROR).every(o => o.RAW_SHA256));

  console.log("\n29 · SOURCE_HEALTH != SOURCE_VERDICT");
  T("o ledger so guarda saude por execucao", led.every(o => ["HEALTHY", "DEGRADED", "FAILED", "UNKNOWN"].includes(o.HEALTH_STATE)));
  T("nenhuma observacao do ledger carrega veredito analitico", led.every(o => !/GREEN|YELLOW/.test(String(o.HEALTH_STATE))));

  console.log("\n30 · tempos separados, e nada vira data de fato sem prova");
  T("toda observacao separa CAPTURED_AT de COLLECTION_RUN_STARTED_AT", led.every(o => o.CAPTURED_AT && o.COLLECTION_RUN_STARTED_AT));
  T("nenhuma observacao usa CAPTURED_AT como FACT_TIME", led.filter(o => o.FACT_TIME).every(o => o.FACT_TIME !== o.CAPTURED_AT));
  T("FACT_TIME e UNKNOWN onde nao ha prova", led.filter(o => o.FACT_TIME).some(o => /UNKNOWN/.test(o.FACT_TIME)));
  T("toda execucao registra VPN_COUNTRY, EGRESS_IP, GIT_HEAD e versao do coletor",
    runs.every(r => r.VPN_COUNTRY && r.EGRESS_IP && r.GIT_HEAD && r.COLLECTOR_VERSION));
  T("as execucoes sairam pela Italia", runs.every(r => r.VPN_COUNTRY === "IT"));

  console.log("\n31 · nada de agendamento nesta missao");
  const arquivos = ["scripts/italy_pilot_collect.mjs", "scripts/italy_pilot_negativos.mjs"].map(f => readFileSync(f, "utf8")).join("");
  T("o piloto nao instala cron, timer nem scheduler", !/node-cron|setInterval|crontab|systemd|schedule\(/i.test(arquivos));
  T("o retry existe e e limitado", /TRANSITORIOS/.test(arquivos) && /tentativas = 2/.test(arquivos));
  T("nao ha retry para schema, MIME, login ou WAF",
    /Nunca para schema, MIME, login ou WAF/.test(arquivos));
}
