// GUARDAS DO AGENDAMENTO FORWARD-ONLY.
// Cada lei critica tem um controle negativo REAL, medido do log de execucoes.
import { readFileSync, existsSync } from "node:fs";
import { PROFILES } from "./italy_profiles.mjs";

const OPS = "C:/eame-sintonia-ops";
const LOG = `${OPS}/data/collection-ledger/italy/logs/runs.log`;

export function guardasDeAgendamento(T) {
  const P = PROFILES["forward-only-live"];
  const runs = existsSync(LOG) ? readFileSync(LOG, "utf8").trim().split("\n").filter(Boolean).map(l => JSON.parse(l)) : [];
  const runner = readFileSync("coleta/italy_recurrent_collect.mjs", "utf8");

  console.log("\n32 · ONLY_FORWARD_ONLY_PROFILE · NO_SILENT_FOURTH_SOURCE");
  T("o perfil forward-only-live tem exatamente 3 fontes", P.SOURCES.length === 3, P.SOURCES.join(","));
  T("sao exatamente as tres FORWARD_ONLY contratadas",
    ["IT-T3-005", "IT-T2-002", "IT-T2-004"].every(s => P.SOURCES.includes(s)));
  T("nenhuma fonte de outra prioridade entrou no perfil",
    !P.SOURCES.some(s => ["IT-T3-002", "IT-T3-010", "IT-T3-008", "IT-T4-001"].includes(s)));
  T("nenhuma execucao agendada tocou mais de 3 fontes",
    runs.filter(r => r.SOURCE_ATTEMPTED > 0).every(r => r.SOURCE_ATTEMPTED === 3),
    [...new Set(runs.map(r => r.SOURCE_ATTEMPTED))].join(","));

  console.log("\n33 · VPN_CHECK_PRECEDES_SOURCE_ACCESS · VPN_FAILURE != SOURCE_FAILURE");
  T("no codigo, a checagem de egress vem ANTES de importar o coletor",
    runner.indexOf("checarEgress()") < runner.indexOf("italy_pilot_collect.mjs"));
  const vpnFail = runs.filter(r => r.reason === "VPN_NOT_ITALY");
  T("existe controle negativo REAL de VPN nao italiana", vpnFail.length > 0, `${vpnFail.length} execucoes`);
  T("com VPN errada, ZERO fontes foram tocadas", vpnFail.every(r => r.SOURCE_ATTEMPTED === 0 && r.SOURCE_DOWNLOADS === 0));
  T("com VPN errada, nenhuma fonte foi marcada FAILED", vpnFail.every(r => r.SOURCE_FAILED === 0));
  T("com VPN errada, as fontes ficaram NOT_MEASURED", vpnFail.every(r => r.SOURCE_NOT_MEASURED === 3));
  T("toda execucao que coletou registrou egress italiano",
    runs.filter(r => r.SOURCE_ATTEMPTED > 0 && !r.EGRESS_CITY?.includes("simulado")).every(r => r.EGRESS_COUNTRY === "IT"));

  console.log("\n34 · RUNNER_HEALTH != SOURCE_HEALTH");
  T("o resumo separa os dois campos", runs.every(r => "RUNNER_HEALTH" in r && "SOURCE_HEALTHY" in r));
  T("VPN caiu -> RUNNER FAILED e fonte NOT_MEASURED, nunca fonte FAILED",
    vpnFail.every(r => r.RUNNER_HEALTH === "FAILED" && r.SOURCE_NOT_MEASURED === 3));
  const storageRuim = runs.filter(r => r.RUN_STORAGE_STATE === "LOCAL_ONLY");
  T("existe controle negativo REAL de push quebrado", storageRuim.length > 0, `${storageRuim.length} execucoes`);
  T("push quebrado -> RUNNER DEGRADED_STORAGE, mas as fontes seguem saudaveis",
    storageRuim.every(r => r.RUNNER_HEALTH === "DEGRADED_STORAGE" && r.SOURCE_HEALTHY === 3));

  console.log("\n35 · SINGLE_INSTANCE_LOCK");
  const lock = runs.filter(r => r.RUN_STATE === "SKIPPED_LOCK_HELD");
  T("existe controle negativo REAL de trava ocupada", lock.length > 0, `${lock.length} execucoes`);
  T("com trava ocupada, zero fontes tocadas", lock.every(r => r.SOURCE_ATTEMPTED === 0));
  T("com trava ocupada, o corredor NAO e marcado como quebrado", lock.every(r => r.RUNNER_HEALTH === "HEALTHY"));
  T("o codigo usa criacao exclusiva de arquivo como trava", /openSync\(LOCK, "wx"\)/.test(runner));
  T("o agendador tambem recusa segunda instancia (MultipleInstances IgnoreNew)",
    /IgnoreNew/.test(readFileSync("docs/operacao/ITALY-FORWARD-ONLY-SCHEDULING-V1.md", "utf8")));

  console.log("\n36 · LOCAL_COMMIT != REMOTE_DURABILITY · FAILED_PUSH_PRESERVES_LOCAL_STATE");
  T("o resumo declara RUN_STORAGE_STATE", runs.filter(r => r.SOURCE_ATTEMPTED > 0).every(r => !!r.RUN_STORAGE_STATE));
  T("so ha DURABLE_REMOTE quando local e remoto batem",
    runs.filter(r => r.RUN_STORAGE_STATE === "DURABLE_REMOTE").every(r => r.LOCAL_HEAD === r.REMOTE_HEAD));
  T("push quebrado nao apaga nem refaz: a lei esta escrita no proprio resumo",
    storageRuim.every(r => /nao foram apagados|nao sera refeita/i.test(String(r.lei_storage))));
  // apagar o arquivo de TRAVA e correto; o que nao pode e apagar ledger ou store.
  const blocoCatch = (runner.split("catch (e) {")[1] ?? "").split("}")[0];
  T("o bloco de erro de push nao apaga ledger nem store",
    !/LEDGER_DIR|STORE|collection-(ledger|store)/.test(blocoCatch));
  const remocoes = runner.match(/unlinkSync\([^)]*\)/g) ?? [];
  T("o runner remove algum arquivo (o teste tem o que medir)", remocoes.length > 0, String(remocoes.length));
  T("a unica remocao de arquivo no runner e a da trava ou do teste de escrita",
    remocoes.every(m => /LOCK/.test(m) || /\.w`/.test(m)), remocoes.join(" · "));

  console.log("\n37 · SCHEDULER_TIMEZONE_EXPLICIT · RAW_BEFORE_PARSE");
  T("o fuso operacional e declarado como Europe/Rome", P.SCHEDULER_TIMEZONE === "Europe/Rome");
  T("o codigo calcula a hora em Europe/Rome, e nao no fuso da maquina",
    /timeZone: "Europe\/Rome"/.test(runner));
  T("toda execucao registra a hora em Roma", runs.every(r => typeof r.HORA_EM_ROMA === "number"));
  T("existe execucao que PULOU por estar fora da janela de Roma",
    runs.some(r => r.RUN_STATE === "SKIPPED_OUT_OF_WINDOW"));
  T("o perfil separa hora de coleta de hora de publicacao da fonte",
    /NAO e SOURCE_DECLARED_PUBLICATION_TIME/.test(P.aviso_de_horario));
  T("a ordem do run poe RAW antes do parse, escrita no proprio arquivo",
    /8 RAW primeiro · 9 bytes · 10 sha · 11 RAW imutavel · 12 ledger · 13 normalizar/.test(runner));

  console.log("\n38 · SCHEDULER_HOST_MUST_BE_PERSISTENT");
  const doc = readFileSync("docs/operacao/ITALY-FORWARD-ONLY-SCHEDULING-V1.md", "utf8");
  T("o host foi medido, nao inferido", /HOST_KIND/.test(doc) && /LastBootUpTime|uptime/i.test(doc));
  T("esta declarado se o host sobrevive ao fim da sessao do Claude", /PERSISTENT_AFTER_CLAUDE_SESSION/.test(doc));
  T("a limitacao do fuso do Windows esta declarada", /n[aã]o tem fuso por tarefa/i.test(doc));
  T("o documento diz que o fuso mora no codigo, nao no agendador", /o fuso mora no c[oó]digo, n[aã]o no agendador/i.test(doc));
  T("a condicao da VPN apos reinicio esta declarada", /login|reinici/i.test(doc));

  console.log("\n39 · ARPAV: cobertura declarada, nao presumida");
  const z = P.ARPAV_OPERATIONAL_ZONES;
  T("o universo de zonas foi decidido explicitamente", z.publicadas === 29 && z.numeradas === 32);
  T("as zonas nao publicadas estao nomeadas", z.nao_publicadas.join(",") === "17,18,19");
  T("o custo por execucao foi MEDIDO antes de decidir", /13\.373\.903/.test(z.custo_medido_por_execucao));
  T("nao se diz 'Veneto capturado' com cobertura parcial", /nao se pode dizer 'Veneto capturado'/.test(z.por_que_29_e_nao_4));

  console.log("\n40 · a mensagem automatica nao mente");
  T("a mensagem de commit e factual e cita seen again",
    runs.filter(r => r.COMMIT && r.COMMIT.startsWith("ops italy")).every(r => /healthy · \d+ new · \d+ changed · \d+ seen again/.test(r.COMMIT)));
  T("nenhuma mensagem diz 'new data' quando so houve SEEN_AGAIN",
    !runs.some(r => /new data/i.test(String(r.COMMIT)) && r.NEW_DOCUMENTS === 0));
  T("houve execucao com 0 novos que ainda assim registrou observacoes",
    runs.some(r => r.NEW_DOCUMENTS === 0 && r.SEEN_AGAIN > 0));
}
