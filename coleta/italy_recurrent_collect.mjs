// ENTRYPOINT CANONICO DA COLETA AGENDADA — FORWARD-ONLY.
// O agendador chama SO isto. Nenhuma logica mora no agendador.
//
// LEIS QUE ESTE ARQUIVO CARREGA:
//   VPN_FAILURE            != SOURCE_FAILURE      VPN caiu nao e a fonte que falhou
//   RUNNER_HEALTH          != SOURCE_HEALTH       o corredor e a pista sao coisas diferentes
//   LOCAL_COMMIT           != REMOTE_DURABILITY   commit local nao e durabilidade
//   RAW BEFORE PARSE       preservar antes de interpretar
//   SAME_HASH              != DEGRADED
//   uma fonte falhar NAO impede as outras de serem preservadas
//
// ORDEM OBRIGATORIA (nunca reordenar):
//   1 lock · 2 runtime · 3 timezone · 4 VPN Italia · 5 storage · 6 contratos · 7 RUN_ID
//   8 RAW primeiro · 9 bytes · 10 sha · 11 RAW imutavel · 12 ledger · 13 normalizar
//   14 saude da fonte · 15 guardas · 16 commit · 17 push · 18 provar remoto · 19 soltar lock
//
// Uso:
//   node coleta/italy_recurrent_collect.mjs --profile forward-only-live
//   ... --gate-hour           so executa dentro da janela de 20h em Europe/Rome
//   ... --simulate-vpn XX     controle negativo: finge outro pais
//   ... --simulate-push-fail  controle negativo: finge push quebrado
//   ... --no-git              nao commita nem faz push (para teste local)

import { execFile, execFileSync } from "node:child_process";
import { promisify } from "node:util";
import { openSync, closeSync, unlinkSync, existsSync, writeFileSync, readFileSync, mkdirSync, appendFileSync } from "node:fs";
import { PROFILES, PERFIL_PADRAO } from "./italy_profiles.mjs";
import { CONTRACTS } from "./italy_contracts.mjs";

const run = promisify(execFile);
const arg = n => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : null; };
const tem = n => process.argv.includes(n);

const PROFILE_NAME = arg("--profile") || PERFIL_PADRAO;
const PROFILE = PROFILES[PROFILE_NAME];
const OPS_ROOT = process.env.ITALY_OPS_ROOT || process.cwd();
const LOCK = `${OPS_ROOT}/.italy-forward-only.lock`;
const LEDGER_DIR = `${OPS_ROOT}/data/collection-ledger/italy`;
const LOG_DIR = `${OPS_ROOT}/data/collection-ledger/italy/logs`;

const agora = () => new Date().toISOString();
const horaEmRoma = () => Number(new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Rome", hour: "2-digit", hour12: false }).format(new Date()));
const dataEmRoma = () => new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Rome" }).format(new Date());

function log(o) { mkdirSync(LOG_DIR, { recursive: true }); appendFileSync(`${LOG_DIR}/runs.log`, JSON.stringify(o) + "\n"); }

// ---------- 1 · LOCK: uma instancia por vez ----------
function pegarLock() {
  try { const fd = openSync(LOCK, "wx"); writeFileSync(LOCK, JSON.stringify({ pid: process.pid, at: agora() })); closeSync(fd); return true; }
  catch { return false; }
}
function soltarLock() { try { unlinkSync(LOCK); } catch { } }

// ---------- 4 · VPN: precondicao, ANTES de tocar em qualquer fonte ----------
async function checarEgress() {
  const simulado = arg("--simulate-vpn");
  if (simulado) return { EGRESS_COUNTRY: simulado, EGRESS_IP: "0.0.0.0", EGRESS_CITY: "simulado", EGRESS_ASN: null, CHECKED_AT: agora(), SIMULADO: true };
  try {
    const { stdout } = await run("curl", ["-sS", "--max-time", "20", "https://ipinfo.io/json"], { encoding: "utf8" });
    const j = JSON.parse(stdout);
    return { EGRESS_IP: j.ip, EGRESS_COUNTRY: j.country, EGRESS_CITY: j.city, EGRESS_ASN: j.org ?? null, CHECKED_AT: agora() };
  } catch (e) { return { EGRESS_COUNTRY: null, erro: String(e.message).slice(0, 120), CHECKED_AT: agora() }; }
}

// ---------- git operacional ----------
function git(args, opts = {}) { return execFileSync("git", args, { cwd: OPS_ROOT, encoding: "utf8", ...opts }).trim(); }

async function main() {
  const STARTED_AT = agora();
  const t0 = Date.now();
  const resumo = {
    RUN_ID: null, PROFILE: PROFILE_NAME, STARTED: STARTED_AT, FINISHED: null, DURATION_S: null,
    RUNNER_HEALTH: "HEALTHY", RUN_STATE: null,
    SCHEDULER_TIMEZONE: PROFILE?.SCHEDULER_TIMEZONE, HORA_EM_ROMA: horaEmRoma(), DATA_EM_ROMA: dataEmRoma(),
    EGRESS_COUNTRY: null, EGRESS_IP: null,
    SOURCE_ATTEMPTED: 0, SOURCE_HEALTHY: 0, SOURCE_DEGRADED: 0, SOURCE_FAILED: 0, SOURCE_NOT_MEASURED: 0,
    NEW_DOCUMENTS: 0, CHANGED_IN_PLACE: 0, SEEN_AGAIN: 0, RAW_CREATED: 0, NORMALIZED_NEW: 0,
    COMMIT: null, REMOTE_HEAD: null, LOCAL_HEAD: null, RUN_STORAGE_STATE: null
  };

  // 2 · runtime
  if (!PROFILE) { resumo.RUN_STATE = "FAILED_PRECONDITION"; resumo.reason = `perfil desconhecido: ${PROFILE_NAME}`; resumo.RUNNER_HEALTH = "FAILED"; return fim(resumo, t0); }

  // 1 · lock
  if (!pegarLock()) {
    resumo.RUN_STATE = "SKIPPED_LOCK_HELD";
    resumo.RUNNER_HEALTH = "HEALTHY";
    resumo.SOURCE_NOT_MEASURED = PROFILE.SOURCES.length;
    resumo.reason = "outra coleta ja esta rodando — nao se inicia segunda instancia";
    return fim(resumo, t0);
  }

  try {
    // 3 · janela de horario, explicitamente em Europe/Rome (nunca no fuso implicito da maquina)
    if (tem("--gate-hour")) {
      const h = horaEmRoma();
      if (h !== PROFILE.OPERATIONAL_COLLECTION_HOUR) {
        resumo.RUN_STATE = "SKIPPED_OUT_OF_WINDOW";
        resumo.SOURCE_NOT_MEASURED = PROFILE.SOURCES.length;
        resumo.reason = `sao ${h}h em Europe/Rome; a janela e ${PROFILE.OPERATIONAL_COLLECTION_HOUR}h`;
        return fim(resumo, t0);
      }
    }

    // 4 · VPN Italia — ANTES de qualquer acesso a fonte
    const eg = await checarEgress();
    resumo.EGRESS_COUNTRY = eg.EGRESS_COUNTRY; resumo.EGRESS_IP = eg.EGRESS_IP;
    resumo.EGRESS_CITY = eg.EGRESS_CITY; resumo.EGRESS_ASN = eg.EGRESS_ASN; resumo.EGRESS_CHECKED_AT = eg.CHECKED_AT;
    if (eg.EGRESS_COUNTRY !== "IT") {
      resumo.RUN_STATE = "FAILED_PRECONDITION";
      resumo.reason = "VPN_NOT_ITALY";
      resumo.RUNNER_HEALTH = "FAILED";
      resumo.SOURCE_NOT_MEASURED = PROFILE.SOURCES.length;   // NAO_MEDIDO, nunca FAILED
      resumo.lei = "VPN_FAILURE != SOURCE_FAILURE — as fontes nao foram sequer tocadas";
      resumo.SOURCE_DOWNLOADS = 0;
      return fim(resumo, t0);
    }

    // 5 · storage gravavel
    try { mkdirSync(LEDGER_DIR, { recursive: true }); writeFileSync(`${LEDGER_DIR}/.w`, "x"); unlinkSync(`${LEDGER_DIR}/.w`); }
    catch (e) { resumo.RUN_STATE = "FAILED_PRECONDITION"; resumo.reason = "storage nao gravavel"; resumo.RUNNER_HEALTH = "FAILED"; resumo.SOURCE_NOT_MEASURED = PROFILE.SOURCES.length; return fim(resumo, t0); }

    // 6 · contratos existem para todas as fontes do perfil
    const semContrato = PROFILE.SOURCES.filter(s => !CONTRACTS[s]);
    if (semContrato.length) { resumo.RUN_STATE = "FAILED_PRECONDITION"; resumo.reason = `sem contrato: ${semContrato}`; resumo.RUNNER_HEALTH = "FAILED"; resumo.SOURCE_NOT_MEASURED = PROFILE.SOURCES.length; return fim(resumo, t0); }

    // 7..14 · a coleta em si fica no coletor do piloto, reusado com o perfil restrito
    const { executarRodada } = await import("./italy_pilot_collect.mjs");
    const r = await executarRodada({ nota: `ops ${PROFILE_NAME}`, apenas: PROFILE.SOURCES, arpavZonas: PROFILE.ARPAV_OPERATIONAL_ZONES ? "TODAS" : null, raiz: OPS_ROOT });
    const c = r.resumo.contadores;
    resumo.RUN_ID = r.resumo.RUN_ID;
    resumo.SOURCE_ATTEMPTED = c.SOURCES_ATTEMPTED; resumo.SOURCE_HEALTHY = c.HEALTHY;
    resumo.SOURCE_DEGRADED = c.DEGRADED; resumo.SOURCE_FAILED = c.FAILED;
    resumo.NEW_DOCUMENTS = c.NEW_DOCUMENTS; resumo.CHANGED_IN_PLACE = c.CHANGED_IN_PLACE;
    resumo.SEEN_AGAIN = c.SEEN_AGAIN; resumo.RAW_CREATED = c.RAW_OBJECTS_CREATED;
    resumo.NORMALIZED_NEW = c.NORMALIZED_OBSERVATIONS_NEW;
    resumo.RUN_STATE = c.FAILED > 0 ? "COMPLETED_WITH_SOURCE_FAILURES" : "COMPLETED";
    // uma fonte falhar NAO derruba o corredor
    resumo.RUNNER_HEALTH = "HEALTHY";

    // 16..18 · durabilidade
    if (!tem("--no-git")) {
      try {
        git(["add", "data/collection-ledger", "data/collection-store"]);
        const staged = git(["diff", "--cached", "--name-only"]);
        if (staged) {
          const msg = `ops italy forward-only: ${c.HEALTHY} healthy · ${c.NEW_DOCUMENTS} new · ${c.CHANGED_IN_PLACE} changed · ${c.SEEN_AGAIN} seen again`;
          git(["commit", "-q", "-m", msg]);
          resumo.COMMIT = msg;
        } else { resumo.COMMIT = "nada a commitar — nenhum byte novo"; }
        resumo.LOCAL_HEAD = git(["rev-parse", "HEAD"]);
        if (tem("--simulate-push-fail")) throw new Error("push simulado como quebrado");
        git(["push", "-q", "origin", `HEAD:${PROFILE.OPS_BRANCH}`]);
        git(["fetch", "-q", "origin"]);
        resumo.REMOTE_HEAD = git(["rev-parse", `origin/${PROFILE.OPS_BRANCH}`]);
        resumo.RUN_STORAGE_STATE = resumo.LOCAL_HEAD === resumo.REMOTE_HEAD ? "DURABLE_REMOTE" : "LOCAL_ONLY";
        if (resumo.RUN_STORAGE_STATE !== "DURABLE_REMOTE") resumo.RUNNER_HEALTH = "DEGRADED_STORAGE";
      } catch (e) {
        resumo.RUN_STORAGE_STATE = "LOCAL_ONLY";
        resumo.RUNNER_HEALTH = "DEGRADED_STORAGE";
        resumo.storage_erro = String(e.message).slice(0, 160);
        resumo.lei_storage = "LOCAL_COMMIT != REMOTE_DURABILITY. Os dados NAO foram apagados e a coleta NAO sera refeita — a proxima execucao reconcilia primeiro.";
        try { resumo.LOCAL_HEAD = git(["rev-parse", "HEAD"]); } catch { }
      }
    } else { resumo.RUN_STORAGE_STATE = "NOT_ATTEMPTED_NO_GIT"; }

    return fim(resumo, t0);
  } finally { soltarLock(); }
}

function fim(resumo, t0) {
  resumo.FINISHED = agora();
  resumo.DURATION_S = Math.round((Date.now() - t0) / 1000);
  log(resumo);
  console.log(JSON.stringify(resumo, null, 1));
  return resumo;
}

const r = await main();
process.exit(r.RUNNER_HEALTH === "FAILED" ? 2 : r.SOURCE_FAILED > 0 ? 1 : 0);
